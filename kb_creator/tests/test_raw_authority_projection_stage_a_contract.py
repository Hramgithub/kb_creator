import json

import pytest

from kb_creator.pdf_raw import raw_authority_projection as stage_a
from kb_creator.pdf_raw import raw_interpreter_authority as legacy
from kb_creator.pdf_raw.raw_authority_projection import (
    project_stage_a_raw_authority,
    replay_stage_a_raw_authority,
)


@pytest.mark.parametrize("row", stage_a._FIXTURES)
def test_projection_replays_exact_canonical_inventory(row):
    authority = project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector)
    replay = replay_stage_a_raw_authority(
        row.fixture_id, row.pdf, row.profile, row.selector, authority.canonical_bytes()
    )
    artifact = json.loads(authority.canonical_bytes())
    assert replay.canonical_bytes() == authority.canonical_bytes()
    assert artifact["terminal_state"] == "provenance_complete_no_consumer"
    assert artifact["trailer_root"]["ref"] == [1, 0]
    assert artifact["page"]["page_tree_route"][-1] == artifact["page"]["page_ref"]
    assert artifact["inventory_sha256"]
    assert all("row_id" in item and "row_sha256" in item for item in artifact["streams"])


def test_legacy_registry_is_literal_immutable_and_matches_stage_a_leaves():
    assert type(legacy._ALLOWLIST_ROWS) is tuple
    assert len(legacy._ALLOWLIST_ROWS) == 2
    assert [row.fixture_id for row in stage_a._FIXTURES[:2]] == [row.fixture_id_raw for row in legacy._ALLOWLIST_ROWS]
    for stage_row, legacy_row in zip(stage_a._FIXTURES[:2], legacy._ALLOWLIST_ROWS, strict=True):
        assert (legacy_row.fixture_id_raw, legacy_row.pdf_raw, legacy_row.profile_raw, legacy_row.selector_raw) == (
            stage_row.fixture_id,
            stage_row.pdf,
            stage_row.profile,
            stage_row.selector,
        )
        assert legacy_row.fixture_binding_sha256 != stage_row.binding_sha256
        with pytest.raises(AttributeError):
            legacy_row.pdf_raw = b"mutated"
