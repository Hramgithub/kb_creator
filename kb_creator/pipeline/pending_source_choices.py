"""Verified pre-R1 accounting for visible pending source alternatives."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .identity import file_identity
from .mechanical_reconstruction import verify_mechanical_draft


class PendingSourceChoiceError(ValueError):
    pass


def _relative(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or value.startswith(("/", "\\")) or "\\" in value:
        raise PendingSourceChoiceError(f"{label} path is not portable")
    path = (root / value).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise PendingSourceChoiceError(f"{label} path escapes binding root") from error
    return path


def _bound(root: Path, row: Any, label: str) -> Path:
    if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256"}:
        raise PendingSourceChoiceError(f"{label} binding is malformed")
    path = _relative(root, row["path"], label)
    if not path.is_file() or file_identity(path) != {key: row[key] for key in ("bytes", "sha256")}:
        raise PendingSourceChoiceError(f"{label} identity drift")
    return path


def derive_pending_source_keys(*, review_input: Mapping[str, Any], input_path: Path,
                               binding_root: Path, run_root: Path,
                               selected_keys: set[tuple[int, str, int]],
                               coverage_owner_keys: set[tuple[int, str, int]] | None = None) -> set[tuple[int, str, int]]:
    """Derive only unselected, packet-bound pending alternatives once per operation."""
    root = Path(binding_root).resolve()
    pending = [row for row in review_input.get("source_issues", {}).get("issues", [])
               if isinstance(row, Mapping) and row.get("kind") == "translation_source_choice_pending"]
    if not pending:
        return set()
    try:
        from .review_draft import validate_review_draft_input
        from .review_draft_preparation import validate_review_draft_author_input
        sealed = validate_review_draft_input(dict(review_input))
        if json.loads(Path(input_path).read_text(encoding="utf-8")) != sealed.value:
            raise ValueError("supplied review input differs from sealed input")
        validate_review_draft_author_input(input_path=Path(input_path), binding_root=root)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise PendingSourceChoiceError(f"review input authority is invalid: {error}") from error
    candidate_manifest = _bound(root, review_input.get("bindings", {}).get("candidate_manifest"), "candidate manifest")
    try:
        report = verify_mechanical_draft(candidate_manifest.parent)
        run = json.loads((Path(run_root).resolve() / "run.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
        raise PendingSourceChoiceError(f"mechanical candidate verification failed: {error}") from error
    source = report.get("authorities", {}).get("source")
    if not isinstance(source, Mapping) or source.get("sha256") != run.get("source", {}).get("sha256"):
        raise PendingSourceChoiceError("mechanical candidate source does not match selected run")
    pages = {row.get("source_page"): row for row in report.get("pages", []) if isinstance(row, Mapping)}
    owners = set() if coverage_owner_keys is None else set(coverage_owner_keys)
    if any(type(page) is not int or not isinstance(view, str) or type(raw) is not int
           for page, view, raw in owners):
        raise PendingSourceChoiceError("coverage owner keys are malformed")
    result: set[tuple[int, str, int]] = set()
    for issue in pending:
        page = issue.get("source_page")
        selector = issue.get("source_selector", {}).get("mechanical_diagnostic", {})
        code, keys = selector.get("code"), selector.get("source_keys")
        if type(page) is not int or not isinstance(code, str) or not isinstance(keys, list) or not keys:
            raise PendingSourceChoiceError("pending source selector is malformed")
        normalized = {(page, row.get("view"), row.get("raw_index")) for row in keys if isinstance(row, Mapping)}
        if len(normalized) != len(keys) or any(not isinstance(view, str) or type(raw) is not int for _, view, raw in normalized):
            raise PendingSourceChoiceError("pending source keys are malformed")
        if issue.get("source_pdf_sha256") != source.get("sha256"):
            raise PendingSourceChoiceError("pending source issue has a foreign PDF")
        row = pages.get(page)
        if row is None or not isinstance(row.get("packet"), Mapping):
            raise PendingSourceChoiceError("pending source issue page is absent")
        packet = Path(run_root).resolve() / "outputs/04-visual-merge-bundle/merge_packets/pages" / row["packet"].get("path", "")
        if not packet.is_file() or file_identity(packet) != {key: row["packet"].get(key) for key in ("bytes", "sha256")}:
            raise PendingSourceChoiceError("pending source packet identity drift")
        matches = [item for item in report.get("diagnostics", []) if isinstance(item, Mapping)
                   and item.get("page") == page and item.get("code") == code and item.get("source_keys") == keys]
        anchors = selected_keys | owners
        if len(matches) != 1 or not normalized.intersection(anchors):
            raise PendingSourceChoiceError("pending source diagnostic is not bound to a visible selected occurrence")
        result.update(normalized - anchors)
    return result
