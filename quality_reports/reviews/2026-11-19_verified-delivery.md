# Paper2PR delivery verification

The local branch is `codex/verified-delivery`, based on the fetched `origin/main` at `dc364cb`. The full PR verification command ran against clean implementation commit `e6bc0ed06881`. The review work used its own checkout. The active W13 worktree supplied read-only teaching references.

```bash
./verify --changed-from origin/main --regressions --site _site
```

Shared changes selected all eight publishable decks and the three fixtures. The run passed the six existing regression suites, the site-packaging and affected-deck tests, and the full-index note and PR language checks. All eight published decks scored 100/100 against their actual audience HTML. Each audience page was derived from one fresh render. The browser fetched those bytes over loopback before taking its screenshots, and DeckTape fetched the same bytes before exporting the handout.

| Audience build | Slides and PDF pages | Forward actions, repeated in reverse | Checked widths at 720 px high |
| --- | ---: | ---: | --- |
| design-test | 21 | 20 | 1280, 896 |
| series | 7 | 6 | 1280, 896 |
| video | 4 | 4 | 1280, 896 |
| dgist-2026f-w02 | 47 | 60 | 1280, 896 |
| dgist-2026f-w06 | 58 | 116 | 1280, 896 |
| dgist-2026f-w09 | 96 | 124 | 1280, 896 |
| DreamDojo | 50 | 49 | 1280 |
| DreamZero | 58 | 57 | 1280 |
| RoboTTT | 51 | 82 | 1280 |
| SUNY | 62 | 76 | 1280 |
| tta-2026 | 47 | 46 | 1280 |

The run produced 734 final-fragment PNGs and 501 PDF pages. All 470 local references resolved and all 144 Release URLs on the published pages returned HTTP 200. The video fixture had six additional verified Release URLs. The landing page remained byte-identical to the base revision, with eight canonical deck URLs and four legacy redirects intact. The local Pages tar contained 470 files. Every extracted file matched the verified site by SHA-256, and the extracted site passed the asset and privacy checks. The per-deck hashes, navigation counts and handout hashes are in the run's `verification.json`. The runtime archive is `exports/verified-pages.tar`. Its SHA-256 is `91f1330613b0abe5f971b6b39b6d889f2587b393e070268748953ef91a030445`.

## Delivery and privacy

- The five previous media inventories account for 85 managed clips. Their 170 approved video and poster URLs match the baseline and the existing public releases. A clip without a redistribution decision defaults to classroom use. The four legacy decks retain 25 explicitly marked playback-only embeds at their original hosts.
- A real mixed-manifest render played the local inline and background classroom examples in Chrome. Its public version showed publisher links. A recording `gh` and HTTP stub received exactly the explicitly approved pair. Revoked approval, a tampered poster mapping and protected release filenames, tags or URLs failed before an external write.
- In a disposable normal clone and linked worktree, a real `git add` kept the presenter text in the QMD and removed it from the staged blob. An unbalanced fence failed the add and preserved the previous index entry. Two speaker-note canaries appeared in the local Reveal speaker window and zero appeared in the public notes panes. New clones require the documented Git bootstrap before staging presenter material.
- A one-deck copy-edit PR simulation ran all six suites, published only the selected audience page into a local directory and produced its three-page handout. A separate `--delivery classroom` run included the local video and poster. A catalog with every deck opted out produced an empty public landing page and still verified the three private fixtures.
- A disposable deck's QMD hash and mtime remained fixed through three targeted runs. An include-only edit changed the public text and frame. A theme-only edit then changed the compiled stylesheet and frame. The three audience hash prefixes were `817860af2b95`, `86705273e28c` and `6a292ece9d73`.

## Visual, factual and teaching evidence

