"""Shared terminology is frozen and enforced before the first pipeline stage."""
import json

import pytest

from kb_creator.__main__ import _parser
from kb_creator.pipeline import five_step as flow
from kb_creator.tests.test_coc_glossary import inputs as coc_inputs
from kb_creator.tests.test_five_step_runner import adapters


def test_root_run_composes_and_passes_shared_dictionary_to_language(tmp_path, coc_inputs, adapters, monkeypatch):
    registry, overlay = coc_inputs
    source = tmp_path / "source.pdf"
    source.write_bytes(b"fixture")
    root = tmp_path / "run"
    result = flow.start(source, overlay, root, system="coc", book_id="fixture", shared_registry=registry)
    assert result["state"] == "needs_agent_work"
    state = json.loads((root / "state.json").read_text())
    effective = root / "terminology/glossary.json"
    value = json.loads(effective.read_text(encoding="utf-8"))
    assert {row["source"] for row in value["terms"]} == {"Keeper", "SAN", "Walter"}
    assert value["context"]["shared_rows"][0]["definition"] == "Ведущий игры."
    assert state["terminology"]["book_id"] == "fixture"
    assert state["glossary"]["path"] == str(effective.resolve())
    language = flow._module("language")
    original = language.prepare_language
    observed = []

    def prepare(master, glossary, output):
        observed.append(glossary)
        return original(master, glossary, output)

    monkeypatch.setattr(language, "prepare_language", prepare)
    submission = tmp_path / "submission.json"
    submission.write_text("{}")
    assert flow.resume(root, submission=submission)["phase"] == "reconstruction"
    assert flow.resume(root, submission=submission, decisions_root=root)["phase"] == "documentary_draft"
    assert observed == [effective.resolve()]
    # An existing run uses its exact embedded snapshot, even if the shared source evolves.
    registry.write_text("new registry revision", encoding="utf-8")
    assert flow.status(root)["phase"] == "documentary_draft"
    effective.write_text("tampered", encoding="utf-8")
    with pytest.raises(flow.FiveStepError, match="glossary changed"):
        flow.resume(root, submission=submission)


def test_conflict_stops_before_intake_and_cannot_be_resumed(tmp_path, coc_inputs, adapters):
    registry, overlay = coc_inputs
    source = tmp_path / "source.pdf"
    source.write_bytes(b"fixture")
    overlay.write_text(json.dumps({"terms": [{"source": "Keeper", "target": "Ведущий", "domain": "role"}]}), encoding="utf-8")
    root = tmp_path / "run"
    result = flow.start(source, overlay, root, system="coc", book_id="fixture", shared_registry=registry)
    assert result["state"] == "failed" and "terminology conflicts" in result["reason"]
    assert adapters == []
    assert (root / "terminology/conflicts.json").is_file()
    assert not (root / "terminology/glossary.json").exists()
    with pytest.raises(flow.FiveStepError, match="conflicted"):
        flow.resume(root, submission=overlay)


def test_shared_terminology_flags_and_code_dependencies():
    args = _parser().parse_args(["translate", "run", "--source", "book.pdf", "--glossary", "book.json", "--run-root", "run", "--system", "coc", "--book-id", "book"])
    assert args.system == "coc" and args.book_id == "book"
    for step in (1, 3, 4):
        assert "kb_creator/pipeline/coc_glossary.py" in {row["path"] for row in flow._codes(step)}


@pytest.mark.parametrize("options", [{"book_id": "book"}, {"system": "coc"}])
def test_incomplete_shared_terminology_options_do_not_allocate_run(tmp_path, coc_inputs, options):
    _, overlay = coc_inputs
    source = tmp_path / "source.pdf"
    source.write_bytes(b"fixture")
    root = tmp_path / "run"
    with pytest.raises(flow.FiveStepError, match="--system coc and --book-id"):
        flow.start(source, overlay, root, **options)
    assert not root.exists()
