from hashlib import sha256

import pytest

from kb_creator.pipeline.reviewed_prose_binding import (
    ReviewedProseBindingError,
    verify_reviewed_prose_bindings,
    verify_reviewed_prose_roles,
)


def digest(text):
    return sha256(text.encode("utf-8")).hexdigest().upper()


SOURCE = "The girl's coat is blue."
BEFORE = "girl's"
AFTER = "girl’s"
READER = "The girl’s coat is blue."
KEY = ("original_pipeline_ocr", 268)


def decision(*, span=None, source=SOURCE, bindings=True, corrections=True):
    result = {
        "selected_blocks": [{"view": KEY[0], "raw_index": KEY[1], "purpose": "text"}],
        "reviewed_block_corrections": [],
    }
    if corrections:
        result["reviewed_block_corrections"] = [{
            "view": KEY[0], "raw_index": KEY[1], "before": BEFORE, "after": AFTER,
            "reason": "source visual", "original_text_sha256": digest(source),
        }]
    if bindings:
        result["reviewed_prose_bindings_v1"] = [{
            "view": KEY[0], "raw_index": KEY[1], "original_text_sha256": digest(source),
            "markdown_span": span or {"start_line": 1, "end_line": 1, "sha256": digest(READER)},
        }]
    return result


def verify(data=None, markdown=READER, source_text=SOURCE, **kwargs):
    return verify_reviewed_prose_bindings(
        data or decision(), {KEY: {"text": source_text}}, {KEY}, markdown, 16,
        semantic_units=kwargs.pop("semantic_units", []), **kwargs,
    )


def test_returns_sealed_complete_paragraph_proof_after_all_authorized_corrections():
    proof = verify()

    assert proof[KEY]["corrected_text_sha256"] == digest(READER)
    assert proof[KEY]["visible_text_sha256"] == digest(READER)
    assert proof[KEY]["correction_intervals"] == [{
        "start": 4, "end": 10, "before_sha256": digest(BEFORE), "after_sha256": digest(AFTER),
    }]


def _wrapped_decision(source, reader):
    data = decision(source=source, span={"start_line": 1, "end_line": 1, "sha256": digest(reader)})
    data["reviewed_block_corrections"][0].update(before=source, after=reader)
    data["reviewed_prose_bindings_v1"][0]["source_layout"] = "soft_wrapped_paragraph_v1"
    return data


def test_wrapped_source_requires_explicit_full_correction_and_preserves_raw_identity():
    source = "ikki is missing in the rug  \nged terrain."
    reader = "Nikki is missing in the rugged terrain."
    data = _wrapped_decision(source, reader)
    proof = verify(data, reader, source)[KEY]
    assert proof["source_text_sha256"] == digest(source)
    assert proof["source_layout"] == "soft_wrapped_paragraph_v1"
    assert proof["correction_intervals"][0]["end"] == len(source)
    del data["reviewed_prose_bindings_v1"][0]["source_layout"]
    with pytest.raises(ReviewedProseBindingError, match="complete"):
        verify(data, reader, source)


@pytest.mark.parametrize("source", [
    "First.\n\nSecond.", "First.\n- A list item.", "First.\n# Heading",
    "First.\n> Quote", "First.\n| table |", "First.\n`code`",
    "First.\n    indented code", "First.\n", "No wraps.",
])
def test_wrapped_source_policy_does_not_flatten_structural_or_multiple_blocks(source):
    with pytest.raises(ReviewedProseBindingError):
        verify(_wrapped_decision(source, "Flattened."), "Flattened.", source)


def test_wrapped_source_policy_does_not_implicitly_join_uncorrected_newline():
    source = "Bad first  \nsecond."
    data = _wrapped_decision(source, "Good first second.")
    data["reviewed_block_corrections"][0].update(before="Bad", after="Good")
    with pytest.raises(ReviewedProseBindingError, match="complete"):
        verify(data, "Good first second.", source)


