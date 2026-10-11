import json

import pytest

from kb_creator.pdf_raw import raw_authority_projection as stage_a
from kb_creator.pdf_raw.errors import RawPdfError
from kb_creator.pdf_raw.raw_authority_projection import project_stage_a_raw_authority, replay_stage_a_raw_authority


def test_replay_rejects_noncanonical_or_tampered_artifact_before_projection(monkeypatch):
    row = stage_a._FIXTURES[0]
    source = project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector)
    artifact = json.loads(source.canonical_bytes())
    artifact["fixture"]["id"] = "stage-a.flate-single-use.v1"
    tampered = json.dumps(artifact).encode("utf-8")
    monkeypatch.setattr(stage_a.RawPdfDocument, "open", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("must not open")))
    with pytest.raises(RawPdfError, match="^raw_interpreter_authority_blocked$"):
        replay_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector, tampered)
