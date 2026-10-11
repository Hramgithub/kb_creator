import copy
import json

import pytest

from kb_creator.pipeline import mechanical_reconstruction as mechanical
from kb_creator.tests.test_mechanical_reconstruction import _block, _packet, _stage04, VIEWS


def candidate(tmp_path, texts, *, correction=None, semantic=False, assets=False):
    blocks = {view: [_block(0, text)] for view, text in zip(VIEWS, texts)}
    if semantic:
        blocks[VIEWS[2]][0]["semantic_evidence"] = {"text_level": 2}
    if assets:
        blocks[VIEWS[2]][0]["assets"] = ["different.png"]
    root = _stage04(tmp_path / "run", {1: _packet(1, blocks)})
    packet = json.loads((root / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json").read_text())
    ledger = {}
    if correction:
        before, after = correction
        identity = {"path": "example.json", "bytes": 1, "sha256": "A" * 64}
        ledger[(1, VIEWS[1], 0)] = {
            "source_page": 1, "view": VIEWS[1], "raw_index": 0,
            "before": before, "after": after, "reason": "Visible source spelling",
            "before_sha256": mechanical._sha(before.encode()),
            "after_sha256": mechanical._sha(after.encode()),
            "packet": identity, "report": identity, "source_render": identity,
        }
    result, diagnostics = mechanical._aligned_page_candidate(1, packet, None, ledger)
    mechanical._validate_candidate_page(result)
    return result, diagnostics


def test_corrupt_native_selects_real_ocr_preimage_and_retains_all_views(tmp_path):
    page, diagnostics = candidate(tmp_path, ["garbled\x01", "Readable", "Readable"])
    assert not diagnostics and page["markdown"] == "Readable"
    row = page["entries"][0]
    assert row["chosen_view"] == VIEWS[1]
    assert row["source_text_sha256"] == mechanical._sha(b"Readable")
    assert row["unit"]["source_offsets"] == [{"view": VIEWS[1], "raw_index": 0, "field": "text", "source_sha256": mechanical._sha(b"Readable"), "start": 0, "end": 8}]
    assert len(row["source_keys"]) == 3
    assert row["alternatives"][0]["blocks"][0]["text"] == "garbled\x01"
    assert row["text_selection"]["view_status"][VIEWS[0]] == "tainted"


@pytest.mark.parametrize("native,raster", [("WESTERNUNION", "WESTERNUNION"), ("garbled\x01", "different")])
def test_reviewed_full_block_correction_precedes_agreement(tmp_path, native, raster):
    page, diagnostics = candidate(tmp_path, [native, "WESTERNUNION", raster], correction=("WESTERNUNION", "WESTERN UNION"))
    assert not diagnostics and page["markdown"] == "WESTERN UNION"
    row = page["entries"][0]
    assert row["source_text_sha256"] == mechanical._sha(b"WESTERNUNION")
    assert row["text_selection"]["output_sha256"] == mechanical._sha(b"WESTERN UNION")
    assert row["unit"]["source_offsets"][0]["end"] == 12


@pytest.mark.parametrize("options,code", [({"semantic": True}, "semantic_conflict"), ({"assets": True}, "asset_difference")])
def test_reviewed_correction_does_not_clear_orthogonal_hold(tmp_path, options, code):
    page, diagnostics = candidate(tmp_path, ["garbled\x01", "before", "before"], correction=("before", "after"), **options)
    assert page["markdown"] == "" and diagnostics[0]["code"] == code
    assert page["entries"][0]["bound_correction"]["after"] == "after"


def test_disagreeing_ocr_remains_held(tmp_path):
    page, diagnostics = candidate(tmp_path, ["garbled\x01", "left", "right"])
    assert not page["markdown"] and diagnostics[0]["code"] == "ocr_text_disagreement"


@pytest.mark.parametrize("mutation", ["offset", "alternative", "output", "contributor", "markdown", "chosen"])
def test_recovery_provenance_mutations_rejected(tmp_path, mutation):
    page, _ = candidate(tmp_path, ["garbled\x01", "Readable", "Readable"])
    bad = copy.deepcopy(page)
    row = bad["entries"][0]
    if mutation == "offset": row["unit"]["source_offsets"][0]["source_sha256"] = "A" * 64
    elif mutation == "alternative": row["alternatives"][0]["blocks"][0]["text"] = "forged"
    elif mutation == "output": row["text_selection"]["output_sha256"] = "A" * 64
    elif mutation == "contributor": row["text_selection"]["view_status"][VIEWS[0]] = "corroborating"
    elif mutation == "markdown": bad["markdown"] = "invented"
    elif mutation == "chosen": row["chosen_view"] = VIEWS[0]
    with pytest.raises(ValueError): mechanical._validate_candidate_page(bad)


def test_dropping_complete_source_component_and_resealing_cannot_hide_loss(tmp_path):
    blocks = {view: [_block(0, "", kind="text")] for view in VIEWS}
    root = _stage04(tmp_path / "run", {1: _packet(1, blocks)})
    output = tmp_path / "candidate"
    report = mechanical.compile_mechanical_draft(root, output, authority_validator=lambda _: None)
    page_path = output / "pages/page-001.json"
    page = json.loads(page_path.read_text())
    assert page["entries"][0]["disposition"] == "excluded_empty"
    page["entries"] = []
    page_path.write_text(json.dumps(page), encoding="utf-8")
    report["pages"][0]["candidate"].update(mechanical._identity(page_path))
    report["manifest_sha256"] = mechanical._sha(mechanical._canonical({k:v for k,v in report.items() if k != "manifest_sha256"}))
    with pytest.raises(ValueError, match="conserve all packet source keys"):
        mechanical._validate_generated_draft(report, output)
