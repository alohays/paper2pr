#!/usr/bin/env python3
"""Exercise real assembly entry points on two decks sharing a genre."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class SiteTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "checkout"
        shutil.copytree(ROOT / "scripts", self.root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(ROOT / ".claude/rules/slide-profiles", self.root / ".claude/rules/slide-profiles")
        self.env = os.environ.copy()
        self.private = "sample-" + "private-value"
        deny = Path(tmp.name) / "deny.txt"
        deny.write_text(self.private + "\n")
        self.env["PAPER2PR_PRIVATE_DENYLIST"] = str(deny)
        self.write("Quarto/_genres.txt", "lectures\n")
        for name in ["Public", "Hidden"]:
            self.write(f"Quarto/lectures/{name}.qmd", "## Title\n")
        self.write("Quarto/lectures/Public.deck.yml",
                   "title: Public talk\nruntime_assets:\n  - dynamic/diagram.json\n")
        self.write("Quarto/lectures/Hidden.deck.yml", "title: Hidden talk\npublish: false\n")
        self.page = self.write("Quarto/lectures/Public.html", """
        <section data-notes="sample-private-value"><h2>Audience view</h2>
        <aside id="presenter" class="fragment notes">sample-private-value
          <img src="../../Figures/lectures/Public/private-source.jpg"></aside>
        <script src="widget.js?v=2026"></script><link rel="stylesheet" href='lesson.css'>
        <img srcset="../../Figures/lectures/Public/demo.png 1x, ../../Figures/lectures/Public/full.png 2x">
        <img src="../../Figures/lectures/Public/diagram.svg#view"></section>""")
        self.write("Quarto/lectures/Hidden.html", "Private talk")
        self.write("Quarto/lectures/Hidden-timer.js", self.private)
        self.write("Quarto/lectures/Public_files/orphan.css", self.private)
        self.write("Quarto/lectures/dynamic/diagram.json", '{"frame": 1}')
        self.write("Quarto/lectures/widget.js", 'fetch("./dynamic/diagram.json")')
        self.write("Quarto/lectures/lesson.css", """@import"../fonts/font.css";""")
        self.write("Quarto/fonts/font.css", """@font-face{font-family:room;src:url("room.woff2")}""")
        self.write("Quarto/fonts/room.woff2", "font")
        self.write("Quarto/fonts/OFL.txt", "Synthetic font license")
        self.write("Figures/lectures/Public/diagram.svg",
                   '<svg xmlns="http://www.w3.org/2000/svg"><image href="svg-image.png"/></svg>')
        for image in ("demo.png", "full.png", "svg-image.png", "private-source.jpg"):
            self.write(f"Figures/lectures/Public/{image}", "image")
        self.write("Figures/lectures/Public/figures.yml", "source: /Users/fixture/private-original\n")
        self.write("Quarto/lectures/Public.forbidden.txt", self.private)

    def write(self, name, contents):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
        return path

    def cli(self, *command, success=True):
        run = subprocess.run(command, cwd=self.root, env=self.env,
                             text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertNotIn(self.private, run.stdout)
        self.assertNotIn("/Users/fixture", run.stdout)
        self.assertEqual(run.returncode == 0, success, run.stdout)
        return run.stdout

    def assemble(self, *args, success=True):
        return self.cli("bash", "scripts/assemble_site.sh", "_site", *args, success=success)

    def test_deck_closure_and_privacy(self):
        self.assemble()
        page = self.root / "_site/slides/lectures/Public.html"
        self.assertIn(self.private, self.page.read_text())
        self.assertNotIn(self.private, page.read_text())
        self.assertNotIn("Hidden", (self.root / "_site/index.html").read_text())
        self.assertNotIn("hidden", (self.root / "_site/index.html").read_text())
        files = {p.relative_to(self.root / "_site").as_posix()
                 for p in (self.root / "_site").rglob("*") if p.is_file()}
        self.assertEqual(files, {
            ".nojekyll", "index.html", "slides/lectures/Public.html", "slides/lectures/widget.js",
            "slides/lectures/lesson.css", "slides/lectures/dynamic/diagram.json",
            "slides/fonts/font.css", "slides/fonts/room.woff2", "slides/fonts/OFL.txt", "Figures/lectures/Public/demo.png",
            "Figures/lectures/Public/full.png", "Figures/lectures/Public/svg-image.png",
            "Figures/lectures/Public/diagram.svg",
        })
        self.assemble("lectures/Hidden", success=False)
        self.assertTrue(page.exists())
        self.cli(sys.executable, "scripts/assemble_site.py", "--preview", "public",
                 "exports/private/audience", "lectures/Hidden")
        self.assertTrue((self.root / "exports/private/audience/slides/lectures/Hidden.html").exists())
        self.cli(sys.executable, "scripts/assemble_site.py", "--preview", "public",
                 "_site", "lectures/Hidden", success=False)

    def test_failure_preserves_site_and_redacts_inputs(self):
        self.assemble()
        approved = (self.root / "_site/slides/lectures/Public.html").read_bytes()
        for extra in ('<img src="file:///Users/fixture/private-original">',
                      '<link href="../../Figures/lectures/Public/figures.yml">',
                      '<img src="../../Figures/lectures/Public/videos/private.mp4">',
                      '<script src="Hidden-timer.js"></script>',
                      '<img src="broken.png">', f'<p>{self.private}</p>',
                      f'<a href="https://example.org/{self.private.replace("-", "%2D")}">Source</a>'):
            with self.subTest():
                self.page.write_text("<section>" + extra + "</section>")
                self.assemble(success=False)
                self.assertEqual((self.root / "_site/slides/lectures/Public.html").read_bytes(), approved)
        self.write("_site/slides/lectures/extra.js", self.private)
        self.cli(sys.executable, "scripts/check_site_assets.py", "_site", success=False)

    def test_revoked_release_and_private_source_are_redacted(self):
        source = "private-source-library/raw/footage.mp4"
        self.write("Figures/lectures/Public/videos.yml", f"""videos:
  - slug: lesson
    title: Lesson
    publisher: Test publisher
    source_url: https://example.org/lesson
    published: 2026-11
    autonomy: unknown
    source: {source}
    redistribution: classroom
