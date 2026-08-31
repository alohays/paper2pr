# Final Fact Check: dgist-2026f-w02

**Date:** 2026-08-30
**Reviewer:** domain-reviewer agent (fact check)
**Profile:** lecture | **Audience:** First- and second-year undergraduates outside AI-related majors; assumes no prior AI background; 93 students
**Source precedence applied:** `deck-plan.md` §1b > `★8/30` blocks > slide planner text > `outline.md`
**Sources read:**

- `/Users/iyunseong/Documents/vault/1-projects/maum/dgist-future-literacy-2026fall/lectures/w02-paradigm-shift/outline.md` - read end to end
- `/Users/iyunseong/Documents/vault/1-projects/maum/dgist-future-literacy-2026fall/lectures/w02-paradigm-shift/assets/README.md` - read end to end
- `/Users/iyunseong/Documents/vault/1-projects/maum/dgist-future-literacy-2026fall/lectures/w02-paradigm-shift/deck-plan.md` - read end to end

**Coverage:** all 823 QMD lines; all 47 slide-note payloads (title `data-notes` plus 46 fenced note blocks); all 12 `videos.yml` and `videos.json` records; all 30 `figures.yml` records; visible SVG text; both generated semester maps; and all 6 forbidden terms. No web sources were introduced.
**Read-only verification:** `videos.yml`/`videos.json` parity passed; all 12 local media records were fresh in a dry run; `series_assets.py dgist-2026f --check` passed.

## Summary

- **Overall:** MEDIUM ISSUES
- **Critical:** 0 | **Medium:** 2 | **Low:** 2
- **S34 remediation:** PASS. The shipment count is now explicitly company-reported, and the 460% IPO movement is explicitly tied to the debut day.
- **Autonomy audit:** PASS for all 12 clips and their spoken caveats.
- **Rejected/internal claims:** PASS. No rejected claim, forbidden-term equivalent, internal project or dataset name, or customer disclosure appears in the slides or notes.

## Medium findings

### 1. The notes add an unsourced attendance-policy consequence

- **Location:** `Quarto/lectures/dgist-2026f-w02.qmd:62`
- **Speaker-note meaning:** "A signature entered by someone else will not be accepted."
- **Source evidence:** `outline.md:66` and `deck-plan.md:213-220` authorize an entrance sign-in sheet and random TA spot-checks. Neither source states the additional consequence for a proxy signature.
- **Why it matters:** This is a grading-policy claim in a course where attendance is 40% and three absences result in F. It should not be inferred beyond the official record.
- **Fix:** Verify the rule against the official DGIST policy or LMS notice, or soften it to the instruction "Please sign for yourself."

### 2. The ILSVRC numbers are never identified as top-5 error

- **Location:** `dgist-2026f-w02.qmd:202`, `:211`, and `:215`; `s13-ilsvrc.svg:2-3` and `:50`
- **Deck says:** The chart and narration call the values generic image-recognition or photo-recognition error rates.
- **Source says:** `assets/README.md:52` identifies the entire series as ILSVRC top-5 error. `deck-plan.md:390-391` expressly requires the simplified axis to be accompanied by a footnote naming the top-5 metric.
- **What is correct:** The values 28.2, 25.8, 16.4, 11.7, 6.7, 3.57, and the approximately 5.1 human reference all match the source; the 2015 ensemble and single-annotator qualifications are also present.
- **Why it matters:** Omitting the metric materially obscures what the machine-human comparison measures, even though the numerical trend remains correct.
- **Fix:** Name "ILSVRC top-5 error (%)" in the figure or footnote and use the same term once in the narration.

## Low findings

### 1. Three required flex-skip cues are absent from the notes

- **Location:** S17, S28, and S34 note blocks at `dgist-2026f-w02.qmd:303`, `:517`, and `:633`
- **Source evidence:** `outline.md:54` requires S17, S28, and S34 to be pre-marked as skip candidates; `deck-plan.md:478-479`, `:728-729`, and `:885` preserves that requirement.
- **Impact:** This is not a factual error, but the final script omits the source-required delivery cue.
- **Fix:** Add a local note-only skip marker and the prescribed one-sentence bridge for each slide.

### 2. The Ask-anytime note refers to a screen address that is not displayed

- **Location:** visible fallback at `dgist-2026f-w02.qmd:84-86`; speaker instruction at `:94-97`
- **Mismatch:** The note tells students to use "the address on screen," while the current fallback slide displays only "code announced in class" and no address or QR.
- **Source evidence:** `deck-plan.md:254-257` describes the intended QR state; `deck-plan.md:1070` permits the current announced-code fallback.
- **Fix:** Change the spoken instruction to "Use the address and code announced in class," or restore the intended QR/address before delivery.

## S34 remediation evidence

