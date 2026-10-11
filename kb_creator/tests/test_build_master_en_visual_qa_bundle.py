from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image

from kb_creator.scripts import build_master_en_visual_qa_bundle as bundle


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def make_candidate(tmp_path: Path) -> tuple[Path, Path, Path]:
    candidate = tmp_path / "candidate"
    assets_dir = candidate / "assets"
    assets_dir.mkdir(parents=True)
    config_assets, manifest_assets = [], []
    for index in range(123):
        suffix = ".png" if index in {0, 106} else ".jpg"
        path = assets_dir / f"asset-{index:03d}{suffix}"
        Image.new("RGB", (20 + index % 4, 16 + index % 3), (index, index, index)).save(path)
        role = "front_cover" if index == 0 else "back_cover" if index == 106 else "map" if 1 <= index <= 12 else "full_page" if 13 <= index <= 25 else "handout" if 26 <= index <= 37 else "inline"
        row = {"asset_id": f"asset-{index:03d}", "origin": "source_page_render", "logical_name": path.name, "bytes": path.stat().st_size, "sha256": digest(path), "media_type": "image/png" if suffix == ".png" else "image/jpeg", "dimensions": {"width": 20 + index % 4, "height": 16 + index % 3}, "source_page": 1 if index == 0 else 124 if index == 106 else (index % 100) + 1, "source_region": {"kind": "full_media_box"}, "semantic_role": role, "representation": "reader" if index < 107 else "evidence_only", "owner_anchor": "viral" if index != 80 else "viral-handout-13", "placement_index": index if index < 107 else index + 100, "alt_text": f"asset {index}"}
        config_assets.append(row)
        manifest_assets.append({**row, "source": {"kind": "source_page_render"}, "output_path": f"assets/{path.name}", "visual_review_status": "pending_external_visual_qa"})
    manifest_assets[0]["asset_id"] = config_assets[0]["asset_id"] = "viral-render-cover-front"
    manifest_assets[106]["asset_id"] = config_assets[106]["asset_id"] = "viral-render-cover-back"
    write_json(candidate / "ASSET_MANIFEST.json", {"schema": "kb_creator.master_en_asset_manifest.v1", "scenario_id": "viral", "assets": manifest_assets, "summary": {"total": 123, "reader": 107}})
    (candidate / "MASTER_EN.md").write_text('<a id="viral"></a>\n\n<a id="viral-handout-13"></a>\n\nHey Marco Babez, test.\n', encoding="utf-8", newline="\n")
    write_json(candidate / "MASTER_EN.provenance.json", {"schema": "test"})
    write_json(candidate / "SOURCE_DISPOSITION.json", {"schema": "test"})
    write_json(candidate / "MASTER_EN.qa.json", {"metrics": {"candidate_assets": 123, "reader_assets": 107, "visual_review_units": 91}})
    (candidate / "MASTER_EN.qa.md").write_text("test\n", encoding="utf-8", newline="\n")
    rows = [{"path": p.relative_to(candidate).as_posix(), "bytes": p.stat().st_size, "sha256": digest(p)} for p in sorted((item for item in candidate.rglob("*") if item.is_file()), key=lambda item: item.relative_to(candidate).as_posix())]
    encoded = "".join(f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in rows).encode()
    write_json(candidate / "INVENTORY.json", {"schema": "kb_creator.candidate_inventory.v1", "algorithm": bundle.INVENTORY_ALGORITHM, "scope": "all regular candidate files except INVENTORY.json", "rows": rows, "file_count": 129, "total_bytes": sum(row["bytes"] for row in rows), "inventory_sha256": hashlib.sha256(encoded).hexdigest().upper()})
    source_pdf = tmp_path / "source.pdf"
    source_pdf.write_bytes(b"synthetic source PDF")
    reviews = [{"review_id": f"review-{index:03d}", "classification": "physical_handout" if index == 80 else "illustration", "owner_anchor": "viral-handout-13" if index == 80 else "viral", "source_pages": [80 if index == 80 else 1], "asset_ids": [] if index == 80 else [config_assets[index % 107]["asset_id"]], "review_requirements": ["reader-scale"], "special_requirement": "Babez" if index == 80 else "", "status": "pending_external_visual_qa"} for index in range(91)]
    config = {"schema": "kb_creator.master_en_publication.v1", "scenario_id": "viral", "contract": {}, "accepted_reconstruction": {}, "document": {"source_pdf": {"bytes": source_pdf.stat().st_size, "sha256": digest(source_pdf), "page_count": 124}}, "hierarchy": [], "source_disposition": [], "xrefs": [], "handouts": [], "structured_content": [], "assets": config_assets, "visual_review_units": reviews, "reader_noise_patterns": [], "reader_surface": {"schema_version": "kb_creator.master_en_reader_surface.v1", "heading_policy": {}, "semantic_fragments": [{} for _ in range(25)], "authorized_suppressions": [{} for _ in range(22)], "alt_policy": {}}}
    config_path = tmp_path / "config.json"
    write_json(config_path, config)
    return candidate, config_path, source_pdf


