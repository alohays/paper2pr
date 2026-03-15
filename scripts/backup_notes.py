#!/usr/bin/env python3
"""Backup and restore speaker notes for QMD files.

Speaker notes live in the working directory but are stripped by git clean
filters. This script backs them up to .speaker-notes/ (gitignored) so they
can be restored after git checkout or on a new machine.

Usage:
    python3 scripts/backup_notes.py backup DreamZero
    python3 scripts/backup_notes.py restore DreamZero
    python3 scripts/backup_notes.py backup              # all QMD files
    python3 scripts/backup_notes.py restore              # all backed-up files
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
QUARTO_DIR = REPO_ROOT / "Quarto"
NOTES_DIR = REPO_ROOT / ".speaker-notes"

# Matches a slide heading followed by content and a notes block
NOTES_PATTERN = re.compile(
    r'(::: \{\.notes\}\n)(.*?)(\n:::)',
    re.DOTALL,
)


def find_qmd(name: str) -> Path:
    """Find QMD file by paper name."""
    path = QUARTO_DIR / f"{name}.qmd"
    if not path.exists():
        sys.exit(f"Error: {path} not found")
    return path


def extract_notes(qmd_path: Path) -> list[dict]:
    """Extract all notes blocks with their preceding slide heading."""
    content = qmd_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    notes = []
    current_heading = None
    heading_line = 0

    for i, line in enumerate(lines):
        if line.startswith("## ") or line.startswith("# "):
            current_heading = line
            heading_line = i

    # Use regex to find notes and map them to slide positions
    for match in NOTES_PATTERN.finditer(content):
        start = content[:match.start()].count("\n")
        # Find the closest heading before this notes block
        heading = None
        for i, line in enumerate(lines):
            if i > start:
                break
            if line.startswith("## ") or line.startswith("# "):
                heading = line
                heading_line = i

        notes.append({
            "heading": heading,
            "heading_line": heading_line,
            "note_line": start,
            "content": match.group(2),
        })

    return notes


def backup(name: str) -> None:
    """Backup notes from QMD to .speaker-notes/."""
    qmd_path = find_qmd(name)
    notes = extract_notes(qmd_path)

    if not notes:
        print(f"No notes found in {qmd_path.name}")
        return

    NOTES_DIR.mkdir(exist_ok=True)
    out_path = NOTES_DIR / f"{name}.json"
    out_path.write_text(
        json.dumps(notes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Backed up {len(notes)} notes to {out_path}")


def restore(name: str) -> None:
    """Restore notes from .speaker-notes/ into QMD."""
    backup_path = NOTES_DIR / f"{name}.json"
    if not backup_path.exists():
        sys.exit(f"Error: No backup found at {backup_path}")

    qmd_path = find_qmd(name)
    content = qmd_path.read_text(encoding="utf-8")

    # Check if notes already exist
    if "::: {.notes}" in content:
        print(f"{qmd_path.name} already has notes. Skipping restore.")
        return

    notes = json.loads(backup_path.read_text(encoding="utf-8"))
    lines = content.split("\n")

    # Build a map of heading text -> line numbers in current file
    heading_lines = {}
    for i, line in enumerate(lines):
        if line.startswith("## ") or line.startswith("# "):
            heading_lines[line] = i

    # Insert notes in reverse order (to preserve line numbers)
    insertions = []
    for note in notes:
        heading = note["heading"]
        if heading not in heading_lines:
            print(f"  Warning: heading not found, skipping: {heading[:50]}")
            continue

        # Find the end of this slide's content (next heading or EOF)
        h_line = heading_lines[heading]
        end_line = len(lines)
        for j in range(h_line + 1, len(lines)):
            if lines[j].startswith("## ") or lines[j].startswith("# "):
                end_line = j
                break

        notes_block = f"\n::: {{.notes}}\n{note['content']}\n:::\n"
        insertions.append((end_line, notes_block))

    # Sort by line number descending and insert
    insertions.sort(key=lambda x: x[0], reverse=True)
    for line_num, block in insertions:
        lines.insert(line_num, block)

    qmd_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Restored {len(insertions)} notes to {qmd_path.name}")


def main():
    if len(sys.argv) < 2:
        print("Usage: backup_notes.py <backup|restore> [PaperName]")
        sys.exit(1)

    action = sys.argv[1]
    if len(sys.argv) >= 3:
        names = [sys.argv[2]]
    else:
        # All QMD files
        names = [p.stem for p in QUARTO_DIR.glob("*.qmd")]

    for name in names:
        if action == "backup":
            backup(name)
        elif action == "restore":
            restore(name)
        else:
            sys.exit(f"Unknown action: {action}")


if __name__ == "__main__":
    main()
