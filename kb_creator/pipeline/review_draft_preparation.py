"""Compose honest review-draft preparation from a mechanical candidate.

This module only transports selections already present in the mechanical
candidate plus explicit, book-owned overrides.  It deliberately leaves every
other mechanical hold visible, so callers cannot mistake preparation for a
reviewed semantic decision or an authorable R0 input.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .identity import canonical_bytes, file_identity, sha256_bytes
from .review_draft import ISSUES_SCHEMA, INPUT_SCHEMA, validate_review_draft_input


VIEWS = {"original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr"}
CONFIG_SCHEMA = "kb_creator.review_draft_preparation_config.v1"
REPORT_SCHEMA = "kb_creator.review_draft_preparation_report.v1"


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _read(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}") from exc


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _key(value: Any) -> tuple[str, int]:
    if not isinstance(value, dict) or set(value) != {"view", "raw_index"}:
        raise ValueError("source key has an invalid closed shape")
    if value["view"] not in VIEWS or type(value["raw_index"]) is not int or value["raw_index"] < 0:
        raise ValueError("source key is invalid")
    return value["view"], value["raw_index"]


def _config(value: Any) -> dict[int, list[dict[str, Any]]]:
    if not isinstance(value, dict) or set(value) != {"schema", "forced_selections"} or value["schema"] != CONFIG_SCHEMA:
        raise ValueError("preparation config has an invalid closed shape")
    if not isinstance(value["forced_selections"], list):
        raise ValueError("forced selections must be a list")
    result: dict[int, list[dict[str, Any]]] = {}
    seen: set[tuple[int, str, int]] = set()
    for row in value["forced_selections"]:
        fields = {"source_page", "source_key", "expected_text_sha256", "purpose", "after_ordinal"}
        if not isinstance(row, dict) or set(row) != fields:
            raise ValueError("forced selection has an invalid closed shape")
        page = row["source_page"]
        view, raw = _key(row["source_key"])
        if type(page) is not int or page < 1 or not isinstance(row["expected_text_sha256"], str) or len(row["expected_text_sha256"]) != 64:
            raise ValueError("forced selection is invalid")
        if row["purpose"] not in {"text", "structure", "asset"} or (type(row["after_ordinal"]) is not int and row["after_ordinal"] is not None):
            raise ValueError("forced selection purpose or position is invalid")
        identity = (page, view, raw)
        if identity in seen:
            raise ValueError("forced selection is duplicated")
        seen.add(identity)
        result.setdefault(page, []).append(row)
    return result


def _entry_key(entry: dict[str, Any]) -> tuple[str, int]:
    return entry.get("chosen_view"), entry.get("raw_index")


def _issue_id(page: int, code: str, index: int) -> str:
    return f"source-choice-p{page:03d}-{code}-{index:03d}"


def _choice_issues(manifest: dict[str, Any], draft_text: dict[int, str], *,
                   selected_reader_text: dict[int, dict[tuple[str, int], str]] | None = None,
                   ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Project visible differing diagnostic readings to the existing issue shape."""
    result, pending = [], []
    source_sha = manifest["authorities"]["source"]["sha256"]
    legacy_codes = {"reading_order_conflict", "three_view_content_mismatch", "ocr_text_disagreement"}
    selected_owner_codes = {"semantic_conflict", "asset_difference"}
    for index, diagnostic in enumerate(manifest.get("diagnostics", []), start=1):
        page, code, keys = diagnostic.get("page"), diagnostic.get("code"), diagnostic.get("source_keys")
        if code not in legacy_codes | selected_owner_codes or type(page) is not int or not isinstance(keys, list):
            continue
        texts = [block.get("text", "") for alternative in diagnostic.get("alternatives", []) for block in alternative.get("blocks", [])]
        visible_texts = {text for text in texts if isinstance(text, str) and text}
        # Equal readings still need structural accounting, but do not belong in
        # the text-choice queue.  Keeping this separate from a missing visible
        # excerpt prevents a reading-order diagnostic from becoming a false
        # language choice merely because it is not yet represented in markdown.
        if len(visible_texts) < 2:
            if code in legacy_codes:
                pending.append({"diagnostic_index": index - 1, "source_page": page, "code": code,
                                "reason": "structural_only_equal_readings"})
            continue
        # A source key can legitimately occur in more than one reader span
        # (for example repeated NPC statistics).  The later author-input
        # producer binds this issue to a declared semantic source occurrence;
        # it must not discard the issue merely because its prose repeats.
        if code in selected_owner_codes:
            # The new diagnostic codes gain source-choice authority only from a
            # declared reader selection.  Markdown is evidence that its exact
            # packet text is reader-visible; it never selects an owner by
            # matching prose alone.
            owners = {
                key: text for key, text in (selected_reader_text or {}).get(page, {}).items()
                if key in {_key(value) for value in keys} and text in visible_texts and text in draft_text.get(page, "")
            }
            if len(owners) != 1:
                continue
            visible = next(iter(owners.values()))
        else:
            visible = next((text for text in texts if isinstance(text, str) and text and text in draft_text.get(page, "")), None)
        if visible is None:
            if code in legacy_codes:
                pending.append({"diagnostic_index": index - 1, "source_page": page, "code": code,
                                "reason": "no visible provisional excerpt"})
            continue
        start = draft_text[page].index(visible)
        selector = [{"view": view, "raw_index": raw} for view, raw in map(_key, keys)]
        result.append({
            "issue_id": _issue_id(page, code, index), "kind": "translation_source_choice_pending",
            "reason": "Exact source views differ for one reviewed structural occurrence",
            "source_pdf_sha256": source_sha, "source_page": page,
            "source_selector": {"mechanical_diagnostic": {"code": code, "source_keys": selector}},
            "source_excerpt_en": visible, "source_excerpt_sha256": _sha(visible),
            "evidence": [{"mechanical_diagnostic_index": index - 1}],
            "candidate_span": {"character_start": start, "character_end": start + len(visible), "text_sha256": _sha(visible)},
            "state": "open",
        })
    return result, pending


def _selected_reader_text(manifest: dict[str, Any], draft_pages: list[Path]) -> dict[int, dict[tuple[str, int], str]]:
    """Read explicit reader owners and their exact packet text from draft pages."""
    run_root = Path(str(manifest.get("run_root", "")))
    if not run_root.is_dir():
        raise ValueError("mechanical candidate run root is unavailable")
    result: dict[int, dict[tuple[str, int], str]] = {}
    for path in draft_pages:
        draft = _read(path)
        page, markdown, selected = draft.get("source_page"), draft.get("markdown"), draft.get("selected_blocks")
        if type(page) is not int or not isinstance(markdown, str) or not isinstance(selected, list):
            raise ValueError("reviewed draft lacks selected reader blocks")
        blocks = _packet_blocks(run_root, page)
        owners: dict[tuple[str, int], str] = {}
        for row in selected:
            if not isinstance(row, dict):
                raise ValueError("reviewed draft selected reader block is invalid")
            purpose = row.get("purpose")
            if purpose not in {"text", "structure", "asset"}:
                raise ValueError("reviewed draft selected reader purpose is invalid")
            key = _key({"view": row.get("view"), "raw_index": row.get("raw_index")})
            if purpose == "asset":
                continue
            block = blocks.get(key)
            text = block.get("text") if isinstance(block, dict) else None
            if not isinstance(text, str):
                raise ValueError("reviewed draft selected reader source is absent from packet")
            # A repeated text/asset entry has one text owner.  Do not make
            # ownership depend on the number of selected-purpose records.
            if text and text in markdown:
                previous = owners.get(key)
                if previous is not None and previous != text:
                    raise ValueError("reviewed draft selected reader text is inconsistent")
                owners[key] = text
        result[page] = owners
    return result


