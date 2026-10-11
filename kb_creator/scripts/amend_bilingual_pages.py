from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_creator.pipeline.bilingual_page_amendments import BilingualPageAmendmentError, amend_pages


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply exact reviewed RU amendments to bilingual pages.")
    for name in ("pages", "manifest", "plan", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    try:
        report = amend_pages(args.pages, args.manifest, args.plan, args.output)
    except BilingualPageAmendmentError as error:
        print(json.dumps({"state": "blocked", "reason": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"state": report["state"], "output": str(args.output),
                      "changed_pages": report["changed_pages"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
