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
        --audience none --duration 60 --video-min 10 --qa-min 5 \\
        --series-index 2 --sources ../vault/research.md

    # In a course series (Quarto/lectures/_series/<series>.yml): the title and
    # date come from the series file, the name defaults to <series>-w<NN>,
    # the genre to lectures, and the stub carries the four shared include
    # slides. deck.yml gets series: / series_index:, the qmd front matter
    # series: <course> (what the series shortcodes read).
    python3 scripts/new_deck.py --series dgist-2026f --series-index 2 \\
        --audience none --duration 60 --video-min 10 --qa-min 5

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
import series_assets  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{1,63}$")

AUDIENCE_LEVELS = ("none", "practitioner", "expert")
DELIVERY = ("in-person", "remote", "hybrid")
# Publishing is opt-out rather than an interview answer. The scaffold omits
# `publish`, so a deck publishes by default. Authors hosting it elsewhere may
# add `publish: false` to deck.yml; the source stays public and directly
# renderable, but the Paper2PR Pages pipeline leaves the deck out.


def die(msg: str):
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


# Everything the answer set may contain. An unrecognised key is a typo, and
# a typo here is invisible: `audiance: none` would leave audience at its
# default and write `assumes: practitioner` into the config for a room of
# first-years, which is precisely the premise the interview exists to pin
# down. Reject it instead.
ANSWER_KEYS = {
    "name", "genre", "profile", "title", "subtitle", "date",
    "audience", "audience_size", "duration", "video_min", "qa_min",
    "delivery", "slide_lang", "notes_lang", "series", "series_index", "prior",
    "sources",
}


def validate(a: dict) -> dict:
    """Normalise and check the answers, failing on anything ambiguous."""
    unknown = sorted(set(a) - ANSWER_KEYS)
    if unknown:
        die(f"unrecognised answer key(s): {', '.join(unknown)}. "
            f"Known: {', '.join(sorted(ANSWER_KEYS))}")

    # A series resolves the session first: it supplies the default name,
    # genre, title and date, and it is checked before anything is written.
    series = str(a.get("series") or "").strip() or None
    series_index = a.get("series_index")
    session = None
    prior = None
    if series_index is not None:
        try:
            series_index = int(series_index)
        except (TypeError, ValueError):
            die("series_index must be a number")
    if series:
        try:
            data = series_assets.load_lock_or_yml(series)
        except series_assets.SeriesError as e:
            die(f"series {series!r}: {e}. Known series: "
                f"{', '.join(series_assets.courses()) or 'none'}")
        if series_index is None:
            die(f"--series {series} needs --series-index (1.."
                f"{len(data['sessions'])})")
        session = series_assets.session_by_index(data, series_index)
        if session is None:
            die(f"series_index {series_index} is not a session of {series!r} "
                f"(1..{len(data['sessions'])})")
        pi = session.get("prior_index")
        if pi is None:
            pi = series_assets.prior_index(data["sessions"], series_index)
        prior = series_assets.session_by_index(data, pi) if pi else None
        if not a.get("name"):
            a["name"] = session.get("deck") or f"{series}-w{series_index:02d}"
        if not a.get("genre"):
            a["genre"] = "lectures"
        if not a.get("title"):
            a["title"] = session["title"]
        if not a.get("date"):
            a["date"] = session["date"]

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
                  deckprofile.genre_defaults().get(genre, ""))
    if profile not in deckprofile.profiles():
        die(f"no profile for genre {genre!r}. Either pass --profile, or add "
            f"`genre_default: {genre}` to one of "
            f"{', '.join(deckprofile.profiles())} "
            f"(.claude/rules/slide-profiles/)")

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

    try:
        duration = int(a.get("duration") or 30)
    except (TypeError, ValueError):
        die("duration must be a number of minutes")

    def optional_minutes(key):
        raw_value = a.get(key)
        if raw_value in (None, ""):
            return None
        try:
            n = int(raw_value)
        except (TypeError, ValueError):
            die(f"{key} must be a number of minutes")
        if n < 0:
            die(f"{key} cannot be negative")
        return n

    video_min = optional_minutes("video_min")
    qa_min = optional_minutes("qa_min")
    if (video_min or 0) + (qa_min or 0) > duration:
        die(f"video_min + qa_min ({(video_min or 0) + (qa_min or 0)}) exceeds "
            f"duration ({duration}); there would be no time left to speak")

    sources = a.get("sources") or []
    if isinstance(sources, str):
        sources = [sources]
    if not isinstance(sources, list) or not all(
            isinstance(x, str) and x.strip() for x in sources):
        die("sources must be a list of non-empty strings (paths or URLs)")

    return {
        "name": name,
        "genre": genre,
        "profile": profile,
        "title": str(a.get("title") or name),
        "subtitle": str(a.get("subtitle") or ""),
        "audience": level,
        "audience_size": a.get("audience_size") or "",
        "duration": duration,
        "video_min": video_min,
        "qa_min": qa_min,
        "delivery": delivery,
        "slide_lang": str(a.get("slide_lang") or "en"),
        "notes_lang": str(a.get("notes_lang") or "ko"),
        "date": str(a.get("date") or ""),
        "series": series,
        "series_index": series_index,
        "session": session,
        "prior_session": prior,
        "prior": a.get("prior") or [],
        "sources": [str(x).strip() for x in sources],
    }


