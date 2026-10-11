"""Fail-closed foundation for authoring Viral's reconstruction-bound v2 config.

The later B2 materializer consumes these real-input facts.  This module never
uses builder/verifier helpers as authoring truth and never writes a partial
publication contract.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
import re
from pathlib import Path
from typing import Any, Callable

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4"
EVIDENCE = ROOT / "kb_creator/working/viral/master_en/review_evidence/20260902_user_review_remediation_v1"
V1 = ROOT / "kb_creator/working/viral/master_en/publication_config_v1.json"
SOURCE_PDF = ROOT / "kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf"
COMPARISON = ROOT / "kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full/comparison/comparison.json"
TEMPORARY_CONFIG_ROOT = ROOT / "kb_creator/working/viral/master_en"
ASSET_DIGEST = re.compile(r"[0-9a-f]{64}(?=\.(?:jpg|jpeg|png))", re.IGNORECASE)
PACKAGE_ALGORITHM = "SHA-256 over ordinal UTF-8 LF relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>"
EXPECTED = {
    V1: "C16DFA975F3F05DFCE923CDD54A56B1069B9A8337C70809B0DC99771CDF63B30",
    EVIDENCE / "boundary_ledger_pages_001_040.json": "8C0A666D962C879C62B7168B60AB717EA04F833FFE728446F150F64FCB24DDAF",
    EVIDENCE / "boundary_ledger_pages_041_068.json": "8673868ED762E327517891D7C72DBA21A5C88F1A4173EBB0EFF597D30453EF13",
    EVIDENCE / "boundary_ledger_pages_069_122.json": "14338236CDB2AAE6213CCE5F36DA93C661F2DF35D9F7E96F8346C770BF00CFD1",
    EVIDENCE / "semantic_unit_review.json": "41E3F6F7AAC5970D9FCFC032926B0F5FB48E41D544414130AED85AB8672EAB78",
    EVIDENCE / "closure_report.json": "3AB47BE01FED57773A3DD3419D0CF0D2DF4658A56E813FF3B02BD5E4C8B99ACA",
}
EXPECTED_PACKAGE = (377, 41079424, "68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83")
MIGRATION_DOMAINS = (
    ("hierarchy_rows", "hierarchy", "anchor"), ("asset_rows", "assets", "asset_id"),
    ("xref_rows", "xrefs", "xref_id"), ("source_disposition_rows", "source_disposition", "page"),
    ("handout_rows", "handouts", "anchor"), ("structured_rows", "structured_content", "structure_id"),
)


class AuthoringError(ValueError):
    """Stable, no-output failure for an untrusted or incomplete authoring run."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def identity(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw), "sha256": sha256_bytes(raw)}


