# DGIST W13 Research and Instructor Study Plan

**Lecture:** Foundations of Robot Hardware, Control, and Modern Platforms<br>
**Session:** DGIST HSS118 W13, November 20, 2026, 13:00-14:00<br>
**Planning date:** August 31, 2026<br>
**Status:** APPROVED FOR EXECUTION<br>
**Clarity:** CLEAR<br>
**Scope of this turn:** research and instructor-study planning only; no research execution, study-site implementation, deck outline, or slide authoring

This is the detailed execution source of truth for the W13 research, instructor
study, lecture planning, and production sequence. It supersedes the earlier
September scheduling assumptions while preserving their substantive technical
study design.

## Requirements specification

### Confirmed context

- The audience is approximately 93 first- and second-year students in a required general-education course. No robotics, mechanical engineering, control, or machine-learning prerequisite may be assumed.
- The session is in person and lasts 60 minutes. Protect the final 10 minutes for Q&A, leaving approximately 50 minutes for instruction.
- W13 follows a robot-learning-first sequence: W03 on video and robot foundation models, W06 on action data, W09 on learning methods, and W11 on spatial AI. The lecture must synthesize those established concepts without re-teaching VLA history, data scaling, imitation learning, reinforcement learning, diffusion policies, or spatial AI.
- The prior session is W12, "Leadership talk." Use only its published title for the required callback; do not invent content, a presenter, or a takeaway. The next session is W14, "Ethics, Safety, and Social Responsibility in the Age of Embodied AI," so W13 should hand off naturally from physical engineering constraints to safety and responsibility.
- W13 is a late engineering special module: it explains how embodiment, mechanics, actuation, sensing, and feedback control turn a learned policy into physical motion and contact after the course has established the robot-learning stack.
- The instructor is already expert in AI and robot learning. The study plan must specifically close gaps in mechanics, actuators and transmissions, classical feedback, contact and whole-body control, and deployment engineering without pretending to create mechanical-design expertise in one week.
- Course materials are due November 13, 2026.

### MUST

1. Make the primary student outcome the ability to deconstruct a robot demonstration into body, actuator and transmission, sensing, low-level control, policy or operator, and physical contact, then state what the demonstration does and does not prove.
2. Use the journey from command to motion as the explanatory spine: task and environment -> embodiment choice -> command or policy -> controller hierarchy -> actuation and transmission -> contact and motion -> sensed feedback.
3. Compare embodiments by task suitability rather than by a universal ranking. The four core ground-robot categories are fixed-base arms, mobile bases or mobile manipulators, quadrupeds, and humanoids. Aerial, soft, and medical robots receive only a very brief landscape mention.
4. Cover the title in an explicit 40/25/35 balance: hardware 40%, control 25%, and modern platforms 35%. Within motion, target approximately 60% manipulation and 40% locomotion or balance.
5. Begin the historical comparison at the ASIMO era. Use history only to explain why modern design choices changed, not as a chronology to memorize.
6. Make actuators and transmissions the instructor's deepest hardware study: motors, gearing, hydraulic and electric actuation, series elasticity, low-ratio or quasi-direct drive, torque-speed trade-offs, backdrivability, reflected inertia, thermal limits, and duty cycle.
7. Teach control through layers and intuition. Use `u = Kp(r - y)` as the one student-facing anchor equation. Explain servo, impedance, whole-body control, and model predictive control by role and time scale; do not teach controller derivations or tuning in the lecture.
8. Build a broad current landscape, then retain four evidence-rich deep cases selected for distinct task and engineering trade-offs. National representation is not a selection criterion.
9. Treat software only as a hardware-control interface axis: command and state access, update rate, latency and jitter, low-level permissions, logging, reset and recovery, simulation support, and safety isolation. Do not turn W13 into a ROS 2 or simulator ecosystem lecture.
10. Balance currency with rigor. Vendor material may establish a labeled vendor claim, but central comparisons and conclusions must rest on cross-checkable public evidence. Never compare revision-mismatched or condition-mismatched payload, speed, runtime, torque, control-rate, or cost figures.
11. Use only public sources for research, examples, claims, visuals, and teaching material. Do not use the instructor's field experience, internal platform notes, company systems, non-public measurements, or de-identified anecdotes as lecture evidence.
12. Use literature and source double-verification rather than an external expert review. High-risk claims that cannot be independently checked remain unknown, conditional, or excluded.
13. Make the first research output a private, local, static interactive mini-site for the instructor, stored outside Paper2PR. The site is an instructor-learning artifact, not a student handout and not a Quarto deck.
14. Design the study site to achieve lecture-and-Q&A readiness: the instructor can teach the non-major session confidently, answer introductory robotics questions with evidence, and state a principled boundary for detailed mechanical-design questions.
15. Include three core interactive simulations: feedback gain and delay, actuator or gear-ratio torque-speed and backdrivability trade-offs, and task-conditioned embodiment selection.
16. Complete the full study site before the instructor studies it and before the lecture plan or deck outline is produced.
17. Use platform videos plus the interactive feedback simulation as candidate teaching media. Do not plan a live physical-hardware demonstration. Do not add an in-lecture poll; preserve interaction for the final Q&A.
18. Put safety, battery and thermal limits, reliability, maintenance, manufacturability, and deployment evidence in a final "deployment reality" learning module rather than distributing them as the primary organizing rubric for every earlier module.
19. Argue that modern platforms are at an important technical transition. The primary test for that transition is the integration of actuation, sensing, control, onboard compute, and usable interfaces. Treat repeatable task and deployment evidence as a separate readiness test so that a technical inflection is not overstated as proven scale readiness.

