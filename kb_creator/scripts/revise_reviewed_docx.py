"""Create one sealed DOCX successor; write its QA report outside the candidate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.reviewed_docx_revision import revise_docx


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--reviewed-docx", type=Path, required=True)
    parser.add_argument("--source-pdf", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = revise_docx(args.manifest, args.reviewed_docx, args.source_pdf,
                         args.output_root, args.report)
    print(json.dumps({"status": report["status"], "accepted": report["accepted"],
                      "docx_sha256": report["output"]["docx_sha256"],
                      "document": report["output"]["path"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
