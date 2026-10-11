from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

pytest.importorskip("docx")
pytest.importorskip("lxml")
pytest.importorskip("PIL")

from PIL import Image

from kb_creator.pipeline import five_step_docx as subject
from kb_creator.tests.fidelity_fixture import synthetic_guard


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _refresh_projection(root: Path) -> None:
    path = root / "semantic_context" / "RU_PROJECTION.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["master_ru"] = {"path": "MASTER_RU.md", "bytes": (root / "MASTER_RU.md").stat().st_size, "sha256": _sha(root / "MASTER_RU.md")}
    value["units"][0]["ru_text"] = (root / "MASTER_RU.md").read_text(encoding="utf-8").strip()
    value["units"][0]["ru_sha256"] = hashlib.sha256(value["units"][0]["ru_text"].encode("utf-8")).hexdigest().upper()
    value.pop("projection_sha256", None)
    value["projection_sha256"] = hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest().upper()
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def _build(master: Path, output: Path, *, title: str) -> dict:
    config, options, plan, _ = synthetic_guard(master, output.parent / f"guard-{output.name}", title=title)
    return subject.build_docx_package(master, output, title=title, config=config,
                                      reader_options=options, fidelity_plan=plan)


@pytest.fixture
def master_ru(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "master-ru"
    (root / "assets").mkdir(parents=True)
    Image.new("RGB", (24, 16), "white").save(root / "assets" / "map.png")
    (root / "MASTER_RU.md").write_text(
        "<!-- source-page-001 -->\n\n<a id=\"intro\"></a>\n# Заголовок\n\n"
        "См. [начало](#intro).  \nСледующая строка.\n\n"
        "| Характеристика | Значение |\n| --- | --- |\n| СИЛ | 50 |\n\n"
        "> **Хранитель:** СИЛ 50\n\n![Карта](assets/map.png)\n",
        encoding="utf-8", newline="\n",
    )
    asset = root / "assets" / "map.png"
    (root / "ASSET_MANIFEST.json").write_text(json.dumps({"assets": [{"path": "assets/map.png", "bytes": asset.stat().st_size, "sha256": _sha(asset)}]}), encoding="utf-8")
    (root / "MASTER_RU.manifest.json").write_text("{}\n", encoding="utf-8")
    (root / "PROOFREAD_LEDGER.json").write_text("{}\n", encoding="utf-8")
    (root / "INVENTORY.json").write_text("{}\n", encoding="utf-8")
    (root / "semantic_context").mkdir()
    (root / "semantic_context" / "source.json").write_text('{"role":"source"}\n', encoding="utf-8")
    projection = {
        "schema": "kb_creator.five_step_ru_projection.v3",
        "master_en": {"path": "evidence/MASTER_EN.md", "bytes": 1, "sha256": "0" * 64},
        "master_ru": {"path": "MASTER_RU.md", "bytes": (root / "MASTER_RU.md").stat().st_size, "sha256": _sha(root / "MASTER_RU.md")},
        "unit_order": ["unit-001"],
        "units": [{"unit_id": "unit-001", "source_hash": "0" * 64, "parent_unit_id": None, "part_index": None, "part_count": None, "ru_text": (root / "MASTER_RU.md").read_text(encoding="utf-8").strip(), "ru_sha256": ""}],
        "spans": [],
    }
    statblock = "> **Хранитель:** СИЛ 50\n"
    start = projection["units"][0]["ru_text"].index(statblock)
    projection["spans"] = [{"span_id": "stats.1", "semantic_kind": "statblock", "source_span_id": "source-keeper-001", "unit_ids": ["unit-001"], "start": {"unit_id": "unit-001", "char_offset": start}, "end": {"unit_id": "unit-001", "char_offset": start + len(statblock)}, "source_sha256": "1" * 64}]
    projection["units"][0]["ru_sha256"] = hashlib.sha256(projection["units"][0]["ru_text"].encode("utf-8")).hexdigest().upper()
    projection["projection_sha256"] = hashlib.sha256(json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest().upper()
    (root / "semantic_context" / "RU_PROJECTION.json").write_text(json.dumps(projection, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr("kb_creator.pipeline.five_step_language.verify_language_result", lambda value: {"state": "verified"})
    return root


def test_rejects_dropped_table_inside_callout(master_ru: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    master = master_ru / "MASTER_RU.md"
    with master.open("a", encoding="utf-8") as stream:
        stream.write("\n> | Предмет | Цена |\n> | --- | --- |\n> | Книга | 5 |\n")
    _refresh_projection(master_ru)
    monkeypatch.setattr(subject, "build_docx_projection", lambda *args, **kwargs: {"tables": 1, "images": 1})
    with pytest.raises(subject.FiveStepDocxError, match=r"tables expected>=2, actual=1"):
        _build(master_ru, tmp_path / "dropped-table", title="Проверка")


def test_builds_neutral_docx_and_preserves_required_structure(master_ru: Path, tmp_path: Path) -> None:
    result = _build(master_ru, tmp_path / "docx-001", title="Нейтральный документ")

    assert result["state"] == "built_pending_render"
    manifest = json.loads(result["manifest_path"].read_text(encoding="utf-8"))
    assert manifest["schema"] == "kb_creator.five_step_docx_package.v3"
    assert manifest["profile"] == "five_step_docx_v3"
    assert not (result["manifest_path"].parent / "internal.html").exists()
    assert not any(path.suffix.lower() in {".html", ".htm", ".pdf"}
                   for path in result["manifest_path"].parent.rglob("*") if path.is_file())
    assert manifest["docx"]["build"]["tables"] >= 1
    assert manifest["docx"]["build"]["images"] == 1
    assert manifest["projection"]["markdown"]["statblocks"] == 1
    assert manifest["config"]["path"] == "docx_config.json"
    config = json.loads((result["manifest_path"].parent / "docx_config.json").read_text(encoding="utf-8"))
    assert config["metadata"]["title"] == "Нейтральный документ"
    assert "Вирус" not in json.dumps(config, ensure_ascii=False)
    assert (result["manifest_path"].parent / "semantic_context" / "source.json").is_file()
    verified = subject.verify_docx_package(result["manifest_path"].parent)
    assert verified["status"] == "verified_pending_visual_review"


def test_representative_sealed_v1_archive_verifies_read_only(master_ru: Path, tmp_path: Path) -> None:
    built = _build(master_ru, tmp_path / "current", title="Исторический архив")
    archive_root = tmp_path / "historical-v1"
    shutil.copytree(built["manifest_path"].parent, archive_root)
    transport = archive_root / "internal.html"
    transport.write_text("<html><body>Historical Word transport snapshot</body></html>\n", encoding="utf-8")
    manifest_path = archive_root / "DOCX_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.pop("manifest_sha256")
    manifest.pop("projection_transport_sha256")
    manifest["schema"] = subject.LEGACY_SCHEMA
    manifest["profile"] = "five_step_docx_v1"
    manifest["internal_html"] = subject._identity(transport, archive_root)
    manifest["projection"]["transport"] = "html"
    manifest["inventory"] = subject._inventory(archive_root)
    manifest["manifest_sha256"] = hashlib.sha256(subject._canonical(manifest)).hexdigest().upper()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    before = {p.relative_to(archive_root).as_posix(): _sha(p) for p in archive_root.rglob("*") if p.is_file()}
    result = subject.verify_docx_package(archive_root)
    after = {p.relative_to(archive_root).as_posix(): _sha(p) for p in archive_root.rglob("*") if p.is_file()}
    assert result["status"] == "legacy_verified_source_completeness_not_assessed"
    assert before == after


@pytest.mark.parametrize("reference", ["assets/missing.png", "../outside.png"])
def test_rejects_missing_or_escaping_asset(master_ru: Path, tmp_path: Path, reference: str) -> None:
    master = master_ru / "MASTER_RU.md"
    master.write_text(master.read_text(encoding="utf-8").replace("assets/map.png", reference), encoding="utf-8", newline="\n")
    with pytest.raises(subject.FiveStepDocxError):
        _build(master_ru, tmp_path / "broken", title="Тест")


def test_rejects_dropped_asset_manifest_binding(master_ru: Path, tmp_path: Path) -> None:
    manifest = master_ru / "ASSET_MANIFEST.json"
    value = json.loads(manifest.read_text(encoding="utf-8")); value["assets"][0]["sha256"] = "0" * 64
    manifest.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(subject.FiveStepDocxError, match="asset manifest"):
        _build(master_ru, tmp_path / "broken", title="Тест")


def test_verifier_rejects_stale_inventory(master_ru: Path, tmp_path: Path) -> None:
    result = _build(master_ru, tmp_path / "docx-001", title="Тест")
    package = result["manifest_path"].parent
    (package / "MASTER_RU.md").write_text("# Повреждено\n", encoding="utf-8")
    with pytest.raises(subject.FiveStepDocxError, match="inventory"):
        subject.verify_docx_package(package)


def test_reuses_one_asset_for_multiple_markdown_occurrences(master_ru: Path, tmp_path: Path) -> None:
    master = master_ru / "MASTER_RU.md"
    master.write_text(master.read_text(encoding="utf-8") + "\n![Повтор](assets/map.png)\n", encoding="utf-8", newline="\n")
    _refresh_projection(master_ru)
    result = _build(master_ru, tmp_path / "docx-001", title="Тест")
    manifest = json.loads(result["manifest_path"].read_text(encoding="utf-8"))
    assert len(manifest["asset_plan"]) == 1
    assert manifest["projection"]["markdown"]["image_occurrences"] == 2
    assert manifest["docx"]["build"]["images"] == 2


def test_published_access_failure_quarantines_new_package(master_ru, tmp_path, monkeypatch):
    output = tmp_path / "docx-001"
    def fail(path):
        assert path == output
        assert (path / "DOCX_MANIFEST.json").is_file()
        raise RuntimeError("desktop read grant failed")
    monkeypatch.setattr(subject, "normalize_publication_access_if_managed", fail)
    with pytest.raises(RuntimeError, match="desktop read grant"):
        _build(master_ru, output, title="Тест")
    assert not output.exists()
    quarantines = list(tmp_path.glob(".docx-001.quarantine.*"))
    assert len(quarantines) == 1
    assert (quarantines[0] / "docx/document.docx").is_file()


def test_post_publish_access_callback_cannot_change_artifact_bytes(master_ru, tmp_path, monkeypatch):
    output = tmp_path / "docx-001"
    def corrupt(path):
        (path / "MASTER_RU.md").write_text("altered", encoding="utf-8")
    monkeypatch.setattr(subject, "normalize_publication_access_if_managed", corrupt)
    with pytest.raises(subject.FiveStepDocxError, match="inventory"):
        _build(master_ru, output, title="Тест")
    assert not output.exists()


def test_projection_uses_shared_split_assembly_offsets(master_ru: Path) -> None:
    master = master_ru / "MASTER_RU.md"
    master.write_text("Первая часть вторая часть\n\nСИЛ 50\nНавыки: Внимание 25%.\n![Портрет](assets/map.png)\n", encoding="utf-8")
    projection_path = master_ru / "semantic_context/RU_PROJECTION.json"
    value = {
        "schema": "kb_creator.five_step_ru_projection.v3",
        "master_en": {"path": "evidence/MASTER_EN.md", "bytes": 1, "sha256": "0" * 64},
        "master_ru": {"path": "MASTER_RU.md", "bytes": master.stat().st_size, "sha256": _sha(master)},
        "unit_order": ["split__part01", "split__part02", "stats"],
        "units": [
            {"unit_id": "split__part01", "source_hash": "A" * 64, "parent_unit_id": "split", "part_index": 1, "part_count": 2, "ru_text": "Первая часть", "ru_sha256": hashlib.sha256("Первая часть".encode()).hexdigest().upper()},
            {"unit_id": "split__part02", "source_hash": "A" * 64, "parent_unit_id": "split", "part_index": 2, "part_count": 2, "ru_text": "вторая часть", "ru_sha256": hashlib.sha256("вторая часть".encode()).hexdigest().upper()},
            {"unit_id": "stats", "source_hash": "B" * 64, "parent_unit_id": None, "part_index": None, "part_count": None, "ru_text": "СИЛ 50\nНавыки: Внимание 25%.\n![Портрет](assets/map.png)", "ru_sha256": hashlib.sha256("СИЛ 50\nНавыки: Внимание 25%.\n![Портрет](assets/map.png)".encode()).hexdigest().upper()},
        ],
        "spans": [{"span_id": "stats.1", "semantic_kind": "statblock", "source_span_id": "source-stats", "unit_ids": ["stats"], "start": {"unit_id": "stats", "char_offset": 0}, "end": {"unit_id": "stats", "char_offset": len("СИЛ 50\nНавыки: Внимание 25%.")}, "source_sha256": "C" * 64}],
    }
    value["projection_sha256"] = hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()
    projection_path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    loaded = subject._semantic_projection(master_ru, master, master.read_text(encoding="utf-8"))
    transported, spans = subject._transport_semantic_spans(master.read_text(encoding="utf-8"), loaded, loaded["spans"])
    assert spans[0]["start_offset"] == len("Первая часть вторая часть\n\n")
    assert spans[0]["visible_text"].endswith("Внимание 25%.")
    assert "semantic-span-end: statblock" in transported
