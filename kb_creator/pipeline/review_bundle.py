"""Create a portable, sealed bundle for human review of a candidate.

The bundle deliberately carries only relative destination paths.  Its manifest
therefore remains useful after the package is copied to another machine, and
does not disclose the local working paths from which the candidate was built.
"""
from __future__ import annotations

import json
import os
import shutil
import uuid
from pathlib import Path, PurePosixPath
from typing import Any

from .identity import (
    assert_existing_path_components_are_not_reparse,
    canonical_bytes,
    file_identity,
    is_reparse_point,
    sha256_bytes,
)
from .manifests import sealed, validate_seal


MANIFEST_NAME = "REVIEW_BUNDLE.json"
README_NAME = "README.md"
SCHEMA = "kb_creator.review_bundle.v1"


class ReviewBundleError(ValueError):
    """The requested review bundle is unsafe, incomplete, or has drifted."""


def _relative_destination(value: object) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ReviewBundleError("review bundle destination must be a non-empty POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ReviewBundleError("review bundle destination escapes its root")
    return path


def _is_prefix(left: PurePosixPath, right: PurePosixPath) -> bool:
    return len(left.parts) <= len(right.parts) and right.parts[: len(left.parts)] == left.parts


def _assert_safe_tree(path: Path) -> None:
    if is_reparse_point(path):
        raise ReviewBundleError(f"review bundle sources cannot contain symlinks or reparse points: {path}")
    if path.is_file():
        return
    if not path.is_dir():
        raise ReviewBundleError(f"review bundle source is neither a file nor a directory: {path}")
    for child in path.iterdir():
        _assert_safe_tree(child)


def _metadata_is_json(value: Any) -> bool:
    if value is None or isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, list):
        return all(_metadata_is_json(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _metadata_is_json(item) for key, item in value.items())
    return False


def _has_acceptance_claim(value: Any) -> bool:
    """Keep an in-progress review package from being labelled as accepted."""
    forbidden = {
        "accepted",
        "acceptance",
        "accepted_for_release",
        "release_accepted",
        "candidate_for_release_review",
        "released",
    }
    if isinstance(value, str):
        return value.casefold() in forbidden
    if isinstance(value, list):
        return any(_has_acceptance_claim(item) for item in value)
    if isinstance(value, dict):
        for key, item in value.items():
            if key.casefold() in {"accepted", "acceptance", "release_accepted"} and item:
                return True
            if _has_acceptance_claim(item):
                return True
    return False


def _validate_metadata(metadata: object) -> dict[str, Any]:
    if not isinstance(metadata, dict) or not _metadata_is_json(metadata):
        raise ReviewBundleError("review bundle metadata must be JSON-compatible object")
    if metadata.get("state") != "awaiting_user_review":
        raise ReviewBundleError("review bundle metadata state must be awaiting_user_review")
    if _has_acceptance_claim(metadata):
        raise ReviewBundleError("review bundle metadata must not claim acceptance")
    # JSON round-tripping avoids caller mutation while retaining only portable values.
    return json.loads(json.dumps(metadata, ensure_ascii=False, sort_keys=True))


def _add_parent_directories(path: PurePosixPath, directories: set[str]) -> None:
    parent = path.parent
    while parent.parts:
        directories.add(parent.as_posix())
        parent = parent.parent


def _plan_entries(entries: object) -> tuple[list[dict[str, Any]], set[str]]:
    if not isinstance(entries, list) or not entries:
        raise ReviewBundleError("review bundle requires one or more selections")
    parsed: list[tuple[Path, PurePosixPath, str]] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"source", "destination", "role"}:
            raise ReviewBundleError("each review bundle selection requires source, destination, and role")
        source = entry["source"]
        if not isinstance(source, Path):
            raise ReviewBundleError("review bundle source must be pathlib.Path")
        destination = _relative_destination(entry["destination"])
        role = entry["role"]
        if not isinstance(role, str) or not role.strip():
            raise ReviewBundleError("review bundle selection role must be non-empty")
        if destination.as_posix() in {MANIFEST_NAME, README_NAME}:
            raise ReviewBundleError("review bundle destination is reserved for generated control files")
        if not source.exists():
            raise ReviewBundleError(f"review bundle source does not exist: {source}")
        _assert_safe_tree(source)
        parsed.append((source, destination, role))

    for index, (_, destination, _) in enumerate(parsed):
        for _, other, _ in parsed[index + 1 :]:
            if _is_prefix(destination, other) or _is_prefix(other, destination):
                raise ReviewBundleError("review bundle selection destinations collide or overlap")

    files: list[dict[str, Any]] = []
    directories: set[str] = set()
    seen_files: set[str] = set()
    for source, destination, role in parsed:
        if source.is_file():
            targets = [(source, destination)]
        else:
            directories.add(destination.as_posix())
            targets = []
            for child in sorted(source.rglob("*"), key=lambda item: item.as_posix()):
                relative = PurePosixPath(child.relative_to(source).as_posix())
                target = destination / relative
                if child.is_dir():
                    directories.add(target.as_posix())
                elif child.is_file():
                    targets.append((child, target))
                else:
                    raise ReviewBundleError(f"review bundle source contains an unsupported path: {child}")
        for child, target in targets:
            target_name = target.as_posix()
            if target_name in seen_files or target_name in directories:
                raise ReviewBundleError("review bundle file destination collides with another selection")
            seen_files.add(target_name)
            _add_parent_directories(target, directories)
            files.append({"source": child, "path": target_name, "role": role})
    if seen_files.intersection(directories):
        raise ReviewBundleError("review bundle file and directory destinations collide")
    return sorted(files, key=lambda item: item["path"]), directories


