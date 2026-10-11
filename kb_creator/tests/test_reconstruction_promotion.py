import json
import shutil
import uuid
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from kb_creator.__main__ import main
from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.reconstruction import RuntimeOptions, StageAdapter, resume_engine, run_engine
from kb_creator.pipeline.reconstruction_promotion import (
    ACCEPTANCE_NAME,
    INVENTORY_NAME,
    ROLE_PATHS,
    ReconstructionPromotionError,
    materialize_reconstruction_promotion,
    preflight_reconstruction_promotion,
    record_reconstruction_acceptance,
    validate_reconstruction_package,
)
from kb_creator.pipeline.publication import PublicationControlError, publication_preflight
from kb_creator.tests.test_publication_control_plane import _fixture as publication_fixture
import kb_creator.pipeline.reconstruction_promotion as promotion


REPO = Path(__file__).resolve().parents[2]
REAL_REPLAY_RUN = REPO / "kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-10"


def _json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def repository_tools_root():
    """Materialize the repository-local tools root required by preflight."""
    tools_root = REPO / ".tools"
    created = not tools_root.exists()
    tools_root.mkdir(exist_ok=True)
    try:
        yield tools_root
    finally:
        if created:
            tools_root.rmdir()


def _source(path: Path) -> None:
    document = canvas.Canvas(str(path), pagesize=(500, 700), invariant=1)
    for page in (1, 2):
        document.drawString(40, 650, f"page {page}")
        document.showPage()
    document.save()


def _sha(path: Path) -> str:
    return file_identity(path)["sha256"]


def _contract(source: Path, handouts: int = 0) -> dict:
    return {
        "schema": "kb_creator.scenario_reconstruction_contract.v1",
        "contract_revision": 1,
        "scenario": {"id": "sample", "title": "Sample"},
        "source": {"sha256": _sha(source), "byte_count": source.stat().st_size, "page_count": 2, "media_box_points": [500, 700], "rotation_degrees": 0},
        "scope": {"mode": "all_source_pages", "first_page": 1, "last_page": 2, "required_entities": {"numbered_player_handouts": handouts}},
        "page_roles": [
            {"role": "cover", "first_page": 1, "last_page": 1, "content_mode": "visual", "traits": [], "strategies": ["visual_preserve"]},
            {"role": "scenario_body", "first_page": 2, "last_page": 2, "content_mode": "text", "traits": [], "strategies": ["reading_order"]},
        ],
        "reconstruction": {"strategies": ["reading_order", "visual_preserve"], "required_review": True},
        "acceptance": {"approval_authority": "configured_reconstruction_review"},
    }


def _runtime(tmp_path: Path) -> RuntimeOptions:
    mineru = tmp_path / ".tools/MinerU"
    _json(mineru / "capability.json", {"schema": "nri.mineru_cuda_capability.v1", "capability": "mineru_cuda", "state": "available", "reason_code": "cuda_available", "checked_at_utc": "2026-09-14T00:00:00Z", "probe": {"nvidia": True}})
    tools = {
        "python": tmp_path / "tools/python.exe",
        "powershell": tmp_path / "tools/pwsh.exe",
        "pdftoppm": tmp_path / "tools/pdftoppm.exe",
        "mineru": mineru / ".venv/Scripts/mineru.exe",
    }
    for path in tools.values():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((path.name + "\n").encode())
    return RuntimeOptions(mineru_root=mineru, pdftoppm=tools["pdftoppm"], powershell=tools["powershell"], python=tools["python"])


def _run_adapters() -> dict[str, StageAdapter]:
    def prepare(output: Path) -> dict:
        _json(output / "prepared/sample_pages.json", {})
        return {"fixture": "prepare"}

    def mineru(output: Path) -> dict:
        _json(output / "raw_receipt.json", {})
        return {"fixture": "mineru"}

    def compare(output: Path) -> dict:
        _json(output / "comparison.json", {"status": "pass"})
        return {"fixture": "compare"}

    def bundle(output: Path) -> dict:
        for page, role in ((1, "cover"), (2, "scenario_body")):
            _json(output / f"merge_packets/pages/page-{page:03d}.json", {"source_page": page, "semantic_role": role})
        return {"fixture": "bundle"}

    return {name: StageAdapter(name, adapter) for name, adapter in (("prepare_inputs", prepare), ("mineru_three_view", mineru), ("compare_views", compare), ("visual_merge_bundle", bundle))}


