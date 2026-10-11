"""Rebind only exact reviewed v2 source-choice answers to a successor queue."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.source_choice_rebinding import rebind_source_choice_submissions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old_queue", type=Path)
    parser.add_argument("new_queue", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--old-submission", type=Path, action="append", required=True)
    args = parser.parse_args()
    print(json.dumps(rebind_source_choice_submissions(args.old_queue, args.new_queue,
                                                      args.old_submission, args.output), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
