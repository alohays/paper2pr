# W13 pedagogical review · Foundations of Robot Hardware, Control, and Modern Platforms

**Date** 2026-11-19 · **Reviewer** pedagogy-reviewer · **Profile** lecture · **Delivery** in person, about 90 people.

**Audience from the deck configuration** “First-year undergraduates in their second semester. Survey arms, mobile manipulators, quadrupeds and humanoids from the perspective of a robot-learning researcher. Introduce each term through an observable action. Assume no prior mechanics or control course.”

**Prior session** W12, Leadership talk, November 13. Slide 2 names the actual event. It identifies W09 as the previous technical anchor and explains the command as a timed target. A student who missed W09 can follow the wheel example on slide 7.

## Verdict and evidence

The deck covers all ten original chapters. Changing the body or task changes the question, from wheel slip to a loaded arm, a yielding joint, foot support, tactile sensing and field inspection. The cup appears briefly in the narration for slide 25. Atlas serves as the opening puzzle and the final test. Both choices fit the breadth-first remit.

**High priority for delivery:** establish the running time with the actual notes and media. **Medium priority for instruction:** qualify the workstation example on slide 38 in visible text. The source qualifies it in the Korean notes, but the projected sequence invites the reader to classify a mobile-capable robot as a fixed-base arm.

I ran the profile resolver, read the deck configuration, all authored slide bodies and Korean notes, the shared course slides, the original ten-chapter outline and the survey course references. The classroom HTML at port 4315 contained 50 sections, 13 video elements and zero speaker notes. The screenshot directory contained exactly `slide-01.png` through `slide-50.png`; even its oldest frame postdated this broad QMD. I inspected the rendered body-comparison, reducer, foot-support, history and four-platform sequences. The reviewed QMD SHA-256 began `acfe88d79270`. Slide numbers below count the title as 1.

## Chapter coverage and course adaptation

| Chapter / slides | Comparison with the original plan | Evidence a first-year can use |
| --- | --- | --- |
| 0 · 1–6 | The course map, rules, question wall, W12 and W09 callbacks precede the Atlas turn. The opening question remains unresolved until chapter 9. | Observe the direction change. A student can point at the wheels before knowing a control term. Advance briskly through the three recurring course screens. |
| 1 · 7–10 | Command journey, command interfaces, timing and evidence questions are present. The original frequency matrix becomes one clock calculation; the separate speed-up demonstration is condensed. | The motor turns the wheel; a turning wheel can slip. At 1 m/s, 100 ms corresponds to 10 cm. Spot accepts a base-speed command in this example and Franka a joint-position target. These are alternative interfaces, including additional ones on each product. |
| 2 · 11–14 | Independent coordinates, reach/load, runtime and the conditions attached to a payload rating remain in the survey. The original multi-row specification sheet becomes two comparisons. | A fixed-axis wheel needs one coordinate in the pictured model. Doubling the horizontal moment arm at the same load doubles that load's torque. The Stretch 4 value changes with extension. Slide 13's conditions prevent a battery-life ranking. |
| 3 · 15–22 | The chapter retains the electric joint, electromagnetic drive, ideal reduction, three gear families, backdrivability, a series spring, thermal limits and hydraulic/electric Atlas. Reflected inertia is introduced qualitatively in the notes. | The 3:1 gearbox calculation gives students a rule they can test. The foot pushing the motor and the spring yielding at a door give distinct mechanical consequences. This is a credible adaptation of MIT 2.12's actuators-and-drives sequence. |
| 4 · 23–26 | Encoder measurement, internal/external sensing, hand design and the sensing comparison are represented. The original removed wrist-sensor showcase remains outside the main sequence. | The encoder counts from a starting position; a camera sees the stair; a fingertip can receive pressure in a hidden contact. The hand-sensing comparison specifies what to watch on the bottle cap and what the video can establish. |
| 5 · 27–32 | Open/closed loop, numerical proportional correction, delay, compliance, balance and a layered controller all appear. MPC is explained verbally during foot support. | MIT's target-versus-reading example and Stanford CS123's one-joint, single-variable comparison are recognizable. The 30° wheel and the separate 1 m linear simulation are identified as different examples. Slide 31 limits the support picture to slow motion. |
| 6 · 33–36 | ASIMO, BigDog, the DRC-HUBO competition, Mini Cheetah, electric Atlas and the modern measured motor model are distinct historical cases. | The student can see the ASIMO flight phase, explain why an uneven surface differs from tool use, and distinguish the published Mini Cheetah trajectory from learned behavior. The manufacturer describes the real-motor measurements that inform the Atlas simulation. |
| 7 · 37–42 | Four task/embodiment choices and a hybrid are restored. Packaging, trailer reach, inspecting a gauge, carrying a box and the CMU Pixel demonstrator introduce materially different constraints. | MIT's body comparison, CMU's task-driven mechanisms and ETH/Berkeley's wheel-leg comparisons are adapted to one decision per task. Slide 38 needs the visible qualification below. On slide 39, Boston Dynamics Stretch is a distinct robot from Hello Robot Stretch 4 on slide 14. |
| 8 · 43–47 | Labels, an actual denominator, real field records, a changed aisle, and current hardware/learning research replace the original compilation of incidents and standards. | A short clip, 37 successful block stacks in 255 attempts, a company-reported inspection count, and a planned Atlas trial answer different questions. Slide 46 gives students an unfamiliar obstruction and asks for an additional record. |
| 9 · 48–50 | The gamepad and simulated robot return to the warehouse opening. The closing questions and question wall protect the W14 safety connection. | A student can name the wheeled body and give an example of measured feedback while explaining why the gamepad frame alone cannot establish who chose the warehouse direction. |

