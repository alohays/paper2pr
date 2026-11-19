# Verifying an audience build

Run `./verify <deck>` from a checkout with the QA dependencies installed. A deck can be a bare name or a genre/name pair. The command prints the directory containing its evidence under `exports/verify/`.

## One-time setup

Use Python 3.11 or later, Node 22.12 or later, the Quarto release in `.quarto-version`, Chrome or Chromium, FFmpeg, qrencode and Poppler. On macOS the system Chrome application is supported. On Linux install Chrome or Chromium on PATH. Set `CHROME` to an executable to select a particular installation. Download the matching Quarto release for your platform and put its executable on PATH or unpack its `bin` and `share` directories into `.tools/quarto/`. [Quarto downloads](https://github.com/quarto-dev/quarto-cli/releases)

```bash
bash scripts/setup-git-filters.sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-qa.txt
PUPPETEER_SKIP_DOWNLOAD=true npm ci
```

FFmpeg includes ffprobe. Poppler supplies pdfinfo, pdftotext and pdftoppm. On macOS install these command-line tools with `brew install ffmpeg poppler qrencode`. On Ubuntu use `sudo apt-get install ffmpeg poppler-utils qrencode`. The verifier picks up the project virtual environment and checks the Quarto pin. Normal authoring and Git hooks use the Python standard library.

## Choose the audience

| Command | What it verifies |
| --- | --- |
| `./verify DreamZero` | The public page, every final fragment, both navigation directions and the handout. DreamZero also checks the equations and waits for every HLS player to advance on entry and return. |
| `./verify dgist-2026f-w02 --delivery classroom` | Classroom playback and the handout. Prepare any classroom-only files first with `python3 scripts/media_prep.py <deck>`. |
| `./verify <deck> --slide <section-id>` | A fresh affected-slide capture and its neighboring transition. The hash fragment in the rendered slide URL identifies its section. |
| `./verify --all --regressions --site _site` | The full Pages simulation, every publishable deck and the design, video and series fixtures. |
| `./verify --changed-from origin/main --regressions --site _site` | The CI pull-request path. It compares commits with the merge base. Shared runtime, filter, theme, include and build changes widen the build. |

The render next to the QMD retains the presenter's notes. Verification assembles a separate audience copy and runs the asset checks, browser and handout against those bytes. The browser checks 1280 by 720 pixels and adds the DGIST caption-room viewport of 896 by 720 for course decks. Each run records the commit, fresh render hash, audience HTML hash, navigation counts and handout hash in `verification.json`. Single-slide checks skip the full PDF. Screenshots, classroom media and handouts stay under ignored local paths.

The release simulation requires network access to referenced release assets and publisher-hosted demos. The output at `_site/` is the artifact intended for Pages. Only a publish job on main can deploy it. GitHub-hosted execution, the presenter's pacing and the classroom projector, audio and network can be checked at the authorized release and rehearsal.
