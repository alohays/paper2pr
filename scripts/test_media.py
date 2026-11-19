#!/usr/bin/env python3
"""Regression tests for the video pipeline (WP3).

What is pinned here, and why it is worth a test:

  1. videos.yml validation -- media_prep.py refuses a manifest with a missing
     required key, a bad autonomy value, a bad slug, a bad month, a segment
     without a source, an unknown key (release_url belongs in videos.json).
     A manifest that loads with the wrong fields would put a wrong caption on
     a public page.
  2. segment parsing: "S-E", "S-", absent, and the rejects.
  3. the autonomy label table: Python and Lua must agree (the caption strip
     is rendered by Lua from the same values media_prep.py writes), and the
     wording is the presenter's plain wording.
  4. videos.json generation end to end on the repo's placeholder clip (ffmpeg
     runs; a few seconds), including the Release URLs, the hand-edited-URL
     rule, local_only, and staleness: a changed segment re-encodes (the lock's
     duration_s follows), --only leaves a "cut" record behind that
     lock_mismatches() reports and the next full run repairs, a lock without
     the record is not trusted.
  5. URL construction for a tag; local path construction from a deck dir.
  6. deckpath.find_media on a deck name, a videos.yml path, a directory, and
     the fixture naming rule (media-fixture-<dir>).
  7. check_site_assets: a page pointing at Figures/**/videos/ fails even when
     the file exists; the RoboTTT videos/*.mp4 exemption still holds; Release
     URLs are external.
  8. the Lua side, through `quarto pandoc lua`: relpath, month text, caption
     HTML (escaping, fragment class, none) -- skipped with a message when
     quarto is not on PATH.
  9. the committed fixture lock agrees with its manifest and release.
 10. render-level: a deck asking for an unknown slug, and one whose lock file
     is missing, make `quarto render` exit 1 with one "(E) video-manifest:"
     line and no output page. This has to be a real render: inside Quarto the
     global `error` is a non-throwing logger, so `quarto pandoc lua` (8.)
     cannot see whether a failure actually aborts. Skipped when quarto is
     absent.

Usage: python3 scripts/test_media.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import browser  # noqa: E402
import check_site_assets  # noqa: E402
import deckpath  # noqa: E402
import media_prep  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = REPO_ROOT / "Quarto" / "_fixtures" / "assets" / "placeholder-video.mp4"
FIXTURE = REPO_ROOT / "Quarto" / "_fixtures" / "video"

fail = 0


def check(label, condition, detail=""):
    global fail
    if condition:
        print(f"  ok    {label}")
    else:
        print(f"  FAIL  {label}" + (f" -- {detail}" if detail else ""))
        fail = 1


def expect_error(label, text, fragment):
    """Loading `text` as a videos.yml must raise a ManifestError that
    mentions `fragment`."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "videos.yml"
        p.write_text(text, encoding="utf-8")
        try:
            media_prep.load_manifest(p)
        except media_prep.ManifestError as e:
            check(label, fragment in str(e), f"got: {e}")
            return
        check(label, False, "no error raised")


GOOD = """\
videos:
  - slug: hook
    title: A clip
    publisher: Some Lab
    source_url: https://example.org/v
    published: 2026-05
    autonomy: autonomous
"""

print("1. videos.yml validation")
expect_error("missing required key (publisher)",
             GOOD.replace("    publisher: Some Lab\n", ""), "publisher")
expect_error("invalid redistribution", GOOD + "    redistribution: maybe\n", "redistribution must be")
expect_error("bad autonomy value",
             GOOD.replace("autonomous", "maybe"), "autonomy must be one of")
expect_error("bad slug (uppercase, underscore)",
             GOOD.replace("slug: hook", "slug: Hook_1"), "slug must match")
expect_error("bad published month",
             GOOD.replace("2026-05", "2026-13"), "published must be YYYY-MM")
expect_error("segment without a source",
             GOOD + "    segment: 0-2\n", "segment needs a source")
expect_error("release_url is not a manifest key",
             GOOD + "    release_url: https://x/y.mp4\n", "release_url and poster_url")
expect_error("bad caption value",
             GOOD + "    caption: loud\n", "caption must be one of")
expect_error("duplicate slug",
             GOOD + GOOD.split("videos:\n", 1)[1], "duplicate slug")
