"""Compile a reviewed-staging ledger into cold-authoring drafts."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_creator.pipeline.reviewed_draft_staging import stage_reviewed_drafts

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, required=True); parser.add_argument("--source-run", type=Path, required=True); parser.add_argument("--target-run", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True); parser.add_argument("--semantic-spec", type=Path, required=True, nargs="+"); parser.add_argument("--review-root", type=Path); parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args(); result = stage_reviewed_drafts(candidate_dir=args.candidate_dir, source_run_root=args.source_run, target_run_root=args.target_run, ledger_path=args.ledger, semantic_spec_paths=args.semantic_spec, review_root=args.review_root, destination=args.destination)
    print(json.dumps({"state": result["state"], "destination": str(args.destination)}, ensure_ascii=False)); return 0

if __name__ == "__main__": raise SystemExit(main())
