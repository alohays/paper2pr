# Paper2PR authoring reference

Paper2PR serves paper reviews, invited talks and course lectures from Quarto. The public URL for a deck is `slides/<genre>/<deck>.html`. Each source lives at `Quarto/<genre>/<deck>.qmd` and its assets at `Figures/<genre>/<deck>/`. The root instructions describe the everyday workflow. [Agent instructions](../AGENTS.md)

Paper reviews use the supplied paper as the primary source. Include the main ideas, technical details, the presenter's interpretation and relevant observations from official code. A thirty-minute paper review often spans 40 to 60 lightweight slides. Keep source paper copies local.

## Deck metadata

`<deck>.deck.yml` records the audience, prior experience, duration, delivery, sources, language and course session. Run `python3 scripts/deckprofile.py <deck>` for the resolved values. Profiles under `.claude/rules/slide-profiles/` define the defaults for each genre in `Quarto/_genres.txt`. A new genre needs an entry there and a profile with a matching `genre_default`.

`duration_min` covers the full slot. `qa_min` reserves time for questions. `video_min` counts only quiet playback, so speakers can budget narration over a clip once. A series supplies dates, session titles and the preceding session. Declare `sources` using public primary sources or repository-relative references suitable for sharing. Keep private research paths in the presenter's local working notes.

For assets reached through computed JavaScript URLs, list the file paths under `runtime_assets` in the deck config, relative to the QMD. Assembly follows HTML, CSS and SVG references. The public artifact also receives the configured external private vocabulary scan.

Set `publish: false` for a deck hosted elsewhere. That setting removes its page and listing from Paper2PR Pages. Its tracked sources remain visible to repository readers. New decks inherit publishing and their genre profile by default.

### Optional presenter brief

Use stable slide IDs for the requirements the presenter specifies. Keep the agreed audience and time in the existing deck metadata. For example, a ten-minute demonstration with two minutes for questions might have this brief.

```yaml
duration_min: 10
qa_min: 2
audience:
  assumes: none
  description: First-year undergraduates seeing feedback control for the first time.
brief:
  chapters:
    - slide: read-the-wheel
      title: What can the wheel encoder tell us?
      seconds: 180
    - slide: feedback
      seconds: 300
  demonstrations:
    - slide: turning-wheel
      chapter: read-the-wheel
      clip: wheel-turn
  complete_clock: true
```

A chapter's `slide` names its opening Reveal section, e.g., `## Read the wheel {#read-the-wheel}`. Chapters appear in brief order. A demonstration names its slide and optionally a manifest clip. Add `chapter` with a chapter slide ID when a demo has an agreed placement, such as an opening question or a closing reprise. Either list accepts a plain slide ID when that is the whole requirement. Other slides, examples and reveal steps are the author's choices.

An optional `title` on a chapter or demonstration preserves the presenter’s wording for the teaching reviewer while the slide heading can evolve. Each chapter may have a budget in seconds. When the presenter apportions the whole teaching slot, `complete_clock: true` checks that the budgets sum to `60 × (duration_min - qa_min)`, which includes video time. If the QMD includes per-slide `data-seconds`, verification also checks those figures against the chapter's budget. Actual presentation speed comes from rehearsal. List just the constrained items for a partial brief. Chapter and demonstration checks inspect the rendered audience sections and their clip markers. Reviewers assess what those sections teach. The [archived W13 fixture](../Quarto/_fixtures/gates/w13-brief.yml) preserves an example with ten chapters and a fifty-minute clock.

## Notes and delivery

Install the note filter and commit hook once with `bash scripts/setup-git-filters.sh`. Notes belong in a fenced `.notes` div following their slide; the title slide uses `title-slide-attributes.data-notes`. Back them up with `python3 scripts/backup_notes.py backup <deck>` before changing checkouts. The matching `restore` command reads the ignored backup in `.speaker-notes/`. Press `S` on the local deck to open the presenter's notes, timer and next slide. On a new deployment, the same action should show an empty notes panel.

The media guide covers source manifests, approved release assets, classroom playback, publisher links, poster handouts and shortcodes. [Media guide](media.md)

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
   an error. `dgist-2026f` is the DGIST HSS118 term (Seminar for Comprehensive Competency Cultivation, SCCC).
2. **Build** `python3 scripts/series_assets.py <course>`: validates the yml (one
   mapping per week with unique indices 1..N, increasing dates on the `meets_on`
   days, kinds from the enum, unique decks) and writes `Figures/lectures/_series/<course>/`: `series.json`
   (the lock: the yml plus, per session, `week` "W02", `short_date` "Sep 4",
   `prior_index` = the nearest earlier session that is not a holiday or exam week; a
   guest or DGIST session counts), `qr-qa.png` and `qr-qa.svg` (qrencode, from
   `qa_tool.url`), `semester-map.svg` and one `semester-map-wNN.svg` per session
   with that week ringed in gold as "today". The map is one 1100x300 timeline drawn
   for the student who wants to know when the talks are: a month band, one mark per
   session, a date only above the talks (lecture / guest / keynote, 23 px bold; the
   kind is the mark: navy dot, navy dot with a white core, gold diamond), a small
   muted tag under the quiet weeks only ("holiday", "report", "essay") and a legend
   row; never session titles or presenter names. The host institution's own sessions
   (`kind: dgist`) are a hollow navy mark that prints nothing, and their `tag:` is
   the legend's wording, so a course names its own weeks ("Leadership talk", not
   "DGIST session"); a tag printed under a dot is capped at 12 characters, a legend
   one at 24. A talk date moves to a far
   row (hairline down to its dot) only when the talk before it is adjacent, and a
   layout whose texts would overlap fails loudly (SeriesError) instead of rendering. Output
   is byte-deterministic, and a re-run rewrites only files whose bytes change.
   `--check` verifies every file exists and is byte-identical to a fresh in-memory
   render from the yml (content, never mtimes: a clone or checkout lands the yml
   and the figures in any order, and a comment-only edit to the yml changes no
   output). A new series starts with the Wooclap URL and code set to
   `PLACEHOLDER`; once the Message wall event exists, replace both in the yml and
   re-run the script, and the slides pick the new QR up through the lock. Everything in the directory is
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

