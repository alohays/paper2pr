# Plan: On-Manifold TFG project-page hosting

**Date:** 2026-09-01
**Status:** COMPLETED

## Objective

Make `https://manluml.github.io/on-manifold-tfg/slides/` the canonical presentation URL while retaining the authored deck in Paper2PR and preventing a duplicate Paper2PR Pages deployment.

## User decisions

- Use the clean `/slides/` canonical path.
- Copy this validated static bundle once; do not add cross-repository credentials or automatic synchronization.
- Exclude the deck from the Paper2PR landing page and Pages artifact while keeping its source and direct local render available.

## Implementation

1. Start from the latest remote `gh-pages` state in an isolated worktree so the divergent local checkout is preserved.
2. Package the note-stripped Reveal output as a self-contained `slides/` subtree, rewrite only the two bundle-relative asset prefixes, and add canonical metadata.
3. Add `Slides` links to the project-page navigation and hero actions.
4. Add a strict, default-true `publish` field to Paper2PR deck configuration and use it in render selection, landing generation, and site assembly.
5. Mark `talks/on-manifold-tfg` as `publish: false`, regenerate the Paper2PR landing page, and verify stale rendered HTML and deck-scoped assets cannot leak into its Pages output.

## Verification

- Every project-page local reference resolves.
- `/slides/` contains 16 slides, zero speaker-note elements, no broken images, and the expected canonical URL.
- The project-page `Slides` links are visible without horizontal overflow.
- Paper2PR's publishable list omits this deck; its unpublishable list contains it.
- A full Paper2PR render skips this deck, and a fresh assembled site contains neither its HTML, compiled files, loose CSS, landing entry, nor deck-scoped figures.
- No push or pull request is made without separate authorization.
