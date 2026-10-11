"""Create a validated reviewed-artifact reader successor from a sealed manifest."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from kb_creator.pipeline.reviewed_reader_revision import RevisionError, revise_reader


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--docx", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--source-pdf", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = revise_reader(args.manifest, args.docx, args.html, args.assets, args.source_pdf, args.output_root)
    except RevisionError as error:
        print(json.dumps({"state": "blocked", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps({"status": report["status"], "output_root": args.output_root.resolve().as_posix(),
                      "docx_sha256": report["outputs"]["docx_sha256"],
                      "html_sha256": report["outputs"]["html_sha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
