#!/usr/bin/env python3
"""Thin shim over scripts/shoot_slides.py, kept for the fixture wrappers.

Usage: python3 shoot.py <deck.html> <max_slides> <out_dir> <prefix>

The screenshot engine lives in scripts/shoot_slides.py (one engine, one
place); this file only translates the old positional CLI the fixture
wrappers (theme-mockups/shoot.sh) still use. New callers should invoke
scripts/shoot_slides.py directly -- it also resolves deck names and
re-renders a stale html.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import shoot_slides  # noqa: E402


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__.strip())
    html, n, out_dir, prefix = sys.argv[1:5]
    return shoot_slides.main(
        [html, "--max", n, "--out", out_dir, "--prefix", prefix])


if __name__ == "__main__":
    sys.exit(main())
