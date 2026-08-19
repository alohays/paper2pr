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

What a deck may declare, and where each value is read from (deck config first,
then the profile, then the built-in default):

    profile                      which slide-profiles/<profile>.yml grades it
    duration_min                 wall-clock minutes the slot runs
    video_min, qa_min            minutes of the slot spent on clips and on Q&A
                                 (deck only, default 0). speaking_min is derived:
                                 max(duration_min - video_min - qa_min, 0); the
                                 speaker-notes budget is built on speaking_min
    bullets.*, checks.*          the quality-gate budget and which checks run
                                 (checks: dash_lint, attribution, forbidden_terms,
                                 level1_heading, expand_acronyms, ...)
    language.slides, .notes      which language the slides / the notes are in
    language.korean_allowance    max Hangul characters the slides may carry
                                 after the notes filter, when slides are not
                                 `ko` (deck -> profile -> 0); the Korean
                                 pre-commit gate reads it
    sources                      list of paths or URLs the fact-check agent
                                 compares the slides against (deck only, [])
    series_index                 position in a course series
    audience.*, delivery         context for the review agents, not the gate

Two optional files next to the deck are surfaced as paths when they exist:
Quarto/<genre>/<deck>.forbidden.txt (forbidden_file) and
Figures/<genre>/<deck>/figures.yml (figures_manifest; a figures.yml sitting
next to the qmd is accepted as a fallback, which is how the fixtures under
Quarto/_fixtures/ carry one).

A qmd outside the genre directories (the fixtures) resolves by path when a
<name>.deck.yml sits next to it; bare-name lookup never finds those, so a
fixture can never be mistaken for a publishable deck.

Usage as a library:
    from deckprofile import load, resolve
    cfg = load(deck)              # deck from deckpath.find(...)
    cfg = resolve("Quarto/_fixtures/gates/pass.qmd")   # deck or fixture
    cfg.bullets_max, cfg.expand_acronyms, cfg.slide_language

Usage from the shell:
    python3 scripts/deckprofile.py RoboTTT
    python3 scripts/deckprofile.py RoboTTT --field profile
    python3 scripts/deckprofile.py Quarto/lectures/w02.qmd --field korean_allowance
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
        # The WP2 gates. Profiles opt in explicitly; these are what a deck on
        # an unknown profile gets. level1_heading is "fail" everywhere because
        # a level-1 heading is a rendering defect (a vertical stack), not a
        # style choice; "off" switches it off for a deck that wants stacks.
        "dash_lint": False,
        "attribution": False,
        "forbidden_terms": True,
        "level1_heading": "fail",
    },
    "language": {"slides": "en", "notes": "ko", "korean_allowance": 0},
}

