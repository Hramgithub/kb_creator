from __future__ import annotations

import importlib.util
import os
import re
from pathlib import Path
import sys

import pytest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "build_innsmouth_master_en_packet7_user_review_successor.py"
)
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location(
    "innsmouth_packet7_user_review_successor", SCRIPT
)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


@pytest.fixture(scope="module")
def predecessor() -> Path:
    raw = os.environ.get("NRI_INNSMOUTH_PACKET7_R2")
    if not raw:
        pytest.skip("NRI_INNSMOUTH_PACKET7_R2 is required for the real Packet 7 test")
    return Path(raw)


@pytest.fixture(scope="module")
def data(predecessor: Path) -> dict[str, bytes]:
    return builder.read_predecessor(predecessor)


@pytest.fixture(scope="module")
def result(data: dict[str, bytes]) -> dict:
    return builder.build_twice(data)


def test_real_predecessor_identity_and_two_build_determinism(data, result):
    assert len(data["MASTER_EN.md"]) == 132097
    assert builder.sha256(data["MASTER_EN.md"]) == builder.EXPECTED_PREDECESSOR["MASTER_EN.md"][1]
    assert result == builder.build_once(data)
    assert result["counts"]["operations"] == 56


def test_every_ordinary_reference_replaces_only_page_token(data, result):
    reconstruction = __import__("json").loads(data["MASTER_EN.reconstruction.json"])
    accepted = reconstruction["projection"]["operations"]["internal_reference_operations"]
    ordinary = [row for row in accepted if row["target_kind"] != "HANDOUT"]
    assert len(ordinary) == 33
    expected = []
    for row in ordinary:
        replacement = f"[link](#{row['canonical_anchor']})"
        value, count = builder.PAGE_TOKEN.subn(replacement, row["before_utf8"])
        assert count == 1
        expected.append(value)
    output = result["markdown"].decode("utf-8")
    for value in expected:
        assert value in output
    assert output.count("[link](#nri-") == 33


def test_fire_station_seed_case_and_outer_parenthesis(result):
    text = result["markdown"].decode("utf-8")
    expected = "to Zadok Allen (The Fire Station, [link](#nri-h-1b70234c4ece0af6255492e8))."
    assert text.count(expected) == 1
    assert "([The Fire Station](#nri-h-1b70234c4ece0af6255492e8)." not in text


def test_handout_keeps_visible_number_and_external_pages_remain(result):
    text = result["markdown"].decode("utf-8")
    assert text.count("See [**Handout 1-b**](#nri-h-f8e3b2764c3b8f24c4c83bfa)") == 1
    assert len(builder.PAGE_TOKEN.findall(text)) == 3
    assert text.count("Call of Cthulhu: Keeper Rulebook.") == 3


def test_all_eleven_major_toc_groups_are_linked(result):
    markdown = result["markdown"]
    toc = markdown[markdown.index(b"# CONTENTS"):markdown.index(b"<!-- mineru-page: 4 -->")]
    for label, page, token in builder.SECTION_GROUPS:
        assert f"## [{label}](#nri-h-{token})".encode() in toc
        assert f"## {label} {page}".encode() not in toc
    assert len(re.findall(rb"\]\(#([^\)]+)\)", toc)) == 45


def test_all_fragments_resolve_and_structure_is_conserved(result):
    markdown = result["markdown"]
    ids = re.findall(rb'<a id="([^"]+)"></a>', markdown)
    fragments = re.findall(rb"\]\(#([^\)]+)\)", markdown)
    assert len(ids) == len(set(ids)) == 50
    assert len(fragments) == 79
    assert not (set(fragments) - set(ids))
    assert len(re.findall(rb"(?m)^#{1,6} ", markdown)) == 155
    assert markdown.count(b"<table>") == 51
    assert len(re.findall(rb"!?\[[^\]]*\]\(assets/[^\)]+\)", markdown)) == 38


def test_preflight_build_does_not_mutate_predecessor(predecessor, data, result):
    after = builder.read_predecessor(predecessor)
    assert after == data
    assert result["roots"]["markdown"]["sha256"] == builder.sha256(result["markdown"])


def test_confined_publication_and_occupied_target_fail(predecessor, tmp_path):
    target = tmp_path / "candidate"
    receipt = builder.publish_once(predecessor, target)
    assert receipt["file_count"] == 41
    assert receipt["asset_count"] == 38
    assert target.is_dir()
    assert not Path(str(target) + ".stage").exists()
    with pytest.raises(ValueError, match="E_TARGET_EXISTS"):
        builder.publish_once(predecessor, target)
