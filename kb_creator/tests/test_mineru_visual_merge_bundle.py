import json
import os
from pathlib import Path
from types import SimpleNamespace
import shutil
import subprocess

import pytest
from PIL import Image

from kb_creator.scripts.build_mineru_visual_merge_bundle import (
    ROLES,
    TRIPTYCH_LABELS,
    VIEWS,
    _check_resume,
    _contract_roles,
    _packet_pairwise,
    build_contact_sheets,
    build_packets,
    build_triptychs,
    ordered_rendered_pages,
    poppler_path_argument,
    poppler_paths_equivalent,
    poppler_render_prefix_is_valid,
    render_layouts,
    review_signals,
    role_for_page,
    safe_relative,
)


def _comparison():
    blocks = {
        "original_hybrid": [{"raw_index": 0, "source_page": 1, "type": "text", "bbox": [0, 0, 10, 10], "text": "alpha", "assets": ["images/a.jpg"]}],
        "original_pipeline_ocr": [{"raw_index": 1, "source_page": 1, "type": "text", "bbox": [0, 0, 10, 10], "text": "beta", "assets": ["images/b.jpg"]}],
        "raster_hybrid": [{"raw_index": 2, "source_page": 1, "type": "image", "bbox": None, "text": "", "assets": ["images/c.jpg"]}],
    }
    return {"views": {view: {"blocks": blocks[view]} for view in VIEWS}, "pairwise": {
        "original_hybrid__vs__original_pipeline_ocr": {"bbox_matches": [{"left_raw_index": 0, "right_raw_index": 1, "bbox_iou": 1.0}], "left_unmatched": [], "right_unmatched": []},
        "original_hybrid__vs__raster_hybrid": {"bbox_matches": [], "left_unmatched": blocks["original_hybrid"], "right_unmatched": blocks["raster_hybrid"]},
    }}


def test_canonical_role_boundaries_cover_all_124_pages_once():
    assert [role_for_page(page) for page in (1, 5, 6, 16, 17, 25, 26, 68, 69, 103, 104, 110, 111, 123, 124)] == [
        "front_matter", "front_matter", "introduction_investigator_material", "introduction_investigator_material", "one_night_in_perla", "one_night_in_perla", "island_main_scenario", "island_main_scenario", "handouts", "handouts", "keeper_maps", "keeper_maps", "pre_generated_investigators", "pre_generated_investigators", "back_cover"]
    assert sum(last - first + 1 for first, last, _ in ROLES) == 124


def test_neutral_contract_roles_replace_legacy_124_page_fallback(tmp_path):
    contract = tmp_path / "contract.json"
    contract.write_text(
        json.dumps(
            {
                "schema": "kb_creator.scenario_reconstruction_contract.v1",
                "contract_revision": 1,
                "scenario": {"id": "sample", "title": "Sample"},
                "source": {"sha256": "A" * 64, "byte_count": 1, "page_count": 2, "media_box_points": [100, 200], "rotation_degrees": 0},
                "scope": {"mode": "all_source_pages", "first_page": 1, "last_page": 2, "required_entities": {"numbered_player_handouts": 0}},
                "page_roles": [
                    {"role": "cover", "first_page": 1, "last_page": 1, "content_mode": "visual", "traits": [], "strategies": ["visual_preserve"]},
                    {
                        "role": "scenario_body",
                        "first_page": 2,
                        "last_page": 2,
                        "content_mode": "text",
                        "traits": [],
                        "strategies": ["reading_order"],
                    },
                ],
                "reconstruction": {"strategies": ["reading_order"], "required_review": True},
                "acceptance": {"approval_authority": "configured_reconstruction_review"},
            }
        ),
        encoding="utf-8",
    )
    expected_pages, roles = _contract_roles(contract)
    assert expected_pages == 2
    assert roles == ((1, 1, "cover"), (2, 2, "scenario_body"))
    assert [role_for_page(page, roles) for page in (1, 2)] == [
        "cover",
        "scenario_body",
    ]
    assert not any(role in str(roles) for role in ("handouts", "keeper_maps"))


