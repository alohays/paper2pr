"""Selection regressions for read-only PR verification. Run from any directory."""
import unittest

import deckpath
from verify import affected


class Selection(unittest.TestCase):
    def setUp(self):
        self.decks = deckpath.all_decks()

    def test_single_deck_and_docs(self):
        w02 = deckpath.find("dgist-2026f-w02")
        paths = [str(w02.qmd.relative_to(deckpath.REPO_ROOT)), "README.md"]
        self.assertEqual(affected(paths, self.decks), ([w02], False))
        self.assertEqual(affected(["quality_reports/reviews/change.md"], self.decks), ([], False))

    def test_shared_and_deleted_sources(self):
        for path in ("Quarto/lectures/_series/dgist-2026f/semester-map.qmd",
                     "Quarto/clean-academic.scss", "Quarto/_filters/video-card.lua",
                     "Quarto/lectures/dgist-2026f-w06-fonts.css",
                     "Quarto/_quarto.yml", "Quarto/lectures/removed.qmd",
                     "Figures/lectures/_series/dgist-2026f/series.json"):
            with self.subTest(path=path):
                self.assertEqual(affected([path], self.decks), (self.decks, True))


if __name__ == "__main__":
    unittest.main()
