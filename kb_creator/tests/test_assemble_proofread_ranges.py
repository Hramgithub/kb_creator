import json

import pytest

from kb_creator.pipeline import five_step_language as language
from kb_creator.scripts.assemble_proofread_ranges import assemble
from kb_creator.tests.test_five_step_language import _fixture, _complete_draft


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def inputs(tmp_path):
    master, glossary, root = _fixture(tmp_path)
    prepared = language.prepare_language(master, glossary, root)
    drafted = language.submit_draft(root, _complete_draft(prepared["template_path"]), tmp_path / "draft")
    template = json.loads(drafted["template_path"].read_text(encoding="utf-8"))
    for row in template["units"]:
        row["disposition"] = "checked_unchanged"
    left, right = tmp_path / "left.json", tmp_path / "right.json"
    _write(left, {**template, "units": template["units"][:2]})
    _write(right, {**template, "units": template["units"][2:]})
    return drafted, [left, right], tmp_path / "combined"


def test_disjoint_out_of_order_ranges_assemble_exact_task_order(inputs):
    drafted, parts, output = inputs
    report = assemble(drafted["task_path"], drafted["template_path"], parts[::-1], output)
    value = json.loads((output / "proofread.submission.json").read_text(encoding="utf-8"))
    assert report["review_inferred"] is False
    assert value["units"][0]["unit_id"] == "unit-00001"
    assert len(value["units"]) == report["units"]


@pytest.mark.parametrize("mutation", ["missing", "overlap", "task", "preimage", "pending", "unresolved", "false_changed"])
def test_rejects_incomplete_or_unbound_reviews_before_output(inputs, mutation):
    drafted, parts, output = inputs
    value = json.loads(parts[0].read_text(encoding="utf-8"))
    if mutation == "missing":
        parts = parts[:1]
    elif mutation == "overlap":
        parts = parts + parts[:1]
    elif mutation == "task":
        value["task"]["sha256"] = "0" * 64
    elif mutation == "preimage":
        value["units"][0]["source_hash"] = "0" * 64
    elif mutation == "pending":
        value["units"][0]["disposition"] = "pending"
    elif mutation == "unresolved":
        value["units"][0]["unresolved"] = ["uncertain"]
    elif mutation == "false_changed":
        value["units"][0]["disposition"] = "changed"
        value["units"][0]["reason"] = "not actually changed"
    _write(parts[0], value)
    with pytest.raises(ValueError):
        assemble(drafted["task_path"], drafted["template_path"], parts, output)
    assert not output.exists()
