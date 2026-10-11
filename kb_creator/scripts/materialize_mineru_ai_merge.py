"""Materialize reviewed MinerU page decisions without making merge decisions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path, PureWindowsPath
from typing import Any
from kb_creator.pipeline.source_page_render import render_source_pdf_page, validate_source_page_render_row


DECISION_SCHEMA = "kb_creator.mineru_ai_page_decision.v1"
DECISION_KEYS = frozenset(
    {
        "schema",
        "source_page",
        "semantic_role",
        "overlay_preference",
        "selected_blocks",
        "markdown",
        "assets",
        "unresolved",
        "review",
    }
)
BLOCK_BOUNDARY_KEYS = frozenset({"style", "heading_line", "first_body_line"})
PURPOSES = {"text", "structure", "asset", "visual"}
PLACEMENTS = {"inline", "full_width", "full_page", "handout", "map", "reference_only"}
VISUAL_ONLY = {"full_page", "handout", "map", "reference_only"}
SOURCE_PAGE_MARKER = re.compile(r"<!--\s*source-page-", re.IGNORECASE)
HTML_TAG = re.compile(r"<\s*/?\s*[A-Za-z][A-Za-z0-9:-]*(?:\s+[^<>]*)?\s*/?\s*>")
WINDOWS_ABSOLUTE = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/]+")
UNC_ABSOLUTE = re.compile(r"(?<!\S)\\\\[^\s]+")
# A lone slash-prefixed token can be source-visible punctuation in a map label
# (for example ``Guest Bedroom /Study``). A second separator makes a POSIX
# filesystem path unambiguous while still covering Markdown image/link targets.
POSIX_ABSOLUTE = re.compile(r"(?:^|[\s\[\(\]])/(?![\s/])\S*/\S+")
# A Markdown destination is an explicit path-bearing syntax, so even a
# single-component absolute destination cannot be treated as a map label.
MARKDOWN_ABSOLUTE_DESTINATION = re.compile(
    r"(?:!?\[[^\]\r\n]*\]\(\s*<?|^[ \t]{0,3}\[[^\]\r\n]+\]:\s*<?)/(?![\s/])[^)\s>]+",
    re.MULTILINE,
)
ASSET_PLACEHOLDER = re.compile(r"\{\{asset:([^{}]+)\}\}")
IMAGE_PLACEHOLDER = re.compile(r"!\[([^\]\r\n]*)\]\(\{\{asset:([^{}]+)\}\}\)")
V2_BUNDLE_SCHEMA = "kb_creator.mineru_visual_merge_bundle.v2"
V1_BUNDLE_SCHEMA = "kb_creator.mineru_visual_merge_bundle.v1"
V2_RUN_SCHEMA = "kb_creator.run_spec.v2"
V2_AUDIT_SCHEMA = "kb_creator.ai-merge-fidelity-audit/v2"
V3_BUNDLE_SCHEMA = "kb_creator.mineru_visual_merge_bundle.v3"
V3_AUDIT_SCHEMA = "kb_creator.ai-merge-fidelity-audit/v3"
V4_AUDIT_SCHEMA = "kb_creator.ai-merge-fidelity-audit/v4"
V2_COMPARISON_RELATIVE = "outputs/03-compare-views/comparison.json"
FILE_ATTRIBUTE_REPARSE_POINT = 0x400


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_hash(value: dict[str, Any], key: str) -> str:
    unsigned = {name: item for name, item in value.items() if name != key}
    encoded = json.dumps(
        unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _is_reparse(path: Path) -> bool:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise ValueError(f"cannot inspect path without following links: {path}") from exc
    attributes = getattr(info, "st_file_attributes", None)
    if os.name == "nt" and attributes is None:
        raise ValueError("Windows reparse-point inspection is unavailable")
    return stat.S_ISLNK(info.st_mode) or bool(
        attributes is not None and attributes & FILE_ATTRIBUTE_REPARSE_POINT
    )


def _assert_components_not_reparse(path: Path) -> None:
    absolute = path.absolute()
    existing: list[Path] = []
    cursor = absolute
    while True:
        if cursor.exists() or cursor.is_symlink():
            existing.append(cursor)
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    for component in reversed(existing):
        if _is_reparse(component):
            raise ValueError(f"path crosses a reparse point: {component}")


def _assert_tree_not_reparse(root: Path) -> None:
    """Reject symlinks, junctions and mount-point reparses before traversal."""
    _assert_components_not_reparse(root)
    if not root.is_dir():
        raise ValueError(f"required directory is missing: {root}")
    pending = [root.absolute()]
    while pending:
        current = pending.pop()
        try:
            entries = list(os.scandir(current))
        except OSError as exc:
            raise ValueError(f"cannot enumerate authority tree: {current}") from exc
        for entry in entries:
            child = Path(entry.path)
            if _is_reparse(child):
                raise ValueError(f"authority tree contains a reparse point: {child}")
            if entry.is_dir(follow_symlinks=False):
                pending.append(child)


def _checked_file(path: Path, *, root: Path | None = None) -> Path:
    _assert_components_not_reparse(path)
    if not path.is_file():
        raise ValueError(f"required regular file is missing: {path}")
    resolved = path.resolve(strict=True)
    if root is not None:
        root_resolved = root.resolve(strict=True)
        try:
            resolved.relative_to(root_resolved)
        except ValueError as exc:
            raise ValueError(f"path escapes its authority root: {path}") from exc
    return resolved


def _identity(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def _require_identity(record: Any, path: Path, label: str) -> None:
    if not isinstance(record, dict) or set(record) != {"bytes", "sha256"}:
        raise ValueError(f"{label} identity shape mismatch")
    if record != _identity(path):
        raise ValueError(f"{label} identity mismatch")


def _safe_basename(value: Any) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or value in {".", ".."}:
        raise ValueError("logical_name must be a safe nonempty basename")
    path = PureWindowsPath(value)
    if path.name != value or path.drive or any(part == ".." for part in path.parts):
        raise ValueError("logical_name must be a safe basename")
    return value


def _safe_relative(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("asset source_path must be a nonempty relative path")
    path = PureWindowsPath(value)
    if value.startswith(("/", "\\")) or path.is_absolute() or path.drive or ".." in path.parts:
        raise ValueError("asset source_path escapes its raw view directory")
    return path.as_posix()


def _closed(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label} has unknown or missing keys")
    return value


def _asset_placeholders(markdown: str) -> list[str]:
    placeholders = ASSET_PLACEHOLDER.findall(markdown)
    residue = ASSET_PLACEHOLDER.sub("", markdown)
    if "{{" in residue or "}}" in residue:
        raise ValueError("markdown contains a malformed or unsupported template")
    return placeholders


def _image_placeholder_names(markdown: str) -> set[str]:
    valid_spans: set[tuple[int, int]] = set()
    names: set[str] = set()
    for match in IMAGE_PLACEHOLDER.finditer(markdown):
        if not match.group(1).strip():
            raise ValueError("asset image alt text must be nonempty")
        valid_spans.add(match.span(2))
        names.add(match.group(2))
    for placeholder in ASSET_PLACEHOLDER.finditer(markdown):
        if placeholder.span(1) not in valid_spans:
            raise ValueError("every asset placeholder must be an exact Markdown image target")
    return names


def _validate_markdown(markdown: str) -> None:
    if SOURCE_PAGE_MARKER.search(markdown):
        raise ValueError("markdown contains a generated source-page marker")
    if MARKDOWN_ABSOLUTE_DESTINATION.search(markdown):
        raise ValueError("markdown contains a POSIX absolute path")
    if HTML_TAG.search(markdown):
        raise ValueError("markdown contains an HTML tag")
    if WINDOWS_ABSOLUTE.search(markdown):
        raise ValueError("markdown contains a device-specific Windows absolute path")
    if UNC_ABSOLUTE.search(markdown):
        raise ValueError("markdown contains a UNC absolute path")
    if POSIX_ABSOLUTE.search(markdown):
        raise ValueError("markdown contains a POSIX absolute path")


def _substitute_assets(markdown: str, stored_paths: dict[str, str], prefix: str) -> str:
    def replace(match: re.Match[str]) -> str:
        logical_name = match.group(1)
        try:
            return prefix + stored_paths[logical_name]
        except KeyError as exc:  # validation should make this unreachable
            raise ValueError("asset placeholder is not a selected decision asset") from exc
    return ASSET_PLACEHOLDER.sub(replace, markdown)


def _v2_authority(
    bundle_root: Path,
    raw_root: Path,
    comparison_path: Path,
    comparison_sha256: str,
) -> tuple[Path, dict[str, Any]]:
    if not re.fullmatch(r"[0-9A-Fa-f]{64}", comparison_sha256):
        raise ValueError("comparison SHA-256 must be exactly 64 hexadecimal characters")
    run_root = bundle_root.parent.parent
    expected_bundle = run_root / "outputs" / "04-visual-merge-bundle"
    expected_raw = run_root / "outputs" / "02-mineru-three-view"
    expected_comparison = run_root / Path(V2_COMPARISON_RELATIVE)
    for candidate, expected, label in (
        (bundle_root, expected_bundle, "bundle root"),
        (raw_root, expected_raw, "raw root"),
        (comparison_path, expected_comparison, "comparison path"),
    ):
        if candidate.absolute() != expected.absolute():
            raise ValueError(f"v2 {label} is not the fixed run-local path")
    _assert_tree_not_reparse(run_root / "outputs" / "02-mineru-three-view")
    _assert_tree_not_reparse(run_root / "outputs" / "03-compare-views")
    _assert_tree_not_reparse(run_root / "outputs" / "04-visual-merge-bundle")
    resolved_comparison = _checked_file(expected_comparison, root=run_root)
    if sha256_file(resolved_comparison) != comparison_sha256.upper():
        raise ValueError("explicit comparison SHA-256 mismatch")

    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from kb_creator.pipeline.reconstruction import (  # local import keeps v1 standalone
        RUN_STAGES,
        _validate_live_run_bindings,
        _validate_stage_prefix,
        load_run,
        validate_queue,
    )

    run = load_run(run_root)
    if run.get("schema") != V2_RUN_SCHEMA:
        raise ValueError("v2 visual bundle requires a v2 run")
    _validate_live_run_bindings(run_root, run)
    _validate_stage_prefix(run_root, run, RUN_STAGES)
    queue_path = _checked_file(run_root / "review" / "review_queue.json", root=run_root)
    queue = validate_queue(queue_path, run)
    queue_comparison = queue.get("comparison")
    expected_record = {"path": V2_COMPARISON_RELATIVE, **_identity(resolved_comparison)}
    if queue_comparison != expected_record:
        raise ValueError("review queue comparison authority mismatch")
    if queue_comparison["sha256"] != comparison_sha256.upper():
        raise ValueError("explicit comparison is not the sealed queue authority")

    visual_path = _checked_file(
        bundle_root / "visual" / "visual_manifest.json", root=bundle_root
    )
    visual = _json(visual_path)
    if visual.get("schema") != V2_BUNDLE_SCHEMA:
        raise ValueError("expected v2 visual bundle")
    inputs = visual.get("inputs")
    view_set_path = _checked_file(expected_raw / "view-set.json", root=expected_raw)
    if not isinstance(inputs, dict) or inputs.get("comparison") != {
        "path": str(resolved_comparison),
        "sha256": comparison_sha256.upper(),
    } or inputs.get("raw_root") != str(expected_raw.resolve(strict=True)) or inputs.get(
        "raw_receipt"
    ) != {
        "path": str(view_set_path),
        "sha256": sha256_file(view_set_path),
    }:
        raise ValueError("visual bundle input graph does not bind the queue authority")
    geometry_path = _checked_file(
        bundle_root / "visual" / "geometry_plan.json", root=bundle_root
    )
    geometry = _json(geometry_path)
    view_set = _json(view_set_path)
    if geometry.get("run_identity_sha256") != run["portable_identity_sha256"]:
        raise ValueError("geometry plan run identity mismatch")
    if geometry.get("comparison") != {
        "path_hint": V2_COMPARISON_RELATIVE,
        **_identity(resolved_comparison),
    }:
        raise ValueError("geometry plan comparison authority mismatch")
    if geometry.get("view_set") != {
        "path_hint": "outputs/02-mineru-three-view/view-set.json",
        **_identity(view_set_path),
        "receipt_sha256": view_set.get("receipt_sha256"),
    }:
        raise ValueError("geometry plan view-set authority mismatch")
    return resolved_comparison, queue


def _v2_fidelity_authority(
    audit_path: Path,
    audit_sha256: str,
    bundle_root: Path,
    queue: dict[str, Any],
    comparison_path: Path,
) -> tuple[Path, dict[str, Any]]:
    if not re.fullmatch(r"[0-9A-Fa-f]{64}", audit_sha256 or ""):
        raise ValueError("fidelity audit SHA-256 must be exactly 64 hexadecimal characters")
    run_root = bundle_root.parent.parent
    expected = run_root / "outputs" / "05-fidelity-audit" / "audit.json"
    if audit_path.absolute() != expected.absolute():
        raise ValueError("v2 fidelity audit is not the fixed Stage05 path")
    resolved = _checked_file(audit_path, root=run_root)
    if sha256_file(resolved) != audit_sha256.upper():
        raise ValueError("explicit fidelity audit SHA-256 mismatch")
    report = _json(resolved)
    if not isinstance(report, dict) or set(report) != {"schema", "authorities", "policy", "pages", "boundaries", "errors", "passed"} or report.get("schema") != V2_AUDIT_SCHEMA or report.get("passed") is not True or report.get("errors") != []:
        raise ValueError("v2 materialization requires a passing v2 fidelity audit")
    expected_policy = {"source_completeness_threshold": 1.0, "selected_recall_threshold": 0.95, "required_views": ["original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr"], "normalization": "unicode_nfkc_casefold_alphanumeric_stream_v1", "low_text_exemption": False}
    if report.get("policy") != expected_policy or not isinstance(report.get("boundaries"), list):
        raise ValueError("v2 fidelity audit policy or boundary shape mismatch")
    authorities = report.get("authorities")
    if not isinstance(authorities, dict) or set(authorities) != {"run", "review_queue", "comparison", "decision_set", "reviewed_allowlist", "packets"}:
        raise ValueError("v2 fidelity audit lacks closed authorities")
    if authorities.get("review_queue") != {
        "path_hint": "review/review_queue.json",
        **_identity(run_root / "review" / "review_queue.json"),
        "queue_sha256": queue["queue_sha256"],
    } or authorities.get("comparison") != {
        "path_hint": V2_COMPARISON_RELATIVE,
        **_identity(comparison_path),
    }:
        raise ValueError("v2 fidelity audit authority mismatch")
    decision_set_path = run_root / "review" / "validated-submission-v1" / "decision_set.json"
    if authorities.get("decision_set") != {"path_hint": "validated-submission/decision_set.json", **_identity(_checked_file(decision_set_path, root=run_root))}:
        raise ValueError("v2 fidelity audit decision authority mismatch")
    packet_authorities = authorities.get("packets")
    queue_items = queue.get("items")
    expected_packets = []
    for item in queue_items if isinstance(queue_items, list) else []:
        page = item.get("source_page")
        packet = bundle_root / "merge_packets" / "pages" / f"page-{page:03d}.json"
        expected_packets.append({"source_page": page, "path_hint": f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json", **_identity(_checked_file(packet, root=bundle_root))})
    if packet_authorities != expected_packets:
        raise ValueError("v2 fidelity audit packet authority mismatch")
    allowlist_authority = authorities.get("reviewed_allowlist")
    allowlist_path = decision_set_path.parent / "reviewed_allowlist.json"
    if allowlist_authority is None:
        if allowlist_path.exists(): raise ValueError("v2 fidelity audit omits existing allowlist authority")
    elif not isinstance(allowlist_authority, dict) or allowlist_authority != {"path_hint": "reviewed_allowlist.json", **_identity(_checked_file(allowlist_path, root=run_root)), "schema": "kb_creator.ai_merge_fidelity_reviewed_allowlist.v2"}:
        raise ValueError("v2 fidelity audit allowlist authority mismatch")
    pages = report.get("pages")
    page_keys = {"source_page", "required_character_count", "covered_character_count", "completeness", "selected_recall", "selected_precision", "ordered_span_mappings", "units", "substitutions", "visual_assertions", "unaccounted_unit_count", "errors", "passed"}
    expected_domain = [item["source_page"] for item in queue_items]
    if not isinstance(pages, list) or [row.get("source_page") for row in pages if isinstance(row, dict)] != expected_domain or any(set(row) != page_keys or row.get("passed") is not True or row.get("completeness") != 1.0 or row.get("unaccounted_unit_count") != 0 or row.get("errors") != [] for row in pages):
        raise ValueError("v2 fidelity audit page closure mismatch")
    return resolved, report


def _replay_authority(
    bundle_root: Path,
    raw_root: Path,
    visual_manifest_path: Path,
    *,
    comparison: Path | None,
    comparison_sha256: str | None,
    fidelity_audit: Path | None,
    fidelity_audit_sha256: str | None,
    replay_run_root: Path,
    replay_bridge_sha256: str | None,
    replay_submission: Path | None,
    replay_submission_sha256: str | None,
) -> tuple[Path, dict[str, Any], Path, dict[str, Any]]:
    values = (replay_bridge_sha256, replay_submission, replay_submission_sha256, fidelity_audit, fidelity_audit_sha256)
    if any(value is None for value in values):
        raise ValueError("replay materialization requires complete run/bridge/submission/audit authority")
    if comparison is not None or comparison_sha256 is not None:
        raise ValueError("replay comparison is fixed by the bridge")
    if bundle_root.absolute() != (replay_run_root / "outputs/04-visual-merge-bundle").absolute() or raw_root.absolute() != (replay_run_root / "outputs/02-mineru-three-view").absolute():
        raise ValueError("replay run root is not the bundle/raw authority")
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from kb_creator.pipeline.reconstruction_replay import (
        validate_replay_authorities,
        validate_replayed_prefix,
    )
    has_completion = (replay_run_root / "replay/completion.json").is_file()
    authorities = (
        validate_replay_authorities(replay_run_root)
        if has_completion
        else validate_replayed_prefix(replay_run_root)
    )
    if authorities.visual_manifest is None or authorities.comparison is None or authorities.visual_manifest.absolute() != visual_manifest_path.absolute():
        raise ValueError("replay visual authority mismatch")
    visual_schema = _json(visual_manifest_path).get("schema")
    if visual_schema == V2_BUNDLE_SCHEMA and not has_completion:
        raise ValueError("native v2 visual bundle requires hybrid completion authority")
    if visual_schema == V3_BUNDLE_SCHEMA and has_completion:
        raise ValueError("replay v3 visual bundle cannot have hybrid completion authority")
    if visual_schema not in {V2_BUNDLE_SCHEMA, V3_BUNDLE_SCHEMA}:
        raise ValueError("replay visual bundle schema mismatch")
    if authorities.bridge_sha256 != replay_bridge_sha256:
        raise ValueError("replay bridge authority mismatch")
    queue_path = _checked_file(replay_run_root / "review/review_queue.json", root=replay_run_root)
    queue = _json(queue_path)
    expected_submission = replay_run_root / "review/validated-submission-v2/submission_inventory.json"
    if replay_submission.absolute() != expected_submission.absolute() or sha256_file(_checked_file(replay_submission, root=replay_run_root)) != replay_submission_sha256.upper():
        raise ValueError("replay submission authority mismatch")
    expected_audit = replay_run_root / "outputs/05-fidelity-audit/audit.json"
    if fidelity_audit.absolute() != expected_audit.absolute() or sha256_file(_checked_file(fidelity_audit, root=replay_run_root)) != fidelity_audit_sha256.upper():
        raise ValueError("replay audit authority mismatch")
    report = _json(fidelity_audit)
    if report.get("schema") not in {V3_AUDIT_SCHEMA, V4_AUDIT_SCHEMA} or report.get("passed") is not True or report.get("errors") != []:
        raise ValueError("replay materialization requires a passing v3 or v4 audit")
    report_authority = report.get("authorities", {})
    if report_authority.get("bridge_sha256") != replay_bridge_sha256 or report_authority.get("submission_sha256") != _json(replay_submission).get("submission_sha256"):
        raise ValueError("replay audit authority graph mismatch")
    return authorities.comparison, queue, fidelity_audit, report


def _load_bundle(
    bundle_root: Path,
    raw_root: Path,
    comparison_path: Path,
) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]], dict[str, Any]]:
    index_path = _checked_file(
        bundle_root / "merge_packets" / "merge_index.json", root=bundle_root
    )
    index = _json(index_path)
    ordered = index.get("by_source_page") if isinstance(index, dict) else None
    if not isinstance(ordered, list) or not ordered:
        raise ValueError("bundle merge index lacks by_source_page")
    pages: dict[int, dict[str, Any]] = {}
    for row in ordered:
        _closed(row, {"source_page", "semantic_role", "priority_score", "packet"}, "merge index row")
        page = row["source_page"]
        if type(page) is not int or page in pages:
            raise ValueError("merge index page domain is invalid")
        packet_rel = _safe_relative(row["packet"])
        packet_path = _checked_file(
            bundle_root / "merge_packets" / packet_rel,
            root=bundle_root / "merge_packets",
        )
        packet = _json(packet_path)
        if packet.get("source_page") != page or packet.get("semantic_role") != row["semantic_role"]:
            raise ValueError("merge index and packet disagree")
        pages[page] = {"row": row, "packet": packet, "path": packet_path}
    expected = list(range(min(pages), max(pages) + 1))
    if sorted(pages) != expected:
        raise ValueError("merge index pages must be contiguous")
    comparison = _json(_checked_file(comparison_path))
    return ordered, pages, comparison


def _load_decisions(decisions_root: Path, page_domain: list[int]) -> dict[int, tuple[Path, bytes, dict[str, Any]]]:
    _assert_tree_not_reparse(decisions_root)
    files = sorted(decisions_root.glob("page-*.json"))
    expected = {f"page-{page:03d}.json" for page in page_domain}
    if {path.name for path in files} != expected or len(files) != len(expected):
        raise ValueError("decision files do not exactly cover the bundle page domain")
    result = {}
    for path in files:
        path = _checked_file(path, root=decisions_root)
        page = int(path.stem.split("-")[1])
        raw = path.read_bytes()
        result[page] = (path, raw, json.loads(raw.decode("utf-8")))
    return result


def _is_title(block: dict[str, Any]) -> bool:
    evidence = block.get("semantic_evidence")
    if not isinstance(evidence, dict):
        return False
    # Evidence also carries non-title signals such as `v2_table_text`.
    # Only the closed title signal set may activate the heading guard.
    return any(bool(evidence.get(key)) for key in (
        "text_level", "v2_title", "middle_title", "markdown_heading", "model_title",
    ))


def _explicit_title_override(notes: str, title: str, visual_reviewed: bool) -> bool:
    return visual_reviewed and re.search(
        rf"(?im)^\s*title override:\s*{re.escape(title)}\s*;\s*reason:\s*\S.+$", notes
    ) is not None


def _exact_nested_heading(markdown: str, title: str, semantic_structure: Any, key: tuple[str, int]) -> bool:
    """Prove an exact ATX heading inside one reviewed semantic container."""
    if not isinstance(semantic_structure, dict) or not isinstance(semantic_structure.get("units"), list):
        return False
    units = semantic_structure["units"]
    headings = [
        unit for unit in units
        if isinstance(unit, dict)
        and unit.get("kind") == "heading"
        and unit.get("representation") == "atx_heading"
        and isinstance(unit.get("container_parent"), str)
        and any(
            isinstance(source, dict)
            and (source.get("view"), source.get("raw_index")) == key
            for source in unit.get("source_blocks", [])
        )
    ]
    if len(headings) != 1:
        return False
    parents = [unit for unit in units if isinstance(unit, dict) and unit.get("id") == headings[0]["container_parent"]]
    if len(parents) != 1 or parents[0].get("representation") not in {"blockquote", "semantic_span"}:
        return False
    parent_representation = parents[0]["representation"]
    span = headings[0].get("markdown_span")
    if not isinstance(span, dict) or type(span.get("start_line")) is not int or span.get("start_line") != span.get("end_line"):
        return False
    lines = markdown.split("\n")
    line_number = span["start_line"]
    if not 1 <= line_number <= len(lines):
        return False
    prefix = r">\s+" if parent_representation == "blockquote" else ""
    return re.fullmatch(rf"{prefix}#{{1,6}}\s+{re.escape(title)}\s*#*\s*", lines[line_number - 1]) is not None


def _validated_v2_title_role(
    decision: dict[str, Any], packet: dict[str, Any], title: str,
    key: tuple[str, int], split_structure_proof_keys: set[tuple[int, str, int]] | None,
    visual_assertions: dict[str, dict[str, Any]] | None = None,
) -> bool:
    """Recognize only the five sealed V2 title roles after local Stage05 validation."""
    structure = decision.get("semantic_structure")
    if not isinstance(structure, dict) or (
        structure.get("schema"), structure.get("profile")
    ) != ("kb_creator.page_semantic_structure.v2", "reviewed_role_outline_and_partitions_v2"):
        return False
    units = structure.get("units")
    if not isinstance(units, list):
        return False
    # Do not let a caller assert that V2 proof happened.  Re-run the shared
    # fragment/span/correction validator over this exact decision and packet.
    # The outer replay path additionally verifies these visual identities
    # against its sealed inventory before materialization.
    visual = structure.get("review", {}).get("visual") if isinstance(structure.get("review"), dict) else None
    if not isinstance(visual, dict) or not isinstance(visual.get("path"), str):
        return False
    try:
        from kb_creator.pipeline.semantic_structure import SemanticStructureError, validate_semantic_structure
        validate_semantic_structure(
            {decision["source_page"]: decision}, {decision["source_page"]: packet},
            {visual["path"]: {"bytes": visual.get("bytes"), "sha256": visual.get("sha256")}},
            required_pages=[decision["source_page"]], visual_assertions=visual_assertions,
        )
    except (KeyError, SemanticStructureError, ValueError, TypeError):
        return False
    lines = decision["markdown"].split("\n")
    blocks = {
        (view, block.get("raw_index")): block
        for view, view_data in packet.get("views", {}).items()
        if isinstance(view_data, dict)
        for block in view_data.get("blocks", [])
        if isinstance(block, dict)
    }
    source = blocks.get(key)
    raw_title = source.get("text") if isinstance(source, dict) else None
    if not isinstance(raw_title, str):
        return False
    if raw_title == "":
        # Empty OCR still has an exact source occurrence. The shared validator
        # above verifies its source-region assertion, reader heading and visual.
        restored = [unit for unit in units if isinstance(unit, dict)
                    and unit.get("kind") == "heading"
                    and unit.get("representation") == "atx_heading"
                    and unit.get("source_fragments") == []
                    and unit.get("visual_assertion_ids")
                    and unit.get("source_blocks") == [{"view": key[0], "raw_index": key[1]}]]
        return len(restored) == 1
    try:
        from kb_creator.pipeline.semantic_structure import _packet_blocks, _selected_keys, verified_reviewed_prose_role_keys
        role_keys, _ = verified_reviewed_prose_role_keys(
            decision, _packet_blocks(packet), _selected_keys(decision), decision["markdown"], decision["source_page"],
            semantic_units=units, visual_inventory={visual["path"]: {"bytes": visual.get("bytes"), "sha256": visual.get("sha256")}},
        )
        if key in role_keys:
            return True
    except (KeyError, SemanticStructureError, ValueError, TypeError):
        return False

    def bound(unit: Any, *, kind: str, representation: str, full_source: bool = True) -> bool:
        if not isinstance(unit, dict) or unit.get("kind") != kind or unit.get("representation") != representation:
            return False
        if not any(isinstance(row, dict) and (row.get("view"), row.get("raw_index")) == key for row in unit.get("source_blocks", [])):
            return False
        fragments = [row for row in unit.get("source_fragments", []) if isinstance(row, dict) and (row.get("view"), row.get("raw_index")) == key]
        return len(fragments) == 1 and (
            not full_source or (fragments[0].get("start"), fragments[0].get("end")) == (0, len(raw_title))
        )

    def span_lines(unit: dict[str, Any]) -> list[str] | None:
        span = unit.get("markdown_span", {})
        start, end = span.get("start_line"), span.get("end_line")
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            return None
        return lines[start - 1:end]

    headings = [unit for unit in units if bound(unit, kind="heading", representation="atx_heading")]
    if len(headings) == 1:
        from kb_creator.pipeline.heading_display import flatten_word_wrapped_heading
        covered = span_lines(headings[0])
        # Source fragments and reader span were validated above. This display
        # variant removes only whole-word OCR wraps; no lexical correction or
        # formula normalization is admitted by the heading consumer.
        display_titles = {title, flatten_word_wrapped_heading(title)}
        if covered and len(covered) == 1 and any(re.fullmatch(
            rf"#{{1,6}}\s+{re.escape(display)}\s*#*\s*", covered[0]
        ) is not None for display in display_titles):
            return True

    # One reviewed ATX heading may own a consecutive stack of complete OCR
    # title blocks.  Validate the entire ordered group here; accepting only the
    # currently replayed fragment would let a missing or reordered sibling pass.
    grouped_headings = [unit for unit in units if isinstance(unit, dict)
                        and unit.get("kind") == "heading"
                        and unit.get("representation") == "atx_heading"
                        and any(isinstance(row, dict) and (row.get("view"), row.get("raw_index")) == key
                                for row in unit.get("source_blocks", []))]
    if len(grouped_headings) == 1:
        group = grouped_headings[0]
        group_keys = [(row.get("view"), row.get("raw_index")) for row in group.get("source_blocks", [])
                      if isinstance(row, dict)]
        if (len(group_keys) > 1 and len(set(group_keys)) == len(group_keys)
                and all(isinstance(view, str) and type(index) is int for view, index in group_keys)
                and len({view for view, _index in group_keys}) == 1
                and [index for _view, index in group_keys] == sorted(index for _view, index in group_keys)):
            fragments: list[str] = []
            complete = True
            for group_key in group_keys:
                group_source = blocks.get(group_key)
                rows = [row for row in group.get("source_fragments", []) if isinstance(row, dict)
                        and (row.get("view"), row.get("raw_index")) == group_key]
                if (not isinstance(group_source, dict) or not isinstance(group_source.get("text"), str)
                        or len(rows) != 1
                        or (rows[0].get("start"), rows[0].get("end")) != (0, len(group_source["text"]))):
                    complete = False
                    break
                owners = [unit for unit in units if isinstance(unit, dict) and any(
                    isinstance(row, dict) and (row.get("view"), row.get("raw_index")) == group_key
                    for row in unit.get("source_blocks", [])
                )]
                if owners != [group]:
                    complete = False
                    break
                fragments.append(group_source["text"])
            covered = span_lines(group)
            if complete and covered and len(covered) == 1:
                from kb_creator.pipeline.heading_display import flatten_word_wrapped_heading
                grouped_title = " ".join(fragment.strip() for fragment in fragments).strip()
                display_titles = {grouped_title, flatten_word_wrapped_heading(grouped_title)}
                if any(re.fullmatch(rf"#{{1,6}}\s+{re.escape(display)}\s*#*\s*", covered[0]) is not None
                       for display in display_titles):
                    return True
    labels = [unit for unit in units if bound(unit, kind="label", representation="semantic_span")]
    if len(labels) == 1 and span_lines(labels[0]) == [title]:
        return True

    # A title-marked source block can legitimately be a stack of reviewed
    # cover labels.  The shared V2 validator has already checked each source
    # fragment's hashes and the complete partition; retain an additional
    # ordered reader projection here so a title guard never accepts a gap,
    # overlap, duplicate, or reordered label sequence.
    partition_labels = [unit for unit in units if bound(
        unit, kind="label", representation="semantic_span", full_source=False,
    )]
    source_units = [unit for unit in units if isinstance(unit, dict) and any(
        isinstance(row, dict) and (row.get("view"), row.get("raw_index")) == key
        for row in unit.get("source_blocks", [])
    )]
    if partition_labels and len(partition_labels) == len(source_units):
        partitions = []
        for label in partition_labels:
            fragments = [row for row in label.get("source_fragments", [])
                         if isinstance(row, dict) and (row.get("view"), row.get("raw_index")) == key]
            covered = span_lines(label)
            if len(fragments) != 1 or covered is None or len(covered) != 1:
                return False
            partitions.append((fragments[0].get("start"), fragments[0].get("end"), covered[0]))
        if any(type(start) is not int or type(end) is not int for start, end, _ in partitions):
            return False
        partitions.sort(key=lambda row: (row[0], row[1]))
        if (partitions[0][0] != 0 or partitions[-1][1] != len(raw_title)
                or any(end != next_start for (_, end, _), (next_start, _, _) in zip(partitions, partitions[1:]))):
            return False
        from kb_creator.pipeline.semantic_structure import _normalized
        return "".join(_normalized(line) for _, _, line in partitions) == _normalized(raw_title)

    callouts = [unit for unit in units if bound(unit, kind="callout", representation="blockquote")]
    if len(callouts) == 1:
        covered = span_lines(callouts[0])
        pattern = re.compile(rf"> #{{1,6}}\s+{re.escape(title)}\s*#*\s*")
        if covered and re.fullmatch(pattern, covered[0]) and sum(bool(pattern.fullmatch(line)) for line in lines) == 1:
            return True
    quotes = [unit for unit in units if bound(unit, kind="blockquote", representation="blockquote")]
    if len(quotes) == 1:
        covered = span_lines(quotes[0])
        if covered == [f"> {title}"] and lines.count(f"> {title}") == 1:
            return True
    statblocks = [unit for unit in units if bound(unit, kind="statblock", representation="semantic_span")]
    if len(statblocks) == 1:
        covered = span_lines(statblocks[0])
        if covered is not None and covered.count(title) == 1 and lines.count(title) == 1:
            return True
    handouts = [unit for unit in units if bound(unit, kind="handout", representation="blockquote")]
    if len(handouts) == 1 and decision.get("review", {}).get("visual_reviewed") is True:
        covered = span_lines(handouts[0])
        note = re.compile(
            rf"(?im)^\s*title downgrade:\s*{re.escape(raw_title.strip())}\s*;\s*representation:\s*blockquote\s*;\s*reason:\s*\S.+$"
        )
        if covered and covered[0] == f"> **{title}**" and lines.count(f"> **{title}**") == 1 and note.search(str(decision["review"].get("notes", ""))):
            return True
    if (decision.get("source_page"), key[0], key[1]) not in (split_structure_proof_keys or set()):
        return False
    split = [unit for unit in units if isinstance(unit, dict) and any(
        isinstance(row, dict) and (row.get("view"), row.get("raw_index")) == key for row in unit.get("source_blocks", [])
    )]
    if len(split) != 2:
        return False
    heading = [unit for unit in split if unit.get("kind") == "heading" and unit.get("representation") == "atx_heading"]
    labels = [unit for unit in split if unit.get("kind") == "label" and unit.get("representation") == "semantic_span"]
    if len(heading) != 1 or len(labels) != 1:
        return False
    fragments = []
    for unit in split:
        rows = [row for row in unit.get("source_fragments", []) if isinstance(row, dict) and (row.get("view"), row.get("raw_index")) == key]
        if len(rows) != 1:
            return False
        fragments.append((rows[0].get("start"), rows[0].get("end"), unit))
    fragments.sort(key=lambda row: row[:2])
    if [(start, end) for start, end, _ in fragments] != [(0, fragments[0][1]), (fragments[0][1], len(raw_title))]:
        return False
    prefix, suffix = raw_title[:fragments[0][1]], raw_title[fragments[0][1]:]
    # Stage05 compares fragments through its normalized reader projection. At
    # this one physical partition boundary, the reader line may omit only the
    # leading horizontal whitespace carried by the suffix fragment. Preserve
    # its source hash and offsets; do not normalize interior reader content.
    reader_suffix = suffix.lstrip(" \t")
    if reader_suffix == suffix:
        return False
    heading_lines, label_lines = span_lines(heading[0]), span_lines(labels[0])
    return (
        prefix + suffix == title
        and heading_lines is not None and label_lines is not None
        and len(heading_lines) == 1 and len(label_lines) == 1
        and re.fullmatch(rf"#{{1,6}}\s+{re.escape(prefix)}\s*#*\s*", heading_lines[0]) is not None
        and sum(bool(re.fullmatch(rf"#{{1,6}}\s+{re.escape(prefix)}\s*#*\s*", line)) for line in lines) == 1
        and label_lines[0] == reader_suffix and lines.count(reader_suffix) == 1
    )


def _selected_conflicts(comparison: dict[str, Any], selected: dict[tuple[str, int], dict[str, Any]]) -> list[tuple[dict[str, Any], list[dict[str, Any]]]]:
    conflicts: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    pairwise = comparison.get("pairwise", {})
    if not isinstance(pairwise, dict):
        return conflicts
    for pair_name, pair in pairwise.items():
        if not isinstance(pair_name, str) or "__vs__" not in pair_name or not isinstance(pair, dict):
            continue
        left_view, right_view = pair_name.split("__vs__", 1)
        for conflict_index, conflict in enumerate(pair.get("semantic_conflicts", [])):
            if not isinstance(conflict, dict) or conflict.get("resolution") is not None:
                continue
            keys: set[tuple[str, int]] = set()
            if type(conflict.get("left_raw_index")) is int:
                keys.add((left_view, conflict["left_raw_index"]))
            if type(conflict.get("right_raw_index")) is int:
                keys.add((right_view, conflict["right_raw_index"]))
            asset_side = conflict.get("asset_side", conflict.get("side"))
            heading_side = conflict.get("heading_side", conflict.get("side"))
            if type(conflict.get("asset_raw_index")) is int and asset_side in {"left", "right"}:
                keys.add(((left_view if asset_side == "left" else right_view), conflict["asset_raw_index"]))
            if type(conflict.get("heading_raw_index")) is int and heading_side in {"left", "right"}:
                keys.add(((left_view if heading_side == "left" else right_view), conflict["heading_raw_index"]))
            selected_units = [
                {"view": key[0], "raw_index": key[1], "block": selected[key]}
                for key in keys if key in selected
            ]
            if selected_units:
                conflicts.append(({**conflict, "_pair_name": pair_name,
                                  "_semantic_conflict_index": conflict_index}, selected_units))
    return conflicts


def structural_conflict_locator(source_page: int, conflict: dict[str, Any]) -> tuple[int, str, int, str]:
    """Return the stable locator used by sealed structural-role issue proofs."""
    pair, index = conflict.get("_pair_name"), conflict.get("_semantic_conflict_index")
    if type(source_page) is not int or not isinstance(pair, str) or type(index) is not int:
        raise ValueError("structural conflict lacks an exact comparison locator")
    unsigned = {key: value for key, value in conflict.items() if not key.startswith("_")}
    digest = hashlib.sha256(json.dumps(unsigned, ensure_ascii=False, sort_keys=True,
                                      separators=(",", ":")).encode("utf-8")).hexdigest()
    return source_page, pair, index, digest


def _resolved_title_to_text_downgrade(
    conflict: dict[str, Any], selected_units: list[dict[str, Any]], markdown: str,
    review: dict[str, Any], semantic_structure: Any = None,
) -> bool:
    """Allow an exact reviewed heading or sealed container-role resolution."""
    if conflict.get("kind") != "title_to_text_downgrade" or len(selected_units) != 1:
        return False
    selected = selected_units[0]
    block = selected.get("block")
    title = block.get("text") if isinstance(block, dict) else None
    if not isinstance(title, str) or not title.strip():
        return False
    exact_title = title.strip()
    heading = re.search(rf"(?m)^#{{1,6}}\s+{re.escape(exact_title)}\s*#*\s*$", markdown)
    if heading and _explicit_title_override(review["notes"], exact_title, review["visual_reviewed"]):
        return True
    # Some engines label a visually subordinate line inside a handout/card or
    # statblock as a title.  A reviewer may preserve it as ordinary container
    # content only when the exact source block is bound to one reviewed unit
    # and the decision records an exact, reasoned downgrade.  This avoids both
    # silent flattening and the false requirement to promote every card field
    # or subtitle to a document heading.
    if not review.get("visual_reviewed") or not isinstance(semantic_structure, dict):
        return False
    units = semantic_structure.get("units")
    if not isinstance(units, list):
        return False
    key = (selected.get("view"), selected.get("raw_index"))
    matches = [
        unit for unit in units
        if isinstance(unit, dict)
        and unit.get("representation") in {"blockquote", "semantic_span", "unordered_list"}
        and any(
            isinstance(source, dict)
            and (source.get("view"), source.get("raw_index")) == key
            for source in unit.get("source_blocks", [])
        )
    ]
    if len(matches) != 1:
        return False
    span = matches[0].get("markdown_span")
    if not isinstance(span, dict) or type(span.get("start_line")) is not int or type(span.get("end_line")) is not int:
        return False
    lines = markdown.split("\n")
    start, end = span["start_line"], span["end_line"]
    if not 1 <= start <= end <= len(lines):
        return False
    representation = matches[0]["representation"]
    if representation == "unordered_list":
        if matches[0].get("kind") != "list" or matches[0].get("item_count") != 1 or not exact_title.startswith("● "):
            return False
        item = exact_title[2:]
        if not item:
            return False
        if end != start:
            return False
        list_match = re.fullmatch(r"-[ \t]+(?:(?:\*\*)(?P<bold>.+?)(?:\*\*)|(?P<plain>.+))", lines[start - 1])
        if not list_match or (list_match.group("bold") or list_match.group("plain")) != item:
            return False
        return re.search(
            rf"(?im)^\s*title downgrade:\s*{re.escape(exact_title)}\s*;\s*representation:\s*unordered_list\s*;\s*reason:\s*\S.+$",
            review.get("notes", ""),
        ) is not None
    if representation == "blockquote":
        preserved = re.compile(rf"^>\s+(?:[*_]{{1,2}})?{re.escape(exact_title)}(?:[*_]{{1,2}})?\s*$")
    else:
        preserved = re.compile(rf"^(?:[*_]{{1,2}})?{re.escape(exact_title)}(?:[*_]{{1,2}})?\s*$")
    if sum(bool(preserved.fullmatch(line)) for line in lines[start - 1:end]) != 1:
        return False
    return re.search(
        rf"(?im)^\s*title downgrade:\s*{re.escape(exact_title)}\s*;\s*representation:\s*{re.escape(representation)}\s*;\s*reason:\s*\S.+$",
        review.get("notes", ""),
    ) is not None


def _resolved_image_heading_overlap(
    conflict: dict[str, Any], selected_units: list[dict[str, Any]], decision: dict[str, Any],
    reference_proof_keys: set[tuple[int, str, int, str, str]] | None = None,
    split_structure_proof_keys: set[tuple[int, str, int]] | None = None,
    packet: dict[str, Any] | None = None,
) -> bool:
    """Resolve cross-view image/title ambiguity through the selected role."""
    if conflict.get("kind") != "image_heading_overlap" or len(selected_units) != 1:
        return False
    selected = selected_units[0]
    block = selected.get("block")
    if not isinstance(block, dict) or decision.get("review", {}).get("visual_reviewed") is not True:
        return False
    purpose = block.get("_selection_purpose")
    key = (selected.get("view"), selected.get("raw_index"))
    if purpose == "text" and block.get("type") == "table" and packet is not None:
        structure = decision.get("semantic_structure")
        units = structure.get("units") if isinstance(structure, dict) else None
        if not isinstance(units, list):
            return False
        visual = structure.get("review", {}).get("visual") if isinstance(structure.get("review"), dict) else None
        if not isinstance(visual, dict) or not isinstance(visual.get("path"), str):
            return False
        try:
            from kb_creator.pipeline.semantic_structure import SemanticStructureError, validate_semantic_structure
            validate_semantic_structure(
                {decision["source_page"]: decision}, {decision["source_page"]: packet},
                {visual["path"]: {"bytes": visual.get("bytes"), "sha256": visual.get("sha256")}},
                required_pages=[decision["source_page"]],
            )
        except (KeyError, SemanticStructureError, ValueError, TypeError):
            return False
        source_text = block.get("text")
        matches = [unit for unit in units if isinstance(unit, dict)
            and unit.get("kind") == "statblock" and unit.get("representation") == "table"
            and any(isinstance(row, dict) and (row.get("view"), row.get("raw_index")) == key for row in unit.get("source_blocks", []))]
        if len(matches) != 1 or not isinstance(source_text, str):
            return False
        fragments = [row for row in matches[0].get("source_fragments", []) if isinstance(row, dict) and (row.get("view"), row.get("raw_index")) == key]
        if len(fragments) != 1 or (fragments[0].get("start"), fragments[0].get("end")) != (0, len(source_text)):
            return False
        source_paths = block.get("assets")
        crops = [asset for asset in decision.get("assets", []) if isinstance(asset, dict)
            and asset.get("view") == key[0] and asset.get("placement") == "reference_only"
            and isinstance(source_paths, list) and asset.get("source_path") in source_paths]
        if len(crops) != 1:
            return False
        pair_name = conflict.get("_pair_name")
        if not isinstance(pair_name, str) or "__vs__" not in pair_name:
            return False
        left, right = pair_name.split("__vs__", 1)
        heading_side, asset_side = conflict.get("heading_side", conflict.get("side")), conflict.get("asset_side", conflict.get("side"))
        if heading_side not in {"left", "right"} or asset_side not in {"left", "right"}:
            return False
        selected_side = "left" if key[0] == left else "right" if key[0] == right else None
        if selected_side not in {heading_side, asset_side}:
            return False
        other_side = asset_side if selected_side == heading_side else heading_side
        selected_raw = conflict.get("heading_raw_index") if selected_side == heading_side else conflict.get("asset_raw_index")
        if selected_raw != key[1]:
            return False
        other_view = left if other_side == "left" else right
        other_raw = conflict.get("asset_raw_index") if other_side == asset_side else conflict.get("heading_raw_index")
        if type(other_raw) is not int:
            return False
        other = [row for row in packet.get("views", {}).get(other_view, {}).get("blocks", []) if isinstance(row, dict) and row.get("raw_index") == other_raw]
        # Comparison owns the paired source-region geometry. MinerU may round
        # one view's coordinates differently, so require its sealed overlap
        # signal rather than inventing an exact-bbox equality contract.
        overlap = conflict.get("bbox_iou")
        return len(other) == 1 and other[0].get("type") == "table" and type(overlap) in {int, float} and overlap >= 0.8
    if purpose == "structure":
        structure = decision.get("semantic_structure")
        units = structure.get("units") if isinstance(structure, dict) else None
        if not isinstance(units, list):
            return False
        matches = [
            unit for unit in units
            if isinstance(unit, dict)
            and unit.get("representation") in {"blockquote", "semantic_span", "table"}
            and any(
                isinstance(source, dict)
                and (source.get("view"), source.get("raw_index")) == key
                for source in unit.get("source_blocks", [])
            )
        ]
        if len(matches) == 1:
            return True
        if len(matches) < 2:
            return False
        if (decision.get("source_page"), key[0], key[1]) not in (split_structure_proof_keys or set()):
            return False
        # The key is emitted only after the shared v2 validator proves exact
        # fragments and their complete partition. Keep local shape checks so a
        # proof cannot be used for a different structure in the same decision.
        if structure.get("schema") != "kb_creator.page_semantic_structure.v2" or structure.get("profile") != "reviewed_role_outline_and_partitions_v2":
            return False
        bound = [
            unit for unit in units
            if isinstance(unit, dict)
            and any(
                isinstance(source, dict) and (source.get("view"), source.get("raw_index")) == key
                for source in unit.get("source_blocks", [])
            )
        ]
        if len(bound) != len(matches) + sum(unit.get("representation") == "atx_heading" for unit in bound):
            return False
        if any(
            not isinstance(unit.get("source_fragments"), list)
            or not any(
                isinstance(fragment, dict) and (fragment.get("view"), fragment.get("raw_index")) == key
                for fragment in unit["source_fragments"]
            )
            for unit in bound
        ):
            return False
        return any(unit.get("representation") == "atx_heading" for unit in bound)
    if purpose == "asset":
        paths = block.get("assets")
        if not isinstance(paths, list) or not paths:
            return False
        matches = [
            asset for asset in decision.get("assets", [])
            if isinstance(asset, dict)
            and asset.get("view") == key[0]
            and asset.get("source_path") in paths
            and (asset.get("placement") != "reference_only" or any(
                key_row[:4] == (decision.get("source_page"), key[0], key[1], asset.get("logical_name"))
                for key_row in (reference_proof_keys or set())
            ))
        ]
        return len(matches) == 1
    return False


def _resolved_semantic_conflict(
    conflict: dict[str, Any], selected_units: list[dict[str, Any]], decision: dict[str, Any],
    reference_proof_keys: set[tuple[int, str, int, str, str]] | None = None,
    split_structure_proof_keys: set[tuple[int, str, int]] | None = None,
    packet: dict[str, Any] | None = None,
    visual_assertions: dict[str, dict[str, Any]] | None = None,
) -> bool:
    title_role = False
    if conflict.get("kind") == "title_to_text_downgrade" and len(selected_units) == 1 and packet is not None:
        selected = selected_units[0]
        block = selected.get("block")
        raw_title = block.get("text") if isinstance(block, dict) else None
        if isinstance(raw_title, str) and raw_title.strip():
            title_role = _validated_v2_title_role(
                decision, packet, raw_title.strip(), (selected.get("view"), selected.get("raw_index")),
                split_structure_proof_keys, visual_assertions,
            )
    return title_role or _resolved_title_to_text_downgrade(
        conflict, selected_units, decision["markdown"], decision["review"], decision.get("semantic_structure")
    ) or _resolved_image_heading_overlap(
        conflict, selected_units, decision, reference_proof_keys, split_structure_proof_keys, packet,
    )


def _apply_block_boundaries(markdown: str, boundaries: Any) -> str:
    # Kept as a public compatibility shim for existing callers/tests.  Stage05
    # and Stage06 use the shared implementation so their span hashes cannot
    # diverge.
    from kb_creator.pipeline.semantic_structure import apply_block_boundaries
    try:
        return apply_block_boundaries(markdown, boundaries)
    except Exception as error:
        raise ValueError(str(error)) from error
    """unreachable legacy body retained below for narrow backport diff."""
    if boundaries is None:
        return markdown
    if not isinstance(boundaries, list) or not boundaries:
        raise ValueError("block_boundaries must be a nonempty list when present")
    lines = markdown.split("\n")
    removals: list[int] = []
    selectors: set[tuple[str, str]] = set()
    for boundary in boundaries:
        row = _closed(boundary, set(BLOCK_BOUNDARY_KEYS), "block boundary")
        heading = row["heading_line"]
        first_body = row["first_body_line"]
        if row["style"] != "compact":
            raise ValueError("unsupported block boundary style")
        if (
            not isinstance(heading, str)
            or "\n" in heading
            or "\r" in heading
            or re.fullmatch(r"#{1,6}[ \t]+\S.*", heading) is None
        ):
            raise ValueError("compact block boundary heading_line must be one exact ATX heading")
        if (
            not isinstance(first_body, str)
            or not first_body.strip()
            or "\n" in first_body
            or "\r" in first_body
        ):
            raise ValueError("compact block boundary first_body_line must be one exact nonempty line")
        selector = (heading, first_body)
        if selector in selectors:
            raise ValueError("duplicate compact block boundary selector")
        selectors.add(selector)
        if lines.count(heading) != 1:
            raise ValueError("compact block boundary heading_line must match exactly once")
        matches = [
            index
            for index in range(len(lines) - 2)
            if lines[index] == heading
            and lines[index + 1] == ""
            and lines[index + 2] == first_body
        ]
        if len(matches) != 1:
            raise ValueError(
                "compact block boundary must match exactly one heading, one empty separator, and its first body line"
            )
        removals.append(matches[0] + 1)
    if len(set(removals)) != len(removals):
        raise ValueError("compact block boundaries overlap")
    for index in sorted(removals, reverse=True):
        del lines[index]
    return "\n".join(lines)


def _validate_decision(
    decision: Any,
    packet: dict[str, Any],
    comparison: dict[str, Any],
    raw_root: Path,
    names: set[str],
    source_render_context: dict[str, Any] | None = None,
    source_render_staging: Path | None = None,
    reference_proof_keys: set[tuple[int, str, int, str, str]] | None = None,
    split_structure_proof_keys: set[tuple[int, str, int]] | None = None,
    structural_role_proofs: dict[tuple[int, str, int, str], dict[str, Any]] | None = None,
    visual_assertions: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    optional_fields = {"block_boundaries", "semantic_structure", "reviewed_block_corrections",
                       "reviewed_prose_bindings_v1", "reviewed_prose_roles_v1", "linguistic_source_choice_corrections"}
    if (not isinstance(decision, dict) or not DECISION_KEYS <= frozenset(decision)
            or not frozenset(decision) - DECISION_KEYS <= optional_fields):
        raise ValueError("decision must be an object with exact keys")
    data = decision
    if data["schema"] != DECISION_SCHEMA or data["source_page"] != packet["source_page"] or data["semantic_role"] != packet["semantic_role"]:
        raise ValueError("decision does not bind to its source packet")
    views = packet.get("views")
    if not isinstance(views, dict) or data["overlay_preference"] not in views:
        raise ValueError("invalid overlay_preference")
    if not isinstance(data["selected_blocks"], list) or not isinstance(data["assets"], list) or not isinstance(data["unresolved"], list):
        raise ValueError("decision lists are invalid")
    if not isinstance(data["markdown"], str):
        raise ValueError("markdown must be a string")
    _validate_markdown(data["markdown"])
    materialized_markdown = _apply_block_boundaries(
        data["markdown"], data.get("block_boundaries")
    )
    review = _closed(data["review"], {"visual_reviewed", "notes"}, "review")
    if type(review["visual_reviewed"]) is not bool or not isinstance(review["notes"], str):
        raise ValueError("invalid review")
    if any(not isinstance(item, str) or not item.strip() for item in data["unresolved"]):
        raise ValueError("unresolved items must be nonempty strings")
    # A source key normally has one selection purpose.  The sole additional
    # shape is a reader selection plus its exact binary asset: maps and tables
    # can be both readable and preserved as a source raster.  Keep the reader
    # record as the representative for downstream title/conflict checks, while
    # retaining the asset purpose separately for binary validation below.
    selected: dict[tuple[str, int], dict[str, Any]] = {}
    selected_asset_keys: set[tuple[str, int]] = set()
    selected_purposes: dict[tuple[str, int], set[str]] = {}
    for row in data["selected_blocks"]:
        _closed(row, {"view", "raw_index", "purpose"}, "selected block")
        if row["view"] not in views or type(row["raw_index"]) is not int or row["purpose"] not in PURPOSES:
            raise ValueError("invalid selected block")
        matches = [block for block in views[row["view"]].get("blocks", []) if block.get("raw_index") == row["raw_index"]]
        key = (row["view"], row["raw_index"])
        if len(matches) != 1:
            raise ValueError("selected block is missing or ambiguous")
        purposes = selected_purposes.setdefault(key, set())
        if row["purpose"] in purposes:
            raise ValueError("selected block duplicates one purpose")
        purposes.add(row["purpose"])
        if row["purpose"] == "asset":
            selected_asset_keys.add(key)
            selected.setdefault(key, {**matches[0], "_selection_purpose": "asset"})
        else:
            selected[key] = {**matches[0], "_selection_purpose": row["purpose"]}
    for key, purposes in selected_purposes.items():
        if "visual" in purposes:
            if len(purposes) != 1:
                raise ValueError("legacy visual purpose cannot enter selected source route")
            # Legacy visual-only selections retain their established isolated
            # behavior.  They cannot be combined with this reader-plus-asset
            # route.
            continue
        if len(purposes) > 2 or purposes == {"text", "structure"}:
            raise ValueError("selected block has incompatible purposes")
        if len(purposes) == 2 and purposes != {"text", "asset"} and purposes != {"structure", "asset"}:
            raise ValueError("selected block has incompatible purposes")
        block = selected.get(key)
        if block is None:
            continue
        if block.get("type") != "image":
            continue
        if not purposes & {"text", "structure"}:
            continue
        if purposes not in ({"text", "asset"}, {"structure", "asset"}):
            raise ValueError("an image block cannot be selected as body text")
        caption = block.get("text")
        if not isinstance(caption, str) or not caption.strip():
            raise ValueError("image reader selection lacks an extracted caption")
        if data["markdown"].splitlines().count(caption) != 1:
            raise ValueError("image caption lacks exact source-to-reader proof")
    # Title-view disagreement is resolved by the same closed review ledger as
    # Stage 05.  Do this before the legacy selected-title guard so a reviewed
    # source-to-reader correction is neither silently downgraded nor rejected
    # for differing from noisy selected OCR.
    from kb_creator.pipeline.semantic_structure import (
        apply_reviewed_text_corrections, reviewed_block_text_corrections,
        reviewed_text_corrections, reviewed_title_evidence_confirmations,
    )
    packet_blocks = {
        (view, block["raw_index"]): block
        for view, view_data in views.items()
        for block in view_data.get("blocks", [])
        if isinstance(block, dict) and type(block.get("raw_index")) is int
    }
    title_confirmations = reviewed_title_evidence_confirmations(
        data, packet_blocks, materialized_markdown, data["source_page"],
    )
    text_selected = {key for key, block in selected.items() if block["_selection_purpose"] != "asset"}
    corrections = reviewed_text_corrections(data, packet_blocks, text_selected, materialized_markdown, data["source_page"])
    block_corrections = reviewed_block_text_corrections(data, packet_blocks, text_selected, materialized_markdown, data["source_page"])
    selected_conflicts = _selected_conflicts(comparison, selected)
    unresolved_conflicts = []
    for conflict, selected_units in selected_conflicts:
        if _resolved_semantic_conflict(conflict, selected_units, data, reference_proof_keys,
                                       split_structure_proof_keys, packet, visual_assertions):
            continue
        locator = structural_conflict_locator(data["source_page"], conflict)
        proof = (structural_role_proofs or {}).get(locator)
        occurrence = selected_units[0] if len(selected_units) == 1 else None
        if (not isinstance(proof, dict) or not isinstance(occurrence, dict)
                or proof.get("selected_source_key") != {"view": occurrence.get("view"), "raw_index": occurrence.get("raw_index")}):
            unresolved_conflicts.append(conflict)
    if unresolved_conflicts:
        raise ValueError("selected block has an unresolved semantic comparison conflict (no exact structural issue proof)")
    for (view, raw_index), block in selected.items():
        if not _is_title(block):
            continue
        title = block.get("text")
        if not isinstance(title, str) or not title.strip():
            if title == "" and _validated_v2_title_role(
                data, packet, title, (view, raw_index), split_structure_proof_keys,
                visual_assertions,
            ):
                continue
            raise ValueError("title evidence lacks exact source text")
        exact_title = title_confirmations.get(
            (view, raw_index),
            apply_reviewed_text_corrections(title, (view, raw_index), corrections, block_corrections),
        ).strip()
        structure = data.get("semantic_structure")
        is_v2 = isinstance(structure, dict) and (
            structure.get("schema"), structure.get("profile")
        ) == ("kb_creator.page_semantic_structure.v2", "reviewed_role_outline_and_partitions_v2")
        heading = re.search(rf"(?m)^#{{1,6}}\s+{re.escape(exact_title)}\s*#*\s*$", data["markdown"])
        nested_heading = _exact_nested_heading(
            data["markdown"], exact_title, structure, (view, raw_index)
        )
        reviewed_downgrade = _resolved_title_to_text_downgrade(
            {"kind": "title_to_text_downgrade"},
            [{"view": view, "raw_index": raw_index, "block": block}],
            data["markdown"], review, data.get("semantic_structure"),
        )
        title_role = _validated_v2_title_role(
            data, packet, exact_title, (view, raw_index), split_structure_proof_keys,
            visual_assertions,
        )
        # V2 decisions have a sealed source-fragment role ledger.  Page-wide
        # Markdown presence can only be used by the legacy profile: otherwise
        # a neighbouring equal heading would satisfy the wrong source key.
        accepted = title_role if is_v2 else (
            heading or nested_heading or reviewed_downgrade or title_role
            or _explicit_title_override(review["notes"], exact_title, review["visual_reviewed"])
        )
        if not accepted:
            raise ValueError(f"selected title evidence {view}:{raw_index} is silently downgraded")
    asset_records = []
    for asset in data["assets"]:
        if isinstance(asset, dict) and asset.get("origin") == "source_pdf_page_render_v1":
            if source_render_context is None:
                raise ValueError("source-page render requires replay authority")
            validate_source_page_render_row(asset, decision_page=data["source_page"], expected_source_sha256=source_render_context["source_sha256"], expected_renderer_sha256=source_render_context["renderer_sha256"], markdown=data["markdown"], page_visual_reviewed=review["visual_reviewed"])
            proofs = source_render_context.get("proofs", {}).get(data["source_page"], [])
            if len([proof for proof in proofs if proof.get("logical_name") == asset["logical_name"] and proof.get("render") == asset["render"]]) != 1:
                raise ValueError("source-page render lacks one matching Stage05 proof")
            logical_name = _safe_basename(asset["logical_name"])
            if logical_name.casefold() in names:
                raise ValueError("invalid or duplicate logical asset name")
            if source_render_staging is None:
                raise ValueError("source-page render requires owned staging root")
            preview = source_render_staging / f"page-{data['source_page']:03d}-{logical_name}"
            facts = render_source_pdf_page(source_render_context["source"], data["source_page"], source_render_context["renderer"], asset["render"]["dpi"], preview, expected_source_sha256=source_render_context["source_sha256"], expected_renderer_sha256=source_render_context["renderer_sha256"])
            if {key: facts[key] for key in ("recipe", "dpi", "renderer_sha256", "pixels", "bytes", "sha256")} != asset["render"]:
                raise ValueError("source-page render does not match sealed Stage05 facts")
            names.add(logical_name.casefold())
            asset_records.append({"origin": asset["origin"], "source_page": asset["source_page"], "source_sha256": asset["source_sha256"], "logical_name": logical_name, "placement": asset["placement"], "render": asset["render"], "source_visual_review": asset["source_visual_review"], "resolved_source": preview, "sha256": facts["sha256"]})
            continue
        _closed(asset, {"view", "source_path", "logical_name", "placement"}, "asset")
        view, source_path, logical_name, placement = asset["view"], _safe_relative(asset["source_path"]), _safe_basename(asset["logical_name"]), asset["placement"]
        if view not in views or placement not in PLACEMENTS or logical_name.casefold() in names:
            raise ValueError("invalid or duplicate logical asset name")
        candidates = [
            block for key, block in selected.items()
            if key[0] == view
            and (key in selected_asset_keys or len(selected_purposes[key]) == 1)
            and source_path in block.get("assets", [])
        ]
        if len(candidates) != 1:
            raise ValueError("selected asset is not an exact reference of one selected block")
        content_list = comparison.get("views", {}).get(view, {}).get("artifacts", {}).get("content_list")
        if isinstance(content_list, dict):
            _closed(content_list, {"base", "view_id", "path", "bytes", "sha256"}, "replay content-list reference")
            if content_list["base"] != "view_artifact_root" or content_list["view_id"] != view:
                raise ValueError("replay content-list scope mismatch")
            relative = _safe_relative(content_list["path"])
            content_list_path = _checked_file(raw_root / "views" / view / "artifacts" / relative, root=raw_root)
            if _identity(content_list_path) != {"bytes": content_list["bytes"], "sha256": content_list["sha256"]}:
                raise ValueError("replay content-list identity mismatch")
        elif isinstance(content_list, str):
            content_list_path = _checked_file(Path(content_list), root=raw_root)
        else:
            raise ValueError("comparison lacks raw content-list artifact path")
        raw_dir = content_list_path.parent
        try:
            raw_dir.relative_to(raw_root.resolve())
        except ValueError as exc:
            raise ValueError("raw view artifact directory escapes raw root") from exc
        source = _checked_file(raw_dir / source_path, root=raw_dir)
        names.add(logical_name.casefold())
        asset_records.append({"view": view, "source_path": source_path, "logical_name": logical_name, "placement": placement, "resolved_source": source, "sha256": sha256_file(source)})
    for key, purposes in selected_purposes.items():
        if len(purposes) == 2 and "asset" in purposes:
            paths = selected[key].get("assets", [])
            if not any(asset.get("view") == key[0] and asset.get("source_path") in paths
                       for asset in asset_records):
                raise ValueError("dual-purpose source lacks a materialized binary asset")
    placeholders = _asset_placeholders(data["markdown"])
    image_names = _image_placeholder_names(data["markdown"])
    logical_names = {asset["logical_name"] for asset in asset_records}
    if any(name not in logical_names for name in placeholders):
        raise ValueError("markdown references an unknown decision asset")
    for asset in asset_records:
        if asset["placement"] != "reference_only" and asset["logical_name"] not in image_names:
            raise ValueError("selected non-reference asset is missing its Markdown image")
    if not data["markdown"] and not any(asset["placement"] == "reference_only" for asset in asset_records):
        raise ValueError("empty markdown requires a reference_only asset")
    return list(selected.values()), asset_records, materialized_markdown


def _reviewed_visual_assertions(decisions_root: Path) -> dict[str, dict[str, Any]]:
    """Load the one sealed Stage05 assertion set beside a V4 decision snapshot."""
    snapshot_root = decisions_root.parent
    candidates = [snapshot_root / "reviewed_allowlist.json", snapshot_root / "reviewed_allowlist.v3.json"]
    present = [path for path in candidates if path.is_file()]
    if len(present) != 1:
        raise ValueError("replay-v4 image-text proof requires reviewed allowlist beside decisions")
    allowlist = _json(_checked_file(present[0], root=snapshot_root))
    rows = allowlist.get("visual_text_assertions") if isinstance(allowlist, dict) else None
    if not isinstance(rows, list):
        raise ValueError("replay-v4 image-text proof allowlist is malformed")
    assertions = {row["assertion_id"]: row for row in rows if isinstance(row, dict) and isinstance(row.get("assertion_id"), str)}
    if len(assertions) != len(rows):
        raise ValueError("replay-v4 image-text proof assertions are malformed")
    return assertions


def _enriched_reviewed_visual_assertions(
    decisions_root: Path, decisions: dict[int, dict[str, Any]], packets: dict[int, dict[str, Any]],
    geometry: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Recreate the validated ephemeral positional context for Stage06 consumers."""
    from kb_creator.scripts.author_reviewed_semantic_decisions import semantic_assertion_map

    try:
        return semantic_assertion_map(_reviewed_visual_assertions(decisions_root), decisions, packets, geometry)
    except ValueError as error:
        raise ValueError(f"replay-v4 positional assertion context is invalid: {error}") from error


