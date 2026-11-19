# Replaying the W13 presenter brief

The November 18 outline allocates 50 minutes across ten chapters, followed by ten minutes of questions. The November 19 restoration keeps four ground embodiments and uses the wheeled Atlas at the beginning and end. The audience is second-semester first-years with no mechanics or control prerequisite. The acceptance fixture records chapter opening IDs, the original allocations and eight demonstration requirements. Individual slide count, examples and fragment order remain author decisions. [W13 fixture](../../Quarto/_fixtures/gates/w13-brief.yml)

We rendered two historical revisions with Quarto 1.11.9 in temporary directories and compared their actual Reveal sections with the same brief.

| Lecture revision | Audience sections | Required chapter anchors in order | Required demonstrations present | Result |
| --- | ---: | ---: | ---: | --- |
| `1abb968`, narrowed survey | 25 | 2 of 10 | 3 of 8 | Failed |
| `b1517c4`, restored survey | 50 | 10 of 10 | 8 of 8 | Passed |

The restored metadata matched the audience, 60-minute booking, ten minutes of questions and one minute of quiet playback. Video occupies part of the 3,000-second teaching clock. In the shortened deck, a warehouse overview and the returning Atlas clip still appeared. The missing actuator chapter and embodiment demonstrations identified the scope loss. The current local W13 classroom render also passed the same brief. This checks the planned clock and visible content. Presenter pacing is measured in rehearsal.

To repeat in a checkout with the archived W13 revisions available locally, select the pinned Quarto on PATH and run the following commands from the repository root.

```bash
replay=$(mktemp -d)
for revision in 1abb968 b1517c4; do
  mkdir "$replay/$revision"
  git archive "$revision" Quarto/_quarto.yml Quarto/_filters Quarto/clean-academic.scss \
    Quarto/fonts Quarto/lectures/_series Quarto/lectures/dgist-2026f-w13.qmd \
    Quarto/lectures/dgist-2026f-w13.deck.yml Figures/lectures/_series \
    Figures/lectures/dgist-2026f-w13 Bibliography_base.bib | tar -x -C "$replay/$revision"
  quarto render "$replay/$revision/Quarto/lectures/dgist-2026f-w13.qmd" -M w13-local-clips:true --quiet
done
python3 scripts/test_profiles.py \
  --w13-before "$replay/1abb968/Quarto/lectures/dgist-2026f-w13.html" \
  --w13-html "$replay/b1517c4/Quarto/lectures/dgist-2026f-w13.html" \
  --w13-config "$replay/b1517c4/Quarto/lectures/dgist-2026f-w13.deck.yml"
```

The default regression suite also checks missing, duplicate and reordered IDs, a substituted clip, an incorrect chapter budget, notes-only content and the freedom to add slides inside the brief. The historical replay reads the classroom clip identities from HTML. Playback verification runs on the actual media-equipped build.
