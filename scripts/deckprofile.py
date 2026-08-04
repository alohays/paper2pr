#!/usr/bin/env python3
"""Load a deck's config and the design profile it selects.

A deck declares its premises once, in <deck>.deck.yml next to the qmd, and
everything downstream reads them from there instead of guessing: the quality
gate picks its bullet budget and its extra checks, the Korean gate learns
whether this deck is allowed non-English slides, and /write-speaker-notes
learns which language the notes are in.

Profiles live in .claude/rules/slide-profiles/<profile>.yml. They carry both
the numbers and the prose, in one file, because two files drift.

A deck with no config keeps the old behaviour exactly: the profile is inferred
from its genre, and the quality gate's theme-based main/legacy split still
decides whether design checks run at all. That is what keeps the four decks
that predate this system scoring what they scored before.

A config that exists but cannot be parsed is a hard error, not a warning.
Falling back to defaults there would grade a lecture as a paper review and
still print a passing score.

Usage as a library:
    from deckprofile import load
    cfg = load(deck)              # deck from deckpath.find(...)
    cfg.bullets_max, cfg.expand_acronyms, cfg.slide_language

Usage from the shell:
    python3 scripts/deckprofile.py RoboTTT
    python3 scripts/deckprofile.py RoboTTT --field profile
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deckpath  # noqa: E402
import minyaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILE_DIR = REPO_ROOT / ".claude" / "rules" / "slide-profiles"

# Which profile a genre implies when a deck does not say. Genres and profiles
# are deliberately not the same axis -- a deck can sit in lectures/ and still
# be scored as a talk if that is what it is.
GENRE_DEFAULT_PROFILE = {
    "papers": "paper-review",
    "talks": "invited-talk",
    "lectures": "lecture",
}

DEFAULTS = {
    "bullets": {"max_per_slide": 5, "max_with_figure": 3, "max_two_line": 1},
    "checks": {
        "font_shrink": "forbid",
        "box_density": 1,
        "max_nesting": 1,
        "expand_acronyms": False,
        "prior_session_callback": False,
    },
    "language": {"slides": "en", "notes": "ko"},
}

# Top-level keys, which follow the same deck-then-profile-then-default order.
TOP_DEFAULTS = {"duration_min": 30}


class ConfigError(Exception):
    """A config file exists but could not be read. Never soften this."""


def _load_yaml(path: Path):
    """Read a config file, or fail. Absent is fine; unreadable is not.

    This used to catch everything and return {}, which meant a deck with a
    malformed config -- or a machine without PyYAML -- kept scoring, silently
    graded against built-in defaults instead of its own declared budget. A
    lecture would quietly get the paper-review numbers with both lecture
    checks off. The parser is stdlib now (scripts/minyaml.py) so the import
    can no longer fail, and a file we cannot parse stops the run.
    """
    if not path.exists():
        return {}
    try:
        loaded = minyaml.load_path(path)
    except minyaml.MinYamlError as e:
        raise ConfigError(f"{path}: {e}") from e
    except OSError as e:
        raise ConfigError(f"{path}: {e}") from e
    if not isinstance(loaded, dict):
        raise ConfigError(f"{path}: expected a mapping at the top level")
    return loaded


@dataclass
class DeckConfig:
    deck: "deckpath.Deck"
    profile: str
    raw: dict = field(default_factory=dict)
    profile_raw: dict = field(default_factory=dict)

    def _get(self, section: str, key: str):
        """Deck config wins, then the profile, then the built-in default."""
        for src in (self.raw, self.profile_raw):
            sec = src.get(section)
            if isinstance(sec, dict) and key in sec:
                return sec[key]
        return DEFAULTS[section][key]

    def _top(self, key: str):
        for src in (self.raw, self.profile_raw):
            if key in src:
                return src[key]
        return TOP_DEFAULTS[key]

    @property
    def duration_min(self) -> int:
        """How long the deck runs. The notes budget is derived from this, so
        a 60-minute lecture does not inherit a 30-minute script length."""
        try:
            return int(self._top("duration_min"))
        except (TypeError, ValueError):
            raise ConfigError(
                f"{self.deck.config}: duration_min must be a number of "
                f"minutes, got {self._top('duration_min')!r}")

    @property
    def bullets_max(self) -> int:
        return int(self._get("bullets", "max_per_slide"))

    @property
    def bullets_max_with_figure(self) -> int:
        return int(self._get("bullets", "max_with_figure"))

    @property
    def bullets_max_two_line(self) -> int:
        return int(self._get("bullets", "max_two_line"))

    @property
    def box_density(self) -> int:
        return int(self._get("checks", "box_density"))

    @property
    def max_nesting(self) -> int:
        return int(self._get("checks", "max_nesting"))

    @property
    def expand_acronyms(self) -> bool:
        return bool(self._get("checks", "expand_acronyms"))

    @property
    def prior_session_callback(self) -> bool:
        return bool(self._get("checks", "prior_session_callback"))

    @property
    def slide_language(self) -> str:
        return str(self._get("language", "slides"))

    @property
    def notes_language(self) -> str:
        return str(self._get("language", "notes"))

    @property
    def series_index(self) -> int | None:
        """Position in a course series; 1 has no previous session to recall."""
        value = self.raw.get("series_index")
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ConfigError(
                f"{self.deck.config}: series_index must be a number, "
                f"got {value!r}")

    @property
    def has_config(self) -> bool:
        return bool(self.raw)

    def as_dict(self) -> dict:
        return {
            "deck": self.deck.slug,
            "profile": self.profile,
            "has_config": self.has_config,
            "duration_min": self.duration_min,
            "bullets_max": self.bullets_max,
            "bullets_max_with_figure": self.bullets_max_with_figure,
            "bullets_max_two_line": self.bullets_max_two_line,
            "box_density": self.box_density,
            "max_nesting": self.max_nesting,
            "expand_acronyms": self.expand_acronyms,
            "prior_session_callback": self.prior_session_callback,
            "series_index": self.series_index,
            "slide_language": self.slide_language,
            "notes_language": self.notes_language,
        }


def profiles() -> list[str]:
    if not PROFILE_DIR.is_dir():
        return []
    return sorted(p.stem for p in PROFILE_DIR.glob("*.yml"))


def load(deck: "deckpath.Deck") -> DeckConfig:
    raw = _load_yaml(deck.config)
    name = raw.get("profile") or GENRE_DEFAULT_PROFILE.get(deck.genre)
    if name not in profiles():
        if name:
            print(f"warning: unknown profile {name!r} for {deck.slug}, "
                  f"using built-in defaults", file=sys.stderr)
        return DeckConfig(deck=deck, profile=name or "unknown", raw=raw)
    return DeckConfig(deck=deck, profile=name, raw=raw,
                      profile_raw=_load_yaml(PROFILE_DIR / f"{name}.yml"))


def load_for_path(qmd: Path) -> DeckConfig | None:
    """Resolve straight from a qmd path; None if it is not a deck."""
    try:
        return load(deckpath.find(str(qmd)))
    except (deckpath.DeckNotFound, deckpath.AmbiguousDeck):
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("deck", nargs="?")
    ap.add_argument("--field")
    ap.add_argument("--list-profiles", action="store_true")
    args = ap.parse_args(argv)

    if args.list_profiles:
        print("\n".join(profiles()))
        return 0
    if not args.deck:
        ap.error("a deck name is required unless --list-profiles is given")

    try:
        cfg = load(deckpath.find(args.deck))
        d = cfg.as_dict()
    except (deckpath.DeckNotFound, deckpath.AmbiguousDeck, ConfigError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.field:
        if args.field not in d:
            print(f"error: unknown field {args.field!r}. "
                  f"Known: {', '.join(d)}", file=sys.stderr)
            return 1
        print(d[args.field])
    else:
        print(json.dumps(d, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
