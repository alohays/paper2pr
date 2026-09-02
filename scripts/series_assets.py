#!/usr/bin/env python3
"""Build a course series' lock file and images from its series yml.

A course is declared once, in Quarto/lectures/_series/<course>.yml (schema in
that file's header). The shared include slides every lecture of the series
carries (Quarto/lectures/_series/<course>/*.qmd) read nothing from the yml
directly: this script turns the yml into a JSON lock and a few images, and
the Lua shortcodes in Quarto/_filters/series.lua read the lock. The same
manifest -> lock -> shortcode pattern as the videos (media_prep.py ->
videos.json -> video-card.lua), for the same reason: the slide never carries
a fact that can drift from the source.

What it writes, all under Figures/lectures/_series/<course>/:

    series.json          the lock: everything in the yml plus, per session,
                         `week` ("W02"), `short_date` ("Sep 4") and, for
                         lecture/guest/keynote/dgist sessions, `prior_index`
                         (the nearest earlier session that is not a holiday
                         or exam week; a guest or DGIST session counts)
    qr-qa.png            the question-wall QR (qrencode -s 12 -m 2)
    qr-qa.svg            the same code as SVG, so the slide can scale it
    semester-map.svg     the semester timeline, nothing highlighted
    semester-map-wNN.svg one per session, that session ringed as "today"

The map is one horizontal timeline in a 1100x300 viewBox, drawn for the
student who wants to know when the talks are: a month band (AUG SEP ...,
faint rules between months), a baseline, one mark per session, evenly
spaced. Only the talks (lecture / guest / keynote) print a date ("Sep 4",
23 px bold); their kind is the mark, not a word: filled navy dot, navy dot
with a white core for a guest, gold diamond for the keynote. The quiet
weeks are small marks (hollow navy for a DGIST-arranged session, grey for
holiday and exam weeks) with one 15 px muted tag under the line ("DGIST",
"holiday", "report", "essay"). A legend row at the bottom names the marks.
No session titles (they are said aloud, never memorised) and no presenter
names. Sixteen slots on 1100 units leave about 64 units of pitch and a
23 px "Sep 11" is about 69 units wide, so a talk date moves to a far row
(with a hairline down to its dot) only when the talk right before it is
adjacent and on the near row; map_layout() checks with a width estimate
that no two texts of one row come closer than ROW_GAP and raises a loud
SeriesError otherwise. The highlighted session adds a gold ring and a bold
"today" tag in the theme's text gold (the colour binds the tag to the ring):
under the dot for a talk, where a tag would go, above the line for a quiet
week that already has its tag there. Text is fill #1a1a1a (muted #5a5a5a for the band, the
quiet tags and the legend), font-family inherit; the SVG is inlined into
the slide by the semester-map shortcode, so the theme font applies.
Nothing in the output depends on the clock, so a re-run on an unchanged yml
writes byte-identical files, and --check compares the tree against a fresh
in-memory render (never mtimes: a clone or checkout lands the yml and the
figures in any order, and a comment-only edit to the yml changes no output).

Usage:
    python3 scripts/series_assets.py dgist-2026f            # (re)build
    python3 scripts/series_assets.py dgist-2026f --check    # verify, exit 1 if stale
                                                          # (content, not mtimes)
    python3 scripts/series_assets.py --list

Library:
    from series_assets import load_series, derive, map_layout, semester_map_svg
    from series_assets import series_yml, lock_path, figure_dir, load_lock_or_yml
    from series_assets import build, check, expected_contents, render_qr
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import minyaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SERIES_DIR = REPO_ROOT / "Quarto" / "lectures" / "_series"
FIGURE_ROOT = REPO_ROOT / "Figures" / "lectures" / "_series"

KINDS = ("lecture", "guest", "keynote", "dgist", "holiday", "exam")
TITLED = ("lecture", "guest", "keynote")        # filled dot, bold date, navy tag
SKIPPED_FOR_PRIOR = ("holiday", "exam")          # never "the previous session"
KIND_TAG = {"lecture": "Lecture", "guest": "Guest", "keynote": "Keynote",
            "dgist": "DGIST", "holiday": "holiday"}
EXAM_TAG_DEFAULT = "exam"                        # overridden per session by `tag:`
# Monday = 0, as datetime.date.weekday() counts. `meets_on:` in the series yml
# names the day (or days) the course meets; the constant here only turns the
# names into numbers. It used to be a single module-level WEEKDAY = 4, which
# made "the course meets on Fridays" a property of the repo rather than of a
# course: a second course could not be declared at all (aSSIST runs Sat 11/28
# to Fri 12/11, and validate() rejected its first session outright).
WEEKDAYS = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6}

SCALAR_FIELDS = ("course", "code", "term", "institution", "room", "time",
                 "instructor", "co_instructor", "course_page", "lms_note")
# Everything else a series yml may say at the top level. A key outside both
# sets is a typo, and a silently ignored `meets_of:` is a weekday check that
# quietly never runs.
STRUCTURED_FIELDS = ("qa_tool", "rules", "notation", "sessions", "meets_on")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# ---- map geometry (viewBox units) -------------------------------------------
MAP_W, MAP_H = 1100, 300
MAP_MARGIN = 70             # x of the first dot; the last sits at MAP_W - MAP_MARGIN
# Sixteen slots on 1100 leave about 64 units of pitch. Only the talks
# (lecture / guest / keynote) print a date, at 23 px about 69 units wide, so
# a date sits on the near row unless the talk right before it is adjacent
# and already there; then it takes the far row, with a hairline down to its
# dot (Sep 11 above Sep 4; Nov 27 between Nov 20 and Dec 4). The quiet weeks
# print one small tag on a single row under the line; the widest neighbours
# ("holiday" beside "DGIST") clear the pitch at 15 px. The talk kinds are
# told apart by the mark, not by a word: filled navy dot, navy dot with a
# white core (guest), gold diamond (keynote); the legend says which is which.
Y_MONTH = 30                # month band baseline (AUG SEP OCT ...)
Y_DATE_ROWS = (124, 92)     # talk-date baselines: row 0 near the line, row 1 far
Y_LINE = 176                # the timeline
Y_QUIET = 208               # quiet-week tag baseline
Y_LEGEND = 272              # legend baseline
TODAY_LIFT = 30             # a highlighted quiet week: "today" this far above the near date row
DOT_R = 9                   # talk mark
DOT_R_DGIST = 5.5           # hollow navy
DOT_R_QUIET = 4.5           # grey
RING_R = 16
RING_W = 3.5
FONT_DATE, FONT_MONTH, FONT_QUIET, FONT_LEGEND, FONT_TODAY = 23, 16, 15, 16, 17
FONT_TAG = FONT_QUIET       # the name older callers use
NAVY, GOLD, GREY, INK, MUTED = "#012169", "#B9975B", "#aab4c8", "#1a1a1a", "#5a5a5a"
GOLD_TEXT = "#9A7B3F"       # the theme's text gold: #B9975B on white fails contrast
RULE = "#e3e7ee"            # month separators and the far-row date hairlines

# Width estimate for the overlap assertion: half the font size per character
# (Source Sans Pro measures about 0.45 em on these short strings; 0.5 keeps
# slack for the fallback fonts). map_layout() fails loudly when two texts of
# one row would come closer than ROW_GAP under this estimate.
CHAR_EM = 0.5
ROW_GAP = 8


class SeriesError(Exception):
    """The series yml is wrong, or cannot be drawn. Always loud."""


# ---- paths ------------------------------------------------------------------

def series_yml(course: str) -> Path:
    return SERIES_DIR / f"{course}.yml"


def figure_dir(course: str) -> Path:
    return FIGURE_ROOT / course


def lock_path(course: str) -> Path:
    return figure_dir(course) / "series.json"


def courses() -> list[str]:
    if not SERIES_DIR.is_dir():
        return []
    return sorted(p.stem for p in SERIES_DIR.glob("*.yml"))


# ---- loading and validation -------------------------------------------------

def _text(value, where: str, key: str, required: bool = True) -> str:
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise SeriesError(f"{where}: {key} is required")
        return ""
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise SeriesError(f"{where}: {key} must be a string, got {value!r}")
    return str(value).strip()


def parse_date(value, where: str) -> dt.date:
    s = _text(value, where, "date")
    try:
        d = dt.date.fromisoformat(s)
    except ValueError:
        raise SeriesError(f"{where}: date must be YYYY-MM-DD, got {s!r}")
    if len(s) != 10:
        raise SeriesError(f"{where}: date must be YYYY-MM-DD, got {s!r}")
    return d


def validate(data: dict, name: str = "<series>") -> dict:
    """Check the yml's shape and values; return a normalised copy."""
    if not isinstance(data, dict):
        raise SeriesError(f"{name}: expected a mapping at the top level")
    unknown_top = sorted(set(data) - set(SCALAR_FIELDS) - set(STRUCTURED_FIELDS))
    if unknown_top:
        raise SeriesError(f"{name}: unknown top-level key(s): "
                          f"{', '.join(unknown_top)}")
    out: dict = {}
    for key in SCALAR_FIELDS:
        out[key] = _text(data.get(key), name, key)

    qa = data.get("qa_tool")
    if not isinstance(qa, dict):
        raise SeriesError(f"{name}: qa_tool must be a mapping (name, url, code, note)")
    # The code is an opaque identifier the QR slide prints verbatim, so it is
    # written as a string even when it happens to be digits. minyaml already
    # refuses `0123`; this catches `code: 1234`, which would round-trip
    # through int() looking fine and then lose any padding it ever gains.
    if qa.get("code") is not None and not isinstance(qa["code"], str):
        raise SeriesError(
            f"{name}: qa_tool.code must be quoted -- it is an identifier the "
            f"slide prints as written, not a number (got {qa['code']!r})")
    out["qa_tool"] = {
        "name": _text(qa.get("name"), name, "qa_tool.name"),
        "url": _text(qa.get("url"), name, "qa_tool.url"),
        "code": _text(qa.get("code"), name, "qa_tool.code"),
        "note": _text(qa.get("note"), name, "qa_tool.note", required=False),
    }
    if not out["qa_tool"]["url"].startswith(("http://", "https://")):
        raise SeriesError(f"{name}: qa_tool.url must be an http(s) URL")

    rules = data.get("rules")
    if not isinstance(rules, list) or not rules:
        raise SeriesError(f"{name}: rules must be a non-empty list of lines")
    out["rules"] = [_text(r, name, "rules[]") for r in rules]

    notation = data.get("notation")
    if not isinstance(notation, dict):
        raise SeriesError(f"{name}: notation must be a mapping (policy, note)")
    out["notation"] = {
        "policy": _text(notation.get("policy"), name, "notation.policy"),
        "note": _text(notation.get("note"), name, "notation.note", required=False),
    }

    # Which weekday(s) the course meets on. Optional: a weekly course names
    # its day and gets a typo check for free ("2026-09-05 is a Saturday"); an
    # intensive block that runs on whatever days the room was free omits it
    # and is only held to unique, increasing dates.
    meets_raw = data.get("meets_on")
    if meets_raw is None or meets_raw == "":
        meets_on: list[str] = []
    elif isinstance(meets_raw, str):
        meets_on = [meets_raw]
    elif isinstance(meets_raw, list):
        meets_on = [_text(d, name, "meets_on[]") for d in meets_raw]
    else:
        raise SeriesError(
            f"{name}: meets_on must be a weekday name or a list of them, "
            f"got {meets_raw!r}")
    meets_on = [d.strip().lower() for d in meets_on]
    unknown_days = [d for d in meets_on if d not in WEEKDAYS]
    if unknown_days:
        raise SeriesError(
            f"{name}: meets_on: {', '.join(unknown_days)} is not a weekday "
            f"({', '.join(WEEKDAYS)})")
    out["meets_on"] = meets_on
    allowed_weekdays = {WEEKDAYS[d] for d in meets_on}

    sessions = data.get("sessions")
    if not isinstance(sessions, list) or not sessions:
        raise SeriesError(f"{name}: sessions must be a non-empty list")
    seen_idx: set[int] = set()
    seen_deck: dict[str, int] = {}
    out_sessions = []
    for n, s in enumerate(sessions, 1):
        where = f"{name}: sessions[{n}]"
        if not isinstance(s, dict):
            raise SeriesError(f"{where}: each session is a mapping")
        unknown = sorted(set(s) - {"index", "date", "kind", "title", "tag",
                                   "presenter", "deck", "remote", "tentative"})
        if unknown:
            raise SeriesError(f"{where}: unknown key(s) {', '.join(unknown)}")
        idx = s.get("index")
        if isinstance(idx, bool) or not isinstance(idx, int) or idx < 1:
            raise SeriesError(f"{where}: index must be a positive integer")
        if idx in seen_idx:
            raise SeriesError(f"{where}: duplicate index {idx}")
        seen_idx.add(idx)
        date = parse_date(s.get("date"), where)
        if allowed_weekdays and date.weekday() not in allowed_weekdays:
            raise SeriesError(
                f"{where}: {date.isoformat()} is a {date.strftime('%A')}, "
                f"and meets_on says {', '.join(meets_on)}")
        kind = _text(s.get("kind"), where, "kind")
        if kind not in KINDS:
            raise SeriesError(f"{where}: kind must be one of {', '.join(KINDS)}, got {kind!r}")
        title = _text(s.get("title"), where, "title")
        presenter = _text(s.get("presenter"), where, "presenter", required=False)
        deck = _text(s.get("deck"), where, "deck", required=False)
        tag = _text(s.get("tag"), where, "tag", required=False)
        if tag and len(tag) > 12:
            raise SeriesError(
                f"{where}: tag {tag!r} is too long for the map "
                f"(12 characters; it sits under a dot)")
        if deck:
            if deck in seen_deck:
                raise SeriesError(
                    f"{where}: deck {deck!r} is already session {seen_deck[deck]}")
            seen_deck[deck] = idx
        for flag in ("remote", "tentative"):
            v = s.get(flag, False)
            if v is None:
                v = False
            if not isinstance(v, bool):
                raise SeriesError(f"{where}: {flag} must be true or false")
        out_sessions.append({
            "index": idx,
            "date": date.isoformat(),
            "kind": kind,
            "title": title,
            "tag": tag,
            "presenter": presenter,
            "deck": deck,
            "remote": bool(s.get("remote") or False),
            "tentative": bool(s.get("tentative") or False),
        })
    out_sessions.sort(key=lambda x: x["index"])
    expected = list(range(1, len(out_sessions) + 1))
    got = [x["index"] for x in out_sessions]
    if got != expected:
        raise SeriesError(
            f"{name}: session indices must be 1..{len(out_sessions)} with no gap, got {got}")
    dates = [x["date"] for x in out_sessions]
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise SeriesError(f"{name}: session dates must increase with the index")
    out["sessions"] = out_sessions
    return out


