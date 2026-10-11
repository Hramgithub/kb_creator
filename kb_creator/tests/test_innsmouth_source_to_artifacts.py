from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "kb_creator/scripts/build_innsmouth_source_to_artifacts.py"
PREPARE_SCRIPT = ROOT / "kb_creator/scripts/prepare_translation_batches.py"
MERGE_SCRIPT = ROOT / "kb_creator/scripts/merge_translation_batches.py"
KEEPER_SCRIPT = ROOT / "kb_creator/scripts/build_keeperbook_from_ru_master.py"
STATBLOCK_SCRIPT = ROOT / "kb_creator/scripts/project_innsmouth_statblocks_from_ru.py"
COMPARE_SCRIPT = ROOT / "kb_creator/scripts/compare_innsmouth_artifacts.py"
SOURCE_INTEGRITY_AUDIT_SCRIPT = ROOT / "kb_creator/scripts/audit_innsmouth_source_pdf_integrity.py"


def load_module():
    name = "build_innsmouth_source_to_artifacts"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_script(path: Path, name: str):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


def test_runner_does_not_define_old_innsmouth_root_as_source_root() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    forbidden_assignments = [
        "SCENARIO_ROOT = ROOT / \"CoC/Working/Scenarios/The_Innsmouth_Terror\"",
        "DEFAULT_MANIFEST = ROOT / \"kb_creator/inputs/innsmouth_v6_freeze_manifest.json\"",
    ]
    for forbidden in forbidden_assignments:
        assert forbidden not in text


def test_legacy_dependency_guard_flags_old_paths_and_reference_inputs() -> None:
    module = load_module()
    config = {
        "source": "CoC/Working/Scenarios/The_Innsmouth_Terror/Formatted/old.md",
        "output": "CoC/Output/Scenarios/The_Innsmouth_Terror/For_Keeper/KeeperBook_v6.md",
        "reference": str(module.REFERENCE_KEEPER),
    }
    findings = module.legacy_dependency_findings(config)
    codes = {item["code"] for item in findings}
    assert "legacy_innsmouth_path_in_config" in codes
    assert "reference_artifact_used_as_input" in codes


def test_runner_treats_reconstruct_column_ocr_review_as_expected_gate() -> None:
    module = load_module()
    record = {
        "command": ["python", "translator/translator.py", "reconstruct-column-ocr", "--force", "--apply"],
        "stdout": "status=needs_review mode=apply pages=44 chars=118656 chunks=44 findings=2 gate_changed=false\n",
    }
    assert module.command_is_expected_gate(record)


def test_structured_pdf_lines_preserve_left_to_right_column_order() -> None:
    module = load_module()
    lines = [
        {"text": "Anna Diaz, age 26, producer", "top": 100.0, "bottom": 110.0, "x0": 80.0, "x1": 260.0, "column": "left"},
        {"text": "Anna has encyclopedic knowledge.", "top": 115.0, "bottom": 125.0, "x0": 80.0, "x1": 270.0, "column": "left"},
        {
            "text": "Christopher McGuire, age 37, engineer",
            "top": 98.0,
            "bottom": 108.0,
            "x0": 360.0,
            "x1": 540.0,
            "column": "right",
        },
        {"text": "A tall white man with curly hair.", "top": 113.0, "bottom": 123.0, "x0": 360.0, "x1": 530.0, "column": "right"},
    ]
    ordered = module.ordered_structured_page_lines(lines)
    blocks = module.lines_to_structured_blocks(ordered)
    text = module.render_structured_blocks_markdown(blocks)

    assert text.index("Anna Diaz") < text.index("Christopher McGuire")


def test_structured_pdf_blocks_keep_bullets_and_keeper_note_separate() -> None:
    module = load_module()
    lines = [
        {"text": "THE BREWSTER RESIDENCE", "top": 70.0, "bottom": 80.0, "x0": 60.0, "x1": 220.0, "column": "left"},
        {"text": "Investigators can arrive at the residence.", "top": 96.0, "bottom": 106.0, "x0": 60.0, "x1": 260.0, "column": "left"},
        {"text": "The house is currently occupied.", "top": 111.0, "bottom": 121.0, "x0": 60.0, "x1": 260.0, "column": "left"},
        {"text": "• Asking Sammy about Ginny, he confirms.", "top": 90.0, "bottom": 100.0, "x0": 330.0, "x1": 560.0, "column": "right"},
        {"text": "• Asked about the Atlantean Jewel, Sammy confirms.", "top": 121.0, "bottom": 131.0, "x0": 330.0, "x1": 560.0, "column": "right"},
        {"text": "Keeper note: in most cases, the investigators will recover", "top": 590.0, "bottom": 600.0, "x0": 330.0, "x1": 560.0, "column": "right"},
        {"text": "the Atlantean Jewel knowing that Ginny stole it.", "top": 605.0, "bottom": 615.0, "x0": 330.0, "x1": 560.0, "column": "right"},
    ]
    blocks = module.lines_to_structured_blocks(module.ordered_structured_page_lines(lines))
    kinds = [block["kind"] for block in blocks]
    rendered = module.render_structured_blocks_markdown(blocks)

    assert kinds[:2] == ["heading", "paragraph"]
    assert kinds.count("bullet") == 2
    assert "Keeper note:" in rendered
    assert rendered.index("THE BREWSTER RESIDENCE") < rendered.index("- Asking Sammy")
    assert "\n\n- Asked about the Atlantean Jewel" in rendered
    assert "\n\n> Keeper note:" in rendered


def test_innsmouth_source_page_overrides_repair_known_layout_failures() -> None:
    module = load_module()
    broken = """<!-- source-page-005 -->

“We shall swim out to that brooding reef in the sea and dive Y’ha-nthlei, and in that lair of the Deep Ones

INTRODUCTION

Lights, Camera, Action!

down through black abysses to Cyclopean and many-columned we shall dwell amidst wonder and glory for ever.”

<!-- source-page-006 -->

The Second Oath: ...

Table 1: timeline

Evening of the The Epic finale begins filming. 2nd day

InformatIon

The Third Oath: ...

of events

the Jewel.

<!-- source-page-023 -->

Table 2:

1D100

What Luck: The Investigators discover 1-5 feels like a great little caper scampering

encounters in the caves

<!-- source-page-031 -->

the

Playing the Hero Investigators making their way determinedly up to the cliffs.

epIc fInale

What if they’re captured? Captured investigators wake up tied-up on the cliff-face and see the Epic Finale playing out in front of them.
"""

    fixed, applied = module.apply_innsmouth_source_page_overrides(broken)

    assert [item["page"] for item in applied] == ["005", "006", "023", "031"]
    assert fixed.index("glory for ever.”") < fixed.index("INTRODUCTION")
    assert fixed.index("The Second Oath") < fixed.index("The Third Oath") < fixed.index("Table 1: timeline of events")
    assert "InformatIon" not in fixed
    assert "\nof events\n" not in fixed
    assert "| Evening of the 2nd day | The Epic finale begins filming. |" in fixed
    assert "| 1D100 | Description |" in fixed
    assert "| 96-100 | Close encounters:" in fixed
    assert "What Luck: The Investigators discover 1-5 feels like" not in fixed
    page_031 = fixed.split("<!-- source-page-031 -->", 1)[1]
    assert page_031.startswith("\n\nPlaying the Hero\n\nInvestigators making")
    assert "\nthe\n" not in page_031
    assert "epIc fInale" not in page_031
    assert "What if they’re captured?" not in page_031


