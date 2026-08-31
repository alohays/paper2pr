# Fact Check: dgist-2026f-w02

**Date:** 2026-08-30
**Reviewer:** domain-reviewer agent (fact check)
**Profile:** lecture | **Audience:** First- and second-year undergraduates outside AI-related majors; assumes no prior AI background; 93 students
**Source precedence applied:** `deck-plan.md` §1b > `★8/30` blocks > slide planner text > `outline.md`
**Sources read:**

- `/Users/iyunseong/Documents/vault/1-projects/maum/dgist-future-literacy-2026fall/lectures/w02-paradigm-shift/outline.md` - read end to end (176 lines)
- `/Users/iyunseong/Documents/vault/1-projects/maum/dgist-future-literacy-2026fall/lectures/w02-paradigm-shift/assets/README.md` - read end to end (84 lines)
- `/Users/iyunseong/Documents/vault/1-projects/maum/dgist-future-literacy-2026fall/lectures/w02-paradigm-shift/deck-plan.md` - read end to end (1,094 lines)

**Forbidden list:** `Quarto/lectures/dgist-2026f-w02.forbidden.txt`, 6 terms
**Additional generated content inspected:** all 602 QMD lines; all 12 `videos.yml` and `videos.json` entries; generated video captions; both semester-map appearances; visible SVG text; the current series lock and schedule. `series_assets.py dgist-2026f --check` passed. No web sources were introduced.

## Summary

- **Overall:** MAJOR ISSUES
- **Claims checked:** 188 grouped factual or data-label items | **Verified:** 187 | **Mismatches:** 1 | **Unsourced:** 0
- The deck otherwise follows the authoritative audit ledger closely. All autonomy states, model dates, schedule names, timeline ordering, and quantitative chart labels agree with the declared local sources.

## Mismatches

### Issue 1: Unitree figures lose mandatory source qualifications

- **Slide:** "The pull now comes from industry, not academia" (`dgist-2026f-w02.qmd`, lines 451 and 456)
- **Severity:** MAJOR
- **Slide says:** "Unitree shipped 5,500+ humanoids in 2025; its $904M IPO surged 460%." The footer gives "Bloomberg / Unitree prospectus, Aug 2026."
- **Source says:** "Unitree: 5,500+ humanoids shipped in 2025; its $904M IPO surged 460% on debut," and explicitly requires the shipment figure to be marked "company-reported (IPO prospectus)" (`deck-plan.md` §2, lines 101 and 104).
- **Why this matters:** The shipment quantity is a company-reported figure, not an independently established count, and the 460% movement is specifically an on-debut change. The current wording turns the first into an unqualified fact and leaves the second without its time window. This is a load-bearing industry-momentum statistic, so the source's mandatory qualification should remain visible.
- **Fix:** Use wording such as "Unitree reports 5,500+ humanoids shipped in 2025; its $904M IPO rose 460% on debut." State in the footer that shipments are company-reported from the IPO prospectus and retain Bloomberg's August 19, 2026 attribution for the IPO figures.

## Unsourced claims

None. Every checkable slide claim is covered by at least one declared source or by generated series/video data that `deck-plan.md` designates as the implementation source of truth.

## Forbidden-term findings

None. No literal hit, translation, abbreviation, near-miss, or equivalent disclosure was found for `Optimus Gen 3`, `fifth-gen Atlas`, `GR00T N2`, `tech report`, `failure`, or `failed`. The "Two Waves, One Wall" sequence consistently uses the approved generalization-wall framing rather than implying that either learning wave failed.

## Verified highlights

- **Autonomy labeling is exact across all 12 video records.** The Atlas hook defers its `autonomy claimed` label to the S8 answer reveal as required; Unitree Embodied Avatar is `teleoperated`; Helix, Atlas CES, the selected NEO interval, and CostNav are `autonomy not stated`; NEO's separate launch-demo teleoperation history is not generalized to the selected clip; and the §1b overrides for CostNav (`unknown`) and WoRV bimanual (`autonomous`) are correctly applied. `videos.yml` and `videos.json` agree.
- **The easy-to-misstate quantitative slides are otherwise correct.** The ILSVRC chart carries 28.2, 25.8, 16.4, 11.7, 6.7, and 3.57 percent for 2010-2015 plus the approximately 5.1 percent human reference, with the 2015 point separately attributed. The data-barrier figure carries approximately `10^13` words, `10^7` to `10^9` images, and `10^4` teleoperation hours, matching the authoritative starred specification.
- **The 2023-2026 timeline honors the final audit ledger.** It places Gemini Robotics before GR00T N1 within March 2025, ends with Gemini Robotics 2 in July 2026, makes no technical-report claim, and omits every prohibited release. The eight cells span exactly 36 months from July 2023 to July 2026.
- **Course dates and names resolve consistently.** Both generated semester maps match the current series lock, the title resolves to W02 on September 4, 2026, the prior-session callback resolves to August 28, and the roadmap names Hyeongmin Lee, Sunghwan Hong, and Chris Choi on the dates specified by the series source of truth.
