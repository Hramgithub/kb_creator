import json
from pathlib import Path

import pytest

from kb_creator.pipeline.identity import file_identity, sha256_bytes
from kb_creator.pipeline.source_observation_binding import ObservationBindingError, bind_observations


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def fixture(tmp_path, transcript="the ending", reader="prefix the ending"):
    source = tmp_path / "source.pdf"
    source.write_bytes(b"immutable source fixture")
    run, drafts = tmp_path / "run", tmp_path / "drafts"
    write(run / "run.json", {"source": file_identity(source)})
    for page in (1, 2):
        packet = {"source_page": page, "views": {
            "original_pipeline_txt": {"blocks": [{"raw_index": 4, "text": "encoded raw", "bbox": [1, 2, 3, 4]}]},
            "original_pipeline_ocr": {"blocks": [{"raw_index": 5, "text": reader if page == 1 else "other"}]}}}
        write(run / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json", packet)
        png = run / f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03d}.png"
        png.parent.mkdir(parents=True, exist_ok=True)
        png.write_bytes(b"source image fixture")
        write(drafts / f"pages/page-{page:03d}.json", {"source_page": page, "markdown": reader if page == 1 else "other",
              "selected_blocks": [{"view": "original_pipeline_ocr", "raw_index": 5, "purpose": "text"}]})
    observations = tmp_path / "observations.json"
    write(observations, {"observations": [{"source_page": 2,
          "source_unit": {"view": "original_pipeline_txt", "raw_index": 4, "text_sha256": "WRONG"},
          "source_transcription": transcript, "reader_character_span": [999, 1000],
          "reader_exact_occurrences": 1, "state": "approved", "reviewer": "fixture"}]})
    return {"run_root": run, "source_pdf": source, "drafts_root": drafts, "observations_path": observations}


def test_recomputes_full_match_and_identities_in_previous_reader_page(tmp_path):
    args = fixture(tmp_path)
    row = bind_observations(**args)["observations"][0]
    assert row["state"] == "exact_reader_candidate"
    assert row["reader_page"] == 1 and row["reader_character_span"] == [7, 17]
    assert row["source_unit"]["text_sha256"] == sha256_bytes(b"encoded raw")
    assert row["source_transcription_sha256"] == sha256_bytes(b"the ending")
    assert row["selected_raw_exact_matches"] == [{"view": "original_pipeline_ocr", "raw_index": 5}]
    assert row["reader_draft"]["sha256"] == file_identity(args["drafts_root"] / "pages/page-001.json")["sha256"]


@pytest.mark.parametrize("transcript,reader,reason", [
    ("the ending missing", "prefix the ending", "no_complete_reader_match"),
    ("aa", "aaa", "ambiguous_reader_match"),
    ("girl’s", "girl's", "no_complete_reader_match"),
])
def test_partial_overlapping_and_punctuation_mismatches_are_held(tmp_path, transcript, reader, reason):
    row = bind_observations(**fixture(tmp_path, transcript, reader))["observations"][0]
    assert row["state"] == "held" and row["reason"] == reason
    assert row["reader_character_span"] is None


def test_source_byte_drift_is_rejected(tmp_path):
    args = fixture(tmp_path)
    args["source_pdf"].write_bytes(b"changed source")
    with pytest.raises(ObservationBindingError, match="source PDF"):
        bind_observations(**args)


def test_reader_match_alone_does_not_prove_selected_canonical_mapping(tmp_path):
    args = fixture(tmp_path)
    p = args["drafts_root"] / "pages/page-001.json"
    value = json.loads(p.read_text()); value["selected_blocks"] = []; write(p, value)
    row = bind_observations(**args)["observations"][0]
    assert row["reason"] == "canonical_mapping_pending" and row["state"] == "held"
