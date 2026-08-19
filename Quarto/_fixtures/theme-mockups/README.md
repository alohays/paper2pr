# W02 slide-type fixture (not published)

Five W02 slides (outline 7, 12, 13, 25, 33) plus the title slide, rendered on
the main theme `Quarto/clean-academic.scss`: video-full hook, divider, chart
figure + footnote, formula + legend + gloss, eight-item timeline. `body.qmd`
holds the slides; `w02-sample.qmd` is the wrapper with the fixture-local
defaults that `_quarto.yml` would supply for a real deck (width/height/margin,
the slide-types filter, the Pretendard link). Media in `media/` is third-party
and gitignored; screenshots land in `shots/` (also gitignored, regenerable).
The WP0 mockup round rendered the same slides on three themes; the presenter
chose the light academic one on 2026-08-19, and that decision is recorded in
`quality_reports/plans/2026-08-19_presentation-framework-v2.md` (WP0).

    quarto render w02-sample.qmd && bash shoot.sh w02-sample 6
