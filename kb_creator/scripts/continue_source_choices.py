from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.source_choice_translation import (
    prepare, prepare_v2, record_decisions, record_decisions_v2,
    verify_ledger, verify_ledger_v2, verify_queue, verify_queue_v2,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare or record an evidence-bound translation source-choice task")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare"); p.add_argument("review_master", type=Path); p.add_argument("candidate", type=Path); p.add_argument("output", type=Path)
    p = sub.add_parser("verify"); p.add_argument("queue", type=Path)
    p = sub.add_parser("verify-ledger"); p.add_argument("ledger", type=Path)
    p = sub.add_parser("record"); p.add_argument("queue", type=Path); p.add_argument("submission", type=Path); p.add_argument("output", type=Path)
    p = sub.add_parser("prepare-v2"); p.add_argument("review_master", type=Path); p.add_argument("candidate", type=Path); p.add_argument("output", type=Path)
    p.add_argument("--binding-root", type=Path, help="Root for relative paths in reviewed source evidence")
    p = sub.add_parser("verify-v2"); p.add_argument("queue", type=Path)
    p = sub.add_parser("verify-ledger-v2"); p.add_argument("ledger", type=Path)
    p = sub.add_parser("record-v2"); p.add_argument("queue", type=Path); p.add_argument("submission", type=Path); p.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.review_master, args.candidate, args.output)
    elif args.command == "prepare-v2":
        result = prepare_v2(args.review_master, args.candidate, args.output, binding_root=args.binding_root)
    elif args.command == "verify":
        result = verify_queue(args.queue)
    elif args.command == "verify-v2":
        result = verify_queue_v2(args.queue)
    elif args.command == "verify-ledger":
        result = verify_ledger(args.ledger)
    elif args.command == "verify-ledger-v2":
        result = verify_ledger_v2(args.ledger)
    elif args.command == "record-v2":
        result = record_decisions_v2(args.queue, args.submission, args.output)
    else:
        result = record_decisions(args.queue, args.submission, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
