from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from kb_creator.scripts import scenario_master_ru, verify_scenario_master_ru


COC7E_STATBLOCK_TERMS = [
    {"source": "STR", "target": "СИЛ"},
    {"source": "CON", "target": "ВЫН"},
    {"source": "SIZ", "target": "ТЕЛ", "bad_ru": ["РАЗМ"]},
    {"source": "INT", "target": "ИНТ"},
    {"source": "POW", "target": "МОЩ"},
    {"source": "DEX", "target": "ЛВК"},
    {"source": "APP", "target": "НАР", "bad_ru": ["ВНЕШ"]},
    {"source": "EDU", "target": "ОБР"},
    {"source": "SAN", "target": "РАС", "bad_ru": ["РАССУДОК"]},
    {"source": "HP", "target": "ПЗ"},
    {"source": "MP", "target": "ПМ"},
    {"source": "MOV", "target": "СКО"},
    {"source": "Move", "target": "СКО"},
    {"source": "DB", "target": "БКУ"},
    {"source": "Build", "target": "Комплекция"},
    {"source": "Damage bonus", "target": "бонус к урону"},
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def identity(path: Path, root: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha(path),
    }


def seal(value: dict[str, object], key: str) -> dict[str, object]:
    result = {name: item for name, item in value.items() if name != key}
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    result[key] = hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()
    return result


def boundary_transition(left: str, right: str, from_page: int, to_page: int) -> dict[str, object]:
    return {
        "from_page": from_page,
        "to_page": to_page,
        "mode": "dehyphenated_word" if left.endswith("-") else "continued_prose",
        "left_line_sha256": hashlib.sha256(left.splitlines()[-1].rstrip().encode("utf-8")).hexdigest().upper(),
        "right_line_sha256": hashlib.sha256(right.splitlines()[0].lstrip().encode("utf-8")).hexdigest().upper(),
    }


def canonical_sha(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


class ScenarioMasterRuTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.master_root = self.root / "master-en"
        (self.master_root / "assets").mkdir(parents=True)
        self.master = self.master_root / "MASTER_EN.md"
        self.master.write_text(
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
        (self.master_root / "assets" / "map.png").write_bytes(b"synthetic-map")
        producer = self.root / "producer.json"
        evidence = self.root / "qa.json"
        producer.write_text("{}\n", encoding="utf-8")
        evidence.write_text("{}\n", encoding="utf-8")
        acceptance = {
            "schema": "kb_creator.artifact_acceptance.v1",
            "scenario_id": "sample",
            "artifact_kind": "master_en",
            "candidate": identity(self.master, self.root),
            "producer_stage": identity(producer, self.root),
            "evidence": [identity(evidence, self.root)],
            "decision": "accepted",
            "decision_at_utc": "2026-09-14T00:00:00Z",
            "user_decision_reference": "synthetic fixture",
            "recorder_role": "main_orchestrator",
        }
        self.acceptance = self.root / "master-en.acceptance.json"
        self.acceptance.write_text(
            json.dumps(seal(acceptance, "receipt_sha256"), ensure_ascii=False),
            encoding="utf-8",
        )
        self.terms = self.root / "coc-terms.json"
        self.terms.write_text(
            json.dumps({"terms": [
                {"source": "Keeper", "target": "Хранитель", "aliases": ["Хранителя"], "bad_ru": ["Ведущий"]},
                {"source": "Pilot", "target": "Пилотирование", "domain": "skill"},
                *COC7E_STATBLOCK_TERMS,
            ]}, ensure_ascii=False),
            encoding="utf-8",
        )
        self.packet_root = self.root / "packet"
        scenario_master_ru.prepare(
            self.master,
            self.acceptance,
            {"coc_common": self.terms},
            self.packet_root,
            5000,
            self.root,
        )
        self.batch_root = self.root / "translated-batches"
        self.batch_root.mkdir()
        self.submission = self.root / "submission.json"
        self._write_submission()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _translate(self, text: str) -> str:
        return (
            text.replace("The Keeper", "Хранитель")
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

    def _write_submission(self) -> None:
        manifest = json.loads((self.packet_root / "packet_manifest.json").read_text(encoding="utf-8"))
        for batch in manifest["batches"]:
            source_path = self.packet_root / batch["input"]["path"]
            translated = copy.deepcopy(json.loads(source_path.read_text(encoding="utf-8")))
            for unit in translated["units"]:
                unit["ru_text"] = self._translate(unit["source_text"])
            output_path = self.batch_root / Path(batch["output_path"]).name
            output_path.write_text(json.dumps(translated, ensure_ascii=False), encoding="utf-8")
        scenario_master_ru.author_submission(self.packet_root, self.batch_root, self.submission, self.root)

    def _master_en_v3_provenance(self, transitions: list[dict[str, object]]) -> dict[str, object]:
        placeholder = {"path": "authority.json", "bytes": 0, "sha256": "A" * 64}
        return {
            "schema": "kb_creator.master_en_provenance.v3",
            "scenario_id": "sample",
            "inputs": {
                "publication_contract": dict(placeholder),
                "reconstruction_inventory": dict(placeholder),
                "reconstruction_acceptance": dict(placeholder),
                "reconstructed_en": dict(placeholder),
            },
            "projection": {
                "output_name": "MASTER_EN.md",
                "excluded_source_pages": [],
                "page_marker_policy": "source_page_comment_v1",
                "anchor_policy": "preserve_v1",
                "asset_policy": "copy_markdown_references_v1",
            },
            "master_en": identity(self.master, self.master_root),
            "derived": {
                "source_pages": 1,
                "excluded_pages": 0,
                "anchors": 1,
                "headings": 2,
                "assets": 1,
                "page_boundary_joins": len(transitions),
            },
            "page_boundary_transitions": transitions,
        }

    def _install_hash_bound_master_en_provenance(
        self, transitions: list[dict[str, object]]
    ) -> Path:
        provenance_path = self.master_root / "MASTER_EN.provenance.json"
        provenance_path.write_text(
            json.dumps(self._master_en_v3_provenance(transitions), ensure_ascii=False),
            encoding="utf-8",
        )
        output_files = [
            identity(path, self.master_root)
            for path in sorted(
                (item for item in self.master_root.rglob("*") if item.is_file()),
                key=lambda item: item.relative_to(self.master_root).as_posix(),
            )
        ]
        reproducible = {
            "stage_id": "10-master-en-candidate",
            "stage_name": "master_en_candidate",
            "stage_version": 1,
            "state": "succeeded",
            "run_identity_sha256": "B" * 64,
            "upstream": [],
            "inputs": [{"kind": "synthetic", "file": {"path": "authority.json", "bytes": 0, "sha256": "A" * 64}}],
            "adapter": {},
            "effective_config": {},
            "tools": [],
            "implementation_inventory_sha256": "C" * 64,
            "outputs": {
                "root": self.master_root.relative_to(self.root).as_posix(),
                "files": output_files,
                "inventory_sha256": canonical_sha(output_files),
            },
            "evidence": {},
            "cache_key": "D" * 64,
        }
        stage = {
            "schema": "kb_creator.publication_stage_manifest.v1",
            "reproducible": reproducible,
            "execution": {},
            "reproducible_sha256": canonical_sha({
                "schema": "kb_creator.publication_stage_manifest.v1",
                "reproducible": reproducible,
            }),
        }
        producer = self.root / "master-en-stage.json"
        producer.write_text(json.dumps(stage, ensure_ascii=False), encoding="utf-8")
        acceptance = json.loads(self.acceptance.read_text(encoding="utf-8"))
        acceptance["producer_stage"] = identity(producer, self.root)
        self.acceptance.write_text(
            json.dumps(seal(acceptance, "receipt_sha256"), ensure_ascii=False),
            encoding="utf-8",
        )
        manifest_path = self.packet_root / "packet_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["accepted_master_en"] = identity(self.acceptance, self.root)
        manifest_path.write_text(
            json.dumps(seal(manifest, "manifest_sha256"), ensure_ascii=False),
            encoding="utf-8",
        )
        return provenance_path

    def test_prepare_validate_and_assemble_preserve_structure_and_authority(self) -> None:
        validation = scenario_master_ru.validate_submission(self.packet_root, self.submission, self.root)
        self.assertEqual(validation["status"], "pass")

        output = self.root / "master-ru"
        result = scenario_master_ru.assemble(self.packet_root, self.submission, output, self.root)

        text = (output / "MASTER_RU.md").read_text(encoding="utf-8")
        self.assertEqual(result["status"], "awaiting_master_ru_acceptance")
        self.assertIn("Хранитель", text)
        self.assertIn("СИЛ 50", text)
        self.assertIn("ТЕЛ 50", text)
        self.assertIn("НАР 50", text)
        self.assertNotIn("STR 50", text)
        self.assertNotIn("SIZ 50", text)
        self.assertNotIn("APP 50", text)
        self.assertIn("1d6", text)
        self.assertIn('id="intro"', text)
        self.assertTrue((output / "assets" / "map.png").is_file())
        self.assertEqual(json.loads((output / "MASTER_RU.qa.json").read_text(encoding="utf-8"))["status"], "pass")

    def test_python_normalizes_declared_bad_statblock_labels_before_hashing(self) -> None:
        batch_path = next(
            path for path in self.batch_root.glob("*.ru.json")
            if "SIZ 50" in path.read_text(encoding="utf-8")
        )
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
        unit = next(row for row in batch["units"] if "SIZ 50" in row["source_text"])
        unit["ru_text"] = unit["ru_text"].replace("SIZ 50", "РАЗМ 50").replace("APP 50", "ВНЕШ 50")
        batch_path.write_text(json.dumps(batch, ensure_ascii=False), encoding="utf-8")

        submission = self.root / "normalized.submission.json"
        scenario_master_ru.author_submission(self.packet_root, self.batch_root, submission, self.root)
        output = self.root / "normalized-master-ru"
        scenario_master_ru.assemble(self.packet_root, submission, output, self.root)

        text = (output / "MASTER_RU.md").read_text(encoding="utf-8")
        self.assertIn("ТЕЛ 50", text)
        self.assertIn("НАР 50", text)
        self.assertNotIn("РАЗМ 50", text)
        self.assertNotIn("ВНЕШ 50", text)
        evidence = json.loads((output / "TERMINOLOGY.qa.json").read_text(encoding="utf-8"))
        replaced = {(row["from"], row["to"]) for row in evidence["replacements"]}
        self.assertIn(("РАЗМ", "ТЕЛ"), replaced)
        self.assertIn(("ВНЕШ", "НАР"), replaced)

    def test_statblock_profile_rejects_missing_characteristic_authority(self) -> None:
        incomplete = self.root / "incomplete-terms.json"
        incomplete.write_text(
            json.dumps({"terms": [
                {"source": "Keeper", "target": "Хранитель"},
                *[row for row in COC7E_STATBLOCK_TERMS if row["source"] != "APP"],
            ]}, ensure_ascii=False),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "profile is incomplete: APP"):
            scenario_master_ru.prepare(
                self.master, self.acceptance, {"incomplete": incomplete},
                self.root / "incomplete-packet", 5000, self.root,
            )

    def test_current_master_en_provenance_resolves_through_accepted_stage_inventory(self) -> None:
        provenance_path = self._install_hash_bound_master_en_provenance([])
        manifest = scenario_master_ru._validate_packet(self.packet_root, self.root)

        resolved, provenance, transitions = scenario_master_ru._resolve_current_master_en_provenance(
            manifest, self.root
        )

        self.assertEqual(resolved, provenance_path.resolve())
        self.assertEqual(provenance["master_en"], identity(self.master, self.master_root))
        self.assertEqual(transitions, [])

        provenance_path.write_text(
            json.dumps({**provenance, "untrusted": True}, ensure_ascii=False),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "identity mismatch"):
            scenario_master_ru._resolve_current_master_en_provenance(manifest, self.root)

    def test_master_en_v3_provenance_is_closed_and_current_master_bound(self) -> None:
        provenance_path = self.master_root / "MASTER_EN.provenance.json"
        value = self._master_en_v3_provenance([])
        provenance_path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        _validated, transitions = scenario_master_ru._validate_master_en_provenance(
            provenance_path, self.master, "sample"
        )
        self.assertEqual(transitions, [])

        attacks = (
            {**value, "untrusted": True},
            {**value, "master_en": {**value["master_en"], "sha256": "0" * 64}},
            {**value, "schema": "kb_creator.master_en_provenance.v2"},
        )
        for attack in attacks:
            with self.subTest(attack=attack):
                provenance_path.write_text(json.dumps(attack, ensure_ascii=False), encoding="utf-8")
                with self.assertRaises(scenario_master_ru.MasterRuError):
                    scenario_master_ru._validate_master_en_provenance(
                        provenance_path, self.master, "sample"
                    )

    def test_translation_rebind_handles_both_master_en_page_boundary_modes(self) -> None:
        prior = [
            {"unit_id": "old-0", "source_text": "<!-- source-page-003 -->", "ru_text": "<!-- source-page-003 -->"},
            {"unit_id": "old-1", "source_text": "testing malle-", "ru_text": "проверяя пласти-"},
            {"unit_id": "old-2", "source_text": "<!-- source-page-004 -->", "ru_text": "<!-- source-page-004 -->"},
            {"unit_id": "old-3", "source_text": "ability of bodies.", "ru_text": "чность тел."},
            {"unit_id": "old-4", "source_text": "the end of the", "ru_text": "конец"},
            {"unit_id": "old-5", "source_text": "<!-- source-page-005 -->", "ru_text": "<!-- source-page-005 -->"},
            {"unit_id": "old-6", "source_text": "same day.", "ru_text": "того же дня."},
        ]
        current = [
            {"unit_id": "new-0", "source_text": "<!-- source-page-003 -->"},
            {"unit_id": "new-1", "source_text": "testing malleability of bodies."},
            {"unit_id": "new-2", "source_text": "<!-- source-page-004 -->"},
            {"unit_id": "new-3", "source_text": "the end of the same day."},
            {"unit_id": "new-4", "source_text": "<!-- source-page-005 -->"},
        ]
        transitions = [
            boundary_transition("testing malle-", "ability of bodies.", 3, 4),
            boundary_transition("the end of the", "same day.", 4, 5),
        ]

        translated, report = scenario_master_ru._rebind_translation_units(prior, current, transitions)

        self.assertEqual(translated, [
            "<!-- source-page-003 -->",
            "проверяя пластичность тел.",
            "<!-- source-page-004 -->",
            "конец того же дня.",
            "<!-- source-page-005 -->",
        ])
        self.assertEqual(
            [row["mode"] for row in report],
            ["exact_source", "dehyphenated_word", "exact_source", "continued_prose", "exact_source"],
        )
        self.assertEqual(
            [row["provenance_transition"] for row in report if row["mode"] != "exact_source"],
            transitions,
        )

    def test_translation_rebind_rejects_text_shaped_join_absent_from_provenance(self) -> None:
        prior = [
            {"unit_id": "p3", "source_text": "<!-- source-page-003 -->", "ru_text": "<!-- source-page-003 -->"},
            {"unit_id": "left", "source_text": "alpha", "ru_text": "альфа"},
            {"unit_id": "p4", "source_text": "<!-- source-page-004 -->", "ru_text": "<!-- source-page-004 -->"},
            {"unit_id": "right", "source_text": "beta", "ru_text": "бета"},
        ]
        current = [
            {"unit_id": "p3", "source_text": "<!-- source-page-003 -->"},
            {"unit_id": "joined", "source_text": "alpha beta"},
            {"unit_id": "p4", "source_text": "<!-- source-page-004 -->"},
        ]
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "not authorized by current MASTER_EN provenance"):
            scenario_master_ru._rebind_translation_units(prior, current, [])

    def test_translation_rebind_rejects_wrong_provenance_fields(self) -> None:
        prior = [
            {"unit_id": "p3", "source_text": "<!-- source-page-003 -->", "ru_text": "<!-- source-page-003 -->"},
            {"unit_id": "left", "source_text": "alpha", "ru_text": "альфа"},
            {"unit_id": "p4", "source_text": "<!-- source-page-004 -->", "ru_text": "<!-- source-page-004 -->"},
            {"unit_id": "right", "source_text": "beta", "ru_text": "бета"},
        ]
        current = [
            {"unit_id": "p3", "source_text": "<!-- source-page-003 -->"},
            {"unit_id": "joined", "source_text": "alpha beta"},
            {"unit_id": "p4", "source_text": "<!-- source-page-004 -->"},
        ]
        valid = boundary_transition("alpha", "beta", 3, 4)
        attacks = []
        for key, value in (
            ("mode", "dehyphenated_word"),
            ("from_page", 8),
            ("left_line_sha256", "0" * 64),
            ("right_line_sha256", "F" * 64),
        ):
            attack = dict(valid)
            attack[key] = value
            if key == "from_page":
                attack["to_page"] = 9
            attacks.append(attack)
        for attack in attacks:
            with self.subTest(attack=attack):
                with self.assertRaises(scenario_master_ru.MasterRuError):
                    scenario_master_ru._rebind_translation_units(prior, current, [attack])

    def test_translation_rebind_rejects_duplicate_and_unused_provenance(self) -> None:
        transition = boundary_transition("alpha", "beta", 3, 4)
        exact_prior = [{"unit_id": "same", "source_text": "same", "ru_text": "то же"}]
        exact_current = [{"unit_id": "same", "source_text": "same"}]
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "duplicate page transition"):
            scenario_master_ru._rebind_translation_units(exact_prior, exact_current, [transition, dict(transition)])
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "left provenance transitions unused"):
            scenario_master_ru._rebind_translation_units(exact_prior, exact_current, [transition])
        translated, rows = scenario_master_ru._rebind_translation_units(exact_prior, exact_current, [])
        self.assertEqual(translated, ["то же"])
        self.assertEqual([row["mode"] for row in rows], ["exact_source"])

    def test_translation_rebind_fails_closed_on_unproved_edit(self) -> None:
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "cannot prove exactly one source"):
            scenario_master_ru._rebind_translation_units(
                [{"unit_id": "old", "source_text": "source", "ru_text": "перевод"}],
                [{"unit_id": "new", "source_text": "changed"}],
                [],
            )

    def test_translation_rebind_projects_quote_and_heading_structure_only(self) -> None:
        prior = [
            {
                "unit_id": "old-stat",
                "source_text": "> ### KEEPER\n> STR 60 HP 10",
                "ru_text": "> ### ХРАНИТЕЛЬ\n> СИЛ 60 ПЗ 10",
            },
            {
                "unit_id": "old-background",
                "source_text": "## Background",
                "ru_text": "## Предыстория",
            },
        ]
        current = [
            {"unit_id": "new-stat", "source_text": "### KEEPER\nSTR 60 HP 10"},
            {"unit_id": "new-background", "source_text": "### Background"},
        ]

        translated, report = scenario_master_ru._rebind_translation_units(prior, current, [])

        self.assertEqual(translated, ["### ХРАНИТЕЛЬ\nСИЛ 60 ПЗ 10", "### Предыстория"])
        self.assertEqual(
            [row["mode"] for row in report],
            ["markdown_structure_only", "markdown_structure_only"],
        )

    def test_translation_rebind_splits_inline_stat_title_without_retranslation(self) -> None:
        prior = [{
            "unit_id": "old",
            "source_text": "> ELSIE WEBB STR 30 APP 60\n> HP 9",
            "ru_text": "> ЭЛСИ УЭББ СИЛ 30 НАР 60\n> ПЗ 9",
        }]
        current = [{
            "unit_id": "new",
            "source_text": "### ELSIE WEBB\nSTR 30 APP 60\nHP 9",
        }]

        translated, report = scenario_master_ru._rebind_translation_units(prior, current, [])

        self.assertEqual(translated, ["### ЭЛСИ УЭББ\nСИЛ 30 НАР 60\nПЗ 9"])
        self.assertEqual(report[0]["mode"], "markdown_structure_only")

    def test_translation_rebind_structure_mode_rejects_lexical_edit(self) -> None:
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "cannot prove exactly one source"):
            scenario_master_ru._rebind_translation_units(
                [{"unit_id": "old", "source_text": "## Background", "ru_text": "## Предыстория"}],
                [{"unit_id": "new", "source_text": "### New Background"}],
                [],
            )

    def test_legacy_rebind_can_validate_prior_packet_without_new_profile_gate(self) -> None:
        with mock.patch.object(
            scenario_master_ru,
            "_require_coc7e_statblock_profile",
            side_effect=scenario_master_ru.MasterRuError("legacy profile incomplete"),
        ):
            with self.assertRaisesRegex(
                scenario_master_ru.MasterRuError, "legacy profile incomplete"
            ):
                scenario_master_ru._validate_packet(self.packet_root, self.root)
            manifest = scenario_master_ru._validate_packet(
                self.packet_root,
                self.root,
                require_complete_system_profile=False,
            )
        self.assertEqual(manifest["scenario_id"], "sample")

    def test_mechanics_drift_blocks_before_materialization(self) -> None:
        value = json.loads(self.submission.read_text(encoding="utf-8"))
        batch_path = self.root / value["batches"][0]["path"]
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
        target = next(unit for unit in batch["units"] if "1d6" in unit["ru_text"])
        target["ru_text"] = target["ru_text"].replace("1d6", "1d8")
        batch_path.write_text(json.dumps(batch, ensure_ascii=False), encoding="utf-8")
        value["batches"][0] = identity(batch_path, self.root)
        for row in value["units"]:
            if row["unit_id"] == target["unit_id"]:
                row["russian_payload_sha256"] = hashlib.sha256(target["ru_text"].encode("utf-8")).hexdigest().upper()
        self.submission.write_text(json.dumps(seal(value, "submission_sha256"), ensure_ascii=False), encoding="utf-8")

        validation = scenario_master_ru.validate_submission(self.packet_root, self.submission, self.root)
        self.assertEqual(validation["status"], "blocked")
        self.assertIn("markdown_or_mechanics_drift", {row["code"] for row in validation["findings"]})
        output = self.root / "blocked-output"
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "submission blocked"):
            scenario_master_ru.assemble(self.packet_root, self.submission, output, self.root)
        self.assertFalse(output.exists())

    def test_resealed_packet_with_unknown_field_is_not_authority(self) -> None:
        path = self.packet_root / "packet_manifest.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["unknown"] = True
        path.write_text(json.dumps(seal(value, "manifest_sha256"), ensure_ascii=False), encoding="utf-8")

        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "closed schema mismatch"):
            scenario_master_ru.validate_submission(self.packet_root, self.submission, self.root)

    def test_terminology_is_enforced_per_applicable_unit_and_unknown_variant_blocks(self) -> None:
        value = json.loads(self.submission.read_text(encoding="utf-8"))
        batch_path = self.root / value["batches"][0]["path"]
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
        targets = [row for row in batch["units"] if scenario_master_ru._term_present("Keeper", row["source_text"])]
        self.assertGreaterEqual(len(targets), 2)
        targets[0]["ru_text"] = targets[0]["ru_text"].replace("Хранитель", "Мастер")
        batch_path.write_text(json.dumps(batch, ensure_ascii=False), encoding="utf-8")
        value["batches"][0] = identity(batch_path, self.root)
        for row in value["units"]:
            changed = next((unit for unit in targets if unit["unit_id"] == row["unit_id"]), None)
            if changed is not None:
                row["russian_payload_sha256"] = hashlib.sha256(changed["ru_text"].encode("utf-8")).hexdigest().upper()
        self.submission.write_text(json.dumps(seal(value, "submission_sha256"), ensure_ascii=False), encoding="utf-8")

        validation = scenario_master_ru.validate_submission(self.packet_root, self.submission, self.root)

        self.assertEqual(validation["status"], "blocked")
        by_code = {row["code"]: row for row in validation["findings"] if row["code"].startswith("terminology_")}
        self.assertEqual(by_code["terminology_target_missing"]["unit_id"], targets[0]["unit_id"])
        self.assertNotIn("terminology_bad_variant", by_code)
        checks = [
            row for row in validation["terminology"]
            if row["required"] and row["source"] == "Keeper"
        ]
        self.assertEqual({row["unit_id"] for row in checks}, {row["unit_id"] for row in targets})
        self.assertTrue(any(row["present"] for row in checks))
        self.assertTrue(any(not row["present"] for row in checks))

    def test_skill_terminology_is_required_only_in_bound_skill_context(self) -> None:
        validation = scenario_master_ru.validate_submission(self.packet_root, self.submission, self.root)
        checks = [row for row in validation["terminology"] if row["source"] == "Pilot"]
        self.assertEqual(
            [row["applicability"] for row in checks],
            ["required_skill", "excluded_non_skill_context", "excluded_non_skill_context"],
        )
        self.assertEqual([row["required"] for row in checks], [True, False, False])
        self.assertTrue(checks[0]["present"])
        self.assertTrue(all(row["context"]["ambiguous_occurrences"] == 0 for row in checks))

        batch_path = next(
            path for path in self.batch_root.glob("*.ru.json")
            if "Пилотирование" in path.read_text(encoding="utf-8")
        )
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
        skill = next(row for row in batch["units"] if "Pilot roll" in row["source_text"])
        skill["ru_text"] = skill["ru_text"].replace("Пилотирование", "Пилот")
        batch_path.write_text(json.dumps(batch, ensure_ascii=False), encoding="utf-8")
        rejected = self.root / "skill-target-missing.submission.json"
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "submission blocked"):
            scenario_master_ru.author_submission(
                self.packet_root, self.batch_root, rejected, self.root
            )
        self.assertFalse(rejected.exists())

    def test_ambiguous_skill_occurrence_blocks_submission_before_write(self) -> None:
        ambiguous_root = self.root / "ambiguous"
        ambiguous_root.mkdir()
        master = ambiguous_root / "MASTER_EN.md"
        master.write_text("Pilot approaches the hangar.\n", encoding="utf-8", newline="\n")
        acceptance = json.loads(self.acceptance.read_text(encoding="utf-8"))
        acceptance["candidate"] = identity(master, self.root)
        acceptance_path = ambiguous_root / "master-en.acceptance.json"
        acceptance_path.write_text(
            json.dumps(seal(acceptance, "receipt_sha256"), ensure_ascii=False),
            encoding="utf-8",
        )
        terms = ambiguous_root / "terms.json"
        terms.write_text(
            json.dumps({"terms": [{"source": "Pilot", "target": "Пилотирование", "domain": "skill"}]}, ensure_ascii=False),
            encoding="utf-8",
        )
        packet = ambiguous_root / "packet"
        scenario_master_ru.prepare(
            master, acceptance_path, {"skills": terms}, packet, 5000, self.root
        )
        batches = ambiguous_root / "batches"
        batches.mkdir()
        manifest = json.loads((packet / "packet_manifest.json").read_text(encoding="utf-8"))
        for row in manifest["batches"]:
            translated = json.loads((packet / row["input"]["path"]).read_text(encoding="utf-8"))
            for unit in translated["units"]:
                unit["ru_text"] = "Пилот подходит к ангару."
            (batches / Path(row["output_path"]).name).write_text(
                json.dumps(translated, ensure_ascii=False), encoding="utf-8"
            )
        destination = ambiguous_root / "submission.json"
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "submission blocked"):
            scenario_master_ru.author_submission(packet, batches, destination, self.root)
        self.assertFalse(destination.exists())

    def test_author_submission_is_byte_deterministic_and_schema_valid(self) -> None:
        second = self.root / "submission-second.json"
        result = scenario_master_ru.author_submission(self.packet_root, self.batch_root, second, self.root)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(second.read_bytes(), self.submission.read_bytes())
        self.assertEqual(
            scenario_master_ru.validate_submission(self.packet_root, second, self.root)["status"],
            "pass",
        )
        schema = json.loads(
            (Path(__file__).resolve().parents[1] / "contracts" / "master_ru_submission.v1.schema.json").read_text(encoding="utf-8")
        )
        from jsonschema import Draft202012Validator

        Draft202012Validator.check_schema(schema)
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(json.loads(second.read_text(encoding="utf-8")))), [])

    def test_exact_ten_hard_breaks_pass_and_zero_hard_breaks_fail_before_write(self) -> None:
        validation = scenario_master_ru.validate_submission(self.packet_root, self.submission, self.root)
        statblock = next(row for row in validation["units"] if "STR 50" in row["source_text"])
        self.assertEqual(sum(scenario_master_ru._structure_signature(statblock["source_text"])["hard_breaks"]), 10)
        self.assertEqual(sum(scenario_master_ru._structure_signature(statblock["ru_text"])["hard_breaks"]), 10)

        batch_path = next(self.batch_root.glob("*.ru.json"))
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
        target = next(row for row in batch["units"] if "STR 50" in row["source_text"])
        target["ru_text"] = "\n".join(line.rstrip() for line in target["ru_text"].splitlines())
        batch_path.write_text(json.dumps(batch, ensure_ascii=False), encoding="utf-8")
        rejected = self.root / "zero-breaks.submission.json"
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "submission blocked"):
            scenario_master_ru.author_submission(self.packet_root, self.batch_root, rejected, self.root)
        self.assertFalse(rejected.exists())
        self.assertEqual(list(self.root.glob(f".{rejected.name}.staging.*")), [])

    def test_line_topology_tracks_explicit_breaks_fences_and_emphasis(self) -> None:
        source = "**Strong**<br>  \n```text\nvalue\n```"
        unchanged = "**Сильно**<br>  \n```text\nзначение\n```"
        self.assertEqual(scenario_master_ru._structure_signature(source), scenario_master_ru._structure_signature(unchanged))
        attacks = (
            source.replace("  \n", "\n"),
            source.replace("<br>", ""),
            source.replace("```text", "text"),
            source.replace("**Strong**", "*Strong*"),
        )
        for attack in attacks:
            with self.subTest(attack=attack):
                self.assertNotEqual(scenario_master_ru._structure_signature(source), scenario_master_ru._structure_signature(attack))

    def test_author_rejects_batch_topology_and_source_mutation_before_destination(self) -> None:
        batch_path = next(self.batch_root.glob("*.ru.json"))
        original = batch_path.read_bytes()

        def missing() -> None:
            batch_path.rename(batch_path.with_name("renamed.ru.json"))

        def extra() -> None:
            (self.batch_root / "extra.json").write_text("{}", encoding="utf-8")

        def reordered() -> None:
            value = json.loads(original.decode("utf-8")); value["units"].reverse()
            batch_path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

        def duplicated() -> None:
            value = json.loads(original.decode("utf-8")); value["units"].append(copy.deepcopy(value["units"][0]))
            batch_path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

        def changed_source() -> None:
            value = json.loads(original.decode("utf-8")); value["units"][0]["source_text"] += " changed"
            batch_path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

        def changed_hash() -> None:
            value = json.loads(original.decode("utf-8")); value["units"][0]["source_hash"] = "0" * 64
            batch_path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

        def empty_ru() -> None:
            value = json.loads(original.decode("utf-8")); value["units"][0]["ru_text"] = ""
            batch_path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

        for index, mutate in enumerate((missing, extra, reordered, duplicated, changed_source, changed_hash, empty_ru)):
            with self.subTest(case=mutate.__name__):
                for path in tuple(self.batch_root.iterdir()):
                    path.unlink()
                batch_path.write_bytes(original)
                mutate()
                destination = self.root / f"rejected-{index}.json"
                with self.assertRaises(scenario_master_ru.MasterRuError):
                    scenario_master_ru.author_submission(self.packet_root, self.batch_root, destination, self.root)
                self.assertFalse(destination.exists())

    def test_author_rejects_escape_and_stale_packet_without_write(self) -> None:
        outside = self.root.parent / f"{self.root.name}-outside-submission.json"
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "escapes authority root"):
            scenario_master_ru.author_submission(self.packet_root, self.batch_root, outside, self.root)
        self.assertFalse(outside.exists())

        manifest_path = self.packet_root / "packet_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["scenario_id"] = "stale"
        manifest_path.write_text(json.dumps(seal(manifest, "manifest_sha256"), ensure_ascii=False), encoding="utf-8")
        destination = self.root / "stale-packet-submission.json"
        with self.assertRaises(scenario_master_ru.MasterRuError):
            scenario_master_ru.author_submission(self.packet_root, self.batch_root, destination, self.root)
        self.assertFalse(destination.exists())

    def test_author_never_overwrites_and_rejects_reparse_batch_root(self) -> None:
        existing = self.root / "existing-submission.json"
        existing.write_bytes(b"user-owned")
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "must be absent"):
            scenario_master_ru.author_submission(self.packet_root, self.batch_root, existing, self.root)
        self.assertEqual(existing.read_bytes(), b"user-owned")

        linked = self.root / "linked-batches"
        try:
            linked.symlink_to(self.batch_root, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        rejected = self.root / "reparse-submission.json"
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "reparse"):
            scenario_master_ru.author_submission(self.packet_root, linked, rejected, self.root)
        self.assertFalse(rejected.exists())


