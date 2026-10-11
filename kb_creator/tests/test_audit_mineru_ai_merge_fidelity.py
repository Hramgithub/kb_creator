import json

import pytest
from jsonschema import validate

from kb_creator.scripts.audit_mineru_ai_merge_fidelity import (
    V3_ALLOWLIST_SCHEMA,
    _fraction_bbox,
    _normalized,
    _public_unit,
    _v3_page_context,
    _make_unit,
    _sha,
    _spatial_metrics,
    audit,
    audit_v2_content,
    audit_v3_content,
    write_output,
)


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def fixture(root, *, source=None, markdown=None, image=False):
    source = source if source is not None else " ".join(f"word{i}" for i in range(100))
    markdown = markdown if markdown is not None else source
    packets = root / "packets"; decisions = root / "decisions"
    blocks = [{"raw_index":0,"source_page":1,"type":"image" if image else "text","text":"" if image else source},{"raw_index":1,"source_page":1,"type":"page_number","text":"1"}]
    put(packets / "pages" / "page-001.json", {"source_page":1,"views":{"original_hybrid":{"blocks":blocks}}})
    put(packets / "merge_index.json", {"by_source_page":[{"source_page":1,"packet":"pages/page-001.json"}]})
    put(decisions / "page-001.json", {"source_page":1,"selected_blocks":[{"view":"original_hybrid","raw_index":0,"purpose":"text"}],"markdown":markdown})
    return decisions, packets


def test_p20_like_l_to_e_mass_drift_fails_recall_and_pattern(tmp_path):
    decisions, packets = fixture(tmp_path, source="will will will will " + "stable " * 20, markdown="wiee wiee wiee wiee " + "stable " * 20)
    report = audit(decisions, packets)
    assert not report["passed"] and any("ll->ee count 4" in error for error in report["errors"])


def test_p44_like_h_to_a_fails_pattern_even_with_high_recall(tmp_path):
    source = "house house house " + "stable " * 97; decisions, packets = fixture(tmp_path, source=source, markdown="aouse aouse aouse " + "stable " * 97)
    report = audit(decisions, packets)
    assert report["pages"][0]["recall"] >= .95 and not report["passed"] and any("h->a count 3" in error for error in report["errors"])


def test_exact_reviewed_allowlist_passes_and_overbroad_or_unused_fails(tmp_path):
    source = "will will will " + "stable " * 97; decisions, packets = fixture(tmp_path, source=source, markdown="wiee wiee wiee " + "stable " * 97)
    allow = tmp_path / "allow.json"; put(allow, {"allowlist":[{"source_page":1,"pattern":{"from":"ll","to":"ee"},"max_count":3,"evidence":"source glyph normalization"}]})
    assert audit(decisions, packets, allow)["passed"]
    put(allow, {"allowlist":[{"source_page":1,"pattern":{"from":"ll","to":"ee"},"max_count":4,"evidence":"too broad"}]})
    assert not audit(decisions, packets, allow)["passed"]


def test_missing_selected_facts_fails_recall(tmp_path):
    decisions, packets = fixture(tmp_path, source=" ".join(f"fact{i}" for i in range(20)), markdown="fact0")
    report = audit(decisions, packets)
    assert not report["passed"] and "recall" in report["errors"][0]


def test_images_and_low_text_pages_are_reported_without_recall_false_fail(tmp_path):
    decisions, packets = fixture(tmp_path, image=True, markdown="![visual]({{asset:cover.jpg}})")
    report = audit(decisions, packets)
    assert report["passed"] and report["pages"][0]["selected_token_count"] == 0 and not report["pages"][0]["recall_threshold_applied"]


def test_inserted_markdown_heading_and_table_labels_do_not_create_cascade_patterns(tmp_path):
    source = "house house house " + "stable " * 97
    decisions, packets = fixture(tmp_path, source=source, markdown="# Added heading\n| Label | Value |\n|---|---|\n" + source)
    report = audit(decisions, packets)
    assert report["passed"] and not report["pages"][0]["substitutions"]


@pytest.mark.parametrize("mutation", ["missing_packet", "duplicate_ref", "unknown_ref", "bad_allowlist"])
def test_malformed_schema_refs_and_allowlist_fail_closed(tmp_path, mutation):
    decisions, packets = fixture(tmp_path)
    if mutation == "missing_packet": (packets / "pages" / "page-001.json").unlink(); call = lambda: audit(decisions, packets)
    elif mutation == "duplicate_ref":
        data=json.loads((decisions/"page-001.json").read_text()); data["selected_blocks"].append(data["selected_blocks"][0]); put(decisions/"page-001.json",data); call=lambda: audit(decisions,packets)
    elif mutation == "unknown_ref":
        data=json.loads((decisions/"page-001.json").read_text()); data["selected_blocks"][0]["raw_index"]=99; put(decisions/"page-001.json",data); call=lambda: audit(decisions,packets)
    else:
        allow=tmp_path/"allow.json"; put(allow,{"allowlist":[{"source_page":1,"pattern":{"from":"l","to":"e"},"max_count":3,"evidence":""}]}); call=lambda: audit(decisions,packets,allow)
    with pytest.raises(ValueError): call()


def test_output_is_deterministic_utf8_lf_and_no_scenario_constants(tmp_path):
    decisions, packets = fixture(tmp_path); one, two = audit(decisions, packets), audit(decisions, packets)
    assert one == two
    output=tmp_path/"report.json"; write_output(output, one)
    assert output.read_bytes().endswith(b"\n") and b"Viral" not in output.read_bytes() and b"Innsmouth" not in output.read_bytes()


def test_legacy_v1_selected_block_audit_keeps_legacy_schema_and_vocabulary(tmp_path):
    decisions, packets = fixture(tmp_path, source="legacy comparison pass", markdown="legacy comparison pass")
    report = audit(decisions, packets)
    assert report["schema"] == "kb_creator.ai-merge-fidelity-audit/v1"
    assert report["passed"] is True
    assert "pass_for_review" not in json.dumps(report)


def v2_packet(texts, *, raster_texts=None, page=1):
    raster_texts = texts if raster_texts is None else raster_texts
    def blocks(values, offset):
        return [{"raw_index": offset + index, "source_page": page, "type": "text", "bbox": [0, index * 10, 100, index * 10 + 9], "text": text} for index, text in enumerate(values)]
    return {"source_page": page, "views": {
        "original_pipeline_txt": {"blocks": blocks(texts, 0)},
        "original_pipeline_ocr": {"blocks": blocks(texts, 100)},
        "raster_pipeline_ocr": {"blocks": blocks(raster_texts, 200)},
    }}


def v2_decision(markdown, selected, *, page=1):
    return {"source_page": page, "markdown": markdown, "selected_blocks": [{"view": view, "raw_index": index, "purpose": "text"} for view, index in selected], "assets": []}


def test_v2_longer_unselected_raster_suffix_fails_but_full_selection_passes():
    packet = v2_packet(["At its center is a mound"], raster_texts=["At its center is a mound with an open mine tunnel descending into the darkness."])
    short = v2_decision("At its center is a mound", [("original_pipeline_txt", 0)])
    report = audit_v2_content({1: packet}, {1: short})
    assert report["pages"][0]["selected_recall"] == 1.0
    assert not report["passed"] and any("raster_pipeline_ocr:200" in error for error in report["errors"])
    full = v2_decision("At its center is a mound with an open mine tunnel descending into the darkness.", [("raster_pipeline_ocr", 200)])
    assert audit_v2_content({1: packet}, {1: full})["passed"]


def test_v2_short_cross_page_start_is_never_exempt_and_boundary_is_closed():
    packets = {1: v2_packet(["testing the malle-"], page=1), 2: v2_packet(["ability of the human body. The rest became vessels."], page=2)}
    omitted = {1: v2_decision("testing the malle-", [("original_pipeline_txt", 0)], page=1), 2: v2_decision("", [], page=2)}
    report = audit_v2_content(packets, omitted)
    assert not report["passed"] and report["pages"][1]["unaccounted_unit_count"] == 3
    complete = {1: omitted[1], 2: v2_decision("ability of the human body. The rest became vessels.", [("original_pipeline_txt", 0)], page=2)}
    report = audit_v2_content(packets, complete)
    assert report["passed"] and report["boundaries"][0]["kind"] == "hyphenated_continuation"


@pytest.mark.parametrize("markdown", ["alpha gamma", "alpha beta", "beta gamma", "alpha beta extra"])
def test_v2_prefix_suffix_middle_and_extra_prose_are_fail_closed(markdown):
    packet = v2_packet(["alpha beta gamma"])
    report = audit_v2_content({1: packet}, {1: v2_decision(markdown, [("original_pipeline_txt", 0)])})
    assert not report["passed"]