def _closed_decisions(
    run_root: Path,
    destination: Path,
    handouts: int,
    decision_extension: str | None = None,
) -> tuple[Path, Path]:
    queue = json.loads((run_root / "review/review_queue.json").read_text(encoding="utf-8"))
    records = []
    for page, role in ((1, "cover"), (2, "scenario_body")):
        assets = [{"view": "original_hybrid", "source_path": "handout.png", "logical_name": "Player-Handout-1.png", "placement": "handout"}] if page == 2 and handouts else []
        markdown = "![Player Handout 1]({{asset:Player-Handout-1.png}})" if assets else f"Page {page}"
        path = destination / f"pages/page-{page:03d}.json"
        decision = {"schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": page, "semantic_role": role, "overlay_preference": "original_hybrid", "selected_blocks": [], "markdown": markdown, "assets": assets, "unresolved": [], "review": {"visual_reviewed": True, "notes": ""}}
        if page == 2 and decision_extension == "compact":
            decision["markdown"] = "## Stats\n\nSTR 50"
            decision["block_boundaries"] = [
                {
                    "style": "compact",
                    "heading_line": "## Stats",
                    "first_body_line": "STR 50",
                }
            ]
        elif page == 2 and decision_extension == "unknown":
            decision["layout"] = "compact"
        _json(path, decision)
        records.append({"source_page": page, "path": f"pages/page-{page:03d}.json", **file_identity(path)})
    decision_set = destination / "DecisionSet.json"
    _json(decision_set, {"schema": "kb_creator.reconstruction_decision_set.v1", "review_queue_sha256": queue["queue_sha256"], "contract_sha256": queue["contract_sha256"], "source_sha256": queue["source_sha256"], "decisions": records, "reviewed_allowlist": None, "submission_state": "submitted_for_validation"})
    return decision_set, destination


def _resume_adapters(run_root: Path, handouts: int) -> dict[str, StageAdapter]:
    def audit(output: Path) -> dict:
        _json(output / "audit.json", {"schema": "kb_creator.ai-merge-fidelity-audit/v1", "recall_threshold": 0.95, "pages": [{"source_page": page, "selected_token_count": 0, "decision_token_count": 0, "recall": 1.0, "precision": 1.0, "recall_threshold_applied": False, "word_pairs": [], "substitutions": [], "passed": True} for page in (1, 2)], "errors": [], "passed": True})
        return {"fixture": "audit"}

    def materialize(output: Path) -> dict:
        candidate = output / "candidate"
        pages = []
        provenance = []
        asset_rows = []
        (candidate / "assets").mkdir(parents=True)
        (candidate / "decisions").mkdir()
        for page, role in ((1, "cover"), (2, "scenario_body")):
            source_decision = run_root / f"review/validated-submission-v1/pages/page-{page:03d}.json"
            decision = json.loads(source_decision.read_text(encoding="utf-8"))
            shutil.copyfile(source_decision, candidate / f"decisions/page-{page:03d}.json")
            asset_markdown = "![Player Handout 1](assets/handout.png)" if page == 2 and handouts else f"Page {page}"
            root_text = f"<!-- source-page-{page:03d} -->\n\n{asset_markdown}\n"
            page_markdown = asset_markdown.replace("assets/", "../assets/")
            page_text = f"<!-- source-page-{page:03d} -->\n\n{page_markdown}\n"
            target = candidate / f"pages/page-{page:03d}.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page_text, encoding="utf-8")
            pages.append(root_text)
            packet = run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json"
            provenance.append({"source_page": page, "semantic_role": role, "packet": str(packet.resolve()), "packet_sha256": _sha(packet), "decision_sha256": _sha(source_decision), "selected_blocks": [], "unresolved": []})
            if page == 2 and handouts:
                asset = candidate / "assets/handout.png"
                asset.write_bytes(b"image")
                asset_rows.append({"view": "original_hybrid", "source_path": "handout.png", "logical_name": "Player-Handout-1.png", "placement": "handout", "sha256": _sha(asset), "stored_path": "assets/handout.png"})
        (candidate / "RECONSTRUCTED_EN.md").write_text("\n".join(pages), encoding="utf-8")
        _json(candidate / "MERGE_PROVENANCE.json", {"schema": "kb_creator.mineru_ai_merge_provenance.v1", "status": "candidate_ready_for_reconstruction_qa", "raw_comparison": str((run_root / "outputs/03-compare-views/comparison.json").resolve()), "pages": provenance})
        _json(candidate / "ASSET_MANIFEST.json", {"assets": asset_rows})
        _json(candidate / "OVERLAY_SELECTION.json", {"pages": [{"source_page": page, "overlay_preference": "original_hybrid"} for page in (1, 2)]})
        return {"fixture": "materialize"}

    return {"fidelity_audit": StageAdapter("fidelity_audit", audit), "materialize_candidate": StageAdapter("materialize_candidate", materialize)}


