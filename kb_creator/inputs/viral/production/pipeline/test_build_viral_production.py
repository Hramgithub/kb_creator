from __future__ import annotations

from pathlib import Path
import json

from kb_creator.scripts import build_viral_production as viral


def test_move_image_after_heading_preserves_alt_and_existing_attribute() -> None:
    name = "art.jpg"
    source = f"![Исходная подпись](assets/{name}){{.old}}\n\n<a id=\"target\"></a>\n## Раздел\n\nТекст\n"

    result = viral.move_image_after_heading(source, name, "target")

    assert result.index("## Раздел") < result.index("![Исходная подпись]") < result.index("Текст")
    assert f"![Исходная подпись](assets/{name}){{.old}}" in result


def test_render_statblock_is_structured_and_not_a_quote() -> None:
    lines = [
        "**The Devourer** — Aspect",
        "STR: 150",
        r"\* Starting Stats",
        "ATTACKS",
        "Attacks per round: 3",
        "Grab: description",
        "SPECIAL ABILITIES",
        "Devour: description",
    ]

    result = viral.render_statblock(lines, ru=False)

    assert result.startswith("##### The Devourer — Aspect")
    assert "| STR | 150 |" in result
    assert "###### Attacks" in result
    assert "###### Special Abilities" in result
    assert not any(line.startswith(">") for line in result.splitlines())


def test_metric_residual_detects_imperial_units() -> None:
    assert viral.residual_imperial("Он прошёл десять футов.\n")
    assert not viral.residual_imperial("Он прошёл 3 метра.\n")


def test_orphan_near_empty_pdf_pages_catches_short_text_only_tail() -> None:
    rows = [
        {"page": 1, "text_characters": 0, "image_xobjects": 0},
        {"page": 65, "text_characters": 45, "image_xobjects": 0},
        {"page": 66, "text_characters": 45, "image_xobjects": 1},
        {"page": 67, "text_characters": 80, "image_xobjects": 0},
    ]

    assert viral.orphan_near_empty_pdf_pages(rows) == [65]


def test_a4_size_accepts_word_and_chromium_rounding() -> None:
    assert viral.is_uniform_a4([(595.32, 841.92)])
    assert viral.is_uniform_a4([(594.96, 841.92)])
    assert not viral.is_uniform_a4([(612.0, 792.0)])


def test_pdf_page_title_ignores_word_page_number() -> None:
    assert viral.pdf_page_starts_with_title("71\nРаздаточные материалы для игроков\n", "Раздаточные материалы")


def test_bind_pregen_headings_to_pages_pairs_each_heading_with_its_art() -> None:
    pairs = []
    for index, name in enumerate(("marco", "corrina", "enoch", "peter", "ku-hyeon", "blank"), 1):
        pairs.append(
            f'<a id="viral-pregen-{name}-front"></a>\n### {name} front\n\n'
            f'<a id="viral-pregen-{name}-background"></a>\n### {name} background\n\n'
            f'![front](assets/front-{index}.png)\n\n![back](assets/back-{index}.png)'
        )

    result = viral.bind_pregen_headings_to_pages("\n\n".join(pairs))

    for index, name in enumerate(("marco", "corrina", "enoch", "peter", "ku-hyeon", "blank"), 1):
        front = f'<a id="viral-pregen-{name}-front"></a>\n### {name} front\n\n![front](assets/front-{index}.png)'
        background = f'<a id="viral-pregen-{name}-background"></a>\n### {name} background\n\n![back](assets/back-{index}.png)'
        assert front in result
        assert background in result