def test_source_structure_hazard_audit_allows_long_markdown_tables() -> None:
    module = load_module()
    tmp_path = ROOT / "kb_creator/working/test_source_structure_hazard_audit"
    tmp_path.mkdir(parents=True, exist_ok=True)
    source = tmp_path / "source.md"
    keeper = tmp_path / "keeper.md"
    report = tmp_path / "report.json"
    long_cell = "A long table cell. " * 220
    pages = {f"{page:03d}": "Placeholder page." for page in range(1, 47)}
    pages["009"] = "Anna Diaz, age 26\n\nChristopher McGuire, age 37"
    pages["012"] = "ORNE LIBRARY\n\nTHE ARKHAM ADVERTISER"
    pages["023"] = "Table 2: encounters in the caves\n\n| 1D100 | Description |\n| --- | --- |\n| 1-5 | " + long_cell.strip() + " |"
    pages["024"] = "THE BREWSTER RESIDENCE\n\nAsking Sammy about Ginny\n\n> Keeper note: in most cases"
    body = "\n\n".join(f"<!-- source-page-{page} -->\n\n{text}" for page, text in pages.items())
    source.write_text(body, encoding="utf-8")
    keeper.write_text(body, encoding="utf-8")

    record = module.source_structure_hazard_audit(source, keeper, report)

    assert record["returncode"] == 0
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["status"] == "pass"
    assert not data["findings"]


def test_source_integrity_audit_does_not_flag_markdown_table_as_collapsed_prose() -> None:
    audit = load_script(SOURCE_INTEGRITY_AUDIT_SCRIPT, "audit_innsmouth_source_pdf_integrity")
    row = {
        "pdf_left_first_line": "Table 2:",
        "pdf_right_first_line": "encounters in the caves",
        "pdf_paragraph_blocks": 28,
        "pdf_chars_no_ws": 1000,
        "source_chars_no_ws": 1000,
    }
    source_page = "Table 2: encounters in the caves\n\n| 1D100 | Description |\n| --- | --- |\n| 1-5 | What Luck. |"
    source_blocks = audit.source_text_blocks(source_page)

    assert "paragraphs_collapsed_in_normalized_source" not in audit.detect_fragile_flow(
        row, source_blocks, source_page
    )


def test_occluded_text_layer_content_is_recorded_but_excluded_from_main_source() -> None:
    module = load_module()
    tmp_path = ROOT / "kb_creator/working/test_occluded_text_layer_content"
    report = tmp_path / "occluded_text_layer_recovered_content.json"
    receipt = module.write_innsmouth_occluded_text_layer_artifact(report)
    data = json.loads(report.read_text(encoding="utf-8"))
    source_text, _ = module.apply_innsmouth_source_page_overrides("<!-- source-page-031 -->\n\nWhat if they’re captured?\n")

    assert receipt["count"] == 1
    assert data["policy"]["main_source"] == "exclude"
    assert data["items"][0]["classification"] == "occluded_text_layer_recovered_content"
    assert "What if they’re captured?" in data["items"][0]["text"]
    assert "What if they’re captured?" not in source_text


def test_source_cleanup_strips_old_printed_page_numbers_but_keeps_source_toc_numbers() -> None:
    module = load_module()
    text = """<!-- source-page-004 -->

1
Введение

<!-- source-page-008 -->

4
Genevieve ‘Ginny’ Dubois

<!-- source-page-013 -->

START: Arkham
9
THE MISKATONIC PLAYHOUSE
"""

    cleaned, report = module.strip_printed_page_number_residue(text)

    page_004 = cleaned.split("<!-- source-page-004 -->", 1)[1].split("<!-- source-page-008 -->", 1)[0]
    assert "\n1\n" in page_004
    assert "\n4\n" not in cleaned.split("<!-- source-page-008 -->", 1)[1].split("<!-- source-page-013 -->", 1)[0]
    assert "\n9\n" not in cleaned.split("<!-- source-page-013 -->", 1)[1]
    assert report["count"] == 2


def test_source_art_anchor_layer_maps_npc_art_to_character_source_anchor() -> None:
    module = load_module()
    source_text = """# The Innsmouth Terror

<!-- source-page-008 -->

DRAMATIS PERSONAE

Genevieve ‘Ginny’ Dubois, age 25, actor

P.A. Bazzledon, age 40, producer
"""
    art_manifest = {
        "placements": [
            {
                "placement_id": "xref-00367",
                "asset_id": "xref-00367",
                "source_page": "008",
                "semantic_role": "npc",
                "runtime_role": "npc",
                "emit_reader_art_block": True,
                "runtime_src": "Images/NPC/innsmouth-page-008-xref-00367-npc.png",
            },
            {
                "placement_id": "xref-00379",
                "asset_id": "xref-00379",
                "source_page": "008",
                "semantic_role": "npc",
                "runtime_role": "npc",
                "emit_reader_art_block": True,
                "runtime_src": "Images/NPC/innsmouth-page-008-xref-00379-npc.png",
            },
        ]
    }

    pdf_layout = {
        "pages": {
            "008": {
                "images": {
                    "367": [[332.1, 420.9, 534.2, 704.3]],
                    "379": [[325.6, 86.9, 536.5, 367.9]],
                },
                "text_blocks": [
                    {"bbox": [370.0, 373.6, 494.8, 391.0], "text": "Genevieve ‘Ginny’ Dubois"},
                    {"bbox": [403.5, 719.1, 465.4, 730.5], "text": "P.A. Bazzledon"},
                ],
            }
        }
    }

    manifest, report = module.build_source_art_anchor_manifest(source_text, art_manifest, pdf_layout)
    keeper_en = module.build_keeperbook_en_with_source_art_anchors(source_text, manifest)
    placements = manifest["placements"]

    assert report["status"] == "pass"
    assert placements[0]["source_anchor_text"] == "P.A. Bazzledon"
    assert placements[1]["source_anchor_text"] == "Genevieve ‘Ginny’ Dubois"
    assert placements[0]["source_anchor_method"] == "npc_caption_match"
    assert placements[1]["source_anchor_method"] == "npc_caption_match"
    assert report["counts"]["page_fallbacks"] == 0
    assert 'data-placement-id="xref-00367"' in keeper_en
    assert keeper_en.index("Genevieve") < keeper_en.index('data-placement-id="xref-00379"') < keeper_en.index("P.A. Bazzledon")
    assert keeper_en.index("P.A. Bazzledon") < keeper_en.index('data-placement-id="xref-00367"')


def test_source_art_anchor_layer_blocks_missing_runtime_src() -> None:
    module = load_module()
    source_text = """<!-- source-page-002 -->

INTRODUCTION
"""
    art_manifest = {
        "placements": [
            {
                "placement_id": "xref-00058",
                "asset_id": "xref-00058",
                "source_page": "002",
                "semantic_role": "atmospheric",
                "runtime_role": "atmospheric",
                "emit_reader_art_block": True,
            }
        ]
    }

    manifest, report = module.build_source_art_anchor_manifest(source_text, art_manifest)

    assert manifest["status"] == "fail"
    assert report["status"] == "fail"
    assert report["findings"][0]["code"] == "reader_art_missing_runtime_src"