@pytest.fixture
def production_run(tmp_path: Path):
    roots = []

    def build(handouts: int = 0, decision_extension: str | None = None) -> Path:
        source = tmp_path / f"source-{handouts}.pdf"
        _source(source)
        contract_path = tmp_path / f"contract-{handouts}.json"
        _json(contract_path, _contract(source, handouts))
        run_root = REPO / "kb_creator/working/sample/reconstruction" / f"pytest-{uuid.uuid4().hex}"
        run_root.parent.mkdir(parents=True, exist_ok=True)
        roots.append(run_root)
        run_engine(contract_path, source, run_root, run_root.name, adapters=_run_adapters(), runtime=_runtime(tmp_path / f"runtime-{handouts}"))
        destination = tmp_path / f"decisions-{handouts}-{decision_extension or 'legacy'}"
        decisions, decisions_root = _closed_decisions(
            run_root, destination, handouts, decision_extension
        )
        resume_engine(run_root, decisions, decisions_root, adapters=_resume_adapters(run_root, handouts))
        return run_root

    yield build
    for root in roots:
        shutil.rmtree(root, ignore_errors=True)


@pytest.mark.parametrize("handouts", [0, 1])
def test_materialize_and_accept_exact_portable_package(production_run, handouts):
    run_root = production_run(handouts)
    result = materialize_reconstruction_promotion(run_root)
    package = Path(result["package_root"])
    inventory, acceptance = validate_reconstruction_package(package, require_acceptance=False)
    assert result["state"] == "candidate_awaiting_reconstruction_acceptance"
    assert acceptance is None and not (package / ACCEPTANCE_NAME).exists()
    assert {row["role"]: row["path"] for row in inventory["artifacts"]} == ROLE_PATHS
    for document_name in (
        "SOURCE_IDENTITY.json", "RECONSTRUCTION_QA.json",
        "RECONSTRUCTION_MANIFEST.json", "RECONSTRUCTION_INVENTORY.json",
        "evidence/review/MERGE_PROVENANCE.portable.json",
    ):
        document = json.loads((package / document_name).read_text(encoding="utf-8"))

        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in {"path", "basename"} and isinstance(child, str):
                        assert not child.startswith(("/", "\\"))
                        assert "\\" not in child and ":" not in child
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(document)
    accepted = record_reconstruction_acceptance(run_root, "explicit test decision")
    assert accepted["state"] == "accepted_reconstruction_upstream_ready"
    validate_reconstruction_package(package, require_acceptance=True)
    for schema_name, document_name in (
        ("reconstruction_upstream_inventory.v1.schema.json", INVENTORY_NAME),
        ("reconstruction_upstream_manifest.v1.schema.json", "RECONSTRUCTION_MANIFEST.json"),
        ("reconstruction_source_identity.v1.schema.json", "SOURCE_IDENTITY.json"),
        ("artifact_acceptance.v1.schema.json", ACCEPTANCE_NAME),
    ):
        schema = json.loads((REPO / "kb_creator/contracts" / schema_name).read_text(encoding="utf-8"))
        document = json.loads((package / document_name).read_text(encoding="utf-8"))
        assert schema["additionalProperties"] is False
        assert set(schema["required"]) == set(document)
        assert document["schema"] == schema["properties"]["schema"]["const"]
    with pytest.raises(ReconstructionPromotionError, match="acceptance_receipt_exists"):
        record_reconstruction_acceptance(run_root, "explicit test decision")


def test_promotion_accepts_only_the_optional_compact_boundary_extension(production_run):
    extended = production_run(decision_extension="compact")
    result = materialize_reconstruction_promotion(extended)
    assert result["state"] == "candidate_awaiting_reconstruction_acceptance"

    unknown = production_run(decision_extension="unknown")
    with pytest.raises(ReconstructionPromotionError, match="candidate_not_promotable"):
        materialize_reconstruction_promotion(unknown)


