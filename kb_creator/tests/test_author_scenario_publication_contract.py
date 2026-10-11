from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest

from kb_creator.pipeline.identity import canonical_bytes, file_identity
from kb_creator.pipeline.publication import MANDATORY_PACKAGE_ROLES, _validate_contract


ROOT = Path(__file__).resolve().parents[2]
AUTHOR_PATH = ROOT / "kb_creator" / "scripts" / "author_scenario_publication_contract.py"
SPEC = importlib.util.spec_from_file_location("publication_contract_author", AUTHOR_PATH)
assert SPEC and SPEC.loader
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value) + b"\n")


def _blueprint() -> dict:
    return {
        "schema": "kb_creator.scenario_publication_blueprint.v1",
        "blueprint_revision": 1,
        "scenario": {
            "id": "sample",
            "title_en": "Sample",
            "title_ru": "Образец",
            "language_source": "en",
            "language_target": "ru",
        },
        "upstream": {
            "reconstruction_contract_sha256": "A" * 64,
            "required_artifact_roles": [
                "reconstructed_en",
                "reconstruction_manifest",
                "reconstruction_qa",
                "source_identity",
            ],
        },
        "artifact_names": {
            "master_en": "MASTER_EN.md",
            "master_ru": "MASTER_RU.md",
            "html": "Sample_RU.html",
            "docx": "Sample_RU.docx",
            "pdf": "Sample_RU.pdf",
        },
        "configs": {
            "master_en": "master_en.json",
            "master_ru": "master_ru.json",
            "artview": "artview.json",
            "html": "render/html.json",
            "docx": "render/docx.json",
            "pdf": "pdf.json",
            "package": "package.json",
        },
        "master_en": {
            "profile": "neutral_v3",
            "required_qa": ["structure"],
        },
        "master_ru": {
            "profile": "neutral_v1",
            "terminology": ["terminology/coc7e.json"],
            "packet_policy": "ordered_hash_bound_units_v1",
            "required_qa": ["mechanics", "terminology"],
        },
        "artview": {
            "required_bundle_roles": [
                "candidate_manifest",
                "review_html",
                "accepted_decisions",
                "application_receipt",
                "effective_visual_config",
            ],
            "decision_schema": "kb_creator.scenario_artview_decisions.v3",
            "decision_version": 3,
        },
        "html": {
            "adapter": "translator_build_production_html_v1",
            "required_qa": ["links"],
        },
        "docx": {
            "adapter": "production_docx_explicit_config_v1",
            "required_qa": ["ooxml", "all_page_png"],
        },
        "pdf": {
            "adapter": "docx_pdf_export_v1",
            "export_policy": {
                "document_input_role": "accepted_docx",
                "format": "pdf",
                "all_pages": True,
                "fresh_export": True,
            },
            "required_qa": ["all_page_png"],
        },
        "package": {
            "required_roles": sorted(MANDATORY_PACKAGE_ROLES),
            "stable_names": True,
            "verifier_version": 1,
        },
        "tool_policy": {
            "repository_tool_root": ".tools",
            "allowed_system_tools": ["powershell", "microsoft_word_com"],
        },
    }


def _fixture(tmp_path: Path) -> tuple[Path, Path, dict]:
    config_root = tmp_path / "configs"
    config_root.mkdir(parents=True)
    blueprint = _blueprint()
    for role, relative in blueprint["configs"].items():
        _write_json(config_root / relative, {"role": role, "version": 1})
    _write_json(
        config_root / blueprint["master_ru"]["terminology"][0],
        {"terms": [{"en": "Keeper", "ru": "Хранитель"}]},
    )
    blueprint_path = tmp_path / "publication-blueprint.json"
    _write_json(blueprint_path, blueprint)
    return blueprint_path, config_root, blueprint


