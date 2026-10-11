"""Exact duplicate heading ownership for reviewed body presentation."""
from __future__ import annotations

import copy
import unittest
from pathlib import Path

from lxml import html
from translator.translator import markdown_to_review_html

from kb_creator.pipeline import reader_projection
from kb_creator.tests.test_reader_whole_artifact import PDF_HASH, _unit


def fixture():
    text = "## Национальность: **американец**"
    strings = ["<!-- source-page-041 -->", text, "<!-- source-page-042 -->",
               "# Персонажи", text, "Первый персонаж.", text,
               "Второй персонаж.", text, "Третий персонаж."]
    units = [_unit(f"unit-{index}", value) for index, value in enumerate(strings)]
    binding = lambda index: {key: units[index][key] for key in ("unit_id", "ru_sha256")}
    cohort = [binding(index) for index in (4, 6, 8)]
    decision = {"role": "prose_presentation", "unit": binding(6),
                "heading_occurrence": {"ordinal": 1, "cohort": cohort},
                "reason": "reviewed stat field", "source_evidence": "exact source fixture"}
    options = {"source_toc": {"state": "absent", "source_pdf_sha256": PDF_HASH,
                              "reason": "fixture"}, "body_links": [], "asset_choices": [],
               "hit_points": {"presentation": "numeric"}, "display_roles": [decision]}
    body, toc, _ = markdown_to_review_html("\n\n".join(strings), source_path=Path("unit.md"),
                                           html_path=Path("unit.html"), blockquote_heading_offset=0)
    return body, toc, {"units": units, "spans": []}, options


class ProseOccurrenceTests(unittest.TestCase):
    def project(self, body, toc, projection, options):
        return reader_projection.project_reader_html(body, toc, projection, options)

    def test_only_reviewed_middle_occurrence_changes_and_inline_text_survives(self):
        body, toc, projection, options = fixture()
        rendered, _, report = self.project(body, toc, projection, options)
        tree = html.fragment_fromstring(rendered, create_parent="main")
        page = tree.xpath('.//section[@data-page="042"]')[0]
        headings = page.xpath('./h2')
        self.assertEqual(len(headings), 2)
        self.assertEqual(len(page.xpath('./p[strong]')), 1)
        self.assertEqual(page.xpath('./p[strong]')[0].text_content(), "Национальность: американец")
        self.assertEqual(len(tree.xpath('.//section[@data-page="041"]/h2')), 1)
        self.assertEqual([row.text_content() for row in page.xpath('./p[not(strong)]')],
                         ["Первый персонаж.", "Второй персонаж.", "Третий персонаж."])
        self.assertEqual(report["display_roles"], options["display_roles"])

    def test_all_cohort_members_bind_before_any_mutation_regardless_of_role_order(self):
        body, toc, projection, options = fixture()
        template = options["display_roles"][0]
        roles = []
        for ordinal, binding in enumerate(template["heading_occurrence"]["cohort"]):
            decision = copy.deepcopy(template)
            decision["unit"] = binding
            decision["heading_occurrence"]["ordinal"] = ordinal
            roles.append(decision)
        results = []
        for ordered in (roles, list(reversed(roles))):
            options["display_roles"] = ordered
            rendered, _, _ = self.project(body, toc, projection, options)
            page = html.fragment_fromstring(rendered, create_parent="main").xpath(
                './/section[@data-page="042"]')[0]
            self.assertEqual(len(page.xpath('./p[strong]')), 3)
            self.assertFalse(page.xpath('./h2'))
            results.append(rendered)
        self.assertEqual(*results)

    def test_bad_witnesses_unknown_roles_and_changed_source_cohorts_fail_closed(self):
        for case in ("malformed", "partial", "ordinal", "bool", "hash", "order", "source", "unknown"):
            with self.subTest(case=case):
                body, toc, projection, options = fixture()
                decision = options["display_roles"][0]
                witness = decision["heading_occurrence"]
                if case == "malformed": witness["guess"] = True
                if case == "partial": witness["cohort"].pop()
                if case == "ordinal": witness["ordinal"] = 0
                if case == "bool": witness["ordinal"] = True
                if case == "hash": witness["cohort"][0]["ru_sha256"] = "0" * 64
                if case == "order": witness["cohort"].reverse()
                if case == "source": projection["units"][4]["ru_text"] += " изменено"
                if case == "unknown": decision["role"] = "heading_prose_split"
                with self.assertRaisesRegex(ValueError, "heading occurrence"):
                    self.project(body, toc, projection, options)

    def test_missing_extra_or_changed_dom_occurrences_fail_closed(self):
        for case in ("missing", "extra", "markup"):
            with self.subTest(case=case):
                body, toc, projection, options = fixture()
                tree = html.fragment_fromstring(body, create_parent="main")
                headings = tree.xpath('.//section[@data-page="042"]/h2')
                if case == "missing": headings[0].getparent().remove(headings[0])
                if case == "extra": headings[0].getparent().append(copy.deepcopy(headings[0]))
                if case == "markup": headings[0][0].tag = "em"
                changed = "".join(html.tostring(node, encoding="unicode") for node in tree)
                with self.assertRaisesRegex(ValueError, "DOM count"):
                    self.project(changed, toc, projection, options)

    def test_other_structural_owner_is_rejected(self):
        body, toc, projection, options = fixture()
        options["display_roles"].append({"role": "heading_prose_split",
                                         "unit": options["display_roles"][0]["unit"],
                                         "heading_text": "Национальность:",
                                         "source_evidence": "fixture", "reason": "conflict"})
        with self.assertRaisesRegex(ValueError, "conflicts"):
            self.project(body, toc, projection, options)

    def test_existing_standalone_repeated_title_keeps_unselected_siblings(self):
        body, toc, projection, options = fixture()
        role = options["display_roles"][0]
        role.update(role="repeated_title", standalone_running_heading=True,
                    retained={key: projection["units"][1][key] for key in ("unit_id", "ru_sha256")})
        rendered, _, report = self.project(body, toc, projection, options)
        tree = html.fragment_fromstring(rendered, create_parent="main")
        self.assertEqual(len(tree.xpath('.//section[@data-page="042"]/h2')), 2)
        self.assertEqual(len(tree.xpath('.//section[@data-page="041"]/h2')), 1)
        self.assertEqual(report["standalone_running_headings"][0]["removed"], role["unit"])


if __name__ == "__main__":
    unittest.main()