expect_error("no videos list", "title: x\n", "top-level 'videos:' list")
with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "videos.yml"
    p.write_text(GOOD + "    speed: 2x\n    keep_audio: true\n    caption: fragment\n",
                 encoding="utf-8")
    entries = media_prep.load_manifest(p)
    e = entries[0]
    check("a good manifest loads with defaults filled",
          e["slug"] == "hook" and e["speed"] == "2x" and e["keep_audio"] is True
          and e["caption"] == "fragment" and e["segment"] is None and e["source"] is None,
          repr(e))
    p.write_text(GOOD, encoding="utf-8")
    e = media_prep.load_manifest(p)[0]
    check("defaults: speed 1x, caption visible, keep_audio false",
          e["speed"] == "1x" and e["caption"] == "visible" and e["keep_audio"] is False)
    check("an unspecified policy defaults to classroom", e["redistribution"] == "classroom")

print("2. segment parsing")
check('"0-2" -> (0, 2)', media_prep.parse_segment("0-2") == (0.0, 2.0))
check('"12.5-40" -> (12.5, 40)', media_prep.parse_segment("12.5-40") == (12.5, 40.0))
check('"7-" -> (7, None)', media_prep.parse_segment("7-") == (7.0, None))
check("absent -> (0, None)", media_prep.parse_segment(None) == (0.0, None))
for bad in ("2-0", "abc", "1:30-2:00", "-5"):
    try:
        media_prep.parse_segment(bad)
        check(f"rejects {bad!r}", False, "no error")
    except media_prep.ManifestError:
        check(f"rejects {bad!r}", True)

# A library link can change more recently than the prepared clip even when
# its new target is an older original. Use explicit times on both filesystems.
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    original = root / "older-original.mp4"
    prepared = root / "prepared.mp4"
    link = root / "source.mp4"
    original.touch()
    prepared.touch()
    link.symlink_to(original)
    os.utime(original, (1, 1))
    os.utime(prepared, (2, 2))
    os.utime(link, (3, 3), follow_symlinks=False)
    check("a retargeted library link invalidates the previous cut",
          media_prep.stale_reason(prepared, link, {}, {}) == "source is newer")

print("3. autonomy label mapping")
check("four labels, plain wording",
      media_prep.AUTONOMY_LABEL == {
          "autonomous": "autonomous",
          "claimed": "autonomy claimed",
          "teleop": "teleoperated",
          "unknown": "autonomy not stated"},
      repr(media_prep.AUTONOMY_LABEL))
lua_src = (REPO_ROOT / "Quarto" / "_filters" / "video-manifest.lua").read_text(encoding="utf-8")
for key, label in media_prep.AUTONOMY_LABEL.items():
    check(f"Lua table carries {key} -> {label!r}",
          f'{key:<10} = "{label}"' in lua_src or f'{key} = "{label}"' in lua_src)

print("4. URL and path construction")
check("release_url(tag, file)",
      media_prep.release_url("media-w02", "hook.mp4")
      == "https://github.com/alohays/paper2pr/releases/download/media-w02/hook.mp4")
check("hand-edited URL detection",
      not media_prep.is_ours("https://cdn.example.org/x.mp4")
      and media_prep.is_ours(media_prep.release_url("media-w02", "a.jpg")))
# The base comes from the repo's own remote, so a fork or a rename mints its
# own URLs; and any GitHub Release download URL counts as ours, so URLs
# minted before a rename are regenerated rather than frozen as "hand-edited".
check("release base is derived from the remote, not written down",
      media_prep.RELEASE_BASE.startswith("https://github.com/")
      and media_prep.RELEASE_BASE.endswith("/releases/download"))
check("a Release URL under another owner is still ours",
      media_prep.is_ours(
          "https://github.com/someone/elsewhere/releases/download/media-x/a.mp4"))
qmd_dir = REPO_ROOT / "Quarto" / "lectures"
videos_dir = REPO_ROOT / "Figures" / "lectures" / "dgist-2026f-w02" / "videos"
check("local path from Quarto/<genre>/ to Figures/<genre>/<deck>/videos/",
      media_prep.local_rel_path(qmd_dir, videos_dir, "hook.mp4")
      == "../../Figures/lectures/dgist-2026f-w02/videos/hook.mp4",
      media_prep.local_rel_path(qmd_dir, videos_dir, "hook.mp4"))

