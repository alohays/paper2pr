#!/usr/bin/env python3
"""Locate a deck's files from a bare name.

Decks live at Quarto/<genre>/<name>.qmd, and their figures, speaker-note
backups, and presenter scripts are scoped the same way. Before genres existed
every script hardcoded Quarto/<name>.qmd; now they all come through here, so
the layout is written down once instead of in seven places that drift apart.

A bare name is resolved by searching the genres in Quarto/_genres.txt. Names
are expected to be unique across genres -- if two genres claim the same name
the lookup fails loudly rather than picking one, because picking one would
silently render the wrong deck.

Also accepts an explicit "genre/name" or a path to the qmd, so callers that
already know exactly which deck they mean do not have to rely on uniqueness.

Usage as a library:
    from deckpath import find, all_decks, genres
    deck = find("DreamZero")
    deck.qmd, deck.genre, deck.figures, deck.notes_json, deck.script
    deck.config, deck.forbidden, deck.figures_manifest
    deck.videos_manifest, deck.videos_lock, deck.videos_dir, deck.release_tag

Videos (WP3) have one home per deck, next to the figures:
    Figures/<genre>/<deck>/videos.yml    the hand-written manifest (committed)
    Figures/<genre>/<deck>/videos.json   the lock file media_prep.py writes
                                         (committed; the shortcodes read it)
    Figures/<genre>/<deck>/videos/       trimmed mp4s and posters (gitignored,
                                         uploaded to the GitHub Release
                                         tagged media-<deck>)
find_media() also accepts a direct path to a videos.yml or to the directory
holding one, so a fixture outside Figures/ (Quarto/_fixtures/video/) goes
through the same media scripts. A path under Quarto/_fixtures/ gets the
release tag media-fixture-<dir>, so a fixture release can never collide with
a deck's.

Usage from the shell:
    python3 scripts/deckpath.py DreamZero              # -> Quarto/papers/DreamZero.qmd
    python3 scripts/deckpath.py DreamZero --field genre
    python3 scripts/deckpath.py --list
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
QUARTO_DIR = REPO_ROOT / "Quarto"
GENRES_FILE = QUARTO_DIR / "_genres.txt"


class DeckNotFound(Exception):
    pass


class AmbiguousDeck(Exception):
    pass


def genres() -> list[str]:
    """The publishable genres, in the order _genres.txt lists them."""
    if not GENRES_FILE.exists():
        raise DeckNotFound(f"{GENRES_FILE} is missing; it defines the layout")
    out = []
    for line in GENRES_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


@dataclass(frozen=True)
class Deck:
    name: str
    genre: str

    @property
    def qmd(self) -> Path:
        return QUARTO_DIR / self.genre / f"{self.name}.qmd"

    @property
    def html(self) -> Path:
        return QUARTO_DIR / self.genre / f"{self.name}.html"

    @property
    def files_dir(self) -> Path:
        """Where Quarto writes the deck's compiled RevealJS assets."""
        return QUARTO_DIR / self.genre / f"{self.name}_files"

    @property
    def figures(self) -> Path:
        return REPO_ROOT / "Figures" / self.genre / self.name

    @property
    def notes_json(self) -> Path:
        """Speaker-note backup. Gitignored -- notes never enter git."""
        return REPO_ROOT / ".speaker-notes" / self.genre / f"{self.name}.json"

    @property
    def script_dir(self) -> Path:
        """Presenter scripts. Gitignored, same reason."""
        return QUARTO_DIR / "_script" / self.genre

    @property
    def script(self) -> Path:
        return self.script_dir / f"{self.name}-script.md"

    @property
    def config(self) -> Path:
        """Deck config written by /new-deck: audience, length, language."""
        return QUARTO_DIR / self.genre / f"{self.name}.deck.yml"

    @property
    def forbidden(self) -> Path:
        """Per-deck forbidden-term list (one term per line). Optional: the
        quality gate only reads it when it exists."""
        return QUARTO_DIR / self.genre / f"{self.name}.forbidden.txt"

    @property
    def figures_manifest(self) -> Path:
        """Provenance of the deck's figures (file, source, licence,
        third_party). Optional, same as the forbidden list."""
        return self.figures / "figures.yml"

    @property
    def media(self) -> "MediaHome":
        """The deck's video home (manifest, lock, media dir, release tag)."""
        return MediaHome(slug=self.slug, name=self.name,
                         manifest=self.figures / "videos.yml")

    @property
    def videos_manifest(self) -> Path:
        """Figures/<genre>/<deck>/videos.yml: the hand-written clip list."""
        return self.media.manifest

    @property
    def videos_lock(self) -> Path:
        """Figures/<genre>/<deck>/videos.json: written by media_prep.py, read
        by the video-card / video-caption shortcodes and by @slug."""
        return self.media.lock

    @property
    def videos_dir(self) -> Path:
        """Figures/<genre>/<deck>/videos/: trimmed clips and posters.
        Gitignored; they live on the GitHub Release instead."""
        return self.media.videos_dir

    @property
    def release_tag(self) -> str:
        """GitHub Release tag that hosts this deck's media: media-<deck>."""
        return self.media.release_tag

    @property
    def slug(self) -> str:
        return f"{self.genre}/{self.name}"

    def __str__(self) -> str:
        return self.slug