def test_semantic_sidecar_bridge_requires_sealed_v2_v4_authority_and_exact_page_identities(tmp_path):
    pages = [1, 2]
    audit_path = tmp_path / "audit.json"
    audit_path.write_text("audit", encoding="utf-8")
    decisions = {}
    submission_rows = []
    for page in pages:
        path = tmp_path / f"page-{page:03d}.json"
        path.write_text(f"decision {page}", encoding="utf-8")
        decisions[page] = path
        submission_rows.append({"source_page": page, "path": f"pages/page-{page:03d}.json", **file_identity(path)})
    structure = {
        "schema": promotion.SEMANTIC_STRUCTURE_SCHEMA,
        "profile": promotion.SEMANTIC_STRUCTURE_PROFILE,
        "pages": [{"source_page": page} for page in pages],
        "structure_sha256": "A" * 64,
    }
    audit = {
        "schema": "kb_creator.ai-merge-fidelity-audit/v4",
        "semantic_structure_profile": promotion.SEMANTIC_STRUCTURE_PROFILE,
        "semantic_structure": structure,
        "authorities": {"submission_sha256": "B" * 64},
    }
    submission = {"submission_sha256": "B" * 64, "page_decisions": submission_rows}
    sidecar = {
        **structure,
        "submission_sha256": submission["submission_sha256"],
        "fidelity_audit": {"path": "outputs/05-fidelity-audit/audit.json", **file_identity(audit_path)},
        "page_decisions": [{"source_page": page, "sha256": file_identity(decisions[page])["sha256"]} for page in pages],
    }
    sidecar_path = tmp_path / "SEMANTIC_STRUCTURE.json"
    _json(sidecar_path, sidecar)
    assert promotion._structural_mode(
        {"schema": "kb_creator.reconstruction_decision_set.v2", "semantic_structure_profile": promotion.SEMANTIC_STRUCTURE_PROFILE},
        audit, submission, code="test",
    ) is True
    assert promotion._validate_semantic_sidecar(
        sidecar_path, pages=pages, fidelity=audit, audit_path=audit_path,
        submission=submission, decision_paths=decisions, code="test",
    ) == sidecar
    sidecar["page_decisions"].reverse()
    _json(sidecar_path, sidecar)
    with pytest.raises(ReconstructionPromotionError, match="page-decision domain"):
        promotion._validate_semantic_sidecar(
            sidecar_path, pages=pages, fidelity=audit, audit_path=audit_path,
            submission=submission, decision_paths=decisions, code="test",
        )
    with pytest.raises(ReconstructionPromotionError, match="declaration and fidelity"):
        promotion._structural_mode(
            {"schema": "kb_creator.reconstruction_decision_set.v2", "semantic_structure_profile": promotion.SEMANTIC_STRUCTURE_PROFILE},
            {"schema": "kb_creator.ai-merge-fidelity-audit/v3"}, submission, code="test",
        )


@pytest.mark.parametrize("caption", ["Handout #7", "Handout # 7", "Handout 7", "Player Handout 7", "Handout #7 — Map"])
def test_visible_handout_heading_numbers_preserve_source_caption_syntax(caption):
    assert promotion._visible_handout_heading_numbers(f"## {caption}\n") == {7}


@pytest.mark.parametrize("text", ["Give Handout #7 to the players", "## Discuss Handout #7", "## Handout #7 is mentioned in prose", "## Handout #0", "![Handout #7](map.png)"])
def test_visible_handout_heading_numbers_do_not_count_mentions(text):
    assert promotion._visible_handout_heading_numbers(text) == set()


def test_visible_handout_heading_numbers_cover_fourteen_source_captions():
    text = "\n".join(f"# Handout #{number}" for number in (1, 3, 4, 2, 9, 10, 14, 7, 8, 5, 12, 6, 11, 13))
    assert promotion._visible_handout_heading_numbers(text) == set(range(1, 15))


