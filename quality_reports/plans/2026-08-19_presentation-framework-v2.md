# Presentation framework v2: finish the pivot before the first lecture deck lands

**Date:** 2026-08-19
**Status:** implementation in progress on the `framework-v2` stack (gh-stack, one branch per WP). WP0 decided and landed; see each WP section for its record.
**Trigger:** the first course lecture, `dgist-2026f-w02` (DGIST HSS118, 2026-09-04, 42 slides, 8-10 videos, 100+ non-major first-years), is the first deck that will be graded by the main theme and the `lecture` profile at the same time. Neither has ever met a real deck.
**Decided by:** the presenter, in a 28-question interview on 2026-08-18/19. The Korean record of that interview lives in the vault (`1-projects/maum/dgist-future-literacy-2026fall/lectures/paper2pr-readiness.md`); this file is the English source of truth for the work.
**Evidence:** two read-only audits, both code-verified (scaffold dry-run, brief slides scored by `quality_score.py`, a probe deck rendered against `clean-academic.scss`, the asset-gate regex executed). Copies: vault `lectures/paper2pr-audit/01-w02-readiness-audit.md` and `02-framework-inventory.md`. Line numbers below refer to HEAD `6530b84`.

---

## 1. Verdict in one paragraph

The authoring skeleton built on 2026-08-04 (`Quarto/<genre>/`, `_genres.txt`, `<deck>.deck.yml`, `slide-profiles/`, `/new-deck`, the Korean gate, the three-layer notes privacy, the deploy chain) is real code and fits a lecture. The media and publication half does not exist: no video tooling, no PDF export, no series object, no manifest for asset provenance, and the agent that writes speaker notes is hardwired for paper reviews. Separately, the repo still carries three archaeological layers (an upstream econometrics template, the Beamer paper-review generator, the Quarto framework); governance prose outweighs pipeline code two to one, and about 55-60 files have never executed. The presenter decided to remove all of it, keep the name and URL, and finish the framework **before** authoring W02.

## 2. Decisions (binding for the work below)

| # | Topic | Decision |
|---|---|---|
| D1 | Scope | Whole-framework re-examination, not a W02 patch |
| D2 | Order | Framework first, then `dgist-2026f-w02` |
| D3 | Legacy | Delete every retire candidate; git history is the archive. Includes the whole Beamer/LaTeX path (single Quarto path) |
| D4 | Name | Keep `paper2pr` and the `/paper2pr/` Pages URL; change only the tagline to "presentation framework" |
| D5 | Docs | `AGENTS.md` is the single canonical description. `README.md` becomes a short external intro. `guide/` goes. Rule files keep only what a script or hook enforces plus short principles. Root `MEMORY.md` stays |
| D6 | Videos on the public copy | Third-party clips (official channels) are embedded as mp4 on the public page too, as educational quotation |
| D7 | Video hosting | GitHub Release assets per deck (the SUNY precedent), never in git |
| D8 | Build targets | One build. Video sources point at the Release URL only; the classroom trusts the network (pre-play once before class to warm the cache) |
| D9 | Classroom | Presenter's own MacBook, reveal speaker view (`S`) for notes, timer, next slide |
| D10 | Students | Web link plus a PDF handout uploaded to the LMS by hand |
| D11 | Publish timing | The presenter decides when a deck goes public; no new mechanism. Work on a branch, merge to `main` = publish |
| D12 | Course page | Links pasted by hand into the separate MkDocs site; paper2pr only keeps `/slides/lectures/<deck>.html` stable |
| D13 | Speaker notes | Local only, presenter screen only, never in the deployed HTML, done the standard Quarto way (`::: {.notes}` + speaker view). Implementation detail is the agent's call |
| D14 | Series | `Quarto/lectures/_series/<course>.yml` plus shared include slides; `deck.yml` references the series |
| D15 | Video slides | Per-deck `videos.yml` manifest plus a shortcode/include that emits the HTML (poster, caption, sources, autoplay convention) |
| D16 | Timing tools | None. Rehearsal is human; the notes budget formula is merely made honest |
| D17 | Acronym check | Off for the `lecture` profile |
| D18 | Korean on English slides | A small allowance per deck (term glosses, Wooclap instructions) |
| D19 | QR | Large, on the orientation and Q&A slides only; nothing persistent in the body; no theme logo slot involved |
| D20 | Theme | Undecided. Render W02 samples (hook video, formula, timeline) in the light main theme and in a dark lecture variant, then decide. First task of the implementation turn |
| D21 | Figures | Agent's judgment per figure: inline SVG, matplotlib, or image generation (Codex). TikZ path retired |
| D22 | Gate additions | Attribution/licence footer required for third-party figures; `---` (em dash) lint; per-deck forbidden-term scan (internal names, unpublished numbers) |
| D23 | Review pipeline for lectures | pedagogy with the audience read from `deck.yml`; fact check against the vault research verdicts; visual render audit from full-deck screenshots |
| D24 | Future needs (W04+, aSSIST) | Not designed now |

