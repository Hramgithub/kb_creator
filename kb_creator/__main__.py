from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .pipeline.reconstruction import (
    ControlPlaneError,
    RuntimeOptions,
    preflight,
    resume_engine,
    run_engine,
)
from .pipeline.reconstruction_promotion import (
    ReconstructionPromotionError,
    materialize_reconstruction_promotion,
    record_reconstruction_acceptance,
)
from .pipeline.reconstruction_replay import (
    ReplayError,
    replay_run_engine,
    verify_replay_transform,
    verify_replay_source,
)
from .pipeline.reconstruction_replay_resume import (
    ReplayResumeError,
    replay_resume_engine,
)
from .pipeline.publication import (
    PublicationControlError,
    parse_authorities,
    publication_preflight,
    publication_resume,
    publication_run,
    record_artifact_acceptance,
    reject_legacy_publication_writer,
    verify_production_package,
)
from .pipeline.publication_adapters import (
    PublicationAdapterError,
    PublicationAdapterRuntime,
    fixed_publication_adapters,
)
from .scripts.revise_publication_docx_package import (
    DocxRevisionError,
    build_revision_package,
    materialize_release_layout,
    record_visual_acceptance,
    reject_legacy_revision_writer,
)
from .scripts.verify_docx_revision_package import verify_revision_package


def _runtime(args: argparse.Namespace) -> RuntimeOptions:
    return RuntimeOptions(
        mineru_root=args.mineru_root,
        pdftoppm=args.pdftoppm,
        powershell=args.powershell,
        python=args.python,
        raster_dpi=args.raster_dpi,
        review_dpi=args.review_dpi,
        provider_capabilities=args.provider_capabilities,
        mineru_source_root=args.mineru_source_root,
        ocr_language=args.ocr_language,
    )