def test_blueprint_schema_is_closed_parseable_and_declares_exact_config_roles():
    schema = json.loads(
        (ROOT / "kb_creator" / "contracts" / "scenario_publication_blueprint.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert schema["$schema"].endswith("2020-12/schema")
    assert schema["$id"] == "kb_creator.scenario_publication_blueprint.v1"
    assert schema["additionalProperties"] is False
    configs = schema["properties"]["configs"]
    assert configs["additionalProperties"] is False
    assert configs["required"] == list(A.CONFIG_ROLES)
    assert set(configs["properties"]) == set(A.CONFIG_ROLES)
    assert schema["$defs"]["nonblank"] == {
        "type": "string",
        "minLength": 1,
        "pattern": r"\S",
    }
    assert schema["properties"]["scenario"]["properties"]["title_en"] == {
        "$ref": "#/$defs/nonblank"
    }
    assert schema["$defs"]["required_qa"]["items"] == {
        "$ref": "#/$defs/nonblank"
    }
    assert schema["$defs"]["relative_file"]["$ref"] == "#/$defs/nonblank"


def test_author_binds_all_file_identities_and_passes_runtime_validator(tmp_path):
    blueprint_path, config_root, blueprint = _fixture(tmp_path)
    output = tmp_path / "publication-contract.json"

    contract = A.author_publication_contract(blueprint_path, config_root, output)

    assert output.read_bytes() == canonical_bytes(contract) + b"\n"
    assert "acceptance" not in contract
    assert [row["role"] for row in contract["configs"]] == list(A.CONFIG_ROLES)
    for row in contract["configs"]:
        path = config_root / blueprint["configs"][row["role"]]
        assert row["file"] == {
            "path": blueprint["configs"][row["role"]],
            **file_identity(path),
        }
    terminology_path = config_root / "terminology" / "coc7e.json"
    assert contract["master_ru"]["terminology"] == [
        {"path": "terminology/coc7e.json", **file_identity(terminology_path)}
    ]
    validated, contract_sha = _validate_contract(output, config_root)
    assert validated == contract
    assert contract_sha == file_identity(output)["sha256"]


def test_author_is_byte_deterministic_and_cli_reports_authored_state(tmp_path, capsys):
    blueprint_path, config_root, _ = _fixture(tmp_path)
    replica_blueprint, replica_config_root, _ = _fixture(tmp_path / "replica")
    first = tmp_path / "first.json"
    second = tmp_path / "replica" / "second.json"

    assert A.main([
        "--blueprint", str(blueprint_path),
        "--config-root", str(config_root),
        "--output", str(first),
    ]) == 0
    A.author_publication_contract(replica_blueprint, replica_config_root, second)

    assert first.read_bytes() == second.read_bytes()
    status = json.loads(capsys.readouterr().out)
    assert status["state"] == "authored"
    assert status["scenario_id"] == "sample"


def test_existing_output_is_never_overwritten(tmp_path):
    blueprint_path, config_root, _ = _fixture(tmp_path)
    output = tmp_path / "publication-contract.json"
    output.write_bytes(b"user-owned")

    with pytest.raises(A.PublicationContractAuthoringError, match="must be absent"):
        A.author_publication_contract(blueprint_path, config_root, output)

    assert output.read_bytes() == b"user-owned"


@pytest.mark.parametrize(
    "unsafe",
    [
        "contract.json:ads",
        "C:contract.json",
        "\\\\server\\share\\contract.json",
        "contract.txt",
        "contract.JSON",
        ".contract.json",
        "CON.json",
        "unsafe?/contract.json",
        "nested/../contract.json",
        "trailing-space /contract.json",
    ],
)
def test_output_path_syntax_rejects_ads_drive_relative_unc_and_unsafe_names(unsafe):
    with pytest.raises(A.PublicationContractAuthoringError):
        A._validate_output_path_syntax(Path(unsafe))


@pytest.mark.skipif(os.name != "nt", reason="NTFS alternate data streams are Windows-specific")
def test_windows_ads_output_is_rejected_without_mutating_existing_base_file(tmp_path):
    blueprint_path, config_root, _ = _fixture(tmp_path)
    base = tmp_path / "contract.json"
    base.write_bytes(b"user-owned")
    output = Path(f"{base}:ads")

    with pytest.raises(A.PublicationContractAuthoringError, match="alternate data stream"):
        A.author_publication_contract(blueprint_path, config_root, output)

    assert base.read_bytes() == b"user-owned"
    assert not os.path.lexists(output)


def test_output_parent_reparse_guard_fails_before_blueprint_or_output_write(tmp_path, monkeypatch):
    blueprint_path, config_root, _ = _fixture(tmp_path)
    parent = tmp_path / "output"
    parent.mkdir()
    output = parent / "contract.json"
    original = A.assert_existing_path_components_are_not_reparse

    def reject_output_parent(path):
        if Path(path).absolute() == parent.absolute():
            raise ValueError("synthetic output reparse point")
        original(path)

    monkeypatch.setattr(A, "assert_existing_path_components_are_not_reparse", reject_output_parent)
    with pytest.raises(A.PublicationContractAuthoringError, match="synthetic output reparse point"):
        A.author_publication_contract(blueprint_path, config_root, output)

    assert not output.exists()


SEMANTIC_STRING_PATHS = [
    ("scenario", "title_en"),
    ("scenario", "title_ru"),
    ("configs", "master_en"),
    ("master_en", "profile"),
    ("master_en", "required_qa", 0),
    ("master_ru", "profile"),
    ("master_ru", "terminology", 0),
    ("master_ru", "required_qa", 0),
    ("html", "required_qa", 0),
    ("docx", "required_qa", 0),
    ("pdf", "required_qa", 0),
]


def _set_nested(value: object, path: tuple[object, ...], replacement: object) -> None:
    target = value
    for component in path[:-1]:
        target = target[component]
    target[path[-1]] = replacement


@pytest.mark.parametrize("path", SEMANTIC_STRING_PATHS)
def test_runtime_rejects_whitespace_only_semantic_strings_before_output(tmp_path, path):
    blueprint_path, config_root, blueprint = _fixture(tmp_path)
    _set_nested(blueprint, path, " \t\n")
    _write_json(blueprint_path, blueprint)
    output = tmp_path / "publication-contract.json"

    with pytest.raises(A.PublicationContractAuthoringError, match="nonempty"):
        A.author_publication_contract(blueprint_path, config_root, output)

    assert not output.exists()


@pytest.mark.parametrize("path", SEMANTIC_STRING_PATHS)
def test_blueprint_schema_and_runtime_reject_the_same_whitespace_only_fields(tmp_path, path):
    jsonschema = pytest.importorskip("jsonschema")
    blueprint_path, config_root, blueprint = _fixture(tmp_path)
    _set_nested(blueprint, path, " \t\n")
    _write_json(blueprint_path, blueprint)
    output = tmp_path / "publication-contract.json"
    schema = json.loads(
        (ROOT / "kb_creator" / "contracts" / "scenario_publication_blueprint.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(blueprint)
    with pytest.raises(A.PublicationContractAuthoringError):
        A.author_publication_contract(blueprint_path, config_root, output)

    assert not output.exists()


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (lambda value: value.update({"acceptance": "accepted"}), "unknown or missing"),
        (lambda value: value.pop("pdf"), "unknown or missing"),
        (lambda value: value["configs"].pop("package"), "unknown or missing"),
        (lambda value: value["configs"].update({"preview": "preview.json"}), "unknown or missing"),
        (lambda value: value["package"].update({"stable_names": False}), "stable_names"),
    ],
)
def test_blueprint_rejects_missing_extra_or_acceptance_fields_before_output(tmp_path, mutation, match):
    blueprint_path, config_root, blueprint = _fixture(tmp_path)
    mutation(blueprint)
    _write_json(blueprint_path, blueprint)
    output = tmp_path / "publication-contract.json"

    with pytest.raises(A.PublicationContractAuthoringError, match=match):
        A.author_publication_contract(blueprint_path, config_root, output)

    assert not output.exists()


def test_duplicate_config_role_key_is_rejected_during_json_load(tmp_path):
    blueprint_path, config_root, blueprint = _fixture(tmp_path)
    raw = canonical_bytes(blueprint).decode("utf-8")
    marker = '"master_en":"master_en.json"'
    blueprint_path.write_text(
        raw.replace(marker, marker + ',"master_en":"other.json"'),
        encoding="utf-8",
    )
    output = tmp_path / "publication-contract.json"

    with pytest.raises(A.PublicationContractAuthoringError, match="duplicate JSON key: master_en"):
        A.author_publication_contract(blueprint_path, config_root, output)

    assert not output.exists()


@pytest.mark.parametrize(
    "unsafe",
    [
        "../outside.json",
        "nested/../outside.json",
        "/outside.json",
        "C:/outside.json",
        "C:outside.json",
        "inside.json:stream",
        "\\\\server\\share\\outside.json",
        "nested\\outside.json",
        "./inside.json",
    ],
)
def test_config_paths_reject_traversal_absolute_drive_unc_and_backslash(tmp_path, unsafe):
    blueprint_path, config_root, blueprint = _fixture(tmp_path)
    blueprint["configs"]["html"] = unsafe
    _write_json(blueprint_path, blueprint)
    output = tmp_path / "publication-contract.json"

    with pytest.raises(A.PublicationContractAuthoringError, match="config_root-relative"):
        A.author_publication_contract(blueprint_path, config_root, output)

    assert not output.exists()


@pytest.mark.parametrize("kind", ["missing", "directory", "empty"])
def test_referenced_files_must_be_existing_nonempty_regular_files(tmp_path, kind):
    blueprint_path, config_root, blueprint = _fixture(tmp_path)
    relative = Path(blueprint["configs"]["pdf"])
    target = config_root / relative
    target.unlink()
    if kind == "directory":
        target.mkdir()
    elif kind == "empty":
        target.write_bytes(b"")
    output = tmp_path / "publication-contract.json"

    with pytest.raises(A.PublicationContractAuthoringError):
        A.author_publication_contract(blueprint_path, config_root, output)

    assert not output.exists()


def test_reparse_or_symlink_reference_is_rejected(tmp_path):
    blueprint_path, config_root, blueprint = _fixture(tmp_path)
    target = config_root / blueprint["configs"]["html"]
    target.unlink()
    outside = tmp_path / "outside.json"
    _write_json(outside, {"outside": True})
    try:
        os.symlink(outside, target)
    except OSError as error:
        pytest.skip(f"symlink creation unavailable: {error}")
    output = tmp_path / "publication-contract.json"

    with pytest.raises(A.PublicationContractAuthoringError, match="unsafe or missing"):
        A.author_publication_contract(blueprint_path, config_root, output)

    assert not output.exists()


def test_identity_binding_calls_reparse_guard_for_each_reference(tmp_path, monkeypatch):
    blueprint_path, config_root, blueprint = _fixture(tmp_path)
    output = tmp_path / "publication-contract.json"
    blocked = (config_root / blueprint["configs"]["html"]).absolute()
    original = A.assert_existing_path_components_are_not_reparse

    def reject_blocked(path):
        if Path(path).absolute() == blocked:
            raise ValueError("synthetic reparse point")
        original(path)

    monkeypatch.setattr(A, "assert_existing_path_components_are_not_reparse", reject_blocked)
    with pytest.raises(A.PublicationContractAuthoringError, match="synthetic reparse point"):
        A.author_publication_contract(blueprint_path, config_root, output)

    assert not output.exists()


def test_runtime_validation_failure_leaves_no_output(tmp_path, monkeypatch):
    blueprint_path, config_root, _ = _fixture(tmp_path)
    output = tmp_path / "publication-contract.json"

    def reject(*_args, **_kwargs):
        raise A.PublicationControlError("runtime parity probe")

    monkeypatch.setattr(A, "_validate_contract", reject)
    with pytest.raises(A.PublicationContractAuthoringError, match="runtime parity probe"):
        A.author_publication_contract(blueprint_path, config_root, output)

    assert not output.exists()
    assert not list(tmp_path.glob(".publication-contract.json.validation.*.json"))


def test_blueprint_and_generated_contract_pass_jsonschema_when_available(tmp_path):
    jsonschema = pytest.importorskip("jsonschema")
    blueprint_path, config_root, blueprint = _fixture(tmp_path)
    output = tmp_path / "publication-contract.json"
    contract = A.author_publication_contract(blueprint_path, config_root, output)

    for value, name in (
        (blueprint, "scenario_publication_blueprint.v1.schema.json"),
        (contract, "scenario_publication_contract.v1.schema.json"),
    ):
        schema = json.loads((ROOT / "kb_creator" / "contracts" / name).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(value)
