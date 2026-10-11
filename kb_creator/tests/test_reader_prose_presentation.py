"""Reviewed whole-heading demotion preserves prose and Word bookmarks."""
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

from lxml import etree, html
from translator.translator import markdown_to_review_html

from kb_creator.pipeline import five_step_docx, reader_options_rebind, reader_projection
from kb_creator.scripts.production_docx import bookmark_name
from kb_creator.tests.test_reader_whole_artifact import PDF_HASH, _unit, _write


FALSE_HEADING = "## Следователи, по той или иной причине, **вовлечены** в историю и читают [письмо](https://example.org)."


def fixture(root: Path):
    master = root / "language/MASTER_RU.md"
    strings = ["<!-- source-page-042 -->", "# Настоящая глава", FALSE_HEADING,
               "См. текст следователей.", "## Настоящий раздел", "Обычный соседний абзац."]
    units = [_unit(f"prose-{index}", value) for index, value in enumerate(strings)]
    bind = lambda index: {key: units[index][key] for key in ("unit_id", "ru_sha256")}
    master.parent.mkdir(parents=True, exist_ok=True)
    master.write_text("\n\n".join(strings) + "\n", encoding="utf-8", newline="\n")
    _write(master.parent / "ASSET_MANIFEST.json", {"assets": []})
    for name in ("MASTER_RU.manifest.json", "PROOFREAD_LEDGER.json", "INVENTORY.json"):
        _write(master.parent / name, {})
    projection = {"schema": "kb_creator.five_step_ru_projection.v3",
                  "master_en": {"path": "evidence/MASTER_EN.md", "bytes": 1, "sha256": "C" * 64},
                  "master_ru": {"path": "MASTER_RU.md", **reader_projection.identity(master)},
                  "unit_order": [unit["unit_id"] for unit in units], "units": units, "spans": []}
    projection["projection_sha256"] = reader_projection.seal(projection)
    projection_path = master.parent / "semantic_context/RU_PROJECTION.json"
    _write(projection_path, projection)
    decision = {"role": "prose_presentation", "unit": bind(2),
                "source_evidence": "N199 source42 visual review: one ordinary source paragraph",
                "reason": "preliminary false heading requires normal body presentation"}
    options = {"schema": reader_projection.SCHEMA,
               "master_ru": {"path": "MASTER_RU.md", **reader_projection.identity(master)},
               "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **reader_projection.identity(projection_path)},
               "source_toc": {"state": "absent", "source_pdf_sha256": PDF_HASH, "reason": "fixture source"},
               "body_links": [{"unit": bind(3), "target": bind(2), "text": "текст следователей",
                               "label": "текст следователей", "reason": "fixture exact incoming link"}],
               "asset_choices": [], "hit_points": {"presentation": "numeric"}, "display_roles": [decision]}
    options["options_sha256"] = reader_projection.seal(options)
    options_path = root / "options/reader-options.json"
    _write(options_path, options)
    return master, projection_path, options_path


