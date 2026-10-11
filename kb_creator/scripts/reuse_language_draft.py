"""Prepare a new draft from verified final text with unchanged English inputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.language_draft_reuse import prepare_reused_draft


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("prior-result", "continuation", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        report = prepare_reused_draft(args.prior_result, args.continuation, args.output)
    except (ValueError, OSError, KeyError) as error:
        print(json.dumps({"state": "failed", "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
