"""Carry verified final text into an identical source's new draft, never its review."""
from __future__ import annotations

import shutil
from pathlib import Path

from . import five_step_language as language
from . import language_continuation as continuation
from .identity import assert_existing_path_components_are_not_reparse, file_identity


def prepare_reused_draft(prior_result: Path, target: Path, output: Path) -> dict:
    for path in (prior_result, target, output):
        assert_existing_path_components_are_not_reparse(path)
    prior_result, target, output = (path.resolve() for path in (prior_result, target, output))
    if output.exists() or any(output.is_relative_to(path) or path.is_relative_to(output)
                              for path in (prior_result, target)):
        raise ValueError("reuse output must be absent and outside both inputs")
    current = continuation.verify_continuation(target)
    if current["phase"] != "documentary_draft":
        raise ValueError("reuse requires a documentary draft task")
    # Artifact verification is deliberately separate from historical code freshness.
    # The old continuation is not resealed or declared current.
    language.verify_language_result(prior_result)
    old_task = language._read(prior_result / "evidence/draft.task.json")
    task_path = Path(current["task_path"])
    task = language._read(task_path)
    if old_task["master_en"] != task["master_en"] or old_task["source_spans"] != task["source_spans"]:
        raise ValueError("reuse requires byte-identical MASTER_EN and source spans")
    if old_task["units"] != task["units"]:
        raise ValueError("reuse requires exact ordered source units, including split metadata")
    prior = language._read(prior_result / "evidence/proofread.submission.json")
    if len(prior["units"]) != len(task["units"]):
        raise ValueError("prior final coverage mismatch")
    rows = []
    for source, final in zip(task["units"], prior["units"]):
        if any(final[key] != source[key] for key in ("unit_id", "source_hash")):
            raise ValueError("prior final unit identity/order mismatch")
        rows.append({"unit_id": source["unit_id"], "source_hash": source["source_hash"],
                     "ru_text": final["final_ru_text"], "unresolved": []})
    provenance_files = {
        "prior-inventory.json": prior_result / "INVENTORY.json",
        "prior-manifest.json": prior_result / "MASTER_RU.manifest.json",
        "prior-proofread.submission.json": prior_result / "evidence/proofread.submission.json",
    }
    provenance = {"schema": "kb_creator.language_draft_reuse.v1",
                  "prior_result": str(prior_result),
                  "prior_evidence": {name: file_identity(path) for name, path in provenance_files.items()},
                  "prior_master_ru": file_identity(prior_result / "MASTER_RU.md"),
                  "prior_glossary": old_task["glossary"], "current_glossary": task["glossary"],
                  "units": len(rows), "review_transferred": False, "new_proofread_required": True}
    submission = {"schema": "kb_creator.five_step_language_draft_submission.v2",
                  "task": language._id(task_path, task_path.parent),
                  "master_en": task["master_en"], "glossary": task["glossary"],
                  "units": rows, "text_reuse": provenance}
    master = language._source(task, "master_en")
    unit_context = language._verified_unit_context(task, master)
    language._draft_rows(task, submission["task"], submission, language._source(task, "glossary"), unit_context)
    report = {**provenance, "state": "draft_ready_for_submission",
              "target_task": {"path": str(task_path), **file_identity(task_path)},
              "mechanical_findings": [], "book_acceptance": "pending"}

    def build(stage: Path) -> None:
        for name, path in provenance_files.items():
            shutil.copyfile(path, stage / name)
            if file_identity(stage / name) != provenance["prior_evidence"][name]:
                raise ValueError("prior evidence changed during copy")
        language._write(stage / "draft.submission.json", language._seal(
            submission["schema"], submission, "submission_sha256"))
        language._write(stage / "reuse-report.json", report)

    language._atomic(output, build)
    return report
