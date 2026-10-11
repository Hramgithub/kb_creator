from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline.review_draft import validate_review_draft_input
from kb_creator.pipeline.review_draft_preparation import validate_review_draft_author_input
from kb_creator.pipeline.source_choice_successor import linguistic_choice_corrections
from kb_creator.pipeline.source_choice_successor_preparation import (
    SourceChoiceSuccessorPreparationError,
    prepare_source_choice_successor,
)
from kb_creator.pipeline import source_choice_translation as sc
from kb_creator.pipeline.mechanical_reconstruction import verify_mechanical_draft
from kb_creator.tests.test_source_choice_translation import _candidate, _candidate_source, _issue, _master, _submission
from kb_creator.tests.test_mechanical_reconstruction import VIEWS, _verified


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _route(tmp_path: Path, monkeypatch, *, structural: bool = False,
           retained_semantic: bool = False) -> tuple[Path, Path, Path, Path, list[Path]]:
    """Build the same queue/ledger records that R1 must consume."""
    candidate = _candidate(tmp_path)
    diagnostic = json.loads((candidate / "mechanical_draft.json").read_text(encoding="utf-8"))["diagnostics"][0]
    master = _master(tmp_path, _issue(code=diagnostic["code"], source_keys=diagnostic["source_keys"],
                                      source_pdf_sha256=_candidate_source(candidate)["sha256"]), _candidate_source(candidate))
    monkeypatch.setattr(sc, "verify_master_en", lambda root: {"state": "verified_review_draft"})
    monkeypatch.setattr(sc, "verify_mechanical_draft", lambda path: verify_mechanical_draft(path, authority_validator=_verified))
    queue_root, ledger_root = tmp_path / "queue", tmp_path / "ledger"
    sc.prepare(master, candidate, queue_root)
    queue = json.loads((queue_root / "SOURCE_CHOICE_QUEUE.v1.json").read_text(encoding="utf-8"))
    selected = queue["choices"][0]["alternatives"][0 if retained_semantic else 1]["alternative_id"]
    decision = {"issue_id": "choice-001", "disposition": "unresolved_semantic" if retained_semantic else "selected_alternative",
                "alternative_id": selected, "reason": "semantic meaning remains ambiguous" if retained_semantic else "exact witnessed reading"}
    if retained_semantic:
        decision["label"] = "Проверить смысл"
    sc.record_decisions(queue_root, _submission(queue_root, [decision], tmp_path / "submission.json"), ledger_root)
    # The production author-input contract permits only portable identities
    # beneath one binding root.  Queue/ledger live beside this R0 input.
    root = tmp_path
    for name in ("candidate_manifest", "composer_config", "composer_report"):
        _write(root / f"{name}.json", {"name": name})
    source_issue = _issue(code=diagnostic["code"], source_keys=diagnostic["source_keys"],
                          source_pdf_sha256=_candidate_source(candidate)["sha256"])
    draft = root / "r0/draft-pages/page-001.json"
    _write(draft, {"source_page": 1, "markdown": "Old reading", "selected_blocks": [
        {"view": "original_pipeline_txt", "raw_index": 1, "purpose": "text"}],
        "review": {"visual_reviewed": False, "notes": "R0 source choice pending"}})
    spec = root / "r0/spec-00.json"
    _write(spec, {"semantic_structure_profile": "reviewed_role_outline_and_partitions_v2", "pages": [
        {"source_page": 1, "role_contract": {"role": "body", "group_id": "fixture"}, "units": [
            {"id": "body", "kind": "paragraph", "representation": "paragraph", "raw_indices": [1],
             "start": "Old reading", "end": "Old reading"}]}], "ocr_equivalence_classes": []})
    bindings = {name: {"path": f"{name}.json", **file_identity(root / f"{name}.json")}
                for name in ("candidate_manifest", "composer_config", "composer_report")}
    bindings["input_00"] = {"path": "r0/spec-00.json", **file_identity(spec)}
    bindings["draft_page-001"] = {"path": "r0/draft-pages/page-001.json", **file_identity(draft)}
    issues = [source_issue]
    if structural:
        issues.append({"issue_id": "structural-001", "kind": "source_structure_role_pending",
            "reason": "Source views disagree about this exact occurrence", "source_pdf_sha256": source_issue["source_pdf_sha256"],
            "source_page": 1, "source_selector": {"comparison_structural_role_v1": {
                "selected_source_key": {"view": "original_pipeline_txt", "raw_index": 1},
                "provisional_selection_purpose": "text", "provisional_block_type": "paragraph",
                "comparison_records": [{"pair_name": "original_pipeline_txt__vs__original_pipeline_ocr",
                    "semantic_conflict_index": 0, "record_sha256": "A" * 64}]}},
            "source_excerpt_en": "Old reading", "source_excerpt_sha256": hashlib.sha256(b"Old reading").hexdigest().upper(),
            "evidence": [{"kind": "fixture"}], "candidate_span": {"binding": "ordered_selected_source_v1",
                "source_page": 1, "source_key": {"view": "original_pipeline_txt", "raw_index": 1}}, "state": "open"})
    value = {"schema": "kb_creator.review_draft_input.v1", "bindings": bindings,
             "source_issues": {"schema": "kb_creator.review_draft_source_issues.v1", "issues": issues},
             "unresolved_dispositions": []}
    value["input_sha256"] = sha256_bytes(canonical_bytes(value))
    input_path = root / "r0/review-draft-input.json"; _write(input_path, value)
    return root, input_path, ledger_root / "SOURCE_CHOICE_LEDGER.v1.json", draft.parent, [spec]