## 3. What the audits found (short form)

Top gaps for W02, with evidence in the audit files:

1. No video tooling anywhere (`ls scripts/`; `assemble_site.sh:37-66` copies no mp4; `check_site_assets.py:21-25` only exempts `videos/*.mp4`, which yields a silent 404 on the public page).
2. `publish:` in `deck.yml` is written by `new_deck.py` and read by nothing (`grep -rn publish scripts/ .github/`). Push to `main` publishes every deck. Resolved by D11 without code.
3. `check_acronym_expansion` costs the W02 brief -18 on 14 slides; four of nine hits are hyphen artefacts (`RT-2` -> `RT`, `QT-Opt`, `DALL-E`, `LAION-5B`) at `quality_score.py:233-241`. Resolved by D17.
4. `.reveal video { max-height: 432px }` (`clean-academic.scss:879-886`) blocks the full-bleed hook and the montage; `_fixtures/design-test.qmd` has no video, logo, or footer slide.
5. Logo slot is 50x50 px bottom-left (`clean-academic.scss:847-856`) and cannot be hidden per slide. Moot after D19.
6. `sync_notes.py` cannot run on a scaffolded lecture (`:139-142` requires `title-slide-attributes`, `:44-47` requires an appendix file, `:82-85` matches by title so untitled video slides collide) and has no caller. Retired under D13.
7. `agents/script-writer.md` says "state the paper being reviewed" (`:42`) and "compare to baselines" (`:64`); `pedagogy-reviewer.md:8` assumes "advanced students". Neither reads `deck.yml`.
8. No series object; `audience.prior`, `audience.size`, `delivery`, `publish` are dead fields (`new_deck.py:57-61` vs `deckprofile.py:183-199`).
9. No provenance or licence metadata for figures or videos; nothing can consume the vault `manifest.json` (35 clips with autonomy labels, publisher, date).
10. `duration_min` has one consumer, the notes budget (`write-speaker-notes/SKILL.md:115`), which over-budgets a 42-minute body with 8-10 minutes of video by ~77 percent.

Also confirmed live: a level-1 `#` heading collapses every following slide into one vertical stack; the theme has no `@media print`, so video slides print blank; density and prior-session checks pass on the brief.

Framework-wide: 24 skills (8 retire, 3 merge), 11 agents (5 retire, `tikz-reviewer` has zero references, `verifier` is never launched), 19 rules (9 retire; `meta-governance.md` at 251 lines still says "Emory, econometrics" and "others fork this repo"), 25 scripts (3 dead), `guide/` is the upstream author's document about a different course, 20 contradictions (sharpest: `quality-gates.md:29` ">5 bullets" vs `lecture.yml:17` `4`, and `AGENTS.md` forbidding `.smaller` at line 68 while listing it as usable at line 220). `clean-academic.scss`, the declared main theme scaffolded into every new deck, is pinned by zero decks.

## 4. Work packages

Ordered. Each package ends in a commit set on a branch; the branch merges when its acceptance list is green. No dates.

### WP0 - Theme decision (D20)

- Build, outside the repo tree or in a throwaway branch, three W02 slides (hook video full-bleed, the `pi(a | o, l)` formula slide, the 2012-2026 timeline) twice: once on `clean-academic.scss`, once on a dark lecture variant (Pretendard or equivalent, high contrast for a lit room). Screenshot both at 1280x720.
- Present the six images; the presenter picks. Record the pick here.
- Accept: a written decision plus the chosen theme file(s) checked in with a fixture slide for each new class.

