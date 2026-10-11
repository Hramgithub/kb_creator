import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from kb_creator.scripts.build_mineru_visual_merge_bundle import _contract_roles


def test_direct_script_cli_bootstraps_repo_package_without_pythonpath():
    script = Path(__file__).parents[1] / "scripts" / "build_mineru_visual_merge_bundle.py"
    environment = {**os.environ, "PYTHONPATH": ""}

    completed = subprocess.run(
        [sys.executable, str(script), "--help"],
        capture_output=True,
        check=False,
        encoding="utf-8",
        env=environment,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Build a visual review" in completed.stdout


def _contract(version: int) -> dict:
    source = (
        {"sha256": "A" * 64, "byte_count": 1, "page_count": 1, "media_box_points": [100, 200], "rotation_degrees": 0}
        if version == 1
        else {
            "sha256": "A" * 64,
            "byte_count": 1,
            "page_count": 1,
            "page_geometry": [{"source_page": 1, "media_box_coordinates": [0, 0, 100, 200], "crop_box_coordinates": [0, 0, 100, 200], "rotation_degrees": 0, "user_unit": 1.0}],
        }
    )
    required_entities = (
        {"numbered_player_handouts": 0}
        if version < 3
        else {"handout_label_sets": [{"scope_id": "sample", "labels": [{"label": "A", "occurrences": [{"source_page": 1, "section": "body"}]}]}]}
    )
    return {
        "schema": f"kb_creator.scenario_reconstruction_contract.v{version}",
        "contract_revision": version,
        "scenario": {"id": "sample", "title": "Sample"},
        "source": source,
        "scope": {"mode": "all_source_pages", "first_page": 1, "last_page": 1, "required_entities": required_entities},
        "page_roles": [{"role": "body_sample", "first_page": 1, "last_page": 1, "content_mode": "text", "traits": [], "strategies": ["reading_order"]}],
        "reconstruction": {"strategies": ["reading_order"], "required_review": True},
        "acceptance": {"approval_authority": "configured_reconstruction_review"},
    }


@pytest.mark.parametrize("version", (1, 2, 3))
def test_contract_roles_accepts_each_canonical_reconstruction_version(tmp_path, version):
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(_contract(version)), encoding="utf-8")

    assert _contract_roles(path) == (1, ((1, 1, "body_sample"),))


def test_contract_roles_rejects_unknown_contract_version(tmp_path):
    contract = _contract(3)
    contract["schema"] = "kb_creator.scenario_reconstruction_contract.v4"
    contract["contract_revision"] = 4
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid reconstruction contract"):
        _contract_roles(path)


def test_contract_roles_preserves_topology_fail_closed_after_canonical_validation(tmp_path):
    contract = _contract(1)
    contract["source"]["page_count"] = 2
    contract["scope"]["last_page"] = 2
    contract["page_roles"] = [{"role": "body_sample", "first_page": 1, "last_page": 1, "content_mode": "text", "traits": [], "strategies": ["reading_order"]}]
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid reconstruction contract"):
        _contract_roles(path)
