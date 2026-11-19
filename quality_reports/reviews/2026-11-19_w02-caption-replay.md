# W02 caption replay

The August 30 render audit records three claims above a 768px-wide video card. On its final reveal the teleoperation label fell below the canvas. The earliest published W02 QMD already puts the card beside the claims. The original pre-fix QMD and screenshot set were unavailable. The replay removes the column fences from the historical slide at 746c2ff, retaining its claims, clip, theme, attribution and four fragment groups. The control uses the approved W02 slide at dc364cb. [Archived render finding](dgist-2026f-w02-render-2026-08-30.md)

| Chrome viewport | Bottom of visible canvas | Reconstructed caption bottom | Approved caption bottom |
| --- | ---: | ---: | ---: |
| 1280 × 720 | 720 px | 920 px | 605 px |
| 896 × 720 | 612 px | 752 px | 532 px |

Chrome reached the final reveal by keyboard and retraced the fragment states in reverse. Both reconstructions failed the caption check. The approved slide passed at both sizes. Its screenshots show the demonstrator and robot together with the clip title, publisher, date, teleoperation label and playback speed. In the reconstruction the slide cuts off the video and both caption lines.

To repeat with the current audience build, run the following from the repository root. The replay writes each final PNG, measured caption bounds, navigation counts and HTML digest into the corresponding viewport directory.

```sh
./verify dgist-2026f-w02 --site _site
python3 scripts/replay_w02.py _site/slides/lectures/dgist-2026f-w02.html --out exports/w02-caption-replay
```
