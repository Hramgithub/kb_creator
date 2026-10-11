"""Compose review-master preparation inputs from a mechanical candidate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# Keep direct ``python kb_creator/scripts/...`` invocation consistent with the
# established script entry points when the repository is not installed.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kb_creator.pipeline.review_draft_preparation import (
    prepare_review_draft_author_inputs,
    prepare_review_draft_inputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mechanical-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--semantic-spec", type=Path, action="append")
    parser.add_argument("--binding-root", type=Path)
    parser.add_argument("--reviewed-draft-pages", type=Path)
    parser.add_argument("--coverage-factories", type=Path)
    args = parser.parse_args()
    if (args.semantic_spec is None) != (args.binding_root is None):
        parser.error("--semantic-spec and --binding-root must be supplied together")
    if (args.reviewed_draft_pages is not None or args.coverage_factories is not None) and args.semantic_spec is None:
        parser.error("--reviewed-draft-pages and --coverage-factories require --semantic-spec and --binding-root")
    if args.semantic_spec is not None:
        factories = None
        if args.coverage_factories is not None:
            try:
                factories = json.loads(args.coverage_factories.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                parser.error(f"cannot read --coverage-factories: {exc}")
            if not isinstance(factories, list):
                parser.error("--coverage-factories must contain a JSON list")
        result = prepare_review_draft_author_inputs(
            mechanical_dir=args.mechanical_dir, config_path=args.config,
            semantic_spec_paths=args.semantic_spec, output_dir=args.output,
            binding_root=args.binding_root, reviewed_draft_pages=args.reviewed_draft_pages,
            coverage_factories=factories,
        )
        print(json.dumps({key: result[key] for key in ("state", "draft_pages", "draft_input", "open_source_issue_count")}, ensure_ascii=False))
        return 0
    result = prepare_review_draft_inputs(mechanical_dir=args.mechanical_dir, config_path=args.config, output_dir=args.output)
    print(json.dumps({key: result[key] for key in ("state", "page_count", "unrenderable_source_count", "forced_selection_count")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
