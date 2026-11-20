## DGIST HSS118 W13 classroom check

*Foundations of Robot Hardware, Control, and Modern Platforms* uses the lecture profile for first-years in their second semester. The presenter teaches from the English RevealJS deck with private Korean notes on all 50 screens. The profile allows four one-line bullets, three with a figure, one wrapped bullet and one colored box per screen.

### Teaching clock for November 20

| Chapter | Screens | KST | Slot | Clip playback | Timed student pauses |
|---|---:|---|---:|---:|---:|
| 0 · Opening scene | 1–6 | 13:00:00–13:02:50 | 2:50 | 16 s | 15 s |
| 1 · Wheel command | 7–10 | 13:02:50–13:07:00 | 4:10 | | 20 s |
| 2 · Reading specifications | 11–14 | 13:07:00–13:10:20 | 3:20 | | 17 s |
| 3 · Actuators and transmissions | 15–22 | 13:10:20–13:20:40 | 10:20 | 15 s | 26 s |
| 4 · Sensors and hands | 23–26 | 13:20:40–13:23:20 | 2:40 | 8.5 s | 9 s |
| 5 · Feedback and control | 27–32 | 13:23:20–13:33:20 | 10:00 | 17 s | 35 s |
| 6 · History | 33–36 | 13:33:20–13:37:00 | 3:40 | 43 s | 5 s |
| 7 · Jobs and platforms | 37–42 | 13:37:00–13:44:10 | 7:10 | 55.1 s | 15 s |
| 8 · Evidence in the field | 43–47 | 13:44:10–13:48:30 | 4:20 | | 21 s |
| 9 · Return to wheeled Atlas | 48–49 | 13:48:30–13:50:00 | 1:30 | 12 s | 12 s |
| Questions | 50 | 13:50:00–14:00:00 | 10:00 | | Open discussion |

The 50 teaching minutes include 2 minutes 47 seconds of footage and 2 minutes 55 seconds of explicitly timed waits for tracing, predicting, reading or opening the question wall. The two Berkeley clips share an 11-second interval. The script allows about a minute of quiet viewing and narrates the remaining footage. Individual student answers, pointing and clicks share their screen's slot. The presenter notes give each screen's start and finish time. The Reveal speaker timer uses the same allocations.

### What students can now test

- On 9–10 they read three quarters of a turn in the first second, then choose where to put a ruler. The two carts give them evidence for distinguishing wheel rotation from cart travel.
- On 14 they choose a pose for a 3 kg load before seeing the two manufacturer ratings. On 17 three keyboard advances rotate the marked motor gear one revolution apiece. Each moves the joint gear a third of a revolution in the opposite direction. The fourth advance asks about torque and the fifth shows the steady, lossless comparison.
- On 28 both encoder readings share a 30° target and a positive gain. The presenter allows eight seconds to choose. The first reveal identifies the 10° and 2° gaps. The second shows the proportional control equation. The equation renders locally.
- On 41 each half of the screen follows the bottom edge of one box through a lift. The lift count appears after the class has inspected both attempts. On 48 the monitor beside the gamepad frames a new question about the recorded warehouse turn.

### Evidence checked before class

- The ArmnetBench authors report 37 successes and 218 failures in 255 block-stacking attempts. They released video, joint states and commands for those attempts. [November 2 preprint, Table 2](https://arxiv.org/html/2611.03168v1)
- Berkeley's result is 9 successful G1 lifts in 10 attempts with 2 kg added to the box. The project shows one selected attempt per method. [Hardware results](https://forcectrl.github.io/#hardware) · [November 3 preprint](https://arxiv.org/abs/2611.05507)
- Boston Dynamics describes tuning a simulated motor against measurements from its wheeled Atlas testbed. The film shows an operator with a simulated robot. Identifying the steering input for the physical warehouse turn would require that run's input record. [November 9 engineer's account](https://bostondynamics.com/blog/atlas-on-a-roll/)
- The trailer footage shows the 2021 Stretch prototype. The new valves and sensing are described in the manufacturer's separate Gen 2 announcement. The Spot inspection count comes from two robots in Singapore since April. The same announcement dates planned Atlas testing to early 2027. [Prototype film](https://www.youtube.com/watch?v=yYUuWWnfRsk) · [November 3 Stretch announcement](https://bostondynamics.com/news/boston-dynamics-launches-next-generation-stretch-robot/) · [November 17 joint announcement](https://bostondynamics.com/news/boston-dynamics-globalfoundries-expand-robotics-collaboration/)

### Classroom checks on the presenter's Mac

Chrome displayed all 50 screens and 40 reveal states at 1280 × 720 and 896 × 720. The narrower window has an 896 × 504 slide canvas. Inspection of all 180 rendered states led to larger source captions, centered equation text and more room under the inspection-point label on 46. The full frame of each G1 clip includes the hands, the box and the floor.

All 13 clips played at normal file speed to their final frame. The last frame holds while students answer. The two box examples played concurrently. A keyboard traversal reached Q&A in 89 advances. Both local pages ran with outside lecture requests blocked. The live Wooclap form was tested online.

The presenter page opens the Korean scripts with S. Its ordinary slide window hides the scripts. Both student HTML copies have zero note elements, zero note attributes and zero Hangul characters. The W13 clean filter and installed commit hook passed using a temporary index. The original 45-note backup and the final 50-note backup each restored byte for byte in memory. The deck scored 100/100 and the assembled site asset check passed.

### In-room rehearsal in E7-233

Check the physical display assignment, live captions, back-row readability and a phone scan on the classroom network. The course-wide Wooclap form opens with a question dated October 23. The presenter notes identify it as the shared course wall and provide a spoken-question alternative. Rehearse one timed run with responses and switch to Q&A at 13:50.

On the presenter's Mac, open the [presenter deck](http://127.0.0.1:4317/slides/lectures/dgist-2026f-w13-classroom.html) and press S for the private window. The [student copy](http://127.0.0.1:4315/slides/lectures/dgist-2026f-w13.html) can be opened independently. To move it to a classroom computer, copy the complete `.local/w13-classroom-preview/site/` directory, which contains the films, fonts and Reveal runtime. After a reboot of this Mac, run the following command from the W13 checkout to restore both local links.

```sh
python3 .local/w13-final/playback/start.py
```