""")
        for hidden in (source, "https://github.com/alohays/paper2pr/releases/download/media-Public/lesson-poster.jpg"):
            self.page.write_text(f'<section><p>{hidden}</p></section>')
            log = self.assemble(success=False)
            self.assertNotIn(hidden, log)
        self.page.write_text('<section>Public lesson</section>')
        self.assemble()

    def test_classroom_media_is_preview_only(self):
        self.write("Figures/lectures/Hidden/videos/c.mp4", "video")
        self.write("Figures/lectures/Hidden/videos/c-poster.jpg", "poster")
        self.write("Quarto/lectures/Hidden.html", """
        <video poster="../../Figures/lectures/Hidden/videos/c-poster.jpg">
        <source data-src="../../Figures/lectures/Hidden/videos/c.mp4"></video>""")
        self.cli(sys.executable, "scripts/assemble_site.py", "--preview", "classroom",
                 "exports/classroom/site", "lectures/Hidden")
        self.cli(sys.executable, "scripts/check_site_assets.py", "--classroom", "exports/classroom/site")
        self.cli(sys.executable, "scripts/check_site_assets.py", "exports/classroom/site", success=False)
        self.cli(sys.executable, "scripts/assemble_site.py", "--preview", "public", "exports/public/site",
                 "lectures/Hidden", success=False)

    def test_legacy_output_kept_intact(self):
        self.write("_site/.nojekyll", "")
        self.write("_site/index.html", "Old preview")
        self.write("_site/slides/old.html", "Slides")
        self.write("_site/unrelated.md", "User work")
        self.assemble()
        [previous] = (self.root / "exports").glob("legacy-site-*/_site")
        self.assertEqual((previous / "unrelated.md").read_text(), "User work")
        self.assertFalse((self.root / "_site/unrelated.md").exists())
        self.assemble()
        self.assertEqual(len(list((self.root / "exports").glob("legacy-site-*"))), 1)

    def test_output_ownership(self):
        original = self.write("_site/keep.txt", "keep")
        self.assemble(success=False)
        self.assertEqual(original.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
