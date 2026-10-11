import copy
import hashlib
import json

import pytest

from kb_creator.pipeline.heading_display import flatten_word_wrapped_heading
from kb_creator.pipeline.semantic_structure import _normalized
from kb_creator.scripts.author_reviewed_semantic_decisions import _render_reviewed_markdown
from kb_creator.scripts.materialize_mineru_ai_merge import _validated_v2_title_role
from kb_creator.scripts.normalize_heading_display import normalize_heading_spec


@pytest.mark.parametrize("source,expected", [
    ("<sup>Researching</sup> <sub>Winoka</sub> <sub>Point</sub>", "Researching Winoka Point"),
    ("Saturday Morning at the <sub>Phlebotomy</sub> <sub>Lab</sub>", "Saturday Morning at the Phlebotomy Lab"),
    ("Investigating Frank <sub>Phelps</sub>", "Investigating Frank Phelps"),
    ("<SUB>Русский заголовок</SUB>", "Русский заголовок"),
])
def test_word_wrapped_heading_display(source, expected):
    assert flatten_word_wrapped_heading(source) == expected


@pytest.mark.parametrize("source", [
    "x<sup>2</sup>", "H<sub>two</sub>O", "Note <sup>2</sup>",
    "<sup class='x'>Title</sup>", "<sub>Title</sup>", "<sup>Title",
    "<sup><sub>Title</sub></sup>", "<sub>Title</sub> <img src='x'>",
    "<sub>Title</sub> <sup>2</sup>", "<script>Title</script>",
])
def test_display_never_flattens_formula_or_unsupported_html(source):
    assert flatten_word_wrapped_heading(source) == source


def _fixture(source, reader):
    sha = lambda text: hashlib.sha256(text.encode()).hexdigest().upper()
    key = {"view": "original_pipeline_txt", "raw_index": 7}
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    unit = {"id": "title", "kind": "heading", "representation": "atx_heading",
            "source_blocks": [key], "source_fragments": [{**key, "start": 0, "end": len(source),
                "source_sha256": sha(source), "fragment_sha256": sha(source),
                "normalized_sha256": sha(_normalized(source))}],
            "markdown_span": {"start_line": 1, "end_line": 1, "sha256": sha(reader)},
            "container_parent": None, "semantic_parent": None, "continuation_of": None,
            "heading_level": 2, "item_count": None}
    decision = {"source_page": 1, "semantic_role": "body", "markdown": reader,
                "review": {"visual_reviewed": False, "notes": ""},
                "selected_blocks": [{**key, "purpose": "text"}], "assets": [],
                "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v2",
                    "profile": "reviewed_role_outline_and_partitions_v2",
                    "role_contract": {"role": "body", "group_id": "example"},
                    "review": {"state": "complete", "visual": visual}, "units": [unit]}}
    packet = {"views": {key["view"]: {"blocks": [{"raw_index": 7, "text": source,
        "assets": [], "semantic_evidence": {"v2_title": True}}]}}}
    return decision, packet


def test_display_consumer_requires_exact_source_and_reader_proof():
    source = "Investigating Frank <sub>Phelps</sub>"
    decision, packet = _fixture(source, "## Investigating Frank Phelps")
    assert _validated_v2_title_role(decision, packet, source, ("original_pipeline_txt", 7), set())
    # A text-equal heading belonging to another key is still insufficient.
    assert not _validated_v2_title_role(decision, packet, source, ("original_pipeline_txt", 8), set())
    decision["semantic_structure"]["units"][0]["source_fragments"][0]["source_sha256"] = "B" * 64
    assert not _validated_v2_title_role(decision, packet, source, ("original_pipeline_txt", 7), set())


def test_consumer_rejects_resealed_lexical_change_and_flattened_exponent():
    for source, reader in [("Frank <sub>Phelps</sub>", "## Frank Other"), ("Formula x<sup>2</sup>", "## Formula x2")]:
        decision, packet = _fixture(source, reader)
        assert not _validated_v2_title_role(decision, packet, source, ("original_pipeline_txt", 7), set())


def test_spec_normalization_preserves_units_and_uses_existing_patch_order(tmp_path):
    source = "Investigating Frank <sub>Phelps</sub>"
    decision, packet = _fixture(source, source)
    decision["overlay_preference"] = "original_pipeline_txt"
    unit = {"id": "title", "kind": "heading", "representation": "atx_heading",
            "view": "original_pipeline_txt", "raw_indices": [7], "start_line": 1,
            "end_line": 1, "heading_level": 2}
    row = {"source_page": 1, "units": [unit],
           "post_patches": [{"before": source, "after": "## " + source, "count": 1}]}
    spec = {"semantic_structure_profile": "reviewed_role_outline_and_partitions_v2", "pages": [row]}
    before = copy.deepcopy(spec)
    drafts, packets = tmp_path / "drafts", tmp_path / "packets"
    for path, value in ((drafts, decision), (packets, packet)):
        path.mkdir()
        (path / "page-001.json").write_text(json.dumps(value), encoding="utf-8")
    successor, report = normalize_heading_spec(spec, drafts, packets)
    assert spec == before
    assert successor["pages"][0]["units"] == row["units"]
    assert report["accepted"] is False and len(report["changes"]) == 1
    rendered, _ = _render_reviewed_markdown(decision, packet, successor["pages"][0], 1)
    assert rendered == "## Investigating Frank Phelps"
    packet["views"]["original_pipeline_txt"]["blocks"][0]["text"] = "Changed source"
    (packets / "page-001.json").write_text(json.dumps(packet), encoding="utf-8")
    with pytest.raises(ValueError, match="source text differs"):
        normalize_heading_spec(spec, drafts, packets)


def test_repeated_heading_normalization_keeps_two_distinct_source_occurrences(tmp_path):
    source = "Investigating <sub>Phelps</sub>"
    decision, packet = _fixture(source, f"## {source}\nBody one\n## {source}\nBody two")
    decision["overlay_preference"] = "original_pipeline_txt"
    decision["selected_blocks"].append({"view": "original_pipeline_txt", "raw_index": 8, "purpose": "text"})
    packet["views"]["original_pipeline_txt"]["blocks"].append({"raw_index": 8, "text": source})
    units = [{"id": f"title-{raw}", "kind": "heading", "representation": "atx_heading",
              "view": "original_pipeline_txt", "raw_indices": [raw], "start_line": line,
              "end_line": line, "heading_level": 2} for raw, line in ((7, 1), (8, 3))]
    spec = {"semantic_structure_profile": "reviewed_role_outline_and_partitions_v2",
            "pages": [{"source_page": 1, "units": units}]}
    drafts, packets = tmp_path / "drafts", tmp_path / "packets"
    for path, value in ((drafts, decision), (packets, packet)):
        path.mkdir()
        (path / "page-001.json").write_text(json.dumps(value), encoding="utf-8")
    successor, report = normalize_heading_spec(spec, drafts, packets)
    assert [row["raw_index"] for row in report["changes"]] == [7, 8]
    assert successor["pages"][0]["units"] == units
    rendered, _ = _render_reviewed_markdown(decision, packet, successor["pages"][0], 1)
    assert rendered == "## Investigating Phelps\nBody one\n## Investigating Phelps\nBody two"
