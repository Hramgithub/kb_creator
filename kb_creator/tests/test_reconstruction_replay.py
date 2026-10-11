from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
from pathlib import Path

import pytest

from kb_creator.pipeline import reconstruction_replay as replay
from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline.manifests import sealed


SHA = "A" * 64


def _origin() -> dict:
    return {
        "path": "outputs/02-mineru-three-view/views/v/view.json",
        "bytes": 10,
        "sha256": SHA,
        "source_run_id": "old",
        "source_run_identity_sha256": "B" * 64,
        "source_stage_id": "02-mineru-three-view",
    }


def _view(state: str = "succeeded", output_inventory: list[dict] | None = None) -> dict:
    value = {
        "schema": "kb_creator.mineru_view_execution.v1",
        "view_id": "v",
        "required": state == "succeeded",
        "provider_id": "pipeline_cpu" if state == "succeeded" else "gpu",
        "run_identity_sha256": "B" * 64,
        "input": {"kind": "original", "path_hint": "source.pdf", "bytes": 1, "sha256": SHA, "source_sha256": SHA},
        "execution_profile": {"view_id": "v"},
        "capability_snapshot": {"bytes": 1, "sha256": SHA, "receipt_sha256": SHA},
        "provider_verification": {} if state == "succeeded" else None,
        "profile_identity": {} if state == "succeeded" else None,
        "state": state,
        "reason_code": None if state == "succeeded" else "unavailable",
        "artifact_root": "views/v/artifacts" if state == "succeeded" else None,
        "output_inventory": (output_inventory if output_inventory is not None else [{"path": "x.txt", "bytes": 1, "sha256": SHA}]) if state == "succeeded" else [],
        "page_coverage": [1] if state == "succeeded" else None,
        "exit_code": 0,
        "diagnostics": {"argv": [r"C:\host\tool.exe"], "environment": {"HOME": r"C:\Users\host"}} if state == "succeeded" else {"invoked": False},
        "blocked_by": None if state == "succeeded" else {"provider_id": "gpu"},
        "cache_key": SHA,
    }
    return sealed(value.pop("schema"), value, digest_key="receipt_sha256")


def test_registry_is_sealed_closed_exact_and_ordered():
    registry = replay.load_registry()
    assert registry["fixed_graph"] == list(replay.STAGE_IDS)
    assert [row["stage_name"] for row in registry["stages"]] == list(replay.STAGE_NAMES)
    assert [row["direct_upstream"] for row in registry["stages"]] == [list(replay.STAGE_IDS[:i]) for i in range(4)]
    assert all(len(row["implementation_paths"]) == len(set(row["implementation_paths"])) for row in registry["stages"])
    assert not any("*" in path or "?" in path for row in registry["stages"] for path in row["implementation_paths"])


def test_registry_has_exact_conservative_common_closure():
    common = {
        "kb_creator/pipeline/reconstruction.py",
        "kb_creator/pipeline/identity.py",
        "kb_creator/pipeline/manifests.py",
        "kb_creator/pipeline/mineru_cpu_first.py",
        "kb_creator/pipeline/process.py",
        "kb_creator/pipeline/windows_process_tree.py",
        "kb_creator/contracts/run_spec.v2.schema.json",
    }
    assert all(common <= set(row["implementation_paths"]) for row in replay.load_registry()["stages"])
    assert "kb_creator/__main__.py" not in set().union(*(set(row["implementation_paths"]) for row in replay.load_registry()["stages"]))


@pytest.mark.parametrize("value,count", list(replay.THROUGH_ALIASES.items()))
def test_contiguous_prefix_aliases_are_closed(value: str, count: int):
    assert replay._through_count(value) == count


@pytest.mark.parametrize("value", ["", "05", "05-fidelity-audit", "06-materialize-candidate", "02,04", "1", "latest"])
def test_stage_05_06_gap_and_implicit_prefixes_rejected(value: str):
    with pytest.raises(replay.ReplayError, match="invalid_replay_prefix"):
        replay._through_count(value)


@pytest.mark.parametrize("value", [r"C:\outside\x", r"\\server\share\x", "../x", "a/../x", "a\\x", "NUL", "a/COM1.txt", "a. "])
def test_portable_path_rejects_windows_escape_and_aliases(value: str):
    with pytest.raises(replay.ReplayError):
        replay._validate_relative(value)


def test_per_view_reference_requires_exact_view_scope(tmp_path: Path):
    root = tmp_path / "run"
    artifact = root / "outputs/02-mineru-three-view/views/a/artifacts/x.txt"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("x", encoding="utf-8")
    ref = replay._typed_ref("view_artifact_root", "x.txt", file_identity(artifact), view_id="a")
    assert replay.resolve_reference(root, ref, {"a": artifact.parent}) == artifact
    with pytest.raises(replay.ReplayError, match="unknown_view_artifact_root"):
        replay.resolve_reference(root, {**ref, "view_id": "b"}, {"a": artifact.parent})


def test_typed_reference_rejects_cross_base_view_scope():
    with pytest.raises(replay.ReplayError, match="unexpected_view_scope"):
        replay._typed_ref("stage_02_root", "x", {"bytes": 1, "sha256": SHA}, view_id="a")
    with pytest.raises(replay.ReplayError, match="view_reference_lacks_scope"):
        replay._typed_ref("view_artifact_root", "x", {"bytes": 1, "sha256": SHA})


@pytest.mark.parametrize("state", ["succeeded", "skipped"])
def test_view_transform_is_typed_truthful_and_projection_preserving(state: str):
    source = _view(state)
    fresh = replay._rebase_view(source, "C" * 64, _origin())
    assert fresh["schema"] == replay.VIEW_SCHEMA
    assert fresh["run_identity_sha256"] == "C" * 64
    assert fresh["execution"] == {"mode": "replayed", "producer_invoked": False, "origin_execution": _origin()}
    assert not any(key in fresh["execution"] for key in ("argv", "environment", "stdout", "stderr"))
    assert fresh["semantic_projection_sha256"] == sha256_bytes(canonical_bytes(replay._semantic_view(source)))
    if state == "succeeded":
        assert fresh["artifact_root"] == {"base": "view_artifact_root", "view_id": "v", "path": "artifacts"}
    else:
        assert fresh["artifact_root"] is None


def test_view_transform_rejects_fully_resealed_unknown_field():
    source = _view()
    source.pop("receipt_sha256")
    source["unexpected"] = True
    source = sealed(source.pop("schema"), source, digest_key="receipt_sha256")
    with pytest.raises(replay.ReplayError, match="shape_mismatch"):
        replay._rebase_view(source, "C" * 64, _origin())


def test_view_transform_rejects_tampered_receipt():
    source = _view()
    source["state"] = "skipped"
    with pytest.raises(replay.ReplayError, match="source_view_seal_mismatch"):
        replay._rebase_view(source, "C" * 64, _origin())


def test_stage04_has_typed_rebasers_not_generic_envelopes():
    source = Path(replay.__file__).read_text(encoding="utf-8")
    assert "def _rebase_geometry(" in source
    assert "def _rebase_visual(" in source
    assert "def _replay_envelope(" not in source


@pytest.mark.parametrize("suffix", [".pdf", ".png", ".jpg", ".jpeg"])
def test_binary_payload_scan_is_schema_routed_without_text_decoding(tmp_path: Path, suffix: str):
    path = tmp_path / f"x{suffix}"
    path.write_bytes(b"\xff\xfeC:\\not-text")
    replay._scan_payload(path, "01-prepare-inputs", path.name, "B" * 64)