def test_prepares_verified_ledger_bound_r1_successor(monkeypatch, tmp_path):
    root, r0_input, ledger, drafts, specs = _route(tmp_path, monkeypatch)
    result = prepare_source_choice_successor(input_path=r0_input, binding_root=root, ledger_path=ledger,
        draft_pages=drafts, spec_paths=specs, output_dir=root / "r1")
    assert result["state"] == "sealed_source_choice_successor"
    successor = json.loads((root / "r1/review-draft-input.json").read_text(encoding="utf-8"))
    assert validate_review_draft_input(successor).source_issues == []
    assert validate_review_draft_author_input(input_path=root / "r1/review-draft-input.json", binding_root=root)["state"] == "sealed_author_input"
    assert set(("source_choice_predecessor", "source_choice_ledger", "source_choice_queue")) <= set(successor["bindings"])
    draft = json.loads((root / "r1/draft-pages/page-001.json").read_text(encoding="utf-8"))
    # The new spec owns the replacement.  The successor draft remains an
    # exact R0 source-selection preimage so frozen authoring applies it once.
    assert draft["markdown"] == "Old reading"
    assert draft["review"]["visual_reviewed"] is False
    spec = json.loads((root / "r1/author-specs/spec-00.json").read_text(encoding="utf-8"))
    row = spec["pages"][0]
    assert row["units"][0]["start"] == "New reading"
    correction = row["linguistic_source_choice_corrections"][0]
    assert correction["ledger"] == str(ledger.resolve())
    assert row["patches"] == [{"before": "Old reading", "after": "New reading", "count": 1}]
    # This is the frozen downstream authority adapter, reopened against the
    # actual sealed queue and ledger rather than a test-only replacement.
    rows = {("original_pipeline_txt", 1): {"text": "Old reading"}}
    materialized = {**correction, "authority": "linguistic_source_choice",
                    "ledger": {"path": str(ledger.resolve()), **file_identity(ledger)},
                    "original_text_sha256": hashlib.sha256(b"Old reading").hexdigest().upper()}
    assert linguistic_choice_corrections({"linguistic_source_choice_corrections": [materialized]}, rows,
        {("original_pipeline_txt", 1)}, 1) == {("original_pipeline_txt", 1): [("Old reading", "New reading")]}


