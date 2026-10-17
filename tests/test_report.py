import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.fleet_street.report import create_report, render_report


ROOT = Path(__file__).resolve().parents[1]


class ReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = json.loads((ROOT / "examples/report.json").read_text())
        self.budget = json.loads((ROOT / "examples/budget.json").read_text())
        (ROOT / ".temp").mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT / ".temp")
        self.addCleanup(self.temporary.cleanup)
        self.output = Path(self.temporary.name) / "report"

    def test_complete_local_bundle_is_not_publication(self) -> None:
        result = create_report(self.report, self.budget, self.output)
        self.assertFalse(result["published"])
        self.assertEqual({str(filename.relative_to(self.output)) for filename in self.output.rglob("*") if filename.is_file()}, {"index.html", "assets/report.css", "assets/proscenium.svg", "assets/LICENSE.txt", "data/budget.json"})
        self.assertEqual((self.output / "assets/LICENSE.txt").read_bytes(), (ROOT / "LICENSE").read_bytes())
        self.assertEqual(json.loads((self.output / "data/budget.json").read_text())["balance"], "-457.75")
        html = (self.output / "index.html").read_text()
        self.assertIn("Fictional example", html)
        self.assertIn("GBP 4,745.25", html)
        self.assertIn("297 paid tickets", html)
        self.assertNotIn("<script", html)
        self.assertTrue(all(filename.stat().st_nlink == 1 and not filename.is_symlink() for filename in self.output.rglob("*") if filename.is_file()))

    def test_supplied_markup_is_text_not_executable_html(self) -> None:
        self.report["title"] = '<img src=x onerror="alert(1)">'
        self.report["findings"][0]["text"] = "<script>bad()</script>"
        self.budget["costs"][0]["label"] = "<iframe>"
        html, _ = render_report(self.report, self.budget)
        self.assertIn("&lt;img", html)
        self.assertIn("&lt;script&gt;bad()&lt;/script&gt;", html)
        self.assertIn("&lt;iframe&gt;", html)
        self.assertNotIn("<img src=x", html)
        self.assertNotIn("<script>", html)

    def test_unsafe_sources_fail_before_creating_a_directory(self) -> None:
        for reference in ["javascript:alert(1)", "data:text/html,bad", "http://example.test", "https://user:secret@example.test", "/home/someone/private.txt", "../private.txt", "C:\\private\\file.txt"]:
            with self.subTest(reference=reference):
                changed = {**self.report, "sources": [{"label": "Test", "reference": reference}]}
                with self.assertRaises(ValueError):
                    create_report(changed, self.budget, self.output)
                self.assertFalse(self.output.exists())

    def test_https_citations_are_links_without_external_resources(self) -> None:
        self.report["sources"] = [{"label": "Venue", "reference": "https://venue.example.org/information?layout=studio&version=1"}]
        html, _ = render_report(self.report, self.budget)
        self.assertIn('href="https://venue.example.org/information?layout=studio&amp;version=1"', html)
        self.assertNotIn('src="https://', html)

    def test_existing_output_is_never_overwritten(self) -> None:
        self.output.mkdir()
        marker = self.output / "keep.txt"
        marker.write_text("keep")
        with self.assertRaises(FileExistsError):
            create_report(self.report, self.budget, self.output)
        self.assertEqual(marker.read_text(), "keep")

    def test_invalid_schema_does_not_write_partial_output(self) -> None:
        for changed in [{**self.report, "unreviewed": "not accepted"}, {**self.report, "findings": [{"label": "Guaranteed", "text": "No"}]}]:
            with self.assertRaises(ValueError):
                create_report(changed, self.budget, self.output)
            self.assertFalse(self.output.exists())

    def test_render_does_not_change_inputs(self) -> None:
        before = copy.deepcopy((self.report, self.budget))
        render_report(self.report, self.budget)
        self.assertEqual((self.report, self.budget), before)
