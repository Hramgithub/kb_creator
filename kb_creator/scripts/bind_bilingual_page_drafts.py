from __future__ import annotations
import argparse
from pathlib import Path
from kb_creator.pipeline.bilingual_draft_binding import BilingualDraftBindingError, bind

def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("task", "template", "pages", "asset-manifest", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--explicit-translations", type=Path)
    args = parser.parse_args()
    try:
        report = bind(args.task, args.template, args.pages, args.asset_manifest, args.output, explicit_translations=args.explicit_translations)
    except BilingualDraftBindingError as error:
        print(f"state=hold reason={error}")
        return 2
    print(f"state={report['state']} pages={report['pages']} units={report['units']} output={args.output}")
    return 0 if report["state"] != "blocked" else 2

if __name__ == "__main__":
    raise SystemExit(main())
