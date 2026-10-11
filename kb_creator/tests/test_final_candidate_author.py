from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline import reviewed_draft_staging
from kb_creator.scripts import author_reviewed_semantic_decisions as author


def _write(path: Path, value: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _identity(path: Path) -> dict[str, object]:
    return {"path": str(path.resolve()), **file_identity(path)}


def _review_input(*, candidate_manifest: Path, spec: Path) -> dict[str, object]:
    value = {
        "schema": "kb_creator.review_draft_input.v1",
        "bindings": {
            "reviewed_candidate_manifest": {"path": "candidate_manifest.json", **file_identity(candidate_manifest)},
            "input_00": {"path": "spec.json", **file_identity(spec)},
        },
        "source_issues": {"schema": "kb_creator.review_draft_source_issues.v1", "issues": []},
        "unresolved_dispositions": [],
    }
    value["input_sha256"] = sha256_bytes(canonical_bytes(value))
    return value


def _case(tmp_path: Path, monkeypatch) -> tuple[Path, Path, list[Path], Path]:
    run, baseline, candidate = tmp_path / "run", tmp_path / "baseline", tmp_path / "candidate"
    run_json = _write(run / "run.json", {"schema": "kb_creator.run_spec.v2", "source": {"sha256": "B" * 64, "bytes": 1, "path_hint": "source.pdf"}})
    queue = _write(run / "review/review_queue.json", {"items": [{"source_page": 1, "contract_role": "body"}]})
    baseline_page = _write(baseline / "pages/page-001.json", {"raw": True})
    _write(baseline / "decision_set.json", {"reviewed_allowlist": {"path": "reviewed_allowlist.v3.json"}})
    spec = _write(tmp_path / "spec.json", {"pages": [{"source_page": 1}]})
    candidate_page = _write(candidate / "pages/page-001.json", {"final": True})
    validation = {"page_count": 1, "unit_count": 0}
    manifest = {
        "schema": "kb_creator.validated_draft_candidate.v1", "state": "validated_candidate_only",
        "scope": "candidate_only", "acceptance": "pending", "validation": validation,
        "inputs": {
            "source": {"sha256": "B" * 64, "bytes": 1, "path_hint": "source.pdf"},
            "run": _identity(run_json), "review_queue": {"path": "review/review_queue.json", **file_identity(queue)},
            "baseline": {"path": str(baseline.resolve()), "pages": [{"path": "pages/page-001.json", **file_identity(baseline_page)}]},
            "specs": [_identity(spec)], "code": _identity(Path(author.__file__)),
        },
        "pages": [{"source_page": 1, "path": "pages/page-001.json", **file_identity(candidate_page)}],
    }
    manifest_path = _write(candidate / "candidate_manifest.json", manifest)
    review_input = _write(tmp_path / "review-input.json", _review_input(candidate_manifest=manifest_path, spec=spec))

    def fake_validate(run_root, baseline_root, spec_paths, *, candidate_output):
        _write(candidate_output / "pages/page-001.json", {"final": True})
        _write(candidate_output / "candidate_manifest.json", {"pages": [{"source_page": 1, "path": "pages/page-001.json"}], "validation": validation})
        return dict(validation)

    monkeypatch.setattr(author, "validate_spec", fake_validate)
    return run, candidate, [spec], review_input


def test_final_candidate_requires_raw_replay_equality(tmp_path, monkeypatch):
    run, candidate, specs, review_input = _case(tmp_path, monkeypatch)
    result = author.validate_final_candidate(run, candidate, specs, review_input)
    assert result["page_count"] == 1
    assert result["pages"] == {1: {"final": True}}


def test_final_candidate_rejects_page_identity_drift_before_regeneration(tmp_path, monkeypatch):
    run, candidate, specs, review_input = _case(tmp_path, monkeypatch)
    (candidate / "pages/page-001.json").write_text('{"final": false}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="page 1 identity differs"):
        author.validate_final_candidate(run, candidate, specs, review_input)


def test_final_candidate_rejects_valid_but_unrelated_review_input(tmp_path, monkeypatch):
    run, candidate, specs, review_input = _case(tmp_path, monkeypatch)
    value = json.loads(review_input.read_text(encoding="utf-8"))
    value["bindings"]["reviewed_candidate_manifest"]["sha256"] = "0" * 64
    value["input_sha256"] = sha256_bytes(canonical_bytes({key: item for key, item in value.items() if key != "input_sha256"}))
    _write(review_input, value)
    with pytest.raises(ValueError, match="not bound to this final candidate manifest"):
        author.validate_final_candidate(run, candidate, specs, review_input)


def test_final_author_validates_prepared_staging_before_archive_path_use(tmp_path, monkeypatch):
    """The final branch must not read an unassigned staging authority."""
    from kb_creator.pipeline import review_draft

    draft_input = _write(tmp_path / "review-input.json", {})
    candidate = tmp_path / "candidate"; candidate.mkdir()
    calls = []
    monkeypatch.setattr(review_draft, "validate_review_draft_input", lambda value: object())
    monkeypatch.setattr(review_draft, "prepare_review_draft_input", lambda value: {"state": "prepared_for_audit"})
    monkeypatch.setattr(author, "validate_final_candidate", lambda *args: {"review_draft_input_sha256": "A" * 64})
    def prepared(path, manifest, input_sha):
        calls.append((path, manifest, input_sha))
        return {"archive_authority": {}}
    monkeypatch.setattr(author, "_validate_prepared_staging", prepared)
    with pytest.raises(ValueError, match="archive authority lacks checked replay paths"):
        author.author_drafts(
            tmp_path / "run", None, tmp_path / "out", [], mode="review_draft",
            draft_input=draft_input, validated_candidate=candidate,
            prepared_staging=tmp_path / "staging-manifest.json",
        )
    assert len(calls) == 1


def test_prepared_staging_rejects_unrelated_valid_candidate_binding(tmp_path, monkeypatch):
    _, candidate, _, review_input = _case(tmp_path, monkeypatch)
    candidate_manifest = candidate / "candidate_manifest.json"
    input_sha = json.loads(review_input.read_text(encoding="utf-8"))["input_sha256"]
    staging = {
        "schema": "kb_creator.reviewed_draft_staging.v3", "state": "prepared_for_audit",
        "bindings": {"finalized_candidate_manifest": {"path": "other.json", **file_identity(candidate_manifest)}},
        "evidence": {
            "review_draft_preflight": {"input_sha256": input_sha},
            "authority": {"archive_authority": {"schema": "kb_creator.review_draft_archive_consumption.v1"}},
        },
    }
    staging["bindings"]["finalized_candidate_manifest"]["sha256"] = "0" * 64
    staging["manifest_sha256"] = sha256_bytes(canonical_bytes(staging))
    path = _write(tmp_path / "staging-manifest.json", staging)
    with pytest.raises(ValueError, match="not bound to this final candidate"):
        author._validate_prepared_staging(path, candidate_manifest, input_sha)


def test_final_candidate_coverage_rederives_factories_and_rejects_resealed_source(tmp_path, monkeypatch):
    """A staging status/payload is evidence inventory, never author authority."""
    from kb_creator.pipeline import reviewed_draft_staging
    source = tmp_path / "source.pdf"; source.write_bytes(b"source")
    selectors = tmp_path / "selectors.json"; selectors.write_text("{}", encoding="utf-8")
    evidence = tmp_path / "evidence.json"; evidence.write_text("{}", encoding="utf-8")
    staging = tmp_path / "staging.json"
    _write(staging, {"evidence": {"coverage_factories": {
        "schema": "kb_creator.review_draft_coverage_factories.v1",
        "source_pdf": {"path": str(source), **file_identity(source)},
        "factories": [{"factory_id": "f", "selectors": {"path": str(selectors), **file_identity(selectors)}, "evidence": {"path": str(evidence), **file_identity(evidence)}, "claim_count": 1}],
        "claims": [{"claim": {"status": "validated", "claim": {"claim_id": "forged"}}}],
    }}})
    seen = {}
    monkeypatch.setattr(reviewed_draft_staging, "recompute_coverage_factories", lambda **kwargs: seen.update(kwargs) or {
        "claims": [{"claim": {"status": "validated", "claim": {"claim_id": "rederived"}}}], "source_key_owner_count": 1,
    })
    assert author._recompute_prepared_coverage(staging, tmp_path / "run", tmp_path / "candidate") == [{"status": "validated", "claim": {"claim_id": "rederived"}}]
    assert seen["factories"][0]["factory_id"] == "f"
    source.write_bytes(b"changed")
    with pytest.raises(ValueError, match="source PDF identity is stale"):
        author._recompute_prepared_coverage(staging, tmp_path / "run", tmp_path / "candidate")


@pytest.mark.parametrize(("target", "changed", "message"), [
    ("selectors", b"selector changed", "selector identity is stale"),
    ("evidence", b"evidence changed", "evidence identity is stale"),
])
def test_recompute_prepared_coverage_rejects_stale_factory_descriptors(tmp_path, monkeypatch, target, changed, message):
    source, selectors, evidence = (tmp_path / "source.pdf", tmp_path / "selectors.json", tmp_path / "evidence.json")
    source.write_bytes(b"source")
    selectors.write_text('{"selectors": []}', encoding="utf-8")
    evidence.write_text('{"evidence": []}', encoding="utf-8")
    staging = tmp_path / "staging.json"
    _write(staging, {"evidence": {"coverage_factories": {
        "schema": "kb_creator.review_draft_coverage_factories.v1",
        "source_pdf": {"path": str(source), **file_identity(source)},
        "factories": [{"factory_id": "f", "selectors": {"path": str(selectors), **file_identity(selectors)}, "evidence": {"path": str(evidence), **file_identity(evidence)}, "claim_count": 0}],
        "claims": [],
    }}})
    monkeypatch.setattr(reviewed_draft_staging, "recompute_coverage_factories", lambda **kwargs: pytest.fail("stale descriptor reached rederivation"))
    {"selectors": selectors, "evidence": evidence}[target].write_bytes(changed)
    with pytest.raises(ValueError, match=message):
        author._recompute_prepared_coverage(staging, tmp_path / "run", tmp_path / "candidate")


@pytest.mark.parametrize("mutate", [
    lambda row: row["selectors"].pop("sha256"),
    lambda row: row["evidence"].update({"unexpected": True}),
])
def test_recompute_prepared_coverage_rejects_malformed_factory_descriptors(tmp_path, monkeypatch, mutate):
    source, selectors, evidence = (tmp_path / "source.pdf", tmp_path / "selectors.json", tmp_path / "evidence.json")
    source.write_bytes(b"source")
    selectors.write_text('{"selectors": []}', encoding="utf-8")
    evidence.write_text('{"evidence": []}', encoding="utf-8")
    row = {"factory_id": "f", "selectors": {"path": str(selectors), **file_identity(selectors)}, "evidence": {"path": str(evidence), **file_identity(evidence)}, "claim_count": 0}
    mutate(row)
    staging = tmp_path / "staging.json"
    _write(staging, {"evidence": {"coverage_factories": {
        "schema": "kb_creator.review_draft_coverage_factories.v1",
        "source_pdf": {"path": str(source), **file_identity(source)}, "factories": [row], "claims": [],
    }}})
    monkeypatch.setattr(reviewed_draft_staging, "recompute_coverage_factories", lambda **kwargs: pytest.fail("malformed descriptor reached rederivation"))
    with pytest.raises(ValueError, match="descriptor is malformed"):
        author._recompute_prepared_coverage(staging, tmp_path / "run", tmp_path / "candidate")


def test_final_author_copies_sealed_page_and_only_generated_source_render(tmp_path, monkeypatch):
    run, candidate, specs, review_input = _case(tmp_path, monkeypatch)
    sealed = {"source_page": 1, "markdown": "sealed", "assets": []}
    _write(candidate / "pages/page-001.json", sealed)
    monkeypatch.setattr(author, "validate_final_candidate", lambda *args: {
        "pages": {1: sealed}, "review_draft_input_sha256": "A" * 64,
    })

    def generated(run_root, baseline_root, destination, paths, *, preview_root):
        generated_page = {
            "source_page": 1, "markdown": "sealed", "assets": [{
                "origin": "source_pdf_page_render_v1", "logical_name": "page-001",
            }],
        }
        _write(destination / "pages/page-001.json", generated_page)
        _write(destination / "reviewed_allowlist.v3.json", {"schema": "allowlist"})
        return {"decisions": [], "reviewed_allowlist": {"path": "reviewed_allowlist.v3.json"}}

    monkeypatch.setattr(author, "author", generated)
    result, decisions = author._author_final_candidate(run, candidate, tmp_path / "out", specs, review_input)
    assert decisions[1]["markdown"] == "sealed"
    assert decisions[1]["assets"] == [{"origin": "source_pdf_page_render_v1", "logical_name": "page-001"}]
    assert sealed["assets"] == []
    assert result["decisions"][0]["source_page"] == 1


def test_final_evidence_projection_copies_only_sealed_candidate_topology(tmp_path, monkeypatch):
    _, candidate, _, _ = _case(tmp_path, monkeypatch)
    staging = _write(tmp_path / "prepared-staging.json", {"prepared": True})
    manifest = candidate / "candidate_manifest.json"
    page = candidate / "pages/page-001.json"
    projection = author._copy_final_evidence_projection(
        candidate_root=candidate,
        verified={"candidate_manifest": {"path": str(manifest), **file_identity(manifest)}, "pages": {1: {}}},
        staging_manifest=staging,
        output=tmp_path / "authored",
    )
    assert projection["final_candidate"]["path"] == "final-candidate/candidate_manifest.json"
    assert projection["prepared_staging"]["path"] == "prepared-staging/staging-manifest.json"
    assert (tmp_path / "authored/final-candidate/candidate_manifest.json").read_bytes() == manifest.read_bytes()
    assert (tmp_path / "authored/final-candidate/pages/page-001.json").read_bytes() == page.read_bytes()
    assert (tmp_path / "authored/prepared-staging/staging-manifest.json").read_bytes() == staging.read_bytes()


def test_final_evidence_projection_rejects_unexpected_candidate_file(tmp_path, monkeypatch):
    _, candidate, _, _ = _case(tmp_path, monkeypatch)
    manifest = candidate / "candidate_manifest.json"
    _write(candidate / "unexpected.json", {"unexpected": True})
    with pytest.raises(ValueError, match="source inventory is not exact"):
        author._copy_final_evidence_projection(
            candidate_root=candidate,
            verified={"candidate_manifest": {"path": str(manifest), **file_identity(manifest)}, "pages": {1: {}}},
            staging_manifest=_write(tmp_path / "prepared-staging.json", {}),
            output=tmp_path / "authored",
        )


@pytest.mark.parametrize("path", ["../decision.json", "/decision.json", "C:/decision.json", "a//decision.json", "a\\\\decision.json"])
def test_final_evidence_rejects_nonportable_authored_path(tmp_path, monkeypatch, path):
    from kb_creator.pipeline.review_draft import ReviewDraftError, finalize_review_draft_evidence

    _, _, _, review_input = _case(tmp_path, monkeypatch)
    value = json.loads(review_input.read_text(encoding="utf-8"))
    output = _write(tmp_path / "decision.json", {})
    with pytest.raises(ReviewDraftError, match="path must"):
        finalize_review_draft_evidence(value, authored={
            "decision_set": {"path": path, **file_identity(output)},
        }, audit={"passed": True, "errors": []}, visual_reviewed_false_pages=[])


def _ocr_packet(run: Path, block: dict[str, object]) -> None:
    views = {
        view: {"blocks": [{**block, "raw_index": 7, "source_page": 1}]}
        for view in ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")
    }
    _write(run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json", {"source_page": 1, "views": views})


def _ocr_spec(tmp_path: Path, *, canonical_view="original_pipeline_txt") -> Path:
    return _write(tmp_path / "ocr-spec.json", {
        "semantic_structure_profile": author.PROFILE,
        "pages": [],
        "ocr_equivalence_classes": [{
            "class_id": "class-7", "source_page": 1,
            "canonical": {"view_id": canonical_view, "raw_index": 7},
            "alternates": [{"view_id": "original_pipeline_ocr", "raw_index": 7}],
            "rationale": "test textual selector domain",
        }],
    })


def test_validate_spec_rejects_image_ocr_canonical_before_downstream_validation(tmp_path):
    run = tmp_path / "run"
    _ocr_packet(run, {"type": "image", "bbox": [0, 0, 10, 10], "text": "", "assets": ["image.png"]})
    with pytest.raises(ValueError, match=r"OCR class 'class-7' page 1: canonical member is not a textual Stage05 unit view='original_pipeline_txt' raw_index=7"):
        author.validate_spec(run, tmp_path / "baseline", [_ocr_spec(tmp_path)])


def test_author_rejects_image_ocr_alternate_before_reading_author_inputs(tmp_path):
    run = tmp_path / "run"
    _ocr_packet(run, {"type": "text", "bbox": [0, 0, 10, 10], "text": "reader prose", "assets": []})
    packet = json.loads((run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json").read_text(encoding="utf-8"))
    packet["views"]["original_pipeline_ocr"]["blocks"][0] = {"raw_index": 7, "source_page": 1, "type": "image", "bbox": [0, 0, 10, 10], "text": "", "assets": ["image.png"]}
    _write(run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json", packet)
    with pytest.raises(ValueError, match=r"OCR class 'class-7' page 1: alternate member is not a textual Stage05 unit view='original_pipeline_ocr' raw_index=7"):
        author.author(run, tmp_path / "baseline", tmp_path / "out", [_ocr_spec(tmp_path)])


def test_ocr_selector_domain_accepts_nonempty_table_text():
    run = Path("unused")
    # The unit itself uses Stage05 normalization, which must retain numeric and
    # non-Latin table text instead of applying an image/non-reader shortcut.
    block = {"raw_index": 7, "source_page": 1, "type": "table", "bbox": [0, 0, 10, 10], "text": "Таблица 42", "assets": []}
    import tempfile
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        _ocr_packet(root, block)
        author._validate_ocr_selector_domain(root, [{
            "class_id": "table-class", "source_page": 1,
            "canonical": {"view_id": "original_pipeline_txt", "raw_index": 7},
            "alternates": [{"view_id": "original_pipeline_ocr", "raw_index": 7}],
        }])


def test_validate_spec_rejects_named_ocr_support_anchored_to_another_unit_before_page_work(tmp_path):
    run = tmp_path / "run"
    _ocr_packet(run, {"type": "text", "bbox": [0, 0, 10, 10], "text": "reader prose", "assets": []})
    spec = json.loads(_ocr_spec(tmp_path).read_text(encoding="utf-8"))
    spec["ocr_equivalence_classes"][0].update({
        "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption",
        "equivalence_policy": "reviewed_visual_full_unit_v1",
        "supporting_assertion_ids": ["wrong-anchor"],
    })
    spec["visual_text_assertions"] = [{
        "assertion_id": "wrong-anchor", "source_page": 1,
        "anchor": {"view_id": "original_pipeline_txt", "raw_index": 99},
    }]
    path = _write(tmp_path / "support-spec.json", spec)
    with pytest.raises(ValueError, match=r"OCR class 'class-7' page 1: named support is absent or anchored elsewhere"):
        author.validate_spec(run, tmp_path / "baseline", [path])
