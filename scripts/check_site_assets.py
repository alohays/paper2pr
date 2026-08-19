#!/usr/bin/env python3
"""Fail the build if a deployed page references a local file that is not there.

The assemble step in .github/workflows/deploy.yml hand-picks what goes into
_site. Anything a deck references by relative path but nobody thought to copy
becomes a silent 404 -- the page still loads and looks fine, so the break only
shows up when someone interacts with it. That is exactly how
`robottt-stepper.js` shipped missing: every slide rendered correctly and only
the arrow-key stepping was dead.

Two kinds of failure:
  * a local reference whose file is not under the site root (the original
    case above);
  * a reference into Figures/**/videos/ -- a deck's trimmed clips and posters
    live on a GitHub Release (scripts/media_release.sh), never in git and
    never in the deployed tree, so a page that still points there was built
    from a videos.json written with `media_prep.py --local` (authoring mode).
    That fails even when the file happens to exist in a local preview, which
    it never will on CI.

Usage:  python3 scripts/check_site_assets.py _site

Self-test of the rules (what scripts/test_media.py asserts):
  >>> LOCAL_MEDIA.search("../../Figures/lectures/w02/videos/hook.mp4") is not None
  True
  >>> LOCAL_MEDIA.search("../../Figures/lectures/w02/hook-poster.jpg") is None
  True
  >>> any(p.match("../videos/task1.mp4") for p in ALLOW_MISSING)
  True
  >>> is_external("https://github.com/alohays/paper2pr/releases/download/media-x/a.mp4")
  True
"""
import os
import re
import sys
from urllib.parse import unquote, urlparse

# `<source src>` in the task-video blocks lists NVIDIA's CDN first and a local
# copy second. The local copy is deliberately not deployed (the media is not in
# git), so a missing videos/*.mp4 is by design, not an oversight.
ALLOW_MISSING = (
    # The `../` prefix appeared when decks moved into Quarto/<genre>/; the
    # reference is still the same deliberately-undeployed local fallback.
    re.compile(r"^(?:\.\./)*videos/.*\.mp4$"),
)

# Local media of a deck: Figures/<genre>/<deck>/videos/<slug>.mp4 and the
# posters beside it. Gitignored, hosted on the Release; a deployed page must
# reference the Release URL (external) instead. Matched on the raw reference
# so a `../../Figures/...` from slides/<genre>/ is caught before resolution.
LOCAL_MEDIA = re.compile(r"(?:^|/)Figures/[^/]+/[^/]+/videos/")

# src/href covers <script>, <link>, <img>, <source>. RevealJS also pulls media
# in through data-background-* attributes (and data-src, its lazy-load hook
# that the video-card shortcode uses for <source>), <video> through poster
# and data-background-poster, and stylesheets through url() -- a 404 in any
# of them is just as invisible as the one this script was written for.
REF = re.compile(
    r'(?:(?:src|data-src|href|poster|data-background-image|data-background-video'
    r'|data-background-poster|data-background-iframe)\s*=\s*"([^"]+)"'
    r'|url\(\s*["\']?([^"\')]+?)["\']?\s*\))'
)


def is_external(url):
    return (url.startswith(("data:", "#", "mailto:", "javascript:"))
            or bool(urlparse(url).scheme) or url.startswith("//"))


def resolve(site_root, page_dir, rel):
    """Where the browser would look, or None if it escapes the site.

    A root-relative `/x` means the site root to a browser, not the filesystem
    root, and a `../../x` that climbs out of _site would resolve against the CI
    workspace here and pass while 404ing once deployed. Both have to be handled
    explicitly or the gate lies in one direction or the other.
    """
    base = site_root if rel.startswith("/") else page_dir
    target = os.path.normpath(os.path.join(base, rel.lstrip("/")))
    root = os.path.normpath(site_root)
    if os.path.commonpath([root, target]) != root:
        return None
    return target


def refs_in(path):
    """-> the local paths a page or stylesheet asks the browser to fetch."""
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    out = []
    for m in REF.findall(text):
        for raw in m:
            raw = raw.strip()
            if not raw or is_external(raw):
                continue
            rel = unquote(raw.split("#")[0].split("?")[0]).strip()
            if rel:
                out.append(rel)
    return sorted(set(out))


def check(site_root):
    """Walk pages, then only the stylesheets those pages actually link.

    Scanning every .css on disk sounds more thorough but is wrong here:
    <name>_files accumulates hashed bundles from earlier renders, and those
    orphans carry stale paths nobody ever requests. Following links from the
    HTML checks what actually ships to a reader.
    """
    pages = [os.path.join(d, n)
             for d, _sub, names in os.walk(site_root)
             for n in names if n.endswith(".html")]

    missing = []
    checked = 0
    queue = [(p, False) for p in pages]
    scanned = set()
    while queue:
        page, _ = queue.pop()
        if page in scanned:
            continue
        scanned.add(page)
        here = os.path.dirname(page)
        for rel in refs_in(page):
            if any(p.match(rel) for p in ALLOW_MISSING):
                continue
            checked += 1
            if LOCAL_MEDIA.search(rel):
                missing.append((os.path.relpath(page, site_root),
                                rel + "   (local media: never deployed; re-run "
                                      "media_prep.py without --local)"))
                continue
            target = resolve(site_root, here, rel)
            if target is None:
                missing.append((os.path.relpath(page, site_root),
                                rel + "   (escapes the site root)"))
            elif not os.path.exists(target):
                missing.append((os.path.relpath(page, site_root), rel))
            elif target.endswith(".css"):
                queue.append((target, True))
    return checked, missing


def main():
    site_root = sys.argv[1] if len(sys.argv) > 1 else "_site"
    if not os.path.isdir(site_root):
        print(f"no such directory: {site_root}", file=sys.stderr)
        return 2

    checked, missing = check(site_root)
    if missing:
        print(f"{len(missing)} referenced file(s) are not in {site_root}:",
              file=sys.stderr)
        for page, rel in missing:
            print(f"   {page}  ->  {rel}", file=sys.stderr)
        print("\nAdd them to the 'Assemble site' step in "
              ".github/workflows/deploy.yml -- or, for local media, point the "
              "deck at its Release (python3 scripts/media_prep.py <deck>, "
              "without --local).", file=sys.stderr)
        return 1

    print(f"all {checked} local references resolve under {site_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
