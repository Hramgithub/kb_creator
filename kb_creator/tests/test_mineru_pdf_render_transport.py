from __future__ import annotations

import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pytest


pytest.importorskip("fitz")
pytest.importorskip("pypdfium2")

from mineru.utils import pdf_image_tools as render_tools
from mineru.utils.enum_class import ImageType
from mineru.utils.pdfium_guard import close_pdfium_document, open_pdfium_document


def _two_page_pdf_bytes() -> bytes:
    import fitz

    document = fitz.open()
    for text in ("first transport page", "second transport page"):
        page = document.new_page(width=144, height=144)
        page.insert_text((24, 72), text, fontsize=12)
    try:
        return document.tobytes()
    finally:
        document.close()


def _close_images(images) -> None:
    for item in images:
        image = item.get("img_pil")
        if image is not None:
            image.close()


def test_file_transport_spawn_worker_matches_legacy_bytes(tmp_path: Path) -> None:
    pdf_bytes = _two_page_pdf_bytes()
    spool = tmp_path / "sealed.pdf"
    spool.write_bytes(pdf_bytes)
    identity = render_tools.get_pdf_render_spool_identity(spool)

    legacy = render_tools.load_images_from_pdf_core(
        pdf_bytes, dpi=72, start_page_id=0, end_page_id=1, image_type=ImageType.PIL
    )
    with ProcessPoolExecutor(
        max_workers=1, mp_context=multiprocessing.get_context("spawn")
    ) as executor:
        future = executor.submit(
            render_tools._load_images_from_pdf_path_worker,
            str(spool),
            identity,
            72,
            0,
            1,
            ImageType.PIL,
        )
        transported = future.result(timeout=30)

    try:
        assert [item["img_pil"].size for item in transported] == [
            item["img_pil"].size for item in legacy
        ]
        assert [item["img_pil"].tobytes() for item in transported] == [
            item["img_pil"].tobytes() for item in legacy
        ]
    finally:
        _close_images(legacy)
        _close_images(transported)


def test_public_path_branch_matches_legacy_and_preserves_order(tmp_path: Path) -> None:
    import pypdfium2 as pdfium

    pdf_bytes = _two_page_pdf_bytes()
    spool = tmp_path / "sealed.pdf"
    spool.write_bytes(pdf_bytes)
    identity = render_tools.get_pdf_render_spool_identity(spool)
    legacy = render_tools.load_images_from_pdf_core(
        pdf_bytes, dpi=72, start_page_id=0, end_page_id=1, image_type=ImageType.PIL
    )
    parent_document = open_pdfium_document(pdfium.PdfDocument, pdf_bytes)
    try:
        transported = render_tools.load_images_from_pdf_doc(
            parent_document,
            dpi=72,
            start_page_id=0,
            end_page_id=1,
            image_type=ImageType.PIL,
            verified_pdf_path=spool,
            verified_pdf_identity=identity,
            threads=1,
        )
    finally:
        close_pdfium_document(parent_document)

    try:
        assert [item["img_pil"].tobytes() for item in transported] == [
            item["img_pil"].tobytes() for item in legacy
        ]
    finally:
        _close_images(legacy)
        _close_images(transported)
        render_tools.shutdown_pdf_render_executor()


@pytest.mark.parametrize("change", ["missing", "mutated", "replaced"])
def test_file_transport_rejects_stale_spool(tmp_path: Path, change: str) -> None:
    spool = tmp_path / "sealed.pdf"
    spool.write_bytes(_two_page_pdf_bytes())
    identity = render_tools.get_pdf_render_spool_identity(spool)

    if change == "missing":
        spool.unlink()
    elif change == "mutated":
        spool.write_bytes(spool.read_bytes() + b"changed")
    else:
        replacement = tmp_path / "replacement.pdf"
        replacement.write_bytes(spool.read_bytes())
        os.replace(replacement, spool)

    with pytest.raises((FileNotFoundError, ValueError)):
        render_tools._verify_pdf_render_spool(spool, identity)


def test_file_transport_requires_identity(tmp_path: Path) -> None:
    spool = tmp_path / "sealed.pdf"
    spool.write_bytes(_two_page_pdf_bytes())
    with pytest.raises(ValueError, match="requires an identity"):
        render_tools._load_images_from_pdf_path_range(
            spool,
            None,
            dpi=72,
            start_page_id=0,
            end_page_id=0,
            image_type=ImageType.PIL,
            threads=1,
        )
