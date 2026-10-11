"""Read-only proof that reviewed Markdown tables retain their source cells."""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


_VIEWS = {"original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr"}
_DELIMITER = re.compile(r"^:?-{3,}:?$")


class _SourceTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.header_rows: list[bool] = []
        self._cell: list[str] | None = None
        self._cell_is_header: bool | None = None
        self._in_row = False
        self._table_depth = 0
        self.invalid = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self._table_depth += 1
            if self._table_depth != 1:
                self.invalid = True
        elif tag == "tr":
            if self._table_depth != 1 or self._in_row or self._cell is not None:
                self.invalid = True
            self.rows.append([])
            self._in_row = True
            self._cell_is_header = None
        elif tag in {"td", "th"}:
            if self._table_depth != 1 or not self._in_row or self._cell is not None:
                self.invalid = True
                return
            if any(name in {"rowspan", "colspan"} for name, _ in attrs):
                self.invalid = True
            self._cell = []
            self._cell_is_header = tag == "th"

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"}:
            if self._cell is None or self._cell_is_header != (tag == "th") or not self.rows:
                self.invalid = True
                return
            self.rows[-1].append("".join(self._cell))
            if len(self.rows[-1]) == 1:
                self.header_rows.append(bool(self._cell_is_header))
            elif self.header_rows[-1] != bool(self._cell_is_header):
                self.invalid = True
            self._cell = None
        elif tag == "tr":
            if not self._in_row or self._cell is not None:
                self.invalid = True
            self._in_row = False
        elif tag == "table":
            if self._table_depth != 1 or self._in_row or self._cell is not None:
                self.invalid = True
            self._table_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)
        elif data.strip():
            self.invalid = True


def verify_table_evidence(
    run_root: Path, packet: dict, decision: dict, page_spec: dict, bindings: list[dict],
) -> list[dict]:
    """Verify every editable reviewed table against exact source-table metadata.

    The function reads only the supplied run tree. It returns one compact
    identity record per table and raises ``ValueError`` for any stale, missing,
    ambiguous, or structurally lossy binding.
    """
    root = Path(run_root).resolve()
    if not root.is_dir():
        raise ValueError("table evidence run root is not a directory")
    source_page = _source_page(decision, page_spec)
    selected_tables = _selected_tables(packet, decision, page_spec)
    if not isinstance(bindings, list):
        raise ValueError("table evidence bindings must be a list")
    by_key: dict[tuple[str, int], dict] = {}
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) not in (
            {"view", "raw_index", "metadata", "table_body_sha256"},
            {"view", "raw_index", "metadata", "table_body_sha256", "header_review"},
        ):
            raise ValueError("table evidence binding has an invalid closed shape")
        view, raw_index = binding["view"], binding["raw_index"]
        if view not in _VIEWS or type(raw_index) is not int or raw_index < 0 or not _sha(binding["table_body_sha256"]):
            raise ValueError("table evidence binding identity is invalid")
        key = view, raw_index
        if key in by_key:
            raise ValueError("table evidence repeats a binding")
        by_key[key] = binding
    if set(by_key) != set(selected_tables):
        raise ValueError("table evidence bindings must exactly cover selected editable tables")

    results: list[dict] = []
    for key, unit in selected_tables.items():
        binding = by_key[key]
        metadata_path = _metadata_path(root, key[0], binding["metadata"])
        metadata = _read_metadata(metadata_path)
        if key[1] >= len(metadata):
            raise ValueError("table evidence raw index is outside metadata")
        source = metadata[key[1]]
        if not isinstance(source, dict) or source.get("type") != "table" or source.get("page_idx") != source_page - 1:
            raise ValueError("table evidence source type, view, or page does not match")
        body = source.get("table_body")
        if not isinstance(body, str) or _digest(body) != binding["table_body_sha256"]:
            raise ValueError("table evidence source body hash mismatch")
        source_rows, html_has_header = _parse_source_table(body)
        source_has_header, header_basis, header_review = _header_treatment(
            binding.get("header_review"), html_has_header,
        )
        markdown_rows = _markdown_rows(decision["markdown"], unit)
        _compare_rows(source_rows, source_has_header, markdown_rows)
        columns = len(source_rows[0])
        results.append({
            "view": key[0], "raw_index": key[1], "source_page": source_page,
            "row_count": len(source_rows), "column_count": columns,
            "cell_count": sum(len(row) for row in source_rows),
            "source_has_header_row": source_has_header,
            "header_basis": header_basis,
            "header_review": header_review,
        })
    return results


