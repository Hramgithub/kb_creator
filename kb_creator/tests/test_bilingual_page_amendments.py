import hashlib
import json
from pathlib import Path

import pytest

from kb_creator.pipeline.bilingual_page_amendments import BilingualPageAmendmentError, amend_pages


def _sha(raw):
    return hashlib.sha256(raw).hexdigest().upper()


def _identity(path):
    raw = path.read_bytes()
    return {"path": path.name, "bytes": len(raw), "sha256": _sha(raw)}


def _fixture(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    values = [("EN 1", "Первый текст. Повтор."), ("EN 2", "Продолжение один раз."), ("EN 3", "Без изменений.")]
    for number, (en, ru) in enumerate(values, 1):
        row = {"source_page": number, "source_markdown_sha256": _sha(en.encode()),
               "en_markdown": en, "ru_markdown": ru, "unresolved": ["held"]}
        (pages / f"page-{number:03}.json").write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = tmp_path / "predecessor.json"
    manifest.write_text("{}\n", encoding="utf-8")
    plan = {"schema": "kb_creator.bilingual_page_amendments.v1", "page_count": 3,
            "predecessor": {"manifest": _identity(manifest),
                            "pages": [_identity(pages / f"page-{number:03}.json") for number in range(1, 4)]},
            "amendments": [{"source_page": 1, "before": "Первый текст.", "after": "Исправленный текст.",
                            "expected_count": 1, "reason": "Reviewed wording", "evidence": ["reviews/decision.json"]}],
            "checks": [{"source_page": 2, "text": "Продолжение один раз.", "expected_count": 1,
                        "reason": "Retain continuation", "evidence": ["reviews/decision.json"]}]}
    plan_path = tmp_path / "amendments.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    return pages, manifest, plan_path, plan


def _run(tmp_path, plan=None):
    pages, manifest, plan_path, original = _fixture(tmp_path)
    if plan is not None:
        plan(original, pages)
        plan_path.write_text(json.dumps(original, ensure_ascii=False), encoding="utf-8")
    output = tmp_path / "successor"
    return pages, manifest, plan_path, output


def test_exact_change_preserves_source_en_other_fields_and_unchanged_bytes(tmp_path):
    pages, manifest, plan_path, output = _run(tmp_path)
    before = {path.name: path.read_bytes() for path in pages.iterdir()}
    report = amend_pages(pages, manifest, plan_path, output)
    assert report["changed_pages"] == [1]
    assert report["unchanged_page_count"] == 2
    assert report["accepted"] is False and report["translation_semantics_validated"] is False
    assert report["checks"][0]["actual_count"] == 1
    assert {path.name: path.read_bytes() for path in pages.iterdir()} == before
    assert (output / "pages/page-002.json").read_bytes() == before["page-002.json"]
    assert (output / "pages/page-003.json").read_bytes() == before["page-003.json"]
    old = json.loads(before["page-001.json"])
    new = json.loads((output / "pages/page-001.json").read_bytes())
    assert new.pop("ru_markdown") == "Исправленный текст. Повтор."
    old.pop("ru_markdown")
    assert new == old
    assert (output / "reviewed-amendments.json").read_bytes() == plan_path.read_bytes()


@pytest.mark.parametrize("mutation,message", [
    (lambda plan, pages: plan["predecessor"]["pages"][0].__setitem__("sha256", "0" * 64), "stale page"),
    (lambda plan, pages: plan["predecessor"]["pages"][0].__setitem__("path", "../page-001.json"), "unsafe reference"),
    (lambda plan, pages: plan["amendments"][0].__setitem__("before", "missing"), "stale preimage"),
    (lambda plan, pages: plan["amendments"].append(dict(plan["amendments"][0])), "overlapping"),
    (lambda plan, pages: plan["amendments"].append({**plan["amendments"][0], "before": "текст. Повтор", "after": "другое"}), "overlapping"),
    (lambda plan, pages: plan["checks"][0].__setitem__("text", "absent"), "continuation check failed"),
    (lambda plan, pages: (pages / "page-003.json").unlink(), "missing"),
])
def test_fail_closed_before_output(tmp_path, mutation, message):
    pages, manifest, plan_path, output = _run(tmp_path, mutation)
    with pytest.raises(BilingualPageAmendmentError, match=message):
        amend_pages(pages, manifest, plan_path, output)
    assert not output.exists()


def test_rejects_nonunique_preimage_and_existing_output(tmp_path):
    def duplicate(plan, pages):
        row_path = pages / "page-001.json"
        row = json.loads(row_path.read_text(encoding="utf-8"))
        row["ru_markdown"] += " Первый текст."
        row_path.write_text(json.dumps(row, ensure_ascii=False), encoding="utf-8")
        plan["predecessor"]["pages"][0] = _identity(row_path)
    pages, manifest, plan_path, output = _run(tmp_path, duplicate)
    with pytest.raises(BilingualPageAmendmentError, match="non-unique"):
        amend_pages(pages, manifest, plan_path, output)
    assert not output.exists()
    output.mkdir()
    with pytest.raises(BilingualPageAmendmentError, match="absent"):
        amend_pages(pages, manifest, plan_path, output)


def test_rejects_stale_manifest_and_input_en_hash(tmp_path):
    pages, manifest, plan_path, output = _run(tmp_path)
    manifest.write_text("changed\n", encoding="utf-8")
    with pytest.raises(BilingualPageAmendmentError, match="stale predecessor manifest"):
        amend_pages(pages, manifest, plan_path, output)
    manifest.write_text("{}\n", encoding="utf-8")
    page = pages / "page-001.json"
    row = json.loads(page.read_text(encoding="utf-8"))
    row["source_markdown_sha256"] = "0" * 64
    page.write_text(json.dumps(row, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(BilingualPageAmendmentError, match="EN hash mismatch"):
        amend_pages(pages, manifest, plan_path, output)
    assert not output.exists()