def test_json_and_text_payload_poison_rejected(tmp_path: Path):
    js = tmp_path / "x.json"
    js.write_text(json.dumps({"path": r"C:\outside\x"}), encoding="utf-8")
    with pytest.raises(replay.ReplayError, match="path_or_identity_poison"):
        replay._scan_payload(js, "01-prepare-inputs", "prepared/sample_pages.json", "B" * 64)
    md = tmp_path / "x.md"
    md.write_text("C:\\outside\\x\n", encoding="utf-8")
    with pytest.raises(replay.ReplayError, match="path_or_identity_poison"):
        replay._scan_payload(md, "03-compare-views", "comparison.md", "B" * 64)


def test_real_shape_mineru_content_list_array_is_accepted():
    fixture = Path(__file__).parent / "fixtures/mineru_content_list_array.sanitized.json"
    replay._scan_payload(
        fixture,
        "02-mineru-three-view",
        "views/original_pipeline_txt/artifacts/Dissociation/txt/Dissociation_content_list.json",
        "B" * 64,
    )


@pytest.mark.parametrize(
    "poison",
    [
        r"C:\outside\stolen.png",
        r"\\server\share\stolen.png",
        r"\\?\C:\device\stolen.png",
        "../../stolen.png",
        "/etc/passwd",
        "B" * 64,
        "nested/NUL.txt",
    ],
)
def test_mineru_content_list_recursively_rejects_nested_path_and_identity_poison(
    tmp_path: Path, poison: str
):
    path = tmp_path / "sample_content_list.json"
    _write_json(path, [{"page_idx": 0, "nested": [{"asset": poison}]}])
    with pytest.raises(replay.ReplayError, match="path_or_identity_poison_in_payload"):
        replay._scan_payload(
            path,
            "02-mineru-three-view",
            "views/original_pipeline_ocr/artifacts/sample/ocr/sample_content_list.json",
            "B" * 64,
        )


@pytest.mark.parametrize('word', ['CON', 'NUL', 'AUX', 'PRN', 'COM1', 'LPT1'])
def test_typed_ocr_words_are_not_windows_device_paths(tmp_path, word):
    path = tmp_path / 'sample_middle.json'
    payload = {'pdf_info': [{'preproc_blocks': [{'lines': [{'spans': [
        {'bbox': [1, 2, 3, 4], 'type': 'text', 'content': word, 'score': 1.0}
    ]}]}]}]}
    _write_json(path, payload)
    before = path.read_bytes()
    replay._scan_payload(path, '02-mineru-three-view', 'views/original_pipeline_ocr/artifacts/sample/ocr/sample_middle.json', 'B' * 64)
    assert path.read_bytes() == before
    assert replay._payload_contains_poison({'asset': word}, 'B' * 64)
    assert replay._payload_contains_poison({'content': word}, 'B' * 64)


@pytest.mark.parametrize('literal', ['CON.txt', 'nested/NUL.txt', '../CON', '/CON', r'C:\CON', '/RQJ\x03 EHIRUH\x03'])
def test_source_literals_stay_text_but_asset_fields_stay_paths(literal):
    assert not replay._payload_contains_poison({'type': 'text', 'content': literal}, 'B' * 64)
    assert not replay._payload_contains_poison({'label': 'ocr_text', 'text': literal}, 'B' * 64)
    assert replay._payload_contains_poison({'type': 'text', 'asset': literal}, 'B' * 64)
    assert replay._payload_contains_poison({'label': 'ocr_text', 'path': literal}, 'B' * 64)
    assert replay._payload_contains_poison({'content': literal}, 'B' * 64)


def test_text_labels_never_exempt_stale_run_identity():
    assert replay._payload_contains_poison({'type': 'text', 'content': 'B' * 64}, 'B' * 64)
    assert replay._payload_contains_poison({'label': 'ocr_text', 'text': 'B' * 64}, 'B' * 64)


def test_content_list_array_exception_is_exactly_routed(tmp_path: Path):
    array = tmp_path / "other.json"
    _write_json(array, [])
    with pytest.raises(replay.ReplayError, match="unknown_json_payload_route"):
        replay._scan_payload(
            array,
            "02-mineru-three-view",
            "views/original_pipeline_txt/artifacts/sample/other.json",
            "B" * 64,
        )
    object_payload = tmp_path / "sample_content_list.json"
    _write_json(object_payload, {"not": "a list"})
    with pytest.raises(replay.ReplayError, match="invalid_json_payload_shape"):
        replay._scan_payload(
            object_payload,
            "02-mineru-three-view",
            "views/original_pipeline_txt/artifacts/sample/sample_content_list.json",
            "B" * 64,
        )


def test_physical_copy_is_distinct_and_exact(tmp_path: Path):
    source = tmp_path / "source.bin"
    target = tmp_path / "target.bin"
    source.write_bytes(b"payload")
    assert replay._copy_physical(source, target) == file_identity(source)
    assert not os.path.samefile(source, target)


def test_hardlink_source_rejected_when_supported(tmp_path: Path):
    source = tmp_path / "source.bin"
    link = tmp_path / "link.bin"
    source.write_bytes(b"payload")
    try:
        os.link(source, link)
    except OSError:
        pytest.skip("hardlinks unavailable")
    with pytest.raises(replay.ReplayError, match="hardlink_source"):
        replay._copy_physical(source, tmp_path / "target.bin")


@pytest.mark.parametrize("relation", ["same", "nested_source", "nested_destination"])
def test_source_destination_self_and_nesting_rejected(tmp_path: Path, relation: str):
    source = tmp_path / "source"
    source.mkdir()
    if relation == "same":
        target = source
    elif relation == "nested_source":
        target = source / "new"
    else:
        target = tmp_path
    with pytest.raises(replay.ReplayError):
        replay._assert_roots(source, target)


def test_existing_destination_rejected(tmp_path: Path):
    source, target = tmp_path / "source", tmp_path / "target"
    source.mkdir(); target.mkdir()
    with pytest.raises(replay.ReplayError, match="destination_exists"):
        replay._assert_roots(source, target)


def test_run07_wrapper_fixture_is_exactly_thirteen_and_fully_classified():
    assert len(replay.RUN07_BOUND_WRAPPER_FIXTURE) == 13
    assert len(set(replay.RUN07_BOUND_WRAPPER_FIXTURE)) == 13
    for path in replay.RUN07_BOUND_WRAPPER_FIXTURE:
        _, stage_id, relative = path.split("/", 2)
        assert replay._classify(stage_id, relative) != "payload"


@pytest.mark.parametrize("path", ["unknown.json", "views/x/unknown.json", "views/x/evidence/other.json", "views/x/artifacts"])
def test_unknown_stage02_artifacts_fail_closed(path: str):
    with pytest.raises(replay.ReplayError, match="unregistered_stage_artifact"):
        replay._classify("02-mineru-three-view", path)


def test_recovered_view_evidence_rejects_tampered_or_unbound_receipt(tmp_path: Path):
    root = tmp_path / "source"
    root.mkdir()
    _synthetic_replay_source(root, recovered_view_evidence=True)
    stage = root / "outputs/02-mineru-three-view"
    evidence = stage / "views/v/evidence/origin-view.json"
    evidence.write_text("{}\n", encoding="utf-8")
    with pytest.raises(replay.ReplayError, match="recovered_view_evidence_identity_mismatch"):
        replay._validate_recovered_view_evidence(evidence, stage / "views/v/view.json", "v")


def test_stage04_binary_and_text_routes_are_payloads_but_registered_wrappers_are_not():
    assert replay._classify("04-visual-merge-bundle", "visual/original_pipeline_txt/pages/page-001.png") == "payload"
    assert replay._classify("04-visual-merge-bundle", "merge_packets/pages/page-001.json") == "payload"
    assert replay._classify("04-visual-merge-bundle", "visual/visual_manifest.json") == "visual_manifest"