def _entry_alternatives(entry: dict[str, Any], blocks: dict[tuple[str, int], dict[str, Any]], page: int) -> list[dict[str, Any]]:
    """Return closed same-entry alternatives, checked against the bound packet."""
    values = entry.get("alternatives")
    if values is None:
        return []
    if not isinstance(values, list):
        raise ValueError(f"page {page}: entry alternatives are invalid")
    result: list[dict[str, Any]] = []
    for alternative in values:
        if not isinstance(alternative, dict) or not isinstance(alternative.get("view"), str) or not isinstance(alternative.get("blocks"), list):
            raise ValueError(f"page {page}: entry alternative is invalid")
        for candidate in alternative["blocks"]:
            if not isinstance(candidate, dict) or type(candidate.get("raw_index")) is not int or not isinstance(candidate.get("text"), str):
                raise ValueError(f"page {page}: alternative block is invalid")
            key = alternative["view"], candidate["raw_index"]
            actual = blocks.get(key)
            if actual is None or actual.get("text") != candidate["text"]:
                raise ValueError(f"page {page}: alternative differs from bound packet")
            result.append({"source_key": {"view": key[0], "raw_index": key[1]},
                           "text": candidate["text"], "text_sha256": _sha(candidate["text"])})
    return result


def _packet_blocks(run_root: Path, page: int) -> dict[tuple[str, int], dict[str, Any]]:
    packet = _read(run_root / "outputs/04-visual-merge-bundle/merge_packets/pages" / f"page-{page:03d}.json")
    views = packet.get("views")
    if not isinstance(views, dict):
        raise ValueError(f"page {page}: packet views are invalid")
    result = {}
    for view, data in views.items():
        for block in data.get("blocks", []) if isinstance(data, dict) else []:
            if isinstance(block, dict) and type(block.get("raw_index")) is int:
                result[view, block["raw_index"]] = block
    return result


def _empty_source_observation(entry: dict[str, Any], blocks: dict, page: int) -> dict[str, Any]:
    """Empty OCR is evidence to inspect, never proof that a source region is blank."""
    key = _entry_key(entry)
    witnesses = {_key(row["source_key"]): row for row in _entry_alternatives(entry, blocks, page)}
    block = blocks[key]
    text = block.get("text")
    witnesses.setdefault(key, {"source_key": {"view": key[0], "raw_index": key[1]},
                               "text": text, "text_sha256": _sha(text) if isinstance(text, str) else None})
    rows = [{**row, "block_type": blocks[source].get("type"), "bbox": blocks[source].get("bbox"),
             "assets": blocks[source].get("assets", [])} for source, row in witnesses.items()]
    return {"source_page": page, "ordinal": entry.get("ordinal"),
            "source_key": {"view": key[0], "raw_index": key[1]},
            "source_content_verification": "unverified_from_empty_ocr",
            "all_three_views_empty": {source[0] for source in witnesses} == VIEWS and all(row["text"] == "" for row in rows),
            "alternate_text_available": any(row["text"] for row in rows),
            "witnesses": rows}


def _assets(page: int, view: str, raw: int, block: dict[str, Any]) -> list[dict[str, Any]]:
    paths = block.get("assets", [])
    if not isinstance(paths, list) or any(not isinstance(path, str) or not path for path in paths):
        raise ValueError(f"page {page}: packet asset reference is invalid")
    result = []
    for source_path in paths:
        digest = hashlib.sha256(source_path.encode("utf-8")).hexdigest()[:12]
        suffix = Path(source_path).suffix
        result.append({"view": view, "source_path": source_path,
                       "logical_name": f"p{page:03d}-r{raw:05d}-{digest}{suffix}", "placement": "reference_only"})
    return result


