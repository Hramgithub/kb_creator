from copy import deepcopy

import pytest

from kb_creator.pipeline.identity import sha256_bytes
from kb_creator.pipeline.reviewed_quote_projection import project_corrected_quote, quote_text
from kb_creator.pipeline.semantic_structure import _normalized


def fixture():
    key = ("original_pipeline_txt", 5)
    source = "garbled interview"
    corrected = "A: Why?\n\nB: I don't know."
    reader = quote_text(corrected)
    fragment = {"view": key[0], "raw_index": key[1], "start": 0, "end": len(source),
                "source_sha256": sha256_bytes(source.encode()), "fragment_sha256": sha256_bytes(source.encode()),
                "normalized_sha256": sha256_bytes(_normalized(source).encode())}
    unit = {"id": "interview", "kind": "handout", "representation": "blockquote",
            "source_blocks": [{"view": key[0], "raw_index": key[1]}], "source_fragments": [fragment],
            "markdown_span": {"start_line": 1, "end_line": 3, "sha256": sha256_bytes(reader.encode())}}
    return key, {key: {"text": source}}, {key: [(source, corrected)]}, {"markdown": reader, "semantic_structure": {"units": [unit]}}


def test_exact_quote_retains_paragraphs():
    key, blocks, corrections, decision = fixture()
    reader, proof = project_corrected_quote(decision, blocks, key, corrections, 1)
    assert reader == "> A: Why?\n>\n> B: I don't know."
    assert proof["payload_sha256"] == sha256_bytes(corrections[key][0][1].encode())


@pytest.mark.parametrize("mutation", ["fragment_hash", "fragment_start", "fragment_key", "extra_source", "duplicate_owner", "foreign_owner", "span_hash", "punctuation", "flattened", "hidden_target", "parent", "missing_correction"])
def test_quote_rejects_unproved_or_changed_container(mutation):
    key, blocks, corrections, decision = fixture()
    units = decision["semantic_structure"]["units"]; unit = units[0]
    if mutation == "fragment_hash": unit["source_fragments"][0]["fragment_sha256"] = "0" * 64
    elif mutation == "fragment_start": unit["source_fragments"][0]["start"] = 1
    elif mutation == "fragment_key": unit["source_fragments"][0]["raw_index"] = 9
    elif mutation == "extra_source": unit["source_blocks"].append({"view": key[0], "raw_index": 9})
    elif mutation == "duplicate_owner": units.append(deepcopy(unit))
    elif mutation == "foreign_owner":
        other = deepcopy(unit); other["id"] = "other"; other["source_blocks"] = [{"view": key[0], "raw_index": 9}]; units.append(other)
    elif mutation == "span_hash": unit["markdown_span"]["sha256"] = "0" * 64
    elif mutation == "parent": unit["container_parent"] = "parent"
    elif mutation == "missing_correction": corrections.clear()
    else:
        decision["markdown"] = {"punctuation": "> A: Why!\n>\n> B: I don't know.",
                                "flattened": "> A: Why? B: I don't know.\n>\n>",
                                "hidden_target": "> [hidden](A: Why?)\n>\n> B: I don't know."}[mutation]
        unit["markdown_span"]["sha256"] = sha256_bytes(decision["markdown"].encode())
    with pytest.raises(ValueError):
        project_corrected_quote(decision, blocks, key, corrections, 1)


def test_alternative_quote_does_not_hide_payload_as_markdown():
    with pytest.raises(ValueError):
        quote_text("[label](hidden payload)")
