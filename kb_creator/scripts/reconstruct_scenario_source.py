"""Closed CLI for the recovery-only source reconstruction builder."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from scenario_source_reconstruction import ReconstructionStop, build, preflight, remediate, verify

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=("preflight", "build", "remediate", "verify"))
    p.add_argument("--contract", required=True, type=Path)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--recovery-root", required=True, type=Path)
    p.add_argument("--run-root", required=True, type=Path)
    return p

def main() -> int:
    args = parser().parse_args()
    try:
        result = {"preflight": preflight, "build": build, "remediate": remediate, "verify": verify}[args.action](args.contract, args.source, args.recovery_root, args.run_root)
    except (ReconstructionStop, OSError, ValueError, KeyError) as error:
        print(json.dumps({"state": "blocked", "error": str(error)}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
