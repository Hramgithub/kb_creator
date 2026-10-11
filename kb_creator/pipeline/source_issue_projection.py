"""Project sealed structural source issues onto verified Russian units.

The source issue remains an English/source authority.  This module only derives
the Russian placement that is needed for a reader-facing review comment.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .five_step_language import _source_intervals
from .identity import canonical_bytes, file_identity, sha256_bytes
from .manifests import sealed, validate_seal
from .reader_occurrence_projection import (
    ReaderOccurrenceError,
    SCHEMA as ISSUE_EN_BINDINGS_V2_SCHEMA,
    build_issue_en_bindings_v2,
    validate_issue_reader_occurrence,
)


SCHEMA = "kb_creator.source_issue_ru_projection.v1"
# These issue kinds are review provenance.  Lexical source-choice issues keep
# their separate language gate and are never converted into DOCX comments here.
REVIEW_KINDS = frozenset({"source_structure_role_pending", "semantic_source_uncertainty", "editorial_choice"})


class SourceIssueProjectionError(ValueError):
    pass


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise SourceIssueProjectionError(f"cannot read sealed source-issue authority: {path}") from error
    if not isinstance(value, dict):
        raise SourceIssueProjectionError("sealed source-issue authority must be an object")
    return value


def _identity(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), **file_identity(path)}


def _same_identity(path: Path, record: object, label: str) -> None:
    if not isinstance(record, dict) or record.get("bytes") != path.stat().st_size or record.get("sha256") != file_identity(path)["sha256"]:
        raise SourceIssueProjectionError(f"{label} identity mismatch")


def _issue_map(final_evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    source_issues = final_evidence.get("source_issues")
    rows = source_issues.get("issues") if isinstance(source_issues, dict) else None
    if not isinstance(rows, list):
        raise SourceIssueProjectionError("final evidence has no source issue collection")
    result: dict[str, dict[str, Any]] = {}
    for issue in rows:
        if not isinstance(issue, dict) or not isinstance(issue.get("issue_id"), str):
            raise SourceIssueProjectionError("final evidence has malformed source issue")
        if issue["issue_id"] in result:
            raise SourceIssueProjectionError("final evidence has duplicate source issue IDs")
        result[issue["issue_id"]] = issue
    return result


def _complete_split_group(rows: list[dict[str, Any]], hit: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return one ordinary unit or every sibling of a complete split parent."""
    if len(hit) == 1 and hit[0].get("parent_unit_id") is None:
        return hit
    parent = hit[0].get("parent_unit_id") if hit else None
    if not isinstance(parent, str) or not parent or any(row.get("parent_unit_id") != parent for row in hit):
        raise SourceIssueProjectionError("EN issue crosses unrelated translation units")
    group = [row for row in rows if row.get("parent_unit_id") == parent]
    if not group:
        raise SourceIssueProjectionError("EN issue must bind a complete split-parent group")
    expected = list(range(1, len(group) + 1))
    if [row.get("part_index") for row in group] != expected or any(row.get("part_count") != len(group) for row in group):
        raise SourceIssueProjectionError("split-parent group metadata is incomplete")
    return group