- **Visible slide:** `dgist-2026f-w02.qmd:624` now says, "Unitree reports 5,500+ humanoids shipped in 2025; its $904M IPO rose 460% on debut."
- **Visible attribution:** `dgist-2026f-w02.qmd:628-630` explicitly says the shipments are company-reported.
- **Speaker notes:** `dgist-2026f-w02.qmd:633` says the shipment count comes from the company's IPO document and explains that 460% is the first trading day's movement.
- **Canonical source:** These qualifications match `deck-plan.md:101` and `:104`. All remaining S34 values also match: Figure $1B+ at $39B; Skild $1.4B at $14B+; NEURA up to $1.4B; Unitree 5,500+, $904M, and 460%; NVIDIA's open GR00T reference humanoid; and Google DeepMind's whole-body Gemini Robotics 2.

## Autonomy and video evidence

| Clip | Final label and required caveat | Evidence | Result |
|---|---|---|---|
| Atlas drink hook | `autonomy claimed`; label deliberately deferred to the S8 answer | `videos.yml:2-11`; QMD `:113-119`, `:132-140` | PASS |
| Unitree Embodied Avatar | `teleoperated` | `videos.yml:13-22`; QMD `:128`, `:138-140` | PASS |
| Atlas parkour | `autonomous`, explicitly distinguished from learned behavior | `videos.yml:24-33`; QMD `:348-355` | PASS |
| RT-2 extinct animal | `autonomous`; claim limited to a robot-data-absent instruction interpreted through web knowledge | `videos.yml:35-44`; QMD `:468-476` | PASS |
| π0 laundry | `autonomous`; selected demo is not generalized to all laundry or environments | `videos.yml:46-55`; QMD `:534-540` | PASS |
| π0.5 unseen homes | `autonomous`; 10x source burn-in and 1x player rate are both explained | `videos.yml:57-67`; QMD `:543-549` | PASS |
| Helix 2025 | `autonomy not stated`; the separate Helix 02 statement remains a company claim and is not back-projected | `videos.yml:69-78`; QMD `:554-565` | PASS |
| Unitree gala | `autonomy claimed`, not independently established autonomy | `videos.yml:80-89`; QMD `:568-574` | PASS |
| Atlas CES | `autonomy not stated`; no status is inherited from another Atlas clip | `videos.yml:91-100`; QMD `:577-583` | PASS |
| 1X NEO selected cut | `autonomy not stated`; launch-day teleoperation history is kept separate and not generalized | `videos.yml:102-111`; QMD `:586-592` | PASS |
| CostNav | `autonomy not stated`; simulation is disclosed | `videos.yml:113-122`; QMD `:639`, `:646-648` | PASS |
| WoRV bimanual | `autonomous` under the final §1b TTA precedent; described as not real-time teleoperation | `videos.yml:124-133`; QMD `:641`, `:646-648` | PASS |

`videos.json` matches every manifest field and renders the corresponding labels: `claimed` to `autonomy claimed`, `teleop` to `teleoperated`, `unknown` to `autonomy not stated`, and `autonomous` unchanged.

## Other verified facts

- **Data barrier:** The visible SVG and notes carry approximately `10^13` words, `10^7` to `10^9` images, and `10^4` teleoperation hours, with the mixed-unit warning and token-to-word simplification disclosed (`dgist-2026f-w02.qmd:520-531`; `deck-plan.md:739-754`).
- **Timeline:** The eight cells run RT-2 (Jul 2023), OpenVLA (Jun 2024), π0 (Oct 2024), Helix (Feb 2025), Gemini Robotics (Mar 2025), GR00T N1 (Mar 2025), π0.5 (Apr 2025), and Gemini Robotics 2 (Jul 2026). The final-ledger ordering of Gemini Robotics before GR00T N1 is correct, and July 2023 to July 2026 is exactly 36 months (`dgist-2026f-w02.qmd:595-617`; `deck-plan.md:837-847`, `:863`).
- **Course schedule and names:** The title date, prior-session callback, both semester maps, remote dates, and roadmap names agree with the current series lock. Hyeongmin Lee, Sunghwan Hong, and Chris Choi are attached to the intended sessions. The series lock and generated maps are current.
- **Figures:** All 30 manifest entries exist and are referenced by the QMD. The 24 third-party figures have matching author, organization, and year attribution in the relevant slide footers; the five custom SVGs and WoRV logo are correctly marked as non-third-party.

## Forbidden, rejected, and internal-claim findings

None. The slides and notes contain no literal or semantic equivalent of the six forbidden entries: `Optimus Gen 3`, `fifth-gen Atlas`, `GR00T N2`, a Gemini Robotics 2 technical-report claim, `failure`, or `failed`. They also omit every rejected S34 value: the $8.6B aggregate, the approximately $7B NEURA valuation, Unitree global-number-one or $66B claims, and Figure's $2.34B cumulative figure. The notes name only public WoRV material (`CostNav`) and the approved TTA precedent; no internal project, dataset, person, or customer is disclosed.
