# Audience canvas review

The browser survey covered the seven published decks alongside the separate DreamZero playback and equation review. Chrome measured video, figure and caption bounds in 560 slide and fragment states at 1280 × 720. The DGIST runs repeated 303 states at 896 × 720. Representative final screenshots from each deck were inspected at its delivery sizes.

| Deck | Observed loss | Repair and verification |
| --- | --- | --- |
| DreamDojo | Illustrations, chart captions, adaptation details and final interpretations fell below twelve slides. The distillation figures extended 227 px below their visible area and their captions were lost. | Reflowed the existing material into columns or resized its illustration. Reviewed all twelve repaired frames. Fifty audience frames remain. The bounds check rejects the old distillation slide and accepts the repaired version. |
| RoboTTT | The three bimanual task descriptions ran as much as 57 px below the task montage. The circuit training/test split and the last gear-bot instruction were cut off. | Reduced the montage width. The three descriptions and all demonstration stills now fit. |
| SUNY | The global author footer overlapped the labor comparison on page 7. Four product features on page 18 sat below the frame. | Raised the comparison strip and reserved footer space below the product image and feature labels. Inspected the two audience frames. |
| W02, W06, W09 and TTA | The visible audience state passed the bounds check. | Inspected the W02 autonomy label and two-wave comparison, W06 recovery and generated-world demonstrations, W09 DAgger and source-panel reveals, and TTA's paired demonstration slides. |

The W09 value chart trims the source image's margins, and the ACT backup slide alternately frames two panels of the source figure. SUNY's browser and phone mockups also use intentional image crops. All three render their intended content. The geometry check intersects source artwork with these inner panels, examines visible teaching text and outer figure boxes after fragments settle, and records slide IDs and content types in the local browser receipt. Overlap between two elements that both fit on the slide still needs visual review.

```sh
./verify papers/DreamDojo
./verify papers/RoboTTT --slide three-tasks-all-bimanual-all-long
./verify talks/SUNY --slide section-17
```
