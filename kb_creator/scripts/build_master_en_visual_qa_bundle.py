"""Create a deterministic, read-only visual-QA bundle for a MASTER_EN candidate."""
from __future__ import annotations

import argparse
import html
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

if __package__ in {None, ""}:  # Support the repository's documented script invocation.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from kb_creator.scripts.build_mineru_visual_merge_bundle import build_contact_sheets
from kb_creator.scripts.verify_scenario_master_en import validate_v2_verification_report


INVENTORY_ALGORITHM = "SHA-256 over ordinal UTF-8 LF relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>"
READER_COUNT, ASSET_COUNT, REVIEW_COUNT = 107, 123, 91
PRIORITY_ROLES = {"front_cover", "back_cover", "full_page", "map", "handout"}
ANCHOR = re.compile(r'<a id="([a-z0-9-]+)"></a>')


def fail(message: str) -> None:
    raise ValueError(f"E_VISUAL_QA_BUNDLE {message}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON: {path}")
    if not isinstance(value, dict):
        fail(f"JSON root is not an object: {path}")
    return value


def safe_relative(value: object) -> str:
    if not isinstance(value, str) or not value:
        fail("invalid relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value or "\\" in value:
        fail(f"unsafe relative path: {value!r}")
    return value


def identity(path: Path, relative_to: Path | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
    result["path"] = (path.relative_to(relative_to).as_posix() if relative_to else str(path.resolve()))
    return result


def image_size(path: Path) -> tuple[int, int]:
    try:
        from PIL import Image
        with Image.open(path) as image:
            return image.size
    except Exception as exc:  # Pillow reports corrupt images with varied exceptions.
        fail(f"unreadable image: {path}")


def validate_inventory(candidate: Path) -> dict[str, Any]:
    inventory = canonical_json(candidate / "INVENTORY.json")
    required = {"schema", "algorithm", "scope", "rows", "file_count", "total_bytes", "inventory_sha256"}
    if set(inventory) != required or inventory["schema"] != "kb_creator.candidate_inventory.v1":
        fail("candidate inventory schema")
    if inventory["algorithm"] != INVENTORY_ALGORITHM or inventory["scope"] != "all regular candidate files except INVENTORY.json":
        fail("candidate inventory contract")
    rows = []
    for path in sorted((item for item in candidate.rglob("*") if item.is_file()), key=lambda item: item.relative_to(candidate).as_posix()):
        if path.is_file() and path.name != "INVENTORY.json":
            rows.append({"path": path.relative_to(candidate).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    encoded = "".join(f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in rows).encode("utf-8")
    if inventory["rows"] != rows or inventory["file_count"] != len(rows) or inventory["total_bytes"] != sum(x["bytes"] for x in rows):
        fail("candidate inventory rows")
    if inventory["inventory_sha256"] != hashlib.sha256(encoded).hexdigest().upper():
        fail("candidate inventory digest")
    if len(rows) != 129:
        fail("candidate inventory count")
    return inventory


def owner_block(master: str, owner: str) -> str:
    matches = list(ANCHOR.finditer(master))
    starts = [match for match in matches if match.group(1) == owner]
    if len(starts) != 1:
        fail(f"owner block missing: {owner}")
    start = starts[0].start()
    following = [match.start() for match in matches if match.start() > start]
    return master[start:min(following, default=len(master))]


def validate_inputs(candidate: Path, config_path: Path, source_pdf: Path, output: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if not candidate.is_dir() or not config_path.is_file() or not source_pdf.is_file():
        fail("missing input")
    candidate, config_path, source_pdf, output = (x.resolve() for x in (candidate, config_path, source_pdf, output))
    if output.exists() or output == candidate or candidate in output.parents or output.parent == output:
        fail("output root must be absent and outside candidate")
    if not output.parent.is_dir():
        fail("output parent missing")
    config = canonical_json(config_path)
    required = {"schema", "scenario_id", "contract", "accepted_reconstruction", "document", "hierarchy", "source_disposition", "xrefs", "handouts", "structured_content", "assets", "visual_review_units", "reader_noise_patterns", "reader_surface"}
    if set(config) != required or config.get("schema") != "kb_creator.master_en_publication.v1" or config.get("scenario_id") != "viral":
        fail("publication config schema or identity")
    reader_surface = config["reader_surface"]
    reader_surface_keys = {"schema_version", "heading_policy", "semantic_fragments", "authorized_suppressions", "alt_policy"}
    if not isinstance(reader_surface, dict) or set(reader_surface) != reader_surface_keys:
        fail("reader surface schema")
    if reader_surface["schema_version"] != "kb_creator.master_en_reader_surface.v1":
        fail("reader surface schema version")
    if not isinstance(reader_surface["semantic_fragments"], list) or len(reader_surface["semantic_fragments"]) != 25:
        fail("reader surface semantic fragment count")
    if not isinstance(reader_surface["authorized_suppressions"], list) or len(reader_surface["authorized_suppressions"]) != 22:
        fail("reader surface authorized suppression count")
    source = config.get("document", {}).get("source_pdf", {})
    if source.get("bytes") != source_pdf.stat().st_size or source.get("sha256") != sha256_file(source_pdf) or source.get("page_count") != 124:
        fail("source PDF identity")
    inventory = validate_inventory(candidate)
    manifest = canonical_json(candidate / "ASSET_MANIFEST.json")
    if set(manifest) != {"schema", "scenario_id", "assets", "summary"} or manifest.get("schema") != "kb_creator.master_en_asset_manifest.v1" or manifest.get("scenario_id") != "viral":
        fail("asset manifest schema")
    assets = manifest.get("assets")
    if not isinstance(assets, list) or len(assets) != ASSET_COUNT or manifest.get("summary", {}).get("reader") != READER_COUNT:
        fail("asset manifest counts")
    declared = {asset.get("asset_id"): asset for asset in config["assets"] if isinstance(asset, dict)}
    if len(declared) != ASSET_COUNT or len({asset.get("asset_id") for asset in assets}) != ASSET_COUNT:
        fail("asset declarations")
    reader_rows: list[dict[str, Any]] = []
    for asset in assets:
        if not isinstance(asset, dict) or asset.get("asset_id") not in declared:
            fail("undeclared candidate asset")
        declared_asset = declared[asset["asset_id"]]
        fields = ("asset_id", "origin", "logical_name", "bytes", "sha256", "media_type", "dimensions", "source_page", "source_region", "semantic_role", "representation", "owner_anchor", "placement_index", "alt_text")
        if any(field in declared_asset and asset.get(field) != declared_asset.get(field) for field in fields):
            fail(f"asset/config mismatch: {asset.get('asset_id')}")
        path = candidate / safe_relative(asset.get("output_path"))
        if not path.is_file() or path.stat().st_size != asset["bytes"] or sha256_file(path) != asset["sha256"]:
            fail(f"candidate asset identity: {asset.get('asset_id')}")
        width, height = image_size(path)
        if asset.get("dimensions") != {"width": width, "height": height}:
            fail(f"candidate asset dimensions: {asset.get('asset_id')}")
        if asset.get("representation") == "reader":
            reader_rows.append({**asset, "candidate_path": asset["output_path"]})
    reader_rows.sort(key=lambda row: row["placement_index"])
    if len(reader_rows) != READER_COUNT or len({row["placement_index"] for row in reader_rows}) != READER_COUNT:
        fail("reader asset ordering")
    reviews = config["visual_review_units"]
    if not isinstance(reviews, list) or len(reviews) != REVIEW_COUNT or len({row.get("review_id") for row in reviews if isinstance(row, dict)}) != REVIEW_COUNT:
        fail("visual review units")
    reader_ids = {row["asset_id"] for row in reader_rows}
    for review in reviews:
        if not isinstance(review, dict) or set(review) != {"review_id", "classification", "owner_anchor", "source_pages", "asset_ids", "review_requirements", "special_requirement", "status"}:
            fail("visual review schema")
        if review["status"] != "pending_external_visual_qa" or any(asset_id not in reader_ids for asset_id in review["asset_ids"]):
            fail(f"visual review mapping: {review.get('review_id')}")
    master = (candidate / "MASTER_EN.md").read_text(encoding="utf-8")
    babez = owner_block(master, "viral-handout-13")
    if master.count("Hey Marco Babez") != 1 or babez.count("Hey Marco Babez") != 1:
        fail("Babez owner-block text")
    priorities = [row for row in reader_rows if row["semantic_role"] in PRIORITY_ROLES]
    if len(priorities) != 39:
        fail("priority asset count")
    required_cover_ids = {"viral-render-cover-front", "viral-render-cover-back"}
    if not required_cover_ids.issubset({row["asset_id"] for row in priorities}):
        fail("priority cover assets")
    front = next(row for row in reader_rows if row["asset_id"] == "viral-render-cover-front")
    back = next(row for row in reader_rows if row["asset_id"] == "viral-render-cover-back")
    if front["source_page"] != 1 or back["source_page"] != 124 or front["semantic_role"] != "front_cover" or back["semantic_role"] != "back_cover":
        fail("priority cover source pages")
    qa = canonical_json(candidate / "MASTER_EN.qa.json")
    if qa.get("metrics", {}).get("candidate_assets") != ASSET_COUNT or qa.get("metrics", {}).get("reader_assets") != READER_COUNT or qa.get("metrics", {}).get("visual_review_units") != REVIEW_COUNT:
        fail("candidate QA metrics")
    return config, reader_rows, reviews, priorities, {"candidate_inventory": inventory, "candidate_root": str(candidate), "config": identity(config_path), "source_pdf": identity(source_pdf)}


def build_tiles(candidate: Path, readers: list[dict[str, Any]], destination: Path) -> list[Path]:
    from PIL import Image, ImageDraw, ImageFont
    destination.mkdir(parents=True)
    font = ImageFont.load_default()
    tile_size, header = (1000, 750), 78
    outputs = []
    for ordinal, row in enumerate(readers, start=1):
        source = candidate / row["output_path"]
        with Image.open(source) as image:
            image = image.convert("RGB")
            image.thumbnail((tile_size[0], tile_size[1] - header), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", tile_size, "white")
            left = (tile_size[0] - image.width) // 2
            top = header + (tile_size[1] - header - image.height) // 2
            canvas.paste(image, (left, top))
        draw = ImageDraw.Draw(canvas)
        label = f"{ordinal:03d} | {row['asset_id']} | p{row['source_page']} | {row['semantic_role']} | {row['owner_anchor']}"
        draw.text((8, 8), label, fill="black", font=font)
        path = destination / f"tile-{ordinal:03d}.png"
        canvas.save(path)
        outputs.append(path)
    return outputs


def render_p80(source_pdf: Path, destination: Path, pdftoppm: str) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    version = subprocess.run([pdftoppm, "-v"], check=True, capture_output=True, text=True)
    version_text = (version.stdout + version.stderr).strip()
    prefix = destination / "p080"
    command = [pdftoppm, "-r", "200", "-png", "-singlefile", "-f", "80", "-l", "80", str(source_pdf), str(prefix)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    path = destination / "p080.png"
    if not path.is_file():
        fail("Poppler p80 output")
    width, height = image_size(path)
    return {"path": "p80/p080.png", "source_page": 80, "reader_scale_dpi": 200, "command": {"executable": Path(pdftoppm).name, "arguments": command[1:9], "source_pdf_sha256": sha256_file(source_pdf)}, "version": version_text, "bytes": path.stat().st_size, "sha256": sha256_file(path), "dimensions": {"width": width, "height": height}}


def transport_priority_originals(candidate: Path, priorities: list[dict[str, Any]], destination: Path) -> list[dict[str, Any]]:
    if len(priorities) != 39:
        fail("priority asset count")
    destination.mkdir(parents=True)
    transported = []
    used_names: set[str] = set()
    for row in priorities:
        original = safe_relative(row["candidate_path"])
        source = candidate / original
        name = original.replace("/", "__")
        if name in used_names or Path(name).suffix != Path(original).suffix:
            fail("priority transport destination collision")
        used_names.add(name)
        target = destination / name
        shutil.copyfile(source, target)
        if not target.is_file() or target.read_bytes() != source.read_bytes():
            fail(f"priority transport bytes: {original}")
        width, height = image_size(target)
        expected_dimensions = row["dimensions"]
        if {"width": width, "height": height} != expected_dimensions:
            fail(f"priority transport dimensions: {original}")
        copied = identity(target, destination.parent)
        if copied["bytes"] != row["bytes"] or copied["sha256"] != row["sha256"]:
            fail(f"priority transport identity: {original}")
        transported.append({"asset_id": row["asset_id"], "semantic_role": row["semantic_role"], "source_page": row["source_page"], "original_candidate_path": original, "identity": identity(source, candidate), "transported_path": copied["path"], "transported_identity": copied, "transported_dimensions": {"width": width, "height": height}})
    actual = sorted(path.name for path in destination.iterdir() if path.is_file())
    if len(actual) != 39 or actual != sorted(used_names):
        fail("priority transport closure")
    return transported


def write_bundle(candidate: Path, config: dict[str, Any], readers: list[dict[str, Any]], reviews: list[dict[str, Any]], priorities: list[dict[str, Any]], inputs: dict[str, Any], output: Path, pdftoppm: str) -> dict[str, Any]:
    output.mkdir()
    tiles = build_tiles(candidate, readers, output / "tiles")
    contacts = build_contact_sheets(tiles, output / "contact_sheets")
    if len(tiles) != READER_COUNT or len(contacts) != 27:
        fail("generated tile/contact count")
    p80 = render_p80(Path(inputs["source_pdf"]["path"]), output / "p80", pdftoppm)
    transported_priorities = transport_priority_originals(candidate, priorities, output / "priority_originals")
    def generated(path: Path) -> dict[str, Any]:
        return identity(path, output)
    manifest = {
        "schema": "kb_creator.master_en_visual_qa_bundle.v1",
        "status": "generated_pending_external_visual_inspection",
        "inspection_claim": "No visual inspection or acceptance is asserted by this generator.",
        "inputs": inputs,
        "counts": {"candidate_assets": ASSET_COUNT, "reader_assets": READER_COUNT, "visual_review_units": REVIEW_COUNT, "tiles": len(tiles), "contact_sheets": len(contacts), "priority_originals": len(transported_priorities), "open_generation_errors": 0},
        "reader_rows": [{"ordinal": number, "asset_id": row["asset_id"], "source_page": row["source_page"], "semantic_role": row["semantic_role"], "owner_anchor": row["owner_anchor"], "original_candidate_path": row["candidate_path"], "identity": identity(candidate / row["output_path"], candidate)} for number, row in enumerate(readers, start=1)],
        "visual_review_units": reviews,
        "tiles": [generated(path) for path in tiles],
        "contact_sheets": [generated(path) for path in contacts],
        "priority_assets": transported_priorities,
        "p80_render": p80,
        "babez_owner_block": {"owner_anchor": "viral-handout-13", "exact_visible_text": "Hey Marco Babez", "occurrences": 1},
    }
    manifest_path = output / "VISUAL_QA_BUNDLE.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


def v2_report_inputs(candidate: Path, config_path: Path, source_pdf: Path, report_path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Validate the external verifier report before any v2 QA output is made."""
    candidate, config_path, source_pdf, report_path = (item.resolve() for item in (candidate, config_path, source_pdf, report_path))
    if not candidate.is_dir() or not config_path.is_file() or not source_pdf.is_file() or not report_path.is_file():
        fail("missing v2 input")
    config = canonical_json(config_path)
    if config.get("schema") != "kb_creator.master_en_publication.v2":
        fail("v2 publication config schema")
    try:
        repository_root = next((parent for parent in (config_path.parent, *config_path.parents) if (parent / ".git").exists()), None)
        if repository_root is None:
            fail("v2 repository root")
        target = candidate.relative_to(repository_root).as_posix()
        validated = validate_v2_verification_report(str(config_path), target, report_path)
    except (ValueError, OSError) as exc:
        fail(f"v2 verification report: {exc}")
    report = canonical_json(report_path)
    if validated.get("status") != "validated_v2_verification_report" or report.get("status") != "verified_v2_candidate":
        fail("v2 verification report status")
    if report.get("candidate_root_name") != candidate.name or report.get("publication_config_sha256") != sha256_file(config_path) or report.get("source_pdf_sha256") != sha256_file(source_pdf):
        fail("v2 report input binding")
    return config, report, {"candidate_root": str(candidate), "config": identity(config_path), "source_pdf": identity(source_pdf), "verification_report": identity(report_path)}


def render_source_pages(source_pdf: Path, pages: list[int], destination: Path, pdftoppm: str) -> dict[int, Path]:
    destination.mkdir(parents=True)
    rendered: dict[int, Path] = {}
    for page in pages:
        prefix = destination / f"p{page:03d}"
        subprocess.run([pdftoppm, "-r", "150", "-png", "-singlefile", "-f", str(page), "-l", str(page), str(source_pdf), str(prefix)], check=True, capture_output=True, text=True)
        path = destination / f"p{page:03d}.png"
        if not path.is_file(): fail(f"v2 source crop missing: {page}")
        image_size(path); rendered[page] = path
    return rendered


def build_tiles_from_crops(crops: dict[int, Path], destination: Path) -> list[Path]:
    from PIL import Image, ImageDraw, ImageFont
    destination.mkdir(parents=True); result = []
    for page, crop in sorted(crops.items()):
        with Image.open(crop) as image:
            image = image.convert("RGB"); image.thumbnail((1000, 672), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (1000, 750), "white"); canvas.paste(image, ((1000 - image.width) // 2, 78))
        ImageDraw.Draw(canvas).text((8, 8), f"source page {page}", fill="black", font=ImageFont.load_default())
        path = destination / f"page-{page:03d}.png"; canvas.save(path); result.append(path)
    return result


def v2_reader_value(asset: dict[str, Any]) -> bool:
    """Support sealed legacy fixtures and canonical v2 disposition rows."""
    return bool(asset.get("reader_value", asset.get("disposition") == "reader"))


def v2_reader_asset_identity(asset: dict[str, Any], manifest: dict[str, Any]) -> tuple[int, str]:
    """Bind candidate bytes to the manifest and, when available, canonical binary."""
    bytes_, digest = manifest.get("bytes"), manifest.get("sha256")
    if not isinstance(bytes_, int) or bytes_ <= 0 or not isinstance(digest, str):
        fail("v2 asset manifest identity")
    binary = asset.get("binary")
    if binary is not None:
        if not isinstance(binary, dict) or binary.get("bytes") != bytes_ or binary.get("sha256") != digest:
            fail("v2 asset/config identity")
    elif "sha256" in asset and (asset.get("bytes") != bytes_ or asset.get("sha256") != digest):
        fail("v2 asset/config identity")
    return bytes_, digest


def copy_v2_reader_asset(candidate: Path, asset_id: str, manifest: dict[str, Any], destination: Path) -> dict[str, Any]:
    original = safe_relative(manifest.get("output_path"))
    source = candidate / original
    bytes_, digest = v2_reader_asset_identity({}, manifest)
    if not source.is_file() or source.stat().st_size != bytes_ or sha256_file(source) != digest:
        fail("v2 candidate asset identity")
    suffix = Path(original).suffix
    target = destination / f"{asset_id}{suffix}"
    if target.exists(): fail("v2 reader asset output collision")
    shutil.copyfile(source, target)
    if target.stat().st_size != bytes_ or sha256_file(target) != digest: fail("v2 reader asset copy identity")
    return {"asset_id": asset_id, "candidate_path": original, "review_path": target.relative_to(destination.parent).as_posix(), "identity": identity(source, candidate), "review_identity": identity(target, destination.parent)}


def v2_review_html(rows: list[dict[str, Any]]) -> str:
    """A self-contained reader/source review surface, deliberately without acceptance claims."""
    sections = ["<html><head><meta charset=\"utf-8\"><title>Visual QA v2</title></head><body><h1>Visual QA v2</h1><p>Pending external inspection; no acceptance is asserted.</p>"]
    for row in rows:
        sections.append(f"<section><h2>{html.escape(row['review_id'])} — {html.escape(row['kind'])}</h2><p>group: {html.escape(row['contact_sheet_group'])}; priority: {row['priority']}</p>")
        sections.append("<h3>Source</h3>" + "".join(f'<img src="{html.escape(item["path"])}" alt="source page {item["page"]}">' for item in row["source_crops"]))
        if row["events"]:
            sections.append("<h3>Reader excerpts</h3>" + "".join(f"<article><h4>{html.escape(item['event_id'])}</h4><pre>{html.escape(item['reader_excerpt'])}</pre></article>" for item in row["events"]))
        if row["assets"]:
            figures = []
            for item in row["assets"]:
                declaration = item["declaration"]
                provenance = declaration.get("provenance", {})
                disposition = declaration.get("disposition", "reader" if declaration.get("reader_value") else "evidence_only")
                details = f"{item['asset_id']} | {disposition} | p{declaration.get('source_page', declaration.get('page', '?'))} | {provenance.get('kind', 'legacy')} | {item['candidate_path']}"
                figures.append(f'<figure><img src="{html.escape(item["review_path"])}" alt="reader asset {html.escape(item["asset_id"])}"><figcaption>{html.escape(details)}</figcaption></figure>')
            sections.append("<h3>Reader assets</h3>" + "".join(figures))
        sections.append("</section>")
    return "".join(sections) + "</body></html>\n"


def write_v2_bundle(candidate: Path, config_path: Path, source_pdf: Path, report_path: Path, output: Path, pdftoppm: str) -> dict[str, Any]:
    config, report, inputs = v2_report_inputs(candidate, config_path, source_pdf, report_path)
    if output.exists() or not output.parent.is_dir() or output == candidate or candidate in output.parents: fail("output root must be absent and outside candidate")
    excluded = {row["page"] for row in config["source_disposition"] if row["publication_disposition"] == "excluded_advertising"}
    if excluded != {123, 124}: fail("v2 excluded disposition")
    units = config.get("visual_review_units")
    if not isinstance(units, list) or not units: fail("v2 review units")
    event_by_id = {row["event_id"]: row for row in config["events"]}; ledger = {row["event_id"]: row for row in canonical_json(candidate / "MASTER_EN.provenance.json").get("events", [])}
    asset_by_id = {row["asset_id"]: row for row in config["assets"]}; manifest_assets = {row["asset_id"]: row for row in canonical_json(candidate / "ASSET_MANIFEST.json").get("assets", [])}
    pages = sorted({page for unit in units for page in unit["source_pages"]})
    if not pages or excluded & set(pages): fail("v2 excluded page leakage")
    for unit in units:
        if set(unit) != {"review_id", "kind", "source_pages", "event_ids", "asset_ids", "priority", "contact_sheet_group"}: fail("v2 review unit schema")
        if any(page in excluded for page in unit["source_pages"]): fail("v2 excluded review leakage")
        for event_id in unit["event_ids"]:
            if event_id not in event_by_id or event_id not in ledger: fail("v2 event binding")
        for asset_id in unit["asset_ids"]:
            if asset_id not in asset_by_id or asset_id not in manifest_assets or not v2_reader_value(asset_by_id[asset_id]): fail("v2 asset binding")
    output.mkdir(); crops = render_source_pages(source_pdf, pages, output / "source_crops", pdftoppm); tiles = build_tiles_from_crops(crops, output / "source_tiles")
    groups: dict[str, list[Path]] = {}
    for unit in units: groups.setdefault(unit["contact_sheet_group"], []).extend(crops[page] for page in unit["source_pages"])
    contact_paths: list[Path] = []; contact_root = output / "contact_sheets"; contact_root.mkdir()
    for group, paths in sorted(groups.items()):
        group_dir = contact_root / group; group_dir.mkdir(); contact_paths.extend(build_contact_sheets(list(dict.fromkeys(paths)), group_dir))
    master = (candidate / "MASTER_EN.md").read_text(encoding="utf-8")
    reader_root = output / "reader_assets"; reader_root.mkdir()
    copied_assets: dict[str, dict[str, Any]] = {}
    rows = []
    for unit in units:
        event_rows = []
        for event_id in unit["event_ids"]:
            event_ledger = ledger[event_id]; start, end = event_ledger.get("start_char"), event_ledger.get("end_char")
            if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= len(master): fail("v2 reader excerpt range")
            event_rows.append({"event_id": event_id, "declared": event_by_id[event_id], "ledger": event_ledger, "reader_excerpt": master[start:end]})
        asset_rows = []
        for asset_id in unit["asset_ids"]:
            manifest_asset = manifest_assets[asset_id]; v2_reader_asset_identity(asset_by_id[asset_id], manifest_asset)
            if asset_id not in copied_assets: copied_assets[asset_id] = copy_v2_reader_asset(candidate, asset_id, manifest_asset, reader_root)
            asset_rows.append({"asset_id": asset_id, "declaration": asset_by_id[asset_id], "manifest": manifest_asset, **copied_assets[asset_id]})
        rows.append({"review_id": unit["review_id"], "kind": unit["kind"], "priority": unit["priority"], "contact_sheet_group": unit["contact_sheet_group"], "source_crops": [{**identity(crops[page], output), "page": page} for page in unit["source_pages"]], "events": event_rows, "assets": asset_rows})
    audit_rows = [{"page": page, "audit_disposition": "reconstructed", "publication_disposition": "excluded_advertising", "generated": []} for page in sorted(excluded)]
    manifest = {"schema": "kb_creator.master_en_visual_qa_bundle.v2", "status": "generated_pending_external_visual_inspection", "inspection_claim": "No visual inspection or acceptance is asserted by this generator.", "inputs": inputs, "verification_report": report, "counts": {"visual_review_units": len(units), "source_pages": len(pages), "contact_sheet_groups": len(groups), "priority_review_units": sum(unit["priority"] for unit in units), "source_crops": len(crops), "source_tiles": len(tiles), "contact_sheets": len(contact_paths), "reader_asset_copies": len(copied_assets), "excluded_advertising_pages": len(audit_rows), "open_generation_errors": 0}, "review_rows": rows, "excluded_audit_rows": audit_rows, "source_tiles": [identity(path, output) for path in tiles], "contact_sheets": [identity(path, output) for path in contact_paths]}
    (output / "VISUAL_QA_BUNDLE.json").write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    (output / "review.html").write_text(v2_review_html(rows), encoding="utf-8", newline="\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", required=True, type=Path)
    parser.add_argument("--publication-config", required=True, type=Path)
    parser.add_argument("--source-pdf", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--verification-report", type=Path)
    parser.add_argument("--pdftoppm", default=shutil.which("pdftoppm") or "pdftoppm")
    args = parser.parse_args()
    try:
        schema = canonical_json(args.publication_config).get("schema")
        if schema == "kb_creator.master_en_publication.v2":
            if args.verification_report is None: fail("v2 verification report required")
            manifest = write_v2_bundle(args.candidate_root.resolve(), args.publication_config.resolve(), args.source_pdf.resolve(), args.verification_report.resolve(), args.output_root.resolve(), args.pdftoppm)
        else:
            if args.verification_report is not None: fail("verification report unsupported for v1")
            config, readers, reviews, priorities, inputs = validate_inputs(args.candidate_root, args.publication_config, args.source_pdf, args.output_root)
            manifest = write_bundle(args.candidate_root.resolve(), config, readers, reviews, priorities, inputs, args.output_root.resolve(), args.pdftoppm)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        raise SystemExit(str(exc))
    print(json.dumps({"status": manifest["status"], "counts": manifest["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
