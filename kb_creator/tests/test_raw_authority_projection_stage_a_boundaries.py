import copy

import pytest

from kb_creator.pdf_raw import raw_authority_projection as stage_a
from kb_creator.pdf_raw.errors import RawPdfError
from kb_creator.pdf_raw.raw_authority_projection import RawAtomProvenanceAuthorityV1, project_stage_a_raw_authority


def test_authority_is_closed_immutable_and_stage_a_is_not_a_consumer():
    row = stage_a._FIXTURES[0]
    authority = project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector)
    with pytest.raises(TypeError):
        RawAtomProvenanceAuthorityV1(object(), b"{}", {})
    with pytest.raises(AttributeError):
        authority._raw = b"mutated"
    with pytest.raises(TypeError):
        copy.copy(authority)
    assert authority.terminal_state == "provenance_complete_no_consumer"
    with pytest.raises(RawPdfError, match="^raw_interpreter_fixture_admission_forbidden$"):
        project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, b"{}")
