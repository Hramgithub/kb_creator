from pathlib import Path
from types import SimpleNamespace

import pytest

from kb_creator.pipeline import reconstruction_replay, reconstruction_replay_resume
from kb_creator.pipeline.review_draft import ReviewDraftError, build_archive_consumption_context


def _archive(root: Path, source_sha: str = "A" * 64):
    paths = ["outputs/02-mineru-three-view", "outputs/03-compare-views/comparison.json",
             "outputs/04-visual-merge-bundle/merge_packets",
             "outputs/04-visual-merge-bundle/visual/visual_manifest.json",
             "outputs/04-visual-merge-bundle/visual/geometry_plan.json"]
    for relative in paths:
        path = root / relative
        if path.suffix:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}", encoding="utf-8")
        else:
            path.mkdir(parents=True, exist_ok=True)
    return SimpleNamespace(run_root=root, stage04_root=root / "outputs/04-visual-merge-bundle",
                           source_sha256=source_sha, run_identity_sha256="B" * 64,
                           bridge_sha256="C" * 64,
                           producer_freshness={"state": "current", "changed_paths": []})


def _queue(monkeypatch):
    monkeypatch.setattr(reconstruction_replay_resume, "validate_replay_review_queue",
                        lambda authority: SimpleNamespace(queue_path=authority.run_root / "review/review_queue.json"))


def test_one_archive_is_verified_once_per_call_but_never_cached_between_calls(tmp_path, monkeypatch):
    authority = _archive(tmp_path / "source")
    observed = []

    def verify(path):
        observed.append(path)
        if len(observed) > 1:
            raise ValueError("source changed since prior public call")
        return authority

    monkeypatch.setattr(reconstruction_replay, "validate_replay_artifacts_for_consumption", verify)
    _queue(monkeypatch)
    result = build_archive_consumption_context(source_run_root=authority.run_root, target_run_root=authority.run_root)
    assert result["source"] == result["target"]
    assert len(observed) == 1
    with pytest.raises(ValueError, match="source changed"):
        build_archive_consumption_context(source_run_root=authority.run_root, target_run_root=authority.run_root)
    assert len(observed) == 2


@pytest.mark.parametrize("defect", [None, "source_identity", "unknown", "path_safety"])
def test_distinct_archive_target_keeps_its_own_validation(tmp_path, monkeypatch, defect):
    source, target = _archive(tmp_path / "source"), _archive(tmp_path / "target")
    if defect == "source_identity":
        target.source_sha256 = "D" * 64
    elif defect == "unknown":
        target.producer_freshness = {"state": "unknown"}
    observed = []

    def verify(path):
        observed.append(path)
        if path == target.run_root and defect == "path_safety":
            raise ValueError("unsafe target")
        return source if path == source.run_root else target

    monkeypatch.setattr(reconstruction_replay, "validate_replay_artifacts_for_consumption", verify)
    _queue(monkeypatch)
    if defect is None:
        result = build_archive_consumption_context(source_run_root=source.run_root, target_run_root=target.run_root)
        assert result["target_run_root"] == str(target.run_root)
    else:
        with pytest.raises((ReviewDraftError, ValueError)):
            build_archive_consumption_context(source_run_root=source.run_root, target_run_root=target.run_root)
    assert observed == [source.run_root, target.run_root]