def test_v2_monotonic_selected_order_and_unicode_normalization():
    packet = v2_packet(["First block", "mi-go’s soft\u00adhyphen"])
    reordered = v2_decision("mi go's softhyphen First block", [("original_pipeline_txt", 0), ("original_pipeline_txt", 1)])
    assert not audit_v2_content({1: packet}, {1: reordered})["passed"]
    faithful = v2_decision("First block\n\nmi go's softhyphen", [("original_pipeline_txt", 0), ("original_pipeline_txt", 1)])
    assert audit_v2_content({1: packet}, {1: faithful})["passed"]


def test_normalization_strips_only_literal_inline_sup_and_sub_tags():
    assert _normalized("7<sup>th</sup>") == _normalized("7th")
    assert _normalized("<sub>p</sub>erform") == _normalized("perform")
    assert _normalized("<em>perform</em>") != _normalized("perform")
    assert _normalized("<sup class='x'>th</sup>") != _normalized("th")


def test_v2_exact_exclusion_is_used_and_selected_exclusion_fails():
    packet = v2_packet(["Narrative", "117"])
    decision = v2_decision("Narrative", [("original_pipeline_txt", 0)])
    baseline = audit_v2_content({1: packet}, {1: decision})
    page_number = next(row["unit"] for row in baseline["pages"][0]["units"] if row["unit"]["view_id"] == "original_pipeline_txt" and row["unit"]["raw_index"] == 1)
    exclusions = []
    for view, index in (("original_pipeline_txt", 1), ("original_pipeline_ocr", 101), ("raster_pipeline_ocr", 201)):
        unit = next(row["unit"] for row in baseline["pages"][0]["units"] if row["unit"]["view_id"] == view and row["unit"]["raw_index"] == index)
        exclusions.append({"unit": unit, "classification": "non_reader", "rationale": "printed folio", "visual": {"path": "visual/triptych.jpg", "bytes": 1, "sha256": "A" * 64}, "logical_asset": None})
    allowlist = {"substitutions": [], "source_text_exclusions": exclusions, "visual_text_assertions": []}
    assert audit_v2_content({1: packet}, {1: decision}, allowlist=allowlist)["passed"]
    selected = v2_decision("Narrative 117", [("original_pipeline_txt", 0), ("original_pipeline_txt", 1)])
    assert not audit_v2_content({1: packet}, {1: selected}, allowlist=allowlist)["passed"]


def test_v2_report_schema_is_closed_and_rejects_unknown_fields():
    packet = v2_packet(["complete source unit"])
    authorities = {
        "run": {"portable_identity_sha256": "A" * 64, "source_sha256": "B" * 64, "contract_sha256": "C" * 64},
        "review_queue": {"path_hint": "review/review_queue.json", "bytes": 1, "sha256": "D" * 64, "queue_sha256": "E" * 64},
        "comparison": {"path_hint": "outputs/03-compare-views/comparison.json", "bytes": 1, "sha256": "F" * 64},
        "decision_set": {"path_hint": "validated-submission/decision_set.json", "bytes": 1, "sha256": "1" * 64},
        "reviewed_allowlist": None,
        "packets": [{"source_page": 1, "path_hint": "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json", "bytes": 1, "sha256": "2" * 64}],
    }
    report = audit_v2_content({1: packet}, {1: v2_decision("complete source unit", [("original_pipeline_txt", 0)])}, authorities=authorities)
    schema = json.loads((__import__("pathlib").Path(__file__).parents[1] / "contracts/ai_merge_fidelity_audit.v2.schema.json").read_text(encoding="utf-8"))
    validate(report, schema)
    report["unknown"] = True
    with pytest.raises(Exception): validate(report, schema)


def _v3_geometry(page=1):
    return {"observed_geometry": [
        {
            "view_id": view,
            "source_page": page,
            "media_box_coordinates": ["0", "0", "595", "841"],
            "crop_box_coordinates": ["0", "0", "595", "841"],
            "rotation_degrees": 0,
            "user_unit": "1",
            "effective_displayed_size_points": ["595", "841"],
        }
        for view in ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")
    ]}


def _v3_visual():
    identity = {"bytes": 7, "sha256": "A" * 64}
    path = "outputs/04-visual-merge-bundle/visual/triptychs/page-001.png"
    return {path: identity}, {"path": path, **identity}


def _v3_unit(packet, view, index):
    block = next(row for row in packet["views"][view]["blocks"] if row["raw_index"] == index)
    return _public_unit(_make_unit(1, view, block))


def _v3_allowlist(*, assertions=None, classes=None, exclusions=None):
    return {"schema": V3_ALLOWLIST_SCHEMA, "authority": {}, "substitutions": [], "source_text_exclusions": exclusions or [], "visual_text_assertions": assertions or [], "ocr_equivalence_classes": classes or []}


@pytest.mark.parametrize("purpose", ["text", "structure"])
def test_v3_explicit_image_caption_has_exact_reader_span_and_binary_selection(purpose):
    packet = v2_packet(["before", "after"])
    packet["views"]["original_pipeline_txt"]["blocks"].append({
        "raw_index": 77, "source_page": 1, "type": "image", "text": "4",
        "bbox": [200, 200, 300, 300], "assets": ["images/figure.png"],
    })
    decision = v2_decision("before\n\n4\n\nafter", [("original_pipeline_txt", 0),
        ("original_pipeline_txt", 77), ("original_pipeline_txt", 1)])
    decision["selected_blocks"][1]["purpose"] = purpose
    decision["selected_blocks"].insert(2, {"view": "original_pipeline_txt", "raw_index": 77, "purpose": "asset"})
    def run():
        return audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(),
                                geometry=_v3_geometry(), visual_inventory={})
    report = run()
    assert report["passed"], report["errors"]
    stream = report["pages"][0]["ordered_proof_stream"]
    assert [row["unit"]["raw_index"] for row in stream] == [0, 77, 1]
    assert stream[1]["markdown_span"] == [6, 7]
    assert stream[1]["unit"]["block_type"] == "image"
    for wrong in ("before after", "before 5 after", "before 4 4 after"):
        decision["markdown"] = wrong
        assert not run()["passed"]
    decision["markdown"] = "before 4 after"
    decision["selected_blocks"].append({"view": "original_pipeline_txt", "raw_index": 77, "purpose": purpose})
    with pytest.raises(ValueError, match="duplicate selected text unit"):
        run()
    decision["selected_blocks"].pop()
    decision["selected_blocks"] = [row for row in decision["selected_blocks"] if row["purpose"] != purpose or row["raw_index"] != 77]
    decision["markdown"] = "before after"
    assert run()["passed"]  # Asset-only caption does not enter the reader stream.
    decision["markdown"] = "before 4 after"
    assert not run()["passed"]  # A binary selection cannot prove reader text.


def _geometry_row(view, page=1, *, media=None, crop=None, rotation=0, user_unit="1"):
    media = media or ["0", "0", "595", "841"]
    crop = crop or media
    width = (float(media[2]) - float(media[0])) * float(user_unit)
    height = (float(media[3]) - float(media[1])) * float(user_unit)
    effective = [height, width] if rotation in {90, 270} else [width, height]
    return {"view_id": view, "source_page": page, "media_box_coordinates": [str(item) for item in media], "crop_box_coordinates": [str(item) for item in crop], "rotation_degrees": rotation, "user_unit": str(user_unit), "effective_displayed_size_points": [str(item) for item in effective]}


