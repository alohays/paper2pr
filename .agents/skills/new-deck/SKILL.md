---
name: new-deck
description: Create or substantially revise a Paper2PR Quarto presentation from the presenter's brief.
---

# Author a Paper2PR deck

Read the brief, the existing deck metadata and any series handoff in the active worktree. Write down the audience, what they already know, the teaching slot and any required chapters, demos or time allocations. Ask only about a consequential gap. Keep agreed content across revisions and leave routine examples, figure design, layout, slide count and reveal sequence to the author.

For a new deck, scaffold with `python3 scripts/new_deck.py --help` and the relevant options. A series and session index supply the title and date. Refine the resulting `.deck.yml` with public sources, audience context and any explicit `brief` obligations. Express required chapters and demonstrations with stable IDs on the corresponding QMD slides. [Brief format and worked example](../../../guides/framework.md)

Write the deck in `Quarto/<genre>/<deck>.qmd`. Open the design principles for new work and the resolved profile from `python3 scripts/deckprofile.py <deck>`. Select a legible comparison, diagram or sequence for each teaching point. Choose examples that let the audience see what each required chapter contributes. Cite the evidence for claims and credit third-party figures on the slide. Declare clips with their redistribution policy. [Design reference](../../../.claude/rules/slide-design-principles.md) · [Media guide](../../../guides/media.md)

Run `./verify <deck>` and use its audience frames. When the brief calls for local demos, also run `./verify <deck> --delivery classroom`. For a new talk, obtain the three independent reviews and resolve verified findings within scope. [Review workflow](../slide-excellence/SKILL.md)