def deck_yml(v: dict) -> str:
    lines = [
        "# Written by /new-deck. These are the premises the deck was built on;",
        "# every downstream tool reads them from here rather than guessing.",
        "#   quality_score.py  -> bullet budget and the profile's extra checks",
        "#   the Korean gate   -> whether non-English slides are allowed here,",
        "#                        and how much Hangul an English deck may carry",
        "#   write-speaker-notes -> which language the notes are in, and the",
        "#                        speaking minutes the script is budgeted on",
        "#   slide-excellence  -> audience, delivery, sources (review context)",
        "# Changing a value here changes how the deck is graded, so change it",
        "# when the premise changes, not to make a warning go away.",
        f"profile: {v['profile']}",
        f"title: {json.dumps(v['title'])}",
    ]
    if v["subtitle"]:
        lines.append(f"subtitle: {json.dumps(v['subtitle'])}")
    lines += [
        "",
        "# audience.assumes, audience.size, audience.prior and delivery are",
        "# context for the review agents (slide-excellence reads them), not",
        "# consumed by the gate; the gate's budget and checks come from the",
        "# profile above.",
        "audience:",
        f"  assumes: {v['audience']}    # none | practitioner | expert",
    ]
    if v["audience_size"]:
        lines.append(f"  size: {json.dumps(str(v['audience_size']))}")
    if v["prior"]:
        lines.append("  prior: [" + ", ".join(str(p) for p in v["prior"]) + "]")
    lines += [
        f"delivery: {v['delivery']}    # in-person | remote | hybrid",
        "",
        "# Wall-clock minutes. video_min (clips playing without narration) and",
        "# qa_min (questions) are subtracted: the speaker-notes budget runs on",
        "# speaking_min = duration_min - video_min - qa_min.",
        f"duration_min: {v['duration']}",
    ]
    if v["video_min"] is not None:
        lines.append(f"video_min: {v['video_min']}")
    if v["qa_min"] is not None:
        lines.append(f"qa_min: {v['qa_min']}")
    lines += [
        "",
        "language:",
        f"  slides: {v['slide_lang']}",
        f"  notes: {v['notes_lang']}",
        "  # korean_allowance: <n>  -- max Hangul characters on English slides",
        "  # (term glosses, Wooclap instructions). Omit to take the profile's",
        "  # default (lecture 300, others 0). Slides declared ko are not counted.",
    ]
    if v["sources"]:
        lines += [
            "",
            "# What the fact-check agent compares the slides against: paths or",
            "# URLs. Add to it as the deck grows.",
            "sources:",
        ] + [f"  - {json.dumps(src)}" for src in v["sources"]]
    if v["series"]:
        lines += [
            "",
            "# The course series (Quarto/lectures/_series/<series>.yml) and this",
            "# deck's session in it. deckprofile.py resolves the session date,",
            "# title and the previous session from the series lock; the gate",
            "# names that session when the callback slide is missing;",
            "# build_landing.py groups the deck under the course.",
            f"series: {v['series']}",
            f"series_index: {int(v['series_index'])}",
        ]
    elif v["series_index"] is not None:
        lines += [
            "",
            "# Position in its series. 1 exempts the deck from the "
            "prior-session",
            "# callback check -- there is no previous session to call back to.",
            f"series_index: {int(v['series_index'])}",
        ]
    lines += [
        "",
        "# Two optional files next to this deck are read when they exist:",
        f"#   Quarto/{v['genre']}/{v['name']}.forbidden.txt  (one term per line;",
        "#     any hit in visible slide text is a BLOCKER at the gate)",
        f"#   Figures/{v['genre']}/{v['name']}/figures.yml  (file, source, licence,",
        "#     third_party per figure; third-party figures need their source on",
        "#     the slide)",
    ]
    return "\n".join(lines) + "\n"


