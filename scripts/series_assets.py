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

The map is one horizontal timeline in a 1100x200 viewBox: a baseline, one dot
per session, evenly spaced. It shows only dates and short kind tags, in large
type; no session titles (they are said aloud, never memorised) and no
presenter names. Above each dot sits the short date ("Sep 4") at 26 px, bold
for lecture/guest/keynote sessions, regular and muted for the rest; below the
line one kind tag: "Lecture" (navy bold), "Guest" / "Keynote" (navy),
"DGIST" (muted) at 20 px, and "holiday" / "report" / "essay" muted at 18 px.
Sixteen slots on 1100 units leave about 64 units of pitch and a 26 px
"Sep 11" is about 78 units wide, so the dates (and the tags below, for the
same reason) alternate two rows by index parity; map_layout() checks with a
width estimate that no two texts of one row come closer than ROW_GAP and
raises a loud SeriesError otherwise. Dots are filled navy for
lecture/guest/keynote, hollow navy for DGIST-arranged sessions, grey for
holiday and exam weeks; the highlighted session adds a gold ring and, at the
very top of its column, a bold "today" tag in the theme's text gold (the
colour binds the tag to the ring). Text is fill #1a1a1a (muted #5a5a5a for
the quiet weeks), font-family inherit; the SVG is inlined into the slide by
the semester-map shortcode, so the theme font applies.
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
EXAM_TAG = {8: "report", 16: "essay"}            # fallback is "exam"
WEEKDAY = 4                                      # Friday (Monday = 0)

SCALAR_FIELDS = ("course", "code", "term", "institution", "room", "time",
                 "instructor", "co_instructor", "course_page", "lms_note")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# ---- map geometry (viewBox units) -------------------------------------------
MAP_W, MAP_H = 1100, 200
MAP_MARGIN = 70             # x of the first dot; the last sits at MAP_W - MAP_MARGIN
# Sixteen slots on 1100 leave about 64 units of pitch and a 26 px "Sep 11" is
# about 78 units wide, so a single date row would touch everywhere: dates
# alternate two rows by index parity (odd low, even high), which puts
# same-row neighbours two slots (about 128 units) apart. The 20 px kind tags
# below the line collide the same way ("Lecture" next to "holiday"), so they
# alternate the same two rows.
Y_TODAY = 26                # "today" baseline, above everything else
Y_DATE_ROWS = (96, 60)      # date baselines: row 0 (low, odd indices), row 1 (high)
Y_LINE = 126                # the timeline
Y_TAG_ROWS = (158, 186)     # tag baselines: row 0 (near the line, odd), row 1 (low)
DOT_R = 7
RING_R = 13
RING_W = 4
FONT_DATE, FONT_TAG, FONT_TAG_SMALL, FONT_TODAY = 26, 20, 18, 20
NAVY, GOLD, GREY, INK, MUTED = "#012169", "#B9975B", "#aab4c8", "#1a1a1a", "#5a5a5a"
GOLD_TEXT = "#9A7B3F"       # the theme's text gold: #B9975B on white fails contrast

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
        unknown = sorted(set(s) - {"index", "date", "kind", "title",
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
        if date.weekday() != WEEKDAY:
            raise SeriesError(
                f"{where}: {date.isoformat()} is a {date.strftime('%A')}, "
                f"the course meets on Fridays")
        kind = _text(s.get("kind"), where, "kind")
        if kind not in KINDS:
            raise SeriesError(f"{where}: kind must be one of {', '.join(KINDS)}, got {kind!r}")
        title = _text(s.get("title"), where, "title")
        presenter = _text(s.get("presenter"), where, "presenter", required=False)
        deck = _text(s.get("deck"), where, "deck", required=False)
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
    """The one short tag printed under a session's dot."""
    kind = session["kind"]
    if kind == "exam":
        return EXAM_TAG.get(session["index"], "exam")
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
    date ("Sep 4"), tag ("Lecture" / "DGIST" / "holiday" ...), titled (bold
    date, navy tag), tag_size, and date_row / tag_row (0 low-near, 1 high-far:
    both alternate by index parity, because a 26 px date is wider than the
    slot pitch). Raises SeriesError when two texts of one row would overlap
    under the width estimate."""
    sessions = sorted(series["sessions"], key=lambda s: s["index"])
    n = len(sessions)
    items: dict[int, dict] = {}
    for s in sessions:
        idx = s["index"]
        titled = s["kind"] in TITLED
        items[idx] = {
            "index": idx, "kind": s["kind"], "x": dot_x(n, idx),
            "date": short_date(s["date"]), "tag": kind_tag(s),
            "date_row": (idx + 1) % 2, "tag_row": (idx + 1) % 2,
            "titled": titled,
            "tag_size": FONT_TAG if titled or s["kind"] == "dgist" else FONT_TAG_SMALL,
        }
    for row in (0, 1):
        _assert_row_clear(
            f"date {row}",
            [(it["x"], text_width(it["date"], FONT_DATE), f"date {it['date']!r}")
             for it in items.values() if it["date_row"] == row])
        _assert_row_clear(
            f"tag {row}",
            [(it["x"], text_width(it["tag"], it["tag_size"]), f"tag {it['tag']!r}")
             for it in items.values() if it["tag_row"] == row])
    return items


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


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
        f'<line x1="{dot_x(n, 1):.1f}" y1="{Y_LINE}" x2="{dot_x(n, n):.1f}" '
        f'y2="{Y_LINE}" stroke="{GREY}" stroke-width="2"/>',
    ]
    for idx in sorted(layout):
        it = layout[idx]
        kind = it["kind"]
        xs = f"{it['x']:.1f}"
        if kind in TITLED:
            out.append(f'<circle cx="{xs}" cy="{Y_LINE}" r="{DOT_R}" fill="{NAVY}"/>')
        elif kind == "dgist":
            out.append(f'<circle cx="{xs}" cy="{Y_LINE}" r="{DOT_R - 1}" fill="#fff" '
                       f'stroke="{NAVY}" stroke-width="2"/>')
        else:
            out.append(f'<circle cx="{xs}" cy="{Y_LINE}" r="{DOT_R - 1}" fill="{GREY}"/>')
        if highlight == idx:
            out.append(f'<circle cx="{xs}" cy="{Y_LINE}" r="{RING_R}" fill="none" '
                       f'stroke="{GOLD}" stroke-width="{RING_W}" class="today-ring"/>')
            out.append(f'<text x="{xs}" y="{Y_TODAY}" font-size="{FONT_TODAY}" '
                       f'font-weight="700" text-anchor="middle" fill="{GOLD_TEXT}" '
                       f'class="today-tag">today</text>')
        date_weight = "700" if it["titled"] else "400"
        date_fill = INK if it["titled"] else MUTED
        out.append(f'<text x="{xs}" y="{Y_DATE_ROWS[it["date_row"]]}" '
                   f'font-size="{FONT_DATE}" font-weight="{date_weight}" '
                   f'text-anchor="middle" fill="{date_fill}" '
                   f'class="date">{_esc(it["date"])}</text>')
        if it["titled"]:
            tag_fill = NAVY
            tag_weight = ' font-weight="700"' if kind == "lecture" else ""
        else:
            tag_fill = MUTED
            tag_weight = ""
        out.append(f'<text x="{xs}" y="{Y_TAG_ROWS[it["tag_row"]]}" '
                   f'font-size="{it["tag_size"]}"{tag_weight} '
                   f'text-anchor="middle" fill="{tag_fill}" class="tag">'
                   f'{_esc(it["tag"])}</text>')
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
