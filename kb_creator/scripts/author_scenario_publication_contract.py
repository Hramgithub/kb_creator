#!/usr/bin/env python3
"""Author one identity-bound publication contract from a closed blueprint."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_creator.pipeline.identity import (  # noqa: E402
    assert_existing_path_components_are_not_reparse,
    canonical_bytes,
    file_identity,
)
from kb_creator.pipeline.publication import (  # noqa: E402
    MANDATORY_PACKAGE_ROLES,
    PublicationControlError,
    _validate_contract,
)


BLUEPRINT_SCHEMA = "kb_creator.scenario_publication_blueprint.v1"
CONTRACT_SCHEMA = "kb_creator.scenario_publication_contract.v1"
CONFIG_ROLES = (
    "master_en",
    "master_ru",
    "artview",
    "html",
    "docx",
    "pdf",
    "package",
)
UPSTREAM_ROLES = {
    "reconstructed_en",
    "reconstruction_manifest",
    "reconstruction_qa",
    "source_identity",
}
ARTVIEW_ROLES = {
    "candidate_manifest",
    "review_html",
    "accepted_decisions",
    "application_receipt",
    "effective_visual_config",
    "bundle_inventory",
    "candidate_binaries",
    "source_context",
}
SHA256 = re.compile(r"^[0-9A-F]{64}$")
SCENARIO_ID = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
WINDOWS_UNSAFE_COMPONENT_CHARS = frozenset('<>:"|?*')
WINDOWS_RESERVED_COMPONENTS = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


class PublicationContractAuthoringError(ValueError):
    """Stable fail-closed error for blueprint authoring."""


def _duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PublicationContractAuthoringError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise PublicationContractAuthoringError(f"non-finite JSON number: {value}")


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        assert_existing_path_components_are_not_reparse(path)
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_duplicate_keys,
            parse_constant=_reject_nonfinite,
        )
    except PublicationContractAuthoringError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise PublicationContractAuthoringError(f"cannot read {label}: {error}") from error
    if not isinstance(value, dict):
        raise PublicationContractAuthoringError(f"{label} must be an object")
    return value


def _object(value: object, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise PublicationContractAuthoringError(f"{label} has unknown or missing fields")
    return value


def _nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PublicationContractAuthoringError(f"{label} must be a nonempty string")
    return value


def _unique_strings(
    value: object,
    label: str,
    *,
    minimum: int = 1,
    allowed: set[str] | frozenset[str] | None = None,
) -> list[str]:
    if (
        not isinstance(value, list)
        or len(value) < minimum
        or any(not isinstance(item, str) or not item.strip() for item in value)
        or len(value) != len(set(value))
    ):
        raise PublicationContractAuthoringError(f"{label} must contain unique nonempty strings")
    if allowed is not None and not set(value).issubset(allowed):
        raise PublicationContractAuthoringError(f"{label} contains an unsupported value")
    return value


def _exact_integer(value: object, expected: int, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value != expected:
        raise PublicationContractAuthoringError(f"invalid {label}")


def _validate_qa(value: object, label: str) -> list[str]:
    return _unique_strings(value, label)


def _validate_blueprint(value: dict[str, Any]) -> None:
    _object(
        value,
        {
            "schema",
            "blueprint_revision",
            "scenario",
            "upstream",
            "artifact_names",
            "configs",
            "master_en",
            "master_ru",
            "artview",
            "html",
            "docx",
            "pdf",
            "package",
            "tool_policy",
        },
        "publication blueprint",
    )
    if value["schema"] != BLUEPRINT_SCHEMA:
        raise PublicationContractAuthoringError("invalid publication blueprint schema")
    _exact_integer(value["blueprint_revision"], 1, "blueprint revision")

    scenario = _object(
        value["scenario"],
        {"id", "title_en", "title_ru", "language_source", "language_target"},
        "scenario",
    )
    scenario_id = _nonempty_string(scenario["id"], "scenario.id")
    if not SCENARIO_ID.fullmatch(scenario_id):
        raise PublicationContractAuthoringError("invalid scenario.id")
    _nonempty_string(scenario["title_en"], "scenario.title_en")
    _nonempty_string(scenario["title_ru"], "scenario.title_ru")
    if scenario["language_source"] != "en" or scenario["language_target"] != "ru":
        raise PublicationContractAuthoringError("unsupported publication language pair")

    upstream = _object(
        value["upstream"],
        {"reconstruction_contract_sha256", "required_artifact_roles"},
        "upstream",
    )
    if not isinstance(upstream["reconstruction_contract_sha256"], str) or not SHA256.fullmatch(
        upstream["reconstruction_contract_sha256"]
    ):
        raise PublicationContractAuthoringError("invalid reconstruction contract SHA-256")
    upstream_roles = _unique_strings(
        upstream["required_artifact_roles"],
        "upstream.required_artifact_roles",
        minimum=2,
        allowed=UPSTREAM_ROLES,
    )
    if "reconstructed_en" not in upstream_roles:
        raise PublicationContractAuthoringError("upstream roles must include reconstructed_en")

    names = _object(value["artifact_names"], {"master_en", "master_ru", "html", "docx", "pdf"}, "artifact_names")
    suffixes = {"master_en": ".md", "master_ru": ".md", "html": ".html", "docx": ".docx", "pdf": ".pdf"}
    for role, suffix in suffixes.items():
        name = _nonempty_string(names[role], f"artifact_names.{role}")
        if Path(name).name != name or "\\" in name or not name.lower().endswith(suffix):
            raise PublicationContractAuthoringError(f"artifact_names.{role} must be a stable {suffix} basename")

    configs = _object(value["configs"], set(CONFIG_ROLES), "configs")
    for role in CONFIG_ROLES:
        _relative_file(configs[role], f"configs.{role}")

    master_en = _object(value["master_en"], {"profile", "required_qa"}, "master_en")
    _nonempty_string(master_en["profile"], "master_en.profile")
    _validate_qa(master_en["required_qa"], "master_en.required_qa")

    master_ru = _object(value["master_ru"], {"profile", "terminology", "packet_policy", "required_qa"}, "master_ru")
    _nonempty_string(master_ru["profile"], "master_ru.profile")
    terminology = _unique_strings(master_ru["terminology"], "master_ru.terminology")
    for index, path in enumerate(terminology):
        _relative_file(path, f"master_ru.terminology[{index}]")
    if master_ru["packet_policy"] != "ordered_hash_bound_units_v1":
        raise PublicationContractAuthoringError("invalid master_ru.packet_policy")
    _validate_qa(master_ru["required_qa"], "master_ru.required_qa")

    artview = _object(value["artview"], {"required_bundle_roles", "decision_schema", "decision_version"}, "artview")
    artview_roles = _unique_strings(
        artview["required_bundle_roles"],
        "artview.required_bundle_roles",
        minimum=4,
        allowed=ARTVIEW_ROLES,
    )
    if "accepted_decisions" not in artview_roles:
        raise PublicationContractAuthoringError("ArtView roles must include accepted_decisions")
    if (artview["decision_schema"], artview["decision_version"]) not in {
        ("kb_creator.scenario_artview_decisions.v3", 3),
        ("kb_creator.scenario_artview_decisions.v4", 4),
    }:
        raise PublicationContractAuthoringError("invalid ArtView decision schema")

    for role, adapter in (
        ("html", "translator_build_production_html_v1"),
        ("docx", "production_docx_explicit_config_v1"),
    ):
        policy = _object(value[role], {"adapter", "required_qa"}, role)
        if policy["adapter"] != adapter:
            raise PublicationContractAuthoringError(f"invalid {role} adapter")
        _validate_qa(policy["required_qa"], f"{role}.required_qa")

    pdf = _object(value["pdf"], {"adapter", "export_policy", "required_qa"}, "pdf")
    export = _object(pdf["export_policy"], {"document_input_role", "format", "all_pages", "fresh_export"}, "pdf.export_policy")
    if pdf["adapter"] != "docx_pdf_export_v1" or export != {
        "document_input_role": "accepted_docx",
        "format": "pdf",
        "all_pages": True,
        "fresh_export": True,
    }:
        raise PublicationContractAuthoringError("invalid accepted-DOCX-only PDF policy")
    _validate_qa(pdf["required_qa"], "pdf.required_qa")

    package = _object(value["package"], {"required_roles", "stable_names", "verifier_version"}, "package")
    package_roles = _unique_strings(package["required_roles"], "package.required_roles", minimum=22, allowed=MANDATORY_PACKAGE_ROLES)
    if len(package_roles) != 22 or set(package_roles) != MANDATORY_PACKAGE_ROLES:
        raise PublicationContractAuthoringError("package roles must be the exact mandatory set")
    if package["stable_names"] is not True:
        raise PublicationContractAuthoringError("package stable_names must be true")
    _exact_integer(package["verifier_version"], 1, "package verifier version")

    tool_policy = _object(value["tool_policy"], {"repository_tool_root", "allowed_system_tools"}, "tool_policy")
    if tool_policy != {
        "repository_tool_root": ".tools",
        "allowed_system_tools": ["powershell", "microsoft_word_com"],
    }:
        raise PublicationContractAuthoringError("invalid publication tool policy")


def _relative_file(value: object, label: str) -> PurePosixPath:
    text = _nonempty_string(value, label)
    windows = PureWindowsPath(text)
    posix = PurePosixPath(text)
    if (
        "\\" in text
        or ":" in text
        or text.startswith("/")
        or windows.drive
        or windows.is_absolute()
        or posix.is_absolute()
        or any(part in {"", ".", ".."} for part in posix.parts)
        or posix.as_posix() != text
    ):
        raise PublicationContractAuthoringError(f"{label} must be a normalized config_root-relative path")
    return posix


def _config_root(path: Path) -> Path:
    try:
        assert_existing_path_components_are_not_reparse(path)
        root = path.resolve(strict=True)
    except (OSError, ValueError) as error:
        raise PublicationContractAuthoringError(f"invalid config_root: {error}") from error
    if not root.is_dir():
        raise PublicationContractAuthoringError("config_root must be an existing directory")
    return root


def _identity_for(root: Path, relative_value: object, label: str) -> dict[str, Any]:
    relative = _relative_file(relative_value, label)
    candidate = root.joinpath(*relative.parts)
    try:
        assert_existing_path_components_are_not_reparse(candidate)
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as error:
        raise PublicationContractAuthoringError(f"unsafe or missing {label}: {error}") from error
    if not resolved.is_file():
        raise PublicationContractAuthoringError(f"{label} must identify an existing regular file")
    try:
        identity = file_identity(resolved)
    except OSError as error:
        raise PublicationContractAuthoringError(f"cannot bind {label} identity: {error}") from error
    if identity["bytes"] < 1:
        raise PublicationContractAuthoringError(f"{label} must not be empty")
    return {"path": relative.as_posix(), **identity}


def _schema_validate_if_available(value: object, schema_name: str, label: str) -> bool:
    try:
        import jsonschema
    except ImportError:
        return False
    schema_path = REPO_ROOT / "kb_creator" / "contracts" / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.exceptions.JsonSchemaException as error:
        raise PublicationContractAuthoringError(f"{label} JSON Schema validation failed: {error.message}") from error
    return True


def _build_contract(blueprint: dict[str, Any], root: Path) -> dict[str, Any]:
    config_by_role = {
        role: _identity_for(root, blueprint["configs"][role], f"configs.{role}")
        for role in CONFIG_ROLES
    }
    terminology = [
        _identity_for(root, path, f"master_ru.terminology[{index}]")
        for index, path in enumerate(blueprint["master_ru"]["terminology"])
    ]
    return {
        "schema": CONTRACT_SCHEMA,
        "contract_revision": 1,
        "scenario": dict(blueprint["scenario"]),
        "upstream": dict(blueprint["upstream"]),
        "artifact_names": dict(blueprint["artifact_names"]),
        "configs": [
            {"role": role, "file": config_by_role[role]} for role in CONFIG_ROLES
        ],
        "master_en": {
            **blueprint["master_en"],
            "config": config_by_role["master_en"],
        },
        "master_ru": {
            **blueprint["master_ru"],
            "config": config_by_role["master_ru"],
            "terminology": terminology,
        },
        "artview": {
            "profile": config_by_role["artview"],
            **blueprint["artview"],
        },
        "html": {
            **blueprint["html"],
            "config": config_by_role["html"],
        },
        "docx": {
            **blueprint["docx"],
            "config": config_by_role["docx"],
        },
        "pdf": dict(blueprint["pdf"]),
        "package": dict(blueprint["package"]),
        "tool_policy": dict(blueprint["tool_policy"]),
    }


def _validate_output_path_syntax(path: Path) -> None:
    text = os.fspath(path)
    windows = PureWindowsPath(text)
    if not text or windows.drive.startswith("\\\\") or text.startswith(("\\\\", "//")):
        raise PublicationContractAuthoringError("output must be a normalized local JSON path")
    if windows.drive and not windows.is_absolute():
        raise PublicationContractAuthoringError("output must not be drive-relative")

    # A local absolute drive prefix is the only permitted colon. Any later colon
    # names an NTFS alternate data stream, including on an existing base file.
    remainder = text[len(windows.drive) :] if windows.drive else text
    if ":" in remainder:
        raise PublicationContractAuthoringError("output must not identify an alternate data stream")

    components = list(windows.parts)
    if windows.anchor and components and components[0] == windows.anchor:
        components.pop(0)
    if not components or any(component in {"", ".", ".."} for component in components):
        raise PublicationContractAuthoringError("output must be a normalized local JSON path")
    for component in components:
        if (
            component != component.strip()
            or component.endswith(".")
            or any(ord(character) < 32 for character in component)
            or any(character in WINDOWS_UNSAFE_COMPONENT_CHARS for character in component)
            or component.split(".", 1)[0].upper() in WINDOWS_RESERVED_COMPONENTS
        ):
            raise PublicationContractAuthoringError("output contains an unsafe path component")

    filename = components[-1]
    if filename.startswith(".") or not filename.endswith(".json") or not filename[:-5].strip():
        raise PublicationContractAuthoringError("output must use a visible safe .json filename")


def _validated_output_path(path: Path) -> Path:
    _validate_output_path_syntax(path)
    if os.path.lexists(path):
        raise PublicationContractAuthoringError("output target must be absent")
    parent = path.parent
    try:
        assert_existing_path_components_are_not_reparse(parent)
        resolved_parent = parent.resolve(strict=True)
        assert_existing_path_components_are_not_reparse(resolved_parent)
    except (OSError, ValueError) as error:
        raise PublicationContractAuthoringError(f"unsafe output parent: {error}") from error
    if not resolved_parent.is_dir():
        raise PublicationContractAuthoringError("output parent must be an existing directory")
    output = resolved_parent / path.name
    if os.path.lexists(output):
        raise PublicationContractAuthoringError("output target must be absent")
    return output


def author_publication_contract(
    blueprint_path: Path,
    config_root: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Validate, bind file identities, and write exactly one absent output."""
    output_path = _validated_output_path(output_path)
    parent = output_path.parent

    blueprint = _load_object(blueprint_path, "publication blueprint")
    _validate_blueprint(blueprint)
    _schema_validate_if_available(
        blueprint,
        "scenario_publication_blueprint.v1.schema.json",
        "publication blueprint",
    )
    root = _config_root(config_root)
    contract = _build_contract(blueprint, root)
    payload = canonical_bytes(contract) + b"\n"

    staging: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{output_path.name}.validation.",
            suffix=".json",
            dir=parent,
            delete=False,
        ) as stream:
            stream.write(payload)
            staging = Path(stream.name)
        try:
            _validate_contract(staging, root)
        except PublicationControlError as error:
            raise PublicationContractAuthoringError(
                f"generated contract failed runtime validation: {error}"
            ) from error
        _schema_validate_if_available(
            contract,
            "scenario_publication_contract.v1.schema.json",
            "generated publication contract",
        )
    finally:
        if staging is not None and staging.exists():
            staging.unlink()

    output_path = _validated_output_path(output_path)
    created_output = False
    try:
        with output_path.open("xb") as stream:
            created_output = True
            stream.write(payload)
    except FileExistsError as error:
        raise PublicationContractAuthoringError("output target must be absent") from error
    except OSError as error:
        if created_output and output_path.exists():
            output_path.unlink()
        raise PublicationContractAuthoringError(f"cannot write output: {error}") from error
    return contract


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Author an identity-bound scenario publication contract."
    )
    parser.add_argument("--blueprint", required=True, type=Path)
    parser.add_argument("--config-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        contract = author_publication_contract(
            args.blueprint,
            args.config_root,
            args.output,
        )
    except PublicationContractAuthoringError as error:
        print(f"publication contract authoring failed: {error}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "schema": CONTRACT_SCHEMA,
                "scenario_id": contract["scenario"]["id"],
                "output": str(args.output),
                "state": "authored",
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
