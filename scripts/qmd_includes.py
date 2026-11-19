"""Expand standalone Quarto include shortcodes for source checks.

Nested include paths resolve from the main document, as they do in Quarto.
A leading slash names a path from the Quarto project root.
"""
from pathlib import Path
import re

INCLUDE = re.compile(r"""^\s*\{\{<\s*include\s+(?:"([^"]+)"|'([^']+)'|([^\s>]+))\s*>\}\}\s*$""")


def expanded_source(qmd):
    main = qmd.resolve()
    project = next((p for p in main.parents if (p / "_quarto.yml").is_file()), main.parent)
    lines, origins = [], []

    def expand(path, parents):
        if path in parents:
            raise ValueError("Cycle in Quarto includes")
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            raise ValueError("Cannot read a Quarto source or include") from None
        for number, line in enumerate(text.splitlines(), 1):
            match = INCLUDE.fullmatch(line)
            if match:
                name = next(group for group in match.groups() if group is not None)
                target = project / name[1:] if name.startswith("/") else main.parent / name
                expand(target.resolve(), (*parents, path))
            else:
                lines.append(line)
                origins.append((path, number))

    expand(main, ())
    return "\n".join(lines), origins
