---
name: write-speaker-notes
description: Write or revise a Paper2PR presentation's local speaker notes for its audience, language and teaching time.
---

# Write the local script

Resolve the deck with `python3 scripts/deckprofile.py <deck>`. Read its brief, existing notes, delivery context and sources. Preserve the presenter's wording where it already works. Back up the notes before replacing them with `python3 scripts/backup_notes.py backup <deck>`.

Use the requested notes language or the deck's `language.notes`. Budget speech against `duration_min - video_min - qa_min`. Include narration during a clip only once. Follow the required chapter timing and link each cue to what is actually visible at that point in the reveal sequence. Rehearsal with the presenter's own pace is the timing check.

Write directly under each slide in a `.notes` div. The title slide uses `title-slide-attributes.data-notes`. A shared slide takes its per-deck notes immediately after the include in the deck. Keep private wording in the working QMD, its local presenter render and ignored backups. Store public-safe timing or coverage counts in a requested report.

Use `./verify <deck> --delivery classroom` to check the local presentation and `./verify <deck>` for the audience version. Press `S` in the presenter render to check cues on the actual transitions. [Notes and delivery](../../../guides/framework.md)
