"""Prepare or validate identity-bound full text-read evidence for a DOCX."""
from __future__ import annotations

import argparse
from pathlib import Path

from kb_creator.pipeline.docx_text_review import record_docx_text_review, write_docx_text_review_task


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--docx", required=True)
    prepare.add_argument("--output", required=True)
    record = commands.add_parser("record")
    record.add_argument("--task", required=True)
    record.add_argument("--submission", required=True)
    record.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        write_docx_text_review_task(Path(args.docx), Path(args.output))
    else:
        record_docx_text_review(Path(args.task), Path(args.submission), Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
