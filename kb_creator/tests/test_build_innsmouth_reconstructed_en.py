"""Focused tests for the Innsmouth RECONSTRUCTED_EN base builder."""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_innsmouth_reconstructed_en.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("innsmouth_reconstructed_en", SCRIPT)
assert SPEC and SPEC.loader
MASTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MASTER)


class MasterHelpersTests(unittest.TestCase):
    def test_split_pages_preserves_original_indices(self) -> None:
        preamble, pages = MASTER.split_pages(
            "<!-- trial -->\n\n<!-- mineru-page: 0 -->\nCover\n"
            "<!-- mineru-page: 1 -->\nText\n"
        )

        self.assertIn("trial", preamble)
        self.assertEqual(sorted(pages), [0, 1])
        self.assertIn("Cover", pages[0])
        self.assertIn("Text", pages[1])

    def test_split_pages_retains_backmatter_page_indices(self) -> None:
        markdown = "".join(
            f"<!-- mineru-page: {index} -->\npage {index}\n"
            for index in range(46)
        )

        _, pages = MASTER.split_pages(markdown)

        self.assertEqual(sorted(pages), list(range(46)))
        self.assertIn("page 43", pages[43])
        self.assertIn("page 45", pages[45])

    def test_promotes_card_identity_and_standard_sections(self) -> None:
        page = (
            "![](images/entity.jpg)\n\nDeep One\n\n<table>x</table>\n\n"
            "![](images/combat.jpg)\n\nCombat\nAttacks per round: 2\n\n<table>y</table>\n\n"
            "## Sanity\n"
        )

        result = MASTER.promote_card_captions(page)

        self.assertIn("### Deep One", result)
        self.assertIn("#### Combat\nAttacks per round: 2", result)
        self.assertIn("#### Sanity", result)

    def test_preserves_age_line_below_investigator_heading(self) -> None:
        page = (
            "![](images/ian.jpg)\n\nIAN TORRES\n"
            "Age: 23 Occupation: Football Player / Student\n\n<table>x</table>\n"
        )

        result = MASTER.promote_card_captions(page)

        self.assertIn("### IAN TORRES\n\nAge: 23 Occupation", result)

    def test_replace_once_rejects_ambiguous_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected one exact match"):
            MASTER.replace_once("x x", "x", "y", "fixture")

    def test_replace_once_applies_confirmed_ocr_correction(self) -> None:
        self.assertEqual(
            MASTER.replace_once("CALL OF\nTHULHU", "THULHU", "CTHULHU", "logo"),
            "CALL OF\nCTHULHU",
        )

    def test_table_line_break_uses_html_break_without_changing_value(self) -> None:
        value = MASTER.replace_once(
            "damage 10D6A Star Spawn may attack",
            "damage 10D6A Star Spawn may attack",
            "damage 10D6<br>A Star Spawn may attack",
            "star spawn",
        )

        self.assertEqual(value, "damage 10D6<br>A Star Spawn may attack")

    def test_timeline_spacing_correction_is_exact(self) -> None:
        self.assertEqual(
            MASTER.replace_once(
                "Evening of the 2ndday",
                "2ndday",
                "2nd day",
                "timeline",
            ),
            "Evening of the 2nd day",
        )

    def test_recovered_asset_identity_is_pinned(self) -> None:
        self.assertEqual(len(MASTER.RECOVERED_ASSETS), 6)
        for name, digest in MASTER.RECOVERED_ASSETS.items():
            self.assertTrue(name.endswith(".jpg"))
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
        self.assertRegex(MASTER.SOURCE_CANDIDATE_SHA256, r"^[0-9a-f]{64}$")
        self.assertRegex(MASTER.PDF_CONTROL_SHA256, r"^[0-9a-f]{64}$")
        self.assertRegex(MASTER.PAGE19_ASSET_SHA256, r"^[0-9a-f]{64}$")

    def test_rejects_unexpected_retained_source_identity(self) -> None:
        with mock.patch.object(MASTER, "sha256", return_value="0" * 64):
            with self.assertRaisesRegex(ValueError, "source candidate hash mismatch"):
                MASTER.verify_source_candidate(Path(__file__))

    def test_real_full_source_reconstruction_when_inputs_are_available(self) -> None:
        reading_raw = os.environ.get("NRI_INNSMOUTH_READING_CANDIDATE")
        pdf_raw = os.environ.get("NRI_INNSMOUTH_SOURCE_PDF")
        if not reading_raw or not pdf_raw:
            self.skipTest(
                "NRI_INNSMOUTH_READING_CANDIDATE and NRI_INNSMOUTH_SOURCE_PDF are required"
            )
        reading = Path(reading_raw)
        source_pdf = Path(pdf_raw)

        self.assertEqual(MASTER.verify_source_candidate(reading), MASTER.SOURCE_CANDIDATE_SHA256)
        self.assertEqual(MASTER.sha256(source_pdf), MASTER.PDF_CONTROL_SHA256)
        source = reading.read_text(encoding="utf-8")
        first = MASTER.build_reconstructed_en(source)
        second = MASTER.build_reconstructed_en(source)

        self.assertEqual(first, second)
        markdown, qa = first
        self.assertEqual(
            hashlib.sha256(markdown.encode("utf-8")).hexdigest().upper(),
            "72CF965DF27C28D5D3927867E0A08C8655F5A7A117E108716FA84521649A8F13",
        )
        self.assertEqual(
            qa["counts"],
            {
                "page_markers": 46,
                "first_page": 0,
                "last_page": 45,
                "image_links": 135,
                "tables": 53,
                "headings": 169,
                "table_evidence_comments": 0,
            },
        )
        self.assertEqual(qa["excluded_page_indices"], [])
        self.assertEqual([row["page_index"] for row in qa["page_inventory"]], list(range(46)))
        self.assertIn("<!-- mineru-page: 43 -->", markdown)
        self.assertIn("<!-- mineru-page: 45 -->", markdown)
        self.assertIn("<!-- mineru-page: 0 -->\nTHE\n\n# THE INNSMOUTH TERROR", markdown)
        self.assertNotRegex(markdown, r"\]\(#nri-")

    def test_real_asset_materialization_when_inputs_are_available(self) -> None:
        reading_raw = os.environ.get("NRI_INNSMOUTH_READING_CANDIDATE")
        reading_assets_raw = os.environ.get("NRI_INNSMOUTH_READING_ASSETS")
        ocr_assets_raw = os.environ.get("NRI_INNSMOUTH_OCR_ASSETS")
        pdf_raw = os.environ.get("NRI_INNSMOUTH_SOURCE_PDF")
        if not all((reading_raw, reading_assets_raw, ocr_assets_raw, pdf_raw)):
            self.skipTest("real reading/OCR/PDF asset inputs are required")
        source = Path(reading_raw).read_text(encoding="utf-8")
        markdown, _ = MASTER.build_reconstructed_en(source)
        source_links = MASTER.IMAGE_LINK.findall(source)
        final_links = MASTER.IMAGE_LINK.findall(markdown)

        with tempfile.TemporaryDirectory() as temp:
            output_images = Path(temp) / "images"
            result = MASTER.copy_reading_assets(
                source_links, final_links, Path(reading_assets_raw), output_images
            )
            MASTER.recover_assets(Path(ocr_assets_raw), output_images)
            MASTER.recover_page19_pdf_asset(Path(pdf_raw), output_images)
            inventory = MASTER.asset_inventory(final_links, output_images)

        self.assertEqual(result["copied_asset_count"], 128)
        self.assertEqual(inventory["link_count"], 135)
        self.assertEqual(inventory["asset_count"], 135)
        self.assertEqual(inventory["inventory_sha256"], MASTER.FINAL_ASSET_INVENTORY_SHA256)

    def test_reader_text_matches_packet5b_except_declared_publication_differences(self) -> None:
        reading_raw = os.environ.get("NRI_INNSMOUTH_READING_CANDIDATE")
        packet5b_raw = os.environ.get("NRI_INNSMOUTH_PACKET5B")
        if not reading_raw or not packet5b_raw:
            self.skipTest("real reading candidate and Packet 5b oracle are required")
        reconstructed, _ = MASTER.build_reconstructed_en(
            Path(reading_raw).read_text(encoding="utf-8")
        )
        packet5b = Path(packet5b_raw).read_text(encoding="utf-8")
        reconstructed_pages = MASTER.split_pages(reconstructed)[1]
        packet5b_pages = MASTER.split_pages(packet5b)[1]

        def reader_text(value: str) -> str:
            value = re.sub(r"<!--[\s\S]*?-->", " ", value)
            value = re.sub(r"!\[\]\((?:images|assets)/[^)]+\)", " ", value)
            value = re.sub(r"CALL OF\s+CTHULHU\s+Miskatonic Repository", " ", value)
            return re.sub(r"\s+", " ", value).strip()

        self.assertEqual(
            [reader_text(reconstructed_pages[index]) for index in range(1, 43)],
            [reader_text(packet5b_pages[index]) for index in range(1, 43)],
        )


if __name__ == "__main__":
    unittest.main()