def fake_poppler(monkeypatch: pytest.MonkeyPatch) -> None:
    class Result:
        stdout = "pdftoppm 1.0"
        stderr = ""
    def run(command, **_kwargs):
        if "-singlefile" in command:
            Image.new("RGB", (200, 300), "white").save(Path(command[-1] + ".png"))
        return Result()
    monkeypatch.setattr(bundle.subprocess, "run", run)


def run_bundle(candidate: Path, config: Path, source: Path, monkeypatch: pytest.MonkeyPatch, output: Path) -> None:
    fake_poppler(monkeypatch)
    args = ["--candidate-root", str(candidate), "--publication-config", str(config), "--source-pdf", str(source), "--output-root", str(output), "--pdftoppm", "fake-pdftoppm"]
    monkeypatch.setattr("sys.argv", ["bundle"] + args)
    bundle.main()


def test_builds_closed_deterministic_bundle_and_preserves_candidate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    candidate, config, source = make_candidate(tmp_path)
    first = tmp_path / "first"
    run_bundle(candidate, config, source, monkeypatch, first)
    candidate_digest = digest(candidate / "INVENTORY.json")
    # A second absent output proves the generated contents are stable, without mutating inputs.
    second = tmp_path / "second"
    run_bundle(candidate, config, source, monkeypatch, second)
    first_manifest, second_manifest = (first / "VISUAL_QA_BUNDLE.json").read_bytes(), (second / "VISUAL_QA_BUNDLE.json").read_bytes()
    assert first_manifest == second_manifest
    assert digest(candidate / "INVENTORY.json") == candidate_digest
    data = json.loads(first_manifest)
    assert data["counts"] == {"candidate_assets": 123, "reader_assets": 107, "visual_review_units": 91, "tiles": 107, "contact_sheets": 27, "priority_originals": 39, "open_generation_errors": 0}
    assert len(list((first / "tiles").glob("*.png"))) == 107
    assert len(list((first / "contact_sheets").glob("*.png"))) == 27
    assert data["p80_render"]["source_page"] == 80
    assert data["babez_owner_block"]["exact_visible_text"] == "Hey Marco Babez"
    assert len(data["priority_assets"]) == 39
    assert {row["asset_id"] for row in data["priority_assets"]} >= {"viral-render-cover-front", "viral-render-cover-back"}
    for row in data["priority_assets"]:
        transported = first / row["transported_path"]
        source = candidate / row["original_candidate_path"]
        assert transported.read_bytes() == source.read_bytes()
        assert row["transported_identity"]["sha256"] == digest(source)


def test_rejects_priority_transport_byte_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    candidate, config, source = make_candidate(tmp_path)
    inventory_hash = digest(candidate / "INVENTORY.json")
    _, _, _, priorities, _ = bundle.validate_inputs(candidate, config, source, tmp_path / "absent")
    actual_copy = bundle.shutil.copyfile
    def corrupt_copy(origin: Path, destination: Path) -> str:
        actual_copy(origin, destination)
        destination.write_bytes(b"corrupt")
        return str(destination)
    monkeypatch.setattr(bundle.shutil, "copyfile", corrupt_copy)
    with pytest.raises(ValueError, match="priority transport bytes"):
        bundle.transport_priority_originals(candidate, priorities, tmp_path / "transport")
    assert digest(candidate / "INVENTORY.json") == inventory_hash