def load_series(path: Path) -> dict:
    """Read and validate a series yml. Raises SeriesError."""
    path = Path(path)
    if not path.exists():
        raise SeriesError(f"no series file at {path}")
    try:
        data = minyaml.load_path(path)
    except minyaml.MinYamlError as e:
        raise SeriesError(str(e)) from e
    return validate(data, str(path))


# ---- derived fields ---------------------------------------------------------

def week_label(index: int) -> str:
    return f"W{int(index):02d}"


def short_date(iso: str) -> str:
    d = dt.date.fromisoformat(iso)
    return f"{MONTHS[d.month - 1]} {d.day}"


def prior_index(sessions: list[dict], index: int):
    """The nearest earlier session that is not a holiday or exam week, or
    None. Only meaningful for a session that is itself a teaching slot."""
    by_idx = {s["index"]: s for s in sessions}
    me = by_idx[index]
    if me["kind"] in SKIPPED_FOR_PRIOR:
        return None
    for i in range(index - 1, 0, -1):
        s = by_idx.get(i)
        if s and s["kind"] not in SKIPPED_FOR_PRIOR:
            return i
    return None


def derive(series: dict) -> dict:
    """The lock content: the validated yml plus the derived fields."""
    out = json.loads(json.dumps(series))   # deep copy, JSON-shaped
    for s in out["sessions"]:
        s["week"] = week_label(s["index"])
        s["short_date"] = short_date(s["date"])
        s["prior_index"] = prior_index(out["sessions"], s["index"])
    return out


