#!/usr/bin/env python3
"""Backup and restore speaker notes for QMD files.

Speaker notes live in the working directory but are stripped by git clean
filters. This script backs them up to .speaker-notes/ (gitignored) so they
can be restored after git checkout or on a new machine.

Notes live in two places (see scripts/strip_qmd_notes.py), and both are
backed up: `::: {.notes}` divs in the body, and the `data-notes:` block
under `title-slide-attributes:` that carries the title slide's notes.

Restore is exact when the qmd has not changed since the backup: the backup
records where each block sat in the *stripped* text (which is what a
checkout puts in the working tree), so re-inserting reproduces the original
byte for byte. That precision exists for lecture decks, where notes for
shared include slides sit after an `{{< include >}}` line with no heading of
their own -- a restore keyed on "nearest preceding heading" (the old backup
format) dropped every note of a heading-less stretch onto one wrong slide.
If the qmd HAS changed since the backup, restore falls back to anchoring
each note to the line it originally followed, and says so.

Old list-format backups still restore through the original heading-keyed
path.

Usage:
    python3 scripts/backup_notes.py backup DreamZero
    python3 scripts/backup_notes.py restore DreamZero
    python3 scripts/backup_notes.py backup              # all QMD files
    python3 scripts/backup_notes.py restore              # all backed-up files
"""

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deckpath  # noqa: E402
import strip_qmd_notes  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
QUARTO_DIR = REPO_ROOT / "Quarto"
NOTES_DIR = REPO_ROOT / ".speaker-notes"

# The exact block the clean filter removes (strip_qmd_notes.strip_note_divs
# replaces each match with a single newline). Group 1 is the note text.
BLOCK_RE = re.compile(r'\n::: \{\.notes\}\n(.*?)\n:::\n', re.DOTALL)
DATA_NOTES_RE = re.compile(r'^(\s*)data-notes:')


def _sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def resolve(name: str) -> deckpath.Deck:
    """Find a deck by bare name, genre/name, or qmd path."""
    try:
        return deckpath.find(name)
    except (deckpath.DeckNotFound, deckpath.AmbiguousDeck) as e:
        sys.exit(f"Error: {e}")


def find_qmd(name: str) -> Path:
    """Find QMD file by deck name."""
    path = resolve(name).qmd
    if not path.exists():
        sys.exit(f"Error: {path} not found")
    return path


def _anchor(content: str, start: int) -> tuple[str, int]:
    """The nearest non-blank line before offset `start`, and which
    occurrence of that exact line it is (1-based, from the top). The
    fallback restore re-finds the note's place by this pair, which works
    for include-slide notes exactly as well as for headed slides."""
    before = content[:start].split("\n")
    for i in range(len(before) - 1, -1, -1):
        if before[i].strip():
            return before[i], before[: i + 1].count(before[i])
    return "", 1


def extract(content: str) -> tuple[str, list[dict], list[dict]]:
    """Take the notes out the same way the clean filter does, remembering
    where each block sat. Returns (stripped, title_notes, div_notes):
    div_notes offsets index into the div-stripped text (title notes still
    in place); title_notes line indices index into the fully stripped
    text's line list. Restore inverts in the opposite order."""
    div_notes = []
    removed = 0
    for m in BLOCK_RE.finditer(content):
        line, ordinal = _anchor(content, m.start())
        div_notes.append({
            "anchor": line,
            "anchor_ordinal": ordinal,
            # The single "\n" the filter leaves behind sits at this offset.
            "stripped_offset": m.start() - removed,
            "content": m.group(1),
        })
        removed += len(m.group(0)) - 1
    stripped1 = BLOCK_RE.sub("\n", content)

    # Mirror strip_qmd_notes.strip_title_slide_notes line by line, keeping
    # what it drops and where (index into the output line list).
    lines = stripped1.split("\n")
    out = []
    title_notes = []
    i = 0
    while i < len(lines):
        m = DATA_NOTES_RE.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        indent = len(m.group(1))
        start = i
        i += 1
        while i < len(lines):
            line = lines[i]
            if line.strip() and len(line) - len(line.lstrip()) <= indent:
                break
            i += 1
        title_notes.append({"at_line": len(out), "lines": lines[start:i]})
    stripped2 = "\n".join(out)

    # The whole design rests on this mirroring the filter exactly.
    assert stripped2 == strip_qmd_notes.strip_notes(content), \
        "backup_notes.extract disagrees with strip_qmd_notes.strip_notes"
    return stripped2, title_notes, div_notes


def backup(name: str) -> None:
    """Backup notes from QMD to .speaker-notes/."""
    qmd_path = find_qmd(name)
    content = qmd_path.read_text(encoding="utf-8")
    stripped, title_notes, div_notes = extract(content)

    if not div_notes and not title_notes:
        print(f"No notes found in {qmd_path.name}")
        return

    # Backups are genre-scoped like everything else a deck owns, so a lecture
    # and a paper review can share a name without overwriting each other.
    out_path = resolve(name).notes_json
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "format": 2,
        "qmd": str(qmd_path.relative_to(REPO_ROOT)),
        "stripped_sha1": _sha1(stripped),
        "original_sha1": _sha1(content),
        "title_notes": title_notes,
        "notes": div_notes,
    }
    out_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    extra = " + title-slide notes" if title_notes else ""
    print(f"Backed up {len(div_notes)} notes{extra} to {out_path}")


