"""End-to-end fixture for exact retained-text duplicate reader omissions."""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from lxml import etree
from PIL import Image
from translator.translator import markdown_to_review_html

from kb_creator.pipeline import five_step_docx, reader_projection
from kb_creator.pipeline import reader_options_rebind
from kb_creator.scripts.production_docx import bookmark_name


STATS = "СИЛ 50 ВЫН 90 ТЕЛ 35 ИНТ 80 МОЩ 90  \nЛВК 80 НАР 40 ОБР 80 РАС 0 ПЗ 12"
LINE1 = "СИЛ 50 ВЫН 90 ТЕЛ 35 ИНТ 80 МОЩ 90"
LINE2 = "ЛВК 80 НАР 40 ОБР 80 РАС 0 ПЗ 12"
PDF_HASH = "A" * 64


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _unit(uid: str, text: str):
    return {"unit_id": uid, "source_hash": "B" * 64, "parent_unit_id": None,
            "part_index": None, "part_count": None, "ru_text": text,
            "ru_sha256": _hash(text.encode("utf-8"))}


def _binding(row, ordinal):
    return {"unit_id": row["unit_id"], "ru_sha256": row["ru_sha256"], "match_ordinal": ordinal}


def fixture(root: Path, *, statblock: bool = True, with_asset: bool = False):
    master = root / "language" / "MASTER_RU.md"
    rows = [_unit("page85", "<!-- source-page-085 -->"), _unit("heading", "# Ребекка"),
            _unit("kept", STATS), _unit("whole", STATS), _unit("line1", LINE1),
            _unit("line2", LINE2), _unit("page86", "<!-- source-page-086 -->"),
            _unit("other", STATS)]
    if with_asset:
        rows.append(_unit("image", "![Карта](assets/map.png)"))
    master.parent.mkdir(parents=True, exist_ok=True)
    master.write_text("\n\n".join(row["ru_text"] for row in rows) + "\n", encoding="utf-8", newline="\n")
    assets = []
    if with_asset:
        original = master.parent / "assets/map.png"
        original.parent.mkdir()
        Image.new("RGB", (20, 20), "red").save(original)
        assets.append({"path": "assets/map.png", **reader_projection.identity(original)})
    for name in ("ASSET_MANIFEST.json", "MASTER_RU.manifest.json", "PROOFREAD_LEDGER.json", "INVENTORY.json"):
        _write(master.parent / name, {"assets": assets} if name == "ASSET_MANIFEST.json" else {})
    projection = {"schema": "kb_creator.five_step_ru_projection.v3",
                  "master_en": {"path": "evidence/MASTER_EN.md", "bytes": 1, "sha256": "C" * 64},
                  "master_ru": {"path": "MASTER_RU.md", **reader_projection.identity(master)},
                  "unit_order": [row["unit_id"] for row in rows], "units": rows, "spans": []}
    if statblock:
        projection["spans"] = [{"span_id": "rebecca.stats", "semantic_kind": "statblock", "source_span_id": "source.rebecca.stats",
                                "unit_ids": ["kept"], "start": {"unit_id": "kept", "char_offset": 0},
                                "end": {"unit_id": "kept", "char_offset": len(STATS)}, "source_sha256": "D" * 64}]
    projection["projection_sha256"] = reader_projection.seal(projection)
    projection_path = master.parent / "semantic_context" / "RU_PROJECTION.json"
    _write(projection_path, projection)
    visual = root / "options" / "evidence" / "source-page085.png"
    visual.parent.mkdir(parents=True, exist_ok=True)
    visual.write_bytes(b"reviewed source-page visual fixture")
    evidence = {"finding_id": "fixture-p85", "approval": "reviewed", "reviewer": "fixture reviewer",
                "source_pdf_sha256": PDF_HASH, "source_visual": {"path": "evidence/source-page085.png", **reader_projection.identity(visual)},
                "observed_source_occurrences": 1}
    decisions = []
    for omitted, ordinal, span in ((rows[3], 1, (0, len(STATS))),
                                   (rows[4], 0, (0, len(LINE1))),
                                   (rows[5], 0, (len(LINE1) + 3, len(STATS)))):
        decisions.append({"role": "omit_extraction_duplicate_text", "unit": _binding(omitted, ordinal),
                          "retained": _binding(rows[2], 0),
                          "retained_raw_span": {"start": span[0], "end": span[1]},
                          "source_page": 85, "source_evidence": evidence,
                          "reason": "reviewed extraction-only duplicate in fixture"})
    options = {"schema": reader_projection.SCHEMA,
               "master_ru": {"path": "MASTER_RU.md", **reader_projection.identity(master)},
               "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **reader_projection.identity(projection_path)},
               "source_toc": {"state": "absent", "source_pdf_sha256": PDF_HASH, "reason": "reviewed fixture source"},
               "body_links": [], "asset_choices": [], "hit_points": {"presentation": "numeric"},
               "display_roles": decisions}
    if with_asset:
        selected = root / "options/selected/map.png"
        selected.parent.mkdir()
        Image.new("RGB", (20, 20), "blue").save(selected)
        options["asset_choices"] = [{"original_ref": "assets/map.png", "original": reader_projection.identity(original),
                                     "selected_ref": "selected/map.png", "selected": reader_projection.identity(selected),
                                     "provenance": "reviewed fixture", "reason": "reviewed fixture"}]
    options["options_sha256"] = reader_projection.seal(options)
    options_path = root / "options" / "reader-options.json"
    _write(options_path, options)
    return master, projection_path, options_path


