# DGIST W02 local presenter launch (2026-09-03)

## Goal

Open the DGIST HSS118 lecture scheduled for 2026-09-04 from the current local
source and show its RevealJS presenter view with the Korean speaker script.

## Steps

1. Resolve the 2026-09-04 session from the course manifest and confirm the deck.
2. Render the deck from its Quarto source and run the deck quality gate.
3. Verify that the local HTML contains speaker notes.
4. Serve the Quarto output on localhost, open the audience deck, and launch the
   RevealJS presenter window.

## Acceptance

- The opened deck is `dgist-2026f-w02` dated 2026-09-04.
- The latest local QMD renders successfully.
- The quality score is at least 80/100.
- The presenter window shows the current slide, next slide, timer, and Korean
  speaker notes.
