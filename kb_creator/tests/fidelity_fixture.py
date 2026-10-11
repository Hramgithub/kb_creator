"""Explicit synthetic, PDF-bound review authority for guarded DOCX tests.

The source is authored before its inventory and decisions. This is test data,
not a switch around production validation or a claim about a real book.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from translator.translator import slugify

from kb_creator.pipeline.five_step_docx import _default_config
from kb_creator.pipeline.coc_glossary import HEADER
from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline.reader_fidelity import PLAN_SCHEMA
from kb_creator.pipeline.reader_projection import seal as seal_options
from kb_creator.pipeline.source_graphics import REVIEW_SCHEMA, build_inventory


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def synthetic_source_review(source_pdf: Path, guard_root: Path) -> tuple[Path, Path]:
    """Review every page of an explicitly graphic-free synthetic PDF."""
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        raise RuntimeError("pdftoppm is required for synthetic source review tests")
    guard_root.mkdir(parents=True, exist_ok=True)
    inventory_path = build_inventory(source_pdf, Path(renderer), guard_root / "inventory")
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    pages = [{"page": row["page"], "render_sha256": row["render"]["sha256"],
              "status": "reviewed_no_meaningful_graphics", "graphic_ids": [],
              "residual_issues": [],
              "manual_page_coverage": {"view_sha256": row["render"]["sha256"],
                                       "reviewed": True, "regions": [],
                                       "remaining_limits": "synthetic text-only page reviewed in full",
                                       "reviewer_reference": "test-only page review"}}
             for row in inventory["pages"]]
    review = sealed(REVIEW_SCHEMA, {
        "inventory": {"path": str(inventory_path.resolve()), **file_identity(inventory_path)},
        "source_pdf": inventory["source_pdf"],
        "reviewer": {"role": "test_source_page_reviewer", "reference": "synthetic text-only fixture",
                     "time_utc": "2026-01-01T00:00:00Z"},
        "page_reviews": pages, "graphics": [], "technical_occurrences": [], "state": "closed"},
        digest_key="review_sha256")
    review_path = guard_root / "SOURCE_GRAPHICS_REVIEW.json"
    _write(review_path, review)
    return inventory_path, review_path


def synthetic_guard(master_root: Path, guard_root: Path, *, title: str = "Тест",
                    source_pdf: Path | None = None, reader_options: Path | None = None,
                    config: Path | None = None, source_graphic_page: int = 1) -> tuple[Path, Path, Path, Path]:
    """Make a source-visible one-section fixture for the current test master.

    Existing source PDFs must already depict the selected image(s); callers
    should not use this helper to claim coverage for an unrelated source.
    """
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        raise RuntimeError("pdftoppm is required for guarded DOCX tests")
    plan_path = guard_root / "READER_FIDELITY_PLAN.json"
    if plan_path.is_file():
        return (config or guard_root / "docx_config.json",
                reader_options or guard_root / "reader_options.json",
                plan_path, guard_root / "inventory" / "SOURCE_GRAPHICS_INVENTORY.json")
    guard_root.mkdir(parents=True, exist_ok=True)
    master = master_root / "MASTER_RU.md"
    projection = master_root / "semantic_context" / "RU_PROJECTION.json"
    text = master.read_text(encoding="utf-8")
    headings = re.findall(r"^#\s+(.+?)\s*$", text, re.M)
    if not headings:
        raise ValueError("synthetic guarded fixture needs a top-level section")
    section = slugify(headings[0].strip())
    images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    # The source PDF is generated from fixture decisions before review. Tests
    # with a mutated/broken Markdown reference can still review the original
    # selected asset, then exercise the real asset validator downstream.
    available = [master_root / ref for ref in images if (master_root / ref).is_file()]
    selected = available[0] if available else master_root / "assets" / "map.png"
    selected_copy = guard_root / "selected-map.png"
    if selected.is_file():
        shutil.copyfile(selected, selected_copy)
    if source_pdf is None:
        source_pdf = guard_root / "synthetic-source.pdf"
        pdf = canvas.Canvas(str(source_pdf), pagesize=(400, 600), pageCompression=0)
        pdf.drawString(20, 560, headings[0])
        for index in range(max(1 if selected.is_file() else 0, len(images))):
            if selected.is_file():
                pdf.drawImage(ImageReader(str(selected)), 20, 450 - index * 110,
                              width=90, height=60)
        pdf.showPage()
        pdf.save()
    inventory_path = build_inventory(source_pdf, Path(renderer), guard_root / "inventory")
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    source_images = max(1 if selected.is_file() else 0, len(images))
    if source_images and not selected.is_file():
        raise ValueError("synthetic source graphic needs selected image bytes")
    if source_images and not images:
        # An absent-from-master source illustration is intentionally explicit.
        image_relation = "absent_from_master"
    else:
        image_relation = "in_master"
    graphics = []
    regions = []
    placements = []
    for index in range(source_images):
        gid = f"fixture-map-{index + 1}"
        rid = f"fixture-region-{index + 1}"
        bbox = [20, 90 + index * 110, 110, 150 + index * 110]
        graphics.append({"graphic_id": gid, "page": source_graphic_page, "category": "map",
                         "owner": section, "source_region": bbox,
                         "occurrence_ids": [], "manual_region_id": rid,
                         "disposition": "include", "rationale": "synthetic source map visible",
                         "decision_reference": "test-only full-page source review",
                         "selected": {"path": selected_copy.name, **file_identity(selected_copy)}})
        regions.append({"region_id": rid, "bbox": bbox, "graphic_id": gid})
        placements.append({"placement_id": f"fixture-placement-{index + 1}",
                           "graphic_id": gid, "story_id": section, "anchor": section,
                           "position": "after", "repeat_ordinal": index,
                           "selected_sha256": file_identity(selected)["sha256"],
                           "representation": "word_drawing", "master_relation": image_relation,
                           "route": "retain_exact" if image_relation == "in_master" else "reviewed_reader_insertion",
                           "crop": {"left": 0, "top": 0, "right": 0, "bottom": 0,
                                    "approved": True},
                           "fit": {"width_emu": 2000000, "height_emu": 1400000},
                           "decision_reference": "synthetic source map placement"})
    pages = []
    for page in inventory["pages"]:
        ids = [row["graphic_id"] for row in graphics] if page["page"] == source_graphic_page else []
        pages.append({"page": page["page"], "render_sha256": page["render"]["sha256"],
                      "status": "reviewed_graphics" if ids else "reviewed_no_meaningful_graphics",
                      "graphic_ids": ids, "residual_issues": [],
                      "manual_page_coverage": {"view_sha256": page["render"]["sha256"],
                                               "reviewed": True,
                                               "regions": regions if ids else [],
                                               "remaining_limits": "test-only manual review of synthetic page",
                                               "reviewer_reference": "synthetic fixture"}})
    review = sealed(REVIEW_SCHEMA, {
        "inventory": {"path": str(inventory_path.resolve()), **file_identity(inventory_path)},
        "source_pdf": inventory["source_pdf"],
        "reviewer": {"role": "test_source_page_reviewer", "reference": "synthetic fixture",
                     "time_utc": "2026-01-01T00:00:00Z"},
        "page_reviews": pages, "graphics": graphics, "technical_occurrences": [],
        "state": "closed"}, digest_key="review_sha256")
    review_path = guard_root / "SOURCE_GRAPHICS_REVIEW.json"
    _write(review_path, review)
    if config is None:
        config = guard_root / "docx_config.json"
        _write(config, _default_config(title))
    if reader_options is None:
        reader_options = guard_root / "reader_options.json"
        options = {"schema": "kb_creator.five_step_reader_options.v1",
                   "master_ru": {"path": "MASTER_RU.md", **file_identity(master)},
                   "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **file_identity(projection)},
                   "source_toc": {"state": "absent", "source_pdf_sha256": inventory["source_pdf"]["sha256"],
                                  "reason": "reviewed synthetic page has no TOC"},
                   "body_links": [], "asset_choices": [],
                   "hit_points": {"presentation": "numeric", "expected_counts": []},
                   "display_roles": []}
        _write(reader_options, {**options, "options_sha256": seal_options(options)})
    registry = guard_root / "accepted-registry.csv"
    overlay = guard_root / "accepted-overlay.json"
    registry.write_text(",".join(HEADER) + "\n", encoding="utf-8")
    _write(overlay, {"terms": []})
    plan = sealed(PLAN_SCHEMA, {
        "inventory": {"path": str(inventory_path.resolve()), **file_identity(inventory_path)},
        "review": {"path": str(review_path.resolve()), **file_identity(review_path)},
        "source_pdf": inventory["source_pdf"],
        "master_ru": {"path": str(master.resolve()), **file_identity(master)},
        "projection": {"path": str(projection.resolve()), **file_identity(projection)},
        "config": {"path": str(config.resolve()), **file_identity(config)},
        "glossary_registry": {"path": str(registry.resolve()), **file_identity(registry)},
        "glossary_overlay": {"path": str(overlay.resolve()), **file_identity(overlay)},
        "policy": {"target_edition": "7e", "edition_applicability": "applicable",
                   "book_id": "synthetic-fixture",
                   "rules_version": "synthetic-review-v1", "reader_profile": "five_step_docx_v3",
                   "review_reference": "complete synthetic source page and section"},
        "placements": placements, "edition_domain": [], "edition_rows": [], "terminology_rows": [],
        "section_domain": [section],
        "section_reviews": [{"section_id": section, "cards": 0, "prose": 0,
                             "pregens": 0, "checks": 0, "labels": 0, "reviewed": True,
                             "decision_reference": "test-only whole section review",
                             "residual_issues": []}], "state": "closed"},
        digest_key="plan_sha256")
    _write(plan_path, plan)
    return config, reader_options, plan_path, inventory_path
