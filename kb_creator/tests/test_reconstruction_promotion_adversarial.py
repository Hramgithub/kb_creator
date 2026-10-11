"""Bounded adversarial coverage for the reconstruction promotion bridge."""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.reconstruction_promotion import (
    INVENTORY_NAME,
    ROLE_PATHS,
    ReconstructionPromotionError,
    _safe_inventory,
    _safe_relative,
    _run_kind,
    _validate_cpu_first_capability,
    materialize_reconstruction_promotion,
    validate_reconstruction_package,
)
from kb_creator.tests.test_reconstruction_promotion import production_run


REPO = Path(__file__).resolve().parents[2]
REAL_REPLAY_RUN = REPO / "kb_creator/working/dissociation/reconstruction/20260915-cpu-replay-09"
SHA256 = "A" * 64
PROMOTION_SCHEMAS = (
    "reconstruction_upstream_inventory.v1.schema.json",
    "reconstruction_upstream_manifest.v1.schema.json",
    "reconstruction_source_identity.v1.schema.json",
)


def _file(path: str) -> dict:
    return {"path": path, "bytes": 1, "sha256": SHA256}


def _schema_documents() -> dict[str, tuple[dict, tuple[str | int, ...]]]:
    inventory = {
        "schema": "kb_creator.reconstruction_upstream_inventory.v1",
        "scenario_id": "sample",
        "reconstruction_contract_sha256": SHA256,
        "artifacts": [
            {"role": role, **_file(path)} for role, path in ROLE_PATHS.items()
        ],
        "inventory_sha256": SHA256,
    }
    manifest = {
        "schema": "kb_creator.reconstruction_upstream_manifest.v1",
        "package_state": "candidate_awaiting_reconstruction_acceptance",
        "scenario": {"id": "sample", "title": "Sample"},
        "run": {"run_id": "run-01", "portable_identity_sha256": SHA256},
        "reconstruction_contract": {
            "basename": "sample.reconstruction.json",
            "bytes": 1,
            "sha256": SHA256,
            "contract_revision": 1,
        },
        "source_identity": _file("SOURCE_IDENTITY.json"),
        "review": {
            "queue": _file("evidence/review/review_queue.json"),
            "validated_submission": _file(
                "evidence/review/submission_inventory.json"
            ),
            "decision_set": _file("evidence/review/decision_set.json"),
            "decisions": [_file("evidence/review/pages/page-001.json")],
            "reviewed_allowlist": None,
        },
        "stages": [
            {
                "stage_id": f"0{index}-stage-{index}",
                "stage_name": f"stage_{index}",
                "manifest": _file(f"evidence/stages/0{index}-stage-{index}.json"),
                "reproducible_sha256": SHA256,
            }
            for index in range(1, 7)
        ],
        "candidate": {"files": [], "inventory_sha256": SHA256},
        "content": {"files": [], "inventory_sha256": SHA256},
        "fidelity": _file("evidence/fidelity/audit.json"),
        "qa": _file("RECONSTRUCTION_QA.json"),
        "implementation": {"files": [], "inventory_sha256": SHA256},
        "package_files": [_file("content/RECONSTRUCTED_EN.md")],
        "manifest_sha256": SHA256,
    }
    source_identity = {
        "schema": "kb_creator.reconstruction_source_identity.v1",
        "scenario_id": "sample",
        "run_identity_sha256": SHA256,
        "contract": {
            "basename": "sample.reconstruction.json",
            "bytes": 1,
            "sha256": SHA256,
            "contract_revision": 1,
        },
        "source": {
            "basename": "source.pdf",
            "bytes": 1,
            "sha256": SHA256,
            "page_count": 1,
            "media_box_points": [500, 700],
            "rotation_degrees": 0,
        },
        "source_identity_sha256": SHA256,
    }
    return {
        PROMOTION_SCHEMAS[0]: (inventory, ("artifacts", 0, "path")),
        PROMOTION_SCHEMAS[1]: (manifest, ("package_files", 0, "path")),
        PROMOTION_SCHEMAS[2]: (source_identity, ("contract", "basename")),
    }