### SHOULD

1. Use a modular learning path, progressing from system boundaries and physical quantities through actuation, feedback and control, embodiment cases, modern platforms, and deployment reality.
2. Write explanations in Korean while retaining standard English engineering terms, notation, source titles, and searchable keywords.
3. Target a 3-4 hour first completion path, with optional expandable depth rather than forcing all derivations into the main path.
4. Use diagrams, annotated cutaways, animations, manipulable plots, side-by-side video frames, and evidence cards; the artifact should be visual-first and materially faster to learn from than a reading list.
5. Present mathematics as intuition first, with collapsible derivations for kinematics, Jacobians, dynamics, impedance, stability, and whole-body control.
6. Use technical integration as the main test for a modern-platform inflection point, then separately test whether that integration has produced repeatable work, pilot readiness, or scale readiness.
7. Attach claim-level provenance labels such as independently tested, peer-reviewed author-reported, customer-reported, vendor-specified, inferred, and not reported.
8. Add short mastery checks and a teach-or-defer note to each module even though the three simulations are the main interactions.

### MAY

- Include a shallow, clearly labeled 2026 watch list for technically interesting platforms that lack enough public evidence for a deep case.
- Include instructor-only appendices on full rigid-body dynamics, ZMP and capture-point assumptions, fieldbus and real-time systems, safety standards, and platform dossiers.
- Link to canonical textbooks, lectures, papers, standards, manuals, and official engineering talks for later study.

### Explicit exclusions

- No Paper2PR deck, QMD scaffold, slide outline, slide copy, speaker notes, bibliography edits, or media preparation in this planning turn.
- No aerial, soft, or medical robotics module beyond a very brief existence map.
- No motor electromagnetic design, gearbox tooth design, finite-element analysis, controller tuning, or full dynamics derivation in the student-facing lecture.
- No exhaustive product catalog, cross-vendor league table, investment narrative, market forecast, or unsupported claim that humanoids are universally optimal.
- No internal or proprietary information, including material abstracted from private notes.

### Adopted planning defaults

The interview ended with an instruction to proceed. The following recommended defaults are therefore adopted:

- a Korean-first, English-term modular site with a 3-4 hour core path;
- the thesis "a command is not motion";
- intuition-first mathematics with optional collapsible derivations;
- a complete study-site freeze before instructor study, followed by lecture planning and deck production before the November 13 handoff.

## 1. Communication and learning jobs

### Lecture communication job

By the end of W13, non-major first- and second-year students should be able to trace how an AI or human command becomes physical work, because they can separate embodiment, actuation, sensing, feedback control, policy or operator, and contact, and can explain why the best robot body depends on the task.

### Instructor-study job

By the end of the private study site, the instructor should be able to:

1. explain the command-to-motion stack without collapsing the policy, controller, actuator, and platform into one black box;
2. explain the main actuator and transmission trade-offs behind modern arms, mobile robots, quadrupeds, and humanoids;
3. predict the qualitative effects of feedback gain, damping, delay, saturation, compliance, and contact;
4. distinguish position, velocity, torque, force, and impedance interfaces and explain what a learned policy usually commands;
5. compare embodiments for a stated task without creating a universal platform ranking;
6. read a platform specification, SDK description, manual, and demo claim with revision and condition awareness;
7. describe why the ASIMO era, the DRC era, and current integrated electric platforms differ without claiming that every modern design is superior on every axis;
8. answer introductory Q&A with sources and explicitly defer motor design, structural analysis, controller tuning, and proprietary architecture questions.

### One memorable thesis

> A command is not motion. Reliable physical work appears only after a chosen body, actuators and transmissions, sensing, and layered feedback turn the command into controlled contact.

