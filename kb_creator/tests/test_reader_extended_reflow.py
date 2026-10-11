"""Exact p98/99/100 shaped reflow across retained map labels and reviewed furniture."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from lxml import html
from lxml import etree
from PIL import Image
from translator.translator import markdown_to_review_html

from kb_creator.pipeline import five_step_docx, reader_options_rebind, reader_projection
from kb_creator.tests.test_reader_interrupted_reflow import handout_group, reflow, setup
from kb_creator.tests.test_reader_whole_artifact import PDF_HASH, _binding, _unit, _write


LABELS = ["Кладовая" if index in (10, 11) else f"Метка {index:02d}" for index in range(1, 53)]
LIST_TEXT = "\n".join("- " + label for label in LABELS)
LEFT = "Камеры включают операционную,"
RIGHT = "послеоперационную палату, комнату отдыха. Здесь сохраняется криохранилище."


def guarded_fixture(root: Path, case: str, *, reverse: bool = False,
                    word_left: str | None = None, word_right: str | None = None,
                    duplicate_title: str | None = None, title_level_mismatch: bool = False,
                    caption_text: str | None = None):
    """Small final-stage DOCX fixtures shaped like the three reviewed intervals."""
    title = "## ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА"
    cases = {
        "word": ["<!-- source-page-052 -->", "Он подслушива", "ПАРАНОЙЯ", "51",
                 "ОДЕРЖИМОСТЬ", "СПИРИТИЧЕСКАЯ ДОСКА", "<!-- source-page-053 -->",
                 "ет. Разговор продолжился.", "Следующий абзац."],
        "title": ["<!-- source-page-024 -->", title, "Автор сценария", "<!-- source-page-027 -->",
                  "Он может подняться", "ПРОМЫВКА МОЗГОВ", "ЗОМБИ", "26",
                  "<!-- source-page-028 -->", "## Последнее желание Уолтера", "и пройти дальше.",
                  "Следующий абзац."],
        "title_plus_standalone": ["<!-- source-page-024 -->", title, "Автор сценария",
                                  "<!-- source-page-027 -->", "Он может подняться", "ПРОМЫВКА МОЗГОВ",
                                  "ЗОМБИ", "26", "<!-- source-page-028 -->",
                                  "## Последнее желание Уолтера", "и пройти дальше.",
                                  "Следующий абзац.", "<!-- source-page-029 -->",
                                  "# Последнее желание Уолтера", "Продолжение раздела."],
        "fish": ["<!-- source-page-077 -->", "Эти люди будут", "76",
                 "![Рыба](assets/fish.jpg)", "<!-- source-page-078 -->", "периодически приходить.",
                 "Следующий абзац."],
        "caption": ["<!-- source-page-163 -->", "Вести приходят", "Раздаточный материал 5",
                    "Полный текст письма.", "![Письмо](assets/letter.jpg)",
                    "<!-- source-page-164 -->", "позже.", "Следующий абзац."],
        "single": ["<!-- source-page-081 -->", "В библиотеке", "ZG ZIGLT KTQROFU ZIOL FGZT.",
                   "<!-- source-page-082 -->", "тише, чем обычно.", "Следующий абзац."],
        "chain": ["<!-- source-page-160 -->", "Начало", "Подпись первого материала",
                  "Текст первого материала.", "<!-- source-page-161 -->", "середина",
                  "Подпись второго материала", "Текст второго материала.",
                  "<!-- source-page-162 -->", "конец.", "Следующий абзац."],
        "standalone": ["<!-- source-page-020 -->", "## ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА",
                       "Основной текст.", "<!-- source-page-021 -->",
                       "# Последнее желание Уолтера", "См. название."],
        "standalone_heading_and_p": ["<!-- source-page-020 -->", "## ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА",
                                     "Основной текст.", "<!-- source-page-021 -->",
                                     "# Последнее желание Уолтера", "Последнее желание Уолтера",
                                     "См. название."],
        "standalone_heading_cohort": ["<!-- source-page-020 -->", "## ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА",
                                      "Основной текст.", "<!-- source-page-021 -->",
                                      "# Последнее желание Уолтера", "# Последнее желание Уолтера",
                                      "Последнее желание Уолтера"],
        "standalone_same_level": ["<!-- source-page-020 -->", "## ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА",
                                  "Основной текст.", "<!-- source-page-021 -->",
                                  "## Последнее желание Уолтера", "См. название."],
        "standalone_same_page": ["<!-- source-page-020 -->", "## ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА",
                                 "Основной текст.", "# Последнее желание Уолтера",
                                 "<!-- source-page-021 -->", "См. название."],
        "standalone_later_retained": ["<!-- source-page-020 -->", "# Последнее желание Уолтера",
                                      "Основной текст.", "<!-- source-page-021 -->",
                                      "## ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА", "См. название."],
        "standalone_retained_removed": ["<!-- source-page-019 -->", "## ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА",
                                        "<!-- source-page-020 -->", "## ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА",
                                        "<!-- source-page-021 -->", "# Последнее желание Уолтера",
                                        "См. название."],
    }
    strings = cases[case]
    if case == "word":
        if word_left is not None:
            strings[1] = word_left
        if word_right is not None:
            strings[7] = word_right
    if case == "title" and duplicate_title is not None:
        strings[9] = duplicate_title
    elif case == "title" and title_level_mismatch:
        strings[9] = "# Последнее желание Уолтера"
    if case == "caption" and caption_text is not None:
        strings[2] = caption_text
    if case == "standalone" and duplicate_title is not None:
        strings[4] = duplicate_title
    units = [_unit(f"guard-{index}", value) for index, value in enumerate(strings)]
    bind = lambda index: {key: units[index][key] for key in ("unit_id", "ru_sha256")}
    master = root / "language/MASTER_RU.md"
    master.parent.mkdir(parents=True)
    master.write_text("\n\n".join(strings) + "\n", encoding="utf-8", newline="\n")
    for name in ("MASTER_RU.manifest.json", "PROOFREAD_LEDGER.json", "INVENTORY.json"):
        _write(master.parent / name, {})
    assets = []
    if case in {"fish", "caption"}:
        fish = master.parent / "assets/fish.jpg"
        if case == "caption":
            fish = master.parent / "assets/letter.jpg"
        fish.parent.mkdir()
        Image.new("RGB", (90, 60), "blue").save(fish)
        assets.append({"path": f"assets/{fish.name}", **reader_projection.identity(fish)})
    _write(master.parent / "ASSET_MANIFEST.json", {"assets": assets})
    projection = {"schema": "kb_creator.five_step_ru_projection.v3",
                  "master_en": {"path": "evidence/MASTER_EN.md", "bytes": 1, "sha256": "C" * 64},
                  "master_ru": {"path": "MASTER_RU.md", **reader_projection.identity(master)},
                  "unit_order": [unit["unit_id"] for unit in units], "units": units, "spans": []}
    projection["projection_sha256"] = reader_projection.seal(projection)
    projection_path = master.parent / "semantic_context/RU_PROJECTION.json"
    _write(projection_path, projection)
    options_root = root / "options"
    visual = options_root / "evidence/source.png"
    visual.parent.mkdir(parents=True)
    Image.new("RGB", (100, 100), "white").save(visual)
    evidence = {"approval": "reviewed", "reviewer": "fixture reviewer", "source_pdf_sha256": PDF_HASH,
                "source_visual": {"path": "evidence/source.png", **reader_projection.identity(visual)},
                "source_region": {"coordinate_space": "source_visual_pixels_top_left_v1", "bbox": [1, 1, 80, 80]},
                "visual_verdict": "whole_unit_is_running_furniture", "rationale": "fixture source comparison"}
    if case == "word":
        left, right, furniture, marker = 1, 7, [2, 3, 4, 5], 6
    elif case in {"title", "title_plus_standalone"}:
        left, right, furniture, marker = 4, 10, [5, 6, 7], 8
    elif case == "caption":
        left, right, furniture, marker = 1, 6, [], 5
    elif case == "single":
        left, right, furniture, marker = 1, 4, [], 3
    elif case == "chain":
        left, right, furniture, marker = 1, 5, [], 4
    elif case.startswith("standalone"):
        left, right, furniture, marker = 1, 4, [], 3
    else:
        left, right, furniture, marker = 1, 5, [2], 4
    decision = {"role": "interrupted_prose_reflow", "units": [bind(left), bind(right)],
                "intervening_units": [bind(index) for index in range(left + 1, right)],
                "source_evidence": "reviewed source boundary fixture", "reason": "restore one source sentence"}
    if case == "word":
        decision["join_mode"] = "word"
    if case in {"caption", "single", "chain"}:
        decision["join_mode"] = "space"
        group = handout_group(bind, [2] if case == "single" else [2, 3], 2)
        group["title_kind"] = "plain_paragraph"
        decision["intervening_handout_groups"] = [group]
    furniture_roles = [{"role": "omit_source_artifact", "classification": "source_furniture_text",
                        "text_policy": "reviewed_whole_plain_block_v2", "unit": _binding(units[index]),
                        "source_page": {"word": 52, "title": 27, "title_plus_standalone": 27,
                                        "fish": 77, "caption": 163,
                                        "single": 81, "chain": 160}[case],
                        "expected_raw_text": units[index]["ru_text"],
                        "furniture_kind": "page_number" if units[index]["ru_text"].isdigit() else "running_header",
                        "extracted_as_ocr_fragment": False, "source_evidence": copy.deepcopy(evidence),
                        "reason": "reviewed source furniture fixture"} for index in furniture]
    title_role = []
    if case in {"title", "title_plus_standalone"}:
        title_role = [{"role": "repeated_title", "unit": bind(9), "retained": bind(1),
                       "text_match": "casefold", "source_evidence": "p24 retained title and p28 repeated running title",
                       "reason": "reviewed running duplicate"}]
        if title_level_mismatch:
            title_role[0]["heading_level_mismatch"] = {
                "removed_level": 1, "retained_level": 2,
                "source_evidence": "reviewed source-page-028 running title h1 repeats source-page-024 chapter h2"}
    roles = [decision, *furniture_roles, *title_role]
    if case == "title_plus_standalone":
        roles.append({"role": "repeated_title", "unit": bind(13), "retained": bind(1),
                      "standalone_running_heading": True, "text_match": "casefold",
                      "heading_level_mismatch": {"removed_level": 1, "retained_level": 2,
                                                 "source_evidence": "reviewed heading levels on 24/29"},
                      "source_evidence": "reviewed original source 24/29 running heading",
                      "reason": "remove the standalone repeated heading"})
    if case == "chain":
        downstream = {"role": "interrupted_prose_reflow", "units": [bind(5), bind(9)],
                      "intervening_units": [bind(index) for index in range(6, 9)],
                      "intervening_handout_groups": [{**handout_group(bind, [6, 7], 6),
                                                     "title_kind": "plain_paragraph"}],
                      "join_mode": "space", "source_evidence": "reviewed second source boundary fixture",
                      "reason": "restore the second part before joining the first"}
        roles = [downstream, decision]
    if case.startswith("standalone"):
        retained_index, removed_index = {
            "standalone": (1, 4), "standalone_same_level": (1, 4),
            "standalone_heading_and_p": (1, 4), "standalone_heading_cohort": (1, 4),
            "standalone_same_page": (1, 3),
            "standalone_later_retained": (4, 1), "standalone_retained_removed": (3, 5),
        }[case]
        standalone = {"role": "repeated_title", "unit": bind(removed_index),
                      "retained": bind(retained_index), "standalone_running_heading": True,
                      "text_match": "casefold", "heading_level_mismatch": {
                          "removed_level": 1, "retained_level": 2,
                          "source_evidence": "reviewed exact source heading levels"},
                      "source_evidence": "reviewed native source running heading",
                      "reason": "remove only a repeated running heading"}
        if case == "standalone_same_level":
            standalone.pop("heading_level_mismatch")
        roles = [standalone]
        if case == "standalone_retained_removed":
            roles.append({"role": "repeated_title", "unit": bind(3), "retained": bind(1),
                          "reason": "fixture removes the retained title after standalone route"})
    if reverse:
        roles = [*title_role, *reversed(furniture_roles), decision]
    options = {"schema": reader_projection.SCHEMA,
               "master_ru": {"path": "MASTER_RU.md", **reader_projection.identity(master)},
               "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **reader_projection.identity(projection_path)},
               "source_toc": {"state": "absent", "source_pdf_sha256": PDF_HASH, "reason": "fixture source"},
               "body_links": [], "asset_choices": [], "hit_points": {"presentation": "numeric"},
               "display_roles": roles}
    options["options_sha256"] = reader_projection.seal(options)
    options_path = options_root / "reader-options.json"
    _write(options_path, options)
    return master, projection_path, options_path


def fixture(root: Path, *, title_first: bool = False, selected_map: bool = False,
            singleton_label: bool = False, partial_list: bool = False):
    master = root / "language/MASTER_RU.md"
    strings = ["<!-- source-page-098 -->", "# Сценарий", LEFT, "84", "Книга",
               "<!-- source-page-099 -->", "ПЛАН", "85", LIST_TEXT,
               "![Карта](assets/map.png)", "<!-- source-page-100 -->", "# Сценарий", RIGHT,
               "Полезный абзац после продолжения."]
    if singleton_label or partial_list:
        strings[8] = "- ЗДРАВСТВУЙТЕ, МЕНЯ ЗОВУТ"
    if partial_list:
        strings[7] = "- Первая метка"
    units = [_unit(f"n197-{index}", value) for index, value in enumerate(strings)]
    master.parent.mkdir(parents=True, exist_ok=True)
    master.write_text("\n\n".join(strings) + "\n", encoding="utf-8", newline="\n")
    image = master.parent / "assets/map.png"
    image.parent.mkdir()
    Image.new("RGB", (120, 80), "orange").save(image)
    _write(master.parent / "ASSET_MANIFEST.json", {"assets": [{"path": "assets/map.png", **reader_projection.identity(image)}]})
    for name in ("MASTER_RU.manifest.json", "PROOFREAD_LEDGER.json", "INVENTORY.json"):
        _write(master.parent / name, {})
    projection = {"schema": "kb_creator.five_step_ru_projection.v3",
                  "master_en": {"path": "evidence/MASTER_EN.md", "bytes": 1, "sha256": "C" * 64},
                  "master_ru": {"path": "MASTER_RU.md", **reader_projection.identity(master)},
                  "unit_order": [unit["unit_id"] for unit in units], "units": units, "spans": []}
    projection["projection_sha256"] = reader_projection.seal(projection)
    projection_path = master.parent / "semantic_context/RU_PROJECTION.json"
    _write(projection_path, projection)
    options_root = root / "options"
    selected_choice = None
    if selected_map:
        selected = options_root / "selected/full-map.png"
        selected.parent.mkdir(parents=True)
        Image.new("RGB", (180, 120), "green").save(selected)
        selected_choice = {"original_ref": "assets/map.png", "original": reader_projection.identity(image),
                           "selected_ref": "selected/full-map.png", "selected": reader_projection.identity(selected),
                           "provenance": "reviewed complete native source map fixture",
                           "reason": "replace clipped source image with complete original map"}
    visual = options_root / "evidence/source.png"
    visual.parent.mkdir(parents=True)
    Image.new("RGB", (100, 100), "white").save(visual)
    evidence = {"approval": "reviewed", "reviewer": "fixture reviewer", "source_pdf_sha256": PDF_HASH,
                "source_visual": {"path": "evidence/source.png", **reader_projection.identity(visual)},
                "source_region": {"coordinate_space": "source_visual_pixels_top_left_v1", "bbox": [1, 1, 80, 80]},
                "visual_verdict": "whole_unit_is_running_furniture", "rationale": "fixture source comparison"}
    bind2 = lambda unit: {key: unit[key] for key in ("unit_id", "ru_sha256")}
    reflow = {"role": "interrupted_prose_reflow", "units": [bind2(units[2]), bind2(units[12])],
              "intervening_units": [bind2(unit) for unit in units[3:12]],
              "intervening_asset_labels": [{"unit": bind2(units[8]), "image": bind2(units[9]),
                                             "source_evidence": "reviewed complete source map labels",
                                             "reason": "preserve map labels with original map"}],
              "source_evidence": "reviewed interruption and running duplicate title on source pages 98-100",
              "reason": "join the exact sentence around preserved map and reviewed furniture"}
    if selected_choice is not None:
        reflow["intervening_asset_labels"][0]["reviewed_asset_choice"] = copy.deepcopy(selected_choice)
    repeated = {"role": "repeated_title", "unit": bind2(units[11]), "retained": bind2(units[1]),
                "reason": "reviewed running duplicate scenario title"}
    furniture = [{"role": "omit_source_artifact", "classification": "source_furniture_text",
                  "text_policy": "reviewed_whole_plain_block_v2", "unit": _binding(units[index]),
                  "source_page": 98 if index < 5 else 99, "expected_raw_text": units[index]["ru_text"],
                  "furniture_kind": "page_number" if index in (3, 7) else "running_footer",
                  "extracted_as_ocr_fragment": False, "source_evidence": copy.deepcopy(evidence),
                  "reason": "reviewed printed furniture"} for index in (3, 4, 6, 7)
                 if not (partial_list and index == 7)]
    roles = ([repeated, *furniture, reflow] if title_first else [reflow, repeated, *furniture])
    options = {"schema": reader_projection.SCHEMA,
               "master_ru": {"path": "MASTER_RU.md", **reader_projection.identity(master)},
               "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **reader_projection.identity(projection_path)},
               "source_toc": {"state": "absent", "source_pdf_sha256": PDF_HASH, "reason": "fixture source"},
               "body_links": [], "asset_choices": [selected_choice] if selected_choice is not None else [],
               "hit_points": {"presentation": "numeric"},
               "display_roles": roles}
    options["options_sha256"] = reader_projection.seal(options)
    options_path = options_root / "reader-options.json"
    _write(options_path, options)
    return master, projection_path, options_path


class ExtendedReflowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.master, self.projection, self.options = fixture(self.root)

    def _project(self):
        projection = json.loads(self.projection.read_text(encoding="utf-8"))
        options = reader_projection.load_options(self.options, self.master, self.projection)
        body, toc, _ = markdown_to_review_html(self.master.read_text(encoding="utf-8"), source_path=self.master,
                                               html_path=self.master.parent / "internal.html", blockquote_heading_offset=0)
        return reader_projection.project_reader_html(body, toc, projection, options,
                                                     options_path=self.options, master_root=self.master.parent)

    def _build(self):
        with patch("kb_creator.pipeline.five_step_language.verify_language_result",
                   return_value={"state": "verified", "inputs": {"source_pdf": {"identity": {"sha256": PDF_HASH}}}}):
            return five_step_docx.build_docx_package(self.master, self.root / "package", title="Map fixture",
                                                     reader_options=self.options)["manifest_path"].parent

    def _change(self, mutate):
        options = json.loads(self.options.read_text(encoding="utf-8"))
        mutate(options)
        options.pop("options_sha256")
        options["options_sha256"] = reader_projection.seal(options)
        _write(self.options, options)

    def test_guarded_furniture_title_and_fish_build_actual_docx_in_either_role_order(self):
        expected = {"word": "Он подслушивает. Разговор продолжился.",
                    "title": "Он может подняться и пройти дальше.",
                    "fish": "Эти люди будут периодически приходить."}
        base = self.root
        for case in ("word", "title", "fish"):
            rendered_by_order = []
            reports_by_order = []
            for reverse in (False, True):
                with self.subTest(case=case, reverse=reverse):
                    root = base / f"{case}-{reverse}"
                    self.master, self.projection, self.options = guarded_fixture(root, case, reverse=reverse)
                    rendered, _, report = self._project()
                    rendered_by_order.append(rendered)
                    reports_by_order.append(report)
                    assert expected[case] in html.fragment_fromstring(rendered, create_parent="main").text_content()
                    assert len(report["reflow_dependencies"]) == 1
                    if case == "title":
                        assert report["reflow_dependencies"][0]["retained_title_owners"][0]["source_page"] == 24
                        assert 24 in report["reflow_dependencies"][0]["source_pages"]
                    if case == "fish":
                        assert len(report["retained_image_dependencies"]) == 1
                    if not reverse:
                        self.root = root
                        package = self._build()
                        assert five_step_docx.verify_docx_package(package)["status"] == "verified_pending_visual_review"
                        with zipfile.ZipFile(package / "docx/document.docx") as archive:
                            if case == "fish":
                                fish = (self.master.parent / "assets/fish.jpg").read_bytes()
                                assert sum(archive.read(name) == fish for name in archive.namelist()
                                           if name.startswith("word/media/")) == 1
            assert rendered_by_order[0] == rendered_by_order[1]
            assert reports_by_order[0] == reports_by_order[1]

    def test_guarded_interval_rejects_missing_or_stale_furniture_and_false_routes(self):
        changes = {
            "missing_furniture": lambda options: options["display_roles"].pop(1),
            "stale_visual": lambda options: options["display_roles"][1]["source_evidence"]["source_visual"].update(
                {"sha256": "0" * 64}),
            "wrong_page": lambda options: options["display_roles"][1].update({"source_page": 53}),
            "skipped_marker": lambda options: options["display_roles"][0]["intervening_units"].pop(),
            "empty_fake_labels": lambda options: options["display_roles"][0].update({"intervening_asset_labels": []}),
            "interval_overlap": lambda options: options["display_roles"].append(
                copy.deepcopy(options["display_roles"][0])),
        }
        base = self.root
        for name, mutate in changes.items():
            with self.subTest(name=name):
                self.master, self.projection, self.options = guarded_fixture(base / name, "word")
                self._change(mutate)
                with self.assertRaises(ValueError):
                    self._project()
        for name, left, right in (("space", "Он подслушива ", None),
                                  ("digit", "Он 42", None),
                                  ("punctuation", "Он подслушива.", None),
                                  ("right_digit", None, "7Разговор.")):
            with self.subTest(name=name):
                self.master, self.projection, self.options = guarded_fixture(
                    base / name, "word", word_left=left, word_right=right)
                with self.assertRaisesRegex(ValueError, "letter boundaries"):
                    self._project()

    def test_guarded_title_requires_exact_casefold_and_supported_retained_heading(self):
        base = self.root
        for name, change in (
            ("missing_evidence", lambda options: options["display_roles"][-1].pop("source_evidence")),
            ("unsupported_owner", lambda options: options["display_roles"][-1].update(
                {"retained": {"unit_id": "guard-2", "ru_sha256":
                              hashlib.sha256("Автор сценария".encode()).hexdigest().upper()}})),
        ):
            with self.subTest(name=name):
                self.master, self.projection, self.options = guarded_fixture(base / name, "title")
                self._change(change)
                with self.assertRaises(ValueError):
                    self._project()
        self.master, self.projection, self.options = guarded_fixture(
            base / "different_word", "title", duplicate_title="## ПОСЛЕДНЕЕ ЖЕЛАНИЕ ДРУГОГО")
        with self.assertRaisesRegex(ValueError, "safe removal"):
            self._project()

    def test_reviewed_heading_level_mismatch_builds_docx_and_rejects_tampering(self):
        base = self.root
        rendered_by_order = []
        for reverse in (False, True):
            self.root = base / f"level-mismatch-{reverse}"
            self.master, self.projection, self.options = guarded_fixture(
                self.root, "title", reverse=reverse, title_level_mismatch=True)
            rendered, _, report = self._project()
            rendered_by_order.append(rendered)
            tree = html.fragment_fromstring(rendered, create_parent="main")
            self.assertEqual(len(tree.xpath('.//h1[contains(., "Последнее желание Уолтера")]')), 0)
            self.assertEqual(len(tree.xpath('.//h2[contains(., "ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА")]')), 1)
            self.assertEqual(report["reflow_dependencies"][0]["source_pages"], [24, 27, 28])
            if not reverse:
                package = self._build()
                self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                                 "verified_pending_visual_review")
        self.assertEqual(*rendered_by_order)

        for name, mutate in (
            ("missing_contract", lambda role: role.pop("heading_level_mismatch")),
            ("missing_evidence", lambda role: role["heading_level_mismatch"].pop("source_evidence")),
            ("empty_evidence", lambda role: role["heading_level_mismatch"].update(source_evidence=" ")),
            ("wrong_removed_level", lambda role: role["heading_level_mismatch"].update(removed_level=3)),
            ("wrong_retained_level", lambda role: role["heading_level_mismatch"].update(retained_level=3)),
            ("equal_levels", lambda role: role["heading_level_mismatch"].update(retained_level=1)),
            ("extra_field", lambda role: role["heading_level_mismatch"].update(guess=True)),
            ("missing_title_binding", lambda role: role.pop("retained")),
        ):
            with self.subTest(name=name):
                self.root = base / name
                self.master, self.projection, self.options = guarded_fixture(
                    self.root, "title", title_level_mismatch=True)
                self._change(lambda options: mutate(options["display_roles"][-1]))
                with self.assertRaises((ValueError, KeyError)):
                    self._project()
        self.root = base / "wrong-text"
        self.master, self.projection, self.options = guarded_fixture(
            self.root, "title", title_level_mismatch=True,
            duplicate_title="# Другое желание Уолтера")
        with self.assertRaisesRegex(ValueError, "safe removal"):
            self._project()

    def test_standalone_running_heading_participates_in_reflow_once_in_either_order(self):
        base = self.root
        outputs = []
        for reverse in (False, True):
            self.root = base / f"participating-standalone-{reverse}"
            self.master, self.projection, self.options = guarded_fixture(
                self.root, "title", reverse=reverse, title_level_mismatch=True)
            self._change(lambda options: next(role for role in options["display_roles"]
                                              if role["role"] == "repeated_title").update(
                                                  standalone_running_heading=True))
            rendered, _, report = self._project()
            outputs.append(rendered)
            tree = html.fragment_fromstring(rendered, create_parent="main")
            self.assertFalse(tree.xpath('.//h1[normalize-space()="Последнее желание Уолтера"]'))
            self.assertEqual(len(tree.xpath('.//h2[normalize-space()="ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА"]')), 1)
            self.assertIn("Он может подняться и пройти дальше.", tree.text_content())
            self.assertEqual(len(report["standalone_running_headings"]), 1)
            self.assertEqual(sum(role["role"] == "repeated_title"
                                 for role in report["display_roles"]), 1)
            self.assertEqual(report["reflow_dependencies"][0]["source_pages"], [24, 27, 28])
            if not reverse:
                package = self._build()
                self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                                 "verified_pending_visual_review")
                archived = json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))
                self.assertEqual(archived["standalone_running_headings"], report["standalone_running_headings"])
        self.assertEqual(*outputs)

    def test_participating_standalone_heading_rejects_tampered_evidence_and_protected_target(self):
        base = self.root
        for name, mutate in (
            ("false_opt_in", lambda role: role.update(standalone_running_heading=False)),
            ("non_bool_opt_in", lambda role: role.update(standalone_running_heading=1)),
            ("empty_evidence", lambda role: role.update(source_evidence=" ")),
            ("unknown_field", lambda role: role.update(guessed=True)),
            ("unknown_match", lambda role: role.update(text_match="fuzzy")),
            ("exact_case_mismatch", lambda role: role.update(text_match="exact")),
            ("missing_level_witness", lambda role: role.pop("heading_level_mismatch")),
            ("wrong_removed_level", lambda role: role["heading_level_mismatch"].update(removed_level=3)),
            ("wrong_retained_level", lambda role: role["heading_level_mismatch"].update(retained_level=3)),
            ("empty_level_evidence", lambda role: role["heading_level_mismatch"].update(source_evidence="")),
            ("stale_binding", lambda role: role["unit"].update(ru_sha256="0" * 64)),
        ):
            with self.subTest(name=name):
                self.root = base / name
                self.master, self.projection, self.options = guarded_fixture(
                    self.root, "title", title_level_mismatch=True)
                self._change(lambda options: options["display_roles"][-1].update(standalone_running_heading=True))
                self._change(lambda options: mutate(options["display_roles"][-1]))
                with self.assertRaises(ValueError):
                    self._project()
        self.root = base / "different-text"
        self.master, self.projection, self.options = guarded_fixture(
            self.root, "title", title_level_mismatch=True, duplicate_title="# Другое желание Уолтера")
        self._change(lambda options: options["display_roles"][-1].update(standalone_running_heading=True))
        with self.assertRaises(ValueError):
            self._project()
        self.root = base / "protected-title"
        self.master, self.projection, self.options = guarded_fixture(
            self.root, "title", title_level_mismatch=True)
        projection = json.loads(self.projection.read_text(encoding="utf-8"))
        bind = lambda index: {key: projection["units"][index][key] for key in ("unit_id", "ru_sha256")}
        self._change(lambda options: options["display_roles"][-1].update(standalone_running_heading=True))
        self._change(lambda options: options["body_links"].append({
            "unit": bind(2), "target": bind(9), "text": "сценария", "label": "сценария",
            "reason": "protect the running title"}))
        with self.assertRaises(ValueError):
            self._project()

    def test_guarded_fish_reopen_rejects_media_and_native_bookmark_tamper(self):
        word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        from kb_creator.scripts.production_docx import bookmark_name
        base = self.root
        for name in ("media", "bookmark"):
            with self.subTest(name=name):
                self.root = base / name
                self.master, self.projection, self.options = guarded_fixture(self.root, "fish")
                package = self._build()
                report = json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))
                def change(parts):
                    if name == "media":
                        member = next(member for member in parts if member.startswith("word/media/"))
                        parts[member] = b"wrong fish bytes"
                    else:
                        xml = etree.fromstring(parts["word/document.xml"])
                        anchor = bookmark_name(report["retained_image_dependencies"][0]["anchor"])
                        marker = next(node for node in xml.iter(f"{{{word}}}bookmarkStart")
                                      if node.get(f"{{{word}}}name") == anchor)
                        marker.getparent().remove(marker)
                        parts["word/document.xml"] = etree.tostring(xml, encoding="UTF-8", xml_declaration=True)
                self._tamper_docx(package, change)
                with self.assertRaises(five_step_docx.FiveStepDocxError):
                    five_step_docx.verify_docx_package(package)

    def test_guarded_rebind_rejects_changed_title_interval_and_fish_bytes(self):
        base = self.root
        for case in ("title", "fish"):
            with self.subTest(case=case):
                self.master, self.projection, self.options = guarded_fixture(base / case, case)
                old = json.loads(self.projection.read_text(encoding="utf-8"))
                old["source_spans"] = {"sha256": "F" * 64}
                new = copy.deepcopy(old)
                current = base / case / "current"
                shutil.copytree(self.master.parent, current)
                new_master = current / "MASTER_RU.md"
                new_projection = current / "semantic_context/RU_PROJECTION.json"
                def projections(root):
                    return ((old, self.master, self.projection) if root == self.master.parent
                            else (new, new_master, new_projection))
                def run(name):
                    with (patch.object(reader_options_rebind, "_projection", side_effect=projections),
                          patch.object(reader_options_rebind, "_same_assets")):
                        return reader_options_rebind.rebind_reader_options(
                            self.master.parent, current, self.options, base / case / name)
                assert run("unchanged")["state"] == "candidate_only"
                if case == "title":
                    new = copy.deepcopy(old)
                    retained = next(row for row in new["units"] if row["unit_id"] == "guard-1")
                    retained["ru_sha256"] = "0" * 64
                    with self.assertRaisesRegex(ValueError, "changed operand"):
                        run("changed-title")
                else:
                    new = copy.deepcopy(old)
                    new["units"].insert(4, _unit("injected", "Unreviewed interval prose."))
                    with self.assertRaisesRegex(ValueError, "topology changed|identical ordered source unit metadata"):
                        run("extra-interval")
                    new = copy.deepcopy(old)
                    (current / "assets/fish.jpg").write_bytes(b"changed source fish")
                    with self.assertRaisesRegex(ValueError, "figure bytes changed"):
                        run("changed-fish")

    def _tamper_docx(self, package, change):
        docx = package / "docx/document.docx"
        with zipfile.ZipFile(docx) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()}
        change(parts)
        with zipfile.ZipFile(docx, "w") as archive:
            for name, data in parts.items():
                archive.writestr(name, data)
        manifest_path = package / "DOCX_MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["docx"].update(five_step_docx._identity(docx, package))
        manifest["inventory"] = five_step_docx._inventory(package)
        manifest.pop("manifest_sha256")
        manifest["manifest_sha256"] = hashlib.sha256(five_step_docx._canonical(manifest)).hexdigest().upper()
        _write(manifest_path, manifest)

    def test_complete_route_preserves_map_and_both_role_orders(self):
        first, _, report = self._project()
        self.assertEqual(len(report["reflow_dependencies"]), 1)
        self.assertEqual(report["reflow_dependencies"][0]["joined_owner"]["text"], LEFT + " " + RIGHT)
        self.assertEqual(report["reflow_dependencies"][0]["joined_owner"]["paragraph_ordinal"], 1)
        self.assertEqual({row["source_page"] for row in report["reflow_page_witness"]}, {98, 99, 100})
        tree = html.fragment_fromstring(first, create_parent="main")
        self.assertIn(LEFT + " " + RIGHT, tree.text_content())
        self.assertEqual([item.text_content() for item in tree.xpath(".//ul/li") if item.text_content() in LABELS], LABELS)
        self.assertEqual(len(tree.xpath('.//figure/img[@src="assets/map.png"]')), 1)
        self.assertEqual(len(tree.xpath('.//h1[normalize-space()="Сценарий"]')), 1)
        self.assertEqual(len(report["omitted_artifacts"]), 4)
        other = self.root / "other"
        master, projection, options = fixture(other, title_first=True)
        body, toc, _ = markdown_to_review_html(master.read_text(encoding="utf-8"), source_path=master,
                                               html_path=master.parent / "internal.html", blockquote_heading_offset=0)
        second, _, second_report = reader_projection.project_reader_html(
            body, toc, json.loads(projection.read_text(encoding="utf-8")),
            reader_projection.load_options(options, master, projection), options_path=options, master_root=master.parent)
        self.assertEqual(first, second)
        self.assertEqual(report, second_report)

    def test_reviewed_selected_map_survives_actual_docx_and_replay(self):
        self.master, self.projection, self.options = fixture(self.root / "selected", selected_map=True)
        rendered, _, report = self._project()
        pair = report["reflow_dependencies"][0]["asset_pairs"][0]
        selected = self.options.parent / "selected/full-map.png"
        self.assertEqual(pair["reference"], "assets/reader/full-map.png")
        self.assertEqual(pair["identity"], reader_projection.identity(selected))
        self.assertEqual(report["retained_image_dependencies"][0]["identity"], reader_projection.identity(selected))
        self.assertEqual(len(html.fragment_fromstring(rendered, create_parent="main").xpath(
            './/figure/img[@src="assets/reader/full-map.png"]')), 1)
        package = self._build()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                         "verified_pending_visual_review")
        with zipfile.ZipFile(package / "docx/document.docx") as archive:
            self.assertIn(selected.read_bytes(), [archive.read(name) for name in archive.namelist()
                                                  if name.startswith("word/media/")])

    def test_singleton_list_label_owns_whole_list_in_actual_docx(self):
        self.master, self.projection, self.options = fixture(self.root / "singleton", singleton_label=True)
        rendered, _, report = self._project()
        pair = report["reflow_dependencies"][0]["asset_pairs"][0]
        tree = html.fragment_fromstring(rendered, create_parent="main")
        self.assertEqual(len(tree.xpath('.//ul[@id=$anchor]/li', anchor=pair["list_anchor"])), 1)
        package = self._build()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                         "verified_pending_visual_review")

    def test_partial_multiunit_list_label_rejected(self):
        self.master, self.projection, self.options = fixture(self.root / "partial", partial_list=True)
        projection = json.loads(self.projection.read_text(encoding="utf-8"))
        options = reader_projection.load_options(self.options, self.master, self.projection)
        body, toc, _ = markdown_to_review_html(self.master.read_text(encoding="utf-8"),
                                               source_path=self.master, html_path=self.master.parent / "internal.html",
                                               blockquote_heading_offset=0)
        tree = html.fragment_fromstring(body, create_parent="main")
        lists = tree.xpath('.//section[@data-page="099"]//ul')
        self.assertEqual(len(lists), 2)
        lists[0].append(lists[1][0])
        lists[1].getparent().remove(lists[1])
        joined_body = "".join(html.tostring(node, encoding="unicode") for node in tree)
        with self.assertRaisesRegex(ValueError, "whole flat list"):
            reader_projection.project_reader_html(joined_body, toc, projection, options,
                                                  options_path=self.options, master_root=self.master.parent)

    def test_selected_map_requires_exact_unique_opt_in_and_unchanged_bytes(self):
        cases = [
            ("missing_optin", lambda o: o["display_roles"][0]["intervening_asset_labels"][0]
             .pop("reviewed_asset_choice")),
            ("stale_optin", lambda o: o["display_roles"][0]["intervening_asset_labels"][0]
             ["reviewed_asset_choice"].update({"reason": "stale"})),
            ("ambiguous", lambda o: o["asset_choices"].append(copy.deepcopy(o["asset_choices"][0]))),
        ]
        for name, mutate in cases:
            with self.subTest(name=name):
                self.master, self.projection, self.options = fixture(self.root / name, selected_map=True)
                self._change(mutate)
                with self.assertRaises(ValueError):
                    self._project()
        self.master, self.projection, self.options = fixture(self.root / "changed", selected_map=True)
        Image.new("RGB", (180, 120), "purple").save(self.options.parent / "selected/full-map.png")
        with self.assertRaises(ValueError):
            self._project()

    def test_selected_map_replay_rejects_changed_embedded_media_and_image_omission(self):
        self.master, self.projection, self.options = fixture(self.root / "media", selected_map=True)
        package = self._build()
        def change(parts):
            member = next(name for name in parts if name.startswith("word/media/"))
            parts[member] = b"changed selected map"
        self._tamper_docx(package, change)
        with self.assertRaises(five_step_docx.FiveStepDocxError):
            five_step_docx.verify_docx_package(package)

        self.master, self.projection, self.options = fixture(self.root / "omit", selected_map=True)
        image_unit = json.loads(self.projection.read_text(encoding="utf-8"))["units"][9]
        def add_omission(options):
            role = copy.deepcopy(options["display_roles"][3])
            role["unit"] = _binding(image_unit)
            role["expected_raw_text"] = image_unit["ru_text"]
            options["display_roles"].append(role)
        self._change(add_omission)
        with self.assertRaises(ValueError):
            self._project()

    def test_real_docx_build_and_reopen(self):
        package = self._build()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"], "verified_pending_visual_review")

    def test_reopen_rejects_forged_joined_owner_witness(self):
        package = self._build()
        report_path = package / "READER_PROJECTION.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["reflow_dependencies"][0]["joined_owner"]["paragraph_ordinal"] = 0
        _write(report_path, report)
        manifest_path = package / "DOCX_MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["reader_projection"] = report
        _write(manifest_path, manifest)
        self._tamper_docx(package, lambda parts: None)
        with self.assertRaisesRegex(five_step_docx.FiveStepDocxError, "projection differs from replay"):
            five_step_docx.verify_docx_package(package)

    def test_reopen_rejects_invalid_native_bookmark_occurrence_and_owner(self):
        from kb_creator.scripts.production_docx import bookmark_name
        word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        for mutation in ("duplicate_continuation", "missing_end", "list_on_image", "title_on_other_text",
                         "both_continuations_on_title"):
            with self.subTest(mutation=mutation):
                self.root = self.root / mutation
                self.master, self.projection, self.options = fixture(self.root)
                package = self._build()
                self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                                 "verified_pending_visual_review")
                report = json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))
                dependency = report["reflow_dependencies"][0]
                def change(parts):
                    xml = etree.fromstring(parts["word/document.xml"])
                    def mark(anchor):
                        return next(node for node in xml.iter(f"{{{word}}}bookmarkStart")
                                    if node.get(f"{{{word}}}name") == bookmark_name(anchor))
                    if mutation in {"duplicate_continuation", "missing_end"}:
                        start = mark(dependency["right_anchor"])
                        ident = start.get(f"{{{word}}}id")
                        if mutation == "duplicate_continuation":
                            twin = copy.deepcopy(start)
                            twin.set(f"{{{word}}}id", "9001")
                            start.getparent().append(twin)
                            end = etree.Element(f"{{{word}}}bookmarkEnd")
                            end.set(f"{{{word}}}id", "9001")
                            start.getparent().append(end)
                        else:
                            end = next(node for node in xml.iter(f"{{{word}}}bookmarkEnd")
                                       if node.get(f"{{{word}}}id") == ident)
                            end.getparent().remove(end)
                    elif mutation == "both_continuations_on_title":
                        destination = mark(dependency["retained_title_anchors"][0]).getparent()
                        for anchor in (dependency["left_anchor"], dependency["right_anchor"]):
                            source = mark(anchor)
                            ident = source.get(f"{{{word}}}id")
                            end = next(node for node in xml.iter(f"{{{word}}}bookmarkEnd")
                                       if node.get(f"{{{word}}}id") == ident)
                            destination.append(source)
                            destination.append(end)
                    else:
                        if mutation == "list_on_image":
                            source = mark(dependency["asset_pairs"][0]["list_anchor"])
                            destination = mark(dependency["asset_pairs"][0]["image_anchor"]).getparent()
                        else:
                            source = mark(dependency["retained_title_anchors"][0])
                            destination = next(paragraph for paragraph in xml.iter(f"{{{word}}}p")
                                               if "Камеры включают" in "".join(paragraph.itertext()))
                        ident = source.get(f"{{{word}}}id")
                        end = next(node for node in xml.iter(f"{{{word}}}bookmarkEnd")
                                   if node.get(f"{{{word}}}id") == ident)
                        destination.append(source)
                        destination.append(end)
                    parts["word/document.xml"] = etree.tostring(xml, encoding="UTF-8", xml_declaration=True)
                self._tamper_docx(package, change)
                error = ("extended reflow joined paragraph text changed"
                         if mutation == "both_continuations_on_title" else ".*")
                with self.assertRaisesRegex(five_step_docx.FiveStepDocxError, error):
                    five_step_docx.verify_docx_package(package)

    def test_asset_labels_and_textual_handout_groups_compose_without_overlap(self):
        body, projection, options, bind = setup([
            "<!-- source-page-001 -->", "До карты", "## Меморандум", "Сохранённый пункт.",
            "<!-- source-page-002 -->", "- Первая метка\n- Первая метка", "![Карта](map.png)",
            "<!-- source-page-003 -->", "после карты.", "Конечный абзац.",
        ])
        Image.new("RGB", (40, 30), "blue").save(self.root / "map.png")
        decision = reflow(bind, 1, 8, [2, 3, 4, 5, 6, 7])
        decision["intervening_handout_groups"] = [handout_group(bind, [2, 3], 2)]
        decision["intervening_asset_labels"] = [{"unit": bind(5), "image": bind(6),
                                                 "source_evidence": "reviewed full labels",
                                                 "reason": "retain source labels and map"}]
        options["display_roles"] = [decision]
        rendered, _, report = reader_projection.project_reader_html(body, [], projection, options,
                                                                    master_root=self.root)
        self.assertIn("До карты после карты.", html.fragment_fromstring(rendered, create_parent="main").text_content())
        self.assertEqual(len(report["reflow_dependencies"]), 1)

    def test_unreviewed_or_conflicting_intermediate_fails_closed(self):
        cases = [
            ("unbound_list", lambda o: o["display_roles"][0].pop("intervening_asset_labels"), "unrelated|protected ownership"),
            ("wrong_order", lambda o: o["display_roles"][0]["intervening_asset_labels"][0].update(
                {"unit": o["display_roles"][0]["intervening_asset_labels"][0]["image"]}), "adjacent"),
            ("extra_field", lambda o: o["display_roles"][0]["intervening_asset_labels"][0].update(
                {"guess": True}), "exact reviewed fields"),
            ("missing_furniture", lambda o: o["display_roles"].pop(2), "unreviewed|unrelated"),
            ("missing_title", lambda o: o["display_roles"].pop(1), "unreviewed|unrelated"),
            ("stale_hash", lambda o: o["display_roles"][0]["intervening_asset_labels"][0]["unit"].update(
                {"ru_sha256": "0" * 64}), "preimage"),
        ]
        for name, mutate, error in cases:
            with self.subTest(name=name):
                self.root = self.root / name
                self.master, self.projection, self.options = fixture(self.root)
                self._change(mutate)
                with self.assertRaisesRegex(ValueError, error):
                    self._project()

    def test_reopen_rejects_lost_label_and_moved_continuation_bookmark(self):
        word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        for name in ("label", "bookmark"):
            self.root = self.root / name
            self.master, self.projection, self.options = fixture(self.root)
            package = self._build()
            report = json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))
            def change(parts):
                xml = etree.fromstring(parts["word/document.xml"])
                if name == "label":
                    node = next(node for node in xml.iter(f"{{{word}}}t") if node.text == "Метка 01")
                    node.text = "Потерянная метка"
                else:
                    from kb_creator.scripts.production_docx import bookmark_name
                    expected = bookmark_name(report["reflow_dependencies"][0]["right_anchor"])
                    marker = next(node for node in xml.iter(f"{{{word}}}bookmarkStart")
                                  if node.get(f"{{{word}}}name") == expected)
                    marker.getparent().remove(marker)
                parts["word/document.xml"] = etree.tostring(xml, encoding="UTF-8", xml_declaration=True)
            self._tamper_docx(package, change)
            with self.assertRaises(five_step_docx.FiveStepDocxError):
                five_step_docx.verify_docx_package(package)

    def test_reopen_rejects_original_map_media_substitution(self):
        package = self._build()
        def change(parts):
            member = next(name for name in parts if name.startswith("word/media/"))
            parts[member] = b"altered embedded map"
        self._tamper_docx(package, change)
        with self.assertRaisesRegex(five_step_docx.FiveStepDocxError, "original image bytes changed"):
            five_step_docx.verify_docx_package(package)

    def test_reopen_rejects_restored_blocks_and_missing_source_boundary(self):
        word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        from kb_creator.scripts.production_docx import bookmark_name
        for name in ("footer", "title", "right", "boundary", "retained_title_bookmark"):
            self.root = self.root / name
            self.master, self.projection, self.options = fixture(self.root)
            package = self._build()
            report = json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))
            def change(parts):
                xml = etree.fromstring(parts["word/document.xml"])
                if name in {"boundary", "retained_title_bookmark"}:
                    if name == "boundary":
                        page = next(row for row in report["reflow_page_witness"] if row["source_page"] == 99)
                        removed_anchor = page["boundary"]
                    else:
                        removed_anchor = report["reflow_dependencies"][0]["retained_title_anchors"][0]
                    marker = next(node for node in xml.iter(f"{{{word}}}bookmarkStart")
                                  if node.get(f"{{{word}}}name") == bookmark_name(removed_anchor))
                    marker.getparent().remove(marker)
                else:
                    page_number = 98 if name == "footer" else 100
                    page = next(row for row in report["reflow_page_witness"] if row["source_page"] == page_number)
                    marker = next(node for node in xml.iter(f"{{{word}}}bookmarkStart")
                                  if node.get(f"{{{word}}}name") == bookmark_name(page["boundary"]))
                    paragraph = next(parent for parent in marker.iterancestors() if parent.tag == f"{{{word}}}p")
                    restored = etree.Element(f"{{{word}}}p")
                    text = {"footer": "Книга", "title": "Сценарий", "right": RIGHT}[name]
                    etree.SubElement(etree.SubElement(restored, f"{{{word}}}r"), f"{{{word}}}t").text = text
                    paragraph.addnext(restored)
                parts["word/document.xml"] = etree.tostring(xml, encoding="UTF-8", xml_declaration=True)
            self._tamper_docx(package, change)
            with self.assertRaises(five_step_docx.FiveStepDocxError):
                five_step_docx.verify_docx_package(package)

    def test_retained_list_and_removed_title_reject_protected_links(self):
        for name, target_index in (("list", 8), ("title", 11)):
            self.root = self.root / name
            self.master, self.projection, self.options = fixture(self.root)
            unit = _binding(_unit(f"n197-{target_index}",
                                  LIST_TEXT if target_index == 8 else "# Сценарий"))
            self._change(lambda o: o["body_links"].append({
                "unit": {key: o["display_roles"][0]["units"][1][key] for key in ("unit_id", "ru_sha256")},
                "target": {key: unit[key] for key in ("unit_id", "ru_sha256")},
                "text": "послеоперационную", "label": "послеоперационную",
                "reason": "fixture protected incoming link"}))
            with self.assertRaisesRegex(ValueError, "conflicts|safe removal"):
                self._project()

    def test_standalone_running_heading_preserves_retained_chapter_and_incoming_link_in_docx(self):
        self.root = self.root / "standalone"
        self.master, self.projection, self.options = guarded_fixture(self.root, "standalone")
        projection = json.loads(self.projection.read_text(encoding="utf-8"))
        bind = lambda index: {key: projection["units"][index][key] for key in ("unit_id", "ru_sha256")}
        self._change(lambda options: options["body_links"].append({
            "unit": bind(5), "target": bind(1), "text": "название",
            "label": "название", "reason": "fixture link to retained chapter"}))
        rendered, _, report = self._project()
        tree = html.fragment_fromstring(rendered, create_parent="main")
        self.assertEqual(len(tree.xpath('.//h2[normalize-space()="ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА"]')), 1)
        self.assertEqual(len(tree.xpath('.//h1[normalize-space()="Последнее желание Уолтера"]')), 0)
        witness = report["standalone_running_headings"][0]
        self.assertEqual((witness["retained_page"], witness["removed_page"]), (20, 21))
        self.assertEqual(len(tree.xpath('.//p//a[@href=$ref]', ref="#" + witness["retained_anchor"])), 1)
        package = self._build()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                         "verified_pending_visual_review")
        archived = json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))
        self.assertEqual(archived["standalone_running_headings"], report["standalone_running_headings"])
        with zipfile.ZipFile(package / "docx/document.docx") as archive:
            document = etree.fromstring(archive.read("word/document.xml"))
            word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            visible = "".join(node.text or "" for node in document.iter(f"{{{word}}}t"))
            self.assertEqual(visible.count("ПОСЛЕДНЕЕ ЖЕЛАНИЕ УОЛТЕРА"), 2)
            self.assertNotIn("Последнее желание Уолтера", visible)

    def test_heading_binding_keeps_equal_text_plain_paragraph(self):
        self.master, self.projection, self.options = guarded_fixture(
            self.root / "heading-and-p", "standalone_heading_and_p")
        rendered, _, _ = self._project()
        tree = html.fragment_fromstring(rendered, create_parent="main")
        self.assertFalse(tree.xpath('.//h1[normalize-space()="Последнее желание Уолтера"]'))
        self.assertEqual(len(tree.xpath('.//p[normalize-space()="Последнее желание Уолтера"]')), 1)
        body, toc, _ = markdown_to_review_html(self.master.read_text(encoding="utf-8"),
                                               source_path=self.master,
                                               html_path=self.master.parent / "internal.html",
                                               blockquote_heading_offset=0)
        source_tree = html.fragment_fromstring(body, create_parent="main")
        heading = source_tree.xpath('.//h1[normalize-space()="Последнее желание Уолтера"]')[0]
        emphasis = etree.SubElement(heading, "em")
        emphasis.text, heading.text = heading.text, None
        changed = "".join(html.tostring(node, encoding="unicode") for node in source_tree)
        with self.assertRaisesRegex(ValueError, "exact HTML matches"):
            reader_projection.project_reader_html(
                changed, toc, json.loads(self.projection.read_text(encoding="utf-8")),
                reader_projection.load_options(self.options, self.master, self.projection),
                options_path=self.options, master_root=self.master.parent)

    def test_exact_heading_cohort_preserves_second_heading_in_actual_docx_replay(self):
        self.master, self.projection, self.options = guarded_fixture(
            self.root / "cohort", "standalone_heading_cohort")
        projection = json.loads(self.projection.read_text(encoding="utf-8"))
        bind = lambda index: {key: projection["units"][index][key] for key in ("unit_id", "ru_sha256")}
        witness = {"ordinal": 0, "cohort": [bind(4), bind(5)]}
        with self.assertRaisesRegex(ValueError, "exact HTML matches"):
            self._project()
        self._change(lambda options: options["display_roles"][0].update(
            heading_occurrence=copy.deepcopy(witness)))
        rendered, _, report = self._project()
        tree = html.fragment_fromstring(rendered, create_parent="main")
        self.assertEqual(len(tree.xpath('.//h1[normalize-space()="Последнее желание Уолтера"]')), 1)
        self.assertEqual(len(tree.xpath('.//p[normalize-space()="Последнее желание Уолтера"]')), 1)
        self.assertEqual(report["standalone_running_headings"][0]["heading_occurrence"], witness)
        package = self._build()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                         "verified_pending_visual_review")
        archived = json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))
        self.assertEqual(archived["standalone_running_headings"][0]["heading_occurrence"], witness)
        with zipfile.ZipFile(package / "docx/document.docx") as archive:
            document = etree.fromstring(archive.read("word/document.xml"))
            word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            visible = "".join(node.text or "" for node in document.iter(f"{{{word}}}t"))
            self.assertIn("Последнее желание Уолтера", visible)
            owners = [paragraph for paragraph in document.iter(f"{{{word}}}p")
                      if "".join(node.text or "" for node in paragraph.iter(f"{{{word}}}t"))
                      == "Последнее желание Уолтера"]
            self.assertGreaterEqual(len(owners), 2)
            styles = [paragraph.find(f"{{{word}}}pPr/{{{word}}}pStyle") for paragraph in owners]
            self.assertEqual(sum(style is not None and style.get(f"{{{word}}}val") == "Heading1"
                                 for style in styles), 1)
            self.assertGreaterEqual(sum(style is None for style in styles), 1)

    def test_heading_cohort_rejects_stale_incomplete_reordered_and_wrong_ordinal(self):
        for name in ("stale", "incomplete", "reordered", "wrong_ordinal"):
            with self.subTest(name=name):
                self.master, self.projection, self.options = guarded_fixture(
                    self.root / name, "standalone_heading_cohort")
                projection = json.loads(self.projection.read_text(encoding="utf-8"))
                bind = lambda index: {key: projection["units"][index][key]
                                      for key in ("unit_id", "ru_sha256")}
                witness = {"ordinal": 0, "cohort": [bind(4), bind(5)]}
                if name == "stale": witness["cohort"][0]["ru_sha256"] = "0" * 64
                if name == "incomplete": witness["cohort"].pop()
                if name == "reordered": witness["cohort"].reverse()
                if name == "wrong_ordinal": witness["ordinal"] = 1
                self._change(lambda options: options["display_roles"][0].update(
                    heading_occurrence=witness))
                with self.assertRaisesRegex(ValueError, "heading occurrence"):
                    self._project()

    def test_standalone_running_heading_rejects_missing_or_stale_contract_and_protected_targets(self):
        self.master, self.projection, self.options = guarded_fixture(
            self.root / "same_level", "standalone_same_level")
        rendered, _, report = self._project()
        self.assertEqual(len(report["standalone_running_headings"]), 1)
        self.assertEqual(len(html.fragment_fromstring(rendered, create_parent="main").xpath(
            './/h2[normalize-space()="Последнее желание Уолтера"]')), 0)
        for name, mutate in (
            ("missing_opt_in", lambda role: role.pop("standalone_running_heading")),
            ("false_opt_in", lambda role: role.update(standalone_running_heading=False)),
            ("missing_evidence", lambda role: role.pop("source_evidence")),
            ("empty_evidence", lambda role: role.update(source_evidence=" ")),
            ("missing_level_witness", lambda role: role.pop("heading_level_mismatch")),
            ("wrong_removed_level", lambda role: role["heading_level_mismatch"].update(removed_level=2)),
            ("wrong_retained_level", lambda role: role["heading_level_mismatch"].update(retained_level=1)),
            ("unknown_field", lambda role: role.update(guessed=True)),
        ):
            with self.subTest(name=name):
                self.master, self.projection, self.options = guarded_fixture(self.root / name, "standalone")
                self._change(lambda options: mutate(options["display_roles"][0]))
                with self.assertRaises(ValueError):
                    self._project()
        for case in ("standalone_same_page", "standalone_later_retained",
                     "standalone_retained_removed"):
            with self.subTest(case=case):
                self.master, self.projection, self.options = guarded_fixture(self.root / case, case)
                with self.assertRaises(ValueError):
                    self._project()
        self.master, self.projection, self.options = guarded_fixture(
            self.root / "wrong_text", "standalone", duplicate_title="# Другое желание Уолтера")
        with self.assertRaises(ValueError):
            self._project()
        self.master, self.projection, self.options = guarded_fixture(self.root / "review_anchor", "standalone")
        projection = json.loads(self.projection.read_text(encoding="utf-8"))
        bind = lambda index: {key: projection["units"][index][key] for key in ("unit_id", "ru_sha256")}
        self._change(lambda options: options["display_roles"].append({
            "role": "source_issue_review_anchor", "issue_id": "running-heading-review",
            "unit": bind(4), "source_page": 21, "en_excerpt": "Running title",
            "source_evidence": "reviewed fixture", "reason": "protected review location",
            "placement": "first_visible_text_block_v1"}))
        with self.assertRaises(ValueError):
            self._project()
        self.master, self.projection, self.options = guarded_fixture(self.root / "protected", "standalone")
        projection = json.loads(self.projection.read_text(encoding="utf-8"))
        bind = lambda index: {key: projection["units"][index][key] for key in ("unit_id", "ru_sha256")}
        self._change(lambda options: options["body_links"].append({
            "unit": bind(5), "target": bind(4), "text": "название",
            "label": "название", "reason": "fixture protected running heading"}))
        with self.assertRaises(ValueError):
            self._project()

    def test_standalone_running_heading_survives_archived_guarded_replay(self):
        self.root = self.root / "standalone-replay"
        self.master, self.projection, self.options = guarded_fixture(self.root, "title_plus_standalone")
        rendered, _, report = self._project()
        tree = html.fragment_fromstring(rendered, create_parent="main")
        self.assertEqual(len(report["reflow_dependencies"]), 1)
        self.assertEqual(len(report["standalone_running_headings"]), 1)
        self.assertFalse(tree.xpath('.//h1[normalize-space()="Последнее желание Уолтера"]'))
        package = self._build()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                         "verified_pending_visual_review")
        archived = json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))
        self.assertEqual(archived["standalone_running_headings"], report["standalone_running_headings"])

    def test_plain_paragraph_group_preserves_caption_media_and_single_encoded_handout(self):
        for case, joined, caption in (
            ("caption", "Вести приходят позже.", "Раздаточный материал 5"),
            ("single", "В библиотеке тише, чем обычно.", "ZG ZIGLT KTQROFU ZIOL FGZT."),
        ):
            with self.subTest(case=case):
                self.root = self.root / case
                self.master, self.projection, self.options = guarded_fixture(self.root, case)
                rendered, _, report = self._project()
                tree = html.fragment_fromstring(rendered, create_parent="main")
                self.assertIn(joined, tree.text_content())
                caption_nodes = tree.xpath('.//p[normalize-space()=$text]', text=caption)
                self.assertEqual(len(caption_nodes), 1)
                self.assertTrue(caption_nodes[0].get("id"))
                narrative = next(node for node in tree.xpath(".//p") if joined in node.text_content())
                self.assertLess(list(tree.iter()).index(narrative), list(tree.iter()).index(caption_nodes[0]))
                self.assertEqual(len(report["reflow_dependencies"]), 1)
                package = self._build()
                self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                                 "verified_pending_visual_review")
                with zipfile.ZipFile(package / "docx/document.docx") as archive:
                    xml = etree.fromstring(archive.read("word/document.xml"))
                    word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
                    text = "".join(node.text or "" for node in xml.iter(f"{{{word}}}t"))
                    self.assertIn(caption, text)
                    if case == "caption":
                        image = (self.master.parent / "assets/letter.jpg").read_bytes()
                        self.assertEqual(sum(archive.read(name) == image for name in archive.namelist()
                                             if name.startswith("word/media/")), 1)

    def test_plain_paragraph_group_rejects_missing_stale_structured_and_unknown_kind(self):
        cases = {
            "missing_opt_in": lambda group: group.pop("title_kind"),
            "stale": lambda group: group["title"].update({"ru_sha256": "0" * 64}),
            "missing_member": lambda group: group["units"].pop(),
            "unknown_kind": lambda group: group.update({"title_kind": "caption"}),
            "unknown_shape": lambda group: group.update({"title_kind": ["plain_paragraph"]}),
        }
        for name, change in cases.items():
            with self.subTest(name=name):
                self.master, self.projection, self.options = guarded_fixture(self.root / name, "caption")
                self._change(lambda options: change(options["display_roles"][0]["intervening_handout_groups"][0]))
                with self.assertRaises(ValueError):
                    self._project()
        self.master, self.projection, self.options = guarded_fixture(
            self.root / "structured", "caption", caption_text="> Раздаточный материал 5")
        with self.assertRaises(ValueError):
            self._project()

    def test_backward_chained_plain_paragraph_reflows_preserve_all_boundaries(self):
        self.root = self.root / "chain"
        self.master, self.projection, self.options = guarded_fixture(self.root, "chain")
        rendered, _, report = self._project()
        tree = html.fragment_fromstring(rendered, create_parent="main")
        joined = "Начало середина конец."
        self.assertEqual(sum(joined in node.text_content() for node in tree.xpath(".//p")), 1)
        self.assertEqual(len(report["reflow_dependencies"]), 2)
        self.assertEqual(len(tree.xpath('.//p[normalize-space()="Подпись первого материала"]')), 1)
        self.assertEqual(len(tree.xpath('.//p[normalize-space()="Подпись второго материала"]')), 1)
        package = self._build()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                         "verified_pending_visual_review")

    def test_rebind_requires_unchanged_list_image_and_original_bytes(self):
        old = json.loads(self.projection.read_text(encoding="utf-8"))
        old["source_spans"] = {"sha256": "F" * 64}
        new = copy.deepcopy(old)
        current_root = self.root / "current"
        shutil.copytree(self.master.parent, current_root)
        current_master = current_root / "MASTER_RU.md"
        current_projection = current_root / "semantic_context/RU_PROJECTION.json"
        def projections(root):
            return ((old, self.master, self.projection) if root == self.master.parent
                    else (new, current_master, current_projection))
        def rebind(name, reviewed=None):
            with (patch.object(reader_options_rebind, "_projection", side_effect=projections),
                  patch.object(reader_options_rebind, "_same_assets")):
                return reader_options_rebind.rebind_reader_options(self.master.parent, current_root, self.options,
                                                                   self.root / name, reviewed)
        self.assertEqual(rebind("rebound")["state"], "candidate_only")
        self.assertEqual((self.root / "rebound/evidence/source.png").read_bytes(),
                         (self.options.parent / "evidence/source.png").read_bytes())
        for uid in ("n197-8", "n197-9"):
            new = copy.deepcopy(old)
            unit = next(row for row in new["units"] if row["unit_id"] == uid)
            unit["ru_text"] += "!"
            unit["ru_sha256"] = hashlib.sha256(unit["ru_text"].encode()).hexdigest().upper()
            reviewed = self.root / ("reviewed-" + uid + ".json")
            prior = next(row for row in old["units"] if row["unit_id"] == uid)
            _write(reviewed, [{"unit_id": uid, "prior_ru_sha256": prior["ru_sha256"],
                               "current_ru_sha256": unit["ru_sha256"], "reason": "generic changed hash"}])
            with self.assertRaisesRegex(ValueError, "changed operand"):
                rebind("changed-" + uid, reviewed)
        new = copy.deepcopy(old)
        (current_root / "assets/map.png").write_bytes(b"altered map")
        with self.assertRaisesRegex(ValueError, "original map bytes changed"):
            rebind("changed-image-bytes")


if __name__ == "__main__":
    unittest.main()
