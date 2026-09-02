# AGENTS.md -- Paper2PR: presentation framework

**Project:** Paper2PR
**Presenter:** Yunsung Lee
**Institution:** WoRV, MaumAI
**Branch:** main

---

## Core Principles

- **Plan first** -- enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** -- compile/render and confirm output at the end of every task
- **Single source of truth** -- Quarto `.qmd` is the only source; there is no other export format. Presentations are delivered from the rendered RevealJS HTML
- **Design principles** -- extreme minimalism, big type, centered content; see `.claude/rules/slide-design-principles.md` (mandatory for new decks)
- **Quality gates** -- nothing ships below 80/100; a forbidden term or a level-1 heading is a BLOCKER (score 0), see `.claude/rules/quality-gates.md`
- **[LEARN] tags** -- when corrected, save `[LEARN:category] wrong → right` to MEMORY.md
- **English only** -- all content committed to git must be in English (see Language Policy below)

---

## Language Policy

**All content pushed to GitHub must be in English.** This includes documentation, session logs, commit messages, comments, and slide content.

**Exceptions:**
- `.claude/skills/` and `.claude/agents/` may contain Korean examples for bilingual functionality
- Speaker notes in QMD files are automatically stripped by the git clean filter (see Speaker Notes below)
- A deck that declares `language.slides: ko` in its own `<deck>.deck.yml`. That is the supported way to get Korean slides -- per deck, written on purpose. Do not add a path exemption for it; a directory exemption covers every future deck in that directory, including the ones that should stay English.
- An English deck may carry up to `language.korean_allowance` Hangul characters (term glosses, Wooclap instructions), counted on the staged qmd after the notes filter. The lecture profile allows 300, the others 0; a deck may set its own number.

**Enforcement:**
- Pre-commit hook (`scripts/check-korean-pre-commit.sh`) blocks Korean text in staged files
- Exempt paths: `.claude/skills/`, `.claude/agents/`
- git runs a *copy* at `.git/hooks/pre-commit`, and that copy is the wrapper `scripts/pre-commit.sh`: the speaker-note gate first, then this one. Editing either script does nothing until `bash scripts/setup-git-filters.sh` reinstalls it -- `scripts/test_korean_gate.sh` checks the installed hook matches before checking anything else

## Speaker Notes Policy