def test_source_art_anchor_layer_uses_bbox_nearest_source_text() -> None:
    module = load_module()
    source_text = """<!-- source-page-020 -->

McGuire’s Lab Wooden lab benches cover one entire length of this room.

Though the lab may be messy, there’s not really anywhere to hide in it.
"""
    art_manifest = {
        "placements": [
            {
                "placement_id": "xref-00732",
                "asset_id": "xref-00732",
                "source_page": "020",
                "source_xref": 732,
                "semantic_role": "source_image",
                "runtime_role": "source_image",
                "emit_reader_art_block": True,
                "runtime_src": "Images/Source_Images/innsmouth-page-020-xref-00732-source_image.png",
            }
        ]
    }
    pdf_layout = {
        "pages": {
            "020": {
                "images": {"732": [[0.0, 200.0, 600.0, 790.0]]},
                "text_blocks": [
                    {
                        "bbox": [36.0, 70.0, 290.0, 218.0],
                        "text": "McGuire’s Lab Wooden lab benches cover one entire length of this room.",
                    },
                    {
                        "bbox": [36.0, 221.0, 290.0, 266.0],
                        "text": "Though the lab may be messy, there’s not really anywhere to hide in it.",
                    },
                ],
            }
        }
    }

    manifest, report = module.build_source_art_anchor_manifest(source_text, art_manifest, pdf_layout)
    placement = manifest["placements"][0]

    assert report["status"] == "pass"
    assert report["counts"]["page_fallbacks"] == 0
    assert placement["source_anchor_method"] == "nearest_source_text_bbox"
    assert placement["source_anchor_kind"] == "paragraph_lead"
    assert placement["source_anchor_text"].startswith("McGuire’s Lab")
    assert placement["source_anchor_bbox"] == [36.0, 70.0, 290.0, 218.0]


def test_keeperbook_strips_heading_prefix_from_first_paragraph() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    source = """# Иннсмутский ужас

<!-- source-page-031 -->

### Эпический финал

Эпический финал Наконец на Иннсмут обрушивается обещанная буря.

### Универсальный магазин

Универсальный магазин - известная сеть магазинов.
"""

    fixed, report = keeper.strip_heading_prefix_from_first_paragraph(source)

    assert report["count"] == 2
    assert "### Эпический финал\n\nНаконец на Иннсмут" in fixed
    assert "### Универсальный магазин\n\nИзвестная сеть магазинов." in fixed
    assert keeper.heading_qa(fixed)["heading_prefix_duplicates"] == []


def test_keeperbook_rejects_source_only_reconstruction_comments_in_ru_master() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master_reader_gate")
    clean_source = "# Иннсмутский ужас\n\n<!-- source-page-001 -->\n\nЧитательский текст.\n"

    keeper.validate_reader_master(clean_source)
    for marker, kind in (
        ("<!-- mineru-page: 32 -->", "mineru-page"),
        ("<!-- table-evidence: tbl-p032-003 -->", "table-evidence"),
    ):
        try:
            keeper.build_keeperbook(f"{clean_source}\n{marker}\n", "v1")
        except ValueError as exc:
            message = str(exc)
            assert message.startswith("E_RU_READER_MASTER_TECHNICAL_COMMENT:")
            assert kind in message
        else:
            raise AssertionError(f"RU reader-master gate accepted {kind}")


def test_keeperbook_keeps_character_metadata_in_heading_after_art_injection() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    source = """# Иннсмутский ужас

<!-- source-page-009 -->

Действующие лица

Anna Díaz, 26 лет, продюсер

Christopher McGuire, 37 лет, инженер
"""

    fixed = keeper.build_keeperbook(source, "v1")
    fixed = fixed.replace(
        "### Anna Díaz\n\n26 лет, продюсер",
        "### Anna Díaz\n\n<div class=\"keeper-art-block\"></div>\n\n26 лет, продюсер Технически блестящая актриса.",
    )
    fixed = fixed.replace(
        "### Christopher McGuire\n\n37 лет, инженер",
        "### Christopher McGuire\n\n<div class=\"keeper-art-block\"></div>\n\n37 лет, инженер Высокий мужчина.",
    )
    fixed, report = keeper.merge_main_character_heading_metadata(fixed)
    qa = keeper.heading_qa(fixed)

    assert report["count"] == 2
    assert "### Anna Díaz, 26 лет, продюсер\n\n<div class=\"keeper-art-block\"></div>" in fixed
    assert "### Christopher McGuire, 37 лет, инженер\n\n<div class=\"keeper-art-block\"></div>" in fixed
    assert "\n\nТехнически блестящая актриса." in fixed
    assert "\n\nВысокий мужчина." in fixed
    assert "\n\n26 лет, продюсер" not in fixed
    assert "\n\n37 лет, инженер" not in fixed
    assert "\n, 26 лет" not in fixed
    assert "\n, 37 лет" not in fixed
    assert qa["heading_tail_residues"] == []


def test_keeperbook_keeps_character_body_with_lead_not_caption_residue() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    source = """# Иннсмутский ужас

<!-- source-page-008 -->

ДЕЙСТВУЮЩИЕ ЛИЦА

П.А. Баззлдон

Женевьева «Джинни» Дюбуа, 25 лет, старлетка

Описание Джинни.

П.А. Баззлдон, 40 лет, режиссёр и мошенник

Финеас Артур Баззлдон - подающий надежды режиссёр прямиком из Нью-Йорка.

Bazzledon не тот, за кого себя выдаёт.

<!-- source-page-009 -->

P.A. Bazzledon
"""

    fixed = keeper.build_keeperbook(source, "v1")
    qa = keeper.heading_qa(fixed)

    assert fixed.count("### P.A. Bazzledon") == 1
    assert fixed.index("### Genevieve ‘Ginny’ Dubois") < fixed.index("### P.A. Bazzledon")
    assert "### P.A. Bazzledon\n\n40 лет, режиссёр и мошенник" in fixed
    assert fixed.index("### P.A. Bazzledon") < fixed.index("Финеас Артур Bazzledon")
    assert qa["empty_character_bodies"] == []


def test_heading_qa_blocks_character_heading_tail_residue() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    text = """# Иннсмутский ужас

### Christopher McGuire

, 37 лет, инженер
"""

    qa = keeper.heading_qa(text)

    assert qa["status"] == "fail"
    assert qa["heading_tail_residues"]


def test_heading_qa_blocks_empty_main_character_body() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    text = """# Иннсмутский ужас

## Действующие лица

### P.A. Bazzledon

<div class="keeper-art-block"> <img src="bazzledon.png"> </div>

### Anna Díaz

26 лет, продюсер.
"""

    qa = keeper.heading_qa(text)

    assert qa["status"] == "fail"
    assert qa["empty_character_bodies"] == [{"heading_line": 5, "heading": "### P.A. Bazzledon"}]


def test_keeperbook_strips_and_blocks_old_printed_page_numbers() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    source = """# Иннсмутский ужас

<!-- source-page-008 -->

Действующие лица
4
Genevieve ‘Ginny’ Dubois

<!-- source-page-009 -->

Действующие лица
5
Christopher McGuire

<!-- source-page-011 -->

7 НАЧАЛО: АРКХЭМ
"""

    cleaned, report = keeper.strip_printed_page_number_residue(source)
    qa_before = keeper.structural_qa(source, source)
    qa_after = keeper.structural_qa(source, cleaned)

    assert report["count"] == 3
    assert "\n4\n" not in cleaned
    assert "\n5\n" not in cleaned
    assert "7 НАЧАЛО: АРКХЭМ" not in cleaned
    assert [item["code"] for item in qa_before["findings"] if item["code"] == "printed_page_number_residue"]
    assert not [item for item in qa_after["findings"] if item["code"] == "printed_page_number_residue"]


def test_current_keeperbook_has_no_heading_prefix_duplicates() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master_current")
    path = ROOT / "kb_creator/output/innsmouth_source_to_artifacts/runs/20260730T210831Z/For_Keeper/KeeperBook.md"
    if not path.exists():
        return
    qa = keeper.heading_qa(path.read_text(encoding="utf-8"))
    assert qa["heading_prefix_duplicates"] == []


