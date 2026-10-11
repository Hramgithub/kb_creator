"""Finalize a reviewed MinerU reconstruction into a deterministic review package."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Iterable

from pypdf import PdfReader, PdfWriter

VIEWS = ("original_hybrid", "original_pipeline_ocr", "raster_hybrid")
GATE_NAMES = ("source_identity", "page_coverage", "role_partition", "text_ocr_provenance", "required_entity_closure", "asset_closure", "no_open_blockers")
MARKER = re.compile(r"<!-- source-page-(\d{3}) -->")
HANDOUT_LINE = re.compile(r"^\s*\*Handout\s+#(\d+(?:[a-z])?)\*\s*$", re.I)
ANY_HANDOUT_LINE = re.compile(r"^\s*(?:\*|#{1,6}).*Handout\b", re.I)
EXPECTED_HANDOUTS = ("1", "2a", "2b", "3a", "3b", *map(str, range(4, 40)))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path, description: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{description}: invalid JSON") from error


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def require_exact_domain(paths: Iterable[Path], pages: int, kind: str) -> dict[int, Path]:
    result: dict[int, Path] = {}
    pattern = re.compile(r"^page-(\d{3})$")
    for path in paths:
        match = pattern.match(path.stem)
        if not match:
            raise ValueError(f"{kind}: unexpected filename {path.name}")
        page = int(match.group(1))
        if page in result:
            raise ValueError(f"{kind}: duplicate page {page}")
        result[page] = path
    if set(result) != set(range(1, pages + 1)):
        raise ValueError(f"{kind}: page domain must be 1..{pages}")
    return result


def role_partition(contract: dict[str, Any]) -> dict[int, str]:
    pages = contract.get("source", {}).get("page_count")
    if not isinstance(pages, int) or pages < 1:
        raise ValueError("contract: invalid source page count")
    roles: dict[int, str] = {}
    for row in contract.get("page_roles", []):
        try:
            first, last, role = row["first_page"], row["last_page"], row["role"]
        except KeyError as error:
            raise ValueError("contract: invalid page role") from error
        for page in range(first, last + 1):
            if page in roles:
                raise ValueError("contract: role overlap")
            roles[page] = role
    if set(roles) != set(range(1, pages + 1)):
        raise ValueError("contract: role ranges have gap")
    return roles


def relative_under(root: Path, path: Path, description: str) -> Path:
    try:
        return path.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"{description}: path escapes candidate") from error


def inventory_records(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if path.is_file():
            records.append({"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
    return records


def inventory_digest(records: list[dict[str, Any]]) -> str:
    text = "".join(f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in records)
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def tree_identity(root: Path) -> dict[str, Any]:
    records = inventory_records(root) if root.exists() else []
    return {"file_count": len(records), "byte_count": sum(row["bytes"] for row in records), "ordinal_trailing_lf_inventory_sha256": inventory_digest(records)}


def expected_handout_pages(contract: dict[str, Any]) -> set[int]:
    for row in contract["page_roles"]:
        if row["role"] == "player_handouts":
            return set(range(row["first_page"], row["last_page"] + 1))
    raise ValueError("contract: player_handouts role is absent")


def validate_handouts(contract: dict[str, Any], markdown: dict[int, Path]) -> list[dict[str, Any]]:
    permitted_pages = expected_handout_pages(contract)
    found: list[dict[str, Any]] = []
    for page, path in markdown.items():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not ANY_HANDOUT_LINE.match(line):
                continue
            match = HANDOUT_LINE.match(line)
            if not match:
                raise ValueError(f"page {page}: Handout marker must be '*Handout #<label>*'")
            if page not in permitted_pages:
                raise ValueError(f"page {page}: Handout marker outside player_handouts")
            found.append({"label": match.group(1).lower(), "source_page": page})
    labels = [row["label"] for row in found]
    if len(labels) != len(set(labels)):
        raise ValueError("handout inventory: duplicate full label")
    if set(labels) != set(EXPECTED_HANDOUTS):
        raise ValueError("handout inventory: required labels missing or unexpected")
    ordinals = [(int(re.match(r"\d+", label).group()), label.lstrip("0123456789")) for label in labels]
    if len(ordinals) != len(set(ordinals)) or {number for number, _ in ordinals} != set(range(1, 40)):
        raise ValueError("handout inventory: numeric ordinal closure failed")
    return sorted(found, key=lambda row: (int(re.match(r"\d+", row["label"]).group()), row["label"]))


def validate_assets(candidate: Path, markdown: dict[int, Path]) -> None:
    manifest = read_json(candidate / "ASSET_MANIFEST.json", "asset manifest")
    entries = manifest.get("assets") if isinstance(manifest, dict) else None
    if not isinstance(entries, list):
        raise ValueError("asset manifest: assets must be a list")
    declared: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("stored_path"), str):
            raise ValueError("asset manifest: invalid entry")
        stored = Path(entry["stored_path"])
        if stored.is_absolute() or not stored.parts or stored.parts[0] != "assets":
            raise ValueError("asset manifest: stored path outside assets")
        path = candidate / stored
        relative = relative_under(candidate, path, "asset manifest").as_posix()
        if relative in declared:
            raise ValueError("asset manifest: duplicate stored path")
        if not path.is_file() or sha256(path) != entry.get("sha256"):
            raise ValueError("asset manifest: missing or corrupt asset")
        declared[relative] = entry["sha256"]
    assets = candidate / "assets"
    actual = {relative_under(candidate, path, "assets").as_posix() for path in assets.rglob("*") if path.is_file()} if assets.exists() else set()
    if actual != set(declared):
        raise ValueError("asset closure: declared and actual assets differ")
    image_links = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
    for document in list(markdown.values()) + [candidate / "RECONSTRUCTED_EN.md"]:
        for target in image_links.findall(document.read_text(encoding="utf-8")):
            target_path = Path(target)
            if target_path.is_absolute():
                raise ValueError(f"{document.name}: absolute asset link")
            resolved = document.parent / target_path
            relative = relative_under(candidate, resolved, document.name).as_posix()
            if relative not in declared or not resolved.is_file():
                raise ValueError(f"{document.name}: broken or undeclared asset link")


def comparison_blocks(raw: Path) -> dict[str, list[dict[str, Any]]]:
    comparison = read_json(raw / "comparison" / "comparison.json", "comparison")
    views = comparison.get("views") if isinstance(comparison, dict) else None
    if not isinstance(views, dict):
        raise ValueError("comparison: views missing")
    result = {}
    for view in VIEWS:
        blocks = views.get(view, {}).get("blocks") if isinstance(views.get(view), dict) else None
        if not isinstance(blocks, list):
            raise ValueError(f"comparison: {view} blocks missing")
        result[view] = blocks
    return result


def validate_decisions(candidate: Path, provenance: dict[str, Any], comparison: dict[str, list[dict[str, Any]]], pages: int) -> tuple[dict[int, dict[str, Any]], list[dict[str, Any]]]:
    decisions = require_exact_domain((candidate / "decisions").glob("*.json"), pages, "decisions")
    rows = provenance.get("pages") if isinstance(provenance, dict) else None
    if not isinstance(rows, list):
        raise ValueError("merge provenance: pages missing")
    by_page = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("source_page"), int) or row["source_page"] in by_page:
            raise ValueError("merge provenance: invalid or duplicate source page")
        by_page[row["source_page"]] = row
    if set(by_page) != set(range(1, pages + 1)):
        raise ValueError("merge provenance: page domain mismatch")
    unresolved, used = [], set()
    for page, path in decisions.items():
        decision = read_json(path, f"page {page} decision")
        selection, blockers = decision.get("selected_blocks"), decision.get("unresolved", [])
        if not isinstance(selection, list) or not isinstance(blockers, list):
            raise ValueError(f"page {page}: invalid decision lists")
        record = by_page[page]
        normalized = []
        for block in selection:
            if not isinstance(block, dict) or block.get("view") not in VIEWS or not isinstance(block.get("raw_index"), int):
                raise ValueError(f"page {page}: unknown view or invalid raw reference")
            normalized.append({"view": block["view"], "raw_index": block["raw_index"]})
        provenance_selection = record.get("selected_blocks", [])
        if not isinstance(provenance_selection, list) or any(
            not isinstance(block, dict) or set(block) != {"view", "raw_index"}
            for block in provenance_selection
        ) or canonical(normalized) != canonical(provenance_selection):
            raise ValueError(f"page {page}: decision/provenance selected_blocks mismatch")
        if canonical(blockers) != canonical(record.get("unresolved", [])):
            raise ValueError(f"page {page}: decision/provenance unresolved mismatch")
        blocker_keys = set()
        for blocker in blockers:
            key = canonical(blocker)
            if key in blocker_keys:
                raise ValueError(f"page {page}: duplicate unresolved record")
            blocker_keys.add(key); unresolved.append({"source_page": page, "record": blocker})
        for block in normalized:
            reference = (block["view"], block["raw_index"])
            if reference in used:
                raise ValueError(f"page {page}: duplicate raw reference")
            used.add(reference)
            matches = [row for row in comparison[block["view"]] if row.get("raw_index") == block["raw_index"] and row.get("source_page") == page]
            if len(matches) != 1:
                raise ValueError(f"page {page}: selected block not frozen comparison match")
    return by_page, unresolved


def validate_selection(candidate: Path, pages: int) -> dict[int, str]:
    selection = read_json(candidate / "OVERLAY_SELECTION.json", "overlay selection")
    rows = selection.get("pages") if isinstance(selection, dict) else None
    if not isinstance(rows, list):
        raise ValueError("overlay selection: pages missing")
    selected = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("source_page"), int):
            raise ValueError("overlay selection: invalid row")
        page, view = row["source_page"], row.get("overlay_preference")
        if page in selected:
            raise ValueError("overlay selection: duplicate source page")
        if view not in VIEWS:
            raise ValueError("overlay selection: bad overlay preference")
        selected[page] = view
    if set(selected) != set(range(1, pages + 1)):
        raise ValueError("overlay selection: page domain mismatch")
    return selected


def page_geometry(page: Any) -> tuple[tuple[float, float, float, float], int]:
    return tuple(float(value) for value in page.mediabox), int(page.get("/Rotate", 0) or 0)


def validate_geometry(reader: PdfReader, expected: tuple[tuple[float, float, float, float], int], description: str) -> None:
    for page_number, page in enumerate(reader.pages, start=1):
        if page_geometry(page) != expected:
            raise ValueError(f"{description}: geometry mismatch page {page_number}")


def contract_geometry(contract: dict[str, Any], source_reader: PdfReader) -> tuple[tuple[float, float, float, float], int]:
    source = contract["source"]
    media_box, rotation = source.get("media_box_points"), source.get("rotation_degrees")
    if not isinstance(media_box, list) or len(media_box) != 2 or not all(isinstance(value, (int, float)) for value in media_box) or not isinstance(rotation, int):
        raise ValueError("contract: source media_box_points and rotation_degrees required")
    expected = ((0.0, 0.0, float(media_box[0]), float(media_box[1])), rotation)
    validate_geometry(source_reader, expected, "source")
    return expected


def layout_pdf(raw: Path, view: str, pages: int, expected_geometry: tuple[tuple[float, float, float, float], int]) -> tuple[Path, PdfReader]:
    matches = list((raw / "runs" / view).rglob("*_layout.pdf"))
    if len(matches) != 1:
        raise ValueError(f"{view}: expected exactly one layout PDF")
    reader = PdfReader(str(matches[0]))
    if len(reader.pages) != pages:
        raise ValueError(f"{view}: layout page domain mismatch")
    validate_geometry(reader, expected_geometry, view)
    return matches[0], reader


def build_overlay(stage: Path, raw: Path, selected: dict[int, str], pages: int, contract: dict[str, Any], source_reader: PdfReader) -> list[dict[str, Any]]:
    declared_geometry = contract_geometry(contract, source_reader)
    layouts = {view: layout_pdf(raw, view, pages, declared_geometry) for view in VIEWS}
    writer, overlay_rows, expected = PdfWriter(), [], []
    for page_number in range(1, pages + 1):
        view = selected[page_number]
        layout_path, reader = layouts[view]
        layout_page = reader.pages[page_number - 1]
        expected.append(page_geometry(layout_page)); writer.add_page(layout_page)
        overlay_rows.append({"source_page": page_number, "selected_view": view, "layout_pdf": layout_path.relative_to(raw).as_posix(), "layout_sha256": sha256(layout_path)})
    writer.add_metadata({"/Producer": "kb_creator reconstruction finalizer", "/Creator": "kb_creator reconstruction finalizer"})
    overlay_path = stage / "SELECTED_OVERLAY.pdf"
    with overlay_path.open("wb") as stream:
        writer.write(stream)
    output = PdfReader(str(overlay_path))
    if len(output.pages) != pages:
        raise ValueError("selected overlay: page count mismatch")
    for page_number, output_page in enumerate(output.pages, start=1):
        if page_geometry(output_page) != expected[page_number - 1] or page_geometry(output_page) != declared_geometry:
            raise ValueError(f"selected overlay: geometry mismatch page {page_number}")
    return overlay_rows


def finalise(contract_path: Path, source: Path, raw: Path, candidate: Path, out: Path) -> dict[str, Any]:
    if out.exists():
        raise FileExistsError("output root must be absent")
    contract = read_json(contract_path, "contract")
    roles = role_partition(contract)
    source_contract, pages = contract["source"], contract["source"]["page_count"]
    source_reader = PdfReader(str(source))
    if sha256(source) != source_contract.get("sha256") or source.stat().st_size != source_contract.get("byte_count") or len(source_reader.pages) != pages:
        raise ValueError("source identity mismatch")
    markdown = require_exact_domain((candidate / "pages").glob("*.md"), pages, "pages")
    # CRCRLF is malformed and lone CR is not a supported reconstruction EOL.
    # Admit LF/CRLF input only; publication serialization may normalize later.
    for path in [*markdown.values(), candidate / "RECONSTRUCTED_EN.md"]:
        raw_bytes = path.read_bytes()
        if b"\r\r\n" in raw_bytes or b"\r" in raw_bytes.replace(b"\r\n", b""):
            raise ValueError(f"{path.name}: malformed EOL; use LF or CRLF only")
    combined = (candidate / "RECONSTRUCTED_EN.md").read_text(encoding="utf-8")
    if [int(value) for value in MARKER.findall(combined)] != list(range(1, pages + 1)):
        raise ValueError("root page markers mismatch")
    handouts = validate_handouts(contract, markdown)
    validate_assets(candidate, markdown)
    provenance = read_json(candidate / "MERGE_PROVENANCE.json", "merge provenance")
    provenance_by_page, unresolved = validate_decisions(candidate, provenance, comparison_blocks(raw), pages)
    if unresolved:
        raise ValueError("open blockers: " + canonical(unresolved))
    selected, candidate_identity = validate_selection(candidate, pages), tree_identity(candidate)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.stage-", dir=out.parent))
    try:
        shutil.copytree(candidate, stage, dirs_exist_ok=True)
        overlay_rows = build_overlay(stage, raw, selected, pages, contract, source_reader)
        overlay = stage / "SELECTED_OVERLAY.pdf"
        identity = {**candidate_identity, "algorithm": "SHA-256 over ordinal UTF-8 LF path<TAB>bytes<TAB>UPPER_SHA256<LF>", "candidate_root_sha256": candidate_identity["ordinal_trailing_lf_inventory_sha256"], "assets_root_sha256": tree_identity(candidate / "assets")["ordinal_trailing_lf_inventory_sha256"]}
        named_roots = {name: {"sha256": sha256(candidate / name), "bytes": (candidate / name).stat().st_size} for name in ("RECONSTRUCTED_EN.md", "MERGE_PROVENANCE.json", "ASSET_MANIFEST.json", "OVERLAY_SELECTION.json") if (candidate / name).is_file()}
        output_provenance = {"provenance_schema": "kb_creator.reconstruction-finalizer/v2", "scenario": contract.get("scenario"), "source": {"path": source.name, "sha256": sha256(source), "bytes": source.stat().st_size, "pages": pages}, "contract": {"path": contract_path.name, "sha256": sha256(contract_path), "revision": contract.get("contract_revision")}, "candidate_identity": {**identity, "named_root_artifacts": named_roots}, "selected_overlay": {"sha256": sha256(overlay), "bytes": overlay.stat().st_size, "pages": pages}, "handouts": handouts, "pages": [{"source_page": page, "fine_grained_role": provenance_by_page[page].get("semantic_role"), "contract_role": roles[page], "selected_blocks": provenance_by_page[page].get("selected_blocks"), "overlay": overlay_rows[page - 1]} for page in range(1, pages + 1)]}
        gates = {name: {"status": "pass", "errors": []} for name in GATE_NAMES}
        write_json(stage / "RECONSTRUCTION_PROVENANCE.json", output_provenance)
        write_json(stage / "RECONSTRUCTION_QA.json", {"status": "candidate_ready_for_reconstruction_review", "gates": gates})
        (stage / "RECONSTRUCTION_QA.md").write_text("# Reconstruction QA\n\n" + "\n".join(f"- {name}: pass" for name in GATE_NAMES) + "\n", encoding="utf-8")
        os.replace(stage, out)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return {"status": "candidate_ready_for_reconstruction_review", "pages": pages, "overlay_pages": pages}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True); parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True); parser.add_argument("--candidate-root", type=Path, required=True); parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(finalise(args.contract, args.source, args.raw_root, args.candidate_root, args.output_root)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
