"""Focused regressions for opt-in package remediation support."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from translator import translator


class RecoverySupportTests(unittest.TestCase):
    def write_config(self, root: Path, values: dict) -> Path:
        config = {"project_key": "recovery-test", "workbench_qa_root": str(root / "qa"), **values}
        path = root / "package.json"
        path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
        return path

    def toc_config(self) -> dict:
        return {
            "page_map": {"005": {"type": "source_toc"}},
            "production_html": {"toc_policy": {"replace_source_toc_pages": True, "max_heading_level": 3}},
        }

    def test_inline_markdown_preserves_commonmark_escaped_asterisk(self) -> None:
        rendered = translator.inline_markdown(r"\* Новое заклинание; **Mythos Investigators**")

        self.assertEqual(rendered, "* Новое заклинание; <strong>Mythos Investigators</strong>")
        self.assertNotIn("<em>", rendered)

    def test_generated_toc_can_exclude_heading_id_prefixes(self) -> None:
        headings = [
            {"href": "viral-player-handouts", "level": 2, "title": "Раздаточные материалы"},
            {"href": "viral-handout-1", "level": 3, "title": "Раздаточный материал 1"},
            {"href": "viral-history", "level": 2, "title": "История"},
        ]
        config = {
            "production_html": {
                "toc_policy": {"max_heading_level": 3, "exclude_heading_id_prefixes": ["viral-handout-"]}
            }
        }

        filtered = translator.filter_production_toc(headings, config)

        self.assertEqual([item["href"] for item in filtered], ["viral-player-handouts", "viral-history"])

    def test_generated_toc_can_exclude_source_anchor_prefixes(self) -> None:
        markdown = '<a id="viral-handout-01"></a>\n### Раздаточный материал 1\n<a id="viral-history"></a>\n## История\n'
        _, headings, _ = translator.markdown_to_review_html(
            markdown, source_path=Path("source.md"), html_path=Path("book.html")
        )
        config = {
            "production_html": {
                "toc_policy": {"max_heading_level": 3, "exclude_source_anchor_prefixes": ["viral-handout-"]}
            }
        }

        filtered = translator.filter_production_toc(headings, config)

        self.assertEqual([item["title"] for item in filtered], ["История"])
        self.assertEqual(headings[0]["source_anchor_ids"], ["viral-handout-01"])

    def test_single_column_print_matches_accepted_innsmouth_flow(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = {
                "project_key": "single-column",
                "production_html": {
                    "output_html": str(root / "book.html"),
                    "print_columns": 1,
                },
            }
            html = translator.build_production_html_document(config, "<p>Body</p>", "")
            source = root / "source.html"
            source.write_text(html, encoding="utf-8")
            (root / "render").mkdir()
            variant, _ = translator.production_pdf_variant_html(
                source,
                root / "render",
                "innsmouth",
                {"print_columns": 1, "layout_mode": "single_column_flow"},
            )

            self.assertIn("column-count: 1", html)
            self.assertIn("body.print-columns-1 .production-page.page-type-credits", html)
            self.assertIn("column-span: none !important", html)
            self.assertIn("height: 194mm", html)
            self.assertIn("body.print-columns-1 .credits-page-boundary { display: none !important", html)
            self.assertIn("break-before: auto; page-break-before: auto", html)
            self.assertIn("main { column-count: 1 !important", variant.read_text(encoding="utf-8"))

    def test_single_column_print_can_use_normal_page_flow_without_column_fragmentation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = {
                "project_key": "normal-single-column",
                "production_html": {
                    "output_html": str(root / "book.html"),
                    "print_columns": 1,
                    "avoid_single_column_fragmentation_context": True,
                },
            }
            html = translator.build_production_html_document(config, "<p>Body</p>", "")
            source = root / "source.html"
            source.write_text(html, encoding="utf-8")
            (root / "render").mkdir()
            variant, _ = translator.production_pdf_variant_html(
                source,
                root / "render",
                "normal-flow",
                {
                    "print_columns": 1,
                    "layout_mode": "single_column_flow",
                    "avoid_single_column_fragmentation_context": True,
                },
            )

            self.assertIn("column-count: auto", html)
            self.assertIn('<body class="print-columns-1 normal-single-column-flow">', html)
            self.assertIn("main { column-count: auto !important", variant.read_text(encoding="utf-8"))
            self.assertIn(
                '<body class="print-columns-1 normal-single-column-flow">',
                variant.read_text(encoding="utf-8"),
            )

    def test_initial_package_config_uses_default_source_toc_profile(self) -> None:
        config = translator.build_initial_package_config(
            source_pdf=Path("source.pdf"),
            project_key="sample_book",
            project_family="CoC",
            project_type="scenario",
            title_en=None,
            title_ru=None,
            package_root_value=None,
            public_package_root_value=None,
            workbench_root_value=None,
            qa_root_value=None,
        )

        toc_policy = config["production_html"]["toc_policy"]
        self.assertEqual(toc_policy["mode"], "preserve_and_link")
        self.assertEqual(toc_policy["source_title"], "Содержание")
        self.assertEqual(toc_policy["generated_fallback_title"], "Оглавление")
        self.assertEqual(toc_policy["columns"], 2)
        self.assertEqual(toc_policy["font_size"], "9.5pt")
        self.assertEqual(toc_policy["line_height"], "1.18")
        self.assertEqual(toc_policy["item_gap"], "3px")
        self.assertEqual(toc_policy["column_fill"], "balance")
        self.assertEqual(toc_policy["column_gap"], "7mm")

    def test_source_toc_preserves_title_entries_and_internal_links(self) -> None:
        config = self.toc_config()
        markdown = """<!-- source-page-005 -->
## Содержание
Введение ........ 6
  Глава ........ 7
<!-- source-page-006 -->
## Введение
### Глава
"""

        source_toc = translator.source_toc_from_markdown(markdown, config)
        _, headings, _ = translator.markdown_to_review_html(markdown, source_path=Path("source.md"), html_path=Path("book.html"))
        linked = translator.source_toc_with_internal_links(source_toc, headings)
        nav = translator.build_production_toc(headings, config, source_toc=linked)

        self.assertEqual(linked["title"], "Содержание")
        self.assertEqual([entry["href"] for entry in linked["entries"]], ["vvedenie", "glava"])
        self.assertEqual([entry["level"] for entry in linked["entries"]], [2, 3])
        self.assertIn('data-toc-origin="source"', nav)
        self.assertIn("<h1>Содержание</h1>", nav)
        self.assertNotIn("Оглавление", nav)
        self.assertIn('class="toc-level-2"', nav)
        self.assertIn('class="toc-level-3"', nav)
        self.assertEqual(nav.count('<a href="#'), 2)

    def test_source_toc_strips_dash_page_numbers(self) -> None:
        config = self.toc_config()
        markdown = """<!-- source-page-005 -->