def _prevalidated_reference_proof_keys(
    *, replay_run_root: Path | None, fidelity_report: dict[str, Any] | None,
    visual_manifest_path: Path, decisions: dict[int, dict[str, Any]],
    packets: dict[int, dict[str, Any]],
    decisions_root: Path, geometry: dict[str, Any],
) -> tuple[set[tuple[int, str, int, str, str]], set[tuple[int, str, int]]]:
    if replay_run_root is None or not isinstance(fidelity_report, dict) or fidelity_report.get("schema") != V4_AUDIT_SCHEMA:
        return set(), set()
    from kb_creator.pipeline.semantic_structure import (
        SemanticStructureError, collect_reference_image_proof_keys,
        collect_split_structure_proof_keys, validate_semantic_structure,
    )
    visual_manifest = _json(visual_manifest_path)
    inventory = {f"outputs/04-visual-merge-bundle/{row['path']}": {"bytes": row["bytes"], "sha256": row["sha256"]} for row in visual_manifest.get("files", [])}
    from kb_creator.pipeline.reconstruction_asset_inventory import selected_asset_inventory
    inventory = selected_asset_inventory(replay_run_root, inventory)
    assertions = _enriched_reviewed_visual_assertions(decisions_root, decisions, packets, geometry)
    try:
        sidecar = validate_semantic_structure(decisions, packets, inventory, required_pages=sorted(decisions), visual_assertions=assertions)
    except SemanticStructureError as error:
        raise ValueError(f"replay-v4 semantic structure invalid: {error}") from error
    if fidelity_report.get("semantic_structure", {}).get("structure_sha256") != sidecar["structure_sha256"]:
        raise ValueError("replay-v4 audit semantic structure identity mismatch")
    return (
        collect_reference_image_proof_keys(decisions, packets, assertions),
        collect_split_structure_proof_keys(decisions, packets),
    )


