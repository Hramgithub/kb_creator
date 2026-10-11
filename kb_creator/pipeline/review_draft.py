"""Sealed, acyclic authority records for the review-draft reconstruction path.

The production reconstruction path deliberately requires closed visual review.
This module does not weaken that rule.  It provides the separate records used
by the pre-handoff draft path: an input record that can be sealed before the
Stage05 audit, and a final record that can only be sealed after that audit.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .identity import canonical_bytes, file_identity, sha256_bytes


INPUT_SCHEMA = "kb_creator.review_draft_input.v1"
ISSUES_SCHEMA = "kb_creator.review_draft_source_issues.v1"
FINAL_SCHEMA = "kb_creator.review_draft_evidence.v1"
INPUT_FIELDS = frozenset({"schema", "bindings", "source_issues", "unresolved_dispositions", "input_sha256"})
ISSUE_FIELDS = frozenset({
    "issue_id", "kind", "reason", "source_pdf_sha256", "source_page",
    "source_selector", "source_excerpt_en", "source_excerpt_sha256",
    "evidence", "candidate_span", "state",
})
DISPOSITION_FIELDS = frozenset({"source_page", "predecessor_unresolved", "category", "outcome", "evidence", "predecessor", "current"})


class ReviewDraftError(ValueError):
    """A review-draft authority record is stale, circular, or incomplete."""


@dataclass(frozen=True)
class ArchiveConsumptionAuthorities:
    """Read-only queue-validation view of sealed archived replay artifacts."""
    run_root: Path
    stage_02_root: Path
    comparison: Path
    merge_packets: Path
    visual_manifest: Path
    geometry_plan: Path
    bridge_sha256: str


def build_archive_consumption_context(*, source_run_root: Path, target_run_root: Path) -> dict[str, Any]:
    """Recompute sealed, read-only replay authority for review-draft staging.

    This deliberately returns no fresh replay authority and provides no resume
    capability.  Unknown inventory paths fail closed; recorded stale producer
    paths remain explicit provenance for consumption of sealed payloads.
    """
    from . import reconstruction_replay, reconstruction_replay_resume
    source_path, target_path = Path(source_run_root), Path(target_run_root)
    source = reconstruction_replay.validate_replay_artifacts_for_consumption(source_path)
    # Most consumers name one archive as both predecessor and target. Reuse
    # its fresh result within this call only; distinct paths retain independent
    # validation, including path-safety checks. Do not resolve aliases here.
    target = (source if source_path == target_path else
              reconstruction_replay.validate_replay_artifacts_for_consumption(target_path))
    if source.source_sha256 != target.source_sha256:
        raise ReviewDraftError("archive source identities differ")
    for label, authority in (("source", source), ("target", target)):
        if authority.producer_freshness.get("state") == "unknown":
            raise ReviewDraftError(f"archive {label} producer inventory has unknown paths")
    checked_paths = {
        "stage_02_root": target.run_root / "outputs/02-mineru-three-view",
        "comparison": target.run_root / "outputs/03-compare-views/comparison.json",
        "merge_packets": target.stage04_root / "merge_packets",
        "visual_manifest": target.stage04_root / "visual/visual_manifest.json",
        "geometry_plan": target.stage04_root / "visual/geometry_plan.json",
    }
    if any(not path.exists() for path in checked_paths.values()):
        raise ReviewDraftError("archive authority required read-only path is missing")
    queue_authority = ArchiveConsumptionAuthorities(
        run_root=target.run_root, bridge_sha256=target.bridge_sha256, **checked_paths)
    review_queue = reconstruction_replay_resume.validate_replay_review_queue(queue_authority)
    checked_paths["review_queue"] = review_queue.queue_path
    return {
        "schema": "kb_creator.review_draft_archive_consumption.v1",
        "state": "read_only_consumption",
        "source_run_root": str(source.run_root), "target_run_root": str(target.run_root),
        "source_sha256": source.source_sha256,
        "source": {"run_identity_sha256": source.run_identity_sha256,
                   "bridge_sha256": source.bridge_sha256, "producer_freshness": source.producer_freshness},
        "target": {"run_identity_sha256": target.run_identity_sha256,
                   "bridge_sha256": target.bridge_sha256, "producer_freshness": target.producer_freshness},
        "checked_paths": {name: str(path) for name, path in checked_paths.items()},
    }


@dataclass(frozen=True)
class ReviewDraftInput:
    value: dict[str, Any]
    sha256: str
    source_issues: list[dict[str, Any]]
    audit_pending: list[dict[str, Any]]


def _sealed_hash(value: dict[str, Any], field: str) -> str:
    unsigned = {key: item for key, item in value.items() if key != field}
    return sha256_bytes(canonical_bytes(unsigned))


def _identity(value: Any, label: str) -> None:
    if not isinstance(value, dict) or set(value) != {"path", "bytes", "sha256"}:
        raise ReviewDraftError(f"{label} must be a closed file identity")
    path = value.get("path")
    if (not isinstance(path, str) or not path or "\\" in path or ":" in path
            or path.startswith("/") or path.endswith("/")):
        raise ReviewDraftError(f"{label} path must be portable")
    segments = path.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise ReviewDraftError(f"{label} path must be a normalized relative path")
    if type(value["bytes"]) is not int or value["bytes"] < 0 or not isinstance(value["sha256"], str) or len(value["sha256"]) != 64:
        raise ReviewDraftError(f"{label} identity is invalid")


def _validate_issues(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, dict) or set(value) != {"schema", "issues"} or value["schema"] != ISSUES_SCHEMA or not isinstance(value["issues"], list):
        raise ReviewDraftError("source issues have an invalid closed shape")
    issues: list[dict[str, Any]] = []
    seen: set[str] = set()
    for issue in value["issues"]:
        if not isinstance(issue, dict) or frozenset(issue) != ISSUE_FIELDS:
            raise ReviewDraftError("source issue has an invalid closed shape")
        issue_id = issue["issue_id"]
        if not isinstance(issue_id, str) or not issue_id or issue_id in seen:
            raise ReviewDraftError("source issue ID is missing or duplicated")
        if issue["state"] != "open" or type(issue["source_page"]) is not int or issue["source_page"] < 1:
            raise ReviewDraftError("source issue state or page is invalid")
        for field in ("kind", "reason", "source_pdf_sha256", "source_excerpt_en", "source_excerpt_sha256"):
            if not isinstance(issue[field], str) or not issue[field]:
                raise ReviewDraftError(f"source issue {field} is required")
        if not isinstance(issue["source_selector"], dict) or not isinstance(issue["candidate_span"], dict) or not isinstance(issue["evidence"], list):
            raise ReviewDraftError("source issue lacks a source/candidate locator")
        if issue["kind"] == "source_structure_role_pending":
            try:
                from .structural_role_issues import validate_structural_issue
                validate_structural_issue(issue)
            except ValueError as error:
                raise ReviewDraftError(f"structural source issue is invalid: {error}") from error
        # Generated EN/RU identifiers must not be fabricated in the source
        # record; they are introduced by later, independently sealed stages.
        if any(key in issue for key in ("reader_unit_id", "reader_block_anchor", "ru_unit_id", "target_text")):
            raise ReviewDraftError("source issue contains a future reader locator")
        seen.add(issue_id)
        issues.append(issue)
    return issues


def validate_review_draft_input(value: Any) -> ReviewDraftInput:
    """Validate an input-only authority record without consulting future output."""
    if not isinstance(value, dict) or frozenset(value) != INPUT_FIELDS or value.get("schema") != INPUT_SCHEMA:
        raise ReviewDraftError("review-draft input has an invalid closed shape")
    if value.get("input_sha256") != _sealed_hash(value, "input_sha256"):
        raise ReviewDraftError("review-draft input seal mismatch")
    if not isinstance(value["bindings"], dict) or not value["bindings"]:
        raise ReviewDraftError("review-draft input requires bindings")
    # Bindings may grow by version, but every supplied authority is a portable
    # identity and no future audit/final record may appear in an input.
    for name, identity in value["bindings"].items():
        if not isinstance(name, str) or not name or "audit" in name.casefold() or "final" in name.casefold():
            raise ReviewDraftError("review-draft input contains a future authority")
        _identity(identity, f"binding {name}")
    issues = _validate_issues(value["source_issues"])
    dispositions = value["unresolved_dispositions"]
    if not isinstance(dispositions, list):
        raise ReviewDraftError("unresolved dispositions must be a list")
    seen: set[tuple[int, str]] = set(); pending: list[dict[str, Any]] = []
    for row in dispositions:
        if not isinstance(row, dict) or frozenset(row) != DISPOSITION_FIELDS:
            raise ReviewDraftError("unresolved disposition has an invalid closed shape")
        key = (row["source_page"], row["predecessor_unresolved"])
        if type(key[0]) is not int or key[0] < 1 or not isinstance(key[1], str) or not key[1] or key in seen:
            raise ReviewDraftError("predecessor unresolved entry is missing or duplicated")
        if row["category"] not in {"administrative_pending", "covered_continuation", "source_typography_decision", "editorial_open", "machine_blocker"}:
            raise ReviewDraftError("unresolved disposition category is invalid")
        if row["outcome"] not in {"closed", "audit_pending", "open", "blocked"} or not isinstance(row["evidence"], list) or not row["evidence"]:
            raise ReviewDraftError("unresolved disposition outcome is invalid")
        _identity(row["predecessor"], "disposition predecessor"); _identity(row["current"], "disposition current")
        if row["outcome"] == "closed" and row["category"] == "administrative_pending":
            raise ReviewDraftError("administrative pending entry cannot close before audit")
        if row["outcome"] == "audit_pending":
            if row["category"] != "administrative_pending":
                raise ReviewDraftError("only an administrative entry may await audit")
            pending.append(row)
        if row["category"] == "editorial_open" and not issues:
            raise ReviewDraftError("editorial disposition requires a source issue")
        seen.add(key)
    return ReviewDraftInput(value=value, sha256=value["input_sha256"], source_issues=issues, audit_pending=pending)


def prepare_review_draft_input(value: Any) -> dict[str, Any]:
    """Return the sole state that may enter cold authoring from an input record."""
    record = validate_review_draft_input(value)
    blockers = [row for row in record.value["unresolved_dispositions"] if row["outcome"] in {"open", "blocked"}]
    if blockers:
        raise ReviewDraftError("review-draft input retains unresolved machine or editorial holds")
    return {
        "schema": "kb_creator.review_draft_preflight.v1",
        "state": "prepared_for_audit",
        "input_sha256": record.sha256,
        "open_issue_ids": [row["issue_id"] for row in record.source_issues],
        "audit_pending_count": len(record.audit_pending),
    }


def finalize_review_draft_evidence(input_value: Any, *, authored: dict[str, Any], audit: dict[str, Any], visual_reviewed_false_pages: list[int]) -> dict[str, Any]:
    """Seal output authority after a successful audit; never mutate input rows."""
    record = validate_review_draft_input(input_value)
    if not isinstance(audit, dict) or audit.get("passed") is not True or audit.get("errors") != []:
        raise ReviewDraftError("review-draft finalization requires a passing fidelity audit")
    if not isinstance(authored, dict) or not authored:
        raise ReviewDraftError("review-draft finalization requires authored output identity")
    for name, identity in authored.items():
        if not isinstance(name, str) or not name:
            raise ReviewDraftError("authored output identity name is invalid")
        _identity(identity, f"authored {name}")
    if any(type(page) is not int or page < 1 for page in visual_reviewed_false_pages) or len(visual_reviewed_false_pages) != len(set(visual_reviewed_false_pages)):
        raise ReviewDraftError("literal false visual page list is invalid")
    dispositions = []
    for row in record.value["unresolved_dispositions"]:
        row = dict(row)
        if row["outcome"] == "audit_pending":
            row["outcome"] = "closed_after_audit"
        dispositions.append(row)
    unsigned = {
        "schema": FINAL_SCHEMA, "input_sha256": record.sha256, "authored": authored,
        "audit": audit, "source_issues": record.value["source_issues"],
        "unresolved_dispositions": dispositions,
        "visual_reviewed_false_pages": sorted(visual_reviewed_false_pages),
    }
    return {**unsigned, "evidence_sha256": sha256_bytes(canonical_bytes(unsigned))}


def validate_review_draft_evidence(value: Any) -> dict[str, Any]:
    """Validate final-only authority without treating it as production approval."""
    required = {
        "schema", "input_sha256", "authored", "audit", "source_issues",
        "unresolved_dispositions", "visual_reviewed_false_pages", "evidence_sha256",
    }
    if not isinstance(value, dict) or set(value) != required or value.get("schema") != FINAL_SCHEMA:
        raise ReviewDraftError("review-draft evidence has an invalid closed shape")
    if value.get("evidence_sha256") != _sealed_hash(value, "evidence_sha256"):
        raise ReviewDraftError("review-draft evidence seal mismatch")
    if not isinstance(value.get("input_sha256"), str) or len(value["input_sha256"]) != 64:
        raise ReviewDraftError("review-draft evidence input identity is invalid")
    if not isinstance(value["audit"], dict) or value["audit"].get("passed") is not True or value["audit"].get("errors") != []:
        raise ReviewDraftError("review-draft evidence audit is not passing")
    for name, identity in value["authored"].items() if isinstance(value["authored"], dict) else []:
        _identity(identity, f"authored {name}")
    if not isinstance(value["authored"], dict) or not value["authored"]:
        raise ReviewDraftError("review-draft evidence lacks authored identities")
    _validate_issues(value["source_issues"])
    for row in value["unresolved_dispositions"]:
        if not isinstance(row, dict) or set(row) != DISPOSITION_FIELDS or row.get("outcome") in {"audit_pending", "open", "blocked"}:
            raise ReviewDraftError("review-draft evidence retains an unresolved disposition")
    if not isinstance(value["visual_reviewed_false_pages"], list) or any(type(page) is not int or page < 1 for page in value["visual_reviewed_false_pages"]):
        raise ReviewDraftError("review-draft evidence false visual page list is invalid")
    return value


def prepare_review_draft_input_from_files(*, candidate_dir: Path, ledger_path: Path,
        semantic_specs: list[Path], factory_records: list[Path],
        source_dispositions: Path, destination: Path, binding_root: Path,
        reviewed_candidate_dir: Path | None = None) -> dict[str, Any]:
    """Build a sealed draft input from current evidence; never alter book data.

    The proposal supplies each predecessor unresolved string.  This preparer
    reopens its predecessor page bytes and requires that the current candidate
    still contains that exact string before recording the disposition.
    """
    if destination.exists():
        raise ReviewDraftError("review-draft input destination already exists")
    proposal = json.loads(Path(source_dispositions).read_text(encoding="utf-8"))
    rows = proposal.get("rows") if isinstance(proposal, dict) else None
    if not isinstance(rows, list) or proposal.get("unresolved_count") != len(rows):
        raise ReviewDraftError("source disposition proposal is incomplete")
    candidate_dir = Path(candidate_dir); reviewed_candidate_dir = Path(reviewed_candidate_dir or candidate_dir)
    binding_root = Path(binding_root).resolve()
    def record(path: Path) -> dict[str, Any]:
        path = Path(path).resolve()
        try: relative = path.relative_to(binding_root).as_posix()
        except ValueError as error: raise ReviewDraftError(f"binding escapes root: {path}") from error
        return {"path": relative, **file_identity(path)}
    dispositions = []
    for row in rows:
        if not isinstance(row, dict):
            raise ReviewDraftError("source disposition row is malformed")
        page, text, index = row.get("source_page"), row.get("exact_unresolved"), row.get("unresolved_index")
        predecessor = Path(str(row.get("predecessor_path", "")))
        if type(page) is not int or not isinstance(text, str) or type(index) is not int or not predecessor.is_file():
            raise ReviewDraftError("source disposition predecessor is missing")
        if file_identity(predecessor)["sha256"] != row.get("predecessor_sha256"):
            raise ReviewDraftError(f"predecessor page identity changed: {page}")
        old = json.loads(predecessor.read_text(encoding="utf-8"))
        if not isinstance(old.get("unresolved"), list) or index >= len(old["unresolved"]) or old["unresolved"][index] != text:
            raise ReviewDraftError(f"predecessor unresolved preimage mismatch: {page}")
        current = reviewed_candidate_dir / "pages" / f"page-{page:03d}.json"
        if not current.is_file() or text not in json.loads(current.read_text(encoding="utf-8")).get("unresolved", []):
            raise ReviewDraftError(f"successor dropped predecessor unresolved string: {page}")
        kind = row.get("kind")
        categories = {"covered_continuation": "covered_continuation", "source_typography_decision": "source_typography_decision", "administrative_pending": "administrative_pending", "empty_source_bookkeeping": "machine_blocker"}
        if kind not in categories: raise ReviewDraftError(f"unknown source disposition kind: {kind}")
        category = categories[kind]; outcome = "audit_pending" if category == "administrative_pending" else "closed"
        evidence = [record(Path(source_dispositions))]
        if kind == "source_typography_decision":
            proof = row.get("evidence")
            if not isinstance(proof, dict) or not isinstance(proof.get("path"), str):
                raise ReviewDraftError("source typography disposition lacks exact proof")
            proof_path = Path(proof["path"])
            if not proof_path.is_file() or file_identity(proof_path)["sha256"] != proof.get("sha256"):
                raise ReviewDraftError("source typography proof identity changed")
            evidence.append(record(proof_path))
        dispositions.append({"source_page": page, "predecessor_unresolved": text, "category": category, "outcome": outcome, "evidence": evidence, "predecessor": record(predecessor), "current": record(current)})
    manifest_name = "mechanical_draft.json" if (candidate_dir / "mechanical_draft.json").is_file() else "candidate_manifest.json"
    bindings = {"candidate_manifest": record(candidate_dir / manifest_name),
                "ledger": record(Path(ledger_path)), "source_dispositions": record(Path(source_dispositions))}
    if reviewed_candidate_dir.resolve() != candidate_dir.resolve():
        bindings["reviewed_candidate_manifest"] = record(reviewed_candidate_dir / "candidate_manifest.json")
    for index, path in enumerate([*semantic_specs, *factory_records]):
        path = Path(path)
        if not path.is_file(): raise ReviewDraftError(f"missing bound input: {path}")
        bindings[f"input_{index:02d}"] = record(path)
    value = {"schema": INPUT_SCHEMA, "bindings": bindings,
             "source_issues": {"schema": ISSUES_SCHEMA, "issues": []},
             "unresolved_dispositions": dispositions}
    value["input_sha256"] = sha256_bytes(canonical_bytes(value))
    validate_review_draft_input(value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"path": str(destination), **file_identity(destination), "unresolved_count": len(dispositions)}


def prepare_review_draft_staging_successor(*, candidate_dir: Path, prior_ledger_path: Path,
        semantic_candidate_dir: Path, semantic_specs: list[Path], ownership_proposal: Path,
        source_dispositions: Path, destination: Path, binding_root: Path) -> dict[str, Any]:
    """Prepare a new ledger from a mechanical candidate and reviewed draft bytes.

    The successor preserves the old ledger's component decisions except for
    explicitly proposed reader-coverage rows.  It writes fresh *machine
    bindings* for the reviewed drafts; those bindings retain the predecessor
    receipt identity in a separate provenance record and never claim visual
    approval.
    """
    if destination.exists():
        raise ReviewDraftError("review-draft successor destination already exists")
    candidate_dir = Path(candidate_dir).resolve(); semantic_candidate_dir = Path(semantic_candidate_dir).resolve()
    binding_root = Path(binding_root).resolve(); prior_ledger_path = Path(prior_ledger_path).resolve()
    def load(path: Path) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ReviewDraftError(f"cannot read successor input: {path}") from error
    def record(path: Path, root: Path = binding_root) -> dict[str, Any]:
        path = Path(path).resolve()
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError as error:
            raise ReviewDraftError(f"binding escapes root: {path}") from error
        return {"path": relative, **file_identity(path)}
    mechanical = candidate_dir / "mechanical_draft.json"
    semantic_manifest = semantic_candidate_dir / "candidate_manifest.json"
    if not mechanical.is_file() or not semantic_manifest.is_file():
        raise ReviewDraftError("mechanical and semantic candidate manifests are required")
    prior = load(prior_ledger_path); proposal = load(Path(ownership_proposal)); semantic = load(semantic_manifest)
    if prior.get("schema") != "kb_creator.reviewed_staging_ledger.v2":
        raise ReviewDraftError("successor requires a v2 predecessor ledger")
    if proposal.get("schema") != "kb_creator.book_coverage_ownership_proposal.v1" or not isinstance(proposal.get("rows"), list):
        raise ReviewDraftError("coverage ownership proposal is malformed")
    mechanical_pages = {row.get("source_page"): row for row in load(mechanical).get("pages", []) if isinstance(row, dict)}
    semantic_pages = {row.get("source_page"): row for row in semantic.get("pages", []) if isinstance(row, dict)}
    prior_pages = {row.get("source_page"): row for row in prior.get("pages", []) if isinstance(row, dict)}
    if not mechanical_pages or set(mechanical_pages) != set(semantic_pages) or set(mechanical_pages) != set(prior_pages):
        raise ReviewDraftError("successor page domains are incomplete or differ")
    supplied_specs = [Path(path).resolve() for path in semantic_specs]
    declared_specs = semantic.get("inputs", {}).get("specs")
    if not isinstance(declared_specs, list) or len(declared_specs) != len(supplied_specs):
        raise ReviewDraftError("semantic candidate must declare exactly the supplied specs")
    for declared, supplied in zip(declared_specs, supplied_specs):
        if not isinstance(declared, dict) or Path(str(declared.get("path", ""))).resolve() != supplied or file_identity(supplied) != {key: declared.get(key) for key in ("bytes", "sha256")}:
            raise ReviewDraftError("semantic spec identity differs from candidate manifest")
    owners: dict[tuple[int, int], dict[str, Any]] = {}
    for row in proposal["rows"]:
        if not isinstance(row, dict) or row.get("proposed_action") != "covered_by_reader":
            raise ReviewDraftError("coverage proposal contains an unsupported action")
        page, ordinal = row.get("source_page"), row.get("component_ordinal")
        claim = row.get("fidelity_owner", {})
        if (type(page) is not int or type(ordinal) is not int or not isinstance(claim, dict)
                or claim.get("kind") not in {"coverage_claim", "ocr_class_referenced_by_claim"}
                or not isinstance(claim.get("claim_id"), str) or not claim["claim_id"]):
            raise ReviewDraftError("coverage proposal row lacks an exact claim owner")
        key = (page, ordinal)
        if key in owners: raise ReviewDraftError("coverage proposal duplicates a component owner")
        source_keys = row.get("source_keys")
        meaningful = row.get("meaningful_key")
        companions = row.get("empty_companion_keys")
        pending = row.get("pending_companion_keys", [])
        if (not isinstance(source_keys, list) or not isinstance(meaningful, dict)
                or set(meaningful) != {"view_id", "raw_index"} or not isinstance(companions, list)
                or not isinstance(pending, list)):
            raise ReviewDraftError("coverage proposal row lacks closed source-key ownership")
        try:
            component = {(item["view"], item["raw_index"]) for item in source_keys}
            coverage_key = (meaningful["view_id"], meaningful["raw_index"])
            companion_keys = {(item["view_id"], item["raw_index"]) for item in companions}
            pending_keys = {(item["view_id"], item["raw_index"]) for item in pending}
        except (KeyError, TypeError):
            raise ReviewDraftError("coverage proposal source-key ownership is malformed")
        if (not component or len(component) != len(source_keys) or coverage_key not in component
                or len(companion_keys) != len(companions) or len(pending_keys) != len(pending)
                or companion_keys & pending_keys or companion_keys | pending_keys != component - {coverage_key}):
            raise ReviewDraftError("coverage proposal source-key ownership is incomplete or duplicated")
        owners[key] = row
    destination.mkdir(parents=True); receipts = destination / "reviews"; receipts.mkdir()
    successor_pages = []; provenance = []
    for page in sorted(mechanical_pages):
        old = prior_pages[page]
        if old.get("candidate_page") != mechanical_pages[page].get("candidate"):
            raise ReviewDraftError(f"mechanical candidate page differs from predecessor ledger: {page}")
        draft_path = semantic_candidate_dir / str(semantic_pages[page].get("path", ""))
        if not draft_path.is_file(): raise ReviewDraftError(f"semantic candidate page is missing: {page}")
        draft = load(draft_path)
        if draft.get("source_page") != page or not isinstance(draft.get("review"), dict) or type(draft["review"].get("visual_reviewed")) is not bool:
            raise ReviewDraftError(f"semantic draft has no literal review state: {page}")
        row = json.loads(json.dumps(old))
        row["reviewed_draft"] = record(draft_path)
        for resolution in row.get("resolutions", []):
            owner = owners.get((page, resolution.get("ordinal")))
            if owner is None: continue
            if resolution.get("action") != owner.get("old_action") or resolution.get("source_keys") != owner.get("source_keys") or resolution.get("selected") != []:
                raise ReviewDraftError(f"coverage proposal does not match predecessor resolution: {page}")
            resolution["action"] = "covered_by_reader"; resolution["coverage_claim_id"] = owner["fidelity_owner"]["claim_id"]
            resolution["coverage_source_key"] = owner["meaningful_key"]
            resolution["empty_companion_keys"] = owner["empty_companion_keys"]
            if owner.get("pending_companion_keys"):
                resolution["pending_companion_keys"] = owner["pending_companion_keys"]
            resolution["rationale"] = f"{resolution['rationale']} Recomputed reader coverage claim {resolution['coverage_claim_id']} is required at consumption."
        old_receipt = old.get("review_receipt")
        # The staging validator recomputes this same composed-spec hash.  It is
        # a current machine binding, while provenance below retains the older
        # human-review receipt without turning either record into approval.
        from .reviewed_draft_staging import _compose_specs
        spec_sha256 = sha256_bytes(canonical_bytes(_compose_specs(supplied_specs)))
        receipt = {"schema": "kb_creator.reviewed_staging_page_review.v1", "source_page": page,
                   "source_visual": row["target_visual"], "draft_sha256": file_identity(draft_path)["sha256"],
                   "spec_sha256": spec_sha256, "visual_reviewed": draft["review"]["visual_reviewed"],
                   "reviewer": "successor machine binding; predecessor review provenance retained",
                   "notes": "Current draft and source-visual identity binding only; this record does not create visual/source acceptance."}
        receipt_path = receipts / f"page-{page:03d}.json"
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        row["review_receipt"] = {"path": (Path("reviews") / receipt_path.name).as_posix(), **file_identity(receipt_path)}
        successor_pages.append(row)
        provenance.append({"source_page": page, "predecessor_review_receipt": old_receipt,
                           "successor_review_receipt": row["review_receipt"], "literal_visual_reviewed": receipt["visual_reviewed"]})
    ledger = {"schema": prior["schema"], "bindings": dict(prior["bindings"]), "pages": successor_pages}
    # Staging resolves the candidate manifest below ``candidate_dir`` while
    # draft/spec provenance resolves below the broader binding root.
    ledger["bindings"]["candidate_manifest"] = {"path": "mechanical_draft.json", **file_identity(mechanical)}
    ledger["bindings"]["semantic_specs"] = [record(path) for path in supplied_specs]
    ledger_path = destination / "ledger.json"; ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    provenance_value = {"schema": "kb_creator.review_draft_machine_binding_provenance.v1",
                        "prior_ledger": record(prior_ledger_path), "successor_ledger": {"path": "ledger.json", **file_identity(ledger_path)},
                        "coverage_ownership_proposal": record(Path(ownership_proposal), binding_root),
                        "rows": provenance}
    provenance_path = destination / "machine-binding-provenance.json"; provenance_path.write_text(json.dumps(provenance_value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ledger": {"path": str(ledger_path), **file_identity(ledger_path)},
            "provenance": {"path": str(provenance_path), **file_identity(provenance_path)},
            "page_count": len(successor_pages), "coverage_owner_count": len(owners)}
