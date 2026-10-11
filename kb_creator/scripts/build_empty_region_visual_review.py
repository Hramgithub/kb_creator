"""Render unverified empty OCR regions for visual triage; never accept content."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader

from kb_creator.pipeline.source_page_render import render_source_pdf_page, sha256_file


def identity(path: Path) -> dict:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def pixel_box(bbox: list, size: tuple[int, int], padding: int = 0) -> tuple[int, int, int, int]:
    if (not isinstance(bbox, list) or len(bbox) != 4
            or any(type(x) not in (int, float) or not math.isfinite(x) for x in bbox)
            or not 0 <= bbox[0] < bbox[2] <= 1000 or not 0 <= bbox[1] < bbox[3] <= 1000):
        raise ValueError("invalid normalized top-left bbox")
    return (math.floor(max(0, bbox[0] - padding) * size[0] / 1000),
            math.floor(max(0, bbox[1] - padding) * size[1] / 1000),
            math.ceil(min(1000, bbox[2] + padding) * size[0] / 1000),
            math.ceil(min(1000, bbox[3] + padding) * size[1] / 1000))


def validate_rows(report: dict, packets: Path, source: Path) -> tuple[list, list]:
    rows = report.get("rows", report.get("excluded_empty_sources"))
    if not isinstance(rows, list) or not rows:
        raise ValueError("no empty source observations")
    reader, seen, authorities, selected = PdfReader(str(source)), set(), {}, []
    for row in rows:
        page, key = row["source_page"], row["source_key"]
        if type(page) is not int or not 1 <= page <= len(reader.pages):
            raise ValueError("source page outside PDF")
        token = (page, key["view"], key["raw_index"])
        if token in seen:
            raise ValueError("duplicate source observation")
        seen.add(token)
        pdf_page = reader.pages[page - 1]
        if (int(pdf_page.get("/Rotate", 0)) % 360 != 0
                or list(pdf_page.cropbox) != list(pdf_page.mediabox)
                or float(pdf_page.get("/UserUnit", 1)) != 1):
            raise ValueError("unsupported OCR coordinate frame: rotation, crop, or UserUnit")
        packet_path = packets / f"page-{page:03d}.json"
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        if packet.get("source_page") != page:
            raise ValueError("packet page mismatch")
        authorities[page] = identity(packet_path)
        matches = [b for b in packet["views"][key["view"]]["blocks"] if b["raw_index"] == key["raw_index"]]
        witnesses = [w for w in row["witnesses"] if w["source_key"] == key]
        if len(matches) != 1 or len(witnesses) != 1:
            raise ValueError("selected observation lacks unique packet witness")
        block, witness = matches[0], witnesses[0]
        if block.get("text") != "" or witness.get("text") != "" or block.get("bbox") != witness.get("bbox"):
            raise ValueError("empty observation disagrees with source packet")
        pixel_box(block["bbox"], (1000, 1000))
        selected.append({"source_page": page, "source_key": key, "bbox": block["bbox"]})
    return selected, list(authorities.values())


def build(report_path: Path, source: Path, expected_source: str, packets: Path,
          renderer: Path, output: Path) -> dict:
    if sha256_file(source) != expected_source.upper():
        raise ValueError("source PDF identity mismatch")
    rows, authorities = validate_rows(json.loads(report_path.read_text(encoding="utf-8")), packets, source)
    output.mkdir(parents=True, exist_ok=False)
    renderer_sha = sha256_file(renderer)
    pages, renders, tiles, observations = {}, [], [], []
    for page in sorted({r["source_page"] for r in rows}):
        path = output / "pages" / f"page-{page:03d}.png"
        facts = render_source_pdf_page(source, page, renderer, 144, path,
                                      expected_source_sha256=expected_source, expected_renderer_sha256=renderer_sha)
        pages[page] = path
        renders.append({"path": str(path), **facts})
    (output / "regions").mkdir()
    for index, row in enumerate(rows, 1):
        with Image.open(pages[row["source_page"]]) as image:
            box = pixel_box(row["bbox"], image.size, 15)
            exact = pixel_box(row["bbox"], image.size)
            crop = image.convert("RGB").crop(box)
        path = output / "regions" / f"region-{index:03d}.png"
        crop.save(path)
        preview = crop.copy()
        ImageDraw.Draw(preview).rectangle((exact[0]-box[0], exact[1]-box[1], exact[2]-box[0]-1, exact[3]-box[1]-1), outline="red", width=2)
        preview.thumbnail((680, 280))
        tile = Image.new("RGB", (700, 350), "white")
        tile.paste(preview, ((700-preview.width)//2, 60))
        draw = ImageDraw.Draw(tile)
        draw.text((10, 10), f"Region {index:03d} | source {row['source_page']} | {row['source_key']['view']}:{row['source_key']['raw_index']}", fill="black")
        draw.text((10, 30), f"bbox {row['bbox']} | red = OCR region | UNREVIEWED", fill="black")
        tiles.append(tile)
        observations.append({"region_id": index, **row, "crop_pixels": list(box), "crop": identity(path), "disposition": "pending_visual_review"})
    sheets = []
    for start in range(0, len(tiles), 6):
        sheet = Image.new("RGB", (1400, 1050), "white")
        for offset, tile in enumerate(tiles[start:start+6]):
            sheet.paste(tile, ((offset % 2)*700, (offset//2)*350))
        path = output / f"sheet-{start//6+1:02d}.png"
        sheet.save(path)
        sheets.append(identity(path))
    manifest = {"schema": "kb_creator.empty_region_visual_review.v1", "state": "pending_visual_review",
                "claim": "Crops are QA aids, not proof of missing text, retained coverage, or acceptance.",
                "coordinate_frame": "unrotated_full_page_top_left_0_1000_crop_equals_media_userunit_1",
                "source": identity(source), "observations_input": identity(report_path),
                "packets": authorities, "renders": renders, "rows": observations, "contact_sheets": sheets}
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("observations", "source", "packets", "renderer", "output"):
        parser.add_argument("--"+arg, type=Path, required=True)
    parser.add_argument("--source-sha256", required=True)
    args = parser.parse_args()
    result = build(args.observations, args.source, args.source_sha256, args.packets, args.renderer, args.output)
    print(json.dumps({"regions": len(result["rows"]), "pages": len(result["renders"]), "state": result["state"]}))


if __name__ == "__main__":
    main()