def test_keeperbook_projects_mvr_vehicle_statblock() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    source = """# Иннсмутский ужас

<!-- source-page-030 -->

### Играя героя

Эпический финал Паровоз MVR класса B1 «Олмстед» MOV: 11 Build: 10 Armour for people: 1 Ширина колеи: стандартная (4 фута 8 1⁄2 дюйма) Давление в котле: 110 psi Максимальная скорость: 70 mph (110 km/h) Чтобы вести поезд, требуется успешный бросок Вождения поезда или Управления тяжёлой техникой. Если Build снижается до нуля, поезд выходит из строя. Каждые полные 10 очков урона уменьшают Build поезда на 1 пункт (округление вниз); урон менее 10 очков игнорируется. Если Build поезда снижается до половины (округление вниз) от его начального значения или ниже, поезд поврежден; ко всем броскам Вождения поезда (или другого подходящего навыка) применяется одна штрафная кость. Если поезд получает за один инцидент урон, равный всему своему значению Build, транспорт полностью эффектно разрушается. Он может взорваться, загореться, перевернуться или пережить какую-либо комбинацию этих событий. Все, кто находится на площадке паровоза, делают бросок Удачи. Успех означает, что от них останется достаточно, чтобы их можно было опознать. Все в пределах 50 м (165 ft) от локомотива получают 6D10 урона. Все, кто находится за пределами этой зоны и не укрыт, совершают бросок Уклонения. Провал означает, что в них попадают летящие на большой скорости обломки (2D4 урона). В качестве альтернативы такой взрыв может быть вызван опасным повышением давления в котле, если успешен бросок Вождения поезда, Управления тяжёлой техникой или Науки (физика). Если же Build поезда снижается до нуля накопленным уроном (то есть порциями меньше исходного значения Build транспорта), он становится непригодным к движению и, скрежеща, останавливается. В зависимости от ситуации (и, возможно, броска Удачи), это может привести к аварии, наносящей 1D10 урона машинисту и каждому пассажиру.
"""

    projected, report = keeper.project_vehicle_stat_blocks(source)
    qa = keeper.structural_qa(source, projected)

    assert report["count"] == 1
    assert "**Паровоз MVR Class B1 «Olmstead»**" in projected
    assert "| MOV | 11 |" in projected
    assert "| Максимальная скорость | 70 mph (110 km/h) |" in projected
    assert "Эпический финал Паровоз MVR" not in projected
    assert qa["vehicle_statblocks"] == 1
    assert not [finding for finding in qa["findings"] if finding["code"] == "vehicle_statblock_projection_missing"]


def test_keeperbook_splits_keeper_note_for_keeper_variant() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    source = (
        "Последний пункт списка. Примечание для Хранителя: это немой фильм, "
        "а не звуковое кино."
    )

    chunks = keeper.split_keeper_note(source)
    qa = keeper.structural_qa(source, "\n\n".join(chunks))

    assert chunks[0] == "Последний пункт списка."
    assert chunks[1].startswith("> <!-- callout-class: keeper-note -->")
    assert "**Примечание Хранителю.** это немой фильм" in chunks[1]
    assert qa["source_keeper_notes"] == 1
    assert qa["keeper_note_callouts"] == 1
    assert not [finding for finding in qa["findings"] if finding["code"] == "keeper_note_callout_count_mismatch"]


def test_keeperbook_splits_multiple_keeper_notes_in_one_paragraph() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    source = (
        "Основной текст. Примечание для Хранителя: это немой фильм. "
        "Примечание для Хранителя: SEU собирается в библиотеке Орна."
    )

    chunks = keeper.split_keeper_note(source)
    qa = keeper.structural_qa(source, "\n\n".join(chunks))

    assert chunks[0] == "Основной текст."
    assert len([chunk for chunk in chunks if "callout-class: keeper-note" in chunk]) == 2
    assert chunks[1].endswith("это немой фильм.")
    assert chunks[2].endswith("SEU собирается в библиотеке Орна.")
    assert qa["source_keeper_notes"] == 2
    assert qa["keeper_note_callouts"] == 2
    assert not [finding for finding in qa["findings"] if finding["code"] == "keeper_note_callout_count_mismatch"]


def test_clean_config_points_inside_kb_creator() -> None:
    module = load_module()
    working = ROOT / "kb_creator/working/test_clean_config"
    output = ROOT / "kb_creator/output/test_clean_config"
    config_path = ROOT / "kb_creator/working/test_clean_config/package.json"
    config = module.make_config(rid="test", config_path=config_path, working_root=working, output_root=output)
    text = config_path.read_text(encoding="utf-8")
    assert "CoC/Working/Scenarios/The_Innsmouth_Terror" not in text
    assert "CoC/Output/Scenarios/The_Innsmouth_Terror" not in text
    assert str(module.REFERENCE_KEEPER) not in text
    assert str(module.REFERENCE_PDF) not in text
    assert config["production_html"]["source_markdown"].startswith("kb_creator/output/test_clean_config/")
    toc_policy = config["production_html"]["toc_policy"]
    assert toc_policy["mode"] == "preserve_and_link"
    assert toc_policy["source_title"] == "Содержание"
    assert toc_policy["generated_fallback_title"] == "Оглавление"
    assert toc_policy["source_page"] == 4
    assert toc_policy["columns"] == 2
    assert toc_policy["replace_source_toc_pages"] is True
    assert "source_toc" in toc_policy["exclude_page_types"]
    source_entries = toc_policy["source_entries"]
    assert source_entries[0] == {"title": "Введение", "level": 2, "href": "vvedenie"}
    assert source_entries[-1] == {
        "title": "Раздаточный материал 2: записка",
        "level": 3,
        "href": "razdatochnyi-material-2-zapiska",
    }
    source_titles = [entry["title"] for entry in source_entries]
    assert "Раздаточные материалы" in source_titles
    assert "Последний поезд из Иннсмута" in source_titles
    assert "Играя героя" in source_titles
    assert config["frontmatter"]["cover"]["page"] == "001"
    assert config["frontmatter"]["cover"]["background_underlay"] is False
    assert config["frontmatter"]["toc"]["mode"] == "preserve_and_link"
    assert config["frontmatter"]["order"] == ["cover", "toc", "body"]
    assert config["production_outputs"]["keeper_markdown_en"].endswith("For_Keeper/KeeperBook_EN.md")
    assert config["art_integration"]["source_anchor_manifest"] == "art_anchor_manifest.json"
    assert config["art_integration"]["source_anchor_report"] == "source_art_anchor_report.json"
    assert config["page_map"]["001"]["type"] == "cover"
    assert config["page_map"]["004"]["type"] == "source_toc"
    assert config["page_map"]["033"]["type"] == "statblock_card"
    assert config["page_map"]["041"]["type"] == "handout"
    assert config["page_map"]["045"]["type"] == "body"
    assert config["translation"]["source_markdown"].startswith("kb_creator/working/test_clean_config/")
    assert config["translation"]["source_markdown"].endswith(
        "Formatted/The_Innsmouth_Terror_Source_Text_Normalized_EN.md"
    )
    assert config["translation"]["max_unit_chars"] == 3000
    assert config["translation"]["batch_dir"].endswith("Translation_Work/RU_Batches_3000")
    assert config["translation"]["batch_manifest"].endswith(
        "Translation_Work/RU_Batches_3000/translation_batch_manifest.json"
    )
    assert "Column_OCR_Reconstruction" not in config["translation"]["source_markdown"]
    two_column = config["production_pdf"]["variants"]["two_column"]
    assert two_column["layout_mode"] == "page_flow_columns"
    assert two_column["print_body_font_size"] == "9.75pt"
    assert two_column["print_body_line_height"] == "1.24"
    assert two_column["statblock_card_font_size"] == "8pt"
    assert two_column["section_wrappers"] == "display_contents"
    assert two_column["heading_policy"]["h1"] == "column_span_all"
    assert two_column["heading_policy"]["h2_h6"] == "inline_column_flow"
    assert two_column["callout_policy"]["default"] == "split_across_columns"
    assert two_column["statblock_section_policy"]["break_before"] == "inline"
    assert two_column["full_width_table_titles"] == ["Таблица 1", "Таблица 2"]
    assert two_column["art_column_policy"]["default_columnned"] is True
    assert "source_image" in two_column["art_column_policy"]["atomic_columnned_roles"]


