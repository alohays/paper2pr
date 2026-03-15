#!/usr/bin/env python3
"""Git clean filter: strip speaker notes from QMD files before staging.

Reads QMD content from stdin, removes ::: {.notes} ... ::: blocks,
writes cleaned content to stdout. Used by git via .gitattributes.

Setup:
    git config filter.strip-speaker-notes.clean 'python3 scripts/strip_qmd_notes.py'
    git config filter.strip-speaker-notes.smudge 'cat'
"""

import re
import sys


def strip_notes(content: str) -> str:
    """Remove ::: {.notes} ... ::: blocks from QMD content."""
    return re.sub(
        r'\n::: \{\.notes\}\n.*?\n:::\n',
        '\n',
        content,
        flags=re.DOTALL,
    )


if __name__ == "__main__":
    sys.stdout.write(strip_notes(sys.stdin.read()))
