"""Build or verify a complete review package from explicit artifact selections."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.review_bundle import build_review_bundle, verify_review_bundle


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--selection", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build":
        selection = json.loads(args.selection.read_text(encoding="utf-8-sig"))
        if set(selection) != {"metadata", "entries"}:
            parser.error("selection requires metadata and entries")
        entries = [{**entry, "source": args.selection.resolve().parent / entry["source"]} for entry in selection["entries"]]
        result = build_review_bundle(args.output_root, entries=entries, metadata=selection["metadata"])
    else:
        result = verify_review_bundle(args.root)
    print(json.dumps(result, ensure_ascii=False, default=str, indent=2))


if __name__ == "__main__":
    main()
