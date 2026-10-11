"""Small PDF-derived normal DOCX guard fixture; no copyrighted source."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import pytest
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from lxml import etree

from kb_creator.pipeline.five_step_docx import (_default_config, build_docx_package,
                                                  verify_docx_package, FiveStepDocxError)
from kb_creator.pipeline.coc_glossary import HEADER
from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline.reader_fidelity import PLAN_SCHEMA
from kb_creator.pipeline.source_graphics import (REVIEW_SCHEMA, build_inventory,
                                                  validate_produced_inventory)
from kb_creator.tests.test_edition_projection_contract import _row, _selector


def _write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *,
             master_image: bool = True) -> tuple[Path, Path, Path, Path]:
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        pytest.skip("pdftoppm runtime unavailable")
    master_root = tmp_path / "master"
    (master_root / "assets").mkdir(parents=True)
    map_path = master_root / "assets" / "map.png"
    Image.new("RGB", (24, 16), "black").save(map_path)
    markdown = ('<!-- source-page-001 -->\n\n# Synthetic\n\n' +
                ('![Map](assets/map.png)\n' if master_image else 'A reviewed source scene follows.\n'))
    master = master_root / "MASTER_RU.md"
    master.write_text(markdown, encoding="utf-8")
    _write(master_root / "ASSET_MANIFEST.json", {"assets": [{"path": "assets/map.png", **file_identity(map_path)}]})
    for name in ("MASTER_RU.manifest.json", "PROOFREAD_LEDGER.json", "INVENTORY.json"):
        _write(master_root / name, {})
    semantic = master_root / "semantic_context"
    semantic.mkdir()
    _write(semantic / "source.json", {"role": "source"})
    unit = {"unit_id": "unit-1", "source_hash": "A" * 64,
            "parent_unit_id": None, "part_index": None, "part_count": None,
            "ru_text": markdown.strip(), "ru_sha256": _sha_text(markdown.strip())}
    projection = {"schema": "kb_creator.five_step_ru_projection.v3",
                  "master_en": {"path": "evidence/MASTER_EN.md", "bytes": 1, "sha256": "0" * 64},
                  "master_ru": {"path": "MASTER_RU.md", **file_identity(master)},
                  "unit_order": ["unit-1"], "units": [unit], "spans": []}
    projection["projection_sha256"] = _sha_text(json.dumps(projection, ensure_ascii=False,
                                                       sort_keys=True, separators=(",", ":")))
    projection_path = semantic / "RU_PROJECTION.json"
    _write(projection_path, projection)
    monkeypatch.setattr("kb_creator.pipeline.five_step_language.verify_language_result",
                        lambda value: {"state": "verified"})
    source = tmp_path / "synthetic-source.pdf"
    pdf = canvas.Canvas(str(source), pagesize=(288, 360), pageCompression=0)
    pdf.drawString(20, 330, "Synthetic")
    pdf.drawImage(ImageReader(str(map_path)), 20, 260, width=96, height=64)
    pdf.showPage()
    pdf.save()
    guard = tmp_path / "guard"
    guard.mkdir()
    inventory_path = build_inventory(source, Path(renderer), guard / "inventory")
    inventory = validate_produced_inventory(inventory_path, source_pdf=source)
    selected = guard / "selected-map.png"
    shutil.copyfile(map_path, selected)
    graphic = {"graphic_id": "map-1", "page": 1, "category": "map", "owner": "synthetic",
               "source_region": [20, 36, 116, 100], "occurrence_ids": [],
               "manual_region_id": "map-region", "disposition": "include",
               "rationale": "synthetic source map seen on full page", "decision_reference": "fixture manual review",
               "selected": {"path": selected.name, **file_identity(selected)}}
    review = sealed(REVIEW_SCHEMA, {
        "inventory": {"path": str(inventory_path.resolve()), **file_identity(inventory_path)},
        "source_pdf": inventory["source_pdf"],
        "reviewer": {"role": "independent_page_reviewer", "reference": "synthetic fixture",
                     "time_utc": "2026-01-01T00:00:00Z"},
        "page_reviews": [{"page": 1, "render_sha256": inventory["pages"][0]["render"]["sha256"],
                          "status": "reviewed_graphics", "graphic_ids": ["map-1"],
                          "residual_issues": [], "manual_page_coverage": {
                              "view_sha256": inventory["pages"][0]["render"]["sha256"],
                              "reviewed": True, "regions": [{"region_id": "map-region",
                                  "bbox": [20, 36, 116, 100], "graphic_id": "map-1"}],
                              "remaining_limits": "paint traversal incomplete; manually reviewed page",
                              "reviewer_reference": "synthetic page 1"}}],
        "graphics": [graphic], "technical_occurrences": [], "state": "closed",
    }, digest_key="review_sha256")
    review_path = guard / "SOURCE_GRAPHICS_REVIEW.json"
    _write(review_path, review)
    config = guard / "docx_config.json"
    _write(config, _default_config("Synthetic"))
    registry = guard / "accepted-registry.csv"
    overlay = guard / "accepted-overlay.json"
    registry.write_text(",".join(HEADER) + "\n", encoding="utf-8")
    _write(overlay, {"terms": []})
    options = {"schema": "kb_creator.five_step_reader_options.v1",
               "master_ru": {"path": "MASTER_RU.md", **file_identity(master)},
               "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **file_identity(projection_path)},
               "source_toc": {"state": "absent", "source_pdf_sha256": inventory["source_pdf"]["sha256"],
                              "reason": "reviewed synthetic page contains no TOC"},
               "body_links": [], "asset_choices": [],
               "hit_points": {"presentation": "numeric", "expected_counts": []},
               "display_roles": []}
    options["options_sha256"] = _sha_text(json.dumps(options, ensure_ascii=False,
                                                 sort_keys=True, separators=(",", ":")))
    options_path = guard / "reader_options.json"
    _write(options_path, options)
    plan = sealed(PLAN_SCHEMA, {
        "inventory": {"path": str(inventory_path.resolve()), **file_identity(inventory_path)},
        "review": {"path": str(review_path.resolve()), **file_identity(review_path)},
        "source_pdf": inventory["source_pdf"],
        "master_ru": {"path": str(master.resolve()), **file_identity(master)},
        "projection": {"path": str(projection_path.resolve()), **file_identity(projection_path)},
        "config": {"path": str(config.resolve()), **file_identity(config)},
        "glossary_registry": {"path": str(registry.resolve()), **file_identity(registry)},
        "glossary_overlay": {"path": str(overlay.resolve()), **file_identity(overlay)},
        "policy": {"target_edition": "7e", "edition_applicability": "applicable",
                   "book_id": "synthetic-fixture",
                   "rules_version": "synthetic-review-v1", "reader_profile": "five_step_docx_v3",
                   "review_reference": "full synthetic page and section reviewed"},
        "placements": [{"placement_id": "map-placement-1", "graphic_id": "map-1",
                        "story_id": "synthetic", "anchor": "synthetic", "position": "after",
                        "repeat_ordinal": 0, "selected_sha256": file_identity(selected)["sha256"],
                        "representation": "word_drawing", "master_relation": "in_master" if master_image else "absent_from_master",
                        "route": "retain_exact" if master_image else "reviewed_reader_insertion", "crop": {"left": 0, "top": 0,
                        "right": 0, "bottom": 0, "approved": True},
                        "fit": {"width_emu": 2000000, "height_emu": 1400000},
                        "decision_reference": "synthetic map placement"}],
        "edition_domain": [], "edition_rows": [], "terminology_rows": [], "section_domain": ["synthetic"],
        "section_reviews": [{"section_id": "synthetic", "cards": 0, "prose": 0,
                             "pregens": 0, "checks": 0, "labels": 0, "reviewed": True,
                             "decision_reference": "full synthetic section reviewed", "residual_issues": []}],
        "state": "closed",
    }, digest_key="plan_sha256")
    plan_path = guard / "READER_FIDELITY_PLAN.json"
    _write(plan_path, plan)
    return master_root, config, options_path, plan_path


def test_synthetic_pdf_approved_map_survives_guarded_docx_and_reopened_verifier(tmp_path: Path,
                                                                               monkeypatch: pytest.MonkeyPatch) -> None:
    master, config, options, plan = _fixture(tmp_path, monkeypatch)
    result = build_docx_package(master, tmp_path / "package", title="Synthetic",
                                config=config, reader_options=options, fidelity_plan=plan)
    verified = verify_docx_package(result["manifest_path"].parent)
    assert verified["status"] == "verified_pending_visual_review"
    manifest = json.loads(result["manifest_path"].read_text(encoding="utf-8"))
    assert manifest["schema"] == "kb_creator.five_step_docx_package.v3"
    assert manifest["source_fidelity"]["graphic_projection"] == {"placements": 1, "insertions": 0}
    fidelity = json.loads((result["manifest_path"].parent / "READER_FIDELITY_VERIFICATION.json").read_text(encoding="utf-8"))
    assert fidelity["mechanical_state"] == "closed"
    assert fidelity["semantic_state"] == "needs_output_review"
    with zipfile.ZipFile(result["docx_path"]) as package:
        word = etree.fromstring(package.read("word/document.xml"))
    ns = {"wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"}
    descriptors = word.xpath(".//wp:docPr/@descr", namespaces=ns)
    extents = word.xpath(".//wp:extent", namespaces=ns)
    assert descriptors == ["map-placement-1"]
    assert [(row.get("cx"), row.get("cy")) for row in extents] == [("2000000", "1400000")]
    assert not any(path.suffix.lower() in {".html", ".htm", ".pdf"}
                   for path in result["manifest_path"].parent.rglob("*") if path.is_file())


def test_direct_builder_missing_guard_fails_before_output(tmp_path: Path) -> None:
    with pytest.raises(FiveStepDocxError, match="source-fidelity plan"):
        build_docx_package(tmp_path / "missing-master", tmp_path / "no-output", title="x")
    assert not (tmp_path / "no-output").exists()


def test_source_scene_absent_from_master_is_inserted_only_in_reader_docx(tmp_path: Path,
                                                                         monkeypatch: pytest.MonkeyPatch) -> None:
    master, config, options, plan = _fixture(tmp_path, monkeypatch, master_image=False)
    original_master = (master / "MASTER_RU.md").read_bytes()
    result = build_docx_package(master, tmp_path / "inserted", title="Synthetic",
                                config=config, reader_options=options, fidelity_plan=plan)
    manifest = json.loads(result["manifest_path"].read_text(encoding="utf-8"))
    assert manifest["source_fidelity"]["graphic_projection"] == {"placements": 1, "insertions": 1}
    assert verify_docx_package(result["manifest_path"].parent)["status"] == "verified_pending_visual_review"
    assert (master / "MASTER_RU.md").read_bytes() == original_master


def test_missing_before_master_scene_cannot_be_hidden_by_zero_reader_counts(tmp_path: Path,
                                                                             monkeypatch: pytest.MonkeyPatch) -> None:
    master, config, options, plan_path = _fixture(tmp_path, monkeypatch, master_image=False)
    value = json.loads(plan_path.read_text(encoding="utf-8"))
    value["placements"] = []
    value = sealed(PLAN_SCHEMA, {key: row for key, row in value.items()
                                 if key not in {"schema", "plan_sha256"}}, digest_key="plan_sha256")
    _write(plan_path, value)
    output = tmp_path / "forbidden"
    with pytest.raises(FiveStepDocxError, match="source-fidelity plan is not closed"):
        build_docx_package(master, output, title="Synthetic",
                           config=config, reader_options=options, fidelity_plan=plan_path)
    assert not output.exists()


@pytest.mark.parametrize("variant", ["partial_operand", "foreign_page", "foreign_story", "invented_term"])
def test_resealed_invalid_operation_fails_public_builder_before_output(tmp_path: Path,
                                                                         monkeypatch: pytest.MonkeyPatch,
                                                                         variant: str) -> None:
    master, config, options, plan_path = _fixture(tmp_path, monkeypatch)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if variant == "invented_term":
        source, target = "Know", "Выдуманный навык"
        plan["terminology_rows"] = [{"occurrence_id": "term-1", "entity_id": "keeper",
            "source_label": source, "source_context": "general", "target_label": target,
            "percentage": 70, "registry_sha256": plan["glossary_registry"]["sha256"],
            "overlay_sha256": plan["glossary_overlay"]["sha256"],
            "disposition": "accepted_direct_mapping", "authority_reference": "overlay:Know",
            "collision_decision": None,
            "selector": _selector(source, target, before_value=source, after_value=target)}]
    else:
        row = _row()
        row.update(book_id="synthetic-fixture", story_id="synthetic", entity_id="keeper",
                   source_pdf_sha256=plan["source_pdf"]["sha256"], decision_reference="fixture review")
        if variant == "partial_operand":
            row.update(before=3, after=15, selector=_selector("STR 13", "STR 115",
                                 before_value="3", after_value="15"))
        elif variant == "foreign_page":
            row["source_page"] = 9999
        else:
            row["story_id"] = "absent-story"
        plan["edition_rows"] = [row]
        plan["edition_domain"] = [{"occurrence_id": row["occurrence_id"],
            "book_id": "synthetic-fixture", "story_id": "synthetic", "entity_id": "keeper",
            "source_page": 1, "field": "STR",
            "source_render_sha256": json.loads((tmp_path / "guard/inventory/SOURCE_GRAPHICS_INVENTORY.json").read_text(encoding="utf-8"))["pages"][0]["render"]["sha256"],
            "decision_reference": "fixture review"}]
    _write(plan_path, sealed(PLAN_SCHEMA, {key: value for key, value in plan.items()
                                           if key not in {"schema", "plan_sha256"}},
                             digest_key="plan_sha256"))
    output = tmp_path / "forbidden-operation"
    with pytest.raises(FiveStepDocxError, match="source-fidelity plan is not closed"):
        build_docx_package(master, output, title="Synthetic", config=config,
                           reader_options=options, fidelity_plan=plan_path)
    assert not output.exists()


def test_offline_verifier_reopens_exact_plan_not_resealed_substitute(tmp_path: Path,
                                                                     monkeypatch: pytest.MonkeyPatch) -> None:
    master, config, options, plan_path = _fixture(tmp_path, monkeypatch)
    result = build_docx_package(master, tmp_path / "sealed-package", title="Synthetic",
                                config=config, reader_options=options, fidelity_plan=plan_path)
    assert verify_docx_package(result["manifest_path"].parent)["status"] == "verified_pending_visual_review"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["policy"]["book_id"] = "foreign-book"
    _write(plan_path, sealed(PLAN_SCHEMA, {key: value for key, value in plan.items()
                                           if key not in {"schema", "plan_sha256"}},
                             digest_key="plan_sha256"))
    with pytest.raises(FiveStepDocxError, match="source/output verification failed"):
        verify_docx_package(result["manifest_path"].parent)
