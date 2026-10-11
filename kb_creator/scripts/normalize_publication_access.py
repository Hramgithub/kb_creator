from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Callable


class PublicationAccessError(RuntimeError):
    """Raised when a published review tree cannot be made user-readable."""


def _repo_root() -> Path:
    module_root = Path(__file__).resolve().parents[2]
    # A reviewed consumer may live below working/. Its module location is not
    # the checkout root; worktrees have a .git file rather than a directory.
    for candidate in (module_root, *module_root.parents):
        if (candidate / ".git").exists() and (candidate / "kb_creator").is_dir():
            return candidate
    return module_root


def _assert_working_tree_target(target: Path, repo_root: Path) -> Path:
    resolved = target.resolve(strict=True)
    working_root = (repo_root / "kb_creator" / "working").resolve(strict=True)
    try:
        resolved.relative_to(working_root)
    except ValueError as error:
        raise PublicationAccessError(
            "publication access target must be inside kb_creator/working"
        ) from error
    if not resolved.is_dir():
        raise PublicationAccessError("publication access target must be a directory")
    return resolved


def _icacls_path() -> Path:
    system_root = os.environ.get("SystemRoot")
    if not system_root:
        raise PublicationAccessError("SystemRoot is unavailable")
    executable = Path(system_root) / "System32" / "icacls.exe"
    if not executable.is_file():
        raise PublicationAccessError("Windows icacls.exe is unavailable")
    return executable


def _desktop_user_principal() -> str:
    domain = os.environ.get("USERDOMAIN", "").strip()
    username = os.environ.get("USERNAME", "").strip()
    if (
        not domain
        or not username
        or username.casefold().startswith("codexsandbox")
        or any(character in domain + username for character in "\r\n:\"")
        or "\\" in domain
        or "\\" in username
    ):
        raise PublicationAccessError("desktop Windows user principal is unavailable")
    return f"{domain}\\{username}"


def normalize_publication_access(
    target: Path,
    *,
    repo_root: Path | None = None,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, object]:
    """Enable inherited Windows ACLs without changing artifact bytes.

    Obsidian owns ``.obsidian`` after a vault is opened, so that directory is
    deliberately outside pipeline ACL maintenance.
    """

    root = _assert_working_tree_target(target, repo_root or _repo_root())
    if os.name != "nt":
        return {
            "schema": "kb_creator.publication_access_normalization.v1",
            "state": "skipped",
            "reason": "non_windows_host",
            "target": str(root),
            "processed": [],
            "excluded": [".obsidian"],
        }

    executable = _icacls_path()
    principal = _desktop_user_principal()
    targets = [root, *(path for path in root.iterdir() if path.name != ".obsidian")]
    processed: list[str] = []
    for path in targets:
        command: list[str] = [
            str(executable),
            str(path),
            "/inheritance:e",
            "/c",
            "/q",
        ]
        if path != root:
            command.insert(3, "/t")
        result = runner(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "icacls failed").strip()
            raise PublicationAccessError(f"ACL normalization failed for {path}: {detail}")
        processed.append(path.relative_to(root).as_posix() if path != root else ".")

    for path in targets:
        rights = "(OI)(CI)(RX)" if path != root and path.is_dir() else "(RX)"
        command = [
            str(executable),
            str(path),
            "/grant",
            f"{principal}:{rights}",
            "/c",
            "/q",
        ]
        if path != root and path.is_dir():
            command.insert(4, "/t")
        result = runner(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "icacls failed").strip()
            raise PublicationAccessError(
                f"desktop read access grant failed for {path}: {detail}"
            )

    return {
        "schema": "kb_creator.publication_access_normalization.v1",
        "state": "normalized",
        "target": str(root),
        "principal": principal,
        "processed": processed,
        "excluded": [".obsidian"],
    }


def normalize_publication_access_if_managed(
    target: Path,
    *,
    repo_root: Path | None = None,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, object]:
    """Normalize real publication trees and skip isolated test/temp trees."""

    repository = repo_root or _repo_root()
    resolved = target.resolve(strict=True)
    working_root = (repository / "kb_creator" / "working").resolve(strict=True)
    try:
        resolved.relative_to(working_root)
    except ValueError:
        return {
            "schema": "kb_creator.publication_access_normalization.v1",
            "state": "skipped",
            "reason": "outside_managed_working_tree",
            "target": str(resolved),
            "processed": [],
            "excluded": [".obsidian"],
        }
    return normalize_publication_access(
        resolved,
        repo_root=repository,
        runner=runner,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Restore inherited Windows ACLs on a published review tree."
    )
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    try:
        result = normalize_publication_access(args.target)
    except (OSError, PublicationAccessError) as error:
        parser.exit(2, f"publication access normalization failed: {error}\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