@pytest.mark.parametrize("mutation", ["bad_hash", "bad_dimensions", "bad_count", "bad_review_path", "missing_reader_surface", "unexpected_reader_surface_key", "wrong_reader_surface_version", "wrong_reader_surface_counts"])
def test_rejects_schema_or_asset_errors_before_creating_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str) -> None:
    candidate, config, source = make_candidate(tmp_path)
    if mutation == "bad_hash":
        manifest = json.loads((candidate / "ASSET_MANIFEST.json").read_text(encoding="utf-8")); manifest["assets"][0]["sha256"] = "0" * 64; write_json(candidate / "ASSET_MANIFEST.json", manifest)
    elif mutation == "bad_dimensions":
        manifest = json.loads((candidate / "ASSET_MANIFEST.json").read_text(encoding="utf-8")); manifest["assets"][0]["dimensions"] = {"width": 1, "height": 1}; write_json(candidate / "ASSET_MANIFEST.json", manifest)
    elif mutation == "bad_count":
        payload = json.loads(config.read_text(encoding="utf-8")); payload["visual_review_units"].pop(); write_json(config, payload)
    elif mutation == "bad_review_path":
        payload = json.loads(config.read_text(encoding="utf-8")); payload["visual_review_units"][0]["asset_ids"] = ["unknown"]; write_json(config, payload)
    elif mutation == "missing_reader_surface":
        payload = json.loads(config.read_text(encoding="utf-8")); del payload["reader_surface"]; write_json(config, payload)
    elif mutation == "unexpected_reader_surface_key":
        payload = json.loads(config.read_text(encoding="utf-8")); payload["reader_surface"]["unexpected"] = True; write_json(config, payload)
    elif mutation == "wrong_reader_surface_version":
        payload = json.loads(config.read_text(encoding="utf-8")); payload["reader_surface"]["schema_version"] = "kb_creator.master_en_reader_surface.v0"; write_json(config, payload)
    else:
        payload = json.loads(config.read_text(encoding="utf-8")); payload["reader_surface"]["semantic_fragments"].pop(); payload["reader_surface"]["authorized_suppressions"].pop(); write_json(config, payload)
    output = tmp_path / "must-stay-absent"
    with pytest.raises(ValueError, match="E_VISUAL_QA_BUNDLE"):
        bundle.validate_inputs(candidate, config, source, output)
    assert not output.exists()