def canonical_row(row: dict[str, Any]) -> str:
    return sha256_bytes(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def eol_profile(raw: bytes) -> dict[str, int]:
    counts = {"lf": 0, "crlf": 0, "crcrlf": 0, "lone_cr": 0}; index = 0
    while index < len(raw):
        if raw[index:index + 3] == b"\r\r\n": counts["crcrlf"] += 1; index += 3
        elif raw[index:index + 2] == b"\r\n": counts["crlf"] += 1; index += 2
        elif raw[index:index + 1] == b"\n": counts["lf"] += 1; index += 1
        elif raw[index:index + 1] == b"\r": counts["lone_cr"] += 1; index += 1
        else: index += 1
    lines = raw.splitlines()
    return {**counts, "line_slots": len(lines), "nonblank_line_slots": sum(bool(line.strip()) for line in lines)}


def package_identity(path: Path = PACKAGE) -> dict[str, Any]:
    if not path.is_dir(): raise AuthoringError("E_V2_AUTHOR_INPUT: reconstruction package missing")
    rows = []
    for child in sorted(path.rglob("*")):
        if child.is_symlink(): raise AuthoringError("E_V2_AUTHOR_INPUT: reconstruction topology")
        if child.is_file():
            raw = child.read_bytes(); rows.append((child.relative_to(path).as_posix(), len(raw), sha256_bytes(raw)))
    # Sort the declared POSIX inventory names, not Windows Path objects; their
    # case/order comparison is not the frozen package algorithm.
    rows.sort(key=lambda row: row[0])
    payload = "".join(f"{name}\t{size}\t{digest}\n" for name, size, digest in rows).encode("utf-8")
    return {"root": path.relative_to(ROOT).as_posix(), "file_count": len(rows), "total_bytes": sum(row[1] for row in rows), "inventory_algorithm": PACKAGE_ALGORITHM, "inventory_sha256": sha256_bytes(payload)}


def verify_inputs() -> dict[str, Any]:
    for path, expected in EXPECTED.items():
        if not path.is_file() or sha256_bytes(path.read_bytes()) != expected:
            raise AuthoringError(f"E_V2_AUTHOR_INPUT: identity drift: {path.name}")
    if not SOURCE_PDF.is_file(): raise AuthoringError("E_V2_AUTHOR_INPUT: source PDF missing")
    package = package_identity()
    if tuple(package[key] for key in ("file_count", "total_bytes", "inventory_sha256")) != EXPECTED_PACKAGE:
        raise AuthoringError("E_V2_AUTHOR_INPUT: reconstruction aggregate drift")
    v1 = json.loads(V1.read_text(encoding="utf-8"))
    counts = {"hierarchy": 168, "assets": 123, "xrefs": 237, "structured_content": 29, "handouts": 41, "source_disposition": 124}
    if {key: len(v1.get(key, [])) for key in counts} != counts: raise AuthoringError("E_V2_AUTHOR_INPUT: frozen v1 domain drift")
    return {"v1": v1, "package": package, "source_pdf": identity(SOURCE_PDF)}


def approved_ledgers() -> list[dict[str, Any]]:
    """Read all three hash-bound ledgers in their published ordinal order.

    The v1 and v2 ledger dialects name the same reviewed coordinates
    differently.  Normalize those spelling differences at this boundary so a
    later interval consumer cannot silently omit every v2 unit.  The original
    artifacts remain hash-bound by ``verify_inputs``; no owner or kind is
    inferred here.
    """
    result: list[dict[str, Any]] = []
    for name in ("boundary_ledger_pages_001_040.json", "boundary_ledger_pages_041_068.json", "boundary_ledger_pages_069_122.json"):
        document = json.loads((EVIDENCE / name).read_text(encoding="utf-8"))
        if document.get("schema") not in {"kb_creator.viral_boundary_ledger.v1", "kb_creator.viral.boundary_ledger.v2"} or not isinstance(document.get("units"), list):
            raise AuthoringError("E_V2_AUTHOR_LEDGER: closed ledger schema drift")
        for raw_unit in document["units"]:
            unit = dict(raw_unit)
            if document["schema"] == "kb_creator.viral.boundary_ledger.v2":
                required = {"segments", "owner", "title", "termination", "order_key"}
                if not required <= set(unit):
                    raise AuthoringError("E_V2_AUTHOR_LEDGER: v2 normalization drift")
                unit.update({
                    "source_segments": unit["segments"],
                    # v2 `owner` is reviewed source evidence and may be a
                    # reader label (for example `Keeper Maps`), not a valid
                    # hierarchy anchor.  Keep it distinct until a later
                    # semantic-authoring seam proves an anchor binding.
                    "reviewed_owner_label": unit["owner"],
                    "title_or_label": unit["title"],
                    "termination_rule": unit["termination"],
                    "source_order_key": unit["order_key"],
                    "ledger_schema": document["schema"],
                    "ledger_kind": unit["kind"],
                })
            else:
                unit["ledger_schema"] = document["schema"]
                unit["ledger_kind"] = unit["kind"]
            if not isinstance(unit.get("source_segments"), list) or not unit["source_segments"]:
                raise AuthoringError("E_V2_AUTHOR_LEDGER: normalized segments")
            result.append(unit)
    if len({unit.get("id") for unit in result}) != len(result):
        raise AuthoringError("E_V2_AUTHOR_LEDGER: duplicate unit id")
    return result


def _line_boundaries(raw: bytes) -> list[tuple[int, int]]:
    """Raw byte offsets for splitlines slots, retaining each line terminator."""
    boundaries: list[tuple[int, int]] = []
    start = 0
    # Python's decoded splitlines is the ledger's line-slot convention.  In
    # particular CRCRLF is two slots (CR, CRLF), unlike a display-only EOL run.
    for line in raw.decode("utf-8").splitlines(keepends=True):
        end = start + len(line.encode("utf-8")); boundaries.append((start, end)); start = end
    if start != len(raw):
        raise AuthoringError("E_V2_AUTHOR_INPUT: raw line coordinate drift")
    return boundaries


def _ledger_intervals(package: Path) -> dict[int, list[tuple[int, int, dict[str, Any]]]]:
    intervals: dict[int, list[tuple[int, int, dict[str, Any]]]] = {page: [] for page in range(1, 123)}
    for unit in approved_ledgers():
        for segment in unit.get("source_segments", []):
            page = segment["page"]
            if page not in intervals:
                raise AuthoringError("E_V2_AUTHOR_LEDGER: reader scope leakage")
            raw = (package / "pages" / segment["path"]).read_bytes(); lines = _line_boundaries(raw)
            begin, end = segment["start_line"] - 1, segment["end_line"]
            decoded = raw.decode("utf-8").splitlines()
            if begin < 0 or end > len(lines) or begin >= end or sha256_bytes("\n".join(decoded[begin:end]).encode("utf-8")) != segment["sha256_lf_lines"]:
                # The v2 ledgers retain their source-review line coordinate.
                # Reconstructed raw pages can have collapsed CRCRLF slots, so
                # recover the exact reviewed range by its sealed LF-line hash.
                wanted = segment["sha256_lf_lines"]
                matches = []
                for left in range(len(decoded)):
                    for right in range(left + 1, len(decoded) + 1):
                        if sha256_bytes("\n".join(decoded[left:right]).encode("utf-8")) == wanted:
                            matches.append((left, right))
                if len(matches) != 1:
                    raise AuthoringError(f"E_V2_AUTHOR_LEDGER: source segment hash drift: {unit['id']}")
                begin, end = matches[0]
            interval = (lines[begin][0], lines[end - 1][1], unit)
            intervals[page].append(interval)
    return intervals


def source_partition(package: Path = PACKAGE) -> dict[str, list[dict[str, Any]]]:
    """Partition all raw reader bytes at every approved ledger boundary.

    Ledger intervals are overlays, rather than an alternate source.  Each
    resulting raw interval therefore has one owner, while every untouched byte
    is retained as ordinary source evidence.
    """
    pages, spans = [], []
    ledger = _ledger_intervals(package)
    for page in range(1, 123):
        relative = f"pages/page-{page:03d}.md"; raw = (package / relative).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"): raise AuthoringError(f"E_V2_AUTHOR_INPUT: BOM on page {page}")
        try: text = raw.decode("utf-8")
        except UnicodeDecodeError as error: raise AuthoringError(f"E_V2_AUTHOR_INPUT: UTF-8 page {page}") from error
        if not raw or not text: raise AuthoringError(f"E_V2_AUTHOR_INPUT: empty reader page {page}")
        cuts = {0, len(raw)}
        for start, end, _ in ledger[page]: cuts.update((start, end))
        ids = []
        for ordinal, (start, end) in enumerate(zip(sorted(cuts), sorted(cuts)[1:]), 1):
            owners = [unit for left, right, unit in ledger[page] if left <= start and end <= right]
            # Overlapping reviewed units are legal analytical overlays.  Their
            # deterministic first source order is the exclusive partition owner.
            unit = min(owners, key=lambda item: (item["source_order_key"], item["id"])) if owners else None
            raw_piece = raw[start:end]; start_char = len(raw[:start].decode("utf-8")); end_char = len(raw[:end].decode("utf-8"))
            is_asset = bool(unit and unit.get("kind") == "asset_ownership")
            event_id = f"event-p{page:03d}-{ordinal:03d}"
            span_id = f"span-p{page:03d}-{ordinal:03d}"; ids.append(span_id)
            spans.append({"span_id": span_id, "page": page, "source_path": relative, "start_byte": start, "end_byte": end, "start_char": start_char, "end_char": end_char, "raw_sha256": sha256_bytes(raw_piece), "raw_text_sha256": sha256_bytes(raw_piece.decode("utf-8").encode("utf-8")), "classification": "asset_reference_source" if is_asset else ("reviewed_structured_source" if unit else "retained_text"), "owner_kind": "asset" if is_asset else "event", "owner_id": unit["id"] if is_asset else event_id, "decision_ref": (unit.get("registry_refs") or [None])[0] if unit else None})
        pages.append({"page": page, "path": relative, "bytes": len(raw), "sha256": sha256_bytes(raw), "encoding": "utf-8-no-bom", "eol_profile": eol_profile(raw), "span_ids": ids})
    return {"pages": pages, "spans": spans}


def source_graph() -> dict[str, Any]:
    """Materialize B1b's complete source graph without claiming a v2 config."""
    bound = verify_inputs(); partition = source_partition(); v1 = bound["v1"]
    spans = partition["spans"]; events: list[dict[str, Any]] = []
    for ordinal, span in enumerate(sorted((row for row in spans if row["owner_kind"] == "event"), key=lambda row: (row["page"], row["start_byte"]))):
        raw = (PACKAGE / span["source_path"]).read_bytes(); text = raw[span["start_byte"]:span["end_byte"]].decode("utf-8")
        events.append({"event_id": span["owner_id"], "type": "text_fragment", "page": span["page"], "order_key": [span["page"], span["start_byte"], 2, ordinal], "anchor": None, "content": text, "fragment_id": span["span_id"], "source_span_ids": [span["span_id"]], "source_operation": "emit_exact", "payload_bindings": [{"json_pointer": "/content", "source_slices": [{"span_id": span["span_id"], "start_char": span["start_char"], "end_char": span["end_char"]}], "joiner": "", "recovery_id": None}], "reviewed_unit_id": None})
    hierarchy = []
    for row in v1["hierarchy"]:
        pages = [page for page in row["source_pages"] if page <= 122]
        # Two audit-only v1 headings point at excluded advertising pages.  Keep
        # their inherited hierarchy identity, but bind their reader projection
        # to the root reader source rather than leaking p123/124 coordinates.
        if not pages:
            pages = [1]
        kind = row["assembly_binding"]["kind"]
        representation = "anchor_only" if kind == "generated" else "heading"
        hierarchy.append({"anchor": row["anchor"], "parent_anchor": row["parent_anchor"] or None, "level": None if representation == "anchor_only" else row["level"], "toc_entry": row["toc_entry"], "semantic_role": row["semantic_role"], "source_pages": pages, "source_title": row["title"], "reader_title": row["title"], "representation": representation, "reviewed_title_transformation": None, "migration_row_id": f"hierarchy_rows:hierarchy:{row['anchor']}"})
    recoveries = []
    for text, page, method in (("Cursed Plague Zombies", 66, "native_text_and_visual"), ("New Mythos Tome", 67, "visual")):
        recoveries.append({"recovery_id": f"recovery-{page}-{text.lower().replace(' ', '-')}", "source_pdf_identity": bound["source_pdf"], "physical_page": page, "extraction_method": method, "source_text": text, "source_text_sha256": sha256_bytes(text.encode("utf-8")), "evidence_identity": identity(EVIDENCE / "semantic_unit_review.json"), "target_event_id": None, "placement": "before_event", "decision_ref": "PROC-014"})
    typed_kinds = {"callout", "ordered_callout", "table", "equipment_card", "creature_statblock", "inline_run_in", "full_page_map", "physical_page_pair"}
    kind_aliases = {"callout_series": "callout", "logical_table": "table", "run_in_series": "inline_run_in"}
    typed = [{"unit_id": unit["id"], "kind": kind_aliases.get(unit["kind"], unit["kind"]), "ledger_kind": unit["ledger_kind"], "owner_anchor": unit.get("final_owner_anchor"), "source_pages": unit.get("source_pages", []), "structured": unit.get("structured"), "source_segments": unit.get("source_segments", [])} for unit in approved_ledgers() if kind_aliases.get(unit.get("kind"), unit.get("kind")) in typed_kinds]
    return {"source_partition": partition, "events": events, "hierarchy": hierarchy, "typed_units": typed, "source_recoveries": recoveries, "ledger_unit_count": len(approved_ledgers())}


def migration_baseline(v1: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for target_key, v1_key, identifier in MIGRATION_DOMAINS:
        rows = []
        for item in v1[v1_key]:
            source_id = f"{v1_key}:{item[identifier]}"
            excluded = (v1_key == "source_disposition" and item["page"] in {123, 124}) or (v1_key == "assets" and item["source_page"] in {123, 124})
            rows.append({"source_id": source_id, "source_row_sha256": canonical_row(item), "outcome": "excluded_advertising" if excluded else "retained_unchanged", "final_target_ids": [] if excluded else [f"pending_a3:{source_id}"], "decision_ref": "OUT-008" if excluded else None})
        result[target_key] = rows
    result["inputs"] = {"frozen_v1_config": identity(V1), "decision_evidence": [{**identity(EVIDENCE / "semantic_unit_review.json"), "kind": "kb_creator.semantic_unit_review.v2"}, {**identity(EVIDENCE / "closure_report.json"), "kind": "kb_creator.semantic_unit_closure.v2"}]}
    result["new_reviewed_targets"] = []
    return result


def foundation() -> dict[str, Any]:
    bound = verify_inputs(); v1 = bound["v1"]; dispositions = []
    for item in v1["source_disposition"]:
        page = item["page"]; excluded = page in {123, 124}
        dispositions.append({"page": page, "audit_disposition": "reconstructed", "publication_disposition": "excluded_advertising" if excluded else "reader", "publish_reader_content": not excluded, "decision_date": "2026-09-02", "reason": "advertising excluded from reader" if excluded else "accepted reconstruction reader page", "page_markdown": identity(PACKAGE / "pages" / f"page-{page:03d}.md")})
    return {"schema": "kb_creator.master_en_publication.v2", "scenario_id": "viral", "document": {"audit_scope": list(range(1, 125)), "reader_scope": list(range(1, 123)), "generated_navigation": {"operation": "generated_navigation_replaces_source_toc", "source_identity": "B1 foundation; reviewed projection materialization pending"}, "source_pdf": bound["source_pdf"], "reconstruction_package": bound["package"]}, "source_disposition": dispositions, "source_partition": source_partition(), "migration": migration_baseline(v1)}


def asset_xref_readiness() -> dict[str, Any]:
    """Bind B1c's inherited asset/xref inventories before any v2 write.

    This is deliberately an author-side audit, not a builder-derived truth.  It
    makes the remaining closure requirement measurable: only ledger-declared
    image-reference spans may own reader asset placement, while all 123 frozen
    assets and all 237 xrefs still require a final, exact migration target.
    """
    bound = verify_inputs()
    graph = source_graph()
    assets = bound["v1"]["assets"]
    xrefs = bound["v1"]["xrefs"]
    asset_spans = [span for span in graph["source_partition"]["spans"] if span["owner_kind"] == "asset"]
    if len({row["asset_id"] for row in assets}) != 123 or len({row["xref_id"] for row in xrefs}) != 237:
        raise AuthoringError("E_V2_AUTHOR_ASSET_XREF_INVENTORY_DRIFT")
    if any(row["source_page"] not in range(1, 125) for row in assets):
        raise AuthoringError("E_V2_AUTHOR_ASSET_XREF_SCOPE_DRIFT")
    # Frozen v1 may retain audit-only advertising rows as reader assets.  The
    # immutable input is not drift; B1c must explicitly migrate those rows to
    # excluded_advertising before any reader event or copy can be emitted.
    excluded = [row for row in assets if row["source_page"] in {123, 124}]
    by_digest = {Path(row["source_path"]).stem.upper(): row for row in assets if isinstance(row.get("source_path"), str)}
    bindings = []
    for span in asset_spans:
        raw = (PACKAGE / span["source_path"]).read_bytes()[span["start_byte"]:span["end_byte"]].decode("utf-8")
        matches = ASSET_DIGEST.findall(raw)
        if len(matches) != 1 or matches[0].upper() not in by_digest:
            raise AuthoringError("E_V2_AUTHOR_ASSET_SPAN_BINDING")
        asset = by_digest[matches[0].upper()]
        bindings.append({"ledger_unit_id": span["owner_id"], "span_id": span["span_id"], "asset_id": asset["asset_id"], "source_page": span["page"], "source_sha256": span["raw_sha256"]})
    if len({row["asset_id"] for row in bindings}) != len(bindings):
        raise AuthoringError("E_V2_AUTHOR_ASSET_SPAN_DUPLICATE")
    return {
        "asset_count": len(assets),
        "xref_count": len(xrefs),
        "asset_owned_span_count": len(asset_spans),
        "asset_owned_unit_ids": sorted({span["owner_id"] for span in asset_spans}),
        "reader_asset_count": sum(row["representation"] == "reader" and row["source_page"] not in {123, 124} for row in assets),
        "evidence_asset_count": sum(row["representation"] == "evidence_only" for row in assets),
        "excluded_advertising_asset_ids": [row["asset_id"] for row in excluded],
        "asset_span_bindings": bindings,
        "pending_asset_targets": [f"pending_a3:assets:{row['asset_id']}" for row in assets],
        "pending_xref_targets": [f"pending_a3:xrefs:{row['xref_id']}" for row in xrefs],
    }


def asset_b1c4_audit() -> dict[str, Any]:
    """Derive the B1c4 asset evidence partition directly from frozen inputs.

    This deliberately returns facts only: it never creates a v2 config, a
    render, or candidate bytes.  The builder and verifier independently repeat
    these checks when a public temporary config is supplied.
    """
    bound = verify_inputs(); v1 = bound["v1"]
    manifest_path = PACKAGE / "ASSET_MANIFEST.json"
    if not COMPARISON.is_file() or sha256_bytes(COMPARISON.read_bytes()) != "5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0":
        raise AuthoringError("E_V2_AUTHOR_ASSET_EVIDENCE")
    if sha256_bytes(manifest_path.read_bytes()) != "914A2C8B46401830EDBDEADDDDA24C7A8C0B6442F2775C439A79CC5529D283E9":
        raise AuthoringError("E_V2_AUTHOR_ASSET_EVIDENCE")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = manifest.get("assets")
    if not isinstance(rows, list):
        raise AuthoringError("E_V2_AUTHOR_ASSET_EVIDENCE")
    by_digest = {row.get("sha256", "").upper(): row for row in rows}
    frozen = v1["assets"]
    if len(frozen) != 123 or len(by_digest) != 121:
        raise AuthoringError("E_V2_AUTHOR_ASSET_INVENTORY")
    excluded = {row["asset_id"] for row in frozen if row["source_page"] in {123, 124}}
    reclassified = {
        "viral-accepted-6acc049ed2ad40ebed064312a87ddfce5a404f4fc2487ea1721c656ed541c419",
        "viral-accepted-647b583cd53fbfdaab7ac6d9643a81bbd5145c125d628c7074b02db0c9f7888b",
        "viral-accepted-eda9c6f6d6ef94ed41034cd12401547ed37101ef2f8b1ebf30d9602b87db71ab",
        "viral-accepted-21704f0d57843965013f5eccfa36bcd64321dcc1513cd7d99dead8627d58994e",
        "viral-accepted-b2ba43b7e57f4c9972780be961deab50d72ea311f795285da15712ba29b6e30e",
        "viral-accepted-af48429e4ab502e7fc33a545039dab60a3e4e28a8c03a29f56ff57b9280cdd12",
        "viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541",
        "viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d",
        "viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc",
        "viral-accepted-5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b",
        "viral-accepted-331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3",
        "viral-accepted-92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50",
        "viral-accepted-07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4",
        "viral-accepted-9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f",
        "viral-accepted-1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8",
        "viral-accepted-dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166",
    }
    rebound = {
        "viral-accepted-b90cb9a3752383888c733905588e9c3859b113e47f1f457057c72e33689a7585",
        "viral-accepted-da0cac1c9c0c880a75d3be69c59e965d0b7b0f223f16a077072786c8af30083e",
    }
    if len(excluded) != 6 or len(reclassified) != 16 or not reclassified.isdisjoint(excluded):
        raise AuthoringError("E_V2_AUTHOR_ASSET_PARTITION")
    audit=[]
    for row in frozen:
        aid=row["asset_id"]; digest=row.get("sha256", "").upper(); source=by_digest.get(digest)
        if aid in excluded:
            outcome, disposition = "excluded_advertising", None
        elif aid in reclassified:
            outcome, disposition = "reclassified", "evidence_only"
        elif aid in rebound:
            outcome, disposition = "retained_rebound", "reader"
        else:
            outcome, disposition = "retained_unchanged", row["representation"]
        if source is not None:
            path=PACKAGE / source["stored_path"]
            if not path.is_file() or sha256_bytes(path.read_bytes()) != digest:
                raise AuthoringError("E_V2_AUTHOR_ASSET_BINARY")
            with Image.open(path) as image:
                dimensions={"width":image.width,"height":image.height}
                media_type=image.get_format_mimetype()
            binary={"path":path.relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":digest,"media_type":media_type,"dimensions":dimensions}
        else:
            binary=None
        audit.append({"asset_id":aid,"source_page":row["source_page"],"outcome":outcome,"disposition":disposition,"binary":binary})
    counts={key:sum(row["outcome"]==key for row in audit) for key in ("retained_unchanged","retained_rebound","reclassified","excluded_advertising")}
    if counts != {"retained_unchanged":99,"retained_rebound":2,"reclassified":16,"excluded_advertising":6}:
        raise AuthoringError("E_V2_AUTHOR_ASSET_PARTITION")
    return {"asset_manifest_identity":identity(manifest_path),"comparison_identity":identity(COMPARISON),"rows":audit,"counts":counts}


def asset_b1c4_projection() -> list[dict[str, Any]]:
    """Closed B1c4 inventory projection; declaration only, never emission."""
    audit = asset_b1c4_audit(); output=[]
    manifest_path = PACKAGE / "ASSET_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_by_digest = {row["sha256"].upper(): row for row in manifest["assets"]}
    comparison = json.loads(COMPARISON.read_text(encoding="utf-8"))
    span_by_asset = {row["asset_id"]: row for row in asset_xref_readiness()["asset_span_bindings"]}
    partition_spans = {row["span_id"]: row for row in source_partition()["spans"]}

    def canonical(value: Any) -> str:
        return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))

    def render_provenance(page: int) -> dict[str, Any]:
        return {
            "kind": "reviewed_provisional_full_page", "source_pdf_identity": identity(SOURCE_PDF),
            "physical_page": page, "page_index_zero_based": page - 1,
            "region": {"kind": "full_media_box", "points": [0, 0, 612, 792]},
            "render_recipe": {"tool": "pdftoppm", "first_page": page, "last_page": page,
                              "dpi": 200, "format": "png", "box": "media_box",
                              "rotation": "source_applied", "color": "rgb", "background": "white",
                              "alpha": False, "metadata": "stripped"},
            "output_media_type": "image/png", "output_dimensions": {"width": 1700, "height": 2200},
            "quality_stage": "provisional_full_page",
        }

    def path_provenance(row: dict[str, Any]) -> dict[str, Any]:
        digest = row["binary"]["sha256"]
        manifest_row = manifest_by_digest[digest]
        span_binding = span_by_asset.get(row["asset_id"])
        if span_binding:
            span = partition_spans[span_binding["span_id"]]
            raw = (PACKAGE / span["source_path"]).read_bytes()[span["start_byte"]:span["end_byte"]]
            if raw.count(digest.lower().encode("ascii")) != 1 or not raw.decode("utf-8").strip().startswith("!["):
                raise AuthoringError("E_V2_AUTHOR_ASSET_PROVENANCE")
            return {"kind": "markdown_image_reference", "span_id": span["span_id"],
                    "page_markdown_identity": identity(PACKAGE / span["source_path"]),
                    "start_byte": span["start_byte"], "end_byte": span["end_byte"],
                    "start_char": span["start_char"], "end_char": span["end_char"],
                    "marker_sha256": sha256_bytes(raw)}
        blocks = []
        for selected_view, view in comparison["views"].items():
            for block in view["blocks"]:
                if manifest_row["source_path"] in block.get("assets", []):
                    blocks.append((selected_view, block))
        selected = [(view, block) for view, block in blocks if view == manifest_row["view"]]
        if len(selected) != 1:
            raise AuthoringError("E_V2_AUTHOR_ASSET_PROVENANCE")
        selected_view, block = selected[0]
        return {"kind": "visual_region", "asset_manifest_identity": identity(manifest_path),
                "asset_manifest_row_sha256": canonical(manifest_row), "comparison_identity": identity(COMPARISON),
                "selected_view": selected_view, "source_asset_reference": manifest_row["source_path"],
                "raw_index": block["raw_index"], "block_type": block["type"], "source_page": block["source_page"],
                "bbox": block["bbox"], "comparison_block_sha256": canonical(block)}

    for row in audit["rows"]:
        if row["outcome"] == "excluded_advertising":
            continue
        item={"asset_id":row["asset_id"],"disposition":row["disposition"],"source_page":row["source_page"],"binary":row["binary"],"provenance":path_provenance(row) if row["binary"] else render_provenance(row["source_page"]),"migration_outcome":row["outcome"]}
        output.append(item)
    pages=(106,107,112,114,116,118,120,122,26)
    names=("map-ground-floor-basement","map-ground-floor-basement","pregen-marco-back","pregen-corrina-back","pregen-enoch-back","pregen-peter-back","pregen-ku-hyeon-back","pregen-blank-back","isola-di-malamente-opening")
    for page,name in zip(pages,names):
        output.append({"asset_id":f"viral-provisional-{name}-page-{page}","disposition":"reader","source_page":page,"binary":None,"provenance":render_provenance(page),"migration_outcome":"new_reviewed_target"})
    if len(output)!=126 or sum(row["disposition"]=="reader" for row in output)!=94 or sum(row["disposition"]=="evidence_only" for row in output)!=32:
        raise AuthoringError("E_V2_AUTHOR_ASSET_PROJECTION")
    return output


MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")


def _source_text(value: str) -> str:
    """Normalize only comparison-safe prose, never a Markdown marker offset."""
    return " ".join(MARKDOWN_IMAGE.sub(" ", value).split())


def _normalized_with_offsets(value: str) -> tuple[str, list[int]]:
    """Return normalized source prose and its original character coordinates."""
    marker_starts = {match.start(): match for match in MARKDOWN_IMAGE.finditer(value)}
    characters: list[tuple[str, int]] = []
    index = 0
    while index < len(value):
        marker = marker_starts.get(index)
        if marker is not None:
            characters.append((" ", index)); index = marker.end(); continue
        characters.append((value[index], index)); index += 1
    normalized, offsets, pending_space = [], [], None
    for character, original in characters:
        if character.isspace():
            pending_space = original if normalized else None
        else:
            if pending_space is not None:
                normalized.append(" "); offsets.append(pending_space); pending_space = None
            normalized.append(character); offsets.append(original)
    return "".join(normalized), offsets


def resolve_asset_source_order(
    *,
    comparison: dict[str, Any],
    manifest_assets: list[dict[str, Any]],
    reader_assets: list[dict[str, Any]],
    events: list[dict[str, Any]],
    physical_units: list[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Derive conservative reader-asset order from one selected MinerU view.

    Raw indexes are meaningful only inside their selected view.  A following
    comparison text block becomes anchor evidence only when its complete
    normalized text occurs exactly once in one non-image reader event.  An
    internal occurrence is *not* a placement: it returns a required split
    coordinate. Missing or ambiguous evidence is reported as such; this
    function never substitutes a page-end marker position or inferred owner.
    """
    views = comparison.get("views")
    if not isinstance(views, dict):
        raise AuthoringError("E_V2_AUTHOR_SOURCE_ORDER: comparison views")
    event_text: list[tuple[int, str, list[int], dict[str, Any]]] = []
    for event in events:
        if event.get("type") == "asset" or not isinstance(event.get("event_id"), str):
            continue
        text = event.get("content")
        if isinstance(text, str):
            normalized, offsets = _normalized_with_offsets(text)
            if normalized:
                event_text.append((event.get("page"), normalized, offsets, event))
    blocks_by_view: dict[str, list[dict[str, Any]]] = {}
    asset_blocks: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for view_name, view in views.items():
        blocks = view.get("blocks") if isinstance(view, dict) else None
        if not isinstance(blocks, list):
            raise AuthoringError("E_V2_AUTHOR_SOURCE_ORDER: comparison blocks")
        ordered = sorted(blocks, key=lambda block: block.get("raw_index", -1))
        if any(not isinstance(block.get("raw_index"), int) for block in ordered):
            raise AuthoringError("E_V2_AUTHOR_SOURCE_ORDER: raw index")
        blocks_by_view[view_name] = ordered
        for block in ordered:
            for source_path in block.get("assets", []):
                asset_blocks.setdefault((view_name, source_path), []).append(block)

    physical_by_page: dict[int, list[dict[str, Any]]] = {}
    for unit in physical_units:
        for slot, page in enumerate(unit.get("pages", [])):
            physical_by_page.setdefault(page, []).append({"unit_id": unit["unit_id"], "slot": slot})
    rows = []
    for asset in reader_assets:
        asset_id = asset["asset_id"]
        physical = physical_by_page.get(asset["source_page"], [])
        if physical:
            if len(physical) != 1:
                raise AuthoringError("E_V2_AUTHOR_SOURCE_ORDER: physical unit collision")
            rows.append({"asset_id": asset_id, "status": "resolved_physical_unit", "reason": "approved_physical_unit_page_order", "source_page": asset["source_page"], "source_order": [asset["source_page"], physical[0]["slot"]], "physical_unit": physical[0], "placement": None})
            continue
        if asset.get("binary") is None:
            rows.append({"asset_id": asset_id, "status": "ambiguous", "reason": "nonbinary_outside_approved_physical_unit", "source_page": asset["source_page"], "source_order": None, "placement": None})
            continue
        digest = asset["binary"]["sha256"]
        provenance = asset.get("provenance", {})
        candidates = [row for row in manifest_assets if row.get("sha256", "").upper() == digest]
        if provenance.get("kind") == "visual_region":
            if provenance.get("source_page") != asset["source_page"]:
                raise AuthoringError("E_V2_AUTHOR_SOURCE_ORDER: provenance page")
            candidates = [row for row in candidates if row.get("view") == provenance.get("selected_view") and row.get("source_path") == provenance.get("source_asset_reference")]
        if len(candidates) != 1:
            rows.append({"asset_id": asset_id, "status": "ambiguous", "reason": "ambiguous_manifest_identity_scope", "source_page": asset["source_page"], "source_order": None, "placement": None})
            continue
        manifest = candidates[0]
        if manifest is None:
            raise AuthoringError("E_V2_AUTHOR_SOURCE_ORDER: manifest identity")
        view_name = manifest.get("view")
        source_path = manifest.get("source_path")
        blocks = asset_blocks.get((view_name, source_path), [])
        if len(blocks) != 1:
            rows.append({"asset_id": asset_id, "status": "ambiguous", "reason": "missing_or_duplicate_selected_view_asset_block", "source_page": asset["source_page"], "source_order": None, "placement": None})
            continue
        block = blocks[0]
        ordered = blocks_by_view[view_name]
        position = ordered.index(block)
        anchor_block = None
        for next_block in ordered[position + 1:]:
            if next_block.get("type") in {"image", "page_number"}:
                continue
            text = next_block.get("text")
            if not isinstance(text, str) or not (normalized := _source_text(text)):
                continue
            anchor_block = next_block
            break
        source_order = [asset["source_page"], block["raw_index"]]
        if anchor_block is None:
            rows.append({"asset_id": asset_id, "status": "ambiguous", "reason": "no_immediate_following_text_block", "source_page": asset["source_page"], "selected_view": view_name, "source_order": source_order, "placement": None})
            continue
        matches = []
        for event_page, event_value, offsets, event in event_text:
            if event_page != anchor_block.get("source_page"):
                continue
            start = event_value.find(normalized)
            if start >= 0:
                occurrences = event_value.count(normalized)
                matches.append((event, offsets, start, occurrences))
        if len(matches) != 1:
            rows.append({"asset_id": asset_id, "status": "ambiguous", "reason": "ambiguous_exact_immediate_text_anchor", "source_page": asset["source_page"], "selected_view": view_name, "source_order": source_order, "anchor_raw_index": anchor_block["raw_index"], "placement": None})
        elif matches[0][3] != 1:
            rows.append({"asset_id": asset_id, "status": "ambiguous", "reason": "repeated_exact_text_within_event", "source_page": asset["source_page"], "selected_view": view_name, "source_order": source_order, "anchor_raw_index": anchor_block["raw_index"], "placement": None})
        else:
            event, offsets, start, _ = matches[0]
            start_char = offsets[start]; end_char = offsets[start + len(normalized) - 1] + 1
            start_byte = len(event["content"][:start_char].encode("utf-8")); end_byte = len(event["content"][:end_char].encode("utf-8"))
            evidence = {"event_id": event["event_id"], "start_char": start_char, "end_char": end_char, "start_byte": start_byte, "end_byte": end_byte, "anchor_raw_index": anchor_block["raw_index"]}
            if start_char == 0:
                rows.append({"asset_id": asset_id, "status": "placement_ready", "reason": "exact_immediate_text_at_event_start", "source_page": asset["source_page"], "selected_view": view_name, "source_order": source_order, "anchor_evidence": evidence, "placement": {"before_event": event["event_id"]}})
            else:
                rows.append({"asset_id": asset_id, "status": "needs_event_split", "reason": "exact_immediate_text_inside_event", "source_page": asset["source_page"], "selected_view": view_name, "source_order": source_order, "anchor_evidence": evidence, "placement": None})
    # Shared gaps retain source order by their selected-view raw index.  The
    # page is not enough: p31 -> p32 is a valid same-view sequence.
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        placement = row.get("placement")
        if placement and row.get("selected_view"):
            grouped.setdefault((row["selected_view"], placement["before_event"]), []).append(row)
    for group in grouped.values():
        for ordinal, row in enumerate(sorted(group, key=lambda item: item["source_order"][1])):
            row["gap_ordinal"] = ordinal
    counts = {status: sum(row["status"] == status for row in rows) for status in ("placement_ready", "needs_event_split", "resolved_physical_unit", "ambiguous")}
    return {"rows": rows, "counts": counts, "reasons": {reason: sum(row["reason"] == reason for row in rows) for reason in sorted({row["reason"] for row in rows})}}


def asset_source_order_readiness() -> dict[str, Any]:
    """Real-input source-order audit consumed by the next asset authoring seam."""
    manifest = json.loads((PACKAGE / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))
    projection = asset_b1c4_projection()
    graph = _author_b1c3()
    physical_units = []
    for unit in approved_ledgers():
        if unit["kind"] in {"full_page_map", "physical_page_pair"}:
            physical_units.append({"unit_id": unit["id"], "pages": [segment["page"] for segment in unit["source_segments"]]})
    return resolve_asset_source_order(
        comparison=json.loads(COMPARISON.read_text(encoding="utf-8")),
        manifest_assets=manifest["assets"],
        reader_assets=[row for row in projection if row["disposition"] == "reader"],
        events=graph["events"],
        physical_units=physical_units,
    )


def _physical_units() -> list[dict[str, Any]]:
    return [
        {"unit_id": unit["id"], "pages": [segment["page"] for segment in unit["source_segments"]]}
        for unit in approved_ledgers()
        if unit["kind"] in {"full_page_map", "physical_page_pair"}
    ]


def split_events_at_asset_anchor_evidence(events: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Split coarse text events only at resolver-proven UTF-8 byte offsets.

    This is deliberately an author-side preparation seam: it retains all bytes
    and never chooses a placement.  Later projection replaces the temporary
    event identities while rebinding source spans, typed units and assets.
    """
    cuts: dict[str, set[int]] = {}
    for row in rows:
        if row.get("status") != "needs_event_split":
            continue
        evidence = row.get("anchor_evidence")
        if not isinstance(evidence, dict) or not isinstance(evidence.get("event_id"), str) or not isinstance(evidence.get("start_byte"), int):
            raise AuthoringError("E_V2_AUTHOR_ASSET_SPLIT: malformed resolver evidence")
        cuts.setdefault(evidence["event_id"], set()).add(evidence["start_byte"])
    refined: list[dict[str, Any]] = []
    for event in events:
        offsets = sorted(cuts.get(event["event_id"], set()))
        if not offsets:
            refined.append(event)
            continue
        content = event.get("content")
        if event.get("type") not in {"text_fragment", "heading"} or not isinstance(content, str):
            raise AuthoringError("E_V2_AUTHOR_ASSET_SPLIT: non-text event")
        raw = content.encode("utf-8")
        if any(offset <= 0 or offset >= len(raw) for offset in offsets):
            raise AuthoringError("E_V2_AUTHOR_ASSET_SPLIT: out-of-range evidence")
        boundaries = [0, *offsets, len(raw)]
        pieces = [raw[left:right].decode("utf-8") for left, right in zip(boundaries, boundaries[1:])]
        if "".join(pieces) != content:
            raise AuthoringError("E_V2_AUTHOR_ASSET_SPLIT: non-character boundary")
        for ordinal, piece in enumerate(pieces, 1):
            # A legacy coarse heading event may contain source prose after its
            # heading bytes. Retain heading identity for the first piece only;
            # later pieces are ordinary source text until typed authoring gives
            # them their reviewed representation.
            kind = event["type"] if ordinal == 1 else "text_fragment"
            refined.append({**event, "event_id": f"{event['event_id']}-asset-split-{ordinal:02d}", "type": kind, "content": piece})
    return refined


def asset_source_order_after_exact_splits() -> dict[str, Any]:
    """Re-run only metadata ordering after all currently proven coarse splits."""
    manifest = json.loads((PACKAGE / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))
    assets = asset_b1c4_projection()
    graph = _author_b1c3()
    initial = resolve_asset_source_order(
        comparison=json.loads(COMPARISON.read_text(encoding="utf-8")),
        manifest_assets=manifest["assets"], reader_assets=[row for row in assets if row["disposition"] == "reader"],
        events=graph["events"], physical_units=_physical_units(),
    )
    refined_events = split_events_at_asset_anchor_evidence(graph["events"], initial["rows"])
    result = resolve_asset_source_order(
        comparison=json.loads(COMPARISON.read_text(encoding="utf-8")),
        manifest_assets=manifest["assets"], reader_assets=[row for row in assets if row["disposition"] == "reader"],
        events=refined_events, physical_units=_physical_units(),
    )
    return {**result, "initial_counts": initial["counts"], "refined_event_count": len(refined_events)}


def _standalone_title_event(events: list[dict[str, Any]], page: int, title: str) -> dict[str, Any]:
    """Find one reviewed title line, never a prose substring or OCR variant."""
    pattern = re.compile(rf"(?m)^\s*#*\s*{re.escape(title)}\s*#*\s*$")
    matches = [event for event in events if event.get("page") == page and isinstance(event.get("content"), str) and pattern.search(event["content"])]
    if len(matches) != 1:
        raise AuthoringError(f"E_V2_AUTHOR_ASSET_TITLE: {page}:{title}")
    return matches[0]


def reviewed_remaining_asset_anchors(events: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Resolve the finite post-split set using reviewed standalone/physical facts.

    This table deliberately contains exact source titles, pages and declared
    hierarchy anchors. It is not a nearest-heading fallback and does not use
    OCR descriptions as reader prose.
    """
    title_cases = {
        "viral-accepted-290e0d241064519a8e796429310676557b8a7e50bd2224341c7ba3d3de96ec54": (17, "One Night in Perla", "viral-one-night-in-perla"),
        "viral-accepted-bc2ae2b3751eaf9754f625794f2d4648a03308dc3dc1042add097cc3649306b0": (25, "Padre Angelo", "viral-one-night-in-perla-npcs-padre-angelo"),
        "viral-accepted-b90cb9a3752383888c733905588e9c3859b113e47f1f457057c72e33689a7585": (32, "Prologue", "viral-isola-prologue"),
        "viral-accepted-da0cac1c9c0c880a75d3be69c59e965d0b7b0f223f16a077072786c8af30083e": (32, "Prologue", "viral-isola-prologue"),
        "viral-accepted-87d8a9e48a47663469f8ae771e291ed10f27cb13f6533d80bd3b569ad7c73ffd": (49, "Hastalÿk Awakens", "viral-isola-hastalyk-awakens"),
        "viral-accepted-81953e331e0b27630c228051831a510c123801aa360c1f6d0fa82d66516ee677": (66, "The Plague Monk", "viral-appendix-new-mythos-horrors-plague-monk"),
        "viral-accepted-faaf56706aeb8cc15c6cfeb89bf7731b313ccdfde78f28b12da65b123d355bcd": (100, "The Witch Board", "viral-handout-34"),
        "viral-accepted-84f3fbba13df63026fc147880fa903b708f67969bb85a2e8ffd7ae95bc921172": (100, "Book Fragment", "viral-handout-35"),
        "viral-accepted-76216221d1c4ed443deccf0a9e64c82ea0084ffc07ae033af3b43e69242b1b84": (102, "Hastalÿk Rises", "viral-handout-38"),
        "viral-accepted-7eb3303bc8a34e16d5891aa781a21297a022e028c029fa8e0d0549f445703fe5": (110, "Secret Underground", "viral-keeper-map-secret-underground"),
    }
    resolved = {}
    for asset_id, (page, title, anchor) in title_cases.items():
        event = _standalone_title_event(events, page, title)
        resolved[asset_id] = {"anchor": anchor, "placement_event_id": event["event_id"]}
    # Whole-page maps are physical units: their source page is the evidence,
    # not a fabricated next-page prose anchor.
    resolved["viral-accepted-9edcd9b27c46e8d689d4baeff43a55497376a581d87cf1e9ad8a0ea9dd63c28a"] = {"anchor": "viral-keeper-map-ground-floor-basement", "physical_unit_id": "viral-map-ground-floor-basement"}
    resolved["viral-accepted-00d84a08f0f7ef0b634da16d22f1832b3e099350a451425c5b2642428fe8f4b9"] = {"anchor": "viral-keeper-map-secret-underground", "physical_unit_id": "viral-map-secret-underground"}
    resolved["viral-render-cover-front"] = {"anchor": "viral", "document_boundary": "start"}
    resolved["viral-provisional-isola-di-malamente-opening-page-26"] = {
        "anchor": "viral-isola-di-malamente",
        "placement_event_id": "heading:viral-isola-di-malamente",
        "relation": "before_event",
        "source_order": {"kind": "physical_unit_page_slot", "unit_id": "page-opening:viral-isola-di-malamente", "page_slot": 0},
    }
    # Reviewed seed corrections are exact source-occurrence bindings.  They
    # deliberately name both the asset and its only permitted target.
    exact = {
        "viral-accepted-4592e580aba8b9bad7a83eb2acf44e0480005e48b034ecd1ac436860efdbd137": {"anchor": "viral-introduction", "placement_event_id": "heading:viral-introduction", "relation": "before_event"},
        "viral-accepted-6e1d78ee26178218de74fd8203ef772eb3e8f4951ea6e419a0a00e25051b8237": {"anchor": "viral-appendix-new-mythos-horrors-reliquae", "placement_event_id": "heading:viral-appendix-new-mythos-horrors-reliquae", "relation": "after_event"},
        "viral-accepted-2fbd31994da00cc5320dccf115f2aae8da89b5e5997e93ad5f853afbf13bad03": {"anchor": "viral-appendix-new-mythos-horrors-reliquae", "placement_event_id": "heading:viral-appendix-new-mythos-tome", "relation": "before_event"},
        "viral-accepted-dbe93023f78f2a8181d333207f407d3ada63c8f33a6f53889b4f3df7bc76a416": {"anchor": "viral-appendix-new-mythos-tome", "placement_event_id": "heading:viral-appendix-new-mythos-tome", "relation": "after_event"},
    }
    portraits = {
        "aa51315c65b2339c22c6928a566dd2ade498b2afc817f9632cf30c09c5def4df": "viral-spektral-krew-marco-proudfoot-maglioni",
        "d65de690f2341a83f4360d658e72d5fb916e7ae5bae952e366262017959f7fa6": "viral-spektral-krew-corrina-trench",
        "1ae78ddfdbcbd36dda84dcf3e34852206355f15827052b2714401493c4765bcb": "viral-spektral-krew-enoch-jeremiah-eakins",
        "a5a54caa96d84e7f6df573ce0c5faa2e52e03213b89f22da03d043087b797201": "viral-spektral-krew-peter-wharton",
        "739a84561947691338ea011d7950446144e6156a4b5aba7924ab24a13b2c6d5f": "viral-spektral-krew-ku-hyeon",
        "f76ae66f2313c44b030bb9cacce1023a95663ed4072a2d93ef8feca74c829004": "viral-spektral-krew-maya-adeduwon",
        "44587a041b63942e4703761b2c3065f459e5637a06e790447d0e0899c1d9a3f6": "viral-spektral-krew-emily-em-lavigne",
        "4fd93a36f8650d97b80a9bde287442646eb741abefad7f520761332c4ec28834": "viral-one-night-in-perla-npcs-santina-maria-salvatore",
        "bc2ae2b3751eaf9754f625794f2d4648a03308dc3dc1042add097cc3649306b0": "viral-one-night-in-perla-npcs-padre-angelo",
    }
    for digest, anchor in portraits.items():
        resolved["viral-accepted-" + digest] = {"anchor": anchor, "placement_event_id": "heading:" + anchor, "relation": "after_event"}
    resolved.update(exact)
    handout_title = _standalone_title_event(events, 69, "Isola di Malamente – Original Google Map")
    resolved["viral-accepted-9cddc3fc484dffdcce7654b3ebc058b362dbb265508a64d64d7485b33dc600c8"] = {"anchor": "viral-handout-01", "placement_event_id": handout_title["event_id"], "relation": "after_event"}
    resolved["viral-accepted-c34aabc5bd16dfcb318cad3a11df583f9f15d4778f488832af69d182dc9d8201"] = {"anchor": "viral-handout-33", "placement_event_id": "heading:viral-handout-33", "relation": "after_event"}
    return resolved




def asset_b1c4_migration() -> dict[str, Any]:
    """Exact frozen-row conservation ledger for the later public validators."""
    audit=asset_b1c4_audit(); rows=[]
    decisions = {
        "viral-accepted-6acc049ed2ad40ebed064312a87ddfce5a404f4fc2487ea1721c656ed541c419": "OUT-006",
        "viral-accepted-647b583cd53fbfdaab7ac6d9643a81bbd5145c125d628c7074b02db0c9f7888b": "OUT-007",
        "viral-accepted-eda9c6f6d6ef94ed41034cd12401547ed37101ef2f8b1ebf30d9602b87db71ab": "OUT-007",
        "viral-accepted-21704f0d57843965013f5eccfa36bcd64321dcc1513cd7d99dead8627d58994e": "OUT-007",
        "viral-accepted-b2ba43b7e57f4c9972780be961deab50d72ea311f795285da15712ba29b6e30e": "OUT-007",
        "viral-accepted-af48429e4ab502e7fc33a545039dab60a3e4e28a8c03a29f56ff57b9280cdd12": "OUT-007",
        "viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541": "OUT-024",
        "viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d": "OUT-024",
        "viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc": "OUT-024",
        "viral-accepted-5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b": "OUT-025",
        "viral-accepted-331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3": "OUT-025",
        "viral-accepted-92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50": "OUT-025",
        "viral-accepted-07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4": "OUT-025",
        "viral-accepted-9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f": "OUT-025",
        "viral-accepted-1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8": "OUT-025",
        "viral-accepted-dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166": "OUT-025",
    }
    for row in audit["rows"]:
        target=[] if row["outcome"]=="excluded_advertising" else [f"assets:{row['asset_id']}"]
        decision = None if row["outcome"] == "retained_unchanged" else "OUT-005" if row["outcome"] == "retained_rebound" else "OUT-026" if row["outcome"] == "excluded_advertising" else decisions.get(row["asset_id"])
        if row["outcome"] == "reclassified" and decision is None:
            raise AuthoringError("E_V2_AUTHOR_ASSET_MIGRATION")
        rows.append({"source_id":f"assets:{row['asset_id']}","outcome":row["outcome"],"target_ids":target,"decision_ref":decision})
    if len(rows)!=123 or sum(not row['target_ids'] for row in rows)!=6:raise AuthoringError("E_V2_AUTHOR_ASSET_MIGRATION")
    targets=[]
    replaces={106:["viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541","viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d"],107:["viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc"],112:["viral-accepted-5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b","viral-accepted-53c2775488f57c8e41f9d42648ecb8a1d30e9a1ce0de8d4108b7926ee26a3595"],114:["viral-accepted-331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3","viral-accepted-89e3eae7390f0ae27a8069bcf2d2aa2956a21047eeb7168a3fd49b0b7cbfc297"],116:["viral-accepted-92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50","viral-accepted-66088dd8192e2a93f140eb9e11fadfed92b3869c509490199a35d272197ebfcb"],118:["viral-accepted-07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4","viral-accepted-fe4c839c1ff9b15dc4a9136f6969271a7a465fe642c77b38f456aa2af38fe0c3"],120:["viral-accepted-9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f","viral-accepted-df1e018979c88b0737200c349889745eadfa119466dc40fb024779a0f8eb4730"],122:["viral-accepted-1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8","viral-accepted-dd0c2d51431a4945f9f7d8293bc7b0b5e870f891dbe31d18c931926bffbb8d8b","viral-accepted-dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166"],26:[]}
    target_details = {
        106: ("viral-keeper-map-ground-floor-basement", "physical_units:viral-map-ground-floor-basement", 0, "map_key_legend_scale"),
        107: ("viral-keeper-map-ground-floor-basement", "physical_units:viral-map-ground-floor-basement", 1, "map_key_legend_scale"),
        112: ("viral-pregen-marco-background", "physical_units:viral-pregen-marco", 1, "pregen_back_semantic_payload"),
        114: ("viral-pregen-corrina-background", "physical_units:viral-pregen-corrina", 1, "pregen_back_semantic_payload"),
        116: ("viral-pregen-enoch-background", "physical_units:viral-pregen-enoch", 1, "pregen_back_semantic_payload"),
        118: ("viral-pregen-peter-background", "physical_units:viral-pregen-peter", 1, "pregen_back_semantic_payload"),
        120: ("viral-pregen-ku-hyeon-background", "physical_units:viral-pregen-ku-hyeon", 1, "pregen_back_semantic_payload"),
        122: ("viral-pregen-blank-background", "physical_units:viral-pregen-blank", 1, "pregen_back_semantic_payload"),
        26: ("viral-isola-di-malamente", "page_opening:viral-isola-di-malamente", 0, "page_opening_visual"),
    }
    for row in asset_b1c4_projection():
        if row["migration_outcome"]=="new_reviewed_target":
            owner, unit, slot, obligation = target_details[row["source_page"]]
            decision_ref = "OUT-038" if row["source_page"] == 26 else "OUT-024" if row["source_page"] in {106,107} else "OUT-025"
            targets.append({"target_id":f"assets:{row['asset_id']}","decision_ref":decision_ref,"evidence_identity":identity(SOURCE_PDF),"physical_unit_id":unit,"page_slot":slot,"owner_anchor":owner,"accessibility_obligation":obligation,"replaces":replaces[row["source_page"]]})
    return {"frozen_rows":rows,"new_reviewed_targets":targets}


def _event_for_page(events: list[dict[str, Any]], page: int) -> dict[str, Any]:
    """Return the first source-ordered retained event for a reader page."""
    try:
        return next(event for event in events if event["page"] == page)
    except StopIteration as error:
        raise AuthoringError(f"E_V2_AUTHOR_EVENT_PAGE: {page}") from error


def author() -> dict[str, Any]:
    """Materialize reviewed source-ordered headings, containers and assets."""
    import importlib.util
    import sys
    from types import SimpleNamespace
    name = "viral_publication_projection"
    module = sys.modules.get(name)
    if module is None:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return module.materialize(sys.modules.get(__name__) or SimpleNamespace(**globals()))


def _author_inventory() -> dict[str, Any]:
    """Project the sealed B1 facts into a deterministic closed v2 envelope.

    This deliberately keeps the B2-only semantic projection explicit: every
    frozen inventory row is present, but reader assets and xrefs retain only
    their source-backed declaration until A3 establishes their final bindings.
    It is still a complete *top-level* v2 object, so the public schema gates
    can report the next semantic seam instead of a generic envelope failure.
    """
    projection = _author_b1c3()
    # Canonical B1c4 inventory: excluded frozen rows remain migration-only;
    # the eight reviewed full-page declarations are reader assets, not a
    # private author side channel.
    projection["assets"] = asset_b1c4_projection()
    projection["migration"]["asset_rows"] = asset_b1c4_migration()["frozen_rows"]
    projection["migration"]["new_reviewed_targets"] = asset_b1c4_migration()["new_reviewed_targets"]
    hierarchy={row["anchor"]:row for row in projection["hierarchy"]}; required={row["source_event_id"] for row in projection["xrefs"]}|{row["target_event_id"] for row in projection["source_recoveries"]}; units=[]
    def add(event,kind,priority,group): units.append({"review_id":f"review:{kind}:{event['event_id']}","kind":kind,"source_pages":[event["page"]],"event_ids":[event["event_id"]],"asset_ids":[],"priority":priority,"contact_sheet_group":group})
    for event in projection["events"]:
        if event["type"]=="heading" and hierarchy[event["anchor"]]["representation"]=="heading": add(event,"heading_outline",True,"outline")
        elif event["type"]=="structured_unit": add(event,event["content"]["kind"],False,"structured")
    for event in projection["events"]:
        if event["event_id"] in required: add(event,"xref_recovery",True,"xref_recovery")
    for asset in projection["assets"]:
        if asset.get("reader_value",asset.get("disposition")=="reader"):
            units.append({"review_id":f"review:asset_placement:{asset['asset_id']}","kind":"asset_placement","source_pages":[asset["source_page"]],"event_ids":[],"asset_ids":[asset["asset_id"]],"priority":False,"contact_sheet_group":"reader_assets"})
    projection["visual_review_units"]=units
    return projection


def _author_b1c3() -> dict[str, Any]:
    """Closed B1c3 projection from frozen xrefs; generated navigation owns no bytes."""
    base = foundation()
    bound = verify_inputs()
    graph = source_graph()
    v1 = bound["v1"]
    fallback_anchor = graph["hierarchy"][0]["anchor"]
    # Locate each exact source line once before assigning it to an event.  The
    # frozen owner is the only authority for a line event; all other retained
    # intervals remain ordinary root-owned source fragments.
    source_rows = [row for row in v1["xrefs"] if row["source_selector"] == "line_exact"]
    raw_pages = {page: (PACKAGE / "pages" / f"page-{page:03d}.md").read_bytes() for page in range(1, 123)}
    line_rows: dict[tuple[int, int, int], list[dict[str, Any]]] = {}
    for row in source_rows:
        raw = raw_pages[row["source_page"]]; needle = row["source_line"].encode("utf-8")
        first = raw.find(needle)
        if first < 0 or raw.find(needle, first + 1) >= 0: raise AuthoringError("E_V2_AUTHOR_XREF_LINE")
        key = (row["source_page"], first, first + len(needle)); line_rows.setdefault(key, []).append(row)
    if any(len({row["owner_anchor"] for row in rows}) != 1 for rows in line_rows.values()): raise AuthoringError("E_V2_AUTHOR_XREF_OWNER")
    # Refine all source spans that contain exact xref lines.  The byte union is
    # conserved; a line gets its own event and can never straddle an owner.
    old_spans = base["source_partition"]["spans"]; new_spans=[]; events=[]
    for span in old_spans:
        if span["owner_kind"] == "asset":
            new_spans.append(span)
            continue
        raw = raw_pages[span["page"]][span["start_byte"]:span["end_byte"]]
        cuts={0,len(raw)}
        for page,start,end in line_rows:
            if page == span["page"] and span["start_byte"] <= start and end <= span["end_byte"]:
                cuts.update((start-span["start_byte"], end-span["start_byte"]))
        for ordinal,(left,right) in enumerate(zip(sorted(cuts),sorted(cuts)[1:]),1):
            absolute_left=span["start_byte"]+left; absolute_right=span["start_byte"]+right; piece=raw[left:right]
            start_char=len(raw_pages[span["page"]][:absolute_left].decode("utf-8")); end_char=len(raw_pages[span["page"]][:absolute_right].decode("utf-8"))
            sid=f"span-p{span['page']:03d}-{absolute_left:06d}"; eid=f"event-p{span['page']:03d}-{absolute_left:06d}"
            owner_rows=line_rows.get((span["page"],absolute_left,absolute_right),[])
            anchor=owner_rows[0]["owner_anchor"] if owner_rows else fallback_anchor
            new_spans.append({**span,"span_id":sid,"start_byte":absolute_left,"end_byte":absolute_right,"start_char":start_char,"end_char":end_char,"raw_sha256":sha256_bytes(piece),"raw_text_sha256":sha256_bytes(piece.decode("utf-8").encode("utf-8")),"owner_id":eid})
            events.append({"event_id":eid,"type":"text_fragment","page":span["page"],"order_key":[span["page"],absolute_left,2,ordinal],"anchor":anchor,"content":piece.decode("utf-8"),"fragment_id":sid,"source_span_ids":[sid],"source_operation":"emit_exact","payload_bindings":[{"json_pointer":"/content","source_slices":[{"span_id":sid,"start_char":start_char,"end_char":end_char}],"joiner":"","recovery_id":None}]})
    events.sort(key=lambda row:(row["page"],row["order_key"][1]))
    for ordinal,event in enumerate(events): event["order_key"][3]=ordinal
    base["source_partition"]={"pages":[{**page,"span_ids":[span["span_id"] for span in new_spans if span["page"]==page["page"]]} for page in base["source_partition"]["pages"]],"spans":new_spans}
    # The source graph is already ordered by its exact byte coordinates.  The
    # public v2 envelope requires anchors on every event; B2 replaces this
    # inherited root binding with the reviewed hierarchy ownership map.
    event_by_page = {page: _event_for_page(events, page) for page in range(1, 123)}
    # The frozen hierarchy names the four generated-navigation containers.  A
    # concrete source event at each owner's first reader page is the approved
    # heading anchor; generated navigation is inserted immediately after it.
    for owner, page in (("viral-contents", 5), ("viral-player-handouts", 69), ("viral-keeper-maps", 104), ("viral-pregenerated-investigators", 111)):
        heading = event_by_page[page]
        heading.update({"type": "heading", "anchor": owner, "source_operation": "emit_exact"})
        heading["order_key"][2] = 0
    spans = {row["span_id"]: row for row in new_spans}
    asset_bindings = {row["asset_id"]: row for row in asset_xref_readiness()["asset_span_bindings"]}
    assets = []
    for row in v1["assets"]:
        page = row["source_page"] if row["source_page"] in range(1, 123) else 1
        binding = asset_bindings.get(row["asset_id"])
        assets.append({
            "asset_id": row["asset_id"],
            "reader_value": False,
            "placement": {"after_event": event_by_page[page]["event_id"]},
            "anchor": fallback_anchor,
            "page": page,
            "source_span_ids": [binding["span_id"]] if binding else [],
        })
    event_for_line={}
    for event in events:
        span=spans[event["source_span_ids"][0]]; event_for_line[(event["page"],span["start_byte"],span["end_byte"])]=event
    xrefs=[]
    for row in source_rows:
        raw=raw_pages[row["source_page"]]; line=row["source_line"].encode("utf-8"); start=raw.find(line); event=event_for_line[(row["source_page"],start,start+len(line))]; span=spans[event["source_span_ids"][0]]; cursor=0
        for index,segment in enumerate(row["segments"],1):
            # The emitted reader text itself is the A3 slice.  Frozen
            # `source_text` may be a longer exact replacement span (for
            # example a parenthetical source suffix), but it is not allowed to
            # masquerade as the materialized reader bytes.
            source_text=segment["source_text"]; source_position=row["source_line"].find(source_text,cursor)
            if source_position < 0 or row["source_line"].find(source_text,source_position+1)>=0: raise AuthoringError("E_V2_AUTHOR_XREF_SEGMENT")
            text=segment["reader_text"]; local=source_text.find(text)
            if local < 0 or source_text.find(text,local+1)>=0: raise AuthoringError("E_V2_AUTHOR_XREF_SEGMENT")
            position=source_position+local; cursor=source_position+len(source_text); prefix=row["source_line"][:position].encode("utf-8"); source=raw[start:start+len(line)]
            char_start=len(source[:len(prefix)].decode("utf-8")); char_end=char_start+len(text)
            xref_id=row["xref_id"] if len(row["segments"])==1 else f"{row['xref_id']}-segment-{index:02d}"
            xrefs.append({"xref_id":xref_id,"source_event_id":event["event_id"],"source_page":row["source_page"],"target_anchor":segment["target_anchor"],"reader_text":segment["reader_text"],"source_slices":[{"span_id":span["span_id"],"start_char":span["start_char"]+char_start,"end_char":span["start_char"]+char_end}],"emit_link":segment["emit_link"],"migration_row_id":f"xrefs:{xref_id}"})
    hierarchy=[row for row in graph["hierarchy"] if row["anchor"] not in {"viral-merchandise","viral-back-cover"}]
    for row in hierarchy: row["migration_row_id"]=f"hierarchy:{row['anchor']}"
    generated=[]; families=(("generated_toc","toc","viral-contents"),("generated_handout_index","handout_index","viral-player-handouts"),("generated_map_index","map_index","viral-keeper-maps"),("generated_pregen_index","pregen_index","viral-pregenerated-investigators"))
    for family_index,(selector,family,owner) in enumerate(families):
        rows=[row for row in v1["xrefs"] if row["source_selector"]==selector and row["xref_id"] not in {"toc-viral-merchandise","toc-viral-back-cover"}]
        headings=[event for event in events if event["type"]=="heading" and event["anchor"]==owner]
        if len(headings)!=1: raise AuthoringError("E_V2_AUTHOR_GENERATED_OWNER")
        heading=headings[0]
        generated.append({"event_id":f"generated-navigation-{family.replace('_','-')}","type":"generated_navigation","page":heading["page"],"order_key":[heading["page"],heading["order_key"][1],5,family_index],"anchor":owner,"content":{"kind":"generated_navigation","family":family,"owner_anchor":owner,"decision_ref":"OUT-002","entry_count":len(rows),"entries":[{"navigation_id":f"navigation:{row['xref_id']}","source_xref_id":row["xref_id"],"reader_text":row["visible_text"],"target_anchor":row["target_anchors"][0],"migration_row_id":f"generated_navigation_items:{row['xref_id']}"} for row in rows]},"fragment_id":f"generated-navigation-{family}","source_span_ids":[],"source_operation":"generated_navigation","payload_bindings":[],"generated_placement":{"after_event":heading["event_id"]}})
    events.extend(generated); events.sort(key=lambda row:tuple(row["order_key"]))
    for ordinal, event in enumerate(events): event["order_key"][3] = ordinal
    # A review unit is a one-object projection: IDs and sequence are derived
    # from immutable semantic IDs and canonical event/asset order, never ordinals.
    hierarchy_by_anchor={row["anchor"]:row for row in hierarchy}
    review_events={row["event_id"]:row for row in events}
    visual_review_units=[]
    def review_event(event, kind, priority, group):
        return {"review_id":f"review:{kind}:{event['event_id']}","kind":kind,"source_pages":[event["page"]],"event_ids":[event["event_id"]],"asset_ids":[],"priority":priority,"contact_sheet_group":group}
    for event in events:
        if event["type"]=="heading" and hierarchy_by_anchor[event["anchor"]]["representation"]=="heading":
            visual_review_units.append(review_event(event,"heading_outline",True,"outline"))
        elif event["type"]=="structured_unit":
            visual_review_units.append(review_event(event,event["content"]["kind"],False,"structured"))
    xref_recovery_ids={row["source_event_id"] for row in xrefs}|{row["target_event_id"] for row in []}
    for event in events:
        if event["event_id"] in xref_recovery_ids:
            visual_review_units.append(review_event(event,"xref_recovery",True,"xref_recovery"))
    for asset in assets:
        if asset.get("reader_value",asset.get("disposition")=="reader"):
            page=asset.get("source_page",asset.get("page"))
            visual_review_units.append({"review_id":f"review:asset_placement:{asset['asset_id']}","kind":"asset_placement","source_pages":[page],"event_ids":[],"asset_ids":[asset["asset_id"]],"priority":False,"contact_sheet_group":"reader_assets"})
    # Close every frozen migration row.  Generated navigation is a real reader
    # materialization namespace, while the two catalogue-advertising rows stay
    # deliberately targetless.
    registry=ROOT / "kb_creator/docs/plans/20260830-kb-creator-next-scenario/USER_REVIEW_TYPICAL_PROBLEMS_20260902.md"
    # The current config records the exact decision evidence it was authored
    # from, but authoring is not blocked by a stale hard-coded registry digest.
    base["migration"]["inputs"]["decision_evidence"].append({**identity(registry),"kind":"kb_creator.user_review_registry.md"})
    for key,v1_key,identifier in MIGRATION_DOMAINS:
        for item in base["migration"][key]:
            frozen=next(row for row in v1[v1_key] if f"{v1_key}:{row[identifier]}"==item["source_id"])
            if key=="hierarchy_rows" and frozen["anchor"] in {"viral-merchandise","viral-back-cover"}:
                item.update({"outcome":"excluded_advertising","final_target_ids":[],"decision_ref":"OUT-026"})
            elif key=="xref_rows":
                xid=frozen["xref_id"]
                if xid in {"toc-viral-merchandise","toc-viral-back-cover"}: item.update({"outcome":"excluded_advertising","final_target_ids":[],"decision_ref":"OUT-026"})
                elif frozen["source_selector"]=="line_exact" and xid=="p037-handout-21": item.update({"outcome":"split","final_target_ids":["xrefs:p037-handout-21-segment-01","xrefs:p037-handout-21-segment-02"],"decision_ref":None})
                elif frozen["source_selector"]=="line_exact": item.update({"outcome":"retained_unchanged","final_target_ids":[f"xrefs:{xid}"],"decision_ref":None})
                else: item.update({"outcome":"replaced","final_target_ids":[f"generated_navigation_items:{xid}"],"decision_ref":"OUT-002"})
            else:
                item.update({"outcome":"retained_unchanged","final_target_ids":[item["source_id"]],"decision_ref":None})
    # Do not claim the two recovery strings are embedded until their B2 event
    # bindings are supplied.  Omitting recoveries here is more precise than a
    # synthetic payload-binding fallback, and leaves their frozen evidence in
    # source_graph() for the next materializer.
    return {
        **base,
        "hierarchy": hierarchy,
        "events": events,
        "assets": assets,
        "xrefs": xrefs,
        "source_recoveries": [],
        "visual_review_units": visual_review_units,
        "metrics": {"source_pages_audited":124,"reader_pages":122,"excluded_advertising_pages":2},
    }


def canonical_json(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def write_atomic_absent(destination: Path, payload: bytes) -> None:
    if destination.exists(): raise AuthoringError("E_V2_AUTHOR_OUTPUT_EXISTS")
    if not destination.parent.is_dir(): raise AuthoringError("E_V2_AUTHOR_OUTPUT_PARENT")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent); temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream: stream.write(payload); stream.flush(); os.fsync(stream.fileno())
        if destination.exists(): raise AuthoringError("E_V2_AUTHOR_OUTPUT_EXISTS")
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True); raise


def checkout_temporary_config_path(token: str | None = None) -> Path:
    """Return the narrowly-authorized B1c checkout-local temporary path."""
    value = uuid.UUID(token) if token is not None else uuid.uuid4()
    return TEMPORARY_CONFIG_ROOT / f".phase-b1c-author-{value}.json"


def with_checkout_temporary_config(payload: bytes, gate: Callable[[Path], Any], token: str | None = None) -> Any:
    """Atomically expose one absent B1c config to a public preflight gate.

    The scope amendment permits no other checkout-local output.  A collision is
    refused without changing the pre-existing path; after a successful write,
    `finally` removes only this invocation's generated JSON.
    """
    destination = checkout_temporary_config_path(token)
    if destination.exists():
        raise AuthoringError("E_V2_AUTHOR_OUTPUT_EXISTS")
    write_atomic_absent(destination, payload)
    try:
        return gate(destination)
    finally:
        destination.unlink(missing_ok=True)


def author_to(destination: Path) -> None:
    """Serialize one deterministic, closed top-level v2 author projection."""
    write_atomic_absent(destination, canonical_json(author()))


if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(canonical_json(author()).decode("utf-8"), end="")
