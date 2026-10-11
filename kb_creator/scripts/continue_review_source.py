"""Verify authored source or explicitly continue its reviewed structural successor."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.review_source_continuation import (
    continue_structural_source, verify_authored_source,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    for operation in ("verify", "structural"):
        command = commands.add_parser(operation)
        command.add_argument("--request", type=Path, required=True,
                             help="Sealed explicit request; paths and runtime must be reviewed and pinned")
    args = parser.parse_args(argv)
    try:
        result = (verify_authored_source if args.operation == "verify" else continue_structural_source)(args.request)
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({"state": "failed", "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"state": result["state"], "operation": result["operation"],
                      "receipt_sha256": result["receipt_sha256"], "accepted": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
