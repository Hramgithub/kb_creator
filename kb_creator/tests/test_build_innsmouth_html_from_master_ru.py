"""Real-input regression for accepted MASTER_RU -> self-contained HTML."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile

import pytest


KB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = KB_ROOT / "scripts" / "build_innsmouth_html_from_master_ru.py"
RU_ROOT = KB_ROOT / "inputs" / "innsmouth" / "master_ru" / "accepted_20260830_r2"
EN_ROOT = KB_ROOT / "inputs" / "innsmouth" / "master_en" / "accepted_20260830_r2"
TERMINOLOGY_REGISTRY = (
    KB_ROOT.parent
    / "CoC"
    / "Project_Reference"
    / "Terminology"
    / "CoC_Terminology_Decisions.csv"
)


def load_script():
    spec = importlib.util.spec_from_file_location("build_innsmouth_html_from_master_ru", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_script()


def test_innsmouth_html_uses_shared_system_registry() -> None:
    assert BUILD.DEFAULT_TERMINOLOGY_REGISTRY.resolve() == TERMINOLOGY_REGISTRY.resolve()


def test_real_accepted_master_ru_builds_self_contained_html() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "candidate"
        result = BUILD.build(RU_ROOT, EN_ROOT, TERMINOLOGY_REGISTRY, output)

        assert result["state"] == "INNSMOUTH_MASTER_RU_HTML_CANDIDATE_BUILT"
        assert result["source_copy"]["sha256"] == BUILD.freeze_ru.PROMOTED_MASTER_RU_SHA256
        assert result["assets"]["count"] == 32
        assert result["assets"]["verified_decodable"] == 32
        assert result["assets"]["formats"] == {"JPEG": 31, "PNG": 1}
        assert result["html"]["counts"]["stable_anchors"] == 52
        assert result["html"]["counts"]["tables"] == 51
        assert result["html"]["counts"]["image_refs"] == 32
        assert result["html"]["counts"]["internal_fragments"] == 86
        assert result["html"]["counts"]["broken_fragments"] == 0
        assert result["html"]["counts"]["missing_assets"] == 0
        assert result["html"]["counts"]["unused_assets"] == 0
        assert result["html"]["counts"]["statblock_cards"] == 22
        assert result["html"]["counts"]["full_width_figures"] == 11
        assert result["html"]["counts"]["inline_half_figures"] == 21
        assert result["html"]["counts"]["inline_owner_bindings"] == 21
        assert result["html"]["counts"]["figure_captions"] == 12
        assert result["html"]["counts"]["source_toc_groups"] == 11
        assert result["html"]["counts"]["title_pages"] == 1
        assert result["html"]["counts"]["title_overlays"] == 1
        assert result["html"]["counts"]["credits_sections"] == 0
        assert result["html"]["counts"]["letter_seal_refs"] == 0
        assert result["positive_content_audit"]["status"] == "pass"
        assert result["positive_content_audit"]["findings"] == []
        assert (output / BUILD.OUTPUT_HTML_NAME).is_file()
        assert len(list((output / "assets").iterdir())) == 32

        with pytest.raises(ValueError, match="refusing to overwrite"):
            BUILD.build(RU_ROOT, EN_ROOT, TERMINOLOGY_REGISTRY, output)