def test_wrapped_source_selector_is_materialized_with_exact_raw_hash():
    from kb_creator.scripts.author_reviewed_semantic_decisions import _materialize_reviewed_prose_bindings
    source = "ikki needs fur  \nther review."
    reader = "Nikki needs further review."
    data = _wrapped_decision(source, reader)
    packet = {"views": {KEY[0]: {"blocks": [{"raw_index": KEY[1], "text": source}]}}}
    selector = {"view": KEY[0], "raw_index": KEY[1], "markdown_span": {"start_line": 1, "end_line": 1},
                "source_layout": "soft_wrapped_paragraph_v1"}
    _materialize_reviewed_prose_bindings(data, packet, [selector], reader, 16)
    assert verify(data, reader, source)[KEY]["source_text_sha256"] == digest(source)
    selector["source_layout"] = "anything"
    with pytest.raises(ValueError, match="source layout"):
        _materialize_reviewed_prose_bindings(data, packet, [selector], reader, 16)


def test_rejects_candidate_map_that_cannot_bypass_existing_six_field_authority():
    with pytest.raises(ReviewedProseBindingError, match="differ"):
        verify(correction_candidates={KEY: [(BEFORE, "wrong")]})
    with pytest.raises(ReviewedProseBindingError, match="no existing authorized"):
        verify(decision(corrections=False))


@pytest.mark.parametrize(
    ("data", "markdown", "message"),
    [
        (decision(span={"start_line": 1, "end_line": 1, "sha256": digest(READER)}), "Other\n\n" + READER, "differs"),
        (decision(span={"start_line": 1, "end_line": 1, "sha256": digest(READER)}), READER + "\n\n" + READER, "unique"),
        (decision(), "[label](https://hidden.example/The%20girl%E2%80%99s%20coat%20is%20blue.)", "prose Markdown"),
        (decision(), "`The girl’s coat is blue.`", "prose Markdown"),
        (decision(), "# The girl’s coat is blue.", "prose Markdown"),
        (decision(), "- The girl’s coat is blue.", "prose Markdown"),
        (decision(), "> The girl’s coat is blue.", "prose Markdown"),
        (decision(), "| The girl’s coat is blue. |", "prose Markdown"),
        (decision(), "<p>The girl’s coat is blue.</p>", "HTML page context"),
    ],
)
def test_rejects_wrong_occurrence_hidden_or_structural_markdown(data, markdown, message):
    data["reviewed_prose_bindings_v1"][0]["markdown_span"]["sha256"] = digest(markdown.split("\n")[0])
    with pytest.raises(ReviewedProseBindingError, match=message):
        verify(data, markdown)


def test_rejects_stale_source_hash_partial_source_and_cross_paragraph_span():
    stale = decision()
    stale["reviewed_prose_bindings_v1"][0]["original_text_sha256"] = digest("old")
    with pytest.raises(ReviewedProseBindingError, match="source hash"):
        verify(stale)
    partial = "The girl's coat is blue.\n\nSecond paragraph."
    with pytest.raises(ReviewedProseBindingError, match="complete"):
        verify(decision(source=partial), source_text=partial)
    data = decision(span={"start_line": 1, "end_line": 2, "sha256": digest(READER + "\nSecond.")})
    with pytest.raises(ReviewedProseBindingError, match="exactly one"):
        verify(data, READER + "\nSecond.")


def test_rejects_malformed_metadata_unselected_key_and_semantic_ownership_overlap():
    malformed = decision()
    malformed["reviewed_prose_bindings_v1"][0]["extra"] = True
    with pytest.raises(ReviewedProseBindingError, match="invalid"):
        verify(malformed)
    unselected = decision()
    unselected["reviewed_prose_bindings_v1"][0]["raw_index"] = 999
    with pytest.raises(ReviewedProseBindingError, match="not uniquely selected"):
        verify(unselected)
    owned = [{"source_blocks": [{"view": KEY[0], "raw_index": KEY[1]}]}]
    with pytest.raises(ReviewedProseBindingError, match="semantic-unit"):
        verify(semantic_units=owned)


