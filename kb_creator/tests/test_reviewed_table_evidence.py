from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb_creator.pipeline.reviewed_table_evidence import verify_table_evidence


def _identity(path: Path, root: Path) -> dict:
    import hashlib
    return {"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()}


def _case(tmp_path: Path, *, source_html: str, markdown: str, page: int = 1, view: str = "original_pipeline_ocr"):
    metadata = tmp_path / "outputs" / "02-mineru-three-view" / "views" / view / "artifacts" / "source_content_list.json"
    metadata.parent.mkdir(parents=True)
    source = [{"type": "text", "page_idx": 0}, {"type": "table", "page_idx": page - 1, "table_body": source_html}]
    metadata.write_text(json.dumps(source), encoding="utf-8")
    packet = {"views": {view: {"blocks": [{"raw_index": 1, "type": "table"}]}}}
    decision = {"source_page": page, "markdown": markdown, "selected_blocks": [{"view": view, "raw_index": 1, "purpose": "text"}]}
    page_spec = {"source_page": page, "units": [{"kind": "statblock", "representation": "table", "view": view, "raw_indices": [1], "start_line": 1, "end_line": len(markdown.splitlines())}]}
    import hashlib
    binding = {"view": view, "raw_index": 1, "metadata": _identity(metadata, tmp_path), "table_body_sha256": hashlib.sha256(source_html.encode()).hexdigest().upper()}
    return packet, decision, page_spec, [binding]


HEADERLESS_HTML = "<table><tr><td>STR</td><td>10</td><td></td><td>85%</td></tr><tr><td>DEX</td><td>12</td><td>A&amp;B</td><td>\u00a0</td></tr></table>"
HEADERLESS_MARKDOWN = "|  |  |  |  |\n| --- | --- | --- | --- |\n| STR | 10 |  | 85% |\n| DEX | 12 | A&B | \u00a0 |"


def test_headerless_table_preserves_empty_cells_numeric_stats_and_entities(tmp_path: Path):
    packet, decision, spec, bindings = _case(tmp_path, source_html=HEADERLESS_HTML, markdown=HEADERLESS_MARKDOWN)
    result = verify_table_evidence(tmp_path, packet, decision, spec, bindings)
    assert result == [{"view": "original_pipeline_ocr", "raw_index": 1, "source_page": 1, "row_count": 2, "column_count": 4, "cell_count": 8, "source_has_header_row": False, "header_basis": "html_th", "header_review": None}]


def test_headered_table_retains_real_header(tmp_path: Path):
    source = "<table><tr><th>Skill</th><th>Value</th></tr><tr><td>Listen</td><td>70%</td></tr></table>"
    markdown = "| Skill | Value |\n| --- | --- |\n| Listen | 70% |"
    packet, decision, spec, bindings = _case(tmp_path, source_html=source, markdown=markdown)
    assert verify_table_evidence(tmp_path, packet, decision, spec, bindings)[0]["source_has_header_row"] is True


def test_td_only_printed_header_requires_explicit_reviewed_declaration(tmp_path: Path):
    source = "<table><tr><td>STR</td><td>CON</td><td>HP</td></tr><tr><td>22</td><td>13</td><td>13</td></tr></table>"
    markdown = "| STR | CON | HP |\n| --- | --- | --- |\n| 22 | 13 | 13 |"
    packet, decision, spec, bindings = _case(tmp_path, source_html=source, markdown=markdown)
    with pytest.raises(ValueError, match="fully empty"):
        verify_table_evidence(tmp_path, packet, decision, spec, bindings)
    bindings[0]["header_review"] = {"source_header_rows": 1, "rationale": "Printed column labels were reviewed."}
    result = verify_table_evidence(tmp_path, packet, decision, spec, bindings)[0]
    assert result["source_has_header_row"] is True
    assert result["header_basis"] == "reviewed_header"
    assert result["header_review"] == bindings[0]["header_review"]


@pytest.mark.parametrize("review", [
    {"source_header_rows": 2, "rationale": "bad count"},
    {"source_header_rows": 1, "rationale": ""},
    {"source_header_rows": 1, "rationale": "valid", "extra": True},
])
def test_malformed_header_review_rejects(tmp_path: Path, review: dict):
    packet, decision, spec, bindings = _case(tmp_path, source_html=HEADERLESS_HTML, markdown=HEADERLESS_MARKDOWN)
    bindings[0]["header_review"] = review
    with pytest.raises(ValueError, match="header review"):
        verify_table_evidence(tmp_path, packet, decision, spec, bindings)


def test_source_th_header_rejects_contradictory_review(tmp_path: Path):
    source = "<table><tr><th>Skill</th><th>Value</th></tr><tr><td>Listen</td><td>70%</td></tr></table>"
    markdown = "| Skill | Value |\n| --- | --- |\n| Listen | 70% |"
    packet, decision, spec, bindings = _case(tmp_path, source_html=source, markdown=markdown)
    bindings[0]["header_review"] = {"source_header_rows": 0, "rationale": "contradiction"}
    with pytest.raises(ValueError, match="contradicts source th"):
        verify_table_evidence(tmp_path, packet, decision, spec, bindings)


def test_semantic_markdown_table_from_ordinary_text_does_not_require_html_binding(tmp_path: Path):
    packet = {"views": {"original_pipeline_ocr": {"blocks": [
        {"raw_index": 1, "type": "text"}, {"raw_index": 2, "type": "text"},
    ]}}}
    decision = {"source_page": 1, "markdown": "| STR | HP |\n| --- | --- |\n| 14 | 14 |", "selected_blocks": [
        {"view": "original_pipeline_ocr", "raw_index": 1, "purpose": "text"},
        {"view": "original_pipeline_ocr", "raw_index": 2, "purpose": "text"},
    ]}
    spec = {"source_page": 1, "units": [{"kind": "statblock", "representation": "table", "view": "original_pipeline_ocr", "raw_indices": [1, 2]}]}
    assert verify_table_evidence(tmp_path, packet, decision, spec, []) == []


def test_source_table_unit_with_multiple_raw_blocks_rejects(tmp_path: Path):
    packet = {"views": {"original_pipeline_ocr": {"blocks": [
        {"raw_index": 1, "type": "table"}, {"raw_index": 2, "type": "text"},
    ]}}}
    decision = {"source_page": 1, "markdown": "", "selected_blocks": [
        {"view": "original_pipeline_ocr", "raw_index": 1, "purpose": "text"},
        {"view": "original_pipeline_ocr", "raw_index": 2, "purpose": "text"},
    ]}
    spec = {"source_page": 1, "units": [{"kind": "statblock", "representation": "table", "view": "original_pipeline_ocr", "raw_indices": [1, 2]}]}
    with pytest.raises(ValueError, match="source-table unit must name exactly one"):
        verify_table_evidence(tmp_path, packet, decision, spec, [])


@pytest.mark.parametrize("markdown", [
    "|  |  |  |  |\n| --- | --- | --- | --- |\n| STR | 11 |  | 85% |\n| DEX | 12 | A&B | \u00a0 |",
    "|  |  |  |  |\n| --- | --- | --- | --- |\n| STR | 10 |  | 85% |",
    "| Skill | Value |  |  |\n| --- | --- | --- | --- |\n| STR | 10 |  | 85% |\n| DEX | 12 | A&B | \u00a0 |",
])
def test_changed_dropped_or_fabricated_headerless_cells_reject(tmp_path: Path, markdown: str):
    packet, decision, spec, bindings = _case(tmp_path, source_html=HEADERLESS_HTML, markdown=markdown)
    with pytest.raises(ValueError, match="Markdown (cells differ|table topology)|fully empty"):
        verify_table_evidence(tmp_path, packet, decision, spec, bindings)


def test_stale_metadata_wrong_view_page_missing_extra_and_traversal_reject(tmp_path: Path):
    packet, decision, spec, bindings = _case(tmp_path, source_html=HEADERLESS_HTML, markdown=HEADERLESS_MARKDOWN, page=2)
    metadata = tmp_path / bindings[0]["metadata"]["path"]
    contents = json.loads(metadata.read_text(encoding="utf-8")); contents[1]["page_idx"] = 0
    metadata.write_text(json.dumps(contents), encoding="utf-8"); bindings[0]["metadata"] = _identity(metadata, tmp_path)
    with pytest.raises(ValueError, match="source type, view, or page"):
        verify_table_evidence(tmp_path, packet, decision, spec, bindings)
    bindings[0]["metadata"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="metadata identity mismatch"):
        verify_table_evidence(tmp_path, packet, decision, spec, bindings)
    packet, decision, spec, bindings = _case(tmp_path / "missing", source_html=HEADERLESS_HTML, markdown=HEADERLESS_MARKDOWN)
    with pytest.raises(ValueError, match="exactly cover"):
        verify_table_evidence(tmp_path / "missing", packet, decision, spec, [])
    extra = {**bindings[0], "raw_index": 2}
    with pytest.raises(ValueError, match="exactly cover"):
        verify_table_evidence(tmp_path / "missing", packet, decision, spec, [*bindings, extra])
    bindings[0]["metadata"]["path"] = "../outside.json"
    with pytest.raises(ValueError, match="outside the approved artifacts"):
        verify_table_evidence(tmp_path / "missing", packet, decision, spec, bindings)


def test_wrong_view_and_unsupported_spans_reject(tmp_path: Path):
    packet, decision, spec, bindings = _case(tmp_path, source_html=HEADERLESS_HTML, markdown=HEADERLESS_MARKDOWN)
    bindings[0]["view"] = "original_pipeline_txt"
    with pytest.raises(ValueError, match="exactly cover"):
        verify_table_evidence(tmp_path, packet, decision, spec, bindings)
    packet, decision, spec, bindings = _case(tmp_path / "span", source_html="<table><tr><td colspan='2'>STR</td></tr></table>", markdown="|  |\n| --- |\n| STR |")
    with pytest.raises(ValueError, match="source HTML is unsupported"):
        verify_table_evidence(tmp_path / "span", packet, decision, spec, bindings)