def test_translation_batches_split_and_remerge_long_units() -> None:
    prepare = load_script(PREPARE_SCRIPT, "prepare_translation_batches")
    merge = load_script(MERGE_SCRIPT, "merge_translation_batches")
    source_text = "First paragraph.\n\n" + ("word " * 900).strip() + "\n\nLast paragraph."
    tasks = {
        "units": [
            {
                "unit_id": "p001_u0001",
                "page": "001",
                "source_hash": prepare.sha256_text(source_text),
                "source_text": source_text,
            }
        ]
    }
    tmp_path = ROOT / "kb_creator/working/test_translation_batches_contract"
    tmp_path.mkdir(parents=True, exist_ok=True)
    tasks_path = tmp_path / "translation_tasks.json"
    tasks_path.write_text(json.dumps(tasks, ensure_ascii=False), encoding="utf-8")
    out_dir = tmp_path / "batches"

    units = prepare.expand_units_for_translation(tasks["units"], max_chars=3000)
    assert len(units) > 1
    assert max(len(unit["source_text"]) for unit in units) <= 3000
    assert {unit["parent_unit_id"] for unit in units} == {"p001_u0001"}

    batches = prepare.batch_units(units, max_chars=3000)
    manifest_batches = []
    for index, batch in enumerate(batches, start=1):
        batch_id = f"batch_{index:02d}"
        en_path = out_dir / f"{batch_id}.en.json"
        ru_path = out_dir / f"{batch_id}.ru.json"
        prepare.write_json(en_path, {"batch_id": batch_id, "units": batch})
        prepare.write_json(
            ru_path,
            {
                "batch_id": batch_id,
                "units": [
                    {
                        "unit_id": unit["unit_id"],
                        "source_hash": unit["source_hash"],
                        "ru_text": f"Перевод {unit['unit_id']}",
                    }
                    for unit in batch
                ],
            },
        )
        manifest_batches.append({"batch_id": batch_id, "input": str(en_path), "output": str(ru_path)})

    manifest = {"counts": {"units": len(units), "original_units": 1}, "batches": manifest_batches}
    all_units = []
    findings = []
    for batch in manifest_batches:
        merged_units, batch_findings = merge.validate_batch(Path(batch["input"]), Path(batch["output"]))
        all_units.extend(merged_units)
        findings.extend(batch_findings)
    assert not findings
    grouped = {}
    for unit in all_units:
        grouped.setdefault(unit["parent_unit_id"], []).append(unit)
    assert list(grouped) == ["p001_u0001"]
    assert len(grouped["p001_u0001"]) == len(units)


def test_cleanup_coc_terms_localizes_mythos_terms_but_keeps_title_heading() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    text = """### The Innsmouth Terror

The Innsmouth Terror assumes the Society for the Exploration of the Unexplained.
The Esoteric Order of Dagon serves the Deep Ones.
A Deep One artifact and a Star Spawn of Cthulhu appear.
"""

    cleaned = keeper.cleanup_coc_terms(text)

    assert "### The Innsmouth Terror" in cleaned
    assert "«Иннсмутский ужас» assumes" in cleaned
    assert "Общество исследования необъяснимого" in cleaned
    assert "Эзотерический орден Дагона" in cleaned
    assert "глубоководные" in cleaned
    assert "глубоководный artifact" in cleaned
    assert "Звёздное Отродье Ктулху" in cleaned
    assert "в 21:00" in keeper.cleanup_coc_terms("автобус отправляется в 9 вечера")
    assert "бросок Вождение автомобиля" in keeper.cleanup_coc_terms("бросок Drive Auto")


def test_body_similarity_report_allows_minor_translation_drift_but_flags_loss() -> None:
    compare = load_script(COMPARE_SCRIPT, "compare_innsmouth_artifacts")
    reference = "<!-- source-page-010 -->\n\nСыщики входят в гостиницу и находят старую записку на столе."
    close_candidate = "<!-- source-page-010 -->\n\nСыщики заходят в гостиницу и обнаруживают старую записку на столе."
    lossy_candidate = "<!-- source-page-010 -->\n\nСыщики входят в гостиницу."

    close = compare.body_similarity_report(close_candidate, reference)
    lossy = compare.body_similarity_report(lossy_candidate, reference)

    assert close["status"] == "pass"
    assert close["pages_requiring_review"] == 0
    assert lossy["status"] == "needs_review"
    assert lossy["pages_requiring_review"] == 1


def test_artifact_comparison_accepts_non_exact_agent_translation_drift() -> None:
    compare = load_script(COMPARE_SCRIPT, "compare_innsmouth_artifacts")
    work_dir = ROOT / "kb_creator/working/test_artifact_comparison_acceptance"
    work_dir.mkdir(parents=True, exist_ok=True)
    reference_keeper = work_dir / "reference.md"
    candidate_keeper = work_dir / "candidate.md"

    reference_keeper.write_text(
        """<!-- source-page-001 -->

# Сценарий

Сыщики входят в гостиницу и находят старую записку на столе. В записке указано, что встреча состоится после заката.

<div class="keeper-art-block"><img src="a.png"></div>
""",
        encoding="utf-8",
    )
    candidate_keeper.write_text(
        """<!-- source-page-001 -->

# Сценарий

Сыщики заходят в гостиницу и находят старую записку на столе. В записке указано, что встреча состоится после заката.

<div class="keeper-art-block"><img src="a.png"></div>
""",
        encoding="utf-8",
    )
    keeper = compare.compare_keeper(candidate_keeper, reference_keeper)

    assert keeper["status"] == "accepted_drift"
    assert keeper["acceptance"]["accepted_non_exact"] is True
    assert keeper["acceptance"]["findings"] == []


def test_page_018_intrapage_repair_preserves_train_links_and_bullets() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    block = """<!-- source-page-018 -->

Исследование

- Сыщики, пытающиеся понять образ мыслей Bazzledon, могут использовать Психологию.

### Вокруг поезда

Рядом со спальным вагоном. Вход со стороны паровоза ведет в Bazzledon’s Office (ниже), центральная дверь ведет в

### Bazzledon’s Office

Шторы в этом кабинете задернуты. Бумаги на столе довольно ошеломляют.

- При успешном броске Бухгалтерии сыщики понимают, что цифры у Bazzledon не сходятся.

- Бросок Внимательности позволяет обнаружить письмо, скомканное и брошенное в корзину.

- Сыщики, изучающие сценарии, могут использовать Язык (английский).
"""
    repaired, changed = keeper._repair_page_018_order(block)
    assert changed
    assert repaired.index("### Вокруг поезда") < repaired.index("### Bazzledon’s Office")
    assert "центральная дверь ведет в Ginny’s Trailer (страница 15)" in repaired
    assert "McGuire’s Lab (страница 16)" in repaired
    assert repaired.index("Бросок Внимательности") < repaired.index("Сыщики, пытающиеся понять образ мыслей")
    assert repaired.index("Сыщики, пытающиеся понять образ мыслей") < repaired.index("Сыщики, изучающие сценарии")


