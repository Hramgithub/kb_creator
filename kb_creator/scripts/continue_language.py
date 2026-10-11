"""CLI for immutable language successors from an existing verified MASTER_EN."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.language_continuation import (
    prepare_continuation, submit_continuation, verify_continuation,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("prepare")
    start.add_argument("--predecessor-run", type=Path, required=True)
    start.add_argument("--binding-root", type=Path, help="Root for relative paths in reviewed source evidence")
    start.add_argument("--glossary", type=Path, required=True)
    start.add_argument("--system", choices=["coc"], help="Compose the shared system registry with the book glossary")
    start.add_argument("--shared-registry", type=Path)
    start.add_argument("--book-id")
    start.add_argument("--output", type=Path, required=True)
    submit = commands.add_parser("submit")
    submit.add_argument("--continuation", type=Path, required=True)
    submit.add_argument("--submission", type=Path, required=True)
    submit.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--continuation", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            if (args.shared_registry or args.book_id) and not args.system:
                raise ValueError("--system coc required with shared registry/book id")
            from kb_creator.pipeline.coc_glossary import DEFAULT_REGISTRY
            registry = (args.shared_registry or DEFAULT_REGISTRY) if args.system == "coc" else None
            result = prepare_continuation(args.predecessor_run, args.glossary, args.output,
                                          shared_registry=registry, book_id=args.book_id,
                                          review_binding_root=args.binding_root)
        elif args.command == "submit":
            result = submit_continuation(args.continuation, args.submission, args.output)
        else:
            result = verify_continuation(args.continuation)
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({"state": "failed", "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
