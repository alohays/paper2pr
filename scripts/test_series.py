#!/usr/bin/env python3
"""Regression tests for the course-series object (WP4).

What is pinned here, and why it is worth a test:

  1. series yml validation -- series_assets.py refuses a bad date, a date
     that is not a Friday, a duplicate index, a bad kind, a duplicate deck,
     a missing field, a gap in the indices. A series that loads with the
     wrong shape would put a wrong date on every shared slide of the course.
  2. lock generation is deterministic: building twice writes identical bytes
     for the lock, every map SVG and both QR files (no clock anywhere).
  3. prior-session resolution skips holiday and exam weeks and counts guest
     and DGIST sessions: w02 -> 1 (DGIST), w04 -> 3 (guest), w06 -> 4,
     w09 -> 6 (8 is the midterm week), w01 -> none, a holiday has none.
  4. week label and short date formatting.
  5. the semester map: every SVG exists; the highlighted file carries the
     gold ring and the "today" tag exactly once and the plain one not at all;
     the map prints only dates and kind tags (no session-title words, no
     presenter names, no leader lines); dates and tags alternate their two
     rows by index parity and nothing on one row overlaps under the width
     estimate; an overlap is a loud SeriesError, never a silent collision.
  6. the QR files exist, the SVG is the scalable one.
  7. deckprofile resolves series / series_index to the session fields and the
     prior session, and fails loudly (ConfigError) on an unknown index or an
     unknown series.
  8. new_deck.py --dry-run --series dgist-2026f --series-index 2 prints the
     session title and date, the include lines, series: in both files.
  9. build_landing groups a series deck under its course heading, ordered by
     series_index, on a temporary deck tree (deckpath pointed at it).
 10. render-level (skipped without quarto): the committed fixture renders with
     one ringed map, the QR block and the rules; a deck named after a session
     resolves its week and prior session from the deck name alone; a deck
     that uses a series shortcode without `series:` aborts with one
     "(E) series:" line and no output page.
 11. the committed lock agrees with the yml (series_assets.py --check, content-based:
     the clock is never consulted, drift in any file is caught, build() is idempotent).

Usage: python3 scripts/test_series.py
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_landing  # noqa: E402
import deckpath  # noqa: E402
import deckprofile  # noqa: E402
import series_assets as sa  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
COURSE = "dgist-2026f"
FIXTURE = REPO_ROOT / "Quarto" / "_fixtures" / "series"

fail = 0


def check(label, condition, detail=""):
    global fail
    if condition:
        print(f"  ok    {label}")
    else:
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else ""))
        fail = 1


GOOD = sa.series_yml(COURSE).read_text(encoding="utf-8")


def expect_error(label, text, fragment):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.yml"
        p.write_text(text, encoding="utf-8")
        try:
            sa.load_series(p)
        except sa.SeriesError as e:
            check(label, fragment in str(e), f"got: {e}")
            return
        check(label, False, "no error raised")


def expect_ok(label, text):
    """The opposite: a series file that must load."""
    loaded = None
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.yml"
        p.write_text(text, encoding="utf-8")
        try:
            loaded = sa.load_series(p)
        except sa.SeriesError as e:
            check(label, False, f"raised: {e}")
            return None
    check(label, True)
    return loaded


print("1. series yml validation")
check("the committed series file loads", bool(sa.load_series(sa.series_yml(COURSE))))
expect_error("bad date", GOOD.replace('date: "2026-09-04"', 'date: "2026-9-4"'), "YYYY-MM-DD")
expect_error("a date that is not one of the meets_on days",
             GOOD.replace('date: "2026-09-04"', 'date: "2026-09-03"'),
             "is a Thursday, and meets_on says friday")
expect_error("a weekday name that is not one", GOOD.replace("meets_on: friday", "meets_on: fryday"),
             "is not a weekday")
expect_error("an unknown top-level key", GOOD.replace("meets_on: friday", "meets_of: friday"),
             "unknown top-level key")
expect_error("a tag too long for the map",
             GOOD.replace("tag: report", "tag: reflection report"), "too long for the map")
# The weekday check belongs to the course, not to the tool. A block course
# that runs Saturday to Friday could not be declared at all while the day was
# a module-level constant.
_no_day = expect_ok("a course with no meets_on takes any weekday",
                    GOOD.replace("meets_on: friday\n", "")
                        .replace('date: "2026-09-04"', 'date: "2026-09-03"'))
check("... and records no weekday", _no_day is not None and _no_day["meets_on"] == [])
_two_days = expect_ok("a course may meet on more than one weekday",
                      GOOD.replace("meets_on: friday", "meets_on: [friday, thursday]")
                          .replace('date: "2026-09-04"', 'date: "2026-09-03"'))
check("... and records both", _two_days is not None
      and _two_days["meets_on"] == ["friday", "thursday"])
# The exam-week wording used to be {8: "report", 16: "essay"} in the tool.
_tagged = sa.load_series(sa.series_yml(COURSE))
check("a session's own tag is what the map prints",
      sa.kind_tag(sa.session_by_index({"sessions": _tagged["sessions"]}, 8)) == "report")
check("a kind with no tag falls back to its own word",
      sa.kind_tag({"kind": "exam", "index": 99, "tag": ""}) == "exam"
      and sa.kind_tag({"kind": "lecture", "index": 1, "tag": ""}) == "Lecture")
expect_error("duplicate index", GOOD.replace("  - index: 3\n", "  - index: 2\n"), "duplicate index")
expect_error("bad kind", GOOD.replace("kind: keynote", "kind: party"), "kind must be one of")
expect_error("duplicate deck", GOOD.replace("deck: dgist-2026f-w04", "deck: dgist-2026f-w02"),
             "already session")
expect_error("missing scalar field", GOOD.replace("room: E7-233\n", ""), "room is required")
expect_error("gap in the indices", GOOD.replace("  - index: 16\n", "  - index: 17\n"), "no gap")
expect_error("unknown session key", GOOD.replace("    remote: true\n", "    remote: true\n    venue: x\n", 1),
             "unknown key")
expect_error("short: is no longer a session key",
             GOOD.replace("    deck: dgist-2026f-w02\n",
                          "    deck: dgist-2026f-w02\n    short: x\n", 1),
             "unknown key")
expect_error("qa_tool url must be http(s)", GOOD.replace("url: https://app.wooclap.com/PLACEHOLDER",
                                                        "url: app.wooclap.com/PLACEHOLDER"),
             "http(s) URL")

print("2. lock generation is deterministic")
series = sa.load_series(sa.series_yml(COURSE))
lock_a = json.dumps(sa.derive(series), sort_keys=True)
lock_b = json.dumps(sa.derive(sa.load_series(sa.series_yml(COURSE))), sort_keys=True)
check("derive() twice -> identical", lock_a == lock_b)
svg_a = sa.semester_map_svg(series, 2)
svg_b = sa.semester_map_svg(sa.load_series(sa.series_yml(COURSE)), 2)
check("semester_map_svg() twice -> identical", svg_a == svg_b)


def digest_dir(d: Path) -> dict:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.iterdir())
            if p.is_file()}


qrencode = shutil.which("qrencode")
if qrencode:
    before = digest_dir(sa.figure_dir(COURSE))
    sa.build(COURSE, quiet=True)
    first = digest_dir(sa.figure_dir(COURSE))
    sa.build(COURSE, quiet=True)
    second = digest_dir(sa.figure_dir(COURSE))
    check("build() twice -> identical bytes for all files", first == second,
          str([k for k in first if first[k] != second.get(k)]))
    check("build() reproduces the committed files", before == first,
          str([k for k in first if before.get(k) != first[k]]))
else:
    check("qrencode on PATH (build() test)", False, "skipped: qrencode not found")

print("3. prior-session resolution")
S = series["sessions"]
for idx, want in ((2, 1), (4, 3), (6, 4), (9, 6), (11, 10), (14, 13), (15, 14), (1, None),
                  (5, None), (8, None)):
    check(f"prior of session {idx} -> {want}", sa.prior_index(S, idx) == want,
          str(sa.prior_index(S, idx)))
lock = sa.derive(series)
check("the lock carries prior_index per session",
      sa.session_by_index(lock, 9)["prior_index"] == 6
      and sa.session_by_index(lock, 4)["prior_index"] == 3)
check("session_by_deck finds w02", sa.session_by_deck(lock, "dgist-2026f-w02")["index"] == 2)
check("session_by_deck tolerates a deck that does not exist yet",
      sa.session_by_deck(lock, "dgist-2026f-w14")["index"] == 14)

print("4. week label and short date")
check("week label", sa.week_label(2) == "W02" and sa.week_label(14) == "W14")
check("short date", sa.short_date("2026-09-04") == "Sep 4" and sa.short_date("2026-11-27") == "Nov 27")
check("lock: week and short_date", sa.session_by_index(lock, 2)["week"] == "W02"
      and sa.session_by_index(lock, 2)["short_date"] == "Sep 4")

print("5. semester map")
figdir = sa.figure_dir(COURSE)
check("plain map exists", (figdir / "semester-map.svg").exists())
check("one highlighted map per session",
      all((figdir / f"semester-map-w{s['index']:02d}.svg").exists() for s in S))
w02 = (figdir / "semester-map-w02.svg").read_text(encoding="utf-8")
plain = (figdir / "semester-map.svg").read_text(encoding="utf-8")
check("highlighted: gold ring exactly once",
      w02.count('class="today-ring"') == 1 and w02.count(sa.GOLD) == 1, str(w02.count(sa.GOLD)))
check("highlighted: 'today' text exactly once", w02.count(">today<") == 1)
check("plain: no ring, no today", "today-ring" not in plain and ">today<" not in plain)
check("svg has no xml prolog (inlined as is) and inherits the font",
      w02.startswith("<svg ") and 'font-family:inherit' in w02)
check("16 dots on the line", len(re.findall(r"<circle [^>]*cy=\"%d\"" % sa.Y_LINE, plain)) == 16)
check("presenter names are not on the map", "Hyeongmin" not in plain and "Yunsung" not in plain)
check("no session titles on the map",
      all(w not in plain for w in ("Paradigm", "Embodied", "Hardware", "Imitation",
                                   "Ethics", "Megatrend", "Foundation", "Spatial",
                                   "Leadership", "Guest:", "Keynote:")))
check("no leader lines, no title labels (the baseline is the only <line>)",
      'class="label"' not in plain and plain.count("<line ") == 1)
check("every kind tag appears",
      all(t in plain for t in (">Lecture<", ">Guest<", ">Keynote<", ">DGIST<",
                               ">holiday<", ">report<", ">essay<")))
check("all 16 dates at 26 px", plain.count(f'font-size="{sa.FONT_DATE}"') == 16)
bold_plain = plain.count('font-weight="700"')
bold_w02 = w02.count('font-weight="700"')
check("bold dates for the 8 lecture/guest/keynote sessions plus 5 bold Lecture tags",
      bold_plain == 13 and bold_w02 == 14, f"plain={bold_plain} w02={bold_w02}")
check("quiet weeks are muted", plain.count(f'fill="{sa.MUTED}"') == 16)

layout = sa.map_layout(series)


def row_clear(entries):
    placed = sorted(entries)
    return all((xb - wb / 2) - (xa + wa / 2) >= sa.ROW_GAP
               for (xa, wa), (xb, wb) in zip(placed, placed[1:]))


check("no two dates on one row overlap (width estimate + gap)",
      all(row_clear([(it["x"], sa.text_width(it["date"], sa.FONT_DATE))
                     for it in layout.values() if it["date_row"] == r]) for r in (0, 1)))
check("no two tags on one row overlap (width estimate + gap)",
      all(row_clear([(it["x"], sa.text_width(it["tag"], it["tag_size"]))
                     for it in layout.values() if it["tag_row"] == r]) for r in (0, 1)))
check("consecutive sessions alternate date rows",
      all(layout[i]["date_row"] != layout[i + 1]["date_row"] for i in range(1, len(layout))))
check("consecutive sessions alternate tag rows",
      all(layout[i]["tag_row"] != layout[i + 1]["tag_row"] for i in range(1, len(layout))))
check("every session has a dot x in order",
      [layout[i]["x"] for i in sorted(layout)] == sorted(layout[i]["x"] for i in layout))

# two texts forced onto the same spot -> refused loudly, never drawn overlapping
try:
    sa._assert_row_clear("date 0", [(100.0, 78.0, "date 'Sep 4'"),
                                    (150.0, 78.0, "date 'Sep 11'")])
    check("overlapping texts on one row are refused", False, "no error")
except sa.SeriesError as e:
    check("overlapping texts on one row are refused", "overlap" in str(e), str(e))
try:
    sa.semester_map_svg(series, 99)
    check("highlighting an unknown session fails", False)
except sa.SeriesError:
    check("highlighting an unknown session fails", True)

print("6. QR files")
check("qr-qa.png exists", (figdir / "qr-qa.png").exists())
qr_svg = figdir / "qr-qa.svg"
check("qr-qa.svg exists and is an SVG with a viewBox",
      qr_svg.exists() and "viewBox" in qr_svg.read_text(encoding="utf-8"))
check("qr-qa.svg snaps to the pixel grid (crispEdges)",
      'shape-rendering="crispEdges"' in qr_svg.read_text(encoding="utf-8"))

print("7. deckprofile resolution")
lecture_profile = deckprofile._load_yaml(deckprofile.PROFILE_DIR / "lecture.yml")


def cfg_for(raw):
    return deckprofile.DeckConfig(deck=deckpath.Deck("probe", "lectures"), profile="lecture",
                                  raw=raw, profile_raw=lecture_profile)


cfg = cfg_for({"series": COURSE, "series_index": 2})
check("series / series_index resolve the session",
      cfg.series == COURSE and cfg.series_course == "Future Literacy"
      and cfg.session_date == "2026-09-04"
      and cfg.session_title == "The Paradigm Shift Toward Embodied AI")
prior = cfg.prior_session
check("prior_session for w02 is the DGIST session",
      prior and prior["index"] == 1 and prior["kind"] == "dgist" and prior["week"] == "W01"
      and prior["short_date"] == "Aug 28" and prior["title"] == "Special lecture on AI", str(prior))
cfg4 = cfg_for({"series": COURSE, "series_index": 4})
check("prior_session for w04 is the guest session (a guest counts)",
      cfg4.prior_session["index"] == 3 and cfg4.prior_session["presenter"] == "Hyeongmin Lee (SeoulTech)")
check("a deck without a series resolves to None everywhere",
      cfg_for({}).series is None and cfg_for({}).prior_session is None
      and cfg_for({}).session_date is None)
check("series without series_index: no session, no error",
      cfg_for({"series": COURSE}).series_session is None
      and cfg_for({"series": COURSE}).series_course == "Future Literacy")
check("as_dict carries the series fields",
      cfg.as_dict()["prior_session"]["index"] == 1 and cfg.as_dict()["series"] == COURSE)
try:
    cfg_for({"series": COURSE, "series_index": 99}).as_dict()
    check("unknown series_index is a hard ConfigError", False, "no error")
except deckprofile.ConfigError as e:
    check("unknown series_index is a hard ConfigError", "99" in str(e) and "1..16" in str(e), str(e))
try:
    cfg_for({"series": "no-such-course", "series_index": 1}).as_dict()
    check("unknown series is a hard ConfigError", False, "no error")
except deckprofile.ConfigError as e:
    check("unknown series is a hard ConfigError", "no-such-course" in str(e), str(e))

print("8. new_deck.py --dry-run with --series")
out = subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "new_deck.py"),
                      "--series", COURSE, "--series-index", "2", "--audience", "none",
                      "--duration", "60", "--dry-run"], capture_output=True, text=True)
check("dry run exits 0", out.returncode == 0, out.stderr[-300:])
check("prints the session title", 'title: "The Paradigm Shift Toward Embodied AI"' in out.stdout)
check("prints the session date", 'date: "2026-09-04"' in out.stdout)
check("names the deck <series>-w<NN>", "Quarto/lectures/dgist-2026f-w02.qmd" in out.stdout)
check("deck.yml gets series: and series_index:",
      "series: dgist-2026f\nseries_index: 2" in out.stdout)
check("qmd front matter gets series: <course>", "\nseries: dgist-2026f\n# Full-bleed" in out.stdout)
inc = [l for l in out.stdout.splitlines() if l.startswith("{{< include _series/")]
check("the four include lines, map/rules/ask near the top and qa last",
      [l.split("/")[-1] for l in inc] == ["semester-map.qmd >}}", "course-runs.qmd >}}",
                                          "ask-anytime.qmd >}}", "qa.qmd >}}"], str(inc))
check("the recap slide names the prior session",
      "(W01, Aug 28: Special lecture on AI)" in out.stdout)
bad = subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "new_deck.py"),
                      "--series", COURSE, "--series-index", "42", "--dry-run"],
                     capture_output=True, text=True)
check("an unknown series_index is refused", bad.returncode != 0 and "42" in bad.stderr, bad.stderr)

print("9. build_landing groups a series deck")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    (root / "Quarto" / "lectures").mkdir(parents=True)
    (root / "Quarto" / "_genres.txt").write_text("lectures\n", encoding="utf-8")
    (root / "Quarto" / "lectures" / "dgist-2026f-w04.qmd").write_text("---\ntitle: x\n---\n")
    (root / "Quarto" / "lectures" / "dgist-2026f-w04.deck.yml").write_text(
        f"profile: lecture\ntitle: \"W04 probe\"\nseries: {COURSE}\nseries_index: 4\n")
    (root / "Quarto" / "lectures" / "dgist-2026f-w02.qmd").write_text("---\ntitle: y\n---\n")
    (root / "Quarto" / "lectures" / "dgist-2026f-w02.deck.yml").write_text(
        f"profile: lecture\ntitle: \"W02 probe\"\nseries: {COURSE}\nseries_index: 2\n")
    (root / "Quarto" / "lectures" / "loose.qmd").write_text("---\ntitle: z\n---\n")
    (root / "Quarto" / "lectures" / "loose.deck.yml").write_text("profile: lecture\ntitle: \"Loose\"\n")
    saved = (deckpath.QUARTO_DIR, deckpath.GENRES_FILE)
    deckpath.QUARTO_DIR = root / "Quarto"
    deckpath.GENRES_FILE = root / "Quarto" / "_genres.txt"
    try:
        page = build_landing.build()
    finally:
        deckpath.QUARTO_DIR, deckpath.GENRES_FILE = saved
    check("course heading", "Future Literacy (HSS118, DGIST, 2026 Fall)" in page)
    i2, i4 = page.find(">W02<"), page.find(">W04<")
    check("rows in series order with week labels", 0 < i2 < i4)
    check("rows show the date and a link",
          ">2026-09-04<" in page and 'href="slides/lectures/dgist-2026f-w04.html"' in page)
    check("a deck without a series stays in the plain table",
          ">Loose<" in page and page.find(">Loose<") > i4)
    check("the live landing page keeps the SUNY row",
          "SUNY" in build_landing.build() or "Career" in build_landing.build())

print("10. render-level")
quarto = shutil.which("quarto")
if not quarto:
    check("quarto on PATH", False, "skipped: quarto not found")
else:
    out = subprocess.run([quarto, "render", "series.qmd"], cwd=FIXTURE,
                         capture_output=True, text=True)
    html = (FIXTURE / "series.html").read_text(encoding="utf-8") if out.returncode == 0 else ""
    check("the fixture renders", out.returncode == 0, (out.stdout + out.stderr)[-400:])
    check("one map is ringed (week=2) and one is plain",
          html.count('class="today-ring"') == 1 and html.count('<figure class="semester-map"') == 2)
    check("the QR block points at the series figures, one level up from _fixtures/<dir>/",
          html.count('src="../../../Figures/lectures/_series/dgist-2026f/qr-qa.svg"') == 2
          and 'class="qr-code">code PLACEHOLDER<' in html)
    check("the rules and the LMS footnote come from the lock",
          "Attendance: every session" in html
          and "answers in the last 10 minutes" in html
          and "live on the DGIST LMS" in html)
    check("series-session prior_title resolves", "Special lecture on AI" in html)

    # a deck named after a session resolves the week from its own name
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        shutil.copytree(sa.figure_dir(COURSE), root / "Figures" / "lectures" / "_series" / COURSE)
        (root / "Quarto" / "lectures").mkdir(parents=True)
        qmd = root / "Quarto" / "lectures" / "dgist-2026f-w04.qmd"
        qmd.write_text(f"""---
