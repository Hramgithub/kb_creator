"""Materialize only the frozen, inspected source-art selection into a new root."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image
from pypdf import PdfReader

from kb_creator.scripts.extract_pdf_image_assets import source_sha256


SPEC_SHA = "4653EB8E849B5F4CBEA4714BB5DB2CE4718E80BB87A3C0BCE0D8CE053F51C203"


def prepare(spec_path: Path, output: Path) -> dict:
    if source_sha256(spec_path).upper() != SPEC_SHA:
        raise ValueError("frozen selection identity changed")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    source = Path(spec["source_identity"]["path"])
    if source_sha256(source).upper() != spec["source_identity"]["sha256"]:
        raise ValueError("original PDF identity changed")
    if output.exists() or output.is_symlink():
        raise FileExistsError("asset output must be a new directory")
    original = PdfReader(source)
    visual = pdfium.PdfDocument(str(source))
    if len(original.pages) != 200 or len(spec["selections"]) != 23:
        raise ValueError("unexpected source or selection domain")
    prepared = []
    for selection in spec["selections"]:
        page = selection["source_page"]
        name = selection["target_asset_name"]
        if Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError("invalid frozen asset name")
        if page == 74:
            bitmap = visual[page - 1].render(scale=2).to_pil().convert("RGB")
            buffer = io.BytesIO()
            bitmap.save(buffer, format="PNG")
            data = buffer.getvalue()
            expected = selection["candidate_png_sha256"]
        else:
            obj = original.get_object(selection["object_xref"])
            encoded = obj.get_data()
            if hashlib.sha256(encoded).hexdigest().upper() != selection["source_encoded_sha256"]:
                raise ValueError(f"source object changed on page {page}")
            if "/SMask" in obj or str(obj["/Filter"]) != selection["source_filter"]:
                raise ValueError(f"unsupported source composition on page {page}")
            data = encoded
            if selection["source_filter"] == "/JPXDecode":
                with Image.open(io.BytesIO(encoded)) as decoded:
                    bitmap = decoded.convert("RGB")
                    buffer = io.BytesIO()
                    bitmap.save(buffer, format="PNG")
                    data = buffer.getvalue()
            expected = selection["candidate_selected_sha256"]
        digest = hashlib.sha256(data).hexdigest().upper()
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            dimensions = list(image.size)
        if digest != expected or dimensions != selection["source_pixel_size"]:
            raise ValueError(f"selected artwork identity changed on page {page}")
        prepared.append((name, data, {
            "source_page": page, "story_title_ru": selection["story_title_ru"],
            "html_heading_anchor": selection["html_heading_anchor"],
            "path": name, "sha256": digest, "dimensions": dimensions,
            "route": selection["selected_route"],
            "fidelity_exception": selection.get("fidelity_exception"),
        }))
    visual.close()
    if len({name for name, _, _ in prepared}) != 23:
        raise ValueError("duplicate selected artwork destination")
    output.mkdir(parents=True, exist_ok=False)
    for name, data, _ in prepared:
        (output / name).write_bytes(data)
    report = {
        "schema": "nri.fear_native_art_materialization.v1",
        "source_pdf_sha256": spec["source_identity"]["sha256"],
        "selection_sha256": SPEC_SHA, "original_pdf_modified": False,
        "assets": [record for _, _, record in prepared],
        "limitations": ["Source page74 retains original English lettering in a complete vector-art facsimile."],
    }
    for item in report["assets"]:
        if source_sha256(output / item["path"]).upper() != item["sha256"]:
            raise ValueError("post-write artwork identity mismatch")
    if source_sha256(source).upper() != report["source_pdf_sha256"]:
        raise ValueError("original PDF changed during materialization")
    (output / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = prepare(args.spec.resolve(), args.output.resolve())
    print(json.dumps({"assets": len(result["assets"]), "verified": True, "output": str(args.output)}, ensure_ascii=False))
