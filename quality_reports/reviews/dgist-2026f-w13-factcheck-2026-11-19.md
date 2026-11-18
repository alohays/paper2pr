# W13 factual and attribution review

**Date** November 19, 2026

**Component** Domain review for slide-excellence

**Profile** Lecture, DGIST HSS118 W13, November 20. Sixty minutes, including ten minutes for questions.

**Audience** “First-year undergraduates in their second semester. Survey arms, mobile manipulators, quadrupeds and humanoids from the perspective of a robot-learning researcher. Introduce each term through an observable action. Assume no prior mechanics or control course.”

**Forbidden list** No W13 list is configured.

## Result

Minor attribution and precision issues on the audited render. There were 50 distinct Reveal slides in both audience variants. The slide-level coverage count is 47 without findings and three requiring wording or attribution clarification. No numerical contradiction, unsupported claimed autonomy, or forbidden-term violation was found. There are no critical findings. The 50 numbered classroom screenshots were present and newer than the audited QMD and classroom HTML. Initial QMD SHA-256 prefix was `acfe88d79270e2`. I compared the actual visible text, SVG text, clip credits and public alternatives. Most teaching figures describe constructed examples and do not purport to report robot measurements.

## Follow-up on the revised source

All three factual clarification requests are closed in the revised QMD. The W09 line now says the course showed a sequence of timed targets, the Figure slide identifies both palm cameras and fingertip sensors, and the Stretch source strip explicitly distinguishes 2021 prototype footage from the 2026 Gen 2 update. The Mini Cheetah strip now supplies both source playback rates.

