"""Bind reviewed page translations to an existing five-step language task.

This module deliberately maps only exact, line-bounded source units.  It is a
reusable adapter for reviewed bilingual pages, not a translation engine.
"""
from __future__ import annotations

import hashlib
import json
import re
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from . import five_step_language as language
from kb_creator.scripts import scenario_master_ru as legacy


class BilingualDraftBindingError(ValueError):
    pass


MARKER = re.compile(r"^<!-- source-page-(\d{3}) -->$")
PLACEHOLDER = re.compile(r"\{\{asset:([^{}]+)\}\}")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def _lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BilingualDraftBindingError(f"cannot read JSON: {path}") from error
    if not isinstance(value, dict):
        raise BilingualDraftBindingError(f"JSON object required: {path}")
    return value


def _identity(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()}


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _seal(value: dict[str, Any], key: str) -> dict[str, Any]:
    result = dict(value)
    result[key] = hashlib.sha256(_canonical(result)).hexdigest().upper()
    return result


def _verify_task(task: dict[str, Any], task_path: Path) -> None:
    unsigned = {key: value for key, value in task.items() if key != "task_sha256"}
    schema = task.get("schema")
    if schema not in {"kb_creator.five_step_language_draft_task.v2", "kb_creator.five_step_language_draft_task.v3"} or task.get("task_sha256") != hashlib.sha256(_canonical(unsigned)).hexdigest().upper():
        raise BilingualDraftBindingError("draft task seal/schema mismatch")
    master = Path(str(task.get("master_en_path", "")))
    record = task.get("master_en")
    if not master.is_file() or record != {"path": "MASTER_EN.md", **_identity(master)}:
        raise BilingualDraftBindingError("draft task MASTER_EN identity mismatch")
    for name in ('glossary', 'source_spans'):
        path = Path(str(task.get(name + '_path', '')))
        if not path.is_file() or task.get(name) != {'path': path.name, **_identity(path)}:
            raise BilingualDraftBindingError(f'draft task {name} identity mismatch')
    units = task.get('units')
    if not isinstance(units, list) or not units:
        raise BilingualDraftBindingError('draft task has no units')
    seen = set()
    for row in units:
        if (not isinstance(row, dict) or not isinstance(row.get('unit_id'), str)
                or not isinstance(row.get('source_text'), str) or not row['source_text']
                or row.get('source_hash') != _sha(row['source_text']) or row['unit_id'] in seen):
            raise BilingualDraftBindingError('draft task unit identity mismatch')
        seen.add(row['unit_id'])
    if schema == "kb_creator.five_step_language_draft_task.v3":
        try:
            canonical_master = language._source(task, "master_en")
            language._source(task, "glossary")
            spans_path, _ = language._source_spans(canonical_master)
            if task.get("source_spans") != {"path": "EN_SOURCE_SPANS.json", **language._id(spans_path, canonical_master.parent)}:
                raise language.FiveStepLanguageError("task source spans differ from canonical authority")
            language._verified_unit_context(task, canonical_master)
            fresh, _ = language._units(canonical_master, task["max_batch_chars"])
            if [language._unit(row) for row in fresh] != units:
                raise language.FiveStepLanguageError("task units differ from canonical source segmentation")
        except (KeyError, TypeError, ValueError, language.FiveStepLanguageError) as error:
            raise BilingualDraftBindingError("draft task v3 canonical source context is invalid") from error


def _asset_paths(manifest_path: Path) -> dict[str, str]:
    manifest = _read(manifest_path)
    result: dict[str, str] = {}
    for row in manifest.get("assets", []):
        if not isinstance(row, dict) or not isinstance(row.get("logical_name"), str) or not isinstance(row.get("stored_path"), str):
            raise BilingualDraftBindingError("asset manifest row is malformed")
        path = row['stored_path']
        if (row["logical_name"] in result or not path or ':' in path or '\\' in path
                or PurePosixPath(path).is_absolute() or '..' in PurePosixPath(path).parts):
            raise BilingualDraftBindingError("asset manifest mapping is unsafe or ambiguous")
        result[row["logical_name"]] = row["stored_path"]
    return result


