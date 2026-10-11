"""Focused tests for the separated RECONSTRUCTED_EN -> MASTER_EN projection."""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import re
import sys
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_innsmouth_master_en.py"
ACCEPTED_MASTER_EN = (
    Path(__file__).resolve().parents[1]
    / "inputs"
    / "innsmouth"
    / "master_en"
    / "accepted_20260830_r2"
    / "MASTER_EN.md"
)
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("innsmouth_master_en", SCRIPT)
assert SPEC and SPEC.loader
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)


class MasterEnProjectionTests(unittest.TestCase):
    def test_rejects_wrong_reconstructed_identity(self) -> None:
        with mock.patch.object(Path, "is_file", return_value=True), mock.patch.object(
            Path, "read_bytes", return_value=b"wrong"
        ):
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                MASTER.verify_reconstructed(Path("RECONSTRUCTED_EN.md"))

    def test_rejects_wrong_reconstructed_qa_identity(self) -> None:
        with mock.patch.object(MASTER, "verify_reconstructed", return_value="markdown"), mock.patch.object(
            Path, "is_file", return_value=True
        ), mock.patch.object(Path, "read_bytes", return_value=b"wrong"):
            with self.assertRaisesRegex(ValueError, "QA identity mismatch"):
                MASTER.verify_reconstructed_package(
                    Path("RECONSTRUCTED_EN.md"),
                    Path("RECONSTRUCTED_EN.qa.json"),
                    Path("images"),
                )

    def test_reader_art_allowlist_is_exact(self) -> None:
        self.assertEqual(len(MASTER.RETAINED_ASSETS), 33)
        self.assertEqual(len(MASTER.ANCHOR_TARGETS), 52)
        self.assertEqual(len(MASTER.TOC_ENTRIES), 34)
        self.assertEqual(len(MASTER.SECTION_GROUPS), 11)
        self.assertIn(
            "497dc1045aa4f06805e86552e2de0207bf15bfbc65856c747e7a88d375212a67.jpg",
            MASTER.RETAINED_ASSETS,
        )
        self.assertNotIn(MASTER.EXCLUDED_LETTER_SEAL_ASSET, MASTER.RETAINED_ASSETS)
        self.assertIn(MASTER.reconstructed.SOURCE_COVER_ASSET, MASTER.RETAINED_ASSETS)

    def test_all_heading_anchors_except_documented_body_target_bind_to_headings(self) -> None:
        for anchor, _page_index, prefix in MASTER.ANCHOR_TARGETS:
            if anchor.startswith("nri-h-") and anchor not in MASTER.BODY_HEADING_EXCEPTIONS:
                self.assertTrue(prefix.startswith("#"), anchor)
        self.assertEqual(
            MASTER.BODY_HEADING_EXCEPTIONS,
            frozenset({"nri-h-e1e4abee7d665d664b579640"}),
        )

    def test_semantic_anchor_alignment_rejects_anchor_inside_body(self) -> None:
        with self.assertRaisesRegex(ValueError, "not aligned to a heading"):
            MASTER.validate_semantic_anchor_alignment(
                '<a id="nri-h-example"></a>\nBody paragraph\n'
            )

    def test_real_publication_base_when_inputs_are_available(self) -> None:
        reconstructed_raw = os.environ.get("NRI_INNSMOUTH_RECONSTRUCTED_EN")
        packet5b_raw = os.environ.get("NRI_INNSMOUTH_PACKET5B")
        if not reconstructed_raw or not packet5b_raw:
            self.skipTest("RECONSTRUCTED_EN and Packet 5b oracle are required")
        source = MASTER.verify_reconstructed(Path(reconstructed_raw))
        first = MASTER.build_publication_base(source)
        second = MASTER.build_publication_base(source)
        self.assertEqual(first, second)
        markdown, qa = first
        self.assertEqual(qa["counts"], {"page_markers": 43, "image_links": 33, "tables": 51, "headings": 155})
        self.assertNotIn("<!-- mineru-page: 43 -->", markdown)
        self.assertIn("assets/497dc1045aa4f06805e86552e2de0207bf15bfbc65856c747e7a88d375212a67.jpg", markdown)
        self.assertNotIn(MASTER.EXCLUDED_LETTER_SEAL_ASSET, markdown)

        packet5b = Path(packet5b_raw).read_text(encoding="utf-8")

        def normalized(value: str) -> str:
            value = re.sub(r"<!--[\s\S]*?-->", " ", value)
            return re.sub(r"\s+", " ", value).strip()

        self.assertEqual(normalized(markdown), normalized(packet5b))
        self.assertRegex(hashlib.sha256(markdown.encode("utf-8")).hexdigest(), r"^[0-9a-f]{64}$")

    def test_real_reader_master_matches_accepted_nonblank_lines(self) -> None:
        reconstructed_raw = os.environ.get("NRI_INNSMOUTH_RECONSTRUCTED_EN")
        if not reconstructed_raw:
            self.skipTest("RECONSTRUCTED_EN is required")
        source_path = Path(reconstructed_raw)
        source, source_identity = MASTER.verify_reconstructed_package(
            source_path,
            source_path.parent / "RECONSTRUCTED_EN.qa.json",
            source_path.parent / "images",
        )
        self.assertEqual(source_identity["markdown"]["path"], "RECONSTRUCTED_EN.md")
        self.assertEqual(source_identity["qa"]["path"], "RECONSTRUCTED_EN.qa.json")
        self.assertEqual(source_identity["asset_inventory"]["asset_count"], 136)
        self.assertNotIn(str(source_path.parent), str(source_identity))
        first = MASTER.build_master_en(source)
        second = MASTER.build_master_en(source)
        self.assertEqual(first, second)
        markdown, qa = first
        self.assertEqual(
            qa["final_counts"],
            {
                "page_markers": 0,
                "table_evidence_comments": 0,
                "image_links": 33,
                "tables": 51,
                "headings": 153,
                "anchors": 52,
                "fragments": 86,
                "broken_fragments": 0,
                "ordinary_page_links": 33,
                "external_page_references": 3,
            },
        )
        self.assertNotIn("<!-- mineru-page:", markdown)
        self.assertNotIn("<!-- table-evidence:", markdown)
        self.assertNotIn("## CONTENT WARNINGS", markdown)
        self.assertIn(
            "to Zadok Allen (The Fire Station, [link](#nri-h-1b70234c4ece0af6255492e8)).",
            markdown,
        )
        self.assertNotIn(
            "### OFFICE OF THE VICE CHANCELLOR MISKATONIC UNIVERSITY",
            markdown,
        )
        self.assertNotIn(
            "Wanted to drop in and see you, but your crew weren't thrilled",
            markdown.partition("## HANDOUTS\n")[0],
        )
        self.assertEqual(
            markdown.count("[**Handout 1-a**](#nri-h-94205138fca7aa22510e0aca)"),
            2,
        )
        self.assertEqual(
            markdown.count("[**Handout 1-b**](#nri-h-f8e3b2764c3b8f24c4c83bfa)"),
            1,
        )
        self.assertEqual(
            markdown.count("[**Handout 2**](#nri-h-1701b4c74a5e58fac76c83d3)"),
            5,
        )
        self.assertIn(
            "**Keeper note:** LLFRFL are directions",
            markdown.partition("## HANDOUTS\n")[2],
        )
        appendix = markdown.partition("## HANDOUTS\n")[2]
        self.assertEqual(appendix.count("### Handout 2: note"), 1)
        self.assertEqual(appendix.count("Hey G,"), 1)
        self.assertNotIn("**Handout 2**: note", appendix)
        for name in (
            MASTER.EXCLUDED_LETTER_SEAL_ASSET,
            "0ee550370e17bfe37128a9d44b271899b8e535c3e0847d1a41a6c32b8c5e4617.jpg",
            "eca0dbf63145cd539f47da6691e5e1675c906be4372d97d73ca9d85efe7b5a6d.jpg",
            "eda68c6d95d2e6dc230faf0f05301f82f282c152251c8ae936f2879d1424d49a.jpg",
            "f442a32a6901a3299a2c4ab5d06ff239bb2ee02cc6b55581b02e8eec7c708da9.jpg",
        ):
            self.assertNotIn(name, markdown)

        accepted = ACCEPTED_MASTER_EN.read_text(encoding="utf-8")
        accepted, _ = MASTER.strip_technical_comments(accepted)

        def nonblank_lines(value: str) -> list[str]:
            return [line.rstrip() for line in value.splitlines() if line.strip()]

        self.assertEqual(nonblank_lines(markdown), nonblank_lines(accepted))
        inventory = MASTER.retained_asset_inventory(source_path.parent / "images")
        self.assertEqual(inventory["asset_count"], 33)
        self.assertEqual(
            inventory["inventory_sha256"], MASTER.RETAINED_ASSET_INVENTORY_SHA256
        )


if __name__ == "__main__":
    unittest.main()
