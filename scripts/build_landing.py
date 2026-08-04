#!/usr/bin/env python3
"""Generate the landing page from the decks that actually exist.

It used to be a hand-maintained table of four rows with hardcoded hrefs. That
is fine at four and wrong at twenty: the page is the one artifact nobody
re-reads after adding a deck, so it drifts silently and the drift is invisible
until someone clicks a dead link. Reading the same Quarto/_genres.txt and
<deck>.deck.yml everything else reads means it cannot fall behind.

Titles and descriptions come from each deck's config. A deck without one still
gets listed, under its own name -- being unlisted would be the worse failure.

Usage:
    python3 scripts/build_landing.py            # write pages/index.html
    python3 scripts/build_landing.py -          # print to stdout
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deckpath  # noqa: E402
import deckprofile  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "pages" / "index.html"

GENRE_HEADING = {
    "papers": ("Paper reviews", "Reading one paper closely and saying whether it holds."),
    "talks": ("Talks", "Invited and keynote."),
    "lectures": ("Lectures", "Course sessions, taught as a series."),
}

STYLE = """    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      max-width: 720px;
      margin: 0 auto;
      padding: 3em 1.5em;
      color: #1a1a1a;
      line-height: 1.7;
      background: #fff;
    }
    h1 { font-size: 2em; margin-bottom: 0.2em; }
    h2 { font-size: 1.25em; margin-top: 2.2em; margin-bottom: 0.1em; }
    .subtitle { color: #666; font-size: 1.1em; margin-bottom: 2em; }
    .section-note { color: #888; font-size: 0.9em; margin: 0 0 0.6em; }
    table { width: 100%; border-collapse: collapse; margin: 0.6em 0 0; }
    th, td { text-align: left; padding: 0.6em 0.8em; border-bottom: 1px solid #eee; }
    th { font-weight: 600; border-bottom: 2px solid #ddd; }
    td.name { white-space: nowrap; font-weight: 600; }
    a { color: #0366d6; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .empty { color: #999; font-style: italic; margin: 0.4em 0 0; }
    .footer { margin-top: 3em; padding-top: 1.5em; border-top: 1px solid #eee; color: #888; font-size: 0.9em; }
    @media (prefers-color-scheme: dark) {
      body { background: #111; color: #e6e6e6; }
      th { border-bottom-color: #333; }
      td, th { border-bottom-color: #262626; }
      .subtitle, .section-note, .footer, .empty { color: #999; }
      a { color: #6cb6ff; }
    }"""


def rows_for(genre: str) -> list[str]:
    out = []
    for deck in deckpath.all_decks():
        if deck.genre != genre:
            continue
        cfg = deckprofile.load(deck)
        title = html.escape(str(cfg.raw.get("title") or deck.name))
        desc = html.escape(str(cfg.raw.get("description") or ""))
        href = f"slides/{deck.genre}/{deck.name}.html"
        out.append(
            "      <tr>\n"
            f'        <td class="name">{title}</td>\n'
            f"        <td>{desc}</td>\n"
            f'        <td><a href="{href}">View</a></td>\n'
            "      </tr>"
        )
    return out


def build() -> str:
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        "  <title>Paper2PR</title>",
        "  <style>",
        STYLE,
        "  </style>",
        "</head>",
        "<body>",
        "  <h1>Paper2PR</h1>",
        '  <p class="subtitle">Slide decks by Yunsung Lee — paper reviews, talks, and lectures.</p>',
    ]

    for genre in deckpath.genres():
        heading, note = GENRE_HEADING.get(genre, (genre.title(), ""))
        rows = rows_for(genre)
        parts.append(f"\n  <h2>{html.escape(heading)}</h2>")
        if note:
            parts.append(f'  <p class="section-note">{html.escape(note)}</p>')
        if not rows:
            parts.append('  <p class="empty">Nothing here yet.</p>')
            continue
        parts += [
            "  <table>",
            "    <thead>",
            "      <tr><th>Deck</th><th>Topic</th><th>Slides</th></tr>",
            "    </thead>",
            "    <tbody>",
            *rows,
            "    </tbody>",
            "  </table>",
        ]

    parts += [
        "",
        '  <div class="footer">',
        "    <p>",
        '      Built with <a href="https://github.com/alohays/paper2pr">paper2pr</a>,',
        '      powered by <a href="https://github.com/pedrohcgs/claude-code-my-workflow">claude-code-my-workflow</a>.',
        "    </p>",
        "  </div>",
        "</body>",
        "</html>",
        "",
    ]
    return "\n".join(parts)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    page = build()
    if argv and argv[0] == "-":
        sys.stdout.write(page)
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    n = sum(1 for _ in deckpath.all_decks())
    print(f"Wrote {OUT.relative_to(REPO_ROOT)} with {n} deck(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
