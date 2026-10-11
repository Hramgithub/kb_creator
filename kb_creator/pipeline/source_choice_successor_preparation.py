"""Prepare a sealed R1 review-draft successor from a source-choice ledger.

The source-choice ledger is the sole authority for a lexical replacement.  This
producer deliberately does not update the pre-R1 ledger and does not infer any
visual review result.  It copies the R0 author inputs into a new immutable
directory, changes only ledger-resolved lexical occurrences, and seals a new
review-draft input which binds the predecessor, queue, and ledger.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .identity import canonical_bytes, file_identity, sha256_bytes
from .review_draft import INPUT_SCHEMA, ISSUES_SCHEMA, validate_review_draft_input
from .review_draft_preparation import validate_review_draft_author_input
from .source_choice_translation import PENDING_KIND, SourceChoiceError, verify_ledger, verify_ledger_v2


class SourceChoiceSuccessorPreparationError(ValueError):
    """The R0 input cannot be turned into an exact R1 successor."""


def _read(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SourceChoiceSuccessorPreparationError(f"cannot read {path}: {error}") from error


def _portable_identity(path: Path, root: Path, label: str) -> dict[str, Any]:
    path = path.resolve()
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as error:
        raise SourceChoiceSuccessorPreparationError(f"{label} escapes binding root") from error
    return {"path": relative, **file_identity(path)}


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _key(value: Any) -> tuple[str, int]:
    if (not isinstance(value, dict) or set(value) != {"view", "raw_index"}
            or not isinstance(value["view"], str) or not value["view"]
            or type(value["raw_index"]) is not int):
        raise SourceChoiceSuccessorPreparationError("source-choice key is malformed")
    return value["view"], value["raw_index"]


def _replace_once(text: str, before: str, after: str, label: str) -> str:
    if not isinstance(text, str) or not isinstance(before, str) or not before or not isinstance(after, str):
        raise SourceChoiceSuccessorPreparationError(f"{label} has invalid lexical text")
    if text.count(before) != 1:
        raise SourceChoiceSuccessorPreparationError(f"{label} does not contain one exact predecessor reading")
    return text.replace(before, after)


def _choice_context(ledger_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        verified = verify_ledger_v2(ledger_path) if ledger_path.name.endswith(".v2.json") else verify_ledger(ledger_path)
    except SourceChoiceError as error:
        raise SourceChoiceSuccessorPreparationError(f"source-choice ledger is invalid: {error}") from error
    ledger = _read(Path(verified["ledger"]))
    queue = _read(Path(verified["queue"]))
    return ledger, queue


def _verify_caller_author_inputs(predecessor: dict[str, Any], binding_root: Path,
                                 draft_pages: Path, specs: list[Path]) -> None:
    """Require caller inputs to be the predecessor's sealed author inputs."""
    bindings = predecessor.get("bindings")
    if not isinstance(bindings, dict):
        raise SourceChoiceSuccessorPreparationError("predecessor author bindings are malformed")

    def expected(prefix: str) -> list[tuple[str, Path, dict[str, Any]]]:
        rows = [(name, identity) for name, identity in bindings.items() if name.startswith(prefix)]
        if not rows:
            raise SourceChoiceSuccessorPreparationError(f"predecessor lacks {prefix} bindings")
        result = []
        for name, identity in sorted(rows):
            if not isinstance(identity, dict) or set(identity) != {"path", "bytes", "sha256"} or not isinstance(identity["path"], str):
                raise SourceChoiceSuccessorPreparationError(f"predecessor {name} identity is malformed")
            path = (binding_root / identity["path"]).resolve()
            if not path.is_file() or file_identity(path) != {key: identity[key] for key in ("bytes", "sha256")}:
                raise SourceChoiceSuccessorPreparationError(f"predecessor {name} identity is stale")
            result.append((name, path, identity))
        return result

    expected_specs = expected("input_")
    supplied_specs = [path.resolve() for path in specs]
    if supplied_specs != [path for _, path, _ in expected_specs]:
        raise SourceChoiceSuccessorPreparationError("caller semantic specs differ from predecessor sealed input order")
    if any(file_identity(path) != {key: identity[key] for key in ("bytes", "sha256")}
           for path, (_, _, identity) in zip(supplied_specs, expected_specs)):
        raise SourceChoiceSuccessorPreparationError("caller semantic spec identity is stale")

    expected_drafts = expected("draft_page-")
    supplied_drafts = sorted(draft_pages.glob("page-*.json"))
    if [path.resolve() for path in supplied_drafts] != [path for _, path, _ in expected_drafts]:
        raise SourceChoiceSuccessorPreparationError("caller draft page domain differs from predecessor sealed inputs")
    if any(file_identity(path) != {key: identity[key] for key in ("bytes", "sha256")}
           for path, (_, _, identity) in zip(supplied_drafts, expected_drafts)):
        raise SourceChoiceSuccessorPreparationError("caller draft page identity is stale")