class ScenarioTerminologyAuthorityTests(unittest.TestCase):
    CSV_HEADER = "source_term,accepted_ru,aliases,bad_ru,domain,status,source_scope,decision_rule,notes\n"

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_csv_models_accepted_alias_and_known_bad_variants(self) -> None:
        path = self.root / "terms.csv"
        path.write_text(
            self.CSV_HEADER + "Sanity,Рассудок,РАС;Рассудка,SAN;санити,mechanic,accepted,book,rule,note\n",
            encoding="utf-8",
        )

        terms = scenario_master_ru._terminology_terms([("shared_csv", path)])

        self.assertEqual(terms[0]["targets"], ["Рассудок", "РАС", "Рассудка"])
        self.assertEqual(terms[0]["bad"], ["SAN", "санити"])
        self.assertEqual(terms[0]["authorities"], ["shared_csv"])
        self.assertEqual(terms[0]["domain"], "mechanic")

    def test_skill_context_classifier_is_structural_and_fail_closed(self) -> None:
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
            with self.subTest(source=source):
                self.assertEqual(
                    scenario_master_ru._term_context(term, source)["applicability"],
                    expected,
                )

    def test_skill_context_parity_excludes_prose_and_accepts_mechanic_phrases(self) -> None:
        cases = (
            ({"source": "Science", "domain": "skill"}, "science students filled the hall.", "excluded_non_skill_context"),
            ({"source": "Anthropology", "domain": "skill"}, "anthropology examines human cultures.", "excluded_non_skill_context"),
            ({"source": "Persuade", "domain": "skill"}, "A successful Persuade roll can persuade the guard.", "required_skill"),
            ({"source": "Psychology", "domain": "skill"}, "Psychology (or Hard INT) reveals the lie.", "required_skill"),
            ({"source": "Spot Hidden", "domain": "skill"}, "A Spot Hidden will reveal the hidden panel.", "required_skill"),
            ({"source": "Spot Hidden", "domain": "skill"}, "A Spot Hidden from one of the investigators will notice the clue.", "required_skill"),
            ({"source": "Track", "domain": "skill"}, "using Track, Survival or Spot Hidden roles", "required_skill"),
            ({"source": "Survival", "domain": "skill"}, "using Track, Survival or Spot Hidden roles", "required_skill"),
            ({"source": "Spot Hidden", "domain": "skill"}, "using Track, Survival or Spot Hidden roles", "required_skill"),
            ({"source": "Track", "domain": "skill"}, "A fast-track promotion follows.", "excluded_non_skill_context"),
            ({"source": "History", "domain": "skill"}, "Incan History Book", "excluded_non_skill_context"),
            ({"source": "Law", "domain": "skill"}, "Frederick Law Olmsted and Law Enforcement", "excluded_non_skill_context"),
            ({"source": "Archaeology", "domain": "skill"}, "in Archaeology circles", "excluded_non_skill_context"),
            ({"source": "Occult", "domain": "skill"}, "ordinary occult items", "excluded_non_skill_context"),
            ({"source": "Track", "domain": "skill"}, "Track, Teacher", "ambiguous"),
        )
        for term, source, expected in cases:
            with self.subTest(term=term["source"], source=source):
                producer = scenario_master_ru._term_context(term, source)["applicability"]
                verifier = verify_scenario_master_ru._applicability(term, source)["applicability"]
                self.assertEqual(producer, expected)
                self.assertEqual(verifier, expected)

    def test_p3_numeric_scanner_parity_for_clocks_durations_ordinals_and_paths(self) -> None:
        from kb_creator.pipeline.language_numeric import represented_numbers
        cases = (
            ("2h", "2 ч"), ("1 hr", "1 ч"), ("1-hour", "1 час"), ("6pm", "6 вечера"), ("6pm", "6 часов вечера"), ("9:45pm", "21:45"),
            ("10am", "10 утра"), ("7th", "7-й"), ("1st мая", "1 мая"),
            ("1880s", "1880-х годов"), ("42nd Street", "42-я улица"),
            ("1d6 and 70%", "1d6 и 70%"),
        )
        for english, russian in cases:
            self.assertEqual(represented_numbers(english), represented_numbers(russian))
            self.assertEqual(scenario_master_ru._structure_signature(english)["represented_numbers"], verify_scenario_master_ru._signature(russian)["represented_numbers"])
        self.assertNotEqual(represented_numbers("6pm"), represented_numbers("7 вечера"))
        self.assertNotEqual(represented_numbers("6 вечера"), represented_numbers("25 вечера"))
        self.assertEqual(represented_numbers("6 часов"), ["duration_hours:6"])
        self.assertNotEqual(represented_numbers("6 часов вечера"), represented_numbers("25 часов вечера"))
        self.assertNotEqual(represented_numbers("2h"), represented_numbers("3 ч"))
        self.assertEqual(represented_numbers("![asset7](assets/page-007.png)"), [])

    def test_bad_variant_inside_accepted_target_and_ocr_i_one_parity(self) -> None:
        targets = ["Вождение автомобиля"]
        for module in (scenario_master_ru, verify_scenario_master_ru):
            with self.subTest(module=module.__name__, text="accepted target"):
                self.assertFalse(module._bad_variant_present("Вождение", targets, "Вождение автомобиля"))
            with self.subTest(module=module.__name__, text="standalone bad variant"):
                self.assertTrue(module._bad_variant_present("Вождение", targets, "Вождение."))

        source = "1 am prepared.\n> 1 have proof.\n> I stayed because you love me and 1 asked.\n> 1d6 damage.\n> 1 is a genuine count."
        translated = "Я готов.\n> У меня есть доказательство.\n> Я остался, потому что ты любишь меня, и я попросил.\n> 1d6 урона.\n> 1 is a genuine count."
        self.assertEqual(scenario_master_ru._structure_signature(source), scenario_master_ru._structure_signature(translated))
        self.assertEqual(verify_scenario_master_ru._signature(source), verify_scenario_master_ru._signature(translated))
        self.assertEqual(scenario_master_ru._structure_signature(source), verify_scenario_master_ru._signature(source))

    def test_normalization_skips_bad_variant_inside_accepted_target(self) -> None:
        term = {
            "source": "Drive Auto", "target": "Вождение автомобиля",
            "targets": ["Вождение автомобиля"], "bad": ["Вождение"], "domain": "skill",
        }
        source = "Skills: Drive Auto 40%"
        for module, normalizer in (
            (scenario_master_ru, scenario_master_ru._normalize_system_terminology),
            (verify_scenario_master_ru, verify_scenario_master_ru._normalize_declared_terms),
        ):
            with self.subTest(module=module.__name__, case="accepted target"):
                normalized, events = normalizer(source, "Вождение автомобиля 40%", [term], "unit-test")
                self.assertEqual(normalized, "Вождение автомобиля 40%")
                self.assertEqual(events, [])
            with self.subTest(module=module.__name__, case="standalone bad variant"):
                normalized, events = normalizer(source, "Вождение 40%", [term], "unit-test")
                self.assertEqual(normalized, "Вождение автомобиля 40%")
                self.assertEqual(sum(row["count"] for row in events), 1)

    def test_mechanics_parity_recovers_known_ocr_label_number_joins_only(self) -> None:
        source = "1HP; 200mph; HP9; DEX70; SIZ70; 7th; 1d6"
        translated = "1 ПЗ; 200 миль/ч; ПЗ 9; ЛВК 70; ТЕЛ 70; 7th; 1d6"
        expected = ["1", "1d6", "200", "70", "70", "9"]
        for module, signature in (
            (scenario_master_ru, scenario_master_ru._structure_signature),
            (verify_scenario_master_ru, verify_scenario_master_ru._signature),
        ):
            with self.subTest(module=module.__name__, case="known joins"):
                self.assertEqual(module._mechanics(source), expected)
                self.assertEqual(signature(source), signature(translated))
            with self.subTest(module=module.__name__, case="ordinal excluded"):
                self.assertNotIn("7", module._mechanics("the 7th witness"))
            with self.subTest(module=module.__name__, case="genuine mismatch"):
                self.assertNotEqual(module._mechanics("HP9"), module._mechanics("ПЗ 10"))
        self.assertEqual(scenario_master_ru._mechanics(source), verify_scenario_master_ru._mechanics(source))

    def test_hyphenated_ocr_word_is_not_a_stat_terminology_occurrence(self) -> None:
        source = "The library is con- veniently located."
        term = {"source": "CON", "domain": "characteristic"}
        self.assertFalse(scenario_master_ru._term_present("CON", source))
        self.assertFalse(verify_scenario_master_ru._present("CON", source))
        self.assertEqual(scenario_master_ru._term_context(term, source)["occurrences"], 0)

    def test_move_is_required_only_as_a_numeric_statblock_field(self) -> None:
        term = {"source": "Move", "domain": "characteristic"}
        prose = scenario_master_ru._term_context(
            term, "Activating the device would move things along."
        )
        statblock = scenario_master_ru._term_context(term, "Move: 8")
        self.assertEqual(prose["applicability"], "excluded_non_statblock_context")
        self.assertEqual(statblock["applicability"], "required_general")

    def test_markdown_parses_only_strict_terminology_tables_and_does_not_mine_notes(self) -> None:
        path = self.root / "skills.md"
        path.write_text(
            "# Skills\n\n| English | Принятый русский термин | Примечание |\n"
            "|---|---|---|\n| Track | Чтение следов | Не «Слежение». |\n\n"
            "| Сейчас встречается | Должно быть |\n|---|---|\n| Слежение | Чтение следов |\n",
            encoding="utf-8",
        )

        terms = scenario_master_ru._terminology_terms([("skills_md", path)])

        self.assertEqual([(row["source"], row["target"]) for row in terms], [("Track", "Чтение следов")])
        self.assertEqual(terms[0]["bad"], [])
        self.assertEqual(terms[0]["domain"], "skill")

    def test_unsupported_malformed_and_empty_authorities_fail_closed(self) -> None:
        unsupported = self.root / "terms.txt"; unsupported.write_text("x", encoding="utf-8")
        malformed_csv = self.root / "malformed.csv"; malformed_csv.write_text("source_term,accepted_ru\nKeeper,Хранитель\n", encoding="utf-8")
        empty_csv = self.root / "empty.csv"; empty_csv.write_text(self.CSV_HEADER + "Keeper,Хранитель,,,role,draft,book,rule,note\n", encoding="utf-8")
        empty_value_csv = self.root / "empty-value.csv"; empty_value_csv.write_text(self.CSV_HEADER + "Keeper,,,,role,accepted,book,rule,note\n", encoding="utf-8")
        malformed_md = self.root / "malformed.md"; malformed_md.write_text("| English | Russian |\n|---|---|\n| Keeper | Хранитель |\n", encoding="utf-8")
        malformed_row_md = self.root / "malformed-row.md"; malformed_row_md.write_text("| English | Принятый русский термин | Примечание |\n|---|---|---|\n| Keeper | Хранитель |\n", encoding="utf-8")
        for path, message in (
            (unsupported, "unsupported"), (malformed_csv, "header mismatch"),
            (empty_csv, "zero usable"), (empty_value_csv, "unsafe empty"),
            (malformed_md, "header mismatch"), (malformed_row_md, "malformed Markdown"),
        ):
            with self.subTest(path=path.name):
                with self.assertRaisesRegex(scenario_master_ru.MasterRuError, message):
                    scenario_master_ru._terminology_terms([(path.stem, path)])

    def test_duplicate_and_conflicting_normalized_sources_fail_closed(self) -> None:
        duplicate = self.root / "duplicate.json"
        duplicate.write_text(json.dumps({"terms": [
            {"source": "Keeper", "target": "Хранитель"},
            {"source": " keeper ", "target": "Хранитель"},
        ]}, ensure_ascii=False), encoding="utf-8")
        conflict_a = self.root / "a.json"; conflict_b = self.root / "b.json"
        conflict_a.write_text(json.dumps({"terms": [{"source": "Keeper", "target": "Хранитель"}]}, ensure_ascii=False), encoding="utf-8")
        conflict_b.write_text(json.dumps({"terms": [{"source": "keeper", "target": "Ведущий"}]}, ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "duplicate normalized"):
            scenario_master_ru._terminology_terms([("one", duplicate)])
        with self.assertRaisesRegex(scenario_master_ru.MasterRuError, "conflicting normalized"):
            scenario_master_ru._terminology_terms([("one", conflict_a), ("two", conflict_b)])

    def test_compatible_cross_authority_term_is_merged_and_boundaries_avoid_substrings(self) -> None:
        first = self.root / "first.json"; second = self.root / "second.json"
        first.write_text(json.dumps({"terms": [{"source": "Keeper", "target": "Хранитель"}]}, ensure_ascii=False), encoding="utf-8")
        second.write_text(json.dumps({"terms": [{"en": " keeper ", "ru": "Хранитель", "aliases": "Хранителя"}]}, ensure_ascii=False), encoding="utf-8")

        terms = scenario_master_ru._terminology_terms([("first", first), ("second", second)])

        self.assertEqual(terms[0]["authorities"], ["first", "second"])
        self.assertFalse(scenario_master_ru._term_present("Keeper", "Bookkeeper notes"))
        self.assertTrue(scenario_master_ru._term_present("Keeper", "The Keeper rolls"))
