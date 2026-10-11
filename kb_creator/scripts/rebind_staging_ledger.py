"""Rebind an unchanged reviewed staging ledger to a fresh replay queue."""
import argparse
import json
from pathlib import Path

from kb_creator.pipeline.staging_ledger_rebind import rebind_staging_ledger
from kb_creator.pipeline.identity import file_identity


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("prior-run", "target-run", "ledger", "review-root", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output directory must be absent")
    ledger, report = rebind_staging_ledger(prior_run=args.prior_run, target_run=args.target_run,
        ledger_path=args.ledger, review_root=args.review_root)
    args.output.mkdir(parents=True, exist_ok=False)
    path = args.output / "ledger.json"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
    report["successor_ledger"] = {"path": "ledger.json", **file_identity(path)}
    with (args.output / "rebind-report.json").open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"state": report["state"], "pages": len(report["identical_packet_and_visual_pages"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
