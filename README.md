# Paper2PR

Yunsung Lee's presentation framework: Quarto RevealJS decks for paper
reviews, invited talks, and course lectures, with a quality gate and an
automated publish path. The name is historical (the repo started as a
paper-to-presentation generator) and is kept because the published slide
URLs depend on it.

![Deck lifecycle: video and series manifests plus the project defaults feed
quarto render; the quality gate, a push to main and CI publish the deck to
GitHub Pages; clips live on a GitHub Release, while speaker notes and the PDF
handout never leave the presenter's machine](assets/pipeline.svg)

One deck, from source to published page. Anything on a dashed path stays local.

**Organization:** WoRV / MaumAI

---

## Published decks

- Landing page: <https://alohays.github.io/paper2pr/>
- One deck: `https://alohays.github.io/paper2pr/slides/<genre>/<deck>.html`

Decks are published by GitHub Actions on every push to `main`: the decks
are rendered, speaker notes are stripped, and the site is deployed. What
is on `main` is public.

## Genres

| Genre | Profile | Audience | Length |
|-------|---------|----------|--------|
| `papers` | `paper-review` | knows deep learning | ~30 min |
| `talks` | `invited-talk` | varies, declared per deck | varies |
| `lectures` | `lecture` | no background | ~60 min |

A deck lives at `Quarto/<genre>/<deck>.qmd` and declares its premises
(audience, length, language) in `Quarto/<genre>/<deck>.deck.yml`. The
quality gate reads that file to choose the budgets and checks that apply.

## What a deck looks like

![Six slide types on the shared theme: title slide, section divider, full-bleed
video on its poster frame, chart figure with bullets, formula with legend and
gloss, and a five-item timeline](assets/slide-types.png)

Rendered from `Quarto/_fixtures/design-test.qmd`, which carries one slide per
theme rule.

## Course series

A lecture belongs to a course declared once in
`Quarto/lectures/_series/<course>.yml`, and the `semester-map` shortcode drops
the shared timeline into every session of it with that week ringed.

![The DGIST 2026 fall semester timeline, week 02 ringed as
today](assets/semester-map.svg)

## Making a deck

```bash
quarto render Quarto/<genre>/<deck>.qmd      # render one deck locally
./scripts/sync_to_docs.sh [<deck>]           # local preview of the published site
```

With Claude Code, `/new-deck` interviews for the premises, scaffolds the
deck, and carries authoring through the quality gate; `/slide-excellence`
runs the review fan-out. Speaker notes (`::: {.notes}`) stay local: a git
clean filter keeps them out of commits and CI strips them from the HTML.

## Layout

```
paper2pr/
├── AGENTS.md          # Canonical description for agents and contributors
├── Quarto/            # <genre>/<deck>.qmd, themes, project defaults, filters, fixtures
├── Figures/           # Per-deck figures, Figures/<genre>/<deck>/
├── assets/            # Diagrams for this README and AGENTS.md (never deployed)
├── scripts/           # Render, assemble, gate, and test utilities (stdlib Python + bash)
├── .claude/           # Rules, skills, agents, hooks
└── quality_reports/   # Plans and session logs (history)
```

`docs/` is the local preview output of `scripts/sync_to_docs.sh`; it is
gitignored and never committed. `AGENTS.md` is the canonical description of
the framework; start there.

## Attribution

The repository grew out of [claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow)
by Pedro H. C. Sant'Anna; the template layer has since been removed, and the
shared history is the record.

## License

MIT License. See [LICENSE](LICENSE).
