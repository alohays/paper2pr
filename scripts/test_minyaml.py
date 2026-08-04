#!/usr/bin/env python3
"""Check the stdlib YAML parser against PyYAML, and against its own promises.

The point of scripts/minyaml.py is that the profile system stops depending on
a package nobody declared. That trade is only safe if the parser agrees with
the real one on the files this repo actually has, so the first section here
is a differential test: every config file in the repo, parsed both ways,
compared exactly. It skips itself with a clear message when PyYAML is absent
rather than passing quietly -- a green run that checked nothing is the bug
this whole file exists to avoid.

The second section pins the behaviour that matters even when PyYAML is gone:
unsupported syntax must raise, not be guessed at.

Usage: python3 scripts/test_minyaml.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import minyaml  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
failures: list[str] = []


def check(label: str, ok: bool, detail: str = ""):
    print(f"  {'ok   ' if ok else 'FAIL '} {label}")
    if not ok:
        failures.append(f"{label}{': ' + detail if detail else ''}")


def config_files() -> list[Path]:
    found = sorted((REPO_ROOT / ".claude" / "rules" / "slide-profiles")
                   .glob("*.yml"))
    found += sorted((REPO_ROOT / "Quarto").glob("*/*.deck.yml"))
    return found


print("1. Same result as PyYAML on every config file in the repo")
try:
    import yaml
except ImportError:
    check("PyYAML available to compare against", False,
          "install PyYAML to run the differential test")
else:
    files = config_files()
    check(f"found config files to compare ({len(files)})", bool(files))
    for path in files:
        rel = path.relative_to(REPO_ROOT)
        try:
            mine = minyaml.load_path(path)
        except minyaml.MinYamlError as e:
            check(str(rel), False, f"minyaml refused it: {e}")
            continue
        theirs = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        check(str(rel), mine == theirs,
              f"differs; mine={mine!r} theirs={theirs!r}")

print("2. The shapes these files are built from")
cases = [
    ("scalars and inline comments",
     'profile: lecture\nduration_min: 60  # minutes\nstrict: true\n',
     {"profile": "lecture", "duration_min": 60, "strict": True}),
    ("nested mapping",
     'bullets:\n  max_per_slide: 4\n  max_with_figure: 3\n',
     {"bullets": {"max_per_slide": 4, "max_with_figure": 3}}),
    ("flow sequence",
     'audience:\n  prior: [w01, w02]\n',
     {"audience": {"prior": ["w01", "w02"]}}),
    ("block sequence at the key's own indent",
     'prior:\n- w01\n- w02\n',
     {"prior": ["w01", "w02"]}),
    ("quoted string keeps its hash",
     'title: "Rewards # and penalties"\n',
     {"title": "Rewards # and penalties"}),
    ("literal block keeps newlines",
     'guidance: |\n  one\n  two\n',
     {"guidance": "one\ntwo\n"}),
    ("folded block joins lines, keeps paragraphs",
     'description: >\n  one\n  two\n\n  three\n',
     {"description": "one two\nthree\n"}),
    ("null and empty",
     'series_index:\nname: ~\n',
     {"series_index": None, "name": None}),
]
for label, text, expected in cases:
    try:
        got = minyaml.loads(text, "<case>")
    except minyaml.MinYamlError as e:
        check(label, False, f"raised {e}")
        continue
    check(label, got == expected, f"got {got!r}, wanted {expected!r}")

print("3. Anything outside the subset raises instead of being guessed at")
bad = [
    ("anchors", 'base: &a\n  x: 1\n'),
    ("aliases", 'x: *a\n'),
    ("flow mapping", 'audience: {assumes: none}\n'),
    ("tab indentation", 'bullets:\n\tmax_per_slide: 4\n'),
    ("missing colon", 'just a line\n'),
    ("document marker", '---\nprofile: lecture\n'),
    ("unterminated quote", 'title: "unclosed\n'),
    ("duplicate key", 'profile: a\nprofile: b\n'),
]
for label, text in bad:
    try:
        got = minyaml.loads(text, "<case>")
    except minyaml.MinYamlError:
        check(label, True)
    else:
        check(label, False, f"parsed to {got!r} instead of raising")

print()
if failures:
    print(f"FAIL ({len(failures)})")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("PASS")