def test_page_007_repair_restores_title_section_before_involvement() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    block = """<!-- source-page-007 -->

Информация для Хранителя 3

### Вовлечение сыщиков

<div class="keeper-art-block" data-placement-id="xref-00354" data-anchor-id="vovlechenie-syschikov"> <img id="xref-00354-image" src="../Images/Atmospheric/innsmouth-page-007-xref-00354-atmospheric.png" alt="xref-00354"> </div>

Сыщики получают письмо от вице-канцлера.

THE INNSMOUTH TERROR Технологии стремительно меняются!
"""
    repaired, changed = keeper._repair_page_007_order(block)
    assert changed
    assert "Информация для Хранителя 3" not in repaired
    assert repaired.index("### The Innsmouth Terror") < repaired.index("### Вовлечение сыщиков")
    assert 'data-anchor-id="the-innsmouth-terror"' in repaired
    assert "Технологии стремительно меняются!" in repaired
    assert "Сыщики получают письмо" in repaired


def test_confirmed_projection_residual_cleanup_removes_reader_noise() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    text = """<!-- source-page-006 -->

### The Innsmouth Terror

Информация для Хранителя 2 ИНФОРМАЦИЯ ДЛЯ ХРАНИТЕЛЯ Город Иннсмут - странное место.

<!-- source-page-017 -->

## Расследование

Расследование Díaz не хочет предвосхищать выводы сыщиков.

<!-- source-page-027 -->

### Пожарная часть

The Fire Station Пожарная часть находится по адресу 100 Paine Street.
"""
    cleaned = keeper.cleanup_confirmed_page_residuals(text)
    assert "### The Innsmouth Terror" in cleaned
    assert "Информация для Хранителя 2" not in cleaned
    assert "ИНФОРМАЦИЯ ДЛЯ ХРАНИТЕЛЯ" not in cleaned
    normalized = keeper.structure_block("006", cleaned.replace("Город Иннсмут", "Город Инсмут"), set())
    assert "## Информация для Хранителя" in normalized
    assert "2 Город Инсмут" not in keeper.cleanup_confirmed_page_residuals(normalized)
    assert "Расследование Díaz" not in cleaned
    assert "Díaz не хочет предвосхищать" in cleaned
    assert "The Fire Station" not in cleaned
    assert "Пожарная часть находится по адресу 100 Paine Street" in cleaned


def test_reader_art_policy_suppresses_page_044_ticket_art() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    temp_dir = ROOT / "kb_creator/working/test_tmp/reader_art_policy"
    temp_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = temp_dir / "art_manifest.json"
    manifest = {
        "placements": [
            {
                "placement_id": "xref-01397",
                "source_page": "044",
                "heading_id": "razdatochnyi-material-2-zapiska",
                "runtime_src": "Images/Handouts/innsmouth-page-044-xref-01397-handout.png",
                "emit_reader_art_block": True,
            }
        ]
    }
    try:
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        updated, report = keeper.apply_reader_art_publication_policy(manifest, manifest_path)
    finally:
        if manifest_path.exists():
            manifest_path.unlink()

    placement = updated["placements"][0]
    assert placement["emit_reader_art_block"] is False
    assert placement["reader_publication_suppressed"] is True
    assert report["suppressed"] == ["xref-01397"]
    assert report["anchor_overrides"] == []


def test_reader_art_cleanup_removes_empty_page_044_marker() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    text = """### Раздаточный материал 2: записка

Эй, Джи.

<!-- source-page-044 -->

<!-- source-page-045 -->

<!-- source-page-046 -->
"""
    cleaned = keeper.cleanup_reader_art_page_marker_residuals(text)
    assert "<!-- source-page-044 -->" not in cleaned
    assert "<!-- source-page-045 -->" in cleaned
    assert "<!-- source-page-046 -->" in cleaned


def test_reader_art_injection_uses_source_anchor_manifest_for_heading_and_order() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    text = """<!-- source-page-008 -->

## Действующие лица

### Genevieve ‘Ginny’ Dubois

Текст Джинни.

### P.A. Bazzledon

Текст Баззлдона.
"""
    art_manifest = {
        "placements": [
            {
                "placement_id": "xref-00379",
                "source_page": "008",
                "source_xref": 379,
                "heading_id": "deistvuyuschie-litsa",
                "runtime_src": "Images/NPC/bazzledon.png",
                "emit_reader_art_block": True,
            },
            {
                "placement_id": "xref-00367",
                "source_page": "008",
                "source_xref": 367,
                "heading_id": "deistvuyuschie-litsa",
                "runtime_src": "Images/NPC/ginny.png",
                "emit_reader_art_block": True,
            },
        ]
    }
    anchor_manifest = {
        "placements": [
            {
                **art_manifest["placements"][0],
                "source_anchor_text": "P.A. Bazzledon",
                "source_anchor_id": "src-p008-character-p-a-bazzledon",
                "source_anchor_kind": "character_lead",
                "source_anchor_method": "npc_order_on_source_page",
                "source_anchor_line_index": 8,
            },
            {
                **art_manifest["placements"][1],
                "source_anchor_text": "Genevieve ‘Ginny’ Dubois",
                "source_anchor_id": "src-p008-character-genevieve-ginny-dubois",
                "source_anchor_kind": "character_lead",
                "source_anchor_method": "npc_order_on_source_page",
                "source_anchor_line_index": 4,
            },
        ]
    }
    temp_dir = ROOT / "kb_creator/working/test_tmp/source_anchor_injection"
    temp_dir.mkdir(parents=True, exist_ok=True)
    art_path = temp_dir / "art_manifest.json"
    anchor_path = temp_dir / "art_anchor_manifest.json"
    try:
        art_path.write_text(json.dumps(art_manifest, ensure_ascii=False), encoding="utf-8")
        anchor_path.write_text(json.dumps(anchor_manifest, ensure_ascii=False), encoding="utf-8")

        projected, report = keeper.inject_reader_art_blocks(text, art_path, anchor_path)
    finally:
        for path in (art_path, anchor_path):
            if path.exists():
                path.unlink()

    assert report["source_anchor_manifest_used"] is True
    assert 'data-anchor-id="genevieve-ginny-dubois"' in projected
    assert 'data-anchor-id="p-a-bazzledon"' in projected
    assert 'data-source-anchor-id="src-p008-character-genevieve-ginny-dubois"' in projected
    assert projected.index('data-placement-id="xref-00367"') < projected.index("Текст Джинни.")
    assert projected.index('data-placement-id="xref-00379"') < projected.index("Текст Баззлдона.")
    assert projected.index('data-placement-id="xref-00367"') < projected.index('data-placement-id="xref-00379"')


