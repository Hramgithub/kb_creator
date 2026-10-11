from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil

import pytest

from kb_creator.pipeline import reviewed_draft_staging as staging
from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline.review_draft import (
    INPUT_SCHEMA, ISSUES_SCHEMA, prepare_review_draft_staging_successor,
)
from kb_creator.scripts import author_reviewed_semantic_decisions as author

FIXTURE = Path(__file__).parent / "fixtures/reviewed_staging"


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _identity(path, root):
    return {"path": path.relative_to(root).as_posix(), **file_identity(path)}


def _fixture(tmp_path, monkeypatch):
    root = tmp_path / "case"; root.mkdir(parents=True)
    candidate, target, review = (root / name for name in ("candidate", "target", "review"))
    candidate.mkdir(); target.mkdir(); review.mkdir()
    page = json.loads((FIXTURE / "candidate-page-001.json").read_text())
    packet = json.loads((FIXTURE / "packet-page-001.json").read_text())
    cp = _write(candidate / "pages/page-001.json", page)
    pp = _write(target / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json", packet)
    visual = target / "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    visual.parent.mkdir(parents=True); visual.write_bytes(b"synthetic visual identity")
    visual_record = _identity(visual, target)
    source_sha = "A" * 64
    queue = {"source_sha256": source_sha, "items": [{"source_page": 1, "contract_role": "body",
              "merge_packet": {"path": "merge_packets/pages/page-001.json", **file_identity(pp)}}]}
    qp = _write(target / "review/review_queue.json", queue)
    manifest = {"authorities": {"source": {"sha256": source_sha}}, "pages": [{
        "source_page": 1, "candidate": _identity(cp, candidate),
        "packet": {"path": "page-001.json", **file_identity(pp)}}]}
    mp = _write(candidate / "mechanical_draft.json", manifest)
    draft = json.loads((FIXTURE / "expected/pages/page-001.json").read_text())
    dp = _write(review / "page-001.json", draft)
    spec = json.loads((FIXTURE / "spec.json").read_text())
    for unit in spec["pages"][0]["units"]:
        unit.update(kind="label", representation="semantic_span")
    sp = _write(review / "spec.json", spec)
    spec_full = staging._compose_specs([sp])
    rp = _write(review / "review.json", {
        "schema": staging.REVIEW_SCHEMA, "source_page": 1, "source_visual": visual_record,
        "draft_sha256": file_identity(dp)["sha256"], "spec_sha256": sha256_bytes(canonical_bytes(spec_full)),
        "visual_reviewed": True, "reviewer": "synthetic test", "notes": "no real book review"})
    selected = {(x["view"], x["raw_index"]) for x in draft["selected_blocks"]}
    resolutions = []
    for entry in page["entries"]:
        chosen = [x for x in entry["source_keys"] if (x["view"], x["raw_index"]) in selected]
        resolutions.append({"ordinal": entry["ordinal"], "source_keys": entry["source_keys"],
                            "action": "selected" if chosen else "excluded_empty",
                            "selected": chosen, "rationale": "synthetic exact component review"})
    ledger = {"schema": staging.LEDGER_SCHEMA, "bindings": {
        "candidate_manifest": _identity(mp, candidate), "source_sha256": source_sha,
        "target_queue": _identity(qp, target), "semantic_specs": [_identity(sp, review)]},
        "pages": [{"source_page": 1, "candidate_page": _identity(cp, candidate),
                   "target_packet": _identity(pp, target), "target_visual": visual_record,
                   "reviewed_draft": _identity(dp, review), "review_receipt": _identity(rp, review),
                   "resolutions": resolutions, "tables": []}]}
    lp = _write(review / "ledger.json", ledger)
    # Only archived-run setup and its visual inventory are synthetic. The real
    # candidate-page, cold-draft and full semantic validators still execute.
    monkeypatch.setattr(staging, "_authority", lambda *args, **kwargs: {"synthetic_authority": True})
    monkeypatch.setattr(author, "_visual_inventory", lambda target: {visual_record["path"]: file_identity(visual)})
    return dict(candidate_dir=candidate, source_run_root=root / "source", target_run_root=target,
                ledger_path=lp, semantic_spec_paths=[sp], review_root=review)


def _ledger(args):
    return json.loads(args["ledger_path"].read_text())


def _save_ledger(args, ledger):
    _write(args["ledger_path"], ledger)


def _rebind_review(args, ledger, *, approve=True):
    root = args["review_root"]; row = ledger["pages"][0]
    dp = root / row["reviewed_draft"]["path"]; rp = root / row["review_receipt"]["path"]
    row["reviewed_draft"] = _identity(dp, root)
    review = json.loads(rp.read_text())
    review.update(draft_sha256=file_identity(dp)["sha256"],
                  spec_sha256=sha256_bytes(canonical_bytes(staging._compose_specs(args["semantic_spec_paths"]))),
                  visual_reviewed=approve)
    _write(rp, review); row["review_receipt"] = _identity(rp, root)
    ledger["bindings"]["semantic_specs"] = [_identity(p, root) for p in args["semantic_spec_paths"]]
    _save_ledger(args, ledger)


def test_ready_preserves_exact_draft_and_passes_real_semantic_gate(tmp_path, monkeypatch):
    args = _fixture(tmp_path, monkeypatch)
    result = staging.stage_reviewed_drafts(**args, destination=tmp_path / "out")
    assert result["state"] == "ready"
    assert result["evidence"]["semantic_validation"]["unit_count"] == 2
    assert sum(len(x["source_keys"]) for x in result["source_key_conservation"]) == 9
    assert json.loads((tmp_path / "out/pages/page-001.json").read_text()) == json.loads((args["review_root"] / "page-001.json").read_text())
    assert (tmp_path / "out/staging-manifest.json").is_file()


def test_covered_reader_accepts_one_meaningful_key_and_empty_companions():
    candidate = {"entries": [{"ordinal": 1, "disposition": "emitted", "source_keys": [
        {"view": "original_pipeline_txt", "raw_index": 1}, {"view": "original_pipeline_ocr", "raw_index": 2}, {"view": "raster_pipeline_ocr", "raw_index": 3}]}]}
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 1, "text": "meaningful"}]}, "original_pipeline_ocr": {"blocks": [{"raw_index": 2, "text": ""}]}, "raster_pipeline_ocr": {"blocks": [{"raw_index": 3, "text": ""}]}}}
    draft = {"selected_blocks": []}
    row = {"ordinal": 1, "source_keys": candidate["entries"][0]["source_keys"], "action": "covered_by_reader", "selected": [], "rationale": "reader proof", "coverage_claim_id": "claim-1", "coverage_source_key": {"view_id": "original_pipeline_txt", "raw_index": 1}, "empty_companion_keys": [{"view_id": "original_pipeline_ocr", "raw_index": 2}, {"view_id": "raster_pipeline_ocr", "raw_index": 3}]}
    evidence, unresolved = staging._conserve(1, candidate, packet, draft, [row], {}, coverage_claims={("original_pipeline_txt", 1): "claim-1"})
    assert not unresolved and evidence[0]["empty_companion_keys"] == row["empty_companion_keys"]


