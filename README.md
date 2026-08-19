# Paper2PR

Yunsung Lee's presentation framework: Quarto RevealJS decks for paper
reviews, invited talks, and course lectures, with a quality gate and an
automated publish path. The name is historical (the repo started as a
paper-to-presentation generator) and is kept because the published slide
URLs depend on it.

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
