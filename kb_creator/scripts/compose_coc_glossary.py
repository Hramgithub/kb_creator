"""Compose shared CoC terminology and a selected book glossary."""
import argparse
import json
from pathlib import Path
from kb_creator.pipeline.coc_glossary import DEFAULT_REGISTRY, compose_glossary, verify_glossary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("compose")
    prepare.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    prepare.add_argument("--overlay", type=Path, required=True)
    prepare.add_argument("--book-id", required=True)
    prepare.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = (compose_glossary(args.registry, args.overlay, args.book_id, args.output)
                  if args.command == "compose" else verify_glossary(args.output))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"state": "failed", "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["state"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