def session_by_index(series: dict, index: int) -> dict | None:
    for s in series["sessions"]:
        if s["index"] == index:
            return s
    return None


def session_by_deck(series: dict, deck: str) -> dict | None:
    for s in series["sessions"]:
        if s.get("deck") and s["deck"] == deck:
            return s
    return None


def load_lock_or_yml(course: str) -> dict:
    """The lock when it exists, else the derived yml (same shape)."""
    lock = lock_path(course)
    if lock.exists():
        try:
            return json.loads(lock.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise SeriesError(f"{lock}: not a series.json written by series_assets.py ({e})")
    return derive(load_series(series_yml(course)))


# ---- semester map -----------------------------------------------------------

def dot_x(n_sessions: int, index: int) -> float:
    step = (MAP_W - 2 * MAP_MARGIN) / max(n_sessions - 1, 1)
    return MAP_MARGIN + (index - 1) * step


def kind_tag(session: dict) -> str:
    """The one short tag printed under a session's dot.

    A session may override it with `tag:` in the yml. That is how the DGIST
    course prints "report" in its midterm week and "essay" in its final one;
    the mapping used to be `{8: "report", 16: "essay"}` in this file, which
    is one course's academic calendar written into the tool.
    """
    if session.get("tag"):
        return str(session["tag"])
    kind = session["kind"]
    if kind == "exam":
        return EXAM_TAG_DEFAULT
    return KIND_TAG[kind]


def text_width(text: str, font_size: float) -> float:
    """Estimated width of a map text in viewBox units (CHAR_EM per char)."""
    return len(text) * font_size * CHAR_EM


def _assert_row_clear(row_name: str, entries: list[tuple[float, float, str]]):
    """entries = (x, estimated width, what) of every text on one row, any
    order. A pair closer than ROW_GAP is a loud error, never a silent
    overlap on the slide."""
    placed = sorted(entries)
    for (xa, wa, a), (xb, wb, b) in zip(placed, placed[1:]):
        gap = (xb - wb / 2) - (xa + wa / 2)
        if gap < ROW_GAP:
            raise SeriesError(
                f"semester map: {a} and {b} overlap on the {row_name} row "
                f"(estimated gap {gap:.0f} < {ROW_GAP} viewBox units)")


def map_layout(series: dict) -> dict:
    """Where every session's marks go. Returns {index: item}; an item has x,
    date ("Sep 4"), tag ("DGIST" / "holiday" / "report" ...), month ("Sep"),
    titled (a talk: lecture / guest / keynote), and either date_row (talks:
    0 near the line, 1 far, with a hairline down to the dot) or tag_row
    (quiet weeks: always 0). A talk's date goes to the far row only when the
    talk right before it is adjacent and already on the near row, so two
    dates never touch and the far row stays rare. Raises SeriesError when two
    texts of one row would overlap under the width estimate."""
    sessions = sorted(series["sessions"], key=lambda s: s["index"])
    n = len(sessions)
    items: dict[int, dict] = {}
    prev_talk = None
    for s in sessions:
        idx = s["index"]
        titled = s["kind"] in TITLED
        it = {
            "index": idx, "kind": s["kind"], "x": dot_x(n, idx),
            "date": short_date(s["date"]), "tag": kind_tag(s),
            "month": MONTHS[int(s["date"][5:7]) - 1],
            "titled": titled, "tag_size": FONT_QUIET,
            "date_row": None, "tag_row": None,
        }
        if titled:
            row = 0
            if (prev_talk is not None and prev_talk["index"] == idx - 1
                    and prev_talk["date_row"] == 0):
                row = 1
            it["date_row"] = row
            prev_talk = it
        else:
            it["tag_row"] = 0
        items[idx] = it
    for row in (0, 1):
        _assert_row_clear(
            f"date {row}",
            [(it["x"], text_width(it["date"], FONT_DATE), f"date {it['date']!r}")
             for it in items.values() if it["date_row"] == row])
    _assert_row_clear(
        "tag",
        [(it["x"], text_width(it["tag"], it["tag_size"]), f"tag {it['tag']!r}")
         for it in items.values() if it["tag_row"] == 0])
    return items


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _dot(kind: str, x: float, y: float, r_scale: float = 1.0, cls: str = "") -> str:
    """The mark for a session kind (also drawn in the legend at r_scale)."""
    xs = f"{x:.1f}"
    c = f' class="{cls}"' if cls else ""
    if kind == "lecture":
        return f'<circle{c} cx="{xs}" cy="{y}" r="{DOT_R * r_scale:.1f}" fill="{NAVY}"/>'
    if kind == "guest":
        return (f'<circle{c} cx="{xs}" cy="{y}" r="{DOT_R * r_scale:.1f}" fill="{NAVY}"/>'
                f'<circle cx="{xs}" cy="{y}" r="{3.5 * r_scale:.1f}" fill="#fff"/>')
    if kind == "keynote":
        h = DOT_R * r_scale * 0.9
        return (f'<rect{c} x="{x - h:.1f}" y="{y - h:.1f}" width="{2 * h:.1f}" '
                f'height="{2 * h:.1f}" fill="{GOLD}" transform="rotate(45 {xs} {y})"/>')
    if kind == "dgist":
        return (f'<circle{c} cx="{xs}" cy="{y}" r="{DOT_R_DGIST * r_scale:.1f}" fill="#fff" '
                f'stroke="{NAVY}" stroke-width="2"/>')
    return f'<circle{c} cx="{xs}" cy="{y}" r="{DOT_R_QUIET * r_scale:.1f}" fill="{GREY}"/>'


def _legend_entries(layout: dict) -> list[tuple[str, str]]:
    """(kind, label) pairs for the legend, only for kinds the course has.
    The quiet label joins the quiet weeks' own tags ("holiday / report /
    essay week"), so a course's `tag:` overrides are explained where they
    are printed."""
    kinds = [it["kind"] for it in sorted(layout.values(), key=lambda i: i["index"])]
    out = []
    for kind, label in (("lecture", "Lecture"), ("guest", "Guest lecture"),
                        ("keynote", "Keynote")):
        if kind in kinds:
            out.append((kind, label))
    if "dgist" in kinds:
        out.append(("dgist", f"{KIND_TAG['dgist']} session"))
    quiet = []
    for it in sorted(layout.values(), key=lambda i: i["index"]):
        if it["kind"] in ("holiday", "exam") and it["tag"] not in quiet:
            quiet.append(it["tag"])
    if quiet:
        out.append(("quiet", " / ".join(quiet) + " week"))
    return out


def semester_map_svg(series: dict, highlight: int | None = None,
                     layout: dict | None = None) -> str:
    """The map as an SVG document (no XML prolog, so it inlines as is)."""
    layout = layout or map_layout(series)
    n = len(layout)
    if highlight is not None and highlight not in layout:
        raise SeriesError(f"semester map: no session {highlight} to highlight")
    title = (f"Semester timeline, week {highlight:02d} highlighted"
             if highlight is not None else "Semester timeline")
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MAP_W} {MAP_H}" '
        f'class="semester-map-svg" role="img" aria-label="{_esc(title)}" '
        f'style="font-family:inherit">',
        f'<title>{_esc(title)}</title>',
    ]
    # Month band: one label per month, centred over its sessions, and a
    # faint rule between months.
    months: list[tuple[str, list[float]]] = []
    for idx in sorted(layout):
        it = layout[idx]
        if months and months[-1][0] == it["month"]:
            months[-1][1].append(it["x"])
        else:
            months.append((it["month"], [it["x"]]))
    for name, xs in months:
        cx = sum(xs) / len(xs)
        out.append(f'<text x="{cx:.1f}" y="{Y_MONTH}" font-size="{FONT_MONTH}" '
                   f'font-weight="600" letter-spacing="2" text-anchor="middle" '
                   f'fill="{MUTED}" class="month">{_esc(name.upper())}</text>')
    for (_, xa), (_, xb) in zip(months, months[1:]):
        mx = (max(xa) + min(xb)) / 2
        out.append(f'<line x1="{mx:.1f}" y1="{Y_MONTH + 16}" x2="{mx:.1f}" '
                   f'y2="{Y_QUIET + 18}" stroke="{RULE}" stroke-width="1.5" class="month-rule"/>')
    out.append(f'<line x1="{dot_x(n, 1):.1f}" y1="{Y_LINE}" x2="{dot_x(n, n):.1f}" '
               f'y2="{Y_LINE}" stroke="{GREY}" stroke-width="2" class="baseline"/>')
    for idx in sorted(layout):
        it = layout[idx]
        kind = it["kind"]
        x = it["x"]
        xs = f"{x:.1f}"
        out.append(_dot(kind, x, Y_LINE, cls="dot"))
        if highlight == idx:
            out.append(f'<circle cx="{xs}" cy="{Y_LINE}" r="{RING_R}" fill="none" '
                       f'stroke="{GOLD}" stroke-width="{RING_W}" class="today-ring"/>')
            # A talk has no tag under its dot, so "today" goes there, where a
            # date on the far row next door cannot crowd it; a quiet week
            # keeps its own tag and takes "today" above the line instead.
            y_today = Y_QUIET if it["titled"] else Y_DATE_ROWS[0] - TODAY_LIFT
            out.append(f'<text x="{xs}" y="{y_today}" '
                       f'font-size="{FONT_TODAY}" font-weight="700" text-anchor="middle" '
                       f'fill="{GOLD_TEXT}" class="today-tag">today</text>')
        if it["titled"]:
            y = Y_DATE_ROWS[it["date_row"]]
            if it["date_row"] == 1:
                out.append(f'<line x1="{xs}" y1="{y + 8}" x2="{xs}" y2="{Y_LINE - RING_R + 2}" '
                           f'stroke="{RULE}" stroke-width="1.5" class="date-rule"/>')
            out.append(f'<text x="{xs}" y="{y}" font-size="{FONT_DATE}" font-weight="700" '
                       f'text-anchor="middle" fill="{INK}" class="date">{_esc(it["date"])}</text>')
        else:
            out.append(f'<text x="{xs}" y="{Y_QUIET}" font-size="{it["tag_size"]}" '
                       f'text-anchor="middle" fill="{MUTED}" class="tag">'
                       f'{_esc(it["tag"])}</text>')
    # Legend, centred: mark, label, gap.
    entries = _legend_entries(layout)
    widths = [24 + text_width(label, FONT_LEGEND) for _, label in entries]
    gap = 28
    x = (MAP_W - (sum(widths) + gap * (len(entries) - 1))) / 2
    cy = Y_LEGEND - 5
    for (kind, label), w in zip(entries, widths):
        out.append(_dot(kind, x + 8, cy, r_scale=0.78))
        out.append(f'<text x="{x + 24:.1f}" y="{Y_LEGEND}" font-size="{FONT_LEGEND}" '
                   f'fill="{MUTED}" class="legend">{_esc(label)}</text>')
        x += w + gap
    out.append("</svg>")
    return "\n".join(out) + "\n"