**Decision (2026-08-19): variant A, the light academic theme.** Three variants were rendered on the same five W02 slides plus the title slide (A light academic = `clean-academic.scss` + new classes; B dark lecture, navy/gold, Pretendard + Instrument Serif; C Swiss light, white/black + red, Archivo + Nunito), each critiqued from two lenses (designer, back-row student) and given one fix round. Reviewer averages were C 7.8, B 7.5, A 7.2; the presenter picked A for continuity with the existing decks, and it is the safest palette for a lit 100-seat room. Consequences, all landed on this branch:

- The overlay was folded into `Quarto/clean-academic.scss` (it stays the main theme for every genre; the identity is the presenter's, not an institution's). New classes: `.divider`, `.video-full` + `.video-caption`, `.video-inline`, `figure.chart-figure`, `.formula-legend`, `.gloss`, `.timeline` (one row up to six items, two rows of four from seven). Gold used as text darkened to `#9A7B3F`; `.footnote` 0.45em left; Pretendard is the Hangul fallback in every font stack.
- Full-bleed slides use reveal background attributes, not stretched CSS: `Quarto/_filters/slide-types.lua` maps `## {.divider}` to `data-background-color` and `## {.video-full video=... poster=...}` to `data-background-video` (+ loop, muted, cover) and `data-background-image`. `Quarto/_quarto.yml` wires the filter, sets `margin: 0` (the 1280x720 section is the viewport), and links `../fonts/pretendard.css` for every deck under a genre directory. `_fixtures/` is underscore-prefixed and therefore outside the Quarto project: fixtures repeat those defaults themselves.
- Fixtures: `Quarto/_fixtures/design-test.qmd` gained a "Slide Types" part with committed placeholder assets; `Quarto/_fixtures/theme-mockups/` keeps the W02 sample (`body.qmd` + `w02-sample.qmd`, media gitignored). `Quarto/_fixtures/shoot.py` drives headless Chrome over the DevTools protocol (the `--screenshot` one-liner painted SVG text from a stale layout); WP6 moves it under `scripts/` as the render audit.
- Rejected variants B and C were not committed; the side-by-side comparison page and their contact sheets were shown to the presenter at decision time and live in the session scratchpad only. If a dark variant is wanted later, it is a new piece of work, not a revert.

### WP1 - Remove the dead layers (D3, D5)

Delete, in separate commits by nature:

- Upstream template: `.claude/rules/{meta-governance,replication-protocol,r-code-conventions,orchestrator-research,orchestrator-protocol,exploration-fast-track,exploration-folder-protocol,pdf-processing}.md`; `explorations/`; `master_supporting_docs/`; `templates/{skill-template,constitutional-governance,exploration-readme,archive-readme,quality-report,requirements-spec}.md`; skills `data-analysis`, `review-r`, `lit-review`, `research-ideation`, `interview-me`, `review-paper`; agent `r-reviewer`; `guide/` (qmd, 2.2 MB html, scss, `_quarto.yml`); `.claude/WORKFLOW_QUICK_REF.md`.
- Beamer path: `Slides/`, `Preambles/`, `.chktexrc`; skills `compile-latex`, `extract-tikz`, `translate-to-quarto`, `qa-quarto`, `pdf-diff`; agents `beamer-translator`, `quarto-critic`, `quarto-fixer`, `tikz-reviewer`; rules `no-pause-beamer.md`, `beamer-quarto-sync.md`, `tikz-visual-quality.md`; `scripts/setup-optional-tools.sh`; the Beamer sections of `AGENTS.md` (custom environments, project-state Beamer column) and of `single-source-of-truth.md`.
- Dead code: `scripts/prefix_slide_css.py` (and the `tinycss2` dependency with it), `scripts/sync_notes.py`, `Quarto/_extensions/{pointer,codewindow}`. `scripts/build_widgets.py` stays with RoboTTT until that deck is retired.
- Merge `proofread`, `pedagogy-review`, `devils-advocate` into `slide-excellence` (one skill, one fan-out); resolve `domain-reviewer` (see WP6) and `verifier` (wire into `/deploy` or delete).
- Keep: root `MEMORY.md` (D5), `clean-academic-legacy.scss` (three decks pin it; it is also the switch that turns design deductions off in `quality_score.py:413-415`), `Bibliography_base.bib`, `quality_reports/` history, all seven hooks, `session-logging.md`, `plan-first-workflow.md`, `proofreading-protocol.md`, `verification-protocol.md`, `quality-gates.md` (fixed in WP2), `knowledge-base-template.md` (papers only, say so).
- Fix the drift in what remains: `AGENTS.md` (duplicate `/new-deck` row at 175/187, duplicate speaker-notes section, ClawTeam section out, `.smaller`/`.smallest` rows out of the CSS table, SUNY Beamer row, tagline), `README.md` (scope sentence, tree, agent count, `docs/` claim), `.gitignore:74` (`Figures/SUNY/videos/` -> `Figures/talks/SUNY/videos/`), `DreamZero.deck.yml` and `SUNY.deck.yml` (`notes: ko` claims with zero notes), `quality-gates.md:29` (numbers come from the profile, say so).
- Accept: `python3 scripts/test_profiles.py`, `bash scripts/test_note_filter.sh`, `bash scripts/test_korean_gate.sh`, `python3 scripts/test_minyaml.py` all pass; all four decks still render and score as before; `bash scripts/sync_to_docs.sh` succeeds and `check_site_assets.py` is clean; no `.md` under `.claude/` references a deleted path (`grep -rn` for each deleted name returns nothing outside `quality_reports/`).

