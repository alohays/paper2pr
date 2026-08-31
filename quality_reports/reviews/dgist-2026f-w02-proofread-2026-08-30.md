# Proofreading Report: dgist-2026f-w02
**Date:** 2026-08-30 | **Profile:** lecture | **Audience:** First- and second-year undergraduates outside AI-related majors; assumes no prior knowledge
**Budget applied:** 4 bullets per slide / 3 with a figure / at most 1 two-line bullet / at most 1 box

The automated quality gate scores the deck 100/100, but the prose and rendered slides still contain the issues below. Render observations refer to a 1280x720 capture.

### Issue 1: The “About me” descriptions become sentence fragments after the hard line breaks
- **Location:** “About me,” lines 19-23
- **Current:** “**WoRV:** the autonomous driving & robotics research lab at Maum.AI  \
robots that learn from data” and “**Co-instructor:** Chris Choi, CEO of Maum.AI  \
closing keynote on Dec 4”
- **Proposed:** “**WoRV:** Maum.AI's autonomous-driving and robotics lab, where robots learn from data.” and “**Co-instructor:** Chris Choi, CEO of Maum.AI, gives the closing keynote on Dec 4.”
- **Category:** Grammar
- **Severity:** Medium

### Issue 2: The remote-attendance bullet is missing the noun that “remote” modifies
- **Location:** “Attendance: two numbers,” line 39
- **Current:** “Remote Sep 11 and Nov 6: your DGIST login is the attendance record”
- **Proposed:** “Remote sessions (Sep 11 and Nov 6): your DGIST login records attendance.”
- **Category:** Grammar
- **Severity:** Medium

### Issue 3: The essay categories are not parallel, and two bullets are elliptical
- **Location:** “Essays: submitting is what counts,” lines 47-49
- **Current:** “Eight talks: five lectures, two guests, one closing keynote”; “After each: upload a short reflection essay to the LMS”; “Graded on submission - showing up in writing is what counts”
- **Proposed:** “Eight talk sessions: five lectures, two guest talks, and one closing keynote.”; “After each session, upload a short reflection essay to the LMS.”; “Each essay receives credit for submission - showing up in writing is what counts.”
- **Category:** Grammar
- **Severity:** Medium

### Issue 4: Two idioms are unnecessarily opaque for this audience
- **Location:** “Ask anytime,” line 66; “One case from where I work,” line 467
- **Current:** “Questions go on the wall any time; we answer them in the last 10 minutes.” and “Left: can a robot's route earn its keep? Right: can two arms do real work?”
- **Proposed:** “Post questions to the Wooclap wall at any time; we will answer them in the last 10 minutes.” and “Left: can a robot's route reduce operating costs? Right: can two arms do useful work?”
- **Category:** Register
- **Severity:** Medium

### Issue 5: The Atlas answer states autonomy as fact while its label correctly says it is only claimed
- **Location:** “Autonomous or teleoperated?”, lines 73-79
- **Current:** “Trained in simulation, runs on its own.”; “Atlas · Boston Dynamics · May 2026 · autonomy claimed”; “What is never stated: \"no teleoperation\"”
- **Proposed:** “Boston Dynamics says Atlas was trained in simulation and ran on its own.”; retain “autonomy claimed”; “The company does not state that teleoperation was absent.”
- **Category:** Consistency
- **Severity:** High

### Issue 6: The Moravec example relies on two unexplained metaphors
- **Location:** “Moravec's paradox (1988),” line 92
- **Current:** “Chess fell in 1997. An AI can write your essay. Fetching a drink held out until now.”
- **Proposed:** “A computer defeated the world chess champion in 1997. AI can write an essay. Robots are only now learning to fetch a drink.”
- **Category:** Register
- **Severity:** Medium

### Issue 7: The Transformer instruction uses the deck's only contraction and is long for its 58% column
- **Location:** “2017 · One architecture for everything,” line 147
- **Current:** “You don't need to read this diagram. Just remember the name: Transformer.”
- **Proposed:** “You do not need the details. Remember one name: Transformer.”
- **Category:** Register
- **Severity:** Medium

### Issue 8: Two history claims omit the nouns being compared
- **Location:** “2018-2020 · GPT: One Simple Game,” line 177; “2020 · Bigger kept getting better,” line 191
- **Current:** “Fluent is not the same as true - keep both in mind.” and “Bigger model + more data + more compute = predictably better”
- **Proposed:** “Fluent text is not necessarily true - keep both in mind.” and “A bigger model + more data + more compute = predictably better performance.”
- **Category:** Grammar
- **Severity:** Medium

### Issue 9: The DALL-E 1 image year is absent from its source line
- **Location:** “2022 · Language Meets Images,” image label at line 205 and footnote at line 218
- **Current:** The slide labels the first image “2021 · DALL-E 1” but cites only “Source: OpenAI (2022, 2025).”
- **Proposed:** “Sources: OpenAI (2021, 2022, 2025).”
- **Category:** Consistency
- **Severity:** Medium

