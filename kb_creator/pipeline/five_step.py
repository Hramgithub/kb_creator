"""Resumable PDF-to-DOCX profile; content tasks are executed by an external agent."""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from typing import Any

from .identity import canonical_bytes, deterministic_inventory, file_identity, sha256_bytes
from .manifests import sealed, validate_seal

SCHEMA = "kb_creator.five_step_run.v3"
PREVIOUS_SCHEMA = "kb_creator.five_step_run.v2"
LEGACY_SCHEMA = "kb_creator.five_step_run.v1"
ROOT = Path(__file__).resolve().parents[2]
STEPS = ("reconstruction", "master_en", "documentary_draft", "proofread_final", "docx")
PHASE_STEP = {"intake": 1, "reconstruct": 1, "reconstruction": 1, "master_en": 2,
              "prepare_language": 3, "documentary_draft": 3, "proofread_final": 4,
              "reader_options": 5, "docx": 5, "docx_text_review": 5, "docx_visual": 5, "complete": 5}
DEPENDENCIES = {
    1: ["pipeline/five_step_intake.py", "pipeline/reconstruction.py", "pipeline/reconstruction_promotion.py",
        "pipeline/mineru_cpu_first.py", "pipeline/coc_glossary.py", "scripts/prepare_mineru_three_view_inputs.py",
        "scripts/run_mineru_three_view.ps1", "scripts/compare_mineru_three_views.py",
        "scripts/build_mineru_visual_merge_bundle.py", "scripts/audit_mineru_ai_merge_fidelity.py",
        "scripts/materialize_mineru_ai_merge.py", "scripts/author_reviewed_semantic_decisions.py",
        "pipeline/reviewed_line_group.py", "pipeline/reviewed_prose_binding.py"],
    2: ["pipeline/five_step_intake.py", "scripts/build_scenario_master_en.py", "scripts/verify_scenario_master_en.py"],
    3: ["pipeline/five_step_language.py", "pipeline/language_context.py", "pipeline/language_unit_context.py", "pipeline/language_numeric.py", "scripts/scenario_master_ru.py", "scripts/prepare_translation_batches.py"],
    4: ["pipeline/five_step_language.py", "pipeline/language_context.py", "pipeline/language_unit_context.py", "pipeline/language_numeric.py", "scripts/scenario_master_ru.py", "scripts/verify_scenario_master_ru.py"],
    5: ["pipeline/five_step_docx.py", "pipeline/reader_projection.py", "pipeline/reader_block_relocation.py", "pipeline/docx_text_review.py", "scripts/review_docx_text.py", "scripts/production_docx.py", "scripts/publication_render_qa.py", "scripts/export_docx_to_pdf_local.py"],
}


class FiveStepError(ValueError):
    pass


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise FiveStepError(f"JSON object required: {path}")
    return value


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _save(root: Path, state: dict[str, Any]) -> None:
    state.pop("state_sha256", None)
    state.update(sealed(SCHEMA, state, digest_key="state_sha256"))
    _write(root / "state.json", state)


def _module(name: str):
    return importlib.import_module(f"kb_creator.pipeline.five_step_{name}")


def _codes(step: int) -> list[dict[str, Any]]:
    paths = [ROOT / "kb_creator" / name for name in DEPENDENCIES[step]]
    paths += [Path(__file__), ROOT / "kb_creator/pipeline/identity.py", ROOT / "kb_creator/pipeline/manifests.py",
              ROOT / "kb_creator/pipeline/semantic_structure.py",
              ROOT / "kb_creator/pipeline/reviewed_correction_text.py",
              ROOT / "kb_creator/pipeline/reviewed_prose_binding.py"]
    if step == 1:
        from .reconstruction import _implementation_paths
        paths += _implementation_paths()
        from .reconstruction_replay import REPLAY_IMPLEMENTATION_PATHS
        from .reconstruction_replay_resume import DOWNSTREAM_IMPLEMENTATION
        paths += [ROOT / name for name in (*REPLAY_IMPLEMENTATION_PATHS, *DOWNSTREAM_IMPLEMENTATION)]
    if step in {3, 4}:
        paths += [ROOT / "kb_creator/scripts/merge_translation_batches.py", ROOT / "kb_creator/scripts/prepare_translation_batches.py", ROOT / "kb_creator/pipeline/coc_glossary.py"]
    if step == 5:
        paths += list((ROOT / "translator").glob("*.py"))
    return [{"path": p.relative_to(ROOT).as_posix(), **file_identity(p)} for p in sorted(set(paths))]