def materialize(
    bundle_root: Path,
    raw_root: Path,
    decisions_root: Path,
    output_root: Path,
    *,
    comparison: Path | None = None,
    comparison_sha256: str | None = None,
    fidelity_audit: Path | None = None,
    fidelity_audit_sha256: str | None = None,
    replay_run_root: Path | None = None,
    replay_bridge_sha256: str | None = None,
    replay_submission: Path | None = None,
    replay_submission_sha256: str | None = None,
    source_render_staging: Path | None = None,
    review_draft_authority: dict[str, Any] | None = None,
    review_draft_binding_root: Path | None = None,
) -> dict[str, Any]:
    if source_render_staging is None:
        output_root.parent.mkdir(parents=True, exist_ok=True)
        scratch = Path(tempfile.mkdtemp(prefix=".source-render-", dir=output_root.parent))
        try:
            return materialize(
                bundle_root, raw_root, decisions_root, output_root,
                comparison=comparison, comparison_sha256=comparison_sha256,
                fidelity_audit=fidelity_audit, fidelity_audit_sha256=fidelity_audit_sha256,
                replay_run_root=replay_run_root, replay_bridge_sha256=replay_bridge_sha256,
                replay_submission=replay_submission, replay_submission_sha256=replay_submission_sha256,
                source_render_staging=scratch, review_draft_authority=review_draft_authority,
                review_draft_binding_root=review_draft_binding_root,
            )
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    review_descriptor: dict[str, Any] | None = None
    if review_draft_authority is not None:
        if any(value is not None for value in (comparison, comparison_sha256, fidelity_audit, fidelity_audit_sha256, replay_run_root, replay_bridge_sha256, replay_submission, replay_submission_sha256)):
            raise ValueError("review-draft materialization authority is mutually exclusive with strict/replay arguments")
        from kb_creator.pipeline.review_draft_materialization import (
            verify_descriptor, verify_final_review_draft,
        )
        supplied_descriptor = verify_descriptor(review_draft_authority)
        # A caller-held descriptor is evidence, not authority.  Recompute the
        # whole review route immediately before output staging so a resealed
        # passed flag, decision, audit or source cannot bypass Stage05/06.
        recomputed_descriptor = verify_final_review_draft(
            run_root=Path(bundle_root).resolve().parent.parent,
            authored_root=Path(decisions_root).resolve().parent,
            input_path=Path(supplied_descriptor["input"]["path"]),
            evidence_path=Path(supplied_descriptor["final_evidence"]["path"]),
            binding_root=review_draft_binding_root,
        )
        if recomputed_descriptor != supplied_descriptor:
            raise ValueError("review-draft descriptor differs from freshly recomputed authority")
        review_descriptor = recomputed_descriptor
        if (Path(review_descriptor["bundle_root"]).resolve() != Path(bundle_root).resolve()
                or Path(review_descriptor["raw_root"]).resolve() != Path(raw_root).resolve()
                or Path(review_descriptor["decisions_root"]).resolve() != Path(decisions_root).resolve()):
            raise ValueError("review-draft descriptor roots differ from materialization arguments")
    if (comparison is None) != (comparison_sha256 is None):
        raise ValueError("comparison path and SHA-256 must be supplied together")
    if (fidelity_audit is None) != (fidelity_audit_sha256 is None):
        raise ValueError("fidelity audit path and SHA-256 must be supplied together")
    _assert_components_not_reparse(output_root)
    if output_root.exists() and any(output_root.iterdir()):
        raise FileExistsError(f"refusing non-empty output root: {output_root}")
    _assert_tree_not_reparse(bundle_root)
    _assert_tree_not_reparse(raw_root)
    bundle_root = bundle_root.resolve(strict=True)
    raw_root = raw_root.resolve(strict=True)
    visual_manifest_path = bundle_root / "visual" / "visual_manifest.json"
    queue: dict[str, Any] | None = None
    fidelity_report: dict[str, Any] | None = None
    selected_audit: Path | None = None
    if review_descriptor is not None:
        visual_manifest_path = _checked_file(visual_manifest_path, root=bundle_root)
        selected_comparison = _checked_file(Path(review_descriptor["comparison"]["path"]))
        selected_audit = _checked_file(Path(review_descriptor["audit"]["path"]))
        fidelity_report = _json(selected_audit)
        queue = _json(_checked_file(Path(review_descriptor["review_queue"]["path"])))
    elif replay_run_root is not None:
        visual_manifest_path = _checked_file(visual_manifest_path, root=bundle_root)
        selected_comparison, queue, selected_audit, fidelity_report = _replay_authority(
            bundle_root, raw_root, visual_manifest_path,
            comparison=comparison, comparison_sha256=comparison_sha256,
            fidelity_audit=fidelity_audit, fidelity_audit_sha256=fidelity_audit_sha256,
            replay_run_root=replay_run_root, replay_bridge_sha256=replay_bridge_sha256,
            replay_submission=replay_submission, replay_submission_sha256=replay_submission_sha256,
        )
    elif visual_manifest_path.exists():
        visual_manifest_path = _checked_file(visual_manifest_path, root=bundle_root)
        visual_schema = _json(visual_manifest_path).get("schema")
        if visual_schema == V2_BUNDLE_SCHEMA:
            if comparison is None or comparison_sha256 is None:
                raise ValueError("v2 materialization requires explicit comparison authority")
            selected_comparison, queue = _v2_authority(
                bundle_root, raw_root, comparison, comparison_sha256
            )
            if fidelity_audit is None or fidelity_audit_sha256 is None:
                raise ValueError("v2 materialization requires explicit Stage05 fidelity authority")
            selected_audit, fidelity_report = _v2_fidelity_authority(
                fidelity_audit, fidelity_audit_sha256, bundle_root, queue, selected_comparison
            )
        elif visual_schema == V3_BUNDLE_SCHEMA:
            raise ValueError("replay-v3 materialization requires complete run/bridge/submission/audit authority")
        elif visual_schema == V1_BUNDLE_SCHEMA:
            selected_comparison = (
                _checked_file(comparison)
                if comparison is not None
                else _checked_file(raw_root / "comparison" / "comparison.json", root=raw_root)
            )
            if comparison_sha256 is not None and sha256_file(selected_comparison) != comparison_sha256.upper():
                raise ValueError("explicit legacy comparison SHA-256 mismatch")
        else:
            raise ValueError("unknown visual bundle schema cannot use legacy fallback")
    else:
        selected_comparison = (
            _checked_file(comparison)
            if comparison is not None
            else _checked_file(raw_root / "comparison" / "comparison.json", root=raw_root)
        )
        if comparison_sha256 is not None and sha256_file(selected_comparison) != comparison_sha256.upper():
            raise ValueError("explicit legacy comparison SHA-256 mismatch")
    ordered, packets, comparison_data = _load_bundle(
        bundle_root, raw_root, selected_comparison
    )
    source_render_context = None
    if review_descriptor is not None:
        from kb_creator.pipeline.source_page_render import sha256_file as render_sha256_file
        source = _checked_file(Path(review_descriptor["source"]["path"]))
        renderer = _checked_file(Path(review_descriptor["renderer"]["path"]))
        if (render_sha256_file(source) != review_descriptor["source"]["sha256"]
                or render_sha256_file(renderer) != review_descriptor["renderer"]["sha256"]):
            raise ValueError("review-draft source or renderer identity mismatch")
        source_render_context = {
            "source": source, "renderer": renderer,
            "source_sha256": review_descriptor["source"]["sha256"],
            "renderer_sha256": review_descriptor["renderer"]["sha256"],
            "proofs": {row["source_page"]: row.get("source_page_renders", [])
                       for row in fidelity_report.get("pages", []) if isinstance(row, dict)},
        }
    elif replay_run_root is not None:
        from kb_creator.pipeline.source_page_render import replay_source_render_context
        source_render_context = replay_source_render_context(replay_run_root, _json(replay_run_root / "outputs/04-visual-merge-bundle/visual/geometry_plan.json"))
        source_render_context["proofs"] = {
            row["source_page"]: row.get("source_page_renders", [])
            for row in fidelity_report.get("pages", [])
            if isinstance(row, dict) and type(row.get("source_page")) is int
        }
    if queue is not None:
        queue_items = queue.get("items")
        if not isinstance(queue_items, list) or len(queue_items) != len(ordered):
            raise ValueError("review queue and merge bundle page domains differ")
        for item, row in zip(queue_items, ordered):
            packet_path = packets[row["source_page"]]["path"]
            if item.get("source_page") != row["source_page"] or item.get("merge_packet") != {
                "path": f"merge_packets/{row['packet']}",
                **_identity(packet_path),
            }:
                raise ValueError("review queue merge packet authority mismatch")
    domain = [row["source_page"] for row in ordered]
    if review_descriptor is not None:
        descriptor_pages = {row["source_page"] for row in review_descriptor["pages"]}
        if set(domain) != descriptor_pages:
            raise ValueError("review-draft descriptor page domain differs from merge bundle")
    decisions = _load_decisions(decisions_root, domain)
    requires_visual_assertions = review_descriptor is not None or (
        fidelity_report is not None and fidelity_report.get("schema") == V4_AUDIT_SCHEMA
    )
    geometry = None
    visual_assertions = None
    if requires_visual_assertions:
        geometry = _json(_checked_file(bundle_root / "visual" / "geometry_plan.json", root=bundle_root))
        visual_assertions = _enriched_reviewed_visual_assertions(
            decisions_root, {page: decisions[page][2] for page in domain},
            {page: packets[page]["packet"] for page in domain}, geometry,
        )
    if review_descriptor is not None:
        try:
            reference_proof_keys = {tuple(row) for row in review_descriptor["reference_proof_keys"]}
            split_structure_proof_keys = {tuple(row) for row in review_descriptor["split_structure_proof_keys"]}
        except TypeError as error:
            raise ValueError("review-draft descriptor Stage06 proof keys are malformed") from error
    else:
        reference_proof_keys, split_structure_proof_keys = _prevalidated_reference_proof_keys(
            replay_run_root=replay_run_root, fidelity_report=fidelity_report,
            visual_manifest_path=visual_manifest_path,
            decisions={page: decisions[page][2] for page in domain},
            packets={page: packets[page]["packet"] for page in domain},
            decisions_root=decisions_root, geometry=geometry or {},
        )
    structural_role_proofs = {
        tuple(row["locator"]): row["proof"]
        for row in (review_descriptor or {}).get("structural_role_proofs", [])
    }
    names: set[str] = set(); validated = {}
    for page in domain:
        path, raw, decision = decisions[page]
        try:
            blocks, assets, materialized_markdown = _validate_decision(
                decision, packets[page]["packet"], comparison_data, raw_root, names,
                source_render_context, source_render_staging, reference_proof_keys,
                split_structure_proof_keys, structural_role_proofs, visual_assertions,
            )
        except ValueError as exc:
            raise ValueError(f"page-{page:03d}.json: {exc}") from exc
        validated[page] = {
            "path": path,
            "raw": raw,
            "decision": decision,
            "blocks": blocks,
            "assets": assets,
            "materialized_markdown": materialized_markdown,
        }
    semantic_sidecar = None
    if fidelity_report is not None and fidelity_report.get("schema") == V4_AUDIT_SCHEMA:
        from kb_creator.pipeline.semantic_structure import SemanticStructureError, validate_semantic_structure
        visual_manifest = _json(visual_manifest_path)
        inventory = {
            f"outputs/04-visual-merge-bundle/{row['path']}": {"bytes": row["bytes"], "sha256": row["sha256"]}
            for row in visual_manifest.get("files", [])
        }
        from kb_creator.pipeline.reconstruction_asset_inventory import selected_asset_inventory
        inventory = selected_asset_inventory(replay_run_root, inventory)
        assertion_rows = {}
        if any(
            isinstance(unit, dict) and unit.get("visual_assertion_ids")
            for page in domain for unit in validated[page]["decision"].get("semantic_structure", {}).get("units", [])
        ):
            # Replay materialization receives the submission's `pages/` root;
            # the sealed allowlist is its sibling in the snapshot root.
            assertion_rows = visual_assertions
        try:
            semantic_sidecar = validate_semantic_structure(
                {page: validated[page]["decision"] for page in domain},
                {page: packets[page]["packet"] for page in domain}, inventory, required_pages=domain,
                visual_assertions=assertion_rows or None,
            )
        except SemanticStructureError as error:
            raise ValueError(f"replay-v4 semantic structure invalid: {error}") from error
        if fidelity_report.get("semantic_structure", {}).get("structure_sha256") != semantic_sidecar["structure_sha256"]:
            raise ValueError("replay-v4 audit semantic structure identity mismatch")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.stage-", dir=output_root.parent))
    try:
        pages_dir, decisions_dir, assets_dir = stage / "pages", stage / "decisions", stage / "assets"
        pages_dir.mkdir(); decisions_dir.mkdir(); assets_dir.mkdir()
        markdown_pages, provenance_pages, asset_manifest, blobs = [], [], [], {}
        for page in domain:
            item = validated[page]; decision = item["decision"]
            selected = [{"view": row["view"], "raw_index": row["raw_index"]} for row in decision["selected_blocks"]]
            provenance_pages.append({"source_page": page, "semantic_role": decision["semantic_role"], "packet": str(packets[page]["path"]), "packet_sha256": sha256_file(packets[page]["path"]), "decision_sha256": hashlib.sha256(item["raw"]).hexdigest().upper(), "selected_blocks": selected, "unresolved": decision["unresolved"]})
            for asset in item["assets"]:
                suffix = Path(asset["logical_name"]).suffix.lower()
                if not suffix:
                    suffix = Path(asset["resolved_source"]).suffix.lower() or ".bin"
                stored = f"{asset['sha256'].lower()}{suffix}"
                destination = assets_dir / stored
                if asset["sha256"] not in blobs:
                    shutil.copyfile(asset["resolved_source"], destination)
                    if sha256_file(destination) != asset["sha256"]: raise ValueError("copied asset hash mismatch")
                    blobs[asset["sha256"]] = stored
                asset["stored_path"] = f"assets/{blobs[asset['sha256']]}"
                if asset.get("origin") == "source_pdf_page_render_v1":
                    asset_manifest.append({k: asset[k] for k in ("origin", "source_page", "source_sha256", "logical_name", "placement", "render", "source_visual_review", "sha256", "stored_path")})
                else:
                    asset_manifest.append({k: asset[k] for k in ("view", "source_path", "logical_name", "placement", "sha256", "stored_path")})
            stored_paths = {asset["logical_name"]: asset["stored_path"] for asset in item["assets"]}
            marker = f"<!-- source-page-{page:03d} -->"
            page_markdown = _substitute_assets(item["materialized_markdown"], stored_paths, "../")
            root_markdown = _substitute_assets(item["materialized_markdown"], stored_paths, "")
            page_text = marker + "\n\n" + page_markdown.rstrip() + "\n"
            root_text = marker + "\n\n" + root_markdown.rstrip() + "\n"
            (pages_dir / f"page-{page:03d}.md").write_text(page_text, encoding="utf-8")
            (decisions_dir / f"page-{page:03d}.json").write_bytes(item["raw"])
            markdown_pages.append(root_text)
        combined = "\n".join(markdown_pages); (stage / "RECONSTRUCTED_EN.md").write_text(combined, encoding="utf-8")
        status = ("verified_review_draft_candidate" if review_descriptor is not None else
                  ("candidate_needs_review" if any(item["decision"]["unresolved"] for item in validated.values())
                   else "candidate_ready_for_reconstruction_qa"))
        if review_descriptor is not None:
            provenance = {
                "schema": "kb_creator.mineru_ai_merge_provenance.review_draft.v1",
                "status": status, "acceptance_inferred": False,
                "comparison": review_descriptor["comparison"],
                "review_queue": review_descriptor["review_queue"],
                "final_evidence": review_descriptor["final_evidence"],
                "audit": review_descriptor["audit"],
                "source": review_descriptor["source"],
                "pages": provenance_pages,
            }
        elif queue is None:
            provenance = {"schema": "kb_creator.mineru_ai_merge_provenance.v1", "status": status, "raw_comparison": str(selected_comparison), "pages": provenance_pages}
        elif fidelity_report.get("schema") in {V3_AUDIT_SCHEMA, V4_AUDIT_SCHEMA}:
            provenance = {
                "schema": "kb_creator.mineru_ai_merge_provenance.v3",
                "status": status,
                "run_identity_sha256": fidelity_report["authorities"]["run_identity_sha256"],
                "bridge_sha256": fidelity_report["authorities"]["bridge_sha256"],
                "submission": {"path": "review/validated-submission-v2/submission_inventory.json", **_identity(replay_submission), "submission_sha256": _json(replay_submission)["submission_sha256"]},
                "comparison": {"path": "outputs/03-compare-views/comparison.json", **_identity(selected_comparison)},
                "fidelity_audit": {"path": "outputs/05-fidelity-audit/audit.json", **_identity(selected_audit)},
                "pages": [{**row, "packet": f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{row['source_page']:03d}.json"} for row in provenance_pages],
                "acceptance_inferred": False,
            }
        else:
            provenance = {
                "schema": "kb_creator.mineru_ai_merge_provenance.v2",
                "status": status,
                "raw_comparison": str(selected_comparison),
                "fidelity_audit": {"path": str(selected_audit), **_identity(selected_audit)},
                "authorities": fidelity_report["authorities"],
                "pages": provenance_pages,
            }
        (stage / "MERGE_PROVENANCE.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if semantic_sidecar is not None:
            sidecar = {
                **semantic_sidecar,
                "submission_sha256": _json(replay_submission)["submission_sha256"],
                "fidelity_audit": {"path": "outputs/05-fidelity-audit/audit.json", **_identity(selected_audit)},
                "page_decisions": [
                    {"source_page": page, "sha256": hashlib.sha256(validated[page]["raw"]).hexdigest().upper()}
                    for page in domain
                ],
            }
            raw_sidecar = json.dumps(sidecar, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
            (stage / "SEMANTIC_STRUCTURE.json").write_bytes(raw_sidecar)
            if (stage / "SEMANTIC_STRUCTURE.json").read_bytes() != raw_sidecar:
                raise ValueError("semantic sidecar reopen verification failed")
        (stage / "ASSET_MANIFEST.json").write_text(json.dumps({"assets": asset_manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (stage / "OVERLAY_SELECTION.json").write_text(json.dumps({"pages": [{"source_page": page, "overlay_preference": validated[page]["decision"]["overlay_preference"]} for page in domain]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if review_descriptor is not None:
            review_manifest = {
                "schema": "kb_creator.review_draft_materialization.v1",
                "state": "verified_review_draft_candidate",
                "acceptance": "pending",
                "authority": {
                    key: review_descriptor[key]
                    for key in ("input", "final_evidence", "audit", "source", "renderer", "comparison", "review_queue")
                },
                "pages": [{"source_page": page, "decision_sha256": hashlib.sha256(validated[page]["raw"]).hexdigest().upper()}
                          for page in domain],
                "assets": asset_manifest,
            }
            (stage / "REVIEW_DRAFT_MATERIALIZATION.v1.json").write_text(
                json.dumps(review_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if output_root.exists(): output_root.rmdir()
        os.replace(stage, output_root)
        return {"status": status, "pages": len(domain), "assets": len(asset_manifest), "unique_asset_bytes": len(blobs)}
    except Exception:
        shutil.rmtree(stage, ignore_errors=True); raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", required=True, type=Path); parser.add_argument("--raw-root", required=True, type=Path)
    parser.add_argument("--decisions-root", required=True, type=Path); parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--comparison", type=Path)
    parser.add_argument("--comparison-sha256")
    parser.add_argument("--fidelity-audit", type=Path)
    parser.add_argument("--fidelity-audit-sha256")
    args = parser.parse_args(); print(json.dumps(materialize(args.bundle_root, args.raw_root, args.decisions_root, args.output_root, comparison=args.comparison, comparison_sha256=args.comparison_sha256, fidelity_audit=args.fidelity_audit, fidelity_audit_sha256=args.fidelity_audit_sha256), ensure_ascii=False)); return 0


if __name__ == "__main__": raise SystemExit(main())