def _project(master: Path, projection_path: Path, options_path: Path):
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    options = reader_projection.load_options(options_path, master, projection_path)
    body, toc, _ = markdown_to_review_html(master.read_text(encoding="utf-8"),
                                           source_path=master, html_path=master.parent / "internal.html", blockquote_heading_offset=0)
    return reader_projection.project_reader_html(body, toc, projection, options, options_path=options_path)


class DuplicateTextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.master, self.projection, self.options = fixture(self.root)

    def _change(self, mutate):
        value = json.loads(self.options.read_text(encoding="utf-8"))
        mutate(value)
        value.pop("options_sha256")
        value["options_sha256"] = reader_projection.seal(value)
        _write(self.options, value)

    def _build_package(self):
        with patch("kb_creator.pipeline.five_step_language.verify_language_result",
                   return_value={"state": "verified", "inputs": {"source_pdf": {"identity": {"sha256": PDF_HASH}}}}):
            result = five_step_docx.build_docx_package(self.master, self.root / "package", title="Reader duplicate fixture",
                                                        reader_options=self.options)
        return result["manifest_path"].parent

    def _reseal_package(self, package):
        manifest_path = package / "DOCX_MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["docx"].update(five_step_docx._identity(package / "docx/document.docx", package))
        manifest["inventory"] = five_step_docx._inventory(package)
        manifest.pop("manifest_sha256")
        manifest["manifest_sha256"] = _hash(five_step_docx._canonical(manifest))
        _write(manifest_path, manifest)

    def _edit_word_xml(self, package, change):
        docx = package / "docx/document.docx"
        with zipfile.ZipFile(docx) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()}
        xml = etree.fromstring(parts["word/document.xml"])
        change(xml)
        parts["word/document.xml"] = etree.tostring(xml, encoding="UTF-8", xml_declaration=True)
        with zipfile.ZipFile(docx, "w") as archive:
            for name, data in parts.items():
                archive.writestr(name, data)
        self._reseal_package(package)

    def test_exact_three_omissions_and_page_ownership(self):
        body, _, report = _project(self.master, self.projection, self.options)
        self.assertEqual(len(report["omitted_text_duplicates"]), 3)
        self.assertEqual([row["unit"]["unit_id"] for row in report["omitted_text_duplicates"]], ["whole", "line1", "line2"])
        self.assertEqual(body.count("СИЛ 50 ВЫН 90"), 2)  # retained p85 and untouched p86
        self.assertEqual(report["duplicate_page_witness"][0]["source_page"], 85)
        self.assertEqual(len(report["duplicate_page_witness"][0]["expected_paragraphs"]), 2)  # heading and canonical stats

    def test_repetition_without_reviewed_decision_is_preserved(self):
        self._change(lambda o: o["display_roles"].clear())
        body, _, report = _project(self.master, self.projection, self.options)
        self.assertEqual(body.count("СИЛ 50 ВЫН 90"), 4)
        self.assertEqual(report["omitted_text_duplicates"], [])

    def test_malformed_exact_coverage_and_ordinals_fail(self):
        for field, value in (("end", 68), ("start", True), ("start", 1), ("end", 70)):
            with self.subTest(field=field, value=value):
                self._change(lambda o: o["display_roles"][0]["retained_raw_span"].__setitem__(field, value))
                with self.assertRaisesRegex(ValueError, "raw interval"):
                    _project(self.master, self.projection, self.options)
                self.master, self.projection, self.options = fixture(self.root)
        self._change(lambda o: o["display_roles"][0]["unit"].__setitem__("match_ordinal", 0))
        with self.assertRaisesRegex(ValueError, "ordinal"):
            _project(self.master, self.projection, self.options)

    def test_changed_digits_script_spacing_and_hard_break_fail(self):
        changes = (STATS.replace("50", "51", 1), STATS.replace("СИЛ", "CИЛ", 1),
                   STATS.replace("МОЩ 90", "МОЩ  90", 1), STATS.replace("  \n", "\n", 1),
                   STATS.replace("ПЗ 12", "ПЗ 12.", 1))
        for index, changed in enumerate(changes):
            with self.subTest(index=index):
                self.master, self.projection, self.options = fixture(self.root)
                projection = json.loads(self.projection.read_text(encoding="utf-8"))
                projection["units"][3]["ru_text"] = changed
                projection["units"][3]["ru_sha256"] = _hash(changed.encode("utf-8"))
                projection["projection_sha256"] = reader_projection.seal({key: value for key, value in projection.items()
                                                                           if key != "projection_sha256"})
                _write(self.projection, projection)
                self._change(lambda o: (o["ru_projection"].update(reader_projection.identity(self.projection)),
                                        o["display_roles"][0]["unit"].__setitem__("ru_sha256", projection["units"][3]["ru_sha256"])))
                with self.assertRaisesRegex(ValueError, "raw interval"):
                    _project(self.master, self.projection, self.options)

    def test_conflicts_and_source_occurrences_fail(self):
        self._change(lambda o: o["display_roles"][0]["source_evidence"].__setitem__("observed_source_occurrences", 2))
        with self.assertRaisesRegex(ValueError, "one-occurrence"):
            _project(self.master, self.projection, self.options)
        self.master, self.projection, self.options = fixture(self.root)
        self._change(lambda o: o["display_roles"].append(copy.deepcopy(o["display_roles"][0])))
        with self.assertRaisesRegex(ValueError, "ownership"):
            _project(self.master, self.projection, self.options)

    def test_source_visual_identity_and_retained_target_route(self):
        visual = self.options.parent / "evidence/source-page085.png"
        visual.write_bytes(b"changed visual")
        with self.assertRaisesRegex(ValueError, "visual identity"):
            _project(self.master, self.projection, self.options)
        self.master, self.projection, self.options = fixture(self.root)
        self._change(lambda o: o["body_links"].append({"unit": {k: v for k, v in o["display_roles"][2]["unit"].items() if k != "match_ordinal"},
                                                       "target": {k: v for k, v in o["display_roles"][0]["retained"].items() if k != "match_ordinal"},
                                                       "text": "ЛВК", "label": "ЛВК", "reason": "fixture"}))
        with self.assertRaisesRegex(ValueError, "conflicts"):
            _project(self.master, self.projection, self.options)  # the link source is omitted
        self.master, self.projection, self.options = fixture(self.root)
        heading = json.loads(self.projection.read_text(encoding="utf-8"))["units"][1]
        self._change(lambda o: o["body_links"].append({"unit": {key: heading[key] for key in ("unit_id", "ru_sha256")},
                                                       "target": {key: o["display_roles"][0]["retained"][key] for key in ("unit_id", "ru_sha256")},
                                                       "text": "Ребекка", "label": "Ребекка", "reason": "fixture"}))
        body, _, report = _project(self.master, self.projection, self.options)
        self.assertEqual(len(report["links"]), 1)
        self.assertIn('id="reader-kept"', body)

    def test_existing_reviewed_word_join_still_works(self):
        texts = ["<!-- source-page-001 -->", "Он **подслушива**", "*ет* разговор."]
        units = [_unit(f"word-{index}", value) for index, value in enumerate(texts)]
        body, toc, _ = markdown_to_review_html("\n\n".join(texts), source_path=Path("word.md"),
                                               html_path=Path("word.html"), blockquote_heading_offset=0)
        options = {"source_toc": {"state": "absent", "source_pdf_sha256": PDF_HASH, "reason": "fixture"},
                   "body_links": [], "asset_choices": [], "hit_points": {"presentation": "numeric"},
                   "display_roles": [{"role": "paragraph_continuation",
                                      "units": [{key: row[key] for key in ("unit_id", "ru_sha256")} for row in units[1:]],
                                      "join_mode": "word", "source_evidence": "reviewed", "reason": "fixture"}]}
        projected, _, _ = reader_projection.project_reader_html(body, toc, {"units": units}, options)
        self.assertIn("подслушива", projected)
        self.assertIn("ет", projected)
        self.assertEqual(etree.HTML(projected).xpath("string(//p[1])"), "Он подслушивает разговор.")

    def test_rebind_copies_evidence_and_rejects_changed_duplicate_operand(self):
        old = json.loads(self.projection.read_text(encoding="utf-8"))
        old["source_spans"] = {"sha256": "F" * 64}
        new = copy.deepcopy(old)
        prior_root = self.master.parent
        current_root = self.root / "current"
        current_root.mkdir()
        current_master = current_root / "MASTER_RU.md"
        current_master.write_bytes(self.master.read_bytes())
        current_projection = current_root / "semantic_context/RU_PROJECTION.json"
        def write_current():
            new["projection_sha256"] = reader_projection.seal({key: value for key, value in new.items()
                                                                 if key != "projection_sha256"})
            _write(current_projection, new)
        write_current()
        def projections(root):
            return (old, self.master, self.projection) if root == prior_root else (new, current_master, current_projection)
        with (patch.object(reader_options_rebind, "_projection", side_effect=projections),
              patch.object(reader_options_rebind, "_same_assets")):
            reader_options_rebind.rebind_reader_options(prior_root, current_root, self.options, self.root / "rebound")
        self.assertEqual((self.root / "rebound/evidence/source-page085.png").read_bytes(),
                         (self.options.parent / "evidence/source-page085.png").read_bytes())
        new["units"][3]["ru_text"] += "."
        new["units"][3]["ru_sha256"] = _hash(new["units"][3]["ru_text"].encode())
        write_current()
        reviewed = self.root / "reviewed.json"
        _write(reviewed, [{"unit_id": "whole", "prior_ru_sha256": old["units"][3]["ru_sha256"],
                           "current_ru_sha256": new["units"][3]["ru_sha256"], "reason": "fixture changed unit"}])
        with (patch.object(reader_options_rebind, "_projection", side_effect=projections),
              patch.object(reader_options_rebind, "_same_assets")):
            with self.assertRaisesRegex(ValueError, "changed operand"):
                reader_options_rebind.rebind_reader_options(prior_root, current_root, self.options,
                                                            self.root / "changed-rebound", reviewed)
        new = copy.deepcopy(old)
        new["units"][1]["ru_text"] = STATS
        new["units"][1]["ru_sha256"] = _hash(STATS.encode())
        write_current()
        with (patch.object(reader_options_rebind, "_projection", side_effect=projections),
              patch.object(reader_options_rebind, "_same_assets")):
            with self.assertRaisesRegex(ValueError, "cohort changed"):
                reader_options_rebind.rebind_reader_options(prior_root, current_root, self.options,
                                                            self.root / "cohort-rebound")

    def test_real_docx_build_reopen_and_word_tamper(self):
        package = self._build_package()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"], "verified_pending_visual_review")
        manifest = json.loads((package / "DOCX_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["reader_projection"]["omitted_text_duplicates"]), 3)
        self.assertTrue((package / "evidence/source-page085.png").is_file())
        ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        with zipfile.ZipFile(package / "docx/document.docx") as archive:
            original_xml = etree.fromstring(archive.read("word/document.xml"))
        paragraphs = original_xml.findall(f".//{{{ns}}}body/{{{ns}}}p")
        self.assertEqual(sum("СИЛ 50 ВЫН 90" in "".join(paragraph.itertext()) for paragraph in paragraphs), 2)
        def alter(xml):
            target = next(paragraph for paragraph in xml.findall(f".//{{{ns}}}body/{{{ns}}}p")
                          if "СИЛ 50 ВЫН 90" in "".join(paragraph.itertext()))
            etree.SubElement(etree.SubElement(target, f"{{{ns}}}r"), f"{{{ns}}}t").text = " FORGED"
        self._edit_word_xml(package, alter)
        with self.assertRaisesRegex(five_step_docx.FiveStepDocxError, "paragraph stream"):
            five_step_docx.verify_docx_package(package)

    def test_retained_owner_native_link_survives_and_reopen_rejects_loss(self):
        word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        for mutation in ("target", "link", "retarget"):
            with self.subTest(mutation=mutation):
                self.root = self.root / mutation
                self.master, self.projection, self.options = fixture(self.root)
                units = json.loads(self.projection.read_text(encoding="utf-8"))["units"]
                self._change(lambda o: o["body_links"].append({
                    "unit": {key: units[1][key] for key in ("unit_id", "ru_sha256")},
                    "target": {key: units[2][key] for key in ("unit_id", "ru_sha256")},
                    "text": "Ребекка", "label": "Ребекка", "reason": "retained owner native link fixture",
                }))
                package = self._build_package()
                self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                                 "verified_pending_visual_review")
                def alter(xml):
                    target_name = bookmark_name("reader-kept")
                    if mutation == "target":
                        start = next(node for node in xml.iter(f"{{{word}}}bookmarkStart")
                                     if node.get(f"{{{word}}}name") == target_name)
                        ident = start.get(f"{{{word}}}id")
                        start.getparent().remove(start)
                        end = next(node for node in xml.iter(f"{{{word}}}bookmarkEnd")
                                   if node.get(f"{{{word}}}id") == ident)
                        end.getparent().remove(end)
                    else:
                        link = next(node for node in xml.iter(f"{{{word}}}hyperlink")
                                    if node.get(f"{{{word}}}anchor") == target_name)
                        if mutation == "retarget":
                            link.set(f"{{{word}}}anchor", bookmark_name("page-085"))
                        else:
                            parent = link.getparent()
                            at = parent.index(link)
                            for child in list(link):
                                parent.insert(at, child)
                                at += 1
                            parent.remove(link)
                self._edit_word_xml(package, alter)
                with self.assertRaises(five_step_docx.FiveStepDocxError):
                    five_step_docx.verify_docx_package(package)

    def test_reopen_rejects_restored_duplicate_and_boundary_loss(self):
        package = self._build_package()
        ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        def restore(xml):
            target = next(paragraph for paragraph in xml.findall(f".//{{{ns}}}body/{{{ns}}}p")
                          if "СИЛ 50 ВЫН 90" in "".join(paragraph.itertext()))
            duplicate = copy.deepcopy(target)
            for bookmark in list(duplicate.iter(f"{{{ns}}}bookmarkStart")) + list(duplicate.iter(f"{{{ns}}}bookmarkEnd")):
                bookmark.getparent().remove(bookmark)
            target.addnext(duplicate)
        self._edit_word_xml(package, restore)
        with self.assertRaisesRegex(five_step_docx.FiveStepDocxError, "paragraph stream"):
            five_step_docx.verify_docx_package(package)
        # Rebuild in another fresh temporary fixture for the separate boundary mutation.
        other = self.root / "second"
        master, _, options = fixture(other)
        self.root, self.master, self.options = other, master, options
        package = self._build_package()
        def remove_boundary(xml):
            target = next(node for node in xml.iter(f"{{{ns}}}bookmarkStart")
                          if node.get(f"{{{ns}}}name") == bookmark_name("page-085"))
            target.getparent().remove(target)
        self._edit_word_xml(package, remove_boundary)
        with self.assertRaisesRegex(five_step_docx.FiveStepDocxError, "bookmark"):
            five_step_docx.verify_docx_package(package)

    def test_reopen_rejects_forged_reader_count_and_evidence_drift(self):
        package = self._build_package()
        manifest_path = package / "DOCX_MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["reader_projection"]["omitted_text_duplicates"].pop()
        _write(package / "READER_PROJECTION.json", manifest["reader_projection"])
        manifest["inventory"] = five_step_docx._inventory(package)
        manifest["manifest_sha256"] = _hash(five_step_docx._canonical({key: value for key, value in manifest.items() if key != "manifest_sha256"}))
        _write(manifest_path, manifest)
        with self.assertRaisesRegex(five_step_docx.FiveStepDocxError, "replay"):
            five_step_docx.verify_docx_package(package)
        other = self.root / "third"
        master, _, options = fixture(other)
        self.root, self.master, self.options = other, master, options
        package = self._build_package()
        (package / "evidence/source-page085.png").write_bytes(b"different visual bytes")
        self._reseal_package(package)
        with self.assertRaisesRegex(five_step_docx.FiveStepDocxError, "visual identity"):
            five_step_docx.verify_docx_package(package)

    def test_real_docx_replay_with_selected_reader_asset(self):
        self.root = self.root / "asset-case"
        self.master, self.projection, self.options = fixture(self.root, with_asset=True)
        package = self._build_package()
        self.assertTrue((package / "selected/map.png").is_file())
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"], "verified_pending_visual_review")


if __name__ == "__main__":
    unittest.main()