## Содержание
- Введение — 6
<!-- source-page-006 -->
## Введение
"""

        source_toc = translator.source_toc_from_markdown(markdown, config)

        self.assertEqual(source_toc["entries"][0]["title"], "Введение")

    def test_generated_toc_is_fallback_only_when_source_toc_absent(self) -> None:
        config = {"production_html": {"toc_policy": {"max_heading_level": 2}}}
        markdown = "# Введение\n## Глава\n"

        _, headings, _ = translator.markdown_to_review_html(markdown, source_path=Path("source.md"), html_path=Path("book.html"))
        nav = translator.build_production_toc(headings, config, source_toc=translator.source_toc_from_markdown(markdown, config))

        self.assertIn('data-toc-origin="generated"', nav)
        self.assertIn("<h1>Оглавление</h1>", nav)
        self.assertEqual(nav.count('<a href="#'), 2)

    def test_source_toc_link_map_resolves_manual_alias(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            link_map = root / "toc-links.json"
            link_map.write_text(
                json.dumps(
                    {
                        "schema": "viral_toc_link_map.v1",
                        "entries": [
                            {"source_title": "Другое название", "matched_heading_id": "glava", "status": "approved"}
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            config = {"production_html": {"toc_policy": {"source_link_map": str(link_map)}}}
            source_toc = {"title": "Содержание", "entries": [{"title": "Другое название", "level": 1}]}
            linked = translator.source_toc_with_internal_links(
                source_toc, [{"title": "Глава", "href": "glava", "level": 2}], config
            )

            self.assertEqual(linked["entries"][0]["href"], "glava")
            self.assertEqual(linked["entries"][0]["level"], 2)
            self.assertEqual(linked["entries"][0]["link_status"], "mapped")
            self.assertEqual(linked["link_map_findings"], [])

    def test_source_toc_link_map_accepts_generic_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            link_map = root / "toc-links.json"
            link_map.write_text(
                json.dumps(
                    {
                        "schema": "translator_source_toc_link_map.v1",
                        "entries": [
                            {"source_title": "Alias", "matched_heading_id": "target", "status": "approved"}
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            config = {"production_html": {"toc_policy": {"source_link_map": str(link_map)}}}
            linked = translator.source_toc_with_internal_links(
                {"title": "Содержание", "entries": [{"title": "Alias", "level": 1}]},
                [{"title": "Target", "href": "target", "level": 2}],
                config,
            )

            self.assertEqual(linked["entries"][0]["href"], "target")
            self.assertEqual(linked["link_map_findings"], [])

    def test_source_toc_can_stop_before_service_text(self) -> None:
        config = {
            "page_map": {"004": {"type": "source_toc"}},
            "production_html": {
                "toc_policy": {
                    "manual_toc_titles": ["Содержание"],
                    "source_toc_stop_titles": ["ПРЕДУПРЕЖДЕНИЯ О СОДЕРЖАНИИ"],
                }
            },
        }
        markdown = """<!-- source-page-004 -->