def _replace(document: dict, location: tuple[str | int, ...], value: str) -> dict:
    mutated = copy.deepcopy(document)
    target = mutated
    for key in location[:-1]:
        target = target[key]
    target[location[-1]] = value
    return mutated


NONCANONICAL_PATHS = (
    "",
    " content/x.json",
    "content/x.json ",
    "\tcontent/x.json",
    "content/x.json\n",
    r"C:relative.json",
    r"C:\absolute.json",
    r"\\server\share\x.json",
    "/content/x.json",
    "content:ads",
    "content/file:name",
    "content/\x00x.json",
    "content/CON",
    "content/aux.txt",
    "content/COM1.log",
    "content/lpt9",
    "content/name.",
    "content/name ",
    "content//x.json",
    "content///x.json",
    "content/x.json/",
    "content/x.json//",
    "../content/x.json",
    "content/../x.json",
    "content/./x.json",
    "./content/x.json",
    "content/.",
    "content/x.json/.",
)

NORMALIZED_PATHS = (
    "x.json",
    "content/x.json",
    "content/.hidden",
    "content/name with spaces.json",
    "content/contributor.json",
    "content/com10.json",
    "content/lpt0.json",
    "content/name..json",
)


@pytest.mark.parametrize(
    "value",
    NONCANONICAL_PATHS,
)
def test_portable_path_rejects_windows_lexical_attacks(value):
    with pytest.raises(ReconstructionPromotionError, match="unsafe|absolute|Windows"):
        _safe_relative(value)


@pytest.mark.parametrize("value", NORMALIZED_PATHS)
def test_promotion_schema_relative_path_defs_allow_runtime_normalized_paths(value):
    assert _safe_relative(value) == value
    for schema_name in PROMOTION_SCHEMAS:
        schema = json.loads(
            (REPO / "kb_creator/contracts" / schema_name).read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)
        assert Draft202012Validator(schema["$defs"]["relative_path"]).is_valid(value), (
            schema_name,
            value,
        )


@pytest.mark.parametrize("value", NONCANONICAL_PATHS)
def test_promotion_schemas_match_runtime_noncanonical_path_rejections(value):
    with pytest.raises(ReconstructionPromotionError, match="unsafe|absolute|Windows"):
        _safe_relative(value)
    for schema_name, (document, location) in _schema_documents().items():
        schema = json.loads(
            (REPO / "kb_creator/contracts" / schema_name).read_text(encoding="utf-8")
        )
        validator = Draft202012Validator(schema)
        assert not tuple(validator.iter_errors(document)), schema_name
        mutated = _replace(document, location, value)
        assert tuple(validator.iter_errors(mutated)), (schema_name, value)


def test_inventory_rejects_case_collision_and_path_field_attacks():
    row = {"path": "content/A.json", "bytes": 1, "sha256": "A" * 64}
    with pytest.raises(ReconstructionPromotionError):
        _safe_inventory([row, {**row, "path": "content/a.json"}], code="unsafe_promotion_path")
    with pytest.raises(ReconstructionPromotionError):
        _safe_inventory([{**row, "path": "content/file:name"}], code="unsafe_promotion_path")


@pytest.mark.parametrize(
    "value",
    ["content//x.json", "content/./x.json", "content/x.json/"],
)
def test_inventory_rejects_noncanonical_path_aliases(value):
    row = {"path": value, "bytes": 1, "sha256": "A" * 64}
    with pytest.raises(ReconstructionPromotionError, match="unsafe_promotion_path"):
        _safe_inventory([row], code="unsafe_promotion_path")


def test_package_rejects_extra_file_and_inventory_identity_drift(production_run):
    run_root = production_run()
    materialize_reconstruction_promotion(run_root)
    package = run_root / "promotion/reconstruction-upstream-v1"
    extra = package / "content" / "unexpected.txt"
    extra.write_text("unexpected", encoding="utf-8")
    with pytest.raises(ReconstructionPromotionError, match="package|inventory|content"):
        validate_reconstruction_package(package, require_acceptance=False)

    extra.unlink()
    inventory_path = package / INVENTORY_NAME
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory["artifacts"][0]["bytes"] += 1
    inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
    with pytest.raises(ReconstructionPromotionError, match="inventory|seal"):
        validate_reconstruction_package(package, require_acceptance=False)


