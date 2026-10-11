from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any, Iterable


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_identity(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def deterministic_inventory(root: Path) -> list[dict[str, Any]]:
    if not root.is_dir():
        raise ValueError(f"inventory root is not a directory: {root}")
    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"inventory contains a symlink: {path}")
        if path.is_file():
            records.append(
                {"path": path.relative_to(root).as_posix(), **file_identity(path)}
            )
    return records


def is_reparse_point(path: Path) -> bool:
    try:
        attributes = os.lstat(path).st_file_attributes
    except (AttributeError, FileNotFoundError, OSError):
        return path.is_symlink()
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def assert_existing_path_components_are_not_reparse(path: Path) -> None:
    candidate = path.absolute()
    existing: list[Path] = []
    while True:
        if candidate.exists():
            existing.append(candidate)
        if candidate.parent == candidate:
            break
        candidate = candidate.parent
    for component in reversed(existing):
        if is_reparse_point(component):
            raise ValueError(f"writable path crosses a reparse point: {component}")


def implementation_inventory(repo_root: Path, paths: Iterable[Path]) -> dict[str, Any]:
    records = []
    for path in sorted({item.resolve() for item in paths}):
        if not path.is_file():
            raise FileNotFoundError(path)
        records.append(
            {
                "path": path.relative_to(repo_root.resolve()).as_posix(),
                **file_identity(path),
            }
        )
    return {
        "files": records,
        "inventory_sha256": sha256_bytes(canonical_bytes(records)),
    }
