"""Build, verify, or submit reviews for a DOCX continuation."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from kb_creator.pipeline.docx_continuation import build_docx_continuation, verify_docx_continuation, submit_docx_reviews, verify_docx_review, REVIEW

def main(argv=None):
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
    b=sub.add_parser("build"); b.add_argument("--language-root",type=Path,required=True); b.add_argument("--output",type=Path,required=True); b.add_argument("--title",required=True); b.add_argument("--reader-options",type=Path,required=True); b.add_argument("--config",type=Path)
    b.add_argument("--runtime", type=Path); b.add_argument("--fidelity-plan", type=Path, required=True)
    v=sub.add_parser("verify"); v.add_argument("--root",type=Path,required=True)
    r=sub.add_parser("review"); r.add_argument("--root",type=Path,required=True); r.add_argument("--output",type=Path,required=True); r.add_argument("--text-submission",type=Path,required=True); r.add_argument("--visual-submission",type=Path,required=True)
    a=p.parse_args(argv)
    if a.cmd=="build":
        runtime = json.loads(a.runtime.read_text(encoding="utf-8-sig")) if a.runtime else None
        result = build_docx_continuation(a.language_root,a.output,title=a.title,reader_options=a.reader_options,config=a.config,runtime=runtime,fidelity_plan=a.fidelity_plan)
    elif a.cmd=="verify":
        result = verify_docx_review(a.root) if (a.root / REVIEW).is_file() else verify_docx_continuation(a.root)
    else:
        result = submit_docx_reviews(a.root,a.output,text_submission=a.text_submission,visual_submission=a.visual_submission)
    print(json.dumps({"state": result["state"], "book_acceptance": result["book_acceptance"]}))
    return 0
if __name__=="__main__": raise SystemExit(main())