def _reinsert_exact(stripped: str, data: dict) -> str:
    """Invert extract() on a byte-identical stripped file."""
    lines = stripped.split("\n")
    added = 0
    for block in data.get("title_notes") or []:
        at = block["at_line"] + added
        lines[at:at] = block["lines"]
        added += len(block["lines"])
    text = "\n".join(lines)
    for note in sorted(data["notes"], key=lambda n: n["stripped_offset"],
                       reverse=True):
        off = note["stripped_offset"]
        text = (text[:off] + "\n::: {.notes}\n" + note["content"] + "\n:::\n"
                + text[off + 1:])
    return text


def _find_anchor(lines: list, anchor: str, ordinal: int):
    seen = 0
    for i, line in enumerate(lines):
        if line == anchor:
            seen += 1
            if seen == ordinal:
                return i
    return None


def _restore_by_anchor(qmd_path: Path, content: str, data: dict) -> None:
    """Best-effort restore into a file that changed since the backup: each
    note goes back after the line it originally followed. Spacing may gain
    a blank line; placement stays per-slide."""
    lines = content.split("\n")
    restored = 0
    skipped = 0
    # Bottom-up, so inserted note text cannot shift or shadow the anchors
    # of notes above it.
    for note in reversed(data["notes"]):
        idx = _find_anchor(lines, note["anchor"],
                           note.get("anchor_ordinal", 1))
        if idx is None:
            print(f"  Warning: anchor line not found, skipping note after: "
                  f"{note['anchor'][:50]!r}")
            skipped += 1
            continue
        lines[idx + 1:idx + 1] = (
            ["", "::: {.notes}"] + note["content"].split("\n") + [":::"])
        restored += 1
    for block in data.get("title_notes") or []:
        at = None
        for i, line in enumerate(lines):
            if re.match(r'^\s*title-slide-attributes:\s*$', line):
                at = i + 1
                break
        if at is None:
            print("  Warning: no title-slide-attributes: line; "
                  "skipping the title-slide notes")
            skipped += 1
        else:
            lines[at:at] = block["lines"]
            restored += 1
    qmd_path.write_text("\n".join(lines), encoding="utf-8")
    tail = f", {skipped} skipped" if skipped else ""
    print(f"Restored {restored} note block(s) to {qmd_path.name} "
          f"(anchored{tail})")


def _restore_v1(qmd_path: Path, content: str, notes: list) -> None:
    """The original heading-keyed restore, kept for old list-format
    backups (paper decks whose notes all sit under their own heading)."""
    lines = content.split("\n")

    heading_lines = {}
    for i, line in enumerate(lines):
        if line.startswith("## ") or line.startswith("# "):
            heading_lines[line] = i

    insertions = []
    for note in notes:
        heading = note["heading"]
        if heading not in heading_lines:
            print(f"  Warning: heading not found, skipping: {heading[:50]}")
            continue

        h_line = heading_lines[heading]
        end_line = len(lines)
        for j in range(h_line + 1, len(lines)):
            if lines[j].startswith("## ") or lines[j].startswith("# "):
                end_line = j
                break

        notes_block = f"\n::: {{.notes}}\n{note['content']}\n:::\n"
        insertions.append((end_line, notes_block))

    insertions.sort(key=lambda x: x[0], reverse=True)
    for line_num, block in insertions:
        lines.insert(line_num, block)

    qmd_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Restored {len(insertions)} notes to {qmd_path.name} (v1 backup)")


def restore(name: str, missing_ok: bool = False) -> None:
    """Restore notes from .speaker-notes/ into QMD."""
    backup_path = resolve(name).notes_json
    if not backup_path.exists():
        if missing_ok:
            return
        sys.exit(f"Error: No backup found at {backup_path}")

    qmd_path = find_qmd(name)
    content = qmd_path.read_text(encoding="utf-8")

    # Check if notes already exist
    if "::: {.notes}" in content or re.search(r'^\s*data-notes:', content,
                                              re.MULTILINE):
        print(f"{qmd_path.name} already has notes. Skipping restore.")
        return

    data = json.loads(backup_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        _restore_v1(qmd_path, content, data)
        return

    if _sha1(content) == data["stripped_sha1"]:
        restored = _reinsert_exact(content, data)
        if data.get("original_sha1") and _sha1(restored) != data["original_sha1"]:
            sys.exit(f"Error: exact restore of {qmd_path.name} did not "
                     f"reproduce the original; nothing written")
        qmd_path.write_text(restored, encoding="utf-8")
        extra = " + title-slide notes" if data.get("title_notes") else ""
        print(f"Restored {len(data['notes'])} notes{extra} to "
              f"{qmd_path.name} (exact)")
        return

    print(f"  {qmd_path.name} changed since the backup; anchoring notes to "
          f"the lines they followed")
    _restore_by_anchor(qmd_path, content, data)


def main():
    if len(sys.argv) < 2:
        print("Usage: backup_notes.py <backup|restore> [PaperName]")
        sys.exit(1)

    action = sys.argv[1]
    sweep = len(sys.argv) < 3
    if not sweep:
        names = [sys.argv[2]]
    else:
        # Every deck, addressed as genre/name so the sweep stays unambiguous
        # even if two genres ever share a deck name.
        names = [d.slug for d in deckpath.all_decks()]

    for name in names:
        if action == "backup":
            backup(name)
        elif action == "restore":
            # In a sweep, a deck without a backup is simply not restored
            # (the usage says "all backed-up files"); by name it is an error.
            restore(name, missing_ok=sweep)
        else:
            sys.exit(f"Unknown action: {action}")


if __name__ == "__main__":
    main()