@pytest.mark.parametrize(
    "relation,assertion_text,assertion_bbox,anchor_text,anchor_bbox",
    [
        ("before_anchor", "DISSOCIATION", [100, 100, 600, 180], "by matthew sanderson", [100, 200, 600, 260]),
        ("column_before_anchor", "HEAVY", [50, 700, 450, 900], "next column", [550, 100, 900, 180]),
        ("column_after_anchor", "ISOLATION", [550, 100, 900, 900], "previous column", [100, 700, 450, 900]),
        ("anchor_prefix", "T", [10, 300, 20, 380], "he mi-go came", [10, 300, 500, 380]),
    ],
)
def test_v3_positional_assertions_form_one_interleaved_gapless_stream(relation, assertion_text, assertion_bbox, anchor_text, anchor_bbox):
    packet = v2_packet([anchor_text])
    for view in packet["views"].values():
        view["blocks"][0]["bbox"] = anchor_bbox
    anchor = _v3_unit(packet, "original_pipeline_txt", 0)
    inventory, visual = _v3_visual()
    asset_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/assets/images/handout.png"
    inventory[asset_path] = {"bytes": 11, "sha256": "B" * 64}
    asset_visual = {"path": asset_path, **inventory[asset_path]}
    normalized_assertion = _normalized(assertion_text)
    pair = _normalized(anchor_text) + normalized_assertion if relation in {"after_anchor", "column_after_anchor"} else normalized_assertion + _normalized(anchor_text)
    assertion = {"assertion_id": f"a-{relation}", "source_page": 1, "text": assertion_text, "original_text_sha256": _sha(assertion_text.encode()), "normalized_text_sha256": _sha(normalized_assertion.encode()), "source_region": {"view_id": "original_pipeline_txt", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": assertion_bbox}, "placement": {"relation": relation, "anchor_unit": anchor, "expected_pair_sha256": _sha(pair.encode())}, "visual": visual, "visual_verdict": "source_text_visible_at_region", "rationale": "visible source title/drop cap"}
    markdown = anchor_text + assertion_text if relation in {"after_anchor", "column_after_anchor"} else assertion_text + anchor_text
    report = audit_v3_content({1: packet}, {1: v2_decision(markdown, [("original_pipeline_txt", 0)])}, allowlist=_v3_allowlist(assertions=[assertion]), geometry=_v3_geometry(), visual_inventory=inventory)
    expected_kinds = ["selected", "visual_assertion"] if relation in {"after_anchor", "column_after_anchor"} else ["visual_assertion", "selected"]
    assert report["passed"] and [row["kind"] for row in report["pages"][0]["ordered_proof_stream"]] == expected_kinds


@pytest.mark.parametrize("overlap_view", [None, "original_pipeline_txt", "original_pipeline_ocr"])
def test_v3_repeated_label_assertion_is_bound_to_distinct_source_region(overlap_view):
    text = "Spells: none."
    packet = v2_packet([text, "Education: M.D."])
    for view_name, view in packet["views"].items():
        view["blocks"][0]["bbox"] = [100, 100, 300, 130]
        view["blocks"][1]["bbox"] = [600, 200, 900, 230]
        if view_name == overlap_view:
            view["blocks"][0]["bbox"] = [600, 240, 800, 270]
    normalized = _normalized(text)
    anchor = _v3_unit(packet, "original_pipeline_txt", 1)
    inventory, visual = _v3_visual()
    assertion = {
        "assertion_id": "second-person-spells", "source_page": 1, "text": text,
        "original_text_sha256": _sha(text.encode()), "normalized_text_sha256": _sha(normalized.encode()),
        "source_region": {"view_id": "original_pipeline_txt", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": [600, 240, 800, 270]},
        "placement": {"relation": "after_anchor", "anchor_unit": anchor, "expected_pair_sha256": _sha((_normalized("Education: M.D.") + normalized).encode())},
        "visual": visual, "visual_verdict": "source_text_visible_at_region", "rationale": "A separate printed stat-block field omitted by OCR.",
    }
    decision = v2_decision(text + "Education: M.D." + text, [("original_pipeline_txt", 0), ("original_pipeline_txt", 1)])
    report = audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(assertions=[assertion]), geometry=_v3_geometry(), visual_inventory=inventory)
    if overlap_view is None:
        assert report["passed"], report["errors"]
        stream = report["pages"][0]["ordered_proof_stream"]
        assert [row["kind"] for row in stream] == ["selected", "selected", "visual_assertion"]
    else:
        assert not report["passed"]
        assert any("visual assertion duplicates extracted text" in error for error in report["errors"])


def test_v3_after_anchor_requires_below_geometry_and_reader_order():
    packet = v2_packet(["Cover title"])
    for view in packet["views"].values(): view["blocks"][0]["bbox"] = [100, 100, 600, 180]
    anchor = _v3_unit(packet, "original_pipeline_txt", 0); inventory, visual = _v3_visual(); text = "By Dr. Feuerhuter"; normalized = _normalized(text)
    assertion = {"assertion_id": "byline", "source_page": 1, "text": text, "original_text_sha256": _sha(text.encode()), "normalized_text_sha256": _sha(normalized.encode()), "source_region": {"view_id": "original_pipeline_txt", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": [120, 200, 580, 240]}, "placement": {"relation": "after_anchor", "anchor_unit": anchor, "expected_pair_sha256": _sha((_normalized("Cover title") + normalized).encode())}, "visual": visual, "visual_verdict": "source_text_visible_at_region", "rationale": "printed byline"}
    assert audit_v3_content({1: packet}, {1: v2_decision("Cover title" + text, [("original_pipeline_txt", 0)])}, allowlist=_v3_allowlist(assertions=[assertion]), geometry=_v3_geometry(), visual_inventory=inventory)["passed"]
    assertion["source_region"]["bbox"] = [120, 80, 580, 90]
    assert not audit_v3_content({1: packet}, {1: v2_decision("Cover title" + text, [("original_pipeline_txt", 0)])}, allowlist=_v3_allowlist(assertions=[assertion]), geometry=_v3_geometry(), visual_inventory=inventory)["passed"]


@pytest.mark.parametrize("attack", ["wrong_geometry", "wrong_source", "bad_pair", "missing", "reordered", "duplicate", "malformed_relation"])
def test_v3_column_after_anchor_rejects_wrong_source_geometry_hash_and_reader_stream(attack):
    packet = v2_packet(["previous column"])
    for view in packet["views"].values():
        view["blocks"][0]["bbox"] = [100, 700, 450, 900]
    anchor = _v3_unit(packet, "original_pipeline_txt", 0)
    inventory, visual = _v3_visual()
    text = "ISOLATION"
    normalized = _normalized(text)
    assertion = {
        "assertion_id": "right-column", "source_page": 1, "text": text,
        "original_text_sha256": _sha(text.encode()), "normalized_text_sha256": _sha(normalized.encode()),
        "source_region": {"view_id": "original_pipeline_txt", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": [550, 100, 900, 900]},
        "placement": {"relation": "column_after_anchor", "anchor_unit": anchor, "expected_pair_sha256": _sha((_normalized("previous column") + normalized).encode())},
        "visual": visual, "visual_verdict": "source_text_visible_at_region", "rationale": "visible right-column heading",
    }
    markdown = "previous columnISOLATION"
    if attack == "wrong_geometry":
        assertion["source_region"]["bbox"] = [50, 100, 90, 900]
    elif attack == "wrong_source":
        assertion["source_region"]["view_id"] = "original_pipeline_ocr"
    elif attack == "bad_pair":
        assertion["placement"]["expected_pair_sha256"] = "B" * 64
    elif attack == "missing":
        markdown = "previous column"
    elif attack == "reordered":
        markdown = "ISOLATIONprevious column"
    elif attack == "malformed_relation":
        assertion["placement"]["relation"] = "column_sideways_anchor"
    rows = [assertion, {**assertion, "assertion_id": "duplicate"}] if attack == "duplicate" else [assertion]
    if attack in {"wrong_source", "bad_pair", "duplicate", "malformed_relation"}:
        with pytest.raises(ValueError):
            audit_v3_content({1: packet}, {1: v2_decision(markdown, [("original_pipeline_txt", 0)])}, allowlist=_v3_allowlist(assertions=rows), geometry=_v3_geometry(), visual_inventory=inventory)
    else:
        assert not audit_v3_content({1: packet}, {1: v2_decision(markdown, [("original_pipeline_txt", 0)])}, allowlist=_v3_allowlist(assertions=rows), geometry=_v3_geometry(), visual_inventory=inventory)["passed"]


@pytest.mark.parametrize("attack", ["at_end", "wrong_anchor", "bad_bbox", "bad_pair", "duplicate"])
def test_v3_positional_assertion_attacks_fail_closed(attack):
    packet = v2_packet(["anchor"])
    for view in packet["views"].values(): view["blocks"][0]["bbox"] = [100, 200, 600, 260]
    anchor = _v3_unit(packet, "original_pipeline_txt", 0); inventory, visual = _v3_visual(); text = "TITLE"; normalized = _normalized(text)
    assertion = {"assertion_id": "a", "source_page": 1, "text": text, "original_text_sha256": _sha(text.encode()), "normalized_text_sha256": _sha(normalized.encode()), "source_region": {"view_id": "original_pipeline_txt", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": [100, 100, 600, 180]}, "placement": {"relation": "before_anchor", "anchor_unit": anchor, "expected_pair_sha256": _sha((normalized + _normalized("anchor")).encode())}, "visual": visual, "visual_verdict": "source_text_visible_at_region", "rationale": "visible"}
    markdown = "TITLEanchor"
    if attack == "at_end": markdown = "anchorTITLE"
    elif attack == "wrong_anchor": assertion["placement"]["anchor_unit"] = {**anchor, "raw_index": 99}
    elif attack == "bad_bbox": assertion["source_region"]["bbox"] = [100, 300, 600, 380]
    elif attack == "bad_pair": assertion["placement"]["expected_pair_sha256"] = "B" * 64
    rows = [assertion, {**assertion, "assertion_id": "b"}] if attack == "duplicate" else [assertion]
    try:
        report = audit_v3_content({1: packet}, {1: v2_decision(markdown, [("original_pipeline_txt", 0)])}, allowlist=_v3_allowlist(assertions=rows), geometry=_v3_geometry(), visual_inventory=inventory)
    except ValueError:
        return
    assert not report["passed"]


def test_v3_cross_view_ocr_equivalence_accepts_exact_bounded_class():
    packet = v2_packet(["Examining Vessels (Now and Later)"], raster_texts=["Examining Vessels (ow and Later)"])
    packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "Examining Vessels (fow and Later)"
    for view in packet["views"].values(): view["blocks"][0]["bbox"] = [100, 100, 900, 180]
    canonical = _v3_unit(packet, "original_pipeline_txt", 0)
    alternates = [_v3_unit(packet, "original_pipeline_ocr", 100), _v3_unit(packet, "raster_pipeline_ocr", 200)]
    inventory, visual = _v3_visual()
    row = {"class_id": "vessels-heading", "source_page": 1, "canonical_unit": canonical, "alternate_units": alternates, "visual": visual, "visual_verdict": "canonical_text_visible_alternate_text_absent", "rationale": "source raster confirms canonical heading"}
    report = audit_v3_content({1: packet}, {1: v2_decision("Examining Vessels (Now and Later)", [("original_pipeline_txt", 0)])}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)
    assert report["passed"]
    assert [unit["disposition"] for unit in report["pages"][0]["units"]] == ["included_selected", "included_ocr_equivalent", "included_ocr_equivalent"]


@pytest.mark.parametrize("attack", ["distance", "two_tokens", "wrong_page", "selected_alternate", "missing_bbox", "low_iou", "duplicate_member", "bad_verdict"])
def test_v3_ocr_equivalence_attacks_fail_closed(attack):
    packet = v2_packet(["Examining Vessels now"], raster_texts=["Examining Vessels naw"])
    packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "Examining Vessels naw"
    for view in packet["views"].values(): view["blocks"][0]["bbox"] = [100, 100, 900, 180]
    if attack == "distance": packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "Examining Vessels future"
    if attack == "two_tokens": packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "Examined Vessel naw"
    if attack == "missing_bbox": packet["views"]["original_pipeline_ocr"]["blocks"][0]["bbox"] = None
    if attack == "low_iou": packet["views"]["original_pipeline_ocr"]["blocks"][0]["bbox"] = [0, 800, 100, 900]
    canonical = _v3_unit(packet, "original_pipeline_txt", 0); alt = _v3_unit(packet, "original_pipeline_ocr", 100)
    inventory, visual = _v3_visual(); row = {"class_id": "c", "source_page": 1, "canonical_unit": canonical, "alternate_units": [alt], "visual": visual, "visual_verdict": "canonical_text_visible_alternate_text_absent", "rationale": "visible"}
    decision = v2_decision("Examining Vessels now", [("original_pipeline_txt", 0)])
    if attack == "wrong_page": row["source_page"] = 2
    if attack == "selected_alternate": decision["selected_blocks"].append({"view": "original_pipeline_ocr", "raw_index": 100, "purpose": "text"})
    if attack == "duplicate_member": row["alternate_units"].append(alt)
    if attack == "bad_verdict": row["visual_verdict"] = "alternate_visible"
    try:
        report = audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)
    except ValueError:
        return
    assert not report["passed"]


def test_v3_legacy_v2_contract_remains_explicit_and_unchanged():
    packet = v2_packet(["legacy stable"])
    assert audit_v2_content({1: packet}, {1: v2_decision("legacy stable", [("original_pipeline_txt", 0)])})["schema"] == "kb_creator.ai-merge-fidelity-audit/v2"


@pytest.mark.parametrize("attack", [None, "outside", "duplicate_text", "wrong_asset_binary"])
def test_v3_selected_asset_region_proof_is_closed(attack):
    packet = v2_packet([""])
    for view in packet["views"].values():
        view["blocks"][0].update({"type": "image", "bbox": [100, 100, 900, 900], "assets": ["images/handout.png"]})
    inventory, visual = _v3_visual()
    asset_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/assets/images/handout.png"
    inventory[asset_path] = {"bytes": 11, "sha256": "B" * 64}
    asset_visual = {"path": asset_path, **inventory[asset_path]}
    text = "HANDOUT 9"; normalized = _normalized(text)
    assertion = {
        "assertion_id": "handout-title", "source_page": 1, "text": text,
        "original_text_sha256": _sha(text.encode()), "normalized_text_sha256": _sha(normalized.encode()),
        "source_region": {"view_id": "original_pipeline_txt", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": [200, 200, 700, 300]},
        "placement": {"relation": "within_selected_asset_region", "asset_block": {"source_page": 1, "view_id": "original_pipeline_txt", "raw_index": 0, "block_type": "image", "bbox": [100, 100, 900, 900], "source_path": "images/handout.png"}, "logical_name": "handout-9.png", "asset": asset_visual, "markdown_span": {"start": 0, "end": len(normalized), "sha256": _sha(normalized.encode())}},
        "visual": visual, "visual_verdict": "source_text_visible_at_region", "rationale": "reviewed printed handout title",
    }
    if attack == "outside": assertion["source_region"]["bbox"] = [50, 200, 700, 300]
    if attack == "wrong_asset_binary": assertion["placement"]["asset"] = visual
    decision = v2_decision(text, [("original_pipeline_txt", 0)])
    decision["selected_blocks"][0]["purpose"] = "asset"
    decision["assets"] = [{"view": "original_pipeline_txt", "source_path": "images/handout.png", "logical_name": "handout-9.png", "placement": "reference_only"}]
    rows = [assertion] if attack != "duplicate_text" else [assertion, {**assertion, "assertion_id": "again"}]
    try:
        report = audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(assertions=rows), geometry=_v3_geometry(), visual_inventory=inventory)
    except ValueError:
        assert attack in {"duplicate_text", "wrong_asset_binary"}
    else:
        assert report["passed"] is (attack is None)


def test_v3_selected_asset_region_accepts_sealed_stage02_asset_identity():
    packet = v2_packet([""])
    for view in packet["views"].values():
        view["blocks"][0].update({"type": "image", "bbox": [100, 100, 900, 900], "assets": ["images/handout.png"]})
    inventory, visual = _v3_visual()
    asset_path = "outputs/02-mineru-three-view/views/original_pipeline_txt/artifacts/content_list/images/handout.png"
    inventory[asset_path] = {"bytes": 11, "sha256": "B" * 64}
    text, normalized = "HANDOUT 9", _normalized("HANDOUT 9")
    assertion = {"assertion_id": "stage02-handout", "source_page": 1, "text": text, "original_text_sha256": _sha(text.encode()), "normalized_text_sha256": _sha(normalized.encode()), "source_region": {"view_id": "original_pipeline_txt", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": [200, 200, 700, 300]}, "placement": {"relation": "within_selected_asset_region", "asset_block": {"source_page": 1, "view_id": "original_pipeline_txt", "raw_index": 0, "block_type": "image", "bbox": [100, 100, 900, 900], "source_path": "images/handout.png"}, "logical_name": "handout-9.png", "asset": {"path": asset_path, **inventory[asset_path]}, "markdown_span": {"start": 0, "end": len(normalized), "sha256": _sha(normalized.encode())}}, "visual": visual, "visual_verdict": "source_text_visible_at_region", "rationale": "selected Stage02 source binary"}
    decision = v2_decision(text, [("original_pipeline_txt", 0)])
    decision["selected_blocks"][0]["purpose"] = "asset"
    decision["assets"] = [{"view": "original_pipeline_txt", "source_path": "images/handout.png", "logical_name": "handout-9.png", "placement": "reference_only"}]
    assert audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(assertions=[assertion]), geometry=_v3_geometry(), visual_inventory=inventory)["passed"]


def test_v3_asset_assertion_and_legacy_ocr_proof_share_a_page():
    packet = v2_packet(["canonical"])
    packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "canonicak"
    for view in packet["views"].values(): view["blocks"][0]["bbox"] = [100, 100, 900, 180]
    packet["views"]["original_pipeline_txt"]["blocks"].append({"raw_index": 77, "source_page": 1, "type": "image", "bbox": [100, 300, 900, 900], "text": "", "assets": ["images/handout.png"]})
    inventory, visual = _v3_visual(); asset_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/assets/images/handout.png"; inventory[asset_path] = {"bytes": 11, "sha256": "B" * 64}
    text, normalized = "HANDOUT", _normalized("HANDOUT")
    assertion = {"assertion_id": "asset", "source_page": 1, "text": text, "original_text_sha256": _sha(text.encode()), "normalized_text_sha256": _sha(normalized.encode()), "source_region": {"view_id": "original_pipeline_txt", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": [200, 400, 700, 500]}, "placement": {"relation": "within_selected_asset_region", "asset_block": {"source_page": 1, "view_id": "original_pipeline_txt", "raw_index": 77, "block_type": "image", "bbox": [100, 300, 900, 900], "source_path": "images/handout.png"}, "logical_name": "handout.png", "asset": {"path": asset_path, **inventory[asset_path]}, "markdown_span": {"start": len(_normalized("canonical")), "end": len(_normalized("canonical")) + len(normalized), "sha256": _sha(normalized.encode())}}, "visual": visual, "visual_verdict": "source_text_visible_at_region", "rationale": "printed selected asset text"}
    canonical = _v3_unit(packet, "original_pipeline_txt", 0); alternate = _v3_unit(packet, "original_pipeline_ocr", 100)
    ocr = {"class_id": "same-page", "source_page": 1, "canonical_unit": canonical, "alternate_units": [alternate], "visual": visual, "visual_verdict": "canonical_text_visible_alternate_text_absent", "rationale": "same text OCR view"}
    decision = v2_decision("canonicalHANDOUT", [("original_pipeline_txt", 0)]); decision["selected_blocks"].append({"view": "original_pipeline_txt", "raw_index": 77, "purpose": "asset"}); decision["assets"] = [{"view": "original_pipeline_txt", "source_path": "images/handout.png", "logical_name": "handout.png", "placement": "reference_only"}]
    report = audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(assertions=[assertion], classes=[ocr]), geometry=_v3_geometry(), visual_inventory=inventory)
    assert "page 1: OCR equivalence bounds failed same-page:original_pipeline_ocr:100" in report["errors"]


def test_v3_canonical_crop_geometry_matches_live_p3_proof():
    geometry = {"observed_geometry": [
        _geometry_row("original_pipeline_txt", media=[0, 0, 595, 841], crop=[0, 0, 595, 770]),
        _geometry_row("original_pipeline_ocr", media=[0, 0, 595, 841], crop=[0, 0, 595, 770]),
        _geometry_row("raster_pipeline_ocr", media=[0, 0, 595, 841], crop=[0, 0, 595, 841]),
    ]}
    left = {"source_page": 1, "view_id": "original_pipeline_txt", "bbox": [478, 93, 865, 119]}
    right = {"source_page": 1, "view_id": "raster_pipeline_ocr", "bbox": [478, 171, 865, 195]}
    assert _fraction_bbox(left, geometry)[1:] == pytest.approx([0.169571938169, 0.865, 0.193376932224])
    metrics = _spatial_metrics(left, right, geometry)
    assert metrics["iou"] == pytest.approx(0.880009352350)
    assert metrics["center_distance"] == pytest.approx(0.001078737218)
    assert metrics != {"iou": 0.0, "center_distance": 0.054447222}


@pytest.mark.parametrize("rotation,expected", [
    (0, [0.1, 0.2, 0.3, 0.4]),
    (90, [0.6, 0.1, 0.8, 0.3]),
    (180, [0.7, 0.6, 0.9, 0.8]),
    (270, [0.2, 0.7, 0.4, 0.9]),
])
def test_v3_canonical_geometry_rotation_and_userunit(rotation, expected):
    geometry = {"observed_geometry": [_geometry_row("original_pipeline_txt", media=[10, 20, 610, 820], rotation=rotation, user_unit="2.5")]}
    unit = {"source_page": 1, "view_id": "original_pipeline_txt", "bbox": [100, 200, 300, 400]}
    assert _fraction_bbox(unit, geometry) == pytest.approx(expected)


@pytest.mark.parametrize("attack", ["missing", "duplicate", "rotation", "userunit", "outside_crop", "reversed", "nonfinite", "frame", "effective"])
def test_v3_canonical_geometry_attacks_fail_closed(attack):
    row = _geometry_row("original_pipeline_txt")
    geometry = {"observed_geometry": [row]}
    unit = {"source_page": 1, "view_id": "original_pipeline_txt", "bbox": [100, 200, 300, 400]}
    if attack == "missing": geometry["observed_geometry"] = []
    elif attack == "duplicate": geometry["observed_geometry"].append(dict(row))
    elif attack == "rotation": row["rotation_degrees"] = 45
    elif attack == "userunit": row["user_unit"] = "0"
    elif attack == "outside_crop": row["crop_box_coordinates"] = ["-1", "0", "595", "841"]
    elif attack == "reversed": unit["bbox"] = [300, 200, 100, 400]
    elif attack == "nonfinite": unit["bbox"] = [100, 200, float("nan"), 400]
    elif attack == "frame": unit["bbox"] = [100, 200, 1001, 400]
    else: row["effective_displayed_size_points"] = ["1", "1"]
    with pytest.raises(ValueError, match="v3 geometry"):
        _fraction_bbox(unit, geometry)


def test_v3_unique_exact_whole_unit_equivalence_records_geometry():
    packet = v2_packet(["same complete reader unit"])
    for view in packet["views"].values(): view["blocks"][0]["bbox"] = [100, 100, 800, 180]
    report = audit_v3_content({1: packet}, {1: v2_decision("same complete reader unit", [("original_pipeline_txt", 0)])}, allowlist=_v3_allowlist(), geometry=_v3_geometry(), visual_inventory={})
    assert report["passed"]
    assert [row["disposition"] for row in report["pages"][0]["units"]] == ["included_selected", "included_equivalent_exact", "included_equivalent_exact"]
    assert report["pages"][0]["units"][1]["detail"]["geometry"]["iou"] == 1.0


def test_v3_exact_whole_unit_equivalence_disambiguates_duplicate_text_by_geometry():
    packet = v2_packet(["duplicate", "duplicate"])
    packet["views"]["original_pipeline_txt"]["blocks"][0]["bbox"] = [100, 100, 400, 180]
    packet["views"]["original_pipeline_txt"]["blocks"][1]["bbox"] = [600, 100, 900, 180]
    packet["views"]["original_pipeline_ocr"]["blocks"][0]["bbox"] = [600, 100, 900, 180]
    packet["views"]["original_pipeline_ocr"]["blocks"][1]["bbox"] = [100, 100, 400, 180]
    packet["views"]["raster_pipeline_ocr"]["blocks"][0]["bbox"] = [600, 100, 900, 180]
    packet["views"]["raster_pipeline_ocr"]["blocks"][1]["bbox"] = [100, 100, 400, 180]
    report = audit_v3_content({1: packet}, {1: v2_decision("duplicate duplicate", [("original_pipeline_txt", 0), ("original_pipeline_txt", 1)])}, allowlist=_v3_allowlist(), geometry=_v3_geometry(), visual_inventory={})
    assert report["passed"]
    rows = [row for row in report["pages"][0]["units"] if row["unit"]["view_id"] == "original_pipeline_ocr"]
    assert [row["detail"]["canonical_unit"]["raw_index"] for row in rows] == [1, 0]
    assert all(row["detail"]["policy"] == "exact_unique_cross_view_geometry_v2" for row in rows)


def test_v3_exact_whole_unit_equivalence_refuses_multiple_geometry_candidates():
    packet = v2_packet(["duplicate", "duplicate"])
    for view in packet["views"].values():
        for block in view["blocks"]:
            block["bbox"] = [100, 100, 800, 180]
    report = audit_v3_content({1: packet}, {1: v2_decision("duplicate duplicate", [("original_pipeline_txt", 0), ("original_pipeline_txt", 1)])}, allowlist=_v3_allowlist(), geometry=_v3_geometry(), visual_inventory={})
    assert not report["passed"]


def test_v3_reviewed_visual_full_unit_ocr_class_requires_closed_proof_and_visuals():
    packet = v2_packet(["Complete canonical table of contents entry"], raster_texts=["Comp1ete can0nical fragmented OCR"])
    packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "Com plete canon ical table contents"
    for view in packet["views"].values():
        view["blocks"][0]["bbox"] = [100, 100, 900, 180]
    canonical = _v3_unit(packet, "original_pipeline_txt", 0)
    alternates = [_v3_unit(packet, "original_pipeline_ocr", 100), _v3_unit(packet, "raster_pipeline_ocr", 200)]
    inventory, visual = _v3_visual()
    source_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    source_visual = {"path": source_path, "bytes": 9, "sha256": "B" * 64}
    inventory[source_path] = {"bytes": 9, "sha256": "B" * 64}
    proof = _normalized("Complete canonical table of contents entry")
    row = {"class_id": "gross-reviewed", "source_page": 1, "canonical_unit": canonical, "alternate_units": alternates, "visual": visual, "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption", "rationale": "source render proves canonical reader text", "equivalence_policy": "reviewed_visual_full_unit_v1", "source_visual": source_visual, "canonical_proof": {"supporting_assertion_ids": [], "expected_normalized_sha256": _sha(proof.encode())}}
    report = audit_v3_content({1: packet}, {1: v2_decision("Complete canonical table of contents entry", [("original_pipeline_txt", 0)])}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)
    assert report["passed"]
    assert report["pages"][0]["ocr_equivalence_classes"][0]["equivalence_policy"] == "reviewed_visual_full_unit_v1"
    row["canonical_proof"]["expected_normalized_sha256"] = "C" * 64
    with pytest.raises(ValueError, match="proof hash"):
        audit_v3_content({1: packet}, {1: v2_decision("Complete canonical table of contents entry", [("original_pipeline_txt", 0)])}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)


@pytest.mark.parametrize("source_type", ["text", "header", "footer"])
def test_v3_reviewed_any_cpu_view_canonical_requires_complete_visual_proof_and_alternate_accounting(source_type):
    canonical_text = "There is also a secret elevator behind the shelf."
    packet = v2_packet(["There is also a"], raster_texts=[canonical_text])
    packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "There is also a secret elevat0r"
    for view in packet["views"].values():
        view["blocks"][0]["bbox"] = [100, 100, 900, 180]
        view["blocks"][0]["type"] = source_type
    canonical = _v3_unit(packet, "raster_pipeline_ocr", 200)
    alternates = [_v3_unit(packet, "original_pipeline_txt", 0), _v3_unit(packet, "original_pipeline_ocr", 100)]
    inventory, visual = _v3_visual()
    source_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    source_visual = {"path": source_path, "bytes": 9, "sha256": "B" * 64}
    inventory[source_path] = {"bytes": 9, "sha256": "B" * 64}
    row = {"class_id": "raster-long-txt-short", "source_page": 1, "canonical_unit": canonical, "alternate_units": alternates, "visual": visual, "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption", "rationale": "source render confirms the full raster transcription", "equivalence_policy": "reviewed_visual_full_unit_any_cpu_view_v1", "source_visual": source_visual, "canonical_proof": {"supporting_assertion_ids": [], "expected_normalized_sha256": _sha(_normalized(canonical_text).encode())}}
    decision = v2_decision(canonical_text, [("raster_pipeline_ocr", 200)])
    assert audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)["passed"]
    row["source_visual"]["sha256"] = "C" * 64
    with pytest.raises(ValueError, match="OCR reviewed source"):
        audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)
    row["source_visual"]["sha256"] = "B" * 64
    packet["views"]["original_pipeline_txt"]["blocks"][0]["bbox"] = [10, 10, 40, 40]
    row["alternate_units"] = [_v3_unit(packet, "original_pipeline_txt", 0), _v3_unit(packet, "original_pipeline_ocr", 100)]
    report = audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)
    assert not report["passed"] and any("geometry failed" in error for error in report["errors"])
    packet["views"]["original_pipeline_txt"]["blocks"][0]["bbox"] = [100, 100, 900, 180]
    row["alternate_units"] = [_v3_unit(packet, "original_pipeline_txt", 0), _v3_unit(packet, "original_pipeline_ocr", 100)]
    row["canonical_proof"]["expected_normalized_sha256"] = "D" * 64
    with pytest.raises(ValueError, match="proof hash"):
        audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)
    row["canonical_proof"]["expected_normalized_sha256"] = _sha(_normalized(canonical_text).encode())
    row["alternate_units"] = alternates[:1]
    report = audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)
    assert not report["passed"] and any("unaccounted full source unit original_pipeline_ocr:100" in error for error in report["errors"])


def test_v3_reviewed_any_cpu_non_txt_canonical_allows_strict_ocr_bounds_but_txt_canonical_rejects_them():
    packet = v2_packet(["Oficers"], raster_texts=["Officers"])
    packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "Officers"
    for view in packet["views"].values():
        view["blocks"][0]["bbox"] = [100, 100, 900, 180]
    inventory, visual = _v3_visual()
    source_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    source_visual = {"path": source_path, "bytes": 9, "sha256": "B" * 64}
    inventory[source_path] = {"bytes": 9, "sha256": "B" * 64}
    canonical = _v3_unit(packet, "original_pipeline_ocr", 100)
    alternates = [_v3_unit(packet, "original_pipeline_txt", 0), _v3_unit(packet, "raster_pipeline_ocr", 200)]
    row = {"class_id": "officers-ocr-canonical", "source_page": 1, "canonical_unit": canonical, "alternate_units": alternates, "visual": visual, "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption", "rationale": "source render resolves the missing f in the TXT OCR", "equivalence_policy": "reviewed_visual_full_unit_any_cpu_view_v1", "source_visual": source_visual, "canonical_proof": {"supporting_assertion_ids": [], "expected_normalized_sha256": _sha(_normalized("Officers").encode())}}
    decision = v2_decision("Officers", [("original_pipeline_ocr", 100)])
    assert audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)["passed"]

    row["class_id"] = "officers-txt-canonical"
    row["canonical_unit"] = _v3_unit(packet, "original_pipeline_txt", 0)
    row["alternate_units"] = [_v3_unit(packet, "original_pipeline_ocr", 100), _v3_unit(packet, "raster_pipeline_ocr", 200)]
    row["canonical_proof"]["expected_normalized_sha256"] = _sha(_normalized("Oficers").encode())
    report = audit_v3_content({1: packet}, {1: v2_decision("Oficers", [("original_pipeline_txt", 0)])}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)
    assert not report["passed"] and any("reviewed OCR equivalence is unnecessary" in error for error in report["errors"])


@pytest.mark.parametrize("attack", [None, "raw_text", "bbox", "competing", "ordinary", "corrected_reader"])
def test_v3_exact_raw_text_geometry_drift_policy_is_closed(attack):
    text = "Brawl 40% (20/8) | Damage: 1d3 + DB Dodge 30% (15/6)"
    packet = v2_packet([text], raster_texts=[text])
    packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = text
    for view in packet["views"].values(): view["blocks"][0]["bbox"] = [301, 188, 537, 216]
    packet["views"]["raster_pipeline_ocr"]["blocks"][0]["bbox"] = [307, 195, 765, 222]
    canonical = _v3_unit(packet, "original_pipeline_txt", 0)
    alternates = [_v3_unit(packet, "raster_pipeline_ocr", 200)]
    inventory, visual = _v3_visual(); source_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"; inventory[source_path] = {"bytes": 9, "sha256": "B" * 64}
    row = {"class_id": "p44-lucas-geometry", "source_page": 1, "canonical_unit": canonical, "alternate_units": alternates, "visual": visual, "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption", "rationale": "same printed Lucas text has shifted OCR box", "equivalence_policy": "reviewed_exact_raw_text_geometry_drift_v1", "source_visual": {"path": source_path, "bytes": 9, "sha256": "B" * 64}, "canonical_proof": {"supporting_assertion_ids": [], "expected_normalized_sha256": _sha(_normalized(text).encode())}}
    if attack == "raw_text": packet["views"]["raster_pipeline_ocr"]["blocks"][0]["text"] = "Lucas Angello"; row["alternate_units"] = [_v3_unit(packet, "raster_pipeline_ocr", 200)]
    if attack == "bbox": packet["views"]["raster_pipeline_ocr"]["blocks"][0]["bbox"] = [700, 700, 900, 800]; row["alternate_units"] = [_v3_unit(packet, "raster_pipeline_ocr", 200)]
    if attack == "competing":
        packet["views"]["original_pipeline_txt"]["blocks"].append({"raw_index": 1, "source_page": 1, "type": "text", "bbox": [301, 188, 537, 216], "text": "owner"})
        decision = v2_decision(text + "owner", [("original_pipeline_txt", 0), ("original_pipeline_txt", 1)])
    else: decision = v2_decision(text, [("original_pipeline_txt", 0)])
    if attack == "ordinary":
        packet["views"]["raster_pipeline_ocr"]["blocks"][0]["bbox"] = [301, 188, 537, 216]
        row["alternate_units"] = [_v3_unit(packet, "raster_pipeline_ocr", 200)]
    if attack == "corrected_reader":
        decision["markdown"] = text.replace("Brawl", "Fight")
        decision["review"] = {"notes": "text correction: Brawl -> Fight; reason: fixture review.", "visual_reviewed": True}
        row["canonical_proof"]["expected_normalized_sha256"] = _sha(_normalized(decision["markdown"]).encode())
    geometry = {"observed_geometry": [
        _geometry_row(view, media=[0, 0, 630, 810], crop=([9.1636801, 6.8692002, 623.78497, 801.49103] if view != "raster_pipeline_ocr" or attack == "ordinary" else [0, 0, 630, 810]))
        for view in ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")
    ]}
    report = audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(classes=[row]), geometry=geometry, visual_inventory=inventory)
    assert report["passed"] is (attack is None)


def test_v3_legacy_reviewed_policy_rejects_non_txt_canonical():
    packet = v2_packet(["Short TXT"], raster_texts=["Long raster canonical"])
    for view in packet["views"].values():
        view["blocks"][0]["bbox"] = [100, 100, 900, 180]
    inventory, visual = _v3_visual()
    source_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    inventory[source_path] = {"bytes": 9, "sha256": "B" * 64}
    row = {"class_id": "legacy-raster", "source_page": 1, "canonical_unit": _v3_unit(packet, "raster_pipeline_ocr", 200), "alternate_units": [_v3_unit(packet, "original_pipeline_txt", 0)], "visual": visual, "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption", "rationale": "legacy policy must remain TXT-only", "equivalence_policy": "reviewed_visual_full_unit_v1", "source_visual": {"path": source_path, "bytes": 9, "sha256": "B" * 64}, "canonical_proof": {"supporting_assertion_ids": [], "expected_normalized_sha256": _sha(_normalized("Long raster canonical").encode())}}
    with pytest.raises(ValueError, match="canonical must use original_pipeline_txt"):
        audit_v3_content({1: packet}, {1: v2_decision("Long raster canonical", [("raster_pipeline_ocr", 200)])}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)


def test_v3_reviewed_text_correction_preserves_immutable_ocr_unit_identity():
    packet = v2_packet(["Dou't stop"], raster_texts=["D0u't stop"])
    packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "Do u't stop"
    for view in packet["views"].values():
        view["blocks"][0]["bbox"] = [100, 100, 900, 180]
    canonical = _v3_unit(packet, "original_pipeline_txt", 0)
    alternates = [_v3_unit(packet, "original_pipeline_ocr", 100), _v3_unit(packet, "raster_pipeline_ocr", 200)]
    inventory, visual = _v3_visual()
    source_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    source_visual = {"path": source_path, "bytes": 9, "sha256": "B" * 64}
    inventory[source_path] = {"bytes": 9, "sha256": "B" * 64}
    corrected = _normalized("Don't stop")
    row = {"class_id": "corrected-reviewed", "source_page": 1, "canonical_unit": canonical, "alternate_units": alternates, "visual": visual, "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption", "rationale": "source visual confirms the corrected reader form", "equivalence_policy": "reviewed_visual_full_unit_v1", "source_visual": source_visual, "canonical_proof": {"supporting_assertion_ids": [], "expected_normalized_sha256": _sha(corrected.encode())}}
    decision = v2_decision("Don't stop", [("original_pipeline_txt", 0)])
    decision["review"] = {"visual_reviewed": True, "notes": "text correction: Dou't -> Don't; reason: full-resolution source visual confirms the apostrophe"}
    report = audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(classes=[row]), geometry=_v3_geometry(), visual_inventory=inventory)
    assert report["passed"]
    assert report["pages"][0]["ocr_equivalence_classes"][0]["canonical_unit"] == canonical