## Pacing and prerequisites

The resolved budget is 50 speaking minutes and 10 minutes of Q&A. Forty-five authored note blocks contain 7,566 Hangul syllables. The earlier W02/W06 recording audit reports Hangul-only speech-rate medians of 252.3 and 240.0 per minute. Applying those comparable counts gives **roughly 30–32 minutes of authored speech**. Delivery at different rates, the shared course screens, illustration walkthroughs, replay, prediction pauses and live elaboration can shift this estimate. The 13 clip elements total 179.7 seconds; playing each once takes about 168.6 seconds if the two box-lift clips run concurrently. Narration may overlap playback. No timed W13 performance is established by those calculations. [Earlier recording evidence](/Users/iyunseong/maangeek/paper2pr/quality_reports/reviews/dgist-2026f-w09-recording-acoustics-2026-10-13.md)

Run the full talk once and log chapter entry times. Rehearse actual explanatory work where there is room: trace the parcel's moment arm on slide 12, predict the current-versus-delayed curve on slide 29, and ask which body to choose if the inspection route gains a stair on slide 37. Keep the last two chapters and the 13:50 Q&A transition in that run. A planning table alone cannot determine whether the session will finish early or run over.

## Thirteen teaching patterns

Nine followed, four partially applied, zero violated. The profile allows one colored callout per slide.

| Pattern | Assessment and example |
| --- | --- |
| 1. Motivation before formalism | Partial · 12, 19 and 31 pose an observable problem. On 18 three names arrive together. Cue students to follow the moving part before naming the families. |
| 2. Incremental notation | Followed · 27–28 establish a target and measured angle before revealing the four quantities of proportional correction. No conflict with the series policy notation. |
| 3. Worked example near a definition | Partial · 11–14, 17 and 27–31 supply worked examples. Slide 16 offers a verbal magnetic-field mechanism; point back to the motor in 15 when explaining the rotor. |
| 4. Progressive complexity | Followed · a single shaft, loaded arm and individual position sensor precede a whole-body support problem. |
| 5. Selective reveals | Followed · the distance calculation, correction equation and changed-aisle answer use reveals. Six fragment divs in the source. |
| 6. Major pivots | Partial · numbered opening titles and spoken transitions provide chapter landmarks. Slide 7 is the only command/body route some students will remember; reuse the relevant phrase orally at each new chapter. |
| 7. Dense material spread across slides | Followed · the electric-joint diagram, gearing arithmetic, gear families and backdriving have separate screens. |
| 8. Meaningful color | Followed · paired diagrams preserve visual roles and label the marks explicitly, including load and support in 12 and 31. |
| 9. Box hierarchy | Followed · headings and diagrams carry the argument. The four boxes on 32 are function nodes in one diagram. |
| 10. Callout fatigue | Followed · no sequence relies on accumulating boxed conclusions. |
| 11. Questions and prediction | Followed · 6, 27, 46 and 48 ask questions that the later picture, measurement or discussion can answer. |
| 12. Visual-first explanation | Partial · 18, 29 and 31 give strong visual evidence. Slide 42's Pixel hybrid is text-only and follows four videos. Reuse the wheeled-arm icon from 37 or illustrate the shared camera viewpoint if students need help locating it. |
| 13. Related definitions compared directly | Followed · 8, 14, 17, 27 and 45 each support a comparison without a memory test across pages. |

## Devil's-advocate challenges

| Challenge and severity | Why it matters | Specific resolution |
| --- | --- | --- |
| Ordering · Low · 2–6. Will students encounter a robot soon enough? | Three standing course screens interrupt the technical question. | Use a short course callback, point out the question wall, and play the warehouse turn promptly. |
| Prerequisites · Medium · 15–21. What must a student remember when they leave the reducer diagram? | Chasing three names can obscure speed, torque and how outside contact reaches the motor. | State the one comparison to retain: for the same motor, reduction changes speed and available torque. Ask students to point to one moving element. |
| Gap · Medium · 37–38. Does working at one bench make this a fixed-base robot? | The first concrete clip after the taxonomy features a mobile-capable MICO. Its posture alone cannot establish a fixed base. | Add the visible sentence “MICO stays at this workstation for the insertion.” Refer back to Franka on slide 13 for an actual fixed-base example. |
| Alternative presentation · Low · 42. How can a reader picture a hybrid after four video examples? | A bullet about matched human and robot views leaves the source setup abstract. | Point to the wheeled base and add an upper-body outline, or project two labeled, permitted source views. |
| Notation · Low · 28–29. Did the wheel suddenly move in metres? | The exercise changes plants and units. The spoken note handles the switch. | Preserve the existing spoken transition. For screenshots reused separately, add “linear simulation” to the delay figure caption. |
| Cognitive load · Medium · 31–32. Do the four control blocks describe every robot? | A novice may assume a universal decomposition and fixed update rates. | Keep the “illustrative” credit and the note about systems combining roles. Ask which layer still corrects motion while the walking target remains unchanged. |
| Standalone evidence · Medium · 43. Does every autonomous rollout establish learned control? | A preprogrammed autonomous system can also execute a rollout. Students may mistake a label for proof of learning. | Anchor the policy explanation explicitly to the Pixel example, or describe the generic label as a recorded run under the robot's controller. |

The highest-value intervention is the timed pass with concrete image-reading tasks. The mobile-capable workstation caption would then remove the main ambiguity in the survey's four-family comparison. Broad coverage and the final evidence-reading exercise merit retaining.
