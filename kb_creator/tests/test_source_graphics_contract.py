"""Synthetic source-page domain checks; no copyrighted book fixture."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfWriter

from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline.source_graphics import (
    INVENTORY_SCHEMA,
    REVIEW_SCHEMA,
    SourceGraphicsError,
    build_inventory,
    validate_inventory,
    validate_produced_inventory,
    validate_review,
)


def _write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def _inventory(tmp_path: Path, occurrences: list[dict] | None = None) -> tuple[Path, dict]:
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        pytest.fail("pdftoppm runtime is required for source-graphic regression")
    source = tmp_path / "synthetic.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=288, height=360)
    with source.open("wb") as stream:
        writer.write(stream)
    path = build_inventory(source, Path(renderer), tmp_path / "inventory")
    value = json.loads(path.read_text(encoding="utf-8"))
    if occurrences:
        value["paint_occurrences"] = occurrences
        value = sealed(INVENTORY_SCHEMA, {k: v for k, v in value.items()
                                          if k not in {"schema", "inventory_sha256"}},
                       digest_key="inventory_sha256")
        _write(path, value)
    return path, value


def _review(tmp_path: Path, inventory_path: Path, inventory: dict, graphics: list[dict] | None = None,
            regions: list[dict] | None = None) -> tuple[Path, dict]:
    graphics = graphics or []
    rows = []
    for page in inventory["pages"]:
        ids = [g["graphic_id"] for g in graphics if g["page"] == page["page"]]
        rows.append({"page": page["page"], "render_sha256": page["render"]["sha256"],
                     "status": "reviewed_graphics" if ids else "reviewed_no_meaningful_graphics",
                     "graphic_ids": ids, "residual_issues": [],
                     "manual_page_coverage": {"view_sha256": page["render"]["sha256"],
                                              "reviewed": True, "regions": regions or [],
                                              "remaining_limits": "manual semantic review; raw vector traversal incomplete",
                                              "reviewer_reference": "synthetic fixture page review"}})
    value = sealed(REVIEW_SCHEMA, {
        "inventory": {"path": str(inventory_path.resolve()), **file_identity(inventory_path)},
        "source_pdf": inventory["source_pdf"],
        "reviewer": {"role": "independent_page_reviewer", "reference": "test decision",
                     "time_utc": "2026-01-01T00:00:00Z"},
        "page_reviews": rows, "graphics": graphics, "technical_occurrences": [], "state": "closed",
    }, digest_key="review_sha256")
    path = tmp_path / "SOURCE_GRAPHICS_REVIEW.json"
    _write(path, value)
    return path, value


def _paint(oid: str, *, page: int = 1, kind: str = "raster") -> dict:
    return {"occurrence_id": oid, "page": page, "kind": kind,
            "operator_path": f"Do/{oid}", "invocation_ordinal": 0,
            "resource_path": ["XObject", "Im0"], "stream_sha256": "D" * 64,
            "bbox": [1, 1, 20, 20], "discovery_limit": None}


def _graphic(tmp_path: Path, oid: str, *, gid: str = "scene-1") -> tuple[dict, dict]:
    selected = tmp_path / f"{gid}.png"
    Image.new("RGB", (20, 20), "black").save(selected)
    graphic = {"graphic_id": gid, "page": 1, "category": "body_scene", "owner": "story-one",
               "source_region": [1, 1, 20, 20], "occurrence_ids": [oid],
               "manual_region_id": "region-1", "disposition": "include",
               "rationale": "reviewed source scene", "decision_reference": "fixture decision",
               "selected": {"path": selected.name, **file_identity(selected)}}
    region = {"region_id": "region-1", "bbox": [1, 1, 20, 20], "graphic_id": gid}
    return graphic, region


def test_every_physical_page_requires_hash_bound_manual_review(tmp_path: Path) -> None:
    inventory_path, inventory = _inventory(tmp_path)
    review_path, _ = _review(tmp_path, inventory_path, inventory)
    assert validate_inventory(inventory_path, source_pdf=tmp_path / "synthetic.pdf")["source_pdf"]["page_count"] >= 1
    assert validate_review(review_path, inventory_path, source_pdf=tmp_path / "synthetic.pdf")["state"] == "closed"


def test_missing_blank_page_review_and_stale_render_cannot_pass(tmp_path: Path) -> None:
    inventory_path, inventory = _inventory(tmp_path)
    review_path, value = _review(tmp_path, inventory_path, inventory)
    value["page_reviews"].pop()
    _write(review_path, sealed(REVIEW_SCHEMA, {k: v for k, v in value.items() if k not in {"schema", "review_sha256"}}, digest_key="review_sha256"))
    with pytest.raises(SourceGraphicsError, match="every physical page"):
        validate_review(review_path, inventory_path)


def test_raster_missing_from_review_fails_even_with_empty_downstream_domain(tmp_path: Path) -> None:
    inventory_path, inventory = _inventory(tmp_path, [_paint("use-1")])
    review_path, _ = _review(tmp_path, inventory_path, inventory)
    with pytest.raises(SourceGraphicsError, match="paint/page source domain"):
        validate_review(review_path, inventory_path)


def test_repeated_same_binary_uses_need_distinct_occurrence_dispositions(tmp_path: Path) -> None:
    inventory_path, inventory = _inventory(tmp_path, [_paint("use-1"), _paint("use-2")])
    graphic, region = _graphic(tmp_path, "use-1")
    review_path, _ = _review(tmp_path, inventory_path, inventory, [graphic], [region])
    with pytest.raises(SourceGraphicsError, match="paint/page source domain"):
        validate_review(review_path, inventory_path)
    graphic["occurrence_ids"] = ["use-1", "use-2"]
    review_path, _ = _review(tmp_path, inventory_path, inventory, [graphic], [region])
    assert validate_review(review_path, inventory_path)["state"] == "closed"


def test_uninvoked_resource_never_substitutes_for_page_review(tmp_path: Path) -> None:
    inventory_path, inventory = _inventory(tmp_path, [_paint("unused", kind="uninvoked_resource")])
    review_path, review = _review(tmp_path, inventory_path, inventory)
    assert validate_review(review_path, inventory_path)["state"] == "closed"
    review["page_reviews"][0]["manual_page_coverage"]["reviewed"] = False
    _write(review_path, sealed(REVIEW_SCHEMA, {k: v for k, v in review.items() if k not in {"schema", "review_sha256"}}, digest_key="review_sha256"))
    with pytest.raises(SourceGraphicsError, match="manual page coverage"):
        validate_review(review_path, inventory_path)


def test_vector_only_discovery_cannot_claim_automatic_exhaustiveness(tmp_path: Path) -> None:
    inventory_path, inventory = _inventory(tmp_path, [_paint("vector-1", kind="vector_group")])
    inventory["pages"][0]["discovery"] = {"status": "complete", "diagnostic_ids": [], "limits": []}
    _write(inventory_path, sealed(INVENTORY_SCHEMA, {k: v for k, v in inventory.items() if k not in {"schema", "inventory_sha256"}}, digest_key="inventory_sha256"))
    with pytest.raises(SourceGraphicsError, match="cannot claim exhaustive"):
        validate_inventory(inventory_path)


def test_nonobject_sealed_inventory_is_typed_failure(tmp_path: Path) -> None:
    inventory_path = tmp_path / "not-object.json"
    inventory_path.write_text("[]", encoding="utf-8")
    with pytest.raises(SourceGraphicsError, match="must be an object"):
        validate_inventory(inventory_path)


def test_pdf_derived_inventory_replays_all_physical_page_renders(tmp_path: Path) -> None:
    renderer = shutil.which("pdftoppm")
    if renderer is None:
        pytest.skip("pdftoppm runtime is unavailable")
    source = tmp_path / "synthetic.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=288, height=360)
    writer.add_blank_page(width=288, height=360)
    with source.open("wb") as stream:
        writer.write(stream)
    inventory_path = build_inventory(source, Path(renderer), tmp_path / "inventory")
    value = validate_produced_inventory(inventory_path, source_pdf=source)
    assert [row["page"] for row in value["pages"]] == [1, 2]
    assert all(row["discovery"]["status"] == "incomplete" for row in value["pages"])
    assert value["paint_occurrences"] == []  # not a no-graphics decision