def test_v3_context_scopes_reviewed_block_correction_to_one_repeated_unit():
    packet = v2_packet(["Gear: seems fit", "Gear: seems fit"])
    decision = v2_decision("Gear: sees fit\nGear: seems fit", [
        ("original_pipeline_txt", 0), ("original_pipeline_txt", 1),
    ])
    text = packet["views"]["original_pipeline_txt"]["blocks"][0]["text"]
    decision["reviewed_block_corrections"] = [{
        "view": "original_pipeline_txt", "raw_index": 0,
        "before": "seems fit", "after": "sees fit", "reason": "source render",
        "original_text_sha256": _sha(text.encode()),
    }]
    decision["semantic_structure"] = {"units": [
        {
            "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 0}],
            "markdown_span": {"start_line": 1, "end_line": 1, "sha256": _sha("Gear: sees fit".encode())},
        },
        {
            "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 1}],
            "markdown_span": {"start_line": 2, "end_line": 2, "sha256": _sha("Gear: seems fit".encode())},
        },
    ]}
    errors = []
    context = _v3_page_context(1, packet, decision, _v3_geometry(), errors)
    assert not errors
    assert [mapping["markdown_span"] for mapping in context["mappings"]] == [[0, 11], [11, 23]]


@pytest.mark.parametrize("replacement", ["sees fit", "very much sees fit", "seems fit!"])
@pytest.mark.parametrize("owner", [0, 1])
def test_reviewed_coverage_keeps_repeated_owners_and_transports_changed_offsets(replacement, owner):
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _reviewed_coverage_projection, _unit_key
    from kb_creator.pipeline.reader_text_coverage import normalized_text
    from copy import deepcopy

    raw = "Gear: seems fit"
    corrected = "Gear: " + replacement
    packet = v2_packet([raw, raw])
    decision = v2_decision(corrected + "\n" + raw, [
        ("original_pipeline_txt", 0), ("original_pipeline_txt", 1)])
    decision["reviewed_block_corrections"] = [{
        "view": "original_pipeline_txt", "raw_index": 0,
        "before": "seems fit", "after": replacement, "reason": "source render",
        "original_text_sha256": _sha(raw.encode())}]
    decision["semantic_structure"] = {"units": [{
        "source_blocks": [{"view": "original_pipeline_txt", "raw_index": index}],
        "markdown_span": {"start_line": index + 1, "end_line": index + 1, "sha256": _sha(text.encode())},
    } for index, text in enumerate([corrected, raw])]}
    context = _v3_page_context(1, packet, decision, _v3_geometry(), [])
    unit = context["selected"][owner]
    old_start = owner * (len(raw) + 1)
    claim = {"claim_id": "alias", "canonical_unit": {"raw_text_sha256": _sha(raw.encode())},
             "proof": {"normalized_span": [old_start, old_start + len(raw)],
                       "expected_normalized_sha256": _sha(raw.encode())}}
    untouched = deepcopy(claim)
    visible = normalized_text(decision["markdown"])
    result = _reviewed_coverage_projection(claim, unit, context, visible, context["mappings_by_key"][_unit_key(unit)])
    expected_start = 0 if owner == 0 else len(corrected) + 1
    expected_text = corrected if owner == 0 else raw
    assert result["reader_normalized_span"] == [expected_start, expected_start + len(expected_text)]
    assert result["reader_normalized_sha256"] == _sha(expected_text.encode())
    assert claim == untouched
    # A partial original proof must not be expanded into a full corrected owner.
    partial = deepcopy(claim)
    partial["proof"]["normalized_span"][1] -= 1
    with pytest.raises(ValueError, match="partial owner"):
        _reviewed_coverage_projection(partial, unit, context, visible, context["mappings_by_key"][_unit_key(unit)])
    stale = deepcopy(claim)
    stale["proof"]["expected_normalized_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="partial owner"):
        _reviewed_coverage_projection(stale, unit, context, visible, context["mappings_by_key"][_unit_key(unit)])
    with pytest.raises(ValueError, match="absent or ambiguous"):
        _reviewed_coverage_projection(claim, unit, context, visible.replace(expected_text, "missing"), context["mappings_by_key"][_unit_key(unit)])


def test_v3_fidelity_consumer_accepts_explicit_prose_proof_and_rejects_overlap():
    source, reader = "The girl's coat is blue.", "The girl’s coat is blue."
    packet = v2_packet([source])
    for view in packet["views"].values(): view["blocks"][0]["bbox"] = [100, 100, 900, 180]
    decision = v2_decision(reader, [("original_pipeline_txt", 0)])
    decision["reviewed_block_corrections"] = [{
        "view": "original_pipeline_txt", "raw_index": 0, "before": "girl's", "after": "girl’s",
        "reason": "reviewed source", "original_text_sha256": _sha(source.encode()),
    }]
    decision["reviewed_prose_bindings_v1"] = [{
        "view": "original_pipeline_txt", "raw_index": 0, "original_text_sha256": _sha(source.encode()),
        "markdown_span": {"start_line": 1, "end_line": 1, "sha256": _sha(reader.encode())},
    }]
    errors = []
    context = _v3_page_context(1, packet, decision, _v3_geometry(), errors)
    assert not errors and context["mappings"][0]["markdown_span"] == [0, len(_normalized(reader))]
    decision["semantic_structure"] = {"units": [{"source_blocks": [{"view": "original_pipeline_txt", "raw_index": 0}]}]}
    with pytest.raises(ValueError, match="overlaps semantic-unit"):
        _v3_page_context(1, packet, decision, _v3_geometry(), [])


def test_v3_selected_empty_text_block_with_assets_is_allowed_but_plain_nontext_is_not():
    packet = v2_packet(["reader text"])
    visual_table = {"raw_index": 77, "source_page": 1, "type": "table", "bbox": [100, 250, 900, 500], "text": "", "assets": ["assets/table-77.png"]}
    packet["views"]["original_pipeline_txt"]["blocks"].append(visual_table)
    decision = v2_decision("reader text", [("original_pipeline_txt", 0)])
    decision["selected_blocks"].append({"view": "original_pipeline_txt", "raw_index": 77, "purpose": "asset"})
    assert audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(), geometry=_v3_geometry(), visual_inventory={})["passed"]
    packet["views"]["original_pipeline_txt"]["blocks"][-1]["assets"] = []
    with pytest.raises(ValueError, match="selected text reference absent"):
        audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(), geometry=_v3_geometry(), visual_inventory={})


