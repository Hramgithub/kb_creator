"""Resolve hash-bound MinerU extracted assets from sealed Stage02/03 authorities."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any


def _identity(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"bytes": path.stat().st_size, "sha256": digest.hexdigest().upper()}


def _relative(value: object) -> PurePosixPath:
    if not isinstance(value, str):
        raise ValueError("selected asset reference is invalid")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("selected asset reference escapes its content-list root")
    return path


def selected_asset_inventory(run_root: Path, visual_inventory: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Add every Stage02 extracted asset verified by Stage03 comparison identity."""
    run_root = run_root.resolve()
    comparison = json.loads((run_root / "outputs/03-compare-views/comparison.json").read_text(encoding="utf-8"))
    result = dict(visual_inventory)
    for view, value in comparison.get("views", {}).items():
        artifacts = value.get("artifacts", {}) if isinstance(value, dict) else {}
        ref = artifacts.get("content_list") if isinstance(artifacts, dict) else None
        artifact_root = (run_root / "outputs/02-mineru-three-view/views" / view / "artifacts").resolve()
        if isinstance(ref, dict):
            if ref.get("base") != "view_artifact_root":
                raise ValueError("comparison content-list authority is invalid")
            content_list = artifact_root / Path(*_relative(ref.get("path")).parts)
            expected_content = {"bytes": ref.get("bytes"), "sha256": ref.get("sha256")}
        elif isinstance(ref, str):
            content_list = Path(ref).resolve()
            expected_content = None
        else:
            raise ValueError("comparison content-list authority is invalid")
        try:
            content_list.relative_to(artifact_root)
        except ValueError as exc:
            raise ValueError("comparison content-list escapes view artifacts") from exc
        if not content_list.is_file() or (expected_content is not None and _identity(content_list) != expected_content):
            raise ValueError("comparison content-list identity is stale")
        entries = value.get("asset_inventory")
        if entries is None:
            continue
        if not isinstance(entries, list):
            raise ValueError("comparison asset inventory is invalid")
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {"reference", "bytes", "sha256"}:
                raise ValueError("comparison asset identity is invalid")
            asset = content_list.parent / Path(*_relative(entry["reference"]).parts)
            expected = {"bytes": entry["bytes"], "sha256": entry["sha256"]}
            if not asset.is_file() or _identity(asset) != expected:
                raise ValueError("comparison extracted asset identity is stale")
            path = asset.relative_to(run_root).as_posix()
            if path in result and result[path] != expected:
                raise ValueError("selected asset identity collision")
            result[path] = expected
    return result


def exact_selected_asset_path(inventory: dict[str, dict[str, Any]], view_id: str, source_path: str) -> str:
    source = _relative(source_path).as_posix()
    prefix = f"outputs/02-mineru-three-view/views/{view_id}/artifacts/"
    matches = [path for path in inventory if path.startswith(prefix) and path.endswith("/" + source)]
    if not matches:
        # v3 test/legacy bundles may have copied assets in Stage04. Fresh v2
        # production runs use the Stage02 path above; accepting this existing
        # inventory form keeps old sealed submissions replayable.
        legacy = f"outputs/04-visual-merge-bundle/visual/{view_id}/assets/{source}"
        matches = [legacy] if legacy in inventory else []
    if len(matches) != 1:
        raise ValueError("selected asset has no unique Stage02 inventory identity")
    return matches[0]