def test_packets_preserve_blocks_assets_and_pairwise_rows_in_stable_page_order(tmp_path):
    index, files = build_packets(_comparison(), tmp_path / "merge_packets", 2)
    packet = json.loads((tmp_path / "merge_packets" / "pages" / "page-001.json").read_text(encoding="utf-8"))
    assert index == sorted(index, key=lambda row: row["source_page"])
    assert packet["views"]["original_hybrid"]["blocks"][0]["assets"] == ["images/a.jpg"]
    assert packet["views"]["raster_hybrid"]["blocks"][0]["bbox"] is None
    assert packet["pairwise"]["original_hybrid__vs__original_pipeline_ocr"]["bbox_matches"][0]["left_raw_index"] == 0
    assert sum(len(json.loads((tmp_path / "merge_packets" / "pages" / f"page-{page:03d}.json").read_text(encoding="utf-8"))["pairwise"]["original_hybrid__vs__original_pipeline_ocr"]["bbox_matches"]) for page in (1, 2)) == 1
    assert len(files) == 6


def test_priority_signals_are_transparent_and_not_truth_claims():
    views = {}
    for view in VIEWS:
        blocks = _comparison()["views"][view]["blocks"]
        counts = {}
        for row in blocks:
            counts[row["type"]] = counts.get(row["type"], 0) + 1
        views[view] = {"blocks": blocks, "text_length": sum(len(row["text"]) for row in blocks), "type_counts": counts, "asset_references": [asset for row in blocks for asset in row["assets"]]}
    signals = review_signals(views)
    assert signals["normalized_text_similarity"] < 1
    assert signals["block_type_divergence"] == 1
    assert signals["missing_overlay_box_candidates"] == 1
    assert signals["priority_score"] > 0


def test_pairwise_projection_indexes_each_used_view_once_and_reads_fresh_inputs():
    class CountedBlocks(list):
        def __init__(self, values):
            super().__init__(values)
            self.reads = 0

        def __iter__(self):
            self.reads += 1
            return super().__iter__()

    views = {
        name: {"blocks": CountedBlocks([
            {"raw_index": index, "source_page": index % 2 + 1}
            for index in range(100)
        ])}
        for name in ("left", "right", "third")
    }
    rows = [{"left_raw_index": index, "right_raw_index": index} for index in range(100)]
    unmatched = [{"source_page": 2, "text": "other"}, {"source_page": 1, "text": "keep"}]
    pairs = {
        name: {"bbox_matches": rows, "left_unmatched": unmatched}
        for name in ("left__vs__right", "left__vs__third")
    }
    result = _packet_pairwise(pairs, views, 1)
    for projection in result.values():
        assert projection == {
            "bbox_matches": rows[::2],
            "left_unmatched": [unmatched[1]],
            "right_unmatched": [],
        }
    assert all(view["blocks"].reads == 1 for view in views.values())

    # Historical dictionaries used the last occurrence of a duplicated index.
    for view in views.values():
        view["blocks"].append({"raw_index": 0, "source_page": 2})
    fresh = _packet_pairwise(pairs, views, 1)
    assert fresh["left__vs__right"]["bbox_matches"] == rows[2::2]
    assert all(view["blocks"].reads == 2 for view in views.values())


@pytest.mark.parametrize("row, right_page", [
    ({"left_raw_index": 0}, 1),
    ({"left_raw_index": 0, "right_raw_index": 99}, 1),
    ({"left_raw_index": 0, "right_raw_index": 0}, 2),
    ({"left_raw_index": 0, "right_raw_index": 0}, "1"),
])
def test_pairwise_projection_still_rejects_invalid_match(row, right_page):
    views = {
        "left": {"blocks": [{"raw_index": 0, "source_page": 1}]},
        "right": {"blocks": [{"raw_index": 0, "source_page": right_page}]},
    }
    with pytest.raises(ValueError):
        _packet_pairwise({"left__vs__right": {"bbox_matches": [row]}}, views, 1)


def test_pairwise_projection_empty_matches_do_not_require_unused_views():
    assert _packet_pairwise({"missing__vs__absent": {}}, {}, 1) == {
        "missing__vs__absent": {
            "bbox_matches": [], "left_unmatched": [], "right_unmatched": [],
        },
    }