Speaker notes (a fenced div in the `notes` class, plus the front matter `title-slide-attributes: data-notes:` block that carries the title slide's notes) are **local-only** and never reach git:

1. **Git clean filter** strips notes from QMD before staging (`.gitattributes` + `scripts/strip_qmd_notes.py`). Every spelling pandoc reads as a notes div is removed, not only `::: {.notes}`: `:::{.notes}`, `::: notes`, `::: {.notes .fragment}`, more colons, and a note with another div nested inside it. An unbalanced notes fence exits non-zero so git aborts the add.
2. **Commit gate** `scripts/check-notes-pre-commit.sh` (part of the installed pre-commit hook) refuses the commit when the clean filter is not configured in this clone, when a staged deck qmd is not covered by the `.gitattributes` pattern, or when the staged blob still carries a notes div or a `data-notes:` line. The first two are how this defence fails silently.
3. **CI/CD pipeline** strips notes from HTML during deployment: `scripts/strip_notes.sh` runs `scripts/strip_speaker_notes.py` on every rendered deck (`<aside class="notes">` elements and section `data-notes` attributes)
4. **Backup/restore** via `python3 scripts/backup_notes.py backup|restore [Deck]`; backups land in `.speaker-notes/` (gitignored). A backup records each block's lines verbatim, both fences included, so a restore reproduces whatever spelling the author used.
5. **Setup** (run once after clone): `bash scripts/setup-git-filters.sh`

```bash
./scripts/setup-git-filters.sh                 # one-time, after clone
python3 scripts/backup_notes.py backup DreamZero    # insurance against git checkout
python3 scripts/backup_notes.py restore DreamZero   # after clone or accidental checkout
```

- **Never maintain separate branches** for notes vs no-notes; the filter and CI strip are the only mechanism

**Presenter view (how the notes are used in the room):**

- Press `S` in the rendered deck: reveal's speaker view opens in its own window with the notes, a timer, and the next slide. The projector keeps the plain deck; the notes exist only on the presenter's screen (plan D9/D13).
- **Dual-display leak test**, before presenting from a new deploy: open the *deployed* URL, press `S`, and step through a few slides -- the notes panel must show NOTHING, because deployed HTML carries zero notes. Open the *local* rendered file and press `S` -- the same panel shows the notes. If the deployed speaker view shows any note text, the strip pipeline is broken; stop and fix it before class.
- Per-deck notes for shared include slides (series lectures) go in the deck right after the `{{< include >}}` line: everything before the next `##` belongs to the included slide.

---

## Project Scope

**Every presentation Yunsung gives is built here** -- paper reviews, invited talks, and course lectures. The name is historical; the repo is a framework, and it keeps the name because published slide URLs depend on it.

![Deck lifecycle: video and series manifests plus the project defaults feed quarto render; the quality gate, a push to main and CI publish the deck to GitHub Pages; clips live on a GitHub Release, while speaker notes and the PDF handout never leave the presenter's machine](assets/pipeline.svg)

Left to right: `quarto render` builds `<deck>.qmd` under the `Quarto/_quarto.yml` defaults and the `Quarto/_filters/*.lua` shortcodes, `scripts/quality_score.py` grades the result, and a push to `main` hands it to `.github/workflows/deploy.yml`, which selects decks whose config does not set `publish: false`, then re-runs `render_decks.sh`, `strip_notes.sh`, `assemble_site.sh`, `check_site_assets.py` and `check_release_media.py` (the local references resolve, and the Release URLs the pages point at answer 200). Off the main line: `scripts/media_prep.py` and `scripts/series_assets.py` turn the two manifests into the `videos.json` and `series.json` locks the shortcodes read, `scripts/media_release.sh` puts the clips on the deck's Release, the clean filter `scripts/strip_qmd_notes.py` keeps speaker notes out of git, and `scripts/export_pdf.sh` writes the local-only handout. The source is `assets/pipeline.svg`.

Decks live at `Quarto/<genre>/<name>.qmd`, where genre is one of the lines in `Quarto/_genres.txt`. Listed genres are eligible for Pages publishing; an individual deck opts out with `publish: false` in its `.deck.yml`. A deck's figures, speaker-note backups, and presenter scripts are scoped the same way, so one rule finds everything a deck owns. Adding a genre is two edits and no code: a line in `_genres.txt`, and `genre_default: <genre>` in the profile that should grade it. `deckprofile.py` reads the genre-to-profile mapping from the profiles themselves, and `test_profiles.py` fails when a genre has no profile claiming it.

Each deck declares its own premises in `<deck>.deck.yml` -- who is listening, for how long, what they have already seen, which language the slides and notes are in, and whether Paper2PR Pages should publish it. Those are not documentation. `quality_score.py` reads them to pick a bullet budget and decide which checks apply, the Korean gate reads them to decide how much Hangul this deck may carry, `/write-speaker-notes` reads them for the script budget, and the deploy pipeline reads `publish`. Start a deck with `/new-deck`, which interviews for the presentation premises and defaults to publishing. Set `publish: false` only when the deck is hosted elsewhere: it excludes the deck from Paper2PR Pages and its landing page, but source on `main` remains public and `quarto render Quarto/<genre>/<deck>.qmd` still works.

`deck.yml` fields (`python3 scripts/deckprofile.py <deck>` shows the resolved values):

| Field | Read by | Meaning |
|-------|---------|---------|
| `profile` | gate | which `slide-profiles/<profile>.yml` grades the deck (default: the genre's) |
| `publish` | deploy, landing | whether the deck appears on Paper2PR Pages; omitted or `true` publishes, while `false` excludes it without affecting GitHub source or direct Quarto rendering |
| `duration_min` | notes budget | wall-clock minutes of the slot |
| `video_min`, `qa_min` | notes budget | minutes spent on clips and on Q&A; `speaking_min = duration_min - video_min - qa_min` is what the script is budgeted on |
| `language.slides`, `language.notes` | Korean gate, notes | `ko` slides are exempt from the gate; notes default to `ko` |
| `language.korean_allowance` | Korean gate | max Hangul characters an English deck may carry after the notes filter (deck, else profile: lecture 300, others 0) |
| `sources` | fact-check agent | paths or URLs the slides are compared against |
| `series`, `series_index` | gate, landing, scaffold | the course series (`Quarto/lectures/_series/<series>.yml`) and the deck's session in it; `deckprofile.py` resolves `session_date`, `session_title` and `prior_session` from the series lock, an index the series does not have is a hard error. `series_index: 1` (with or without a series) exempts the deck from the prior-session callback |
| `checks.*` | gate | per-deck override of any profile switch (e.g. `level1_heading: off`) |
| `citations.ignore` | gate | citation keys the broken-citation check must skip, for the `@` forms the scan misreads |
| `audience.*`, `delivery` | review agents | context for `/slide-excellence`, not consumed by the gate |

Two optional files next to a deck are read when they exist: `Quarto/<genre>/<deck>.forbidden.txt` (one term per line, `#` comments; any hit in visible slide text is a BLOCKER) and `Figures/<genre>/<deck>/figures.yml` (`file`, `source`, `licence`, `third_party` per figure; a third-party figure needs its source on the slide). Both are documented in `.claude/rules/quality-gates.md`.

| Genre | Profile | Audience | Length |
|-------|---------|----------|--------|
| `papers` | `paper-review` | knows deep learning | ~30 min |
| `talks` | `invited-talk` | varies, declare it | varies |
| `lectures` | `lecture` | no background | ~60 min |

Paper reviews: each paper is reviewed from its arXiv or PDF source, which the presenter supplies; nothing copyrighted is checked in. A review deck runs 40-60 slides (minimalist slides mean more, lighter slides; splitting beats packing) covering main ideas, technical details, and personal insight. When official code is available, include implementation-level observations.

## Slide Design Principles (new decks)

Shared core: `.claude/rules/slide-design-principles.md`. Per-genre budgets and extra checks: `.claude/rules/slide-profiles/<profile>.yml`. The short version of the core:

1. **Extreme minimalism** -- one idea per slide; ≤5 one-line bullets (≤3 with a figure), ≤1 colored box; a bullet that wraps to two lines costs a slot and only one is allowed per slide; split rather than pack
2. **Big type** -- 40px root font; `.smaller`/`.smallest` and font-size overrides are forbidden in new decks (quality gate deducts -5 each)
3. **Filled frame** -- title pinned at top, content centered vertically and horizontally (theme does this; escape hatches: `{.top-align}`, `{.left}`, `{.statement}`)
4. **Slide types** -- dividers, full-bleed video, inline video, charts, formula legends, timelines are theme classes, not hand-built layouts; see the Quarto CSS Classes table below and `Quarto/_fixtures/design-test.qmd` for a rendered example of each

New decks use `clean-academic.scss`; `center: false` and `auto-stretch: false` reach them from the `Quarto/_quarto.yml` project defaults, not from the deck's own front matter. Legacy decks (DreamZero, DreamDojo, RoboTTT) are pinned to `clean-academic-legacy.scss` and exempt from the new rules.

## Videos

Every clip a deck shows is declared once in `Figures/<genre>/<deck>/videos.yml` and
never referenced by URL from a slide. The pipeline, in order:

1. **Manifest** `videos.yml`: a `videos:` list; per entry `slug` (`[a-z0-9-]`), `title`,
   `publisher`, `source_url`, `published` (YYYY-MM), `autonomy` (`autonomous | claimed |
   teleop | unknown`) are required; `speed` (default `1x`), `segment` (`S-E` or `S-`
   seconds in the source), `source` (path to the source file, relative to the deck's
   `videos/` dir or absolute; absent means `videos/<slug>.mp4` is already final),
   `keep_audio` (default false), `caption` (`visible | fragment | none`), `licence_note`
   are optional. `release_url` / `poster_url` do NOT belong here.
2. **Encode** `python3 scripts/media_prep.py <Deck>`: cuts the segment, re-encodes to
   1280 wide H.264 (`-crf 23 -maxrate 8M`, audio stripped unless `keep_audio`), extracts
   the poster at the segment start, and writes `videos.json` (the lock file: every
   manifest field plus `file`, `poster_file`, `size_mb`, `duration_s`, `autonomy_label`,
   and the deterministic `release_url` / `poster_url` for the tag `media-<deck>`). A clip is
   re-encoded when it is missing, older than its source, or its `segment` / `keep_audio` /
   `source` differ from the `cut` record the lock keeps for it (so nudging a segment and
   re-running really re-cuts; the reason is printed). `--only <slug>` leaves the other
   entries' records untouched and `media_release.sh` refuses to upload while any record
   disagrees with the manifest. A clip
   over 30 MB is warned about: trim the segment or raise the speed, the cap stays. The
   mp4s and posters are gitignored (`Figures/**/videos/`); `videos.yml` and `videos.json`
   are committed. `<Deck>` may also be a path to a `videos.yml` or its directory (the
   fixture: `Quarto/_fixtures/video`, tag `media-fixture-video`).
3. **Release** `bash scripts/media_release.sh <Deck>`: creates the public GitHub Release
   `media-<deck>` if missing, uploads every mp4 and poster (`--clobber`), then polls each
   URL until it answers 200 (a fresh asset can 404 for a few minutes). `--check` only
   verifies and exits 1 listing any missing asset. It refuses to run when `videos.json` is
   older than `videos.yml`. Releases are public as soon as the media is ready; the notes
   point at the manifest for every third-party clip's publisher.
4. **Slides** read `videos.json` only, through `Quarto/_filters/video-manifest.lua`:
   - `{{< video-card slug >}}` -- a `figure.video-card` with the clip (poster first, muted
     loop, reveal `data-autoplay` + lazy `data-src`: plays on entry, pauses on leave, loads
     only within reveal's view distance), a print-only poster image, and the caption strip
     `title | publisher · Mon YYYY · label · speed`. `class="..."` adds classes to the figure.
     One shortcode per paragraph (blank line between two); two side by side go inside
     `::: {.two-up}`.
   - `{{< video-caption slug >}}` -- the caption strip alone, for a full-bleed slide.
   - `## {.video-full video="@slug"}` -- the clip is the reveal background (the poster
     travels as `data-background-poster` and is painted under it; a plain path still works).
   - `caption: fragment` makes the strip a reveal fragment; `caption: none` omits it.
   - Autonomy labels are plain: `autonomous`, `autonomy claimed`, `teleoperated`,
     `autonomy not stated`.
   - A missing `videos.json` or unknown slug fails the render (exit 1, no page written);
     nothing emits an empty card. Inside a Quarto render the Lua global `error` is a
     non-throwing logger, so the filters abort with `assert(false, msg)`; `test_media.py`
     proves it with a real render.
   - Wiring: `Quarto/_quarto.yml` lists `_filters/video-card.lua` under
     `format.revealjs.shortcodes` (Quarto 1.8 registers shortcode handlers from that key
     only; the same file under `filters:` runs as a filter and its handlers are never found)
     and `_filters/slide-types.lua` under `filters:`. Fixtures under `Quarto/_fixtures/`
     are outside the project and declare both themselves plus `video-manifest: <path>`.
5. **Authoring before the Release exists**: `media_prep.py <Deck> --local` writes
   `videos.json` with `local_only: true`; the shortcodes and `@slug` then point at
   `../../Figures/<genre>/<deck>/videos/...` so the deck previews offline. Run
   `media_prep.py` again without `--local` before deploying: `check_site_assets.py` fails
   any deployed page that references `Figures/**/videos/`, and `assemble_site.sh` prunes
   those directories from the site.

The classroom trusts the network (D8): play the deck through once on the classroom
connection before the session so the browser cache is warm.

PDF handouts (`bash scripts/export_pdf.sh <Deck>`, D10) go through decktape's
screen capture, not reveal's `?print-pdf` mode: a paused clip paints its poster
attribute and a background clip its `data-background-poster` underlay, so every
video slide lands in the PDF as its poster with the caption strip intact
(verified on the video fixture; the theme's `@media print` block only matters
when someone prints the HTML from a browser). The export needs the network once,
to fetch the posters from the Release. The script then refuses to ship any PDF
whose text layer carries Hangul the deck does not visibly show itself -- the qmd
after the notes strip, entities decoded, is the allowed set -- so a leaked
speaker note fails the export naming the page while a D18 gloss passes.

## Series

A course is declared once, in `Quarto/lectures/_series/<course>.yml` (underscore
directory: outside the Quarto project, never rendered as a deck), and every lecture
of the course reads from it instead of repeating a date, a room or a URL on a
slide. Same shape as the videos: a hand-written yml, a Python script that writes a
JSON lock plus images, Lua shortcodes that read the lock.

1. **Series file** `Quarto/lectures/_series/<course>.yml` (schema in its header):
   `course`, `code`, `term`, `institution`, `room`, `time`, `instructor`,
   `co_instructor`, `course_page`, `lms_note`, `qa_tool` (`name`, `url`, `code`,
   `note` -- `code` is always quoted, it is an identifier the slide prints as
   written), `rules` (the lines of the "How this course runs" slide), `notation`
   (`policy`, `note`), optional `meets_on` (a weekday name or a list of them that
   every session must fall on; omit it for a block course that runs on whatever
   days the room was free), and `sessions`: one mapping per week with `index` (the
   week number), `date` (quoted `YYYY-MM-DD`, on a `meets_on` day), `kind`
   (`lecture | guest | keynote | dgist | holiday | exam`), `title`, `presenter`,
   `deck` (the deck name, or `""`; a planned name is fine, nothing requires the
   deck to exist yet), optional `tag` (overrides the short word the map prints
   under the dot, at most 12 characters -- this is how the DGIST midterm week
   prints "report"), optional `remote` / `tentative`. An unknown top-level key is
   an error. `dgist-2026f` is the DGIST HSS118 term.
2. **Build** `python3 scripts/series_assets.py <course>`: validates the yml (one
   mapping per week with unique indices 1..N, increasing dates on the `meets_on`
   days, kinds from the enum, unique decks) and writes `Figures/lectures/_series/<course>/`: `series.json`
   (the lock: the yml plus, per session, `week` "W02", `short_date` "Sep 4",
   `prior_index` = the nearest earlier session that is not a holiday or exam week; a
   guest or DGIST session counts), `qr-qa.png` and `qr-qa.svg` (qrencode, from
   `qa_tool.url`), `semester-map.svg` and one `semester-map-wNN.svg` per session
   with that week ringed in gold as "today". The map is one 1100x200 timeline with a
   dot per session, showing only dates and short kind tags, never session titles:
   the short date above each dot (bold for lecture / guest / keynote, muted
   otherwise) and a kind tag below ("Lecture", "Guest", "Keynote", "DGIST";
   "holiday" for holiday weeks, "report" / "essay" for the exam weeks). Dates and
   tags alternate two rows by index parity, and a layout whose texts would
   overlap fails loudly (SeriesError) instead of rendering. Output
   is byte-deterministic, and a re-run rewrites only files whose bytes change.
   `--check` verifies every file exists and is byte-identical to a fresh in-memory
   render from the yml (content, never mtimes: a clone or checkout lands the yml
   and the figures in any order, and a comment-only edit to the yml changes no
   output). The Wooclap URL and code are `PLACEHOLDER` until the
   Message wall event exists: replace both in the yml and re-run the script; the
   slides pick the new QR up through the lock. Everything in the directory is
   committed (`assemble_site.sh` copies `Figures/*`, so the QR ships with the site).
3. **Shortcodes** `Quarto/_filters/series.lua` (wired in `Quarto/_quarto.yml`
   `format.revealjs.shortcodes`, next to `video-card.lua`; fixtures and includes
   outside the project repeat it). They find the course from `series: <course>` in
   the deck's YAML front matter (`new_deck.py --series` writes it) and the deck's own
   session from its file name (the session whose `deck` equals `<deck>` in
   `Quarto/<genre>/<deck>.qmd`); `week=NN` forces one.
   - `{{< semester-map >}}` -- the map with this deck's week ringed, inlined as
     `<figure class="semester-map"><svg ...>` (inlined, not linked, so the theme font
     reaches the SVG text); `plain=true` for the unhighlighted one; a deck that is
     not a session gets the plain map unless `week=NN` is given.
   - `{{< series-qr >}}` -- `<div class="qr-block">` with the QR (`RELPATH/qr-qa.svg`)
     and the `.qr-meta` line (tool, **code**, URL without scheme).
   - `{{< series-field key >}}` -- inline text of a scalar (`course`, `code`,
     `term`, `room`, `time`, `lms_note`, `qa_tool.name`, `notation.policy` ...).
   - `{{< series-rules >}}` -- a bullet list of `rules`.
   - `{{< series-session key >}}` -- `title | date | short_date | presenter | week |
     kind | index | prior_title | prior_date | prior_short_date | prior_presenter |
     prior_week | prior_kind | prior_index` of this deck's session (or `week=NN`).
   - No `series:` metadata, no lock, an unknown key or a session without a prior all
     fail the render with one "(E) series:" line (`assert`, as in
     `video-manifest.lua`). RELPATH is computed from the input file's directory to
     `Figures/lectures/_series/<course>/` (`../../Figures/...` from
     `Quarto/lectures/`, one more `../` from a fixture), which survives deployment
     because `slides/<genre>/` sits next to `Figures/` there too.
4. **Shared slides** `Quarto/lectures/_series/<course>/*.qmd`, included by every
   lecture of the course with `{{< include _series/<course>/<file>.qmd >}}` (path
   relative to the deck); per-deck speaker notes go in the deck right after the
   include line (content before the next `##` belongs to the included slide). For
   `dgist-2026f`: `semester-map.qmd` ("The semester in one picture"),
   `course-runs.qmd` ("How this course runs": the rules, the LMS line as footnote),
   `ask-anytime.qmd` and `qa.qmd` (the two `{.qr-slide}`s: a 420px QR, the meta
   line, one sentence; plan D19 puts the QR on those two slides only and nowhere
   persistent). `new_deck.py --series` writes the four includes into the stub in
   that order (map, rules, ask-anytime near the top; Q&A last).
5. **Consumers**: `deckprofile.py` resolves `series` / `series_index` to
   `series_course`, `session_date`, `session_title`, `prior_session` (from the lock,
   or the yml when the lock is absent) and fails on an index the series lacks;
   `quality_score.py` names that prior session when the callback slide is missing;
   `new_deck.py --series <course> --series-index <NN>` prefills title, date and the
   name `<course>-w<NN>`; `build_landing.py` groups the lecture decks of a series
   under "`<course> (<code>, <institution>, <term>)`" ordered by `series_index`
   (week, date, title, link), decks without a series stay in the plain table.
   Fixture: `Quarto/_fixtures/series/series.qmd` (the four includes plus the
   shortcodes, `week=2` where the fixture pretends to be W02).

## Folder Structure

```
paper2pr/
├── AGENTS.md                    # Canonical agent instructions for this repo
├── .claude/                     # Rules, skills, agents, hooks
├── assets/                      # Images used by README.md and AGENTS.md (repo-only, not deployed)
├── Bibliography_base.bib        # Centralized bibliography (grows per paper)
├── Figures/<genre>/<deck>/      # Per-deck figures, SVG/PNG only, plus the video home:
│   ├── videos.yml               #   clip manifest (hand-written, committed)
│   ├── videos.json              #   lock file written by media_prep.py (committed)
│   └── videos/                  #   trimmed mp4s + posters (gitignored; on the Release)
├── Figures/lectures/_series/<course>/   # series.json lock, qr-qa.{png,svg}, semester-map*.svg
│                                #   (written by scripts/series_assets.py, committed)
├── Quarto/
│   ├── _genres.txt              # Which directories are eligible to publish; deck.yml may opt out
│   ├── _quarto.yml              # Project defaults for every deck (canvas, filter, shortcodes, fonts)
│   ├── _filters/slide-types.lua # .divider / .video-full (video="@slug") -> reveal background attributes
│   ├── _filters/video-card.lua  # {{< video-card >}} / {{< video-caption >}} shortcodes
│   ├── _filters/video-manifest.lua # the one reader of videos.json, shared by both
│   ├── _filters/series.lua      # {{< semester-map >}} / {{< series-qr >}} / {{< series-* >}}
│   ├── _filters/inline-svg.lua  # {{< inline-svg path >}}: an SVG chart inlined so the theme font reaches it
│   ├── lectures/_series/        # <course>.yml (the series file) + <course>/*.qmd shared slides
│   ├── clean-academic*.scss     # Shared themes (main + legacy)
│   ├── fonts/                   # Pretendard (Hangul fallback), linked by _quarto.yml
│   ├── _widgets/ _script/       # Shared includes; presenter scripts (gitignored)
│   ├── _fixtures/               # design-test.qmd + theme-mockups/ + gates/ + video/ + series/ -- not a genre, never published
│   │   ├── gates/               # pass.qmd / trip.qmd: one deck that trips every gate check, one that passes
│   │   ├── video/               # the video pipeline end to end (manifest -> Release media-fixture-video -> shortcodes)
│   │   └── series/              # the series object: shared includes + every series shortcode
│   └── <genre>/                 # <deck>.qmd + <deck>.deck.yml + per-deck assets
├── .speaker-notes/<genre>/      # Note backups (gitignored -- notes never enter git)
├── exports/                     # PDF handouts from scripts/export_pdf.sh (gitignored)
├── docs/                        # Local deploy preview from scripts/sync_to_docs.sh
│                                #   (gitignored; CI publishes from _site)
├── pages/index.html             # Landing page, GENERATED by scripts/build_landing.py
├── scripts/                     # Utility scripts. Python here is stdlib-only
│                                #   on purpose -- see scripts/minyaml.py
├── quality_reports/             # Plans, session logs, merge reports (history, never edited)
└── templates/                   # Session log and speaker-notes report templates
```

---

## Commands

```bash
# Start a new deck (interviews for the premises, then scaffolds)
/new-deck

# Quarto render (primary workflow -- decks are authored and delivered in Quarto)
quarto render Quarto/<genre>/<Deck>.qmd

# Where does this deck keep its things? (bare name resolves the genre)
python3 scripts/deckpath.py <Deck> --field figures --relative
python3 scripts/deckpath.py --list

# What is this deck graded against?
python3 scripts/deckprofile.py <Deck>

# One 1280x720 PNG per slide, in reading order (re-renders a stale html first;
# also takes a .qmd or .html path). The render audit and /visual-audit read these
python3 scripts/shoot_slides.py <Deck> [--out DIR] [--max N]

# Videos: encode the deck's clips from its videos.yml, then publish them on the
# deck's GitHub Release (media-<deck>) and verify every URL answers 200
python3 scripts/media_prep.py <Deck> [--only slug] [--dry-run] [--force] [--local]
bash scripts/media_release.sh <Deck> [--check]

# Series: rebuild a course's lock, QR and semester maps from its yml; --check
# verifies they exist and match what the yml produces (content, not mtimes)
python3 scripts/series_assets.py <course> [--check]
python3 scripts/series_assets.py --list

# PDF handout (D10): decktape export to exports/<deck>.pdf (gitignored), posters
# stand in for videos; re-renders a stale html; also takes a .qmd or .html path;
# fails loudly if Hangul beyond the deck's own visible text reaches the PDF
bash scripts/export_pdf.sh <Deck> [--out FILE]

# Deploy eligible decks to GitHub Pages (automatic via CI/CD on push to main)
git push  # Decks with publish: false stay out of the Pages artifact

# Local deploy preview -- renders, assembles exactly as CI does, then checks assets
./scripts/sync_to_docs.sh [Deck]

# Regression tests
bash scripts/test_note_filter.sh    # the note filter still covers every depth and every notes spelling; the commit gate still refuses
python3 scripts/test_profiles.py    # the profiles still grade differently; the gate checks still trip on the fixtures
python3 scripts/test_minyaml.py     # the config parser still agrees with PyYAML
bash scripts/test_korean_gate.sh    # the Korean gate still blocks, still exempts, still honours korean_allowance
python3 scripts/test_media.py       # videos.yml validation, media_prep output, shortcode lookup, the local-media gate
python3 scripts/test_series.py      # series yml validation, the lock and maps, prior-session resolution, deckprofile / new_deck / landing, the fixture render

# Quality score
python scripts/quality_score.py Quarto/<genre>/<Deck>.qmd

# Theme fixture: one slide per layout rule and slide type (outside the Quarto project,
# so it repeats the _quarto.yml defaults itself)
cd Quarto/_fixtures && quarto render design-test.qmd
# Video fixture: the whole video path, playing from the public Release media-fixture-video
cd Quarto/_fixtures/video && quarto render video.qmd
# Series fixture: the four shared slides and every series shortcode, as W02
cd Quarto/_fixtures/series && quarto render series.qmd
```

---

## Quality Thresholds

| Score | Gate | Meaning |
|-------|------|---------|
| 80 | Commit | Good enough to save |
| 90 | PR | Ready for deployment |
| 95 | Excellence | Aspirational |

---

## Skills Quick Reference

| Command | What It Does |
|---------|-------------|
| `/new-deck [topic]` | Interview a new deck's premises, scaffold it, and carry authoring through the quality gate (the single entry point) |
| `/deploy [Deck]` | Render Quarto + deploy (CI/CD on push) |
| `/slide-excellence [Deck]` | The one review fan-out: slide-auditor + pedagogy-reviewer (with the devil's-advocate challenges) + proofreader + fact check (`domain-reviewer`, against `deck.yml: sources:`) + render audit of `shoot_slides.py` screenshots. Every agent starts from `deckprofile.py` + `deck.yml` and states the audience; reports land in `quality_reports/reviews/` |
| `/visual-audit [Deck]` | Standalone adversarial layout audit on full-deck screenshots from `shoot_slides.py` (density against the profile budget, overflow, font, box fatigue, centering) |
| `/write-speaker-notes [Deck] [--lang en\|ko]` | Generate the presentation script (speaker notes) for a deck, genre-aware via its resolved profile |
| `/validate-bib` | Cross-reference citations against `Bibliography_base.bib` |
| `/commit [msg]` | Stage, commit, PR, merge |
| `/learn [skill-name]` | Extract discovery into persistent skill |
| `/context-status` | Show session health + context usage |
| `/deep-audit` | Repository-wide consistency audit |

---

## Quarto CSS Classes

| Class | Effect | Use Case |
|-------|--------|----------|
| `.primaryblue` | Primary blue text | Headings, emphasis |
| `.primarygold` | Gold text | Secondary emphasis |
| `.primaryyellow` | Yellow text | Highlight markers |
| `.hi` | Bold primary blue | Inline key terms |
| `.hi-gold` | Bold gold | Inline secondary emphasis |
| `.hi-green` | Bold green | Positive results |
| `.hi-red` | Bold red | Negative results, limitations |
| `.positive` | Green + bold | Good outcomes in comparisons |
| `.negative` | Red + bold | Bad outcomes, limitations |
| `.neutral` | Gray | Context, reference values |
| `.compact` | Tighter spacing | Lists needing more items |
| `.footnote` | Bottom-positioned small text | Source attributions |
| `.methodbox` | Blue-bordered div | Technical details |
| `.keybox` | Gold-bordered div | Key insights |
| `.highlightbox` | Yellow-bordered div | Notable findings |
| `.resultbox` | Gold-bordered with shadow | Main results |
| `## {.divider}` | Navy full-bleed chapter block; `.divider-number` / `.divider-title` / `.divider-sub` stack | Section breaks |
| `## {.video-full video=".." poster=".."}` or `video="@slug"` + `.video-caption` / `{{< video-caption slug >}}` | Clip as the slide background (looped, muted, cover), slide chrome hidden, caption strip at the bottom | Hook clips, montages |
| `.video-inline` | 16:9 clip inside a normal content slide | A demo next to bullets |
| `{{< video-card slug >}}` (`figure.video-card`) | Clip + caption strip from `videos.json`; poster printed instead of the video | A declared clip next to bullets |
| `::: {.two-up}` | Two `video-card`s in one flex row, 48 percent each | Side-by-side montage |
| `{{< inline-svg path [width=..] >}}` (`figure.chart-figure`) | An SVG file inlined at 64% width (or `width=`), so its text is set in the theme font; under a chart or a video card, bullets sit a notch smaller | One chart plus takeaways |
| `::: {.question-overlay .fragment .fade-out fragment-index="1"}` | A statement centred over the content area before the first click, gone after it; the content's first fragment takes the same index | A show of hands before the answer is revealed |
| `.formula-legend` | Centered symbol list under a 2em display formula | Hero equation slides |
| `.gloss` | Small gray line pinned to the bottom of the content area | Korean or plain-language gloss of a term |
| `.timeline` | `.tl-item` grid on a gold rail: one row up to six items, two rows of four from seven | Dated milestones |
| `{{< semester-map >}}` (`figure.semester-map`) | The course timeline from the series lock, inlined SVG at full content width, this deck's week ringed | The shared "semester in one picture" slide |
| `## Title {.qr-slide}` + `{{< series-qr >}}` (`.qr-block`) | A 420px QR of the question wall with the tool / code / URL line under it, one sentence below | The orientation and Q&A slides only (D19) |

`{{< inline-svg path >}}` (`Quarto/_filters/inline-svg.lua`, wired next to the video and series shortcodes) reads the file relative to the deck and emits it inside `figure.chart-figure`; use it for a chart the deck owns instead of `![](chart.svg)`, because an `<img>` SVG cannot reach the page's web font and renders in Helvetica or Arial. Once inlined the file is part of the page, so the SVG must carry an `id` on its root, scope every `<style>` selector with it (`#s13-ilsvrc text {...}`), and keep its `<title>` / `<desc>` / marker ids unique; `width` and `height` attributes stay off the root (the theme sizes it from the `viewBox`). A missing file fails the render.

Line breaking is the theme's job, not the author's: `.reveal p`, `li` and `figcaption` carry `text-wrap: pretty` (no single-word last line), `h2`, `.statement` and a standalone centred paragraph carry `text-wrap: balance`. Where a break carries meaning (two sentences of a statement), write the `<br>`.

`.smaller` and `.smallest` still exist in the theme for the legacy decks only; they are forbidden in new decks (quality gate deducts -5 each). `.divider` and `.video-full` get their full-bleed backgrounds from `Quarto/_filters/slide-types.lua`, which turns the class and its `video=` / `poster=` attributes into reveal `data-background-*` attributes (the poster is painted under the background video by a small script the filter includes; it must not become `data-background-image`, which reveal 5.1 loads *instead of* the video); `Quarto/_quarto.yml` wires the filter and the video shortcodes for every deck under a genre directory. Each slide type has a rendered example in `Quarto/_fixtures/design-test.qmd`; the video path end to end is `Quarto/_fixtures/video/video.qmd`.

---

## Current Project State

| Deck | Quarto (source) | Theme | Key Content |
|------|-----------------|-------|-------------|
| DreamZero | `papers/DreamZero.qmd` | legacy | NVIDIA - World Action Models as Zero-shot Policies |
| DreamDojo | `papers/DreamDojo.qmd` | legacy | NVIDIA - A Generalist Robot World Model from Large-Scale Human Videos |
| RoboTTT | `papers/RoboTTT.qmd` | legacy | NVIDIA GEAR - Context Scaling for Robot Policies (PR-561) |
| SUNY Career Sprint | `talks/SUNY.qmd` | own (suny-career) | Career Roadmap for AI Researchers: From Papers to Products (April 4, 2026) |

New decks: main theme (`clean-academic.scss`) + `.claude/rules/slide-design-principles.md`. "legacy" = pinned to `clean-academic-legacy.scss`, exempt from the design principles.
