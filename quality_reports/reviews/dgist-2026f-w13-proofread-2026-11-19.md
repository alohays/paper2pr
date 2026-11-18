# Proofreading report for DGIST HSS118 W13

**November 19, 2026 · Lecture profile · 50 slides including the title and Q&A.**

**Audience (deck configuration).** First-year undergraduates in their second semester. Survey arms, mobile manipulators, quadrupeds and humanoids from the perspective of a robot-learning researcher. Introduce each term through an observable action. Assume no prior mechanics or control course.

**Budget applied.** Four bullets per slide, three with a figure, at most one wrapped bullet and one colored box. English slide text, Korean private notes, 300 Hangul characters allowed in visible slide text.

## Whole-deck coverage

Read the English slide headings, body text, table entries, inline SVG labels, media captions, footnotes and source-link labels in both renders. Checked the corresponding QMD, Korean notes where a public claim needed clarification, the figure and video metadata and the resolved deck profile. Numbering below starts with the title slide. The reviewed classroom and public renders both contain 50 sections and zero presenter notes. The classroom copy contains 13 videos. The public copy uses links or original figures for those examples. The screenshot set contains 50 consecutive PNGs, from slide-01 through slide-50. The blank section seen in an earlier render was removed before this report.

Checked all slides in Chrome at 1280 × 720 for heading, paragraph, list and table boundaries in both builds. No such element crossed the slide bounds. The maximum list length was four, on slides 4 and 10, both text slides. Slide 47 contains three bullets. Neither render had visible Hangul or unresolved citation markers. Credits use descriptive links. Seconds, milliseconds, angles, speed and torque are distinguishable in the worked examples.

## Findings in the reviewed build

| Severity and category | Slide and current wording | Proposed revision and reason |
| --- | --- | --- |
| Medium · Attribution and names | 13, 14, 39. “Stretch 4 · wheeled arm” and “Stretch moves boxes” appear in the same lecture. Slide 39 pairs a March 2021 Boston Dynamics video with a November 2026 Gen 2 reference. | Write “Hello Robot Stretch 4” in slide 13. On slide 39 label the clip “Boston Dynamics Stretch prototype, 2021” and the later footnote “Gen 2 product announcement, 2026.” The Korean notes explain the distinction, but students using the audience copy need it on screen. |
| Medium · Technical wording | 15, “Inside an electric joint.” The original drawing labels the gearbox “Changes the ratio.” | Write “Trades speed for torque.” The illustrated fixed reduction has one ratio. The new caption also prepares the students for slide 17's 3-to-1 example. |
| Medium · Action and observation | 47, “Contact and force can enter a learned action.” | Write “A policy can ask the hands to apply a force.” The example on slide 41 describes a requested force. Students encountered touch as a measurement on slide 24. The study separately specifies the state it reads and the force commands its planner emits. [Ctrl-F, Stage 2](https://forcectrl.github.io/) |
| Medium · Scope of source credit | 47, “CoRL · Everything Beneath the Policy · Nov 12, 2026” appears under three empirical takeaways. | Identify the workshop as further reading. Credit the three examples already used in the deck, ArmnetBench for recorded attempts, Ctrl-F for force commands, and Boston Dynamics for fitting simulated motor behavior to measurements. |
| Low · Beginner vocabulary | 2, “W09 ended with a policy sending timed targets.” | “In W09, a model chose a sequence of movements and when to make them.” Introduce “policy” beside the example model on slide 7. A student who joined this week can then read the first callback independently. |
| Low · Explanatory wording | 22, “Electric Atlas uses electric actuation.” | “Electric Atlas uses motors to turn its joints.” The hydraulic sentence already names the physical mechanism. |
| Low · Playback notation | 35, classroom caption “8x and 0.3x cuts speed.” The caption writer appends “speed” to the manifest field. | Put “mixed playback” in the speed field and write “The edit includes 8× and 0.3× playback” in the shared slide caption or footnote. This agrees with slide 43's multiplication sign and makes the speed qualification available in the public link version. |

The label “autonomy not stated” on the ASIMO archive footage is compatible with Honda's description of the motion. The archive upload date and the event year are both identified. The force figure on slide 41 preserves “2 kg added to the box,” and the field example on slide 45 separates the reported Spot deployment from planned Atlas testing. The deck covers all ten chapters and the four required ground embodiments.
