import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from kb_creator.pipeline.semantic_structure import SemanticStructureError
from kb_creator.scripts import author_reviewed_semantic_decisions as author_module
from kb_creator.scripts import materialize_mineru_ai_merge as materializer_module


def _split_decision(*, missing_fragment=False):
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
            "source_fragments": [] if missing_fragment and identity == "notice-intro" else [fragment(start, end)],
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
        "schema": "kb_creator.mineru_ai_page_decision.v1",
        "source_page": page,
        "semantic_role": "body",
        "overlay_preference": view,
        "selected_blocks": [{**ref, "purpose": "structure"}],
        "markdown": "\n".join(lines),
        "assets": [],
        "unresolved": [],
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
    packet = {
        "source_page": page,
        "semantic_role": "body",
        "views": {view: {"blocks": [{"raw_index": raw_index, "type": "table", "text": source, "assets": []}]}},
    }
    return decision, packet, visual


def _install_cold_author_stubs(monkeypatch, tmp_path, decision, packet, visual):
    run = tmp_path / "run"; raw = tmp_path / "raw"; raw.mkdir()
    comparison = tmp_path / "comparison.json"
    comparison.write_text(json.dumps({"pairwise": {
        "original_pipeline_txt__vs__raster_hybrid": {"semantic_conflicts": [{
            "kind": "image_heading_overlap", "asset_side": "left", "heading_side": "right",
            "asset_raw_index": 109, "heading_raw_index": 0, "resolution": None,
        }]},
    }}), encoding="utf-8")
    authorities = SimpleNamespace(stage_02_root=raw, comparison=comparison)
    queue = {"items": [{"source_page": 7, "contract_role": "body"}]}
    reconstruction = ModuleType("kb_creator.pipeline.reconstruction")
    reconstruction.validate_decision_set = lambda *unused: None
    replay = ModuleType("kb_creator.pipeline.reconstruction_replay")
    replay.validate_replayed_prefix = lambda unused: authorities
    resume = ModuleType("kb_creator.pipeline.reconstruction_replay_resume")
    resume.validate_replay_review_queue = lambda unused: SimpleNamespace(queue=queue)
    audit = ModuleType("kb_creator.scripts.audit_mineru_ai_merge_fidelity")
    audit.audit_v3_content = lambda *unused, **unused_kwargs: {"passed": True, "pages": []}
    for name, module in {
        reconstruction.__name__: reconstruction,
        replay.__name__: replay,
        resume.__name__: resume,
        audit.__name__: audit,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)
    import kb_creator.pipeline as pipeline
    monkeypatch.setattr(pipeline, "reconstruction", reconstruction, raising=False)
    monkeypatch.setattr(pipeline, "reconstruction_replay", replay, raising=False)
    monkeypatch.setattr(pipeline, "reconstruction_replay_resume", resume, raising=False)
    monkeypatch.setattr(author_module, "_visual_inventory", lambda unused: {visual["path"]: {"bytes": 1, "sha256": "A" * 64}})

    def fake_author(unused_run, unused_baseline, output, unused_specs):
        (output / "pages").mkdir(parents=True)
        (output / "pages/page-007.json").write_text(json.dumps(decision), encoding="utf-8")
        (output / "reviewed_allowlist.v3.json").write_text(json.dumps({"authority": {}, "visual_text_assertions": []}), encoding="utf-8")
        return {"schema": "test", "pages": 1}

    monkeypatch.setattr(author_module, "author", fake_author)
    drafts = tmp_path / "drafts"; drafts.mkdir()
    (drafts / "page-007.json").write_text(json.dumps({
        "schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 7,
        "semantic_role": "body", "overlay_preference": "original_pipeline_txt",
        "selected_blocks": [], "markdown": "", "assets": [], "unresolved": [],
        "review": {"visual_reviewed": True, "notes": "reviewed"},
    }), encoding="utf-8")
    packets = run / "outputs/04-visual-merge-bundle/merge_packets/pages"; packets.mkdir(parents=True)
    (packets / "page-007.json").write_text(json.dumps(packet), encoding="utf-8")
    geometry = run / "outputs/04-visual-merge-bundle/visual/geometry_plan.json"; geometry.parent.mkdir(parents=True)
    geometry.write_text("{}", encoding="utf-8")
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"semantic_structure_profile": "reviewed_role_outline_and_partitions_v2", "pages": []}), encoding="utf-8")
    return run, drafts, spec


def test_cold_author_passes_validated_split_key_to_stage06_and_fails_closed(monkeypatch, tmp_path):
    decision, packet, visual = _split_decision()
    run, drafts, spec = _install_cold_author_stubs(monkeypatch, tmp_path, decision, packet, visual)
    seen = {}
    original = materializer_module._validate_decision

    def spy(*args, **kwargs):
        seen["split_keys"] = args[-1]
        return original(*args, **kwargs)

    monkeypatch.setattr(materializer_module, "_validate_decision", spy)
    destination = tmp_path / "accepted"
    author_module.author_drafts(run, drafts, destination, [spec])
    assert seen["split_keys"] == {(7, "original_pipeline_txt", 109)}
    assert destination.is_dir()

    invalid_decision, invalid_packet, invalid_visual = _split_decision(missing_fragment=True)
    invalid_root = tmp_path / "invalid"
    invalid_root.mkdir()
    invalid_run, invalid_drafts, invalid_spec = _install_cold_author_stubs(
        monkeypatch, invalid_root, invalid_decision, invalid_packet, invalid_visual,
    )
    seen.clear()
    with pytest.raises(SemanticStructureError):
        author_module.author_drafts(invalid_run, invalid_drafts, invalid_root / "rejected", [invalid_spec])
    assert not seen
    assert not (invalid_root / "rejected").exists()