title: w04 probe
series: {COURSE}
format:
  revealjs:
    shortcodes: [{REPO_ROOT / 'Quarto' / '_filters' / 'series.lua'}]
---

## Map

{{{{< semester-map >}}}}

## Prior

Last time: {{{{< series-session prior_title >}}}} ({{{{< series-session prior_week >}}}}, {{{{< series-session week >}}}})

{{{{< series-qr >}}}}
""", encoding="utf-8")
        out = subprocess.run([quarto, "render", str(qmd)], cwd=root / "Quarto" / "lectures",
                             capture_output=True, text=True)
        h = qmd.with_suffix(".html").read_text(encoding="utf-8") if out.returncode == 0 else ""
        check("a deck named after a session renders", out.returncode == 0,
              (out.stdout + out.stderr)[-400:])
        check("its map is the W04 one", 'data-map="semester-map-w04.svg"' in h
              and h.count('class="today-ring"') == 1)
        check("its prior session is the guest (W03)",
              "Last time: Video and Robot Foundation Models (W03, W04)" in h)
        check("RELPATH from Quarto/lectures/ is ../../Figures/...",
              'src="../../Figures/lectures/_series/dgist-2026f/qr-qa.svg"' in h)

    with tempfile.TemporaryDirectory() as td:
        qmd = Path(td) / "neg.qmd"
        qmd.write_text(f"""---
