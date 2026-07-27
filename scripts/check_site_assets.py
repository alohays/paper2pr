#!/usr/bin/env python3
"""Fail the build if a deployed page references a local file that is not there.

The assemble step in .github/workflows/deploy.yml hand-picks what goes into
_site. Anything a deck references by relative path but nobody thought to copy
becomes a silent 404 -- the page still loads and looks fine, so the break only
shows up when someone interacts with it. That is exactly how
`robottt-stepper.js` shipped missing: every slide rendered correctly and only
the arrow-key stepping was dead.

Usage:  python3 scripts/check_site_assets.py _site
"""
import os
import re
import sys
from urllib.parse import unquote, urlparse

# `<source src>` in the task-video blocks lists NVIDIA's CDN first and a local
# copy second. The local copy is deliberately not deployed (the media is not in
# git), so a missing videos/*.mp4 is by design, not an oversight.
ALLOW_MISSING = (
    re.compile(r"^videos/.*\.mp4$"),
)

REF = re.compile(r'(?:src|href)\s*=\s*"([^"]+)"')


def is_external(url):
    return (url.startswith(("data:", "#", "mailto:", "javascript:"))
            or bool(urlparse(url).scheme) or url.startswith("//"))


def check(site_root):
    missing = []
    checked = 0
    for dirpath, _dirnames, filenames in os.walk(site_root):
        for name in filenames:
            if not name.endswith(".html"):
                continue
            page = os.path.join(dirpath, name)
            with open(page, encoding="utf-8", errors="replace") as f:
                html = f.read()
            for raw in sorted(set(REF.findall(html))):
                if is_external(raw):
                    continue
                rel = unquote(raw.split("#")[0].split("?")[0])
                if not rel:
                    continue
                if any(p.match(rel) for p in ALLOW_MISSING):
                    continue
                checked += 1
                target = os.path.normpath(os.path.join(dirpath, rel))
                if not os.path.exists(target):
                    missing.append((os.path.relpath(page, site_root), rel))
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
              ".github/workflows/deploy.yml.", file=sys.stderr)
        return 1

    print(f"all {checked} local references resolve under {site_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
