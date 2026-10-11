import json
from pathlib import Path

import pytest

from kb_creator.pipeline import staging_ledger_rebind as module
from kb_creator.pipeline.identity import file_identity


def write(root, rel, value):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value), encoding="utf-8")
    return {"path": rel, **file_identity(p)}


def setup_case(tmp_path, monkeypatch):
    prior, target, review = (tmp_path / p for p in ("prior", "target", "review"))
    for p in (prior, target, review): p.mkdir()
    packet_rel = "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    packet = write(prior, packet_rel, {"source_page": 1})
    write(target, packet_rel, {"source_page": 1})
    visual = write(prior, "visual.png", "same bytes")
    write(target, "visual.png", "same bytes")
    queue = {"schema": "fixture", "source_sha256": "A" * 64,
             "items": [{"source_page": 1, "merge_packet": {**packet, "path": "merge_packets/pages/page-001.json"}}],
             "run_identity_sha256": "OLD"}
    old_queue = write(prior, "review/review_queue.json", queue)
    write(target, "review/review_queue.json", {**queue, "run_identity_sha256": "NEW"})
    ledger = {"schema": module.staging.LEDGER_SCHEMA,
              "bindings": {"source_sha256": "A" * 64, "target_queue": old_queue,
                           "semantic_specs": [write(review, "spec.json", {"pages": [1]})]},
              "pages": [{"source_page": 1, "target_packet": packet, "target_visual": visual,
                         "reviewed_draft": write(review, "draft.json", {"unresolved": ["hold"]}),
                         "review_receipt": write(review, "review.json", {"visual_reviewed": False}),
                         "resolutions": [{"action": "retain_unresolved"}]}]}
    write(review, "ledger.json", ledger)
    calls = []
    monkeypatch.setattr(module, "_authorities", lambda *args: calls.append(args))
    return dict(prior_run=prior, target_run=target, ledger_path=review / "ledger.json", review_root=review), calls


def test_only_queue_provenance_changes_and_authority_is_mandatory(tmp_path, monkeypatch):
    args, calls = setup_case(tmp_path, monkeypatch)
    before = args["ledger_path"].read_bytes()
    old = json.loads(before)
    new, report = module.rebind_staging_ledger(**args)
    assert len(calls) == 1
    assert report["state"] == "candidate_only" and report["approval_transferred"] is False
    assert new["pages"] == old["pages"]
    new["bindings"]["target_queue"] = old["bindings"]["target_queue"]
    assert new == old and args["ledger_path"].read_bytes() == before


@pytest.mark.parametrize("changed", ["packet", "visual", "queue", "draft", "spec"])
def test_rejects_changed_evidence(tmp_path, monkeypatch, changed):
    args, _ = setup_case(tmp_path, monkeypatch)
    paths = {"packet": args["target_run"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json",
             "visual": args["target_run"] / "visual.png", "queue": args["target_run"] / "review/review_queue.json",
             "draft": args["review_root"] / "draft.json", "spec": args["review_root"] / "spec.json"}
    paths[changed].write_text('{"changed":true}', encoding="utf-8")
    with pytest.raises(ValueError): module.rebind_staging_ledger(**args)


def test_authority_failure_cannot_be_bypassed(tmp_path, monkeypatch):
    args, _ = setup_case(tmp_path, monkeypatch)
    def fail(*_): raise ValueError("stale producer")
    monkeypatch.setattr(module, "_authorities", fail)
    with pytest.raises(ValueError, match="stale producer"):
        module.rebind_staging_ledger(**args)