def test_rejects_incomplete_application_of_multiple_authorized_corrections():
    source = "The girl's coat is blue - really."
    corrected = "The girl’s coat is blue – really."
    data = decision(source=source, span={"start_line": 1, "end_line": 1, "sha256": digest(corrected)})
    data["reviewed_block_corrections"].append({
        "view": KEY[0], "raw_index": KEY[1], "before": " - ", "after": " – ",
        "reason": "source visual", "original_text_sha256": digest(source),
    })
    assert verify_reviewed_prose_bindings(data, {KEY: {"text": source}}, {KEY}, corrected, 16, semantic_units={})
    data["reviewed_prose_bindings_v1"][0]["markdown_span"]["sha256"] = digest(READER + " - really.")
    with pytest.raises(ReviewedProseBindingError, match="differs"):
        verify_reviewed_prose_bindings(data, {KEY: {"text": source}}, {KEY}, READER + " - really.", 16, semantic_units=[])


def test_rejects_duplicate_binding_and_prose_row_for_a_non_candidate_key():
    duplicate = decision()
    duplicate["reviewed_prose_bindings_v1"].append(duplicate["reviewed_prose_bindings_v1"][0].copy())
    with pytest.raises(ReviewedProseBindingError, match="uniquely"):
        verify(duplicate)


def test_uses_reader_visible_projection_for_pagewide_duplicate_detection():
    markdown = "The **girl’s** coat is blue.\n\n" + READER
    data = decision(span={"start_line": 3, "end_line": 3, "sha256": digest(READER)})

    with pytest.raises(ReviewedProseBindingError, match="not unique"):
        verify(data, markdown)


def test_accepts_supported_emphasis_at_selected_span_by_its_exact_visible_text():
    markdown = "The **girl’s** coat is blue."
    data = decision(span={"start_line": 1, "end_line": 1, "sha256": digest(markdown)})

    assert verify(data, markdown)[KEY]["visible_text_sha256"] == digest(READER)


@pytest.mark.parametrize(
    ("markdown", "message"),
    [
        ("```\n\n" + READER + "\n\n```", "not one visible paragraph"),
        ("<div>\n\n" + READER + "\n\n</div>", "HTML page context"),
        ("<!--\n\n" + READER + "\n\n-->", "HTML page context"),
        ("````\n\n" + READER + "\n\n```\n\n````", "not one visible paragraph"),
        ("~~~~\n\n" + READER + "\n\n~~~\n\n~~~~", "not one visible paragraph"),
    ],
)
def test_rejects_selected_plain_line_in_fenced_or_html_full_page_context(markdown, message):
    data = decision(span={"start_line": 3, "end_line": 3, "sha256": digest(READER)})

    with pytest.raises(ReviewedProseBindingError, match=message):
        verify(data, markdown)


def test_keeps_normal_heading_and_image_page_context_outside_the_prose_binding():
    markdown = "# Chapter\n\n![map](map.png)\n\n" + READER
    data = decision(span={"start_line": 5, "end_line": 5, "sha256": digest(READER)})

    assert verify(data, markdown)[KEY]["reader_span"]["start_line"] == 5


def test_verified_unchanged_title_misflagged_prose_role_is_closed_and_source_bound():
    source = "An ordinary paragraph."
    key = ("original_pipeline_txt", 9)
    visual = {"path": "visual/page-016.png", "bytes": 7, "sha256": "A" * 64}
    data = {"selected_blocks": [{"view": key[0], "raw_index": key[1], "purpose": "text"}],
            "semantic_structure": {"review": {"visual": visual}, "units": []},
            "reviewed_prose_roles_v1": [{"role": "ordinary_prose", "view": key[0], "raw_index": key[1],
                "selection_purpose": "text", "block_type": "text", "source_bbox": [1, 2, 3, 4],
                "original_text_sha256": digest(source),
                "title_evidence": {"text_level": None, "v2_title": False, "middle_title": False, "markdown_heading": True, "model_title": False},
                "markdown_span": {"start_line": 1, "end_line": 1, "sha256": digest(source)}, "visual": visual,
                "rationale": "reviewed ordinary paragraph"}]}
    block = {"type": "text", "text": source, "bbox": [1, 2, 3, 4], "semantic_evidence": data["reviewed_prose_roles_v1"][0]["title_evidence"]}
    proof = verify_reviewed_prose_roles(data, {key: block}, {key}, source, 16, semantic_units=[], visual_inventory={visual["path"]: {"bytes": 7, "sha256": "A" * 64}})
    assert proof[key]["role"] == "ordinary_prose"
    data["reviewed_prose_roles_v1"][0]["title_evidence"]["markdown_heading"] = False
    with pytest.raises(ReviewedProseBindingError, match="title evidence"):
        verify_reviewed_prose_roles(data, {key: block}, {key}, source, 16, semantic_units=[], visual_inventory={visual["path"]: {"bytes": 7, "sha256": "A" * 64}})


