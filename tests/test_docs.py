import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_authored_markdown_file_links_resolve(self) -> None:
        sources = [ROOT / "README.md", ROOT / "AGENTS.md", *ROOT.joinpath("docs").rglob("*.md"), *ROOT.joinpath("fleet").rglob("*.md")]
        for source in sources:
            for match in re.finditer(r"\[[^\]]*\]\(([^\s)]+)\)", source.read_text()):
                href = urlsplit(match.group(1))
                if href.scheme or not href.path:
                    continue
                target = source.parent / unquote(href.path)
                self.assertTrue(target.is_file() or target.is_dir(), f"{source.relative_to(ROOT)}: {href.path}")
