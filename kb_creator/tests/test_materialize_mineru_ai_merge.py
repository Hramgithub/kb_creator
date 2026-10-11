import copy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from kb_creator.scripts import materialize_mineru_ai_merge as materializer_module
from kb_creator.scripts.materialize_mineru_ai_merge import DECISION_SCHEMA, _exact_nested_heading, _is_title, _prevalidated_reference_proof_keys, _resolved_image_heading_overlap, _resolved_title_to_text_downgrade, _validated_v2_title_role, materialize
from kb_creator.pipeline.semantic_structure import (
    SemanticStructureError, collect_split_structure_proof_keys,
    validate_semantic_structure,
)


def _write(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _fixture(tmp_path, *, unresolved=False):
    raw = tmp_path / "raw"; bundle = tmp_path / "bundle"; decisions = tmp_path / "decisions"
    views = {}
    for view in ("original_hybrid", "original_pipeline_ocr", "raster_hybrid"):
        root = raw / "runs" / view / "parsed"; (root / "images").mkdir(parents=True)
        (root / "images" / "a.jpg").write_bytes(b"same-bytes")
        (root / "images" / "b.jpg").write_bytes(b"same-bytes")
        content = root / "book_content_list.json"; content.write_text("[]", encoding="utf-8")
        views[view] = {"artifacts": {"content_list": str(content)}, "blocks": []}
    views["original_hybrid"]["blocks"] = [
        {"raw_index": 0, "source_page": 1, "type": "text", "bbox": [0, 0, 1, 1], "text": "A", "assets": ["images/a.jpg", "images/b.jpg"]},
        {"raw_index": 1, "source_page": 2, "type": "image", "bbox": [0, 0, 1, 1], "text": "", "assets": ["images/a.jpg"]},
    ]
    _write(raw / "comparison" / "comparison.json", {"views": views})
    pages = bundle / "merge_packets" / "pages"
    index = []
    for page, role in ((1, "front"), (2, "map")):
        packet = {"source_page": page, "semantic_role": role, "views": {view: {"blocks": [block for block in views[view]["blocks"] if block["source_page"] == page]} for view in views}}
        _write(pages / f"page-{page:03d}.json", packet)
        index.append({"source_page": page, "semantic_role": role, "priority_score": 0, "packet": f"pages/page-{page:03d}.json"})
    _write(bundle / "merge_packets" / "merge_index.json", {"by_source_page": index, "by_priority": index})
    one = {"schema": DECISION_SCHEMA, "source_page": 1, "semantic_role": "front", "overlay_preference": "original_hybrid", "selected_blocks": [{"view": "original_hybrid", "raw_index": 0, "purpose": "text"}], "markdown": "![cover]({{asset:cover.jpg}})\n![copy]({{asset:cover-copy.jpg}})", "assets": [{"view": "original_hybrid", "source_path": "images/a.jpg", "logical_name": "cover.jpg", "placement": "full_width"}, {"view": "original_hybrid", "source_path": "images/b.jpg", "logical_name": "cover-copy.jpg", "placement": "inline"}], "unresolved": ["needs human check"] if unresolved else [], "review": {"visual_reviewed": True, "notes": ""}}
    two = {"schema": DECISION_SCHEMA, "source_page": 2, "semantic_role": "map", "overlay_preference": "original_hybrid", "selected_blocks": [{"view": "original_hybrid", "raw_index": 1, "purpose": "visual"}], "markdown": "", "assets": [{"view": "original_hybrid", "source_path": "images/a.jpg", "logical_name": "map.jpg", "placement": "reference_only"}], "unresolved": [], "review": {"visual_reviewed": True, "notes": ""}}
    _write(decisions / "page-001.json", one); _write(decisions / "page-002.json", two)
    return bundle, raw, decisions


def test_happy_path_orders_markers_preserves_decisions_and_deduplicates_assets(tmp_path):
    bundle, raw, decisions = _fixture(tmp_path)
    output = tmp_path / "output"; result = materialize(bundle, raw, decisions, output)
    assert result == {"status": "candidate_ready_for_reconstruction_qa", "pages": 2, "assets": 3, "unique_asset_bytes": 1}
    assert (output / "RECONSTRUCTED_EN.md").read_text(encoding="utf-8").startswith("<!-- source-page-001 -->")
    assert "<!-- source-page-002 -->" in (output / "RECONSTRUCTED_EN.md").read_text(encoding="utf-8")
    assert (output / "decisions" / "page-001.json").read_bytes() == (decisions / "page-001.json").read_bytes()
    assets = json.loads((output / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))["assets"]
    assert len({row["stored_path"] for row in assets}) == 1
    stored = assets[0]["stored_path"]
    assert f"../{stored}" in (output / "pages" / "page-001.md").read_text(encoding="utf-8")
    assert stored in (output / "RECONSTRUCTED_EN.md").read_text(encoding="utf-8")


def test_extensionless_logical_asset_uses_resolved_source_suffix(tmp_path):
    bundle, raw, decisions = _fixture(tmp_path)
    for path in decisions.glob("page-*.json"):
        decision = json.loads(path.read_text(encoding="utf-8"))
        for asset in decision["assets"]:
            old = asset["logical_name"]
            asset["logical_name"] = Path(old).stem
            decision["markdown"] = decision["markdown"].replace(old, asset["logical_name"])
        _write(path, decision)
    output = tmp_path / "output"
    materialize(bundle, raw, decisions, output)
    manifest = json.loads((output / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))
    assert all(row["stored_path"].endswith(".jpg") for row in manifest["assets"])
    rendered = (output / "RECONSTRUCTED_EN.md").read_text(encoding="utf-8")
    assert "assets/" in rendered and ".jpg)" in rendered


def test_compact_block_boundary_removes_only_declared_heading_separator(tmp_path):
    bundle, raw, decisions = _fixture(tmp_path)
    decision_path = decisions / "page-001.json"
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    stat_lines = [
        "STR 50 CON 55 SIZ 50 INT 85 POW 60  ",
        "DEX 55 APP 55 EDU 90 SAN varies HP 10  ",
        "Damage bonus: none.  ",
        "Build: 0  ",
        "Move: 8  ",
        "ATTACKS  ",
        "Fighting (Brawl) 50% (25/10): Dodge 30% (15/6)  ",
        "Skills: Listen 35%, Spot Hidden 45%.  ",
        "Nationality: American  ",
        "Age: varies.  ",
        "Spells: none.",
    ]
    heading = "## HUMAN RESISTANCE (Police, Test Subjects, Residents of Aniak)"
    decision["markdown"] += (
        "\n\nIntroduction.\n\n" + heading + "\n\n" + "\n".join(stat_lines)
    )
    decision["block_boundaries"] = [
        {
            "style": "compact",
            "heading_line": heading,
            "first_body_line": stat_lines[0],
        }
    ]
    _write(decision_path, decision)
    decision_bytes = decision_path.read_bytes()

    output = tmp_path / "output"
    materialize(bundle, raw, decisions, output)

    expected = heading + "\n" + "\n".join(stat_lines)
    for path in (output / "pages/page-001.md", output / "RECONSTRUCTED_EN.md"):
        rendered = path.read_text(encoding="utf-8")
        assert expected in rendered
        assert heading + "\n\n" + stat_lines[0] not in rendered
        assert sum(line.endswith("  ") for line in stat_lines) == 10
    assert (output / "decisions/page-001.json").read_bytes() == decision_bytes


@pytest.mark.parametrize(
    ("boundaries", "message"),
    [
        ([], "nonempty list"),
        ([{"style": "dense", "heading_line": "## Stats", "first_body_line": "STR 50"}], "unsupported"),
        ([{"style": "compact", "heading_line": "Stats", "first_body_line": "STR 50"}], "ATX heading"),
        ([{"style": "compact", "heading_line": "## Missing", "first_body_line": "STR 50"}], "match exactly once"),
        ([{"style": "compact", "heading_line": "## Stats", "first_body_line": "STR 51"}], "must match exactly one"),
    ],
)
def test_compact_block_boundary_is_exact_and_fail_closed(tmp_path, boundaries, message):
    bundle, raw, decisions = _fixture(tmp_path)
    decision_path = decisions / "page-001.json"
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["markdown"] = "## Stats\n\nSTR 50  \nDEX 40"
    decision["block_boundaries"] = boundaries
    _write(decision_path, decision)

    with pytest.raises(ValueError, match=message):
        materialize(bundle, raw, decisions, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_unknown_page_decision_extension_still_fails_closed(tmp_path):
    bundle, raw, decisions = _fixture(tmp_path)
    decision_path = decisions / "page-001.json"
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["layout"] = "compact"
    _write(decision_path, decision)

    with pytest.raises(ValueError, match="exact keys"):
        materialize(bundle, raw, decisions, tmp_path / "output")


@pytest.mark.parametrize("reparse_kind", ["symlink", "junction", "mount-point"])
def test_recursive_authority_tree_rejects_every_windows_reparse_kind(
    tmp_path, monkeypatch, reparse_kind
):
    root = tmp_path / "authority"
    nested = root / "nested"
    nested.mkdir(parents=True)
    (nested / "evidence.json").write_text("{}", encoding="utf-8")
    original_lstat = os.lstat

    def marked_lstat(path):
        observed = original_lstat(path)
        attributes = (
            materializer_module.FILE_ATTRIBUTE_REPARSE_POINT
            if Path(path).absolute() == nested.absolute()
            else 0
        )
        return SimpleNamespace(
            st_mode=observed.st_mode,
            st_file_attributes=attributes,
        )

    monkeypatch.setattr(materializer_module.os, "lstat", marked_lstat)
    with pytest.raises(ValueError, match="reparse point"):
        materializer_module._assert_tree_not_reparse(root)


def test_reparse_inspection_fails_closed_when_windows_attributes_are_unavailable(
    tmp_path, monkeypatch
):
    path = tmp_path / "authority"
    path.mkdir()
    observed = os.lstat(path)
    monkeypatch.setattr(materializer_module.os, "name", "nt")
    monkeypatch.setattr(
        materializer_module.os,
        "lstat",
        lambda unused: SimpleNamespace(st_mode=observed.st_mode),
    )
    with pytest.raises(ValueError, match="inspection is unavailable"):
        materializer_module._is_reparse(path)


def test_unresolved_and_empty_markdown_visual_page_are_preserved(tmp_path):
    bundle, raw, decisions = _fixture(tmp_path, unresolved=True)
    output = tmp_path / "output"; assert materialize(bundle, raw, decisions, output)["status"] == "candidate_needs_review"
    provenance = json.loads((output / "MERGE_PROVENANCE.json").read_text(encoding="utf-8"))
    assert provenance["pages"][0]["unresolved"] == ["needs human check"]
    assert (output / "pages" / "page-002.md").read_text(encoding="utf-8").strip() == "<!-- source-page-002 -->"


@pytest.mark.parametrize("mutation", ["bad_block", "escape_asset", "html_markdown", "empty_nonvisual", "unknown_placeholder", "missing_placeholder", "malformed_placeholder", "bare_placeholder", "empty_alt", "link_only"])
def test_closed_schema_selected_identity_and_path_content_rules_fail(tmp_path, mutation):
    bundle, raw, decisions = _fixture(tmp_path)
    decision = json.loads((decisions / "page-001.json").read_text(encoding="utf-8"))
    if mutation == "bad_block": decision["selected_blocks"][0]["raw_index"] = 99
    elif mutation == "escape_asset": decision["assets"][0]["source_path"] = "../escape.jpg"
    elif mutation == "html_markdown": decision["markdown"] = "<script>x</script>"
    elif mutation == "unknown_placeholder": decision["markdown"] = "![x]({{asset:unknown.jpg}})\n![copy]({{asset:cover-copy.jpg}})"
    elif mutation == "missing_placeholder": decision["markdown"] = "![cover]({{asset:cover.jpg}})"
    elif mutation == "malformed_placeholder": decision["markdown"] = "{{asset:cover.jpg"
    elif mutation == "bare_placeholder": decision["markdown"] = "{{asset:cover.jpg}}\n![copy]({{asset:cover-copy.jpg}})"
    elif mutation == "empty_alt": decision["markdown"] = "![]({{asset:cover.jpg}})\n![copy]({{asset:cover-copy.jpg}})"
    elif mutation == "link_only": decision["markdown"] = "[cover]({{asset:cover.jpg}})\n![copy]({{asset:cover-copy.jpg}})"
    else: decision["markdown"] = ""; decision["assets"][0]["placement"] = "inline"; decision["assets"] = decision["assets"][:1]
    _write(decisions / "page-001.json", decision)
    with pytest.raises(ValueError): materialize(bundle, raw, decisions, tmp_path / "output")


def test_nonempty_output_is_never_replaced(tmp_path):
    bundle, raw, decisions = _fixture(tmp_path)
    output = tmp_path / "output"; output.mkdir(); (output / "keep.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError): materialize(bundle, raw, decisions, output)
    assert (output / "keep.txt").read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize("reader_text", [
    "Lighthouse/Radio", "video editing/sound engineering", "and/or", "1/1D3", "1D8/4D10", "Ideology/Beliefs", "Guest Bedroom /Study", "Damage:\\*", "https://www.chaosium.com",
])
def test_markdown_classifier_allows_reader_slashes_dice_urls_and_escaped_source_text(tmp_path, reader_text):
    bundle, raw, decisions = _fixture(tmp_path)
    decision = json.loads((decisions / "page-001.json").read_text(encoding="utf-8"))
    decision["markdown"] += "\n" + reader_text
    _write(decisions / "page-001.json", decision)
    assert materialize(bundle, raw, decisions, tmp_path / "output")["pages"] == 2


@pytest.mark.parametrize("forbidden,reason", [
    ("C:\\Users\\name\\file.png", "device-specific Windows absolute path"), ("D:/NRI/file.md", "device-specific Windows absolute path"),
    ("\\\\server\\share\\file", "UNC absolute path"), ("/etc/passwd", "POSIX absolute path"), ("![x](/absolute/file.png)", "POSIX absolute path"),
    ("[x](/root)", "POSIX absolute path"), ("![x](/root)", "POSIX absolute path"),
    ("[x](</root>)", "POSIX absolute path"), ("[x]: /root", "POSIX absolute path"),
    ("<script>x</script>", "HTML tag"), ("<!-- source-page-001 -->", "generated source-page marker"),
])
def test_markdown_classifier_rejects_real_absolute_paths_tags_and_adds_page_context(tmp_path, forbidden, reason):
    bundle, raw, decisions = _fixture(tmp_path)
    decision = json.loads((decisions / "page-001.json").read_text(encoding="utf-8"))
    decision["markdown"] += "\n" + forbidden
    _write(decisions / "page-001.json", decision)
    with pytest.raises(ValueError, match=r"page-001\.json: .*" + reason):
        materialize(bundle, raw, decisions, tmp_path / "output")


def test_duplicate_valid_image_use_and_reference_only_absence_are_allowed(tmp_path):
    bundle, raw, decisions = _fixture(tmp_path)
    decision = json.loads((decisions / "page-001.json").read_text(encoding="utf-8"))
    decision["markdown"] += "\n![cover again]({{asset:cover.jpg}})"
    _write(decisions / "page-001.json", decision)
    output = tmp_path / "output"; materialize(bundle, raw, decisions, output)
    page = (output / "pages" / "page-001.md").read_text(encoding="utf-8")
    root = (output / "RECONSTRUCTED_EN.md").read_text(encoding="utf-8")
    assert page.count("../assets/") == 3 and root.count("assets/") == 3
    assert (output / "pages" / "page-002.md").read_text(encoding="utf-8").strip() == "<!-- source-page-002 -->"


def test_selected_title_requires_heading_or_explicit_reviewed_override(tmp_path):
    bundle, raw, decisions = _fixture(tmp_path)
    comparison = json.loads((raw / "comparison" / "comparison.json").read_text(encoding="utf-8"))
    comparison["views"]["original_hybrid"]["blocks"][0]["semantic_evidence"] = {"text_level": 2}
    _write(raw / "comparison" / "comparison.json", comparison)
    packet = json.loads((bundle / "merge_packets" / "pages" / "page-001.json").read_text(encoding="utf-8"))
    packet["views"]["original_hybrid"]["blocks"][0]["semantic_evidence"] = {"text_level": 2}
    _write(bundle / "merge_packets" / "pages" / "page-001.json", packet)
    with pytest.raises(ValueError, match="silently downgraded"):
        materialize(bundle, raw, decisions, tmp_path / "blocked")
    decision = json.loads((decisions / "page-001.json").read_text(encoding="utf-8"))
    decision["markdown"] += "\n## A"
    _write(decisions / "page-001.json", decision)
    assert materialize(bundle, raw, decisions, tmp_path / "accepted")["pages"] == 2
    bundle, raw, decisions = _fixture(tmp_path / "override")
    comparison = json.loads((raw / "comparison" / "comparison.json").read_text(encoding="utf-8"))
    comparison["views"]["original_hybrid"]["blocks"][0]["semantic_evidence"] = {"text_level": 2}
    _write(raw / "comparison" / "comparison.json", comparison)
    packet = json.loads((bundle / "merge_packets" / "pages" / "page-001.json").read_text(encoding="utf-8"))
    packet["views"]["original_hybrid"]["blocks"][0]["semantic_evidence"] = {"text_level": 2}
    _write(bundle / "merge_packets" / "pages" / "page-001.json", packet)
    decision = json.loads((decisions / "page-001.json").read_text(encoding="utf-8"))
    decision["review"] = {"visual_reviewed": False, "notes": "title override: A; reason: card label reviewed"}
    _write(decisions / "page-001.json", decision)
    with pytest.raises(ValueError, match="silently downgraded"):
        materialize(bundle, raw, decisions, tmp_path / "unreviewed-override")
    decision["review"] = {"visual_reviewed": True, "notes": "title override: A; reason: card label reviewed"}
    _write(decisions / "page-001.json", decision)
    assert materialize(bundle, raw, decisions, tmp_path / "reviewed-override")["pages"] == 2


def test_title_evidence_conflict_requires_closed_confirmation_and_exact_correction(tmp_path):
    bundle, raw, decisions = _fixture(tmp_path)
    source, reader = "THE ENLIGHTENEDWEBSITE", "THE ENLIGHTENED WEBSITE"
    comparison = json.loads((raw / "comparison" / "comparison.json").read_text(encoding="utf-8"))
    comparison["views"]["original_hybrid"]["blocks"][0].update({
        "text": source,
        "semantic_evidence": {"v2_title": True, "markdown_heading": True, "middle_title": False},
    })
    _write(raw / "comparison" / "comparison.json", comparison)
    packet_path = bundle / "merge_packets" / "pages" / "page-001.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["views"]["original_hybrid"]["blocks"][0].update({
        "text": source,
        "semantic_evidence": {"v2_title": True, "markdown_heading": True, "middle_title": False},
    })
    _write(packet_path, packet)
    decision_path = decisions / "page-001.json"
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["selected_blocks"][0]["purpose"] = "structure"
    decision["markdown"] += f"\n## {reader}"
    _write(decision_path, decision)
    with pytest.raises(ValueError, match="title_evidence_confirmation_required"):
        materialize(bundle, raw, decisions, tmp_path / "missing-confirmation")
    decision["review"] = {"visual_reviewed": True, "notes": (
        f"text correction: {source} -> {reader}; reason: visual\n"
        f"title evidence confirmation: original_hybrid:0 -> {reader}; reason: visual"
    )}
    _write(decision_path, decision)
    assert materialize(bundle, raw, decisions, tmp_path / "confirmed") ["pages"] == 2


def test_selected_image_cannot_be_reclassified_as_body_text_and_conflicts_are_selection_scoped(tmp_path):
    bundle, raw, decisions = _fixture(tmp_path / "conflict")
    decision = json.loads((decisions / "page-002.json").read_text(encoding="utf-8"))
    decision["selected_blocks"][0]["purpose"] = "text"
    _write(decisions / "page-002.json", decision)
    with pytest.raises(ValueError, match="image block"):
        materialize(bundle, raw, decisions, tmp_path / "image-blocked")
    bundle, raw, decisions = _fixture(tmp_path)
    comparison = json.loads((raw / "comparison" / "comparison.json").read_text(encoding="utf-8"))
    comparison["pairwise"] = {"original_hybrid__vs__raster_hybrid": {"semantic_conflicts": [{"kind": "title_to_text_downgrade", "left_raw_index": 77, "right_raw_index": 77, "resolution": None}]}}
    _write(raw / "comparison" / "comparison.json", comparison)
    assert materialize(bundle, raw, decisions, tmp_path / "unselected-conflict")["pages"] == 2
    comparison["pairwise"]["original_hybrid__vs__raster_hybrid"]["semantic_conflicts"][0]["left_raw_index"] = 0
    _write(raw / "comparison" / "comparison.json", comparison)
    with pytest.raises(ValueError, match="selected block has an unresolved"):
        materialize(bundle, raw, decisions, tmp_path / "selected-conflict")


@pytest.mark.parametrize("mutation", ["missing_heading", "unreviewed", "missing_override", "other_kind", "ambiguous_selection"])
def test_title_to_text_downgrade_requires_exact_reviewed_heading_override(tmp_path, mutation):
    bundle, raw, decisions = _fixture(tmp_path)
    comparison = json.loads((raw / "comparison" / "comparison.json").read_text(encoding="utf-8"))
    conflict = {"kind": "title_to_text_downgrade", "left_raw_index": 0, "right_raw_index": 77, "resolution": None}
    comparison["pairwise"] = {"original_hybrid__vs__raster_hybrid": {"semantic_conflicts": [conflict]}}
    _write(raw / "comparison" / "comparison.json", comparison)
    decision_path = decisions / "page-001.json"
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["markdown"] += "\n## A"
    decision["review"] = {"visual_reviewed": True, "notes": "title override: A; reason: raster title was visually confirmed"}
    if mutation == "missing_heading":
        decision["markdown"] = decision["markdown"].replace("\n## A", "\nA")
    elif mutation == "unreviewed":
        decision["review"]["visual_reviewed"] = False
    elif mutation == "missing_override":
        decision["review"]["notes"] = "title override: A; rationale only"
    elif mutation == "other_kind":
        conflict["kind"] = "image_heading_overlap"
    elif mutation == "ambiguous_selection":
        second = {"raw_index": 2, "source_page": 1, "type": "text", "bbox": [0, 0, 1, 1], "text": "A", "assets": []}
        comparison["views"]["raster_hybrid"]["blocks"].append(second)
        packet_path = bundle / "merge_packets" / "pages" / "page-001.json"
        packet = json.loads(packet_path.read_text(encoding="utf-8")); packet["views"]["raster_hybrid"]["blocks"].append(second); _write(packet_path, packet)
        decision["selected_blocks"].append({"view": "raster_hybrid", "raw_index": 2, "purpose": "text"})
        conflict["right_raw_index"] = 2
    _write(raw / "comparison" / "comparison.json", comparison)
    _write(decision_path, decision)
    with pytest.raises(ValueError, match="selected block has an unresolved"):
        materialize(bundle, raw, decisions, tmp_path / mutation)


def test_title_to_text_downgrade_exact_reviewed_heading_override_materializes(tmp_path):
    bundle, raw, decisions = _fixture(tmp_path)
    comparison = json.loads((raw / "comparison" / "comparison.json").read_text(encoding="utf-8"))
    comparison["pairwise"] = {"original_hybrid__vs__raster_hybrid": {"semantic_conflicts": [{"kind": "title_to_text_downgrade", "left_raw_index": 0, "right_raw_index": 77, "resolution": None}]}}
    _write(raw / "comparison" / "comparison.json", comparison)
    decision_path = decisions / "page-001.json"; decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["markdown"] += "\n## A"
    decision["review"] = {"visual_reviewed": True, "notes": "title override: A; reason: raster title was visually confirmed"}
    _write(decision_path, decision)
    assert materialize(bundle, raw, decisions, tmp_path / "accepted")["pages"] == 2


def test_title_to_text_downgrade_accepts_only_exact_reviewed_blockquote_binding():
    markdown = "> Card\n> Enlightened in Life, Dignified in Death\n> Body"
    selected = [{"view": "original_pipeline_txt", "raw_index": 120, "block": {"text": "Enlightened in Life, Dignified in Death"}}]
    structure = {"units": [{
        "representation": "blockquote",
        "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 120}],
        "markdown_span": {"start_line": 1, "end_line": 3, "sha256": "unused-here"},
    }]}
    review = {
        "visual_reviewed": True,
        "notes": "title downgrade: Enlightened in Life, Dignified in Death; representation: blockquote; reason: source visual shows a subordinate italic card subtitle",
    }
    conflict = {"kind": "title_to_text_downgrade"}
    assert _resolved_title_to_text_downgrade(conflict, selected, markdown, review, structure)
    assert not _resolved_title_to_text_downgrade(conflict, selected, markdown, {**review, "visual_reviewed": False}, structure)
    assert not _resolved_title_to_text_downgrade(conflict, selected, markdown.replace("> Enlightened", "Enlightened"), review, structure)


def test_title_to_text_downgrade_accepts_only_exact_reviewed_semantic_span_binding():
    markdown = "### MIGO\nArmor: 0\nSkills: Dodge 35%"
    selected = [{"view": "original_pipeline_txt", "raw_index": 272, "block": {"text": "Armor: 0"}}]
    structure = {"units": [{
        "representation": "semantic_span",
        "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 272}],
        "markdown_span": {"start_line": 1, "end_line": 3, "sha256": "unused-here"},
    }]}
    review = {
        "visual_reviewed": True,
        "notes": "title downgrade: Armor: 0; representation: semantic_span; reason: source visual shows a statblock field",
    }
    conflict = {"kind": "title_to_text_downgrade"}
    assert _resolved_title_to_text_downgrade(conflict, selected, markdown, review, structure)
    assert not _resolved_title_to_text_downgrade(conflict, selected, markdown, {**review, "notes": review["notes"].replace("semantic_span", "blockquote")}, structure)
    assert not _resolved_title_to_text_downgrade(conflict, selected, markdown.replace("Armor: 0", "> Armor: 0"), review, structure)


@pytest.mark.parametrize("item_line", ["- The Romano Estate", "- **Demon of Pacaritambo**"])
def test_title_to_text_downgrade_accepts_only_exact_reviewed_source_bullet(item_line):
    source_item = item_line[2:].strip().strip("*")
    source_title = "● " + source_item
    selected = [{"view": "original_pipeline_txt", "raw_index": 110, "block": {"text": source_title}}]
    structure = {"units": [{
        "kind": "list", "representation": "unordered_list", "item_count": 1,
        "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 110}],
        "markdown_span": {"start_line": 1, "end_line": 1, "sha256": "unused"},
    }]}
    review = {"visual_reviewed": True, "notes": f"title downgrade: {source_title}; representation: unordered_list; reason: source bullet in reviewed enumeration"}
    assert _resolved_title_to_text_downgrade({"kind": "title_to_text_downgrade"}, selected, item_line, review, structure)
    for mutation in ("- Changed", "The Romano Estate"):
        assert not _resolved_title_to_text_downgrade({"kind": "title_to_text_downgrade"}, selected, mutation, review, structure)
    structure["units"][0]["markdown_span"]["end_line"] = 2
    assert not _resolved_title_to_text_downgrade({"kind": "title_to_text_downgrade"}, selected, "- The Romano Estate\n- Extra", review, structure)
    assert not _resolved_title_to_text_downgrade({"kind": "title_to_text_downgrade"}, selected, item_line, {**review, "visual_reviewed": False}, structure)
    structure["units"][0]["kind"] = "statblock"
    assert not _resolved_title_to_text_downgrade({"kind": "title_to_text_downgrade"}, selected, item_line, review, structure)


def test_exact_nested_heading_requires_reviewed_heading_unit_and_supported_parent():
    markdown = "> # THE ENLIGHTENED\n>\n> Body"
    structure = {"units": [
        {"id": "card", "representation": "blockquote"},
        {"id": "title", "kind": "heading", "representation": "atx_heading", "container_parent": "card", "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 119}], "markdown_span": {"start_line": 1, "end_line": 1}},
    ]}
    assert _exact_nested_heading(markdown, "THE ENLIGHTENED", structure, ("original_pipeline_txt", 119))
    markdown = "# THE ENLIGHTENED\nBody"
    structure["units"][0]["representation"] = "semantic_span"
    assert _exact_nested_heading(markdown, "THE ENLIGHTENED", structure, ("original_pipeline_txt", 119))
    structure["units"][0]["representation"] = "table"
    assert not _exact_nested_heading(markdown, "THE ENLIGHTENED", structure, ("original_pipeline_txt", 119))


def test_table_text_semantic_evidence_is_not_title_evidence():
    assert not _is_title({"semantic_evidence": {"v2_table_text": True}})
    assert _is_title({"semantic_evidence": {"v2_table_text": True, "v2_title": True}})


def test_image_heading_overlap_requires_exact_selected_role_evidence():
    conflict = {"kind": "image_heading_overlap"}
    structure_selected = [{"view": "original_pipeline_txt", "raw_index": 252, "block": {"_selection_purpose": "structure", "assets": ["images/stats.jpg"]}}]
    structure_decision = {
        "review": {"visual_reviewed": True}, "assets": [],
        "semantic_structure": {"units": [{"representation": "blockquote", "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 252}]}]},
    }
    assert _resolved_image_heading_overlap(conflict, structure_selected, structure_decision)
    structure_decision["semantic_structure"]["units"][0]["representation"] = "semantic_span"
    assert _resolved_image_heading_overlap(conflict, structure_selected, structure_decision)
    structure_decision["semantic_structure"]["units"][0]["representation"] = "atx_heading"
    assert not _resolved_image_heading_overlap(conflict, structure_selected, structure_decision)
    asset_selected = [{"view": "original_pipeline_txt", "raw_index": 301, "block": {"_selection_purpose": "asset", "assets": ["images/handout.jpg"]}}]
    asset_decision = {
        "review": {"visual_reviewed": True}, "semantic_structure": {"units": []},
        "assets": [{"view": "original_pipeline_txt", "source_path": "images/handout.jpg", "placement": "handout"}],
    }
    assert _resolved_image_heading_overlap(conflict, asset_selected, asset_decision)
    asset_decision["assets"][0]["placement"] = "reference_only"
    assert not _resolved_image_heading_overlap(conflict, asset_selected, asset_decision)


def _v2_split_structure_fixture():
    source = "THE NOTICE\nOrdinary introduction.\nBoxed note."
    lines = ["## THE NOTICE", "Ordinary introduction.", "> Boxed note."]
    page, view, raw_index = 7, "original_pipeline_txt", 109
    ref = {"view": view, "raw_index": raw_index}
    visual = {
        "path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-007.png",
        "bytes": 1,
        "sha256": "A" * 64,
    }

    def fragment(start, end):
        value = source[start:end]
        normalized = "".join(char for char in value.casefold() if char.isalnum())
        return {
            **ref,
            "source_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
            "normalized_sha256": hashlib.sha256(normalized.encode()).hexdigest().upper(),
            "start": start,
            "end": end,
            "fragment_sha256": hashlib.sha256(value.encode()).hexdigest().upper(),
        }

    def unit(identity, kind, representation, line, start, end):
        return {
            "id": identity,
            "kind": kind,
            "representation": representation,
            "source_blocks": [ref],
            "source_fragments": [fragment(start, end)],
            "markdown_span": {
                "start_line": line,
                "end_line": line,
                "sha256": hashlib.sha256(lines[line - 1].encode()).hexdigest().upper(),
            },
            "container_parent": None,
            "semantic_parent": None,
            "continuation_of": None,
            "heading_level": 2 if kind == "heading" else None,
            "item_count": None,
        }

    first = len("THE NOTICE\n")
    second = first + len("Ordinary introduction.\n")
    decision = {
        "source_page": page,
        "semantic_role": "body",
        "markdown": "\n".join(lines),
        "selected_blocks": [{**ref, "purpose": "structure"}],
        "assets": [],
        "review": {"visual_reviewed": True, "notes": ""},
        "semantic_structure": {
            "schema": "kb_creator.page_semantic_structure.v2",
            "profile": "reviewed_role_outline_and_partitions_v2",
            "role_contract": {"role": "body", "group_id": "notice"},
            "review": {"state": "complete", "visual": visual},
            "units": [
                unit("notice-heading", "heading", "atx_heading", 1, 0, first),
                unit("notice-intro", "label", "semantic_span", 2, first, second),
                unit("notice-box", "blockquote", "blockquote", 3, second, len(source)),
            ],
        },
    }
    packet = {"views": {view: {"blocks": [{"raw_index": raw_index, "type": "table", "text": source, "assets": []}]}}}
    return decision, packet, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}


def _v2_cover_label_title_fixture():
    source = "SE A MONSTER SUMMONING COVER-UP MART IN ’S BEACH"
    reader_lines = ["SEA MONSTER", "SUMMONING", "COVER-UP", "MARTIN’S BEACH"]
    page, view, raw_index = 63, "original_pipeline_txt", 1223
    ref = {"view": view, "raw_index": raw_index}
    visual = {
        "path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-063.png",
        "bytes": 1, "sha256": "A" * 64,
    }
    offsets = [
        (0, len("SE A MONSTER ")),
        (len("SE A MONSTER "), len("SE A MONSTER SUMMONING ")),
        (len("SE A MONSTER SUMMONING "), len("SE A MONSTER SUMMONING COVER-UP ")),
        (len("SE A MONSTER SUMMONING COVER-UP "), len(source)),
    ]

    def fragment(start, end):
        value = source[start:end]
        normalized = "".join(char for char in value.casefold() if char.isalnum())
        return {**ref, "source_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
                "normalized_sha256": hashlib.sha256(normalized.encode()).hexdigest().upper(),
                "start": start, "end": end,
                "fragment_sha256": hashlib.sha256(value.encode()).hexdigest().upper()}

    def unit(index, start, end):
        reader = reader_lines[index]
        return {"id": f"cover-label-{index}", "kind": "label", "representation": "semantic_span",
                "source_blocks": [ref], "source_fragments": [fragment(start, end)],
                "markdown_span": {"start_line": index + 1, "end_line": index + 1,
                                  "sha256": hashlib.sha256(reader.encode()).hexdigest().upper()},
                "container_parent": None, "semantic_parent": None, "continuation_of": None,
                "heading_level": None, "item_count": None}

    decision = {"source_page": page, "semantic_role": "body", "markdown": "\n".join(reader_lines),
                "selected_blocks": [{**ref, "purpose": "text"}], "assets": [],
                "review": {"visual_reviewed": True, "notes": "reviewed"},
                "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v2",
                    "profile": "reviewed_role_outline_and_partitions_v2",
                    "role_contract": {"role": "body", "group_id": "cover-labels"},
                    "review": {"state": "complete", "visual": visual},
                    "units": [unit(index, start, end) for index, (start, end) in enumerate(offsets)]}}
    packet = {"source_page": page, "views": {view: {"blocks": [{
        "raw_index": raw_index, "type": "text", "text": source, "assets": []
    }]}}}
    return decision, packet, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, source, ref


def test_title_guard_accepts_only_validated_ordered_complete_label_partitions():
    decision, packet, visuals, source, ref = _v2_cover_label_title_fixture()
    assert validate_semantic_structure({63: decision}, {63: packet}, visuals, required_pages=[63])["profile"] == "reviewed_role_outline_and_partitions_v2"
    assert _validated_v2_title_role(decision, packet, source, (ref["view"], ref["raw_index"]), set())

    reordered = copy.deepcopy(decision)
    reordered["semantic_structure"]["units"] = list(reversed(reordered["semantic_structure"]["units"]))
    assert not _validated_v2_title_role(reordered, packet, source, (ref["view"], ref["raw_index"]), set())
    for mutation in ("gap", "overlap", "duplicate", "malformed"):
        broken = copy.deepcopy(decision)
        units = broken["semantic_structure"]["units"]
        if mutation == "gap": units[1]["source_fragments"][0]["start"] += 1
        elif mutation == "overlap": units[1]["source_fragments"][0]["start"] -= 1
        elif mutation == "duplicate": units[1]["source_fragments"][0] = dict(units[0]["source_fragments"][0])
        else: units[1]["representation"] = "atx_heading"
        assert not _validated_v2_title_role(broken, packet, source, (ref["view"], ref["raw_index"]), set())


def test_title_guard_preserves_valid_heading_label_split_proof():
    source, page, view, raw_index = "THE NOTICE label", 70, "original_pipeline_txt", 70
    ref = {"view": view, "raw_index": raw_index}
    lines = ["## THE NOTICE", "label"]
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-070.png",
              "bytes": 1, "sha256": "A" * 64}

    def unit(identity, kind, representation, line, start, end):
        value = source[start:end]
        normalized = "".join(char for char in value.casefold() if char.isalnum())
        return {"id": identity, "kind": kind, "representation": representation, "source_blocks": [ref],
                "source_fragments": [{**ref, "source_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
                    "normalized_sha256": hashlib.sha256(normalized.encode()).hexdigest().upper(),
                    "start": start, "end": end, "fragment_sha256": hashlib.sha256(value.encode()).hexdigest().upper()}],
                "markdown_span": {"start_line": line, "end_line": line,
                                  "sha256": hashlib.sha256(lines[line - 1].encode()).hexdigest().upper()},
                "container_parent": None, "semantic_parent": None, "continuation_of": None,
                "heading_level": 2 if kind == "heading" else None, "item_count": None}

    split = len("THE NOTICE")
    decision = {"source_page": page, "semantic_role": "body", "markdown": "\n".join(lines),
                "selected_blocks": [{**ref, "purpose": "text"}], "assets": [],
                "review": {"visual_reviewed": True, "notes": "reviewed"},
                "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v2",
                    "profile": "reviewed_role_outline_and_partitions_v2",
                    "role_contract": {"role": "body", "group_id": "heading-label"},
                    "review": {"state": "complete", "visual": visual},
                    "units": [unit("heading", "heading", "atx_heading", 1, 0, split),
                              unit("label", "label", "semantic_span", 2, split, len(source))]}}
    packet = {"source_page": page, "views": {view: {"blocks": [{
        "raw_index": raw_index, "type": "text", "text": source, "assets": []
    }]}}}
    inventory = {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}
    assert validate_semantic_structure({page: decision}, {page: packet}, inventory, required_pages=[page])["profile"] == "reviewed_role_outline_and_partitions_v2"
    assert _validated_v2_title_role(decision, packet, source, (view, raw_index), {(page, view, raw_index)})


def test_title_guard_requires_the_sealed_stage05_empty_source_assertion():
    from kb_creator.pipeline.empty_text_assertions import RELATION, author_assertion
    from kb_creator.tests.test_empty_text_assertions import fixture as empty_fixture
    packet, decision, inventory, _ = empty_fixture()
    source, ref = "Unchanged body.", {"view": "original_pipeline_txt", "raw_index": 1}
    decision["markdown"] = "## Unchanged body.\n\n## Restored source heading?"
    empty = decision["semantic_structure"]["units"][0]
    empty["markdown_span"] = {"start_line": 3, "end_line": 3,
                              "sha256": hashlib.sha256("## Restored source heading?".encode()).hexdigest().upper()}
    decision["semantic_structure"]["units"].insert(0, {
        "id": "title", "kind": "heading", "representation": "atx_heading", "source_blocks": [ref],
        "source_fragments": [{**ref, "source_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
            "normalized_sha256": hashlib.sha256("unchangedbody".encode()).hexdigest().upper(), "start": 0,
            "end": len(source), "fragment_sha256": hashlib.sha256(source.encode()).hexdigest().upper()}],
        "markdown_span": {"start_line": 1, "end_line": 1,
                          "sha256": hashlib.sha256("## Unchanged body.".encode()).hexdigest().upper()},
        "container_parent": None, "semantic_parent": None, "continuation_of": None,
        "heading_level": 2, "item_count": None,
    })
    selector = {"assertion_id": "source-visible", "source_page": 1, "text": "Restored source heading?",
                "bbox": [100, 100, 800, 200], "relation": RELATION,
                "empty_source": {"view_id": "original_pipeline_txt", "raw_index": 0},
                "rationale": "Synthetic sealed Stage05 empty-source proof."}
    assertion = author_assertion(selector, packet, decision, inventory)
    assertions = {assertion["assertion_id"]: assertion}
    assert _validated_v2_title_role(decision, packet, source, (ref["view"], ref["raw_index"]), set(), assertions)
    assert not _validated_v2_title_role(decision, packet, source, (ref["view"], ref["raw_index"]), set())
    mutated = copy.deepcopy(assertion); mutated["placement"]["markdown_span"]["start"] += 1
    assert not _validated_v2_title_role(decision, packet, source, (ref["view"], ref["raw_index"]), set(), {mutated["assertion_id"]: mutated})


def test_image_heading_overlap_allows_only_validated_v2_split_structure_proof():
    decision, packet, visuals = _v2_split_structure_fixture()
    assert validate_semantic_structure({7: decision}, {7: packet}, visuals, required_pages=[7])["profile"] == "reviewed_role_outline_and_partitions_v2"
    proof_keys = collect_split_structure_proof_keys({7: decision}, {7: packet})
    assert proof_keys == {(7, "original_pipeline_txt", 109)}
    conflict = {"kind": "image_heading_overlap"}
    selected = [{"view": "original_pipeline_txt", "raw_index": 109, "block": {"_selection_purpose": "structure"}}]
    assert _resolved_image_heading_overlap(conflict, selected, decision, split_structure_proof_keys=proof_keys)
    assert not _resolved_image_heading_overlap(conflict, selected, decision, split_structure_proof_keys=set())
    assert not _resolved_image_heading_overlap(
        conflict,
        [{**selected[0], "block": {"_selection_purpose": "text"}}],
        decision,
        split_structure_proof_keys=proof_keys,
    )

    no_heading = copy.deepcopy(decision)
    no_heading["semantic_structure"]["units"][0]["representation"] = "semantic_span"
    no_heading["semantic_structure"]["units"][0]["kind"] = "label"
    no_heading["semantic_structure"]["units"][0]["heading_level"] = None
    assert not _resolved_image_heading_overlap(conflict, selected, no_heading, split_structure_proof_keys=proof_keys)

    unreviewed = copy.deepcopy(decision)
    unreviewed["review"]["visual_reviewed"] = False
    assert not _resolved_image_heading_overlap(conflict, selected, unreviewed, split_structure_proof_keys=proof_keys)

    legacy = copy.deepcopy(decision)
    legacy["semantic_structure"]["schema"] = "kb_creator.page_semantic_structure.v1"
    legacy["semantic_structure"].pop("profile")
    legacy["semantic_structure"].pop("role_contract")
    assert not _resolved_image_heading_overlap(conflict, selected, legacy, split_structure_proof_keys=proof_keys)


@pytest.mark.parametrize("mutation", ["missing_fragment", "missing_hash", "overlapping_fragment"])
def test_split_structure_proof_requires_validator_partition(mutation):
    decision, packet, visuals = _v2_split_structure_fixture()
    if mutation == "missing_fragment":
        decision["semantic_structure"]["units"][1]["source_fragments"] = []
        assert not collect_split_structure_proof_keys({7: decision}, {7: packet})
    elif mutation == "missing_hash":
        decision["semantic_structure"]["units"][2]["source_fragments"][0]["fragment_sha256"] = ""
    else:
        fragment = decision["semantic_structure"]["units"][2]["source_fragments"][0]
        fragment["start"] -= 1
    with pytest.raises(SemanticStructureError):
        validate_semantic_structure({7: decision}, {7: packet}, visuals, required_pages=[7])


def test_v3_or_missing_v4_audit_cannot_emit_split_structure_proof(tmp_path):
    decision, packet, visuals = _v2_split_structure_fixture()
    assert _prevalidated_reference_proof_keys(
        replay_run_root=tmp_path,
        fidelity_report={"schema": "kb_creator.mineru_ai_merge_fidelity.v3"},
        visual_manifest_path=tmp_path / "missing-visual-manifest.json",
        decisions={7: decision},
        packets={7: packet},
        decisions_root=tmp_path / "pages",
        geometry={},
    ) == (set(), set())
    assert _prevalidated_reference_proof_keys(
        replay_run_root=None,
        fidelity_report={"schema": "kb_creator.mineru_ai_merge_fidelity.v4"},
        visual_manifest_path=tmp_path / "missing-visual-manifest.json",
        decisions={7: decision},
        packets={7: packet},
        decisions_root=tmp_path / "pages",
        geometry={},
    ) == (set(), set())


def test_reference_only_image_heading_overlap_requires_trusted_proof_key():
    conflict = {"kind": "image_heading_overlap"}
    selected = [{"view": "original_pipeline_txt", "raw_index": 811, "block": {"_selection_purpose": "asset", "assets": ["images/p045-raw811.png"]}}]
    decision = {"source_page": 45, "review": {"visual_reviewed": True}, "assets": [{"view": "original_pipeline_txt", "source_path": "images/p045-raw811.png", "logical_name": "p045-raw811", "placement": "reference_only"}]}
    key = {(45, "original_pipeline_txt", 811, "p045-raw811", "child")}
    assert _resolved_image_heading_overlap(conflict, selected, decision, key)
    assert not _resolved_image_heading_overlap(conflict, selected, decision, set())
    decision["assets"][0]["placement"] = "inline"
    assert _resolved_image_heading_overlap(conflict, selected, decision, set())


def test_cross_view_image_heading_conflict_uses_each_explicit_side_for_selection(tmp_path):
    bundle, raw, decisions = _fixture(tmp_path)
    comparison = json.loads((raw / "comparison" / "comparison.json").read_text(encoding="utf-8"))
    comparison["pairwise"] = {"original_hybrid__vs__original_pipeline_ocr": {"semantic_conflicts": [{"kind": "image_heading_overlap", "asset_side": "right", "heading_side": "left", "asset_raw_index": 0, "heading_raw_index": 0, "resolution": None}]}}
    _write(raw / "comparison" / "comparison.json", comparison)
    with pytest.raises(ValueError, match="selected block has an unresolved"):
        materialize(bundle, raw, decisions, tmp_path / "cross-selected")
    comparison["pairwise"]["original_hybrid__vs__original_pipeline_ocr"]["semantic_conflicts"][0]["heading_raw_index"] = 77
    _write(raw / "comparison" / "comparison.json", comparison)
    assert materialize(bundle, raw, decisions, tmp_path / "cross-unselected")["pages"] == 2