# ---- QR ---------------------------------------------------------------------

def render_qr(url: str) -> dict[str, bytes]:
    """Run qrencode into a scratch directory and return the bytes the two QR
    files should hold ({"qr-qa.png": ..., "qr-qa.svg": ...}). qrencode writes
    no timestamp, so the same url gives the same bytes every time; build()
    and check() both go through here so the on-disk files can be compared
    against a fresh render instead of against the clock."""
    exe = shutil.which("qrencode")
    if not exe:
        raise SeriesError("qrencode is not on PATH (brew install qrencode)")
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "qr-qa.png"
        svg = Path(td) / "qr-qa.svg"
        subprocess.run([exe, "-s", "12", "-m", "2", "-o", str(png), url], check=True)
        subprocess.run([exe, "-t", "SVG", "-m", "2", "--rle", "-o", str(svg), url], check=True)
        # Scaled to 420 px the module grid lands on fractional pixels and Chrome
        # anti-aliases a hairline seam between every row of rects; crispEdges
        # snaps them (seen on the first fixture render, 2026-08-19).
        text = svg.read_text(encoding="utf-8")
        if 'shape-rendering="crispEdges"' not in text:
            text = text.replace("<svg ", '<svg shape-rendering="crispEdges" ', 1)
        return {"qr-qa.png": png.read_bytes(), "qr-qa.svg": text.encode("utf-8")}


