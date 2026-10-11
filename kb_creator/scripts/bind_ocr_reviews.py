"""Bind source-reviewed full-block OCR corrections to a verified Stage04 run."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from kb_creator.pipeline.ocr_review_binding import bind_ocr_reviews


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run-root", "coverage", "source-review", "renders", "metadata", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = bind_ocr_reviews(args.run_root, args.coverage, args.source_review, args.renders, args.metadata, args.output)
    print(json.dumps({"state": result["state"], "pages": result["page_count"], "corrections": len(result["corrections"]), "ledger_sha256": result["ledger_sha256"]}))


if __name__ == "__main__":
    main()