print("5. deckpath: media homes")
suny = deckpath.find("SUNY")
check("Deck.videos_manifest / lock / dir / tag",
      suny.videos_manifest == REPO_ROOT / "Figures/talks/SUNY/videos.yml"
      and suny.videos_lock == REPO_ROOT / "Figures/talks/SUNY/videos.json"
      and suny.videos_dir == REPO_ROOT / "Figures/talks/SUNY/videos"
      and suny.release_tag == "media-SUNY")
check("find_media by deck name", deckpath.find_media("SUNY").release_tag == "media-SUNY")
home = deckpath.find_media(str(FIXTURE))
check("find_media on a fixture directory -> media-fixture-<dir>",
      home.release_tag == "media-fixture-video" and home.slug == "_fixtures/video"
      and home.lock == FIXTURE / "videos.json")
check("find_media on a videos.yml path",
      deckpath.find_media(str(FIXTURE / "videos.yml")).manifest == FIXTURE / "videos.yml")
with tempfile.TemporaryDirectory() as td:
    d = Path(td) / "Figures" / "lectures" / "w02"
    # An unrelated directory with a videos.yml is its own home, tag media-<dir>.
    d.mkdir(parents=True)
    (d / "videos.yml").write_text(GOOD, encoding="utf-8")
    h = deckpath.find_media(str(d))
    check("find_media on an arbitrary directory -> media-<dir>", h.release_tag == "media-w02")
try:
    deckpath.find_media("Quarto/_fixtures/no-such-dir")
    check("find_media on a missing path raises", False)
except deckpath.DeckNotFound as e:
    check("find_media on a missing path raises", "no such path" in str(e))

print("6. videos.json generation on the placeholder clip (ffmpeg)")
ffmpeg = shutil.which("ffmpeg") or ("/opt/homebrew/bin/ffmpeg" if Path("/opt/homebrew/bin/ffmpeg").exists() else None)
if not ffmpeg:
    check("ffmpeg available", False, "install ffmpeg to run this section")
