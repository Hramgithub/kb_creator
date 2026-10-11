import pytest

from kb_creator.pipeline.reader_text_coverage import (
    OCR_FACT_SCHEMA,
    TRANSCRIPTION_FACT_SCHEMA,
    ReaderTextCoverageError,
    assess_claim,
    normalized_text,
    sha256,
    validate_claims,
)


SHA = "A" * 64


def identity(path):
    return {"path": path, "bytes": 1, "sha256": SHA}


def unit(page, view, index, text, *, kind="text"):
    return {"source_page": page, "view_id": view, "raw_index": index, "block_type": kind, "text": text, "raw_text_sha256": sha256(text), "bbox": [0, 0, 100, 10]}


def selector(*, claim_id="coverage-1", mode="exact_full_unit", source=(2, "txt", 4), canonical=(2, "ocr", 4), page=2, span=None, fact=None, alias_of=None):
    value = {"claim_id": claim_id, "proof_mode": mode, "source_key": {"source_page": source[0], "view_id": source[1], "raw_index": source[2]}, "canonical_key": {"source_page": canonical[0], "view_id": canonical[1], "raw_index": canonical[2]}, "reader_page": page, "reader_span": span or [0, 10], "semantic_container": "body-1", "validated_fact_id": fact}
    if alias_of is not None:
        value["alias_of_claim_id"] = alias_of
    return value


def context(*, source_text="Volume III", reader="Volume III", source=(2, "txt", 4), canonical=(2, "ocr", 4), page=2, facts=None, source_kind="text"):
    source_unit = unit(*source, source_text, kind=source_kind)
    canonical_unit = unit(*canonical, source_text)
    return {"units": {source: source_unit, canonical: canonical_unit}, "selected_keys": [canonical], "reader_pages": {page: {"markdown": reader, "semantic_container": "body-1"}}, "source_pdf": identity("source.pdf"), "packet": identity("packet.json"), "source_visuals": {source[0]: identity("page.png")}, "reader_markdown": {page: identity("reader.md")}, "selected_mappings": {canonical: {"reader_page": page, "normalized_span": [0, len(normalized_text(reader))], "semantic_container": "body-1"}}, "validated_facts": facts or {}}


def claim(s, c):
    return assess_claim(s, **c)


def test_exact_duplicate_binds_every_identity_and_preserves_punctuation_and_numbers():
    c = context(source_text="Rule 1.2: A/B", reader="Rule 1.2: A/B")
    result = claim(selector(span=[0, 13]), c)
    assert result["status"] == "validated"
    assert result["claim"]["source_unit"]["text"] == "Rule 1.2: A/B"
    assert result["claim"]["proof"]["source_text_sha256"] != ""
    validate_claims([result])
    with pytest.raises(ReaderTextCoverageError, match="exactly"):
        claim(selector(span=[0, 12]), c)


def test_meaningful_selected_header_is_reader_text_when_its_mapping_is_bound():
    c = context(source_text="Player Handout C", reader="Player Handout C")
    c["units"][(2, "txt", 4)]["block_type"] = "header"
    c["units"][(2, "ocr", 4)]["block_type"] = "header"
    assert claim(selector(span=[0, 16]), c)["status"] == "validated"


def test_whitespace_folding_only_never_equates_punctuation_case_or_numbers():
    assert normalized_text("A\n B") == "A B"
    for bad in ("Rule 12", "rule 1.2", "Rule 1,2"):
        with pytest.raises(ReaderTextCoverageError, match="exactly"):
            claim(selector(span=[0, len(bad)]), context(source_text="Rule 1.2", reader=bad))


def test_reviewed_ocr_requires_a_bound_fact_and_binds_corrected_text():
    s = selector(mode="reviewed_ocr_class", fact="ocr-4", span=[0, 16])
    c = context(source_text="Call of Cthulhu", reader="Call of Cthulhu®")
    held = claim(s, c)
    assert held == {"status": "deferred", "claim_id": "coverage-1", "reason_code": "missing_bound_evidence", "needed": "validated OCR-class fact", "source_key": s["source_key"]}
    fact = {"schema": OCR_FACT_SCHEMA, "fact_id": "ocr-4", "source_key": s["source_key"], "canonical_key": s["canonical_key"], "source_visual": identity("page.png"), "evidence_kind": "validated_ocr_class", "evidence": identity("ocr-class.json"), "exact_text": "Call of Cthulhu®"}
    assert claim(s, context(source_text="Call of Cthulhu", reader="Call of Cthulhu®", facts={"ocr-4": fact}))["status"] == "validated"
    fact["source_visual"]["sha256"] = "B" * 64
    with pytest.raises(ReaderTextCoverageError, match="visual identity is stale"):
        claim(s, context(source_text="Call of Cthulhu", reader="Call of Cthulhu®", facts={"ocr-4": fact}))


