"""Create a deterministic non-authoritative mechanical candidate from verified Stage04."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.mechanical_reconstruction import compile_mechanical_draft


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True, type=Path, help="verified replay/native run root containing Stage04")
    parser.add_argument("--output", required=True, type=Path, help="new destination directory")
    parser.add_argument("--reviewed-corrections", type=Path, help="optional hash-keyed reviewed source corrections JSON")
    parser.add_argument("--bound-reviews", type=Path, help="source/report/render-bound OCR review ledger")
    args = parser.parse_args(argv)
    corrections = None
    if args.reviewed_corrections:
        loaded = json.loads(args.reviewed_corrections.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict): raise ValueError("reviewed corrections must be a JSON object keyed by source SHA-256")
        corrections = loaded
    result = compile_mechanical_draft(args.run_root, args.output, reviewed_corrections=corrections, bound_reviews=args.bound_reviews)
    print(json.dumps({"state": result["state"], "pages": result["page_count"], "holds": result["unresolved_hold_count"], "manifest_sha256": result["manifest_sha256"], "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