class ProsePresentationTests(unittest.TestCase):
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

    def _change(self, mutate):
        options = json.loads(self.options.read_text(encoding="utf-8"))
        mutate(options)
        options.pop("options_sha256")
        options["options_sha256"] = reader_projection.seal(options)
        _write(self.options, options)

    def _build(self):
        with patch("kb_creator.pipeline.five_step_language.verify_language_result",
                   return_value={"state": "verified", "inputs": {"source_pdf": {"identity": {"sha256": PDF_HASH}}}}):
            return five_step_docx.build_docx_package(self.master, self.root / "package", title="Prose fixture",
                                                     reader_options=self.options)["manifest_path"].parent

    def test_exact_heading_becomes_prose_and_incoming_link_survives(self):
        body, toc, report = self._project()
        tree = html.fragment_fromstring(body, create_parent="main")
        paragraph = tree.xpath('.//section[@data-page="042"]/p[strong[contains(text(), "вовлечены")]]')[0]
        self.assertEqual(paragraph.text_content(), "Следователи, по той или иной причине, вовлечены в историю и читают письмо.")
        self.assertEqual(len(paragraph.xpath('./a[@href="https://example.org"]')), 1)
        self.assertEqual(len(tree.xpath('.//a[@href=$ref]', ref="#" + paragraph.get("id"))), 1)
        self.assertEqual([node.text_content() for node in tree.xpath('.//section[@data-page="042"]/h1 | .//section[@data-page="042"]/h2')],
                         ["Настоящая глава", "Настоящий раздел"])
        self.assertFalse(any("Следователи" in row["title"] for row in toc))
        self.assertFalse(tree.xpath('.//nav[@id="toc"]//a[@href=$ref]', ref="#" + paragraph.get("id")))
        self.assertEqual(report["display_roles"][0]["role"], "prose_presentation")

    def test_source_issue_target_is_order_independent(self):
        source = {"role": "source_issue_review_anchor", "issue_id": "prose-fixture",
                  "unit": {"unit_id": "prose-2", "ru_sha256": json.loads(self.projection.read_text(encoding="utf-8"))["units"][2]["ru_sha256"]},
                  "source_page": 42, "en_excerpt": "The investigators are", "source_evidence": "fixture source",
                  "reason": "review exact body paragraph", "placement": "first_visible_text_block_v1"}
        outputs = []
        for first in (False, True):
            self.master, self.projection, self.options = fixture(self.root / ("first" if first else "last"))
            self._change(lambda o: o.__setitem__("display_roles", [source, o["display_roles"][0]] if first
                                                          else [o["display_roles"][0], source]))
            outputs.append(self._project()[0])
        self.assertEqual(outputs[0], outputs[1])

    def test_real_docx_uses_normal_paragraph_and_preserves_inline_content(self):
        package = self._build()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"], "verified_pending_visual_review")
        body = html.fromstring((package / "internal.html").read_text(encoding="utf-8"))
        paragraph = body.xpath('.//section[@data-page="042"]/p[strong[contains(text(), "вовлечены")]]')[0]
        with zipfile.ZipFile(package / "docx/document.docx") as archive:
            xml = etree.fromstring(archive.read("word/document.xml"))
        word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        name = bookmark_name(paragraph.get("id"))
        marks = [mark for mark in xml.iter(f"{{{word}}}bookmarkStart") if mark.get(f"{{{word}}}name") == name]
        self.assertEqual(len(marks), 1)
        word_paragraph = next(node for node in marks[0].iterancestors() if node.tag == f"{{{word}}}p")
        styles = [node.get(f"{{{word}}}val") for node in word_paragraph.iter(f"{{{word}}}pStyle")]
        self.assertTrue(not styles or styles == ["Normal"])
        self.assertEqual("".join(node.text or "" for node in word_paragraph.iter(f"{{{word}}}t")), paragraph.text_content())
        self.assertTrue(any(True for _ in word_paragraph.iter(f"{{{word}}}b")))
        incoming = [node for node in xml.iter(f"{{{word}}}hyperlink")
                    if node.get(f"{{{word}}}anchor") == name]
        self.assertEqual(len(incoming), 1)
        for label, style in (("Настоящая глава", "Heading1"), ("Настоящий раздел", "Heading2")):
            heading = next(node for node in body.xpath('.//section[@data-page="042"]/*[self::h1 or self::h2]')
                           if node.text_content() == label)
            neighbor_name = bookmark_name(heading.get("id"))
            marker = next(node for node in xml.iter(f"{{{word}}}bookmarkStart")
                          if node.get(f"{{{word}}}name") == neighbor_name)
            neighbor = next(node for node in marker.iterancestors() if node.tag == f"{{{word}}}p")
            self.assertEqual([node.get(f"{{{word}}}val") for node in neighbor.iter(f"{{{word}}}pStyle")], [style])

    def test_stale_unsupported_and_conflicting_decisions_fail(self):
        cases = [
            ("extra", lambda o: o["display_roles"][0].update({"guess": True}), "exact reviewed fields"),
            ("stale", lambda o: o["display_roles"][0]["unit"].update({"ru_sha256": "0" * 64}), "preimage"),
            ("nonheading", lambda o: o["display_roles"][0].update({"unit": {key: json.loads(self.projection.read_text(encoding="utf-8"))["units"][3][key]
                                                                                 for key in ("unit_id", "ru_sha256")}}), "unstructured heading"),
            ("conflict", lambda o: o["display_roles"].append({"role": "heading_prose_split", "unit": copy.deepcopy(o["display_roles"][0]["unit"]),
                                                                "heading_text": "Следователи", "source_evidence": "fixture", "reason": "conflict"}), "conflicts"),
        ]
        for name, mutate, error in cases:
            with self.subTest(name=name):
                self.root = self.root / name
                self.master, self.projection, self.options = fixture(self.root)
                self._change(mutate)
                with self.assertRaisesRegex(ValueError, error):
                    self._project()

    def test_nested_or_ambiguous_heading_is_not_selected(self):
        for name, target, duplicate, split_parent, error in (
            ("nested", "> ## Внутренний заголовок", False, False, "unstructured heading"),
            ("ambiguous", "## Повтор заголовка", True, False, "exact HTML matches"),
            ("split_parent", "## Разбитый заголовок", False, True, "unsplit heading"),
        ):
            with self.subTest(name=name):
                texts = ["<!-- source-page-042 -->", "# Глава", target]
                if duplicate:
                    texts.append(target)
                units = [_unit(f"case-{index}", value) for index, value in enumerate(texts)]
                if split_parent:
                    child = _unit("case-child", "фрагмент")
                    child["parent_unit_id"] = "case-2"
                    units.append(child)
                binding = {key: units[2][key] for key in ("unit_id", "ru_sha256")}
                options = {"source_toc": {"state": "absent", "source_pdf_sha256": PDF_HASH,
                                          "reason": "fixture source"}, "body_links": [], "asset_choices": [],
                           "hit_points": {"presentation": "numeric"},
                           "display_roles": [{"role": "prose_presentation", "unit": binding,
                                              "source_evidence": "reviewed fixture", "reason": "test exact target"}]}
                body, toc, _ = markdown_to_review_html("\n\n".join(texts), source_path=Path("case.md"),
                                                       html_path=Path("case.html"), blockquote_heading_offset=0)
                with self.assertRaisesRegex(ValueError, error):
                    reader_projection.project_reader_html(body, toc, {"units": units}, options)

    def test_rebind_uses_existing_exact_unit_binding_rules(self):
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
        def rebind(name):
            with (patch.object(reader_options_rebind, "_projection", side_effect=projections),
                  patch.object(reader_options_rebind, "_same_assets")):
                return reader_options_rebind.rebind_reader_options(self.master.parent, current_root, self.options,
                                                                   self.root / name)
        self.assertEqual(rebind("rebound")["state"], "candidate_only")
        self.assertEqual(json.loads((self.root / "rebound/reader_options.json").read_text(encoding="utf-8"))["display_roles"][0]["role"],
                         "prose_presentation")
        new["units"][2]["ru_text"] += "!"
        new["units"][2]["ru_sha256"] = hashlib.sha256(new["units"][2]["ru_text"].encode()).hexdigest().upper()
        with self.assertRaisesRegex(ValueError, "affected by changed unit"):
            rebind("changed-unit")


if __name__ == "__main__":
    unittest.main()