def _transform_assets(text: str, assets: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        try:
            return assets[match.group(1)]
        except KeyError as error:
            raise BilingualDraftBindingError("asset placeholder lacks manifest mapping") from error
    return PLACEHOLDER.sub(replace, text)


def _pages(master: str) -> dict[int, str]:
    parts = re.split(r"(?m)^(<!-- source-page-(\d{3}) -->)\n?", master)
    result: dict[int, str] = {}
    if parts[0].strip():
        raise BilingualDraftBindingError('MASTER_EN has content before first page marker')
    for index in range(1, len(parts), 3):
        page = int(parts[index + 1])
        if page in result:
            raise BilingualDraftBindingError("MASTER_EN has duplicate page marker")
        # Markers are independent formal task units and must be copied
        # verbatim; reviewed page payload begins after its marker.
        result[page] = _lf(parts[index + 2]).strip("\n") + "\n"
    if not result:
        raise BilingualDraftBindingError("MASTER_EN lacks page markers")
    if list(result) != list(range(1, len(result) + 1)):
        raise BilingualDraftBindingError('MASTER_EN page markers are not contiguous')
    return result


def _page_inputs(pages_root: Path, assets: dict[str, str]) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for path in sorted(pages_root.glob("page*.json")):
        row = _read(path)
        page = row.get("source_page")
        if type(page) is not int or page < 1 or page in result:
            raise BilingualDraftBindingError("reviewed page identity is malformed or duplicate")
        required = {"source_page", "source_markdown_sha256", "en_markdown", "ru_markdown", "unresolved"}
        if set(row) != required or not isinstance(row["en_markdown"], str) or not isinstance(row["ru_markdown"], str) or not isinstance(row["unresolved"], list):
            raise BilingualDraftBindingError("reviewed page shape is malformed")
        if _sha(row["en_markdown"]) != row["source_markdown_sha256"].upper():
            raise BilingualDraftBindingError("reviewed page source markdown hash mismatch")
        result[page] = {**row, "post_en": _lf(_transform_assets(row["en_markdown"], assets)), "post_ru": _lf(_transform_assets(row["ru_markdown"], assets)), "path": path}
    return result


def _unit_bounds(source: str, page_en: str, cursor: int) -> tuple[int, int]:
    start = page_en.find(source, cursor)
    if start < 0 or page_en[cursor:start].strip():
        raise BilingualDraftBindingError("source unit cannot be located in its page")
    return start, start + len(source)


def _line_bounded_unit(source: str, page_en: str, page_ru: str, cursor: int) -> tuple[str, int]:
    start, end = _unit_bounds(source, page_en, cursor)
    line_start = page_en.rfind("\n", 0, start) + 1
    line_end = page_en.find("\n", end)
    if line_end < 0:
        line_end = len(page_en)
    omitted_left, omitted_right = page_en[line_start:start], page_en[end:line_end]
    if (omitted_left and any(char not in " \t" for char in omitted_left)) or (omitted_right and any(char not in " \t" for char in omitted_right)):
        raise BilingualDraftBindingError("source unit is not line bounded")
    # Two final spaces are Markdown hard-break syntax.  Do not silently turn
    # an omitted semantic delimiter into ordinary formatting whitespace.
    if len(omitted_left) >= 4 or '\t' in omitted_left:
        raise BilingualDraftBindingError('source unit omits Markdown indentation')
    if len(omitted_right.expandtabs(4)) >= 2:
        raise BilingualDraftBindingError("source unit omits Markdown hard-break whitespace")
    before = page_en[:start].count("\n")
    count = source.count("\n") + 1
    en_lines = page_en.splitlines()
    ru_lines = page_ru.splitlines()
    if len(en_lines) != len(ru_lines) or "\n".join(en_lines[before:before + count]).strip(" \t") != source.strip(" \t"):
        raise BilingualDraftBindingError("source unit line topology is ambiguous")
    return "\n".join(ru_lines[before:before + count]), end


def _overrides(path: Path | None, task_units: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    value = _read(path)
    rows = value.get("units")
    if value.get("schema") != "kb_creator.bilingual_explicit_unit_translations.v1" or not isinstance(rows, list):
        raise BilingualDraftBindingError("explicit translation authority shape mismatch")
    task_by_id = {row["unit_id"]: row for row in task_units}
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"unit_id", "source_hash", "ru_text", "unresolved"} or not isinstance(row["unit_id"], str) or not isinstance(row["source_hash"], str) or not isinstance(row["ru_text"], str) or not isinstance(row["unresolved"], list):
            raise BilingualDraftBindingError("explicit translation row shape mismatch")
        expected = task_by_id.get(row["unit_id"])
        if expected is None or expected["source_hash"] != row["source_hash"]:
            raise BilingualDraftBindingError("explicit translation unit identity mismatch")
        if row["unit_id"] in result:
            raise BilingualDraftBindingError("explicit translation duplicate unit")
        if MARKER.fullmatch(expected['source_text']):
            raise BilingualDraftBindingError('page markers cannot have translation overrides')
        if not row['ru_text'].strip():
            raise BilingualDraftBindingError('explicit translation is empty')
        result[row["unit_id"]] = row
    return result


def _topology_mismatch(row: dict[str, Any]) -> bool:
    en_lines, ru_lines = row['post_en'].splitlines(), row['post_ru'].splitlines()
    return (len(en_lines) != len(ru_lines)
            or any(bool(en.strip()) != bool(ru.strip()) for en, ru in zip(en_lines, ru_lines)))


def _plain_prose(text: str) -> bool:
    signature = legacy._structure_signature(text)
    return (bool(text.strip())
            and all(kind == 'text' for kind in signature['line_classes'])
            and not signature['page_markers'] and not signature['anchors']
            and not signature['image_targets'] and not signature['link_targets']
            and not signature['mechanics'] and not any(signature['hard_breaks'])
            and not any(signature['explicit_br'])
            and not any(signature['emphasis_delimiters']))


def _page_units(task_units: list[dict[str, Any]], pages: set[int]) -> dict[int, list[dict[str, Any]]]:
    result = {page: [] for page in pages}
    current: int | None = None
    for unit in task_units:
        marker = MARKER.fullmatch(unit['source_text'])
        if marker:
            current = int(marker.group(1))
        elif current in result:
            result[current].append(unit)
    return result


def _page_mapping_authority(path: Path | None, *, task_path: Path, task: dict[str, Any],
                            asset_manifest: Path, reviewed: dict[int, dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    """Validate reviewed positional mappings before they can waive topology holds."""
    if path is None:
        return {}
    value = _read(path)
    unsigned = {key: item for key, item in value.items() if key != 'mapping_sha256'}
    if (value.get('schema') != 'kb_creator.bilingual_explicit_page_mappings.v1'
            or value.get('mapping_sha256') != hashlib.sha256(_canonical(unsigned)).hexdigest().upper()
            or set(value) != {'schema', 'task', 'asset_manifest', 'pages', 'mapping_sha256'}
            or not isinstance(value.get('pages'), list)):
        raise BilingualDraftBindingError('explicit page mapping seal/schema mismatch')
    if value['task'] != {'path': task_path.name, **_identity(task_path)}:
        raise BilingualDraftBindingError('explicit page mapping task identity mismatch')
    if value['asset_manifest'] != {'path': asset_manifest.name, **_identity(asset_manifest)}:
        raise BilingualDraftBindingError('explicit page mapping asset identity mismatch')
    mismatched = {page for page, row in reviewed.items() if _topology_mismatch(row)}
    if len(value['pages']) != len(mismatched):
        raise BilingualDraftBindingError('explicit page mapping coverage mismatch')
    expected = _page_units(task['units'], set(reviewed))
    result: dict[str, dict[str, dict[str, Any]]] = {}
    seen_pages: set[int] = set()
    for page_row in value['pages']:
        if not isinstance(page_row, dict) or set(page_row) != {'source_page', 'reviewed_page', 'post_en_sha256', 'post_ru_sha256', 'units'}:
            raise BilingualDraftBindingError('explicit page mapping page shape mismatch')
        page = page_row.get('source_page')
        if type(page) is not int or page not in mismatched or page in seen_pages or not isinstance(page_row['units'], list):
            raise BilingualDraftBindingError('explicit page mapping page coverage mismatch')
        seen_pages.add(page); reviewed_row = reviewed[page]
        if (page_row['reviewed_page'] != {'path': reviewed_row['path'].name, **_identity(reviewed_row['path'])}
                or page_row['post_en_sha256'] != _sha(reviewed_row['post_en'])
                or page_row['post_ru_sha256'] != _sha(reviewed_row['post_ru'])):
            raise BilingualDraftBindingError('explicit page mapping reviewed page identity mismatch')
        units = expected[page]
        if len(page_row['units']) != len(units):
            raise BilingualDraftBindingError('explicit page mapping unit coverage mismatch')
        page_bytes = reviewed_row['post_ru'].encode('utf-8')
        cursor = 0; page_result: dict[str, dict[str, Any]] = {}
        for mapping, unit in zip(page_row['units'], units):
            required = {'unit_id', 'source_hash', 'ru_span', 'ru_slice_sha256', 'ru_text', 'mode', 'reason', 'unresolved'}
            if not isinstance(mapping, dict) or set(mapping) != required or mapping.get('unit_id') != unit['unit_id'] or mapping.get('source_hash') != unit['source_hash']:
                raise BilingualDraftBindingError('explicit page mapping unit identity/order mismatch')
            span = mapping['ru_span']
            if (not isinstance(span, dict) or set(span) != {'start_byte', 'end_byte'}
                    or type(span.get('start_byte')) is not int or type(span.get('end_byte')) is not int
                    or not 0 <= span['start_byte'] < span['end_byte'] <= len(page_bytes)
                    or span['start_byte'] < cursor):
                raise BilingualDraftBindingError('explicit page mapping UTF-8 span is invalid')
            try:
                raw = page_bytes[span['start_byte']:span['end_byte']].decode('utf-8')
            except UnicodeDecodeError as error:
                raise BilingualDraftBindingError('explicit page mapping UTF-8 span boundary is invalid') from error
            if page_bytes[cursor:span['start_byte']].decode('utf-8').strip():
                raise BilingualDraftBindingError('explicit page mapping has non-whitespace RU gap')
            cursor = span['end_byte']
            if (not isinstance(mapping['ru_text'], str) or mapping['ru_slice_sha256'] != _sha(raw)
                    or mapping['unresolved'] != [] or mapping['mode'] not in {'exact_slice', 'reviewed_plain_text_whitespace'}):
                raise BilingualDraftBindingError('explicit page mapping unit payload is invalid')
            if mapping['mode'] == 'exact_slice':
                if mapping['ru_text'] != raw.strip() or mapping['reason'] not in {'', None}:
                    raise BilingualDraftBindingError('explicit page mapping exact slice differs')
            else:
                if (not isinstance(mapping['reason'], str) or not mapping['reason'].strip()
                        or not _plain_prose(unit['source_text']) or not _plain_prose(raw)
                        or not _plain_prose(mapping['ru_text'])
                        or ' '.join(raw.split()) != ' '.join(mapping['ru_text'].split())
                        or legacy._structure_signature(unit['source_text']) != legacy._structure_signature(mapping['ru_text'])):
                    raise BilingualDraftBindingError('explicit page mapping plain-text whitespace mode is invalid')
            page_result[unit['unit_id']] = mapping
        if page_bytes[cursor:].decode('utf-8').strip():
            raise BilingualDraftBindingError('explicit page mapping has non-whitespace RU suffix')
        result[str(page)] = page_result
    if seen_pages != mismatched:
        raise BilingualDraftBindingError('explicit page mapping coverage mismatch')
    return result


def bind(task_path: Path, template_path: Path, pages_root: Path, asset_manifest: Path, output_root: Path, *, explicit_translations: Path | None = None) -> dict[str, Any]:
    task_path, template_path, pages_root, asset_manifest, output_root = (path.resolve() for path in (task_path, template_path, pages_root, asset_manifest, output_root))
    explicit_translations = explicit_translations.resolve() if explicit_translations is not None else None
    if output_root.exists() or not output_root.parent.is_dir():
        raise BilingualDraftBindingError("output root must be absent below an existing parent")
    task = _read(task_path); _verify_task(task, task_path)
    template = _read(template_path)
    if template.get("schema") != "kb_creator.five_step_language_draft_submission.v2" or template.get("task") != {"path": task_path.name, **_identity(task_path)} or template.get("master_en") != task["master_en"] or template.get("glossary") != task["glossary"]:
        raise BilingualDraftBindingError("draft template authority mismatch")
    master = Path(task["master_en_path"]); assets = _asset_paths(asset_manifest)
    master_pages, reviewed = _pages(_lf(master.read_text(encoding="utf-8"))), _page_inputs(pages_root, assets)
    if set(master_pages) != set(reviewed):
        raise BilingualDraftBindingError("reviewed page coverage mismatch")
    for page, row in reviewed.items():
        if row["post_en"] != master_pages[page]:
            raise BilingualDraftBindingError(f"posttransform EN differs from formal MASTER page {page:03d}")
    authority_schema = None if explicit_translations is None else _read(explicit_translations).get('schema')
    page_mappings = _page_mapping_authority(explicit_translations, task_path=task_path, task=task,
                                             asset_manifest=asset_manifest, reviewed=reviewed) if authority_schema == 'kb_creator.bilingual_explicit_page_mappings.v1' else {}
    overrides = {} if authority_schema == 'kb_creator.bilingual_explicit_page_mappings.v1' else _overrides(explicit_translations, task["units"])
    for page, row in reviewed.items():
        if _topology_mismatch(row) and str(page) not in page_mappings:
            # Every nonempty RU line must be covered by a source-bearing line;
            # otherwise text in a source paragraph gap could silently vanish.
            row['unresolved'] = [*row['unresolved'], 'binding_hold:page blank-line topology differs']
    rows, methods, holds, cursors, current_page = [], [], [], {page: 0 for page in master_pages}, None
    holds.extend({'source_page': page, 'code': 'unresolved_page', 'detail': row['unresolved']}
                 for page, row in reviewed.items() if row['unresolved'])
    for unit in task.get("units", []):
        if not isinstance(unit, dict) or not isinstance(unit.get("unit_id"), str) or not isinstance(unit.get("source_text"), str):
            raise BilingualDraftBindingError("task unit is malformed")
        marker = MARKER.fullmatch(unit["source_text"])
        override = overrides.get(unit["unit_id"])
        if marker:
            if current_page is not None and master_pages[current_page][cursors[current_page]:].strip():
                raise BilingualDraftBindingError('task omits source page content')
            expected_page = 1 if current_page is None else current_page + 1
            if int(marker.group(1)) != expected_page or expected_page not in master_pages:
                raise BilingualDraftBindingError('task page marker order mismatch')
            current_page = int(marker.group(1)); ru = unit["source_text"]
            unresolved, method = [], "page_marker_verbatim"
        else:
            if current_page is None:
                raise BilingualDraftBindingError("task unit occurs before first page marker")
            _, end = _unit_bounds(_lf(unit['source_text']), master_pages[current_page], cursors[current_page])
            page_mapping = page_mappings.get(str(current_page), {}).get(unit['unit_id'])
            if page_mapping is not None:
                ru, unresolved = page_mapping['ru_text'], []
                method = ('explicit_page_exact_slice' if page_mapping['mode'] == 'exact_slice'
                          else 'explicit_page_plain_text_whitespace')
            elif override is not None:
                ru, unresolved, method = override['ru_text'], list(override['unresolved']), 'explicit_unit_translation'
            else:
                try:
                    ru, _ = _line_bounded_unit(_lf(unit["source_text"]), master_pages[current_page], reviewed[current_page]["post_ru"], cursors[current_page])
                    unresolved, method = [], "verifiable_page_projection"
                except BilingualDraftBindingError as error:
                    ru, unresolved, method = "", [f"binding_hold:{error}"], "unsupported_boundary"
            cursors[current_page] = end
            unresolved.extend(reviewed[current_page]['unresolved'])
            if not ru.strip() and not unresolved:
                unresolved.append('binding_hold:empty translation')
        if unresolved:
            holds.append({'unit_id': unit['unit_id'], 'source_hash': unit['source_hash'],
                          'code': method if method == 'unsupported_boundary' else 'unresolved_translation',
                          'detail': unresolved})
        rows.append({"unit_id": unit["unit_id"], "source_hash": unit["source_hash"], "ru_text": ru, "unresolved": unresolved})
        methods.append({"unit_id": unit["unit_id"], "method": method})
    if current_page != len(master_pages) or any(text[cursors[page]:].strip() for page, text in master_pages.items()):
        raise BilingualDraftBindingError('task does not cover complete MASTER_EN')
    if [(row.get("unit_id"), row.get('source_hash')) for row in template.get("units", [])] != [(row["unit_id"], row['source_hash']) for row in rows]:
        raise BilingualDraftBindingError("draft template unit topology mismatch")
    submission = _seal({"schema": "kb_creator.five_step_language_draft_submission.v2", "task": {"path": task_path.name, **_identity(task_path)}, "master_en": task["master_en"], "glossary": task["glossary"], "units": rows}, "submission_sha256")
    report = {"schema": "kb_creator.bilingual_draft_binding.v1", "state": "blocked" if holds else "candidate_ready_for_draft_submission", "task": {"path": str(task_path), **_identity(task_path)}, "pages": len(reviewed), "units": len(rows), "holds": holds, "binding_methods": methods, "explicit_translation_authority": None if explicit_translations is None else {"path": str(explicit_translations), **_identity(explicit_translations)}, "acceptance_inferred": False}
    report['inputs'] = {'template': _identity(template_path), 'asset_manifest': _identity(asset_manifest),
                        'pages': [{'source_page': page, **_identity(row['path'])} for page, row in sorted(reviewed.items())]}
    staging = Path(tempfile.mkdtemp(prefix=f'.{output_root.name}.', dir=output_root.parent))
    try:
        if authority_schema == 'kb_creator.bilingual_explicit_page_mappings.v1':
            archived = staging / 'explicit-page-mapping.json'
            shutil.copyfile(explicit_translations, archived)
            report['archived_explicit_page_mapping'] = {'path': archived.name, **_identity(archived)}
        for name, value in [('draft.submission.json', submission), ('binding-report.json', report)]:
            (staging / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.rename(staging, output_root)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return report
