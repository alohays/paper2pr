# Paper2PR

Yunsung Lee presents paper reviews, invited talks and lectures from canonical Quarto QMD rendered to RevealJS. Keep deck names and published URLs stable. Use the presenter's GUI model selection.

## Start in the right worktree

Run `git worktree list` and `git status --short --branch`. For the November 20 DGIST HSS118 W13 lecture, the active checkout is `~/maangeek/paper2pr-w13` on `codex/dgist-w13`. Its local handoff is `.local/w13-prep/codex-handoff.md`. Keep other checkouts, local notes and ongoing lecture edits intact. Save nontrivial plans in `quality_reports/plans/` and keep archived decisions. Record reusable presenter corrections in `MEMORY.md` under `[LEARN:category]`.

## Author from the brief

Record the audience, scheduled minutes, language and sources in the deck's `.deck.yml`. Preserve any agreed chapters, demonstrations and allocations. Choose examples, diagrams, layouts and reveal order within those commitments. Reuse the series metadata for course lectures. Ask the presenter when a missing premise would change the talk. [Authoring workflow](.agents/skills/new-deck/SKILL.md) · [Brief, series and layout reference](guides/framework.md) · [New-deck design principles](.claude/rules/slide-design-principles.md)

## Keep presenter material local

Install the Git filter and hook with `bash scripts/setup-git-filters.sh` once per clone. Stage QMDs through the filter and keep working notes in local presenter renders. Public output contains audience slides, their runtime assets and approved release media. Classroom-only clips turn into publisher links. Use an external `PAPER2PR_PRIVATE_DENYLIST` file for private vocabulary. [Media policy and commands](guides/media.md)

Tracked content is English, including commits and reports. Korean examples are permitted in `.claude/skills/` and `.claude/agents/`. Declare Korean slides per deck with `language.slides: ko`. English lectures have a default allowance of 300 Hangul characters, other profiles zero, with a per-deck `language.korean_allowance` override. Speaker notes default to Korean and stay on the presenter’s machine.

## Verify the audience view

Install the pinned local QA tools once. [Setup and verification evidence](guides/verification.md)

- `./verify <deck>` builds and checks the public version. Use `--delivery classroom` for local playback.
- For a copy edit use `./verify <deck> --slide <id>` and inspect the affected frame. For a changed number also check its meaning, units and scope against the primary source.
- For a new talk or release, run independent factual, visual and teaching reviews. Use `./verify --all --regressions` for the framework release. Punctuation, estimated wrapping and callback wording are editorial feedback. The existing thresholds are 80 for a commit, 90 for a PR and 95 for excellence. [Review workflow](.agents/skills/slide-excellence/SKILL.md) · [Quality checks](.claude/rules/quality-gates.md)

Publish or upload media when the presenter authorizes it.
