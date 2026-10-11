import pytest
import ast
from pathlib import Path

from kb_creator.pdf_raw import raw_authority_projection as stage_a
from kb_creator.pdf_raw.errors import RawPdfError
from kb_creator.pdf_raw.raw_authority_projection import project_stage_a_raw_authority
from kb_creator.pdf_raw.source_reconstruction import (
    derive_page_reconstruction_v1,
    validate_page_reconstruction_ledger_v1,
)


def test_any_unpinned_leaf_is_rejected_before_open_or_extract(monkeypatch):
    row = stage_a._FIXTURES[0]
    opens, extracts = [], []
    monkeypatch.setattr(stage_a.RawPdfDocument, "open", lambda *args, **kwargs: opens.append(1))
    monkeypatch.setattr(stage_a, "extract_raw_pdf_page_atoms", lambda *args, **kwargs: extracts.append(1))
    with pytest.raises(RawPdfError, match="^raw_interpreter_fixture_admission_forbidden$"):
        project_stage_a_raw_authority(row.fixture_id, row.pdf + b"canary", row.profile, row.selector)
    with pytest.raises(RawPdfError, match="^raw_interpreter_fixture_admission_forbidden$"):
        project_stage_a_raw_authority(b"fixture", row.pdf, row.profile, row.selector)
    assert opens == [] and extracts == []


def test_three_module_import_graph_is_ast_closed():
    root = Path(__file__).parents[1] / "pdf_raw"
    allowed = {
        "raw_authority_projection.py": {"document", "errors", "page_capable"},
        "raw_interpreter_authority.py": {"document", "errors", "page_capable"},
        "source_reconstruction.py": {"errors"},
    }
    forbidden = {"innsmouth", "keeper", "markdown", "html", "output", "run", "pypdf", "pdfplumber", "fitz"}
    for name, local_allowed in allowed.items():
        tree = ast.parse((root / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = "" if isinstance(node, ast.Import) else (node.module or "")
                imported = [alias.name for alias in node.names]
                text = " ".join([module, *imported]).lower()
                assert not any(term in text for term in forbidden)
                if isinstance(node, ast.ImportFrom) and node.level:
                    assert module in local_allowed
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"__import__", "eval", "exec"}


class _Poison:
    def __getattribute__(self, name):
        raise AssertionError(f"argument accessed: {name}")

    def __iter__(self):
        raise AssertionError("argument iterated")


def test_source_reconstruction_shims_fail_before_any_argument_access():
    poison = _Poison()
    with pytest.raises(RawPdfError, match="^raw_interpreter_authority_profile_unsupported$"):
        derive_page_reconstruction_v1(poison, poison, poison)
    with pytest.raises(RawPdfError, match="^raw_interpreter_authority_profile_unsupported$"):
        validate_page_reconstruction_ledger_v1(poison, poison, poison, poison)