def test_covered_reader_accepts_sealed_pending_companion_partition():
    candidate = {"entries": [{"ordinal": 1, "disposition": "emitted", "source_keys": [
        {"view": "original_pipeline_txt", "raw_index": 1}, {"view": "original_pipeline_ocr", "raw_index": 2}, {"view": "raster_pipeline_ocr", "raw_index": 3}]}]}
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 1, "text": "1D6"}]},
        "original_pipeline_ocr": {"blocks": [{"raw_index": 2, "text": "ID6"}]},
        "raster_pipeline_ocr": {"blocks": [{"raw_index": 3, "text": ""}]}}}
    row = {"ordinal": 1, "source_keys": candidate["entries"][0]["source_keys"], "action": "covered_by_reader",
           "selected": [], "rationale": "sealed source alternative", "coverage_claim_id": "claim-1",
           "coverage_source_key": {"view_id": "original_pipeline_txt", "raw_index": 1},
           "empty_companion_keys": [{"view_id": "raster_pipeline_ocr", "raw_index": 3}],
           "pending_companion_keys": [{"view_id": "original_pipeline_ocr", "raw_index": 2}]}
    evidence, unresolved = staging._conserve(1, candidate, packet, {"selected_blocks": []}, [row], {},
        coverage_claims={("original_pipeline_txt", 1): "claim-1"},
        pending_source_keys={(1, "original_pipeline_ocr", 2)})
    assert not unresolved and evidence[0]["pending_companion_keys"] == row["pending_companion_keys"]
    with pytest.raises(staging.ReviewedDraftStagingError, match="pending companion"):
        staging._conserve(1, candidate, packet, {"selected_blocks": []}, [row], {},
            coverage_claims={("original_pipeline_txt", 1): "claim-1"}, pending_source_keys=set())