def test_continuation_allows_preceding_reader_page_only_with_bound_transcription():
    s = selector(mode="continuation_subspan", source=(4, "txt", 35), canonical=(3, "ocr", 7), page=3, span=[7, 22], fact="transcript-35")
    c = context(source_text="unreadable", reader="prefix paint elaborate suffix", source=(4, "txt", 35), canonical=(3, "ocr", 7), page=3)
    assert claim(s, c)["status"] == "deferred"
    fact = {"schema": TRANSCRIPTION_FACT_SCHEMA, "fact_id": "transcript-35", "source_key": s["source_key"], "canonical_key": s["canonical_key"], "source_visual": identity("page.png"), "evidence_kind": "source_bound_decoder", "evidence": identity("decoder-receipt.json"), "exact_text": "paint elaborate"}
    c["validated_facts"] = {"transcript-35": fact}
    assert claim(s, c)["status"] == "validated"
    distant = context(source_text="unreadable", reader="paint elaborate", source=(4, "txt", 35), canonical=(2, "ocr", 7), page=2)
    with pytest.raises(ReaderTextCoverageError, match="immediately preceding"):
        claim(selector(mode="continuation_subspan", source=(4, "txt", 35), canonical=(2, "ocr", 7), page=2, span=[0, 1], fact="transcript-35"), distant)


@pytest.mark.parametrize("mutate, message", [
    (lambda s, c: s.update(canonical_key=s["source_key"]), "cannot be the source"),
    (lambda s, c: c["selected_keys"].clear(), "not selected"),
    (lambda s, c: c.update(excluded_keys=[(2, "txt", 4)]), "excluded"),
    (lambda s, c: c["units"].__setitem__((2, "txt", 4), unit(2, "txt", 4, "text", kind="table")), "asset, table"),
    (lambda s, c: c["reader_pages"][2].update(semantic_container="other"), "semantic container"),
])
def test_rejects_selected_source_nonselected_asset_and_wrong_container(mutate, message):
    s, c = selector(), context()
    mutate(s, c)
    with pytest.raises(ReaderTextCoverageError, match=message):
        claim(s, c)


def test_batch_rejects_duplicate_source_and_overlapping_reader_spans():
    c = context(source=(2, "txt", 4), canonical=(2, "ocr", 4), source_text="first", reader="first second")
    first = claim(selector(claim_id="one", span=[0, 5]), c)
    duplicate = claim(selector(claim_id="two", span=[0, 5]), c)
    with pytest.raises(ReaderTextCoverageError, match="more than one"):
        validate_claims([first, duplicate])
    c2 = context(source=(2, "txt", 5), canonical=(2, "ocr", 5), source_text="rst s", reader="first second")
    second = claim(selector(claim_id="two", source=(2, "txt", 5), canonical=(2, "ocr", 5), span=[2, 7]), c2)
    with pytest.raises(ReaderTextCoverageError, match="overlaps"):
        validate_claims([first, second])


def test_coincident_exact_alias_requires_named_exact_primary_and_allows_only_its_overlap():
    primary_context = context(source_text="Move 8", reader="Move 8")
    primary = claim(selector(claim_id="primary", span=[0, 6]), primary_context)["claim"]
    alias_context = context(source=(2, "ocr-copy", 9), canonical=(2, "ocr", 4), source_text="Move 8", reader="Move 8")
    alias = claim(selector(claim_id="alias", mode="coincident_exact_alias", source=(2, "ocr-copy", 9), canonical=(2, "ocr", 4), span=[0, 6], alias_of="primary"), alias_context | {"primary_claims": {"primary": primary}})
    assert alias["status"] == "validated"
    assert alias["claim"]["proof"]["alias_of_claim_id"] == "primary"
    validate_claims([alias, {"status": "validated", "claim": primary}])


