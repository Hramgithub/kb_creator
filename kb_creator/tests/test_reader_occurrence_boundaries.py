"""Stage05 alphanumeric proof bounds must preserve source punctuation."""
import pytest

from kb_creator.pipeline.identity import sha256_bytes
from kb_creator.pipeline.reader_occurrence_projection import (
    ReaderOccurrenceError, resolve_issue_reader_occurrence,
)


def _case(raw, reader):
    key = {"view": "txt", "raw_index": 1}
    issue = {"issue_id": "source-1", "source_page": 1, "source_excerpt_en": raw,
             "source_excerpt_sha256": sha256_bytes(raw.encode()),
             "source_selector": {"mechanical_diagnostic": {"source_keys": [key]}},
             "candidate_span": {"binding": "ordered_selected_source_v1", "source_key": key, "source_page": 1}}
    decision = {"source_page": 1, "markdown": reader, "selected_blocks": [key]}
    audit = {"ordered_proof_stream": [{"kind": "selected", "unit": {"view_id": "txt", "raw_index": 1},
                                       "markdown_span": [0, sum(c.isalnum() for c in reader)]}]}
    return issue, decision, audit


@pytest.mark.parametrize("text", ["The target.", '"The target."', "[The target]", "The target?!"])
def test_identity_preserves_punctuation_outside_alphanumeric_proof_bounds(text):
    result = resolve_issue_reader_occurrence(*_case(text, text), "\n" + text + "\n")
    assert result["reader_projection"]["policy"] == "identity_v1"
    assert result["reader_projection"]["reader_text"] == text
    span = result["page_reader_span"]
    assert text[span["character_start"]:span["character_end"]] == text


def test_normalized_equality_does_not_authorize_punctuation_change():
    with pytest.raises(ReaderOccurrenceError):
        resolve_issue_reader_occurrence(*_case("Christopher Smith", "Christopher, Smith"), "\nChristopher, Smith\n")
