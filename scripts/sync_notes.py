#!/usr/bin/env python3
"""Push the presenter scripts into the deck's speaker notes.

The masters for a deck are
  Quarto/_script/<genre>/<deck>-script.md     main deck, the words to say
  Quarto/_script/<genre>/<deck>-appendix.md   appendix slides, for jumping to
Each `### <id> | <slide title>` section becomes the `::: {.notes}` block of the
matching `## <slide title>` in
  Quarto/<genre>/<deck>.qmd
so the RevealJS presenter view (press S) shows them beside the slide.

This has to REBUILD, not just replace. `.gitattributes` runs a clean filter
that strips notes on the way into git, so the notes live only in the working
tree -- any checkout, stash pop, or branch switch rewrites the qmd and wipes
every one of them. Running this script has to be enough to get them all back.
That is also why the appendix notes need a master file even though they are
never read aloud.

Sections are matched on the heading text, not on position, so reordering
slides in either file cannot silently misalign them. Anything unmatched is a
hard error rather than a skipped slide.

Usage:  python3 scripts/sync_notes.py [Deck] [--check]
        Deck defaults to RoboTTT, the only deck with masters so far.
        --check reports drift and exits non-zero instead of writing.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "scripts"))
import deckpath  # noqa: E402


def resolve_deck(argv):
    """-> (qmd path, [script master paths]) for the deck named on the CLI."""
    positional = [a for a in argv[1:] if not a.startswith("-")]
    ref = positional[0] if positional else "RoboTTT"
    try:
        deck = deckpath.find(ref)
    except (deckpath.DeckNotFound, deckpath.AmbiguousDeck) as e:
        raise SystemExit(f"error: {e}")
    return str(deck.qmd), [
        os.path.join(str(deck.script_dir), f"{deck.name}-script.md"),
        os.path.join(str(deck.script_dir), f"{deck.name}-appendix.md"),
    ]


QMD, SCRIPTS = resolve_deck(sys.argv)

TITLE_KEY = "(title slide)"

NOTES_RE = re.compile(r"\n*^::: \{\.notes\}\n.*?\n^:::\n", re.S | re.M)
SLIDE_RE = re.compile(r"^## [^\n]*$", re.M)
# an HTML comment sitting at the end of a slide labels the NEXT one, so notes
# belong before it rather than after
TRAILING_COMMENT_RE = re.compile(r"\n(<!--[^\n]*-->)\s*$")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_scripts():
    """-> {slide title: body}, across every master file."""
    out = {}
    for path in SCRIPTS:
        if not os.path.exists(path):
            raise SystemExit(f"missing script master: {path}")
        _, _, rest = read(path).partition("\n---\n")
        for m in re.finditer(r"^### \S+ \| (.+?)$\n(.*?)(?=^---$|\Z)",
                             rest, re.S | re.M):
            title = m.group(1).strip()
            if title in out:
                raise SystemExit(f"duplicate section title in scripts: {title}")
            out[title] = m.group(2).strip()
    return out


def heading_title(line):
    """`## Foo {.smaller}` -> `Foo`"""
    t = re.sub(r"^##\s+", "", line)
    return re.sub(r"\s*\{[^}]*\}\s*$", "", t).strip()


def splice(qmd, bodies):
    """Set every scripted slide's notes block. Returns (new_qmd, matched)."""
    matched = set()
    starts = [m.start() for m in SLIDE_RE.finditer(qmd)]
    if not starts:
        raise SystemExit("no `## ` slide headings in the deck")

    bounds = starts + [len(qmd)]
    out = [qmd[:starts[0]]]
    for i, start in enumerate(starts):
        head, _, rest = qmd[start:bounds[i + 1]].partition("\n")
        body = bodies.get(heading_title(head))
        if body is None:
            # not scripted (nothing should be, but leave it alone if so)
            out.append(head + "\n" + rest)
            continue
        matched.add(heading_title(head))

        rest = NOTES_RE.sub("\n", rest)
        out.append(head + "\n" + insert_notes(rest, body))
    return "".join(out), matched


def insert_notes(rest, body):
    """Put a notes block at the end of a notes-free slide body.

    The placement is pinned by the clean filter in scripts/strip_qmd_notes.py,
    which collapses `\\n::: {.notes}\\n...\\n:::\\n` back to a single newline.
    Giving up one newline from the blank run after the body makes that round
    trip byte-exact, so a synced working tree still reads as clean to git
    instead of showing permanent whitespace churn.
    """
    m = TRAILING_COMMENT_RE.search(rest)
    # a comment at the end of a slide labels the NEXT one, so stay above it
    head_part, tail = (rest[:m.start()], rest[m.start():]) if m else (rest, "")

    stripped = head_part.rstrip("\n")
    gap = head_part[len(stripped):] or "\n"
    return f"{stripped}\n::: {{.notes}}\n{body}\n:::\n{gap[1:]}{tail}"


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


def main():
    check = "--check" in sys.argv
    bodies = parse_scripts()
    title_body = bodies.pop(TITLE_KEY, None)
    if title_body is None:
        raise SystemExit(f"scripts have no '{TITLE_KEY}' section")

    qmd = read(QMD)
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
        print(f"{len(missing)} slides have no script section "
              f"(their notes are left as-is):")
        for t in missing:
            print(f"   {t}")

    # The notes must be invisible to git. Prove it rather than trust it: run
    # the result back through the same clean filter and require the notes-free
    # form to be unchanged, so a synced tree never shows as dirty.
    sys.path.insert(0, os.path.join(HERE, "scripts"))
    from strip_qmd_notes import strip_notes
    if strip_notes(out) != strip_notes(qmd):
        print("BUG: syncing changed the deck outside the notes blocks.",
              file=sys.stderr)
        return 2

    if check:
        if out != qmd:
            print("DRIFT: deck notes differ from the scripts", file=sys.stderr)
            return 1
        print("in sync")
        return 0

    with open(QMD, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"synced {len(matched) + 1} notes blocks into "
          f"{os.path.relpath(QMD, HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