else:
    with tempfile.TemporaryDirectory() as td:
        home_dir = Path(td) / "Quarto" / "_fixtures" / "gen"
        home_dir.mkdir(parents=True)
        (home_dir / "videos.yml").write_text(f"""\
videos:
  - slug: one
    redistribution: release
    title: One <b>bold</b>
    publisher: Lab
    source_url: https://example.org/one
    published: 2026-05
    autonomy: claimed
    segment: 0-1
    source: {PLACEHOLDER}
  - slug: two
    redistribution: release
    title: Two
    publisher: Lab
    source_url: https://example.org/two
    published: 2026-06
    autonomy: teleop
    speed: 2x
    source: {PLACEHOLDER}
    caption: none
""", encoding="utf-8")
        home = deckpath.MediaHome(slug="test/gen", name="gen", manifest=home_dir / "videos.yml")
        logs = []
        payload = media_prep.prepare(home, log=logs.append)
        lock = json.loads((home_dir / "videos.json").read_text(encoding="utf-8"))
        check("lock file written with deck and release_tag",
              lock["deck"] == "test/gen" and lock["release_tag"] == "media-gen")
        one = lock["videos"][0]
        check("mp4 and poster produced",
              (home_dir / "videos" / "one.mp4").exists()
              and (home_dir / "videos" / "one-poster.jpg").exists())
        check("entry carries file, poster_file, size_mb, duration_s",
              one["file"] == "one.mp4" and one["poster_file"] == "one-poster.jpg"
              and one["size_mb"] > 0 and abs(one["duration_s"] - 1.0) < 0.2,
              json.dumps(one))
        check("entry carries the Release URLs from the tag",
              one["release_url"] == media_prep.release_url("media-gen", "one.mp4")
              and one["poster_url"] == media_prep.release_url("media-gen", "one-poster.jpg"))
        check("autonomy_label written", one["autonomy_label"] == "autonomy claimed"
              and lock["videos"][1]["autonomy_label"] == "teleoperated")
        check("no local_only by default", "local_only" not in one)
        check("entry records what the file was cut with",
              one["cut"] == media_prep.cut_of(media_prep.load_manifest(home.manifest)[0])
              and str(PLACEHOLDER) not in json.dumps(lock) and str(PLACEHOLDER) not in "\n".join(logs),
              json.dumps(one.get("cut")))
        second = []
        media_prep.prepare(home, log=second.append)
        check("second run skips fresh outputs",
              any("fresh   one.mp4" in l for l in second)
              and not any(l.lstrip().startswith("encode") for l in second),
              "\n".join(second))
        # A changed segment re-encodes even though one.mp4 is newer than its
        # source (the W02 loop: nudge a segment, re-run). Before the fix the
        # lock said segment 0-3 over a 1 s file.
        yml = home_dir / "videos.yml"
        yml.write_text(yml.read_text(encoding="utf-8").replace("segment: 0-1", "segment: 0-3"),
                       encoding="utf-8")
        third = []
        media_prep.prepare(home, log=third.append)
        lock_c = json.loads((home_dir / "videos.json").read_text(encoding="utf-8"))
        check("a changed segment re-encodes and says why",
              any("encode  one.mp4" in l and "segment changed" in l for l in third),
              "\n".join(third))
        check("duration_s follows the new cut (3 s, not the old 1 s)",
              abs(lock_c["videos"][0]["duration_s"] - 3.0) < 0.2
              and lock_c["videos"][0]["cut"]["segment"] == "0-3",
              json.dumps(lock_c["videos"][0]))
        check("the unchanged entry stays fresh",
              any("fresh   two.mp4" in l for l in third), "\n".join(third))
        # --only skips a slug whose manifest changed: the lock keeps the old
        # cut record for it, lock_mismatches() names it, and the next full
        # run re-encodes it.
        yml.write_text(yml.read_text(encoding="utf-8").replace("    caption: none\n",
                                                               "    caption: none\n    segment: 1-2\n"),
                       encoding="utf-8")
        only_log = []
        media_prep.prepare(home, only="one", log=only_log.append)
        lock_d = json.loads((home_dir / "videos.json").read_text(encoding="utf-8"))
        two = lock_d["videos"][1]
        check("--only carries the skipped entry's old cut record forward",
              two["segment"] == "1-2" and two["cut"]["segment"] is None and two["needs_prep"]
              and not any("two.mp4" in l for l in only_log),
              json.dumps(two))
        mism = media_prep.lock_mismatches(lock_d, media_prep.load_manifest(yml))
        check("lock_mismatches names the skipped entry",
              len(mism) == 1 and mism[0].startswith("two:") and "segment" in mism[0], repr(mism))
        full_log = []
        media_prep.prepare(home, log=full_log.append)
        lock_e = json.loads((home_dir / "videos.json").read_text(encoding="utf-8"))
        check("the next full run re-encodes it and the lock is consistent again",
              any("encode  two.mp4" in l and "segment changed" in l for l in full_log)
              and media_prep.lock_mismatches(lock_e, media_prep.load_manifest(yml)) == []
              and abs(lock_e["videos"][1]["duration_s"] - 1.0) < 0.2,
              "\n".join(full_log))
        # A lock without a cut record (older format, or deleted) is not trusted.
        for v in lock_e["videos"]:
            v.pop("cut", None)
        (home_dir / "videos.json").write_text(json.dumps(lock_e), encoding="utf-8")
        norec = []
        media_prep.prepare(home, log=norec.append)
        check("no cut record -> re-encode with that reason",
              sum(1 for l in norec if "encode" in l and "no record of the cut" in l) == 2,
              "\n".join(norec))
        forced = []
        media_prep.prepare(home, force=True, log=forced.append)
        check("--force re-encodes and says so", any("(--force)" in l for l in forced))
        # Hand-edited URL survives a regeneration.
        lock["videos"][0]["release_url"] = "https://cdn.example.org/one.mp4"
        (home_dir / "videos.json").write_text(json.dumps(lock), encoding="utf-8")
        media_prep.prepare(home, log=logs.append)
        lock2 = json.loads((home_dir / "videos.json").read_text(encoding="utf-8"))
        check("a hand-edited release_url on another host is kept",
              lock2["videos"][0]["release_url"] == "https://cdn.example.org/one.mp4"
              and lock2["videos"][0]["poster_url"].startswith(media_prep.RELEASE_BASE))
        # local_only
        media_prep.prepare(home, local=True, log=logs.append)
        lock3 = json.loads((home_dir / "videos.json").read_text(encoding="utf-8"))
        check("--local marks every entry local_only",
              all(v.get("local_only") is True for v in lock3["videos"]))
        # --only with an unknown slug
        try:
            media_prep.prepare(home, only="nope", log=logs.append)
            check("--only unknown slug raises", False)
        except media_prep.ManifestError:
            check("--only unknown slug raises", True)
        # dry run writes nothing
        (home_dir / "videos.json").unlink()
        media_prep.prepare(home, dry_run=True, log=logs.append)
        check("--dry-run writes no lock file", not (home_dir / "videos.json").exists())