def test_stage_producer_and_queue_mutations_fail_before_package_write(production_run):
    run_root = production_run()
    stage = run_root / "stages/06-materialize-candidate/stage.json"
    payload = json.loads(stage.read_text(encoding="utf-8"))
    payload["producer"] = "wrong-producer"
    stage.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ReconstructionPromotionError, match="stage|producer"):
        materialize_reconstruction_promotion(run_root)
    assert not (run_root / "promotion/reconstruction-upstream-v1").exists()


def test_decision_snapshot_bytes_drift_is_rejected(production_run):
    run_root = production_run()
    decision = run_root / "review/validated-submission-v1/pages/page-001.json"
    payload = json.loads(decision.read_text(encoding="utf-8"))
    payload["review"]["notes"] = "drift"
    decision.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ReconstructionPromotionError, match="decision|submission|stage"):
        materialize_reconstruction_promotion(run_root)
    assert not (run_root / "promotion/reconstruction-upstream-v1").exists()


def _real_replay_run_spec() -> dict:
    if not REAL_REPLAY_RUN.is_dir():
        pytest.skip("immutable run09 fixture is absent")
    return json.loads((REAL_REPLAY_RUN / "run.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "mutate",
    [
        lambda rows: rows.reverse(),
        lambda rows: rows[0].update(state="unavailable", reason_code="nvidia_device_not_detected", verification_receipt=None),
        lambda rows: rows[1].update(reason_code="arbitrary_probe_failure"),
        lambda rows: rows[1].update(required=True),
    ],
)
def test_v2_capability_semantics_fail_closed(mutate):
    run = _real_replay_run_spec()
    mutate(run["capability_snapshot"]["providers"])
    run["capability_snapshot"]["provider_receipt"]["providers"] = copy.deepcopy(run["capability_snapshot"]["providers"])
    with pytest.raises(ReconstructionPromotionError, match="capability_drift"):
        _validate_cpu_first_capability(run)


def test_any_replay_marker_dispatches_v2_to_replay(tmp_path):
    run = {"schema": "kb_creator.run_spec.v2"}
    assert _run_kind(tmp_path, run) == "direct_v2"
    (tmp_path / "review/validated-submission-v2").mkdir(parents=True)
    assert _run_kind(tmp_path, run) == "replay_v2"


def test_post_publish_validation_fault_rolls_back_only_current_package(production_run, monkeypatch):
    run_root = production_run()
    promotion = run_root / "promotion"
    promotion.mkdir()
    unrelated = promotion / "unrelated.keep"
    unrelated.write_text("preserve", encoding="utf-8")
    import kb_creator.pipeline.reconstruction_promotion as module

    def injected_validator(*_args, **_kwargs):
        raise ReconstructionPromotionError(
            "invalid_or_unaccepted_reconstruction", "injected post-publish failure"
        )

    monkeypatch.setattr(module, "validate_reconstruction_package", injected_validator)
    with pytest.raises(ReconstructionPromotionError, match="injected post-publish failure"):
        module.materialize_reconstruction_promotion(run_root)
    assert unrelated.read_text(encoding="utf-8") == "preserve"
    assert not (promotion / "reconstruction-upstream-v1").exists()
    assert not (promotion / ".reconstruction-upstream-v1.staging").exists()

    preexisting = promotion / "reconstruction-upstream-v1"
    preexisting.mkdir()
    sentinel = preexisting / "sentinel.keep"
    sentinel.write_text("preexisting", encoding="utf-8")
    with pytest.raises(ReconstructionPromotionError, match="promotion_path_exists"):
        module.materialize_reconstruction_promotion(run_root)
    assert sentinel.read_text(encoding="utf-8") == "preexisting"