def test_annotate_art_uses_role_aware_production_classes() -> None:
    source = """<a id="viral-body"></a>
![body](assets/body.jpg)
<a id="viral-handout-01"></a>
![handout](assets/handout.jpg)
<a id="viral-keeper-map-island"></a>
![map](assets/map.jpg)
<a id="viral-pregen-marco-front"></a>
![sheet](assets/sheet.jpg)
<a id="viral-body-two"></a>
![opening](assets/viral-provisional-isola-di-malamente-opening-page-26.png)
"""

    result = viral.annotate_art(source, viral.REPO_ROOT)

    assert "![body](assets/body.jpg){.art-body-right}" in result
    assert "![handout](assets/handout.jpg){.art-handout-page}" in result
    assert "![map](assets/map.jpg){.art-full-page}" in result
    assert "![sheet](assets/sheet.jpg){.art-pregen-fullpage}" in result
    assert "![opening](assets/viral-provisional-isola-di-malamente-opening-page-26.png){.art-full-page}" in result


def test_current_viral_html_layout_policy_is_render_only_safe() -> None:
    policy = viral.current_viral_html_layout_policy()

    assert policy["allow_long_callout_page_breaks"] is True
    assert policy["avoid_single_column_fragmentation_context"] is True
    assert policy["suppress_section_navigation_after_anchor_ids"] == [
        "viral-player-handouts",
        "viral-keeper-maps",
        "viral-pregenerated-investigators",
    ]
    assert policy["page_break_before_anchor_ids"] == [
        "viral-player-handouts",
        "viral-keeper-maps",
    ]
    assert policy["bind_section_heading_into_first_card_anchor_ids"] == [
        "viral-pregenerated-investigators"
    ]


def test_refresh_pipeline_snapshot_includes_current_builder_and_renderer(tmp_path: Path) -> None:
    viral.refresh_pipeline_snapshot(tmp_path)

    assert (tmp_path / "pipeline" / "build_viral_production.py").read_bytes() == Path(viral.__file__).read_bytes()
    assert (tmp_path / "pipeline" / "translator.py").read_bytes() == (
        viral.REPO_ROOT / "translator/translator.py"
    ).read_bytes()
    assert (tmp_path / "pipeline" / "production_docx.py").read_bytes() == (
        viral.REPO_ROOT / "kb_creator/scripts/production_docx.py"
    ).read_bytes()


def test_phone_facsimile_is_suppressed() -> None:
    assert "8dcb6eee3da06a699ff2ac68c0b32338209a8abad3327bf0c8e246c2722dc76e.jpg" in viral.SUPPRESSED_TEXT_FACSIMILES


def test_swap_image_references_exchanges_only_targets() -> None:
    source = "before assets/first.jpg middle assets/second.jpg after"

    result = viral.swap_image_references(source, "first.jpg", "second.jpg")

    assert result == "before assets/second.jpg middle assets/first.jpg after"


def test_restore_handout_8_postscript_preserves_text_when_phone_art_is_hidden() -> None:
    source = "Maya's Emails\n\n(2 of 2)\n\n<a id=\"next\"></a>"

    result = viral.restore_handout_8_postscript(source, ru=False)

    assert "P.S. I have also included the usual “read to camera” bit" in result
    assert "P.P.S. Meant to tell you" in result
    assert "Attachment [5.3M]" in result
    assert result.index("Attachment [5.3M]") < result.index('<a id="next"></a>')


def test_remove_ru_credits_preserves_opening() -> None:
    source = (
        '<a id="viral-credits"></a>\n## Авторы\n\nИмена\n\n'
        '<a id="viral-opening-message"></a>\n\nВступление\n'
    )

    result = viral.remove_ru_credits(source)

    assert "viral-credits" not in result
    assert "## Авторы" not in result
    assert result.startswith('<a id="viral-opening-message"></a>')


def test_normalize_ru_headings_preserves_anchor_and_removes_location_ordinal() -> None:
    source = (
        "# ВИРУС\n\n## ПРЕДУПРЕЖДЕНИЕ\n\n## КОМАНДА «СПЕКТРАЛ»\n\n"
        '<a id="viral-isola-location-03-the-weeping-bridge"></a>\n'
        "### 3. Плачущий мост\n"
    )

    result = viral.normalize_ru_headings(source)

    assert "# Вирус" in result
    assert "## Предупреждение" in result
    assert "## Команда «Спектрал»" in result
    assert '<a id="viral-isola-location-03-the-weeping-bridge"></a>\n### Плачущий мост' in result