def prepare_review_draft_inputs(*, mechanical_dir: Path, config_path: Path, output_dir: Path) -> dict[str, Any]:
    """Materialize deterministic draft pages and a precise unresolved-hold report."""
    mechanical_dir, config_path, output_dir = Path(mechanical_dir), Path(config_path), Path(output_dir)
    if output_dir.exists():
        raise FileExistsError("preparation output already exists")
    manifest = _read(mechanical_dir / "mechanical_draft.json")
    if manifest.get("page_count") != len(manifest.get("pages", [])) or not isinstance(manifest.get("pages"), list):
        raise ValueError("mechanical manifest page domain is invalid")
    forced = _config(_read(config_path))
    stage = output_dir.parent / f".{output_dir.name}.staging"
    if stage.exists():
        raise FileExistsError("preparation staging directory already exists")
    try:
        run_root = Path(str(manifest.get("run_root", "")))
        if not run_root.is_dir():
            raise ValueError("mechanical candidate run root is unavailable")
        draft_text: dict[int, str] = {}; unresolved: list[dict[str, Any]] = []
        provisional_sources: list[dict[str, Any]] = []; excluded_empty: list[dict[str, Any]] = []
        page_count = 0
        for page_row in manifest["pages"]:
            page = page_row.get("source_page")
            if type(page) is not int or page < 1:
                raise ValueError("mechanical manifest page is invalid")
            candidate = _read(mechanical_dir / "pages" / f"page-{page:03d}.json")
            entries = candidate.get("entries")
            if not isinstance(entries, list):
                raise ValueError(f"page {page}: entries are invalid")
            blocks = _packet_blocks(run_root, page)
            selected: list[dict[str, Any]] = []; markdown: list[str] = []; assets: list[dict[str, Any]] = []
            remaining = list(forced.get(page, []))
            def select(view: str, raw: int, purpose: str) -> None:
                row = {"view": view, "raw_index": raw, "purpose": purpose}
                # Stage06 accepts one selected record per source unit.  An
                # asset attached to an already-selected text unit therefore
                # belongs in ``assets`` only; emitting a second purpose record
                # makes an otherwise valid composed page unmaterializable.
                if not any(item["view"] == view and item["raw_index"] == raw for item in selected):
                    selected.append(row)
            for entry in entries:
                if not isinstance(entry, dict):
                    raise ValueError(f"page {page}: entry is invalid")
                key = _entry_key(entry)
                block = blocks.get(key)
                if block is None:
                    raise ValueError(f"page {page}: selected mechanical source is absent from packet")
                emitted = entry.get("disposition") == "emitted"
                text = entry.get("reader_text") if emitted else block.get("text")
                matched = [row for row in remaining if _key(row["source_key"]) == key]
                if text is not None and not isinstance(text, str):
                    raise ValueError(f"page {page}: packet text is invalid")
                # A chosen empty block does not prove that the source component
                # is empty.  Preserve one exact, same-entry packet alternative
                # as provisional reader text.  The report retains every witness
                # and says whether a later source-choice decision is required.
                provisional = False
                if not text and not matched:
                    alternatives = _entry_alternatives(entry, blocks, page)
                    nonempty = next((row for row in alternatives if row["text"]), None)
                    if nonempty is not None:
                        select(nonempty["source_key"]["view"], nonempty["source_key"]["raw_index"], "text")
                        markdown.append(nonempty["text"])
                        nonempty_texts = {row["text"] for row in alternatives if row["text"]}
                        provisional_sources.append({
                            "source_page": page, "ordinal": entry.get("ordinal"),
                            "chosen_source_key": {"view": key[0], "raw_index": key[1]},
                            "provisional_source_key": nonempty["source_key"],
                            "provisional_text_sha256": nonempty["text_sha256"],
                            "alternatives": alternatives,
                            "text_choice_open": len(nonempty_texts) >= 2,
                        })
                        text = nonempty["text"]
                        provisional = True
                if text and not matched and not provisional:
                    select(key[0], key[1], "text")
                    markdown.append(text)
                for asset in _assets(page, key[0], key[1], block) if not matched else []:
                    select(key[0], key[1], "asset")
                    if asset not in assets: assets.append(asset)
                if matched and entry.get("disposition") == "emitted":
                    raise ValueError(f"page {page}: forced selection duplicates emitted mechanical source")
                for row in list(remaining):
                    if row["after_ordinal"] == entry.get("ordinal"):
                        view, raw = _key(row["source_key"])
                        actual = blocks.get((view, raw))
                        if actual is None or _sha(str(actual.get("text", ""))) != row["expected_text_sha256"]:
                            raise ValueError(f"page {page}: forced source text identity differs from packet")
                        select(view, raw, row["purpose"])
                        if actual.get("text"): markdown.append(actual["text"])
                        remaining.remove(row)
                if entry.get("disposition") == "excluded_empty" and not text and not block.get("assets"):
                    excluded_empty.append(_empty_source_observation(entry, blocks, page))
                elif entry.get("disposition") == "hold" and not text and not block.get("assets"):
                    unresolved.append({"source_page": page, "ordinal": entry.get("ordinal"), "source_key": {"view": key[0], "raw_index": key[1]}, "reason": "selected source has neither visible text nor asset"})
            for row in remaining:
                view, raw = _key(row["source_key"])
                actual = blocks.get((view, raw))
                if actual is None or _sha(str(actual.get("text", ""))) != row["expected_text_sha256"]:
                    raise ValueError(f"page {page}: forced source text identity differs from packet")
                select(view, raw, row["purpose"])
                if actual.get("text"): markdown.append(actual["text"])
            text = "\n\n".join(markdown)
            draft_text[page] = text
            _write(stage / "draft-pages" / f"page-{page:03d}.json", {
                "schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": page,
                "semantic_role": candidate.get("semantic_role"), "overlay_preference": "original_pipeline_txt",
                "selected_blocks": selected, "markdown": text,
                "assets": assets, "unresolved": ["source block has no visible provisional content"] if any(h["source_page"] == page for h in unresolved) else [],
                "review": {"visual_reviewed": False, "notes": "prepared from mechanical candidate; visual review remains false"},
            })
            page_count += 1
        prepared_drafts = sorted((stage / "draft-pages").glob("page-*.json"))
        issues, pending_issues = _choice_issues(
            manifest, draft_text, selected_reader_text=_selected_reader_text(manifest, prepared_drafts),
        )
        report = {"schema": REPORT_SCHEMA, "state": "blocked_by_unrenderable_source" if unresolved else "prepared_for_semantic_authoring",
                  "page_count": page_count, "mechanical_manifest_sha256": manifest.get("manifest_sha256"),
                  "forced_selection_count": sum(map(len, forced.values())), "unrenderable_source_count": len(unresolved),
                  "unrenderable_sources": unresolved, "excluded_empty_count": len(excluded_empty), "excluded_empty_sources": excluded_empty,
                  "all_three_views_empty_count": sum(row["all_three_views_empty"] for row in excluded_empty),
                  "provisional_source_count": len(provisional_sources), "provisional_sources": provisional_sources,
                  "pending_issue_count": len(pending_issues), "pending_issues": pending_issues,
                  "source_issues": {"schema": "kb_creator.review_draft_source_issues.v1", "issues": issues}}
        _write(stage / "preparation-report.json", report)
        stage.replace(output_dir)
        return report
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def _semantic_unit_index(spec_paths: list[Path], *, partition_units: dict | None = None) -> tuple[dict[tuple[int, str, int], list[str]], set[int]]:
    """Index explicit semantic units by source occurrence, never by prose text."""
    result: dict[tuple[int, str, int], list[str]] = {}
    pages: set[int] = set()
    for path in spec_paths:
        value = _read(path)
        if not isinstance(value, dict) or not isinstance(value.get("semantic_structure_profile"), str):
            raise ValueError(f"semantic spec is missing its profile: {path}")
        rows = value.get("pages")
        if not isinstance(rows, list):
            raise ValueError(f"semantic spec pages are invalid: {path}")
        for row in rows:
            page = row.get("source_page") if isinstance(row, dict) else None
            units = row.get("units") if isinstance(row, dict) else None
            if type(page) is not int or page < 1 or page in pages or not isinstance(units, list):
                raise ValueError(f"semantic spec page is missing, duplicated, or invalid: {path}")
            pages.add(page)
            for unit in units:
                if not isinstance(unit, dict) or not isinstance(unit.get("id"), str) or not unit["id"]:
                    raise ValueError(f"semantic unit is invalid on page {page}")
                sources = unit.get("source_blocks")
                if sources is None:
                    view = unit.get("view", "original_pipeline_txt")
                    raws = unit.get("raw_indices")
                    sources = [{"view": view, "raw_index": raw} for raw in raws] if isinstance(raws, list) else []
                if not isinstance(sources, list):
                    raise ValueError(f"semantic unit sources are invalid on page {page}")
                for source in sources:
                    view = source.get("view", source.get("view_id")) if isinstance(source, dict) else None
                    raw = source.get("raw_index") if isinstance(source, dict) else None
                    if view not in VIEWS or type(raw) is not int or raw < 0:
                        raise ValueError(f"semantic unit source is invalid on page {page}")
                    result.setdefault((page, view, raw), []).append(unit["id"])
                    if partition_units is not None:
                        partition_units.setdefault((page, view, raw), []).append(unit)
    return result, pages


def _declared_label_partition(units: list[dict], key: tuple[str, int], source: str) -> bool:
    """Check explicit selectors only; final author rebinds them to packet hashes."""
    if len(units) < 2 or not isinstance(source, str) or not source:
        return False
    intervals = []
    for unit in units:
        if (unit.get("kind"), unit.get("representation")) != ("label", "semantic_span"):
            return False
        sources = unit.get("source_blocks", [{"view": unit.get("view", "original_pipeline_txt"),
                                               "raw_index": raw} for raw in unit.get("raw_indices", [])])
        fragments = unit.get("source_fragments")
        if sources != [{"view": key[0], "raw_index": key[1]}] or not isinstance(fragments, list) or len(fragments) != 1:
            return False
        fragment = fragments[0]
        if not isinstance(fragment, dict) or (fragment.get("view", key[0]), fragment.get("raw_index")) != key:
            return False
        start, end = fragment.get("start"), fragment.get("end")
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(source):
            return False
        intervals.append((start, end))
    intervals.sort()
    return (intervals[0][0] == 0 and intervals[-1][1] == len(source)
            and all(left[1] == right[0] for left, right in zip(intervals, intervals[1:])))