def _next(root: Path, name: str) -> Path:
    for number in range(1, 10000):
        path = root / f"{name}-{number:03}"
        if not path.exists():
            return path
    raise FiveStepError("too many attempts")


def _record(root: Path, state: dict[str, Any], directory: Path, step: int) -> None:
    directory = directory.resolve(strict=True)
    relative = directory.relative_to(root.resolve()).as_posix()
    state["evidence"].append({"step": step, "root": relative, "files": deterministic_inventory(directory), "code": _codes(step)})


def _load(root: Path, *, rebuilding_docx: bool = False, allow_legacy_read_only: bool = False) -> dict[str, Any]:
    state = _json(root / "state.json")
    validate_seal(state, "state_sha256")
    legacy = state.get("schema") in {LEGACY_SCHEMA, PREVIOUS_SCHEMA} and allow_legacy_read_only
    if state.get("schema") != SCHEMA and not legacy:
        raise FiveStepError("unsupported run state")
    if legacy and state.get("profile") != ("five_step_docx_v1" if state["schema"] == LEGACY_SCHEMA else "five_step_docx_v2"):
        raise FiveStepError("invalid legacy run profile")
    for key in ("source", "glossary"):
        record = state[key]
        if file_identity(Path(record["path"])) != record["identity"]:
            raise FiveStepError(f"{key} changed; start a successor run, dependent results cannot be reused")
    terminology = state.get("terminology")
    if terminology is not None:
        from .coc_glossary import verify_glossary
        if (not isinstance(terminology, dict) or set(terminology) != {"system", "book_id", "root"}
                or terminology["system"] != "coc" or terminology["root"] != "terminology"):
            raise FiveStepError("terminology authority is malformed")
        composed = verify_glossary(root / "terminology")
        if (composed["state"] != "ready" or composed["book_id"] != terminology["book_id"]
                or Path(composed["glossary_path"]).resolve() != Path(state["glossary"]["path"]).resolve()):
            raise FiveStepError("shared/book terminology is conflicted or unbound")
    reader_options = state.get("reader_options")
    if reader_options is not None:
        if not isinstance(reader_options, dict) or set(reader_options) != {"path", "identity"}:
            raise FiveStepError("reader options authority is malformed")
        path = Path(str(reader_options["path"]))
        if not path.is_file() or file_identity(path) != reader_options["identity"]:
            raise FiveStepError("reader options changed; start a successor run, dependent results cannot be reused")
    if not legacy:
        for key in ("source_inventory", "source_review"):
            record = state.get(key)
            if not isinstance(record, dict) or set(record) != {"path", "identity"}:
                raise FiveStepError(f"{key} authority is missing from guarded run")
            path = Path(str(record["path"]))
            if not path.is_file() or file_identity(path) != record["identity"]:
                raise FiveStepError(f"{key} authority changed")
        plan = state.get("fidelity_plan")
        if plan is not None:
            if not isinstance(plan, dict) or set(plan) != {"path", "identity"}:
                raise FiveStepError("source-fidelity plan authority is malformed")
            path = Path(str(plan["path"]))
            if not path.is_file() or file_identity(path) != plan["identity"]:
                raise FiveStepError("source-fidelity plan authority changed")
    for record in state["evidence"] + state.get("predecessor_docx_evidence", []):
        base = (root / record["root"]).resolve(strict=True)
        if not base.is_relative_to(root.resolve()):
            raise FiveStepError("evidence root escapes run")
        for item in record["files"]:
            path = (base / item["path"]).resolve(strict=True)
            if not path.is_relative_to(base) or file_identity(path) != {k: item[k] for k in ("bytes", "sha256")}:
                raise FiveStepError(f"changed evidence: {item['path']}")
        if record in state["evidence"] and not legacy and not (rebuilding_docx and record["step"] == 5):
            if record["code"] != _codes(record["step"]):
                raise FiveStepError(f"step {record['step']} implementation changed; verified successor required")
    return state


