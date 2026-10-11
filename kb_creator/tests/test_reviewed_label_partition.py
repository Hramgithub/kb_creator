import copy

import pytest

from kb_creator.pipeline.identity import sha256_bytes
from kb_creator.pipeline.review_draft_preparation import _bind_issue_occurrences
from kb_creator.pipeline.reviewed_label_partition import project_label_partition
from kb_creator.pipeline.semantic_structure import _normalized


def _fixture():
    key = ("original_pipeline_txt", 5)
    source = "RED BL UE RED GOLD"
    labels = ["RED", "BLUE", "RED", "GOLD"]
    starts = [0, 4, 10, 14]
    units = []
    definitions = []
    for index, (start, end, label) in enumerate(zip(starts, starts[1:] + [len(source)], labels)):
        fragment = {"view": key[0], "raw_index": key[1], "start": start, "end": end}
        definition = {"id": f"label-{index}", "kind": "label", "representation": "semantic_span",
                      "view": key[0], "raw_indices": [key[1]], "source_fragments": [fragment.copy()]}
        definitions.append(definition)
        fragment.update(source_sha256=sha256_bytes(source.encode()),
                        fragment_sha256=sha256_bytes(source[start:end].encode()),
                        normalized_sha256=sha256_bytes(_normalized(source[start:end]).encode()))
        units.append({"id": definition["id"], "kind": "label", "representation": "semantic_span",
                      "source_blocks": [{"view": key[0], "raw_index": key[1]}],
                      "source_fragments": [fragment],
                      "markdown_span": {"start_line": 1 + 2 * index, "end_line": 1 + 2 * index,
                                        "sha256": sha256_bytes(label.encode())}})
    decision = {"markdown": "\n\n".join(labels) + "\n\nUnrelated paragraph.",
                "semantic_structure": {"units": units}}
    return key, source, decision, definitions


def test_repeated_labels_replay_by_source_and_reader_coordinates():
    key, source, decision, _ = _fixture()
    text, proof = project_label_partition(decision, {key: {"text": source}}, key, {key: [("BL UE", "BLUE")]}, 1)
    assert text == "RED\n\nBLUE\n\nRED\n\nGOLD"
    assert proof["page_character_span"] == {"start": 0, "end": len(text)}
    assert [row["fragment"]["start"] for row in proof["units"]] == [0, 4, 10, 14]
    assert proof["source_sha256"] == sha256_bytes(source.encode())


@pytest.mark.parametrize("mutation", ["hash", "source_hash", "gap", "overlap", "wrong_key",
                                     "foreign_source", "duplicate_id", "reversed_reader", "reader_hash",
                                     "changed_punctuation", "foreign_owner", "separator_content"])
def test_partition_rejects_unproved_source_or_reader_changes(mutation):
    key, source, decision, _ = _fixture()
    units = decision["semantic_structure"]["units"]
    fragment = units[1]["source_fragments"][0]
    if mutation == "hash":
        fragment["fragment_sha256"] = "0" * 64
    elif mutation == "source_hash":
        fragment["source_sha256"] = "0" * 64
    elif mutation in {"gap", "overlap"}:
        fragment["start"] += 1 if mutation == "gap" else -1
        raw = source[fragment["start"]:fragment["end"]]
        fragment.update(fragment_sha256=sha256_bytes(raw.encode()), normalized_sha256=sha256_bytes(_normalized(raw).encode()))
    elif mutation == "wrong_key":
        fragment["raw_index"] = 9
    elif mutation == "foreign_source":
        units[1]["source_blocks"].append({"view": key[0], "raw_index": 9})
    elif mutation == "duplicate_id":
        units[1]["id"] = units[0]["id"]
    elif mutation == "reversed_reader":
        units[0]["markdown_span"], units[2]["markdown_span"] = units[2]["markdown_span"], units[0]["markdown_span"]
    elif mutation == "reader_hash":
        units[1]["markdown_span"]["sha256"] = "0" * 64
    elif mutation == "changed_punctuation":
        decision["markdown"] = decision["markdown"].replace("BLUE", "BLUE!")
        units[1]["markdown_span"]["sha256"] = sha256_bytes(b"BLUE!")
    elif mutation == "foreign_owner":
        foreign = copy.deepcopy(units[1]); foreign["id"] = "other-owner"
        foreign["source_blocks"] = [{"view": key[0], "raw_index": 9}]
        units.append(foreign)
    else:
        decision["markdown"] = decision["markdown"].replace("RED\n\nBLUE", "RED\nforeign\nBLUE")
    with pytest.raises(ValueError):
        project_label_partition(decision, {key: {"text": source}}, key, {key: [("BL UE", "BLUE")]}, 1)


def _bind(definitions, source, *, extra_owner=False, selected=True):
    key = ("original_pipeline_txt", 5)
    names = [row["id"] for row in definitions]
    issue = {"source_page": 1, "issue_id": "partition", "source_excerpt_en": source,
             "source_selector": {"mechanical_diagnostic": {"source_keys": [{"view": key[0], "raw_index": key[1]}]}}}
    index = {(1, *key): names + (["unproved-owner"] if extra_owner else [])}
    return _bind_issue_occurrences([issue], index, selected_source_keys={1: {key} if selected else set()},
                                   partition_units={(1, *key): definitions})


def test_preparation_preserves_complete_partition_source_anchor():
    key, source, _, definitions = _fixture()
    assert _bind(definitions, source)[0]["candidate_span"] == {
        "source_key": {"view": key[0], "raw_index": key[1]}, "source_page": 1,
        "binding": "ordered_selected_source_v1"}


@pytest.mark.parametrize("mutation", ["missing", "gap", "overlap", "duplicate", "mixed_key", "extra_owner", "unselected"])
def test_preparation_does_not_bypass_ambiguous_or_incomplete_ownership(mutation):
    _, source, _, definitions = _fixture()
    if mutation == "missing":
        definitions.pop()
    elif mutation in {"gap", "overlap"}:
        definitions[1]["source_fragments"][0]["start"] += 1 if mutation == "gap" else -1
    elif mutation == "duplicate":
        definitions.append(copy.deepcopy(definitions[0]))
    elif mutation == "mixed_key":
        definitions[1]["raw_indices"].append(9)
    with pytest.raises(ValueError, match="semantic occurrence"):
        _bind(definitions, source, extra_owner=mutation == "extra_owner", selected=mutation != "unselected")