@dataclass(frozen=True)
class MediaHome:
    """Where a deck (or a fixture) keeps its videos.yml, videos.json and the
    local media directory, and which Release tag hosts the uploads. Built by
    Deck.media for decks and by find_media() for paths."""
    slug: str            # "genre/name" for a deck, "_fixtures/video" for a fixture
    name: str            # what the release tag is built from
    manifest: Path       # .../videos.yml

    @property
    def lock(self) -> Path:
        return self.manifest.with_name("videos.json")

    @property
    def videos_dir(self) -> Path:
        return self.manifest.parent / "videos"

    @property
    def release_tag(self) -> str:
        return f"media-{self.name}"

    def __str__(self) -> str:
        return self.slug


def find_media(ref: str) -> MediaHome:
    """Resolve a deck reference (as find() does) or a path.

    A path is recognised when it exists: either a videos.yml file or a
    directory that holds one. Fixtures under Quarto/_fixtures/<dir>/ become
    slug "_fixtures/<dir>" with release tag media-fixture-<dir>; any other
    directory becomes media-<dir>. Decks keep media-<deck>.
    """
    ref = ref.strip()
    p = Path(ref)
    p = p if p.is_absolute() else (Path.cwd() / p)
    if p.is_dir() and (p / "videos.yml").exists():
        p = p / "videos.yml"
    if p.is_file() and p.name == "videos.yml":
        p = p.resolve()
        home = p.parent
        try:
            rel = home.relative_to(REPO_ROOT)
        except ValueError:
            rel = home
        if len(rel.parts) >= 2 and rel.parts[0] == "Figures" and rel.parts[1] in genres():
            # Figures/<genre>/<deck>/videos.yml: the deck itself, by path.
            if len(rel.parts) == 3:
                return Deck(name=rel.parts[2], genre=rel.parts[1]).media
        fixtures = (QUARTO_DIR / "_fixtures").resolve()
        if home.parent == fixtures:
            return MediaHome(slug=f"_fixtures/{home.name}",
                             name=f"fixture-{home.name}", manifest=p)
        return MediaHome(slug=rel.as_posix(), name=home.name, manifest=p)
    if ref.endswith("videos.yml") or (p.exists() and p.is_dir()):
        raise DeckNotFound(f"{ref}: no videos.yml there")
    if not p.exists() and Path(ref).parts[:1] in (("Quarto",), ("Figures",)):
        raise DeckNotFound(
            f"{ref}: no such path (expected a videos.yml or its directory)")
    return find(ref).media


def all_decks() -> list[Deck]:
    out = []
    for genre in genres():
        d = QUARTO_DIR / genre
        if not d.is_dir():
            continue
        for qmd in sorted(d.glob("*.qmd")):
            if "_backup" in qmd.name:
                continue
            out.append(Deck(name=qmd.stem, genre=genre))
    return out


