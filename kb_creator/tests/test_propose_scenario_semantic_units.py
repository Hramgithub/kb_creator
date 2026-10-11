import json

import pytest

from kb_creator.scripts.propose_scenario_semantic_units import candidates, write_evidence


def test_proposer_writes_absent_closed_review_evidence(tmp_path):
    pages = tmp_path / "pages"; pages.mkdir()
    (pages / "page-001.md").write_text("# APPEARANCE\ntext\n## Keeper's Notes\ntext\n| A | B |\n", encoding="utf-8")
    (pages / "page-002.md").write_text("## APPEARANCE\nPossible Vision from The Sight\n", encoding="utf-8")
    (pages / "page-123.md").write_text("# APPEARANCE\nadvert\n", encoding="utf-8")
    output = tmp_path / "evidence"
    closure = write_evidence(pages, output, "test-reviewer")
    assert closure["unresolved_blocking_candidates"] == []
    assert closure["unresolved_blocking_count"] == 0
    assert closure["excluded_audit_pages"] == [123, 124]
    assert set(path.name for path in output.iterdir()) == {"semantic_unit_candidates.json", "semantic_unit_review.json", "semantic_unit_review.html", "closure_report.json"}
    review = json.loads((output / "semantic_unit_review.json").read_text(encoding="utf-8"))
    assert review["reviewer"] == "test-reviewer"
    assert {row["decision"] for row in review["decisions"]} >= {"confirm", "reject", "adjusted_boundary"}
    with pytest.raises(FileExistsError):
        write_evidence(pages, output, "test-reviewer")


def test_geometry_repetition_and_repeat_build_equality(tmp_path):
    pages = tmp_path / "pages"; pages.mkdir()
    for number in (1, 2): (pages / f"page-{number:03d}.md").write_text("## APPEARANCE\n", encoding="utf-8")
    rows = candidates(pages)
    assert rows[0]["confidence"] == "high" and rows[0]["bbox"] == [0.0, 0.0, 1.0, 1.0]
    first, second = tmp_path / "a", tmp_path / "b"
    write_evidence(pages, first, "reviewer"); write_evidence(pages, second, "reviewer")
    assert (first / "semantic_unit_candidates.json").read_bytes() == (second / "semantic_unit_candidates.json").read_bytes()


def test_six_pregen_pairs_are_explicit_family_coverage(tmp_path):
    pages = tmp_path / "pages"; pages.mkdir()
    for number in range(110, 122): (pages / f"page-{number:03d}.md").write_text("form\n", encoding="utf-8")
    output = tmp_path / "evidence"
    closure = write_evidence(pages, output, "reviewer")
    assert closure["required_family_coverage"]["pregen_page_pairs"] == 6
    assert sum(row["family"] == "pregen_character_sheet_pair" for row in candidates(pages)) == 6
