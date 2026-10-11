"""Focused tests for reproducible MASTER_RU terminology sync and promotion."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "freeze_innsmouth_master_ru_repo_input.py"
RU = ROOT / "working" / "innsmouth_direct_master_ru" / "MASTER_RU.md"
EN_ROOT = ROOT / "inputs" / "innsmouth" / "master_en" / "accepted_20260830_r2"
ASSETS = EN_ROOT / "assets"
TERMINOLOGY_REGISTRY = (
    ROOT.parent
    / "CoC"
    / "Project_Reference"
    / "Terminology"
    / "CoC_Terminology_Decisions.csv"
)


def load_script():
    spec = importlib.util.spec_from_file_location("freeze_innsmouth_master_ru_repo_input", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FREEZE = load_script()


def test_current_system_registry_verifies_historical_accepted_package() -> None:
    registry = FREEZE.verify_terminology_registry(TERMINOLOGY_REGISTRY)
    accepted = FREEZE.verify_promoted(
        ROOT / "inputs" / "innsmouth" / "master_ru" / "accepted_20260830_r2",
        TERMINOLOGY_REGISTRY,
        EN_ROOT,
    )
    assert accepted["terminology_registry"] == registry
    assert accepted["glossary"] == FREEZE.LEGACY_GLOSSARY_PROVENANCE


def test_real_candidate_preflight_is_exact_and_glossary_synced() -> None:
    report, output = FREEZE.inspect_candidate(
        RU,
        ASSETS,
        TERMINOLOGY_REGISTRY,
        EN_ROOT,
        FREEZE.ACCEPTED_SOURCE_MASTER_RU_SHA256,
    )
    assert report["state"] == "MASTER_RU_PROMOTION_PREFLIGHT_OK"
    assert report["markdown"] == {
        "path": "MASTER_RU.md",
        "byte_count": FREEZE.PROMOTED_MASTER_RU_BYTES,
        "sha256": FREEZE.PROMOTED_MASTER_RU_SHA256,
    }
    assert report["asset_inventory"]["asset_count"] == 32
    assert report["counts"] == {
        "image_links": 32,
        "tables": 51,
        "headings": 152,
        "anchors": 52,
        "fragments": 86,
        "broken_fragments": 0,
    }
    text = output.decode("utf-8")
    assert "Чтения следов" in text
    assert "Работа в библиотеке" in text
    assert "Внимание" in text
    assert "Средства" in text
    assert "<!-- mineru-page:" not in text
    assert "<!-- table-evidence:" not in text
    assert "ПРЕДУПРЕЖДЕНИЯ О СОДЕРЖАНИИ" not in text
    assert "Не предназначено для перепродажи" not in text
    assert report["front_matter_projection"] == {
        "source_cover_links_added": 1,
        "credits_sections_suppressed": 1,
        "content_warning_blocks_suppressed": 1,
    }
    for anchor, heading in FREEZE.RU_HEADING_TARGETS:
        assert f'<a id="{anchor}"></a>\n{heading}\n' in text
    assert report["semantic_anchor_realignments"] == dict(FREEZE.RU_HEADING_TARGETS)
    assert report["handout_projection"] == {
        "body_handout_duplicates_suppressed": 2,
        "keeper_notes_relocated_to_appendix": 1,
        "appendix_handout_duplicates_suppressed": 1,
        "body_handout_links": 8,
        "appendix_handout_anchors_added": 2,
        "decorative_handout_assets_suppressed": 5,
    }
    body, _boundary, appendix = text.partition("## РАЗДАТОЧНЫЕ МАТЕРИАЛЫ\n")
    assert "### КАБИНЕТ ВИЦЕ-КАНЦЛЕРА МИСКАТОНИКСКОГО УНИВЕРСИТЕТА" not in body
    assert "Хотел заглянуть и повидаться, но твоя группа не обрадовалась" not in body
    assert body.count("#nri-h-94205138fca7aa22510e0aca") == 2
    assert body.count("#nri-h-f8e3b2764c3b8f24c4c83bfa") == 1
    assert body.count("#nri-h-1701b4c74a5e58fac76c83d3") == 5
    assert appendix.count("**Заметка Хранителя:** LLFRFL — указания") == 1
    assert appendix.count("### Раздаточный материал 2: записка") == 1
    assert appendix.count("Привет, G,") == 1
    assert "**Раздаточный материал 2**: записка" not in appendix


def test_promote_verify_and_refuse_overwrite() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        target = Path(temporary) / "accepted_20260830"
        promoted = FREEZE.promote(
            RU,
            ASSETS,
            TERMINOLOGY_REGISTRY,
            EN_ROOT,
            target,
            FREEZE.ACCEPTED_SOURCE_MASTER_RU_SHA256,
            "2026-08-30",
        )
        assert promoted["state"] == "ACCEPTED_MASTER_RU_REPO_INPUT_VERIFIED"
        assert len(list((target / "assets").iterdir())) == 32
        verified = FREEZE.verify_promoted(target, TERMINOLOGY_REGISTRY, EN_ROOT)
        assert verified == promoted
        manifest_path = target / "MASTER_RU.acceptance.json"
        manifest = json.loads(manifest_path.read_bytes())
        manifest["accepted_on"] = "2099-01-01"
        manifest_path.write_bytes(FREEZE.canonical_json(manifest))
        with pytest.raises(ValueError, match="manifest identity mismatch"):
            FREEZE.verify_promoted(target, TERMINOLOGY_REGISTRY, EN_ROOT)
        manifest["accepted_on"] = "2026-08-30"
        manifest_path.write_bytes(FREEZE.canonical_json(manifest))
        with pytest.raises(ValueError, match="refusing to overwrite"):
            FREEZE.promote(
                RU,
                ASSETS,
                TERMINOLOGY_REGISTRY,
                EN_ROOT,
                target,
                FREEZE.ACCEPTED_SOURCE_MASTER_RU_SHA256,
                "2026-08-30",
            )


def test_reject_wrong_candidate_identity() -> None:
    with pytest.raises(ValueError, match="not the accepted candidate identity"):
        FREEZE.inspect_candidate(
            RU, ASSETS, TERMINOLOGY_REGISTRY, EN_ROOT, "0" * 64
        )


def test_reject_technical_comments_wrong_counts_and_broken_fragment() -> None:
    source = RU.read_text(encoding="utf-8")
    aligned, _anchors = FREEZE.realign_semantic_anchors(source)
    synchronized, _counts = FREEZE.synchronize_terminology(aligned)
    synchronized, _front_matter = FREEZE.project_front_matter(synchronized)
    synchronized, _handouts = FREEZE.project_handout_reader_flow(synchronized)
    en = (EN_ROOT / "MASTER_EN.md").read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="technical reconstruction comments"):
        FREEZE.validate_ru_markdown("<!-- table-evidence: x -->\n" + synchronized, en)
    with pytest.raises(ValueError, match="ordered image references"):
        FREEZE.validate_ru_markdown(synchronized.replace("![](", "[image](", 1), en)
    with pytest.raises(ValueError, match="structural counts mismatch"):
        FREEZE.validate_ru_markdown(synchronized.replace("<table>", "<div>", 1), en)
    broken = synchronized.replace("#nri-h-", "#missing-nri-h-", 1)
    with pytest.raises(ValueError, match="structural counts mismatch"):
        FREEZE.validate_ru_markdown(broken, en)


def test_reject_missing_or_changed_asset() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        copied = Path(temporary) / "assets"
        shutil.copytree(ASSETS, copied)
        first = sorted(copied.iterdir())[0]
        first.unlink()
        with pytest.raises(ValueError, match="exactly 33 canonical files"):
            FREEZE.inspect_candidate(
                RU,
                copied,
                TERMINOLOGY_REGISTRY,
                EN_ROOT,
                FREEZE.ACCEPTED_SOURCE_MASTER_RU_SHA256,
            )
    with tempfile.TemporaryDirectory() as temporary:
        copied = Path(temporary) / "assets"
        shutil.copytree(ASSETS, copied)
        (copied / "unexpected.txt").write_text("extra", encoding="utf-8")
        with pytest.raises(ValueError, match="exactly 33 canonical files"):
            FREEZE.inspect_candidate(
                RU,
                copied,
                TERMINOLOGY_REGISTRY,
                EN_ROOT,
                FREEZE.ACCEPTED_SOURCE_MASTER_RU_SHA256,
            )
    with tempfile.TemporaryDirectory() as temporary:
        copied = Path(temporary) / "assets"
        shutil.copytree(ASSETS, copied)
        first = sorted(copied.iterdir())[0]
        first.write_bytes(first.read_bytes() + b"tamper")
        with pytest.raises(ValueError, match="retained asset inventory mismatch"):
            FREEZE.inspect_candidate(
                RU,
                copied,
                TERMINOLOGY_REGISTRY,
                EN_ROOT,
                FREEZE.ACCEPTED_SOURCE_MASTER_RU_SHA256,
            )


def test_reject_registry_copy() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        altered = Path(temporary) / "terminology.csv"
        altered.write_bytes(TERMINOLOGY_REGISTRY.read_bytes())
        with pytest.raises(ValueError, match="canonical CoC system registry"):
            FREEZE.verify_terminology_registry(altered)


def test_reject_obsolete_terminology() -> None:
    source = RU.read_text(encoding="utf-8")
    aligned, _anchors = FREEZE.realign_semantic_anchors(source)
    synchronized, _counts = FREEZE.synchronize_terminology(aligned)
    synchronized, _front_matter = FREEZE.project_front_matter(synchronized)
    synchronized, _handouts = FREEZE.project_handout_reader_flow(synchronized)
    en = (EN_ROOT / "MASTER_EN.md").read_text(encoding="utf-8")
    drifted = synchronized.replace("Чтения следов", "Слежение", 1)
    with pytest.raises(ValueError, match="obsolete skill terminology"):
        FREEZE.validate_ru_markdown(drifted, en)
