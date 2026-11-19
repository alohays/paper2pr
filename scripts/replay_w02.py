#!/usr/bin/env python3
"""Replay W02's August caption finding beside an approved audience HTML build.

The first published QMD (746c2ff) already has the repair. Reconstruct the
archived review's single-column arrangement by removing its column fences.
Keep the original clip, captions, three claim fragments and historical theme.
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from shoot_slides import shoot

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "Quarto/lectures/dgist-2026f-w02.qmd"
SLIDE = "autonomous-or-teleoperated"
BASE = "746c2ff"
ASSETS = ["Bibliography_base.bib", "Quarto/_quarto.yml", "Quarto/_filters",
          "Quarto/clean-academic.scss", "Quarto/fonts", SOURCE,
          "Figures/lectures/dgist-2026f-w02/videos.json",
          "Figures/lectures/_series/dgist-2026f/series.json"]


def replay(directory):
    archive = directory / "source.tar"
    with archive.open("wb") as stream:
        subprocess.run(["git", "archive", BASE, *ASSETS], cwd=ROOT, stdout=stream, check=True)
    subprocess.run(["tar", "-xf", archive, "-C", directory], check=True)
    qmd = directory / SOURCE
    source = qmd.read_text()
    boundary = source.index("\n---\n") + len("\n---\n")
    start = source.index("## Autonomous or teleoperated?")
    slide = source[start:source.index("\n## ", start)]
    for fences in (':::: {.columns}\n::: {.column style="flex:0 0 44%;"}\n',
                   ':::\n\n::: {.column style="flex:0 0 52%;"}\n',
                   ":::\n::::\n"):
        if slide.count(fences) != 1:
            raise ValueError("source does not match the archived column repair")
        slide = slide.replace(fences, "\n")
    qmd.write_text(source[:boundary] + "\n" + slide)
    subprocess.run(["bash", ROOT / "scripts/render_decks.sh", qmd], check=True)
    return qmd.with_suffix(".html")


def run(approved, out):
    with tempfile.TemporaryDirectory(prefix="paper2pr-w02-") as source:
        broken = replay(Path(source))
        for width in (1280, 896):
            for name, html in (("reconstruction", broken), ("approved", approved)):
                dest = out / name / f"{width}x720"
                try:
                    shoot(html, dest, "w02", width=width, slide_id=SLIDE)
                except ValueError as error:
                    if name != "reconstruction" or not str(error).startswith(f"caption clipped on {SLIDE} "):
                        raise
                else:
                    if name == "reconstruction":
                        raise ValueError("the reconstructed clipping defect escaped detection")
                boxes = json.loads((dest / "browser.json").read_text())["captions"][SLIDE]
                if len(boxes) != 1:
                    raise ValueError("expected one visible teleoperation caption")
                box = boxes[0]
                print(f"{name}, {width}x720: caption ends at {box['bottom']}px, "
                      f"canvas ends at {box['canvas_bottom']}px")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("approved", type=Path, help="verified W02 HTML with its runtime assets")
    parser.add_argument("--out", type=Path, default=ROOT / "exports/w02-caption-replay")
    args = parser.parse_args()
    run(args.approved.resolve(), args.out.resolve())