def _readme(metadata: dict[str, Any], files: list[dict[str, Any]]) -> str:
    roles: dict[str, list[str]] = {}
    for item in files:
        roles.setdefault(item["role"], []).append(item["path"])
    lines = [
        "# Review bundle",
        "",
        "This package is a candidate for user proofreading and review.",
        "It does not record acceptance or release.",
        "",
        f"Review state: `{metadata['state']}`",
        "",
        "## Included artifacts",
        "",
    ]
    for role in sorted(roles):
        lines.append(f"- `{role}`: {len(roles[role])} file(s)")
        for path in roles[role]:
            lines.append(f"  - `{path}`")
    lines.extend(["", f"Verify the copied package with `{MANIFEST_NAME}` before review.", ""])
    return "\n".join(lines)


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_review_bundle(output_root: Path, *, entries: list[dict[str, Any]], metadata: dict[str, Any]) -> dict[str, Any]:
    """Copy selected files/trees into a sealed, relocatable review bundle.

    ``output_root`` must be absent.  All preflight checks finish before a
    staging directory is created, so invalid selections do not materialize a
    partial package.
    """
    if not isinstance(output_root, Path) or output_root.exists() or not output_root.parent.is_dir():
        raise ReviewBundleError("review bundle output root must be an absent pathlib.Path")
    assert_existing_path_components_are_not_reparse(output_root.parent)
    planned_files, directories = _plan_entries(entries)
    clean_metadata = _validate_metadata(metadata)

    stage = output_root.parent / f".{output_root.name}.review-bundle-stage-{uuid.uuid4().hex}"
    try:
        stage.mkdir(parents=False)
        for directory in sorted(directories):
            (stage / Path(*PurePosixPath(directory).parts)).mkdir(parents=True, exist_ok=False)
        inventory: list[dict[str, Any]] = []
        for item in planned_files:
            destination = stage / Path(*PurePosixPath(item["path"]).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(item["source"], destination)
            inventory.append({"path": item["path"], "role": item["role"], **file_identity(destination)})
        readme_path = stage / README_NAME
        readme_path.write_text(_readme(clean_metadata, planned_files), encoding="utf-8", newline="\n")
        inventory.append({"path": README_NAME, "role": "review_bundle_readme", **file_identity(readme_path)})
        inventory.sort(key=lambda item: item["path"])
        manifest = sealed(
            SCHEMA,
            {
                "metadata": clean_metadata,
                "directories": sorted(directories),
                "files": inventory,
                "inventory_sha256": sha256_bytes(canonical_bytes(inventory)),
            },
            digest_key="manifest_sha256",
        )
        _write_json(stage / MANIFEST_NAME, manifest)
        if output_root.exists():
            raise ReviewBundleError("review bundle output root was created during materialization")
        os.replace(stage, output_root)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise
    return verify_review_bundle(output_root)


def _walk_bundle(root: Path) -> tuple[set[str], set[str]]:
    files: set[str] = set()
    directories: set[str] = set()
    for child in root.rglob("*"):
        if is_reparse_point(child):
            raise ReviewBundleError(f"review bundle contains a symlink or reparse point: {child}")
        relative = child.relative_to(root).as_posix()
        if child.is_dir():
            directories.add(relative)
        elif child.is_file():
            files.add(relative)
        else:
            raise ReviewBundleError(f"review bundle contains an unsupported path: {child}")
    return files, directories


def verify_review_bundle(root: Path) -> dict[str, Any]:
    """Verify the sealed, complete inventory without relying on its original path."""
    if not isinstance(root, Path) or not root.is_dir() or is_reparse_point(root):
        raise ReviewBundleError("review bundle root must be a normal directory")
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.is_file() or is_reparse_point(manifest_path):
        raise ReviewBundleError("review bundle manifest is missing")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReviewBundleError("review bundle manifest is unreadable") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise ReviewBundleError("review bundle manifest schema is invalid")
    try:
        validate_seal(manifest, "manifest_sha256")
    except ValueError as exc:
        raise ReviewBundleError("review bundle manifest seal is invalid") from exc
    metadata = _validate_metadata(manifest.get("metadata"))
    files = manifest.get("files")
    directories = manifest.get("directories")
    if not isinstance(files, list) or not isinstance(directories, list) or not all(isinstance(item, str) for item in directories):
        raise ReviewBundleError("review bundle inventory is invalid")
    if sha256_bytes(canonical_bytes(files)) != manifest.get("inventory_sha256"):
        raise ReviewBundleError("review bundle inventory seal is invalid")
    expected_files: dict[str, dict[str, Any]] = {}
    for record in files:
        if not isinstance(record, dict) or set(record) != {"path", "role", "bytes", "sha256"}:
            raise ReviewBundleError("review bundle file inventory record is invalid")
        path = _relative_destination(record["path"])
        if path.as_posix() == MANIFEST_NAME or not isinstance(record["role"], str):
            raise ReviewBundleError("review bundle file inventory record is invalid")
        if not isinstance(record["bytes"], int) or record["bytes"] < 0 or not isinstance(record["sha256"], str):
            raise ReviewBundleError("review bundle file inventory record is invalid")
        if path.as_posix() in expected_files:
            raise ReviewBundleError("review bundle file inventory has duplicates")
        expected_files[path.as_posix()] = record
    expected_directories = {_relative_destination(item).as_posix() for item in directories}
    if len(expected_directories) != len(directories) or set(expected_files).intersection(expected_directories):
        raise ReviewBundleError("review bundle directory inventory is invalid")
    if expected_files.get(README_NAME, {}).get("role") != "review_bundle_readme":
        raise ReviewBundleError("review bundle README inventory record is invalid")
    required_directories: set[str] = set()
    for path in expected_files:
        _add_parent_directories(PurePosixPath(path), required_directories)
    if not required_directories.issubset(expected_directories):
        raise ReviewBundleError("review bundle directory inventory is incomplete")
    actual_files, actual_directories = _walk_bundle(root)
    if actual_files != set(expected_files) | {MANIFEST_NAME} or actual_directories != expected_directories:
        raise ReviewBundleError("review bundle has unexpected or missing paths")
    for path, record in expected_files.items():
        if file_identity(root / Path(*PurePosixPath(path).parts)) != {"bytes": record["bytes"], "sha256": record["sha256"]}:
            raise ReviewBundleError(f"review bundle file identity mismatch: {path}")
    return {
        "schema": SCHEMA,
        "state": metadata["state"],
        "bundle_root": str(root),
        "file_count": len(expected_files),
        "manifest_sha256": manifest["manifest_sha256"],
        "inventory_sha256": manifest["inventory_sha256"],
    }