def test_normalize_handout_headers_uses_navigation_as_canonical_order() -> None:
    nav = []
    blocks = []
    identifiers = ["1", "2a", "2b", "3a", "3b", *[str(index) for index in range(4, 40)]]
    for handout_id in identifiers:
        anchor_id = handout_id.zfill(2) if handout_id.isdigit() else handout_id.zfill(3)
        title = f"Название {handout_id}"
        nav.append(f"- [Материал {handout_id}: {title}](#viral-handout-{anchor_id})")
        if handout_id == "4":
            blocks.append(
                f'<a id="viral-handout-{anchor_id}"></a>\n'
                f"### Старое название\n\nТекст\n\n*Раздаточный материал #{handout_id}*"
            )
        else:
            blocks.append(
                f'<a id="viral-handout-{anchor_id}"></a>\n'
                f"### *Раздаточный материал #{handout_id}*\n\n{title}\n\nТекст"
            )
    source = "\n".join(nav) + "\n\n" + "\n\n".join(blocks) + (
        '\n\n<a id="viral-keeper-map-isola-location"></a>\n## Карты\n'
    )

    result = viral.normalize_handout_headers(source, ru=True)

    block = result.split('<a id="viral-handout-04"></a>', 1)[1].split(
        '<a id="viral-handout-05"></a>', 1
    )[0]
    assert block.startswith("\n### *Раздаточный материал #4*\n\nНазвание 4\n\nТекст")
    assert "Старое название" not in block
    assert block.count("Раздаточный материал #4") == 1


def test_normalize_handout_headers_joins_split_parenthetical_title() -> None:
    nav = []
    blocks = []
    identifiers = ["1", "2a", "2b", "3a", "3b", *[str(index) for index in range(4, 40)]]
    for handout_id in identifiers:
        anchor_id = handout_id.zfill(2) if handout_id.isdigit() else handout_id.zfill(3)
        title = "Письма Майи (2 из 2)" if handout_id == "8" else f"Название {handout_id}"
        nav.append(f"- [Материал {handout_id}: {title}](#viral-handout-{anchor_id})")
        split_title = "Письма Майи\n\n*(2 из 2)*" if handout_id == "8" else title
        blocks.append(
            f'<a id="viral-handout-{anchor_id}"></a>\n'
            f"### *Раздаточный материал #{handout_id}*\n\n{split_title}\n\nТекст"
        )
    source = "\n".join(nav) + "\n\n" + "\n\n".join(blocks) + (
        '\n\n<a id="viral-keeper-map-isola-location"></a>\n## Карты\n'
    )

    result = viral.normalize_handout_headers(source, ru=True)
    block = result.split('<a id="viral-handout-08"></a>', 1)[1].split(
        '<a id="viral-handout-09"></a>', 1
    )[0]

    assert block.startswith("\n### *Раздаточный материал #8*\n\nПисьма Майи (2 из 2)")
    assert block.count("Письма Майи") == 1
    assert block.count("2 из 2") == 1


def test_preheading_body_art_registry_binding_excludes_non_body() -> None:
    registry = {
        "assets": [
            {"anchor": "body", "disposition": "reader", "source_page": 2,
             "source_order": {"raw_index": 3}, "binary": {"path": "assets/b.jpg"},
             "placement": {"before_event": "heading:body"}},
            {"anchor": "body", "disposition": "reader", "source_page": 1,
             "source_order": {"raw_index": 2}, "binary": {"path": "assets/a.jpg"},
             "placement": {"before_event": "heading:body"}},
            {"anchor": "viral-handout-01", "disposition": "reader", "source_page": 3,
             "source_order": {"raw_index": 4}, "binary": {"path": "assets/handout.jpg"},
             "placement": {"before_event": "heading:viral-handout-01"}},
        ]
    }

    assert viral.preheading_body_art_bindings(registry) == [("body", ["a.jpg", "b.jpg"])]


