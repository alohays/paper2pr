# Proofreading Report: DreamZero

**Files Reviewed:** `Slides/DreamZero.tex` + `Quarto/DreamZero.qmd`
**Date:** 2026-03-15

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Medium   | 4 |
| Low      | 5 |

**Overall:** EXCELLENT -- very clean text with minor consistency issues

---

## Medium Issues

### M1. Inconsistent em-dash spacing
- **Beamer (line 52-53):** `\negative{language-first} ---` (spaced em-dash)
- **Beamer (line 56-57):** `not \emph{physics}` (no em-dash issue here)
- **Quarto (line 49):** `[**language-first**]{.negative} --- vision is a "second-class citizen"` (spaced em-dash -- consistent here)
- The deck generally uses spaced em-dashes ` --- `, which is fine, but there is one inconsistency:
  - **Beamer (line 93-94):** `\emph{``Intelligence is a function of experience.''}` uses single quotes inside double quotes (correct LaTeX), but Quarto (line 84) uses `*"Intelligence is a function of experience."*` which is an italic string with straight quotes inside.
- **Recommendation:** Ensure consistent typographic quote style in Quarto. Consider using smart quotes or removing inner quotes and relying on italic for emphasis.

### M2. Mixed use of "cont." abbreviation
- **Slide 3b title:** "The Data Problem in Robotics (cont.)" -- uses "(cont.)"
- **Slide 36b title:** "What DreamZero Means for the Field (2/2)" -- uses "(2/2)"
- **Recommendation:** Pick one continuation convention and use it consistently. "(1/2)" and "(2/2)" is generally clearer than "(cont.)".

### M3. Inconsistent spacing before `\vspace` in Beamer
- Most slides use `\vspace{0.5em}` as a separator, but spacing varies:
  - `\vspace{0.5em}` (most common)
  - `\vspace{0.3em}` (some slides)
  - No `\vspace` (some transitions)
- This is not an error per se, but the inconsistency suggests some spacing was tuned per-slide while others use defaults.
- **Recommendation:** Standardize on `\vspace{0.5em}` for major section breaks and `\vspace{0.3em}` for minor breaks within a slide.

### M4. "from-scratch" hyphenation inconsistency
- **Slide 4b (line 132):** "VLA from-scratch at ~0%" -- hyphenated as compound modifier
- **Slide 19 (line 645):** "VLA from-scratch: ~0%" -- hyphenated (consistent)
- **Slide 18b (line 614):** "from-scratch & from-pretrained" -- hyphenated (consistent)
- All consistent here, but "from-scratch" is technically a phrasal adjective only when preceding a noun. When used as a predicate ("trained from scratch"), no hyphen is needed.
- **Recommendation:** Minor; current usage is acceptable in presentation context.

---

## Low Issues

### L1. Quotation mark styles in Quarto
- Quarto uses straight double quotes `"..."` consistently (e.g., line 54: `"Language is a bottleneck..."`).
- Beamer uses LaTeX curly quotes ` ``...'' ` (correct).
- RevealJS renders straight quotes as-is, which is acceptable but less typographically refined.
- **Recommendation:** No action needed; Quarto's Pandoc handles this appropriately for HTML output.

### L2. Missing period after "DZ = DreamZero" footnote
- **Beamer (line 811):** `DZ = DreamZero.` -- has period (correct)
- **Quarto (line 614):** `DZ = DreamZero.` -- also has period (correct)
- No issue here upon closer inspection.

### L3. "vs." usage
- Consistently uses "vs." with period throughout (correct in American English).
- Beamer uses `vs.\` (correct for LaTeX non-sentence-ending period).

### L4. Citation format differences between Beamer and Quarto
- Beamer: `\citep{key1,key2}` renders as "(Author1 et al., Year; Author2 et al., Year)"
- Quarto: `[@key1; @key2]` renders as "(Author1 et al. Year; Author2 et al. Year)"
- Minor difference in comma placement is due to Pandoc vs. biblatex rendering.
- **Recommendation:** Acceptable; consistent within each format.

### L5. Subtitle in YAML front matter
- Quarto YAML: `subtitle: "Ye, Ge, Zheng, Gao, Yu et al. (NVIDIA, 2026)"`
- Beamer: `\subtitle{Ye, Ge, Zheng, Gao, Yu et al.\ (NVIDIA, 2026)}`
- The `\ ` before `(NVIDIA` in Beamer is correct LaTeX spacing after abbreviation period; Quarto renders fine without it.

---

## Grammar & Style Checks

All slides pass the following checks:
- [x] No sentence fragments that impede understanding
- [x] Subject-verb agreement
- [x] Consistent tense (present tense for descriptions, past tense for results)
- [x] No spelling errors detected
- [x] Technical terminology used correctly
- [x] Mathematical notation consistent between text and equations
- [x] Figure captions present where needed
- [x] No orphaned bullet points (single-item lists)

---

## Citation Audit

### Citations in Beamer (.tex):
- `rt22023arxiv` -- present in bib
- `kim2024openvla` -- present in bib
- `bjorck2025gr00t` -- present in bib
- `black2024pi0` -- present in bib
- `wan2025wan` -- present in bib
- `ye2026dreamzero` -- present in bib
- `intelligence2025pi05` -- present in bib
- `liu2022flow` -- present in bib
- `lipman2022flow` -- present in bib
- `khazatsky2024droid` -- present in bib

### Citations in Quarto (.qmd):
Same 10 keys -- all present in `Bibliography_base.bib`.

### Unused bib entries (not cited in either file):
- `team2025gemini`
- `teng2025magi`
- `albergo2023stochastic`
- `kim2026cosmos`
- `liao2025genie`
- `zhu2025unified`
- `li2025unified`
- `pai2025mimic`
- `agarwal2025cosmos`
- `hafner2019dream`
- `hafner2020mastering`
- `hafner2023mastering`
- `cheang2024gr2`
- `jang2025dreamgen`
- `du2024video`
- `liang2025video`
- `bu2025agibot`
- `walke2023bridgedata`
- `assran2025vjepa2`
- `lecun2022path`
- `kaplan2020scaling`
- `chi2023diffusion`
- `zhao2023unipc`
- `hu2022lora`

**Note:** 24 of 34 bib entries are unused in the slides. These may be intentionally kept as a comprehensive reference library. Not an error, but worth noting for bibliography maintenance.