def _ordinary_role_fixture():
    source, key = "Ordinary prose.", ("original_pipeline_txt", 7)
    visual = {"path": "visual/page-016.png", "bytes": 7, "sha256": "A" * 64}
    evidence = {"text_level": None, "v2_title": False, "middle_title": False, "markdown_heading": True, "model_title": False}
    row = {"role": "ordinary_prose", "view": key[0], "raw_index": key[1], "selection_purpose": "text", "block_type": "text", "source_bbox": [1, 2, 3, 4], "original_text_sha256": digest(source), "title_evidence": evidence, "markdown_span": {"start_line": 1, "end_line": 1, "sha256": digest(source)}, "visual": visual, "rationale": "reviewed"}
    data = {"selected_blocks": [{"view": key[0], "raw_index": key[1], "purpose": "text"}], "semantic_structure": {"review": {"visual": visual}, "units": []}, "reviewed_prose_roles_v1": [row]}
    block = {"type": "text", "text": source, "bbox": [1, 2, 3, 4], "semantic_evidence": evidence}
    return data, key, block, source, visual


@pytest.mark.parametrize("fault", ["duplicate", "purpose", "source_hash", "bbox", "visual", "span", "owner", "non_title"])
def test_ordinary_role_mutations_fail_closed(fault):
    data, key, block, source, visual = _ordinary_role_fixture()
    if fault == "duplicate": data["reviewed_prose_roles_v1"].append(data["reviewed_prose_roles_v1"][0].copy())
    elif fault == "purpose": data["selected_blocks"][0]["purpose"] = "structure"
    elif fault == "source_hash": data["reviewed_prose_roles_v1"][0]["original_text_sha256"] = digest("stale")
    elif fault == "bbox": data["reviewed_prose_roles_v1"][0]["source_bbox"] = [0, 0, 1, 1]
    elif fault == "visual": data["reviewed_prose_roles_v1"][0]["visual"] = {**visual, "sha256": "B" * 64}
    elif fault == "span": data["reviewed_prose_roles_v1"][0]["markdown_span"]["sha256"] = digest("stale")
    elif fault == "owner": data["semantic_structure"]["units"] = [{"source_blocks": [{"view": key[0], "raw_index": key[1]}]}]
    elif fault == "non_title": block["semantic_evidence"]["markdown_heading"] = False
    with pytest.raises(ReviewedProseBindingError):
        verify_reviewed_prose_roles(data, {key: block}, {key}, source, 16, semantic_units=data["semantic_structure"]["units"], visual_inventory={visual["path"]: {"bytes": 7, "sha256": "A" * 64}})


def test_ordinary_role_rejects_present_null_ledger_and_noop_correction_authority():
    data, key, block, source, visual = _ordinary_role_fixture()
    data["reviewed_prose_roles_v1"] = None
    with pytest.raises(ReviewedProseBindingError, match="roles must be a list"):
        verify_reviewed_prose_roles(data, {key: block}, {key}, source, 16, semantic_units=[], visual_inventory={visual["path"]: {"bytes": 7, "sha256": "A" * 64}})
    data, key, block, source, visual = _ordinary_role_fixture()
    data["reviewed_block_corrections"] = [{"view": key[0], "raw_index": key[1], "before": "Ordinary", "after": "Ordinary", "reason": "forged", "original_text_sha256": digest(source)}]
    with pytest.raises((ReviewedProseBindingError, ValueError), match="correction"):
        verify_reviewed_prose_roles(data, {key: block}, {key}, source, 16, semantic_units=[], visual_inventory={visual["path"]: {"bytes": 7, "sha256": "A" * 64}})
