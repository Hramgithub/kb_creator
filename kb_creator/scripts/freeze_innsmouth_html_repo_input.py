"""Freeze the explicitly accepted Innsmouth HTML review package."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any


KB_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE_ROOT = (
    KB_ROOT
    / "working"
    / "innsmouth_direct_html"
    / "accepted_20260830_candidate_r7f"
)
DEFAULT_MASTER_RU_ROOT = (
    KB_ROOT / "inputs" / "innsmouth" / "master_ru" / "accepted_20260830_r2"
)
DEFAULT_TARGET_ROOT = (
    KB_ROOT / "inputs" / "innsmouth" / "html" / "accepted_20260830_r2"
)

HTML_NAME = "The_Innsmouth_Terror_RU.html"
MANIFEST_NAME = "HTML.acceptance.json"
EXPECTED_HTML_BYTES = 223_459
EXPECTED_HTML_SHA256 = (
    "040C7AF42A76241B3BC280350C0151096CF81E5F9A9194E6F5003B0388E4EF39"
)
EXPECTED_MASTER_RU_BYTES = 189_302
EXPECTED_MASTER_RU_SHA256 = (
    "E9A0AF27BEFE56630E1DBF24CD63EB9C8768706FEAE4C4DB1836E3175D4DED8E"
)
EXPECTED_MASTER_RU_ACCEPTANCE_SHA256 = (
    "87B3B867895209D8444F5B7E940EE6E14BECE3C79D810F35C92BD5D4FA6ED412"
)
EXPECTED_ASSET_COUNT = 32
EXPECTED_ASSET_INVENTORY_SHA256 = (
    "849C8238A9165EADC8A796B6A2501C84E9CD220F303CD70E46940FAF6C1E3019"
)
ACCEPTANCE_MANIFEST_BYTES = 6_966
ACCEPTANCE_MANIFEST_SHA256 = (
    "B0ADDD901CCD0DED10D84D331B3F168987070558641D374F13ABC30852E6D7E6"
)
LETTER_SEAL_ASSET = (
    "334f14bd517569e118d9445575f8c2bed6a356c7504142c3ac75a6f472e954f5.jpg"
)

IMAGE_REFERENCE = re.compile(r'<img\b[^>]*\bsrc="assets/([^"]+)"', re.I)
HTML_ID = re.compile(r'\bid="([^"]+)"')
HTML_FRAGMENT = re.compile(r'\bhref="#([^"]+)"')
STABLE_ANCHOR = re.compile(r'<a\s+id="(nri-[A-Za-z0-9_-]+)"\s*></a>')


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def logical_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(KB_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def asset_records(assets_root: Path) -> list[dict[str, Any]]:
    if not assets_root.is_dir():
        raise ValueError(f"assets directory is missing: {assets_root}")
    records: list[dict[str, Any]] = []
    for path in sorted(assets_root.iterdir(), key=lambda item: item.name):
        if not path.is_file():
            raise ValueError(f"unexpected assets entry: {path}")
        raw = path.read_bytes()
        records.append(
            {
                "path": f"assets/{path.name}",
                "byte_count": len(raw),
                "sha256": sha256(raw).lower(),
            }
        )
    return records


def asset_inventory_sha256(records: list[dict[str, Any]]) -> str:
    raw = json.dumps(records, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return sha256(raw)


def validate_master_ru_source(master_ru_root: Path) -> dict[str, Any]:
    master = master_ru_root / "MASTER_RU.md"
    acceptance = master_ru_root / "MASTER_RU.acceptance.json"
    if not master.is_file() or not acceptance.is_file():
        raise ValueError("accepted MASTER_RU source package is incomplete")
    master_raw = master.read_bytes()
    acceptance_raw = acceptance.read_bytes()
    if len(master_raw) != EXPECTED_MASTER_RU_BYTES or sha256(master_raw) != EXPECTED_MASTER_RU_SHA256:
        raise ValueError("accepted MASTER_RU identity mismatch")
    if sha256(acceptance_raw) != EXPECTED_MASTER_RU_ACCEPTANCE_SHA256:
        raise ValueError("accepted MASTER_RU acceptance identity mismatch")
    records = asset_records(master_ru_root / "assets")
    inventory = asset_inventory_sha256(records)
    if len(records) != EXPECTED_ASSET_COUNT or inventory != EXPECTED_ASSET_INVENTORY_SHA256:
        raise ValueError("accepted MASTER_RU asset inventory mismatch")
    return {
        "path": logical_path(master),
        "bytes": len(master_raw),
        "sha256": sha256(master_raw),
        "acceptance_path": logical_path(acceptance),
        "acceptance_sha256": sha256(acceptance_raw),
        "asset_count": len(records),
        "asset_inventory_sha256": inventory,
    }


def validate_html_candidate(candidate_root: Path, master_ru_root: Path) -> dict[str, Any]:
    source = validate_master_ru_source(master_ru_root)
    html_path = candidate_root / HTML_NAME
    if not html_path.is_file():
        raise ValueError(f"accepted HTML candidate is missing: {html_path}")
    html_raw = html_path.read_bytes()
    html_sha = sha256(html_raw)
    if len(html_raw) != EXPECTED_HTML_BYTES or html_sha != EXPECTED_HTML_SHA256:
        raise ValueError("accepted HTML candidate identity mismatch")
    html = html_raw.decode("utf-8")

    candidate_records = asset_records(candidate_root / "assets")
    source_records = asset_records(master_ru_root / "assets")
    if candidate_records != source_records:
        raise ValueError("accepted HTML assets differ from accepted MASTER_RU assets")
    inventory = asset_inventory_sha256(candidate_records)
    if len(candidate_records) != EXPECTED_ASSET_COUNT or inventory != EXPECTED_ASSET_INVENTORY_SHA256:
        raise ValueError("accepted HTML asset inventory mismatch")

    image_references = IMAGE_REFERENCE.findall(html)
    image_counts = Counter(image_references)
    expected_names = {Path(str(record["path"])).name for record in candidate_records}
    if set(image_counts) != expected_names or len(image_references) != EXPECTED_ASSET_COUNT:
        raise ValueError("accepted HTML image-reference inventory mismatch")
    if any(count != 1 for count in image_counts.values()):
        raise ValueError("accepted HTML must reference each reader asset exactly once")

    ids = HTML_ID.findall(html)
    fragments = HTML_FRAGMENT.findall(html)
    broken = sorted(set(fragments) - set(ids))
    stable_anchors = STABLE_ANCHOR.findall(html)
    if len(stable_anchors) != 52 or len(fragments) != 86 or broken:
        raise ValueError("accepted HTML anchor/fragment contract mismatch")
    if len(set(stable_anchors)) != len(stable_anchors):
        raise ValueError("accepted HTML has duplicate stable anchors")

    checks = {
        "stable_anchors": len(stable_anchors),
        "internal_fragments": len(fragments),
        "broken_fragments": len(broken),
        "images": len(image_references),
        "tables": html.count("<table>"),
        "statblock_cards": html.count('class="statblock-card"'),
        "source_toc_groups": html.count('class="source-toc-group"'),
        "title_pages": html.count('id="title-page"'),
        "full_width_figures": len(
            re.findall(r'<figure\b[^>]*\bclass="[^"]*\bart-full-width\b', html)
        ),
        "inline_figures": len(
            re.findall(r'<figure\b[^>]*\bclass="[^"]*\bart-float-right\b', html)
        ),
        "figure_captions": html.count("<figcaption>"),
        "technical_comments": html.count("mineru-page") + html.count("table-evidence"),
        "letter_seal_references": html.count(LETTER_SEAL_ASSET),
    }
    expected_checks = {
        "stable_anchors": 52,
        "internal_fragments": 86,
        "broken_fragments": 0,
        "images": 32,
        "tables": 51,
        "statblock_cards": 22,
        "source_toc_groups": 11,
        "title_pages": 1,
        "full_width_figures": 11,
        "inline_figures": 21,
        "figure_captions": 12,
        "technical_comments": 0,
        "letter_seal_references": 0,
    }
    if checks != expected_checks:
        raise ValueError(f"accepted HTML structural contract mismatch: {checks}")
    if html.count('id="innsmouth-presentation-r7"') != 1:
        raise ValueError("accepted HTML presentation stylesheet identity mismatch")
    if html.count('class="title-overlay"') != 1 or 'id="credits"' in html:
        raise ValueError("accepted HTML title/credits layout contract mismatch")

    return {
        "html": {
            "name": HTML_NAME,
            "bytes": len(html_raw),
            "sha256": html_sha,
        },
        "source_master_ru": source,
        "assets": {
            "count": len(candidate_records),
            "inventory_sha256": inventory,
            "files": candidate_records,
        },
        "checks": checks,
    }


def acceptance_manifest(validation: dict[str, Any], accepted_on: str) -> dict[str, Any]:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", accepted_on):
        raise ValueError("accepted-on must be YYYY-MM-DD")
    return {
        "schema": "kb_creator.innsmouth.accepted_html.v1",
        "accepted_on": accepted_on,
        "acceptance": "user_visual_acceptance",
        "html": validation["html"],
        "source_master_ru": validation["source_master_ru"],
        "assets": validation["assets"],
        "checks": validation["checks"],
        "policy": {
            "manual_html_edits": "forbidden",
            "downstream": "accepted HTML -> reproducible PDF candidate",
        },
    }


def promote(candidate_root: Path, master_ru_root: Path, target_root: Path, accepted_on: str) -> dict[str, Any]:
    validation = validate_html_candidate(candidate_root, master_ru_root)
    if target_root.exists():
        raise FileExistsError(f"accepted HTML target already exists: {target_root}")
    target_root.parent.mkdir(parents=True, exist_ok=True)
    stage_root = Path(tempfile.mkdtemp(prefix=f".{target_root.name}.stage-", dir=target_root.parent))
    try:
        shutil.copy2(candidate_root / HTML_NAME, stage_root / HTML_NAME)
        shutil.copytree(candidate_root / "assets", stage_root / "assets")
        manifest_raw = canonical_json(acceptance_manifest(validation, accepted_on))
        (stage_root / MANIFEST_NAME).write_bytes(manifest_raw)
        os.replace(stage_root, target_root)
    finally:
        if stage_root.exists():
            shutil.rmtree(stage_root)
    return verify(target_root, master_ru_root)


def verify(target_root: Path, master_ru_root: Path) -> dict[str, Any]:
    allowed = {HTML_NAME, MANIFEST_NAME, "assets"}
    actual = {path.name for path in target_root.iterdir()} if target_root.is_dir() else set()
    if actual != allowed:
        raise ValueError(f"accepted HTML root inventory mismatch: {sorted(actual)}")
    manifest_path = target_root / MANIFEST_NAME
    manifest_raw = manifest_path.read_bytes()
    if (
        len(manifest_raw) != ACCEPTANCE_MANIFEST_BYTES
        or sha256(manifest_raw) != ACCEPTANCE_MANIFEST_SHA256
    ):
        raise ValueError("accepted HTML acceptance manifest identity mismatch")
    manifest = json.loads(manifest_raw.decode("utf-8"))
    validation = validate_html_candidate(target_root, master_ru_root)
    expected = canonical_json(acceptance_manifest(validation, str(manifest.get("accepted_on", ""))))
    if manifest_raw != expected:
        raise ValueError("accepted HTML acceptance manifest mismatch")
    return {
        **validation,
        "manifest": {
            "name": MANIFEST_NAME,
            "bytes": len(manifest_raw),
            "sha256": sha256(manifest_raw),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--promote", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE_ROOT)
    parser.add_argument("--master-ru-root", type=Path, default=DEFAULT_MASTER_RU_ROOT)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET_ROOT)
    parser.add_argument("--accepted-on", default="2026-08-30")
    args = parser.parse_args()

    if args.preflight:
        result = validate_html_candidate(args.candidate.resolve(), args.master_ru_root.resolve())
        marker = "INNSMOUTH_ACCEPTED_HTML_PREFLIGHT_OK"
    elif args.promote:
        result = promote(
            args.candidate.resolve(),
            args.master_ru_root.resolve(),
            args.target.resolve(),
            args.accepted_on,
        )
        marker = "INNSMOUTH_ACCEPTED_HTML_PROMOTION_OK"
    else:
        result = verify(args.target.resolve(), args.master_ru_root.resolve())
        marker = "INNSMOUTH_ACCEPTED_HTML_REPO_INPUT_OK"
    print(marker)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
