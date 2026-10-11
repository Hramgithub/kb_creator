"""Wrapper control flow plus compact actual Stage05/Stage06 verifier coverage.

Control tests replace runtime/API dispatch, never assert real book fidelity.
The integration test uses the existing one-page fixture, whose archive/queue
boundary is stubbed; verification, rendering and Stage05/Stage06 are real.
"""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

from kb_creator.pipeline import review_source_continuation as bridge
from kb_creator.pipeline.identity import deterministic_inventory, file_identity, sha256_bytes
from kb_creator.pipeline.manifests import sealed, validate_seal
from kb_creator.pipeline.review_draft import finalize_review_draft_evidence
from kb_creator.pipeline.review_draft_materialization import SCHEMA


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def fixture_module(filename):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location("continuation_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def request_for(root, run, authored, input_path, evidence_path, pages):
    authorities = {}
    for name in bridge.AUTHORITY:
        path = root / "authorities" / (name + ".json")
        write(path, {"name": name})
        authorities[name] = bridge.record(path)
    runtime = root / "runtime"
    manifest = write(runtime / "manifest.json", {"files": []})
    request = {"operation": "verify", "binding_root": str(root), "run_root": str(run),
        "authored_root": str(authored), "input": bridge.record(input_path),
        "evidence": bridge.record(evidence_path), "expected_pages": pages,
        "runtime": {"root": str(runtime), "manifest": bridge.record(manifest),
                    "executable": bridge.record(Path(sys.executable)), "dependencies": []},
        "authority_files": authorities,
        "authority_inventories": [{"root": str(path), "files": deterministic_inventory(path)}
                                  for path in (run, authored)],
        "output_root": str(root / "verified")}
    return sealed(bridge.REQUEST_SCHEMA, request, digest_key="request_sha256")


def save_request(root, value, name="request.json"):
    value = deepcopy(value)
    value.pop("request_sha256", None)
    return write(root / name, sealed(bridge.REQUEST_SCHEMA, value, digest_key="request_sha256"))


def control_fixture(tmp_path, monkeypatch):
    helper = fixture_module("test_review_draft_structural_successor.py")
    input_path, authored, edits_path = helper._sealed_two_page_predecessor(tmp_path)
    run = tmp_path / "run"
    visual_path = run / "visual.png"; visual_path.write_bytes(b"visual")
    visual = {"path": "visual.png", **file_identity(visual_path)}
    for page in (1, 2):
        path = authored / f"pages/page-{page:03d}.json"
        decision = bridge.read_json(path)
        decision["semantic_structure"]["review"]["visual"] = visual
        write(path, decision)
    decision_set = write(authored / "decision_set.json", {"decisions": [
        {"source_page": p, "path": f"pages/page-{p:03d}.json",
         **file_identity(authored / f"pages/page-{p:03d}.json")} for p in (1, 2)]})
    audit = write(authored / "review-draft-stage05-audit.json", {"passed": True, "errors": []})
    evidence = finalize_review_draft_evidence(bridge.read_json(input_path), authored={
        "decision_set": {"path": decision_set.name, **file_identity(decision_set)},
        "stage05_audit": {"path": audit.name, **file_identity(audit)}},
        audit=bridge.read_json(audit), visual_reviewed_false_pages=[])
    evidence_path = write(authored / "review-draft-evidence.json", evidence)
    for name in ("outputs/04-visual-merge-bundle", "outputs/02-mineru-three-view"):
        (run / name).mkdir(parents=True, exist_ok=True)
    request = request_for(tmp_path, run, authored, input_path, evidence_path, [1, 2])
    request_path = save_request(tmp_path, request)
    records = {}
    for name in ("comparison", "queue"):
        records[name] = bridge.record(write(tmp_path / f"{name}.json", {}))
    def descriptor(**kwargs):
        a, i, e = kwargs["authored_root"], kwargs["input_path"], kwargs["evidence_path"]
        return {"schema": SCHEMA, "state": "verified_review_draft_candidate",
            "bundle_root": str(run / "outputs/04-visual-merge-bundle"),
            "raw_root": str(run / "outputs/02-mineru-three-view"), "decisions_root": str(a / "pages"),
            "input": bridge.record(i), "final_evidence": bridge.record(e),
            "audit": bridge.record(a / "review-draft-stage05-audit.json"),
            "source": request["authority_files"]["source"], "renderer": request["authority_files"]["renderer"],
            "comparison": records["comparison"], "review_queue": records["queue"],
            "pages": [{"source_page": p, **file_identity(a / f"pages/page-{p:03d}.json")} for p in (1, 2)],
            "assets": [], "reference_proof_keys": [], "split_structure_proof_keys": []}
    calls = []
    def verify(**kwargs):
        calls.append(("verify", kwargs))
        return descriptor(**kwargs)
    operations = {"verify_final_review_draft": verify}
    monkeypatch.setattr(bridge, "_runtime", lambda unused: None)
    monkeypatch.setattr(bridge, "_operations", lambda unused: operations)
    return request_path, request, operations, calls, helper, edits_path


def structural_request(root, request_path, request, edits_path):
    original = bridge.read_json(edits_path)
    sidecar = bridge.read_json(edits_path.parent / "marker-dispositions.json")
    for collection in ("candidates", "dispositions"):
        for row in sidecar[collection]:
            row["visual"] = {"path": "run/visual.png", **file_identity(root / "run/visual.png")}
    proposal = {"normal_api_edit_sections": {
        "schema": original["schema"], "source_marker_dispositions_sidecar_proposal": sidecar,
        **{name: original[name] for name in ("structural_post_patches", "retained_owner_assertions", "page_units")}}}
    proposal_path = write(root / "proposal.json", proposal)
    projection_path = write(root / "projection.json", {"parents": [{"path": "proposal.json", **file_identity(proposal_path)}],
        "post_ledger_page_projections": [{"source_page": p, "projected_post_ledger_markdown_sha256":
            sha256_bytes(bridge.read_json(root / f"authored/pages/page-{p:03d}.json")["markdown"].encode())}
            for p in (1, 2)]})
    value = {**request, "operation": "structural", "output_root": str(root / "structural"),
        "verification_receipt": bridge.record(root / "verified/receipt.json"),
        "verification_request": bridge.record(request_path),
        "proposal": bridge.record(proposal_path), "projection": bridge.record(projection_path),
        "review_root": str(root), "excluded_owner_pages": [2]}
    return save_request(root, value, "structural-request.json")


def test_verify_argument_propagation_and_unchanged_closed_descriptor(tmp_path, monkeypatch):
    path, request, _, calls, *_ = control_fixture(tmp_path, monkeypatch)
    receipt = bridge.verify_authored_source(path)
    assert calls == [("verify", {"run_root": tmp_path / "run", "authored_root": tmp_path / "authored",
        "input_path": Path(request["input"]["path"]), "evidence_path": Path(request["evidence"]["path"]),
        "binding_root": tmp_path})]
    assert receipt["accepted"] is False
    assert receipt["inventory_before"] == receipt["inventory_after"]
    validate_seal(receipt, "receipt_sha256")
    assert bridge.read_json(tmp_path / "verified/descriptor.json")["schema"] == SCHEMA
    assert "runtime" not in bridge.read_json(tmp_path / "verified/descriptor.json")


@pytest.mark.parametrize("target", ["input", "evidence", "runtime", "decision", "archive", "authority"])
def test_stale_verification_dependencies_rejected_before_output(tmp_path, monkeypatch, target):
    path, request, _, calls, *_ = control_fixture(tmp_path, monkeypatch)
    changed = {"input": Path(request["input"]["path"]), "evidence": Path(request["evidence"]["path"]),
        "runtime": tmp_path / "runtime/manifest.json", "decision": tmp_path / "authored/pages/page-001.json",
        "archive": tmp_path / "run/visual.png", "authority": Path(request["authority_files"]["exit_observation"]["path"])}[target]
    changed.write_bytes(b"drift")
    # Runtime dispatch is stubbed in these control tests; pin its manifest in authority closure.
    if target == "runtime":
        monkeypatch.setattr(bridge, "_runtime", lambda value: bridge._checked(value["manifest"]))
    with pytest.raises(ValueError):
        bridge.verify_authored_source(path)
    assert not (tmp_path / "verified").exists()
    assert not calls


@pytest.mark.parametrize("behavior", ["raise", "passed_flag", "wrong_descriptor", "drift_on_return"])
def test_failed_api_or_closing_gate_never_emits_success(tmp_path, monkeypatch, behavior):
    path, request, operations, _, *_ = control_fixture(tmp_path, monkeypatch)
    real = operations["verify_final_review_draft"]
    def verify(**kwargs):
        if behavior == "raise":
            raise ValueError("underlying failure")
        if behavior == "passed_flag":
            return {"passed": True}
        value = real(**kwargs)
        if behavior == "wrong_descriptor":
            value["pages"] = [{"source_page": 2, **value["pages"][1]}]
        if behavior == "drift_on_return":
            (tmp_path / "run/visual.png").write_bytes(b"changed while verifying")
        return value
    operations["verify_final_review_draft"] = verify
    with pytest.raises(ValueError):
        bridge.verify_authored_source(path)
    assert not (tmp_path / "verified/receipt.json").exists()
    assert bridge.read_json(tmp_path / "verified/failure.json")["state"] == "failed"


def test_existing_output_and_staging_refuse_overwrite(tmp_path, monkeypatch):
    path, _, _, calls, *_ = control_fixture(tmp_path, monkeypatch)
    staging = tmp_path / ".verified.staging"; staging.mkdir()
    with pytest.raises(ValueError, match="output exists"):
        bridge.verify_authored_source(path)
    staging.rmdir()
    (tmp_path / "verified").mkdir()
    sentinel = tmp_path / "verified/receipt.json"; sentinel.write_bytes(b"predecessor")
    with pytest.raises(ValueError, match="output exists"):
        bridge.verify_authored_source(path)
    assert sentinel.read_bytes() == b"predecessor" and not calls


@pytest.mark.parametrize("target", ["receipt", "input", "evidence", "runtime", "descriptor", "projection", "selected_key", "parent", "visual"])
def test_structural_stale_or_unreviewed_inputs_stop_before_outputs(tmp_path, monkeypatch, target):
    path, request, _, _, _, edits_path = control_fixture(tmp_path, monkeypatch)
    bridge.verify_authored_source(path)
    structural = structural_request(tmp_path, path, request, edits_path)
    value = bridge.read_json(structural)
    if target in {"receipt", "input", "evidence", "runtime", "descriptor"}:
        changed = {"receipt": tmp_path / "verified/receipt.json", "input": Path(request["input"]["path"]),
            "evidence": Path(request["evidence"]["path"]), "runtime": tmp_path / "runtime/manifest.json",
            "descriptor": tmp_path / "verified/descriptor.json"}[target]
        changed.write_bytes(b"stale")
        if target == "runtime":
            monkeypatch.setattr(bridge, "_runtime", lambda runtime: bridge._checked(runtime["manifest"]))
    elif target == "projection":
        projection = bridge.read_json(tmp_path / "projection.json")
        projection["post_ledger_page_projections"][0]["projected_post_ledger_markdown_sha256"] = "A" * 64
        write(tmp_path / "projection.json", projection)
        value["projection"] = bridge.record(tmp_path / "projection.json")
        structural = save_request(tmp_path, value, "structural-request.json")
    elif target == "selected_key":
        proposal = bridge.read_json(tmp_path / "proposal.json")
        proposal["normal_api_edit_sections"]["source_marker_dispositions_sidecar_proposal"]["candidates"][0]["raw_index"] = 999
        write(tmp_path / "proposal.json", proposal)
        projection = bridge.read_json(tmp_path / "projection.json")
        projection["parents"] = [{"path": "proposal.json", **file_identity(tmp_path / "proposal.json")}]
        write(tmp_path / "projection.json", projection)
        value.update(proposal=bridge.record(tmp_path / "proposal.json"), projection=bridge.record(tmp_path / "projection.json"))
        structural = save_request(tmp_path, value, "structural-request.json")
    elif target == "parent":
        (tmp_path / "proposal.json").write_bytes(b"changed parent")
    else:
        (tmp_path / "run/visual.png").write_bytes(b"changed visual")
    with pytest.raises((ValueError, KeyError)):
        bridge.continue_structural_source(structural)
    assert not (tmp_path / "structural").exists()


def structural_control_setup(tmp_path, monkeypatch):
    path, request, operations, calls, helper, edits_path = control_fixture(tmp_path, monkeypatch)
    bridge.verify_authored_source(path)
    structural = structural_request(tmp_path, path, request, edits_path)
    operations["prepare_review_draft_structural_successor"] = helper.prepare_review_draft_structural_successor
    def preflight(*args, **kwargs):
        calls.append(("preflight", args, kwargs))
        return {"page_count": 2, "correction_coverage": {"page_count": 2, "unbound_keys": 0}}
    def author(run, drafts, authored, specs, **kwargs):
        calls.append(("author", run, drafts, authored, specs, kwargs))
        authored.mkdir()
        (authored / "pages").mkdir()
        for page in (1, 2):
            write(authored / f"pages/page-{page:03d}.json", bridge.read_json(drafts / f"page-{page:03d}.json"))
        decision_set = write(authored / "decision_set.json", {"decisions": [
            {"source_page": p, "path": f"pages/page-{p:03d}.json", **file_identity(authored / f"pages/page-{p:03d}.json")} for p in (1, 2)]})
        audit = write(authored / "review-draft-stage05-audit.json", {"passed": True, "errors": []})
        evidence = finalize_review_draft_evidence(bridge.read_json(kwargs["draft_input"]), authored={
            "decision_set": {"path": decision_set.name, **file_identity(decision_set)},
            "stage05_audit": {"path": audit.name, **file_identity(audit)}},
            audit=bridge.read_json(audit), visual_reviewed_false_pages=[])
        write(authored / "review-draft-evidence.json", evidence)
        return {"decisions": [1, 2]}
    def materialize(*args, **kwargs):
        calls.append(("materialize", args, kwargs)); args[3].mkdir()
        return {"status": "verified_review_draft_candidate"}
    def build(*args, **kwargs):
        calls.append(("build", args, kwargs)); args[2].mkdir()
        (args[2] / "MASTER_EN.md").write_text("fixture", encoding="utf-8")
        write(args[2] / "ASSET_MANIFEST.json", {})
        return {"state": "verified_review_draft"}
    operations.update(validate_spec=preflight, author_drafts=author, materialize=materialize, build_review_master_en=build)
    return structural, operations, calls


def test_real_structural_prepare_then_full_gate_argument_propagation(tmp_path, monkeypatch):
    structural, _, calls = structural_control_setup(tmp_path, monkeypatch)
    receipt = bridge.continue_structural_source(structural)
    assert [call[0] for call in calls] == ["verify", "preflight", "author", "verify", "materialize", "build"]
    assert calls[1][1][0] == tmp_path / "run" and calls[1][1][1] is None
    assert calls[1][2]["binding_root"] == tmp_path
    assert calls[2][-1]["mode"] == "review_draft"
    assert calls[3][1]["authored_root"] == tmp_path / "structural/authored"
    assert calls[4][2]["review_draft_authority"]["schema"] == SCHEMA
    assert calls[5][2] == {"binding_root": tmp_path}
    assert receipt["operation"] == "structural_continuation" and receipt["accepted"] is False
    assert receipt["predecessor_receipt"] == bridge.record(tmp_path / "verified/receipt.json")


@pytest.mark.parametrize("stage", ["prepare_review_draft_structural_successor", "validate_spec", "author_drafts",
                                   "verify_final_review_draft", "materialize", "build_review_master_en"])
def test_each_structural_api_failure_never_emits_success(tmp_path, monkeypatch, stage):
    structural, operations, _ = structural_control_setup(tmp_path, monkeypatch)
    def fail(*args, **kwargs):
        raise ValueError("operation failure: " + stage)
    operations[stage] = fail
    with pytest.raises(ValueError, match="operation failure"):
        bridge.continue_structural_source(structural)
    assert not (tmp_path / "structural/receipt.json").exists()
    assert bridge.read_json(tmp_path / "structural/failure.json")["state"] == "failed"


@pytest.mark.parametrize("stage", ["materialize", "build_review_master_en"])
def test_structural_passed_flag_is_not_real_result(tmp_path, monkeypatch, stage):
    structural, operations, _ = structural_control_setup(tmp_path, monkeypatch)
    operations[stage] = lambda *args, **kwargs: {"passed": True}
    with pytest.raises(ValueError, match="did not return verified"):
        bridge.continue_structural_source(structural)
    assert not (tmp_path / "structural/receipt.json").exists()


def test_structural_between_stage_drift_preserves_partial_diagnostics(tmp_path, monkeypatch):
    structural, operations, _ = structural_control_setup(tmp_path, monkeypatch)
    original = operations["validate_spec"]
    def preflight(*args, **kwargs):
        result = original(*args, **kwargs)
        (tmp_path / "run/visual.png").write_bytes(b"changed after preflight")
        return result
    operations["validate_spec"] = preflight
    with pytest.raises(ValueError, match="identity drift"):
        bridge.continue_structural_source(structural)
    assert (tmp_path / "structural/prepared").is_dir()
    assert (tmp_path / "structural/stage-preflight.json").is_file()
    assert not (tmp_path / "structural/authored").exists()
    assert not (tmp_path / "structural/receipt.json").exists()


def test_runtime_checks_manifest_import_origins_executable_and_dependencies(tmp_path, monkeypatch):
    runtime = tmp_path / "runtime"; runtime.mkdir()
    manifest = write(runtime / "manifest.json", {"files": []})
    dependency = tmp_path / "dependency.bin"; dependency.write_bytes(b"dependency")
    value = {"root": str(runtime), "manifest": bridge.record(manifest),
        "executable": bridge.record(Path(sys.executable)), "dependencies": [bridge.record(dependency)]}
    with pytest.raises(ValueError, match="unbound runtime import"):
        bridge._runtime(value)
    filtered = {name: module for name, module in sys.modules.items() if not name.startswith("kb_creator")}
    monkeypatch.setattr(bridge.sys, "modules", filtered)
    bridge._runtime(value)
    wrong = deepcopy(value)
    wrong["executable"] = bridge.record(dependency)
    with pytest.raises(ValueError, match="executable mismatch"):
        bridge._runtime(wrong)
    dependency.write_bytes(b"drift")
    with pytest.raises(ValueError, match="identity drift"):
        bridge._runtime(value)


def test_actual_one_page_verifier_stage05_stage06_and_receipt(tmp_path, monkeypatch):
    helper = fixture_module("test_review_draft_materialization.py")
    route, _, run, authored, input_path, evidence_path, *_ = helper._review_route_fixture(tmp_path, monkeypatch)
    request = request_for(tmp_path, run, authored, input_path, evidence_path, [1])
    run_value = bridge.read_json(run / "run.json")
    request["authority_files"]["source"] = bridge.record(Path(run_value["local"]["source_path"]))
    request["authority_files"]["renderer"] = bridge.record(Path(run_value["local"]["common_paths"]["pdftoppm"]))
    path = save_request(tmp_path, request)
    monkeypatch.setattr(bridge, "_runtime", lambda unused: None)
    monkeypatch.setattr(bridge, "_operations", lambda unused: {"verify_final_review_draft": route.verify_final_review_draft})
    receipt = bridge.verify_authored_source(path)
    assert receipt["state"] == "completed"
    descriptor = bridge.read_json(tmp_path / "verified/descriptor.json")
    assert len(descriptor["pages"]) == 1 and len(descriptor["assets"]) == 1
    assert descriptor["source"] == request["authority_files"]["source"]


def test_cli_dispatch_success_failure_and_help(tmp_path, monkeypatch, capsys):
    from kb_creator.scripts import continue_review_source as cli
    calls = []
    def operation(path):
        calls.append(path)
        return {"state": "completed", "operation": "fixture", "receipt_sha256": "A" * 64}
    monkeypatch.setattr(cli, "verify_authored_source", operation)
    monkeypatch.setattr(cli, "continue_structural_source", operation)
    assert cli.main(["verify", "--request", str(tmp_path / "request.json")]) == 0
    assert cli.main(["structural", "--request", str(tmp_path / "structural.json")]) == 0
    assert calls == [tmp_path / "request.json", tmp_path / "structural.json"]
    monkeypatch.setattr(cli, "verify_authored_source", lambda unused: (_ for _ in ()).throw(ValueError("failed")))
    assert cli.main(["verify", "--request", "missing.json"]) == 2
    with pytest.raises(SystemExit) as result:
        cli.main(["--help"])
    assert result.value.code == 0 and "structural" in capsys.readouterr().out


def test_request_duplicate_keys_and_caller_passed_flag_rejected(tmp_path, monkeypatch):
    path, request, _, _, *_ = control_fixture(tmp_path, monkeypatch)
    request["passed"] = True
    path = save_request(tmp_path, request)
    with pytest.raises(ValueError, match="closed shape"):
        bridge.verify_authored_source(path)
    path.write_text('{"schema": "one", "schema": "two"}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON key"):
        bridge.verify_authored_source(path)
