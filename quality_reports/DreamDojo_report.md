# Proofreading Report: DreamDojo.qmd

**Date:** 2026-03-17
**Reviewer:** proofreader agent
**File:** `Quarto/DreamDojo.qmd`

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Medium | 3 |
| Low | 5 |

---

## Medium Issues

### M1. Em-Dash Usage Inconsistency

The file uses three different dash styles:
- `---` (triple-hyphen, line 50): "how to move" --- inverse dynamics
- `---` (line 82): DreamZero is a policy, DreamDojo is a simulator
- `$\rightarrow$` (line 96): used as an arrow in "robot data -> in-distribution"

This is mostly consistent (triple-hyphen for em-dashes, LaTeX arrow for logical flow), but line 114 uses `---` as an attribution dash before `@gao2026dreamdojo`, which in standard typography should be an em-dash without surrounding spaces or should use a dedicated attribution format.

**Fix:** Standardize attribution format. Either use `-- @gao2026dreamdojo` (en-dash) or wrap in a footnote class.

### M2. Slide 33b Table: Tokenizer Naming Mismatch

Line 922: "Wan2.1 ($4\times$)" vs "WAN2.2 ($4\times$)" -- note the capitalization difference (Wan vs WAN). Check whether the paper uses "Wan" or "WAN" consistently. This could confuse readers into thinking these are different products rather than different versions.

**Fix:** Use consistent capitalization. The paper refers to "WAN 2.2" (all caps), so standardize to "WAN 2.1" for DreamZero as well.

### M3. Equation Variable Definitions Incomplete

Slide 19 (line 523-530): The distillation loss uses $s_{\text{real}}$ and $s_{\text{fake}}$ without defining them. The reader must infer these are score functions. Similarly, $G_{\text{student}}$ is used without formal definition (though contextually clear).

**Fix:** Add parenthetical: "where $s_{\text{real}}$, $s_{\text{fake}}$ are teacher and student score functions."

---

## Low Issues

### L1. "~30 min" Implied but Not Stated

The CLAUDE.md indicates 30-min presentations, but the slide count is ~36 slides including section dividers. This is at the upper end. Not a proofreading error per se, but worth noting for timing.

### L2. arXiv Number Validity

Line 979: "arXiv: 2602.06949" -- arXiv IDs starting with "26" would correspond to 2026. This is plausible given the paper date but is a future paper. Verify this is the correct ID.

### L3. GitHub URL Not Hyperlinked

Line 980: `github.com/NVIDIA/DreamDojo` appears as plain text, not a clickable link. In Quarto revealjs, this will render as plain text.

**Fix:** Wrap in markdown link: `[github.com/NVIDIA/DreamDojo](https://github.com/NVIDIA/DreamDojo)`.

### L4. "dreamzero0.github.io" Not Hyperlinked

Line 985: Same issue as L3. Should be a clickable link.

**Fix:** Wrap in markdown link: `[dreamzero0.github.io](https://dreamzero0.github.io)`.

### L5. Minor: "DreamDojo-HV" vs "HV" Label Inconsistency

The dataset is called "DreamDojo-HV" on Slides 5 and 22, but shortened to "HV" in the data mixture table (Slide 6, line 162) and comparison table (Slide 22). This is acceptable shorthand but could confuse on first encounter.

---

## Citation Cross-Reference

All 11 bibliography keys referenced in the QMD are present in `Bibliography_base.bib`:

| Key | Status |
|-----|--------|
| `gao2026dreamdojo` | Present |
| `ye2026dreamzero` | Present |
| `ali2025world` | Present |
| `huang2025self` | Present |
| `gao2025adaworld` | Present |
| `bruce2024genie` | Present |
| `peebles2023scalable` | Present |
| `lipman2022flow` | Present |
| `zhang2023adding` | Present |
| `yin2024one` | Present |
| `goswami2025dexwm` | Present |

All citations validated.

---

## Grammar and Spelling

No grammatical errors or spelling mistakes found. The writing is clear, concise, and maintains an appropriate academic register throughout. The "My Take" sections use a slightly more informal tone, which is appropriate for personal commentary.

## Overall Proofreading Assessment

**EXCELLENT** -- The text is clean and well-written. The issues found are minor formatting inconsistencies rather than substantive errors. All citations are valid. The main actionable items are the tokenizer capitalization mismatch and unhyperlinked URLs.
