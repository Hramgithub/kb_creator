import os
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from kb_creator.scripts.build_mineru_visual_merge_bundle import (
    poppler_paths_equivalent,
    poppler_render_prefix_is_valid,
    render_layouts,
)


POPPLER = os.environ.get("KB_CREATOR_PDFTOPPM") or shutil.which("pdftoppm")


def test_scratch_render_copies_validated_pages_and_records_actual_command(tmp_path, monkeypatch):
    import kb_creator.scripts.build_mineru_visual_merge_bundle as bundle

    layout = tmp_path / "layout.pdf"
    layout.write_bytes(b"%PDF-1.4\n")
    managed_pages = tmp_path / "managed" / "view" / "pages"

    def fake_run(command, **_kwargs):
        if command[1:] == ["-v"]:
            return SimpleNamespace(stdout="pdftoppm fixture", stderr="")
        prefix = Path(command[-1])
        Image.new("RGB", (4, 5), "white").save(prefix.with_name(prefix.name + "-1.png"))
        return SimpleNamespace(returncode=0, stdout="rendered", stderr="")

    monkeypatch.setattr(bundle.subprocess, "run", fake_run)
    rendered, commands, _ = render_layouts({"view": layout}, managed_pages.parent.parent, "pdftoppm", 72, 1, ("view",))

    assert poppler_paths_equivalent(commands[0][-2], layout)
    assert poppler_render_prefix_is_valid(commands[0][-1])
    assert not poppler_paths_equivalent(commands[0][-1], managed_pages / "_render")
    assert [path.name for path in rendered["view"]] == ["page-001.png"]
    assert (managed_pages / "page-001.png").is_file()
    assert not list(managed_pages.glob("_render-*.png"))


def test_success_without_pngs_is_rejected_with_renderer_diagnostics(tmp_path, monkeypatch):
    import kb_creator.scripts.build_mineru_visual_merge_bundle as bundle

    layout = tmp_path / "layout.pdf"
    layout.write_bytes(b"%PDF-1.4\n")

    def fake_run(command, **_kwargs):
        if command[1:] == ["-v"]:
            return SimpleNamespace(stdout="pdftoppm fixture", stderr="")
        return SimpleNamespace(returncode=0, stdout="renderer stdout", stderr="renderer stderr")

    monkeypatch.setattr(bundle.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match=r"exit_code=0;.*output_inventory=\[\];.*renderer stderr.*renderer stdout"):
        render_layouts({"view": layout}, tmp_path / "visual", "pdftoppm", 72, 1, ("view",))


@pytest.mark.skipif(os.name != "nt" or not POPPLER or not Path(POPPLER).is_file(), reason="requires Windows Poppler; set KB_CREATOR_PDFTOPPM")
def test_real_poppler_renders_three_views_and_21_pages_when_managed_output_path_is_long(tmp_path):
    layout = tmp_path / "layout.pdf"
    images = [Image.new("RGB", (20, 20), "white") for _ in range(21)]
    try:
        images[0].save(layout, "PDF", save_all=True, append_images=images[1:])
    finally:
        for image in images:
            image.close()
    long_root = tmp_path.joinpath(*[f"segment_{number}_{'x' * 24}" for number in range(10)])
    visual_root = long_root / "visual"
    assert len(str(visual_root / "original" / "pages" / "_render-1.png")) > 260
    views = ("original", "ocr", "raster")

    rendered, commands, _ = render_layouts({view: layout for view in views}, visual_root, str(POPPLER), 72, 21, views)

    assert all(len(command[-1]) < 260 for command in commands)
    assert all(poppler_paths_equivalent(command[-2], layout) for command in commands)
    assert all([path.name for path in rendered[view]] == [f"page-{page:03d}.png" for page in range(1, 22)] for view in views)
    assert sum(1 for _ in visual_root.rglob("page-*.png")) == 63