def test_successor_producer_partition_is_consumed_without_rewriting_keys(tmp_path):
    canonical = {"view": "original_pipeline_txt", "raw_index": 0}
    component_keys = [
        {"view": view, "raw_index": 1}
        for view in ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")
    ]
    candidate = {"entries": [
        {"ordinal": 0, "disposition": "emitted", "source_keys": [canonical]},
        {"ordinal": 1, "disposition": "emitted", "source_keys": component_keys},
    ]}
    packet = {"views": {
        "original_pipeline_txt": {"blocks": [
            {"raw_index": 0, "text": "Aggregate with line"},
            {"raw_index": 1, "text": "line"},
        ]},
        "original_pipeline_ocr": {"blocks": [{"raw_index": 1, "text": ""}]},
        "raster_pipeline_ocr": {"blocks": [{"raw_index": 1, "text": ""}]},
    }}
    draft = {"source_page": 1, "markdown": "Aggregate with line",
             "review": {"visual_reviewed": False},
             "selected_blocks": [{**canonical, "purpose": "text"}]}
    candidate_dir, semantic_dir = tmp_path / "candidate", tmp_path / "semantic"
    cp = _write(candidate_dir / "pages/page-001.json", candidate)
    _write(candidate_dir / "mechanical_draft.json", {"pages": [
        {"source_page": 1, "candidate": _identity(cp, candidate_dir)},
    ]})
    _write(semantic_dir / "page-001.json", draft)
    spec = _write(tmp_path / "spec.json", {"pages": [{"source_page": 1, "units": []}]})
    _write(semantic_dir / "candidate_manifest.json", {
        "pages": [{"source_page": 1, "path": "page-001.json"}],
        "inputs": {"specs": [{"path": str(spec), **file_identity(spec)}]},
    })
    prior = _write(tmp_path / "prior.json", {
        "schema": "kb_creator.reviewed_staging_ledger.v2", "bindings": {},
        "pages": [{"source_page": 1, "candidate_page": _identity(cp, candidate_dir),
                   "target_visual": {"path": "synthetic-only.png", "bytes": 0, "sha256": "A" * 64},
                   "resolutions": [
                       {"ordinal": 0, "source_keys": [canonical], "selected": [canonical],
                        "action": "selected", "rationale": "canonical aggregate"},
                       {"ordinal": 1, "source_keys": component_keys, "selected": [],
                        "action": "retain_unresolved", "rationale": "needs coverage"},
                   ]}],
    })
    meaningful = {"view_id": "original_pipeline_txt", "raw_index": 1}
    companions = [{"view_id": row["view"], "raw_index": row["raw_index"]}
                  for row in component_keys[1:]]
    proposal = _write(tmp_path / "proposal.json", {
        "schema": "kb_creator.book_coverage_ownership_proposal.v1", "rows": [{
            "source_page": 1, "component_ordinal": 1,
            "proposed_action": "covered_by_reader", "old_action": "retain_unresolved",
            "source_keys": component_keys, "meaningful_key": meaningful,
            "empty_companion_keys": companions,
            "fidelity_owner": {"kind": "coverage_claim", "claim_id": "claim-1"},
        }],
    })
    before = prior.read_bytes()
    result = prepare_review_draft_staging_successor(
        candidate_dir=candidate_dir, prior_ledger_path=prior,
        semantic_candidate_dir=semantic_dir, semantic_specs=[spec],
        ownership_proposal=proposal, source_dispositions=_write(tmp_path / "dispositions.json", []),
        destination=tmp_path / "successor", binding_root=tmp_path,
    )
    ledger = json.loads(Path(result["ledger"]["path"]).read_text())
    # Exercise the exact producer output, including its view_id key spelling.
    evidence, unresolved = staging._conserve(
        1, candidate, packet, draft, ledger["pages"][0]["resolutions"], {},
        coverage_claims={("original_pipeline_txt", 1): "claim-1"},
    )
    assert not unresolved
    assert evidence[1]["coverage_source_key"] == meaningful
    assert evidence[1]["empty_companion_keys"] == companions
    assert prior.read_bytes() == before
    receipt = json.loads((tmp_path / "successor/reviews/page-001.json").read_text())
    assert receipt["visual_reviewed"] is False


