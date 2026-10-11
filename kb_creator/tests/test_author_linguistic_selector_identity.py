from kb_creator.pipeline.identity import file_identity, sha256_bytes
from kb_creator.scripts.author_reviewed_semantic_decisions import _materialize_linguistic_source_choice_corrections


def test_author_binds_ledger_file_and_immutable_selected_source(tmp_path):
    ledger = tmp_path / "ledger.json"
    ledger.write_text('{"fixture": "identity conversion only"}', encoding="utf-8")
    decision = {"selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 1, "purpose": "text"}],
                "review": {"visual_reviewed": False}}
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 1, "text": "Old reading"}]}}}
    selector = {"ledger": str(ledger), "issue_id": "choice-1", "alternative_id": "alternative-1",
                "view": "original_pipeline_txt", "raw_index": 1, "before": "Old reading", "after": "New reading"}
    _materialize_linguistic_source_choice_corrections(decision, packet, [selector], 1)
    actual = decision["linguistic_source_choice_corrections"][0]
    assert actual["ledger"] == {"path": str(ledger.resolve()), **file_identity(ledger)}
    assert actual["original_text_sha256"] == sha256_bytes(b"Old reading")
    assert actual["authority"] == "linguistic_source_choice"
    assert decision["review"]["visual_reviewed"] is False
