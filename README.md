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

Decks are published by GitHub Actions on every push to `main`: by default,
each deck is rendered, speaker notes are stripped, and the site is deployed.
Set `publish: false` in a deck's `.deck.yml` to leave that deck out of the
Paper2PR Pages site and landing page. This is a hosting switch, not an access
control: source committed to `main` remains public on GitHub, and the QMD can
still be rendered directly with Quarto.

## Genres

| Genre | Profile | Audience | Length |
|-------|---------|----------|--------|
| `papers` | `paper-review` | knows deep learning | ~30 min |
| `talks` | `invited-talk` | varies, declared per deck | varies |
| `lectures` | `lecture` | no background | ~60 min |

A deck lives at `Quarto/<genre>/<deck>.qmd` and declares its premises
(audience, length, language, and whether Paper2PR Pages should publish it) in
`Quarto/<genre>/<deck>.deck.yml`. The quality gate reads that file to choose
the budgets and checks that apply; the deploy pipeline reads `publish`, which
defaults to `true` when omitted.

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

## Authoring and verification

Give Codex or Claude the audience, the slot and any chapters or demonstrations you want to keep. The agent chooses examples, diagrams, layouts and reveal order. The deck's QMD remains the presentation source. The optional brief in its deck config records presenter requirements.

After the one-time QA setup, verify the same audience HTML that you intend to present or publish.

```bash
./verify dgist-2026f-w02                         # public slides
./verify dgist-2026f-w02 --delivery classroom    # classroom playback
./verify --all --regressions --site _site        # simulate a Pages release
```

The command saves final-fragment screenshots, a checked PDF handout and the HTML hashes in a local run directory. The public site contains the audience pages and their runtime assets. [QA setup and commands](guides/verification.md) · [Authoring a deck](guides/framework.md) · [Classroom media](guides/media.md)

## Layout

```
paper2pr/
├── AGENTS.md          # Canonical description for agents and contributors
├── Quarto/            # <genre>/<deck>.qmd, themes, project defaults, filters, fixtures
├── Figures/           # Per-deck figures, Figures/<genre>/<deck>/
├── assets/            # Diagrams for this README and AGENTS.md (never deployed)
├── scripts/           # Render, assemble, gate, and test utilities (stdlib Python + bash)
├── .claude/           # Rules, skills, agents, hooks
├── guides/           # Authoring, delivery and verification references
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