@pytest.mark.parametrize("malformation", ["none", "object", "wrong_action", "mixed_key"])
def test_covered_reader_rejects_malformed_partition_even_without_companions(malformation):
    key = {"view": "original_pipeline_txt", "raw_index": 1}
    candidate = {"entries": [{"ordinal": 1, "disposition": "emitted", "source_keys": [key]}]}
    packet = {"views": {
        "original_pipeline_txt": {"blocks": [{"raw_index": 1, "text": "line"}]},
        "original_pipeline_ocr": {"blocks": []}, "raster_pipeline_ocr": {"blocks": []},
    }}
    row = {"ordinal": 1, "source_keys": [key], "selected": [], "rationale": "coverage",
           "action": "covered_by_reader", "coverage_claim_id": "claim-1",
           "coverage_source_key": {"view_id": "original_pipeline_txt", "raw_index": 1},
           "empty_companion_keys": []}
    if malformation == "none":
        row["empty_companion_keys"] = None
    elif malformation == "object":
        row["empty_companion_keys"] = {}
    elif malformation == "wrong_action":
        row["action"] = "retain_unresolved"
    else:
        row["coverage_source_key"]["view"] = "original_pipeline_txt"
    with pytest.raises(staging.ReviewedDraftStagingError):
        staging._conserve(1, candidate, packet, {"selected_blocks": []}, [row], {},
                          coverage_claims={("original_pipeline_txt", 1): "claim-1"})


def test_legacy_covered_reader_preserves_evidence_shape():
    key = {"view": "original_pipeline_txt", "raw_index": 1}
    candidate = {"entries": [{"ordinal": 1, "disposition": "emitted", "source_keys": [key]}]}
    packet = {"views": {
        "original_pipeline_txt": {"blocks": [{"raw_index": 1, "text": "line"}]},
        "original_pipeline_ocr": {"blocks": []}, "raster_pipeline_ocr": {"blocks": []},
    }}
    row = {"ordinal": 1, "source_keys": [key], "action": "covered_by_reader",
           "selected": [], "rationale": "legacy coverage", "coverage_claim_id": "claim-1"}
    evidence, unresolved = staging._conserve(
        1, candidate, packet, {"selected_blocks": []}, [row], {},
        coverage_claims={("original_pipeline_txt", 1): "claim-1"},
    )
    assert not unresolved
    assert evidence == [{"source_page": 1, "ordinal": 1, "machine_disposition": "emitted",
                         "source_keys": [("original_pipeline_txt", 1)], "selected": [],
                         "action": "covered_by_reader", "rationale": "legacy coverage"}]


@pytest.mark.parametrize("mutation", ["text", "assets", "table", "duplicate", "missing", "extra", "wrong_owner"])
def test_covered_reader_rejects_fake_empty_or_bad_partition(mutation):
    candidate = {"entries": [{"ordinal": 1, "disposition": "emitted", "source_keys": [{"view": "original_pipeline_txt", "raw_index": 1}, {"view": "original_pipeline_ocr", "raw_index": 2}]}]}
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 1, "text": "meaningful"}]}, "original_pipeline_ocr": {"blocks": [{"raw_index": 2, "text": ""}]}, "raster_pipeline_ocr": {"blocks": []}}}
    companions = [{"view": "original_pipeline_ocr", "raw_index": 2}]
    if mutation == "text": packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "forged"
    elif mutation == "assets": packet["views"]["original_pipeline_ocr"]["blocks"][0]["assets"] = ["x.png"]
    elif mutation == "table": packet["views"]["original_pipeline_ocr"]["blocks"][0]["table_body"] = [["x"]]
    elif mutation == "duplicate": companions *= 2
    elif mutation == "missing": companions = []
    elif mutation == "extra": companions.append({"view": "original_pipeline_txt", "raw_index": 1})
    companions = [{"view_id": item.get("view"), "raw_index": item["raw_index"]} for item in companions]
    row = {"ordinal": 1, "source_keys": candidate["entries"][0]["source_keys"], "action": "covered_by_reader", "selected": [], "rationale": "reader proof", "coverage_claim_id": "claim-1", "coverage_source_key": {"view_id": "original_pipeline_txt", "raw_index": 1}, "empty_companion_keys": companions}
    claims = {("original_pipeline_txt", 1): "wrong" if mutation == "wrong_owner" else "claim-1"}
    with pytest.raises(staging.ReviewedDraftStagingError):
        staging._conserve(1, candidate, packet, {"selected_blocks": []}, [row], {}, coverage_claims=claims)