- All 99 DreamZero equations rendered. All 11 HLS players advanced on entry and return with their full pictures and captions inside the canvas. All 58 named slides matched the baseline's IDs in order. Comparing the frames exposed clipped demonstrations and teaching text. Twelve DreamZero layouts were repaired. The training slide now gives 880 tokens per latent frame, matching the authors' AgiBot configuration and implementation. [Training recipe](https://github.com/dreamzero0/dreamzero/blob/ab790c198fbce33503358efbbd4187ce9a89adf3/scripts/train/agibot_training.sh#L62-L91) · [Definition of frame sequence length](https://github.com/dreamzero0/dreamzero/blob/ab790c198fbce33503358efbbd4187ce9a89adf3/groot/vla/model/dreamzero/modules/wan_video_dit_action_casual_chunk.py#L318-L342)
- The visual review also repaired twelve DreamDojo slides, one RoboTTT slide and two SUNY slides. The browser now traverses all nine unnumbered RoboTTT appendix slides. The rasterized video handout showed the full poster and its attribution strip. [Audience canvas review](2026-11-19_audience-canvas.md)
- The earliest committed W02 slide already includes its repair. Reconstructing the archived one-column arrangement put its caption 200 px below the canvas at 1280 and 140 px below at 896. The approved slide cleared the bottom by 115 and 80 px. The reconstruction and approved slide used the same original clip. [W02 replay](2026-11-19_w02-caption-replay.md)
- The archived W13 replay detected 13 lost obligations in the shortened lecture. The restored version retained the first-year audience, ten ordered chapters, eight required demonstration checks and 3,000 teaching seconds plus ten minutes for questions. Removing a player from a comparison or moving the opening Atlas demo to the closing chapter failed. The author can still choose other examples, diagrams and reveal sequences. [W13 replay](2026-11-19_framework-presenter-brief.md)
- A changed-number review of TTA compared `8d05a00` and `e5c00c5`. The primary report gives less than 0.15% weight movement after ten steps. The archived 2.5–11.4% statement failed that check. The approved 83% mean task-success statement remained supported. The paired source check took 35 seconds and needed no presenter intervention. [Generalist's GEN-1.5 report](https://generalistai.com/blog/gen-1.5)

## Toolchain and release boundary

The local render and CI setup read `.quarto-version`. The macOS Quarto 1.11.9 archive matched the upstream SHA-256. KaTeX 0.19.1, hls.js 1.7.4 and the locked DeckTape 3.17.0 passed the browser and PDF checks. [Quarto release](https://github.com/quarto-dev/quarto-cli/releases/tag/v1.11.9) · [KaTeX release](https://github.com/KaTeX/KaTeX/releases/tag/v0.19.1) · [hls.js release](https://github.com/video-dev/hls.js/releases/tag/v1.7.4) · [DeckTape release](https://github.com/astefanutti/decktape/releases/tag/v3.17.0)

The local runs used macOS arm64, Chrome 157.0.8103.79, Node 22.20.0 and Python 3.11.6. Linux executable discovery was exercised with a PATH fixture. The workflow passed actionlint 1.7.12. A pull request gets a contents-read verification job. The publish job on main holds the Pages and OIDC write permissions. Checkout, Configure Pages, Upload Pages Artifact and Deploy Pages were pinned after the local PR path passed. [Checkout](https://github.com/actions/checkout/releases/tag/v7.0.1) · [Configure Pages](https://github.com/actions/configure-pages/releases/tag/v6.0.0) · [Upload Pages Artifact](https://github.com/actions/upload-pages-artifact/releases/tag/v5.0.0) · [Deploy Pages](https://github.com/actions/deploy-pages/releases/tag/v5.0.1)

A hosted Actions run, GitHub Pages deployment and a deployed speaker-window check require an authorized remote run. Projector and caption placement, classroom connectivity and delivery pace require a rehearsal. All uploads in this verification were simulated.

## Local implementation commits

Review the series in order with `git log --reverse --oneline dc364cb..e6bc0ed06881`.

| Commit | Change |
| --- | --- |
| `f3f7c92` | Plan verified classroom and public delivery |
| `ebd0cb4` | Pin Quarto 1.11.9 for reproducible renders |
| `2352de8` | Share a pinned KaTeX 0.19.1 renderer across decks and fixtures |
| `a4908c5` | Pin DreamZero HLS playback to hls.js 1.7.4 |
| `e80db78` | Open DreamZero directly on the demo after its title |
| `6259407` | Lock DeckTape 3.17.0 and validate handouts from the verified HTML |
| `863d81b` | Exercise every DreamZero equation and HLS player on navigation |
| `ac1965a` | Protect presenter notes in Git worktrees and public HTML |
| `14509cc` | Check PR changes with the existing language policy |
| `86f874a` | Separate classroom playback from approved clip redistribution |
| `b5050f2` | Use resolved Quarto includes for handout language checks |
| `36ccc9e` | Verify final audience frames and reverse clicker navigation in Chrome |
| `fefa6f1` | Verify fresh audience builds with one local command |
| `c3f555d` | Verify pull requests read-only and isolate Pages deployment |
| `afea27f` | Recut classroom media when a library source link changes |
| `78e6417` | Load DreamDojo demos on slide entry so handout export can start |
| `c130819` | Check presenter briefs and resolved slides against the audience build |
| `7f9fcfc` | Share brief-led authoring and proportionate review across agents |
| `05b4d92` | Rebuild the site when deck publication settings change |
| `a9c3239` | Assemble note-free audience sites from referenced runtime assets |
| `63b7b7f` | Report handout navigation timeouts without exposing browser console text |
| `b9598a5` | Serve cold browser loads reliably and capture uncounted appendix slides |
| `da4a233` | Show speaker notes with extra classes in Reveal presenter view |
| `27e3474` | Verify visible demonstrations and their agreed chapter placement |
| `25c3e97` | Bind verification receipts to browser frames and exercise speaker view |
| `360b623` | Upgrade verified Pages actions and group future updates |
| `bb29b3d` | Check neighboring navigation for edits to a deck's final slide |
| `9f40a49` | Evaluate language exceptions against staged deck and profile metadata |
| `73a83d7` | Include the validated Pages marker in the uploaded artifact |
| `5c1a239` | Check approved Release metadata against private vocabulary before remote calls |
| `f05b6c6` | Redact protected vocabulary in URL-encoded audience references |
| `a39e9d2` | Keep DreamZero comparison clips and captions inside the projected frame |
| `68bbe63` | Verify the landing page when every deck opts out |
| `e7f6d0f` | Check live landing membership against the declared publishing policy |
| `d765e96` | Link the startup instructions to QA and linked-worktree setup |
| `c6f508c` | Fit DreamDojo evidence and its interpretation on twelve legacy slides |
| `23d759e` | Keep design fixtures verifiable when reference decks opt out |
| `b62cd35` | Keep DreamZero teaching figures and conclusions on screen |
| `66ad1cc` | Reserve room for all three RoboTTT task descriptions |
| `545b9a5` | Keep SUNY product features and labor figures clear of the footer |
| `45c60df` | Classify existing hosted video embeds and verify public playback policies |
| `e6bc0ed` | Check rendered teaching text and figures against the audience canvas |
