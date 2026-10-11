import json
import shutil
from pathlib import Path

import pytest

from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.reader_text_coverage import OCR_FACT_SCHEMA, TRANSCRIPTION_FACT_SCHEMA, sha256
from kb_creator.pipeline.reader_text_coverage_binding import (
    EVIDENCE_SCHEMA, SELECTORS_SCHEMA, ReaderTextCoverageBindingError,
    SOURCE_TRANSCRIPTION_APPROVAL, bind_reader_coverage_claims,
)


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def block(raw, text, *, bbox=None, kind="text"):
    return {"raw_index": raw, "text": text, "bbox": bbox or [0, 0, 10, 10], "type": kind}


def fixture(tmp_path: Path, *, mode="exact_full_unit", source_text="Volume III", canonical_text=None, reader=None):
    tmp_path.mkdir(parents=True, exist_ok=True)
    canonical_text = canonical_text or source_text
    reader = reader or canonical_text
    source = tmp_path / "source.pdf"; source.write_bytes(b"source bytes")
    run, drafts = tmp_path / "run", tmp_path / "drafts"
    write(run / "run.json", {"source": file_identity(source)})
    for page in (1, 2):
        text_block = block(4, source_text) if page == 2 else block(4, "other")
        ocr_block = block(5, canonical_text if page == 2 else "other")
        write(run / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json",
              {"source_page": page, "views": {"txt": {"blocks": [text_block]}, "raster": {"blocks": [text_block]}, "ocr": {"blocks": [ocr_block]}}})
        for view in ("txt", "raster", "ocr"):
            image = run / f"outputs/04-visual-merge-bundle/visual/{view}/pages/page-{page:03d}.png"
            image.parent.mkdir(parents=True, exist_ok=True); image.write_bytes(f"{view}-{page}".encode())
        write(drafts / f"pages/page-{page:03d}.json", {"source_page": page, "markdown": reader if page == 2 else "other",
              "selected_blocks": [{"view": "ocr", "raw_index": 5, "purpose": "text"}]})
    selector = {"claim_id": "claim-1", "proof_mode": mode,
                "source_key": {"source_page": 2, "view_id": "txt", "raw_index": 4},
                "canonical_key": {"source_page": 2, "view_id": "ocr", "raw_index": 5},
                "reader_page": 2, "reader_span": [0, len(reader)],
                "semantic_container": "complete_selected_block", "validated_fact_id": None}
    selectors = tmp_path / "selectors.json"; write(selectors, {"schema": SELECTORS_SCHEMA, "claims": [selector]})
    evidence = tmp_path / "evidence.json"; write(evidence, {"schema": EVIDENCE_SCHEMA, "facts": []})
    return {"run_root": run, "source_pdf": source, "drafts_root": drafts, "selectors_path": selectors, "evidence_path": evidence}, selector


