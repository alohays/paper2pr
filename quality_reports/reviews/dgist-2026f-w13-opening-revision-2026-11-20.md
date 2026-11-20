## W13 opening revision · November 20, 2026

The instructor reviewed screens 2 to 10 on the morning of the class and asked for ten changes. The deck now has 51 screens. The private Korean notes follow the new order. The edit was made from a Claude Code session, outside the Codex thread that authored the deck.

| New screen | Change |
|---|---|
| 2 | The question QR moved up from screen 5. It is written inline (`## Ask anytime {#ask-anytime .qr-slide ...}`). The shared include starts with an HTML comment, and a comment before the first `##` renders an empty screen. |
| 3 | Agenda. The notes preview all ten chapters in order. Chapter 2 is renamed from "Reading a datasheet" to "Joints, reach, payload and power". |
| 4 | "Why is Physical AI taking off?" recalls the September 4 lecture as three steps (language models, robots, scaling the data). One advance adds "Today · The robot hardware that collects this data and carries out the action". |
| 5 | The four teleoperation films follow directly, retitled "Collecting robot data takes hardware". The notes tie teleoperation to data collection and announce the hardware topic. |
| 6 | Chapter 1 agenda as its own screen (`.w13-agenda-only`). Chapters 2 to 9 keep the overlay. |
| 7 | Atlas now opens chapter 1 and carries the "01 ·" prefix. |
| 8 | Marked wheel. One advance turns the orange mark once in one second (CSS in `marked-cart.svg`), then shows the answer. |
| 9 | Command diagram. Notes shortened by 10 seconds. |
| 10 | New encoder screen (`encoder-count.svg`, `_w13/encoder-count.inc`). First advance: the disc turns three quarters of a turn in one second and the counter goes from 0 to 6. Second advance: "6 of 8 marks in one second: ¾ turn per second. The target was 1." It replaces "Did the wheel make a full turn in one second?". `wheel-turn-record.svg` is no longer used. |
| 11 | Cart distance. A second advance adds proprioception. The notes explain that equal encoder readings can mean different motion. |

### Timing

The opening grew by 98 seconds. Teaching now ends at 13:51:38 and questions run to 14:00 (502 seconds). `.local/w13-claude-2026-11-20/reclock.py <qmd> --write` recomputes every note's clock line from `data-seconds`. The Q&A note refers to screen 42 for the box lift (was 41).

### Checks

- Screens 1 to 11 with every build, on the presenter copy (port 4317) and the audience copy (port 4315), at 1280 × 720: no overflow and no script errors. The audience copy has 51 screens and no notes.
- Not repeated: the caption-width pass (896 × 720), the reduced-motion pass, the repository quality score and the film playback checks from the earlier review.

The files before this edit are in `.local/w13-claude-2026-11-20/` (`before.qmd`, `before.css`, `before-classroom.html`, `marked-cart.svg`, `before.figures.yml`).
