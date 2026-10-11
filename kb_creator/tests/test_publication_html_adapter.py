from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

import pytest

from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline.publication_adapters import PublicationAdapterError, build_html_candidate
from kb_creator.pipeline import publication_adapters as adapters


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value) + b"\n")


def _sealed(schema: str, payload: dict, key: str) -> dict:
    value = {"schema": schema, **payload}
    value[key] = sha256_bytes(canonical_bytes(value))
    return value


def _identity(path: Path, root: Path) -> dict:
    return {"path": path.relative_to(root).as_posix(), **file_identity(path)}


def _asset_inventory_sha(rows: list[dict]) -> str:
    value = "".join(
        f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n"
        for row in sorted(rows, key=lambda item: item["path"])
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _reseal(path: Path, key: str) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    value.pop(key, None)
    value[key] = sha256_bytes(canonical_bytes(value))
    _write(path, value)
    return value


def _frontmatter_manifest(report: Path, *, toc_mode: str = "generated") -> None:
    _write(report.parent / "frontmatter_manifest.json", {
        "toc": {"mode": toc_mode, "origin": "source" if toc_mode == "preserve_and_link" else "generated"},
        "credits": {"pages": []}, "body": {"starts_at": "002"}, "flow": ["page-001", "toc:generated", "page-002"],
    })


def _build(item: dict, runner=None, *, python: Path | None = None, semantic_authority: Path | None = None) -> dict:
    runtime = python or Path(sys.executable)
    if runner is None and python is None:
        def runner(_command, target, report):
            target.write_text('<html><img src="assets/art.png"></html>', encoding="utf-8")
            _frontmatter_manifest(report)
            _write(report, {"status": "pass", "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
            return 0
    return build_html_candidate(
        master_ru=item["master"], master_ru_acceptance=item["acceptance"], artview_decisions=item["decisions"],
        artview_application=item["application"], effective_visual_config=item["effective"], artview_projection_root=item["projection"],
        base_config=item["config"], staging=item["stage"], output_name="Sample_RU.html", python=runtime, runner=runner,
        semantic_authority=semantic_authority,
    )


def _assert_retired_without_output(item: dict, action) -> None:
    with pytest.raises(PublicationAdapterError, match="legacy HTML/DOCX/PDF publication writer is retired"):
        action()
    assert not any((item["stage"] / "artifacts").iterdir())
    assert not any((item["stage"] / "evidence").iterdir())


def _fixture(tmp_path: Path) -> dict:
    run = tmp_path / "run"; stage = run / "local" / "staging" / "40-html-candidate"
    (stage / "artifacts").mkdir(parents=True); (stage / "evidence").mkdir()
    master = run / "outputs" / "21-master-ru-candidate" / "artifacts" / "MASTER_RU.md"
    master.parent.mkdir(parents=True)
    source_asset = master.parent / "assets" / "source.png"
    source_asset.parent.mkdir(); source_asset.write_bytes(b"png")
    master.write_text(
        "<!-- source-page-001 -->\n\n"
        "# Synthetic\n\n<!-- source-page-002 -->\n\n"
        "## Notes\n"
        "First measured line 1  \n"
        "Second measured line 2  \n"
        "Third measured line 3\n\n"
        "This prose keeps the ordinary section open.\n\n"
        "> STR 50  \n"
        "> CON 60\n\n"
        "![Art](assets/source.png)\n\n"
        "## УСЛОВНЫЙ ПРОТИВНИК\n"
        "POWER 50  \n"
        "ENDURANCE 60  \n"
        "Defense: 35%  \n"
        "Move: 8\n",
        encoding="utf-8", newline="\n",
    )
    master_asset_manifest = master.parent / "ASSET_MANIFEST.json"
    source_record = _identity(source_asset, master.parent)
    _write(master_asset_manifest, {
        "schema": "kb_creator.master_ru_asset_manifest.v1", "scenario_id": "sample",
        "assets": [source_record], "summary": {"total": 1},
    })
    acceptance = run / "acceptance" / "master_ru.acceptance.json"
    _write(acceptance, _sealed("kb_creator.artifact_acceptance.v1", {
        "scenario_id": "sample", "artifact_kind": "master_ru",
        "candidate": {"path": master.relative_to(run).as_posix(), **file_identity(master)},
        "producer_stage": {"path": master.relative_to(run).as_posix(), **file_identity(master)},
        "evidence": [{"path": master.relative_to(run).as_posix(), **file_identity(master)}],
        "decision": "accepted", "decision_at_utc": "2026-09-14T00:00:00Z",
        "user_decision_reference": "synthetic explicit acceptance", "recorder_role": "main_orchestrator",
    }, "receipt_sha256"))
    decisions = run / "acceptance" / "artview.decisions.json"
    _write(decisions, _sealed("kb_creator.scenario_artview_decisions.v3", {"scenario_id": "sample", "state": "accepted", "bindings": {}, "decisions": [], "review": {"state": "closed", "reviewed_count": 0, "unresolved_asset_ids": []}}, "decisions_sha256"))
    manifest = run / "outputs" / "30-artview-bundle" / "artifacts" / "candidate_manifest.json"
    candidate_current = manifest.parent / "assets" / "current" / "art.png"
    candidate_current.parent.mkdir(parents=True); candidate_current.write_bytes(source_asset.read_bytes())
    _write(manifest, {
        "schema": "kb_creator.scenario_artview_candidate.v3", "scenario_id": "sample",
        "bindings": {
            "master_ru": _identity(master, run),
            "master_ru_asset_manifest": _identity(master_asset_manifest, run),
        },
        "rows": [{
            "asset_id": "art",
            "current": {
                **_identity(candidate_current, manifest.parent),
                "source_graph_membership": [{"role": "accepted_reconstruction_asset", "identity": source_record}],
            },
        }],
    })
    profile = run / "outputs" / "30-artview-bundle" / "evidence" / "profile.runtime.json"
    _write(profile, {"schema": "fixture-profile"})
    artview_acceptance = run / "acceptance" / "artview.acceptance.json"
    _write(artview_acceptance, _sealed("kb_creator.artifact_acceptance.v1", {
        "scenario_id": "sample", "artifact_kind": "artview",
        "candidate": _identity(manifest, run),
        "producer_stage": _identity(manifest, run),
        "evidence": [_identity(decisions, run)],
        "decision": "accepted", "decision_at_utc": "2026-09-14T00:00:00Z",
        "user_decision_reference": "synthetic explicit acceptance", "recorder_role": "main_orchestrator",
    }, "receipt_sha256"))
    projection = run / "outputs" / "31-artview-apply" / "artifacts"
    (projection / "assets").mkdir(parents=True); (projection / "assets" / "art.png").write_bytes(b"png")
    projected_asset = projection / "assets" / "art.png"
    projected_record = _identity(projected_asset, projection)
    reader_projection = projection / "reader_projection.json"
    projection_row = {
        "asset_id": "art", "anchor": "synthetic", "status": "included",
        "source_choice": "keep_current", "candidate_id": None,
        "output_path": "assets/art.png",
        "presentation": {"alignment": "center", "width_percent": 100, "wrap_text": False, "wrap_tables": False},
    }
    _write(reader_projection, _sealed("kb_creator.scenario_artview_reader_projection.v3", {
        "scenario_id": "sample", "rows": [projection_row],
    }, "projection_sha256"))
    effective = projection / "effective_visual_config.json"
    _write(effective, _sealed("kb_creator.scenario_artview_effective_visual_config.v3", {
        "scenario_id": "sample", "decision_bindings": {},
        "rows": [{"asset_id": "art", "output_path": "assets/art.png", "presentation": projection_row["presentation"]}],
    }, "config_sha256"))
    application = projection / "ARTVIEW_APPLIED.json"
    _write(application, _sealed("kb_creator.scenario_artview_application.v3", {
        "scenario_id": "sample",
        "inputs": {
            "profile": _identity(profile, run), "candidate_manifest": _identity(manifest, run),
            "decisions": _identity(decisions, run), "artview_acceptance": _identity(artview_acceptance, run),
        },
        "reader_projection": _identity(reader_projection, projection),
        "effective_visual_config": _identity(effective, projection),
        "assets": [projected_record], "assets_inventory_sha256": _asset_inventory_sha([projected_record]),
        "counts": {"reviewed": 1, "included": 1, "excluded": 0},
    }, "application_sha256"))
    config = run / "local" / "configs" / "html.json"
    _write(config, {
        "production_html": {"typography": {"body_font_size": "10pt"}},
        "html_publication_policy": {
            "schema": "kb_creator.html_publication_policy.v1", "state": "stage40_ready",
            "page_roles": [{"source_page": 1, "role": "cover"}, {"source_page": 2, "role": "body"}],
            "frontmatter_order": ["cover", "toc", "body"], "cover": {"source_page": 1},
            "credits": {"mode": "none", "source_pages": []},
            "toc": {"mode": "generated", "source_page": None, "title": "Оглавление", "entries": []},
            "body_start_page": 2,
        },
    })
    return locals()


def _enable_required_cover_v2(item: dict) -> None:
    projection_path = item["reader_projection"]
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    projection["rows"][0].update({
        "placement_id": "source-cover-page-001",
        "semantic_role": "cover",
        "placement_target": "source_page_cover",
        "required": True,
        "source_page": 1,
    })
    projection.pop("projection_sha256")
    projection["projection_sha256"] = sha256_bytes(canonical_bytes(projection))
    _write(projection_path, projection)

    application_path = item["application"]
    application = json.loads(application_path.read_text(encoding="utf-8"))
    application["reader_projection"] = _identity(projection_path, item["projection"])
    application.pop("application_sha256")
    application["application_sha256"] = sha256_bytes(canonical_bytes(application))
    _write(application_path, application)

    config = json.loads(item["config"].read_text(encoding="utf-8"))
    policy = config["html_publication_policy"]
    policy["schema"] = "kb_creator.html_publication_policy.v2"
    policy["cover"] = {
        "source_page": 1,
        "placement_id": "source-cover-page-001",
        "required": True,
        "render_mode": "replace_source_page",
        "fit": "contain",
    }
    _write(item["config"], config)


def _semantic_authority(item: dict, *, representation: str = "semantic_span") -> Path:
    authority = item["run"] / "outputs" / "10-master-en-candidate" / "evidence" / "master_en_authority" / "upstream"
    decision_path = authority / "evidence" / "review" / "pages" / "page-002.json"
    ru_blocks = [part.strip() for part in re.split(r"\n[ \t]*\n", item["master"].read_text(encoding="utf-8").strip())]
    ru_stat = next(block for block in ru_blocks if block.startswith("## УСЛОВНЫЙ ПРОТИВНИК"))
    en_stat = ru_stat.replace("## УСЛОВНЫЙ ПРОТИВНИК", "## CONDITIONAL OPPONENT", 1)
    en_blocks = [en_stat if block == ru_stat else block for block in ru_blocks]
    page_mark = en_blocks.index("<!-- source-page-002 -->")
    page_markdown = "\n\n".join(en_blocks[page_mark + 1:])
    page_lines = page_markdown.splitlines()
    start = page_lines.index("## CONDITIONAL OPPONENT") + 1
    end = len(page_lines)
    span_text = "\n".join(page_lines[start - 1:end])
    span_sha = hashlib.sha256(span_text.encode("utf-8")).hexdigest().upper()
    _write(decision_path, {
        "source_page": 2,
        "markdown": page_markdown,
        "semantic_structure": {
            "units": [{
                "id": "synthetic-statblock", "kind": "statblock", "representation": representation,
                "container_parent": None,
                "markdown_span": {"start_line": start, "end_line": end, "sha256": span_sha},
            }],
        },
    })
    sidecar_path = authority / "content" / "SEMANTIC_STRUCTURE.json"
    _write(sidecar_path, {
        "schema": "kb_creator.reconstruction_semantic_structure.v1",
        "pages": [{
            "source_page": 2,
            "units": [{
                "id": "synthetic-statblock", "kind": "statblock", "representation": representation,
                "markdown_span_sha256": span_sha,
            }],
        }],
        "page_decisions": [{"source_page": 2, "sha256": file_identity(decision_path)["sha256"]}],
    })
    manifest_path = authority / "RECONSTRUCTION_MANIFEST.json"
    _write(manifest_path, _sealed("kb_creator.reconstruction_manifest.v1", {
        "candidate": {"files": [
            {"path": "SEMANTIC_STRUCTURE.json", **file_identity(sidecar_path)},
            {"path": "pages/page-002.md", **file_identity(_page_file(authority, page_markdown))},
        ]},
        "review": {"decisions": [_identity(decision_path, authority)]},
    }, "manifest_sha256"))
    _write(authority / "RECONSTRUCTION_INVENTORY.json", {
        "schema": "kb_creator.reconstruction_upstream_inventory.v1",
        "artifacts": [{"role": "reconstruction_manifest", **_identity(manifest_path, authority)}],
    })
    _semantic_translation_lineage(item, en_blocks)
    return authority


def _page_file(authority: Path, markdown: str) -> Path:
    path = authority / "content" / "pages" / "page-002.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("<!-- source-page-002 -->\n\n" + markdown + "\n", encoding="utf-8")
    return path


def _semantic_translation_lineage(item: dict, en_blocks: list[str]) -> None:
    """Install a minimal closed Stage20/21 lineage with distinct EN/RU payloads."""
    run = item["run"]; master = item["master"]
    master_en = run / "outputs" / "10-master-en-candidate" / "artifacts" / "MASTER_EN.md"
    master_en.parent.mkdir(parents=True, exist_ok=True)
    master_en.write_text("\n\n".join(en_blocks) + "\n", encoding="utf-8")
    acceptance = run / "acceptance" / "master_en.acceptance.json"
    _write(acceptance, _sealed("kb_creator.artifact_acceptance.v1", {
        "scenario_id": "sample", "artifact_kind": "master_en", "candidate": _identity(master_en, run),
        "producer_stage": _identity(master_en, run), "evidence": [_identity(master_en, run)],
        "decision": "accepted", "decision_at_utc": "2026-09-14T00:00:00Z",
        "user_decision_reference": "synthetic explicit acceptance", "recorder_role": "main_orchestrator",
    }, "receipt_sha256"))
    packet = run / "outputs" / "20-master-ru-packets" / "artifacts"; packet.mkdir(parents=True, exist_ok=True)
    unit_rows = []
    current_page = None
    for index, (en, ru) in enumerate(zip(en_blocks, [part.strip() for part in re.split(r"\n[ \t]*\n", master.read_text(encoding="utf-8").strip())]), 1):
        marker = re.fullmatch(r"<!-- source-page-(\d{3}) -->", en)
        if marker: current_page = int(marker.group(1))
        unit_rows.append({"unit_id": f"unit-{index:05d}", "parent_unit_id": None, "part_index": None, "part_count": None, "page": current_page if marker else None, "source_hash": hashlib.sha256(en.encode("utf-8")).hexdigest().upper(), "part_source_hash": None, "source_text": en, "ru_text": ru})
    en_batch = packet / "batches" / "batch-0001.en.json"
    _write(en_batch, {"schema": "kb_creator.translation_batch.v1", "batch_id": "batch-0001", "instructions": ["synthetic"], "units": [{**row, "ru_text": ""} for row in unit_rows]})
    ru_batch = run / "submissions" / "batch-0001.ru.json"
    _write(ru_batch, {"schema": "kb_creator.translation_batch.v1", "batch_id": "batch-0001", "instructions": ["synthetic"], "units": unit_rows})
    manifest = _sealed("kb_creator.master_ru_packet_manifest.v1", {"scenario_id": "sample", "accepted_master_en": _identity(acceptance, run), "master_en": _identity(master_en, run), "terminology": [], "tasks": _identity(en_batch, packet), "batches": [{"batch_id": "batch-0001", "input": _identity(en_batch, packet), "output_path": "batches/batch-0001.ru.json", "unit_ids": [row["unit_id"] for row in unit_rows]}], "counts": {}, "packet_policy": "ordered_hash_bound_units_v1"}, "manifest_sha256")
    manifest_path = packet / "packet_manifest.json"; _write(manifest_path, manifest)
    submission = _sealed("kb_creator.master_ru_submission.v1", {"scenario_id": "sample", "accepted_master_en": manifest["accepted_master_en"], "packet_manifest": _identity(manifest_path, run), "units": [{"unit_id": row["unit_id"], "source_sha256": row["source_hash"], "russian_payload_sha256": hashlib.sha256(row["ru_text"].encode("utf-8")).hexdigest().upper()} for row in unit_rows], "batches": [_identity(ru_batch, run)], "review": {"state": "closed", "unresolved": []}}, "submission_sha256")
    submission_path = run / "submissions" / "master_ru.submission.json"; _write(submission_path, submission)
    provenance = _sealed("kb_creator.master_ru_provenance.v1", {"scenario_id": "sample", "accepted_master_en": manifest["accepted_master_en"], "packet_manifest": _identity(manifest_path, run), "submission": _identity(submission_path, run), "unit_order": [row["unit_id"] for row in unit_rows], "master_ru": _identity(master, master.parent)}, "provenance_sha256")
    provenance_path = master.parent / "MASTER_RU.provenance.json"; _write(provenance_path, provenance)
    _write(master.parent / "INVENTORY.json", {"schema": "kb_creator.candidate_inventory.v1", "rows": [_identity(master, master.parent), _identity(provenance_path, master.parent)]})


def test_html_adapter_binds_authorities_and_invokes_only_existing_html_cli(tmp_path: Path) -> None:
    item = _fixture(tmp_path); observed = {}

    def runner(command, target, report):
        observed["command"] = list(command)
        derived_config = json.loads(Path(command[-2]).read_text(encoding="utf-8"))
        derived_source = Path(derived_config["production_html"]["source_markdown"])
        observed["derived_source"] = derived_source.read_text(encoding="utf-8")
        target.write_text('<html><body><img src="assets/art.png"><a href="#local">x</a></body></html>', encoding="utf-8")
        _frontmatter_manifest(report)
        _write(report, {"status": "pass", "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        return 0

    _assert_retired_without_output(item, lambda: build_html_candidate(
        master_ru=item["master"], master_ru_acceptance=item["acceptance"], artview_decisions=item["decisions"],
        artview_application=item["application"], effective_visual_config=item["effective"], artview_projection_root=item["projection"],
        base_config=item["config"], staging=item["stage"], output_name="Sample_RU.html", runner=runner,
    ))
    assert observed == {}


def test_html_adapter_projects_manifest_bound_statblock_semantics(tmp_path: Path) -> None:
    item = _fixture(tmp_path)
    authority = _semantic_authority(item)

    def runner(command, target, report):
        config = json.loads(Path(command[-2]).read_text(encoding="utf-8"))
        source = Path(config["production_html"]["source_markdown"])
        markdown = source.read_text(encoding="utf-8")
        assert "<!-- semantic-span-start: statblock; id: synthetic-statblock -->\n## УСЛОВНЫЙ ПРОТИВНИК" in markdown
        assert "<!-- semantic-span-end: statblock; id: synthetic-statblock -->" in markdown
        # This is an unrelated source quotation outside the semantic span; the
        # projection must neither consume nor reinterpret it.
        assert "> STR 50" in markdown
        target.write_text(
            '<html><body><section id="page-002" class="production-page" data-page="002"><section class="statblock-card" data-semantic-kind="statblock" data-semantic-id="synthetic-statblock">'
            '<p>STR 50<br>CON 60</p></section><img src="assets/art.png"></section></body></html>',
            encoding="utf-8",
        )
        _frontmatter_manifest(report)
        _write(report, {"status": "pass", "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        return 0

    _assert_retired_without_output(item, lambda: build_html_candidate(
        master_ru=item["master"], master_ru_acceptance=item["acceptance"], artview_decisions=item["decisions"],
        artview_application=item["application"], effective_visual_config=item["effective"], artview_projection_root=item["projection"],
        base_config=item["config"], staging=item["stage"], output_name="Sample_RU.html",
        semantic_authority=authority, runner=runner,
    ))


def test_html_adapter_projects_semantics_before_required_cover_replacement(tmp_path: Path) -> None:
    item = _fixture(tmp_path)
    authority = _semantic_authority(item)
    _enable_required_cover_v2(item)

    def runner(command, target, report):
        config = json.loads(Path(command[-2]).read_text(encoding="utf-8"))
        source = Path(config["production_html"]["source_markdown"])
        markdown = source.read_text(encoding="utf-8")
        assert "# Synthetic" not in markdown
        assert "![Cover](../artifacts/assets/art.png)" in markdown
        assert "<!-- semantic-span-start: statblock; id: synthetic-statblock -->" in markdown
        target.write_text(
            '<html><body>'
            '<section id="page-001" class="production-page page-type-cover" data-page="001">'
            '<img src="assets/art.png"></section>'
            '<section id="page-002" class="production-page" data-page="002">'
            '<section class="statblock-card" data-semantic-kind="statblock" '
            'data-semantic-id="synthetic-statblock"><p>POWER 50<br>ENDURANCE 60</p></section>'
            '</section></body></html>',
            encoding="utf-8",
        )
        _write(report.parent / "frontmatter_manifest.json", {
            "cover": {}, "toc": {"mode": "generated", "origin": "generated"},
            "credits": {"pages": []}, "body": {"starts_at": "002"},
            "flow": ["page-001", "toc:generated", "page-002"],
        })
        _write(report, {"status": "pass", "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        return 0

    _assert_retired_without_output(item, lambda: build_html_candidate(
        master_ru=item["master"], master_ru_acceptance=item["acceptance"],
        artview_decisions=item["decisions"], artview_application=item["application"],
        effective_visual_config=item["effective"], artview_projection_root=item["projection"],
        base_config=item["config"], staging=item["stage"], output_name="Sample_RU.html",
        semantic_authority=authority, runner=runner,
    ))


def test_cover_replacement_rejects_projected_semantics_on_same_page() -> None:
    with pytest.raises(PublicationAdapterError, match="cover page contains projected semantic spans"):
        adapters._validate_cover_semantic_separation(
            {"source_page": 1}, {"projected": [{"page": 1, "id": "cover-statblock"}]},
        )


def test_stage40_cover_validation_ignores_only_renderer_chrome() -> None:
    policy = {
        "schema": adapters.HTML_POLICY_SCHEMA_V2,
        "frontmatter_order": ["cover", "toc", "body"],
        "cover": {"source_page": 1, "placement_id": "source-cover-page-001"},
        "credits": {"source_pages": []}, "body_start_page": 2,
        "toc": {"mode": "generated", "source_page": None, "entries": []},
    }
    manifest = {
        "cover": {"asset": {"placement_id": "source-cover-page-001", "source_page": "001", "mode": "replace_source_page", "runtime_src": "assets/cover.png"}},
        "toc": {"mode": "generated", "origin": "generated"},
        "credits": {"pages": []}, "body": {"starts_at": "002"},
        "flow": ["page-001", "toc:generated", "page-002"],
    }
    chrome = (
        '<section class="production-page page-type-cover" id="page-001">'
        '<div class="page-marker">page 001</div>'
        '<figure><img src="assets/cover.png" alt="Cover"><figcaption>Cover</figcaption></figure>'
        '</section>'
    )
    adapters._validate_stage40_html_output(policy, manifest, chrome)
    with pytest.raises(PublicationAdapterError, match="duplicate visible source text"):
        adapters._validate_stage40_html_output(
            policy, manifest, chrome.replace("</section>", "<p>Old cover title</p></section>"),
        )


def test_html_adapter_rejects_blockquote_statblock_authority(tmp_path: Path) -> None:
    item = _fixture(tmp_path)
    authority = _semantic_authority(item, representation="blockquote")
    with pytest.raises(PublicationAdapterError, match="legacy HTML/DOCX/PDF publication writer is retired"):
        build_html_candidate(
            master_ru=item["master"], master_ru_acceptance=item["acceptance"], artview_decisions=item["decisions"],
            artview_application=item["application"], effective_visual_config=item["effective"], artview_projection_root=item["projection"],
            base_config=item["config"], staging=item["stage"], output_name="Sample_RU.html",
            semantic_authority=authority,
        )


def test_html_adapter_rejects_stale_semantic_translation_lineage(tmp_path: Path) -> None:
    item = _fixture(tmp_path)
    authority = _semantic_authority(item)
    batch = item["run"] / "submissions" / "batch-0001.ru.json"
    batch.write_text(batch.read_text(encoding="utf-8") + "\n", encoding="utf-8", newline="\n")
    with pytest.raises(PublicationAdapterError, match="legacy HTML/DOCX/PDF publication writer is retired"):
        _build(item, semantic_authority=authority)


def test_semantic_card_parser_preserves_multiple_nested_cards_in_page_order() -> None:
    html = (
        '<html><body><section id="page-018" class="production-page body" data-page="018">'
        '<section class="statblock-card" data-semantic-kind="statblock" data-semantic-id="one"><p>one</p></section>'
        '<section class="statblock-card" data-semantic-id="two" data-semantic-kind="statblock"><p>two</p></section>'
        '</section></body></html>'
    )
    projected = [{"page": 18, "id": "one"}, {"page": 18, "id": "two"}]
    adapters._validate_semantic_cards(html, projected)


@pytest.mark.parametrize("html", [
    '<html><body><section class="production-page" data-page="019"><section class="statblock-card" data-semantic-kind="statblock" data-semantic-id="one"></section></section></body></html>',
    '<html><body><section class="production-page" data-page="018"><section class="statblock-card" data-semantic-kind="statblock" data-semantic-id="two"></section></section></body></html>',
    '<html><body><section class="production-page" data-page="018"><section class="statblock-card" data-semantic-kind="statblock" data-semantic-id="two"></section><section class="statblock-card" data-semantic-kind="statblock" data-semantic-id="one"></section></section></body></html>',
])
def test_semantic_card_parser_rejects_wrong_page_id_or_order(html: str) -> None:
    with pytest.raises(PublicationAdapterError, match="count mismatch|page, order, or id mismatch"):
        adapters._validate_semantic_cards(html, [{"page": 18, "id": "one"}, {"page": 18, "id": "two"}])


def test_semantic_card_parser_rejects_obsolete_and_malformed_nesting() -> None:
    obsolete = '<html><body><section class="production-page" data-page="018"><blockquote class="review-callout statblock-card" data-semantic-kind="statblock" data-semantic-id="one"></blockquote></section></body></html>'
    with pytest.raises(PublicationAdapterError, match="obsolete quote/callout"):
        adapters._validate_semantic_cards(obsolete, [{"page": 18, "id": "one"}])
    malformed = '<html><body><section class="production-page" data-page="018"><section class="statblock-card" data-semantic-kind="statblock" data-semantic-id="one"></div></section></body></html>'
    with pytest.raises(PublicationAdapterError, match="malformed HTML nesting"):
        adapters._validate_semantic_cards(malformed, [{"page": 18, "id": "one"}])


def test_html_adapter_rejects_quote_styled_statblock(tmp_path: Path) -> None:
    item = _fixture(tmp_path)
    authority = _semantic_authority(item)

    def runner(_command, target, report):
        target.write_text(
            '<html><body><section id="page-002"><blockquote class="review-callout statblock-card">late</blockquote>'
            '<img src="assets/art.png"></section></body></html>',
            encoding="utf-8",
        )
        _frontmatter_manifest(report)
        _write(report, {"status": "pass", "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        return 0

    with pytest.raises(PublicationAdapterError, match="legacy HTML/DOCX/PDF publication writer is retired"):
        build_html_candidate(
            master_ru=item["master"], master_ru_acceptance=item["acceptance"], artview_decisions=item["decisions"],
            artview_application=item["application"], effective_visual_config=item["effective"], artview_projection_root=item["projection"],
            base_config=item["config"], staging=item["stage"], output_name="Sample_RU.html",
            semantic_authority=authority, runner=runner,
        )


def test_stage40_policy_rejects_missing_deferred_and_unmapped_source_toc(tmp_path: Path) -> None:
    master = tmp_path / "MASTER_RU.md"
    master.write_text("<!-- source-page-001 -->\n<!-- source-page-002 -->\n<!-- source-page-003 -->\n<!-- source-page-004 -->\n", encoding="utf-8")
    with pytest.raises(PublicationAdapterError, match="missing"):
        adapters._stage40_html_policy({}, master)
    with pytest.raises(PublicationAdapterError, match="deferred"):
        adapters._stage40_html_policy({"html_publication_policy": {"schema": adapters.HTML_POLICY_SCHEMA, "state": "deferred"}}, master)
    incomplete = {
        "schema": adapters.HTML_POLICY_SCHEMA, "state": "stage40_ready",
        "page_roles": [{"source_page": 1, "role": "cover"}, {"source_page": 2, "role": "credits"}, {"source_page": 3, "role": "source_toc"}, {"source_page": 4, "role": "body"}],
        "frontmatter_order": ["cover", "credits", "source_toc", "body"], "cover": {"source_page": 1},
        "credits": {"mode": "source_authored", "source_pages": [2]},
        "toc": {"mode": "preserve_and_link", "source_page": 3, "title": "Contents", "entries": []}, "body_start_page": 4,
    }
    with pytest.raises(PublicationAdapterError, match="lacks"):
        adapters._stage40_html_policy({"html_publication_policy": incomplete}, master)


def test_number_7_dream_source_policy_is_stage40_ready_and_complete(tmp_path: Path) -> None:
    config_path = (
        Path(__file__).resolve().parents[2]
        / "kb_creator/inputs/number-7-dream/publication/v4/configs/html.json"
    )
    config = json.loads(config_path.read_text(encoding="utf-8"))
    master = tmp_path / "MASTER_RU.md"
    master.write_text(
        "\n".join(f"<!-- source-page-{page:03d} -->" for page in range(1, 27)) + "\n",
        encoding="utf-8",
    )
    policy = adapters._stage40_html_policy(config, master)
    assert policy["state"] == "stage40_ready"
    assert policy["frontmatter_order"] == ["cover", "credits", "source_toc", "body"]
    assert policy["body_start_page"] == 4
    assert len(policy["page_roles"]) == 26
    assert len(policy["toc"]["entries"]) == 18
    assert policy["toc"]["display_mode"] == "flat"
    assert policy["toc"]["entries"][-1] == {
        "source_text": "Приложение C — готовые персонажи игроков",
        "target_id": "prilozhenie-c-zaranee-sozdannye-personazhi-igrokov",
    }


def test_stage40_source_toc_output_requires_exact_declared_order_and_links() -> None:
    policy = {
        "frontmatter_order": ["cover", "credits", "source_toc", "body"], "cover": {"source_page": 1},
        "credits": {"source_pages": [2]}, "body_start_page": 4,
        "toc": {"mode": "preserve_and_link", "source_page": 3, "display_mode": "flat", "entries": [{"source_text": "One", "target_id": "one"}, {"source_text": "Two", "target_id": "two"}]},
    }
    manifest = {"toc": {"mode": "preserve_and_link", "origin": "source", "source_page": "003", "entries": 2}, "credits": {"pages": ["002"]}, "body": {"starts_at": "004"}, "flow": ["page-001", "page-002", "toc:source", "page-004"]}
    html = '<section data-page="001"></section><section data-page="002"></section><nav data-toc-origin="source" data-toc-layout="flat"><ol><li class="toc-level-1"><a href="#one">One</a></li><li class="toc-level-1"><a href="#two">Two</a></li></ol></nav><section id="one"></section><section id="two"></section><section data-page="004"></section>'
    adapters._validate_stage40_html_output(policy, manifest, html)
    with pytest.raises(PublicationAdapterError, match="mapping order"):
        adapters._validate_stage40_html_output(policy, manifest, html.replace('#two', '#wrong'))
    with pytest.raises(PublicationAdapterError, match="unresolved or ambiguous"):
        adapters._validate_stage40_html_output(policy, manifest, html.replace('id="two"', 'id="other"'))
    with pytest.raises(PublicationAdapterError, match="display hierarchy"):
        adapters._validate_stage40_html_output(policy, manifest, html.replace('toc-level-1"><a href="#two"', 'toc-level-2"><a href="#two"'))
    with pytest.raises(PublicationAdapterError, match="display mode"):
        adapters._validate_stage40_html_output(policy, manifest, html.replace('data-toc-layout="flat"', 'data-toc-layout="source"'))


def test_stage40_source_toc_policy_accepts_closed_display_levels_and_rejects_invalid_values(tmp_path: Path) -> None:
    master = tmp_path / "MASTER_RU.md"
    master.write_text("<!-- source-page-001 -->\n<!-- source-page-002 -->\n", encoding="utf-8")
    base = {
        "schema": adapters.HTML_POLICY_SCHEMA,
        "state": "stage40_ready",
        "page_roles": [{"source_page": 1, "role": "source_toc"}, {"source_page": 2, "role": "body"}],
        "frontmatter_order": ["source_toc", "body"],
        "cover": {"source_page": 1},
        "credits": {"mode": "none", "source_pages": []},
        "toc": {
            "mode": "preserve_and_link", "source_page": 1, "title": "Contents", "display_mode": "source",
            "entries": [{"source_text": "Child", "target_id": "child", "display_level": 2}],
        },
        "body_start_page": 2,
    }
    # Use a valid cover/body topology for the legacy schema while exercising
    # the closed TOC entry parser directly through the ordinary validator.
    base["page_roles"][0]["role"] = "cover"
    base["page_roles"].insert(1, {"source_page": 2, "role": "source_toc"})
    base["page_roles"][2]["source_page"] = 3
    master.write_text("<!-- source-page-001 -->\n<!-- source-page-002 -->\n<!-- source-page-003 -->\n", encoding="utf-8")
    base["frontmatter_order"] = ["cover", "source_toc", "body"]
    base["toc"]["source_page"] = 2
    base["body_start_page"] = 3
    policy = adapters._stage40_html_policy({"html_publication_policy": base}, master)
    assert policy["toc"]["entries"][0]["display_level"] == 2

    base["toc"]["entries"][0]["display_level"] = 0
    with pytest.raises(PublicationAdapterError, match="entry mapping"):
        adapters._stage40_html_policy({"html_publication_policy": base}, master)


def test_html_adapter_rebases_the_stage21_escape_to_stage40_assets(tmp_path: Path) -> None:
    item = _fixture(tmp_path)

    def runner(command, target, report):
        config = json.loads(Path(command[-2]).read_text(encoding="utf-8"))
        source = Path(config["production_html"]["source_markdown"])
        markdown = source.read_text(encoding="utf-8")
        reference = re.search(r"!\[[^]]*\]\(([^)]+)\)", markdown).group(1)
        resolved = (source.parent / Path(reference)).resolve(strict=True)
        rendered_reference = os.path.relpath(resolved, target.parent).replace("\\", "/")
        assert rendered_reference == "assets/art.png"
        target.write_text(f'<html><img src="{rendered_reference}"></html>', encoding="utf-8")
        _frontmatter_manifest(report)
        _write(report, {"status": "pass", "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        return 0

    _assert_retired_without_output(item, lambda: build_html_candidate(
        master_ru=item["master"], master_ru_acceptance=item["acceptance"], artview_decisions=item["decisions"],
        artview_application=item["application"], effective_visual_config=item["effective"], artview_projection_root=item["projection"],
        base_config=item["config"], staging=item["stage"], output_name="Sample_RU.html", runner=runner,
    ))


def test_html_adapter_renders_compact_terminal_statblock_once_with_tight_spacing(tmp_path: Path) -> None:
    item = _fixture(tmp_path)
    production_python = Path(__file__).resolve().parents[2] / ".tools/MinerU/.venv/Scripts/python.exe"

    _assert_retired_without_output(item, lambda: _build(item, runner=None, python=production_python))


def test_html_adapter_rejects_stale_master_acceptance_before_writes(tmp_path: Path) -> None:
    item = _fixture(tmp_path)
    item["master"].write_text("changed", encoding="utf-8")

    with pytest.raises(PublicationAdapterError, match="legacy HTML/DOCX/PDF publication writer is retired"):
        build_html_candidate(
            master_ru=item["master"], master_ru_acceptance=item["acceptance"], artview_decisions=item["decisions"],
            artview_application=item["application"], effective_visual_config=item["effective"], artview_projection_root=item["projection"],
            base_config=item["config"], staging=item["stage"], output_name="Sample_RU.html", runner=lambda *_: 0,
        )

    assert not any((item["stage"] / "artifacts").iterdir())
    assert not any((item["stage"] / "evidence").iterdir())


def test_html_adapter_blocks_escaping_local_reference(tmp_path: Path) -> None:
    item = _fixture(tmp_path)
    outside = item["run"] / "outside.png"; outside.write_bytes(b"outside")

    def runner(_command, target, report):
        target.write_text('<html><img src="../../../../outside.png"></html>', encoding="utf-8")
        _frontmatter_manifest(report)
        _write(report, {"status": "pass", "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        return 0

    with pytest.raises(PublicationAdapterError, match="legacy HTML/DOCX/PDF publication writer is retired"):
        build_html_candidate(
            master_ru=item["master"], master_ru_acceptance=item["acceptance"], artview_decisions=item["decisions"],
            artview_application=item["application"], effective_visual_config=item["effective"], artview_projection_root=item["projection"],
            base_config=item["config"], staging=item["stage"], output_name="Sample_RU.html", runner=runner,
        )


@pytest.mark.parametrize("mode", ["missing", "stale"])
def test_html_adapter_rejects_missing_or_stale_application_asset_before_renderer(tmp_path: Path, mode: str) -> None:
    item = _fixture(tmp_path)
    projected = item["projected_asset"]
    if mode == "missing":
        projected.unlink()
        expected = "is missing"
    else:
        projected.write_bytes(b"changed")
        expected = "identity drift"

    with pytest.raises(PublicationAdapterError, match="legacy HTML/DOCX/PDF publication writer is retired"):
        _build(item, runner=lambda *_: pytest.fail("renderer must not run"))

    assert not any((item["stage"] / "artifacts").iterdir())
    assert not any((item["stage"] / "evidence").iterdir())


def test_html_adapter_rejects_stale_candidate_manifest_binding(tmp_path: Path) -> None:
    item = _fixture(tmp_path)
    manifest = json.loads(item["manifest"].read_text(encoding="utf-8"))
    manifest["unexpected"] = True
    _write(item["manifest"], manifest)

    with pytest.raises(PublicationAdapterError, match="legacy HTML/DOCX/PDF publication writer is retired"):
        _build(item, runner=lambda *_: pytest.fail("renderer must not run"))


def test_html_adapter_rejects_application_asset_traversal(tmp_path: Path) -> None:
    item = _fixture(tmp_path)
    application = json.loads(item["application"].read_text(encoding="utf-8"))
    application["assets"][0]["path"] = "assets/../outside.png"
    _write(item["application"], application)
    _reseal(item["application"], "application_sha256")

    with pytest.raises(PublicationAdapterError, match="legacy HTML/DOCX/PDF publication writer is retired"):
        _build(item, runner=lambda *_: pytest.fail("renderer must not run"))


def test_html_adapter_rejects_duplicate_application_asset_collision(tmp_path: Path) -> None:
    item = _fixture(tmp_path)
    application = json.loads(item["application"].read_text(encoding="utf-8"))
    application["assets"].append(dict(application["assets"][0]))
    application["assets_inventory_sha256"] = _asset_inventory_sha(application["assets"])
    _write(item["application"], application)
    _reseal(item["application"], "application_sha256")

    with pytest.raises(PublicationAdapterError, match="legacy HTML/DOCX/PDF publication writer is retired"):
        _build(item, runner=lambda *_: pytest.fail("renderer must not run"))