def test_source_art_anchor_prefers_npc_caption_over_placement_order() -> None:
    module = load_module()
    source_text = """<!-- source-page-008 -->

DRAMATIS PERSONAE

Genevieve ‘Ginny’ Dubois, age 25, starlet

P.A. Bazzledon, age 40, director & conman
"""
    art_manifest = {
        "placements": [
            {
                "placement_id": "xref-00367",
                "asset_id": "xref-00367",
                "source_page": "008",
                "source_xref": 367,
                "runtime_src": "Images/NPC/bazzledon.png",
                "runtime_role": "npc",
                "emit_reader_art_block": True,
            },
            {
                "placement_id": "xref-00379",
                "asset_id": "xref-00379",
                "source_page": "008",
                "source_xref": 379,
                "runtime_src": "Images/NPC/ginny.png",
                "runtime_role": "npc",
                "emit_reader_art_block": True,
            },
        ]
    }
    pdf_layout = {
        "pages": {
            "008": {
                "images": {
                    "367": [[332.1, 420.9, 534.2, 704.3]],
                    "379": [[325.6, 86.9, 536.5, 367.9]],
                },
                "text_blocks": [
                    {
                        "bbox": [36.0, 112.5, 290.3, 282.3],
                        "text": "Genevieve ‘Ginny’ Dubois, age 25, starlet In bad light...",
                    },
                    {
                        "bbox": [36.0, 365.0, 290.3, 512.8],
                        "text": "P.A. Bazzledon, age 40, director & conman Phineas Arthur...",
                    },
                    {"bbox": [370.0, 373.6, 494.8, 391.0], "text": "Genevieve ‘Ginny’ Dubois"},
                    {"bbox": [403.5, 719.1, 465.4, 730.5], "text": "P.A. Bazzledon"},
                ],
            }
        }
    }

    manifest, report = module.build_source_art_anchor_manifest(source_text, art_manifest, pdf_layout)
    by_id = {item["placement_id"]: item for item in manifest["placements"]}

    assert report["status"] == "pass"
    assert by_id["xref-00379"]["source_anchor_text"] == "Genevieve ‘Ginny’ Dubois"
    assert by_id["xref-00379"]["source_anchor_method"] == "npc_caption_match"
    assert by_id["xref-00367"]["source_anchor_text"] == "P.A. Bazzledon"
    assert by_id["xref-00367"]["source_anchor_method"] == "npc_caption_match"


def test_source_art_anchor_promotes_captioned_character_when_role_is_wrong() -> None:
    module = load_module()
    source_text = """<!-- source-page-009 -->

Anna Díaz, age 26, producer

Christopher McGuire, age 37, engineer
"""
    art_manifest = {
        "placements": [
            {
                "placement_id": "xref-00395",
                "asset_id": "xref-00395",
                "source_page": "009",
                "source_xref": 395,
                "runtime_src": "Images/Atmospheric/christopher.png",
                "runtime_role": "atmospheric",
                "semantic_role": "atmospheric",
                "production_role": "atmospheric",
                "emit_reader_art_block": True,
            }
        ]
    }
    pdf_layout = {
        "pages": {
            "009": {
                "images": {"395": [[315.9, 430.3, 567.6, 680.9]]},
                "text_blocks": [
                    {
                        "bbox": [315.0, 92.0, 568.0, 285.0],
                        "text": "Christopher McGuire, age 37, engineer A tall...",
                    },
                    {"bbox": [401.8, 694.8, 490.6, 708.6], "text": "Christopher McGuire"},
                ],
            }
        }
    }

    manifest, report = module.build_source_art_anchor_manifest(source_text, art_manifest, pdf_layout)
    row = manifest["placements"][0]

    assert report["status"] == "pass"
    assert row["source_anchor_text"] == "Christopher McGuire"
    assert row["source_anchor_method"] == "npc_caption_match"
    assert row["runtime_role"] == "npc"
    assert row["source_identity_role_promoted_from"] == "atmospheric"


def test_source_art_anchor_uses_reviewed_heading_id_for_uncaptioned_npc() -> None:
    module = load_module()
    source_text = """<!-- source-page-036 -->

HUGO ‘SHRIMPY’ HARGREAVES

Age: 27 Occupation: Student / Gentleman

Backstory Hugo never liked his first name, so when school friends nicknamed him Shrimpy...
"""
    art_manifest = {
        "placements": [
            {
                "placement_id": "xref-01172",
                "asset_id": "xref-01172",
                "source_page": "036",
                "source_xref": 1172,
                "runtime_src": "Images/NPC/hugo.png",
                "runtime_role": "npc",
                "heading_id": "hugo-shrimpy-hargreaves",
                "emit_reader_art_block": True,
            }
        ]
    }

    manifest, report = module.build_source_art_anchor_manifest(source_text, art_manifest, pdf_layout=None)
    row = manifest["placements"][0]

    assert report["status"] == "pass"
    assert row["source_anchor_text"] == "HUGO ‘SHRIMPY’ HARGREAVES"
    assert row["source_anchor_method"] == "npc_heading_id_match"
    assert row["source_anchor_kind"] == "character_lead"


def test_source_art_anchor_uses_side_caption_identity_for_npc() -> None:
    module = load_module()
    source_text = """<!-- source-page-011 -->

START: ARKHAM

ORNE LIBRARY (MISKATONIC UNIVERSITY)
"""
    art_manifest = {
        "placements": [
            {
                "placement_id": "xref-00461",
                "asset_id": "xref-00461",
                "source_page": "011",
                "source_xref": 461,
                "runtime_src": "Images/NPC/henry.png",
                "runtime_role": "npc",
                "heading_id": "nachalo-arkhem",
                "emit_reader_art_block": True,
            }
        ]
    }
    pdf_layout = {
        "pages": {
            "011": {
                "images": {"461": [[364.1, 308.0, 538.8, 546.9]]},
                "text_blocks": [
                    {"bbox": [54.0, 111.8, 308.2, 262.3], "text": "ORNE LIBRARY (MISKATONIC UNIVERSITY) Our mystery..."},
                    {"bbox": [535.0, 386.5, 557.7, 471.0], "text": "Dr. Henry Armitage"},
                ],
            }
        }
    }

    manifest, report = module.build_source_art_anchor_manifest(source_text, art_manifest, pdf_layout)
    row = manifest["placements"][0]

    assert report["status"] == "pass"
    assert row["source_anchor_text"] == "Dr. Henry Armitage"
    assert row["source_anchor_method"] == "npc_caption_match"
    assert row["source_anchor_kind"] == "caption_identity"


def test_source_art_anchor_fails_unproven_npc_identity() -> None:
    module = load_module()
    source_text = """<!-- source-page-020 -->

THE GENERAL STORE

Some body text without a character caption.
"""
    art_manifest = {
        "placements": [
            {
                "placement_id": "xref-02000",
                "asset_id": "xref-02000",
                "source_page": "020",
                "source_xref": 2000,
                "runtime_src": "Images/NPC/unknown.png",
                "runtime_role": "npc",
                "heading_id": "the-general-store",
                "emit_reader_art_block": True,
            }
        ]
    }

    manifest, report = module.build_source_art_anchor_manifest(source_text, art_manifest, pdf_layout=None)

    assert manifest["status"] == "fail"
    assert report["status"] == "fail"
    assert manifest["counts"]["npc_identity_unverified"] == 1
    assert manifest["findings"][0]["code"] == "npc_art_identity_not_semantically_proven"


def test_keeper_source_toc_projection_replaces_ocr_order_drift() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    text = """# Иннсмутский ужас

<!-- source-page-004 -->

В ИНСМУТ

Универсальный магазин

СОДЕРЖАНИЕ
ВВЕДЕНИЕ

1
Подготовка к игре

<!-- source-page-005 -->

## Введение
"""
    projected, report = keeper.project_keeper_source_toc(text)
    toc = projected.split("<!-- source-page-004 -->", 1)[1].split("<!-- source-page-005 -->", 1)[0]
    assert report["changed"]
    assert "## Содержание" in toc
    assert "ВВЕДЕНИЕ" in toc
    assert "Подготовка к игре" in toc
    assert "ПРЕДУПРЕЖДЕНИЯ О СОДЕРЖАНИИ" in toc
    assert "1\nПодготовка" not in toc