def test_move_images_after_heading_preserves_source_order() -> None:
    source = (
        "![B](assets/b.jpg)\n\n![A](assets/a.jpg)\n\n"
        '<a id="body"></a>\n### Раздел\n\nТекст\n'
    )

    result = viral.move_images_after_heading(source, ["a.jpg", "b.jpg"], "body")

    assert result.index("### Раздел") < result.index("assets/a.jpg") < result.index("assets/b.jpg") < result.index("Текст")


def test_artview_figure_classes_follow_accepted_presentation() -> None:
    body = {"asset_id": "body", "group": "body"}
    decision = {
        "presentation": {"width_percent": 25, "alignment": "right", "wrap_text": True, "wrap_tables": True}
    }

    classes = viral.artview_figure_classes(body, decision)

    assert "art-body-right" in classes
    assert "artview-width-25" in classes
    assert "artview-wrap-text" in classes
    assert "artview-wrap-tables" in classes


def test_apply_artview_receipt_replaces_binary_and_keeps_master_text_immutable(tmp_path: Path) -> None:
    runtime = tmp_path / "assets" / "artview" / "chosen.png"
    runtime.parent.mkdir(parents=True)
    runtime.write_bytes(b"png")
    master = "<a id=\"section\"></a>\n## Раздел\n\n![Иллюстрация](assets/current.jpg){.old}\n\nТекст\n"
    receipt = {
        "entries": [{
            "asset_id": "asset", "action": "use_candidate", "source_refs": ["assets/current.jpg"],
            "runtime_ref": "assets/artview/chosen.png", "classes": ["artview-decision", "art-body-right"],
            "allow_absent": False, "insert_when_absent": False, "anchor": "section", "source_page": 1,
            "source_order": 0,
        }]
    }

    result = viral.apply_artview_receipt(master, receipt, tmp_path)

    assert master.endswith("Текст\n")
    assert "assets/current.jpg" not in result
    assert "assets/artview/chosen.png" in result
    assert "{.artview-decision .art-body-right}" in result


def test_apply_artview_receipt_inserts_newly_accepted_slot_after_existing_heading_art(tmp_path: Path) -> None:
    runtime = tmp_path / "assets" / "artview" / "chosen.png"
    runtime.parent.mkdir(parents=True)
    runtime.write_bytes(b"png")
    master = "<a id=\"section\"></a>\n## Раздел\n\n![Старый](assets/old.jpg){.art-body-right}\n\nТекст\n"
    receipt = {
        "entries": [{
            "asset_id": "new", "action": "use_candidate", "source_refs": ["assets/missing.jpg"],
            "runtime_ref": "assets/artview/chosen.png", "classes": ["artview-decision", "art-body-right"],
            "allow_absent": False, "insert_when_absent": True, "anchor": "section", "source_page": 2,
            "source_order": 0,
        }]
    }

    result = viral.apply_artview_receipt(master, receipt, tmp_path)

    assert result.index("assets/old.jpg") < result.index("assets/artview/chosen.png") < result.index("Текст")


def test_artview_receipt_consistency_accepts_user_selected_action_counts(tmp_path: Path) -> None:
    decisions = {
        "decisions": [
            {"asset_id": "one", "binary": {"choice": "use_candidate"}},
            {"asset_id": "two", "binary": {"choice": "exclude"}},
        ]
    }
    manifest = {"rows": [{"asset_id": "one"}, {"asset_id": "two"}]}
    decisions_path = tmp_path / viral.PACKAGED_ARTVIEW_DECISIONS
    config_path = tmp_path / viral.PACKAGED_ARTVIEW_CONFIG
    manifest_path = tmp_path / viral.PACKAGED_ARTVIEW_MANIFEST
    decisions_path.write_text(json.dumps(decisions), encoding="utf-8")
    config_path.write_bytes(decisions_path.read_bytes())
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    receipt = {
        "state": "applied",
        "decisions_sha256": viral.sha256(decisions_path),
        "candidate_manifest_sha256": viral.sha256(manifest_path),
        "counts": {"keep_current": 0, "use_candidate": 1, "exclude": 1, "inserted": 0},
        "entries": [
            {"asset_id": "one", "action": "use_candidate", "insert_when_absent": False},
            {"asset_id": "two", "action": "exclude", "insert_when_absent": False},
        ],
    }

    assert viral.artview_receipt_is_consistent(tmp_path, receipt)

    receipt["counts"]["use_candidate"] = 86
    assert not viral.artview_receipt_is_consistent(tmp_path, receipt)