def test_triptych_labels_and_124_page_contact_coverage(tmp_path):
    assert TRIPTYCH_LABELS == ("original_hybrid", "original_pipeline_ocr", "raster_hybrid")
    rendered = {view: [] for view in VIEWS}
    for view_index, view in enumerate(VIEWS):
        pages = tmp_path / view / "pages"; pages.mkdir(parents=True)
        for page in range(1, 125):
            path = pages / f"page-{page:03d}.png"
            Image.new("RGB", (8, 10), (view_index * 80, page % 255, 0)).save(path)
            rendered[view].append(path)
    triptychs = build_triptychs(rendered, tmp_path / "triptychs")
    sheets = build_contact_sheets(triptychs, tmp_path / "contacts")
    assert len(triptychs) == 124 and triptychs[0].name == "page-001.png" and triptychs[-1].name == "page-124.png"
    assert len(sheets) == 31 and sheets[0].name == "pages-001-004.png" and sheets[-1].name == "pages-121-124.png"
    with Image.open(triptychs[0]) as image:
        assert image.size == (24, 28)  # three views plus a stable label band


def test_poppler_rendered_pages_are_numerically_sorted_and_exact(tmp_path):
    for number in (1, 2, 10, 100, 124):
        (tmp_path / f"_render-{number}.png").write_bytes(b"png")
    with pytest.raises(ValueError, match="exactly 1..5"):
        ordered_rendered_pages(tmp_path, 5)
    exact = tmp_path / "exact"; exact.mkdir()
    for number in range(1, 125):
        (exact / f"_render-{number}.png").write_bytes(b"png")
    assert [int(path.stem.split("-")[1]) for path in ordered_rendered_pages(exact, 124)] == list(range(1, 125))


def test_poppler_path_argument_handles_windows_and_non_windows_forms(tmp_path):
    assert poppler_path_argument(r"C:\work\layout.pdf", platform="nt") == r"\\?\C:\work\layout.pdf"
    assert poppler_path_argument(r"\\server\share\layout.pdf", platform="nt") == r"\\?\UNC\server\share\layout.pdf"
    assert poppler_path_argument(r"\\?\C:\work\layout.pdf", platform="nt") == r"\\?\C:\work\layout.pdf"
    assert poppler_path_argument(tmp_path / "layout.pdf", platform="posix") == str((tmp_path / "layout.pdf").resolve())


def test_poppler_path_equivalence_accepts_legacy_and_extended_forms_only():
    plain_drive = r"C:\work\visual\layout.pdf"
    extended_drive = r"\\?\C:\work\visual\layout.pdf"
    plain_unc = r"\\server\share\visual\layout.pdf"
    extended_unc = r"\\?\UNC\server\share\visual\layout.pdf"
    assert poppler_paths_equivalent(plain_drive, extended_drive, platform="nt")
    assert poppler_paths_equivalent(plain_unc, extended_unc, platform="nt")
    assert not poppler_paths_equivalent(r"relative\layout.pdf", r"relative\layout.pdf", platform="nt")
    assert not poppler_paths_equivalent(plain_drive, r"\\?\C:\work\other\layout.pdf", platform="nt")
    assert poppler_render_prefix_is_valid(r"C:\work\visual\_render", platform="nt")
    assert poppler_render_prefix_is_valid(r"\\?\C:\work\visual\_render", platform="nt")
    assert not poppler_render_prefix_is_valid(r"relative\_render", platform="nt")
    assert not poppler_render_prefix_is_valid(r"C:\work\visual\wrong", platform="nt")