def _shift_line_selectors(row: dict[str, Any], before_markdown: str, before: str, after: str) -> None:
    """Keep existing semantic line selectors aligned after one exact patch."""
    offset = before_markdown.index(before)
    start = before_markdown[:offset].count("\n") + 1
    end = start + before.count("\n")
    delta = after.count("\n") - before.count("\n")
    if not delta:
        return
    for unit in row.get("units", []):
        if not isinstance(unit, dict):
            continue
        line_start, line_end = unit.get("start_line"), unit.get("end_line")
        if type(line_start) is not int or type(line_end) is not int:
            continue
        if line_start > end:
            unit["start_line"] = line_start + delta
            unit["end_line"] = line_end + delta
        elif line_end >= start:
            # A containing or exact unit remains anchored at its first line,
            # while its endpoint follows the lexical replacement's line delta.
            unit["end_line"] = line_end + delta


def _patch_text_selectors(row: dict[str, Any], before: str, after: str) -> None:
    """Update only exact textual unit selectors; prose may have no unit."""
    for unit in row.get("units", []):
        if not isinstance(unit, dict):
            continue
        for field in ("start", "end"):
            value = unit.get(field)
            if isinstance(value, str) and value.count(before) == 1:
                unit[field] = value.replace(before, after)


def _patch_spec(spec: dict[str, Any], page: int, key: tuple[str, int], before: str, after: str,
                ledger_path: Path, issue_id: str, alternative_id: str, markdown: str) -> str:
    pages = spec.get("pages")
    if not isinstance(pages, list):
        raise SourceChoiceSuccessorPreparationError("semantic spec pages are malformed")
    rows = [row for row in pages if isinstance(row, dict) and row.get("source_page") == page]
    if len(rows) != 1:
        raise SourceChoiceSuccessorPreparationError(f"page {page}: semantic spec page is absent or duplicated")
    row = rows[0]
    corrections = row.setdefault("linguistic_source_choice_corrections", [])
    if not isinstance(corrections, list):
        raise SourceChoiceSuccessorPreparationError(f"page {page}: source-choice corrections are malformed")
    selector = {"ledger": str(ledger_path.resolve()), "issue_id": issue_id,
                "alternative_id": alternative_id, "view": key[0], "raw_index": key[1],
                "before": before, "after": after}
    if selector in corrections:
        raise SourceChoiceSuccessorPreparationError(f"page {page}: duplicate source-choice correction")
    corrections.append(selector)
    if not isinstance(row.get("units", []), list):
        raise SourceChoiceSuccessorPreparationError(f"page {page}: semantic spec units are malformed")
    # Lexical choices are bound to the selected source occurrence, not to a
    # presentation unit.  Many valid body paragraphs deliberately have none.
    _patch_text_selectors(row, before, after)
    _shift_line_selectors(row, markdown, before, after)
    patches = row.setdefault("patches", [])
    if not isinstance(patches, list):
        raise SourceChoiceSuccessorPreparationError(f"page {page}: semantic spec patches are malformed")
    patches.append({"before": before, "after": after, "count": 1})
    return _replace_once(markdown, before, after, f"page {page} successor patch")


