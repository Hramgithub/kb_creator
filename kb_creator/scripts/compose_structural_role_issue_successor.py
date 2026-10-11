"""CLI for immutable structural-role review-input successors."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.review_draft_preparation import compose_structural_role_issue_successor


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--binding-root", required=True, type=Path)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--preview", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    result = compose_structural_role_issue_successor(
        input_path=args.input, binding_root=args.binding_root, run_root=args.run,
        authored_preview_root=args.preview, destination=args.destination)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