### Issue 10: The 100-million-user statement never names ChatGPT
- **Location:** “2022 · Talking AI becomes a habit,” lines 223-228
- **Current:** “100 million users in two months.”
- **Proposed:** “ChatGPT reached 100 million users in two months.”
- **Category:** Register
- **Severity:** Medium

### Issue 11: All three foundation-model bullets exceed the wrapped-bullet budget in the rendered half-column
- **Location:** “Foundation Models: Train Once, Do Many Things,” lines 235-237
- **Current:** “Huge, varied data → one big model → adapted to many different jobs”; “This recipe has a name: the foundation model”; “Hold onto this diagram - the rest of the course builds on it”
- **Proposed:** “Varied data → one large model → many tasks”; “That general-purpose model is a foundation model.”; “This pattern anchors the rest of the course.”
- **Category:** Overflow
- **Severity:** High

At 1280x720, the first bullet renders on three lines and the second and third on two lines. This is three wrapped bullets against the budget of one, and the three-line first bullet is not acceptable.

### Issue 12: “Generalization” appears as the punch line before it is explained
- **Location:** “Two Waves, One Wall,” line 282
- **Current:** “Both waves met the same wall: generalization.”
- **Proposed:** “Both waves met the same wall: generalization - succeeding beyond the training examples.”
- **Category:** Register
- **Severity:** Medium

### Issue 13: The Embodied AI definition slide contains an unpunctuated question, an awkward definition, and an unnatural closing sentence
- **Location:** “What is Embodied AI,” lines 352-379; terminology-map label at line 369
- **Current:** “What is Embodied AI”; “Embodied AI: intelligence that closes the loop - see, understand, decide, act - in one body.”; “industry's word”; “From here on, this course says Embodied AI.”
- **Proposed:** “What does Embodied AI mean?”; “Embodied AI closes the loop in one body: seeing, understanding, deciding, and acting.”; “industry term”; “From here on, we will use the term Embodied AI.”
- **Category:** Grammar
- **Severity:** Medium

### Issue 14: The π0.5 name and speed disclosure are inconsistent across visible elements
- **Location:** Generalization SVG on “Every new model you will meet...”; π0.5 video caption generated from `videos.json`
- **Current:** The SVG says “pi0.5,” while the other slides say “π0.5.” The rendered caption simultaneously says “π0.5 works across unseen homes (10x)” and “Physical Intelligence · Apr 2025 · autonomous · 1x speed.”
- **Proposed:** Use “π0.5” everywhere. Distinguish the baked-in source speed from player speed explicitly: “π0.5 works across unseen homes (source footage: 10x)” and “... · 1x playback speed.”
- **Category:** Consistency
- **Severity:** Medium

### Issue 15: The data-barrier chart gives three quantitative estimates without data citations
- **Location:** “The data barrier,” SVG labels and footnote at lines 385-393
- **Current:** “Web text ~10^13 words”; “Web images ~10^7 to 10^9”; “Robot teleoperation ~10^4 hours”; footnote: “Log scale; units differ by type (words / images / hours) - read orders of magnitude, not counts. Own figure.”
- **Proposed:** “Sources: [named source for 10^13 words] · [named source for 10^7-10^9 images] · [named source for 10^4 robot hours]. Log scale; units differ by type; compare orders of magnitude, not raw counts. Visualization by the author.”
- **Category:** Consistency
- **Severity:** High

“Own figure” credits the drawing, not the three numerical claims. Named sources are required before delivery.

### Issue 16: The Helix slide mixes a February 2025 clip, a 2026 Helix 02 claim, and a 2025 caveat without marking the chronology
- **Location:** “Helix: two robots, one brain,” lines 407-411
- **Current:** “Two Figure robots share one learned policy to put away groceries.”; “Helix 02 claims \"fully autonomous, not teleoperated\" in writing.”; “The 2025 announcement never states the autonomy mode - the label under the clip is doing the checking for you.”
- **Proposed:** “Two Figure robots, one learned policy, putting away groceries (Feb 2025).”; “By 2026, Helix 02 claimed \"fully autonomous, not teleoperated\" in writing.”; “The Feb 2025 Helix announcement does not state the autonomy mode; the caption therefore says ‘autonomy not stated.’ Source: Figure AI (2025).”
- **Category:** Consistency
- **Severity:** High

### Issue 17: The NEO caption contradicts itself and gives no visible explanation of the distinction
- **Location:** Full-bleed NEO slide generated by lines 422-424 and `videos.json`
- **Current:** The rendered strip says “NEO, the home robot - launch demos were teleoperated” on the left and “1X · Oct 2025 · autonomy not stated · 1x speed” on the right.
- **Proposed:** Render “NEO, the home robot | 1X · Oct 2025 · autonomy not stated · 1x speed,” then add a separately cited sentence: “1X acknowledged that its launch-day live demos were teleoperated; this selected clip does not state its mode.”
- **Category:** Consistency
- **Severity:** High