def test_ritual_oath_sequence_is_restored_as_quote_block() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    text = (
        "Эта поддержка имела свою цену, и члены ордена были вынуждены принести три клятвы: "
        "Первая клятва: «Iä! Dagon! Я клянусь. Iä! Dagon!» "
        "Вторая клятва: «Iä! Dagon! Я помогу. Iä! Dagon!» "
        "Третья клятва: «Iä! Dagon! Я беру это существо. Iä! Dagon! Iä! Hydra!» "
        "Так, с третьей клятвой, появились Гибриды."
    )
    restored = keeper.format_ritual_oath_blocks(text)
    assert "три клятвы:\n\n> Первая клятва:" in restored
    assert "\n>\n> Вторая клятва:" in restored
    assert "\n>\n> Третья клятва:" in restored
    assert "\n\nТак, с третьей клятвой" in restored


def test_statblock_projection_keeps_group_headings_and_card_anchors() -> None:
    statblocks = load_script(STATBLOCK_SCRIPT, "project_innsmouth_statblocks_from_ru")
    lines = []
    for page, spec in [
        ("033", statblocks.CARD_STARTS[0]),
        ("033", statblocks.CARD_STARTS[1]),
        ("033", statblocks.CARD_STARTS[2]),
        ("033", statblocks.CARD_STARTS[3]),
        ("033", statblocks.CARD_STARTS[4]),
        ("033", statblocks.CARD_STARTS[5]),
        ("034", statblocks.CARD_STARTS[6]),
        ("034", statblocks.CARD_STARTS[7]),
        ("034", statblocks.CARD_STARTS[8]),
        ("034", statblocks.CARD_STARTS[9]),
        ("035", statblocks.CARD_STARTS[10]),
        ("035", statblocks.CARD_STARTS[11]),
        ("035", statblocks.CARD_STARTS[12]),
        ("035", statblocks.CARD_STARTS[13]),
        ("035", statblocks.CARD_STARTS[14]),
        ("035", statblocks.CARD_STARTS[15]),
        ("035", statblocks.CARD_STARTS[16]),
        ("036", statblocks.CARD_STARTS[17]),
        ("037", statblocks.CARD_STARTS[18]),
        ("038", statblocks.CARD_STARTS[19]),
        ("039", statblocks.CARD_STARTS[20]),
        ("040", statblocks.CARD_STARTS[21]),
    ]:
        lines.extend(
            [
                f"<!-- source-page-{page} -->",
                spec.patterns[0],
                "СИЛ 50 ТЕЛ 50 РАЗМ 50 ЛВК 50 ИНТ 50 ВНЕШ 50 МОЩ 50 ОБР 50 РАСС 50",
                "ЗД 10 БМ: 0 Телосложение: 0 Движение: 8 МЗ: 10",
                "Бой",
                "Драка 25% (12/5), урон 1D3",
                "Навыки",
                "Слух 40%",
            ]
        )
    replacement, records, page_heading_ids, findings = statblocks.build_cards("\n".join(lines))
    assert not findings
    assert len(records) == len(statblocks.CARD_STARTS)
    assert replacement.index("### Жители Аркхэма") < replacement.index("### Съёмочная группа")
    assert replacement.index("### Съёмочная группа") < replacement.index("### Жители Иннсмута")
    assert replacement.index("### Жители Иннсмута") < replacement.index("### Монстры")
    assert replacement.index("## Заранее созданные сыщики") < replacement.index("### Hugo ‘Shrimpy’ Hargreaves")
    assert "### Diane Loring" not in replacement
    assert '<a id="diane-loring"></a>' in replacement
    assert page_heading_ids["033"] == "zhiteli-arkhema"
    assert page_heading_ids["036"] == "hugo-shrimpy-hargreaves"


def test_statblock_projection_fills_missing_core_values_from_pdf_text_layer() -> None:
    statblocks = load_script(STATBLOCK_SCRIPT, "project_innsmouth_statblocks_from_ru")
    html, record = statblocks.card_html(
        statblocks.CARD_STARTS[0],
        [
            "Дайана Лоринг, 50 лет, библиотекарь справочного отдела",
            "СИЛ 50",
            "ТЕЛ 70",
            "ЛОВ 55",
            "ИНТ 80",
            "ВНЕ 65",
            "РАСС 50",
            "HP 12",
            "DB: 0",
            "Телосложение: 0 Передвижение: 7",
            "MP: 10",
            "Бой",
            "Драка 25% (12/5), урон 1D3",
        ],
        [
            "Diane Loring, age 50, reference librarian",
            "STR 50",
            "CON 70",
            "SIZ    50",
            "DEX 55",
            "INT 80",
            "APP 65",
            "POW 50 EDU 70",
            "SAN 50",
            "HP 12",
            "DB: 0 Build: 0 Move: 7 MP: 10",
        ],
    )
    assert "<td>50</td><td>70</td><td>50</td><td>55</td>" in html
    assert "<td>50</td><td>70</td><td>50</td>" in html
    assert record["supplemental_source"] == "source_pdf_text_layer"
    assert set(record["filled_from_pdf"]) >= {"SIZ", "POW", "EDU"}
    assert record["missing_core"] == []


def test_page_012_repair_splits_orne_library_out_of_loring_bullet() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    block = """<!-- source-page-012 -->

### Аркхэмский вестник

The Arkham Advertiser body.

- При успешном броске Археологии сыщики получают сведения.

- Loring ничего не знает о подробностях фильма и рекомендует сыщикам обратиться в газету. Кроме того, она упоминает, что ресурсы библиотеки Орна остаются в их распоряжении, если они понадобятся. Пользуясь библиотекой Орна, сыщики могут выбрать множество разных направлений исследования. При успешном броске Оккультизма сыщики знают больше.
"""
    repaired, changed = keeper._repair_page_012_order(block)
    assert changed
    assert repaired.index("- При успешном броске Археологии") < repaired.index("### Аркхэмский вестник")
    assert "\n\nСыщики могут использовать разные направления исследований в библиотеке Орна." in repaired
    assert "если они понадобятся. Пользуясь библиотекой Орна" not in repaired


def test_page_021_repair_splits_stage_fright_keeper_note() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    block = """<!-- source-page-021 -->

### На съёмочной площадке

Исследование Сыщики наблюдают за съемками.

### Железнодорожный вход

Если сыщики направятся к станции, они заметят зловеще выглядящую щель между камнями у путей.

Сыщики говорят с Ginny. На съемочной площадке Во время первоначального расследования все участники производства работают в поле.

> <!-- callout-class: keeper-note -->
> **Примечание Хранителю.** хотя костюмы необычны. Примечание Хранителю: сыщики уже встречались с Ginny во время прохождения Stage Fright? Не беспокойтесь об этом. Она совершенно их не помнит и обращается с ними точно так же.
"""
    repaired, changed = keeper._repair_page_021_order(block)
    assert changed
    assert repaired.count("callout-class: keeper-note") == 2
    assert "костюмы необычны. Примечание Хранителю: сыщики уже" not in repaired
    assert repaired.index("Во время первоначального расследования") < repaired.index("Сыщики наблюдают за съемками")
    assert repaired.index("Сыщики говорят с Ginny.") < repaired.index("Stage Fright?")


def test_keeper_information_section_stays_body_section() -> None:
    keeper = load_script(KEEPER_SCRIPT, "build_keeperbook_from_ru_master")
    source = """<!-- source-page-006 -->

Информация для Хранителя

Город Иннсмут - странное место.

Ещё в 1830-х годах капитан Obed Marsh заключил сделку.

<!-- source-page-007 -->

### Вовлечение сыщиков

Сыщики получают письмо.
"""
    repaired, report = keeper.wrap_keeper_info_sections(source)
    assert report["count"] == 0
    assert "Информация для Хранителя\n\nГород" in repaired
    assert "> <!-- callout-class: keeper-note -->" not in repaired
    assert "> **Информация для Хранителя.**" not in repaired
    assert "<!-- source-page-007 -->" in repaired