def _source_page(decision: Mapping[str, Any], page_spec: Mapping[str, Any]) -> int:
    page = decision.get("source_page")
    if type(page) is not int or page < 1 or page_spec.get("source_page") != page:
        raise ValueError("table evidence page identity is invalid")
    if not isinstance(decision.get("markdown"), str) or not isinstance(decision.get("selected_blocks"), list):
        raise ValueError("table evidence decision is invalid")
    if not isinstance(page_spec.get("units"), list):
        raise ValueError("table evidence page spec is invalid")
    return page


def _selected_tables(packet: Mapping[str, Any], decision: Mapping[str, Any], page_spec: Mapping[str, Any]) -> dict[tuple[str, int], dict]:
    views = packet.get("views")
    if not isinstance(views, Mapping):
        raise ValueError("table evidence packet lacks views")
    blocks: dict[tuple[str, int], Mapping[str, Any]] = {}
    for view, data in views.items():
        if view not in _VIEWS or not isinstance(data, Mapping) or not isinstance(data.get("blocks"), list):
            raise ValueError("table evidence packet view is invalid")
        for block in data["blocks"]:
            if not isinstance(block, Mapping) or type(block.get("raw_index")) is not int:
                raise ValueError("table evidence packet block is invalid")
            key = view, block["raw_index"]
            if key in blocks:
                raise ValueError("table evidence packet repeats a raw block")
            blocks[key] = block
    selected: set[tuple[str, int]] = set()
    for row in decision["selected_blocks"]:
        if not isinstance(row, Mapping) or not {"view", "raw_index", "purpose"} <= set(row):
            raise ValueError("table evidence selected block is invalid")
        key = row["view"], row["raw_index"]
        if key not in blocks or row["purpose"] not in {"text", "structure", "asset"}:
            raise ValueError("table evidence selected block is stale")
        if row["purpose"] in {"text", "structure"}:
            selected.add(key)
    tables: dict[tuple[str, int], dict] = {}
    for unit in page_spec["units"]:
        if not isinstance(unit, dict):
            raise ValueError("table evidence unit is invalid")
        if unit.get("representation") != "table":
            continue
        view, raw_indices = unit.get("view"), unit.get("raw_indices")
        if view not in _VIEWS or not isinstance(raw_indices, list) or not raw_indices or any(type(raw_index) is not int for raw_index in raw_indices):
            raise ValueError("table evidence table unit is invalid")
        keys = [(view, raw_index) for raw_index in raw_indices]
        if any(key not in blocks for key in keys):
            raise ValueError("table evidence table unit has a stale source block")
        source_table_keys = [key for key in keys if blocks[key].get("type") == "table"]
        # A semantic Markdown table may be projected from ordinary source text
        # (for example, stat values plus labelled prose). This verifier proves
        # only MinerU table artifacts, whose HTML body has a metadata identity.
        if not source_table_keys:
            continue
        if len(keys) != 1 or len(source_table_keys) != 1:
            raise ValueError("table evidence source-table unit must name exactly one raw block")
        key = source_table_keys[0]
        if key not in selected:
            raise ValueError("editable table is not selected as text or structure")
        if key in tables:
            raise ValueError("table evidence repeats a table unit")
        tables[key] = unit
    return tables


def _metadata_path(root: Path, view: str, identity: Any) -> Path:
    if not isinstance(identity, dict) or set(identity) != {"path", "bytes", "sha256"}:
        raise ValueError("table evidence metadata identity has an invalid shape")
    relative = identity["path"]
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("table evidence metadata path is invalid")
    pure = PurePosixPath(relative)
    prefix = PurePosixPath("outputs") / "02-mineru-three-view" / "views" / view / "artifacts"
    if pure.is_absolute() or ".." in pure.parts or pure.parts[:len(prefix.parts)] != prefix.parts:
        raise ValueError("table evidence metadata path is outside the approved artifacts directory")
    candidate = root.joinpath(*pure.parts)
    _reject_reparse(root, candidate)
    if not candidate.is_file():
        raise ValueError("table evidence metadata is not a regular file")
    actual = {"bytes": candidate.stat().st_size, "sha256": _digest(candidate.read_bytes())}
    if actual != {"bytes": identity["bytes"], "sha256": identity["sha256"]}:
        raise ValueError("table evidence metadata identity mismatch")
    return candidate


