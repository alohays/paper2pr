#!/usr/bin/env python3
"""Scaffold a new deck from the answers /new-deck collected.

The interview is conversational and lives in .claude/skills/new-deck. This
script is the deterministic half: given the answers, it always produces the
same files, in the right places, with the right relative paths. Splitting it
that way means the questions can be asked however they need to be asked while
the output stays exactly reproducible.

What it writes:
    Quarto/<genre>/<name>.deck.yml      the premises, read by every downstream tool
    Quarto/<genre>/<name>.qmd           a stub with the correct theme and bib paths
    Figures/<genre>/<name>/             empty, so figure paths work immediately
    Quarto/_script/<genre>/             where the presenter script will go

Usage:
    python3 scripts/new_deck.py --name dgist-2026f-w02 --genre lectures \\
        --title "The Paradigm Shift Toward Embodied AI" \\
        --audience none --duration 60 --series-index 2

    echo '{"name": "...", "genre": "lectures", ...}' \\
        | python3 scripts/new_deck.py --from-answers -

    python3 scripts/new_deck.py --name probe --genre talks --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deckpath  # noqa: E402
import deckprofile  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{1,63}$")

AUDIENCE_LEVELS = ("none", "practitioner", "expert")
DELIVERY = ("in-person", "remote", "hybrid")
PUBLISH = ("web", "pdf-only", "private")


def die(msg: str):
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def validate(a: dict) -> dict:
    """Normalise and check the answers, failing on anything ambiguous."""
    name = str(a.get("name", "")).strip()
    if not NAME_RE.match(name):
        die(f"deck name {name!r} must start with a letter and use only "
            f"letters, digits, dot, dash, underscore")

    genre = str(a.get("genre", "")).strip()
    known_genres = deckpath.genres()
    if genre not in known_genres:
        die(f"unknown genre {genre!r}. Known: {', '.join(known_genres)}. "
            f"Add a line to Quarto/_genres.txt to introduce one.")

    profile = str(a.get("profile") or
                  deckprofile.GENRE_DEFAULT_PROFILE.get(genre, ""))
    if profile not in deckprofile.profiles():
        die(f"unknown profile {profile!r}. Known: "
            f"{', '.join(deckprofile.profiles())}")

    # Names key the speaker-note backups and presenter scripts, which are flat
    # within a genre but addressed by bare name everywhere else. A duplicate
    # would make `preview.sh <name>` ambiguous forever after.
    for existing in deckpath.all_decks():
        if existing.name == name:
            die(f"a deck named {name!r} already exists at {existing.slug}")

    level = str(a.get("audience", "practitioner")).strip()
    if level not in AUDIENCE_LEVELS:
        die(f"audience must be one of {', '.join(AUDIENCE_LEVELS)}")

    delivery = str(a.get("delivery", "in-person")).strip()
    if delivery not in DELIVERY:
        die(f"delivery must be one of {', '.join(DELIVERY)}")

    publish = str(a.get("publish", "web")).strip()
    if publish not in PUBLISH:
        die(f"publish must be one of {', '.join(PUBLISH)}")

    try:
        duration = int(a.get("duration") or 30)
    except (TypeError, ValueError):
        die("duration must be a number of minutes")

    return {
        "name": name,
        "genre": genre,
        "profile": profile,
        "title": str(a.get("title") or name),
        "subtitle": str(a.get("subtitle") or ""),
        "audience": level,
        "audience_size": a.get("audience_size") or "",
        "duration": duration,
        "delivery": delivery,
        "publish": publish,
        "slide_lang": str(a.get("slide_lang") or "en"),
        "notes_lang": str(a.get("notes_lang") or "ko"),
        "series_index": a.get("series_index"),
        "prior": a.get("prior") or [],
    }


def deck_yml(v: dict) -> str:
    lines = [
        "# Written by /new-deck. These are the premises the deck was built on;",
        "# every downstream tool reads them from here rather than guessing.",
        "#   quality_score.py  -> bullet budget and the profile's extra checks",
        "#   the Korean gate   -> whether non-English slides are allowed here",
        "#   write-speaker-notes -> which language the notes are in",
        "# Changing a value here changes how the deck is graded, so change it",
        "# when the premise changes, not to make a warning go away.",
        f"profile: {v['profile']}",
        f"title: {json.dumps(v['title'])}",
    ]
    if v["subtitle"]:
        lines.append(f"subtitle: {json.dumps(v['subtitle'])}")
    lines += [
        "",
        "audience:",
        f"  assumes: {v['audience']}    # none | practitioner | expert",
    ]
    if v["audience_size"]:
        lines.append(f"  size: {json.dumps(str(v['audience_size']))}")
    if v["prior"]:
        lines.append("  prior: [" + ", ".join(str(p) for p in v["prior"]) + "]")
    lines += [
        f"duration_min: {v['duration']}",
        f"delivery: {v['delivery']}    # in-person | remote | hybrid",
        f"publish: {v['publish']}    # web | pdf-only | private",
        "",
        "language:",
        f"  slides: {v['slide_lang']}",
        f"  notes: {v['notes_lang']}",
    ]
    if v["series_index"] is not None:
        lines += [
            "",
            "# Position in its series. 1 exempts the deck from the "
            "prior-session",
            "# callback check -- there is no previous session to call back to.",
            f"series_index: {int(v['series_index'])}",
        ]
    return "\n".join(lines) + "\n"


def qmd_stub(v: dict) -> str:
    recap = ""
    if v["profile"] == "lecture" and (v["series_index"] or 0) != 1:
        recap = (
            "## Where we left off\n"
            "\n"
            "- TODO: name where the previous session ended\n"
            "\n"
            "::: {.notes}\n"
            "TODO\n"
            ":::\n"
            "\n"
        )
    sub = f'subtitle: {json.dumps(v["subtitle"])}\n' if v["subtitle"] else ""
    return f"""---