def _bind_issue_occurrences(issues: list[dict[str, Any]], index: dict[tuple[int, str, int], list[str]], *,
                            coverage_source_to_canonical: dict[tuple[int, str, int], tuple[int, str, int]] | None = None,
                            selected_source_keys: dict[int, set[tuple[str, int]]] | None = None,
                            partition_units: dict | None = None) -> list[dict[str, Any]]:
    """Bind pending source issues to declared units without substring heuristics."""
    bound: list[dict[str, Any]] = []
    for issue in issues:
        selector = issue.get("source_selector", {}).get("mechanical_diagnostic", {}) if isinstance(issue, dict) else {}
        keys = selector.get("source_keys") if isinstance(selector, dict) else None
        if isinstance(issue, dict) and issue.get("kind") == "source_structure_role_pending":
            from .structural_role_issues import selected_source_key
            selected_key = selected_source_key(issue)
            keys = ([{"view": selected_key[0], "raw_index": selected_key[1]}]
                    if selected_key is not None else None)
        page = issue.get("source_page") if isinstance(issue, dict) else None
        if type(page) is not int or not isinstance(keys, list):
            raise ValueError("source issue lacks an exact selected source occurrence")
        units: set[str] = set()
        for key in keys:
            view, raw = _key(key)
            units.update(index.get((page, view, raw), []))
            canonical = (coverage_source_to_canonical or {}).get((page, view, raw))
            if canonical is not None:
                if (not isinstance(canonical, tuple) or len(canonical) != 3 or canonical[0] != page
                        or not isinstance(canonical[1], str) or type(canonical[2]) is not int):
                    raise ValueError("coverage canonical source occurrence is malformed")
                units.update(index.get(canonical, []))
        if len(units) != 1:
            # Ordinary prose deliberately has no semantic presentation unit.
            # Its exact selected source occurrence is carried forward for the
            # Stage05 ordered reader mapping, which is recreated by the final
            # MASTER_EN binder.  Do not choose a prose substring here.
            selected = [(view, raw) for view, raw in map(_key, keys)
                        if (view, raw) in (selected_source_keys or {}).get(page, set())]
            partition = False
            if len(selected) == 1 and len(units) > 1:
                definitions = (partition_units or {}).get((page, *selected[0]), [])
                partition = ({unit.get("id") for unit in definitions} == units
                             and len(definitions) == len(units)
                             and _declared_label_partition(definitions, selected[0], issue.get("source_excerpt_en")))
            if len(selected) == 1 and (not units or partition):
                row = dict(issue)
                row["candidate_span"] = {"source_key": {"view": selected[0][0], "raw_index": selected[0][1]},
                                         "source_page": page, "binding": "ordered_selected_source_v1"}
                bound.append(row)
                continue
            state = "missing" if not units else "ambiguous"
            raise ValueError(f"source issue {issue.get('issue_id')!r} has {state} semantic occurrence")
        row = dict(issue)
        row["candidate_span"] = {"semantic_unit_id": next(iter(units)), "source_page": page}
        bound.append(row)
    return bound


def _coverage_source_to_canonical(recomputed_coverage: Any) -> dict[tuple[int, str, int], tuple[int, str, int]]:
    """Read only the closed output of the current coverage-factory replay."""
    if recomputed_coverage is None:
        return {}
    if not isinstance(recomputed_coverage, dict) or recomputed_coverage.get("schema") != "kb_creator.review_draft_coverage_factories.v1":
        raise ValueError("coverage semantic bridge requires recomputed coverage factories")
    rows = recomputed_coverage.get("claims")
    if not isinstance(rows, list):
        raise ValueError("recomputed coverage semantic bridge is malformed")
    result = {}
    for wrapped in rows:
        row = wrapped.get("claim") if isinstance(wrapped, dict) else None
        claim = row.get("claim", row) if isinstance(row, dict) else None
        source = claim.get("source_unit") if isinstance(claim, dict) else None
        canonical = claim.get("canonical_unit") if isinstance(claim, dict) else None
        try:
            source_key = (source["source_page"], source["view_id"], source["raw_index"])
            canonical_key = (canonical["source_page"], canonical["view_id"], canonical["raw_index"])
        except (KeyError, TypeError):
            raise ValueError("recomputed coverage semantic bridge claim is malformed") from None
        if (type(source_key[0]) is not int or not isinstance(source_key[1], str) or type(source_key[2]) is not int
                or type(canonical_key[0]) is not int or not isinstance(canonical_key[1], str) or type(canonical_key[2]) is not int
                or source_key in result):
            raise ValueError("recomputed coverage semantic bridge keys are malformed")
        result[source_key] = canonical_key
    return result


def _recompute_coverage_for_author_input(mechanical_dir: Path, drafts_root: Path,
                                         factories: list[dict[str, Any]] | None) -> dict[str, Any] | None:
    if factories is None:
        return None
    manifest = _read(mechanical_dir / "mechanical_draft.json")
    run_root = Path(str(manifest.get("run_root", ""))).resolve()
    run = _read(run_root / "run.json")
    source_path = Path(str(run.get("local", {}).get("source_path", "")))
    if not run_root.is_dir() or not source_path.is_file():
        raise ValueError("coverage factory cannot resolve current run source")
    from .reviewed_draft_staging import recompute_coverage_factories
    bound = [{**factory, "draft_pages_dir": str(drafts_root.resolve())} for factory in factories]
    return recompute_coverage_factories(run_root=run_root, source_pdf=source_path,
                                        drafts_root=drafts_root, factories=bound)