def test_v3_text_bearing_asset_selection_requires_visual_disposition_but_structure_is_mapped():
    packet = v2_packet(["table reader text"])
    for view_id in ("original_pipeline_ocr", "raster_pipeline_ocr"):
        packet["views"][view_id]["blocks"] = []
    block = packet["views"]["original_pipeline_txt"]["blocks"][0]
    block["type"] = "table"
    block["assets"] = ["assets/table.png"]
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    inventory = {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}
    exclusion = {"unit": _public_unit(_make_unit(1, "original_pipeline_txt", block)), "classification": "visual_only", "rationale": "reader text is carried by the selected image asset", "visual": visual, "logical_asset": "table.png"}
    decision = v2_decision("![table]({{asset:table.png}})", [])
    decision["selected_blocks"] = [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "asset"}]
    report = audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(exclusions=[exclusion]), geometry=_v3_geometry(), visual_inventory=inventory)
    assert report["passed"]
    assert report["pages"][0]["units"][0]["disposition"] == "excluded_reviewed"
    decision["selected_blocks"][0]["purpose"] = "structure"
    decision["markdown"] = "table reader text"
    report = audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(), geometry=_v3_geometry(), visual_inventory={})
    assert report["passed"]


@pytest.mark.parametrize("attack", ["ambiguous", "geometry", "missing_markdown"])
def test_v3_exact_whole_unit_equivalence_attacks_fail_closed(attack):
    packet = v2_packet(["same unit"])
    for view in packet["views"].values(): view["blocks"][0]["bbox"] = [100, 100, 800, 180]
    selected = [("original_pipeline_txt", 0)]; markdown = "same unit"
    if attack == "ambiguous": selected.append(("original_pipeline_ocr", 100)); markdown += " same unit"
    elif attack == "geometry": packet["views"]["raster_pipeline_ocr"]["blocks"][0]["bbox"] = [100, 700, 800, 780]
    else: markdown = ""
    report = audit_v3_content({1: packet}, {1: v2_decision(markdown, selected)}, allowlist=_v3_allowlist(), geometry=_v3_geometry(), visual_inventory={})
    assert not report["passed"]