def add_fact(args, selector, *, text, approved=True, schema=TRANSCRIPTION_FACT_SCHEMA, visual_sha=None):
    visual = args["run_root"] / "outputs/04-visual-merge-bundle/visual/txt/pages/page-002.png"
    identity = {"path": str(visual.resolve()), **file_identity(visual)}
    if visual_sha:
        identity["sha256"] = visual_sha
    backing = args["evidence_path"].parent / "review.json"
    review = {"schema": "kb_creator.reviewed_source_transcription.v1", "approval": SOURCE_TRANSCRIPTION_APPROVAL if approved else "visual_reviewed",
              "reviewer": "fixture", "source_key": selector["source_key"], "canonical_key": selector["canonical_key"],
              "source_pdf": {"path": str(args["source_pdf"].resolve()), **file_identity(args["source_pdf"])}, "source_visual": identity,
              "packet": {"path": str((args["run_root"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-002.json").resolve()), **file_identity(args["run_root"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-002.json")},
              "exact_text": text, "scope": "fixture"}
    write(backing, review)
    fact = {"schema": schema, "fact_id": "fact-1", "source_key": selector["source_key"],
            "canonical_key": selector["canonical_key"], "source_visual": identity,
            "evidence_kind": "validated_ocr_class" if schema == OCR_FACT_SCHEMA else "source_render_exact_transcription",
            "evidence": {"path": str(backing.resolve()), **file_identity(backing)}, "exact_text": text,
            "approval": SOURCE_TRANSCRIPTION_APPROVAL if approved else "visual_reviewed"}
    selector["validated_fact_id"] = "fact-1"
    write(args["selectors_path"], {"schema": SELECTORS_SCHEMA, "claims": [selector]})
    write(args["evidence_path"], {"schema": EVIDENCE_SCHEMA, "facts": [fact]})


def add_ocr_class_fact(args, selector, *, text="repaired", approval="existing_audit_v3_ocr_class"):
    """Create a sealed locator; the test validator remains the actual authority."""
    visual = args["run_root"] / "outputs/04-visual-merge-bundle/visual/txt/pages/page-002.png"
    visual_identity = {"path": str(visual.resolve()), **file_identity(visual)}
    source_packet = args["run_root"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-002.json"
    spec = args["evidence_path"].parent / "class-spec.json"
    write(spec, {"ocr_equivalence_classes": [{
        "class_id": "class-1", "source_page": 2,
        "canonical": {"view_id": "ocr", "raw_index": 5},
        "alternates": [{"view_id": "txt", "raw_index": 4}],
    }]})
    backing = args["evidence_path"].parent / "ocr-class.json"
    reviewed = {
        "schema": "kb_creator.reviewed_ocr_class_binding.v1", "approval": approval,
        "class_id": "class-1", "source_key": selector["source_key"],
        "canonical_key": selector["canonical_key"],
        "source_pdf": {"path": str(args["source_pdf"].resolve()), **file_identity(args["source_pdf"])},
        "source_visual": visual_identity,
        "source_packet": {"path": str(source_packet.resolve()), **file_identity(source_packet)},
        "canonical_packet": {"path": str(source_packet.resolve()), **file_identity(source_packet)},
        "class_spec": {"path": str(spec.resolve()), **file_identity(spec)}, "exact_text": text,
    }
    write(backing, reviewed)
    fact = {
        "schema": OCR_FACT_SCHEMA, "fact_id": "fact-1", "source_key": selector["source_key"],
        "canonical_key": selector["canonical_key"], "source_visual": visual_identity,
        "evidence_kind": "validated_ocr_class", "evidence": {"path": str(backing.resolve()), **file_identity(backing)},
        "exact_text": text, "approval": approval,
    }
    selector["validated_fact_id"] = "fact-1"
    write(args["selectors_path"], {"schema": SELECTORS_SCHEMA, "claims": [selector]})
    write(args["evidence_path"], {"schema": EVIDENCE_SCHEMA, "facts": [fact]})
    return backing, spec


def approved_ocr_class_validator(**context):
    canonical = context["canonical_raw"]
    return {
        "status": "validated", "class_id": context["class_id"],
        "source_key": {"source_page": 2, "view_id": "txt", "raw_index": 4},
        "canonical_key": {"source_page": 2, "view_id": "ocr", "raw_index": 5},
        "exact_text": context["exact_text"], "source_visual": context["source_visual"],
        "canonical_raw_text_sha256": canonical["raw_text_sha256"],
    }


def audit_v3_route_fixture(tmp_path):
    source = tmp_path / "source.pdf"; source.write_bytes(b"source bytes")
    run, drafts = tmp_path / "run", tmp_path / "drafts"
    write(run / "run.json", {"source": file_identity(source)})
    packet = {"source_page": 1, "views": {
        "original_pipeline_txt": {"blocks": [block(4, "bad")]},
        "original_pipeline_ocr": {"blocks": [block(5, "repaired")]},
        "raster_pipeline_ocr": {"blocks": [block(6, "repaired")]},
    }}
    packet_path = run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"; write(packet_path, packet)
    visual = run / "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    visual.parent.mkdir(parents=True, exist_ok=True); visual.write_bytes(b"source visual")
    write(run / "outputs/04-visual-merge-bundle/visual/visual_manifest.json", {"files": [{"path": "visual/original_pipeline_txt/pages/page-001.png"}]})
    write(run / "outputs/03-compare-views/comparison.json", {"views": {}})
    geometry = {"observed_geometry": [{
        "view_id": view, "source_page": 1,
        "media_box_coordinates": ["0", "0", "595", "841"],
        "crop_box_coordinates": ["0", "0", "595", "841"], "rotation_degrees": 0,
        "user_unit": "1", "effective_displayed_size_points": ["595", "841"],
    } for view in packet["views"]]}
    write(run / "outputs/04-visual-merge-bundle/visual/geometry_plan.json", geometry)
    write(drafts / "pages/page-001.json", {"source_page": 1, "markdown": "repaired", "selected_blocks": [{"view": "original_pipeline_ocr", "raw_index": 5, "purpose": "text"}], "assets": []})
    selector = {"claim_id": "audit-class", "proof_mode": "reviewed_ocr_class",
        "source_key": {"source_page": 1, "view_id": "original_pipeline_txt", "raw_index": 4},
        "canonical_key": {"source_page": 1, "view_id": "original_pipeline_ocr", "raw_index": 5},
        "reader_page": 1, "reader_span": [0, 8], "semantic_container": "complete_selected_block", "validated_fact_id": "audit-fact"}
    selectors = tmp_path / "selectors.json"; write(selectors, {"schema": SELECTORS_SCHEMA, "claims": [selector]})
    spec = tmp_path / "class-spec.json"; write(spec, {"ocr_equivalence_classes": [{
        "class_id": "audit-class", "source_page": 1,
        "canonical": {"view_id": "original_pipeline_ocr", "raw_index": 5},
        "alternates": [{"view_id": "original_pipeline_txt", "raw_index": 4}],
        "rationale": "fixture uses the v3 OCR class policy", "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption",
        "equivalence_policy": "reviewed_visual_full_unit_any_cpu_view_v1", "supporting_assertion_ids": [],
    }]})
    visual_id = {"path": str(visual.resolve()), **file_identity(visual)}
    packet_id = {"path": str(packet_path.resolve()), **file_identity(packet_path)}
    backing = tmp_path / "audit-class.json"; write(backing, {
        "schema": "kb_creator.reviewed_ocr_class_binding.v1", "approval": "existing_audit_v3_ocr_class", "class_id": "audit-class",
        "source_key": selector["source_key"], "canonical_key": selector["canonical_key"],
        "source_pdf": {"path": str(source.resolve()), **file_identity(source)}, "source_visual": visual_id,
        "source_packet": packet_id, "canonical_packet": packet_id,
        "class_spec": {"path": str(spec.resolve()), **file_identity(spec)}, "exact_text": "repaired",
    })
    evidence = tmp_path / "evidence.json"; write(evidence, {"schema": EVIDENCE_SCHEMA, "facts": [{
        "schema": OCR_FACT_SCHEMA, "fact_id": "audit-fact", "source_key": selector["source_key"], "canonical_key": selector["canonical_key"],
        "source_visual": visual_id, "evidence_kind": "validated_ocr_class", "evidence": {"path": str(backing.resolve()), **file_identity(backing)},
        "exact_text": "repaired", "approval": "existing_audit_v3_ocr_class",
    }]})
    return {"run_root": run, "source_pdf": source, "drafts_root": drafts, "selectors_path": selectors, "evidence_path": evidence}, backing


def decision_page(args):
    return args["drafts_root"] / "pages/page-002.json"


def add_semantic_correction(args, selector, *, source, corrected):
    """Add the existing six-field correction evidence with one semantic span."""
    path = decision_page(args)
    decision = json.loads(path.read_text())
    decision["markdown"] = corrected
    decision["reviewed_block_corrections"] = [{
        "view": "ocr", "raw_index": 5, "before": source, "after": corrected,
        "reason": "source-bound fixture", "original_text_sha256": sha256(source),
    }]
    decision["semantic_structure"] = {"units": [{
        "source_blocks": [{"view": "ocr", "raw_index": 5}],
        "markdown_span": {"start_line": 1, "end_line": 1, "sha256": sha256(corrected)},
    }]}
    write(path, decision)
    selector.update({"proof_mode": "continuation_subspan", "reader_span": [0, len(corrected)]})
    add_fact(args, selector, text=corrected)


def add_prose_correction(args, selector, *, source, corrected):
    """Add the existing source-hash and sealed plain-paragraph proof."""
    path = decision_page(args)
    decision = json.loads(path.read_text())
    decision["markdown"] = corrected
    decision["reviewed_block_corrections"] = [{
        "view": "ocr", "raw_index": 5, "before": "girl's", "after": "girl’s",
        "reason": "source-bound fixture", "original_text_sha256": sha256(source),
    }]
    decision["reviewed_prose_bindings_v1"] = [{
        "view": "ocr", "raw_index": 5, "original_text_sha256": sha256(source),
        "markdown_span": {"start_line": 1, "end_line": 1, "sha256": sha256(corrected)},
    }]
    write(path, decision)
    selector.update({"proof_mode": "continuation_subspan", "reader_span": [0, len(corrected)]})
    add_fact(args, selector, text=corrected)


@pytest.mark.parametrize("reader", ["prefix middle suffix", "mid\n\ndle", "prefix\n\nmiddle suffix"])
def test_complete_selected_mapping_rejects_larger_or_split_paragraph(tmp_path, reader):
    args, _ = fixture(tmp_path, source_text="middle", reader=reader)
    claim = bind_reader_coverage_claims(**args)["claims"][0]
    assert claim["status"] == "held"
    assert "complete visible paragraph" in claim["detail"]


def test_complete_selected_mapping_accepts_one_entire_emphasized_paragraph(tmp_path):
    args, _ = fixture(tmp_path, source_text="middle", reader="First.\n\n**middle**\n\nLast.")
    claim = bind_reader_coverage_claims(**args)["claims"][0]
    assert claim["status"] == "validated"
    assert claim["claim"]["proof"]["normalized_span"] == [7, 13]


@pytest.mark.parametrize("separator", [">", "> ", "  >\t", "> >"])
def test_empty_quote_separator_preserves_complete_paragraph_boundary(tmp_path, separator):
    args, _ = fixture(tmp_path, source_text="middle", reader=f"> First.\n{separator}\n> middle\n{separator}\n> Last.")
    claim = bind_reader_coverage_claims(**args)["claims"][0]
    assert claim["status"] == "validated"
    assert claim["claim"]["proof"]["normalized_span"] == [7, 13]


def test_empty_quote_separator_does_not_join_split_canonical_text(tmp_path):
    args, _ = fixture(tmp_path, source_text="middle end", reader="> middle\n>\n> end")
    claim = bind_reader_coverage_claims(**args)["claims"][0]
    assert claim["status"] == "held"
    assert "complete visible paragraph" in claim["detail"]


def test_indented_quote_marker_still_holds_unsupported_code(tmp_path):
    args, _ = fixture(tmp_path, source_text="middle", reader="middle\n\n    >")
    assert bind_reader_coverage_claims(**args)["claims"][0]["status"] == "held"


def test_binds_exact_full_unit_from_run_packet_selected_reader_and_actual_files(tmp_path):
    args, _ = fixture(tmp_path)
    result = bind_reader_coverage_claims(**args)
    assert result["claims"][0]["status"] == "validated"
    assert result["claims"][0]["claim"]["source_unit"]["text"] == "Volume III"
    assert result["scope"].startswith("Candidate proof")


def test_binder_processes_primary_first_and_binds_exact_coincident_alias(tmp_path):
    args, primary = fixture(tmp_path, source_text="Move 8", reader="Move 8")
    packet_path = args["run_root"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-002.json"
    packet = json.loads(packet_path.read_text())
    packet["views"]["ocr-copy"] = {"blocks": [block(6, "Move 8")]}
    write(packet_path, packet)
    visual = args["run_root"] / "outputs/04-visual-merge-bundle/visual/ocr-copy/pages/page-002.png"
    visual.parent.mkdir(parents=True, exist_ok=True); visual.write_bytes(b"ocr-copy-2")
    alias = {"claim_id": "claim-2", "proof_mode": "coincident_exact_alias",
             "source_key": {"source_page": 2, "view_id": "ocr-copy", "raw_index": 6},
             "canonical_key": primary["canonical_key"], "reader_page": 2, "reader_span": [0, 6],
             "semantic_container": "complete_selected_block", "validated_fact_id": None,
             "alias_of_claim_id": "claim-1"}
    write(args["selectors_path"], {"schema": SELECTORS_SCHEMA, "claims": [alias, primary]})
    result = bind_reader_coverage_claims(**args)
    rows = {row["claim"]["claim_id"]: row for row in result["claims"]}
    assert rows["claim-2"]["status"] == "validated"
    assert rows["claim-2"]["claim"]["proof"]["alias_of_claim_id"] == "claim-1"


@pytest.mark.parametrize("mutate, expected", [
    (lambda args: args["source_pdf"].write_bytes(b"tampered"), "source PDF"),
    (lambda args: write(args["run_root"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-002.json", {"source_page": 99, "views": {}}), "packet page"),
])
def test_rejects_tampered_source_or_wrong_packet_page(tmp_path, mutate, expected):
    args, _ = fixture(tmp_path); mutate(args)
    if expected == "source PDF":
        with pytest.raises(ReaderTextCoverageBindingError, match=expected):
            bind_reader_coverage_claims(**args)
    else:
        row = bind_reader_coverage_claims(**args)["claims"][0]
        assert row["status"] == "held" and expected in row["detail"]


def test_reconstructs_canonical_mapping_and_rejects_bogus_selector_or_hidden_raw_match(tmp_path):
    args, selector = fixture(tmp_path, source_text="hidden", canonical_text="canonical", reader="[label](hidden)")
    selector["reader_span"] = [0, 6]
    write(args["selectors_path"], {"schema": SELECTORS_SCHEMA, "claims": [selector]})
    row = bind_reader_coverage_claims(**args)["claims"][0]
    assert row["status"] == "held" and "canonical unit has no unique" in row["detail"]
    selector["canonical_key"] = selector["source_key"]
    write(args["selectors_path"], {"schema": SELECTORS_SCHEMA, "claims": [selector]})
    assert bind_reader_coverage_claims(**args)["claims"][0]["status"] == "held"


def test_continuation_needs_explicit_source_image_bound_transcription_approval(tmp_path):
    args, selector = fixture(tmp_path, mode="continuation_subspan", source_text="damaged", canonical_text="prefix exact prose suffix", reader="prefix exact prose suffix")
    selector["reader_span"] = [7, 18]
    add_fact(args, selector, text="exact prose", approved=False)
    held = bind_reader_coverage_claims(**args)["claims"][0]
    assert held["status"] == "deferred" and held["reason_code"] == "missing_bound_evidence"
    add_fact(args, selector, text="exact prose")
    assert bind_reader_coverage_claims(**args)["claims"][0]["status"] == "validated"


def test_transcription_fact_reuses_only_identical_archived_packet_and_render(tmp_path):
    args, selector = fixture(tmp_path, mode="continuation_subspan", source_text="damaged", canonical_text="prefix exact prose suffix", reader="prefix exact prose suffix")
    selector["reader_span"] = [7, 18]
    add_fact(args, selector, text="exact prose")
    replay = tmp_path / "replay"
    shutil.copytree(args["run_root"], replay)
    copied = {**args, "run_root": replay}
    before = {path: path.read_bytes() for path in (args["evidence_path"], tmp_path / "review.json")}
    assert bind_reader_coverage_claims(**copied)["claims"][0]["status"] == "held"
    result = bind_reader_coverage_claims(**copied, reuse_run_root=args["run_root"])
    assert result["claims"][0]["status"] == "validated", result
    claim = result["claims"][0]["claim"]
    assert Path(claim["packet"]["path"]).is_relative_to(replay)
    assert Path(claim["source_visual"]["path"]).is_relative_to(replay)
    assert all(path.read_bytes() == raw for path, raw in before.items())
    packet = replay / "outputs/04-visual-merge-bundle/merge_packets/pages/page-002.json"
    packet.write_bytes(packet.read_bytes() + b" ")
    assert bind_reader_coverage_claims(**copied, reuse_run_root=args["run_root"])["claims"][0]["status"] == "held"


def test_explicit_draft_pages_directory_is_used_without_root_inference(tmp_path):
    args, _ = fixture(tmp_path)
    current = tmp_path / "composer" / "draft-pages"
    shutil.copytree(args["drafts_root"] / "pages", current)
    # The explicit current page directory is authoritative even if a legacy
    # root is present; changing that directory must never fall back to legacy.
    row = bind_reader_coverage_claims(**args, draft_pages_dir=current)["claims"][0]
    assert row["status"] == "validated"
    assert Path(row["claim"]["reader_markdown"]["path"]).parent == current
    page = current / "page-002.json"
    draft = json.loads(page.read_text()); draft["markdown"] = "different current reader"
    write(page, draft)
    assert bind_reader_coverage_claims(**args, draft_pages_dir=current)["claims"][0]["status"] == "held"
    assert bind_reader_coverage_claims(**args)["claims"][0]["status"] == "validated"


@pytest.mark.parametrize("attack", ["render", "archived_render", "archived_pdf", "pdf",
                                  "fact_key", "fact_text", "fact_visual", "review_bytes"])
def test_transcription_reuse_rejects_changed_content_or_original_fact(tmp_path, attack):
    args, selector = fixture(tmp_path, mode="continuation_subspan", source_text="damaged",
                             canonical_text="prefix exact prose suffix", reader="prefix exact prose suffix")
    add_fact(args, selector, text="exact prose")
    replay = tmp_path / "replay"; shutil.copytree(args["run_root"], replay)
    if attack in {"render", "archived_render"}:
        target = replay if attack == "render" else args["run_root"]
        (target / "outputs/04-visual-merge-bundle/visual/txt/pages/page-002.png").write_bytes(b"different render")
    elif attack == "archived_pdf":
        write(args["run_root"] / "run.json", {"source": {"bytes": 1, "sha256": "0" * 64}})
    elif attack == "pdf":
        args["source_pdf"].write_bytes(b"different PDF")
    elif attack == "review_bytes":
        review = tmp_path / "review.json"
        review.write_bytes(review.read_bytes() + b" ")
    else:
        facts = json.loads(args["evidence_path"].read_text())
        fact = facts["facts"][0]
        if attack == "fact_key": fact["canonical_key"]["raw_index"] = 99
        elif attack == "fact_text": fact["exact_text"] = "another reading"
        else: fact["source_visual"] = {**fact["source_visual"], "sha256": "0" * 64}
        write(args["evidence_path"], facts)
    copied = {**args, "run_root": replay}
    if attack == "pdf":
        with pytest.raises(ReaderTextCoverageBindingError, match="source PDF"):
            bind_reader_coverage_claims(**copied, reuse_run_root=args["run_root"])
    else:
        row = bind_reader_coverage_claims(**copied, reuse_run_root=args["run_root"])["claims"][0]
        assert row["status"] == "held", row


def test_ocr_class_requires_existing_validator_and_validates_live_binding(tmp_path):
    args, selector = fixture(tmp_path, mode="reviewed_ocr_class", source_text="bad", canonical_text="repaired", reader="repaired")
    add_ocr_class_fact(args, selector)
    row = bind_reader_coverage_claims(**args)["claims"][0]
    assert row["status"] == "held" and "geometry authority is absent" in row["detail"]
    claim = bind_reader_coverage_claims(**args, ocr_class_validator=approved_ocr_class_validator)["claims"][0]
    assert claim["status"] == "validated"
    assert claim["claim"]["canonical_unit"]["text"] == "repaired"
    assert claim["claim"]["canonical_unit"]["raw_text_sha256"] == sha256("repaired")


def test_ocr_class_default_route_runs_existing_audit_v3_policy(tmp_path):
    args, _ = audit_v3_route_fixture(tmp_path)
    claim = bind_reader_coverage_claims(**args)["claims"][0]
    assert claim["status"] == "validated"
    assert claim["claim"]["proof"]["source_text_sha256"] == sha256("repaired")


def test_ocr_class_default_route_reports_policy_rejection(tmp_path):
    args, backing = audit_v3_route_fixture(tmp_path)
    packet = args["run_root"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    value = json.loads(packet.read_text()); value["views"]["original_pipeline_txt"]["blocks"][0]["bbox"] = [20, 20, 30, 30]; write(packet, value)
    reviewed = json.loads(backing.read_text())
    packet_identity = {"path": str(packet.resolve()), **file_identity(packet)}
    reviewed["source_packet"] = packet_identity; reviewed["canonical_packet"] = packet_identity; write(backing, reviewed)
    evidence = json.loads(args["evidence_path"].read_text())
    evidence["facts"][0]["evidence"] = {"path": str(backing.resolve()), **file_identity(backing)}
    write(args["evidence_path"], evidence)
    row = bind_reader_coverage_claims(**args)["claims"][0]
    assert row["status"] == "held" and "audit v3 did not validate" in row["detail"]


def test_scoped_ocr_class_proof_passes_while_full_audit_keeps_unrelated_gap(tmp_path):
    args, backing = audit_v3_route_fixture(tmp_path)
    packet_path = args["run_root"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    packet = json.loads(packet_path.read_text())
    packet["views"]["original_pipeline_txt"]["blocks"].append(block(9, "unaccounted source", bbox=[200, 200, 300, 220]))
    write(packet_path, packet)
    reviewed = json.loads(backing.read_text())
    packet_identity = {"path": str(packet_path.resolve()), **file_identity(packet_path)}
    reviewed["source_packet"] = packet_identity; reviewed["canonical_packet"] = packet_identity; write(backing, reviewed)
    evidence = json.loads(args["evidence_path"].read_text())
    evidence["facts"][0]["evidence"] = {"path": str(backing.resolve()), **file_identity(backing)}; write(args["evidence_path"], evidence)

    assert bind_reader_coverage_claims(**args)["claims"][0]["status"] == "validated"

    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import audit_v3_content
    from kb_creator.scripts.author_reviewed_semantic_decisions import _cold_ocr_classes, _visual_inventory
    decision = json.loads((args["drafts_root"] / "pages/page-001.json").read_text())
    spec = json.loads((tmp_path / "class-spec.json").read_text())
    visuals = _visual_inventory(args["run_root"])
    allowlist = {"schema": "kb_creator.ai_merge_fidelity_reviewed_allowlist.v3", "authority": {}, "substitutions": [], "source_text_exclusions": [], "visual_text_assertions": [], "ocr_equivalence_classes": _cold_ocr_classes(args["run_root"], spec["ocr_equivalence_classes"], visuals, {1: decision}, {})}
    report = audit_v3_content({1: packet}, {1: decision}, allowlist=allowlist, geometry=json.loads((args["run_root"] / "outputs/04-visual-merge-bundle/visual/geometry_plan.json").read_text()), visual_inventory=visuals)
    assert not report["passed"] and any("unaccounted full source unit original_pipeline_txt:9" in item for item in report["errors"])


def test_ocr_class_recomputes_corrected_reader_form_without_mutating_raw_packet(tmp_path):
    args, selector = fixture(tmp_path, mode="reviewed_ocr_class", source_text="l0st", canonical_text="l0st", reader="l0st")
    add_semantic_correction(args, selector, source="l0st", corrected="lost")
    selector["proof_mode"] = "reviewed_ocr_class"
    selector["reader_span"] = [0, 4]
    add_ocr_class_fact(args, selector, text="lost")
    def validator(**context):
        assert context["canonical_raw"]["text"] == "l0st"
        assert context["decision"]["reviewed_block_corrections"][0]["after"] == "lost"
        result = approved_ocr_class_validator(**context)
        result["exact_text"] = "lost"
        return result
    claim = bind_reader_coverage_claims(**args, ocr_class_validator=validator)["claims"][0]["claim"]
    assert claim["canonical_unit"]["text"] == "l0st"
    assert claim["proof"]["source_text_sha256"] == sha256("lost")


@pytest.mark.parametrize("attack", ["approval", "visual", "packet", "spec", "unrelated_key", "forged_receipt"])
def test_ocr_class_rejects_stale_or_forged_authority(tmp_path, attack):
    args, selector = fixture(tmp_path, mode="reviewed_ocr_class", source_text="bad", canonical_text="repaired", reader="repaired")
    backing, spec = add_ocr_class_fact(args, selector)
    if attack == "approval":
        value = json.loads(backing.read_text()); value["approval"] = "visual_reviewed"; write(backing, value)
    elif attack == "visual":
        visual = args["run_root"] / "outputs/04-visual-merge-bundle/visual/txt/pages/page-002.png"
        visual.write_bytes(b"changed")
    elif attack == "packet":
        packet = args["run_root"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-002.json"
        value = json.loads(packet.read_text()); value["views"]["ocr"]["blocks"][0]["text"] = "changed"; write(packet, value)
    elif attack == "spec":
        write(spec, {"ocr_equivalence_classes": [{"class_id": "changed", "source_page": 2,
                "canonical": {"view_id": "ocr", "raw_index": 5},
                "alternates": [{"view_id": "txt", "raw_index": 4}]}]})
    elif attack == "unrelated_key":
        value = json.loads(backing.read_text()); value["canonical_key"]["raw_index"] = 4; write(backing, value)
    def validator(**context):
        result = approved_ocr_class_validator(**context)
        if attack == "forged_receipt":
            result["exact_text"] = "forged"
        return result
    row = bind_reader_coverage_claims(**args, ocr_class_validator=validator)["claims"][0]
    assert row["status"] == "held"


def test_batch_rejects_duplicate_claim_and_reader_interval_overlap(tmp_path):
    args, selector = fixture(tmp_path)
    duplicate = dict(selector); duplicate["claim_id"] = "claim-2"
    write(args["selectors_path"], {"schema": SELECTORS_SCHEMA, "claims": [selector, duplicate]})
    with pytest.raises(ReaderTextCoverageBindingError, match="more than one"):
        bind_reader_coverage_claims(**args)


def test_selected_table_and_ambiguous_complete_canonical_mapping_are_held(tmp_path):
    args, selector = fixture(tmp_path, reader="Volume III then Volume III")
    selector["reader_span"] = [0, 10]
    write(args["selectors_path"], {"schema": SELECTORS_SCHEMA, "claims": [selector]})
    held = bind_reader_coverage_claims(**args)["claims"][0]
    assert held["status"] == "held" and "unique complete visible paragraph" in held["detail"]
    args, _ = fixture(tmp_path / "table")
    packet = args["run_root"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-002.json"
    value = json.loads(packet.read_text()); value["views"]["txt"]["blocks"][0]["type"] = "table"; write(packet, value)
    assert bind_reader_coverage_claims(**args)["claims"][0]["status"] == "held"


@pytest.mark.parametrize("kind", ["table", "image"])
def test_real_packet_type_is_mandatory_and_nontext_is_held(tmp_path, kind):
    args, _ = fixture(tmp_path)
    packet = args["run_root"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-002.json"
    value = json.loads(packet.read_text()); value["views"]["txt"]["blocks"][0]["type"] = kind; write(packet, value)
    assert bind_reader_coverage_claims(**args)["claims"][0]["status"] == "held"
    value["views"]["txt"]["blocks"][0].pop("type"); write(packet, value)
    assert bind_reader_coverage_claims(**args)["claims"][0]["status"] == "held"


def test_structured_transcription_content_tamper_is_held(tmp_path):
    args, selector = fixture(tmp_path, mode="continuation_subspan", source_text="damaged", canonical_text="prefix exact prose suffix", reader="prefix exact prose suffix")
    selector["reader_span"] = [7, 18]; add_fact(args, selector, text="exact prose")
    review = args["evidence_path"].parent / "review.json"
    value = json.loads(review.read_text()); value["canonical_key"] = dict(selector["source_key"]); write(review, value)
    # Update only the outer identity: bytes alone must still not authorize it.
    evidence = json.loads(args["evidence_path"].read_text()); evidence["facts"][0]["evidence"] = {"path": str(review.resolve()), **file_identity(review)}; write(args["evidence_path"], evidence)
    row = bind_reader_coverage_claims(**args)["claims"][0]
    assert row["status"] == "held" and "does not bind asserted fact" in row["detail"]


def test_claim_visual_identity_uses_the_exact_source_view(tmp_path):
    args, selector = fixture(tmp_path)
    selector["source_key"] = {"source_page": 2, "view_id": "raster", "raw_index": 4}
    write(args["selectors_path"], {"schema": SELECTORS_SCHEMA, "claims": [selector]})
    claim = bind_reader_coverage_claims(**args)["claims"][0]["claim"]
    assert "visual/raster/pages/page-002.png" in claim["source_visual"]["path"].replace("\\", "/")


def test_source_bound_semantic_correction_maps_effective_text_without_mutating_raw_provenance(tmp_path):
    args, selector = fixture(tmp_path, source_text="l0st", canonical_text="l0st", reader="l0st")
    packet = args["run_root"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-002.json"
    raw_packet = packet.read_bytes()
    add_semantic_correction(args, selector, source="l0st", corrected="lost")

    claim = bind_reader_coverage_claims(**args)["claims"][0]["claim"]

    assert claim["canonical_unit"]["text"] == "l0st"
    assert claim["proof"]["normalized_span"] == [0, 4]
    assert packet.read_bytes() == raw_packet
    assert json.loads(packet.read_text())["views"]["ocr"]["blocks"][0]["text"] == "l0st"


def test_explicit_prose_correction_maps_only_after_its_existing_paragraph_proof(tmp_path):
    source = "The girl's coat is blue."
    corrected = "The girl’s coat is blue."
    args, selector = fixture(tmp_path, source_text=source, canonical_text=source, reader=source)
    add_prose_correction(args, selector, source=source, corrected=corrected)

    claim = bind_reader_coverage_claims(**args)["claims"][0]["claim"]

    assert claim["canonical_unit"]["text"] == source
    assert claim["proof"]["normalized_span"] == [0, len(corrected)]


@pytest.mark.parametrize("mutation, expected", [
    (lambda decision: decision["reviewed_block_corrections"].clear(), "no existing authorized correction"),
    (lambda decision: decision["reviewed_block_corrections"].__setitem__(0, {**decision["reviewed_block_corrections"][0], "original_text_sha256": "0" * 64}), "invalid reviewed block correction evidence"),
    (lambda decision: decision.update({"markdown": "A different paragraph.", "reviewed_prose_bindings_v1": [{**decision["reviewed_prose_bindings_v1"][0], "markdown_span": {"start_line": 1, "end_line": 1, "sha256": sha256("A different paragraph.")}}]}), "differs"),
    (lambda decision: decision.update({"semantic_structure": {"units": [{"source_blocks": [{"view": "ocr", "raw_index": 5}]}]}}), "overlaps semantic-unit"),
])
def test_invalid_or_unbound_corrected_canonical_evidence_is_held(tmp_path, mutation, expected):
    source = "The girl's coat is blue."
    corrected = "The girl’s coat is blue."
    args, selector = fixture(tmp_path, source_text=source, canonical_text=source, reader=source)
    add_prose_correction(args, selector, source=source, corrected=corrected)
    path = decision_page(args)
    decision = json.loads(path.read_text())
    mutation(decision)
    write(path, decision)

    held = bind_reader_coverage_claims(**args)["claims"][0]

    assert held["status"] == "held"
    assert expected in held["detail"]