def test_production_cannot_skip_absent_run_authority(tmp_path, monkeypatch):
    real_authority = staging._authority
    args = _fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(staging, "_authority", real_authority)
    with pytest.raises(staging.ReviewedDraftStagingError, match="run authority"):
        staging.stage_reviewed_drafts(**args, destination=tmp_path / "out")
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("field", ["reviewed_draft", "target_packet", "target_visual", "candidate_page", "review_receipt"])
def test_changed_bound_artifact_is_rejected_before_output(tmp_path, monkeypatch, field):
    args = _fixture(tmp_path, monkeypatch); ledger = _ledger(args); row = ledger["pages"][0]
    root = args["candidate_dir"] if field == "candidate_page" else args["target_run_root"] if field.startswith("target") else args["review_root"]
    path = root / row[field]["path"]; path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError):
        staging.stage_reviewed_drafts(**args, destination=tmp_path / "out")
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("mutation", ["duplicate_key", "missing_key", "missing_component", "wrong_selection", "unknown_action"])
def test_source_conservation_rejects_invalid_component_decisions(tmp_path, monkeypatch, mutation):
    args = _fixture(tmp_path, monkeypatch); ledger = _ledger(args); rows = ledger["pages"][0]["resolutions"]
    if mutation == "duplicate_key": rows[0]["source_keys"].append(rows[0]["source_keys"][0])
    elif mutation == "missing_key": rows[0]["source_keys"].pop()
    elif mutation == "missing_component": rows.pop()
    elif mutation == "wrong_selection": rows[0]["selected"] = []
    else: rows[0]["action"] = "accept_everything"
    _save_ledger(args, ledger)
    with pytest.raises(ValueError): staging.validate_reviewed_staging_inputs(**args)


def test_unresolved_component_or_unreviewed_page_emits_only_gap_report(tmp_path, monkeypatch):
    args = _fixture(tmp_path, monkeypatch); ledger = _ledger(args)
    ledger["pages"][0]["resolutions"][1]["action"] = "retain_unresolved"; _save_ledger(args, ledger)
    result = staging.stage_reviewed_drafts(**args, destination=tmp_path / "out")
    assert result["gaps"] == {1: ["unresolved_component"]}
    assert not (tmp_path / "out/pages").exists()
    ledger["pages"][0]["resolutions"][1]["action"] = "selected"
    _rebind_review(args, ledger, approve=False)
    assert staging.validate_reviewed_staging_inputs(**args).gaps == {1: ["unreviewed_final_page"]}


def test_review_draft_preflight_keeps_false_visual_flag_and_requires_sealed_input(tmp_path, monkeypatch):
    args = _fixture(tmp_path, monkeypatch); ledger = _ledger(args)
    draft_path = args["review_root"] / "page-001.json"
    draft = json.loads(draft_path.read_text()); draft["review"]["visual_reviewed"] = False; _write(draft_path, draft)
    _rebind_review(args, ledger, approve=False)
    value = {
        "schema": INPUT_SCHEMA,
        "bindings": {"candidate": {"path": "candidate/manifest.json", "bytes": 1, "sha256": "A" * 64}},
        "source_issues": {"schema": ISSUES_SCHEMA, "issues": []},
        "unresolved_dispositions": [{"source_page": 1, "predecessor_unresolved": "Stage05 audit pending", "category": "administrative_pending", "outcome": "audit_pending", "evidence": [{"path": "proposal.json", "bytes": 1, "sha256": "B" * 64}], "predecessor": {"path": "old/page-001.json", "bytes": 1, "sha256": "C" * 64}, "current": {"path": "new/page-001.json", "bytes": 1, "sha256": "D" * 64}}],
    }
    value["input_sha256"] = sha256_bytes(canonical_bytes(value))
    input_path = _write(args["review_root"] / "review-draft-input.json", value)
    result = staging.validate_reviewed_staging_inputs(**args, mode="review_draft", draft_input=input_path)
    assert result.state == "prepared_for_audit"
    assert result.evidence["visual_reviewed_false_pages"] == [1]


