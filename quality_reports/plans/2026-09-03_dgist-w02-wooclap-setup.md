# DGIST W02 Wooclap setup (2026-09-03)

## Goal

Finish the Wooclap question-wall setup for the DGIST HSS118 series and replace
the placeholder participation details in the local RevealJS deck.

## Plan

1. Inspect the supplied Wooclap event in the logged-in Chrome session.
2. Verify the participant code and canonical audience URL.
3. Confirm or create the intended Message wall interaction and its live-session
   state.
4. Update `Quarto/lectures/_series/dgist-2026f.yml` with the verified URL and
   code.
5. Rebuild the series lock and QR assets, then render `dgist-2026f-w02`.
6. Run series, deck, and visual checks and verify both QR slides resolve to the
   Wooclap event.

## Acceptance

- The event has one usable Message wall for questions during the lecture.
- The deck shows the verified participation code and URL, with no placeholder.
- Both QR slides use the regenerated series QR asset.
- The series check, Quarto render, and deck quality score pass.