## Содержание
Введение
ПРЕДУПРЕЖДЕНИЯ О СОДЕРЖАНИИ
Алкоголизм, потеря контроля
<!-- source-page-005 -->
## Введение
"""

        source_toc = translator.source_toc_from_markdown(markdown, config)

        self.assertEqual([entry["title"] for entry in source_toc["entries"]], ["Введение"])

    def test_source_toc_link_map_invalid_id_remains_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            link_map = root / "toc-links.json"
            link_map.write_text(
                json.dumps(
                    {
                        "schema": "viral_toc_link_map.v1",
                        "entries": [
                            {"source_title": "Alias", "href": "missing-id", "status": "approved"}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            config = {"production_html": {"toc_policy": {"source_link_map": str(link_map)}}}
            linked = translator.source_toc_with_internal_links(
                {"title": "Contents", "entries": [{"title": "Alias", "level": 1}]},
                [{"title": "Chapter", "href": "chapter", "level": 1}],
                config,
            )

            self.assertIsNone(linked["entries"][0]["href"])
            codes = {finding["code"] for finding in linked["link_map_findings"]}
            self.assertIn("source_toc_link_map_invalid_target", codes)
            self.assertIn("source_toc_link_unresolved", codes)

    def test_source_toc_link_map_allows_multiple_entries_to_one_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            link_map = root / "toc-links.json"
            link_map.write_text(
                json.dumps(
                    {
                        "artifact": "viral_toc_link_map",
                        "entries": [
                            {"source_title": "Раздел", "matched_heading_id": "target", "status": "link"},
                            {"source_title": "Подраздел", "matched_heading_id": "target", "status": "link"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            config = {"production_html": {"toc_policy": {"source_link_map": str(link_map)}}}
            linked = translator.source_toc_with_internal_links(
                {"title": "Содержание", "entries": [{"title": "Раздел", "level": 1}, {"title": "Подраздел", "level": 2}]},
                [{"title": "Цель", "href": "target", "level": 1}],
                config,
            )

            self.assertEqual([entry["href"] for entry in linked["entries"]], ["target", "target"])
            self.assertEqual(linked["link_map_findings"], [])

    def test_toc_columns_are_emitted_without_background(self) -> None:
        config = {"production_html": {"toc_policy": {"columns": 4}}}
        nav = translator.build_production_toc([{"title": "Глава", "href": "glava", "level": 1}], config)

        self.assertIn('data-toc-columns="4"', nav)
        self.assertIn("--toc-columns: 4", nav)
        self.assertIn("--toc-line-height: 1.18", nav)
        self.assertIn("--toc-item-gap: 3px", nav)
        self.assertNotIn("background-image", nav)

    def test_toc_compact_print_profile_is_emitted_as_css_variables(self) -> None:
        config = {
            "production_html": {
                "toc_policy": {
                    "font_size": "9.5pt",
                    "line_height": "1.05",
                    "item_gap": "2px",
                    "column_fill": "balance",
                    "column_gap": "7mm",
                }
            }
        }
        nav = translator.build_production_toc([{"title": "Глава", "href": "glava", "level": 1}], config)

        self.assertIn("--toc-font-size: 9.5pt", nav)
        self.assertIn("--toc-line-height: 1.05", nav)
        self.assertIn("--toc-item-gap: 2px", nav)
        self.assertIn("--toc-column-fill: balance", nav)
        self.assertIn("--toc-column-gap: 7mm", nav)

    def test_place_landing_and_toc_moves_source_cover_before_toc(self) -> None:
        config = {"postproduction": {"landing_page": "001", "toc_position": "after_landing"}}
        html = """
        <main>
          <nav id="toc" class="toc" data-toc-origin="source"></nav>
          <!-- pdf-page-001 --><section class="production-page page-type-cover" data-page="001"></section>
          <!-- pdf-page-002 --><section class="production-page" data-page="002"></section>
        </main>
        """

        moved, ok, action = translator.place_landing_and_toc(config, html)

        self.assertTrue(ok)
        self.assertEqual(action, "moved_landing_before_toc")
        self.assertLess(moved.index('data-page="001"'), moved.index('id="toc"'))

    def test_credits_default_profile_suppresses_an_unrequested_preceding_heading(self) -> None:
        config = {
            "page_map": {"002": {"type": "credits"}},
            "production_html": {"credits_policy": {"layout_profile": "two_columns_10pt"}},
        }
        body = (
            '<h1 id="viral">Viral</h1><!-- pdf-page-002 -->'
            '<section id="page-002"><h2>Авторы и участники</h2>'
            '<div class="table-wrap"><table><tr><th>Роль</th><th>Имя</th></tr>'
            '<tr><td>Текст</td><td>Автор</td></tr></table></div></section>'
        )

        transformed, report = translator.transform_credits_sections(body, config)

        self.assertNotIn('<h1 id="viral">Viral</h1>', transformed)
        self.assertIn('data-credits-profile="two_columns_10pt"', transformed)
        self.assertIn("--credits-columns: 2", transformed)
        self.assertIn('class="credits-page-boundary"', transformed)
        self.assertTrue(report[0]["suppressed_preceding_heading"])
        self.assertTrue(report[0]["page_boundary"])

    def test_credits_layout_profile_falls_back_to_readable_default(self) -> None:
        profile_name, profile = translator.credits_layout_profile(
            {"production_html": {"credits_policy": {"layout_profile": "unknown"}}}
        )

        self.assertEqual(profile_name, "two_columns_10pt")
        self.assertEqual(profile["columns"], 2)
        self.assertEqual(profile["font_size"], "10pt")

    def test_heading_credits_grid_pairs_roles_and_names(self) -> None:
        config = {
            "production_html": {
                "credits_policy": {
                    "heading_ids": ["authors"],
                    "layout_profile": "three_columns_8pt",
                    "layout_mode": "grid",
                    "role_name_pairs": 2,
                    "end_anchor_by_heading": {"authors": "after-credits"},
                }
            }
        }
        body = '<h2 id="authors">Авторы</h2><p>Текст</p><p>Автор</p><p>Редактура</p><p>Редактор</p><p>Примечание</p><a id="after-credits"></a><p>Вне авторов</p><h2 id="next">Далее</h2>'

        transformed, report = translator.transform_credits_sections(body, config)

        self.assertIn('class="credits-columns credits-grid"', transformed)
        self.assertEqual(transformed.count('class="credit-role"'), 2)
        self.assertEqual(transformed.count('class="credit-names"'), 2)
        self.assertIn('class="credit-item credit-note"', transformed)
        self.assertNotIn('class="credit-item credit-note"><p>Вне авторов</p>', transformed)
        self.assertIn('<a id="after-credits"></a><p>Вне авторов</p>', transformed)
        self.assertEqual(report[0]["layout_mode"], "grid")

    def test_place_custom_landing_credits_and_toc_in_frontmatter_order(self) -> None:
        config = {
            "production_html": {
                "landing_asset": {"src": "cover.png"},
                "credits_policy": {"frontmatter_position": "before_toc"},
            },
            "postproduction": {"toc_position": "after_landing"},
        }
        html = (
            '<main><section class="production-landing"></section>'
            '<nav id="toc" class="toc"></nav><p>Body</p>'
            '<section class="production-page page-type-credits"></section>'
            '<div class="credits-page-boundary" aria-hidden="true"></div></main>'
        )

        moved, ok, action = translator.place_landing_and_toc(config, html)

        self.assertTrue(ok)
        self.assertIn("moved_credits_before_toc", action)
        self.assertLess(moved.index("production-landing"), moved.index("page-type-credits"))
        self.assertLess(moved.index("page-type-credits"), moved.index('id="toc"'))

    def test_document_does_not_add_a_second_page_break_after_toc(self) -> None:
        html = translator.build_production_html_document(
            {"scenario_title_ru": "Тест", "production_html": {"print_columns": 1, "output_html": "tmp/test.html"}},
            '<p>Текст</p>',
            '<nav id="toc" class="toc"></nav>',
        )

        self.assertNotIn('class="hard-page-break"', html)
        self.assertIn("body.print-columns-1 .art-full-page", html)

    def test_declared_table_continuation_merges_rows_and_renumbers_first_column(self) -> None:
        config = {
            "production_html": {
                "table_continuations": [
                    {"heading_id": "outdoor-encounters", "continuation_page": "059", "renumber_first_column": True}
                ]
            }
        }
        body = (
            '<h2 id="outdoor-encounters">Встречи</h2><div class="table-wrap"><table>'
            '<tr><th>d10</th><th>Событие</th></tr><tr><td>1</td><td>Первое</td></tr>'
            '</table></div><!-- pdf-page-059 --><section id="page-059">'
            '<div class="table-wrap"><table><tr><th>d10</th><th>Событие</th></tr>'
            '<tr><td>1</td><td>Второе</td></tr><tr><td>2</td><td>Третье</td></tr>'
            '</table></div></section>'
        )

        merged, report = translator.merge_table_continuations(body, config)

        self.assertEqual(report[0]["status"], "merged")
        self.assertEqual(report[0]["rows_added"], 2)
        self.assertIn('<td>1</td><td>Первое</td>', merged)
        self.assertIn('<td>2</td><td>Второе</td>', merged)
        self.assertIn('<td>3</td><td>Третье</td>', merged)
        self.assertEqual(merged.count('<div class="table-wrap">'), 1)

    def test_page_flow_defaults_to_columns_except_declared_pages_and_types(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            html = root / "book.html"
            html.write_text('<html><head></head><body><main><section id="page-004" class="production-page page-type-full-art">A</section><section id="page-104" class="production-page page-type-map">B</section></main></body></html>', encoding="utf-8")
            rendered, checks = translator.production_pdf_variant_html(
                html,
                root,
                "two_column",
                {
                    "print_columns": 2,
                    "layout_mode": "page_flow_columns",
                    "page_flow_exempt_page_types": ["cover"],
                    "page_flow_exempt_pages": ["104"],
                    "statblock_section_policy": {"break_before": "inline", "heading_ids": []},
                },
            )
            css = rendered.read_text(encoding="utf-8")

        self.assertIn(".production-page.page-type-cover", css)
        self.assertIn("body.pdf-layout-page-flow-columns .production-page.page-type-cover figure", css)
        self.assertIn("max-height: 252mm !important", css)
        self.assertIn(".production-page#page-104", css)
        self.assertNotIn(".production-page.page-type-full-art {\n    display: block", css)
        self.assertNotIn("body.pdf-layout-page-flow-columns #", css)
        self.assertNotIn("padding: 0 !important", css)
        self.assertTrue(checks["display_contents_scoped"])
        self.assertTrue(checks["special_pages_block_display"])
        self.assertTrue(checks["cover_full_page_art_css"])

    def test_cover_page_art_is_promoted_from_manifest_to_full_page_class(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            qa = root / "qa"
            qa.mkdir()
            (qa / "art_manifest.json").write_text(
                json.dumps(
                    {
                        "placements": [
                            {
                                "placement_id": "xref-00001",
                                "source_page": "001",
                                "runtime_src": "Images/cover.png",
                                "semantic_role": "source_image",
                                "css_class": "art-inline",
                                "decision_state": "approved",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            config = {
                "workbench_qa_root": str(qa),
                "page_map": {"001": {"type": "cover"}},
                "production_art_layout": {"art_manifest": "art_manifest.json"},
            }

            classes, _ = translator.reader_art_layout_from_manifest(config)

        self.assertEqual(classes["xref-00001"], "art-cover art-full-page")

    def test_cover_background_underlay_can_be_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "book.html"
            config = {
                "production_html": {"output_html": str(output)},
                "frontmatter": {"cover": {"background_underlay": False}},
            }

            html = translator.build_production_html_document(config, "", "")

        self.assertIn(".production-page.page-type-cover { min-height: 236mm; background: transparent none;", html)
        self.assertNotIn(".production-page.page-type-cover { min-height: 236mm; background: #2b170d", html)

    def test_page_flow_full_width_section_starts_at_semantic_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            html = root / "book.html"
            html.write_text(
                '<html><head></head><body><main>'
                '<section class="production-page" id="page-069"><p>Before.</p><h2 id="appendix">Appendix</h2><figure><img src="a.png"></figure></section>'
                '<section class="production-page page-type-handout" id="page-070"><figure><img src="b.png"></figure></section>'
                '</main></body></html>',
                encoding="utf-8",
            )
            rendered, checks = translator.production_pdf_variant_html(
                html,
                root,
                "two_column",
                {
                    "print_columns": 2,
                    "layout_mode": "page_flow_columns",
                    "page_flow_exempt_page_types": ["cover"],
                    "full_width_sections": [{"start_heading_id": "appendix", "mode": "to_document_end", "title": "APPENDIX"}],
                    "statblock_section_policy": {"break_before": "inline", "heading_ids": []},
                },
            )
            css = rendered.read_text(encoding="utf-8")

        self.assertIn('data-full-width-section-start="appendix"', css)
        self.assertIn('<h1 class="pdf-appendix-title">APPENDIX</h1>', css)
        self.assertIn('id="page-069"><p>Before.</p></section><section class="production-page page-type-appendix pdf-full-width-section"', css)
        self.assertIn('.pdf-full-width-section ~ .production-page', css)
        self.assertTrue(checks["full_width_sections_applied"])
        self.assertEqual(checks["full_width_section_start_ids"], ["appendix"])

    def test_appendix_handout_markers_become_normalized_headings(self) -> None:
        config = {
            "production_html": {
                "handout_heading_policy": {
                    "enabled": True,
                    "appendix_heading": "Раздатки",
                    "heading_level": 2,
                    "required_base_numbers": ["1", "4", "5", "19"],
                    "title_overrides": [
                        {"number": "1", "source_page": "069", "title": "Карта острова", "force_title": True}
                    ],
                }
            }
        }
        markdown = """<!-- source-page-069 -->
