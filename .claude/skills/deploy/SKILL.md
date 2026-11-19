---
name: deploy
description: Verify a Paper2PR release and publish it to GitHub Pages when the presenter requests deployment.
argument-hint: "[DeckName or all]"
allowed-tools: ["Read", "Bash", "Agent"]
---

# Publish slides

Run `./verify --all --regressions` and inspect the verified public artifact. A release receives the independent factual, visual and teaching reviews in the [shared review workflow](../../../.agents/skills/slide-excellence/SKILL.md). Keep loadable runtime assets, privacy and stable URLs intact. For local delivery, hand off the local build and results. When the presenter authorizes publishing, use the repository's main-branch Pages workflow and check the live slide and its empty speaker panel. Release media requires explicit per-clip redistribution approval. [Media guide](../../../guides/media.md)