def test_artview_receipt_consistency_requires_exact_config_copy(tmp_path: Path) -> None:
    decisions = {"decisions": [{"asset_id": "one", "binary": {"choice": "exclude"}}]}
    manifest = {"rows": [{"asset_id": "one"}]}
    decisions_path = tmp_path / viral.PACKAGED_ARTVIEW_DECISIONS
    config_path = tmp_path / viral.PACKAGED_ARTVIEW_CONFIG
    manifest_path = tmp_path / viral.PACKAGED_ARTVIEW_MANIFEST
    decisions_path.write_text(json.dumps(decisions), encoding="utf-8")
    config_path.write_bytes(decisions_path.read_bytes())
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    receipt = {
        "state": "applied",
        "decisions_sha256": viral.sha256(decisions_path),
        "candidate_manifest_sha256": viral.sha256(manifest_path),
        "counts": {"keep_current": 0, "use_candidate": 0, "exclude": 1, "inserted": 0},
        "entries": [{"asset_id": "one", "action": "exclude", "insert_when_absent": False}],
    }

    assert viral.artview_receipt_is_consistent(tmp_path, receipt)
    config_path.write_text("{}", encoding="utf-8")
    assert not viral.artview_receipt_is_consistent(tmp_path, receipt)


def test_prune_artview_runtime_assets_keeps_only_current_candidates(tmp_path: Path) -> None:
    runtime_root = tmp_path / "assets" / "artview"
    runtime_root.mkdir(parents=True)
    (runtime_root / "current.jpg").write_bytes(b"current")
    (runtime_root / "stale.png").write_bytes(b"stale")

    removed = viral.prune_artview_runtime_assets(runtime_root, {"current.jpg"})

    assert removed == ["stale.png"]
    assert sorted(path.name for path in runtime_root.iterdir()) == ["current.jpg"]


def test_resolve_artview_candidate_bundle_skips_incomplete_export_directory(
    tmp_path: Path, monkeypatch,
) -> None:
    export_root = tmp_path / "production"
    export_root.mkdir()
    checkpoint_root = tmp_path / "checkpoint"
    candidate_root = checkpoint_root / "candidate"
    (candidate_root / "assets").mkdir(parents=True)
    decisions = {
        "decisions": [{
            "asset_id": "one",
            "binary": {"choice": "use_candidate", "candidate_id": "chosen"},
        }]
    }
    manifest = {
        "rows": [{
            "asset_id": "one",
            "alternatives": [{"candidate_id": "chosen", "path": "assets/chosen.png"}],
        }]
    }
    decisions_path = export_root / "accepted.json"
    decisions_path.write_text(json.dumps(decisions), encoding="utf-8")
    (export_root / viral.PACKAGED_ARTVIEW_MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")
    (candidate_root / "candidate_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (candidate_root / "assets" / "chosen.png").write_bytes(b"candidate")
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"output_root": str(checkpoint_root)}), encoding="utf-8")
    monkeypatch.setattr(viral, "DEFAULT_ARTVIEW_PROFILE", profile)

    resolved_root, resolved_manifest = viral.resolve_artview_candidate_bundle(decisions_path)

    assert resolved_root == candidate_root.resolve()
    assert resolved_manifest == (candidate_root / "candidate_manifest.json").resolve()