def _view(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    current = PHASE_STEP[state["phase"]]
    return {"schema": SCHEMA, "run_root": str(root.resolve()), "state": state["state"],
            "phase": state["phase"], "step": current,
            "steps": [{"number": n, "name": name, "state": "complete" if n < current or state["phase"] == "complete" else "active" if n == current else "pending"} for n, name in enumerate(STEPS, 1)],
            "task_path": state.get("task_path"), "template_path": state.get("template_path"),
            "reason": state.get("reason"), "docx_path": state.get("docx_path"),
            "exit_code": 2 if state["state"] == "failed" else 0}


def status(run_root: Path) -> dict[str, Any]:
    """Read and validate without changing any run bytes."""
    state = _load(run_root, allow_legacy_read_only=True)
    if state["schema"] in {LEGACY_SCHEMA, PREVIOUS_SCHEMA}:
        return {"schema": state["schema"], "profile": state["profile"], "run_root": str(run_root.resolve()),
                "state": "legacy_read_only", "historical_state": state["state"], "phase": state["phase"],
                "source_completeness": "not_assessed", "mutation": "retired", "exit_code": 0}
    return _view(run_root, state)


def _waiting(state: dict[str, Any], phase: str, result: dict[str, Any]) -> None:
    state.update(phase=phase, state="needs_agent_work", task_path=str(result["task_path"]),
                 template_path=str(result["template_path"]) if result.get("template_path") else None, reason=None)


def start(source: Path, glossary: Path, run_root: Path, *, title: str | None = None,
          runtime: dict[str, Any] | None = None, docx_config: Path | None = None,
          replay_from: Path | None = None, system: str | None = None,
          book_id: str | None = None, shared_registry: Path | None = None, recovery_plan: Path | None = None,
          archived_replay: bool = False, source_inventory: Path | None = None,
          source_review: Path | None = None) -> dict[str, Any]:
    if source_inventory is None or source_review is None:
        raise FiveStepError("guarded run requires source inventory and all-page review before start")
    from .source_graphics import validate_produced_inventory, validate_review
    try:
        validate_produced_inventory(source_inventory, source_pdf=source)
        validate_review(source_review, source_inventory, source_pdf=source)
    except ValueError as error:
        raise FiveStepError(f"source graphic review is not closed: {error}") from error
    source, glossary, run_root = source.resolve(strict=True), glossary.resolve(strict=True), run_root.resolve()
    if run_root.exists():
        raise FiveStepError("run root already exists; use status/resume")
    if source.suffix.lower() != ".pdf":
        raise FiveStepError("source must be PDF")
    if system not in {None, "coc"} or (system is None and (book_id is not None or shared_registry is not None)) or (system == "coc" and not book_id):
        raise FiveStepError("shared terminology requires --system coc and --book-id")
    if replay_from is not None and recovery_plan is not None:
        raise FiveStepError("replay and verified-view recovery are mutually exclusive")
    if archived_replay and replay_from is None:
        raise FiveStepError("archived replay requires --replay-from")
    if archived_replay and recovery_plan is not None:
        raise FiveStepError("archived replay and verified-view recovery are mutually exclusive")
    state = {"schema": SCHEMA, "profile": "five_step_docx_v3", "phase": "intake", "state": "running",
             "source": {"path": str(source), "identity": file_identity(source)},
             "source_inventory": {"path": str(source_inventory.resolve(strict=True)), "identity": file_identity(source_inventory)},
             "source_review": {"path": str(source_review.resolve(strict=True)), "identity": file_identity(source_review)},
             "glossary": {"path": str(glossary), "identity": file_identity(glossary)},
             "title": title or source.stem, "runtime": runtime or {}, "evidence": [], "paths": {},
             "docx_config": str(docx_config.resolve(strict=True)) if docx_config else None,
              "replay_from": str(replay_from.resolve(strict=True)) if replay_from else None,
              "archived_replay": archived_replay,
              "recovery_plan": {"path": str(recovery_plan.resolve(strict=True)), "identity": file_identity(recovery_plan.resolve(strict=True))} if recovery_plan else None,
             "require_reader_options": True}
    run_root.mkdir(parents=True)
    _save(run_root, state)
    try:
        if system == "coc":
            from .coc_glossary import DEFAULT_REGISTRY, compose_glossary
            state["terminology"] = {"system": "coc", "book_id": book_id, "root": "terminology"}
            composed = compose_glossary(shared_registry or DEFAULT_REGISTRY, glossary, book_id, run_root / "terminology")
            if composed["state"] != "ready":
                raise FiveStepError("shared/book terminology conflicts; inspect terminology/conflicts.json")
            effective = Path(composed["glossary_path"]).resolve(strict=True)
            state["glossary"] = {"path": str(effective), "identity": file_identity(effective)}
        intake = _next(run_root, "intake")
        result = _module("intake").prepare_intake(source, intake, title=state["title"])
        state["paths"]["intake"] = str(intake)
        _record(run_root, state, intake, 1)
        _waiting(state, "intake", result)
    except Exception as error:
        state.update(state="failed", reason=f"{type(error).__name__}: {error}")
    _save(run_root, state)
    return _view(run_root, state)


def _runtime(state: dict[str, Any]):
    from .reconstruction import RuntimeOptions
    values = state["runtime"].get("reconstruction", {})
    required = {"mineru_root", "pdftoppm", "powershell", "provider_capabilities", "mineru_source_root", "ocr_language"}
    if not required.issubset(values):
        raise FiveStepError("runtime.reconstruction missing CPU-first paths/language: " + ", ".join(sorted(required - set(values))))
    paths = {"mineru_root", "pdftoppm", "powershell", "python", "provider_capabilities", "mineru_source_root"}
    return RuntimeOptions(**{k: Path(v) if k in paths else v for k, v in values.items()})


def _visual_task(root: Path, state: dict[str, Any], result: dict[str, Any]) -> None:
    package = Path(state["paths"]["docx"])
    pages = result.get("render_pages") or [str(p) for p in sorted(package.rglob("page-*.png"))]
    if not pages:
        raise FiveStepError("DOCX was not rendered; no visual review can be requested")
    records = []
    for index, value in enumerate(pages, 1):
        path = Path(value)
        if not path.is_absolute():
            path = package / path
        path = path.resolve(strict=True)
        if not path.is_relative_to(package.resolve()):
            raise FiveStepError("render page escapes package")
        records.append({"page": index, "path": str(path), **file_identity(path)})
    task = sealed("kb_creator.five_step_visual_task.v1", {"kind": "docx_visual",
                   "docx": {"path": str(result["docx_path"]), **file_identity(Path(result["docx_path"]))},
                   "pages": records,
                   "instructions": "Inspect every page image against MASTER_RU and source: no omissions, clipping, broken tables/statblocks, displaced art or links. Report unresolved findings; machine rendering alone is not review."}, digest_key="task_sha256")
    task_dir = _next(root, "visual-task")
    task_dir.mkdir()
    _write(task_dir / "task.json", task)
    _write(task_dir / "submission.template.json", {"schema": "kb_creator.five_step_visual_submission.v1",
           "task_sha256": task["task_sha256"], "reviewer_role": "agent", "pages": [{"page": r["page"], "reviewed": False, "findings": []} for r in records], "unresolved": []})
    _record(root, state, task_dir, 5)
    _waiting(state, "docx_visual", {"task_path": task_dir / "task.json", "template_path": task_dir / "submission.template.json"})


def _docx_text_review_task(root: Path, state: dict[str, Any], result: dict[str, Any]) -> None:
    """Materialize exhaustive DOCX text-read coverage before visual review."""
    from .docx_text_review import prepare_docx_text_review
    docx_path = Path(result["docx_path"]).resolve(strict=True)
    task = prepare_docx_text_review(docx_path)
    task_dir = _next(root, "text-review-task")
    task_dir.mkdir()
    template = {
        "schema": "kb_creator.docx_text_review_submission.v1",
        "task_sha256": task["task_sha256"], "docx": task["docx"], "reviewer_role": "agent",
        "blocks": [{"block_id": row["block_id"], "text_sha256": row["text_sha256"], "read": False} for row in task["blocks"]],
        "findings": [],
    }
    _write(task_dir / "task.json", task)
    _write(task_dir / "submission.template.json", template)
    _record(root, state, task_dir, 5)
    _waiting(state, "docx_text_review", {"task_path": task_dir / "task.json", "template_path": task_dir / "submission.template.json"})


def _accept_docx_text_review(root: Path, state: dict[str, Any], submission: Path) -> None:
    from .docx_text_review import validate_docx_text_review
    task = _json(Path(state["task_path"]))
    docx_path = Path(state["docx_path"])
    expected_docx = {"path": docx_path.name, **file_identity(docx_path)}
    if task.get("docx") != expected_docx:
        raise FiveStepError("DOCX text review task does not bind active DOCX")
    try:
        record = validate_docx_text_review(task, _json(submission))
    except Exception as error:
        raise FiveStepError(f"DOCX text review invalid: {error}") from error
    output = _next(root, "text-review")
    output.mkdir()
    _write(output / "review.json", record)
    _record(root, state, output, 5)
    _visual_task(root, state, {"docx_path": str(docx_path)})


def _reader_options_task(root: Path, state: dict[str, Any]) -> None:
    """Request source-bound presentation decisions before the first DOCX attempt."""
    final = Path(state["paths"]["final"])
    master = final / "MASTER_RU.md"
    projection = final / "semantic_context" / "RU_PROJECTION.json"
    if not master.is_file() or not projection.is_file():
        raise FiveStepError("verified MASTER_RU and RU_PROJECTION are required for reader options")
    task_dir = _next(root, "reader-options-task")
    task_dir.mkdir()
    source = state["source"]
    task = sealed("kb_creator.five_step_reader_options_task.v1", {
        "kind": "reader_options",
        "master_ru": {"path": "MASTER_RU.md", **file_identity(master)},
        "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **file_identity(projection)},
        "source_pdf": {"path": source["path"], **source["identity"]},
        "instructions": "Review the source PDF and complete sealed reader options. Classify source TOC as present or absent; unresolved or stale bindings must not be submitted.",
    }, digest_key="task_sha256")
    template = {
        "schema": "kb_creator.five_step_reader_options.v1",
        "master_ru": task["master_ru"],
        "ru_projection": task["ru_projection"],
        "source_toc": {"state": "unresolved", "source_pdf_sha256": source["identity"]["sha256"], "reason": "Complete after source review"},
        "body_links": [], "asset_choices": [], "hit_points": {}, "display_roles": [],
    }
    _write(task_dir / "task.json", task)
    _write(task_dir / "options.template.json", template)
    _record(root, state, task_dir, 5)
    _waiting(state, "reader_options", {"task_path": task_dir / "task.json", "template_path": task_dir / "options.template.json"})


def _bind_reader_options(state: dict[str, Any], reader_options: Path) -> None:
    """Validate the existing projection contract before DOCX output allocation."""
    options_path = reader_options.resolve(strict=True)
    final = Path(state["paths"]["final"])
    master = final / "MASTER_RU.md"
    projection = final / "semantic_context" / "RU_PROJECTION.json"
    from .reader_projection import load_options
    try:
        options = load_options(options_path, master, projection)
    except Exception as error:
        raise FiveStepError(f"reader options invalid: {error}") from error
    source_toc = options.get("source_toc")
    if not isinstance(source_toc, dict) or source_toc.get("state") not in {"present", "absent"}:
        raise FiveStepError("reader options source TOC classification must be reviewed as present or absent")
    if source_toc.get("source_pdf_sha256") != state["source"]["identity"]["sha256"]:
        raise FiveStepError("reader options source PDF binding mismatch")
    state["reader_options"] = {"path": str(options_path), "identity": file_identity(options_path)}


def resume(run_root: Path, *, submission: Path | None = None, decisions_root: Path | None = None,
           runtime: dict[str, Any] | None = None, reader_options: Path | None = None,
           fidelity_plan: Path | None = None) -> dict[str, Any]:
    root = run_root.resolve(strict=True)
    state = _load(root)
    if runtime is not None:
        if state["phase"] not in {"intake", "reconstruct", "reader_options", "docx"}:
            raise FiveStepError("runtime can only be set before a mechanical stage")
        state["runtime"] = runtime
    if state["phase"] == "complete":
        return _view(root, state)
    paths = state["paths"]
    phase = state["phase"]
    if (phase == "docx" or (phase == "reader_options" and reader_options is not None)) and fidelity_plan is None:
        raise FiveStepError("closed source-fidelity plan is required before DOCX generation")
    if fidelity_plan is not None and phase in {"docx", "reader_options"}:
        from .reader_fidelity import validate_plan
        plan = validate_plan(fidelity_plan, source_pdf=Path(state["source"]["path"]),
                             master_ru=Path(paths["master_ru"]))
        for key, plan_key in (("source_inventory", "inventory"), ("source_review", "review")):
            bound = state[key]
            if (plan[plan_key]["path"] != bound["path"] or
                    {k: plan[plan_key][k] for k in ("bytes", "sha256")} != bound["identity"]):
                raise FiveStepError(f"{key} differs from run authority")
        configured = state.get("docx_config")
        if (configured is None or
                plan["config"] != {"path": str(Path(configured).resolve(strict=True)),
                                   **file_identity(Path(configured))}):
            raise FiveStepError("DOCX config differs from reviewed fidelity plan")
    if phase == "reader_options" and reader_options is None:
        return _view(root, state)
    if phase in {"intake", "reconstruction", "documentary_draft", "proofread_final", "docx_text_review", "docx_visual"} and submission is None:
        return _view(root, state)
    try:
        state.update(state="running", reason=None)
        if phase == "intake":
            output = _next(root, "contract")
            result = _module("intake").submit_intake(Path(paths["intake"]), submission, output)
            paths["contract"] = str(result["contract_path"])
            _record(root, state, output, 1)
            state["phase"] = "reconstruct"
            state.update(task_path=None, template_path=None)
            _save(root, state)
        elif phase == "reconstruction":
            if decisions_root is None:
                raise FiveStepError("reconstruction submission requires --decisions-root")
            result = _module("intake").finish_reconstruction(Path(paths["reconstruction"]), submission, decisions_root)
            paths.update(reconstruction_root=str(result["reconstruction_root"]), reconstruction_review=str(result["review_path"]))
            _record(root, state, Path(paths["reconstruction"]), 1)
            state["phase"] = "master_en"
            state.update(task_path=None, template_path=None)
            _save(root, state)
        elif phase == "documentary_draft":
            output = _next(root, "draft")
            result = _module("language").submit_draft(Path(paths["language"]), submission, output)
            paths["draft"] = str(output)
            _record(root, state, output, 3)
            _waiting(state, "proofread_final", result)
        elif phase == "proofread_final":
            output = _next(root, "final")
            result = _module("language").submit_proofread(Path(paths["language"]), Path(paths["draft"]), submission, output)
            _module("language").verify_language_result(output)
            paths.update(final=str(output), master_ru=str(result["master_ru"]))
            _record(root, state, output, 4)
            if state.get("require_reader_options", False):
                _reader_options_task(root, state)
            else:
                state["phase"] = "docx"
                state.update(task_path=None, template_path=None)
            _save(root, state)
        elif phase == "reader_options":
            _bind_reader_options(state, reader_options)
            state["phase"] = "docx"
            state.update(task_path=None, template_path=None)
            _save(root, state)
        elif phase == "docx_text_review":
            _accept_docx_text_review(root, state, submission)
        elif phase == "docx_visual":
            _accept_visual(root, state, submission)
        while state["state"] == "running" and state["phase"] != "complete":
            phase = state["phase"]
            if phase == "reconstruct":
                scenario_id = _json(Path(paths["contract"]))["scenario"]["id"]
                parent = root / "upstream" / scenario_id / "reconstruction"
                parent.mkdir(parents=True, exist_ok=True)
                reconstruction = _next(parent, "reconstruction")
                replay = state.get("replay_from")
                options = {"replay_from": Path(replay)} if replay else {}
                if state.get("archived_replay"):
                    options["archived_replay"] = True
                if state.get("recovery_plan"):
                    plan = state["recovery_plan"]
                    if file_identity(Path(plan["path"])) != plan["identity"]:
                        raise FiveStepError("recovery plan changed")
                    options["recovery_plan"] = Path(plan["path"])
                result = _module("intake").start_reconstruction(Path(paths["contract"]), Path(state["source"]["path"]), reconstruction, reconstruction.name, _runtime(state), **options)
                paths["reconstruction"] = str(reconstruction)
                _record(root, state, reconstruction, 1)
                _waiting(state, "reconstruction", result)
            elif phase == "master_en":
                output = _next(root, "master-en")
                result = _module("intake").build_master_en(Path(paths["reconstruction_root"]), Path(paths["reconstruction_review"]), output)
                paths["master_en"] = str(result["master_en"])
                _record(root, state, output, 2)
                state["phase"] = "prepare_language"
                _save(root, state)
            elif phase == "prepare_language":
                output = _next(root, "language")
                result = _module("language").prepare_language(Path(paths["master_en"]), Path(state["glossary"]["path"]), output)
                paths["language"] = str(output)
                _record(root, state, output, 3)
                _waiting(state, "documentary_draft", result)
            elif phase == "docx":
                _module("language").verify_language_result(Path(paths["final"]))
                from .reader_fidelity import validate_plan
                plan = validate_plan(fidelity_plan, source_pdf=Path(state["source"]["path"]),
                                     master_ru=Path(paths["master_ru"]))
                for key, plan_key in (("source_inventory", "inventory"), ("source_review", "review")):
                    bound = state[key]
                    if (plan[plan_key]["path"] != bound["path"] or
                            {k: plan[plan_key][k] for k in ("bytes", "sha256")} != bound["identity"]):
                        raise FiveStepError(f"{key} differs from run authority")
                state["fidelity_plan"] = {"path": str(fidelity_plan.resolve(strict=True)),
                                          "identity": file_identity(fidelity_plan)}
                output = _next(root, "docx")
                result = _module("docx").build_docx_package(Path(paths["master_ru"]), output, title=state["title"],
                    config=Path(state["docx_config"]) if state["docx_config"] else None, runtime=state["runtime"].get("docx"),
                    reader_options=Path(state["reader_options"]["path"]) if state.get("reader_options") else None,
                    fidelity_plan=fidelity_plan)
                _module("docx").verify_docx_package(output)
                paths["docx"] = str(output)
                state["docx_path"] = str(result["docx_path"])
                _record(root, state, output, 5)
                _docx_text_review_task(root, state, result)
            else:
                raise FiveStepError(f"unsupported automatic phase: {phase}")
    except Exception as error:
        state.update(state="failed", reason=f"{type(error).__name__}: {error}")
    _save(root, state)
    return _view(root, state)


def _accept_visual(root: Path, state: dict[str, Any], submission: Path) -> None:
    task = _json(Path(state["task_path"]))
    value = _json(submission)
    if set(value) != {"schema", "task_sha256", "reviewer_role", "pages", "unresolved"} or value["schema"] != "kb_creator.five_step_visual_submission.v1":
        raise FiveStepError("invalid visual submission")
    if value["task_sha256"] != task["task_sha256"] or value["reviewer_role"] not in {"agent", "user"} or value["unresolved"] != []:
        raise FiveStepError("visual task identity/review unresolved")
    expected = [{"page": row["page"], "reviewed": True, "findings": []} for row in task["pages"]]
    if value["pages"] != expected:
        raise FiveStepError("all DOCX pages require explicit review and resolved findings")
    _module("docx").verify_docx_package(Path(state["paths"]["docx"]))
    output = _next(root, "visual-review")
    output.mkdir()
    _write(output / "review.json", value)
    _record(root, state, output, 5)
    state.update(phase="complete", state="ready_for_docx_review", task_path=None, template_path=None, reason=None)


def rebuild_docx(run_root: Path, *, config: Path, runtime: dict[str, Any] | None = None,
                 fidelity_plan: Path | None = None) -> dict[str, Any]:
    root = run_root.resolve(strict=True)
    state = _load(root, rebuilding_docx=True)
    if fidelity_plan is None:
        raise FiveStepError("closed source-fidelity plan is required before DOCX rebuild")
    if state["phase"] not in {"complete", "docx_visual", "docx"} or "final" not in state["paths"]:
        raise FiveStepError("DOCX rebuild requires verified MASTER_RU")
    from .reader_fidelity import validate_plan
    plan = validate_plan(fidelity_plan, source_pdf=Path(state["source"]["path"]),
                         master_ru=Path(state["paths"]["master_ru"]))
    if plan["config"] != {"path": str(config.resolve(strict=True)), **file_identity(config)}:
        raise FiveStepError("DOCX rebuild config differs from fidelity plan")
    # Preserve prior artifacts and their recorded implementation as historical evidence.
    old = [row for row in state["evidence"] if row["step"] == 5]
    state.setdefault("predecessor_docx_evidence", []).extend(old)
    state["evidence"] = [row for row in state["evidence"] if row["step"] != 5]
    state.update(phase="docx", state="running", docx_config=str(config.resolve(strict=True)), task_path=None, template_path=None)
    if runtime is not None:
        state["runtime"] = runtime
    _save(root, state)
    return resume(root, fidelity_plan=fidelity_plan)