## 2. Research target map

The research order follows conceptual dependency, not product chronology.

```text
task and environment
  -> embodiment and mechanism
  -> joint, actuator, and transmission
  -> sensors, state, and timing
  -> feedback and controller hierarchy
  -> contact, balance, and manipulation
  -> policy or operator interface
  -> repeatable work
  -> deployment reality
```

### Tier A: prerequisites that unlock everything else

Research these first and build the shared visual vocabulary from them.

1. **System boundary**
   - platform, mechanism, actuator, transmission, sensor, controller, planner, policy, teleoperator, and environment;
   - command versus state; reference versus measurement; physical plant versus software;
   - what evidence belongs to which layer in a demonstration.

2. **Physical quantities**
   - position, velocity, acceleration, force, torque, power, energy, stiffness, damping, inertia, bandwidth, latency, and duty cycle;
   - peak versus continuous values; nominal versus worst-case; accuracy versus repeatability;
   - why units and test conditions are part of the claim.

3. **Robot anatomy**
   - link, joint, degree of freedom, end effector, serial and parallel chains, workspace, range of motion, payload, reach, and floating base;
   - why more degrees of freedom do not automatically mean more useful dexterity;
   - coordinate-frame, forward-kinematics, inverse-kinematics, Jacobian, singularity, and leverage intuition without derivations in the core path.

### Tier B: the instructor's deepest technical reinforcement

4. **Actuators and transmissions**
   - brushed DC, brushless DC and permanent-magnet synchronous motors at a functional level;
   - hydraulic actuation versus integrated electric joints;
   - harmonic, cycloidal, planetary, belt, cable or tendon, and direct or low-ratio transmission archetypes;
   - high reduction, series elasticity, low-ratio and quasi-direct drive as trade-off families rather than a winner hierarchy;
   - torque-speed envelope, mechanical power, reflected inertia, backdrivability, compliance, sensing, efficiency, heat, and duty cycle;
   - brakes, joint stops, bearing loads, cable routing, serviceability, and module replacement at an instructor-Q&A level.

5. **Sensing, state, and timing**
   - motor current, encoder, joint torque, force-torque, inertial, tactile, vision, and range sensing;
   - proprioception, exteroception, and interaction sensing;
   - calibration, synchronization, estimation, noise, delay, jitter, filtering, and observability intuition;
   - why a high advertised control rate does not guarantee a good closed loop.

6. **Feedback and control hierarchy**
   - open versus closed loop, proportional feedback, damping, feedforward, saturation, and integral action;
   - position, velocity, current or torque, force, stiffness, and impedance control;
   - motor-current loop -> joint servo -> task or whole-body controller -> planner or learned policy;
   - contact transition, friction, support polygon, center of mass, floating-base underactuation, and balance intuition;
   - the purpose, assumptions, and boundaries of zero moment point, capture point, inverse dynamics, whole-body quadratic programming, and model predictive control;
   - controller role and time scale only for students; mathematical derivations remain expandable instructor depth.

### Tier C: embodiment and platform synthesis

7. **Task-conditioned embodiment choice**
   - fixed arm: precision, repeatability, reach, payload, cell design, force interaction, and limited mobility;
   - mobile base or mobile manipulator: navigation, slip, stability, sensor integration, reachability, and docking;
   - quadruped: terrain access, dynamic balance, payload and endurance, hidden locomotion controller, and application API;
   - humanoid: human infrastructure, bimanual reach, locomotion plus manipulation, fall risk, power, cost, safety, and service complexity;
   - ultra-brief existence map only for aerial, soft, and medical robots.

8. **ASIMO-to-modern historical transition**
   - ASIMO-era integration, predictive walking, compactness, and human-environment intent;
   - HRP, HUBO, and DRC-era research openness, supervised autonomy, field tasks, robustness, recovery, and serviceability;
   - current electric integrated joints, richer force and tactile sensing, onboard compute, data logging, developer interfaces, manufacturability, and fleet or workflow layers;
   - continuity as well as change: many control and mechatronics ideas are older than the current AI wave.

9. **Modern platform landscape and four deep cases**
   - scan broadly across the four ground-robot categories;
   - select one evidence-rich primary case per category, with one contrast case when it clarifies a design trade-off;
   - evaluate technical integration first, then separately label demo, pilot, repeated operation, and scale evidence;
   - keep volatile frontier platforms in a dated watch list when technical documentation is insufficient.

### Tier D: final deployment-reality module

