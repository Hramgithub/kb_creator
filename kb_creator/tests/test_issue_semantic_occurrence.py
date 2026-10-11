"""Repeated reader wording must bind to its source unit, not a first hit."""
import json

import pytest

from kb_creator.pipeline.five_step_intake import FiveStepIntakeError, _issue_en_bindings
from kb_creator.pipeline.identity import file_identity, sha256_bytes


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _fixture(tmp_path, *, asset=False):
    lines = ["Mention Same defense here.", "", "NPC one", "Same defense", "",
             "NPC two", "Same defense"]
    assets = []
    if asset:
        lines[0] = "![Portrait]({{asset:portrait.png}}) Mention Same defense here."
        assets = [{"view": "original_pipeline_txt", "source_path": "images/p.png",
                   "logical_name": "portrait.png", "placement": "inline"}]
    markdown = "\n".join(lines)
    keys = [{"view": "original_pipeline_txt", "raw_index": n} for n in (10, 11)]
    units = [{"id": str(key["raw_index"]), "source_blocks": [key],
              "markdown_span": {"start_line": line, "end_line": line,
                                "sha256": sha256_bytes(lines[line - 1].encode())}}
             for key, line in zip(keys, (4, 7))]
    decision = {"source_page": 1, "markdown": markdown, "assets": assets,
                "selected_blocks": keys, "semantic_structure": {"units": units}}
    decision_path = tmp_path / "evidence/review/page-001.json"
    _write(decision_path, decision)
    _write(tmp_path / "ASSET_MANIFEST.json", {"assets": [dict(row, stored_path="assets/long-hashed-name.png") for row in assets]})
    rendered = markdown.replace("{{asset:portrait.png}}", "assets/long-hashed-name.png")
    master = tmp_path / "MASTER_EN.md"
    master.write_text("<!-- source-page-001 -->\n\n" + rendered + "\n", encoding="utf-8")
    evidence = tmp_path / "final-evidence.json"
    _write(evidence, {"fixture": "only the occurrence projection is under test"})
    issue = {"issue_id": "npc-two-defense", "source_page": 1,
             "source_excerpt_en": "Same defense",
             "source_excerpt_sha256": sha256_bytes(b"Same defense"),
             "source_selector": {"mechanical_diagnostic": {"code": "three_view_content_mismatch", "source_keys": [keys[1]]}}}
    return master, evidence, decision_path, decision, issue


@pytest.mark.parametrize("asset", [False, True])
def test_repeated_issue_uses_exact_semantic_source_occurrence(tmp_path, asset):
    master, evidence, _, _, issue = _fixture(tmp_path, asset=asset)
    binding = _issue_en_bindings(master, [issue], [1], evidence)["bindings"][0]
    text = master.read_text(encoding="utf-8")
    assert binding["character_start"] == text.rindex("Same defense")
    assert text[binding["character_start"]:binding["character_end"]] == "Same defense"


@pytest.mark.parametrize("mutation", ["missing_decision", "wrong_source", "stale_span", "wrong_page", "changed_projection", "ambiguous_units"])
def test_repeated_issue_rejects_unbound_or_ambiguous_occurrence(tmp_path, mutation):
    master, evidence, decision_path, decision, issue = _fixture(tmp_path)
    if mutation == "missing_decision":
        decision_path.unlink()
    elif mutation == "wrong_source":
        issue["source_selector"]["mechanical_diagnostic"]["source_keys"][0] = {"view": "original_pipeline_txt", "raw_index": 99}
    elif mutation == "stale_span":
        decision["semantic_structure"]["units"][1]["markdown_span"]["sha256"] = "0" * 64
    elif mutation == "wrong_page":
        decision["source_page"] = 2
    elif mutation == "changed_projection":
        master.write_text(master.read_text(encoding="utf-8").replace("NPC two", "Unbound NPC"), encoding="utf-8")
    else:
        decision["semantic_structure"]["units"][0]["source_blocks"] = decision["semantic_structure"]["units"][1]["source_blocks"]
    if mutation != "missing_decision":
        _write(decision_path, decision)
    with pytest.raises(FiveStepIntakeError):
        _issue_en_bindings(master, [issue], [1], evidence)


def test_unique_issue_keeps_original_offsets_without_semantic_requirement(tmp_path):
    master, evidence, decision_path, _, issue = _fixture(tmp_path)
    decision_path.unlink()
    issue["source_excerpt_en"] = "NPC two"
    issue["source_excerpt_sha256"] = sha256_bytes(b"NPC two")
    binding = _issue_en_bindings(master, [issue], [1], evidence)["bindings"][0]
    assert binding["character_start"] == master.read_text(encoding="utf-8").index("NPC two")


def test_repeated_ordinary_prose_uses_stage05_ordered_source_mapping(tmp_path):
    master, evidence, _, decision, issue = _fixture(tmp_path)
    # Remove semantic presentation units: the second repeated phrase remains
    # identifiable through the audited source-key-to-reader span.
    decision["semantic_structure"] = {"units": []}
    _write(tmp_path / "evidence/review/page-001.json", decision)
    audit = {"pages": [{"source_page": 1, "ordered_proof_stream": [
        {"kind": "selected", "unit": {"view_id": "original_pipeline_txt", "raw_index": 10}, "markdown_span": [0, 20]},
        {"kind": "selected", "unit": {"view_id": "original_pipeline_txt", "raw_index": 11}, "markdown_span": [45, 56]},
    ]}]}
    audit_path = tmp_path / "review-draft-stage05-audit.json"; _write(audit_path, audit)
    _write(evidence, {"authored": {"stage05_audit": {"path": audit_path.name, **file_identity(audit_path)}}})
    binding = _issue_en_bindings(master, [issue], [1], evidence)["bindings"][0]
    assert binding["character_start"] == master.read_text(encoding="utf-8").rindex("Same defense")
