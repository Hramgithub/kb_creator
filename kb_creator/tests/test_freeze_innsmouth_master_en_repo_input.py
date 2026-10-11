"""Tests for reproducible promotion of an explicitly accepted MASTER_EN."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "freeze_innsmouth_master_en_repo_input.py"
)
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("innsmouth_master_en_freeze", SCRIPT)
assert SPEC and SPEC.loader
FREEZE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FREEZE)

MASTER_SHA256 = "DFDF2C0DAA1B5B642C217B4B5C52732070F4CC66582D40A98A77C0E48F2AE405"
QA_SHA256 = "989316A6C148104B28A05626B753DF323FF5595BA5BBE3D1F48F7DF6DBCEBC18"


class MasterEnFreezeTests(unittest.TestCase):
    def test_requires_explicit_sha256(self) -> None:
        with self.assertRaisesRegex(ValueError, "explicit SHA-256"):
            FREEZE.inspect_candidate(Path("missing"), "latest", QA_SHA256)

    def test_acceptance_date_is_strict(self) -> None:
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            FREEZE.acceptance_manifest(
                {
                    "source_reconstructed_en": {},
                    "markdown": {},
                    "qa": {},
                    "asset_inventory": {"asset_count": 32, "inventory_sha256": "x"},
                    "counts": {},
                },
                "today",
            )

    def test_rejects_tampered_stage_b_provenance(self) -> None:
        tampered = {
            **FREEZE.EXPECTED_SOURCE_RECONSTRUCTED_EN,
            "asset_inventory": {
                "asset_count": 135,
                "inventory_sha256": "0" * 64,
            },
        }
        with self.assertRaisesRegex(ValueError, "canonical Stage B provenance mismatch"):
            FREEZE.verify_source_reconstructed_identity(tampered)

    def test_accepts_only_exact_stage_b_provenance(self) -> None:
        self.assertEqual(
            FREEZE.verify_source_reconstructed_identity(
                FREEZE.EXPECTED_SOURCE_RECONSTRUCTED_EN
            ),
            FREEZE.EXPECTED_SOURCE_RECONSTRUCTED_EN,
        )

    def test_real_candidate_preflight_and_temp_promotion(self) -> None:
        candidate_raw = os.environ.get("NRI_INNSMOUTH_MASTER_EN_CANDIDATE")
        if not candidate_raw:
            self.skipTest("strict-pipeline MASTER_EN candidate is required")
        candidate = Path(candidate_raw)
        report = FREEZE.inspect_candidate(candidate, MASTER_SHA256, QA_SHA256)
        self.assertEqual(report["state"], "MASTER_EN_CANDIDATE_PREFLIGHT_OK")
        self.assertEqual(report["asset_inventory"]["asset_count"], 32)
        self.assertEqual(report["source_reconstructed_en"]["asset_inventory"]["asset_count"], 135)

        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "accepted_master_en"
            promoted = FREEZE.promote(
                candidate,
                target,
                MASTER_SHA256,
                QA_SHA256,
                "2026-08-30",
            )
            self.assertEqual(promoted["state"], "ACCEPTED_MASTER_EN_REPO_INPUT_VERIFIED")
            self.assertEqual(len(list((target / "assets").iterdir())), 32)
            manifest = (target / "MASTER_EN.acceptance.json").read_text(encoding="utf-8")
            self.assertNotIn("D:\\\\NRI", manifest)
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                FREEZE.promote(
                    candidate,
                    target,
                    MASTER_SHA256,
                    QA_SHA256,
                    "2026-08-30",
                )


if __name__ == "__main__":
    unittest.main()
