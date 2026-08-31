# Focused Fact-Check Verification: dgist-2026f-w02

**Date:** 2026-08-30
**Reviewer:** domain-reviewer agent (fact check)
**Profile:** lecture | **Audience:** First- and second-year undergraduates outside AI-related majors; assumes no prior AI background; 93 students
**Source precedence applied:** `deck-plan.md` §1b > `★8/30` blocks > slide planner text > `outline.md`
**Scope:** Current QMD, all five custom SVGs, both video manifest files, the current series lock, and the relevant passages of all three declared canonical sources. No browsing or deck edits were performed.

## Summary

- **Overall:** CLEAN
- **Critical:** 0 | **Medium:** 0 | **Low:** 0
- All prior Medium 2 and Low 2 findings are resolved.
- S34, all 12 autonomy records and caveats, previously verified numbers and dates, timeline ordering, and internal/rejected-claim exclusions still pass.

## Prior findings: closure evidence

| Prior finding | Current evidence | Canonical evidence | Result |
|---|---|---|---|
| Unsupported proxy-signing consequence | `dgist-2026f-w02.qmd:62` now gives an instruction to write one's own name and states only that the TA spot-checks attendance. It no longer invents a rejection consequence. | `outline.md:66`; `deck-plan.md:213-220` | RESOLVED |
| ILSVRC metric omitted | QMD alt text names top-5 error (`:202`); the footer names "ILSVRC top-5 error" (`:211`); the notes define it as the rate at which the answer is absent from the model's five candidates (`:215`). The SVG title, description, and axis also say top-5 (`s13-ilsvrc.svg:2-3`, `:50`). | `assets/README.md:52`; `deck-plan.md:390-391` | RESOLVED |
| Missing flex-skip cues | Explicit `FLEX CUT` instructions now appear in the S17, S28, and S34 note blocks at QMD `:303`, `:518`, and `:635`, including the required spoken bridge for S17 and S28. | `outline.md:54`; `deck-plan.md:478-479`, `:728-729`, `:885` | RESOLVED |
| Ask-anytime note referred to a nonexistent screen address | QMD `:94` now tells students to use the address and code announced in class. It no longer says the address is displayed. Lines `:96-97` refer back to that announced address/code, consistent with the visible fallback at `:84-86`. | `deck-plan.md:254-257`, `:1070` | RESOLVED |

## S34 regression check

- `dgist-2026f-w02.qmd:626` says, "Unitree reports shipping 5,500+ humanoids in 2025; after a $904M IPO, its shares rose 460% on debut."
- `dgist-2026f-w02.qmd:631` explicitly marks shipments as company-reported.
- `dgist-2026f-w02.qmd:636` says the shipment figure was reported in the company's IPO document and explains that 460% is the first trading day's movement.
- This still matches `deck-plan.md:101` and `:104`. The other S34 values remain unchanged and correct: Figure $1B+ at $39B; Skild $1.4B at $14B+; NEURA up to $1.4B; NVIDIA's open GR00T reference humanoid; and Google DeepMind's whole-body Gemini Robotics 2.

**Result:** PASS. The earlier company-reporting and time-window problem remains fixed.

## Numeric, date, and timeline regression check

- **ILSVRC:** The values remain 28.2, 25.8, 16.4, 11.7, 6.7, and 3.57 percent for 2010-2015, with a human reference of approximately 5.1 percent. The metric and qualifications are now complete.
- **Data barrier:** The current SVG still carries approximately `10^13` words, `10^7` to `10^9` images, and `10^4` teleoperation hours, with the mixed-unit warning unchanged.
- **Timeline:** The order remains RT-2 (Jul 2023), OpenVLA (Jun 2024), π0 (Oct 2024), Helix (Feb 2025), Gemini Robotics (Mar 2025), GR00T N1 (Mar 2025), π0.5 (Apr 2025), and Gemini Robotics 2 (Jul 2026). Gemini Robotics remains before GR00T N1 within March 2025, and the span remains exactly 36 months.
- **Course dates and names:** The resolved profile still gives W02 on September 4, 2026 and the prior session on August 28. The series lock and generated maps are current.

**Result:** PASS. No new numeric, date, name, or ordering issue was introduced.

## Autonomy and internal-claim regression check

- `videos.yml` and `videos.json` still contain 12 matching records with this state sequence: `claimed`, `teleop`, `autonomous`, `autonomous`, `autonomous`, `autonomous`, `unknown`, `claimed`, `unknown`, `unknown`, `unknown`, `autonomous`.
- The corresponding spoken caveats remain intact: the Atlas hook is a delayed company claim; Unitree Embodied Avatar is teleoperated; Atlas parkour is autonomous but not learned; Helix, Atlas CES, the selected NEO cut, and CostNav remain not stated; the NEO launch-demo history is not generalized; Unitree gala remains claimed; CostNav remains a simulation; and WoRV bimanual remains autonomous under the final §1b TTA precedent.
- The current QMD and custom SVG text contain no rejected model or number, no Gemini Robotics 2 technical-report claim, and no internal WoRV project, dataset, person, or customer disclosure.

**Result:** PASS. Manifest parity passed, all 12 local media records remain current, and no autonomy or internal/rejected-claim regression was introduced.