def test_covered_by_reader_requires_one_recomputed_claim_for_every_nonselected_source_key():
    packet = {"views": {view: {"blocks": [
        {"raw_index": 0, "text": "reader text", "assets": [], "table_body": []},
        {"raw_index": 1, "text": "continued text", "assets": [], "table_body": []},
    ]} for view in staging.mechanical_reconstruction.VIEWS}}
    source_keys = lambda raw: [{"view": view, "raw_index": raw} for view in staging.mechanical_reconstruction.VIEWS]
    candidate = {"entries": [
        {"ordinal": 0, "source_keys": source_keys(0), "disposition": "selected"},
        {"ordinal": 1, "source_keys": source_keys(1), "disposition": "continuation"},
    ]}
    draft = {"selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0}]}
    resolutions = [
        {"ordinal": 0, "source_keys": source_keys(0), "action": "selected", "selected": [{"view": "original_pipeline_txt", "raw_index": 0}], "rationale": "reader canonical"},
        {"ordinal": 1, "source_keys": source_keys(1), "action": "covered_by_reader", "coverage_claim_id": "continuation-1", "selected": [], "rationale": "adjacent reader span"},
    ]
    coverage = {(view, 1): "continuation-1" for view in staging.mechanical_reconstruction.VIEWS}
    rows, unresolved = staging._conserve(1, candidate, packet, draft, resolutions, {"source_text_exclusions": []}, coverage_claims=coverage)
    assert not unresolved and rows[1]["action"] == "covered_by_reader"
    coverage["original_pipeline_txt", 1] = "other"
    with pytest.raises(staging.ReviewedDraftStagingError, match="uniquely own"):
        staging._conserve(1, candidate, packet, draft, resolutions, {"source_text_exclusions": []}, coverage_claims=coverage)


def test_reviewed_correction_uses_exact_text_and_existing_semantic_binding(tmp_path, monkeypatch):
    args = _fixture(tmp_path, monkeypatch); root = args["review_root"]; ledger = _ledger(args)
    draft = json.loads((root / "page-001.json").read_text()); draft["markdown"] = "Synthetic paragraph\n\nBeta repaired"
    _write(root / "page-001.json", draft)
    spec = json.loads((root / "spec.json").read_text())
    spec["pages"][0]["units"][1].update(start="Beta repaired", end="Beta repaired")
    spec["pages"][0]["reviewed_block_corrections"] = [{
        "view": "original_pipeline_ocr", "raw_index": 1, "before": "Beta",
        "after": "Beta repaired", "reason": "synthetic source review"}]
    _write(root / "spec.json", spec); _rebind_review(args, ledger)
    result = staging.validate_reviewed_staging_inputs(**args)
    assert result.state == "ready" and result.pages[1]["markdown"].endswith("Beta repaired")


def test_stale_semantic_selector_fails_even_with_fresh_review_hash(tmp_path, monkeypatch):
    args = _fixture(tmp_path, monkeypatch); ledger = _ledger(args)
    path = args["review_root"] / "spec.json"; spec = json.loads(path.read_text())
    spec["pages"][0]["units"][1]["raw_indices"] = [999]
    _write(path, spec); _rebind_review(args, ledger)
    with pytest.raises(ValueError, match="raw index missing"):
        staging.stage_reviewed_drafts(**args, destination=tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_ocr_equivalence_and_source_only_selectors_are_not_dropped(tmp_path, monkeypatch):
    args = _fixture(tmp_path, monkeypatch)
    path = args["semantic_spec_paths"][0]; spec = json.loads(path.read_text())
    spec["ocr_equivalence_classes"] = [{"class_id": "keep-this-selector"}]
    spec["visual_text_assertions"] = [{"assertion_id": "retained-source-fact"}]
    _write(path, spec)
    composed = staging._compose_specs([path])
    assert composed["ocr_equivalence_classes"] == spec["ocr_equivalence_classes"]
    assert composed["visual_text_assertions"] == spec["visual_text_assertions"]


def test_traversal_and_stale_final_review_are_rejected(tmp_path, monkeypatch):
    args = _fixture(tmp_path, monkeypatch); ledger = _ledger(args); good = copy.deepcopy(ledger)
    ledger["pages"][0]["reviewed_draft"]["path"] = "../review/page-001.json"; _save_ledger(args, ledger)
    with pytest.raises(ValueError, match="escapes"):
        staging.validate_reviewed_staging_inputs(**args)
    _save_ledger(args, good)
    rp = args["review_root"] / "review.json"; review = json.loads(rp.read_text())
    review["draft_sha256"] = "0" * 64; _write(rp, review)
    good["pages"][0]["review_receipt"] = _identity(rp, args["review_root"]); _save_ledger(args, good)
    with pytest.raises(ValueError, match="final draft"):
        staging.validate_reviewed_staging_inputs(**args)