def test_semantic_handout_caption_extractor_is_span_bound_and_disambiguates_figures():
    def decision(markdown, units):
        return {"markdown": markdown, "semantic_structure": {"units": units}}

    def handout(start, end, representation="blockquote"):
        return {"kind": "handout", "representation": representation, "markdown_span": {"start_line": start, "end_line": end}}

    decisions = {
        9: decision(
            "narrative Handout 3\n> Handout 2 – Number Seven\n> Handout 2 – duplicate",
            [handout(2, 3)],
        ),
        10: decision(
            "> ## *Player Handout 3: Number Seven*\n> body\n\n> > Handout 4 — Number Seven\nHandout 5 is in prose",
            [handout(1, 2), handout(4, 4)],
        ),
        14: decision(
            "> Handout 5\n> body\nHandout 1 - wrong semantic kind",
            [handout(1, 2), {"kind": "paragraph", "representation": "plain", "markdown_span": {"start_line": 3, "end_line": 3}}],
        ),
        19: decision(
            "> Fig. 9 Handout 1: Appendix\n> Handout 3 - Appendix\n> body",
            [handout(1, 1), handout(2, 3)],
        ),
    }
    assert promotion._semantic_handout_numbers(decisions, code="test") == {1, 2, 3, 4, 5}
    assert promotion._semantic_handout_numbers(
        {1: decision("give the investigator Handout 3\nHandout 5 is in prose", [handout(1, 2)])}, code="test"
    ) == set()
    with pytest.raises(ReconstructionPromotionError, match="ambiguous visible captions"):
        promotion._semantic_handout_numbers(
            {1: decision("> Handout 1 - One\n> Handout 2 - Two", [handout(1, 2)])}, code="test"
        )
    compact = decision(
        "## Before\n\n> Handout 2 - Number Seven",
        [handout(2, 2)],
    )
    compact["block_boundaries"] = [{
        "style": "compact", "heading_line": "## Before", "first_body_line": "> Handout 2 - Number Seven",
    }]
    assert promotion._semantic_handout_numbers({1: compact}, code="test") == {2}


def test_publication_preflight_consumes_only_exact_accepted_bridge(production_run, repository_tools_root, tmp_path):
    run_root = production_run()
    materialize_reconstruction_promotion(run_root)
    record_reconstruction_acceptance(run_root, "explicit publication decision")
    package = run_root / "promotion/reconstruction-upstream-v1"
    old = publication_fixture(tmp_path)
    publication_contract = json.loads(old["contract"].read_text(encoding="utf-8"))
    reconstruction_contract = json.loads((run_root / "run.json").read_text(encoding="utf-8"))["contract"]["sha256"]
    publication_contract["upstream"]["reconstruction_contract_sha256"] = reconstruction_contract
    _json(old["contract"], publication_contract)
    old["run_root"].parent.mkdir(exist_ok=True)
    result = publication_preflight(old["contract"], package / INVENTORY_NAME, package / ACCEPTANCE_NAME, old["config_root"], old["run_root"], repository_tools_root)
    assert result["state"] == "ready"
    assert not old["run_root"].exists()


def test_core_adversarial_rejections(production_run):
    run_root = production_run()
    with pytest.raises(ReconstructionPromotionError, match="decision_authority_invalid"):
        shutil.rmtree(run_root / "review/validated-submission-v1")
        materialize_reconstruction_promotion(run_root)


def test_stage_output_drift_and_precreated_destination_fail_closed(production_run):
    run_root = production_run()
    (run_root / "outputs/06-materialize-candidate/candidate/RECONSTRUCTED_EN.md").write_text("tampered", encoding="utf-8")
    with pytest.raises(ReconstructionPromotionError, match="reconstruction_stage_chain_invalid"):
        materialize_reconstruction_promotion(run_root)

    fresh = production_run()
    (fresh / "promotion/reconstruction-upstream-v1").mkdir(parents=True)
    with pytest.raises(ReconstructionPromotionError, match="promotion_path_exists"):
        materialize_reconstruction_promotion(fresh)


def test_source_drift_between_a_and_b_leaves_no_acceptance(production_run):
    run_root = production_run()
    materialize_reconstruction_promotion(run_root)
    package = run_root / "promotion/reconstruction-upstream-v1"
    run = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
    Path(run["local"]["source_path"]).write_bytes(b"changed source")
    with pytest.raises(ReconstructionPromotionError, match="source_drift"):
        record_reconstruction_acceptance(run_root, "explicit but stale")
    assert not (package / ACCEPTANCE_NAME).exists()