def _subspan_case(canonical="alpha beta gamma", alternates=("beta",)):
    packet = v2_packet([canonical], raster_texts=[canonical])
    packet["views"]["original_pipeline_ocr"]["blocks"] = [
        {"raw_index": 100 + index, "source_page": 1, "type": "text", "bbox": [150 + index * 100, 100, 250 + index * 100, 180], "text": text}
        for index, text in enumerate(alternates)
    ]
    packet["views"]["original_pipeline_txt"]["blocks"][0]["bbox"] = [100, 100, 700, 180]
    packet["views"]["raster_pipeline_ocr"]["blocks"][0]["bbox"] = [100, 100, 700, 180]
    return packet


def test_v3_exact_subspan_equivalence_is_bound_to_selected_context():
    packet = _subspan_case()
    report = audit_v3_content({1: packet}, {1: v2_decision("alpha beta gamma", [("original_pipeline_txt", 0)])}, allowlist=_v3_allowlist(), geometry=_v3_geometry(), visual_inventory={})
    assert report["passed"]
    row = next(row for row in report["pages"][0]["units"] if row["unit"]["view_id"] == "original_pipeline_ocr")
    assert row["disposition"] == "included_equivalent_exact_subspan"
    assert row["detail"]["normalized_substring_offsets"] == [5, 9]
    assert row["detail"]["markdown_span"] == [5, 9]
    assert row["detail"]["geometry"]["smaller_box_coverage"] == 1.0