**Record (2026-08-19): done on branch `wp1/remove-dead-layers`, eight commits.** Tracked files 369 -> 302. Deleted as listed, plus `Figures/talks/SUNY/*.tex` (TikZ sources behind SVGs that are committed) and the empty `target-papers/`, `scripts/R/` directories. Decisions taken during the work: `verifier` deleted (CI and `check_site_assets.py` cover it; WP6 adds the render audit); `visual-audit` stays standalone while `proofread`, `pedagogy-review`, `devils-advocate` fold into `slide-excellence`; `/commit` keeps its single-PR flow (gh-stack is used for this v2 work only); `scripts/build_widgets.py` now reads the RoboTTT animation sources from a local-only `Quarto/papers/robottt-anim/` (copied from the old clone; `.gitignore` covers it) and regenerates the seven committed widget fragments byte-identical. Acceptance: all four tests pass, all four decks score 100/100 as before, `sync_to_docs.sh` + `check_site_assets.py` report 179/179 references, and a 66-name grep over every tracked text file outside `quality_reports/` finds no dangling reference.

### WP2 - Profiles, gates, Korean gate (D17, D18, D22)

- `lecture.yml`: `expand_acronyms: false`; drop the "readings are optional" guidance (the presenter does not mention readings); replace `duration_min` semantics in `write-speaker-notes` with `speaking_min` derived as `duration_min - video_min - qa_min` when the deck declares them, else `duration_min`; fix the 130-words-per-minute vs 115 inconsistency (`write-speaker-notes/SKILL.md:39,116`).
- Korean gate: honour a per-deck `language.korean_allowance: <int>` (max Hangul characters in the qmd after the notes filter). Default 0. Test in `test_korean_gate.sh`.
- `quality_score.py` additions, each behind the profile so paper decks are unaffected unless their profile opts in:
  - em dash lint: `---` in visible slide text (outside fences) is a deduction; also `--` if the presenter confirms.
  - attribution: any `![](...)` or `<img>` whose file is listed in `Figures/<genre>/<deck>/figures.yml` with `third_party: true` must have a `.footnote` (or the shortcode's caption) on the same slide naming `source` and `licence`.
  - forbidden terms: if `Quarto/<genre>/<deck>.forbidden.txt` exists, any match in visible text is a hard failure. Seed the W02 file from the vault research forbidden list.
  - `#` level-1 heading anywhere after the title: hard failure with the vertical-stack explanation.
- Document `publish:` as informational only, or remove it from `ANSWER_KEYS`; remove `prior`, `audience_size`, `delivery` from the schema or give each a reader. Do not leave a field that is written and never read.
- Accept: `test_profiles.py` extended for the new checks; a fixture deck that trips each new check and one that passes; the W02 brief slides (the 14 used in the audit) score >= 90 on density plus the new checks with acronyms off.

**Record (2026-08-19): done on branch `wp2/profiles-gates`, five commits.** Presenter decisions taken during the work: dash lint covers `---`, `--`, literal and entity em/en dashes (the presenter avoids dash expressions altogether and writes a plain hyphen); `korean_allowance` default 300 for the lecture profile, 0 elsewhere; `publish` removed from the schema (D11), `audience.size`, `audience.prior`, `delivery` kept and documented as review-agent context (WP6 reads them). Implementation notes: raw `{=html}` blocks count as visible text for the dash, forbidden-term and attribution checks (SUNY is written that way) but not for the level-1 check; the attribution check also sees `{background-image=...}` header attributes and `{{< video >}}`; `minyaml` learned block sequences of mappings for the asset manifests; `new_deck.py` stubs rely on `Quarto/_quarto.yml` for the reveal defaults and set the title-slide gradient. Legacy handling: DreamZero and DreamDojo set `checks.level1_heading: off` (their section title slides are level-1 stacks by design) and DreamZero, DreamDojo, SUNY set `checks.dash_lint: false` (delivered before the rule; not rewritten), so all four decks still score 100/100. Acceptance: `test_profiles.py` (12 sections incl. the new checks), `test_minyaml.py`, `test_note_filter.sh`, `test_korean_gate.sh` (10 sections) pass; `Quarto/_fixtures/gates/trip.qmd` trips every new check (4 blockers + 5 majors), `pass.qmd` scores 100; the W02 sample (`_fixtures/theme-mockups/body.qmd`, lecture profile, acronyms off) scores 97, the only deduction being the prior-session callback the five-slide excerpt cannot have; the 14-slide audit probe no longer exists as a file, so the sample stands in for it.

### WP3 - Video pipeline (D6, D7, D8, D15)

- Layout: `Quarto/videos/<genre>/<deck>/videos.yml` (committed) and `Quarto/videos/<genre>/<deck>/*.mp4|*.jpg` (gitignored, replace the flat `Quarto/videos/` rule).
- `videos.yml` schema per entry: `slug`, `title`, `publisher`, `source_url`, `published` (YYYY-MM), `autonomy` (`autonomous | claimed | teleop | unknown`), `speed` (e.g. `1x`, `2x`), `segment` (start-end seconds in the source), `local` (path relative to the deck's video dir), `release_url`, `poster`, `licence_note`. The vault `video-candidates/manifest.json` maps onto this one-to-one; write a one-shot importer or do it by hand for 8-10 clips.
- `scripts/media_prep.py <deck>`: for each entry, trim to `segment`, re-encode to 1280x720 H.264 <= 30 MB (the HUFS preset: `scale=1280:-2`, `libx264`, `-preset fast`, ~8 Mbps, audio stripped unless `keep_audio`), extract the poster at the segment start, write sizes back into `videos.yml`.
- `scripts/media_release.sh <deck>`: `gh release create media/<deck>` (idempotent) and upload every mp4 and poster; write the resulting URLs into `release_url` / `poster`.
- Shortcode or include: `{{< video-card slug >}}` (or `{{< include >}}` of a generated partial) emits, inside a `{=html}` fence, `<video poster=... preload="none" muted playsinline loop autoplay>` with a single `<source>` at `release_url`, and a caption strip built from `autonomy`, `speed`, `publisher`, `published`. Classes: `.video-full` (full-bleed, no title, D19 has no QR to collide with) and `.video-inline`. `check_site_assets.py` must treat `release_url` as external and the poster as required.
- Theme: `.video-full` overrides the 432 px cap; `@media print` swaps `<video>` for the poster (WP7 depends on this).
- Accept: fixture deck with one `.video-full` and one two-up montage renders; `check_site_assets.py` passes with no local mp4 present; a mp4 missing from the Release fails a `media_release.sh --check`; the deployed page plays from the Release URL in Safari and Chrome.

### WP4 - Series object and shared slides (D14, D19)

- `Quarto/lectures/_series/<course>.yml`: `course`, `code`, `term`, `institution`, `room`, `instructor`, `course_page`, `qa_tool` (name + join URL for the QR), `sessions: [{index, date, title, deck, presenter}]`, `notation: {policy: "pi(a | o, l)", ...}`.
- `Quarto/lectures/_series/<course>/*.qmd`: shared include slides -- instructor intro, semester timeline (reads `sessions`), orientation QR slide, Q&A QR slide, the "demo is not deployment" reminder if it recurs. Included with `{{< include >}}`; the QR PNG is generated by a script from `qa_tool.url` (`qrencode` or the Python `qrcode` module) into `Figures/lectures/_series/<course>/`.
- `deck.yml`: `series: <course>` and `series_index` resolve the session; `new_deck.py` reads the series to prefill title, date, and prior session; the prior-session check names the actual previous session (a guest talk counts).
- `build_landing.py`: group lecture decks by series, order by `series_index`, show date and week label.
- Accept: `python3 scripts/deckprofile.py dgist-2026f-w02` prints the resolved series fields; landing shows the series block; a deck whose `series_index` is not in the series file fails loudly.

**Record (2026-08-19): done on branch `wp4/series`, three commits.** Presenter answers: shared slides are the semester map, the two QR slides and "how this course runs" (About me stays per deck); the Wooclap URL is a placeholder until the event exists. Built: `Quarto/lectures/_series/dgist-2026f.yml` (16 sessions from the public course page), `scripts/series_assets.py` (lock, QR via `qrencode`, 17 deterministic semester-map SVGs with tiered labels and alternating date rows; `--check` compares content, not mtimes, after both reviewers showed mtime checks fail on a fresh clone), `Quarto/_filters/series.lua` (five shortcodes; the week is resolved from the deck name, `week=NN` overrides; the map is inlined so the theme font applies), the four shared includes, `.qr-slide` in the theme, `deckprofile` series resolution with a loud `ConfigError` on an unknown index, the prior-session name in the gate message, `new_deck.py --series`, landing grouped by course. Acceptance: `test_series.py` (93 checks incl. render-level cases), all other suites, four decks at 100, `sync_to_docs.sh` + `check_site_assets.py` 179/179 with the series figures deployed, the fixture renders all shared slides, and a scaffolded `dgist-2026f-w02` rendered in a scratch copy rings W02 without any kwarg. Open for the presenter: the map's type is small for a 100-seat room at the specified 1100x300 viewBox (titles about 17 px on the slide); two of the four rule lines wrap; both are content/design calls to make with W02.

### WP5 - Speaker notes for lectures (D13)

- Keep the existing three layers (clean filter, CI strip, `backup_notes.py`); they are verified end to end. Notes are inline `::: {.notes}` under each slide, Korean, plus `title-slide-attributes: data-notes:` for the title. Retire `sync_notes.py` (WP1) and the `_script/` presenter-script convention with it, or keep `_script/` as a free-form local scratch dir that nothing parses.
- `write-speaker-notes` and `script-writer.md`: read the profile guidance and `deck.yml` (audience, speaking minutes, notes language); remove the paper-review-only instructions; add the lecture ones (open on the previous session, gloss each term in Korean in the note the first time it appears, "you already know X" bridges).
- Document the speaker view (`S`) and the dual-display leak test in `AGENTS.md`.
- Accept: a scaffolded lecture deck with two notes passes `strip_qmd_notes.py` (no Hangul in the staged blob) and the deployed HTML has zero `class="notes"`; `backup_notes.py backup|restore` round-trips.

**Record (2026-08-20): done on branch `wp567/notes-agents-pdf`.** `write-speaker-notes` and `script-writer` are genre-aware (profile + deck.yml first; lecture notes open on the prior session from the series, gloss terms in Korean on first use, carry the exact spoken sentences; budget = speaking_min x 280 syllables / 130 words). `backup_notes.py` was rewritten, not patched: the heading-keyed design lost the title-slide `data-notes` block on checkout and clumped include-line notes under the wrong heading; format 2 records positions in the stripped text, restores byte-identically against a sha1 with an anchored fallback, and keeps the v1 path. The note-filter test now covers the title `data-notes` leak. Acceptance ran on a scaffolded throwaway `dgist-2026f-w04`: strip 0 Hangul, CI strip 7 blocks to zero, backup/restore ROUND-TRIP IDENTICAL, then deleted. `Quarto/_script/` stays as unparsed local scratch.

### WP6 - Review agents for lectures (D23)

- Every reviewing agent (`pedagogy-reviewer`, `proofreader`, `slide-auditor`, `script-writer`) receives the deck's resolved profile and `deck.yml` as context; `pedagogy-reviewer` drops "advanced students".
- Repurpose `domain-reviewer` into a fact-check agent that compares dates, numbers, and autonomy labels on the slides against a source list the deck names (`deck.yml: sources: [...]`, for W02 the vault `research.md`) and against `<deck>.forbidden.txt`.
- Add a visual render audit: headless Chrome walks `?slide=N` for every slide at 1280x720, saves PNGs, and an agent reviews them for overflow, missing posters, illegible text. Reuse the deterministic `?slide=` approach recorded in the RoboTTT work; do not use `--virtual-time-budget`.
- `slide-excellence` becomes the one fan-out: auditor + pedagogy + proofreader + fact-check + render audit, each optional by profile.
- Accept: running `/slide-excellence` on the WP2 fixture produces one report per agent with the audience stated correctly.

**Record (2026-08-20): done on the same branch.** All four agents start from `deckprofile.py` + deck.yml and state the audience; density findings quote the deck's own budget; `domain-reviewer` is the fact-check agent (sources from deck.yml, autonomy labels cross-checked against the video manifest, forbidden list in spirit); the devil's-advocate questions have one home, the pedagogy agent. `scripts/shoot_slides.py` is the single screenshot engine (deckpath resolution, stale re-render, CDP walk, parallel-safe); the fixture `shoot.py` is a shim. `slide-excellence` = the five-way fan-out with per-profile gating and reports under `quality_reports/reviews/`. Static acceptance verified (frontmatter, context passing, screenshots on the gates fixture and two real decks); the fan-out itself has not been launched end to end - the first `/slide-excellence` on the W02 draft is the live acceptance and each report header must state the audience.

### WP7 - PDF handout (D10)

- `scripts/export_pdf.sh <deck>`: decktape (`reveal` mode) or headless Chrome on the rendered HTML with `?print-pdf`, output to `exports/<deck>.pdf` (gitignored). Notes must not be in the PDF; assert by grepping the PDF text for a sentinel Korean phrase after `strip`.
- Theme `@media print`: `<video>` hidden, poster shown, fragments resolved, footnotes kept.
- Accept: W02 fixture exports 42 pages with posters where videos were; no Hangul in the PDF text layer.

**Record (2026-08-20): done on the same branch.** `scripts/export_pdf.sh` uses decktape reveal mode at 1280x720 (`--pause 1000`): the video fixture's pages show posters, not black frames, verified visually page by page, so the theme's `?print-pdf` selector gap never applies (that mode was rejected). The Hangul assertion is sharper than the plan text: zero Hangul beyond the deck's own note-stripped visible source (design-test's committed two-character gloss is legitimate, D18), and a leaked note fails even when its Hangul also exists in the qmd because the allowed set is built after `strip_qmd_notes.py`. `exports/` is gitignored. design-test exports 21 pages, the video fixture 4; the 42-page W02 export happens when W02 exists.

### WP8 - Author `dgist-2026f-w02`

- `/new-deck` with the series set; author in batches of 5-10 slides from the vault content brief; videos through the shortcode; figures per D21; notes inline; `/slide-excellence`; `export_pdf.sh`; merge to `main` when the presenter says so (D11).

## 5. Non-goals

- Two build targets, offline mode, or a local-first `<source>` (D8).
- Timing or TTS tooling (D16).
- Persistent QR, logo slot changes (D19).
- Automatic export of a series list for the MkDocs course page (D12).
- Anything W04/W06/aSSIST might need that W02 does not (D24).
- Repo rename (D4).

## 6. Risks

- Classroom playback depends on the network (D8). Mitigation: play the deck end to end on the classroom network before the session; the trimmed mp4s exist locally and a one-line source swap is possible by hand if it comes to that.
- Third-party clips on a public page (D6). Mitigation: `videos.yml` records publisher, source URL, and date for every clip; a takedown means deleting one Release asset, and the slide degrades to its poster.
- First real exercise of the main theme and the lecture profile. Mitigation: WP0-WP3 fixtures before any W02 slide exists; keep the audit's 14-slide probe as a regression fixture.
- The Korean pre-commit gate rejects any Hangul outside notes; `korean_allowance` (WP2) must land before W02's glossed slides, or the first W02 commit fails.

## 7. Verification (repeat at the end of every WP)

```
python3 scripts/test_profiles.py
python3 scripts/test_minyaml.py
bash scripts/test_note_filter.sh
bash scripts/test_korean_gate.sh
bash scripts/sync_to_docs.sh && python3 scripts/check_site_assets.py docs
for d in $(python3 scripts/deckpath.py --list); do python3 scripts/quality_score.py "$(python3 scripts/deckpath.py $d --field qmd)" --summary; done
```

Rendering is not verification; walk the fixture decks in a browser after WP0, WP3, WP4, and WP7.