def test_injected_and_outside_root_runs_are_not_authority(tmp_path):
    source = tmp_path / "source.pdf"
    _source(source)
    contract_path = tmp_path / "contract.json"
    _json(contract_path, _contract(source))
    run_root = REPO / "kb_creator/working/sample/reconstruction" / f"pytest-{uuid.uuid4().hex}"
    outside = tmp_path / "outside-run"
    try:
        run_engine(contract_path, source, run_root, run_root.name, adapters=_run_adapters())
        with pytest.raises(ReconstructionPromotionError, match="run_not_production_authority"):
            materialize_reconstruction_promotion(run_root)
        shutil.copytree(run_root, outside)
        with pytest.raises(ReconstructionPromotionError, match="unsafe_promotion_path"):
            materialize_reconstruction_promotion(outside)
    finally:
        shutil.rmtree(run_root, ignore_errors=True)


def test_skipped_run_is_unpromotable(tmp_path):
    source = tmp_path / "source.pdf"
    _source(source)
    contract_path = tmp_path / "contract.json"
    _json(contract_path, _contract(source))
    runtime = _runtime(tmp_path / "runtime")
    capability_path = runtime.mineru_root / "capability.json"
    capability = json.loads(capability_path.read_text(encoding="utf-8"))
    capability.update({"state": "unavailable", "reason_code": "nvidia_device_not_detected"})
    _json(capability_path, capability)
    run_root = REPO / "kb_creator/working/sample/reconstruction" / f"pytest-{uuid.uuid4().hex}"
    try:
        run_engine(contract_path, source, run_root, run_root.name, runtime=runtime)
        with pytest.raises(ReconstructionPromotionError, match="run_not_promotable_skipped"):
            materialize_reconstruction_promotion(run_root)
    finally:
        shutil.rmtree(run_root, ignore_errors=True)


def test_resealed_fake_qa_and_package_extra_are_rejected(production_run):
    run_root = production_run()
    materialize_reconstruction_promotion(run_root)
    package = run_root / "promotion/reconstruction-upstream-v1"
    qa_path = package / "RECONSTRUCTION_QA.json"
    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    qa["gates"][0]["status"] = "fail"
    qa["qa_sha256"] = "0" * 64
    from kb_creator.pipeline.manifests import sealed
    qa = sealed(qa.pop("schema"), {key: value for key, value in qa.items() if key != "qa_sha256"}, digest_key="qa_sha256")
    _json(qa_path, qa)
    manifest_path = package / "RECONSTRUCTION_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["qa"] = {"path": "RECONSTRUCTION_QA.json", **file_identity(qa_path)}
    for row in manifest["package_files"]:
        if row["path"] == "RECONSTRUCTION_QA.json":
            row.update(file_identity(qa_path))
    manifest = sealed(manifest.pop("schema"), {key: value for key, value in manifest.items() if key != "manifest_sha256"}, digest_key="manifest_sha256")
    _json(manifest_path, manifest)
    inventory_path = package / INVENTORY_NAME
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    for row in inventory["artifacts"]:
        if row["role"] == "reconstruction_qa":
            row.update(file_identity(qa_path))
        if row["role"] == "reconstruction_manifest":
            row.update(file_identity(manifest_path))
    inventory = sealed(inventory.pop("schema"), {key: value for key, value in inventory.items() if key != "inventory_sha256"}, digest_key="inventory_sha256")
    _json(inventory_path, inventory)
    with pytest.raises(ReconstructionPromotionError, match="QA"):
        validate_reconstruction_package(package, require_acceptance=False)

    fresh = production_run()
    materialize_reconstruction_promotion(fresh)
    extra = fresh / "promotion/reconstruction-upstream-v1/unlisted.txt"
    extra.write_text("extra", encoding="utf-8")
    with pytest.raises(ReconstructionPromotionError, match="package"):
        validate_reconstruction_package(extra.parent, require_acceptance=False)