def test_semantic_comparison_projection_changes_for_every_reader_domain():
    base = {
        "status": "pass_for_review", "required_views": ["a"], "succeeded_views": ["a"], "skipped_views": [],
        "views": {"a": {"root": "old", "artifacts": {"markdown": {"path": "old", "bytes": 1, "sha256": SHA}}, "coverage": [1], "block_counts": {"text": 1}, "text_lengths": {"markdown": 1}, "asset_references": [], "asset_inventory": [], "blocks": [{"text": "x"}]}},
        "pairwise": [{"left": "a", "right": "a", "equal": True}], "failures": [],
    }
    baseline = sha256_bytes(canonical_bytes(replay._comparison_projection(base)))
    for mutation in (
        lambda x: x["views"]["a"]["blocks"][0].update(text="y"),
        lambda x: x["views"]["a"]["artifacts"]["markdown"].update(sha256="D" * 64),
        lambda x: x["pairwise"][0].update(equal=False),
        lambda x: x.update(status="fail"),
    ):
        changed = copy.deepcopy(base); mutation(changed)
        assert sha256_bytes(canonical_bytes(replay._comparison_projection(changed))) != baseline


def test_replay_public_module_has_no_stage05_stage06_or_acceptance_execution_route():
    source = Path(replay.__file__).read_text(encoding="utf-8")
    assert "fidelity_audit" not in source
    assert "materialize_candidate" not in source
    assert "record_reconstruction_acceptance" not in source
    assert "remote" not in source.lower()


def test_cli_has_dedicated_replay_and_no_trust_force_or_copy_decisions():
    source = (Path(replay.__file__).parents[1] / "__main__.py").read_text(encoding="utf-8")
    assert 'add_parser("replay")' in source
    assert 'add_parser("verify-source")' in source
    assert 'add_parser("run")' in source
    for forbidden in ("--trust", "--force", "--ignore", "--copy-decisions"):
        assert forbidden not in source


def test_all_replay_schemas_parse_and_close_top_level():
    root = Path(replay.__file__).parents[1] / "contracts"
    for relative in replay.REPLAY_IMPLEMENTATION_PATHS:
        if not relative.endswith(".schema.json"):
            continue
        schema = json.loads((Path(replay.__file__).parents[2] / relative).read_text(encoding="utf-8"))
        assert schema["$schema"].endswith("2020-12/schema")
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False


def test_replay_implementation_inventory_binds_every_contract_and_engine():
    inventory = replay._replay_inventory()
    paths = {row["path"] for row in inventory["files"]}
    assert set(replay.REPLAY_IMPLEMENTATION_PATHS) <= paths
    assert "kb_creator/__main__.py" in paths