def prepare_source_choice_successor(*, input_path: Path, binding_root: Path, ledger_path: Path,
                                    draft_pages: Path, spec_paths: list[Path], output_dir: Path) -> dict[str, Any]:
    """Create an R1 author input and copies of drafts/specs from a sealed R0 input.

    Resolved choices are removed from the open issue list and represented by an
    exact ``linguistic_source_choice`` selector.  Retained choices and every
    unrelated source issue remain byte-for-value in the R1 input.
    """
    input_path = Path(input_path).resolve()
    binding_root = Path(binding_root).resolve()
    ledger_path = Path(ledger_path).resolve()
    draft_pages = Path(draft_pages).resolve()
    specs = [Path(path).resolve() for path in spec_paths]
    output_dir = Path(output_dir).resolve()
    if output_dir.exists() or not output_dir.parent.is_dir() or not draft_pages.is_dir() or not specs:
        raise SourceChoiceSuccessorPreparationError("successor output or R0 inputs are unavailable")
    try:
        output_dir.relative_to(binding_root)
    except ValueError as error:
        raise SourceChoiceSuccessorPreparationError("successor output escapes binding root") from error
    predecessor = _read(input_path)
    record = validate_review_draft_input(predecessor)
    validate_review_draft_author_input(input_path=input_path, binding_root=binding_root)
    _verify_caller_author_inputs(record.value, binding_root, draft_pages, specs)
    ledger, queue = _choice_context(ledger_path)
    queue_path = Path(ledger["queue"]["path"]).resolve()
    queue_rows = {row.get("issue_id"): row for row in queue.get("choices", []) if isinstance(row, dict)}
    ledger_rows = {row.get("issue_id"): row for row in ledger.get("source_choices", []) if isinstance(row, dict)}
    if set(queue_rows) != set(ledger_rows):
        raise SourceChoiceSuccessorPreparationError("verified source-choice queue and ledger disagree")
    original_drafts = sorted(draft_pages.glob("page-*.json"))
    if not original_drafts:
        raise SourceChoiceSuccessorPreparationError("R0 draft pages are absent")
    stage = output_dir.parent / f".{output_dir.name}.staging"
    if stage.exists():
        raise FileExistsError("source-choice successor staging directory already exists")
    try:
        copied_drafts: dict[int, tuple[Path, dict[str, Any]]] = {}
        for source in original_drafts:
            value = _read(source)
            page = value.get("source_page")
            if type(page) is not int or page in copied_drafts:
                raise SourceChoiceSuccessorPreparationError("R0 draft page domain is malformed")
            target = stage / "draft-pages" / source.name
            _write(target, value)
            copied_drafts[page] = (target, value)
        copied_specs: list[tuple[Path, dict[str, Any]]] = []
        for number, source in enumerate(specs):
            value = _read(source)
            target = stage / "author-specs" / f"spec-{number:02d}.json"
            _write(target, value)
            from .source_marker_dispositions import SourceMarkerDispositionError, copy_bound_input
            try:
                copy_bound_input(source, target)
            except SourceMarkerDispositionError as exc:
                raise SourceChoiceSuccessorPreparationError(
                    f"source_marker_dispositions input is invalid: {exc}"
                ) from exc
            copied_specs.append((target, value))
        issues = list(record.source_issues)
        by_issue = {issue["issue_id"]: issue for issue in issues}
        resolved: set[str] = set()
        retained: dict[str, dict[str, Any]] = {}
        v2_page_choices: dict[int, list[tuple[dict[str, Any], dict[str, Any]]]] = {}
        page_markdown = {page: draft.get("markdown") for page, (_, draft) in copied_drafts.items()}
        if any(not isinstance(value, str) for value in page_markdown.values()):
            raise SourceChoiceSuccessorPreparationError("R0 draft page markdown is malformed")
        for issue_id, ledger_row in ledger_rows.items():
            queue_row = queue_rows[issue_id]
            issue = by_issue.get(issue_id)
            if issue is None or issue.get("kind") != PENDING_KIND:
                raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: R0 pending source issue is absent")
            if issue.get("source_selector") != queue_row.get("source_selector"):
                raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: R0 issue selector differs from sealed queue")
            if ledger_row.get("disposition") == "unresolved_semantic":
                reason, label = ledger_row.get("reason"), ledger_row.get("label")
                if not isinstance(reason, str) or not reason.strip() or not isinstance(label, str) or not label:
                    raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: retained semantic ledger reason or label is invalid")
                retained[issue_id] = {**issue, "kind": "semantic_source_uncertainty",
                    "reason": f"Retained source choice ({label}): {reason}",
                    "evidence": [*issue["evidence"], {"kind": "source_choice_ledger_retention_v1",
                        "ledger_binding": "source_choice_ledger", "reason": reason, "label": label}]}
                continue
            if ledger_row.get("disposition") != "selected_alternative":
                raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: ledger disposition is invalid")
            if ledger.get("schema") == "kb_creator.source_choice_ledger.v2":
                page = queue_row.get("source_page")
                anchor = ledger_row.get("reader_anchor", {})
                locator = anchor.get("selected_source_key") if isinstance(anchor, dict) else None
                if locator is None and isinstance(anchor, dict) and isinstance(anchor.get("selected_source_keys"), list):
                    keys = anchor["selected_source_keys"]
                    locator = keys[0] if len(keys) == 1 else None
                if type(page) is not int or not isinstance(locator, dict):
                    raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: v2 reader anchor is invalid")
                _key(locator)
                draft_entry = copied_drafts.get(page)
                if draft_entry is None:
                    raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: R0 page draft is absent")
                eligible = [(path, spec) for path, spec in copied_specs
                            if sum(1 for row in spec.get("pages", []) if isinstance(row, dict) and row.get("source_page") == page) == 1]
                if len(eligible) != 1:
                    raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: semantic spec page is absent or ambiguous")
                row = next(row for row in eligible[0][1]["pages"] if row.get("source_page") == page)
                before = ledger_row.get("r0_reader_span", {}).get("text_sha256")
                reader_preimage = queue_row.get("reader_projection", {}).get("reader_text")
                reader_successor = ledger_row.get("intended_reader_successor", {}).get("text")
                if (not isinstance(reader_preimage, str) or not isinstance(reader_successor, str)
                        or before != sha256_bytes(reader_preimage.encode())):
                    raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: v2 reader replacement is invalid")
                adapter = ledger_row.get("reader_adapter")
                if isinstance(adapter, dict) and adapter.get("policy") == "reviewed_corrected_reader_retention_v1":
                    replay = ledger_row.get("raw_reader_replay")
                    proof = replay.get("presentation_proof") if isinstance(replay, dict) else None
                    if (reader_preimage != reader_successor or not isinstance(proof, dict)
                            or replay.get("presentation_policy") != "reviewed_block_correction_strong_display_v1"
                            or {key: adapter.get("anchor_source_locator", {}).get(key) for key in ("view", "raw_index")} != {key: locator.get(key) for key in ("view", "raw_index")}
                            or adapter.get("anchor_raw_text_sha256") != ledger_row.get("chosen_raw_alternative", {}).get("text_sha256")
                            or adapter.get("reader_text_sha256") != sha256_bytes(reader_preimage.encode())
                            or adapter.get("presentation_proof_sha256") != sha256_bytes(canonical_bytes(proof))):
                        raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: retained corrected reader adapter is stale")
                v2_page_choices.setdefault(page, []).append((queue_row, ledger_row))
                rows = row.setdefault("linguistic_source_choice_corrections", [])
                rows.append({"ledger": str(ledger_path.resolve()), "issue_id": issue_id,
                             "alternative_id": ledger_row["alternative_id"], "view": locator["view"], "raw_index": locator["raw_index"]})
                _write(eligible[0][0], eligible[0][1]); resolved.add(issue_id)
                continue
            page = queue_row.get("source_page")
            before = issue.get("source_excerpt_en")
            alternative_id = ledger_row.get("alternative_id")
            alternative = next((item for item in queue_row.get("alternatives", [])
                                if isinstance(item, dict) and item.get("alternative_id") == alternative_id), None)
            after = alternative.get("text") if isinstance(alternative, dict) else None
            if type(page) is not int or not isinstance(before, str):
                raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: ledger predecessor text is invalid")
            if ledger_row.get("predecessor_span", {}).get("text_sha256") != sha256_bytes(before.encode()):
                raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: ledger predecessor text is invalid")
            if not isinstance(after, str) or ledger_row.get("intended_successor_replacement", {}).get("text_sha256") != sha256_bytes(after.encode()):
                raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: ledger replacement text is invalid")
            draft_entry = copied_drafts.get(page)
            if draft_entry is None:
                raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: R0 page draft is absent")
            draft_path, draft = draft_entry
            source_keys = {_key(row) for row in queue_row.get("source_selector", {}).get("mechanical_diagnostic", {}).get("source_keys", [])}
            selected = {_key({"view": row.get("view"), "raw_index": row.get("raw_index")})
                        for row in draft.get("selected_blocks", []) if isinstance(row, dict) and row.get("purpose") != "asset"}
            matching = source_keys & selected
            if len(matching) != 1:
                raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: R0 draft has no unique selected source occurrence")
            key = next(iter(matching))
            # The author starts from an immutable source-selection draft.  The
            # successor spec owns the one lexical patch; pre-applying it here
            # would make the frozen author apply the same change twice.
            _replace_once(draft.get("markdown"), before, after, f"choice {issue_id} draft")
            eligible = [(path, spec) for path, spec in copied_specs
                        if sum(1 for row in spec.get("pages", []) if isinstance(row, dict) and row.get("source_page") == page) == 1]
            if len(eligible) != 1:
                raise SourceChoiceSuccessorPreparationError(f"choice {issue_id}: semantic spec page is absent or ambiguous")
            page_markdown[page] = _patch_spec(eligible[0][1], page, key, before, after, ledger_path,
                                               issue_id, alternative_id, page_markdown[page])
            _write(eligible[0][0], eligible[0][1])
            resolved.add(issue_id)
        # Rebind each page once from its sealed authored R0 coordinates. Applying
        # one text lookup per choice could move a different equal occurrence or
        # accumulate line shifts against an already-mutated selector.
        from .source_choice_coverage_successor import _open_record
        from .source_choice_selectors import rebind_unit_selectors, rebind_prose_selectors, rebind_prose_role_selectors
        from .source_choice_slice import SourceSlice
        for page, page_choices in v2_page_choices.items():
            master_root = Path(queue["review_master"]["path"]).parent
            decision_record = page_choices[0][0]["raw_reader_replay"]["decision"]
            if any(choice["raw_reader_replay"]["decision"] != decision_record for choice, _ in page_choices):
                raise SourceChoiceSuccessorPreparationError("page choices disagree on predecessor decision")
            decision = _open_record(decision_record, master_root)
            edits = [SourceSlice(chosen["r0_reader_span"]["character_start"],
                                 chosen["r0_reader_span"]["character_end"],
                                 chosen["r0_reader_span"]["text_sha256"],
                                 chosen["intended_reader_successor"]["text"])
                     for _, chosen in page_choices]
            targets = [(path, spec, i) for path, spec in copied_specs for i, row in enumerate(spec.get("pages", []))
                       if isinstance(row, dict) and row.get("source_page") == page]
            if len(targets) != 1:
                raise SourceChoiceSuccessorPreparationError("successor semantic spec page is not unique")
            path, spec, index = targets[0]
            spec["pages"][index] = rebind_unit_selectors(spec["pages"][index], decision["markdown"],
                decision.get("semantic_structure", {}).get("units", []), edits,
                markdown_sha256=sha256_bytes(decision["markdown"].encode()))
            spec["pages"][index] = rebind_prose_selectors(spec["pages"][index], decision["markdown"],
                decision.get("reviewed_prose_bindings_v1", []), edits,
                markdown_sha256=sha256_bytes(decision["markdown"].encode()))
            spec["pages"][index] = rebind_prose_role_selectors(spec["pages"][index], decision["markdown"],
                decision.get("reviewed_prose_roles_v1", []), edits,
                markdown_sha256=sha256_bytes(decision["markdown"].encode()))
            _write(path, spec)
        successor_issues = [retained.get(issue["issue_id"], issue) for issue in issues if issue["issue_id"] not in resolved]
        def future(path: Path) -> Path:
            return output_dir / path.relative_to(stage)
        def future_identity(path: Path, label: str) -> dict[str, Any]:
            target = future(path)
            try:
                relative = target.relative_to(binding_root).as_posix()
            except ValueError as error:
                raise SourceChoiceSuccessorPreparationError(f"{label} escapes binding root") from error
            return {"path": relative, **file_identity(path)}
        bindings = dict(record.value["bindings"])
        # The original factory and its source transcription remain unchanged.
        # Seal only the exact claim selectors whose reader interval a resolved
        # composite v2 choice consumes; Stage05 will rederive this disposition
        # against fresh claims before treating it as R1 coverage.
        coverage_record = bindings.get("coverage_factories")
        if coverage_record is not None:
            if not isinstance(coverage_record, dict) or set(coverage_record) != {"path", "bytes", "sha256"}:
                raise SourceChoiceSuccessorPreparationError("coverage factory binding is malformed")
            coverage_path = binding_root / coverage_record["path"]
            if not coverage_path.is_file() or file_identity(coverage_path) != {key: coverage_record[key] for key in ("bytes", "sha256")}:
                raise SourceChoiceSuccessorPreparationError("coverage factory binding identity drift")
            from kb_creator.scripts.author_reviewed_semantic_decisions import _recompute_composer_coverage
            candidate_report = _read(Path(queue["candidate"]["path"]) / "mechanical_draft.json")
            original_claims = _recompute_composer_coverage(record.value, binding_root,
                Path(candidate_report["run_root"]), draft_pages) or []
            from .source_choice_coverage_successor import make_dispositions
            dispositions = make_dispositions(predecessor_input=input_path, ledger_path=ledger_path, claims=original_claims)
            dispositions_path = stage / "source-choice-coverage-dispositions.json"
            _write(dispositions_path, dispositions)
            bindings["source_choice_coverage_dispositions"] = future_identity(dispositions_path, "coverage successor dispositions")
        bindings.update({
            "source_choice_predecessor": _portable_identity(input_path, binding_root, "predecessor input"),
            "source_choice_ledger": _portable_identity(ledger_path, binding_root, "source-choice ledger"),
            "source_choice_queue": _portable_identity(queue_path, binding_root, "source-choice queue"),
        })
        for target, _ in copied_specs:
            bindings[f"source_choice_successor_{target.stem}"] = future_identity(target, "successor semantic spec")
        for target, _ in copied_drafts.values():
            bindings[f"source_choice_successor_{target.stem}"] = future_identity(target, "successor draft")
        successor = {"schema": INPUT_SCHEMA, "bindings": bindings,
                     "source_issues": {"schema": ISSUES_SCHEMA, "issues": successor_issues},
                     "unresolved_dispositions": record.value["unresolved_dispositions"]}
        successor["input_sha256"] = sha256_bytes(canonical_bytes(successor))
        validate_review_draft_input(successor)
        _write(stage / "review-draft-input.json", successor)
        stage.replace(output_dir)
        output_input = output_dir / "review-draft-input.json"
        validate_review_draft_author_input(input_path=output_input, binding_root=binding_root)
        return {"state": "sealed_source_choice_successor", "input": {"path": str(output_input), **file_identity(output_input)},
                "draft_pages": str(output_dir / "draft-pages"), "spec_paths": [str(future(target)) for target, _ in copied_specs],
                "resolved_choice_count": len(resolved), "retained_source_issue_count": len(successor_issues),
                "retained_semantic_choice_count": len(retained)}
    finally:
        if stage.exists():
            shutil.rmtree(stage)