print("7. check_site_assets rules")
check("Figures/**/videos/ reference is local media",
      check_site_assets.LOCAL_MEDIA.search("../../Figures/lectures/w02/videos/hook.mp4"))
check("a poster next to videos.json is not local media",
      not check_site_assets.LOCAL_MEDIA.search("../../Figures/lectures/w02/hook-poster.jpg"))
check("RoboTTT videos/*.mp4 exemption kept",
      any(p.match("../videos/task1.mp4") for p in check_site_assets.ALLOW_MISSING))
check("Release URL is external",
      check_site_assets.is_external(media_prep.release_url("media-w02", "hook.mp4")))
with tempfile.TemporaryDirectory() as td:
    site = Path(td)
    page_dir = site / "slides" / "lectures"
    page_dir.mkdir(parents=True)
    media = site / "Figures" / "lectures" / "w02" / "videos"
    media.mkdir(parents=True)
    (media / "hook.mp4").write_bytes(b"x")       # exists locally, still must fail
    (page_dir / "w02.html").write_text(
        '<video poster="https://github.com/alohays/paper2pr/releases/download/media-w02/p.jpg">'
        '<source data-src="../../Figures/lectures/w02/videos/hook.mp4"></video>',
        encoding="utf-8")
    checked, missing = check_site_assets.check(str(site))
    check("a page pointing at local media fails even when the file exists",
          len(missing) == 1 and "local media" in missing[0][1], repr(missing))
    (page_dir / "w02.html").write_text(
        '<section data-background-video="https://github.com/alohays/paper2pr/releases/download/media-w02/h.mp4" '
        'data-background-poster="https://github.com/alohays/paper2pr/releases/download/media-w02/h.jpg"></section>'
        '<video poster="https://github.com/alohays/paper2pr/releases/download/media-w02/p.jpg">'
        '<source data-src="https://github.com/alohays/paper2pr/releases/download/media-w02/hook.mp4"></video>'
        '<video><source src="https://cdn.example.org/task1.mp4"><source src="../videos/task1.mp4"></video>',
        encoding="utf-8")
    checked, missing = check_site_assets.check(str(site))
    check("Release URLs and the RoboTTT fallback pass", missing == [], repr(missing))

print("8. Lua side (quarto pandoc lua)")
quarto = shutil.which("quarto")
if not quarto:
    check("quarto on PATH", False, "skipped: quarto not found")
else:
    with tempfile.TemporaryDirectory() as td:
        script = Path(td) / "t.lua"
        script.write_text("""
local M = dofile(arg[1])
print(M.relpath("/r/Figures/lectures/w02/videos", "/r/Quarto/lectures"))
print(M.relpath("/r/Quarto/_fixtures/video/videos", "/r/Quarto/_fixtures/video"))
print(M.month_text("2026-08") .. "|" .. M.month_text("2025-12") .. "|" .. M.month_text("x"))
print(M.caption_html({title="A & B", publisher="Pub", month="May 2026", label="autonomous", speed="2x", caption="fragment"}, "figcaption"))
print(tostring(M.caption_html({caption="none"}, "div")))
print(M.caption_html({title="T", publisher="P", month="Jan 2026", label="teleoperated", speed="1x", caption="visible"}, "div"))
""", encoding="utf-8")
        out = subprocess.run(
            [quarto, "pandoc", "lua", str(script),
             str(REPO_ROOT / "Quarto" / "_filters" / "video-manifest.lua")],
            capture_output=True, text=True)
        lines = out.stdout.splitlines()
        check("lua module loads", out.returncode == 0 and len(lines) == 6, out.stderr[-300:])
        if out.returncode == 0 and len(lines) == 6:
            check("relpath from Quarto/<genre>/ to the deck's videos dir",
                  lines[0] == "../../Figures/lectures/w02/videos", lines[0])
            check("relpath from a fixture dir to its own videos dir",
                  lines[1] == "videos", lines[1])
            check("month text", lines[2] == "Aug 2026|Dec 2025|x", lines[2])
            check("caption html: fragment class, escaping, meta order",
                  lines[3] == '<figcaption class="video-caption fragment">'
                              '<span class="video-caption-title">A &amp; B</span>'
                              '<span class="video-caption-meta">Pub &middot; May 2026 &middot; '
                              'autonomous &middot; 2x speed</span></figcaption>', lines[3])
            check("caption none -> nothing", lines[4] == "nil", lines[4])
            check("caption div for .video-full",
                  lines[5].startswith('<div class="video-caption">') and "teleoperated" in lines[5],
                  lines[5])

