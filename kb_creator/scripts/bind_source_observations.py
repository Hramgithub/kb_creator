"""Bind human source transcriptions to actual source and reader artifacts."""
import argparse
import json
from pathlib import Path

from kb_creator.pipeline.source_observation_binding import bind_observations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run", "source", "drafts", "observations", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be absent")
    value = bind_observations(run_root=args.run, source_pdf=args.source,
                              drafts_root=args.drafts, observations_path=args.observations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "observations": len(value["observations"]),
                      "held": sum(r["state"] == "held" for r in value["observations"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
