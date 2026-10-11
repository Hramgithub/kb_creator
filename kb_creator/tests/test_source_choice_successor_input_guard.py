"""Caller-input identity guard for R1 source-choice successors."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.source_choice_successor_preparation import (
    SourceChoiceSuccessorPreparationError, _verify_caller_author_inputs,
)


def _write(path: Path, value: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _fixture(root: Path) -> tuple[dict, Path, list[Path]]:
    specs = [_write(root / "author-specs/spec-00.json", {"page": 1}),
             _write(root / "author-specs/spec-01.json", {"page": 2})]
    drafts = [_write(root / "draft-pages/page-001.json", {"source_page": 1}),
              _write(root / "draft-pages/page-002.json", {"source_page": 2})]
    bindings = {f"input_{index:02d}": {"path": path.relative_to(root).as_posix(), **file_identity(path)}
                for index, path in enumerate(specs)}
    bindings.update({f"draft_{path.stem}": {"path": path.relative_to(root).as_posix(), **file_identity(path)}
                     for path in drafts})
    return {"bindings": bindings}, root / "draft-pages", specs


def test_r1_caller_input_guard_accepts_exact_ordered_predecessor_set(tmp_path):
    predecessor, drafts, specs = _fixture(tmp_path)
    _verify_caller_author_inputs(predecessor, tmp_path, drafts, specs)


@pytest.mark.parametrize("mutation", ["foreign_spec", "modified_spec", "reordered_specs", "missing_draft", "extra_draft", "modified_draft"])
def test_r1_caller_input_guard_rejects_foreign_modified_or_domain_drift(tmp_path, mutation):
    predecessor, drafts, specs = _fixture(tmp_path)
    supplied_specs = list(specs)
    if mutation == "foreign_spec":
        supplied_specs[0] = _write(tmp_path / "foreign/spec-00.json", {"page": 1})
    elif mutation == "modified_spec":
        _write(specs[0], {"page": "modified"})
    elif mutation == "reordered_specs":
        supplied_specs.reverse()
    elif mutation == "missing_draft":
        (drafts / "page-002.json").unlink()
    elif mutation == "extra_draft":
        _write(drafts / "page-003.json", {"source_page": 3})
    elif mutation == "modified_draft":
        _write(drafts / "page-002.json", {"source_page": "modified"})
    with pytest.raises(SourceChoiceSuccessorPreparationError):
        _verify_caller_author_inputs(predecessor, tmp_path, drafts, supplied_specs)