def series_includes(series: str) -> tuple[str, str]:
    """The shared slides every lecture of a series carries, as include
    lines with a TODO notes block after each (notes written right after an
    include belong to the included slide). Returns (top, bottom): the
    semester map, the course rules and the ask-anytime QR go near the top,
    the Q&A QR is the very last slide."""
    def inc(name, note):
        return (f"{{{{< include _series/{series}/{name}.qmd >}}}}\n"
                "\n"
                "::: {.notes}\n"
                f"TODO: {note}\n"
                ":::\n"
                "\n")
    top = (inc("semester-map", "where today sits in the semester, in one breath")
           + inc("course-runs", "the rules, once; point at the LMS")
           + inc("ask-anytime", "show the wall; say questions are answered in the last 10 minutes"))
    bottom = inc("qa", "work through the wall; close")
    return top, bottom


def qmd_stub(v: dict) -> str:
    recap = ""
    if v["profile"] == "lecture" and (v["series_index"] or 0) != 1:
        prior = v.get("prior_session")
        if prior:
            who = f" by {prior['presenter']}" if prior.get("presenter") else ""
            week = prior.get("week") or series_assets.week_label(prior["index"])
            when = prior.get("short_date") or series_assets.short_date(prior["date"])
            hint = (f"- TODO: name where the previous session ended "
                    f"({week}, {when}: {prior['title']}{who})\n")
        else:
            hint = "- TODO: name where the previous session ended\n"
        recap = (
            "## Where we left off\n"
            "\n"
            + hint +
            "\n"
            "::: {.notes}\n"
            "TODO\n"
            ":::\n"
            "\n"
        )
    top_includes = bottom_includes = ""
    if v["series"]:
        top_includes, bottom_includes = series_includes(v["series"])
        bottom_includes = "\n" + bottom_includes.rstrip("\n") + "\n"
    sub = f'subtitle: {json.dumps(v["subtitle"])}\n' if v["subtitle"] else ""
    date = f'date: {json.dumps(v["date"])}\n' if v["date"] else ""
    # The course the series shortcodes read ({{< semester-map >}} and the
    # shared include slides look the lock up by this name).
    series = f'series: {v["series"]}\n' if v["series"] else ""
    # Canvas, centering, slide numbers, math renderer, the slide-types filter
    # and the Pretendard link come from Quarto/_quarto.yml for every deck
    # under a genre directory; only what is deck-specific is written here.
    return f"""---
title: {json.dumps(v['title'])}
{sub}author: Yunsung Lee
institute: WoRV / MaumAI
{date}{series}# Full-bleed title gradient as a reveal background (fills the viewport at any
# aspect ratio; the theme drops its own section gradient when this is set).
title-slide-attributes:
  data-background-gradient: "linear-gradient(180deg, #ffffff 0%, #E8EDF5 100%)"
format:
  revealjs:
    theme: [default, ../clean-academic.scss]
bibliography: ../../Bibliography_base.bib
---

{recap}{top_includes}## First slide

- TODO

::: {{.notes}}
TODO: the words to say, in {v['notes_lang']}. Notes never reach git -- the
clean filter strips them on the way in.
:::
{bottom_includes}"""


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
    ap.add_argument("--video-min", type=int, default=None,
                    help="minutes of the slot spent on clips (default: not written)")
    ap.add_argument("--qa-min", type=int, default=None,
                    help="minutes of the slot reserved for Q&A (default: not written)")
    ap.add_argument("--delivery", choices=DELIVERY)
    ap.add_argument("--slide-lang", default=None)
    ap.add_argument("--notes-lang", default=None)
    ap.add_argument("--series",
                    help="course series (Quarto/lectures/_series/<series>.yml); "
                         "with --series-index it prefills title, date and the "
                         "deck name <series>-w<NN>, and adds the shared slides")
    ap.add_argument("--series-index", type=int)
    ap.add_argument("--date", help="ISO date shown on the title slide")
    ap.add_argument("--prior", nargs="*", default=None,
                    help="decks or sessions the audience has already seen")
    ap.add_argument("--sources", nargs="*", default=None,
                    help="paths or URLs the fact-check agent compares against")
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

    for key in ("name", "genre", "profile", "title", "subtitle", "date",
                "audience", "duration", "video_min", "qa_min", "delivery",
                "series", "series_index", "prior", "sources"):
        val = getattr(args, key, None)
        if val is not None:
            answers[key] = val
    if args.audience_size is not None:
        answers["audience_size"] = args.audience_size
    if args.slide_lang is not None:
        answers["slide_lang"] = args.slide_lang
    if args.notes_lang is not None:
        answers["notes_lang"] = args.notes_lang

    if not answers.get("series") and (
            not answers.get("name") or not answers.get("genre")):
        die("--name and --genre are required (or supply them in --from-answers, "
            "or give --series with --series-index to derive them)")

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