### Issue 18: One author-year citation drops the punctuation used by the surrounding citations
- **Location:** “The 2023-2026 unlock,” line 444
- **Current:** “OpenVLA (Kim et al. 2024)”
- **Proposed:** “OpenVLA, Kim et al. (2024)”
- **Category:** Consistency
- **Severity:** Low

### Issue 19: The ALOHA citation cannot be matched to the declared bibliography
- **Location:** “Two Waves, One Wall,” line 286; “What each week adds (1/3),” line 531; `Bibliography_base.bib`
- **Current:** Both slides cite “Zhao et al. (2023)” for ALOHA, but the bibliography has no ALOHA/ACT entry; its only Zhao et al. (2023) record is `@zhao2023unipc`, an unrelated diffusion-sampler paper.
- **Proposed:** Keep the visible short form “Zhao et al. (2023),” but add a distinct ALOHA/ACT record for “Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware,” for example `@inproceedings{zhao2023learning,...}`. Do not resolve this citation to `@zhao2023unipc`.
- **Category:** Consistency
- **Severity:** High

### Issue 20: The industry slide uses finance shorthand for novices, and its source footer is visibly clipped
- **Location:** “The pull now comes from industry, not academia,” lines 447-457
- **Current:** “Capital: Figure $1B+ at $39B; Skild $1.4B at $14B+; NEURA up to $1.4B.”; “Production: Unitree shipped 5,500+ humanoids in 2025; its $904M IPO surged 460%.”; “Platforms: NVIDIA's open GR00T reference humanoid and Google DeepMind's whole-body Gemini Robotics 2 arrived in 2026.”
- **Proposed:** Title: “Industry is now driving the field.” Body: “Investment: Figure raised over $1 billion; Skild raised $1.4 billion; NEURA announced up to $1.4 billion.”; “Production: Unitree shipped more than 5,500 humanoid robots in 2025.”; “Platforms: NVIDIA and Google DeepMind released humanoid-robot platforms in 2026.”
- **Category:** Overflow
- **Severity:** High

At 1280x720, the Capital line stays on one line, Production and Platforms each wrap to two, and the source footer is clipped horizontally. Break the footer explicitly:

“Sources: Figure AI (Sep 2025) · Skild AI (Jan 2026) · NEURA/CNBC (Jun 2026)  \
Bloomberg/Unitree (Aug 2026) · NVIDIA (Jun 2026) · Google DeepMind (Jul 2026)”

Also replace “IPO surged 460%”: an IPO does not surge; a share price does. If that statistic remains, name the measured quantity explicitly.

### Issue 21: The semester transition gives the time word “today” an unnatural subject role
- **Location:** “The semester, again,” line 502
- **Current:** “Today set the question. The rest of the semester answers it.”
- **Proposed:** “Today's lecture set the question. The rest of the semester will answer it.”
- **Category:** Grammar
- **Severity:** Medium

### Issue 22: The deck's recurring autonomy question changes tense and starts with a lowercase letter after a colon
- **Location:** “Demo ≠ deployment,” line 477; “Three takeaways,” line 592
- **Current:** “ask first: was it autonomous?” and “ask first: is it autonomous?”
- **Proposed:** Use the same direct question in both places: “ask first, \"Was it autonomous?\"”
- **Category:** Consistency
- **Severity:** Medium

### Issue 23: “Teleop” appears without defining the abbreviation
- **Location:** “What each week adds (1/3),” line 522
- **Current:** “The bodies: arms, hands, and teleop rigs.”
- **Proposed:** “The bodies: arms, hands, and teleoperation rigs.”
- **Category:** Register
- **Severity:** Low

### Issue 24: Slide-title capitalization changes repeatedly without a semantic reason
- **Location:** History-section titles, especially lines 127, 159, 199, 231, 249, 256, and 289
- **Current:** “2012 · AlexNet: Machines Learn to See”; “2018-2020 · GPT: One Simple Game”; “2022 · Language Meets Images”; “Foundation Models: Train Once, Do Many Things”; “Meanwhile, Robots…”; “Two Waves, One Wall”; “What Was Still Missing”
- **Proposed:** Use the sentence-case style already dominant elsewhere: “2012 · AlexNet: Machines learn to see”; “2018-2020 · GPT: One simple game”; “2022 · Language meets images”; “Foundation models: train once, do many things”; “Meanwhile, robots…”; “Two waves, one wall”; “What was still missing.”
- **Category:** Consistency
- **Severity:** Low

## Checks that passed

- No obvious misspellings, duplicated words, or search-and-replace artifacts were found.
- No Hangul appears in the English slide content; the allowance of 0 is respected.
- Numeric bullet counts and box counts stay within 4 / 3-with-figure / 1-box. The confirmed wrapped-bullet violation is Issue 11.
- No inline QMD font-size override below 1em is used to force prose to fit.
- The QMD uses manual visible author-year credits rather than Pandoc `@key` or `[@key]` citations, so there is no mixed Pandoc citation syntax. Issue 19 records the bibliography mismatch that still needs correction.
