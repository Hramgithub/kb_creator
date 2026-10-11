from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.bilingual_boundary_moves import BilingualBoundaryMoveError, move_pages


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize reviewed exact bilingual cross-page RU moves.")
    for name in ("pages", "manifest", "plan", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    try:
        report = move_pages(args.pages, args.manifest, args.plan, args.output)
    except BilingualBoundaryMoveError as error:
        print(json.dumps({"state": "blocked", "reason": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"state": report["state"], "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