def _reject_reparse(root: Path, candidate: Path) -> None:
    resolved_root, resolved = root.resolve(), candidate.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("table evidence metadata path escapes the run root") from exc
    current = root
    for part in candidate.relative_to(root).parts:
        current /= part
        attributes = getattr(os.stat(current, follow_symlinks=False), "st_file_attributes", 0)
        if current.is_symlink() or attributes & 0x400:
            raise ValueError("table evidence metadata path contains a reparse point")


def _read_metadata(path: Path) -> list[Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("table evidence metadata is unreadable JSON") from exc
    if not isinstance(value, list):
        raise ValueError("table evidence source_content_list must be a list")
    return value


def _parse_source_table(body: str) -> tuple[list[list[str]], bool]:
    parser = _SourceTableParser()
    parser.feed(body)
    parser.close()
    rows = parser.rows
    if parser.invalid or parser._table_depth or parser._in_row or parser._cell is not None or not rows:
        raise ValueError("table evidence source HTML is unsupported")
    if not rows[0] or any(not row or len(row) != len(rows[0]) for row in rows):
        raise ValueError("table evidence source table topology is invalid")
    if any(parser.header_rows) and (not parser.header_rows[0] or any(parser.header_rows[1:])):
        raise ValueError("table evidence source header topology is unsupported")
    return rows, parser.header_rows[0]


def _header_treatment(value: Any, html_has_header: bool) -> tuple[bool, str, dict[str, Any] | None]:
    if value is None:
        return html_has_header, "html_th", None
    if not isinstance(value, dict) or set(value) != {"source_header_rows", "rationale"}:
        raise ValueError("table evidence header review has an invalid closed shape")
    rows, rationale = value["source_header_rows"], value["rationale"]
    if type(rows) is not int or rows not in {0, 1} or not isinstance(rationale, str) or not rationale.strip():
        raise ValueError("table evidence header review is invalid")
    if html_has_header and rows != 1:
        raise ValueError("table evidence header review contradicts source th markup")
    return bool(rows), "reviewed_header", {"source_header_rows": rows, "rationale": rationale}


def _markdown_rows(markdown: str, unit: Mapping[str, Any]) -> list[list[str]]:
    start, end = unit.get("start_line"), unit.get("end_line")
    lines = markdown.splitlines()
    if type(start) is not int or type(end) is not int or start < 1 or end < start or end > len(lines):
        raise ValueError("table evidence Markdown span is stale")
    table_lines = lines[start - 1:end]
    if len(table_lines) < 3:
        raise ValueError("table evidence Markdown table is incomplete")
    rows = [_parse_markdown_row(line) for line in table_lines]
    if any(row is None for row in rows):
        raise ValueError("table evidence Markdown table row is invalid")
    if not all(_DELIMITER.fullmatch(cell) for cell in rows[1]):
        raise ValueError("table evidence Markdown delimiter is invalid")
    width = len(rows[0])
    if width == 0 or len(rows[1]) != width or any(len(row) != width for row in rows[2:]):
        raise ValueError("table evidence Markdown table topology is invalid")
    return [rows[0], *rows[2:]]


def _parse_markdown_row(line: str) -> list[str] | None:
    if not line.startswith("|") or not line.endswith("|"):
        return None
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in line[1:-1]:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append(html.unescape("".join(current).strip(" \t")))
            current = []
        else:
            current.append(char)
    if escaped:
        current.append("\\")
    cells.append(html.unescape("".join(current).strip(" \t")))
    return cells


def _compare_rows(source_rows: list[list[str]], source_has_header: bool, markdown_rows: list[list[str]]) -> None:
    if source_has_header:
        expected = source_rows
    else:
        if any(cell != "" for cell in markdown_rows[0]):
            raise ValueError("headerless source table requires a fully empty Markdown transport header")
        expected = [["" for _ in source_rows[0]], *source_rows]
    if markdown_rows != expected:
        raise ValueError("table evidence Markdown cells differ from source")


def _digest(value: bytes | str) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest().upper()


def _sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9A-F]{64}", value) is not None