def _add_runtime_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--mineru-root", required=True, type=Path)
    parser.add_argument("--pdftoppm", required=True, type=Path)
    parser.add_argument("--powershell", required=True, type=Path)
    parser.add_argument("--python", default=Path(sys.executable), type=Path)
    parser.add_argument("--raster-dpi", default=200, type=int)
    parser.add_argument("--review-dpi", default=110, type=int)
    parser.add_argument("--provider-capabilities", type=Path)
    parser.add_argument("--mineru-source-root", type=Path)
    parser.add_argument("--ocr-language")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m kb_creator")
    subcommands = parser.add_subparsers(dest="command", required=True)
    doctor = subcommands.add_parser("doctor")
    doctor.add_argument("--json", action="store_true")

    translate = subcommands.add_parser("translate", help="Five-step PDF to DOCX profile with explicit Codex tasks")
    translate_commands = translate.add_subparsers(dest="translate_command", required=True)
    translate_run = translate_commands.add_parser("run")
    translate_run.add_argument("--source", required=True, type=Path)
    translate_run.add_argument("--glossary", required=True, type=Path)
    translate_run.add_argument("--run-root", required=True, type=Path)
    translate_run.add_argument("--title")
    translate_run.add_argument("--runtime", type=Path, help="Local JSON runtime paths, reconstruction and docx sections")
    translate_run.add_argument("--docx-config", type=Path)
    translate_run.add_argument("--replay-from", type=Path, help="Verify and reuse completed reconstruction stages 01-04 in a new run")
    translate_run.add_argument("--archived-replay", action="store_true", help="Use explicit archived 01-03 replay authority with fresh Stage04")
    translate_run.add_argument("--recovery-plan", type=Path, help="Sealed verified-view import plan for a fresh Stage 02")
    translate_run.add_argument("--system", choices=["coc"], help="Compose the shared CoC dictionary with the book glossary")
    translate_run.add_argument("--book-id", help="Stable book identifier for shared terminology")
    translate_run.add_argument("--shared-registry", type=Path, help="Explicit CoC registry; defaults to the shared NRI dictionary")
    translate_run.add_argument("--source-inventory", required=True, type=Path, help="Sealed independently rendered all-page PDF inventory")
    translate_run.add_argument("--source-review", required=True, type=Path, help="Sealed reviewed all-page graphic domain")
    translate_status = translate_commands.add_parser("status")
    translate_status.add_argument("--run-root", required=True, type=Path)
    translate_resume = translate_commands.add_parser("resume")
    translate_resume.add_argument("--run-root", required=True, type=Path)
    translate_resume.add_argument("--submission", type=Path)
    translate_resume.add_argument("--decisions-root", type=Path)
    translate_resume.add_argument("--runtime", type=Path)
    translate_resume.add_argument("--reader-options", type=Path, help="Sealed source-bound reader projection decisions after MASTER_RU")
    translate_resume.add_argument("--fidelity-plan", type=Path, help="Closed source-to-reader DOCX fidelity plan")
    translate_rebuild = translate_commands.add_parser("rebuild-docx")
    translate_rebuild.add_argument("--run-root", required=True, type=Path)
    translate_rebuild.add_argument("--docx-config", required=True, type=Path)
    translate_rebuild.add_argument("--runtime", type=Path)
    translate_rebuild.add_argument("--fidelity-plan", required=True, type=Path)
    translate_successor = translate_commands.add_parser("successor")
    translate_successor.add_argument("--from-run", required=True, type=Path)
    translate_successor.add_argument("--run-root", required=True, type=Path)
    translate_successor.add_argument("--proofread-submission", required=True, type=Path)
    translate_successor_build = translate_commands.add_parser("successor-build")
    translate_successor_build.add_argument("--run-root", required=True, type=Path)
    translate_successor_build.add_argument("--reader-options", required=True, type=Path)
    translate_successor_build.add_argument("--docx-config", required=True, type=Path)
    translate_successor_build.add_argument("--runtime", required=True, type=Path)
    translate_successor_build.add_argument("--fidelity-plan", required=True, type=Path)
    translate_successor_verify = translate_commands.add_parser("verify-successor")
    translate_successor_verify.add_argument("--run-root", required=True, type=Path)
    translate_successor_review = translate_commands.add_parser("successor-review")
    translate_successor_review.add_argument("--run-root", required=True, type=Path)
    translate_successor_review.add_argument("--submission", required=True, type=Path)
    translate_decisions = translate_commands.add_parser("prepare-decisions", help="Package reviewed page decisions; compute identities automatically")
    translate_decisions.add_argument("--reconstruction-root", required=True, type=Path)
    translate_decisions.add_argument("--decision", required=True, action="append", type=Path)
    translate_decisions.add_argument("--output-root", required=True, type=Path)
    translate_decisions.add_argument("--reviewed-allowlist", type=Path)
    translate_master = translate_commands.add_parser("build-review-master", help="Build MASTER_EN from verified review-draft materialization")
    translate_master.add_argument("--materialized-root", required=True, type=Path)
    translate_master.add_argument("--final-evidence", required=True, type=Path)
    translate_master.add_argument("--output-root", required=True, type=Path)
    translate_master.add_argument("--binding-root", type=Path)

    preflight_parser = subcommands.add_parser("preflight")
    preflight_parser.add_argument("--contract", required=True, type=Path)
    preflight_parser.add_argument("--source", required=True, type=Path)
    preflight_parser.add_argument("--run-root", required=True, type=Path)
    preflight_parser.add_argument("--target", default="reconstructed_en")
    preflight_parser.add_argument("--json", action="store_true")
    _add_runtime_arguments(preflight_parser)

    run_parser = subcommands.add_parser("run")
    run_parser.add_argument("--contract", required=True, type=Path)
    run_parser.add_argument("--source", required=True, type=Path)
    run_parser.add_argument("--run-root", required=True, type=Path)
    run_parser.add_argument("--run-id", required=True)
    run_parser.add_argument("--target", default="reconstructed_en")
    run_parser.add_argument("--json", action="store_true")
    _add_runtime_arguments(run_parser)

    resume_parser = subcommands.add_parser("resume")
    resume_parser.add_argument("--run-root", required=True, type=Path)
    resume_parser.add_argument("--decisions", required=True, type=Path)
    resume_parser.add_argument("--decisions-root", required=True, type=Path)
    resume_parser.add_argument("--target", default="reconstructed_en")
    resume_parser.add_argument("--json", action="store_true")

    replay = subcommands.add_parser("replay")
    replay_commands = replay.add_subparsers(dest="replay_command", required=True)
    replay_verify = replay_commands.add_parser("verify-source")
    replay_verify.add_argument("--contract", required=True, type=Path)
    replay_verify.add_argument("--source", required=True, type=Path)
    replay_verify.add_argument("--source-run-root", required=True, type=Path)
    replay_verify.add_argument("--through-stage", required=True)
    replay_verify.add_argument("--validate-rebase", action="store_true")
    replay_verify.add_argument("--json", action="store_true")
    _add_runtime_arguments(replay_verify)
    replay_run = replay_commands.add_parser("run")
    replay_run.add_argument("--contract", required=True, type=Path)
    replay_run.add_argument("--source", required=True, type=Path)
    replay_run.add_argument("--source-run-root", required=True, type=Path)
    replay_run.add_argument("--run-root", required=True, type=Path)
    replay_run.add_argument("--run-id", required=True)
    replay_run.add_argument("--through-stage", required=True)
    replay_run.add_argument("--json", action="store_true")
    _add_runtime_arguments(replay_run)
    replay_resume = replay_commands.add_parser("resume")
    replay_resume.add_argument("--run-root", required=True, type=Path)
    replay_resume.add_argument("--decisions", required=True, type=Path)
    replay_resume.add_argument("--decisions-root", required=True, type=Path)
    replay_resume.add_argument("--json", action="store_true")

    promotion = subcommands.add_parser("reconstruction-promotion")
    promotion_commands = promotion.add_subparsers(
        dest="reconstruction_promotion_command", required=True
    )
    promotion_materialize = promotion_commands.add_parser("materialize")
    promotion_materialize.add_argument("--run-root", required=True, type=Path)
    promotion_materialize.add_argument("--json", action="store_true")
    promotion_acceptance = promotion_commands.add_parser("record-acceptance")
    promotion_acceptance.add_argument("--run-root", required=True, type=Path)
    promotion_acceptance.add_argument("--user-decision-reference", required=True)
    promotion_acceptance.add_argument("--json", action="store_true")

    publication = subcommands.add_parser("publication")
    publication_commands = publication.add_subparsers(
        dest="publication_command", required=True
    )
    publication_preflight_parser = publication_commands.add_parser("preflight")
    for target in (publication_preflight_parser,):
        target.add_argument("--contract", required=True, type=Path)
        target.add_argument("--upstream-inventory", required=True, type=Path)
        target.add_argument("--reconstruction-acceptance", required=True, type=Path)
        target.add_argument("--config-root", required=True, type=Path)
        target.add_argument("--run-root", required=True, type=Path)
        target.add_argument("--tools-root", type=Path)
        target.add_argument("--json", action="store_true")
    publication_run_parser = publication_commands.add_parser("run")
    for name in ("contract", "upstream-inventory", "reconstruction-acceptance", "config-root", "run-root", "tools-root", "python", "powershell", "pdftoppm"):
        publication_run_parser.add_argument(f"--{name}", required=True, type=Path)
    run_engine = publication_run_parser.add_mutually_exclusive_group(required=True)
    run_engine.add_argument("--word", type=Path)
    run_engine.add_argument("--libreoffice", type=Path)
    publication_run_parser.add_argument("--run-id", required=True)
    publication_run_parser.add_argument("--json", action="store_true")
    publication_resume_parser = publication_commands.add_parser("resume")
    publication_resume_parser.add_argument("--run-root", required=True, type=Path)
    publication_resume_parser.add_argument("--authority", action="append", default=[])
    for name in ("python", "powershell", "pdftoppm"):
        publication_resume_parser.add_argument(f"--{name}", required=True, type=Path)
    resume_engine = publication_resume_parser.add_mutually_exclusive_group(required=True)
    resume_engine.add_argument("--word", type=Path)
    resume_engine.add_argument("--libreoffice", type=Path)
    publication_resume_parser.add_argument("--json", action="store_true")
    acceptance = publication_commands.add_parser("record-acceptance")
    acceptance.add_argument("--run-root", required=True, type=Path)
    acceptance.add_argument("--artifact-kind", required=True)
    acceptance.add_argument("--evidence", required=True, action="append", type=Path)
    acceptance.add_argument("--destination", required=True, type=Path)
    acceptance.add_argument("--user-decision-reference", required=True)
    acceptance.add_argument("--recorder-role", default="main_orchestrator")
    acceptance.add_argument("--json", action="store_true")
    verify_package = publication_commands.add_parser("verify-package")
    verify_package.add_argument("--package-root", required=True, type=Path)
    verify_package.add_argument("--json", action="store_true")
    revise_docx = publication_commands.add_parser("revise-docx")
    revise_docx.add_argument("--base-package", required=True, type=Path)
    revise_docx.add_argument("--reviewed-docx", required=True, type=Path)
    revise_docx.add_argument("--output-root", required=True, type=Path)
    revise_docx.add_argument("--libreoffice", required=True, type=Path)
    revise_docx.add_argument("--pdftoppm", required=True, type=Path)
    revise_docx.add_argument("--user-decision-reference", required=True)
    revise_docx.add_argument("--json", action="store_true")
    revision_review = publication_commands.add_parser("record-revision-review")
    revision_review.add_argument("--package-root", required=True, type=Path)
    revision_review.add_argument("--user-decision-reference", required=True)
    revision_review.add_argument("--json", action="store_true")
    verify_revision = publication_commands.add_parser("verify-revision")
    verify_revision.add_argument("--package-root", required=True, type=Path)
    verify_revision.add_argument("--json", action="store_true")
    materialize_release = publication_commands.add_parser("materialize-release")
    materialize_release.add_argument("--source-root", required=True, type=Path)
    materialize_release.add_argument("--output-root", required=True, type=Path)
    materialize_release.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "translate":
            from .pipeline import five_step
            runtime_path = getattr(args, "runtime", None)
            runtime = json.loads(runtime_path.read_text(encoding="utf-8-sig")) if runtime_path else None
            if args.translate_command == "run":
                result = five_step.start(args.source, args.glossary, args.run_root, title=args.title, runtime=runtime, docx_config=args.docx_config, replay_from=args.replay_from, archived_replay=args.archived_replay, recovery_plan=args.recovery_plan, system=args.system, book_id=args.book_id, shared_registry=args.shared_registry, source_inventory=args.source_inventory, source_review=args.source_review)
            elif args.translate_command == "status":
                result = five_step.status(args.run_root)
            elif args.translate_command == "resume":
                result = five_step.resume(args.run_root, submission=args.submission, decisions_root=args.decisions_root, runtime=runtime, reader_options=args.reader_options, fidelity_plan=args.fidelity_plan)
            elif args.translate_command == "prepare-decisions":
                from .pipeline.five_step_intake import author_reconstruction_decision_set
                result = author_reconstruction_decision_set(args.reconstruction_root, args.decision, args.output_root, reviewed_allowlist=args.reviewed_allowlist)
            elif args.translate_command == "build-review-master":
                from .pipeline.five_step_intake import build_review_master_en
                result = build_review_master_en(args.materialized_root, args.final_evidence, args.output_root, binding_root=args.binding_root)
            elif args.translate_command in {"successor", "successor-build", "verify-successor", "successor-review"}:
                from .pipeline import five_step_successor
                if args.translate_command == "successor":
                    result = five_step_successor.successor_prepare(args.from_run, args.run_root, args.proofread_submission)
                elif args.translate_command == "successor-build":
                    result = five_step_successor.successor_build(args.run_root, args.reader_options, args.docx_config, runtime, fidelity_plan=args.fidelity_plan)
                elif args.translate_command == "verify-successor":
                    result = five_step_successor.verify_successor(args.run_root)
                else:
                    result = five_step_successor.successor_review(args.run_root, args.submission)
            else:
                result = five_step.rebuild_docx(args.run_root, config=args.docx_config, runtime=runtime, fidelity_plan=args.fidelity_plan)
        elif args.command == "reconstruction-promotion":
            if args.reconstruction_promotion_command == "materialize":
                result = materialize_reconstruction_promotion(args.run_root)
            else:
                result = record_reconstruction_acceptance(
                    args.run_root, args.user_decision_reference
                )
        elif args.command == "replay":
            if args.replay_command == "verify-source":
                if args.validate_rebase:
                    result = verify_replay_transform(
                        args.contract,
                        args.source,
                        args.source_run_root,
                        args.through_stage,
                        _runtime(args),
                    )
                else:
                    result = verify_replay_source(
                        args.contract,
                        args.source,
                        args.source_run_root,
                        args.through_stage,
                        _runtime(args),
                    )
            elif args.replay_command == "run":
                result = replay_run_engine(
                    args.contract,
                    args.source,
                    args.source_run_root,
                    args.run_root,
                    args.run_id,
                    args.through_stage,
                    _runtime(args),
                )
            else:
                result = replay_resume_engine(
                    args.run_root,
                    args.decisions,
                    args.decisions_root,
                )
        elif args.command == "publication":
            if args.publication_command in {"preflight", "run", "resume", "record-acceptance"}:
                reject_legacy_publication_writer()
            if args.publication_command in {"revise-docx", "record-revision-review", "materialize-release"}:
                reject_legacy_revision_writer()
            if args.publication_command == "preflight":
                result = publication_preflight(
                    args.contract,
                    args.upstream_inventory,
                    args.reconstruction_acceptance,
                    args.config_root,
                    args.run_root,
                    args.tools_root,
                )
            elif args.publication_command == "run":
                adapters = fixed_publication_adapters(PublicationAdapterRuntime(args.python, args.powershell, args.pdftoppm, args.word, args.libreoffice))
                result = publication_run(
                    args.contract, args.upstream_inventory, args.reconstruction_acceptance,
                    args.config_root, args.run_root, args.run_id, adapters, args.tools_root,
                )
            elif args.publication_command == "resume":
                adapters = fixed_publication_adapters(PublicationAdapterRuntime(args.python, args.powershell, args.pdftoppm, args.word, args.libreoffice))
                result = publication_resume(args.run_root, parse_authorities(args.authority), adapters)
            elif args.publication_command == "record-acceptance":
                result = record_artifact_acceptance(
                    args.run_root,
                    args.artifact_kind,
                    args.evidence,
                    args.destination,
                    args.user_decision_reference,
                    args.recorder_role,
                )
            elif args.publication_command == "verify-package":
                result = verify_production_package(args.package_root)
            elif args.publication_command == "revise-docx":
                result = build_revision_package(
                    args.base_package,
                    args.reviewed_docx,
                    args.output_root,
                    args.libreoffice,
                    args.pdftoppm,
                    args.user_decision_reference,
                )
            elif args.publication_command == "record-revision-review":
                result = record_visual_acceptance(
                    args.package_root, args.user_decision_reference
                )
            elif args.publication_command == "materialize-release":
                result = materialize_release_layout(args.source_root, args.output_root)
            else:
                result = verify_revision_package(args.package_root)
        elif args.command == "doctor":
            result = {
                "schema": "kb_creator.doctor.v1",
                "state": "ready_for_explicit_tool_preflight",
                "target": "reconstructed_en",
            }
        elif args.command == "preflight":
            result = preflight(
                args.contract,
                args.source,
                args.run_root,
                args.target,
                _runtime(args),
            )
        elif args.command == "run":
            if args.target != "reconstructed_en":
                raise ControlPlaneError("unsupported target")
            result = run_engine(
                args.contract,
                args.source,
                args.run_root,
                args.run_id,
                runtime=_runtime(args),
            )
        else:
            if args.target != "reconstructed_en":
                raise ControlPlaneError("unsupported target")
            result = resume_engine(
                args.run_root,
                args.decisions,
                args.decisions_root,
            )
    except (ControlPlaneError, ReplayError, ReplayResumeError, ReconstructionPromotionError, PublicationControlError, PublicationAdapterError, DocxRevisionError, KeyError, OSError, ValueError) as error:
        print(
            json.dumps(
                {"state": "blocked", "error": str(error)},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return int(result.get("exit_code", 0))


if __name__ == "__main__":
    raise SystemExit(main())
