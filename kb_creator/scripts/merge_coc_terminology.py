"""Prepare or apply an evidence-preserving CoC terminology consolidation."""
import argparse
import json
from pathlib import Path
from kb_creator.pipeline.coc_glossary import DEFAULT_REGISTRY
from kb_creator.pipeline.coc_terminology_merge import prepare_merge, apply_merge, apply_reviewed_amendments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("prepare")
    plan.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    plan.add_argument("--inventory", type=Path, required=True)
    plan.add_argument("--output", type=Path, required=True)
    plan.add_argument("--evidence-ref", required=True)
    apply = commands.add_parser("apply")
    apply.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    apply.add_argument("--bundle", type=Path, required=True)
    amend = commands.add_parser("amend")
    amend.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    amend.add_argument("--decisions", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            result = prepare_merge(args.registry, args.inventory, args.output, args.evidence_ref)
            result = {"state": "prepared", "rows": result["total_rows"], "added": len(result["added"]), "conflicts": len(result["conflicts"])}
        elif args.command == "apply":
            result = apply_merge(args.registry, args.bundle)
        else:
            result = apply_reviewed_amendments(args.registry, args.decisions)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        result = {"state": "failed", "error": str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result["state"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