10. **Deployment reality**
    - battery, charging, heat, continuous versus peak operation, and shift coverage;
    - emergency stop, guarding, application-level risk assessment, human proximity, fall zones, and recovery;
    - maintainability, consumables, spares, calibration, repair time, software and firmware lifecycle, and vendor support;
    - manufacturability, quality consistency, integration labor, facility changes, and total workflow rather than robot-only capability;
    - demo-ready, pilot-ready, and scale-ready as separate evidence states.

### Defer from the core study path

- Denavit-Hartenberg parameter exercises, Lie-group derivations, full Jacobian derivation, and Lagrangian dynamics;
- motor electromagnetic design, gear-tooth geometry, bearing sizing, structural stress analysis, topology optimization, and finite-element analysis;
- controller tuning practice, Lyapunov proofs, model predictive control implementation, and whole-body quadratic-program implementation;
- imitation learning, reinforcement learning, diffusion policy, VLA, action tokenization, and data scaling;
- exhaustive safety-standard clause analysis, pricing, procurement, market share, investment, or labor-market forecasting.

## 3. Private interactive study-site blueprint

### Location and implementation boundary

Target directory for the later implementation:

`/Users/iyunseong/Documents/vault/1-projects/maum/dgist-future-literacy-2026fall/lectures/w13-robot-hardware/study-note/`

The site will be a backend-free static mini-site, separate from Paper2PR. It should use local HTML, CSS, JavaScript, data, and media assets; keep citations and claim data machine-readable; store optional progress only in browser local storage; and run through a minimal local static server. It must not depend on a hosted service or a logged-in account.

### Core path and time budget

| Module | Core time | Primary question | Required visual or interaction |
|---|---:|---|---|
| 0. Command is not motion | 10 min | Where does a policy or operator stop and the physical stack begin? | Clickable command-to-contact system map |
| 1. A robot body in quantities | 25 min | What do joints, reach, torque, power, stiffness, inertia, and bandwidth actually constrain? | Annotated anatomy plus unit and claim cards |
| 2. Actuation and transmission | 40 min | Why do torque, speed, backdrivability, heat, and robustness trade off? | Joint cutaways plus gear-ratio simulation |
| 3. Feedback and control layers | 40 min | How does sensed error become stable motion and compliant contact? | Gain-and-delay simulation plus multi-rate loop ladder |
| 4. The task chooses the body | 35 min | When is an arm, mobile manipulator, quadruped, or humanoid the rational choice? | Task-conditioned embodiment selector |
| 5. ASIMO to integrated platforms | 35 min | Which engineering integrations changed, and which fundamentals did not? | Historical lineage and four evidence cards |
| 6. Deployment reality | 20 min | What separates a compelling demonstration from usable work? | Demo-pilot-scale evidence ladder |
| 7. Teach it, question it | 15 min | What belongs in W13, what belongs only in Q&A, and what must be deferred? | Oral mastery checks and anticipated Q&A |

**Core total:** approximately 220 minutes, or 3 hours 40 minutes. Expandable derivations and source readings are outside this budget.

### Repeated module pattern

Every module should contain:

1. a one-sentence learning target;
2. a large visual model before prose;
3. three to five core ideas;
4. one interactive or annotated example;
5. a "common wrong model" panel;
6. a "teach / know for Q&A / defer" classification;
7. two short retrieval or prediction questions;
8. collapsible mathematical depth where relevant;
9. claim-level citations and a recommended primary reading;
10. a two-minute summary that can later seed speaker notes, without writing slide copy now.

### Simulation A: feedback gain and delay

Purpose: make `u = Kp(r - y)` memorable while preventing the misconception that one proportional loop represents an entire robot controller.

Controls:

- reference trajectory or step target;
- proportional gain;
- damping or derivative term as an optional advanced control;
- sensor or communication delay;
- actuator saturation and optional disturbance.

Outputs:

- reference and measured response;
- error and control input;
- rise time, overshoot, settling behavior, and oscillation warnings;
- a visible mapping from the toy loop to motor, joint, whole-body, and policy time scales.

Validation requirement: use a deliberately simple stated plant and verify numerical integration against analytic or independently computed reference cases. Never imply that the toy response predicts a named commercial robot.

### Simulation B: actuator and gear-ratio trade-offs

Purpose: connect motor behavior, transmission choice, and joint-level consequences.

Controls:

- idealized motor torque and no-load speed;
- gear ratio and efficiency;
- load inertia and motion speed;
- optional compliance and thermal duty-cycle setting.

Outputs:

- joint torque and speed envelope;
- mechanical-power view using `P = tau * omega` as an instructor-study relation;
- reflected-inertia and qualitative backdrivability indicators;
- heat or continuous-operation warning clearly labeled as an educational proxy, not a motor-sizing calculator.

