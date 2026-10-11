"""The four versioned contract files remain closed and match runtime documents."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb_creator.pipeline.five_step_docx import build_docx_package
from kb_creator.pipeline.reader_fidelity import PLAN_SCHEMA, VERIFICATION_SCHEMA
from kb_creator.pipeline.source_graphics import INVENTORY_SCHEMA, REVIEW_SCHEMA
from kb_creator.tests.test_guarded_docx_source_fidelity import _fixture


CONTRACTS = Path(__file__).resolve().parents[1] / "contracts"
SCHEMAS = {
    INVENTORY_SCHEMA: CONTRACTS / "source_graphics_inventory.v1.schema.json",
    REVIEW_SCHEMA: CONTRACTS / "source_graphics_review.v1.schema.json",
    PLAN_SCHEMA: CONTRACTS / "reader_fidelity_plan.v2.schema.json",
    VERIFICATION_SCHEMA: CONTRACTS / "reader_fidelity_verification.v1.schema.json",
}


def _assert_closed_objects(node):
    if isinstance(node, dict):
        if node.get("type") == "object":
            assert node.get("additionalProperties") is False
            assert set(node["required"]) == set(node["properties"])
        for item in node.values():
            _assert_closed_objects(item)
    elif isinstance(node, list):
        for item in node:
            _assert_closed_objects(item)


def test_four_contract_documents_are_versioned_and_structurally_closed(tmp_path: Path,
                                                                        monkeypatch: pytest.MonkeyPatch) -> None:
    master, config, options, plan_path = _fixture(tmp_path, monkeypatch)
    result = build_docx_package(master, tmp_path / "package", title="Synthetic",
                                config=config, reader_options=options, fidelity_plan=plan_path)
    guard = tmp_path / "guard"
    documents = [
        guard / "inventory/SOURCE_GRAPHICS_INVENTORY.json",
        guard / "SOURCE_GRAPHICS_REVIEW.json",
        plan_path,
        result["manifest_path"].parent / "READER_FIDELITY_VERIFICATION.json",
    ]
    assert len(documents) == len(SCHEMAS)
    for path in documents:
        value = json.loads(path.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMAS[value["schema"]].read_text(encoding="utf-8"))
        assert schema["$id"] == value["schema"]
        assert set(value) == set(schema["required"]) == set(schema["properties"])
        _assert_closed_objects(schema)