@pytest.mark.parametrize("alternate,expected", [
    ("alpha beta gamma", "included_equivalent_exact"),
    ("beta", "included_equivalent_exact_subspan"),
    ("delta epsilon", "pending_source_choice"),
])
def test_v3_pending_alternative_cannot_displace_native_source_proof(monkeypatch, alternate, expected):
    from kb_creator.pipeline import pending_source_choices
    packet = _subspan_case(alternates=(alternate,))
    if expected == "included_equivalent_exact":
        packet["views"]["original_pipeline_ocr"]["blocks"][0]["bbox"] = [100, 100, 700, 180]
    decision = v2_decision("alpha beta gamma", [("original_pipeline_txt", 0)])
    kwargs = {"allowlist": _v3_allowlist(), "geometry": _v3_geometry(), "visual_inventory": {}}
    baseline = audit_v3_content({1: packet}, {1: decision}, **kwargs)
    # This unit test isolates disposition priority; sealed authority forgery and
    # source identity checks are exercised in test_pending_source_choices.
    monkeypatch.setattr(pending_source_choices, "derive_pending_source_keys",
                        lambda **_kw: {(1, "original_pipeline_ocr", 100), (1, "raster_pipeline_ocr", 200)})
    actual = audit_v3_content({1: packet}, {1: decision}, **kwargs, pending_source_context={
        "review_input": {}, "input_path": ".", "binding_root": ".", "run_root": "."})
    assert actual["passed"], actual["errors"]
    units = actual["pages"][0]["units"]
    assert [row["disposition"] for row in units] == ["included_selected", expected, "included_equivalent_exact"]
    if expected != "pending_source_choice":
        assert actual == baseline
    else:
        assert baseline["pages"][0]["unaccounted_unit_count"] == 1


