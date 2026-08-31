# Final Proofreading Report: dgist-2026f-w02

**Date:** 2026-08-30 | **Profile:** lecture | **Audience:** First- and second-year undergraduates outside AI-related majors; assumes no prior knowledge

**Budget applied:** 4 bullets per slide / 3 with a figure / at most 1 two-line bullet / at most 1 box

**Speaker-note budget:** 12,139 Hangul syllables against a 12,040 target for 43 speaking minutes; permitted range 10,836-13,244

## Actionable counts

| Severity | Count |
|---|---:|
| Critical | 0 |
| Medium | 7 |
| Low | 6 |

### Issue 1: The ILSVRC metric is never identified as top-5 error

- **Location:** “2012 · AlexNet: Machines Learn to See,” lines 202, 211, and 215; `s13-ilsvrc.svg`
- **Current:** The image alt text, chart axis, footer, and Korean narration describe generic image-recognition error. The source ledger identifies every plotted value as ILSVRC top-5 error and explicitly requires the metric to be named.
- **Proposed:** Label the axis “top-5 error rate (%) - lower is better,” name “ILSVRC top-5 error” in the footer, and have the script explain that an answer counts as correct when the true label appears among the model's five guesses.
- **Category:** Consistency
- **Severity:** Medium

### Issue 2: The notes add an attendance rule not supported by the declared sources

- **Location:** “Attendance: two numbers,” line 62
- **Current:** The Korean narration states that having someone else sign the sheet is not accepted. The canonical sources specify the entrance sheet and random TA spot-checks but do not state this proxy-signature rule.
- **Proposed:** Verify the rule with the course authority or soften it to an instruction: ask every student to sign personally and explain that the TA may spot-check attendance.
- **Category:** Consistency
- **Severity:** Medium

### Issue 3: The data-barrier narration points to the wrong axis and dimension

- **Location:** “The data barrier,” line 531
- **Current:** In translation, the script says that each step upward on the vertical axis is tenfold and refers to differences in bar height. The rendered chart is horizontal: powers of ten increase from left to right, and the data are encoded by bar length.
- **Proposed:** Say that each step to the right on the horizontal axis represents a tenfold increase, and refer to bar length rather than bar height.
- **Category:** Consistency
- **Severity:** Medium

### Issue 4: The visible IPO sentence assigns a share-price movement to the IPO itself

- **Location:** “The pull now comes from industry, not academia,” line 624
- **Current:** “Unitree reports 5,500+ humanoids shipped in 2025; its $904M IPO rose 460% on debut.”
- **Proposed:** “Unitree reports shipping 5,500+ humanoids in 2025; after a $904M IPO, its shares rose 460% on debut.”
- **Category:** Grammar
- **Severity:** Medium

The Korean narration already names the share price as the quantity that rose, so the fix also makes the slide and script agree.

### Issue 5: The core Embodied AI definition slide remains grammatically awkward

- **Location:** “What is Embodied AI,” lines 479-506
- **Current:** “What is Embodied AI”; “Embodied AI: intelligence that closes the loop - see, understand, decide, act - in one body.”; “industry's word”; “From here on, this course says Embodied AI.”
- **Proposed:** “What does Embodied AI mean?”; “Embodied AI closes the loop in one body: seeing, understanding, deciding, and acting.”; “industry term”; “From here on, we will use the term Embodied AI.”
- **Category:** Grammar
- **Severity:** Medium

### Issue 6: The Wooclap script does not match the approved fallback screen and contains two awkward live instructions

- **Location:** “Ask anytime,” lines 94-97; “Your questions,” line 818
- **Current:** The first script tells students to use the address on screen, but the fallback screen shows only “code announced in class.” It then asks students to post an unquoted access-confirmation phrase with a repeated “connect/access” construction. The final Q&A script describes a like as a “sympathy vote” and uses the equivalent of “sort in the order that like is many.”
- **Proposed:** Refer to the address and code announced aloud in class, put the requested confirmation sentence in quotation marks, and avoid repeating “connect.” At Q&A, say that a like shows shared interest and sort questions by number of likes.
- **Category:** Consistency
- **Severity:** Medium

### Issue 7: Four Korean sentences still contain calques that will sound awkward when read verbatim

