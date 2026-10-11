import json
import shutil
from pathlib import Path

import pytest

from kb_creator.pipeline.review_bundle import (
    MANIFEST_NAME,
    README_NAME,
    ReviewBundleError,
    build_review_bundle,
    verify_review_bundle,
)
from kb_creator.pipeline.manifests import sealed


def _metadata():
    return {"state": "awaiting_user_review", "scenario_id": "cursed-idol"}


def _entries(source: Path):
    return [{"source": source, "destination": "candidate", "role": "master_ru"}]


def test_bundle_is_relocatable_complete_and_has_no_source_paths(tmp_path):
    source = tmp_path / "source"
    (source / "nested").mkdir(parents=True)
    (source / "MASTER_RU.md").write_text("текст", encoding="utf-8")
    (source / "nested" / "asset.bin").write_bytes(b"asset")
    (source / "empty").mkdir()
    bundle = tmp_path / "review"

    result = build_review_bundle(bundle, entries=_entries(source), metadata=_metadata())

    assert result["state"] == "awaiting_user_review"
    assert (bundle / "candidate/nested/asset.bin").read_bytes() == b"asset"
    assert (bundle / "candidate/empty").is_dir()
    readme = (bundle / README_NAME).read_text(encoding="utf-8")
    assert str(source) not in readme
    moved = tmp_path / "moved"
    shutil.move(str(bundle), moved)
    assert verify_review_bundle(moved)["file_count"] == 3


def test_verifier_rejects_tamper_and_unexpected_files(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("original", encoding="utf-8")
    bundle = tmp_path / "review"
    build_review_bundle(bundle, entries=_entries(source), metadata=_metadata())

    (bundle / "candidate").write_text("tampered", encoding="utf-8")
    with pytest.raises(ReviewBundleError, match="identity mismatch"):
        verify_review_bundle(bundle)

    build_review_bundle(tmp_path / "fresh", entries=_entries(source), metadata=_metadata())
    (tmp_path / "fresh" / "extra.txt").write_text("extra", encoding="utf-8")
    with pytest.raises(ReviewBundleError, match="unexpected or missing"):
        verify_review_bundle(tmp_path / "fresh")


def test_preflight_rejects_overlap_reserved_manifest_and_acceptance_before_write(tmp_path):
    first = tmp_path / "one.txt"
    second = tmp_path / "two.txt"
    first.write_text("one", encoding="utf-8")
    second.write_text("two", encoding="utf-8")
    output = tmp_path / "review"
    with pytest.raises(ReviewBundleError, match="collide or overlap"):
        build_review_bundle(
            output,
            entries=[
                {"source": first, "destination": "assets", "role": "one"},
                {"source": second, "destination": "assets/two.txt", "role": "two"},
            ],
            metadata=_metadata(),
        )
    assert not output.exists()
    with pytest.raises(ReviewBundleError, match="reserved"):
        build_review_bundle(output, entries=[{"source": first, "destination": MANIFEST_NAME, "role": "one"}], metadata=_metadata())
    with pytest.raises(ReviewBundleError, match="must not claim acceptance"):
        build_review_bundle(
            output,
            entries=_entries(first),
            metadata={"state": "awaiting_user_review", "accepted": True},
        )
    assert not output.exists()


def test_symlink_source_and_bundle_path_are_rejected(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    target = source / "target.txt"
    target.write_text("safe", encoding="utf-8")
    link = source / "link.txt"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("host does not permit unprivileged symlink fixtures")
    with pytest.raises(ReviewBundleError, match="symlinks or reparse"):
        build_review_bundle(tmp_path / "review", entries=_entries(source), metadata=_metadata())

    bundle = tmp_path / "normal"
    build_review_bundle(bundle, entries=_entries(target), metadata=_metadata())
    injected = bundle / "injected-link.txt"
    injected.symlink_to(bundle / README_NAME)
    with pytest.raises(ReviewBundleError, match="symlink or reparse"):
        verify_review_bundle(bundle)


def test_manifest_state_cannot_be_rewritten_to_acceptance(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("text", encoding="utf-8")
    bundle = tmp_path / "review"
    build_review_bundle(bundle, entries=_entries(source), metadata=_metadata())
    manifest_path = bundle / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["metadata"]["accepted"] = True
    resealed = sealed(
        manifest["schema"],
        {key: value for key, value in manifest.items() if key not in {"schema", "manifest_sha256"}},
        digest_key="manifest_sha256",
    )
    manifest_path.write_text(json.dumps(resealed), encoding="utf-8")
    with pytest.raises(ReviewBundleError, match="must not claim acceptance"):
        verify_review_bundle(bundle)
