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
        if args.command == "reconstruction-promotion":
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