The author additionally changed the fixed-arm illustration on slide 38. The revised configuration contains 44 declared sources and its media lock contains 15 entries. I checked the new FANUC/CILYX primary upload, its capture receipt and the prepared 55–69 s source cut. A stationary yellow FANUC arm and tooling handle pharmaceutical trays in an enclosed cell. The November 3, 2026 date matches the FANUC Europe upload. The manufacturer describes the workcell as fully automated; the clip does not identify a learned policy, establish trial success rates or specify operator involvement throughout production. The classroom deck no longer uses the Flexiv example. FANUC is the additional declared source, and the earlier 43 remain documented below. **No outstanding substantive factual correction.** [FANUC Europe and CILYX primary film](https://www.youtube.com/watch?v=esGtbGTmHW8)

## Findings

1. **Minor, slide 2, Where we left off.** “W09 ended with a policy sending timed targets” is too literal. W09 introduces action chunks at `#chunk-clock` and closes by returning to the dropped coffee tool, recovery and questions. Use “In W09, a policy sent a sequence of timed targets.” The source editor has already applied that correction during this review.
2. **Minor, slide 26, hand sensing.** The title asks what changes when the hand can sense contact. Figure compares the on/off state of hand sensing, which includes both palm cameras and tactile sensors. The clip credit and speaker note already scope the evidence. “What changes with palm cameras and touch?” would carry that qualification for students reading the slide on their own. No isolated effect size or general success rate is established. [Figure’s method and examples](https://www.figure.ai/news/helix-02)
3. **Minor, slide 39, Stretch.** The original public caption identified Gen 2 while the classroom video was a March 2021 prototype. Its video caption did carry the correct date; “2021 prototype footage” on the shared source strip makes the generational boundary explicit. That clarification is already present in the working source. The April Spot video on slide 40 similarly illustrates a gauge query; the November Singapore field count belongs to the separate company report on slide 45. [Stretch prototype film](https://www.youtube.com/watch?v=yYUuWWnfRsk) · [Gen 2 release](https://bostondynamics.com/news/boston-dynamics-launches-next-generation-stretch-robot/)

## Slide coverage

| Slides | Evidence and disposition |
| --- | --- |
| 1–6 | Series manifest and W09 QMD establish title, presenter, W12 callback, course map, course policy and Q&A wall. Slide 2 correction noted above. Atlas opens on actual wheel motion. The exact person or program selecting the direction remains unidentified. |
| 7–11 | The actuator/encoder loop is an explanatory diagram. Spot supports body velocity targets and Franka supports joint position targets. The cited 1 kHz FCI interface is not assigned to all devices. The cart timing calculation is correct: 1 m/s for 100 ms gives 0.10 m. An axle angle and two independent hinge angles illustrate degrees of freedom. |
| 12–15 | Doubling the horizontal moment arm from 20 to 40 cm doubles the parcel’s contribution to static torque at constant load. Franka uses external power; Stretch 4, Spot and Atlas quote different battery test conditions. Stretch 4 extended/retracted payloads apply to its arm. The joint component drawing does not claim a universal sensor location. |
| 16–22 | BLDC field changes, ideal 3:1 speed/torque exchange, strain wave, planetary and cycloidal principles align with the engineering sources and manufacturer illustrations. Backdriving, motor sizing, deflection-based torque estimation, the 6/12 N·m CubeMars example and the hydraulic/electric Atlas distinction are appropriately scoped. |
| 23–26 | Incremental counts need a reference. Gyroscope, image-plane position and fingertip pressure are appropriately distinguished. Parallel jaws and articulated fingers are example end effectors. Figure’s manufacturer-labelled autonomy is preserved. See the joint vision/touch qualification above. |
| 27–32 | The open/closed-loop example and P-only arithmetic agree with the stated simplification. For the 30-degree target the residuals are 10 and 2 degrees. The study-note simulation independently reproduced peak positions 1.16 m and 1.32 m at 0 and 250 ms delay with other controls fixed. Stanford Lab 1 supplies the teaching idea. KUKA shows programmed compliance and a person pushing. Static support-area teaching is qualified for a quiet, level stance. MIT ground-force planning and ODrive’s current loop support the illustrative layer diagram. |
| 33–36 | Honda documents running at 6 km/h and both feet off the ground; AP’s release is distinguished from filming. BigDog, DRC-HUBO’s human-supervised tool task, Mini Cheetah in 2019, electric Atlas in 2024 and the later measured wheeled-Atlas motor model agree with their primary sources. The MIT flip footage includes 8× and .3× cuts. |
| 37–43 | Four bodies are compared by examples of job requirements. The Flexiv workstation clip does not establish a permanently fixed base. Stretch and Spot occupy different workplaces and dates. The Ctrl-F project explicitly states 2 kg **added** to the bin, 9 of 10 Ctrl-F lifts. Each comparison film illustrates one trial. Pixel’s co-designed grippers and camera geometry match its CMU project description. Its authors mark individual real rollouts as autonomous or teleoperated. |
| 44–50 | ArmnetBench block-stack arithmetic and task-specific denominator agree with Table 2. The November joint release distinguishes actual Spot inspections and planned Atlas testing. Hypothetical pallet and W14 safety prompts make no accident claim. The workshop took place on November 12. Atlas’s simulation gamepad footage cannot identify the warehouse-run operator. Final prompts and the Q&A code match the lecture goals and lock. |

## Media check

In the initial audit, all 14 manifest records have local-only media; 13 unique cuts are present in the classroom deck (the supplementary Pickle cut is available in the library only). Atlas warehouse and gamepad refer to the same publisher film and distinct moments. SONIC and Ctrl-F reference the two publisher-labelled hardware files for the same additional load. The archived KUKA, AP, Boston Dynamics, MIT, Flexiv and Figure media were checked against timestamps, publisher receipts and source frames during preparation and cross-checked against the actual displayed captions here. A person's hand pushing KUKA is a physical disturbance; it is not evidence about the whole run's autonomy. The instructional gear animation is marked CG. “Autonomy not stated” for that animation has no substantive autonomy implication.

## Declared source ledger

Each source below was retrieved or followed to its primary page. The web-tool Honda copy, the DARPA redirect and the video-only sources are identified separately. YouTube landing pages alone only establish titles and publishers; media receipts, original video and manufacturer documentation establish the visible actions.

- **S01** Course syllabus and topics; instructor sequencing reference. [Primary source](https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/pages/syllabus/)
- **S02** Course lab index; vision, line following/odometry and controls labs. [Primary source](https://www.cs.cmu.edu/~16311/current/labs/labsindex.html)
- **S03** Introduction to Robotics; modeling and joint, compliant and vision control. [Primary source](https://khatib.stanford.edu/teaching/cs223a/)
- **S04** Spring 2022 calendar identifies EECS C106B. Instructor background only. [Primary source](https://pages.github.berkeley.edu/EECS-106/sp22-site/calendar/)
- **S05** Wheeled Atlas research testbed, measured motor response, simulation training and the gamepad scene. [Primary source](https://bostondynamics.com/blog/atlas-on-a-roll/)
- **S06** RobotCommandService exposes a mobility velocity command. [Primary source](https://dev.bostondynamics.com/docs/concepts/robot_services.html)
- **S07** The Franka Control Interface accepts joint targets and offers a 1 kHz interface. [Primary source](https://frankarobotics.github.io/docs/overview.html)
- **S08** FR3 datasheet. The controller lists 100–240 VAC supply voltage. [Primary source](https://franka.de/hubfs/Datasheet_FrankaResearch3_R02212_2.4.pdf)
- **S09** Rev. 5 datasheet. Runtime is 8 h under light CPU load; arm payload is 2.5 kg extended and 4 kg retracted. [Primary source](https://hello-robot.com/wp-content/uploads/2026/05/HelloRobot-DataSheet-Stretch-4-Rev5_AsLaunched.pdf)
- **S10** Manufacturer specifies an average 90-minute runtime and notes payload and environment dependence. [Primary source](https://bostondynamics.com/products/spot/)
- **S11** Atlas datasheet separates 4 h battery life from 2 h with heavy lifting. [Primary source](https://bostondynamics.com/wp-content/uploads/2026/01/atlas-spec-sheet.pdf)
- **S12** Section 8.9. Ideal gearing reduces speed and increases torque, with losses in actual transmissions. [Primary source](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-9-actuation-gearing-and-friction/)
- **S13** Strain-wave operating principle and tooth engagement. [Primary source](https://www.hds.co.jp/english/products/hd_theory/)
- **S14** Publisher title and archived manufacturer animation; eccentric cycloidal mechanism. [Primary source](https://www.youtube.com/watch?v=1ijFove42Kw)
- **S15** MIT actuator design explains backdrivability and the choice of small reduction ratios for high dynamic interaction. [Primary source](https://biomimetics.mit.edu/research/1a9ba04b-d200-4743-b8fc-bf231f3231f0/)
- **S16** Original series-elastic actuator paper describing compliant elements and force estimation. [Primary source](https://fab.cba.mit.edu/classes/865.15/people/rebecca.kleinberger/assets/papers/SEA_Pratt.pdf)
- **S17** AK80-6 KV100 specifications distinguish 6 N·m rated and 12 N·m peak; manufacturer describes BLDC motor, planetary gearbox, encoder and driver. [Primary source](https://www.cubemars.com/product/ak80-6-kv100-robotic-actuator.html)
- **S18** Hydraulic research Atlas and transition to electric actuation. [Primary source](https://bostondynamics.com/blog/atlas-evolution-from-research-robot-to-industrial-humanoid/)
- **S19** Manufacturer white paper discusses incremental optical encoding and reference. [Primary source](https://www.usdigital.com/support/resources/reference/technical-docs/white-papers/resolution-accuracy-and-precision-of-encoders/)
- **S20** Spot inertial motion and foot contact data. Specific sensor observations are examples. [Primary source](https://dev.bostondynamics.com/docs/concepts/joint_control/readme)
- **S21** Autonomy claim for the published demonstrations; palm cameras and fingertip tactile sensing. Bottle-cap pair. [Primary source](https://www.figure.ai/news/helix-02)
- **S22** Gripper commands include width, speed, force and reading state. [Primary source](https://frankarobotics.github.io/libfranka/0.15.0/classfranka_1_1Gripper.html)
- **S23** Atlas hand-design discussion. Source for contact geometry and multi-finger manipulation. [Primary source](https://bostondynamics.com/blog/robot-hands-for-modern-ai-and-real-work/)
- **S24** Fall 2026 Lab 1, step 7 varies measured delay. The W13 numerical curves are a different, explicitly attributed simulation. [Primary source](https://cs123-stanford.readthedocs.io/en/latest/schedule/labs/fall-26/lab-1.html)
- **S25** Original KUKA comparison. Measured hand force is not reported. The cut shows a person pushing across programmed settings. [Primary source](https://www.youtube.com/watch?v=lZvPslCIQZY)
- **S26** MIT repository abstract and accepted-paper link. Cheetah 3 uses convex MPC to plan ground-reaction forces. [Primary source](https://dspace.mit.edu/entities/publication/bc8c7e1e-5830-443f-a879-787947111fcf)
- **S27** ODrive controller documentation identifies cascaded position, velocity and current loops. [Primary source](https://docs.odriverobotics.com/v/latest/manual/control.html)
- **S28** AP Archive footage and uploader metadata. Demonstration was filmed in 2005 and uploaded in 2015. [Primary source](https://www.youtube.com/watch?v=QE0pC-hY__4)
- **S29** Honda 2005 release read in the web tool; direct command-line HTTP returned a branded 403. Honda’s contemporary SEC filing independently confirms the 6 km/h and aerial phase claim. [Primary source](https://global.honda/en/newsroom/news/2005/c051213-asimo-eng.html)
- **S30** DARPA’s BigDog project history, terrain negotiation. [Primary source](https://www.darpa.mil/about/innovation-timeline/bigdog)
- **S31** Initial response was an HTML redirect to DARPA’s current program page. The destination identifies the human-supervised competition and pictures KAIST DRC-Hubo cutting a hole at the June 2015 finals. [Primary source](https://www.darpa.mil/research/programs/darpa-robotics-challenge-a)
- **S32** MIT’s Mini Cheetah film, original Feb 2019 upload; mixed-speed cuts visible. [Primary source](https://www.youtube.com/watch?v=xNeZWP5Mx9s)
- **S33** MIT News describes three modular motors per leg and the 2019 backflip work. [Primary source](https://news.mit.edu/2019/mit-mini-cheetah-first-four-legged-robot-to-backflip-0304)
- **S34** Boston Dynamics’ April 2024 all-electric Atlas announcement. [Primary source](https://bostondynamics.com/blog/electric-new-era-for-atlas/)
- **S35** Flexiv’s Nov 3 demonstration of stationary server-memory insertion. [Primary source](https://www.youtube.com/watch?v=bmRYgXO0qgE)
- **S36** Flexiv’s IROS announcement and force control account. [Primary source](https://www.flexiv.com/news/Flexiv_IROS%202026)
- **S37** Nov 3, 2026 Gen 2 announcement. Separate from the confidentially stored classroom excerpt of the March 2021 prototype film. [Primary source](https://bostondynamics.com/news/boston-dynamics-launches-next-generation-stretch-robot/)
- **S38** Nov 17 joint release. Two Singapore Spots, over 90,000 inspections; onsite Atlas testing planned for early 2027. [Primary source](https://bostondynamics.com/news/boston-dynamics-globalfoundries-expand-robotics-collaboration/)
- **S39** Hardware section names SONIC and Ctrl-F programs, identical added load, one film per condition and 9/10 Ctrl-F result. [Primary source](https://forcectrl.github.io/#hardware)
- **S40** Nov 3, 2026 preprint, also read the linked full paper for force commands and object-pose observations. [Primary source](https://arxiv.org/abs/2611.05507)
- **S41** Pixel CMU system page describes matched camera viewpoints and gripper geometry and labels teleoperation and autonomous clips. Its linked November preprint confirms the date. [Primary source](https://pixel-robot.com/pixel/)
- **S42** Nov 2 preprint, Table 2. Block stacking has 37 successes, zero suboptimal runs and 218 failures across 255 policy rollouts. [Primary source](https://arxiv.org/html/2611.03168v1)
- **S43** CoRL workshop page dates the event to Nov 12, 2026 and describes controllers, hardware and data infrastructure. [Primary source](https://beneath-the-policy.github.io/)
