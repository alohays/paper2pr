# Classroom clips and public slides

Declare a clip in `Figures/<genre>/<deck>/videos.yml` and place its original in the gitignored `videos/src/` directory. Use a deck-relative name for the original or link it there from the local library. For an existing, final clip, place it at `videos/<slug>.mp4` and omit `source` and `segment`.

```yaml
videos:
  - slug: grasp
    title: A grasp under load
    publisher: Example Lab
    source_url: https://example.org/grasp
    published: 2026-05
    autonomy: claimed
    redistribution: classroom
    source: src/grasp.mp4
    segment: 2-10
    caption: visible
```

`redistribution: classroom` shows a link to the publisher on public slides. The classroom presentation plays the local clip. Omitted policies have the same behavior. Set `redistribution: release` only when the presenter has approved publishing **both the prepared clip and its poster**. Record provenance in `licence_note` when needed. A manifest entry documents a decision about this particular excerpt.

Prepare the clips with `python3 scripts/media_prep.py <Deck>`. It writes the MP4s, posters and `videos.json`. A change to the manifest requires a fresh lock. The lock records the source identity as a digest. The public site contains the links and captions the slides use. Encoding needs ffmpeg and ffprobe.

| Audience | Render command | Classroom clip | Approved clip |
| --- | --- | --- | --- |
| Public | `quarto render Quarto/<genre>/<Deck>.qmd -M delivery:public` | Publisher link | Release video and poster |
| Classroom | `quarto render Quarto/<genre>/<Deck>.qmd -M delivery:classroom` | Local files | Release video and poster |
| Offline classroom | Prepare with `--local`, then render with `-M delivery:classroom` | Local files | Local files |

A plain render uses public media choices. To keep a separate local presenter copy, render the QMD with `-M delivery:classroom --output <Deck>-classroom.html`. The teaching format in `<Deck>.deck.yml` (e.g. in-person) describes the audience context.

Use `{{< video-card grasp >}}` for an inline clip or two cards inside a `.two-up` div. `## {.video-full video="@grasp"}` sets a full-slide background. An optional `{{< video-caption grasp >}}` adds its caption. Public full-slide treatment includes a publisher link even for an empty slide or `caption: none`. The shortcode also accepts `class="..."`. Both forms preserve `data-video-slug` for verification.

Other manifest fields include `speed` (default `1x`), `keep_audio` (default `false`), `autonomy` (`autonomous`, `claimed`, `teleop` or `unknown`) and `caption` (`visible`, `fragment` or `none`). The segment uses source seconds, either `start-end` or `start-`. `--only <slug>` prepares one entry. `--force` recuts selected clips.

To check existing Release files, use `bash scripts/media_release.sh <Deck> --check`. For an authorized upload, omit `--check`. Both commands select the same approved files from the current manifest, check the lock and use the existing `media-<Deck>` tag and asset names. A manifest with only classroom entries makes zero network calls. Changing a policy updates future renders and upload lists. Previously uploaded assets have their own GitHub Release lifecycle.