def validate_review_draft_author_input(*, input_path: Path, binding_root: Path) -> dict[str, Any]:
    """Reopen every producer binding before handing its input to another stage."""
    input_path, binding_root = Path(input_path).resolve(), Path(binding_root).resolve()
    value = _read(input_path)
    record = validate_review_draft_input(value)
    for name, identity in record.value["bindings"].items():
        relative = Path(identity["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"author-input binding path is unsafe: {name}")
        path = binding_root / relative
        if not path.is_file() or file_identity(path) != {key: identity[key] for key in ("bytes", "sha256")}:
            raise ValueError(f"author-input binding identity drift: {name}")
    return {"state": "sealed_author_input", "input_sha256": record.sha256,
            "binding_count": len(record.value["bindings"]),
            "open_source_issue_count": len(record.source_issues)}


def prepare_review_draft_author_inputs(*, mechanical_dir: Path, config_path: Path,
        semantic_spec_paths: list[Path], output_dir: Path, binding_root: Path,
        reviewed_draft_pages: Path | None = None,
        coverage_factories: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Compose draft pages and a sealed review-draft author input from explicit specs.

    The supplied semantic specs remain the editorial authority. This producer
    copies their exact bytes only to provide stable author paths, binds both
    source and copied bytes, and maps open source questions by semantic source
    occurrence rather than by a unique reader-text substring.
    """
    mechanical_dir, config_path, output_dir = (Path(value).resolve() for value in
                                               (mechanical_dir, config_path, output_dir))
    binding_root = Path(binding_root).resolve()
    specs = [Path(path).resolve() for path in semantic_spec_paths]
    if not specs or len(specs) != len(set(specs)) or any(not path.is_file() for path in specs):
        raise ValueError("supply one or more unique semantic spec files")
    if output_dir.exists():
        raise FileExistsError("author-input output already exists")
    try:
        output_dir.resolve().relative_to(binding_root)
    except ValueError as exc:
        raise ValueError("author-input output escapes binding root") from exc
    stage = output_dir.parent / f".{output_dir.name}.staging"
    if stage.exists():
        raise FileExistsError("author-input staging directory already exists")
    try:
        report = prepare_review_draft_inputs(mechanical_dir=mechanical_dir, config_path=config_path,
                                             output_dir=stage / "prepared")
        if report["unrenderable_source_count"]:
            raise ValueError("author-input rejects unrenderable composed sources")
        partition_units: dict = {}
        semantic_index, semantic_pages = _semantic_unit_index(specs, partition_units=partition_units)
        draft_pages = sorted((stage / "prepared" / "draft-pages").glob("page-*.json"))
        supplied_drafts: list[Path] = []
        if reviewed_draft_pages is not None:
            supplied_drafts = sorted(Path(reviewed_draft_pages).resolve().glob("page-*.json"))
            if not supplied_drafts:
                raise ValueError("reviewed draft page input is empty")
            draft_pages = supplied_drafts
        recomputed_coverage = _recompute_coverage_for_author_input(
            mechanical_dir, Path(reviewed_draft_pages) if reviewed_draft_pages is not None else stage / "prepared" / "draft-pages",
            coverage_factories,
        )
        coverage_factory_path = None
        if coverage_factories is not None:
            coverage_factory_path = stage / "coverage-factories.json"
            _write(coverage_factory_path, [{**factory, "draft_pages_dir": str(
                (Path(reviewed_draft_pages) if reviewed_draft_pages is not None else stage / "prepared" / "draft-pages").resolve())}
                for factory in coverage_factories])
        composed_pages = {json.loads(path.read_text(encoding="utf-8")).get("source_page") for path in draft_pages}
        if composed_pages != semantic_pages:
            raise ValueError("semantic spec page domain differs from composed draft pages")
        current_draft_text = {json.loads(path.read_text(encoding="utf-8")).get("source_page"):
                              json.loads(path.read_text(encoding="utf-8")).get("markdown")
                              for path in draft_pages}
        if any(type(page) is not int or not isinstance(markdown, str)
               for page, markdown in current_draft_text.items()):
            raise ValueError("reviewed draft has invalid page text")
        current_manifest = _read(mechanical_dir / "mechanical_draft.json")
        source_issues, pending_issues = _choice_issues(
            current_manifest, current_draft_text,
            selected_reader_text=_selected_reader_text(current_manifest, draft_pages),
        )
        unsupported_pending = [row for row in pending_issues if row.get("reason") != "structural_only_equal_readings"]
        if unsupported_pending:
            raise ValueError("author-input rejects source issues without visible provisional text")
        report = {**report, "source_issues": {"schema": ISSUES_SCHEMA, "issues": source_issues},
                  "pending_issues": pending_issues}
        _write(stage / "prepared" / "preparation-report.json", report)
        selected_source_keys: dict[int, set[tuple[str, int]]] = {}
        for path in draft_pages:
            draft = _read(path)
            page = draft.get("source_page")
            selected = draft.get("selected_blocks")
            if type(page) is not int or not isinstance(selected, list):
                raise ValueError("reviewed draft lacks selected source keys")
            values = set()
            for row in selected:
                if not isinstance(row, dict) or row.get("purpose") == "asset":
                    continue
                values.add(_key({"view": row.get("view"), "raw_index": row.get("raw_index")}))
            selected_source_keys[page] = values
        issues = _bind_issue_occurrences(source_issues, semantic_index,
                                         coverage_source_to_canonical=_coverage_source_to_canonical(recomputed_coverage),
                                         selected_source_keys=selected_source_keys, partition_units=partition_units)
        copied_specs: list[Path] = []
        for number, spec in enumerate(specs):
            target = stage / "author-specs" / f"spec-{number:02d}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(spec, target)
            from .source_marker_dispositions import SourceMarkerDispositionError, copy_bound_input
            try:
                copy_bound_input(spec, target)
            except SourceMarkerDispositionError as exc:
                raise ValueError(f"source_marker_dispositions input is invalid: {exc}") from exc
            copied_specs.append(target)
        draft_paths: list[Path] = []
        for source in draft_pages:
            target = stage / "prepared" / "draft-pages" / source.name
            if source.resolve() != target.resolve():
                shutil.copyfile(source, target)
            draft_paths.append(target)
        if not draft_paths:
            raise ValueError("author-input composer produced no draft pages")
        def future(path: Path) -> Path:
            return output_dir / path.relative_to(stage)
        def record(path: Path) -> dict[str, Any]:
            target = future(path) if path.is_relative_to(stage) else path.resolve()
            try:
                relative = target.relative_to(binding_root).as_posix()
            except ValueError as exc:
                raise ValueError(f"author-input binding escapes root: {target}") from exc
            return {"path": relative, **file_identity(path)}
        bindings = {
            "candidate_manifest": record(mechanical_dir / "mechanical_draft.json"),
            "composer_config": record(config_path),
            "composer_report": record(stage / "prepared" / "preparation-report.json"),
        }
        if coverage_factory_path is not None:
            bindings["coverage_factories"] = record(coverage_factory_path)
        for number, (source, copied) in enumerate(zip(specs, copied_specs)):
            bindings[f"semantic_source_{number:02d}"] = record(source)
            bindings[f"input_{number:02d}"] = record(copied)
        for draft in draft_paths:
            bindings[f"draft_{draft.stem}"] = record(draft)
        for source in supplied_drafts:
            bindings[f"reviewed_draft_source_{source.stem}"] = record(source)
        value = {"schema": INPUT_SCHEMA, "bindings": bindings,
                 "source_issues": {"schema": ISSUES_SCHEMA, "issues": issues},
                 "unresolved_dispositions": []}
        value["input_sha256"] = sha256_bytes(canonical_bytes(value))
        validate_review_draft_input(value)
        input_path = stage / "review-draft-input.json"
        _write(input_path, value)
        stage.replace(output_dir)
        validate_review_draft_author_input(input_path=output_dir / input_path.name, binding_root=binding_root)
        return {"state": "prepared_for_review_draft_author", "preparation": report,
                "spec_paths": [str(future(path)) for path in copied_specs],
                "draft_pages": str(output_dir / "prepared" / "draft-pages"),
                "draft_input": {"path": str(output_dir / input_path.name), **file_identity(output_dir / input_path.name)},
                "open_source_issue_count": len(issues)}
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def prepare_review_draft_structural_successor(*, predecessor_input: Path, predecessor_authored: Path,
        binding_root: Path, edits_path: Path, output_dir: Path) -> dict[str, Any]:
    """Copy a sealed author input and add reviewed post-v2 structural edits.

    The caller chooses a completed predecessor.  This function intentionally
    knows no producer/job names and never derives reader changes from text.
    """
    predecessor_input, predecessor_authored, binding_root, edits_path, output_dir = (
        Path(value).resolve() for value in (predecessor_input, predecessor_authored, binding_root, edits_path, output_dir))
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("structural successor output is unavailable")
    predecessor = _read(predecessor_input)
    validate_review_draft_author_input(input_path=predecessor_input, binding_root=binding_root)
    evidence_path = predecessor_authored / "review-draft-evidence.json"
    if not predecessor_authored.is_dir() or not evidence_path.is_file():
        raise ValueError("structural successor requires completed predecessor authored evidence")
    from .review_draft import validate_review_draft_evidence
    evidence = validate_review_draft_evidence(_read(evidence_path))
    # Evidence must name the exact sealed predecessor input, not merely exist.
    if evidence.get("input_sha256") != predecessor.get("input_sha256"):
        raise ValueError("structural successor evidence does not bind predecessor input")
    for identity in evidence["authored"].values():
        path = (predecessor_authored / identity["path"]).resolve()
        if not path.is_relative_to(predecessor_authored) or not path.is_file() or file_identity(path) != {key: identity[key] for key in ("bytes", "sha256")}:
            raise ValueError("structural successor authored evidence identity is stale")
    if "decision_set" not in evidence["authored"]:
        raise ValueError("structural successor evidence lacks a decision set")
    decision_set = _read(predecessor_authored / evidence["authored"]["decision_set"]["path"])
    decision_identities: dict[int, dict[str, Any]] = {}
    for record in decision_set.get("decisions", []):
        page = record.get("source_page") if isinstance(record, dict) else None
        if type(page) is not int or page in decision_identities:
            raise ValueError("structural successor predecessor decision domain is malformed")
        decision_identities[page] = record
    edits = _read(edits_path)
    required = {"schema", "predecessor_input", "predecessor_evidence", "source_marker_dispositions", "structural_post_patches", "retained_owner_assertions", "page_units"}
    if set(edits) != required or edits.get("schema") != "kb_creator.review_draft_structural_successor.v1":
        raise ValueError("structural successor edits schema mismatch")
    if edits["predecessor_input"] != {"path": predecessor_input.name, **file_identity(predecessor_input)} or edits["predecessor_evidence"] != {"path": "review-draft-evidence.json", **file_identity(evidence_path)}:
        raise ValueError("structural successor predecessor identity is stale or foreign")
    for name in ("source_marker_dispositions",):
        identity = edits[name]
        if not isinstance(identity, dict) or set(identity) != {"path", "bytes", "sha256"}:
            raise ValueError("structural successor sidecar identity is malformed")
        sidecar = (edits_path.parent / identity["path"]).resolve()
        if not sidecar.is_file() or sidecar.parent != edits_path.parent.resolve() or file_identity(sidecar) != {"bytes": identity["bytes"], "sha256": identity["sha256"]}:
            raise ValueError("structural successor sidecar identity is stale or escapes")
    patches = edits["structural_post_patches"]
    units = edits["page_units"]
    if not isinstance(patches, list) or not isinstance(units, list) or not isinstance(edits["retained_owner_assertions"], list):
        raise ValueError("structural successor edit collections are malformed")
    by_page: dict[int, list[dict[str, Any]]] = {}
    for row in patches:
        if not isinstance(row, dict) or set(row) != {"source_page", "patches"} or type(row["source_page"]) is not int or not isinstance(row["patches"], list):
            raise ValueError("structural successor patch row is malformed")
        patch_keys = {"source_occurrences", "before", "before_sha256", "after", "after_sha256", "count"}
        occurrence_keys = {"view", "raw_index", "source_text_sha256"}
        if row["source_page"] in by_page or any(not isinstance(patch, dict) or set(patch) not in (patch_keys, patch_keys | {"interval_map"}) or not isinstance(patch["source_occurrences"], list) or not patch["source_occurrences"] or any(not isinstance(item, dict) or set(item) != occurrence_keys or not isinstance(item["view"], str) or type(item["raw_index"]) is not int or not isinstance(item["source_text_sha256"], str) or len(item["source_text_sha256"]) != 64 for item in patch["source_occurrences"]) or not isinstance(patch["before"], str) or not isinstance(patch["after"], str) or patch["before_sha256"] != sha256_bytes(patch["before"].encode("utf-8")) or patch["after_sha256"] != sha256_bytes(patch["after"].encode("utf-8")) or patch["count"] != 1 for patch in row["patches"]):
            raise ValueError("structural successor patch domain is duplicate or malformed")
        by_page[row["source_page"]] = row["patches"]
    unit_pages = {row.get("source_page") for row in units if isinstance(row, dict)}
    if len(unit_pages) != len(units) or not unit_pages.issuperset(by_page):
        raise ValueError("structural successor page-unit domain is incomplete or foreign")
    # The manifest's occurrence hashes are source authority, not decorative
    # metadata.  Reopen the same replay packets used by the completed author.
    manifest_binding = predecessor["bindings"].get("candidate_manifest")
    if not isinstance(manifest_binding, dict):
        raise ValueError("structural successor lacks a bound candidate manifest")
    run_root = Path(_read(binding_root / manifest_binding["path"])["run_root"]).resolve()
    packet_cache: dict[int, dict[str, Any]] = {}
    decisions: dict[int, dict[str, Any]] = {}

    def source_occurrence(page: int, view: str, raw_index: int, expected_hash: str) -> None:
        if type(page) is not int or page < 1 or view not in VIEWS or type(raw_index) is not int or raw_index < 0:
            raise ValueError("structural successor source occurrence is malformed")
        if page not in packet_cache:
            packet_cache[page] = _read(run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json")
        if page not in decisions:
            identity = decision_identities.get(page)
            decision_path = predecessor_authored / "pages" / f"page-{page:03d}.json"
            if (identity is None or identity.get("path") != f"pages/page-{page:03d}.json"
                    or not decision_path.is_file()
                    or file_identity(decision_path) != {key: identity[key] for key in ("bytes", "sha256")}):
                raise ValueError("structural successor predecessor page identity is stale")
            decisions[page] = _read(decision_path)
        packet, decision = packet_cache[page], decisions[page]
        blocks = packet.get("views", {}).get(view, {}).get("blocks", [])
        matches = [block for block in blocks if isinstance(block, dict) and block.get("raw_index") == raw_index]
        selected = {(item.get("view"), item.get("raw_index")) for item in decision.get("selected_blocks", [])
                    if isinstance(item, dict) and item.get("purpose") != "asset"}
        if (len(matches) != 1 or not isinstance(matches[0].get("text"), str)
                or (view, raw_index) not in selected
                or sha256_bytes(matches[0]["text"].encode("utf-8")).upper() != expected_hash.upper()):
            raise ValueError("structural successor source occurrence is stale or foreign")

    patch_keys_seen: set[tuple[int, str, int]] = set()
    for page, rows in by_page.items():
        for patch in rows:
            for occurrence in patch["source_occurrences"]:
                key = (page, occurrence["view"], occurrence["raw_index"])
                if key in patch_keys_seen:
                    raise ValueError("structural successor source occurrence is duplicated")
                patch_keys_seen.add(key)
                source_occurrence(*key, occurrence["source_text_sha256"])
            selected_order = {(item["view"], item["raw_index"]): index
                              for index, item in enumerate(decisions[page]["selected_blocks"])
                              if item.get("purpose") != "asset"}
            positions = [selected_order[(item["view"], item["raw_index"])]
                         for item in patch["source_occurrences"]]
            if positions != sorted(positions):
                raise ValueError("structural successor source occurrences are out of order")
    from .semantic_structure import apply_block_boundaries
    from .structural_projection import retained_assertion_key, validate_retained_owner_projection
    spec_prefix = ("source_choice_successor_spec-" if any(name.startswith("source_choice_successor_spec-")
                   for name in predecessor["bindings"]) else "input_")
    spec_records = [record for name, record in sorted(predecessor["bindings"].items())
                    if name.startswith(spec_prefix)]
    if not spec_records:
        raise ValueError("structural successor lacks bound predecessor specs")
    predecessor_specs = [_read(binding_root / record["path"]) for record in spec_records]
    retained_keys: set[tuple[int, str, int]] = set()
    retained_owners: set[tuple[int, str]] = set()
    for assertion in edits["retained_owner_assertions"]:
        key = retained_assertion_key(assertion)
        owner_key = (assertion["source_page"], assertion["owner_id"])
        if key in retained_keys or owner_key in retained_owners:
            raise ValueError("retained owner assertion is duplicated")
        retained_keys.add(key)
        retained_owners.add(owner_key)
        supporting_patches = [patch for patch in by_page.get(key[0], [])
                              if any((item["view"], item["raw_index"]) == key[1:]
                                     for item in patch["source_occurrences"])]
        for patch in supporting_patches:
            interval_map = patch.get("interval_map")
            copies = interval_map.get("segments", []) if isinstance(interval_map, dict) else []
            retained_segments = [index for index, segment in enumerate(copies) if isinstance(segment, dict)
                                 and segment.get("kind") == "copy" and {"view": key[1], "raw_index": key[2]}
                                 in segment.get("source_occurrences", [])]
            if (not retained_segments or any(index > 0 and copies[index - 1].get("kind") == "literal"
                                             for index in retained_segments)):
                raise ValueError("retained owner assertion receives a marker patch")
        source_occurrence(*key, assertion["source_text_sha256"])
        owners = [unit for unit in decisions[key[0]].get("semantic_structure", {}).get("units", [])
                  if isinstance(unit, dict) and unit.get("id") == assertion["owner_id"]
                  and {"view": key[1], "raw_index": key[2]} in unit.get("source_blocks", [])
                  and unit.get("kind") == "list" and unit.get("representation") == "unordered_list"]
        if len(owners) != 1:
            raise ValueError("retained owner assertion is stale or invalid")
        predecessor_units = [unit for spec in predecessor_specs
                             for page_spec in spec.get("pages", []) if page_spec.get("source_page") == key[0]
                             for unit in page_spec.get("units", []) if unit.get("id") == assertion["owner_id"]]
        successor_units = [unit for row in units if row.get("source_page") == key[0]
                           for unit in row.get("units", []) if unit.get("id") == assertion["owner_id"]]
        if len(predecessor_units) != 1 or len(successor_units) != 1:
            raise ValueError("retained owner unit is missing or changed")
        decision = decisions[key[0]]
        validate_retained_owner_projection(
            assertion=assertion, owner=owners[0], predecessor_definition=predecessor_units[0],
            successor_definition=successor_units[0], predecessor_markdown=decision["markdown"],
            effective_markdown=apply_block_boundaries(decision["markdown"], decision.get("block_boundaries")),
            default_view=decision.get("overlay_preference"), patches=by_page.get(key[0], []))
    required_retained = {(row["source_page"], unit["id"])
                         for row in units for spec in predecessor_specs
                         for page_spec in spec.get("pages", [])
                         if page_spec.get("source_page") == row["source_page"]
                         for unit in page_spec.get("units", [])
                         if unit.get("kind") == "list" and unit.get("representation") == "unordered_list"}
    if required_retained != retained_owners:
        raise ValueError("retained owner assertion domain is incomplete or foreign")
    from .structural_projection import project_structural_page, validate_ornament_source
    for page, rows in by_page.items():
        project_structural_page(decisions[page]["markdown"], rows)
    from .source_marker_dispositions import SCHEMA as MARKER_SCHEMA
    sidecar_value = _read(sidecar)
    if (not isinstance(sidecar_value, dict) or set(sidecar_value) != {"schema", "candidates", "dispositions"}
            or sidecar_value["schema"] != MARKER_SCHEMA or not isinstance(sidecar_value["candidates"], list)
            or not isinstance(sidecar_value["dispositions"], list)):
        raise ValueError("structural successor marker domain is malformed")
    from .source_marker_dispositions import _closed_occurrence
    try:
        for row in sidecar_value["candidates"]:
            _closed_occurrence(row, disposition=False)
            source_occurrence(row["source_page"], row["view"], row["raw_index"],
                              row["reader_preimage_sha256"])
        for row in sidecar_value["dispositions"]:
            _closed_occurrence(row, disposition=True)
    except ValueError as exc:
        raise ValueError("structural successor marker domain is malformed") from exc
    candidates = {(row["source_page"], row["view"], row["raw_index"]) for row in sidecar_value["candidates"]}
    dispositions = {(row["source_page"], row["view"], row["raw_index"]): row["disposition"]
                    for row in sidecar_value["dispositions"]}
    list_candidates = {key for key, value in dispositions.items() if value == "unordered_list_item"}
    non_list_candidates = {key for key, value in dispositions.items() if value == "non_list"}
    patch_groups = [{(page, item["view"], item["raw_index"]) for item in patch["source_occurrences"]}
                    for page, rows in by_page.items() for patch in rows]
    if (len(candidates) != len(sidecar_value["candidates"]) or len(dispositions) != len(sidecar_value["dispositions"])
            or candidates != set(dispositions) or not list_candidates <= patch_keys_seen
            or patch_keys_seen & non_list_candidates
            or any(not group & list_candidates for group in patch_groups)):
        raise ValueError("structural successor marker domain is incomplete or foreign")
    def source_text(page: int, view: str, raw_index: int) -> str:
        blocks = packet_cache[page]["views"][view]["blocks"]
        return next(block["text"] for block in blocks if block["raw_index"] == raw_index)
    for page, rows in by_page.items():
        current = decisions[page]["markdown"]
        for patch in rows:
            validate_ornament_source(patch, page, list_candidates, source_text, current)
            current, _ = project_structural_page(current, [patch])
    stage = output_dir.parent / f".{output_dir.name}.staging"
    if stage.exists(): raise FileExistsError("structural successor staging already exists")
    try:
        predecessor_root = predecessor_input.parent
        shutil.copytree(predecessor_root, stage)
        specs = sorted((stage / "author-specs").glob("*.json"))
        changed = set()
        for spec_path in specs:
            spec = _read(spec_path)
            # Attach the reviewed closed classification authority to every
            # copied spec so the existing author guard consumes it.
            copied_sidecar = spec_path.parent / "marker-dispositions.json"
            shutil.copyfile(sidecar, copied_sidecar)
            spec["source_marker_dispositions"] = {"path": copied_sidecar.name, **file_identity(copied_sidecar)}
            for page in spec.get("pages", []):
                page_number = page.get("source_page") if isinstance(page, dict) else None
                if page_number in by_page:
                    page["structural_post_patches"] = [{key: patch[key] for key in ("before", "after", "count")} for patch in by_page[page_number]]; changed.add(page_number)
                matching = [row for row in units if row["source_page"] == page_number]
                if matching:
                    page["units"] = matching[0].get("units"); changed.add(page_number)
            _write(spec_path, spec)
        if changed != set(by_page) | unit_pages:
            raise ValueError("structural successor page does not exist in copied specs")
        bindings = dict(predecessor["bindings"])
        for name, record in list(bindings.items()):
            source = (binding_root / record["path"]).resolve()
            if source.is_relative_to(predecessor_root):
                copied = stage / source.relative_to(predecessor_root)
                target = output_dir / copied.relative_to(stage)
                bindings[name] = {"path": target.relative_to(binding_root).as_posix(), **file_identity(copied)}
        def bound(path: Path) -> dict[str, Any]:
            return {"path": path.relative_to(binding_root).as_posix(), **file_identity(path)}
        bindings.update({"structural_predecessor_input": bound(predecessor_input), "structural_predecessor_evidence": bound(predecessor_authored / "review-draft-evidence.json"), "structural_edits": bound(edits_path)})
        successor = {"schema": INPUT_SCHEMA, "bindings": bindings, "source_issues": predecessor["source_issues"], "unresolved_dispositions": predecessor["unresolved_dispositions"]}
        successor["input_sha256"] = sha256_bytes(canonical_bytes(successor)); validate_review_draft_input(successor)
        _write(stage / predecessor_input.name, successor)
        stage.replace(output_dir)
        validate_review_draft_author_input(input_path=output_dir / predecessor_input.name, binding_root=binding_root)
        return {"state": "sealed_structural_successor", "input": {"path": str(output_dir / predecessor_input.name), **file_identity(output_dir / predecessor_input.name)}, "affected_pages": sorted(changed)}
    finally:
        if stage.exists(): shutil.rmtree(stage)


def compose_structural_role_issue_successor(*, input_path: Path, binding_root: Path,
        run_root: Path, authored_preview_root: Path, destination: Path) -> dict[str, Any]:
    """Seal a successor review input carrying exact open role disagreements.

    ``authored_preview_root`` is diagnostic evidence only.  Its selected page
    decisions are rechecked against the archived replay packets and comparison;
    it cannot grant a future-output authority to its own producer.
    """
    from .structural_role_issues import (SELECTOR_KEY, STRUCTURAL_KIND, load_structural_preview,
                                        pending_structural_conflicts, _selected)
    from kb_creator.scripts.materialize_mineru_ai_merge import structural_conflict_locator
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _v3_page_context

    input_path, binding_root = Path(input_path).resolve(), Path(binding_root).resolve()
    destination, preview = Path(destination).resolve(), Path(authored_preview_root).resolve()
    if destination.exists() or not destination.parent.is_dir():
        raise ValueError("structural successor destination is unavailable")
    value = _read(input_path)
    record = validate_review_draft_input(value)
    validate_review_draft_author_input(input_path=input_path, binding_root=binding_root)
    checked = load_structural_preview(Path(run_root), preview)
    comparison_path = checked["paths"]["comparison"]
    comparison = checked["comparison"]
    run = _read(Path(run_root) / "run.json")
    source_sha = run.get("source", {}).get("sha256")
    pages = checked["decisions"]
    def bound(path: Path) -> dict[str, Any]:
        path = path.resolve()
        try:
            relative = path.relative_to(binding_root).as_posix()
        except ValueError as error:
            raise ValueError("structural successor binding escapes root") from error
        return {"path": relative, **file_identity(path)}
    issues = list(record.source_issues)
    seen_ids = {issue["issue_id"] for issue in issues}
    owned = set()
    pending_by_page: dict[int, list] = {}
    for page, conflict, units in pending_structural_conflicts(pages, checked["packets"], comparison,
            checked["reference_proof_keys"], checked["split_structure_proof_keys"],
            checked["visual_assertions"]):
        pending_by_page.setdefault(page, []).append((conflict, units))
    for page_number, decision in sorted(pages.items()):
        if page_number not in pending_by_page:
            continue
        packet = checked["packets"][page_number]
        selected = _selected(decision, packet)
        errors: list[str] = []
        context = _v3_page_context(page_number, packet, decision, checked["geometry"], errors)
        if errors:
            raise ValueError("preview selected source mapping failed: " + "; ".join(errors))
        grouped: dict[tuple[str, str, int], list[dict[str, Any]]] = {}
        for conflict, units in pending_by_page[page_number]:
            if len(units) != 1:
                raise ValueError("structural conflict requires one exact provisional reader occurrence")
            selected_unit = units[0]
            locator = structural_conflict_locator(page_number, conflict)
            if locator in owned:
                raise ValueError("preview comparison locator is not unique")
            owned.add(locator)
            key = (conflict.get("kind"), selected_unit["view"], selected_unit["raw_index"])
            grouped.setdefault(key, []).append({"pair_name": locator[1], "semantic_conflict_index": locator[2], "record_sha256": locator[3]})
        for (kind, view, raw), rows in grouped.items():
            selected_unit = selected[(view, raw)]; block = selected_unit
            matches = [row for row in context["mappings"]
                       if (row["unit"]["view_id"], row["unit"]["raw_index"]) == (view, raw)]
            if len(matches) != 1:
                raise ValueError("structural source has no exact ordered reader occurrence")
            excerpt = block.get("text")
            if not isinstance(excerpt, str) or not excerpt:
                raise ValueError("structural selected source has no exact text excerpt")
            issue_id = f"source-structure-p{page_number:03d}-{kind}-{view}-{raw:06d}"
            if issue_id in seen_ids:
                raise ValueError("structural successor issue ID collision")
            seen_ids.add(issue_id)
            issues.append({
                "issue_id": issue_id, "kind": STRUCTURAL_KIND,
                "reason": "Source views disagree on the role of one exact selected occurrence",
                "source_pdf_sha256": source_sha, "source_page": page_number,
                "source_selector": {SELECTOR_KEY: {
                    "selected_source_key": {"view": view, "raw_index": raw},
                    "provisional_selection_purpose": selected_unit["_selection_purpose"],
                    "provisional_block_type": block.get("type"), "comparison_records": rows}},
                "source_excerpt_en": excerpt, "source_excerpt_sha256": sha256_bytes(excerpt.encode("utf-8")),
                "evidence": [{"kind": "comparison_conflict_record_v1", "comparison_binding": "comparison",
                              "predecessor_decision_set_binding": "structural_preview_decision_set"}],
                "candidate_span": {"binding": "ordered_selected_source_v1", "source_page": page_number,
                                   "source_key": {"view": view, "raw_index": raw}}, "state": "open"})
    preview_set = preview / "decision_set.json"
    if not preview_set.is_file():
        raise ValueError("preview decision set is missing")
    successor = {"schema": INPUT_SCHEMA, "bindings": {**record.value["bindings"],
                 "comparison": bound(comparison_path), "structural_preview_decision_set": bound(preview_set)},
                 "source_issues": {"schema": ISSUES_SCHEMA, "issues": issues},
                 # Preserve the predecessor disposition list byte-for-value.
                 "unresolved_dispositions": record.value["unresolved_dispositions"]}
    successor["input_sha256"] = sha256_bytes(canonical_bytes(successor))
    validate_review_draft_input(successor)
    with destination.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(successor, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    validate_review_draft_author_input(input_path=destination, binding_root=binding_root)
    return {"state": "sealed_structural_role_successor", "input": {"path": str(destination), **file_identity(destination)},
            "structural_issue_count": len(issues) - len(record.source_issues), "preserved_lexical_issue_count": len(record.source_issues)}