@pytest.mark.parametrize("mutate", [
    lambda c: c["units"][(2, "ocr-copy", 9)].update(bbox=[1, 0, 100, 10]),
    lambda c: c["units"][(2, "ocr-copy", 9)].update(text="Move 9", raw_text_sha256=sha256("Move 9")),
    lambda c: c["reader_markdown"][2].update(path="other.md"),
])
def test_coincident_exact_alias_rejects_forged_geometry_text_or_reader_identity(mutate):
    primary = claim(selector(claim_id="primary", span=[0, 6]), context(source_text="Move 8", reader="Move 8"))["claim"]
    alias_context = context(source=(2, "ocr-copy", 9), canonical=(2, "ocr", 4), source_text="Move 8", reader="Move 8")
    mutate(alias_context)
    alias = selector(claim_id="alias", mode="coincident_exact_alias", source=(2, "ocr-copy", 9), canonical=(2, "ocr", 4), span=[0, 6], alias_of="primary")
    with pytest.raises(ReaderTextCoverageError, match="coincident alias"):
        claim(alias, alias_context | {"primary_claims": {"primary": primary}})


def test_coincident_exact_alias_rejects_missing_primary_and_alias_chain():
    alias_context = context(source=(2, "ocr-copy", 9), canonical=(2, "ocr", 4), source_text="Move 8", reader="Move 8")
    alias = selector(claim_id="alias", mode="coincident_exact_alias", source=(2, "ocr-copy", 9), canonical=(2, "ocr", 4), span=[0, 6], alias_of="primary")
    with pytest.raises(ReaderTextCoverageError, match="primary"):
        claim(alias, alias_context)
    fake_primary = {"schema": "kb_creator.reader_text_coverage_claim.v1", "claim_id": "primary", "proof_mode": "coincident_exact_alias"}
    with pytest.raises(ReaderTextCoverageError, match="primary"):
        claim(alias, alias_context | {"primary_claims": {"primary": fake_primary}})


def test_validate_claims_rechecks_alias_packet_identity_against_its_primary():
    primary = claim(selector(claim_id="primary", span=[0, 6]), context(source_text="Move 8", reader="Move 8"))["claim"]
    alias_context = context(source=(2, "ocr-copy", 9), canonical=(2, "ocr", 4), source_text="Move 8", reader="Move 8")
    alias = claim(selector(claim_id="alias", mode="coincident_exact_alias", source=(2, "ocr-copy", 9), canonical=(2, "ocr", 4), span=[0, 6], alias_of="primary"), alias_context | {"primary_claims": {"primary": primary}})
    alias["claim"]["packet"]["sha256"] = "B" * 64
    with pytest.raises(ReaderTextCoverageError, match="coincident alias"):
        validate_claims([{"status": "validated", "claim": primary}, alias])


def test_overlapping_occurrences_do_not_prove_unique_reader_coverage():
    with pytest.raises(ReaderTextCoverageError, match="ambiguous or duplicated"):
        claim(selector(span=[0, 2]), context(source_text="aa", reader="aaa"))


def test_disjoint_source_claims_still_require_distinct_claim_ids():
    first = claim(selector(claim_id="same", span=[0, 5]),
                  context(source_text="first", reader="first second"))
    second = claim(selector(claim_id="same", source=(2, "txt", 5),
                            canonical=(2, "ocr", 5), span=[6, 12]),
                   context(source=(2, "txt", 5), canonical=(2, "ocr", 5),
                           source_text="second", reader="first second"))
    with pytest.raises(ReaderTextCoverageError, match="claim_id.*duplicated"):
        validate_claims([first, second])
    second["claim"]["claim_id"] = "different"
    validate_claims([first, second])


@pytest.mark.parametrize("mutate, message", [
    (lambda s, c: c["units"].__setitem__((2, "ocr", 4), unit(2, "ocr", 4, "unrelated")), "canonical text differs"),
    (lambda s, c: c["units"][(2, "ocr", 4)].update(bbox=[1, 0, 100, 10]), "canonical geometry differs"),
    (lambda s, c: c["selected_mappings"][(2, "ocr", 4)].update(normalized_span=[0, 5]), "not bound to the canonical"),
    (lambda s, c: c["reader_pages"][2].update(markdown="Volume III then Volume III"), "ambiguous or duplicated"),
    (lambda s, c: c["units"][(2, "txt", 4)].update(raw_text_sha256="B" * 64), "raw text identity"),
])
def test_exact_claim_requires_canonical_text_geometry_mapping_unique_reader_text_and_raw_identity(mutate, message):
    s, c = selector(), context()
    mutate(s, c)
    with pytest.raises(ReaderTextCoverageError, match=message):
        claim(s, c)