# ---- build / check ----------------------------------------------------------

def expected_contents(course: str, series: dict | None = None,
                      with_qr: bool = True) -> dict[Path, bytes]:
    """Every file the build owns, mapped to the bytes it should hold, derived
    from the yml alone. build() writes these; check() compares the tree
    against them (content, not mtimes: a fresh clone or checkout lands the
    yml and the figures in any order, and a comment-only edit to the yml
    changes nothing here, so the clock says nothing about staleness).
    with_qr=False leaves the two qrencode outputs out (for hosts without
    qrencode; check() then only tests that they exist)."""
    if series is None:
        series = load_series(series_yml(course))
    d = figure_dir(course)
    lock = derive(series)
    out: dict[Path, bytes] = {}
    out[lock_path(course)] = (json.dumps(lock, indent=2, sort_keys=True, ensure_ascii=False)
                              + "\n").encode("utf-8")
    layout = map_layout(series)
    out[d / "semester-map.svg"] = semester_map_svg(series, None, layout).encode("utf-8")
    for s in series["sessions"]:
        p = d / f"semester-map-w{s['index']:02d}.svg"
        out[p] = semester_map_svg(series, s["index"], layout).encode("utf-8")
    if with_qr:
        for name, data in render_qr(series["qa_tool"]["url"]).items():
            out[d / name] = data
    return out


