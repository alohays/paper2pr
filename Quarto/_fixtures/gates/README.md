# Gate fixtures (not published)

Two tiny decks that exercise the WP2 quality-gate checks in
`scripts/quality_score.py`, so a change to the checker is caught here before
it is caught on a real deck:

- `pass.qmd` trips nothing: a lecture-profile deck with a footnoted
  third-party figure (once as a markdown image, once as an `<img>` inside a
  raw `{=html}` block whose `<style>` carries `--` custom properties that
  must not count), a `## {.divider}` section break, plain hyphens, display
  math with minus signs, no forbidden terms. Its `deck.yml` omits
  `korean_allowance` so the lecture profile's 300 is what resolves, and
  declares `video_min`/`qa_min` so `speaking_min` is 45.
- `trip.qmd` trips every check at least once: `---` and `--` in visible
  text and an `&mdash;` entity inside a raw block (dash lint, -2 each), a
  level-1 `# Heading` (BLOCKER), a third-party figure with no attribution
  three ways (markdown image, `{background-image=...}` header attribute,
  `{{< video >}}` shortcode; -5 each), and two terms from
  `trip.forbidden.txt` in body text and in a raw block (BLOCKER). Its
  HTML comment and its notes also carry a `---` and a forbidden term, which
  must NOT be reported. Its `deck.yml` sets `korean_allowance: 12` to show
  the deck-level override.

Both resolve their profile from the `.deck.yml` beside them (`deckprofile.py`
accepts a fixture by path when a config sits next to it; bare names never
find them). `figures.yml` sits next to the qmds because the fixtures live
outside `Figures/<genre>/<deck>/`; the checker accepts that as a fallback.
The figure and clip are the committed placeholders in `../assets/`.

    python3 scripts/quality_score.py Quarto/_fixtures/gates/pass.qmd --summary   # 100, exit 0
    python3 scripts/quality_score.py Quarto/_fixtures/gates/trip.qmd --summary   # 0, exit 1, BLOCKER lines

`scripts/test_profiles.py` (sections 6-12) runs the checks on these files
without rendering, so the line numbers asserted there (the level-1 heading at
line 26) move with any edit to `trip.qmd`.