def test_retains_structural_source_evidence_while_successor_spec_changes_reader_text(monkeypatch, tmp_path):
    root, r0_input, ledger, drafts, specs = _route(tmp_path, monkeypatch, structural=True)
    prepare_source_choice_successor(input_path=r0_input, binding_root=root, ledger_path=ledger,
        draft_pages=drafts, spec_paths=specs, output_dir=root / "r1")
    successor = json.loads((root / "r1/review-draft-input.json").read_text(encoding="utf-8"))
    structural = successor["source_issues"]["issues"]
    assert structural == [json.loads(r0_input.read_text(encoding="utf-8"))["source_issues"]["issues"][1]]
    # The changed reader text is deliberately carried by the successor spec,
    # while the retained issue continues to identify immutable source evidence.
    assert json.loads((root / "r1/author-specs/spec-00.json").read_text(encoding="utf-8"))["pages"][0]["units"][0]["start"] == "New reading"


def test_retained_semantic_choice_becomes_semantic_uncertainty(monkeypatch, tmp_path):
    root, r0_input, ledger, drafts, specs = _route(tmp_path, monkeypatch, retained_semantic=True)
    result = prepare_source_choice_successor(input_path=r0_input, binding_root=root, ledger_path=ledger,
        draft_pages=drafts, spec_paths=specs, output_dir=root / "r1")
    issue = json.loads((root / "r1/review-draft-input.json").read_text(encoding="utf-8"))["source_issues"]["issues"][0]
    assert result["resolved_choice_count"] == 0
    assert result["retained_semantic_choice_count"] == 1
    assert issue["kind"] == "semantic_source_uncertainty"
    assert issue["reason"] == "Retained source choice (Проверить смысл): semantic meaning remains ambiguous"
    assert issue["evidence"][-1] == {"kind": "source_choice_ledger_retention_v1",
        "ledger_binding": "source_choice_ledger", "reason": "semantic meaning remains ambiguous", "label": "Проверить смысл"}


def test_preserves_ordinary_prose_and_shifts_later_line_selector():
    from kb_creator.pipeline.source_choice_successor_preparation import _patch_spec
    spec = {"pages": [{"source_page": 4, "units": [
        {"id": "heading", "raw_indices": [3], "start_line": 1, "end_line": 1},
        {"id": "later", "raw_indices": [7], "start_line": 5, "end_line": 5},
    ]}]}
    result = _patch_spec(spec, 4, ("original_pipeline_txt", 4), "ordinary prose", "ordinary\nprose",
        Path("C:/ledger.json"), "choice-004", "alt-004", "# Heading\n\nordinary prose\n\nLater")
    assert result == "# Heading\n\nordinary\nprose\n\nLater"
    assert spec["pages"][0]["units"] == [
        {"id": "heading", "raw_indices": [3], "start_line": 1, "end_line": 1},
        {"id": "later", "raw_indices": [7], "start_line": 6, "end_line": 6},
    ]


@pytest.mark.parametrize("damage", ["free_text", "wrong_selector", "ledger_drift"])
def test_rejects_unbound_or_drifted_choice(monkeypatch, tmp_path, damage):
    root, r0_input, ledger, drafts, specs = _route(tmp_path, monkeypatch)
    if damage == "free_text":
        draft = json.loads((drafts / "page-001.json").read_text(encoding="utf-8")); draft["markdown"] = "Forged reading"
        _write(drafts / "page-001.json", draft)
        value = json.loads(r0_input.read_text(encoding="utf-8")); value["bindings"]["draft_page-001"] = {"path": "r0/draft-pages/page-001.json", **file_identity(drafts / "page-001.json")}; value["input_sha256"] = sha256_bytes(canonical_bytes({key: value[key] for key in value if key != "input_sha256"})); _write(r0_input, value)
    elif damage == "wrong_selector":
        value = json.loads(r0_input.read_text(encoding="utf-8")); value["source_issues"]["issues"][0]["source_selector"]["mechanical_diagnostic"]["source_keys"] = [{"view": VIEWS[1], "raw_index": 1}]
        value["input_sha256"] = sha256_bytes(canonical_bytes({key: value[key] for key in value if key != "input_sha256"})); _write(r0_input, value)
    else:
        value = json.loads(ledger.read_text(encoding="utf-8")); value["ledger_sha256"] = "0" * 64; _write(ledger, value)
    with pytest.raises((SourceChoiceSuccessorPreparationError, ValueError)):
        prepare_source_choice_successor(input_path=r0_input, binding_root=root, ledger_path=ledger,
            draft_pages=drafts, spec_paths=specs, output_dir=root / "r1")