def _write_if_changed(path: Path, data: bytes) -> bool:
    """Write only when the bytes differ. Nothing downstream reads mtimes
    (check() compares content), so an unchanged re-run leaves the tree
    untouched and git sees no churn."""
    if path.exists() and path.read_bytes() == data:
        return False
    path.write_bytes(data)
    return True


def build(course: str, quiet: bool = False) -> list[Path]:
    yml = series_yml(course)
    series = load_series(yml)
    out_dir = figure_dir(course)
    out_dir.mkdir(parents=True, exist_ok=True)
    contents = expected_contents(course, series)
    written: list[Path] = []
    for path, data in contents.items():
        _write_if_changed(path, data)
        written.append(path)
    if not quiet:
        rel = out_dir.relative_to(REPO_ROOT)
        print(f"{course}: {len(series['sessions'])} sessions -> {rel}/ "
              f"({len(written)} files)")
        if "PLACEHOLDER" in series["qa_tool"]["url"] or series["qa_tool"]["code"] == "PLACEHOLDER":
            print(f"  note: qa_tool is still a PLACEHOLDER; {series['qa_tool']['note']}")
    return written


def expected_files(course: str, series: dict) -> list[Path]:
    d = figure_dir(course)
    files = [lock_path(course), d / "semester-map.svg", d / "qr-qa.png", d / "qr-qa.svg"]
    files += [d / f"semester-map-w{s['index']:02d}.svg" for s in series["sessions"]]
    return files


