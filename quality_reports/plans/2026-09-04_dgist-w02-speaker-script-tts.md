# DGIST W02 speaker-script TTS (2026-09-04)

## Goal

Create a local Korean rehearsal audio track from the current speaker notes for
`dgist-2026f-w02`, without sending the local-only script to an external service.

## Plan

1. Extract the title note and all slide note blocks in presentation order.
2. Remove non-spoken production cues and choose one canonical path through
   response branches so alternatives are not read back-to-back.
3. Normalize Markdown, symbols, English abbreviations, and pauses for Korean
   text-to-speech while preserving the meaning of the script.
4. Synthesize with the best installed Korean macOS voice and convert the result
   to a broadly playable MP3 under `exports/`.
5. Verify note coverage, text normalization, audio duration, codec, channels,
   sample rate, and successful decoding.

## Acceptance

- The source remains the local QMD speaker notes; no cloud TTS is used.
- All 47 slides are represented in order.
- Stage directions, branch labels, and non-spoken source blocks are not voiced.
- The output is a valid, seekable MP3 suitable for full-talk rehearsal.
