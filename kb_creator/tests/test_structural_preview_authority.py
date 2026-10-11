"""Preview pages must belong to the exact queue-bound provisional decision set."""
import copy
import json

import pytest

from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.structural_role_issues import read_preview_decisions


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def preview(root):
    queue = {"queue_sha256": "A" * 64, "source_sha256": "B" * 64,
             "contract_sha256": "C" * 64, "required_decision_schema": "kb_creator.page_decision.v1",
             "items": [{"source_page": 1}, {"source_page": 2}]}
    rows = []
    for page in (1, 2):
        path = root / f"pages/page-{page:03d}.json"
        write(path, {"schema": queue["required_decision_schema"], "source_page": page,
                     "markdown": "Provisional text", "unresolved": [], "review": {"visual_reviewed": False}})
        rows.append({"source_page": page, "path": path.relative_to(root).as_posix(), **file_identity(path)})
    allow = root / "reviewed_allowlist.v3.json"
    write(allow, {"authority": {"source": "fixture"}})
    manifest = {"schema": "kb_creator.reconstruction_decision_set.v2",
                "submission_state": "submitted_for_validation",
                "semantic_structure_profile": "reviewed_role_outline_and_partitions_v2",
                "review_queue_sha256": queue["queue_sha256"], "source_sha256": queue["source_sha256"],
                "contract_sha256": queue["contract_sha256"], "decisions": rows,
                "reviewed_allowlist": {"path": allow.name, **file_identity(allow)}}
    write(root / "decision_set.json", manifest)
    return queue, manifest


def test_exact_provisional_pages_are_validated_without_claiming_visual_acceptance(tmp_path):
    queue, _ = preview(tmp_path)
    pages, allowlist = read_preview_decisions(tmp_path, queue)
    assert list(pages) == [1, 2]
    assert all(row["review"]["visual_reviewed"] is False for row in pages.values())
    assert allowlist == {"authority": {"source": "fixture"}}


@pytest.mark.parametrize("damage", ["bytes", "page_content", "missing", "extra", "duplicate",
                                     "alias", "queue", "source", "allowlist", "allowlist_path", "unknown"])
def test_preview_cannot_borrow_a_valid_manifest_from_different_pages(tmp_path, damage):
    queue, manifest = preview(tmp_path)
    if damage == "bytes":
        write(tmp_path / "pages/page-001.json", {"source_page": 1, "markdown": "Replacement"})
    elif damage == "page_content":
        path = tmp_path / "pages/page-001.json"
        write(path, {"schema": queue["required_decision_schema"], "source_page": 2})
        manifest["decisions"][0].update(file_identity(path))
    elif damage == "missing":
        manifest["decisions"].pop()
    elif damage == "extra":
        write(tmp_path / "pages/page-003.json", {"source_page": 3})
    elif damage == "duplicate":
        manifest["decisions"][1] = copy.deepcopy(manifest["decisions"][0])
    elif damage == "alias":
        manifest["decisions"][0]["path"] = "pages/../pages/page-001.json"
    elif damage == "queue":
        manifest["review_queue_sha256"] = "D" * 64
    elif damage == "source":
        manifest["source_sha256"] = "D" * 64
    elif damage == "allowlist":
        write(tmp_path / "reviewed_allowlist.v3.json", {"changed": True})
    elif damage == "allowlist_path":
        manifest["reviewed_allowlist"]["path"] = "../other.json"
    else:
        manifest["extra"] = True
    write(tmp_path / "decision_set.json", manifest)
    with pytest.raises(ValueError):
        read_preview_decisions(tmp_path, queue)
