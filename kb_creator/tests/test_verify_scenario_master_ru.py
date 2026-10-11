from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path

import pytest

from kb_creator.scripts import scenario_master_ru, verify_scenario_master_ru


REQUIRED_QA = [
    "accepted_master_en_identity",
    "ordered_unit_identity",
    "markdown_structure_preservation",
    "mechanics_preservation",
    "terminology_authority",
    "asset_identity",
    "independent_translation_qa",
]

COC7E_STATBLOCK_TERMS = [
    {"source": "STR", "target": "СИЛ"}, {"source": "CON", "target": "ВЫН"},
    {"source": "SIZ", "target": "ТЕЛ", "bad_ru": ["РАЗМ"]},
    {"source": "INT", "target": "ИНТ"}, {"source": "POW", "target": "МОЩ"},
    {"source": "DEX", "target": "ЛВК"},
    {"source": "APP", "target": "НАР", "bad_ru": ["ВНЕШ"]},
    {"source": "EDU", "target": "ОБР"},
    {"source": "SAN", "target": "РАС", "bad_ru": ["РАССУДОК"]},
    {"source": "HP", "target": "ПЗ"}, {"source": "MP", "target": "ПМ"},
    {"source": "MOV", "target": "СКО"}, {"source": "Move", "target": "СКО"},
    {"source": "DB", "target": "БКУ"},
    {"source": "Build", "target": "Комплекция"},
    {"source": "Damage bonus", "target": "бонус к урону"},
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _identity(path: Path, root: Path) -> dict[str, object]:
    return {"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": _sha(path)}


def _seal(value: dict[str, object], key: str) -> dict[str, object]:
    result = {name: item for name, item in value.items() if name != key}
    result[key] = hashlib.sha256(
        json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()
    return result


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


@pytest.fixture
def master_ru_candidate(tmp_path: Path) -> dict[str, Path]:
    master_root = tmp_path / "master-en"
    (master_root / "assets").mkdir(parents=True)
    master = master_root / "MASTER_EN.md"
    master.write_text(
        '<!-- source-page-001 -->\n\n<a id="intro"></a>\n# The Keeper\n\n'
        'Keeper rolls 1d6. [See](#intro)\n\n'
        'Pilot roll succeeds.\n\n'
        '> **OCCUPATIONS:** Pilot, Teacher\n\n'
        'He is a sea-plane charter pilot, hired by the group.\n\n'
        '![Map](assets/map.png)\n\n'
        '## HUMAN RESISTANCE\n\n'
        'STR 50  \nCON 50  \nSIZ 50  \nDEX 50  \nINT 50  \n'
        'APP 50  \nPOW 50  \nEDU 50  \nSAN 50  \nHP 10  \nBuild 0\n',
        encoding="utf-8",
        newline="\n",
    )
    (master_root / "assets" / "map.png").write_bytes(b"synthetic-map")
    producer = tmp_path / "master-en-stage.json"; producer.write_text("{}\n", encoding="utf-8")
    evidence = tmp_path / "master-en-qa.json"; evidence.write_text("{}\n", encoding="utf-8")
    acceptance = _seal({
        "schema": "kb_creator.artifact_acceptance.v1",
        "scenario_id": "sample",
        "artifact_kind": "master_en",
        "candidate": _identity(master, tmp_path),
        "producer_stage": _identity(producer, tmp_path),
        "evidence": [_identity(evidence, tmp_path)],
        "decision": "accepted",
        "decision_at_utc": "2026-09-15T00:00:00Z",
        "user_decision_reference": "explicit synthetic acceptance",
        "recorder_role": "main_orchestrator",
    }, "receipt_sha256")
    acceptance_path = tmp_path / "master-en.acceptance.json"; _write(acceptance_path, acceptance)
    terms = tmp_path / "terms.json"
    _write(terms, {"terms": [
        {"source": "Keeper", "target": "Хранитель", "aliases": ["Хранителя"], "bad_ru": ["Ведущий"]},
        {"source": "Pilot", "target": "Пилотирование", "domain": "skill"},
        *COC7E_STATBLOCK_TERMS,
    ]})
    packet = tmp_path / "packet"
    with master.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write("\n" + "Long source sentence. " * 20 + "\n")
    # The accepted candidate identity changes with the appended long unit.
    acceptance["candidate"] = _identity(master, tmp_path)
    _write(acceptance_path, _seal(acceptance, "receipt_sha256"))
    scenario_master_ru.prepare(master, acceptance_path, {"shared": terms}, packet, 128, tmp_path)
    batches = tmp_path / "submission-batches"; batches.mkdir()
    manifest = json.loads((packet / "packet_manifest.json").read_text(encoding="utf-8"))
    for row in manifest["batches"]:
        translated = copy.deepcopy(json.loads((packet / row["input"]["path"]).read_text(encoding="utf-8")))
        for unit in translated["units"]:
            unit["ru_text"] = (
                unit["source_text"]
                .replace("The Keeper", "Хранитель")
                .replace("Keeper rolls", "Хранитель бросает")
                .replace("Pilot roll succeeds.", "Пилотирование успешно.")
                .replace("> **OCCUPATIONS:** Pilot, Teacher", "> **ЗАНЯТИЯ:** Пилот, учитель")
                .replace(
                    "He is a sea-plane charter pilot, hired by the group.",
                    "Он — пилот чартерного гидросамолёта, нанятый группой.",
                )
                .replace("[See]", "[См.]")
                .replace("![Map]", "![Карта]")
            )
        _write(batches / Path(row["output_path"]).name, translated)
    submission = tmp_path / "master_ru.submission.json"
    scenario_master_ru.author_submission(packet, batches, submission, tmp_path)
    candidate = tmp_path / "candidate"
    scenario_master_ru.assemble(packet, submission, candidate, tmp_path)
    contract = tmp_path / "publication-contract.json"
    _write(contract, {"scenario": {"id": "sample"}, "master_ru": {"required_qa": REQUIRED_QA}})
    return {
        "root": tmp_path,
        "packet": packet,
        "batches": batches,
        "submission": submission,
        "candidate": candidate,
        "contract": contract,
    }


def _verify(paths: dict[str, Path]) -> dict[str, object]:
    return verify_scenario_master_ru.verify_candidate(
        paths["packet"], paths["submission"], paths["candidate"], paths["contract"], paths["root"]
    )


def _refresh_submission_for_changed_batch(paths: dict[str, Path], batch_path: Path) -> None:
    submission = json.loads(paths["submission"].read_text(encoding="utf-8"))
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    for index, record in enumerate(submission["batches"]):
        if Path(record["path"]).name == batch_path.name:
            submission["batches"][index] = _identity(batch_path, paths["root"])
            break
    by_id = {unit["unit_id"]: unit for unit in batch["units"]}
    for row in submission["units"]:
        if row["unit_id"] in by_id:
            text = by_id[row["unit_id"]]["ru_text"].strip()
            row["russian_payload_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest().upper()
    _write(paths["submission"], _seal(submission, "submission_sha256"))


def test_independent_verifier_positive_and_standard_library_boundary(master_ru_candidate: dict[str, Path]) -> None:
    result = _verify(master_ru_candidate)
    assert result["schema"] == "kb_creator.master_ru_independent_verification.v1"
    assert result["status"] == "verified_candidate_pending_user_acceptance"
    assert result["required_qa"] == REQUIRED_QA
    assert result["findings"] == []
    assert all(result["checks"].values())
    assert result["master_ru"] == {
        "bytes": (master_ru_candidate["candidate"] / "MASTER_RU.md").stat().st_size,
        "sha256": _sha(master_ru_candidate["candidate"] / "MASTER_RU.md"),
    }
    source = Path(verify_scenario_master_ru.__file__).read_text(encoding="utf-8")
    imports = {
        alias.name.split(".")[0]
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        (node.module or "").split(".")[0]
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
    }
    assert "kb_creator" not in imports
    assert imports <= {"__future__", "argparse", "base64", "csv", "hashlib", "io", "json", "os", "re", "stat", "tempfile", "unicodedata", "pathlib", "typing"}


def test_independent_verifier_enforces_skill_and_excludes_occupations(master_ru_candidate: dict[str, Path]) -> None:
    result = _verify(master_ru_candidate)
    terminology = json.loads(
        (master_ru_candidate["candidate"] / "TERMINOLOGY.qa.json").read_text(encoding="utf-8")
    )["checks"]
    pilot = [row for row in terminology if row["source"] == "Pilot"]
    assert [row["applicability"] for row in pilot] == [
        "required_skill", "excluded_non_skill_context", "excluded_non_skill_context",
    ]
    assert result["checks"]["terminology_authority"] is True

    batch_path = next(
        path for path in master_ru_candidate["batches"].glob("*.ru.json")
        if "Пилотирование" in path.read_text(encoding="utf-8")
    )
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    skill = next(row for row in batch["units"] if "Pilot roll" in row["source_text"])
    skill["ru_text"] = skill["ru_text"].replace("Пилотирование", "Пилот")
    _write(batch_path, batch)
    _refresh_submission_for_changed_batch(master_ru_candidate, batch_path)
    with pytest.raises(
        verify_scenario_master_ru.MasterRuVerificationError,
        match="terminology mismatch: Pilot",
    ):
        _verify(master_ru_candidate)


def test_independent_verifier_classifier_fails_closed_for_ambiguous_skill_prose() -> None:
    term = {"source": "Pilot", "domain": "skill"}
    cases = {
        "Skills: Pilot 40%": "required_skill",
        "A successful Pilot roll reveals the route.": "required_skill",
        "Occupations: Pilot, Teacher": "excluded_non_skill_context",
        "Names: Pilot, Guide": "excluded_non_skill_context",
        "Pilot, Teacher": "ambiguous",
        "Pilot approaches the hangar.": "ambiguous",
    }
    for source, expected in cases.items():
        assert verify_scenario_master_ru._applicability(
            term, source
        )["applicability"] == expected


@pytest.mark.parametrize("target", ["master", "asset", "qa", "provenance", "terminology", "inventory"])
def test_independent_verifier_rejects_candidate_evidence_drift(master_ru_candidate: dict[str, Path], target: str) -> None:
    candidate = master_ru_candidate["candidate"]
    if target == "master":
        (candidate / "MASTER_RU.md").write_text("tampered\n", encoding="utf-8")
    elif target == "asset":
        (candidate / "assets/map.png").write_bytes(b"tampered")
    else:
        filename = {
            "qa": "MASTER_RU.qa.json",
            "provenance": "MASTER_RU.provenance.json",
            "terminology": "TERMINOLOGY.qa.json",
            "inventory": "INVENTORY.json",
        }[target]
        value = json.loads((candidate / filename).read_text(encoding="utf-8"))
        value["injected"] = True
        _write(candidate / filename, value)
    with pytest.raises(verify_scenario_master_ru.MasterRuVerificationError):
        _verify(master_ru_candidate)


@pytest.mark.parametrize("attack", ["hardbreak", "mechanics", "terminology", "extra_field", "reorder"])
def test_independent_verifier_rejects_resealed_translation_attacks(master_ru_candidate: dict[str, Path], attack: str) -> None:
    candidates = [
        (path, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(master_ru_candidate["batches"].glob("*.ru.json"))
    ]
    needle = {"hardbreak": "STR 50", "mechanics": "1d6", "terminology": "Хранитель"}.get(attack)
    batch_path, batch = next(
        (path, value)
        for path, value in candidates
        if needle is None or any(needle in row.get("ru_text", "") or needle in row.get("source_text", "") for row in value["units"])
    )
    if attack == "hardbreak":
        unit = next(row for row in batch["units"] if "STR 50" in row["source_text"])
        assert sum(line.endswith("  ") for line in unit["ru_text"].splitlines()) == 10
        unit["ru_text"] = "\n".join(line.rstrip() for line in unit["ru_text"].splitlines())
    elif attack == "mechanics":
        unit = next(row for row in batch["units"] if "1d6" in row["ru_text"])
        unit["ru_text"] = unit["ru_text"].replace("1d6", "1d8")
    elif attack == "terminology":
        unit = next(row for row in batch["units"] if "Хранитель" in row["ru_text"])
        unit["ru_text"] = unit["ru_text"].replace("Хранитель", "Ведущий")
    elif attack == "extra_field":
        batch["units"][0]["injected"] = True
    else:
        batch["units"].reverse()
    _write(batch_path, batch)
    _refresh_submission_for_changed_batch(master_ru_candidate, batch_path)
    match = "markdown_or_mechanics_drift" if attack in {"hardbreak", "mechanics"} else None
    with pytest.raises(verify_scenario_master_ru.MasterRuVerificationError, match=match):
        _verify(master_ru_candidate)


def test_independent_verifier_rejects_resealed_packet_and_contract_scenario_drift(master_ru_candidate: dict[str, Path]) -> None:
    manifest_path = master_ru_candidate["packet"] / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["packet_policy"] = "weakened"
    _write(manifest_path, _seal(manifest, "manifest_sha256"))
    with pytest.raises(verify_scenario_master_ru.MasterRuVerificationError, match="packet policy"):
        _verify(master_ru_candidate)