def derive_source_issue_projection(*, master_en: Path, master_ru: Path,
                                   ru_projection: Path, issue_en_bindings: Path,
                                   final_evidence: Path, language_task: Path) -> dict[str, Any]:
    """Derive sealed, unit-exact reader roles for open structural issues.

    All inputs are read again on each call.  Callers must not pass a convenient
    source excerpt or a preselected RU unit as authority.
    """
    master_en, master_ru, ru_projection = (Path(item).resolve() for item in (master_en, master_ru, ru_projection))
    issue_en_bindings, final_evidence, language_task = (Path(item).resolve() for item in (issue_en_bindings, final_evidence, language_task))
    for path, label in ((master_en, "MASTER_EN"), (master_ru, "MASTER_RU"), (ru_projection, "RU projection"),
                        (issue_en_bindings, "issue EN bindings"), (final_evidence, "final evidence"), (language_task, "language task")):
        if not path.is_file() or path.is_symlink():
            raise SourceIssueProjectionError(f"{label} must be a regular file")
    bindings = _read(issue_en_bindings)
    try:
        validate_seal(bindings, "bindings_sha256")
    except ValueError as error:
        raise SourceIssueProjectionError("issue EN bindings seal mismatch") from error
    bindings_schema = bindings.get("schema")
    if bindings_schema not in {"kb_creator.issue_en_bindings.v1", ISSUE_EN_BINDINGS_V2_SCHEMA}:
        raise SourceIssueProjectionError("unsupported issue EN bindings schema")
    _same_identity(master_en, bindings.get("master_en"), "issue EN MASTER_EN")
    _same_identity(final_evidence, bindings.get("final_evidence"), "issue EN final evidence")
    evidence = _read(final_evidence)
    issues = _issue_map(evidence)
    task = _read(language_task)
    try:
        validate_seal(task, "task_sha256")
    except ValueError as error:
        raise SourceIssueProjectionError("language task seal mismatch") from error
    task_master = task.get("master_en")
    if not isinstance(task_master, dict) or task_master.get("sha256") != file_identity(master_en)["sha256"]:
        raise SourceIssueProjectionError("language task MASTER_EN identity mismatch")
    rows = task.get("units")
    if not isinstance(rows, list) or not rows:
        raise SourceIssueProjectionError("language task units are missing")
    try:
        intervals = _source_intervals(master_en, rows)
    except ValueError as error:
        raise SourceIssueProjectionError(f"language task cannot prove EN intervals: {error}") from error
    ru = _read(ru_projection)
    try:
        validate_seal(ru, "projection_sha256")
    except ValueError as error:
        raise SourceIssueProjectionError("RU projection seal mismatch") from error
    _same_identity(master_ru, ru.get("master_ru"), "RU projection MASTER_RU")
    ru_rows = {row.get("unit_id"): row for row in ru.get("units", []) if isinstance(row, dict)}
    if len(ru_rows) != len(ru.get("units", [])):
        raise SourceIssueProjectionError("RU projection unit IDs are duplicated or malformed")
    source_text = master_en.read_text(encoding="utf-8")
    roles: list[dict[str, Any]] = []
    seen: set[str] = set()
    raw_bindings = bindings.get("bindings")
    if not isinstance(raw_bindings, list):
        raise SourceIssueProjectionError("issue EN binding list is missing")
    if bindings_schema == ISSUE_EN_BINDINGS_V2_SCHEMA:
        # A v2 seal proves transport only.  Rebuild from the sealed final
        # evidence, Stage05 audit and copied page decisions before using a span
        # to place a Russian reader comment.
        try:
            expected = build_issue_en_bindings_v2(
                master_en, list(issues.values()),
                sorted({issue["source_page"] for issue in issues.values()
                        if type(issue.get("source_page")) is int}),
                final_evidence,
            )
        except ReaderOccurrenceError as error:
            raise SourceIssueProjectionError(f"v2 issue EN authority cannot be rederived: {error}") from error
        if bindings != expected:
            raise SourceIssueProjectionError("v2 issue EN bindings are not freshly derived")
    for binding in raw_bindings:
        if not isinstance(binding, dict):
            raise SourceIssueProjectionError("issue EN binding is malformed")
        issue_id = binding.get("issue_id")
        issue = issues.get(issue_id) if isinstance(issue_id, str) else None
        if issue is None or issue.get("kind") not in REVIEW_KINDS or issue.get("state") != "open":
            continue
        if issue_id in seen:
            raise SourceIssueProjectionError("structural issue has duplicate EN bindings")
        seen.add(issue_id)
        if (binding.get("source_page") != issue.get("source_page") or binding.get("source_selector") != issue.get("source_selector")):
            raise SourceIssueProjectionError("issue EN binding does not match sealed structural issue")
        excerpt = issue.get("source_excerpt_en")
        reason = issue.get("reason")
        if not isinstance(excerpt, str) or not isinstance(reason, str) or not reason.strip() or sha256_bytes(excerpt.encode("utf-8")) != issue.get("source_excerpt_sha256"):
            raise SourceIssueProjectionError("immutable source excerpt is invalid")
        if bindings_schema == ISSUE_EN_BINDINGS_V2_SCHEMA:
            try:
                validate_issue_reader_occurrence(binding, source_text)
            except ReaderOccurrenceError as error:
                raise SourceIssueProjectionError(f"v2 issue EN reader span is invalid: {error}") from error
            source = binding.get("source_occurrence")
            projection = binding.get("reader_projection")
            span = binding.get("master_reader_span")
            if (not isinstance(source, dict) or not isinstance(projection, dict) or not isinstance(span, dict)
                    or source.get("source_excerpt_en", source.get("source_excerpt")) != excerpt
                    or source.get("source_excerpt_sha256") != issue.get("source_excerpt_sha256")
                    or source.get("source_locator") != issue.get("source_selector")):
                raise SourceIssueProjectionError("v2 immutable source occurrence disagrees with final evidence")
            start, end = span.get("character_start"), span.get("character_end")
            reader_excerpt = projection.get("reader_text")
            if not isinstance(reader_excerpt, str) or source_text[start:end] != reader_excerpt:
                raise SourceIssueProjectionError("v2 reader excerpt identity is invalid")
        else:
            start, end = binding.get("character_start"), binding.get("character_end")
            if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(source_text):
                raise SourceIssueProjectionError("issue EN character span is invalid")
            if (binding.get("text_sha256") != sha256_bytes(source_text[start:end].encode("utf-8"))):
                raise SourceIssueProjectionError("issue EN span or immutable source excerpt is invalid")
            if binding.get("byte_start") != len(source_text[:start].encode("utf-8")) or binding.get("byte_end") != len(source_text[:end].encode("utf-8")):
                raise SourceIssueProjectionError("issue EN byte span is invalid")
            reader_excerpt = excerpt
        hit = [row for left, right, row in intervals if left < end and right > start]
        if not hit or hit != rows[rows.index(hit[0]):rows.index(hit[-1]) + 1]:
            raise SourceIssueProjectionError("issue EN span has noncontiguous translation mapping")
        group = _complete_split_group(rows, hit)
        unit_bindings = []
        for row in group:
            unit = ru_rows.get(row.get("unit_id"))
            if not isinstance(unit, dict) or unit.get("source_hash") != row.get("source_hash") or not isinstance(unit.get("ru_sha256"), str):
                raise SourceIssueProjectionError("RU projection unit does not bind language task")
            unit_bindings.append({"unit_id": unit["unit_id"], "ru_sha256": unit["ru_sha256"]})
        selector = issue.get("source_selector", {}).get("comparison_structural_role_v1", {})
        purpose = selector.get("provisional_selection_purpose") if isinstance(selector, dict) else None
        if not isinstance(purpose, str) or not purpose:
            purpose = "текущее читательское представление"
        role = {"role": "source_issue_review_anchor", "issue_id": issue_id,
                "source_page": issue["source_page"], "en_excerpt": reader_excerpt,
                "source_evidence": "sealed EN issue binding and verified RU projection",
                "reason": f"Проверить смысл: {reason}; предварительное представление сохранено как {purpose}.",
                "placement": "first_visible_text_block_v1"}
        if bindings_schema == ISSUE_EN_BINDINGS_V2_SCHEMA:
            # Persisted in the package projection for provenance; the reader
            # anchor itself continues to use the rendered EN text.
            role["raw_source_excerpt_en"] = excerpt
        if len(unit_bindings) == 1:
            role["unit"] = unit_bindings[0]
        else:
            role["units"] = unit_bindings
        roles.append(role)
    expected = {issue_id for issue_id, issue in issues.items() if issue.get("kind") in REVIEW_KINDS and issue.get("state") == "open"}
    if seen != expected:
        raise SourceIssueProjectionError("open review source issues and EN bindings are not bijective")
    return sealed(SCHEMA, {"master_en": _identity(master_en), "master_ru": _identity(master_ru),
                           "ru_projection": _identity(ru_projection), "issue_en_bindings": _identity(issue_en_bindings),
                           "final_evidence": _identity(final_evidence), "language_task": _identity(language_task),
                           "roles": roles}, digest_key="projection_sha256")