@pytest.mark.parametrize("attack", ["repeated", "fuzzy", "concatenated", "collision", "partial_markdown", "duplicate", "reorder"])
def test_v3_exact_subspan_attacks_fail_closed(attack):
    canonical, alternates, markdown = "alpha beta gamma", ("beta",), "alpha beta gamma"
    if attack == "repeated": canonical, alternates, markdown = "beta alpha beta", ("beta",), "beta alpha beta"
    elif attack == "fuzzy": alternates = ("betx",)
    elif attack == "concatenated": canonical, alternates, markdown = "alpha", ("alphabeta",), "alpha beta"
    elif attack == "duplicate": alternates = ("beta", "beta")
    elif attack == "reorder": alternates = ("gamma", "alpha")
    packet = _subspan_case(canonical, alternates)
    selected = [("original_pipeline_txt", 0)]
    if attack == "collision":
        packet["views"]["raster_pipeline_ocr"]["blocks"].append({"raw_index": 201, "source_page": 1, "type": "text", "bbox": [150, 100, 250, 180], "text": "neighbor"})
        selected.append(("raster_pipeline_ocr", 201)); markdown += " neighbor"
    if attack == "partial_markdown": markdown = "alpha gamma"
    report = audit_v3_content({1: packet}, {1: v2_decision(markdown, selected)}, allowlist=_v3_allowlist(), geometry=_v3_geometry(), visual_inventory={})
    assert not report["passed"]


def _running_header_case(*, second_text="DISSOCIATION", second_bbox=None):
    packets, decisions, exclusions, inventory = {}, {}, [], {}
    for page, header_text in ((1, "DISSOCIATION"), (2, second_text)):
        packet = v2_packet([f"Body page {page}"], page=page)
        for view in packet["views"].values(): view["blocks"][0]["bbox"] = [100, 200, 800, 280]
        bbox = second_bbox if page == 2 and second_bbox is not None else [400, 10, 650, 40]
        header = {"raw_index": 201, "source_page": page, "type": "text", "bbox": bbox, "text": header_text}
        packet["views"]["raster_pipeline_ocr"]["blocks"].append(header)
        packets[page] = packet; decisions[page] = v2_decision(f"Body page {page}", [("original_pipeline_txt", 0)], page=page)
        path = f"outputs/04-visual-merge-bundle/visual/triptychs/page-{page:03}.png"
        visual = {"path": path, "bytes": page, "sha256": str(page) * 64}; inventory[path] = {"bytes": page, "sha256": str(page) * 64}
        exclusions.append({"unit": _public_unit(_make_unit(page, "raster_pipeline_ocr", header)), "classification": "non_reader", "rationale": "reviewed repeated top running furniture", "visual": visual, "logical_asset": None})
    geometry = {"observed_geometry": [_geometry_row(view, page) for page in (1, 2) for view in ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")]}
    return packets, decisions, exclusions, inventory, geometry


def test_v3_reviewed_generic_text_running_header_cohort_passes():
    packets, decisions, exclusions, inventory, geometry = _running_header_case()
    report = audit_v3_content(packets, decisions, allowlist=_v3_allowlist(exclusions=exclusions), geometry=geometry, visual_inventory=inventory)
    assert report["passed"]
    assert sum(row["detail"] == {"classification": "non_reader"} for page in report["pages"] for row in page["units"]) == 2


@pytest.mark.parametrize("attack", ["one_off", "body", "bottom", "shifted", "two_chars", "selected", "missing_visual", "same_page"])
def test_v3_running_header_cohort_attacks_fail_closed(attack):
    second_text = "DISSOCIAXXON" if attack == "two_chars" else "DISSOCIATION"
    second_bbox = [400, 400, 650, 430] if attack in {"body", "bottom"} else [50, 10, 300, 40] if attack == "shifted" else None
    packets, decisions, exclusions, inventory, geometry = _running_header_case(second_text=second_text, second_bbox=second_bbox)
    if attack == "one_off": exclusions.pop()
    elif attack == "selected":
        decisions[1]["selected_blocks"].append({"view": "raster_pipeline_ocr", "raw_index": 201, "purpose": "text"}); decisions[1]["markdown"] += " DISSOCIATION"
    elif attack == "missing_visual": inventory.clear()
    elif attack == "same_page":
        exclusions[1]["unit"]["source_page"] = 1
    try:
        report = audit_v3_content(packets, decisions, allowlist=_v3_allowlist(exclusions=exclusions), geometry=geometry, visual_inventory=inventory)
    except ValueError:
        return
    assert not report["passed"]