title: {json.dumps(v['title'])}
{sub}author: Yunsung Lee
institute: WoRV / MaumAI
format:
  revealjs:
    theme: [default, ../clean-academic.scss]
    width: 1280
    height: 720
    center: false
    auto-stretch: false
    slideNumber: true
    html-math-method:
      method: katex
bibliography: ../../Bibliography_base.bib
---

{recap}## First slide

- TODO

::: {{.notes}}
TODO: the words to say, in {v['notes_lang']}. Notes never reach git -- the
clean filter strips them on the way in.
:::
"""


def scaffold(v: dict, dry_run: bool = False) -> list[Path]:
    deck = deckpath.Deck(name=v["name"], genre=v["genre"])
    planned = [
        (deck.config, deck_yml(v)),
        (deck.qmd, qmd_stub(v)),
        (deck.figures / ".gitkeep", ""),
    ]
    written = []
    for path, body in planned:
        if path.exists():
            die(f"{path.relative_to(REPO_ROOT)} already exists; refusing to "
                f"overwrite")
        if dry_run:
            print(f"--- {path.relative_to(REPO_ROOT)}")
            if body:
                print(body)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        written.append(path)

    if not dry_run:
        deck.script_dir.mkdir(parents=True, exist_ok=True)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--from-answers", metavar="FILE",
                    help="read a JSON object of answers ('-' for stdin)")
    ap.add_argument("--name")
    ap.add_argument("--genre")
    ap.add_argument("--profile")
    ap.add_argument("--title")
    ap.add_argument("--subtitle")
    ap.add_argument("--audience", choices=AUDIENCE_LEVELS)
    ap.add_argument("--audience-size")
    ap.add_argument("--duration", type=int)
    ap.add_argument("--delivery", choices=DELIVERY)
    ap.add_argument("--publish", choices=PUBLISH)
    ap.add_argument("--slide-lang", default=None)
    ap.add_argument("--notes-lang", default=None)
    ap.add_argument("--series-index", type=int)
    ap.add_argument("--prior", nargs="*", default=None,
                    help="decks or sessions the audience has already seen")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    if args.from_answers:
        src = sys.stdin if args.from_answers == "-" else open(args.from_answers)
        try:
            answers = json.load(src)
        except json.JSONDecodeError as e:
            die(f"could not parse the answers as JSON: {e}")
    else:
        answers = {}

    for key in ("name", "genre", "profile", "title", "subtitle", "audience",
                "duration", "delivery", "publish", "series_index", "prior"):
        val = getattr(args, key, None)
        if val is not None:
            answers[key] = val
    if args.audience_size is not None:
        answers["audience_size"] = args.audience_size
    if args.slide_lang is not None:
        answers["slide_lang"] = args.slide_lang
    if args.notes_lang is not None:
        answers["notes_lang"] = args.notes_lang

    if not answers.get("name") or not answers.get("genre"):
        die("--name and --genre are required (or supply them in --from-answers)")

    v = validate(answers)
    written = scaffold(v, dry_run=args.dry_run)

    verb = "Would create" if args.dry_run else "Created"
    print(f"{verb} {v['genre']}/{v['name']} on the {v['profile']} profile:")
    for p in written:
        print(f"  {p.relative_to(REPO_ROOT)}")
    if not args.dry_run:
        print(f"  Quarto/_script/{v['genre']}/")
        print()
        print("Next:")
        print(f"  bash scripts/preview.sh {v['name']}")
        print(f"  python3 scripts/quality_score.py "
              f"Quarto/{v['genre']}/{v['name']}.qmd --summary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