## Раздатки

Раздаточный материал №1

<!-- source-page-074 -->
### Письма Marco: Handout #4 / Handout #5

<!-- source-page-087 -->
## Снаружи больницы

Handout #19

В тексте сценария (Handout #19) остаётся ссылкой.
"""

        normalized, report = translator.normalize_appendix_handout_headings(markdown, config)

        self.assertIn("## Карта острова — Handout #1", normalized)
        self.assertIn("## Письма Marco: Handout #4 / Handout #5", normalized)
        self.assertIn("## Снаружи больницы — Handout #19", normalized)
        self.assertNotIn("\nHandout #19\n", normalized)
        self.assertIn("(Handout #19)", normalized)
        self.assertEqual(report["findings"], [])

    def test_normalized_markdown_output_is_production_only(self) -> None:
        config = {
            "production_html": {
                "handout_heading_policy": {
                    "output_markdown": "CoC/Output/Scenarios/Test/For_Keeper/KeeperBook_v2.md"
                }
            }
        }

        self.assertEqual(
            translator.normalized_markdown_output_path(config),
            translator.root_path("CoC/Output/Scenarios/Test/For_Keeper/KeeperBook_v2.md"),
        )
        self.assertIsNone(translator.normalized_markdown_output_path(config, trial=True))

    def test_coverage_visible_text_excludes_raw_html_traceability_attributes(self) -> None:
        visible = translator.coverage_visible_text(
            '<div data-placement-id="viral-art-051" data-source-page="065">Текст 7</div>',
            kind="markdown",
        )

        self.assertEqual(translator.numeric_tokens(visible), ["7"])

    def test_credits_semantic_qa_rejects_a_heading_outside_the_credits_section(self) -> None:
        config = {
            "page_map": {"002": {"type": "credits"}},
            "production_html": {"credits_policy": {"layout_profile": "two_columns_10pt", "require_background_image": False}},
        }
        html = '''
        <style>
        .production-page.page-type-credits .credits-frame { print-color-adjust: exact; }
        .production-page.page-type-credits .credits-columns { columns: var(--credits-columns, 2); font-size: var(--credits-font-size, 10pt); overflow-wrap: anywhere; }
        </style>
        <h1>Viral</h1><!-- pdf-page-002 -->
        <section id="page-002" class="production-page page-type-credits"><div class="credits-frame">
        <div class="credits-columns" data-credits-profile="two_columns_10pt" style="--credits-columns: 2; --credits-font-size: 10pt; --credits-line-height: 1.15; --credits-column-gap: 9mm;"></div>
        </div></section><div class="credits-page-boundary" aria-hidden="true"></div>
        '''

        _, findings, _ = translator.production_html_semantic_qa(config, html)

        self.assertIn(
            {"code": "credits_preceding_heading_outside_section", "page": "002"},
            findings,
        )

    def test_source_toc_replacement_records_page_type_evidence_and_mixed_manual_policy_is_opt_in(self) -> None:
        config = self.toc_config()
        source_body = '<!-- pdf-page-005 --><section id="page-005"><h2>Содержание</h2><p>Введение</p><ol><li>Глава</li></ol></section>'
        replaced, evidence = translator.remove_source_toc_sections(source_body, config)
        self.assertNotIn("Содержание", replaced)
        self.assertEqual(evidence[0]["page_type"], "source_toc")
        self.assertEqual(evidence[0]["mode"], "preserved_as_production_toc")

        manual_config = {"production_html": {"toc_policy": {"remove_manual_toc_mixed_blocks": True}}}
        mixed, removed = translator.remove_manual_toc_sections(source_body, manual_config)
        self.assertNotIn("Содержание", mixed)
        self.assertNotIn("Введение", mixed)
        self.assertEqual(removed[0]["mode"], "mixed_blocks_replaced_by_generated_toc")

    def test_callout_conversion_honors_declared_boundary_and_excludes_toc(self) -> None:
        config = {
            "production_html": {
                "callout_policy": {
                    "rules": [{"label": "Заметки Хранителя", "boundary": "next_heading_same_or_higher", "style_class": "keeper-note"}],
                    "toc_exclude": True,
                }
            }
        }
        markdown = "## Заметки Хранителя\nТекст для ведущего.\n### Деталь\nСкрытая деталь.\n## Следующий раздел\n"

        transformed, report = translator.transform_markdown_callouts(markdown, config)
        body, headings, _ = translator.markdown_to_review_html(transformed, source_path=Path("source.md"), html_path=Path("book.html"))

        self.assertEqual(len(report["converted"]), 1)
        self.assertIn('class="review-callout keeper-note"', body)
        self.assertNotIn("Заметки Хранителя", [item["title"] for item in translator.filter_production_toc(headings, config)])
        self.assertIn("Следующий раздел", [item["title"] for item in headings])

    def test_callout_conversion_never_consumes_page_marker(self) -> None:
        config = {
            "callout_policy": {
                "rules": [{"label": "Заметки Хранителя", "boundary": "next_heading_same_or_higher"}]
            }
        }
        markdown = "## Заметки Хранителя\nТекст.\n<!-- source-page-006; source_hash: abc -->\n## Раздел\n"

        transformed, report = translator.transform_markdown_callouts(markdown, config)

        self.assertEqual(len(report["converted"]), 1)
        self.assertIn("\n<!-- source-page-006; source_hash: abc -->\n", transformed)
        self.assertNotIn("> <!-- source-page-006", transformed)

    def test_ordered_list_continuity_uses_html_start_without_merging_lists(self) -> None:
        markdown = "1. Первый\n2. Второй\n\nТолько объявленный разделитель.\n\n3. Третий\n4. Четвёртый\n"
        body, _, _ = translator.markdown_to_review_html(markdown, source_path=Path("source.md"), html_path=Path("book.html"))
        report = translator.ordered_list_continuity_report(
            markdown,
            {"production_html": {"ordered_list_continuity_policy": {"known_continuations": [{"next_start": 3}]}}},
        )

        self.assertEqual(body.count("<ol"), 2)
        self.assertIn('<ol start="3">', body)
        self.assertEqual(report["findings"], [])

    def test_preserved_art_injects_into_page_with_type_class(self) -> None:
        config = {
            "production_outputs": {"images": "tmp/recovery-images"},
            "art_integration": {
                "preserved_page_art": [
                    {"page": 7, "role": "source_image", "target_filename": "page-007.png"}
                ]
            },
        }
        body = '<section class="production-page page-type-full-art" id="page-007" data-page="007"><p>Text</p></section>'

        transformed, report = translator.inject_preserved_page_art(body, config, Path("tmp/book.html"))

        self.assertEqual(report[0]["inserted"], True)
        self.assertIn('data-source-page="007"', transformed)

    def test_term_gate_supports_package_registries_contextual_exceptions_and_single_registry_compatibility(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            source = root / "source.md"
            output = root / "output.md"
            shared = root / "shared.csv"
            package = root / "package.csv"
            source.write_text("Test mechanic\nPackage mechanic\n", encoding="utf-8")
            output.write_text("Тестовая механика\nПакетная механика\nSAN на листе персонажа\nSAN в обычном тексте\n", encoding="utf-8")
            shared.write_text("source_term,accepted_ru,status\nTest mechanic,Тестовая механика,accepted\n", encoding="utf-8")
            package.write_text("source_term,accepted_ru,status\nPackage mechanic,Пакетная механика,accepted\n", encoding="utf-8")
            config_path = self.write_config(
                root,
                {
                    "term_gate": {
                        "registry": str(shared),
                        "registries": [str(package)],
                        "source_markdown": str(source),
                        "output_markdown": str(output),
                        "forbidden_mechanics": ["SAN"],
                        "exceptions": [{"term": "SAN", "context_regex": "листе персонажа", "reason": "approved sheet abbreviation"}],
                    }
                },
            )

            result = translator.run_term_gate(config_path, check_only=True)

            self.assertEqual(result["counts"]["registry_rows"], 2)
            self.assertEqual(result["counts"]["term_exception_allowlist_entries"], 1)
            self.assertIn("forbidden_mechanics_term", [finding["code"] for finding in result["findings"]])
            self.assertEqual(result["forbidden_mechanics"][0]["hits"][0]["allowed"], True)

    def test_canonical_art_manifest_requires_crop_or_full_page_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            manifest = root / "art-placement.json"
            placement = {
                "asset_id": "art-001",
                "runtime_filename": "art-001.jpeg",
                "semantic_role": "source_image",
                "source_page": 1,
                "heading_id": "scene-one",
                "insertion_rule": "after_heading",
                "decision_state": "approved",
                "source_kind": "page_render",
            }
            manifest.write_text(json.dumps({"placements": [placement]}), encoding="utf-8")
            config = {"workbench_qa_root": str(root), "art_integration": {"placement_manifest": str(manifest)}}

            findings = translator.canonical_art_placement_findings(config)
            self.assertIn("selected_art_missing_crop_box", [item["code"] for item in findings])

            placement["allow_full_page_art"] = True
            placement["full_page_review_reason"] = "visual-first handout approved for full-page treatment"
            manifest.write_text(json.dumps({"placements": [placement]}), encoding="utf-8")
            self.assertIn("full_page_art_not_reviewed", [item["code"] for item in translator.canonical_art_placement_findings(config)])

            placement["visual_review_status"] = "approved_full_page"
            manifest.write_text(json.dumps({"placements": [placement]}), encoding="utf-8")
            self.assertEqual(translator.canonical_art_placement_findings(config), [])

    def test_art_bearing_package_requires_canonical_placement_manifest(self) -> None:
        config = {
            "workbench_qa_root": "qa",
            "art_integration": {"preserved_page_art": [{"page": 7, "role": "map", "target_filename": "map.png"}]},
        }

        self.assertEqual(
            translator.canonical_art_placement_findings(config),
            [{"code": "missing_art_placement_manifest", "path": None}],
        )

    def test_keeper_art_block_renders_only_the_generated_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            source = root / "For_Keeper" / "KeeperBook.md"
            runtime = root / "Images" / "Runtime_Assets"
            runtime_v2 = root / "Images_v2" / "NPC"
            runtime.mkdir(parents=True)
            runtime_v2.mkdir(parents=True)
            (runtime / "art.jpeg").write_bytes(b"image")
            (runtime_v2 / "npc.png").write_bytes(b"image")
            markdown = (
                '<div class="keeper-art-block" data-placement-id="art-001" data-anchor-id="scene-one"> '
                '<img id="art-001-image" src="Images/Runtime_Assets/art.jpeg" alt="Scene art"> </div>\n\n'
                '<div class="keeper-art-block" data-placement-id="art-002" data-anchor-id="scene-two"> '
                '<img id="art-002-image" src="../Images_v2/NPC/npc.png" alt="NPC art"> </div>\n\n'
                '<div class="untrusted">not raw html</div>\n'
            )
            body, _, _ = translator.markdown_to_review_html(markdown, source_path=source, html_path=root / "book.html")

            self.assertIn('class="keeper-art-block"', body)
            self.assertIn('src="Images/Runtime_Assets/art.jpeg"', body)
            self.assertIn('src="Images_v2/NPC/npc.png"', body)
            self.assertIn('&lt;div class=&quot;untrusted&quot;&gt;', body)

    def test_reader_master_structural_anchors_and_tables_are_rendered(self) -> None:
        markdown = (
            'Вводный абзац без пустой строки перед якорем.\n'
            '<a id="nri-h-scene"></a>\n\n'
            '## Сцена\n\n'
            '<table><tr><th colspan="2">Заголовок</th></tr>'
            '<tr><td>Атака</td><td>45%<br>урон 1D6</td></tr></table>\n'
        )

        body, _, _ = translator.markdown_to_review_html(
            markdown,
            source_path=Path("MASTER_RU.md"),
            html_path=Path("book.html"),
        )

        self.assertIn('<a id="nri-h-scene"></a>', body)
        self.assertIn('<div class="table-wrap raw-html-table"><table>', body)
        self.assertIn('<th colspan="2">Заголовок</th>', body)
        self.assertIn('45%<br>урон 1D6', body)
        self.assertNotIn('&lt;table&gt;', body)

    def test_reader_master_leading_anchor_preserves_following_markdown(self) -> None:
        markdown = (
            'Предыдущий абзац.\n\n'
            '<a id="viral-room-1j"></a>**1J. Изолятор.** [См. 2E](#viral-room-2e)\n'
            '<a id="viral-room-2e"></a><a id="viral-room-2e-alias"></a>Обычный текст.\n'
        )

        body, _, _ = translator.markdown_to_review_html(
            markdown,
            source_path=Path("MASTER_RU.md"),
            html_path=Path("book.html"),
        )

        self.assertIn('<a id="viral-room-1j"></a>', body)
        self.assertIn('<strong>1J. Изолятор.</strong>', body)
        self.assertIn('<a href="#viral-room-2e">См. 2E</a>', body)
        self.assertIn('<a id="viral-room-2e"></a><a id="viral-room-2e-alias"></a>', body)
        self.assertNotIn('&lt;a id=', body)

    def test_reader_master_structural_html_allowlist_rejects_other_markup(self) -> None:
        markdown = (
            '<a id="safe" onclick="alert(1)"></a>\n\n'
            '<a id="safe-two" class="wrong"></a>**not admitted**\n\n'
            '<table><tr><td><script>alert(1)</script></td></tr></table>\n'
        )

        body, _, _ = translator.markdown_to_review_html(
            markdown,
            source_path=Path("MASTER_RU.md"),
            html_path=Path("book.html"),
        )

        self.assertIn('&lt;a id=&quot;safe&quot; onclick=&quot;alert(1)&quot;&gt;', body)
        self.assertIn('&lt;a id=&quot;safe-two&quot; class=&quot;wrong&quot;&gt;', body)
        self.assertIn('&lt;table&gt;', body)
        self.assertIn('&lt;script&gt;', body)

    def test_reader_art_manifest_relocates_and_adds_blocks_with_layout_classes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            manifest = root / "art_manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "placements": [
                            {
                                "placement_id": "art-existing",
                                "heading_id": "correct-heading",
                                "css_class": "art-float-right art-scale-30",
                            },
                            {
                                "placement_id": "art-added",
                                "heading_id": "second-heading",
                                "runtime_filename": "added.jpeg",
                                "emit_reader_art_block": True,
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            config = {
                "workbench_qa_root": str(root),
                "production_art_layout": {"art_manifest": str(manifest)},
            }
            markdown = (
                "## Correct heading\n\n"
                "## Second heading\n\n"
                '<div class="keeper-art-block" data-placement-id="art-existing" data-anchor-id="old-heading"> '
                '<img id="art-existing-image" src="Images/Runtime_Assets/existing.jpeg" alt="art-existing"> </div>\n'
            )

            relocated, report = translator.relocate_reader_art_blocks(markdown, config)
            classes, _ = translator.reader_art_layout_from_manifest(config)
            body, _, _ = translator.markdown_to_review_html(
                relocated,
                source_path=root / "For_Keeper" / "KeeperBook.md",
                html_path=root / "book.html",
                art_classes=classes,
            )

            self.assertEqual(len(report["findings"]), 0)
            self.assertIn('data-anchor-id="correct-heading"', relocated)
            self.assertIn('data-placement-id="art-added"', relocated)
            self.assertIn('class="keeper-art-block art-float-right art-scale-30"', body)

    def test_reader_art_manifest_can_preserve_existing_manual_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            manifest = root / "art_manifest.json"
            manifest.write_text(
                json.dumps({"placements": [{"placement_id": "art-existing", "heading_id": "correct-heading"}]}),
                encoding="utf-8",
            )
            config = {
                "workbench_qa_root": str(root),
                "production_art_layout": {
                    "art_manifest": str(manifest),
                    "preserve_existing_reader_art_blocks": True,
                },
            }
            markdown = (
                "## Correct heading\n\n"
                "Ручной текст.\n\n"
                '<div class="keeper-art-block" data-placement-id="art-existing" data-anchor-id="old-heading"> '
                '<img id="art-existing-image" src="../Images_v2/NPC/existing.png" alt="art-existing"> </div>\n'
            )

            relocated, report = translator.relocate_reader_art_blocks(markdown, config)

            self.assertEqual(len(report["findings"]), 0)
            self.assertEqual(relocated, markdown)
            self.assertTrue(report["relocated"][0]["preserved_existing"])

    def test_reader_metadata_suppression_is_page_scoped(self) -> None:
        markdown = (
            "<!-- source-page-104 -->\n\n"
            "Визуальный артефакт карты оставить.\n\n"
            "<!-- source-page-105 -->\n\n"
            "Визуальный артефакт карты удалить.\nПродолжение служебного текста.\n\n"
            "Читательский текст.\n"
        )
        config = {
            "production_html": {
                "reader_metadata_suppressions": [
                    {"source_page": "105", "starts_with": "Визуальный артефакт карты"}
                ]
            }
        }

        result, suppressed = translator.suppress_reader_metadata_markdown(markdown, config)

        self.assertEqual(len(suppressed), 1)
        self.assertIn("Визуальный артефакт карты оставить.", result)
        self.assertNotIn("Визуальный артефакт карты удалить.", result)
        self.assertIn("Читательский текст.", result)

    def test_map_and_handout_approval_rejects_empty_frame_but_accepts_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            qa = root / "qa"
            qa.mkdir()
            frame = root / "frame.png"
            content = root / "content.png"

            frame_image = Image.new("RGB", (1000, 780), "white")
            ImageDraw.Draw(frame_image).rectangle((5, 5, 994, 774), outline="black", width=5)
            frame_image.save(frame)
            content_image = Image.new("RGB", (1000, 780), "white")
            draw = ImageDraw.Draw(content_image)
            for x in range(80, 920, 80):
                draw.line((x, 60, x, 720), fill="black", width=5)
            for y in range(60, 721, 60):
                draw.line((80, y, 920, y), fill="black", width=5)
            draw.rectangle((330, 230, 670, 550), fill="gray")
            content_image.save(content)

            approval = {
                "allowed_roles": translator.IMAGE_APPROVAL_ROLES,
                "items": [
                    {"xref": 1, "source_path": str(frame), "decision_state": "approved", "target_role": "map", "target_filename": "frame.png"},
                    {"xref": 2, "source_path": str(content), "decision_state": "approved", "target_role": "handout", "target_filename": "content.png"},
                ],
            }
            (qa / "image_role_approval.json").write_text(json.dumps(approval), encoding="utf-8")
            config_path = self.write_config(root, {"production_outputs": {"images": str(root / "Images")}})

            result = translator.apply_image_approval(config_path)

            self.assertEqual(result["status"], "fail")
            self.assertEqual(result["counts"]["applied_or_would_apply"], 1)
            self.assertEqual(result["findings"][0]["code"], "empty_frame_or_mask_asset")
            self.assertEqual(result["findings"][0]["xref"], 1)

            classified = translator.classify_image_candidate(
                {
                    "xref": 1,
                    "path": str(frame),
                    "width": 1000,
                    "height": 780,
                    "ext": "png",
                    "bytes": frame.stat().st_size,
                    "sha256": translator.sha256_file(frame),
                    "page_refs": [{"page": 78}],
                },
                120,
            )
            self.assertEqual(classified["suggested_role"], "decoration")
            self.assertIn("near_empty_frame_or_mask", classified["reasons"])

    def test_art_layout_identity_flags_orphaned_approved_asset_and_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            approval_path = root / "approval.json"
            approval_path.write_text(
                json.dumps(
                    {
                        "items": [
                            {
                                "xref": 1194,
                                "pages": [78],
                                "decision_state": "approved",
                                "target_role": "map",
                                "target_filename": "approved-map.png",
                                "sha256": "approved-hash",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            config = {
                "workbench_qa_root": str(root),
                "intake": {"image_role_approval": str(approval_path)},
            }
            placements = [
                {
                    "asset_id": "page-078.png",
                    "asset_path": "page-078.png",
                    "page_id": "078",
                    "source_kind": "page_render_full_page",
                    "decision_state": "approved",
                }
            ]

            findings = translator.art_layout_approval_identity_findings(config, placements=placements, image_refs=["Images/page-078.png"])

            self.assertEqual(findings[0]["code"], "orphaned_approved_art_with_page_render_fallback")

    def test_art_layout_identity_accepts_matching_approved_asset_and_optimized_html_ref(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            approval_path = root / "approval.json"
            approval_path.write_text(
                json.dumps(
                    {
                        "items": [
                            {
                                "xref": 42,
                                "pages": [7],
                                "decision_state": "approved",
                                "target_role": "map",
                                "target_filename": "island-map.png",
                                "sha256": "source-hash",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            config = {"workbench_qa_root": str(root), "intake": {"image_role_approval": str(approval_path)}}
            placements = [
                {
                    "asset_id": "xref-00042",
                    "asset_path": "island-map.png",
                    "runtime_filename": "island-map.png",
                    "page_id": "007",
                    "source_kind": "extracted_asset",
                    "source_xref": 42,
                    "source_asset_sha256": "source-hash",
                    "decision_state": "approved",
                }
            ]

            findings = translator.art_layout_approval_identity_findings(
                config,
                placements=placements,
                image_refs=["Images/Maps/island-map_a1b2c3_q80.jpg"],
            )

            self.assertEqual(findings, [])

    def test_art_layout_image_refs_block_extension_format_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            html_path = root / "book.html"
            images = root / "Images"
            images.mkdir()
            disguised_png = images / "asset.png"
            Image.new("RGB", (10, 10), "white").save(disguised_png, format="JPEG")
            html_path.write_text('<img src="Images/asset.png" alt="asset">', encoding="utf-8")

            findings = translator.art_layout_image_ref_findings(html_path, ["Images/asset.png"])

            self.assertEqual(findings[0]["code"], "html_image_ref_extension_format_mismatch")
            self.assertEqual(findings[0]["actual_format"], "JPEG")
            self.assertEqual(findings[0]["expected_format"], "PNG")

    def test_canonical_art_manifest_adapts_to_layout_qa_contract(self) -> None:
        placements = translator.canonical_art_placements_as_layout(
            {
                "schema": "translator_art_placement_manifest.v1",
                "placements": [
                    {
                        "asset_id": "xref-1",
                        "runtime_filename": "map.jpeg",
                        "semantic_role": "map",
                        "source_kind": "extracted_asset",
                        "source_page": "007",
                        "heading_id": "island-map",
                        "insertion_rule": "after_heading",
                        "decision_state": "approved",
                        "visual_review_status": "approved",
                    }
                ],
            }
        )

        self.assertEqual(len(placements), 1)
        self.assertEqual(placements[0]["placement"], "page_art_after_heading")
        self.assertEqual(placements[0]["css_class"], "art-full-width")
        self.assertEqual(placements[0]["source_bbox_or_full_page"], "extracted_asset")

    def test_full_page_art_cards_bind_heading_caption_and_figure(self) -> None:
        body = (
            '<a id="handout-1"></a>\n'
            '<h3 id="handout-title">Handout 1</h3>\n'
            '<p>Map caption</p>\n'
            '<figure class="art-full-page"><img src="map.png"></figure>\n'
            '<h3 id="next">Next section</h3>'
        )
        config = {"production_html": {"keep_full_page_art_with_heading": True}}

        result, count = translator.wrap_full_page_art_cards(body, config)

        self.assertEqual(count, 1)
        self.assertIn(
            '<section class="full-page-art-card">\n<a id="handout-1"></a>\n'
            '<h3 id="handout-title">Handout 1</h3>\n<p>Map caption</p>\n'
            '<figure class="art-full-page"><img src="map.png"></figure>\n</section>',
            result,
        )
        self.assertTrue(result.endswith('<h3 id="next">Next section</h3>'))

    def test_full_page_art_card_does_not_capture_unheaded_preceding_prose(self) -> None:
        body = (
            '<h4 id="padre">Падре Анджело</h4>\n'
            '<figure class="art-body-right"><img src="padre.png"></figure>\n'
            '<p>Описание Падре Анджело.</p>\n'
            '<figure class="art-full-page"><img src="next-opening.png"></figure>\n'
            '<h2 id="next">Следующий раздел</h2>'
        )
        config = {"production_html": {"keep_full_page_art_with_heading": True}}

        result, count = translator.wrap_full_page_art_cards(body, config)

        self.assertEqual(count, 1)
        self.assertIn('<p>Описание Падре Анджело.</p>\n<section class="full-page-art-card">', result)
        self.assertNotIn('<section class="full-page-art-card">\n<p>Описание Падре Анджело.</p>', result)

    def test_pregen_art_card_uses_dedicated_atomic_class(self) -> None:
        body = (
            '<a id="pregen-marco"></a>\n'
            '<h3 id="marco-front">Лицевая сторона Марко</h3>\n'
            '<figure class="art-pregen-fullpage"><img src="marco.png"></figure>\n'
            '<h3 id="next">Next section</h3>'
        )
        config = {"production_html": {"keep_full_page_art_with_heading": True}}

        result, count = translator.wrap_full_page_art_cards(body, config)

        self.assertEqual(count, 1)
        self.assertIn('<section class="full-page-art-card pregen-art-card">', result)
        self.assertIn('<figure class="art-pregen-fullpage"><img src="marco.png"></figure>', result)

    def test_generated_toc_can_normalize_document_root_level(self) -> None:
        toc = [
            {"level": 2, "title": "Раздел", "href": "section", "source_anchor_ids": []},
            {"level": 3, "title": "Подраздел", "href": "subsection", "source_anchor_ids": []},
        ]
        config = {"production_html": {"toc_policy": {
            "mode": "generated", "root_heading_level": 2, "max_heading_level": 3
        }}}

        result = translator.build_production_toc(toc, config)

        self.assertIn('class="toc-level-1"><a href="#section">Раздел</a>', result)
        self.assertIn('class="toc-level-2"><a href="#subsection">Подраздел</a>', result)

    def test_production_css_allows_subheadings_and_tables_to_wrap_body_art(self) -> None:
        html = translator.build_production_html_document(
            {"scenario_title_ru": "Тест", "production_html": {
                "print_columns": 1, "output_html": "tmp/test-production.html",
                "allow_statblock_flow_beside_body_art": True,
            }},
            "<p>Body</p>",
            "",
        )

        self.assertIn("h1, h2, h3, h4 { clear: both; }", html)
        self.assertIn("figure.art-body-right + a + h3,", html)
        self.assertIn("figure.art-scenario-right + a + h4 { clear: none; }", html)
        self.assertNotRegex(html, r"\.table-wrap\s*\{[^}]*clear:\s*both")
        self.assertIn("body.print-columns-1 .statblock-card {\n    break-inside: auto !important;", html)
        self.assertIn("overflow: auto !important;", html)

    def test_production_css_allows_long_callouts_and_forces_configured_section_starts(self) -> None:
        html = translator.build_production_html_document(
            {"scenario_title_ru": "Тест", "production_html": {
                "print_columns": 1,
                "output_html": "tmp/test-production.html",
                "allow_long_callout_page_breaks": True,
                "avoid_single_column_fragmentation_context": True,
                "page_break_before_anchor_ids": ["player-handouts", "keeper-maps", "pregens"],
            }},
            "<p>Body</p>",
            "",
        )

        self.assertIn(
            'body.print-columns-1 blockquote.review-callout:not(.callout-keep-together):not([data-break-policy="keep_together"])',
            html,
        )
        self.assertIn("body.print-columns-1 .production-section-start", html)
        self.assertIn("column-count: auto", html)
        self.assertIn("body.normal-single-column-flow .full-page-art-card + a + h3", html)
        self.assertIn("body.normal-single-column-flow .full-page-art-card {", html)
        self.assertIn("page-break-after: auto !important;", html)
        self.assertIn("min-height: 0 !important;", html)
        self.assertIn("body.normal-single-column-flow .full-page-art-card h3", html)
        self.assertIn(
            "body.normal-single-column-flow .full-page-art-card + .production-section-start",
            html,
        )
        self.assertIn(
            "body.normal-single-column-flow .full-page-art-card h3 + figure.art-full-page img",
            html,
        )
        self.assertIn("body.normal-single-column-flow .section-heading-bound-card > h2", html)
        self.assertIn("body.print-columns-1 .section-heading-bound-card", html)
        self.assertIn("page-break-before: always !important;", html)
        self.assertIn(
            "body.print-columns-1 blockquote.review-callout:has(+ .production-section-start)",
            html,
        )
        self.assertIn("font-size: 9.25pt;", html)
        self.assertIn("line-height: 1.16;", html)
        self.assertIn("columns: 2;", html)
        self.assertIn("column-gap: 6mm;", html)
        self.assertIn(
            "blockquote.review-callout:has(+ .production-section-start) > p {",
            html,
        )
        self.assertIn("break-inside: avoid-column;", html)
        self.assertIn(
            "blockquote.review-callout:has(+ .production-section-start) > p:nth-child(2n+3):nth-child(-n+19)",
            html,
        )
        self.assertIn("break-after: avoid-column !important;", html)
        self.assertIn("body.print-columns-1 a#pregens + h2 + .full-page-art-card", html)
        self.assertIn("min-height: 0 !important;", html)

    def test_wrap_section_page_starts_adds_nonempty_heading_blocks(self) -> None:
        body = (
            '<blockquote class="review-callout"><p>Long callout</p></blockquote>\n'
            '<a id="player-handouts"></a>\n'
            '<h2>Раздаточные материалы</h2>\n'
            '<a id="ordinary"></a>\n<h2>Обычный раздел</h2>\n'
            '<section class="production-section-start">\n'
            '<a id="keeper-maps"></a>\n<h2>Карты Хранителя</h2>\n</section>'
        )
        config = {"production_html": {
            "page_break_before_anchor_ids": ["player-handouts", "keeper-maps"]
        }}

        result, inserted = translator.wrap_section_page_starts(body, config)

        self.assertEqual(inserted, ["player-handouts"])
        self.assertIn(
            '</blockquote>\n<section class="production-section-start">\n'
            '<a id="player-handouts"></a>\n<h2>Раздаточные материалы</h2>\n</section>',
            result,
        )
        self.assertEqual(
            result.count('<section class="production-section-start">'),
            2,
        )

    def test_bind_section_heading_into_first_card_keeps_group_title_with_pregen(self) -> None:
        body = (
            '<a id="pregens"></a>\n'
            '<h2 id="characters">Готовые сыщики</h2>\n'
            '<section class="full-page-art-card pregen-art-card">\n'
            '<a id="marco"></a>\n<h3>Марко</h3>\n'
            '<figure class="art-pregen-fullpage"><img src="marco.png"></figure>\n'
            '</section>'
        )
        config = {"production_html": {
            "bind_section_heading_into_first_card_anchor_ids": ["pregens"]
        }}

        result, bound = translator.bind_section_heading_into_first_card(body, config)

        self.assertEqual(bound, ["pregens"])
        self.assertIn(
            '<section class="section-heading-bound-card full-page-art-card pregen-art-card">\n'
            '<a id="pregens"></a>\n<h2 id="characters">Готовые сыщики</h2>\n'
            '<a id="marco"></a>',
            result,
        )

    def test_suppress_section_navigation_lists_removes_only_configured_micro_toc(self) -> None:
        body = (
            '<a id="player-handouts"></a>\n'
            '<h2 id="handouts">Раздаточные материалы</h2>\n'
            '<ul>\n<li><a href="#handout-1">Материал 1</a></li>\n</ul>\n'
            '<section class="full-page-art-card"><h3>Материал 1</h3></section>\n'
            '<a id="keeper-maps"></a>\n'
            '<h2 id="maps">Карты Хранителя</h2>\n'
            '<figure class="art-body-right"><img src="map.png"></figure>\n'
            '<ul>\n<li><a href="#map-1">Карта 1</a></li>\n</ul>\n'
            '<p>Описание карт.</p>\n'
            '<h2 id="ordinary">Обычный раздел</h2>\n'
            '<ul>\n<li>Обычный список</li>\n</ul>'
        )
        config = {"production_html": {
            "suppress_section_navigation_after_anchor_ids": ["player-handouts", "keeper-maps"]
        }}

        result, removed = translator.suppress_section_navigation_lists(body, config)

        self.assertEqual(removed, ["player-handouts", "keeper-maps"])
        self.assertNotIn('href="#handout-1"', result)
        self.assertNotIn('href="#map-1"', result)
        self.assertIn('<figure class="art-body-right"><img src="map.png"></figure>', result)
        self.assertIn("<li>Обычный список</li>", result)

    def test_handout_art_card_binds_description_after_figure(self) -> None:
        body = (
            '<a id="handout-33"></a>\n'
            '<h3 id="handout-title">Handout 33</h3>\n'
            '<figure class="art-handout-page"><img src="pit.png"></figure>\n'
            '<p><em>Handout #33</em></p>\n'
            '<a id="handout-34"></a>\n'
            '<h3 id="next">Handout 34</h3>'
        )
        config = {"production_html": {"keep_full_page_art_with_heading": True}}

        result, count = translator.wrap_full_page_art_cards(body, config)

        self.assertEqual(count, 1)
        self.assertIn(
            '<section class="full-page-art-card handout-art-card">\n<a id="handout-33"></a>\n'
            '<h3 id="handout-title">Handout 33</h3>\n'
            '<figure class="art-handout-page"><img src="pit.png"></figure>\n'
            '<p><em>Handout #33</em></p>\n</section>',
            result,
        )
        self.assertTrue(result.endswith('<h3 id="next">Handout 34</h3>'))

    def test_generic_figure_caption_suppression_is_configured_and_exact(self) -> None:
        body = (
            '<figure><img src="a.jpg"><figcaption>Иллюстрация</figcaption></figure>\n'
            '<figure><img src="b.jpg"><figcaption>Meaningful caption</figcaption></figure>'
        )
        config = {"production_html": {"suppress_figure_captions": ["Illustration", "Иллюстрация"]}}

        result, removed = translator.suppress_generic_figure_captions(body, config)

        self.assertEqual(removed, ["Иллюстрация"])
        self.assertNotIn("<figcaption>Иллюстрация</figcaption>", result)
        self.assertIn("<figcaption>Meaningful caption</figcaption>", result)

    def test_pdf_render_command_resolves_portable_browser_placeholder(self) -> None:
        result = translator.production_pdf_render_command(
            ["{browser_executable}", "--print-to-pdf={output_pdf}", "{source_html_uri}"],
            source_html=Path("book.html"),
            output_pdf=Path("book.pdf"),
            temp_dir=Path("temp"),
            browser_executable="C:/Portable/Edge/msedge.exe",
        )

        self.assertEqual(result[0], "C:/Portable/Edge/msedge.exe")
        self.assertEqual(result[1], "--print-to-pdf=book.pdf")
        self.assertTrue(result[2].startswith("file:"))

    def test_process_output_replaces_device_local_repo_path(self) -> None:
        source = f"123 bytes written to file {translator.REPO_ROOT}\\book.tmp.pdf"

        result = translator.portable_process_output_lines(source)

        self.assertEqual(result, ["123 bytes written to file <repo>\\book.tmp.pdf"])

    def test_release_qa_enforces_nonempty_reports_minima_stale_evidence_and_open_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            html = root / "book.html"
            evidence = root / "evidence.md"
            report = root / "evidence.json"
            ledger = root / "blockers.json"
            html.write_text("<html><body>ok</body></html>", encoding="utf-8")
            evidence.write_text("current evidence", encoding="utf-8")
            report.write_text(json.dumps({"status": "pass", "counts": {"rows": 0}, "sha256": "stale"}), encoding="utf-8")
            ledger.write_text(json.dumps({"open_blockers": [{"status": "open", "id": "VTF-022"}]}), encoding="utf-8")
            config_path = self.write_config(
                root,
                {
                    "production_outputs": {"html": str(html)},
                    "release_qa": {
                        "html": str(html),
                        "required_gates": [],
                        "required_reports": ["evidence"],
                        "require_nonempty_required_reports": True,
                        "report_paths": {"evidence": str(report)},
                        "required_report_minima": {"evidence": {"counts.rows": 1}},
                        "evidence_freshness": [{"report": "evidence", "field": "sha256", "path": str(evidence)}],
                        "open_blocker_ledger": {"path": str(ledger), "fail_on_open": True},
                    },
                },
            )

            result = translator.run_release_qa(config_path, check_only=True)

            codes = {finding["code"] for finding in result["findings"]}
            self.assertIn("required_report_semantic_minimum_not_met", codes)
            self.assertIn("stale_evidence_hash_mismatch", codes)
            self.assertIn("open_release_blockers", codes)
            self.assertEqual(result["counts"]["open_blockers"], 1)


if __name__ == "__main__":
    unittest.main()
