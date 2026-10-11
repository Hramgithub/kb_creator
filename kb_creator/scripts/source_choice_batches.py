"""Prepare bounded source-choice review files or collect their explicit answers."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.source_choice_batches import collect_submissions, prepare_batches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--queue", type=Path, required=True)
    prepare.add_argument("--output", type=Path, required=True)
    prepare.add_argument("--max-choices", type=int, default=25)
    prepare.add_argument("--max-review-chars", type=int, default=50000)
    collect = commands.add_parser("record")
    collect.add_argument("--queue", type=Path, required=True)
    collect.add_argument("--submissions", type=Path, nargs="+", required=True)
    collect.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            result = prepare_batches(args.queue, args.output, max_choices=args.max_choices,
                                     max_review_chars=args.max_review_chars)
        else:
            result = collect_submissions(args.queue, args.submissions, args.output)
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({"state": "failed", "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