print("9. the committed fixture lock agrees with its manifest and release")
lock = json.loads((FIXTURE / "videos.json").read_text(encoding="utf-8"))
check("fixture lock: deck _fixtures/video, tag media-fixture-video, 3 clips",
      lock["deck"] == "_fixtures/video" and lock["release_tag"] == "media-fixture-video"
      and len(lock["videos"]) == 3)
check("fixture lock points at the Release, not local files",
      all(v["release_url"].startswith(media_prep.RELEASE_BASE + "/media-fixture-video/")
          and not v.get("local_only") for v in lock["videos"]))
check("fixture lock records every cut and agrees with its manifest fields",
      all("cut" in v for v in lock["videos"])
      and not media_prep.lock_mismatches(lock, media_prep.load_manifest(FIXTURE / "videos.yml")))
check("fixture release approvals and manifest fingerprint agree",
      len(media_prep.release_assets(deckpath.find_media(str(FIXTURE)))) == 6)

print("10. render-level: a bad slug or a missing lock aborts the render")
if not quarto:
    check("quarto on PATH", False, "skipped: quarto not found")
else:
    filters_dir = REPO_ROOT / "Quarto" / "_filters"

    def render_expect_abort(label, manifest, body, fragment):
        with tempfile.TemporaryDirectory() as td:
            qmd = Path(td) / "neg.qmd"
            qmd.write_text(f"""---
title: neg
video-manifest: {manifest}
format:
  revealjs:
    filters: [{filters_dir / 'slide-types.lua'}]
    shortcodes: [{filters_dir / 'video-card.lua'}]
---

{body}
""", encoding="utf-8")
            out = subprocess.run([quarto, "render", str(qmd)], cwd=td,
                                 capture_output=True, text=True)
            log = out.stdout + out.stderr
            # Quarto 1.11 repeats the diagnostic in its final ERROR summary.
            e_lines = [l for l in log.splitlines() if l.lstrip().startswith("(E) video-manifest:")]
            check(label,
                  out.returncode != 0 and not (Path(td) / "neg.html").exists()
                  and len(e_lines) == 1 and fragment in e_lines[0]
                  and "attempt to index a nil value" not in log
                  and "expected argument of type string" not in log,
                  f"exit={out.returncode} (E)-lines={e_lines!r}\n{log[-600:]}")

    render_expect_abort("unknown slug in {{< video-card >}}: exit 1, one (E), no html",
                        FIXTURE / "videos.json", "## S\n\n{{< video-card nosuchslug >}}\n",
                        "no clip with slug 'nosuchslug'")
    render_expect_abort("missing videos.json: exit 1, one (E), no html",
                        "/nonexistent/videos.json", "## S\n\n{{< video-card hook >}}\n",
                        "no lock file at")
    render_expect_abort('unknown @slug on .video-full: exit 1, one (E), no html',
                        FIXTURE / "videos.json", '## {.video-full video="@nope"}\n',
                        "no clip with slug 'nope'")