def make_v2_inputs(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    (tmp_path / ".git").mkdir()
    candidate = tmp_path / "candidate-v2"; (candidate / "assets").mkdir(parents=True)
    source = tmp_path / "source.pdf"; source.write_bytes(b"synthetic v2 PDF")
    image = candidate / "assets" / "map.png"; Image.new("RGB", (20, 20), "navy").save(image)
    kinds = ["heading_outline", "callout", "ordered_list_callout", "table", "equipment_card", "creature_statblock", "inline_run_in", "full_page_map", "physical_page_pair", "xref_recovery", "asset_placement"]
    events = [{"event_id": f"e{index}", "page": index + 1, "type": "heading" if kind == "heading_outline" else "structured_unit", "content": {"kind": kind}} for index, kind in enumerate(kinds[:-2])]
    events.append({"event_id": "e9", "page": 10, "type": "text_fragment", "content": "xref"})
    master_parts = [f"Reader excerpt {row['event_id']}" for row in events]
    master = "\n\n".join(master_parts) + "\n"
    (candidate / "MASTER_EN.md").write_text(master, encoding="utf-8", newline="\n")
    ledger, cursor = [], 0
    for row, excerpt in zip(events, master_parts):
        start, end = cursor, cursor + len(excerpt)
        ledger.append({"event_id": row["event_id"], "start_char": start, "end_char": end, "slice_sha256": digest_text(excerpt)})
        cursor = end + 2
    asset = {"asset_id": "map", "source_page": 11, "disposition": "reader", "binary": {"path": "kb_creator/working/synthetic/map.png", "bytes": image.stat().st_size, "sha256": digest(image)}}
    units = []
    for index, kind in enumerate(kinds):
        units.append({"review_id": f"r{index}", "kind": kind, "source_pages": [index + 1], "event_ids": [f"e{index}"] if index < 10 else [], "asset_ids": ["map"] if kind == "asset_placement" else [], "priority": index % 2 == 0, "contact_sheet_group": f"g{index % 3}"})
    dispositions = [{"page": page, "publication_disposition": "excluded_advertising" if page in {123, 124} else "reader"} for page in range(1, 125)]
    config = {"schema": "kb_creator.master_en_publication.v2", "scenario_id": "synthetic", "events": events, "assets": [asset], "source_disposition": dispositions, "visual_review_units": units}
    config_path = tmp_path / "config-v2.json"; write_json(config_path, config)
    write_json(candidate / "MASTER_EN.provenance.json", {"events": ledger})
    write_json(candidate / "ASSET_MANIFEST.json", {"assets": [{"asset_id": "map", "reader_value": True, "output_path": "assets/map.png", "bytes": image.stat().st_size, "sha256": digest(image)}]})
    report = tmp_path / "report.json"; write_json(report, {"status": "verified_v2_candidate", "candidate_root_name": candidate.name, "publication_config_sha256": digest(config_path), "source_pdf_sha256": digest(source)})
    return candidate, config_path, source, report


def fake_v2_report_validator(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bundle, "validate_v2_verification_report", lambda *_args: {"status": "validated_v2_verification_report"})


def test_v2_bundle_is_dynamic_kind_complete_and_excludes_advertising(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    candidate, config, source, report = make_v2_inputs(tmp_path); fake_v2_report_validator(monkeypatch); fake_poppler(monkeypatch)
    output = tmp_path / "v2-output"; result = bundle.write_v2_bundle(candidate, config, source, report, output, "fake-pdftoppm")
    assert result["counts"]["visual_review_units"] == 11
    assert {row["kind"] for row in result["review_rows"]} == {row["kind"] for row in json.loads(config.read_text())["visual_review_units"]}
    assert {row["page"] for row in result["excluded_audit_rows"]} == {123, 124}
    assert not (output / "source_crops" / "p123.png").exists()
    assert (output / "review.html").is_file()
    asset_row = next(row for row in result["review_rows"] if row["kind"] == "asset_placement")
    assert asset_row["assets"][0]["declaration"]["disposition"] == "reader"
    assert asset_row["assets"][0]["review_path"] == "reader_assets/map.png"
    assert (output / "reader_assets" / "map.png").read_bytes() == (candidate / "assets" / "map.png").read_bytes()
    html = (output / "review.html").read_text(encoding="utf-8")
    assert "Reader excerpt e0" in html
    assert 'src="source_crops/p001.png"' in html
    assert 'src="reader_assets/map.png"' in html
    assert result["counts"]["reader_asset_copies"] == 1


@pytest.mark.parametrize("mutation", ["report", "excluded_page", "missing_event", "bad_asset", "existing_output"])
def test_v2_rejects_tampering_before_or_during_generation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str) -> None:
    candidate, config, source, report = make_v2_inputs(tmp_path); fake_v2_report_validator(monkeypatch); fake_poppler(monkeypatch)
    payload = json.loads(config.read_text())
    output = tmp_path / "v2-output"
    if mutation == "report":
        report_payload = json.loads(report.read_text()); report_payload["source_pdf_sha256"] = "0" * 64; write_json(report, report_payload)
    elif mutation == "excluded_page":
        payload["visual_review_units"][0]["source_pages"] = [123]; write_json(config, payload)
    elif mutation == "missing_event":
        payload["visual_review_units"][0]["event_ids"] = ["missing"]; write_json(config, payload)
    elif mutation == "bad_asset":
        payload["visual_review_units"][-1]["asset_ids"] = ["missing"]; write_json(config, payload)
    else:
        output.mkdir()
    with pytest.raises(ValueError, match="E_VISUAL_QA_BUNDLE"):
        bundle.write_v2_bundle(candidate, config, source, report, output, "fake-pdftoppm")