def test_full_run_rejects_short_prefix_before_destination_creation(tmp_path: Path):
    destination = tmp_path / "new"
    with pytest.raises(replay.ReplayError, match="partial_prefix_execution_not_implemented"):
        replay.replay_run_engine(Path("c"), Path("s"), Path("old"), destination, "new", "01", None)  # type: ignore[arg-type]
    assert not destination.exists()


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _synthetic_replay_source(
    root: Path, *, semantic: bool = False, recovered_view_evidence: bool = False,
) -> tuple[dict, list[dict]]:
    source_identity = "B" * 64
    contract_file = root / "contract.json"
    contract_file.write_bytes(b"synthetic contract\n")
    run = {
        "schema": "kb_creator.run_spec.v2",
        "run_id": "executed-source",
        "target": "reconstructed_en",
        "profile": "mineru_cpu_first_three_view_v1",
        "contract": {"path_hint": "contract.json", "bytes": 1, "sha256": SHA, "contract_revision": 1},
        "source": {"path_hint": "source.pdf", "bytes": 1, "sha256": SHA, "page_count": 1, "media_box_points": [1, 1], "rotation_degrees": 0},
        "scope": {"ordered_pages": [1]},
        "options": {}, "execution_boundary": {}, "view_plan": [], "capability_snapshot": {}, "provider_profiles": {}, "common_tools": {}, "toolchain": [],
        "implementation": {"files": [], "inventory_sha256": SHA},
        "portable_identity_sha256": source_identity,
        "local": {"run_root": str(root), "contract_path": str(contract_file)},
    }
    _write_json(root / "run.json", run)
    artifact_names = {
        "content_list": "doc_content_list.json", "content_list_v2": "doc_content_list_v2.json",
        "middle_json": "doc_middle.json", "markdown": "doc.md", "layout_pdf": "doc_layout.pdf",
        "origin_pdf": "doc_origin.pdf", "span_pdf": "doc_span.pdf",
    }
    outputs: dict[str, dict[str, bytes]] = {
        "01-prepare-inputs": {"command.json": b"{}", "prepared/sample_pages.json": b"{}", "prepared/source_raster.pdf": b"pdf"},
        "02-mineru-three-view": {
            f"views/v/artifacts/{name}": (
                b"[]" if name.endswith(("_content_list.json", "_content_list_v2.json", "_model.json"))
                else b"{}" if name.endswith(".json")
                else b"x\n" if name.endswith(".md")
                else b"pdf"
            )
            for name in artifact_names.values()
        },
        "03-compare-views": {"command.json": b"{}", "comparison.md": b"ok\n"},
        "04-visual-merge-bundle": {
            "command.json": b"{}", "merge_packets/merge_index.json": b"{}", "merge_packets/pages/page-001.json": b"{}",
            "visual/v/pages/page-001.png": b"render", "visual/triptychs/page-001.png": b"triptych",
            "visual/contact_sheets/pages-001-001.png": b"contact",
        },
    }
    for stage_id, files in outputs.items():
        for relative, raw in files.items():
            path = root / "outputs" / stage_id / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    artifact_root = root / "outputs/02-mineru-three-view/views/v/artifacts"
    artifact_inventory = [{"path": name, **file_identity(artifact_root / name)} for name in artifact_names.values()]
    view = _view(output_inventory=artifact_inventory)
    view_path = root / "outputs/02-mineru-three-view/views/v/view.json"
    if recovered_view_evidence:
        evidence = _view()
        evidence.pop("receipt_sha256")
        evidence["run_identity_sha256"] = "C" * 64
        evidence = sealed(evidence.pop("schema"), evidence, digest_key="receipt_sha256")
        evidence_path = root / "outputs/02-mineru-three-view/views/v/evidence/origin-view.json"
        _write_json(evidence_path, evidence)
        identity = file_identity(evidence_path)
        view.pop("receipt_sha256")
        view["diagnostics"] = {
            "origin": {
                "run_identity_sha256": evidence["run_identity_sha256"],
                "receipt": {"path_hint": "views/v/view.json", **identity, "receipt_sha256": evidence["receipt_sha256"]},
                "receipt_evidence": {"path_hint": "views/v/evidence/origin-view.json", **identity, "receipt_sha256": evidence["receipt_sha256"]},
            },
        }
        view = sealed(view.pop("schema"), view, digest_key="receipt_sha256")
    _write_json(view_path, view)
    outputs["02-mineru-three-view"]["views/v/view.json"] = view_path.read_bytes()
    view_set = sealed("kb_creator.mineru_view_set.v1", {
        "run_identity_sha256": source_identity, "ordered_view_plan": [], "required_succeeded": ["v"], "succeeded_views": ["v"],
        "views": [{"view_id": "v", "state": "succeeded", "receipt": {"path": "views/v/view.json", **file_identity(view_path), "receipt_sha256": view["receipt_sha256"]}}],
    }, digest_key="receipt_sha256")
    view_set_path = root / "outputs/02-mineru-three-view/view-set.json"
    _write_json(view_set_path, view_set)
    outputs["02-mineru-three-view"]["view-set.json"] = view_set_path.read_bytes()
    prepared_file = root / "outputs/01-prepare-inputs/prepared/sample_pages.json"
    block = {"raw_index": 0, "page_idx": 0, "source_page": 1, "type": "text", "bbox": [0, 0, 1, 1], "text": "x", "semantic_evidence": {"text_level": None, "v2_title": False, "middle_title": False, "markdown_heading": False, "model_title": False}, "assets": []}
    comparison = {
        "schema": "kb_creator.mineru_multi_view_comparison.v2", "status": "pass_for_review", "run_identity_sha256": source_identity,
        "manifest": {"path": str(prepared_file), **file_identity(prepared_file)},
        "view_set": {"path": str(view_set_path), **file_identity(view_set_path), "receipt_sha256": view_set["receipt_sha256"]},
        "required_views": ["v"], "succeeded_views": ["v"], "skipped_views": [],
        "views": {"v": {"root": str(artifact_root), "artifacts": {role: str(artifact_root / name) for role, name in artifact_names.items()}, "coverage": {"expected_page_idx": [0], "actual_page_idx": [0], "missing_page_idx": [], "extra_page_idx": []}, "block_counts": {"text": 1}, "text_lengths": {"0": 1}, "asset_references": [], "asset_inventory": [], "blocks": [block]}},
        "pairwise": {}, "failures": [],
    }
    comparison_path = root / "outputs/03-compare-views/comparison.json"
    _write_json(comparison_path, comparison)
    outputs["03-compare-views"]["comparison.json"] = comparison_path.read_bytes()
    renderer = {"path_hint": "pdftoppm.exe", "bytes": 1, "sha256": SHA, "version": "pdftoppm test", "argv_recipe": "pdftoppm-mediabox-png-v1"}
    render_path = root / "outputs/04-visual-merge-bundle/visual/v/pages/page-001.png"
    geometry = sealed("kb_creator.mineru_geometry_plan.v1", {
        "policy": "source_displayed_mediabox_v1", "run_identity_sha256": source_identity,
        "preparation_manifest": {"path_hint": "outputs/01-prepare-inputs/prepared/sample_pages.json", **file_identity(prepared_file)},
        "source": {"path_hint": "source.pdf", "bytes": 1, "sha256": SHA},
        "comparison": {"path_hint": "outputs/03-compare-views/comparison.json", **file_identity(comparison_path)},
        "view_set": {"path_hint": "outputs/02-mineru-three-view/view-set.json", **file_identity(view_set_path), "receipt_sha256": view_set["receipt_sha256"]},
        "review_dpi": 110, "rounding_rule": "ceil(points*dpi/72)", "tolerances": {"dimension_points": "0.001", "relative_aspect_ratio": "0.000005", "pixels": 0},
        "renderer": renderer, "succeeded_views": ["v"],
        "layouts": [{"view_id": "v", "input_kind": "original", "page_count": 1, "layout": {"path_hint": "views/v/artifacts/doc_layout.pdf", **file_identity(artifact_root / "doc_layout.pdf")}}],
        "observed_geometry": [{"view_id": "v", "sample_page": 1, "source_page": 1, "media_box_coordinates": ["0", "0", "1", "1"], "crop_box_coordinates": ["0", "0", "1", "1"], "rotation_degrees": 0, "user_unit": "1", "effective_displayed_size_points": ["1", "1"]}],
        "targets": [{"source_page": 1, "displayed_size_points": ["1", "1"], "target_pixels": [1, 1]}],
        "transforms": {"pad": False, "crop": False, "post_render_resize": False},
        "rendered_pages": [{"view_id": "v", "source_page": 1, "path": "visual/v/pages/page-001.png", "dimensions": [1, 1], "mode": "RGB", **file_identity(render_path)}],
    }, digest_key="plan_sha256")
    geometry_path = root / "outputs/04-visual-merge-bundle/visual/geometry_plan.json"
    _write_json(geometry_path, geometry)
    outputs["04-visual-merge-bundle"]["visual/geometry_plan.json"] = geometry_path.read_bytes()
    if semantic:
        view_set, comparison, geometry = _semantic_fixture_payloads(root, view_set, comparison, geometry)
        artifact_root = root / "outputs/02-mineru-three-view/views/original_pipeline_txt/artifacts"
    visual_files = replay.deterministic_inventory(root / "outputs/04-visual-merge-bundle")
    visual_files = [row for row in visual_files if row["path"] not in {"command.json"}]
    execution = {"commands": [[r"C:\old\pdftoppm.exe"]], "pdftoppm_version": "pdftoppm test", "output_inventory": visual_files}
    execution_path = root / "outputs/04-visual-merge-bundle/evidence/execution.json"
    _write_json(execution_path, execution)
    outputs["04-visual-merge-bundle"]["evidence/execution.json"] = execution_path.read_bytes()
    visual = sealed("kb_creator.mineru_visual_merge_bundle.v2", {
        "inputs": {"raw_receipt": {"path": str(view_set_path), "sha256": file_identity(view_set_path)["sha256"]}, "source": {"path": r"C:\old\source.pdf", "sha256": SHA}, "comparison": {"path": str(comparison_path), "sha256": file_identity(comparison_path)["sha256"]}, "raw_root": str(root / "outputs/02-mineru-three-view"), "dpi": 110, "preparation_manifest": {"path": str(prepared_file), "sha256": file_identity(prepared_file)["sha256"]}, "reconstruction_contract": {"path": r"C:\old\contract.json", "sha256": file_identity(contract_file)["sha256"]}},
        "layouts": {"v": {"path": str(artifact_root / "doc_layout.pdf"), "sha256": file_identity(artifact_root / "doc_layout.pdf")["sha256"]}},
        "execution": {"commands": [[r"C:\old\pdftoppm.exe"]], "pdftoppm_version": "pdftoppm test"},
        "counts": {"rendered_pages": 1, "triptychs": 1, "contact_sheets": 1, "merge_packets": 1, "optional_companions": 0},
        "inventory_scope": "synthetic", "inventory_exclusions": ["visual/visual_manifest.json", "evidence/execution.json", "command.json"],
        "files": visual_files, "geometry_plan": {"path": "visual/geometry_plan.json", **file_identity(geometry_path), "plan_sha256": geometry["plan_sha256"]},
    }, digest_key="manifest_sha256")
    if semantic:
        visual.pop("manifest_sha256")
        visual["layouts"] = {
            view_id: {"path": str(root / "outputs/02-mineru-three-view" / row["layout"]["path_hint"]), "sha256": row["layout"]["sha256"]}
            for view_id, row in zip(geometry["succeeded_views"], geometry["layouts"])
        }
        visual["counts"]["rendered_pages"] = 3
        visual = sealed(visual.pop("schema"), visual, digest_key="manifest_sha256")
    visual_path = root / "outputs/04-visual-merge-bundle/visual/visual_manifest.json"
    _write_json(visual_path, visual)
    outputs["04-visual-merge-bundle"]["visual/visual_manifest.json"] = visual_path.read_bytes()
    evidences = []
    closure_row = {"path": "kb_creator/pipeline/reconstruction_replay.py", **file_identity(Path(replay.__file__))}
    closure_sha = sha256_bytes(canonical_bytes([closure_row]))
    for stage_id in replay.STAGE_IDS:
        inventory = replay.deterministic_inventory(root / "outputs" / stage_id)
        manifest = {"schema": "kb_creator.stage_manifest.v1", "reproducible": {"inputs": [], "outputs": {"root_hint": f"outputs/{stage_id}", "files": inventory, "inventory_sha256": sha256_bytes(canonical_bytes(inventory))}}, "execution": {}, "reproducible_sha256": SHA}
        manifest_path = root / "stages" / stage_id / "stage.json"
        _write_json(manifest_path, manifest)
        evidences.append({
            "stage_id": stage_id,
            "source_manifest": {"path": f"stages/{stage_id}/stage.json", **file_identity(manifest_path), "reproducible_sha256": SHA},
            "source_output": manifest["reproducible"]["outputs"],
            "producer_closure": {"source": [closure_row], "current": [closure_row], "producer_closure_sha256": closure_sha},
            "portable_equivalence": [], "stage_eligibility_key": hashlib.sha256(stage_id.encode()).hexdigest().upper(),
        })
    _write_json(root / "review/review_queue.json", {
        "required_decision_schema": "kb_creator.mineru_ai_page_decision.v1",
        "items": [{"id": "page-001", "source_page": 1, "merge_packet": {"path": "merge_packets/pages/page-001.json", **file_identity(root / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json")}}],
    })
    if semantic:
        queue_path = root / "review/review_queue.json"
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        queue["items"][0].update(contract_role="body", contract_traits=[], contract_strategies=[], issue_kinds=[], required_decision_file="pages/page-001.json", state="open")
        _write_json(queue_path, queue)
    return run, evidences


def _semantic_fixture_payloads(root: Path, view_set: dict, comparison: dict, geometry: dict) -> tuple[dict, dict, dict]:
    """Populate source payloads before inventory sealing; replay validates their bytes."""
    view_ids = ["original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr"]
    stage2 = root / "outputs/02-mineru-three-view"
    stage4 = root / "outputs/04-visual-merge-bundle"
    template_view = json.loads((stage2 / "views/v/view.json").read_text(encoding="utf-8"))
    template_comparison = comparison["views"]["v"]
    template_geometry = copy.deepcopy(geometry)
    comparison["views"] = {}
    view_set["views"] = []
    geometry["layouts"], geometry["observed_geometry"], geometry["rendered_pages"] = [], [], []
    packet = {"source_page": 1, "semantic_role": "body", "views": {}}
    for view_id in view_ids:
        artifacts = stage2 / "views" / view_id / "artifacts"
        shutil.copytree(stage2 / "views/v/artifacts", artifacts)
        blocks = []
        if view_id == "original_pipeline_txt":
            block = copy.deepcopy(template_comparison["blocks"][0])
            block.update(text="Stable heading", bbox=[100, 100, 900, 200])
            blocks = [block]
        _write_json(artifacts / "doc_content_list.json", blocks)
        (artifacts / "doc.md").write_text("Stable heading\n" if blocks else "", encoding="utf-8")
        view = copy.deepcopy(template_view)
        view.pop("receipt_sha256")
        view.update(view_id=view_id, execution_profile={"view_id": view_id}, artifact_root=f"views/{view_id}/artifacts", output_inventory=replay.deterministic_inventory(artifacts))
        view = sealed(view.pop("schema"), view, digest_key="receipt_sha256")
        view_path = stage2 / "views" / view_id / "view.json"
        _write_json(view_path, view)
        view_set["views"].append({"view_id": view_id, "state": "succeeded", "receipt": {"path": f"views/{view_id}/view.json", **file_identity(view_path), "receipt_sha256": view["receipt_sha256"]}})
        row = copy.deepcopy(template_comparison)
        row.update(root=str(artifacts), artifacts={role: str(artifacts / Path(path).name) for role, path in row["artifacts"].items()}, blocks=blocks, block_counts={"text": len(blocks)}, text_lengths={"0": 14 if blocks else 0})
        comparison["views"][view_id] = row
        packet["views"][view_id] = {"blocks": blocks}
        render_path = stage4 / "visual" / view_id / "pages/page-001.png"
        render_path.parent.mkdir(parents=True)
        render_path.write_bytes(b"render")
        layout = copy.deepcopy(template_geometry["layouts"][0])
        layout.update(view_id=view_id, layout={"path_hint": f"views/{view_id}/artifacts/doc_layout.pdf", **file_identity(artifacts / "doc_layout.pdf")})
        geometry["layouts"].append(layout)
        geometry["observed_geometry"].append({**template_geometry["observed_geometry"][0], "view_id": view_id})
        geometry["rendered_pages"].append({**template_geometry["rendered_pages"][0], "view_id": view_id, "path": render_path.relative_to(stage4).as_posix(), **file_identity(render_path)})
    # Remove only the disposable fixture's superseded template before any inventories exist.
    shutil.rmtree(stage2 / "views/v")
    shutil.rmtree(stage4 / "visual/v")
    view_set.pop("receipt_sha256")
    view_set.update(required_succeeded=view_ids, succeeded_views=view_ids)
    view_set = sealed(view_set.pop("schema"), view_set, digest_key="receipt_sha256")
    view_set_path = stage2 / "view-set.json"
    _write_json(view_set_path, view_set)
    comparison.update(required_views=view_ids, succeeded_views=view_ids, view_set={"path": str(view_set_path), **file_identity(view_set_path), "receipt_sha256": view_set["receipt_sha256"]})
    comparison_path = root / "outputs/03-compare-views/comparison.json"
    _write_json(comparison_path, comparison)
    geometry.pop("plan_sha256")
    geometry.update(succeeded_views=view_ids, comparison={"path_hint": "outputs/03-compare-views/comparison.json", **file_identity(comparison_path)}, view_set={"path_hint": "outputs/02-mineru-three-view/view-set.json", **file_identity(view_set_path), "receipt_sha256": view_set["receipt_sha256"]})
    geometry = sealed(geometry.pop("schema"), geometry, digest_key="plan_sha256")
    _write_json(stage4 / "visual/geometry_plan.json", geometry)
    _write_json(stage4 / "merge_packets/pages/page-001.json", packet)
    _write_json(stage4 / "merge_packets/merge_index.json", {"by_source_page": [{"source_page": 1, "semantic_role": "body", "priority_score": 0, "packet": "pages/page-001.json"}], "by_priority": []})
    return view_set, comparison, geometry


def _comparison_rebase_fixture(tmp_path: Path) -> tuple[dict, tuple]:
    source_root = tmp_path / "source"
    source_root.mkdir()
    _synthetic_replay_source(source_root)
    fresh_stage2 = tmp_path / "fresh/outputs/02-mineru-three-view"
    shutil.copytree(source_root / "outputs/02-mineru-three-view/views/v/artifacts", fresh_stage2 / "views/v/artifacts")
    source_view_path = source_root / "outputs/02-mineru-three-view/views/v/view.json"
    fresh_view = replay._rebase_view(json.loads(source_view_path.read_text(encoding="utf-8")), "C" * 64, _origin())
    _write_json(fresh_stage2 / "views/v/view.json", fresh_view)
    source_vs_path = source_root / "outputs/02-mineru-three-view/view-set.json"
    fresh_vs = replay._rebase_view_set(json.loads(source_vs_path.read_text(encoding="utf-8")), "C" * 64, {"v": fresh_view}, fresh_stage2, _origin())
    _write_json(fresh_stage2 / "view-set.json", fresh_vs)
    prepared = tmp_path / "fresh/outputs/01-prepare-inputs/prepared/sample_pages.json"
    prepared.parent.mkdir(parents=True)
    shutil.copyfile(source_root / "outputs/01-prepare-inputs/prepared/sample_pages.json", prepared)
    source = json.loads((source_root / "outputs/03-compare-views/comparison.json").read_text(encoding="utf-8"))
    args = ("C" * 64, prepared, fresh_stage2 / "view-set.json", fresh_stage2, source_root / "outputs/02-mineru-three-view", _origin())
    return source, args


@pytest.mark.parametrize("poison", [r"C:\outside\root", r"\\server\share\root", r"\\?\C:\device\root", r"..\outside", r"Z:\does-not-exist\root"])
def test_comparison_rebase_rejects_poisoned_origin_root_without_resolving_it(tmp_path: Path, poison: str):
    source, args = _comparison_rebase_fixture(tmp_path)
    source["views"]["v"]["root"] = poison
    with pytest.raises(replay.ReplayError, match="origin_comparison_root_mismatch"):
        replay._rebase_comparison(source, *args)


@pytest.mark.parametrize("poison", [r"C:\outside\steal.md", r"\\server\share\steal.md", r"\\.\NUL", r"..\steal.md", r"Z:\missing\steal.md"])
def test_comparison_rebase_rejects_poisoned_origin_artifact_without_resolving_it(tmp_path: Path, poison: str):
    source, args = _comparison_rebase_fixture(tmp_path)
    source["views"]["v"]["artifacts"]["markdown"] = poison
    with pytest.raises(replay.ReplayError, match="origin_comparison_path_mismatch"):
        replay._rebase_comparison(source, *args)


def test_comparison_rebase_derives_all_operational_refs_from_sealed_inventory(tmp_path: Path):
    source, args = _comparison_rebase_fixture(tmp_path)
    fresh = replay._rebase_comparison(source, *args)
    assert fresh["schema"] == replay.COMPARISON_SCHEMA
    assert all(ref["base"] == "view_artifact_root" and ref["view_id"] == "v" for ref in fresh["views"]["v"]["artifacts"].values())
    implementation = Path(replay.__file__).read_text(encoding="utf-8")
    body = implementation[implementation.index("def _rebase_comparison("):implementation.index("def _portable_projection(")]
    assert "Path(str(identity" not in body and ".resolve().relative_to" not in body


@pytest.mark.parametrize("through", ["01", "02", "01-prepare-inputs", "02-mineru-three-view"])
def test_verify_source_rejects_non_runnable_partial_prefix_before_filesystem_access(through: str):
    with pytest.raises(replay.ReplayError, match="partial_prefix_not_runnable"):
        replay.verify_replay_source(Path("missing-contract"), Path("missing-source"), Path("missing-run"), through, object())  # type: ignore[arg-type]


def test_archived_source_closure_preserves_old_producer_and_seals_current_transformer(monkeypatch):
    old = {"path": "kb_creator/scripts/run_mineru_three_view.ps1", "bytes": 1, "sha256": "A" * 64}
    current = {"path": old["path"], "bytes": 2, "sha256": "B" * 64}
    run = {"implementation": {"files": [old]}}
    row = {"implementation_paths": [old["path"]]}
    monkeypatch.setattr(replay, "_current_row", lambda path: current)
    with pytest.raises(replay.ReplayError, match="producer_closure_changed"):
        replay._closure_for(run, row)
    closure = replay._closure_for(run, row, archived_source=True)
    assert closure["source"] == [old]
    assert closure["current"] == [current]
    assert closure["producer_closure_sha256"] != closure["current_transformer_closure_sha256"]


def test_archived_source_public_entry_is_through03_only(monkeypatch):
    observed = {}
    monkeypatch.setattr(replay, "_verify_replay_source", lambda *args, **kwargs: observed.update(kwargs) or {"state": "eligible"})
    assert replay.verify_archived_replay_source(Path("c"), Path("s"), Path("r"), "03", object()) == {"state": "eligible"}  # type: ignore[arg-type]
    assert observed["archived_source"] is True
    with pytest.raises(replay.ReplayError, match="archived_source_requires_through03"):
        replay.verify_archived_replay_source(Path("c"), Path("s"), Path("r"), "04", object())  # type: ignore[arg-type]


def test_archived_transform_preflight_is_explicit_and_read_only(monkeypatch):
    observed = {}
    monkeypatch.setattr(replay, "verify_replay_transform", lambda *args, **kwargs: observed.update(kwargs) or {"published": False})
    assert replay.verify_archived_replay_transform(Path("c"), Path("s"), Path("r"), object()) == {"published": False}  # type: ignore[arg-type]
    assert observed == {"archived_source": True}


def test_archived_source_provenance_rejects_old_or_current_identity_tamper():
    old = {"path": "kb_creator/scripts/run_mineru_three_view.ps1", "bytes": 1, "sha256": "A" * 64}
    current = {"path": old["path"], "bytes": 2, "sha256": "B" * 64}
    closure = {
        "files": [current], "producer_closure_sha256": sha256_bytes(canonical_bytes([current])),
        "archived_source_provenance": {
            "schema": replay.ARCHIVED_SOURCE_PROVENANCE_SCHEMA,
            "recorded_source_producer": {"files": [old], "producer_closure_sha256": sha256_bytes(canonical_bytes([old]))},
            "current_transformer": {"files": [current], "producer_closure_sha256": sha256_bytes(canonical_bytes([current]))},
        },
    }
    source_manifest = {"reproducible": {"producer_closure": {"files": [old]}}}
    replay._validate_archived_source_provenance(closure, source_manifest, "02-mineru-three-view")
    changed = copy.deepcopy(closure)
    changed["archived_source_provenance"]["recorded_source_producer"]["files"][0]["sha256"] = "C" * 64
    with pytest.raises(replay.ReplayError, match="archived_source_provenance_digest"):
        replay._validate_archived_source_provenance(changed, source_manifest, "02-mineru-three-view")
    changed = copy.deepcopy(closure)
    changed["archived_source_provenance"]["current_transformer"]["files"] = [old]
    changed["archived_source_provenance"]["current_transformer"]["producer_closure_sha256"] = sha256_bytes(canonical_bytes([old]))
    with pytest.raises(replay.ReplayError, match="archived_transformer_closure_mismatch"):
        replay._validate_archived_source_provenance(changed, source_manifest, "02-mineru-three-view")


def test_hybrid_authority_dispatch_requires_explicit_completion(monkeypatch, tmp_path: Path):
    calls = []
    monkeypatch.setattr(replay, "validate_replayed_prefix", lambda root, expected_through, **kwargs: calls.append(expected_through) or object())
    assert replay.validate_replay_authorities(tmp_path) is not None
    (tmp_path / "replay").mkdir()
    (tmp_path / "replay/completion.json").write_text("{}", encoding="utf-8")
    assert replay.validate_replay_authorities(tmp_path) is not None
    assert calls == ["04-visual-merge-bundle", "03-compare-views"]


def test_hybrid_completion_schema_is_closed_and_requires_three_replayed_stages():
    schema = json.loads((Path(replay.__file__).parents[1] / "contracts/replay_hybrid_completion.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert schema["properties"]["replayed_stages"]["minItems"] == schema["properties"]["replayed_stages"]["maxItems"] == 3


@pytest.mark.parametrize("semantic,recovered_view_evidence", [(False, False), (True, False), (False, True)])
def test_synthetic_full_prefix_replay_is_atomic_fresh_and_never_accepts(monkeypatch, tmp_path: Path, semantic: bool, recovered_view_evidence: bool):
    source_root, destination = tmp_path / "source", tmp_path / "fresh"
    source_root.mkdir()
    source_run, stages = _synthetic_replay_source(
        source_root, semantic=semantic, recovered_view_evidence=recovered_view_evidence,
    )
    fresh_run = copy.deepcopy(source_run)
    fresh_run["run_id"] = "fresh"
    fresh_run["local"] = {
        "run_root": str(destination.absolute()),
        "contract_path": source_run["local"]["contract_path"],
    }
    portable = {key: value for key, value in fresh_run.items() if key not in {"local", "portable_identity_sha256"}}
    fresh_run["portable_identity_sha256"] = sha256_bytes(canonical_bytes(portable))
    eligibility = sealed("kb_creator.replay_eligibility.v1", {
        "state": "eligible", "source_run_id": source_run["run_id"], "source_run_identity_sha256": source_run["portable_identity_sha256"],
        "source_run_json": file_identity(source_root / "run.json"), "requested_prefix": list(replay.STAGE_IDS),
        "registry": {**file_identity(Path(replay.__file__).parents[1] / "contracts/reconstruction_stage_dependency_registry.v1.json"), "registry_sha256": replay.load_registry()["registry_sha256"]},
        "stages": stages, "acceptance_inferred": False, "decisions_replayed": False, "stages_05_06_replayed": False,
    }, digest_key="eligibility_sha256")
    monkeypatch.setattr(replay, "_build_fresh_run", lambda *args, **kwargs: fresh_run)
    monkeypatch.setattr(replay, "verify_replay_source", lambda *args, **kwargs: eligibility)
    monkeypatch.setattr(replay.reconstruction, "load_run", lambda path: source_run)
    relative_source_root = Path(os.path.relpath(source_root, Path.cwd()))
    result = replay.replay_run_engine(Path("contract"), Path("source"), relative_source_root, destination, "fresh", "04", object())  # type: ignore[arg-type]
    assert result["state"] == "needs_review" and result["exit_code"] == 10
    assert result["acceptance_inferred"] is False
    assert destination.is_dir()
    bridge = json.loads((destination / "replay/bridge.json").read_text(encoding="utf-8"))
    assert bridge["decisions_replayed"] is False and bridge["stages_05_06_replayed"] is False
    assert not (destination / "outputs/05-fidelity-audit").exists()
    assert not (destination / "outputs/06-materialize-candidate").exists()
    assert replay.validate_replayed_prefix(destination).bridge_sha256 == bridge["bridge_sha256"]
    if recovered_view_evidence:
        evidence = "views/v/evidence/origin-view.json"
        assert (destination / "outputs/02-mineru-three-view" / evidence).read_bytes() == (source_root / "outputs/02-mineru-three-view" / evidence).read_bytes()
    assert all(json.loads((destination / "stages" / stage / "stage.json").read_text(encoding="utf-8"))["execution"]["producer_invoked"] is False for stage in replay.STAGE_IDS)
    if semantic:
        _assert_cold_v2_authoring(destination, tmp_path)


def _assert_cold_v2_authoring(run_root: Path, tmp_path: Path) -> None:
    from kb_creator.pipeline import reconstruction_replay_resume as resume
    from kb_creator.scripts import author_reviewed_semantic_decisions as author

    authorities = replay.validate_replayed_prefix(run_root)
    review = resume.validate_replay_review_queue(authorities)
    assert review.queue["bridge"]["bridge_sha256"] == authorities.bridge_sha256
    packet = run_root / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    assert review.queue["items"][0]["merge_packet"]["sha256"] == file_identity(packet)["sha256"]
    draft_root = tmp_path / "drafts"
    _write_json(draft_root / "page-001.json", {
        "schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 1,
        "semantic_role": "body", "overlay_preference": "original_pipeline_txt",
        "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}],
        "markdown": "# Stable heading", "assets": [], "unresolved": [],
        "review": {"visual_reviewed": True, "notes": "Synthetic source heading reviewed."},
    })
    spec_path = tmp_path / "semantic-spec.json"
    _write_json(spec_path, {
        "semantic_structure_profile": "reviewed_role_outline_and_partitions_v2",
        "pages": [{"source_page": 1, "role_contract": {"role": "body", "group_id": "fixture"},
                   "units": [{"id": "heading", "kind": "heading", "representation": "atx_heading",
                              "raw_indices": [0], "start": "# Stable heading", "end": "# Stable heading", "heading_level": 1}]}],
    })
    output = tmp_path / "authored"
    author.author_drafts(run_root, draft_root, output, [spec_path])
    decision = json.loads((output / "pages/page-001.json").read_text(encoding="utf-8"))
    assert decision["semantic_structure"]["units"][0]["source_fragments"]
    decision_set = json.loads((output / "decision_set.json").read_text(encoding="utf-8"))
    assert decision_set["semantic_structure_profile"] == "reviewed_role_outline_and_partitions_v2"
    replay.reconstruction.validate_decision_set(output / "decision_set.json", review.queue, output)
    # author_drafts also executes semantic validation and the actual fidelity audit.
    allowlist = json.loads((output / "reviewed_allowlist.v3.json").read_text(encoding="utf-8"))
    assert allowlist["ocr_equivalence_classes"] == []


_JSON_PAYLOAD_EXAMPLES = {
    "prepared_manifest": ("01-prepare-inputs", "prepared/sample_pages.json"),
    "mineru_content_list": ("02-mineru-three-view", "views/original_pipeline_txt/artifacts/sample/txt/sample_content_list.json"),
    "mineru_content_list_v2": ("02-mineru-three-view", "views/original_pipeline_txt/artifacts/sample/txt/sample_content_list_v2.json"),
    "mineru_middle": ("02-mineru-three-view", "views/original_pipeline_txt/artifacts/sample/txt/sample_middle.json"),
    "mineru_model": ("02-mineru-three-view", "views/original_pipeline_txt/artifacts/sample/txt/sample_model.json"),
    "merge_index": ("04-visual-merge-bundle", "merge_packets/merge_index.json"),
    "merge_packet": ("04-visual-merge-bundle", "merge_packets/pages/page-001.json"),
}


@pytest.mark.parametrize("class_id,stage_id,pattern,shape", replay.JSON_PAYLOAD_ROUTES)
def test_every_registered_json_payload_class_accepts_only_its_observed_shape(
    tmp_path: Path, class_id: str, stage_id: str, pattern: str, shape: str
):
    assert _JSON_PAYLOAD_EXAMPLES[class_id][0] == stage_id
    relative = _JSON_PAYLOAD_EXAMPLES[class_id][1]
    assert re.fullmatch(pattern, relative)
    path = tmp_path / f"{class_id}.json"
    good = [{"nested": ["safe", {"asset": "images/safe.png"}]}] if shape == "array" else {"nested": ["safe", {"asset": "images/safe.png"}]}
    _write_json(path, good)
    replay._scan_payload(path, stage_id, relative, "B" * 64)
    _write_json(path, {} if shape == "array" else [])
    with pytest.raises(replay.ReplayError, match="invalid_json_payload_shape"):
        replay._scan_payload(path, stage_id, relative, "B" * 64)


@pytest.mark.parametrize("class_id,stage_id,pattern,shape", replay.JSON_PAYLOAD_ROUTES)
def test_every_registered_json_payload_class_recursively_rejects_poison(
    tmp_path: Path, class_id: str, stage_id: str, pattern: str, shape: str
):
    relative = _JSON_PAYLOAD_EXAMPLES[class_id][1]
    value = [{"nested": [{"path": "../../escape"}]}] if shape == "array" else {"nested": [{"path": "../../escape"}]}
    path = tmp_path / f"{class_id}.json"
    _write_json(path, value)
    with pytest.raises(replay.ReplayError, match="path_or_identity_poison_in_payload"):
        replay._scan_payload(path, stage_id, relative, "B" * 64)


def test_run07_json_artifact_census_covers_live_inventory_when_present():
    fixture_path = Path(__file__).parent / "fixtures/run07_json_artifact_shape_census.sanitized.json"
    census = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert set(census) == {"schema", "source_run_id", "scope", "total_json_files", "typed_wrapper_count", "path_neutral_payload_count", "classes"}
    assert census["schema"] == "kb_creator.replay_json_artifact_shape_census.v1"
    assert all(set(row) == {"class_id", "authority_kind", "top_level", "observed_count", "bearing_fields"} for row in census["classes"])
    root = Path(replay.__file__).parents[1] / "working/dissociation/reconstruction/20260915-cpu-first-07/outputs"
    if not root.is_dir():
        pytest.skip("immutable run-07 is not present on this checkout")
    wrapper_classes = {
        "command": "typed_command", "view_set": "typed_view_set", "view": "typed_view",
        "comparison": "typed_comparison", "visual_execution": "typed_visual_execution",
        "geometry": "typed_geometry", "visual_manifest": "typed_visual_manifest",
    }
    observed: dict[str, dict[str, object]] = {}
    total = typed = payloads = 0
    for stage_id in replay.STAGE_IDS:
        stage_root = root / stage_id
        for path in sorted(stage_root.rglob("*.json")):
            total += 1
            relative = path.relative_to(stage_root).as_posix()
            route = replay._classify(stage_id, relative)
            value = json.loads(path.read_text(encoding="utf-8"))
            top = "array" if isinstance(value, list) else "object" if isinstance(value, dict) else "scalar"
            if route == "payload":
                class_id, expected_shape = replay._json_payload_route(stage_id, relative)
                assert top == expected_shape
                authority_kind = "path_neutral_payload"; payloads += 1
            else:
                class_id = wrapper_classes[route]
                assert top == "object"
                authority_kind = "typed_wrapper"; typed += 1
            row = observed.setdefault(class_id, {"authority_kind": authority_kind, "top_level": top, "observed_count": 0})
            assert row["authority_kind"] == authority_kind and row["top_level"] == top
            row["observed_count"] = int(row["observed_count"]) + 1
    expected = {row["class_id"]: {key: row[key] for key in ("authority_kind", "top_level", "observed_count")} for row in census["classes"]}
    assert observed == expected
    assert (total, typed, payloads) == (census["total_json_files"], census["typed_wrapper_count"], census["path_neutral_payload_count"])


def _visual_projection_fixture() -> dict:
    return {
        "inputs": {
            "source": {"path": r"C:\\old\\source.pdf", "sha256": "1" * 64},
            "reconstruction_contract": {"path": r"C:\\old\\contract.json", "sha256": "2" * 64},
            "raw_receipt": {"path": r"C:\\old\\view-set.json"},
            "comparison": {"path": r"C:\\old\\comparison.json"},
            "raw_root": r"C:\\old\\stage2",
            "preparation_manifest": {"path": r"C:\\old\\prepared.json"},
            "dpi": 110,
        },
        "layouts": {"v": {"path": r"C:\\old\\layout.pdf", "sha256": "3" * 64}},
        "execution": {"commands": [[r"C:\\old\\tool.exe"]]},
        "counts": {"rendered_pages": 1},
        "inventory_scope": "closed",
        "inventory_exclusions": ["visual/visual_manifest.json"],
        "files": [
            {"path": "visual/v/pages/page-001.png", "bytes": 7, "sha256": "4" * 64, "dimensions": [10, 20]},
            {"path": "visual/geometry_plan.json", "bytes": 8, "sha256": "5" * 64},
        ],
        "geometry_plan": {"path": "visual/geometry_plan.json", "sha256": "5" * 64},
    }


@pytest.mark.parametrize("mutation", [
    lambda value: value["inputs"]["source"].update(path=r"Z:\\poison\\source.pdf"),
    lambda value: value["inputs"]["reconstruction_contract"].update(path=r"Z:\\poison\\contract.json"),
    lambda value: value["inputs"]["reconstruction_contract"].update(sha256="F" * 64),
    lambda value: value["inputs"]["raw_receipt"].update(path=r"Z:\\poison\\view-set.json"),
    lambda value: value["inputs"]["comparison"].update(path=r"Z:\\poison\\comparison.json"),
    lambda value: value["inputs"].update(raw_root=r"Z:\\poison\\stage2"),
    lambda value: value["inputs"]["preparation_manifest"].update(path=r"Z:\\poison\\prepared.json"),
    lambda value: value["layouts"]["v"].update(path=r"Z:\\poison\\layout.pdf"),
    lambda value: value.update(execution={"commands": [[r"Z:\\poison\\tool.exe"]]}),
    lambda value: value["files"][0].update(dimensions=[999, 999]),
    lambda value: value["files"][1].update(bytes=999, sha256="E" * 64),
    lambda value: value.update(geometry_plan={"path": "poison.json", "sha256": "E" * 64}),
])
def test_visual_projection_normalizes_only_guarded_legacy_representation_fields(mutation):
    canonical_contract = "A" * 64
    baseline = replay._visual_projection(
        _visual_projection_fixture(), canonical_contract_sha256=canonical_contract
    )
    changed = _visual_projection_fixture()
    mutation(changed)
    assert replay._visual_projection(
        changed, canonical_contract_sha256=canonical_contract
    ) == baseline


@pytest.mark.parametrize("mutation", [
    lambda value: value["inputs"]["source"].update(sha256="F" * 64),
    lambda value: value["inputs"].update(dpi=111),
    lambda value: value["layouts"]["v"].update(sha256="F" * 64),
    lambda value: value["counts"].update(rendered_pages=2),
    lambda value: value.update(inventory_scope="changed"),
    lambda value: value["inventory_exclusions"].append("extra"),
    lambda value: value["files"][0].update(bytes=8),
    lambda value: value["files"][0].update(sha256="F" * 64),
    lambda value: value["files"][0].update(path="visual/v/pages/page-002.png"),
])
def test_visual_projection_preserves_every_semantic_content_domain(mutation):
    canonical_contract = "A" * 64
    baseline = replay._visual_projection(
        _visual_projection_fixture(), canonical_contract_sha256=canonical_contract
    )
    changed = _visual_projection_fixture()
    mutation(changed)
    assert replay._visual_projection(
        changed, canonical_contract_sha256=canonical_contract
    ) != baseline


def test_comparison_block_accepts_only_positive_v2_table_text_evidence():
    evidence = {
        "text_level": None,
        "v2_title": False,
        "middle_title": False,
        "markdown_heading": False,
        "model_title": False,
        "v2_table_text": True,
    }
    block = {
        "raw_index": 0,
        "page_idx": 0,
        "source_page": 1,
        "type": "table",
        "bbox": [0, 0, 1, 1],
        "text": "A | B",
        "semantic_evidence": evidence,
        "assets": [],
    }
    replay._validate_block(block, "comparison block")
    with pytest.raises(replay.ReplayError, match="shape_mismatch"):
        replay._validate_block(
            {**block, "semantic_evidence": {**evidence, "v2_table_text": False}},
            "comparison block",
        )
    with pytest.raises(replay.ReplayError, match="shape_mismatch"):
        replay._validate_block(
            {**block, "semantic_evidence": {**evidence, "unknown": True}},
            "comparison block",
        )


def test_pairwise_accepts_closed_image_heading_overlap_conflict():
    row = {
        "bbox_matches": [],
        "left_unmatched": [],
        "right_unmatched": [],
        "semantic_conflicts": [{
            "kind": "image_heading_overlap",
            "asset_side": "left",
            "heading_side": "right",
            "asset_raw_index": 1,
            "heading_raw_index": 2,
            "bbox_iou": 1.0,
            "resolution": None,
        }],
    }
    replay._validate_pairwise({"left__right": row})
    with pytest.raises(replay.ReplayError, match="shape_mismatch"):
        replay._validate_pairwise({
            "left__right": {
                **row,
                "semantic_conflicts": [{**row["semantic_conflicts"][0], "unknown": True}],
            }
        })