print("11. mixed manifest: public/classroom renders and recording release commands")
with tempfile.TemporaryDirectory() as td:
    root = Path(td).resolve() / "mixed"
    root.mkdir()
    home = deckpath.MediaHome(slug="test/mixed", name="mixed", manifest=root / "videos.yml")
    source = root / "private-origin-canary.mp4"
    shutil.copyfile(PLACEHOLDER, source)
    def clip(slug, policy):
        return f"""  - slug: {slug}
    title: "{slug} in motion"
    publisher: Example Lab
    source_url: https://example.org/{slug}
    published: 2026-05
    autonomy: claimed
    source: "{source}"
    caption: none
{policy}"""
    approved = clip("approved", "    redistribution: release\n")
    restricted = clip("restricted", "    redistribution: classroom\n")
    legacy = clip("unspecified", "")
    home.manifest.write_text("videos:\n" + approved + restricted + legacy, encoding="utf-8")
    logs = []
    lock = media_prep.prepare(home, local=True, log=logs.append)
    check("classroom entries have local files and carry no release URLs",
          all((home.videos_dir / v["file"]).is_file() and (home.videos_dir / v["poster_file"]).is_file()
              and "release_url" not in v and "poster_url" not in v for v in lock["videos"][1:]))
    media_prep.prepare(home, force=True, dry_run=True, log=logs.append)
    check("dry-run, encode logs and lock omit the private source path",
          source.name not in "\n".join(logs) and source.name not in home.lock.read_text())

    # The stub commands record all calls. Running this suite never needs
    # credentials and cannot create a Release or make an HTTP request.
    bin_dir = root / "stub-bin"
    bin_dir.mkdir()
    calls = root / "calls"
    for name in ("gh", "curl"):
        stub = bin_dir / name
        stub.write_text('#!/bin/sh\necho "' + name + ' $*" >> "$MEDIA_CALLS"\n' +
                        ('[ "$2" != view ]\n' if name == "gh" else 'printf 200\n'))
        stub.chmod(0o755)
    env = dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}", MEDIA_CALLS=str(calls))
    def release(*args, release_env=env):
        calls.write_text("")
        proc = subprocess.run(["bash", str(REPO_ROOT / "scripts/media_release.sh"), str(root), *args],
                              env=release_env, capture_output=True, text=True)
        return proc, calls.read_text().splitlines()
    proc, rows = release()
    uploads = [r.split() for r in rows if r.startswith("gh release upload")]
    check("uploader sends exactly the approved MP4/poster from a --local lock",
          proc.returncode == 0 and uploads == [["gh", "release", "upload", "media-" + root.name,
                                       str(home.videos_dir / "approved.mp4"),
                                       str(home.videos_dir / "approved-poster.jpg"), "--clobber"]]
          and not any("restricted" in r or "unspecified" in r for r in rows), repr(rows))
    proc, rows = release("--check")
    check("release --check probes only the approved URLs", proc.returncode == 0 and len(rows) == 2
          and all(r.startswith("curl ") and "/approved" in r for r in rows))

    # Use external URLs with unrelated filenames so these three probes each
    # isolate one public field. The manifest’s private source is never sent.
    from urllib.parse import quote
    guard = Path(td) / "private-release-terms"
    guarded = dict(env, PAPER2PR_PRIVATE_DENYLIST=str(guard))
    prepared = home.lock.read_text()
    probe = json.loads(prepared)
    probe["videos"][0]["release_url"] = "https://cdn.example.org/movie.mp4"
    probe["videos"][0]["poster_url"] = "https://cdn.example.org/" + quote("draft only") + ".jpg"
    home.lock.write_text(json.dumps(probe))
    for field, term in (("filename", "APPROVED.mp4"), ("release tag", "media-mixed"), ("URL", "draft only")):
        guard.write_text(term)
        for options in ((), ("--check",)):
            proc, rows = release(*options, release_env=guarded)
            output = (proc.stdout + proc.stderr).casefold()
            check(f"protected {field} stops {'checking' if options else 'upload'} before remote commands",
                  proc.returncode != 0 and not rows and term.casefold() not in output
                  and quote(term).casefold() not in output)
    guard.write_text(source.stem)
    proc, rows = release(release_env=guarded)
    check("a private authoring source permits public files and stays out of commands and logs",
          proc.returncode == 0 and any(row.startswith("gh release upload ") for row in rows)
          and source.stem not in (proc.stdout + proc.stderr + "\n".join(rows)))
    home.lock.write_text(prepared)

    filters = REPO_ROOT / "Quarto/_filters"
    qmd = root / "mixed.qmd"
    qmd.write_text(f"""---
title: Mixed media
video-manifest: videos.json
format:
  revealjs:
    filters: [{filters / "slide-types.lua"}]
    shortcodes: [{filters / "video-card.lua"}]
---
## Inline

{{{{< video-card approved >}}}}

{{{{< video-card restricted >}}}}

{{{{< video-card unspecified >}}}}

## {{#full .video-full video="@restricted" poster="private-poster-canary.jpg"}}

{{{{< video-caption restricted >}}}}

## {{#empty .video-full video="@unspecified"}}

## {{#published .video-full video="@approved"}}
""", encoding="utf-8")
    if quarto:
        def render(*options):
            return subprocess.run([quarto, "render", qmd.name, *options], cwd=root,
                                  capture_output=True, text=True)
        result = render()
        html = qmd.with_suffix(".html").read_text() if not result.returncode else ""
        check("default public render links both restricted cards and both full-slide variants",
              html.count('href="https://example.org/restricted"') == 2
              and html.count('href="https://example.org/unspecified"') == 2
              and html.count('data-video-slug="restricted"') == 2
              and 'approved.mp4' in html and 'videos/approved.mp4' not in html
              and all(secret not in html for secret in
                      (source.name, "restricted.mp4", "restricted-poster.jpg", "unspecified.mp4",
                       "unspecified-poster.jpg", "private-poster-canary.jpg")), result.stderr[-300:])
        page = Path("slides/test/mixed.html")
        if html:
            check_site_assets.validate_public_videos(page, html, home)
            check("public cards and backgrounds carry approved manifest playback",
                  html.count('data-redistribution="release"') == 2)
            try:
                altered = html.replace(lock["videos"][0]["release_url"], "https://example.org/unapproved.mp4")
                check_site_assets.validate_public_videos(page, altered, home)
                check("a manifest marker cannot approve a different source", False)
            except ValueError as exc:
                check("a manifest marker cannot approve a different source", "public video" in str(exc))
        result = render("-M", "delivery:classroom")
        html = qmd.with_suffix(".html").read_text() if not result.returncode else ""
        check("classroom + --local renders playable local cards and full-slide backgrounds",
              all(f'data-src="videos/{s}.mp4"' in html for s in ("approved", "restricted", "unspecified"))
              and 'data-background-video="videos/restricted.mp4"' in html
              and 'data-background-video="videos/unspecified.mp4"' in html, result.stderr[-300:])
        if result.returncode == 0:
            shutil.copyfile(home.videos_dir / "restricted-poster.jpg", root / "private-poster-canary.jpg")
            with browser.browser_page(qmd.with_suffix(".html").as_uri()) as page:
                page.evaluate("Reveal.slide(1)")
                page.wait_for("""(() => {
                    const video = Reveal.getCurrentSlide().querySelector('[data-video-slug="restricted"] video');
                    return video && video.videoWidth === 1280 && !video.paused && video.currentTime > 0.1;
                })()""", "classroom card did not play its local clip")
                page.evaluate("Reveal.slide(2)")
                page.wait_for("""(() => {
                    const video = Reveal.getSlideBackground(2).querySelector('video');
                    return video && video.videoWidth === 1280 && !video.paused && video.currentTime > 0.1;
                })()""", "classroom background did not play its local clip")
                check("Chrome decodes and advances both local classroom treatments", True)
        media_prep.prepare(home, log=logs.append)
        result = render("-M", "delivery:classroom")
        html = qmd.with_suffix(".html").read_text() if not result.returncode else ""
        check("classroom without --local still plays restricted media locally",
              'data-src="videos/restricted.mp4"' in html and lock["videos"][0]["release_url"] in html)
    original = home.lock.read_text()
    forged = json.loads(original)
    forged["videos"][0]["poster_file"] = "restricted-poster.jpg"
    home.lock.write_text(json.dumps(forged))
    proc, rows = release()
    check("a renamed locked poster cannot enter the upload list", proc.returncode != 0 and not rows)
    home.lock.write_text(original)
    # Even a checkout in which the stale lock is newer cannot retain a
    # withdrawn approval. Check the website audit's restricted URL inventory.
    home.manifest.write_text(home.manifest.read_text().replace("redistribution: release",
                                                               "redistribution: classroom"))
    os.utime(home.manifest, (1, 1))
    proc, rows = release()
    check("a stale approval fails before any gh or curl call", proc.returncode != 0 and not rows)
    check("the independent site audit can detect revoked Release URLs",
          lock["videos"][0]["release_url"] in media_prep.restricted_media_urls(home))
    if quarto:
        result = render("-M", "delivery:public")
        check("public render rejects a revoked approval in a newer lock", result.returncode != 0
              and "videos.json is stale" in result.stderr + result.stdout)
    media_prep.prepare(home, log=logs.append)
    proc, rows = release()
    check("a classroom-only manifest succeeds with zero network calls", proc.returncode == 0 and not rows)

print()
if fail:
    print("FAIL")
    sys.exit(1)
print("all media tests passed")
