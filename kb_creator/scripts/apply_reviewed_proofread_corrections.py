"""Apply explicit source-bound correction data before normal language verification."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.reader_quality import amend_proofread_submission


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("task", "submission", "corrections", "output", "ledger"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    if args.output.resolve() == args.ledger.resolve() or args.output.exists() or args.ledger.exists():
        raise ValueError("output and ledger must be distinct absent files")
    read = lambda p: json.loads(p.read_text(encoding="utf-8-sig"))
    out, ledger = amend_proofread_submission(read(args.task), read(args.submission), read(args.corrections))
    for path, value in ((args.output, out), (args.ledger, ledger)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"corrected": len(ledger["corrections"]), "unchanged": ledger["unchanged_units"]}))


if __name__ == "__main__":
    main()
