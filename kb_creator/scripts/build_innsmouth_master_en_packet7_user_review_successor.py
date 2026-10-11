"""Build the Packet 7 user-review successor without mutating the accepted package.

The accepted Packet 7 projection linked the whole navigation label and, for
parenthetical references, consumed punctuation that belonged to the sentence.
This successor changes only the printed ``page N`` token to a literal
``[link](#anchor)``.  The Handout reference keeps ``Handout 1-b`` as its visible
link text.  It also links the eleven major TOC groups to explicit section
anchors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any


STATE = "PACKET7_USER_REVIEW_XREF_TOC_SUCCESSOR_CANDIDATE"
ROOT_NAMES = ("MASTER_EN.md", "MASTER_EN.reconstruction.json", "MASTER_EN.qa.json")
EXPECTED_PREDECESSOR = {
    "MASTER_EN.md": (132097, "9C9119795B288525B56209B15B217748EABD7A330E91C04D0036EBCF34F238A0"),
    "MASTER_EN.reconstruction.json": (2185985, "F30D1D491A54911033226F50036E1473DABBE33854B054178DA86575CBDE2E8E"),
    "MASTER_EN.qa.json": (1210, "58B776129668760F7771F0A66CF87CA1E266920EE2E1619E7712BE536390F61D"),
}

# Visible TOC group, printed page tail, exact non-TOC graph node.
SECTION_GROUPS = (
    ("INTRODUCTION", "1", "1e7c84a4e9f5927381bc3dd4"),
    ("DRAMATIS PERSONAE", "4", "b1afc3d2767828f22a3d7b87"),
    ("START: ARKHAM", "7", "29da96049102775b4dcc2b3a"),
    ("INNSMOUTH", "11", "640be35ee56417677f8750f5"),
    ("INVESTIGATION", "13", "579f6cee9279aa85f459d268"),
    ("INTO INNSMOUTH", "22", "1e82f0c963d8a023793fa18e"),
    ("THE EPIC FINALE", "25", "9e45e6c31b8f513fdfc0cbcb"),
    ("EPILOGUE", "28", "784561a8c2d6538c46980f3f"),
    ("CHARACTERS AND MONSTERS", "29", "216abf1f13f006ed96ddabfd"),
    ("PRE-GENERATED INVESTIGATORS", "32", "cef5699cd74c24cd894040ee"),
    ("HANDOUTS", "38", "9eb21ebd1012f4d0e1572e0a"),
)

PAGE_TOKEN = re.compile(r"(?i)\bpage +[0-9]+\b")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def identity(path: str, raw: bytes) -> dict[str, Any]:
    return {"path": path, "byte_count": len(raw), "sha256": sha256(raw)}


def read_predecessor(root: Path) -> dict[str, bytes]:
    data = {name: (root / name).read_bytes() for name in ROOT_NAMES}
    for name, expected in EXPECTED_PREDECESSOR.items():
        actual = (len(data[name]), sha256(data[name]))
        if actual != expected:
            raise ValueError(f"E_PREDECESSOR_IDENTITY:{name}:{actual}")
    assets = sorted((root / "assets").glob("*"))
    if len(assets) != 38 or any(not path.is_file() for path in assets):
        raise ValueError("E_PREDECESSOR_ASSETS")
    return data


def _accepted_projection_operations(reconstruction: dict[str, Any]) -> dict[str, Any]:
    operations = reconstruction.get("projection", {}).get("operations")
    if not isinstance(operations, dict):
        raise ValueError("E_ACCEPTED_OPERATION_LEDGER")
    if len(operations.get("internal_reference_operations", [])) != 34:
        raise ValueError("E_ACCEPTED_REFERENCE_COUNT")
    if len(operations.get("toc_projection_operations", [])) != 34:
        raise ValueError("E_ACCEPTED_TOC_COUNT")
    if len(operations.get("target_anchor_operations", [])) != 42:
        raise ValueError("E_ACCEPTED_ANCHOR_COUNT")
    return operations


def _projected_spans(markdown: bytes, accepted: dict[str, Any]) -> dict[str, tuple[int, int]]:
    """Map original Packet 6 operation coordinates to accepted Packet 7 bytes."""
    flat = (
        accepted["target_anchor_operations"]
        + accepted["internal_reference_operations"]
        + accepted["toc_projection_operations"]
    )
    shift = 0
    spans: dict[str, tuple[int, int]] = {}
    for operation in sorted(flat, key=lambda row: (row["source_start_byte"], row["source_end_byte"])):
        start = operation["source_start_byte"] + shift
        after = operation["after_utf8"].encode("utf-8")
        end = start + len(after)
        if markdown[start:end] != after:
            raise ValueError(f"E_ACCEPTED_PROJECTED_SPAN:{operation['operation_id']}")
        spans[operation["operation_id"]] = (start, end)
        before = operation["before_utf8"].encode("utf-8")
        shift += len(after) - len(before)
    return spans


def _operation(family: str, start: int, end: int, before: bytes, after: bytes, **extra: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "family": family,
        "source_start_byte": start,
        "source_end_byte": end,
        "before_utf8": before.decode("utf-8"),
        "before_sha256": sha256(before),
        "after_utf8": after.decode("utf-8"),
    }
    row.update(extra)
    row["operation_id"] = "review-op-" + sha256(canonical_json(row))[:24]
    return row


def _unique_match(pattern: bytes, data: bytes, start: int = 0, end: int | None = None) -> re.Match[bytes]:
    compiled = re.compile(pattern, re.MULTILINE)
    matches = list(compiled.finditer(data, start, len(data) if end is None else end))
    if len(matches) != 1:
        raise ValueError(f"E_UNIQUE_MATCH:{pattern!r}:{len(matches)}")
    return matches[0]


def make_operations(markdown: bytes, reconstruction: dict[str, Any]) -> list[dict[str, Any]]:
    accepted = _accepted_projection_operations(reconstruction)
    accepted_spans = _projected_spans(markdown, accepted)
    changes: list[dict[str, Any]] = []

    # Restore the complete original navigation expression and replace only its
    # page token.  The one Handout operation intentionally keeps its existing
    # visible Handout number rather than using the word "link".
    ordinary = 0
    handouts = 0
    for row in accepted["internal_reference_operations"]:
        if row["target_kind"] == "HANDOUT":
            handouts += 1
            if row["after_utf8"] != "See [**Handout 1-b**](#nri-h-f8e3b2764c3b8f24c4c83bfa)":
                raise ValueError("E_HANDOUT_VISIBLE_NUMBER")
            continue
        before_expression = row["before_utf8"]
        replacement = f"[link](#{row['canonical_anchor']})"
        after_expression, count = PAGE_TOKEN.subn(replacement, before_expression)
        if count != 1:
            raise ValueError(f"E_PAGE_TOKEN_CARDINALITY:{row['operation_id']}:{count}")
        start, end = accepted_spans[row["operation_id"]]
        current = markdown[start:end]
        if current.decode("utf-8") != row["after_utf8"]:
            raise ValueError("E_ACCEPTED_REFERENCE_BINDING")
        changes.append(_operation(
            "PAGE_TOKEN_LINK",
            start,
            end,
            current,
            after_expression.encode("utf-8"),
            accepted_operation_id=row["operation_id"],
            occurrence_id=row["occurrence_id"],
            target_kind=row["target_kind"],
            canonical_anchor=row["canonical_anchor"],
            original_expression=before_expression,
        ))
        ordinary += 1
    if (ordinary, handouts) != (33, 1):
        raise ValueError(f"E_REFERENCE_CLASSES:{ordinary}:{handouts}")

    toc_end = markdown.index(b"<!-- mineru-page: 4 -->")
    for label, page, token in SECTION_GROUPS:
        anchor = f"nri-h-{token}"
        toc_pattern = rb"^## " + re.escape(f"{label} {page}".encode("utf-8")) + rb"$"
        toc_match = _unique_match(toc_pattern, markdown, 0, toc_end)
        toc_before = markdown[toc_match.start():toc_match.end()]
        toc_after = f"## [{label}](#{anchor})".encode("utf-8")
        changes.append(_operation(
            "TOC_GROUP_LINK",
            toc_match.start(),
            toc_match.end(),
            toc_before,
            toc_after,
            display_label=label,
            printed_page=page,
            canonical_anchor=anchor,
        ))

        body_pattern = rb"^## " + re.escape(label.encode("utf-8")) + rb"$"
        body_match = _unique_match(body_pattern, markdown, toc_end)
        anchor_bytes = f'<a id="{anchor}"></a>\n'.encode("utf-8")
        positions = [match.start() for match in re.finditer(re.escape(anchor_bytes), markdown)]
        if not positions:
            changes.append(_operation(
                "SECTION_ANCHOR_INSERT",
                body_match.start(),
                body_match.start(),
                b"",
                anchor_bytes,
                display_label=label,
                canonical_anchor=anchor,
            ))
        elif len(positions) == 1:
            existing = positions[0]
            if existing + len(anchor_bytes) != body_match.start():
                changes.append(_operation(
                    "SECTION_ANCHOR_MOVE_REMOVE",
                    existing,
                    existing + len(anchor_bytes),
                    anchor_bytes,
                    b"",
                    display_label=label,
                    canonical_anchor=anchor,
                ))
                changes.append(_operation(
                    "SECTION_ANCHOR_MOVE_INSERT",
                    body_match.start(),
                    body_match.start(),
                    b"",
                    anchor_bytes,
                    display_label=label,
                    canonical_anchor=anchor,
                ))
        else:
            raise ValueError(f"E_SECTION_ANCHOR_COLLISION:{anchor}")

    spans = sorted((row["source_start_byte"], row["source_end_byte"]) for row in changes)
    cursor = -1
    for start, end in spans:
        if start < cursor:
            raise ValueError("E_REMEDIATION_OPERATION_OVERLAP")
        cursor = max(cursor, end)
    return changes


def apply_operations(markdown: bytes, operations: list[dict[str, Any]]) -> bytes:
    out: list[bytes] = []
    cursor = 0
    for row in sorted(operations, key=lambda item: (item["source_start_byte"], item["source_end_byte"])):
        start, end = row["source_start_byte"], row["source_end_byte"]
        before = row["before_utf8"].encode("utf-8")
        if start < cursor:
            raise ValueError("E_REMEDIATION_OPERATION_OVERLAP")
        if markdown[start:end] != before or sha256(before) != row["before_sha256"]:
            raise ValueError(f"E_REMEDIATION_OPERATION_BINDING:{row['operation_id']}")
        out.extend((markdown[cursor:start], row["after_utf8"].encode("utf-8")))
        cursor = end
    out.append(markdown[cursor:])
    return b"".join(out)


def validate_output(predecessor_md: bytes, projected: bytes, operations: list[dict[str, Any]]) -> dict[str, Any]:
    text = projected.decode("utf-8")
    if text.count("[link](#nri-") != 33:
        raise ValueError("E_VISIBLE_LINK_COUNT")
    if text.count("See [**Handout 1-b**](#nri-h-f8e3b2764c3b8f24c4c83bfa)") != 1:
        raise ValueError("E_HANDOUT_VISIBLE_NUMBER")
    fire = "to Zadok Allen (The Fire Station, [link](#nri-h-1b70234c4ece0af6255492e8))."
    if text.count(fire) != 1:
        raise ValueError("E_FIRE_STATION_SEED_CASE")

    # The only surviving printed pages are the three external Keeper Rulebook
    # citations.  They have no target inside this document and remain literal.
    page_refs = PAGE_TOKEN.findall(text)
    if len(page_refs) != 3 or text.count("Call of Cthulhu: Keeper Rulebook.") != 3:
        raise ValueError("E_EXTERNAL_REFERENCE_CONSERVATION")

    toc_start = projected.index(b"# CONTENTS")
    toc_end = projected.index(b"<!-- mineru-page: 4 -->", toc_start)
    toc = projected[toc_start:toc_end]
    toc_fragments = re.findall(rb"\]\(#([^\)]+)\)", toc)
    if len(toc_fragments) != 45:
        raise ValueError("E_TOC_LINK_COUNT")
    for label, _page, token in SECTION_GROUPS:
        expected = f"## [{label}](#nri-h-{token})".encode("utf-8")
        if toc.count(expected) != 1:
            raise ValueError(f"E_TOC_GROUP_LINK:{label}")

    ids = re.findall(rb'<a id="([^"]+)"></a>', projected)
    fragments = re.findall(rb"\]\(#([^\)]+)\)", projected)
    if len(ids) != 50 or len(set(ids)) != 50:
        raise ValueError("E_ANCHOR_COUNT")
    if len(fragments) != 79 or any(fragment not in set(ids) for fragment in fragments):
        raise ValueError("E_FRAGMENT_RESOLUTION")
    if len(re.findall(rb"(?m)^#{1,6} ", projected)) != 155:
        raise ValueError("E_HEADING_CONSERVATION")
    if projected.count(b"<table>") != 51 or projected.count(b"<!-- table-evidence:") != 51:
        raise ValueError("E_TABLE_CONSERVATION")
    if len(re.findall(rb"!?\[[^\]]*\]\(assets/[^\)]+\)", projected)) != 38:
        raise ValueError("E_ASSET_LINK_CONSERVATION")
    if predecessor_md == projected:
        raise ValueError("E_NO_REMEDIATION")

    counts: dict[str, int] = {}
    for row in operations:
        counts[row["family"]] = counts.get(row["family"], 0) + 1
    expected_counts = {
        "PAGE_TOKEN_LINK": 33,
        "TOC_GROUP_LINK": 11,
        "SECTION_ANCHOR_INSERT": 8,
        "SECTION_ANCHOR_MOVE_REMOVE": 2,
        "SECTION_ANCHOR_MOVE_INSERT": 2,
    }
    if counts != expected_counts:
        raise ValueError(f"E_OPERATION_COUNTS:{counts}")
    return {
        "operations": len(operations),
        "operation_families": counts,
        "ordinary_page_links": 33,
        "handout_number_links": 1,
        "external_page_references": 3,
        "toc_links": 45,
        "toc_group_links": 11,
        "anchors": 50,
        "fragments": 79,
        "broken_fragments": 0,
        "headings": 155,
        "tables": 51,
        "asset_links": 38,
    }


def build_once(data: dict[str, bytes]) -> dict[str, Any]:
    predecessor_rec = json.loads(data["MASTER_EN.reconstruction.json"])
    operations = make_operations(data["MASTER_EN.md"], predecessor_rec)
    markdown = apply_operations(data["MASTER_EN.md"], operations)
    counts = validate_output(data["MASTER_EN.md"], markdown, operations)
    reconstruction = canonical_json({
        "schema": "InnsmouthMasterReconstruction.v9",
        "state": STATE,
        "predecessor": predecessor_rec,
        "user_review_remediation": {
            "rule": "replace_only_page_token_preserve_expression_and_outer_punctuation",
            "handout_rule": "keep_visible_handout_number",
            "toc_rule": "link_all_11_major_groups_and_34_existing_entries",
            "operations": operations,
            "markdown_sha256": sha256(markdown),
        },
    })
    qa = canonical_json({
        "schema": "InnsmouthMasterPackageQA.v9",
        "state": STATE,
        "inputs": [identity(name, data[name]) for name in ROOT_NAMES],
        "outputs": [identity("MASTER_EN.md", markdown)],
        "counts": counts,
        "checks": {
            "accepted_predecessor_identity": True,
            "seed_fire_station_fixed": True,
            "only_page_token_replaced": True,
            "outer_parentheses_preserved": True,
            "handout_number_visible": True,
            "all_major_toc_groups_linked": True,
            "all_fragments_resolve": True,
            "external_keeper_references_preserved": True,
            "structure_conserved": True,
        },
        "findings": [],
    })
    roots = {
        "markdown": identity("MASTER_EN.md", markdown),
        "reconstruction": identity("MASTER_EN.reconstruction.json", reconstruction),
        "qa": identity("MASTER_EN.qa.json", qa),
    }
    return {"markdown": markdown, "reconstruction": reconstruction, "qa": qa, "roots": roots, "operations": operations, "counts": counts}


def build_twice(data: dict[str, bytes]) -> dict[str, Any]:
    first = build_once(data)
    second = build_once(data)
    if first != second:
        raise ValueError("E_TWO_BUILD_IDENTITY")
    return first


def publish_once(predecessor: Path, target: Path) -> dict[str, Any]:
    stage = Path(str(target) + ".stage")
    if target.exists():
        raise ValueError("E_TARGET_EXISTS")
    if stage.exists():
        raise ValueError("E_STAGE_EXISTS")
    if target.parent != stage.parent:
        raise ValueError("E_STAGE_PARENT")
    data = read_predecessor(predecessor)
    build = build_twice(data)
    stage.mkdir(parents=False)
    try:
        (stage / "MASTER_EN.md").write_bytes(build["markdown"])
        (stage / "MASTER_EN.reconstruction.json").write_bytes(build["reconstruction"])
        (stage / "MASTER_EN.qa.json").write_bytes(build["qa"])
        shutil.copytree(predecessor / "assets", stage / "assets")
        files = sorted(path for path in stage.rglob("*") if path.is_file())
        if len(files) != 41 or len(list((stage / "assets").glob("*"))) != 38:
            raise ValueError("E_PACKAGE_INVENTORY")
        os.rename(stage, target)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise
    return {
        "target": str(target),
        "roots": build["roots"],
        "counts": build["counts"],
        "file_count": 41,
        "asset_count": 38,
        "stage_absent": not stage.exists(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predecessor", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--publish", action="store_true")
    parser.add_argument("--target", type=Path)
    args = parser.parse_args()
    if args.preflight:
        data = read_predecessor(args.predecessor)
        result = build_twice(data)
        print(json.dumps({"roots": result["roots"], "counts": result["counts"]}, ensure_ascii=False, sort_keys=True))
        print("PACKET7_USER_REVIEW_SUCCESSOR_PREFLIGHT_OK")
        return
    if args.target is None:
        raise SystemExit("--target is required with --publish")
    print(json.dumps(publish_once(args.predecessor, args.target), ensure_ascii=False, sort_keys=True))
    print("PACKET7_USER_REVIEW_SUCCESSOR_PUBLISHED")


if __name__ == "__main__":
    main()
