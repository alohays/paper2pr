# DGIST W02 optimistic demo-script revision (2026-09-04)

## Goal

Rebalance the Korean speaker notes so the robot demos primarily communicate
technical progress, scaling potential, and useful insight instead of repeating
autonomy caveats, while preserving factual qualifiers and source accuracy.

## Editorial decisions

- Keep the early Atlas autonomy exercise as the one explicit media-literacy
  framework; later demos may retain a short source label but should not repeat
  the full skeptical analysis.
- Give each demo one distinct technical takeaway: closed-loop control,
  environment generalization, shared policies, coordinated execution,
  industrialization, home deployment, or product-scale learning.
- Use a rounded reference rate of KRW 1,360 per USD, based on the 2026-09-03
  Woori Bank USD/KRW base rate, and label every conversion as approximate.
- Preserve all company names, dates, dollar figures, autonomy labels, and
  quoted claims.

## Work plan

1. Audit every demo note and mark repeated autonomy language.
2. Rewrite the affected notes in a more optimistic, capability-first voice.
3. Add selective won conversions to the industry-financing passage.
4. Run the named `humanize-korean` (`im-not-ai`) skill as a separate style-only
   pass and verify its change rate and six preservation checks.
5. Reinsert the polished notes into the QMD, refresh the local note backup,
   render, and run the quality and regression gates.
6. Regenerate the local rehearsal TTS and classroom bundle from the revised
   notes so no derived copy retains the old script.

## Acceptance

- The early framework remains accurate, but later demos do not repeatedly
  argue for or against autonomy.
- Every demo has a positive, technically specific takeaway.
- Dollar-to-won conversions are clearly approximate and internally correct.
- The humanizer changes style only, preserves all factual anchors, stays below
  the 30% warning threshold, and passes all six checks.
- The deck still renders with 47/47 notes and scores at least 80/100.
