#!/usr/bin/env python3
"""Fail the build when a deployed page points at Release media that is not there.

A deck's clips and posters live on a public GitHub Release, never in git
(scripts/media_prep.py writes the URLs, scripts/media_release.sh uploads the
files). check_site_assets.py deliberately skips every external URL, so the
one state it cannot see is the one this repo actually ships in: a page whose
Release URLs are perfectly well-formed and answer 404 because nobody ran
media_release.sh. Merging is publishing here, so that reaches a lecture room
as a black slide with nothing having failed anywhere.

This checks only URLs on GitHub's own Release download host -- the ones this
repo mints and can therefore be held responsible for. A third-party CDN link
in a deck is not touched: an outage there is not a broken build.

Usage:
    python3 scripts/check_release_media.py _site
    python3 scripts/check_release_media.py _site --timeout 20

Exit 0 when every Release URL answers 200 (or when a page references none),
1 when any does not, 2 when the site root is missing.
"""
from __future__ import annotations

import argparse
import html
import os
import re
import sys
import time
import urllib.error
import urllib.request

RELEASE_URL_RE = re.compile(
    r"https://github\.com/[^/\s\"'<>]+/[^/\s\"'<>]+/releases/download/[^\s\"'<>)]+")

ATTEMPTS = 3
BACKOFF_S = 5


def urls_in_site(site_root: str) -> dict:
    """{url: [pages that reference it]}, pages relative to the site root."""
    found: dict = {}
    for directory, _sub, names in os.walk(site_root):
        for name in names:
            if not name.endswith((".html", ".css")):
                continue
            path = os.path.join(directory, name)
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read()
            for raw in RELEASE_URL_RE.findall(text):
                url = html.unescape(raw).rstrip(")\"'")
                found.setdefault(url, [])
                page = os.path.relpath(path, site_root)
                if page not in found[url]:
                    found[url].append(page)
    return found


def status_of(url: str, timeout: float) -> str:
    """The HTTP status the browser would get, following the redirect GitHub
    answers a Release asset with. A transport error is retried: a flaky
    network must not read as a missing file."""
    last = "000"
    for attempt in range(ATTEMPTS):
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return str(resp.status)
        except urllib.error.HTTPError as e:
            # A real answer from the server: 404 is the finding, not an error.
            return str(e.code)
        except (urllib.error.URLError, OSError, ValueError) as e:
            last = f"000 ({e})"
        if attempt < ATTEMPTS - 1:
            time.sleep(BACKOFF_S)
    return last


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("site_root", nargs="?", default="_site")
    ap.add_argument("--timeout", type=float, default=20.0)
    args = ap.parse_args()

    if not os.path.isdir(args.site_root):
        print(f"no such directory: {args.site_root}", file=sys.stderr)
        return 2

    found = urls_in_site(args.site_root)
    if not found:
        print(f"no Release media referenced under {args.site_root}")
        return 0

    missing = []
    for url in sorted(found):
        code = status_of(url, args.timeout)
        if code == "200":
            print(f"  200  {url}")
        else:
            print(f"  {code}  {url}")
            missing.append((url, found[url], code))

    if missing:
        print(f"\n{len(missing)} Release asset(s) referenced by the site do not "
              f"answer 200:", file=sys.stderr)
        for url, pages, code in missing:
            print(f"   {code}  {url}", file=sys.stderr)
            for page in pages:
                print(f"        referenced by {page}", file=sys.stderr)
        print("\nUpload them: bash scripts/media_release.sh <Deck>   "
              "(or `--check` to verify without uploading).", file=sys.stderr)
        return 1

    print(f"all {len(found)} Release asset(s) answer 200")
    return 0


if __name__ == "__main__":
    sys.exit(main())