def find(ref: str) -> Deck:
    """Resolve a bare name, a "genre/name", or a path to a qmd."""
    ref = ref.strip()
    if ref.endswith(".qmd"):
        p = Path(ref)
        p = p if p.is_absolute() else (Path.cwd() / p)
        try:
            rel = p.resolve().relative_to(QUARTO_DIR)
        except ValueError:
            raise DeckNotFound(f"{ref} is not under {QUARTO_DIR}")
        if len(rel.parts) != 2:
            raise DeckNotFound(
                f"{ref} is not at Quarto/<genre>/<name>.qmd")
        # The directory has to be a real genre. Quarto/_fixtures/ holds the
        # theme regression file, which is a qmd two levels down and would
        # otherwise resolve to a Deck in a genre that does not exist.
        if rel.parts[0] not in genres():
            raise DeckNotFound(
                f"{ref} is under {rel.parts[0]}/, which is not a genre in "
                f"Quarto/_genres.txt ({', '.join(genres())})")
        return Deck(name=rel.stem, genre=rel.parts[0])

    if "/" in ref:
        genre, _, name = ref.partition("/")
        deck = Deck(name=name, genre=genre)
        if not deck.qmd.exists():
            raise DeckNotFound(f"no deck at {deck.qmd.relative_to(REPO_ROOT)}")
        return deck

    hits = [d for d in all_decks() if d.name == ref]
    if not hits:
        known = ", ".join(d.slug for d in all_decks()) or "none"
        raise DeckNotFound(f"no deck named {ref!r}. Known decks: {known}")
    if len(hits) > 1:
        raise AmbiguousDeck(
            f"{ref!r} exists in more than one genre: "
            + ", ".join(d.slug for d in hits)
            + ". Pass genre/name to disambiguate.")
    return hits[0]


FIELDS = {
    "qmd": lambda d: d.qmd,
    "html": lambda d: d.html,
    "files-dir": lambda d: d.files_dir,
    "figures": lambda d: d.figures,
    "notes": lambda d: d.notes_json,
    "script": lambda d: d.script,
    "script-dir": lambda d: d.script_dir,
    "config": lambda d: d.config,
    "forbidden": lambda d: d.forbidden,
    "figures-manifest": lambda d: d.figures_manifest,
    "videos-manifest": lambda d: d.videos_manifest,
    "videos-lock": lambda d: d.videos_lock,
    "videos-dir": lambda d: d.videos_dir,
    "release-tag": lambda d: d.release_tag,
    "genre": lambda d: d.genre,
    "name": lambda d: d.name,
    "slug": lambda d: d.slug,
}

# The fields a MediaHome can answer; the CLI routes these through
# find_media() so that `deckpath.py Quarto/_fixtures/video --field videos-lock`
# works for a fixture as it does for a deck.
MEDIA_FIELDS = {
    "videos-manifest": lambda m: m.manifest,
    "videos-lock": lambda m: m.lock,
    "videos-dir": lambda m: m.videos_dir,
    "release-tag": lambda m: m.release_tag,
    "media-slug": lambda m: m.slug,
}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("deck", nargs="?",
                    help="bare name, genre/name, a .qmd path, or (media "
                         "fields only) a videos.yml path or its directory")
    ap.add_argument("--field", default="qmd",
                    choices=sorted(set(FIELDS) | set(MEDIA_FIELDS)),
                    help="which path or attribute to print (default: qmd)")
    ap.add_argument("--relative", action="store_true",
                    help="print paths relative to the repo root")
    ap.add_argument("--list", action="store_true", help="list every deck as genre/name")
    ap.add_argument("--genres", action="store_true", help="list the genres")
    args = ap.parse_args(argv)

    if args.genres:
        print("\n".join(genres()))
        return 0
    if args.list:
        print("\n".join(d.slug for d in all_decks()))
        return 0
    if not args.deck:
        ap.error("a deck name is required unless --list or --genres is given")

    try:
        if args.field in MEDIA_FIELDS:
            # Media fields also resolve from a videos.yml path or its
            # directory (fixtures live outside Figures/), so go through
            # find_media and read the field off the MediaHome.
            home = find_media(args.deck)
            value = MEDIA_FIELDS[args.field](home)
        else:
            deck = find(args.deck)
            value = FIELDS[args.field](deck)
    except (DeckNotFound, AmbiguousDeck) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if isinstance(value, Path) and args.relative:
        try:
            value = value.relative_to(REPO_ROOT)
        except ValueError:
            pass
    print(value)
    return 0


if __name__ == "__main__":
    sys.exit(main())