- **Location:** Lines 215, 257, 321, and 548
- **Current:** The script uses a bare noun where the adjectival form “skilled” is needed before “annotation worker”; describes the GPT prompt with the equivalent of “the lecture-shortened human's prompt”; uses the equivalent of “the monthly-user scale of about two months”; and switches between “Media player” and “player” within one sentence.
- **Proposed:** Use the natural equivalents of “a skilled annotation worker,” “a human-written prompt shortened for this lecture,” and “UBS estimated that monthly users reached about 100 million after roughly two months.” Preserve the audited 10x-versus-1x distinction, but describe it with one consistent term for the media player.
- **Category:** Register
- **Severity:** Medium

### Issue 8: The essay slide uses nonparallel categories and unclear ellipsis

- **Location:** “Essays: submitting is what counts,” lines 67-69 and 77
- **Current:** “Eight talks: five lectures, two guests, one closing keynote”; “After each: upload a short reflection essay to the LMS”; “Graded on submission - showing up in writing is what counts.” The Korean note also repeatedly inserts the English noun “talk” into otherwise Korean sentences.
- **Proposed:** “Eight talk sessions: five lectures, two guest talks, and one closing keynote”; “After each session, upload a short reflection essay to the LMS”; “Essays receive completion credit - showing up in writing is what counts.” Use the ordinary Korean term for a talk consistently in the narration.
- **Category:** Grammar
- **Severity:** Low

### Issue 9: Three history-slide lines remain unnecessarily elliptical

- **Location:** Lines 222, 250, and 268
- **Current:** “You don't need to read this diagram.”; “Fluent is not the same as true.”; “Bigger model + more data + more compute = predictably better.”
- **Proposed:** “You do not need the details.”; “Fluent text is not necessarily true.”; “A bigger model + more data + more compute = predictably better performance.”
- **Category:** Register
- **Severity:** Low

### Issue 10: The semester transition gives “today” an unnatural subject role

- **Location:** “The semester, again,” line 694
- **Current:** “Today set the question. The rest of the semester answers it.”
- **Proposed:** “Today's lecture set the question. The rest of the semester will answer it.”
- **Category:** Grammar
- **Severity:** Low

### Issue 11: The π0.5 model name changes form across slides

- **Location:** `s28-generalization-axes.svg`, compared with the video caption and timeline
- **Current:** The generalization SVG says “pi0.5”; the video caption and timeline use the Greek model name “π0.5.”
- **Proposed:** Use “π0.5” in the SVG as well. Keep the audited source-footage 10x and player 1x labels unchanged.
- **Category:** Consistency
- **Severity:** Low

### Issue 12: The recurring autonomy question changes tense and capitalization

- **Location:** “Demo ≠ deployment,” line 661; “Three takeaways,” line 800
- **Current:** “Ask first: was it autonomous?” and “ask first: is it autonomous?”
- **Proposed:** Use the same direct question in both places: “Ask first: Was it autonomous?”
- **Category:** Consistency
- **Severity:** Low

### Issue 13: The three canonical flex-cut pages lack presenter cues

- **Location:** Notes for “2022 · Language Meets Images,” “Every new model bets on one of three axes,” and “The pull now comes from industry, not academia,” lines 303, 517, and 633
- **Current:** The final source plan designates these three pages as flex cuts, but their notes do not mark them as optional when the lecture is running late.
- **Proposed:** Add a concise local presenter cue such as “FLEX CUT: omit this page if running late” to each of the three note blocks.
- **Category:** Consistency
- **Severity:** Low

## Verified passes

- The current HTML is newer than the QMD and contains the title note plus 46 slide-note asides, covering all 47 physical pages.
- The independent count is exactly 12,139 Hangul syllables, 99 above the 12,040 target (+0.8%) and inside the permitted range. The interaction branches are alternatives, not cumulative spoken text.
- All 61 captured Reveal states fit at 1280x720. The former autonomy, GPT, Two Waves, foundation-model, industry-footer, schedule, and takeaway overflows are resolved; no actionable wrap or clipping remains.
- `quality_score.py` reports 100/100. Numeric bullet counts, wrapped-bullet limits after remediation, and the one-box budget pass.
- The intentional autonomy distinctions are internally consistent: the π0.5 source footage is 10x while the player remains at 1x; NEO launch-day live demos were teleoperated while the selected promo clip's mode is not stated; Helix 2025 remains not stated while the 2026 Helix 02 wording is a company claim.
- Apart from Issues 1 and 2, visible claims and speaker-note claims align with the canonical local sources and current series/video locks. No forbidden or internal claim appears.