def check(course: str) -> list[str]:
    """Problems with the built assets (empty list = fine). A file is a
    problem when it is missing or when its bytes differ from what the yml
    produces today (the lock additionally when it is not JSON). Timestamps
    are not consulted. Without qrencode the two QR files are only checked
    for existence (main() prints a note)."""
    yml = series_yml(course)
    series = load_series(yml)
    problems = []
    have_qr = shutil.which("qrencode") is not None
    contents = expected_contents(course, series, with_qr=have_qr)
    for p in expected_files(course, series):
        rel = p.relative_to(REPO_ROOT)
        if not p.exists():
            problems.append(f"missing {rel}")
            continue
        if p not in contents:          # a QR file on a host without qrencode
            continue
        if p == lock_path(course):
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                problems.append(f"{rel} is not valid JSON")
                continue
        if p.read_bytes() != contents[p]:
            problems.append(f"stale {rel} (differs from what {yml.name} produces; "
                            f"re-run series_assets.py {course})")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("course", nargs="?", help="series name, e.g. dgist-2026f")
    ap.add_argument("--check", action="store_true",
                    help="verify the lock and images exist and match what the yml produces")
    ap.add_argument("--list", action="store_true", help="list the series files")
    args = ap.parse_args(argv)

    if args.list:
        print("\n".join(courses()))
        return 0
    if not args.course:
        ap.error("a course is required unless --list is given")
    try:
        if args.check:
            problems = check(args.course)
            if not shutil.which("qrencode"):
                print("  note: qrencode is not on PATH; qr-qa.png / qr-qa.svg were only "
                      "checked for existence", file=sys.stderr)
            if problems:
                for p in problems:
                    print(f"  {p}")
                print(f"{args.course}: {len(problems)} problem(s)")
                return 1
            print(f"{args.course}: lock and images are current")
            return 0
        build(args.course)
        return 0
    except SeriesError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