# Top-level keys, which follow the same deck-then-profile-then-default order.
TOP_DEFAULTS = {"duration_min": 30, "video_min": 0, "qa_min": 0, "sources": []}


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

    def _minutes(self, key: str) -> int:
        try:
            return int(self._top(key))
        except (TypeError, ValueError):
            raise ConfigError(
                f"{self.deck.config}: {key} must be a number of minutes, "
                f"got {self._top(key)!r}")

    @property
    def video_min(self) -> int:
        """Minutes of the slot taken by clips that play without narration."""
        return self._minutes("video_min")

    @property
    def qa_min(self) -> int:
        """Minutes of the slot reserved for questions."""
        return self._minutes("qa_min")

    @property
    def speaking_min(self) -> int:
        """Minutes the presenter actually talks: duration minus video and
        Q&A. This, not duration_min, is what the notes budget is built on;
        a 60-minute lecture with 10 minutes of clips and 5 of questions is a
        45-minute script."""
        return max(self.duration_min - self.video_min - self.qa_min, 0)

    @property
    def sources(self) -> list:
        """Paths or URLs the fact-check agent compares the slides against."""
        value = self._top("sources")
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if not isinstance(value, list):
            raise ConfigError(
                f"{self.deck.config}: sources must be a list, got {value!r}")
        return [str(v) for v in value]

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
    def dash_lint(self) -> bool:
        return bool(self._get("checks", "dash_lint"))

    @property
    def attribution(self) -> bool:
        return bool(self._get("checks", "attribution"))

    @property
    def forbidden_terms(self) -> bool:
        return bool(self._get("checks", "forbidden_terms"))

    @property
    def level1_heading(self) -> str:
        """"fail" (blocker) or "off". Anything else is read as "fail"."""
        value = str(self._get("checks", "level1_heading")).strip().lower()
        return "off" if value in ("off", "false", "no", "none") else "fail"

    @property
    def slide_language(self) -> str:
        return str(self._get("language", "slides"))

    @property
    def notes_language(self) -> str:
        return str(self._get("language", "notes"))

    @property
    def korean_allowance(self) -> int:
        """Hangul characters the slides may carry (after the notes filter)
        when they are not declared `ko`. Deck, then profile, then 0."""
        value = self._get("language", "korean_allowance")
        try:
            n = int(value)
        except (TypeError, ValueError):
            raise ConfigError(
                f"{self.deck.config}: language.korean_allowance must be a "
                f"number of characters, got {value!r}")
        return max(n, 0)

    @property
    def forbidden_file(self) -> Path | None:
        """Quarto/<genre>/<deck>.forbidden.txt when it exists, else None."""
        path = self.deck.forbidden
        return path if path.exists() else None

    @property
    def figures_manifest(self) -> Path | None:
        """Figures/<genre>/<deck>/figures.yml when it exists; failing that a
        figures.yml next to the qmd (the fixtures live outside Figures/);
        else None."""
        primary = self.deck.figures_manifest
        if primary.exists():
            return primary
        sibling = self.deck.qmd.parent / "figures.yml"
        if sibling.exists():
            return sibling
        return None

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
            "video_min": self.video_min,
            "qa_min": self.qa_min,
            "speaking_min": self.speaking_min,
            "bullets_max": self.bullets_max,
            "bullets_max_with_figure": self.bullets_max_with_figure,
            "bullets_max_two_line": self.bullets_max_two_line,
            "box_density": self.box_density,
            "max_nesting": self.max_nesting,
            "expand_acronyms": self.expand_acronyms,
            "prior_session_callback": self.prior_session_callback,
            "dash_lint": self.dash_lint,
            "attribution": self.attribution,
            "forbidden_terms": self.forbidden_terms,
            "level1_heading": self.level1_heading,
            "series_index": self.series_index,
            "slide_language": self.slide_language,
            "notes_language": self.notes_language,
            "korean_allowance": self.korean_allowance,
            "sources": self.sources,
            "forbidden_file": _rel(self.forbidden_file),
            "figures_manifest": _rel(self.figures_manifest),
        }


def _rel(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


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


def _fixture_deck(qmd: Path) -> "deckpath.Deck | None":
    """A qmd outside the genre directories with a <name>.deck.yml beside it.

    Fixtures under Quarto/_fixtures/ are graded by the same gate as real
    decks, so they need a config to select a profile -- but they must never
    resolve from a bare name, or a fixture could be rendered and published
    as if it were a deck. Path-only, config-required, and the "genre" is the
    directory below Quarto/ (e.g. "_fixtures/gates"), which keeps every path
    property of Deck pointing next to the qmd.
    """
    qmd = qmd if qmd.is_absolute() else (Path.cwd() / qmd)
    try:
        rel = qmd.resolve().relative_to(deckpath.QUARTO_DIR)
    except ValueError:
        return None
    if len(rel.parts) < 2 or not qmd.with_suffix(".deck.yml").exists():
        return None
    return deckpath.Deck(name=rel.stem, genre=rel.parent.as_posix())


def resolve(ref: str) -> DeckConfig:
    """A deck by name, genre/name or path; a fixture by path only."""
    try:
        return load(deckpath.find(ref))
    except deckpath.DeckNotFound:
        if ref.strip().endswith(".qmd"):
            fixture = _fixture_deck(Path(ref.strip()))
            if fixture is not None:
                return load(fixture)
        raise


def load_for_path(qmd: Path) -> DeckConfig | None:
    """Resolve straight from a qmd path; None if it is neither a deck nor a
    fixture with a config beside it."""
    try:
        return resolve(str(qmd))
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
        cfg = resolve(args.deck)
        d = cfg.as_dict()
    except (deckpath.DeckNotFound, deckpath.AmbiguousDeck, ConfigError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.field:
        if args.field not in d:
            print(f"error: unknown field {args.field!r}. "
                  f"Known: {', '.join(d)}", file=sys.stderr)
            return 1
        value = d[args.field]
        # Scalars print bare so shell callers can compare them; lists and
        # absent values print as JSON so they stay parseable.
        if isinstance(value, (list, dict)) or value is None:
            print(json.dumps(value))
        else:
            print(value)
    else:
        print(json.dumps(d, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
