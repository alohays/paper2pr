## One original 3D film for the November 20 hardware lecture

The audience is in its second semester at DGIST. W06 gave students a hand-position command and W09 showed a lid-opening sequence. W13 already has Atlas at both ends, a manufacturer's strain-wave animation on screen 18, and KUKA's compliant-arm footage on screen 30. An original clip can answer the question on screen 19, where students currently see two lines of text. Screen numbers include the title slide. [W13 lecture source](../../Quarto/lectures/dgist-2026f-w13.qmd)

### First choice · Who lifted the foot?

Show one foot rising through the same angle twice. Students predict which movement the motor drove. A cutaway then shows how a platform pushing on the foot can also turn the motor shaft through the gears. This property is backdrivability. [MIT Biomimetic Robotics Lab, actuator design](https://biomimetics.mit.edu/research/1a9ba04b-d200-4743-b8fc-bf231f3231f0/)

| Film time | Picture |
| --- | --- |
| 0–6 s | A close view of the knee shows a white index line rising twice to the same mark. Keep the source of each movement outside the frame. Leave a still beat for a prediction. |
| 6–13 s | Pull back to show a leg fixed to a bench. Open the housing in cutaway. The powered motor lifts the foot clear of the platform. Keep both the shaft mark and the foot visible. |
| 13–23 s | Repeat from the starting pose with the drive off and the brake released. A gold platform beneath the foot rises. The foot lifts, the joint turns, and the mark on the motor shaft moves again. |
| 23–28 s | Hold the matched poses side by side. Label the inputs `Motor drives foot` and `Foot drives motor`. Ask whether a joint-angle record alone could identify who lifted the foot. |

Use a generic single-pivot leg with one visible gear pair. The platform acts away from the pivot. Drive both takes from the same joint-angle curve and give the rotor a contrasting mark against its stationary housing. ReelForge can track the cutaway with the camera and attach labels to points in the image. The foot, gears and platform use authored motion. The on-screen credit reads `CG render`. Live commentary fits the existing time for screen 19.

### Four alternative films

| Screen | Film | Reveal and production scope |
| --- | --- | --- |
| 10 · Wheel travel | How far did the cart go? | Follow a wheel mark for three quarters of a turn in each take. Pull back to a fixed view of two starting lines. One cart rolled on the floor. The other spun its wheel on a stand. Two copies of one simple model make this a short audience prediction. |
| 12 · Shoulder torque | The weight stayed the same | Show the same parcel held still at the same height in two poses. Swing from the front to a true side view. A plumb line under the parcel exposes the 20 cm and 40 cm horizontal lever arms. The torque from the parcel alone doubles. ReelForge already includes articulated arm models. |
| 43 · Evidence in a demo | What did this hand pick up? | Replay the same 12 seconds of recorded YAM joints in two views. Introduce two possible object histories, an object following the gripper and one staying on the table. Label them as hypotheses. Students name the extra observation that could decide what happened. ReelForge has a vetted left-arm recording in `assets/recordings/catalog.json`, episode 0, 32.5–44.5 s. |
| 36 · Modeling a motor | When the virtual motor gets ahead | Fit a pointer to a motor shaft. Overlay two pointers for a recorded response under load and a simulated response to the same input. Fit the model, then compare another input. A measured command-and-response trace is the extra asset this version needs. A version with synthetic curves should identify them as illustrative. Boston Dynamics describes the corresponding experimental workflow for wheeled Atlas. [Atlas development account](https://bostondynamics.com/blog/atlas-on-a-roll/) |

The cart gives students the quickest prediction. YAM offers a way to build directly from existing motion data. The single-joint film uses a cutaway and matching camera views to make a new hardware concept visible during the actuator chapter.