title: neg
format:
  revealjs:
    shortcodes: [{REPO_ROOT / 'Quarto' / '_filters' / 'series.lua'}]
---

## A

{{{{< series-rules >}}}}
""", encoding="utf-8")
        out = subprocess.run([quarto, "render", str(qmd)], cwd=td, capture_output=True, text=True)
        log = out.stdout + out.stderr
        e_lines = [l for l in log.splitlines() if "(E) series:" in l]
        check("no `series:` metadata aborts the render with one (E) series: line",
              out.returncode != 0 and not (Path(td) / "neg.html").exists()
              and len(e_lines) == 1 and "declares no `series:" in e_lines[0]
              and "attempt to index a nil value" not in log, log[-400:])

print("11. the committed lock agrees with the yml (--check is content-based)")
problems = sa.check(COURSE)
check("series_assets.py --check is clean", not problems, "; ".join(problems))

# --check must not read the clock: a clone or checkout writes Figures/... before
# Quarto/... (index order), a `touch` or a comment-only edit to the yml changes no
# output, and build() leaves unchanged files alone. Each scenario is staged on
# the real tree and undone in the finally block.
yml_path = sa.series_yml(COURSE)
built = sa.expected_files(COURSE, sa.load_series(yml_path))
saved_times = {q: (q.stat().st_atime, q.stat().st_mtime) for q in built + [yml_path]}
w03 = sa.figure_dir(COURSE) / "semester-map-w03.svg"
w03_bytes = w03.read_bytes()
try:
    future = yml_path.stat().st_mtime + 3600
    os.utime(yml_path, (future, future))          # yml newer than every figure
    check("--check stays clean when the yml is newer than the figures (checkout order)",
          not sa.check(COURSE), "; ".join(sa.check(COURSE)))
    if qrencode:
        before_mtimes = {q: q.stat().st_mtime for q in built}
        sa.build(COURSE, quiet=True)
        check("build() after a mtime-only change rewrites nothing (all 20 files untouched)",
              all(q.stat().st_mtime == before_mtimes[q] for q in built),
              str([q.name for q in built if q.stat().st_mtime != before_mtimes[q]]))
        check("--check is clean after that build", not sa.check(COURSE))
    w03.write_bytes(w03_bytes + b"<!-- drift -->")
    drift = sa.check(COURSE)
    check("--check catches a byte-level drift in one map",
          len(drift) == 1 and "stale" in drift[0] and "semester-map-w03.svg" in drift[0]
          and "mtime" not in drift[0].lower() and "older" not in drift[0], "; ".join(drift))
    if qrencode:
        sa.build(COURSE, quiet=True)
        check("build() repairs the drifted file", w03.read_bytes() == w03_bytes
              and not sa.check(COURSE))
finally:
    w03.write_bytes(w03_bytes)
    for q, (at, mt) in saved_times.items():
        os.utime(q, (at, mt))
check("the tree is restored after the --check scenarios",
      w03.read_bytes() == w03_bytes and all(q.stat().st_mtime == saved_times[q][1] for q in built))

print()
print("ALL PASSED" if not fail else "FAILED")
sys.exit(fail)
