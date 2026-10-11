"""Rebind a staging ledger after an identical-payload archived replay.

Only queue provenance changes. Drafts, reviews, decisions and spec identities
are preserved; the normal staging and fidelity gates still decide readiness.
"""
from __future__ import annotations

import copy
from pathlib import Path

from . import reviewed_draft_staging as staging
from .identity import file_identity


def _authorities(prior: Path, target: Path) -> None:
    from . import reconstruction_replay as replay, reconstruction_replay_resume
    replay.validate_replay_artifacts_for_consumption(prior)
    authority = replay.validate_replayed_prefix(target)
    reconstruction_replay_resume.validate_replay_review_queue(authority)


def rebind_staging_ledger(*, prior_run: Path, target_run: Path,
                          ledger_path: Path, review_root: Path) -> tuple[dict, dict]:
    """Derive a candidate only when every page packet and visual is unchanged."""
    prior_run, target_run, ledger_path, review_root = (
        p.resolve(strict=True) for p in (prior_run, target_run, ledger_path, review_root)
    )
    if prior_run == target_run:
        raise ValueError("rebind requires a distinct target run")
    _authorities(prior_run, target_run)
    ledger = staging._read(ledger_path)
    if ledger.get("schema") != staging.LEDGER_SCHEMA:
        raise ValueError("unsupported staging ledger schema")
    old_queue_path = staging._verify(prior_run, ledger["bindings"]["target_queue"], "prior queue")
    new_queue_path = staging._safe_file(target_run, ledger["bindings"]["target_queue"]["path"])
    old_queue, new_queue = staging._read(old_queue_path), staging._read(new_queue_path)
    provenance = {"queue_sha256", "run_identity_sha256", "comparison", "bridge"}
    if ({k: v for k, v in old_queue.items() if k not in provenance}
            != {k: v for k, v in new_queue.items() if k not in provenance}):
        raise ValueError("replay queue content or source contract changed")
    if new_queue.get("source_sha256") != ledger["bindings"]["source_sha256"]:
        raise ValueError("ledger source differs from target queue")
    queue_rows = staging._page_rows(new_queue["items"], "target queue")
    rows = staging._page_rows(ledger["pages"], "ledger")
    if set(rows) != set(queue_rows):
        raise ValueError("ledger does not cover the complete target page domain")
    verified = []
    for page, row in rows.items():
        expected = {**queue_rows[page]["merge_packet"],
                    "path": "outputs/04-visual-merge-bundle/" + queue_rows[page]["merge_packet"]["path"]}
        if row["target_packet"] != expected:
            raise ValueError("ledger packet is not the queue packet")
        for label in ("target_packet", "target_visual"):
            staging._verify(prior_run, row[label], "prior " + label)
            staging._verify(target_run, row[label], "target " + label)
        for label in ("reviewed_draft", "review_receipt"):
            staging._verify(review_root, row[label], label)
        verified.append(page)
    for record in ledger["bindings"]["semantic_specs"]:
        staging._verify(review_root, record, "semantic spec")
    rebound = copy.deepcopy(ledger)
    rebound["bindings"]["target_queue"] = {
        "path": ledger["bindings"]["target_queue"]["path"], **file_identity(new_queue_path)}
    report = {
        "schema": "kb_creator.staging_ledger_rebind.v1",
        "state": "candidate_only", "approval_transferred": False,
        "prior_run": str(prior_run), "target_run": str(target_run),
        "prior_ledger": {"path": str(ledger_path), **file_identity(ledger_path)},
        "prior_queue": ledger["bindings"]["target_queue"],
        "target_queue": rebound["bindings"]["target_queue"],
        "identical_packet_and_visual_pages": sorted(verified),
        "scope": "Only target_queue identity changed; all decisions, drafts, reviews and spec bindings unchanged. Full staging/fidelity still required.",
    }
    return rebound, report
