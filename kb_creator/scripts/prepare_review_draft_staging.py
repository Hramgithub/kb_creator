"""Prepare and probe a review-draft staging successor without book mutation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.review_draft import (
    prepare_review_draft_input_from_files,
    prepare_review_draft_staging_successor,
)
from kb_creator.pipeline.reviewed_draft_staging import stage_reviewed_drafts


def _validate_run_roots(*, candidate_dir: Path, source_run: Path, target_run: Path) -> None:
    """Fail before successor allocation when CLI roots do not match sealed input."""
    source_json = source_run / "run.json"
    target_json = target_run / "run.json"
    if not source_json.is_file() or not target_json.is_file():
        raise ValueError("source-run and target-run must each contain run.json")
    manifest_path = candidate_dir / "mechanical_draft.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_root = Path(manifest["run_root"]).resolve()
        expected_identity = manifest["authorities"]["run"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("candidate mechanical_draft.json lacks sealed run binding") from exc
    if source_run.resolve() != expected_root:
        raise ValueError("source-run does not match candidate sealed run_root")
    if expected_identity != {"path": "run.json", **file_identity(source_json)}:
        raise ValueError("source-run run.json does not match candidate sealed authority")


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("candidate-dir", "prior-ledger", "semantic-candidate-dir", "ownership-proposal",
                 "source-dispositions", "factories", "source-run", "target-run", "source-pdf",
                 "binding-root", "destination"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    destination = Path(args.destination)
    _validate_run_roots(candidate_dir=Path(args.candidate_dir), source_run=Path(args.source_run),
                        target_run=Path(args.target_run))
    manifest = json.loads((Path(args.semantic_candidate_dir) / "candidate_manifest.json").read_text(encoding="utf-8"))
    specs = [Path(row["path"]) for row in manifest["inputs"]["specs"]]
    factories_path = Path(args.factories)
    factories = json.loads(factories_path.read_text(encoding="utf-8"))
    if not isinstance(factories, list):
        raise ValueError("coverage factory file must be a list")
    successor = prepare_review_draft_staging_successor(
        candidate_dir=Path(args.candidate_dir), prior_ledger_path=Path(args.prior_ledger),
        semantic_candidate_dir=Path(args.semantic_candidate_dir), semantic_specs=specs,
        ownership_proposal=Path(args.ownership_proposal), source_dispositions=Path(args.source_dispositions),
        destination=destination, binding_root=Path(args.binding_root),
    )
    draft_input = prepare_review_draft_input_from_files(
        candidate_dir=Path(args.candidate_dir), reviewed_candidate_dir=Path(args.semantic_candidate_dir),
        ledger_path=Path(successor["ledger"]["path"]), semantic_specs=specs,
        factory_records=[factories_path], source_dispositions=Path(args.source_dispositions),
        destination=destination / "review-draft-input.json", binding_root=Path(args.binding_root),
    )
    result = stage_reviewed_drafts(candidate_dir=Path(args.candidate_dir), source_run_root=Path(args.source_run),
        target_run_root=Path(args.target_run), ledger_path=Path(successor["ledger"]["path"]),
        semantic_spec_paths=specs, review_root=Path(args.binding_root), semantic_spec_root=Path(args.binding_root),
        review_receipt_root=destination, mode="review_draft", draft_input=destination / "review-draft-input.json",
        coverage_factories=factories, coverage_source_pdf=Path(args.source_pdf),
        finalized_candidate_dir=Path(args.semantic_candidate_dir),
        destination=destination / "staging")
    print(json.dumps({"successor": successor, "draft_input": draft_input,
                      "coverage_claims": result["evidence"]["coverage_factories"]["source_key_owner_count"], "staging": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