Validation requirement: disclose assumptions, keep units explicit, and cross-check limiting cases such as ratio 1, zero speed, and zero load.

### Simulation C: task-conditioned embodiment selector

Purpose: make platform selection a reasoned task trade-off rather than a popularity ranking.

Inputs:

- fixed or changing workspace;
- need for stairs, rough terrain, or long travel;
- manipulation reach and dexterity;
- payload, precision, speed, human proximity, endurance, and facility-modification tolerance;
- research openness versus managed deployment.

Outputs:

- transparent criterion-by-criterion comparison of the four categories;
- no single aggregate "best robot" score by default;
- explanation of which task assumption changed the recommendation;
- links to relevant deep cases and evidence cards.

Validation requirement: treat weights as a teaching scenario, not empirical truth, and show sensitivity to changed assumptions.

## 4. Research workstreams

### WS0. Source and claim infrastructure

Create before drafting content:

- `source-ledger`: citation, URL or DOI, source class, publication or revision date, access date, rights notes, and module relevance;
- `claim-ledger`: claim ID, exact wording, layer, teaching purpose, source A, source B, evidence label, revision, test conditions, volatility, confidence, and disposition;
- `platform-dossier` template: morphology, mechanics, actuation, transmission, sensing, compute, bus, command and state interfaces, control boundary, safety, power, maintenance, evidence state, and volatile facts;
- `visual-ledger`: visual concept, provenance, licence or quotation basis, redesign status, and intended site module.

Exit: no research note exists without a source-ledger entry and no platform number enters the site without a claim-ledger row.

### WS1. Canonical mechanics and control foundation

Build the shared terminology and conceptual dependencies from canonical textbooks and university notes. The initial source spine should include:

- [Modern Robotics](https://hades.mech.northwestern.edu/index.php/Modern_Robotics) for kinematics, dynamics, and control structure;
- MIT [Underactuated Robotics](https://underactuated.csail.mit.edu/) for floating-base, contact, and legged-control intuition;
- MIT [Robotic Manipulation](https://manipulation.csail.mit.edu/) and its [Manipulator Control chapter](https://manipulation.csail.mit.edu/force.html) for position, force, and impedance control.

Exit: glossary, concept dependency graph, instructor mastery questions, and the mathematical assumptions for all three simulations.

### WS2. Actuator and transmission study

Research actuator families through trade-offs and representative engineering papers rather than a parts encyclopedia. Pair a canonical source on series elasticity with a modern low-ratio or proprioceptive actuator source and at least one official joint or smart-servo manual.

Required outputs:

- actuator and transmission comparison matrix;
- torque-speed-power diagram;
- backdrivability and reflected-inertia explanation;
- peak versus continuous and thermal-duty-cycle evidence note;
- simulation B model and test cases;
- ten likely Q&A questions, including why a larger gear ratio is not always better and why electric is not universally better than hydraulic.

Exit: every trade-off claim has two independent public sources or is explicitly framed as an illustrative model.

### WS3. Feedback, interaction, and control hierarchy

Research proportional and proportional-derivative feedback, feedforward, position and torque loops, force and impedance control, contact, balance, and whole-body control by role and time scale.

Use official system-interface documentation as examples without teaching a software ecosystem. Useful anchors include the [Franka Control Interface](https://franka.de/franka-research-3) and [ros2_control](https://control.ros.org/jazzy/doc/getting_started/getting_started.html).

Required outputs:

- controller hierarchy and multi-rate timing diagram;
- control-mode comparison;
- simulation A and validation cases;
- contact and floating-base misconception cards;
- instructor-only collapsible derivations for PD response, Jacobian-transpose force mapping, manipulator dynamics, and impedance.

Exit: the instructor can explain where a learned policy's output enters the hierarchy and why control rate alone does not establish control quality.

### WS4. Embodiment-by-task study

Define a small task set before choosing products: repetitive factory manipulation, human-adjacent manipulation, long-range indoor logistics, rough-terrain inspection, mixed locomotion and manipulation, and human-infrastructure service.

For each task, research:

- why a fixed arm, mobile platform, quadruped, or humanoid may be favored;
- what facility modification substitutes for embodiment complexity;
- which contact, reachability, power, safety, and maintenance constraints dominate;
- what new failure modes appear as embodiment becomes more mobile and articulated.

Required outputs: simulation C, category comparison without a global score, and one counterexample for every simplistic claim such as "humanoids fit human spaces, therefore humanoids are optimal."

Exit: each platform category wins at least one plausible task and loses at least one plausible task for stated reasons.

### WS5. Historical transition study

Start at ASIMO, then use HRP, HUBO, and the DARPA Robotics Challenge as the bridge to current platforms. Recommended public starting points include Honda's [P2 and ASIMO engineering history](https://global.honda/en/tech/robotics/P2/IEEE/) and the official [DARPA Robotics Challenge](https://www.darpa.mil/research/programs/darpa-robotics-challenge) program history.

Research the same six questions for each era:

1. What task or failure limited the platform?
2. What mechanical or mechatronic design changed?
3. What did the change require from sensing and control?
4. What new capability became possible?
5. What evidence supports the claim?
6. What remained unsolved?

Exit: a causal lineage with no more than three eras and no unsupported "times better" claim.

### WS6. Current landscape and deep-case screening

Create a broad, dated landscape first. Candidate seeds are not selections:

- fixed arm: a stiff industrial arm or cobot contrasted with a force-sensitive research arm such as [Franka Research 3](https://franka.de/franka-research-3);
- mobile base or manipulator: a research platform with an unusually transparent manual such as [Husky A300](https://docs.clearpathrobotics.com/docs_robots/outdoor_robots/husky/a300/user_manual_husky/) plus a mobile-manipulation contrast;
- quadruped: a productized high-level platform such as [Spot and its SDK](https://dev.bostondynamics.com/) contrasted with a developer-access platform;
- humanoid: a developer platform such as [Unitree G1 EDU](https://www.unitree.com/mobile/g1/) contrasted with a task-managed deployment system such as [Digit and Arc](https://www.agilityrobotics.com/solutions);
- inspectable cross-cutting example: [OpenMANIPULATOR-X](https://emanual.robotis.com/docs/en/platform/openmanipulator_x/overview/) or [SO-101](https://huggingface.co/docs/lerobot/so101) for actuator, bus, calibration, and openness literacy.

The [NIST Humanoid Robot Baseline Performance Benchmark](https://www.nist.gov/el/intelligent-systems-division-73500/humanoid-robot-baseline-performance-benchmark) is the methodological warning: a new comparable benchmark is only being developed, so the plan forbids an unsupported cross-vendor "best humanoid" table.

Exit: four selected deep cases, one per core ground category, each with a complete dossier and a short written reason for selection and rejection of its nearest alternative.

### WS7. Deployment-reality research

Use manuals, application safety guidance, standards scope pages, customer or operator evidence, and support documentation. Research the robot as one component of an application or workflow.

Required outputs:

- demo, pilot, repeated operation, and scale evidence definitions;
- runtime, charging, maintenance, and intervention claim checklist;
- application-level safety and facility-risk checklist;
- vendor, customer, and independent evidence comparison;
- final module and Q&A boundaries.

Exit: no statement that a platform is "safe," "autonomous," "production-ready," or "scalable" without scope, configuration, evidence class, and conditions.

### WS8. Visual and interaction production

Create original explanatory diagrams whenever the concept can be redrawn accurately. Use third-party figures or video only when their provenance and educational quotation basis are recorded and the original is materially more useful than a redraw.

Required visual inventory:

- command-to-contact stack;
- robot anatomy and floating-base comparison;
- torque-speed-power chart;
- gearbox, series-elastic, and low-ratio joint schematics;
- sensing and multi-rate feedback ladder;
- contact, support, and balance intuition;
- four-category task map;
- ASIMO-to-modern causal timeline;
- four platform evidence cards;
- demo-to-deployment ladder;
- three interactive simulations.

Exit: every visual is readable at laptop size, has provenance, uses consistent semantics, and directly answers one learning question.

### WS9. Site integration and learning validation

Assemble the full static mini-site only after module claims and visuals pass their research gates. The site must then pass:

- local link and asset checks;
- no-network runtime check after initial load;
- interaction boundary and numeric sanity tests;
- keyboard operation, reduced-motion behavior, text contrast, alt text, and equation accessibility checks;
- desktop widths representative of the instructor's laptop and an external monitor;
- citation and claim-ledger consistency checks;
- a full visual review of every module and state;
- private-information scan proving that no vault or internal platform note became a source.

Exit: the full 3-4 hour core path is complete and verified before the instructor starts the planned study pass.

## 5. Case-screening rubric

Score each current-platform candidate from 0 to 2 on each criterion.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Task contrast | Redundant | Some contrast | Opens a distinct task trade-off |
| Engineering transparency | Marketing page only | Partial specs | Manual, architecture, or credible technical detail |
| Control-boundary clarity | Unknown | High-level interface known | Command, state, rate, and access boundary documented |
| Public evidence depth | Single claim source | Two related sources | Independent or differently situated corroboration |
| Revision and condition clarity | Mixed or missing | Partly scoped | Exact revision, configuration, and conditions |
| Visual teachability | Hard to show | Usable | Clear mechanism, workflow, or failure visual |
| Historical or modern significance | Incidental | Relevant | Essential causal or integration contrast |
| Stability through lecture date | Highly volatile | Recheckable | Stable or version-pinned |

Selection rules:

- **13-16:** eligible for a deep case;
- **9-12:** landscape or contrast case only;
- **0-8:** exclude from the teaching corpus;
- a 0 in engineering transparency or revision clarity blocks quantitative comparison regardless of total score;
- the four selected cases must cover all four ground categories and must not all illustrate the same openness, control, or deployment philosophy;
- price, shipment, production, payload, runtime, and speed claims are volatile by default and require a final dated recheck.

## 6. Evidence and source protocol

### Source hierarchy

1. peer-reviewed papers, canonical textbooks, standards organizations, government laboratories, and public research-institute reports;
2. official manuals, datasheets, SDK documentation, safety manuals, and technical reports;
3. patents, official engineering talks, teardown or design documents with identifiable authors and methods;
4. customer, integrator, or operator reports with stated conditions;
5. vendor launch pages and marketing demonstrations;
6. journalism or analyst material only for discovery, never as the sole technical basis.

### Double-verification rules

- A fundamental concept requires a canonical textbook or university source plus a second independent teaching or primary source.
- A platform architecture claim requires a manual, datasheet, SDK, paper, or engineering report; two marketing pages from the same company do not count as double verification.
- A vendor specification may be quoted as vendor-specified without independent confirmation, but it cannot support a cross-vendor conclusion unless conditions and definitions match.
- A deployment claim requires a customer, integrator, operator, standardized test, or otherwise independent source in addition to the vendor.
- An inference must be labeled as inference and show its premises. If a premise is not public, the inference is excluded.
- Conflicting official pages trigger a revision investigation; they are never averaged.
- Absence of public evidence is recorded as "not reported," not converted into a negative claim.

### Numeric comparison guardrails

- distinguish peak from continuous torque, load, and power;
- distinguish reach, payload at pose, rated payload, and moment limits;
- distinguish accuracy from repeatability;
- distinguish nominal battery capacity from measured task runtime and shift coverage;
- distinguish controller update rate, sensor publication rate, bus cycle, policy inference rate, and achieved closed-loop bandwidth;
- distinguish base product, research or EDU edition, optional hand or compute module, firmware version, and safety configuration;
- never combine different tasks, terrains, payloads, speeds, or autonomy modes into one performance ranking.

### Provenance labels

Use one label on every nontrivial platform claim:

- independently tested;
- peer-reviewed author-reported;
- public-research-institute reported;
- customer or operator reported;
- vendor-specified;
- vendor-demonstrated;
- inferred from public sources;
- not reported.

## 7. Schedule and critical path

The requirement to finish the full site before study makes the schedule sequential and tight. Scope cuts must come from optional depth, never from source verification or the three simulations.

| Date | Milestone | Exit condition |
|---|---|---|
| Aug 31 | Planning complete | This plan is approved, saved, and internally consistent |
| Sep 7 | Source spine and parallel research launch | Ledgers, glossary, task set, module skeleton, candidate landscape, and independent work packets exist |
| Sep 21 | Mechanics, actuation, and control draft | Modules 0-3 and simulations A and B pass first source and sanity review |
| Oct 5 | Embodiment, history, platform, and deployment draft | Modules 4-7, four provisional deep cases, simulation C, and evidence cards are complete |
| Oct 23 | Full study-site integration | Every core module, visual, interaction, citation, and local asset is present |
| Oct 30 | Site QA and v1 freeze | Visual, functional, source, privacy, accessibility, and no-network checks pass; the complete site is frozen for study |
| Nov 2 | Instructor study pass | Instructor completes the 3-4 hour core and records unclear points and Q&A gaps |
| Nov 4 | Gap repair and mastery gate | Study-site corrections land and instructor passes the mastery checks below |
| Nov 5 | Lecture communication plan | W13 thesis, learning outcomes, section timing, cases, robot-learning callbacks, and exclusions are decided |
| Nov 6-8 | Deck authoring | The Quarto deck and required public visual and media assets reach a complete first version |
| Nov 9-10 | Deck verification | Render, visual audit, fact check, timing pass, and quality gate reach at least 80, targeting 90 |
| Nov 11 | Rehearsal and Q&A pass | A full timed rehearsal fits 50 minutes of instruction plus 10 minutes of Q&A, and the defer boundaries are usable aloud |
| Nov 12 | Administrative package freeze | The verified deck, source record, and delivery notes are frozen for handoff |
| Nov 13 | Administrative handoff | Course material is sent to the TA and administrator; the W12 callback remains title-only and the W14 handoff is explicit |
| Nov 20 | Lecture delivery | The local deck, media, presenter notes, and fallback plan pass the room check before class |

Schedule warning: the November 6-10 production window is still tight for a normal 40-60 slide cycle. Research and site work therefore need independent parallel work packets by September 7, and deck-ready public visuals should be identified during WS8 even though slide composition cannot begin before the November 4 mastery gate. If execution starts late, freeze the site scope at the core modules and postpone optional appendices; do not weaken evidence checks or start an incomplete site study pass.

## 8. Instructor mastery gate before lecture planning

The instructor should be able to answer these without reading the site verbatim:

1. Trace a learned or teleoperated command through the physical stack to contact.
2. Explain why a fixed arm can outperform a humanoid for one task even if the humanoid is more general in morphology.
3. Predict the qualitative response of a feedback loop when gain or delay increases.
4. Explain how gear ratio changes joint torque, speed, reflected inertia, backdrivability, and heat risk.
5. Distinguish position, torque, force, and impedance control without claiming one is universally safest or most modern.
6. Explain why a floating-base legged robot is underactuated and why contact makes control harder.
7. Distinguish a policy rate, joint-control rate, sensor rate, and closed-loop bandwidth.
8. Name the main ASIMO-era, DRC-era, and current-platform integration differences.
9. Choose among four embodiments for two different tasks and state the assumptions that drove the choice.
10. Read a demo claim and ask the next evidence questions about teleoperation, repetition, intervention, payload, runtime, safety, and conditions.
11. State why technical integration can mark an inflection point without proving deployment readiness.
12. Identify questions that require a mechanical, actuator, safety, or controls specialist rather than improvising an answer.

Pass condition:

- explain at least 10 of 12 correctly in plain language;
- score at least 80% on the site's retrieval checks;
- produce a five-minute spoken explanation of the central thesis with no layer confusion;
- leave no unresolved misconception rated high risk in the Q&A dossier.

## 9. Go or no-go gate for lecture outline work

Proceed to lecture planning only when all are true:

- the complete core study site is present and verified;
- all three simulations pass their stated sanity tests;
- the four deep platform cases pass the rubric and have complete dossiers;
- every central claim has the required provenance and double verification;
- no private experience or vault platform note appears in the source or visual ledgers;
- the instructor mastery gate passes;
- the technical-inflection conclusion and the separate deployment-readiness conclusion are both supportable;
- the 50-minute content budget still fits hardware 40%, control 25%, and platforms 35%;
- the W12 callback uses only the public title "Leadership talk" and does not invent content or a presenter;
- W03, W06, W09, and W11 remain the robot-learning sequence that W13 synthesizes rather than repeats;
- the close hands the physical constraints forward to W14 ethics, safety, and responsibility.

If any item fails, do not compensate with more platform names or denser slides. Remove the weakest case or optional depth, repair the learning gap, and rerun the gate.

## 10. Risk register

| Risk | Early signal | Mitigation |
|---|---|---|
| Four-category scope becomes a catalog | More than four deep cases or repeated spec tables | One case per category, task questions first, strict rubric |
| Interactive-site build displaces learning | Visual polish starts before claim ledgers and module text are stable | Research gates before integration; three simulations only |
| Vendor material drives the conclusion | Deep case has only vendor pages | Downgrade to landscape or obtain independent evidence |
| Simplification becomes technically wrong | One-word equations or claims lack assumptions | State model boundaries and keep derivations expandable |
| Technical inflection is confused with deployment | Integration evidence is presented as scale evidence | Maintain two separate verdicts and evidence ladders |
| Private experience leaks into the corpus | A claim cites a vault note or unnamed internal observation | Public-source-only scan and source-ledger enforcement |
| Volatile 2026 facts drift | Edition, price, interface, or spec changes | Pin revision and access date; recheck before site and deck freezes |
| Site must be complete before study, delaying feedback | Core site misses Oct 23 integration or Oct 30 freeze | Cut optional appendices immediately; preserve full core and QA |
| Deck schedule becomes unsafe | Mastery gate slips past Nov 4 | Escalate schedule risk and negotiate the handoff, rather than ship unverified content |

## 11. Completion definition for this planning turn

This planning turn is complete when:

- the interview decisions are captured without contradiction;
- the instructor-learning artifact is separated from Paper2PR deck work;
- research targets, dependencies, source rules, case-selection rules, site modules, simulations, schedule, validation, and go/no-go criteria are explicit;
- no research execution, site code, platform selection, deck outline, or slide authoring has been started;
- the vault working note points to this English plan as the execution source of truth.
