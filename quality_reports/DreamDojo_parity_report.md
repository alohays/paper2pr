# Content Parity Report: DreamDojo.qmd vs DreamDojo.tex

**Date:** 2026-03-17
**Reviewer:** parity-checker agent
**Files:** `Quarto/DreamDojo.qmd` vs `Slides/DreamDojo.tex`

---

## Frame Count Comparison

| Source | Frame Count | Notes |
|--------|------------|-------|
| Beamer (.tex) | 33 frames | Includes 7 section dividers, 1 title, 1 bibliography |
| Quarto (.qmd) | 34 slides | Includes 7 section dividers, 1 title, 1 references |

**Difference:** QMD has 1 extra slide. The Beamer title slide uses `\maketitle` (1 frame), while the QMD has a dedicated teaser slide with background-color AND a separate auto-generated title slide from the YAML frontmatter. Net: +1 in QMD.

---

## Slide-by-Slide Parity

| Slide | Beamer | Quarto | Parity | Notes |
|-------|--------|--------|--------|-------|
| Title | `\maketitle` + teaser | `## {background-color}` + teaser + video | **QMD adds video** | QMD has embedded MP4 video |
| DreamZero Recap | Frame 2 | Slide 2 | Match | |
| From DreamZero to DreamDojo | Frame 2b | Slide 2b | Match | |
| Data Gap | Frame 3 | Slide 3 | Match | |
| Human Video Insight | Frame 4 | Slide 4 | Match | |
| DreamDojo-HV | Frame 5 | Slide 5 | Match | |
| Three Data Sources | Frame 6 | Slide 6 | Match | |
| System Overview | Frame 7 | Slide 7 | Match | |
| Section: LAM | Divider | Divider | Match | |
| Action Label Problem | Frame 8 | Slide 8 | Match | |
| LAM Architecture | Frame 9 | Slide 9 | Match | |
| Latent Actions Cross | Frame 10 | Slide 10 | Match | |
| Latent Actions vs Alt | Frame 11 | Slide 11 | Match | |
| Section: Architecture | Divider | Divider | Match | |
| Cosmos Backbone | Frame 12 | Slide 12 | Match | |
| Flow Matching | Frame 12b | Slide 12b | Match | |
| Two Key Innovations | Frame 13 | Slide 13 | Match | |
| Action Embedding Eq | Frame 14 | Slide 14 | Match | |
| Action Embedding Code | Frame 14b | Slide 14b | Match | |
| Temporal Consistency | Frame 15 | Slide 15 | Match | |
| Post-Training | Frame 16 | Slide 16 | Match | |
| Section: Distillation | Divider | Divider | Match | |
| Distillation Challenge | Frame 18 | Slide 18 | Match | |
| Two-Stage Self Forcing | Frame 19 | Slide 19 | Match | |
| Distillation Results | Frame 20 | Slide 20 | **QMD adds video** | QMD embeds real_time.mp4 |
| Section: Results | Divider | Divider | Match | |
| Benchmarks | Frame 21 | Slide 21 | Match | |
| Data Scaling | Frame 22 | Slide 22 | Match | |
| Human Preference | Frame 23 | Slide 23 | Match | |
| Ablation | Frame 24 | Slide 24 | Match | |
| Multi-Embodiment | Frame 25 | Slide 25 | **QMD adds video** | QMD embeds g1 video |
| Policy Evaluation | Frame 26 | Slide 26 | Match | |
| MPC & Teleop | Frame 27 | Slide 27 | **QMD adds video** | QMD replaces teleop PDF with video |
| Section: Code | Divider | Divider | Match | |
| Why Look at Code | Frame 27b | Slide 27b | Match | |
| Code: LAM | Frame 28 | Slide 28 | Match | |
| Code: DiT | Frame 29 | Slide 29 | Match | |
| Code: Pipeline | Frame 30 | Slide 30 | Match | |
| Code: Relative Actions | Frame 31 | Slide 31 | Match | |
| Section: Discussion | Divider | Divider | Match | |
| Limitations | Frame 32 | Slide 32 | Match | |
| Two Paradigms | Frame 33 | Slide 33 | Match | |
| Technical Comparison | Frame 33b | Slide 33b | Match | |
| Landscape | Frame 34 | Slide 34 | Match | |
| Key Takeaways | Frame 35 | Slide 35 | Match | |
| Thank You | Frame 36 | Slide 36 | Match | |
| References | Bibliography frame | References slide | Match | |

---

## Environment Parity

| Beamer Environment | Quarto Class | Count (tex) | Count (qmd) | Match |
|-------------------|-------------|-------------|-------------|-------|
| `keybox` | `.keybox` | 7 | 7 | Yes |
| `highlightbox` | `.highlightbox` | 3 | 3 | Yes |
| `methodbox` | `.methodbox` | 9 | 9 | Yes |
| `resultbox` | `.resultbox` | 4 | 4 | Yes |
| `eqbox` | `.eqbox` | 6 | 6 | Yes |
| `softbox` | `.softbox` | 10 | 10 | Yes |
| `quotebox` | `.quotebox` | 1 | 1 | Yes |

All box environments are perfectly matched.

---

## Figure Parity

| Beamer Figure | Quarto Figure | Notes |
|---------------|---------------|-------|
| teaser_compressed.pdf | teaser_compressed.svg | Format adapted |
| dataset_compressed.pdf | dataset_compressed.svg | Format adapted |
| mecka_compressed.pdf | mecka_compressed.svg | Format adapted |
| egodex.png | egodex.png | Same |
| inlab.png | inlab.png | Same |
| overview_compressed.pdf | overview_compressed.svg | Format adapted |
| lam_compressed.pdf | lam_compressed.svg | Format adapted |
| design_compressed.pdf | design_compressed.svg | Format adapted |
| pretrain_compressed.pdf | pretrain_compressed.svg | Format adapted |
| long_compressed.pdf | long_compressed.svg | Format adapted |
| context_compressed.pdf | context_compressed.svg | Format adapted |
| benchmark_compressed.pdf | benchmark_compressed.svg | Format adapted |
| correlation_compressed.pdf | correlation_compressed.svg | Format adapted |
| mpc_compressed.pdf | mpc_compressed.svg | Format adapted |
| teleop_compressed.pdf | N/A (video used) | QMD uses embedded video |

All 15 Beamer figures accounted for. The QMD correctly uses SVG versions where available and PNG for raster images.

---

## Content Drift

### Additions in QMD (not in Beamer)

1. **4 embedded videos** -- Title slide, Distillation Results, Multi-Embodiment, MPC & Teleop. These are Quarto-specific enhancements using the project website's MP4 files.

### Missing from QMD (present in Beamer)

1. **teleop_compressed.pdf** -- Beamer uses a static figure for teleoperation; QMD replaces with embedded video. This is an improvement, not a loss.

### Figures in Directory Not Used by Either

- `ui_compressed.svg/.pdf` -- Not referenced in either file
- `value1_compressed.svg/.pdf` -- Not referenced in either file
- `value2_compressed.svg/.pdf` -- Not referenced in either file

These 3 figure pairs exist in `Figures/DreamDojo/` but are unused. They may be intended for future slides or were cut during editing.

---

## Overall Parity Assessment

**EXCELLENT** -- Near-perfect content parity between Beamer and Quarto. All slides match, all environments match, all figures are accounted for. The QMD adds 4 embedded videos as medium-appropriate enhancements. The only "drift" is intentional improvement (video embeds replacing static images for teleoperation).
