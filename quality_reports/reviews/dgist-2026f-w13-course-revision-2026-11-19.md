## DGIST W13 revised classroom delivery

The November 20 lecture opens from the series' work on robot demonstrations and learning. Its first Atlas film gives an immediate answer. Ankle motors drive the wheels and a learned whole-body controller helps the robot balance through the turn. The talk distinguishes that control problem from identifying the source of a particular steering input. The closing sequence shows where measurements from the real actuator entered simulated training. [Atlas controls engineer's account, November 9](https://bostondynamics.com/blog/atlas-on-a-roll/)

### Where to look in the deck

| Screens | Material | What the class can see or measure |
|---|---|---|
| 3 and nine chapter entrances | A complete ten-topic agenda with the current entry in bold black and the others in gray | One advance opens the lesson at the same slide number. Reverse navigation restores the agenda. |
| 4, 13, 38 | Trossen Stationary AI, I2RT YAM, Franka Research 3 and original ALOHA | Leader/follower input, a hand-guided joint trajectory, an externally powered control box, and a human operating two arms to open a package. |
| 17, 22–23, 28 | Gearing, ROBOTIS OP3's XM430 actuators, angular measurement and feedback | Count three input turns for one output turn. Identify the shaft that was measured. Compare 20° and 28° against a 30° target before reading the proportional rule. |
| 34, 39–43 | DRC-HUBO, Galbot G1, Unitree inspection quadruped and G1, Rainbow Robotics RB-Y1, Galaxea R1 Lite | Follow the drill, mobile base, instrument, box or bedspread through a specific task. The original playback speed and control evidence accompany the film. |
| 44–49 | Repeated trials, AGIBOT's store trial, reported factory inspections and the return to Atlas | Identify the unit of each count. Connect data collection and actuator measurements to what a learned controller can do on the real body. |

The Trossen workstation and the original ALOHA experiment are separate examples. YAM documents recording a joint trajectory by hand with gravity compensation. DRC-HUBO footage was recorded at the 2015 final, while RB-Y1 is a wheeled dual-arm research platform. The Unitree film credits the manufacturer. The named B2 hydropower photograph on screen 37 comes from a separate case study. [Trossen](https://www.trossenrobotics.com/stationary-ai) · [I2RT](https://doc.i2rt.com/products/yam#record-replay-trajectory) · [Original ALOHA](https://tonyzhaozh.github.io/aloha/) · [ROBOTIS OP3](https://docs.robotis.com/docs/systems/op3/introduction/) · [Rainbow Robotics](https://www.rainbow-robotics.com/en/products/rb-y1) · [Unitree B2 case](https://www.unitree.com/industry/electricity/)

The Galbot G1 freezer and aisle shots come from a manufacturer montage. The R1 Lite film carries the researchers' autonomous, 10× label. AGIBOT's November 6 report counts 1,730 tasks over 24 hours across six G2 robots in a Shanghai store. Four passed the company's assessment. The Singapore semiconductor-fab count is an operator/manufacturer report of two Spot robots performing more than 90,000 inspections since April. [Galbot](https://www.galbot.com/g1/) · [OpenGalaxea](https://opengalaxea.github.io/GalaxeaVLA/) · [AGIBOT](https://agibot.com/news/newsroom/post-134) · [GlobalFoundries and Boston Dynamics](https://bostondynamics.com/news/boston-dynamics-globalfoundries-expand-robotics-collaboration/)

### Presentation and classroom checks

- The ten chapter slots run from 13:00 to 13:50 KST. Screen 50 reserves the final ten minutes for questions. The Korean notes budget the film, agenda and student-response time inside each slot.
- Every screen has revised Korean notes. The presenter HTML opens them in Reveal's native S window. The classroom and regular student HTML files contain zero note elements, zero note attributes and zero Hangul characters.
- All 50 opening states and 45 reveals were inspected at 1280 × 720 and 896 × 720, giving 190 captures including the 896 × 504 slide canvas beside captions, initial views, every reveal and the source credits. The opening film answer, alignment of the four job captions and the Shanghai store photograph were corrected during the projection review.
- Fourteen local clips occupy thirteen screens. The two Berkeley G1 recordings play together. One pass through the films occupies approximately 2 minutes 33 seconds of the teaching clock. Entry films wait for the chapter agenda to be dismissed.
- The course QR opens the existing Wooclap participation form. Its displayed question date is October 23. A question can also be taken aloud. Check the back row, projector brightness, display routing, captions and phone reception in E7-233.
- The repository quality gate scored 100/100. The installed pre-commit hook passed on a temporary index. The pre-revision and final private backups both restored all 50 notes byte for byte.

On the presenter's Mac, open the [presenter copy](http://127.0.0.1:4317/slides/lectures/dgist-2026f-w13-classroom.html?rev=2#/title-slide) or the [student copy](http://127.0.0.1:4315/slides/lectures/dgist-2026f-w13.html?rev=2#/title-slide). The classroom preview folder contains the media and Reveal runtime. After a reboot, the existing local restart script restores both servers.

```sh
python3 .local/w13-final/playback/start.py
```