def test_render_layouts_adapts_long_input_and_uses_scratch_output_without_copying_layouts(tmp_path, monkeypatch):
    import kb_creator.scripts.build_mineru_visual_merge_bundle as bundle

    long_root = tmp_path.joinpath(*[f"segment_{number}_{'x' * 24}" for number in range(10)])
    long_root.mkdir(parents=True)
    layouts = {}
    for view in VIEWS:
        layout = long_root / f"{view}_layout.pdf"
        layout.write_bytes(b"%PDF-1.4\n")
        layouts[view] = layout
    assert all(len(str(path)) > 260 for path in layouts.values())

    calls = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        if command[1:] == ["-v"]:
            return SimpleNamespace(stdout="pdftoppm 1.0", stderr="")
        assert command[-2].startswith("\\\\?\\")
        assert command[-1].startswith("\\\\?\\")
        prefix = Path(command[-1])
        Image.new("RGB", (4, 5), "white").save(prefix.with_name(prefix.name + "-1.png"))
        return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(bundle.subprocess, "run", fake_run)
    rendered, commands, _ = render_layouts(layouts, tmp_path / "visual", "pdftoppm", 110, 1)

    assert all(command[-2] == poppler_path_argument(layouts[view]) for view, command in zip(VIEWS, commands))
    assert all(poppler_render_prefix_is_valid(command[-1]) for command in commands)
    assert all(not poppler_paths_equivalent(command[-1], tmp_path / "visual" / view / "pages" / "_render") for view, command in zip(VIEWS, commands))
    assert not list((tmp_path / "visual").rglob("*.pdf"))
    assert {view: [path.name for path in paths] for view, paths in rendered.items()} == {
        view: ["page-001.png"] for view in VIEWS
    }


def test_render_layouts_preserves_bounded_poppler_failure_diagnostics(tmp_path, monkeypatch):
    import kb_creator.scripts.build_mineru_visual_merge_bundle as bundle

    layout = tmp_path / "layout.pdf"
    layout.write_bytes(b"%PDF-1.4\n")

    def fake_run(command, **_kwargs):
        if command[1:] == ["-v"]:
            return SimpleNamespace(stdout="pdftoppm 1.0", stderr="")
        raise subprocess.CalledProcessError(7, command, output="o" * 3000, stderr="renderer details" + "x" * 3000)

    monkeypatch.setattr(bundle.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match=r"view=original_hybrid; exit_code=7;.*renderer details.*truncated"):
        render_layouts({view: layout for view in VIEWS}, tmp_path / "visual", "pdftoppm", 110, 1)


@pytest.mark.skipif(os.name != "nt", reason="exercises Windows extended-length argv handling")
def test_windows_poppler_renders_valid_pdf_at_long_path(tmp_path):
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm is None:
        pytest.skip("pdftoppm is not available on PATH")
    long_root = tmp_path.joinpath(*[f"segment_{number}_{'x' * 24}" for number in range(10)])
    long_root.mkdir(parents=True)
    layout = long_root / "layout.pdf"
    Image.new("RGB", (20, 20), "white").save(layout, "PDF")
    assert len(str(layout)) > 260
    rendered, _, _ = render_layouts({view: layout for view in VIEWS}, tmp_path / "visual", pdftoppm, 72, 1)
    assert all([path.name for path in rendered[view]] == ["page-001.png"] for view in VIEWS)


def test_safe_root_refusal_resume_and_path_containment(tmp_path):
    identities = {"raw_receipt": {"path": "r", "sha256": "A"}, "source": {"path": "s", "sha256": "B"}, "comparison": {"path": "c", "sha256": "C"}, "raw_root": "raw", "dpi": 110}
    root = tmp_path / "bundle"; (root / "visual").mkdir(parents=True); (root / "merge_packets").mkdir()
    (root / "merge_packets" / "merge_index.json").write_text("{}", encoding="utf-8")
    (root / "visual" / "visual_manifest.json").write_text(json.dumps({"inputs": identities, "files": []}), encoding="utf-8")
    assert _check_resume(root, identities, True)["inputs"] == identities
    with pytest.raises(FileExistsError):
        _check_resume(root, identities, False)
    with pytest.raises(ValueError):
        _check_resume(root, {**identities, "dpi": 111}, True)
    assert safe_relative("visual/triptychs/page-001.png") == "visual/triptychs/page-001.png"
    for path in ("../escape.png", "C:\\escape.png", "/escape.png"):
        with pytest.raises(ValueError):
            safe_relative(path)
