from __future__ import annotations
import argparse, json
from pathlib import Path
from kb_creator.pipeline.reader_options_rebind import rebind_reader_options

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--prior-result",type=Path,required=True); p.add_argument("--result",type=Path,required=True); p.add_argument("--options",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--reviewed-bindings",type=Path)
    print(json.dumps(rebind_reader_options(**vars(p.parse_args())),ensure_ascii=False,indent=2))
if __name__ == "__main__": main()
