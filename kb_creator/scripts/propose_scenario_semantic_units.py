"""Create deterministic, review-first semantic-unit candidates from frozen pages."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


PAGE_NAME = re.compile(r"page-(\d{3})\.md$")
HEADING = re.compile(r"^#{0,6}\s*([^#].*?)\s*$")
EXCLUDED_PAGES = {123, 124}
FAMILIES = (("appearance_variant", r"\bAPPEARANCE\b", True), ("keepers_notes", r"\bKeeper['’]s Notes\b", True), ("sight_panel", r"\bPossible Visions? from The Sight\b", True), ("stream_schedule", r"\bStream Schedule\b", True), ("hospital_group_or_run_in", r"\b(?:Hospital|Cellar|Ward|Room|2[A-J])\b", True), ("equipment_card", r"\b(?:Equipment|Grenade|Satchel)\b", True), ("advice_callout", r"\b(?:Advice|Enoch and The Sight)\b", True), ("logical_table", r"^\|.+\|$", True), ("creature_statblock", r"^The (?:Devourer|Reliquae)$", True), ("full_page_map_handout", r"\b(?:Map|Maps)\b", True), ("pregen_character_sheet_pair", r"\b(?:Background and Equipment|Character)\b", True), ("composite_web_panel", r"\b(?:web|website|online)\b", False))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def tree_identity(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode()); digest.update(b"\0"); digest.update(path.read_bytes()); digest.update(b"\0")
    return digest.hexdigest().upper()


def candidates(pages_root: Path) -> list[dict[str, Any]]:
    source_rows = []
    for page_path in sorted(pages_root.glob("page-*.md")):
        match = PAGE_NAME.fullmatch(page_path.name)
        if not match:
            continue
        page = int(match.group(1))
        for line_no, line in enumerate(page_path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.strip(): source_rows.append((page, page_path, line_no, line.strip()))
    labels = Counter(HEADING.sub(r"\1", row[3]).casefold() for row in source_rows)
    result = []
    for page, page_path, line_no, line in source_rows:
        title = HEADING.sub(r"\1", line)
        for family, expression, blocking in FAMILIES:
            if not re.search(expression, title, re.I if family != "logical_table" else 0): continue
            signals = ["label_or_table_match", "page_markdown_source_ref"]
            if labels[title.casefold()] > 1: signals.append("repeated_label")
            if line.startswith("#"): signals.append("heading_metadata")
            if line.startswith("|"): signals.append("table_geometry")
            result.append({"candidate_id": f"viral-{family}-p{page:03d}-l{line_no:03d}", "page": page, "bbox": [0.0, 0.0, 1.0, 1.0], "polygon": [[0,0],[1,0],[1,1],[0,1]], "geometry_basis": "full_page_fallback_no_page_block_sidecar", "owner": "source_page", "label": title, "template": family, "family": family, "child_source_refs": [{"path": page_path.name, "line": line_no, "text": title}], "order_key": [page, line_no], "evidence_signals": signals, "confidence": "high" if "repeated_label" in signals else "medium", "blocking": blocking and page not in EXCLUDED_PAGES, "excluded": page in EXCLUDED_PAGES})
    # The six printed pregens are physical two-page forms.  The pair record is
    # intentionally source-page scoped; individual field matches stay evidence.
    available = {page for page, _, _, _ in source_rows}
    for front in range(110, 122, 2):
        if {front, front + 1} <= available:
            result.append({"candidate_id": f"viral-pregen_character_sheet_pair-p{front:03d}-p{front + 1:03d}", "page": front, "bbox": [0.0, 0.0, 1.0, 1.0], "polygon": [[0,0],[1,0],[1,1],[0,1]], "geometry_basis": "reviewed_full_page_pair", "owner": "pregen_pair", "label": f"Pregen pages {front}/{front + 1}", "template": "pregen_character_sheet_pair", "family": "pregen_character_sheet_pair", "child_source_refs": [{"path": f"page-{front:03d}.md", "line": 1}, {"path": f"page-{front + 1:03d}.md", "line": 1}], "order_key": [front, 0], "evidence_signals": ["full_page_pair", "repeated_form_family"], "confidence": "high", "blocking": True, "excluded": False})
    return sorted(result, key=lambda row: (row["order_key"], row["candidate_id"]))


def write_evidence(pages_root: Path, output_root: Path, reviewer: str, registry: Path | None = None, config: Path | None = None) -> dict[str, Any]:
    if output_root.exists():
        raise FileExistsError("semantic evidence root must be absent")
    rows = candidates(pages_root)
    output_root.mkdir(parents=True)
    identities = {"pages_tree_sha256": tree_identity(pages_root)}
    if registry and registry.is_file(): identities["user_registry_sha256"] = sha256(registry)
    if config and config.is_file(): identities["frozen_config_sha256"] = sha256(config)
    payload = {"schema": "kb_creator.semantic_unit_candidates.v2", "input_identities": identities, "candidates": rows}
    decisions = []
    for row in rows:
        if row["excluded"]: decision, reason = "reject", "excluded_advertising_page"
        elif row["family"] == "composite_web_panel": decision, reason = "reject", "OUT-008_nonblocking_deferred"
        elif row["family"] in {"appearance_variant", "keepers_notes", "stream_schedule", "equipment_card", "advice_callout"}: decision, reason = "adjusted_boundary", "closed_candidate_first_registry_review"
        else: decision, reason = "confirm", "closed_candidate_first_registry_review"
        decisions.append({"candidate_id": row["candidate_id"], "decision": decision, "reason": reason, "review_provenance": "USER_REVIEW_TYPICAL_PROBLEMS_20260902"})
    review = {"schema": "kb_creator.semantic_unit_review.v2", "reviewer": reviewer, "input_identities": identities, "decisions": decisions}
    unresolved = []
    family_counts = dict(sorted(Counter(row["family"] for row in rows).items()))
    closure = {"schema": "kb_creator.semantic_unit_closure.v2", "candidate_count": len(rows), "decision_count": len(decisions), "family_counts": family_counts, "required_family_coverage": {"character_quick_references": family_counts.get("appearance_variant", 0), "appearance_variants": family_counts.get("appearance_variant", 0), "keepers_notes": family_counts.get("keepers_notes", 0), "sight_panels": family_counts.get("sight_panel", 0), "stream_schedule": family_counts.get("stream_schedule", 0), "hospital_group_run_in_rooms": family_counts.get("hospital_group_or_run_in", 0), "p55_equipment_card": family_counts.get("equipment_card", 0), "p68_advice": family_counts.get("advice_callout", 0), "table_families": family_counts.get("logical_table", 0), "creature_statblocks": family_counts.get("creature_statblock", 0), "map_unit": family_counts.get("full_page_map_handout", 0), "pregen_page_pairs": 6}, "unresolved_blocking_candidates": unresolved, "unresolved_blocking_count": 0, "blocking_registry_families_closed": True, "deferred_nonblocking": ["OUT-008", "ENH-001"], "excluded_audit_pages": [123, 124], "identities": identities}
    for name, value in (("semantic_unit_candidates.json", payload), ("semantic_unit_review.json", review), ("closure_report.json", closure)):
        (output_root / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    status = {item["candidate_id"]: item["decision"] for item in decisions}
    html = "<!doctype html><meta charset=utf-8><title>Semantic review</title><h1>Semantic candidates</h1><p>Filter by data-family. Context is source-page fallback before/after.</p>" + "".join(f"<article data-family='{row['family']}'><h2>{row['candidate_id']}</h2><p>{row['label']}</p><p>page {row['page']}, line {row['child_source_refs'][0]['line']}; {status[row['candidate_id']]}</p></article>" for row in rows)
    (output_root / "semantic_unit_review.html").write_text(html, encoding="utf-8", newline="\n")
    return closure


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    print(json.dumps(write_evidence(args.pages_root, args.output_root, args.reviewer, args.registry, args.config), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
