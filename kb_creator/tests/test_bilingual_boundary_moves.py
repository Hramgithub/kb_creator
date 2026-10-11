import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from kb_creator.pipeline.bilingual_boundary_moves import BilingualBoundaryMoveError, move_pages


def _sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _identity(path):
    raw = path.read_bytes()
    return {"path": path.name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest().upper()}


def _fixture(tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    pages = tmp_path / "pages"; pages.mkdir()
    values = [("EN one", "До: перенеси это. После."), ("EN two", "Начало. Конец."), ("EN three", "Без изменений.")]
    for number, (en, ru) in enumerate(values, 1):
        row = {"source_page": number, "source_markdown_sha256": _sha(en), "en_markdown": en, "ru_markdown": ru, "unresolved": []}
        (pages / f"page-{number:03}.json").write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = tmp_path / "predecessor.json"; manifest.write_text('{"predecessor": true}\n', encoding="utf-8")
    source = values[0][1]; moved = "перенеси это."
    start = source.encode().index(moved.encode()); end = start + len(moved.encode())
    target_offset = len("Начало. ".encode())
    plan = {"schema": "kb_creator.bilingual_boundary_moves.v1", "predecessor": {"manifest": _identity(manifest), "pages": [_identity(pages / f"page-{n:03}.json") for n in range(1, 4)]}, "page_count": 3,
            "moves": [{"source_page": 1, "target_page": 2, "source_span": {"start_byte": start, "end_byte": end}, "source_text": moved, "source_text_sha256": _sha(moved), "target_insert_byte": target_offset, "target_suffix": "\n\n", "rationale": "Reviewed continuation boundary."}], "whitespace_edits": []}
    plan_path = tmp_path / "plan.json"; plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return pages, manifest, plan_path, plan


def test_cross_page_move_conserves_cyrillic_and_copies_unrelated_bytes(tmp_path):
    pages, manifest, plan_path, _ = _fixture(tmp_path)
    before = {path.name: path.read_bytes() for path in pages.iterdir()}
    report = move_pages(pages, manifest, plan_path, tmp_path / "successor")
    output = tmp_path / "successor/pages"
    assert json.loads((output / "page-001.json").read_text(encoding="utf-8"))["ru_markdown"] == "До:  После."
    assert json.loads((output / "page-002.json").read_text(encoding="utf-8"))["ru_markdown"] == "Начало. перенеси это.\n\nКонец."
    assert (output / "page-003.json").read_bytes() == before["page-003.json"]
    assert {path.name: path.read_bytes() for path in pages.iterdir()} == before
    assert report["state"] == "preliminary_boundary_successor_pending_source_binding"
    move = report["moves"][0]
    assert move["successor_destination"]["page"] == 2
    assert move["successor_destination"]["sha256"] == _sha("перенеси это.")
    assert report["conservation"]["exact_transport_construction"] is True
    assert report["conservation"]["non_whitespace_ru_character_multiset_conserved"] is True


def test_non_string_en_hash_has_controlled_preflight_failure(tmp_path):
    pages, manifest, plan_path, plan = _fixture(tmp_path)
    page = pages / "page-001.json"
    row = json.loads(page.read_text(encoding="utf-8"))
    row["source_markdown_sha256"] = None
    page.write_text(json.dumps(row, ensure_ascii=False), encoding="utf-8")
    plan["predecessor"]["pages"][0] = _identity(page)
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(BilingualBoundaryMoveError, match="EN hash"):
        move_pages(pages, manifest, plan_path, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_consumes_and_reports_validated_snapshots_when_paths_change(tmp_path, monkeypatch):
    from kb_creator.pipeline import bilingual_boundary_moves as module
    pages, manifest, plan_path, plan = _fixture(tmp_path)
    plan_bytes = plan_path.read_bytes()
    page_bytes = {p.name: p.read_bytes() for p in pages.iterdir()}
    original = module._validated_edits

    def change_paths_after_snapshot(rows, moves, whitespace):
        result = original(rows, moves, whitespace)
        for path in pages.iterdir():
            path.write_text("Changed externally after validation", encoding="utf-8")
        manifest.write_text("Changed external manifest", encoding="utf-8")
        plan_path.write_text("Changed external plan", encoding="utf-8")
        return result

    monkeypatch.setattr(module, "_validated_edits", change_paths_after_snapshot)
    report = move_pages(pages, manifest, plan_path, tmp_path / "out")
    assert report["inputs"]["manifest"] == plan["predecessor"]["manifest"]
    assert [{k: r[k] for k in ("path", "bytes", "sha256")} for r in report["inputs"]["pages"]] == plan["predecessor"]["pages"]
    assert (tmp_path / "out/reviewed-boundary-moves.json").read_bytes() == plan_bytes
    assert (tmp_path / "out/pages/page-003.json").read_bytes() == page_bytes["page-003.json"]
    target = json.loads((tmp_path / "out/pages/page-002.json").read_text(encoding="utf-8"))
    assert target["ru_markdown"] == "Начало. перенеси это.\n\nКонец."


@pytest.mark.parametrize("mutation, message", [
    (lambda plan: plan["moves"][0].__setitem__("source_text", "другое"), "source text/hash"),
    (lambda plan: plan["moves"][0].__setitem__("target_insert_byte", 9999), "target insertion"),
    (lambda plan: plan["moves"].append(dict(plan["moves"][0])), "(conflicting target insertions|duplicate or overlapping source edits)"),
    (lambda plan: plan["moves"][0]["source_span"].__setitem__("start_byte", 1), "splits a UTF-8"),
])
def test_rejects_stale_target_duplicate_and_multibyte_boundaries_without_output(tmp_path, mutation, message):
    pages, manifest, plan_path, plan = _fixture(tmp_path); mutation(plan)
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(BilingualBoundaryMoveError, match=message):
        move_pages(pages, manifest, plan_path, tmp_path / "successor")
    assert not (tmp_path / "successor").exists()


def test_rejects_path_escape_and_en_hash_mismatch(tmp_path):
    pages, manifest, plan_path, plan = _fixture(tmp_path)
    plan["predecessor"]["pages"][0]["path"] = "../page-001.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(BilingualBoundaryMoveError, match="escapes"):
        move_pages(pages, manifest, plan_path, tmp_path / "out")
    pages, manifest, plan_path, plan = _fixture(tmp_path / "second")
    row_path = pages / "page-002.json"; row = json.loads(row_path.read_text(encoding="utf-8")); row["source_markdown_sha256"] = "0" * 64; row_path.write_text(json.dumps(row), encoding="utf-8")
    plan["predecessor"]["pages"][1] = _identity(row_path)
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(BilingualBoundaryMoveError, match="EN hash"):
        move_pages(pages, manifest, plan_path, tmp_path / "second/out")


@pytest.mark.parametrize("target", ["source", "target", "manifest"])
def test_rejects_actual_stale_input_identity_before_creating_output(tmp_path, target):
    pages, manifest, plan_path, _ = _fixture(tmp_path)
    if target == "manifest":
        manifest.write_text('{"predecessor": false}\n', encoding="utf-8")
        expected = "manifest identity"
    else:
        page = pages / ("page-001.json" if target == "source" else "page-002.json")
        row = json.loads(page.read_text(encoding="utf-8")); row["ru_markdown"] += " изменено"; page.write_text(json.dumps(row, ensure_ascii=False), encoding="utf-8")
        expected = "page identity"
    with pytest.raises(BilingualBoundaryMoveError, match=expected):
        move_pages(pages, manifest, plan_path, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_rejects_distinct_overlapping_deletions(tmp_path):
    pages, manifest, plan_path, plan = _fixture(tmp_path)
    source = json.loads((pages / "page-001.json").read_text(encoding="utf-8"))["ru_markdown"]
    text = "это. После"; start = source.encode().index(text.encode()); end = start + len(text.encode())
    plan["moves"].append({"source_page": 1, "target_page": 3, "source_span": {"start_byte": start, "end_byte": end}, "source_text": text, "source_text_sha256": _sha(text), "target_insert_byte": 0, "target_suffix": "", "rationale": "Deliberately overlaps the reviewed span."})
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(BilingualBoundaryMoveError, match="overlapping"):
        move_pages(pages, manifest, plan_path, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_mixed_insertion_and_deletion_preserves_remainder_order(tmp_path):
    pages, manifest, plan_path, plan = _fixture(tmp_path)
    page_two = json.loads((pages / "page-002.json").read_text(encoding="utf-8"))["ru_markdown"]
    text = "Конец."; start = page_two.encode().index(text.encode()); end = start + len(text.encode())
    plan["moves"].append({"source_page": 2, "target_page": 3, "source_span": {"start_byte": start, "end_byte": end}, "source_text": text, "source_text_sha256": _sha(text), "target_insert_byte": 0, "target_suffix": "", "rationale": "Exercise a page that both receives and sends exact spans."})
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    move_pages(pages, manifest, plan_path, tmp_path / "out")
    output = tmp_path / "out/pages"
    assert json.loads((output / "page-002.json").read_text(encoding="utf-8"))["ru_markdown"] == "Начало. перенеси это.\n\n"
    assert json.loads((output / "page-003.json").read_text(encoding="utf-8"))["ru_markdown"] == "Конец.Без изменений."


def test_explicit_whitespace_edit_and_cli_smoke(tmp_path):
    pages, manifest, plan_path, plan = _fixture(tmp_path)
    ru = json.loads((pages / "page-001.json").read_text(encoding="utf-8"))["ru_markdown"]
    offset = len("До:".encode()); plan["whitespace_edits"] = [{"page": 1, "span": {"start_byte": offset, "end_byte": offset + 1}, "replacement": "", "rationale": "Remove surplus paragraph separator."}]
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    command = [sys.executable, "-m", "kb_creator.scripts.move_bilingual_page_spans", "--pages", str(pages), "--manifest", str(manifest), "--plan", str(plan_path), "--output", str(tmp_path / "cli-out")]
    result = subprocess.run(command, cwd=Path(__file__).resolve().parents[2], env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[2])}, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "preliminary_boundary_successor_pending_source_binding" in result.stdout