def test_precreated_acceptance_and_postwrite_validation_failure_never_overwrite_or_leave_receipt(production_run, monkeypatch):
    run_root = production_run()
    materialize_reconstruction_promotion(run_root)
    package = run_root / "promotion/reconstruction-upstream-v1"
    receipt = package / ACCEPTANCE_NAME
    receipt.write_text("precreated", encoding="utf-8")
    with pytest.raises(ReconstructionPromotionError, match="acceptance_receipt_exists"):
        record_reconstruction_acceptance(run_root, "explicit")
    assert receipt.read_text(encoding="utf-8") == "precreated"

    receipt.unlink()
    import kb_creator.pipeline.reconstruction_promotion as module
    real_validate = module.validate_reconstruction_package
    calls = 0

    def fail_second(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ReconstructionPromotionError("invalid_or_unaccepted_reconstruction", "simulated reopen mutation")
        return real_validate(*args, **kwargs)

    monkeypatch.setattr(module, "validate_reconstruction_package", fail_second)
    with pytest.raises(ReconstructionPromotionError, match="simulated reopen mutation"):
        module.record_reconstruction_acceptance(run_root, "explicit")
    assert not receipt.exists()


def test_package_symlink_or_reparse_is_rejected(production_run):
    run_root = production_run()
    materialize_reconstruction_promotion(run_root)
    package = run_root / "promotion/reconstruction-upstream-v1"
    link = package / "content/link.md"
    try:
        link.symlink_to(package / "content/RECONSTRUCTED_EN.md")
    except OSError:
        pytest.skip("host does not permit an unprivileged symlink fixture")
    with pytest.raises(ReconstructionPromotionError, match="unsafe_promotion_path"):
        validate_reconstruction_package(package, require_acceptance=False)


def test_materialize_rename_race_is_no_replace(production_run, monkeypatch):
    run_root = production_run()
    import kb_creator.pipeline.reconstruction_promotion as module

    def win_race(_source, destination):
        Path(destination).mkdir()
        raise FileExistsError(destination)

    monkeypatch.setattr(module.os, "rename", win_race)
    with pytest.raises(ReconstructionPromotionError, match="promotion_path_exists"):
        module.materialize_reconstruction_promotion(run_root)
    package = run_root / "promotion/reconstruction-upstream-v1"
    assert package.is_dir()
    assert not (package / INVENTORY_NAME).exists()


def test_positive_cli_routes_are_separate(production_run, capsys):
    run_root = production_run()
    assert main(["reconstruction-promotion", "materialize", "--run-root", str(run_root), "--json"]) == 0
    materialized = json.loads(capsys.readouterr().out)
    assert materialized["state"] == "candidate_awaiting_reconstruction_acceptance"
    assert materialized["acceptance"] is None
    assert main(["reconstruction-promotion", "record-acceptance", "--run-root", str(run_root), "--user-decision-reference", "current explicit test acceptance", "--json"]) == 0
    accepted = json.loads(capsys.readouterr().out)
    assert accepted["state"] == "accepted_reconstruction_upstream_ready"


def test_cli_rejects_arbitrary_override_flags():
    with pytest.raises(SystemExit):
        main(["reconstruction-promotion", "materialize", "--run-root", "x", "--destination", "y"])
    with pytest.raises(SystemExit):
        main(["reconstruction-promotion", "record-acceptance", "--run-root", "x", "--user-decision-reference", "yes", "--candidate", "y"])


def test_hand_authored_inventory_and_absent_acceptance_are_rejected(production_run):
    run_root = production_run()
    materialize_reconstruction_promotion(run_root)
    package = run_root / "promotion/reconstruction-upstream-v1"
    with pytest.raises(ReconstructionPromotionError, match="acceptance is absent"):
        validate_reconstruction_package(package, require_acceptance=True)
    inventory = json.loads((package / INVENTORY_NAME).read_text(encoding="utf-8"))
    from kb_creator.pipeline.manifests import sealed
    inventory = sealed(
        "kb_creator.accepted_reconstruction_inventory.v1",
        {key: value for key, value in inventory.items() if key not in {"schema", "inventory_sha256"}},
        digest_key="inventory_sha256",
    )
    _json(package / INVENTORY_NAME, inventory)
    with pytest.raises(ReconstructionPromotionError, match="inventory"):
        validate_reconstruction_package(package, require_acceptance=False)


def test_publication_contract_schema_and_runtime_require_exact_four_roles(repository_tools_root, tmp_path):
    expected = list(ROLE_PATHS)
    for name in (
        "scenario_publication_contract.v1.schema.json",
        "scenario_publication_blueprint.v1.schema.json",
    ):
        schema = json.loads((REPO / "kb_creator/contracts" / name).read_text(encoding="utf-8"))
        assert schema["properties"]["upstream"]["properties"]["required_artifact_roles"] == {"const": expected}
    fixture = publication_fixture(tmp_path)
    contract = json.loads(fixture["contract"].read_text(encoding="utf-8"))
    contract["upstream"]["required_artifact_roles"] = ["reconstructed_en"]
    _json(fixture["contract"], contract)
    with pytest.raises(PublicationControlError, match="upstream authority"):
        publication_preflight(
            fixture["contract"], fixture["inventory"], fixture["reconstruction_acceptance"],
            fixture["config_root"], fixture["run_root"], repository_tools_root,
        )
    assert not fixture["run_root"].exists()


def test_real_current_replay_preflight_is_read_only():
    if not REAL_REPLAY_RUN.is_dir():
        pytest.skip("immutable current replay fixture is absent")
    promotion = REAL_REPLAY_RUN / "promotion"
    before = file_identity(promotion / f"reconstruction-upstream-v1/{INVENTORY_NAME}") if promotion.is_dir() else None
    result = preflight_reconstruction_promotion(REAL_REPLAY_RUN)
    assert result == {
        "schema": "kb_creator.reconstruction_promotion_preflight.v1",
        "state": "promotion_preflight_passed",
        "run_kind": "replay_v2",
        "run_identity_sha256": "1C21F471B2B1092090963DD4DDA692884BC408C54219D6A1D169C1D9940279B2",
        "candidate_inventory_sha256": "6B738103ACEC43BF55A0FB44FEF7AF0AC1B7EEC9537134E04A0A0284BC452CA1",
    }
    after = file_identity(promotion / f"reconstruction-upstream-v1/{INVENTORY_NAME}") if promotion.is_dir() else None
    assert after == before


def test_synthetic_replay_v2_full_materialize_and_validate(tmp_path, monkeypatch):
    if not REAL_REPLAY_RUN.is_dir():
        pytest.skip("immutable current replay fixture is absent")
    import kb_creator.pipeline.reconstruction_promotion as module

    source_context = module._promotion_preflight(REAL_REPLAY_RUN)
    working = tmp_path / "working"
    synthetic = working / "dissociation/reconstruction/synthetic-replay-v2"
    for stage_id in module.STAGE_IDS:
        for relative in (f"stages/{stage_id}/stage.json",):
            destination = synthetic / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REAL_REPLAY_RUN / relative, destination)
    for stage_id in module.STAGE_IDS[:4]:
        relative = f"stages/{stage_id}/rebase.json"
        destination = synthetic / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REAL_REPLAY_RUN / relative, destination)
    for relative in ("review/review_queue.json", "replay/intake.json", "replay/bridge.json"):
        destination = synthetic / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REAL_REPLAY_RUN / relative, destination)
    for page in range(1, 7):
        relative = f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json"
        destination = synthetic / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REAL_REPLAY_RUN / relative, destination)

    def synthetic_preflight(_run_root, _working_root=None):
        return {**source_context, "root": synthetic}

    monkeypatch.setattr(module, "_promotion_preflight", synthetic_preflight)
    result = module.materialize_reconstruction_promotion(synthetic, working_root=working)
    package = Path(result["package_root"])
    inventory, acceptance = module.validate_reconstruction_package(
        package, require_acceptance=False, working_root=working
    )
    assert inventory["scenario_id"] == "dissociation"
    assert acceptance is None
    assert json.loads((package / "evidence/stages/05-fidelity-audit.stage.json").read_text(encoding="utf-8"))["schema"] == "kb_creator.replay_downstream_stage_manifest.v1"


def test_existing_current_replay_package_validates_read_only():
    package = REAL_REPLAY_RUN / "promotion/reconstruction-upstream-v1"
    if not package.is_dir():
        pytest.skip("current replay package is absent")
    before = file_identity(package / INVENTORY_NAME)
    inventory, acceptance = validate_reconstruction_package(package, require_acceptance=False)
    assert inventory["inventory_sha256"] == "F5FD0CD05EADD71C9A2C073B71E5CEA9B345ADDB65F3E59BAFC6F71344872B59"
    assert acceptance is not None
    assert acceptance["receipt_sha256"] == "E660EA6BBF24BAE683715F9C433C68134DC946D6BF9CFD1EF40B867DE0FBEE0B"
    assert file_identity(package / INVENTORY_NAME) == before
    assert (package / ACCEPTANCE_NAME).is_file()
