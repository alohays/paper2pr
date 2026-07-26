#!/usr/bin/env python3
"""Push the presenter script into the deck's speaker notes.

The script in
  Quarto/_script/RoboTTT-script.md
is the master. Each of its `### S<n> | <slide title>` sections replaces the
`::: {.notes}` block of the matching `## <slide title>` in
  Quarto/RoboTTT.qmd
so the RevealJS presenter view (press S) shows the words to say.

Sections are matched on the heading text, not on position, so reordering
slides in either file cannot silently misalign them. Anything unmatched is a
hard error rather than a skipped slide.

Usage:  python3 scripts/sync_notes.py [--check]
        --check reports drift and exits non-zero instead of writing.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QMD = os.path.join(HERE, "Quarto", "RoboTTT.qmd")
SCRIPT = os.path.join(HERE, "Quarto", "_script", "RoboTTT-script.md")

TITLE_KEY = "(title slide)"


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_script():
    """-> {slide title: body}, in file order."""
    text = read(SCRIPT)
    _, _, rest = text.partition("\n---\n")
    out = {}
    for m in re.finditer(r"^### (S\d+) \| (.+?)$\n(.*?)(?=^---$|\Z)",
                         rest, re.S | re.M):
        title = m.group(2).strip()
        if title in out:
            raise SystemExit(f"duplicate section title in script: {title}")
        out[title] = m.group(3).strip()
    return out


def heading_title(line):
    """`## Foo {.smaller}` -> `Foo`"""
    t = re.sub(r"^##\s+", "", line)
    return re.sub(r"\s*\{[^}]*\}\s*$", "", t).strip()


def splice(qmd, bodies):
    """Replace every slide's notes block. Returns (new_qmd, matched titles)."""
    matched = set()

    def repl(m):
        title = heading_title(m.group(1))
        body = bodies.get(title)
        if body is None:
            return m.group(0)
        matched.add(title)
        return f"{m.group(1)}\n{m.group(2)}::: {{.notes}}\n{body}\n:::\n"

    # a slide runs from its `##` heading to its notes block; the notes block is
    # always the last thing in a slide, and `.slidebody` uses five colons, so a
    # three-colon `:::` on its own line closes the notes and nothing else.
    # `.` is DOTALL here, so the heading line must be matched with [^\n]+
    pattern = (r"^(## [^\n]+)$\n(.*?)^::: \{\.notes\}\n.*?\n^:::\n")
    out = re.sub(pattern, repl, qmd, flags=re.S | re.M)
    return out, matched


def splice_title_slide(qmd, body):
    """Attach the opening to the YAML-generated title slide.

    A `::: {.notes}` div before the first `##` does not attach to the title
    slide; Quarto turns it into its own blank slide. RevealJS's notes plugin
    also reads a `data-notes` attribute off the section and renders it with
    `white-space: pre-wrap`, so paragraph breaks survive. Put it there.
    """
    lines = qmd.split("\n")
    try:
        head = next(i for i, l in enumerate(lines)
                    if l == "title-slide-attributes:")
    except StopIteration:
        raise SystemExit("no title-slide-attributes block in the front matter")

    # The block runs until the next line at column 0. Blank lines belong to it
    # too, because a `data-notes: |` scalar contains paragraph breaks; scanning
    # only for indented lines would stop at the first one and orphan the rest.
    end = head + 1
    while end < len(lines) and (lines[end] == "" or lines[end][:1] in " \t"):
        end += 1
    while end > head + 1 and lines[end - 1] == "":
        end -= 1

    # keep the two-space keys, drop data-notes and any block-scalar body
    keep = [l for l in lines[head + 1:end]
            if re.match(r"  \S", l) and not l.startswith("  data-notes:")]
    body_lines = ["    " + l if l.strip() else "" for l in body.split("\n")]
    block = (["title-slide-attributes:"] + keep
             + ["  data-notes: |"] + body_lines)
    return "\n".join(lines[:head] + block + lines[end:])


def drop_stale_title_div(qmd):
    """Remove the notes div an earlier version of this script inserted."""
    marker = "<!-- title-slide notes, managed by scripts/sync_notes.py -->"
    pat = re.compile(r"\n*" + re.escape(marker) + r"\n::: \{\.notes\}\n.*?\n:::\n",
                     re.S)
    return pat.sub("\n", qmd)


def main():
    check = "--check" in sys.argv
    bodies = parse_script()
    title_body = bodies.pop(TITLE_KEY, None)
    if title_body is None:
        raise SystemExit(f"script has no '{TITLE_KEY}' section")

    qmd = drop_stale_title_div(read(QMD))
    out, matched = splice(qmd, bodies)
    out = splice_title_slide(out, title_body)

    unmatched = sorted(set(bodies) - matched)
    if unmatched:
        print("script sections with no matching slide heading:", file=sys.stderr)
        for t in unmatched:
            print(f"   {t}", file=sys.stderr)
        return 1

    deck_titles = {heading_title(l) for l in qmd.splitlines()
                   if l.startswith("## ")}
    missing = sorted(deck_titles - set(bodies))
    if missing:
        print(f"{len(missing)} slides keep their existing notes "
              f"(no script section):")
        for t in missing:
            print(f"   {t}")

    if check:
        if out != qmd:
            print("\nDRIFT: deck notes differ from the script", file=sys.stderr)
            return 1
        print("\nin sync")
        return 0

    with open(QMD, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"\nsynced {len(matched) + 1} notes blocks into "
          f"{os.path.relpath(QMD, HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