def validate_source_issue_projection(value: object, *, master_ru: Path, ru_projection: Path) -> dict[str, Any]:
    """Reopen authority files and rederive roles before a DOCX build/verify."""
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        raise SourceIssueProjectionError("unsupported source issue RU projection")
    try:
        validate_seal(value, "projection_sha256")
    except ValueError as error:
        raise SourceIssueProjectionError("source issue RU projection seal mismatch") from error
    _same_identity(master_ru, value.get("master_ru"), "source issue projection MASTER_RU")
    _same_identity(ru_projection, value.get("ru_projection"), "source issue projection RU projection")
    def reopen(field: str) -> Path:
        record = value.get(field)
        if not isinstance(record, dict) or not isinstance(record.get("path"), str) or not record["path"]:
            raise SourceIssueProjectionError(f"source issue projection {field} reference is missing")
        path = Path(record["path"]).resolve()
        if not path.is_file() or path.is_symlink():
            raise SourceIssueProjectionError(f"source issue projection {field} authority is missing")
        _same_identity(path, record, f"source issue projection {field}")
        return path
    derived = derive_source_issue_projection(
        master_en=reopen("master_en"), master_ru=master_ru, ru_projection=ru_projection,
        issue_en_bindings=reopen("issue_en_bindings"), final_evidence=reopen("final_evidence"),
        language_task=reopen("language_task"),
    )
    if value.get("roles") != derived["roles"]:
        raise SourceIssueProjectionError("source issue projection roles are not freshly derived")
    return value
