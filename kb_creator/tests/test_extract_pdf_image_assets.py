import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image


MODULE = Path(__file__).parents[1] / "scripts" / "extract_pdf_image_assets.py"
spec = importlib.util.spec_from_file_location("extract_pdf_image_assets", MODULE)
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)


def fixture_pdf(tmp_path: Path) -> Path:
    from reportlab.pdfgen import canvas

    image = Image.new("RGBA", (3, 2), (20, 40, 60, 0))
    image.putpixel((1, 1), (200, 100, 50, 128))
    image_path = tmp_path / "fixture.png"
    image.save(image_path)
    pdf_path = tmp_path / "source.pdf"
    pdf = canvas.Canvas(str(pdf_path), pagesize=(100, 100))
    pdf.drawImage(str(image_path), 10, 10, width=30, height=20, mask="auto")
    pdf.save()
    return pdf_path


def test_extract_records_sha_dimensions_and_alpha(tmp_path):
    pdf = fixture_pdf(tmp_path)
    listed = extractor.list_images(pdf, None)
    assert listed["images"]
    selected = listed["images"][0]
    out = tmp_path / "out"
    manifest = extractor.extract_images(pdf, out, [f'{selected["page"]}:{selected["name"]}'], None)
    record = manifest["images"][0]
    data = (out / record["path"]).read_bytes()
    assert record["mode"] == "RGBA"
    assert record["width"] == 3 and record["height"] == 2
    assert record["sha256"] == hashlib.sha256(data).hexdigest()
    assert Image.open(out / record["path"]).mode == "RGBA"


def test_extract_refuses_collision_and_bad_selector(tmp_path):
    pdf = fixture_pdf(tmp_path)
    selected = extractor.list_images(pdf, None)["images"][0]
    selector = f'{selected["page"]}:{selected["name"]}'
    out = tmp_path / "out"
    extractor.extract_images(pdf, out, [selector], None)
    with pytest.raises(FileExistsError):
        extractor.extract_images(pdf, out, [selector], None)
    with pytest.raises(ValueError, match="invalid selector"):
        extractor.parse_selectors(["../escape"])


def test_png_conversion_preserves_decoded_pixels_and_alpha(tmp_path):
    pdf = fixture_pdf(tmp_path)
    selected = extractor.list_images(pdf, None)["images"][0]
    out = tmp_path / "png"
    manifest = extractor.extract_images(pdf, out, [f'{selected["page"]}:{selected["name"]}'], None, "png")
    record = manifest["images"][0]
    converted = Image.open(out / record["path"])
    assert record["path"].endswith(".png")
    assert converted.mode == "RGBA"
    assert converted.tobytes() == bytes([20, 40, 60, 0] * 4 + [200, 100, 50, 128] + [20, 40, 60, 0])


def test_preflight_rejects_bad_page_before_creating_output(tmp_path):
    pdf = fixture_pdf(tmp_path)
    out = tmp_path / "bad"
    with pytest.raises(ValueError, match="out of range"):
        extractor.extract_images(pdf, out, [], [99])
    assert not out.exists()


def test_selected_image_does_not_decode_unrelated_page(tmp_path, monkeypatch):
    from types import SimpleNamespace
    pdf = fixture_pdf(tmp_path)
    reader = extractor.PdfReader(str(pdf))
    image = reader.pages[0].images[0]

    class UnsupportedPage:
        @property
        def images(self):
            raise AssertionError('Unselected image decoder must not run')

    monkeypatch.setattr(extractor, 'PdfReader', lambda _: SimpleNamespace(pages=[reader.pages[0], UnsupportedPage()]))
    result = extractor.extract_images(pdf, tmp_path / 'selected', [f'1:{image.name}'], None)
    assert len(result['images']) == 1
    assert result['images'][0]['page'] == 1
    assert result['images'][0]['width'] == 3
    with pytest.raises(ValueError, match='selected images not found'):
        extractor.extract_images(pdf, tmp_path / 'excluded', [f'1:{image.name}'], [2])
    assert not (tmp_path / 'excluded').exists()


def test_selector_page_out_of_range_fails_before_output(tmp_path):
    pdf = fixture_pdf(tmp_path)
    out = tmp_path / 'bad-selector-page'
    with pytest.raises(ValueError, match='out of range'):
        extractor.extract_images(pdf, out, ['99:any.png'], None)
    assert not out.exists()
