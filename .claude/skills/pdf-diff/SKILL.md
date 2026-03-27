---
name: pdf-diff
description: Visual PDF regression test comparing current Beamer output against a baseline branch. Use when checking if slide changes introduced visual regressions.
argument-hint: "[PaperName] [branch, default: main]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Visual PDF Regression Test

Compare the current Beamer PDF output against a baseline branch to detect visual regressions.

## Prerequisites

- `diff-pdf` must be installed (`brew install diff-pdf`)
- The paper's `.tex` file must compile successfully

## Steps

### Step 1: Parse arguments

- First argument: PaperName (required, e.g., `SUNY`, `DreamZero`)
- Second argument: baseline branch (optional, default: `main`)

### Step 2: Compile current version

```bash
cd /Users/iyunseong/maangeek/paper2pr/Slides
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode $PAPER.tex
cp $PAPER.pdf /tmp/${PAPER}_current.pdf
```

### Step 3: Get baseline version

```bash
cd /Users/iyunseong/maangeek/paper2pr
git stash --include-untracked
git checkout $BRANCH -- Slides/$PAPER.tex
cd Slides
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode $PAPER.tex
cp $PAPER.pdf /tmp/${PAPER}_baseline.pdf
git checkout - -- Slides/$PAPER.tex
git stash pop
```

### Step 4: Run diff-pdf

```bash
diff-pdf --output-diff=/tmp/${PAPER}_diff.pdf /tmp/${PAPER}_baseline.pdf /tmp/${PAPER}_current.pdf
echo "Exit code: $?"
```

- Exit code 0: PDFs are visually identical
- Exit code 1: Visual differences detected (diff PDF saved)

### Step 5: Report results

- If identical: "No visual regressions detected."
- If different: "Visual differences found. Diff PDF saved to /tmp/${PAPER}_diff.pdf"
  - Open the diff PDF: `open /tmp/${PAPER}_diff.pdf`
  - Differences are highlighted in red

### Step 6: Cleanup

```bash
rm -f /tmp/${PAPER}_current.pdf /tmp/${PAPER}_baseline.pdf
```

Keep the diff PDF for review if differences were found.

## Notes

- This compares full visual output, including fonts, spacing, and figure rendering
- Single-pass XeLaTeX is sufficient for visual comparison (no bibtex needed)
- For multi-page diffs, `diff-pdf --skip-identical` shows only changed pages
