"""Deterministically inventory and extract embedded PDF image resources."""

from __future__ import annotations

import argparse
import io
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader
from PIL import Image


SELECTOR = re.compile(r"^(?P<page>[1-9][0-9]*):(?P<name>[^/\\]+)$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_record(page_number: int, image) -> dict:
    ref = image.indirect_reference
    xref = ref.idnum if ref is not None else None
    return {
        "page": page_number,
        "name": image.name,
        "xref": xref,
        "identity": f"page:{page_number}/name:{image.name}/xref:{xref}",
        "format": image.name.rsplit(".", 1)[-1].lower() if "." in image.name else "bin",
        "width": image.image.width,
        "height": image.image.height,
        "mode": image.image.mode,
        "bytes": len(image.data),
    }


def iter_images(reader: PdfReader, pages: Iterable[int] | None = None):
    page_set = set(pages) if pages is not None else None
    for page_number, page in enumerate(reader.pages, start=1):
        if page_set is not None and page_number not in page_set:
            continue
        for image in page.images:
            yield page_number, image


def parse_selectors(values: list[str]) -> list[tuple[int, str]]:
    parsed = []
    for value in values:
        match = SELECTOR.fullmatch(value)
        if not match:
            raise ValueError(f"invalid selector {value!r}; expected PAGE:IMAGE_NAME")
        parsed.append((int(match.group("page")), match.group("name")))
    if len(set(parsed)) != len(parsed):
        raise ValueError("duplicate image selector")
    return parsed


def list_images(input_pdf: Path, pages: list[int] | None) -> dict:
    reader = PdfReader(str(input_pdf))
    records = [image_record(page, image) for page, image in iter_images(reader, pages)]
    return {"source": str(input_pdf), "source_sha256": source_sha256(input_pdf), "images": records}


def extract_images(input_pdf: Path, output_dir: Path, selectors: list[str], pages: list[int] | None, output_format: str = "native") -> dict:
    if not selectors and not pages:
        raise ValueError("extract requires --select or --pages")
    reader = PdfReader(str(input_pdf))
    if pages and any(page < 1 or page > len(reader.pages) for page in pages):
        raise ValueError(f"page out of range; source has {len(reader.pages)} pages")
    wanted = set(parse_selectors(selectors))
    if wanted:
        selected_pages = {page for page, _ in wanted}
        if any(page > len(reader.pages) for page in selected_pages):
            raise ValueError(f"page out of range; source has {len(reader.pages)} pages")
        # A selector should not decode unrelated pages, which may contain
        # unsupported image resources even when the requested image is valid.
        pages = sorted(selected_pages if pages is None else selected_pages.intersection(pages))
    raw_output_dir = output_dir
    for candidate in (raw_output_dir, *raw_output_dir.parents):
        if candidate.exists() and candidate.is_symlink():
            raise ValueError("output path must not contain symlink directories")
        if candidate == candidate.anchor:
            break
    output_dir = output_dir.resolve()
    if output_dir.exists() and output_dir.is_symlink():
        raise ValueError("output directory must not be a symlink")
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError("output path is not a directory")
    if output_dir.exists() and (output_dir / "manifest.json").exists():
        raise FileExistsError(f"refusing to overwrite existing manifest: {output_dir / 'manifest.json'}")
    source_hash = source_sha256(input_pdf)
    selected_images = []
    for page, image in iter_images(reader, pages):
        selected = (page, image.name) in wanted if wanted else True
        if not selected:
            continue
        selected_images.append((page, image))
    found = {(page, image.name) for page, image in selected_images}
    if wanted and found != wanted:
        missing = sorted(wanted - found)
        raise ValueError(f"selected images not found: {missing}")
    if not selected_images:
        raise ValueError("no images selected")
    if output_format not in {"native", "png"}:
        raise ValueError(f"unsupported output format: {output_format}")
    destinations = []
    for page, image in selected_images:
        suffix = "png" if output_format == "png" else (image.name.rsplit(".", 1)[-1].lower() if "." in image.name else "bin")
        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", image.name)
        destination = (output_dir / f"page-{page:03d}-{Path(safe_name).stem}.{suffix}").resolve()
        if output_dir not in destination.parents:
            raise ValueError("output path escapes output directory")
        if destination in destinations or destination.exists():
            raise FileExistsError(f"refusing to overwrite or collide at output: {destination}")
        destinations.append(destination)
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for (page, image), destination in zip(selected_images, destinations):
        data = bytes(image.data)
        if output_format == "png":
            buffer = io.BytesIO()
            image.image.save(buffer, format="PNG")
            data = buffer.getvalue()
        destination.write_bytes(data)
        record = image_record(page, image)
        record.update({"path": destination.relative_to(output_dir).as_posix(), "sha256": sha256_bytes(data)})
        records.append(record)
    manifest = {"source": str(input_pdf), "source_sha256": source_hash, "images": records}
    manifest_path = output_dir / "manifest.json"
    if manifest_path.exists():
        raise FileExistsError(f"refusing to overwrite existing manifest: {manifest_path}")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pdf", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    list_parser = sub.add_parser("list")
    list_parser.add_argument("--pages", nargs="+", type=int)
    list_parser.add_argument("--output", type=Path)
    extract_parser = sub.add_parser("extract")
    extract_parser.add_argument("--output-dir", required=True, type=Path)
    extract_parser.add_argument("--select", action="append", default=[], help="PAGE:IMAGE_NAME")
    extract_parser.add_argument("--pages", nargs="+", type=int)
    extract_parser.add_argument("--format", choices=("native", "png"), default="native")
    args = parser.parse_args()
    if args.command == "list":
        result = list_images(args.input_pdf, args.pages)
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
    else:
        print(json.dumps(extract_images(args.input_pdf, args.output_dir, args.select, args.pages, args.format), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
