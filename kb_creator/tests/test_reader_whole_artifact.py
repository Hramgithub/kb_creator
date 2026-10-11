"""Reviewed whole-unit source furniture and retained facsimile contract probes."""
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
from PIL import Image
from translator.translator import markdown_to_review_html

from kb_creator.pipeline import five_step_docx, reader_duplicate_text, reader_options_rebind, reader_projection
from kb_creator.scripts.production_docx import bookmark_name


PDF_HASH = "A" * 64
CLIP_A = "content\nrents\nrticle\nWikipedia\nstore"
CLIP_B = "ontents [hide]\nsonal life\neer\nography\nography\nrences\nmal Links"


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _unit(uid, text):
    return {"unit_id": uid, "source_hash": "B" * 64, "parent_unit_id": None,
            "part_index": None, "part_count": None, "ru_text": text,
            "ru_sha256": _hash(text.encode("utf-8"))}


def _binding(unit, ordinal=0):
    return {"unit_id": unit["unit_id"], "ru_sha256": unit["ru_sha256"], "match_ordinal": ordinal}


def fixture(root: Path, *, with_duplicate: bool = False, equivalent_cohort: bool = False,
            internal_spaces: bool = False):
    master = root / "language/MASTER_RU.md"
    image_ref = "assets/sidebar.png"
    image_text = f"![Факсимиле]({image_ref})"
    rows = [_unit("p53", "<!-- source-page-053 -->"), _unit("heading53", "# Сцена"),
            _unit("folio", "84"), _unit("stat", "СИЛ 84"),
            _unit("table", "| Показатель | Значение |\n| --- | --- |\n| СИЛ | 84 |"),
            _unit("p197", "<!-- source-page-197 -->"), _unit("heading197", "# Статья"),
            _unit("facsimile", image_text), _unit("clip_a", CLIP_A), _unit("clip_b", CLIP_B),
            _unit("article", "Текст статьи сохранён. [Внешний источник](https://example.org)."),
            _unit("warning", "Предупреждение источника сохранено."),
            _unit("p198", "<!-- source-page-198 -->"), _unit("other_image", image_text),
            _unit("other_text", "Полезный текст другой страницы.")]
    if equivalent_cohort:
        rows[9] = _unit("clip_b", CLIP_A.replace("\n", " "))
    if internal_spaces:
        rows[8] = _unit("clip_a", "СЕНСОРНАЯ ПУТАНИЦА  МИ-ГО")
    if with_duplicate:
        rows.append(_unit("other_text_duplicate", "Полезный текст другой страницы."))
    master.parent.mkdir(parents=True, exist_ok=True)
    master.write_text("\n\n".join(row["ru_text"] for row in rows) + "\n", encoding="utf-8", newline="\n")
    original = master.parent / image_ref
    original.parent.mkdir(exist_ok=True)
    Image.new("RGB", (120, 80), "orange").save(original)
    _write(master.parent / "ASSET_MANIFEST.json", {"assets": [{"path": image_ref, **reader_projection.identity(original)}]})
    for name in ("MASTER_RU.manifest.json", "PROOFREAD_LEDGER.json", "INVENTORY.json"):
        _write(master.parent / name, {})
    projection = {"schema": "kb_creator.five_step_ru_projection.v3",
                  "master_en": {"path": "evidence/MASTER_EN.md", "bytes": 1, "sha256": "C" * 64},
                  "master_ru": {"path": "MASTER_RU.md", **reader_projection.identity(master)},
                  "unit_order": [row["unit_id"] for row in rows], "units": rows, "spans": []}
    projection["projection_sha256"] = reader_projection.seal(projection)
    projection_path = master.parent / "semantic_context/RU_PROJECTION.json"
    _write(projection_path, projection)
    options_root = root / "options"
    furniture_visual = options_root / "evidence/page053.png"
    furniture_visual.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (100, 100), "white").save(furniture_visual)
    artwork_visual = options_root / "evidence/facsimile.png"
    artwork_visual.write_bytes(original.read_bytes())
    def evidence(path, verdict, bbox):
        return {"approval": "reviewed", "reviewer": "fixture reviewer", "source_pdf_sha256": PDF_HASH,
                "source_visual": {"path": path.relative_to(options_root).as_posix(), **reader_projection.identity(path)},
                "source_region": {"coordinate_space": "source_visual_pixels_top_left_v1", "bbox": bbox},
                "visual_verdict": verdict, "rationale": "fixture original-source comparison"}
    common = {"role": "omit_source_artifact", "text_policy": "reviewed_whole_plain_block_v2",
              "source_page": 197, "reason": "reviewed clipped facsimile interface"}
    choices = [{"role": "omit_source_artifact", "classification": "source_furniture_text",
                "text_policy": "reviewed_whole_plain_block_v2", "unit": _binding(rows[2]),
                "source_page": 53, "furniture_kind": "page_number", "extracted_as_ocr_fragment": False,
                "expected_raw_text": "84",
                "source_evidence": evidence(furniture_visual, "whole_unit_is_running_furniture", [4, 4, 30, 30]),
                "reason": "reviewed printed folio"}]
    cohort = None
    if equivalent_cohort:
        cohort = {"source_page": 197, "members": [
            {**_binding(unit, ordinal), "expected_raw_text": unit["ru_text"]}
            for ordinal, unit in enumerate((rows[8], rows[9]))]}
    for ordinal, unit in enumerate((rows[8], rows[9])):
        choices.append({**common, "classification": "duplicate_text_represented_by_retained_artwork",
                        "unit": _binding(unit, ordinal if equivalent_cohort else 0),
                        "expected_raw_text": unit["ru_text"],
                        "retained_image_unit": _binding(rows[7]), "retained_image_reference": image_ref,
                        "retained_image_identity": reader_projection.identity(original),
                        "source_evidence": evidence(artwork_visual, "whole_unit_is_facsimile_interface_text", [2, 2, 70, 60]),
                        **({"rendered_equivalent_cohort": copy.deepcopy(cohort)} if cohort else {})})
    if with_duplicate:
        duplicate_visual = options_root / "evidence/page198.png"
        Image.new("RGB", (100, 100), "white").save(duplicate_visual)
        retained_text = rows[-2]
        choices.append({"role": "omit_extraction_duplicate_text", "unit": _binding(rows[-1], 1),
                        "retained": _binding(retained_text, 0),
                        "retained_raw_span": {"start": 0, "end": len(retained_text["ru_text"])},
                        "source_page": 198,
                        "source_evidence": {"finding_id": "fixture-p198", "approval": "reviewed",
                                            "reviewer": "fixture reviewer", "source_pdf_sha256": PDF_HASH,
                                            "source_visual": {"path": "evidence/page198.png", **reader_projection.identity(duplicate_visual)},
                                            "observed_source_occurrences": 1},
                        "reason": "reviewed fixture extraction duplicate"})
    options = {"schema": reader_projection.SCHEMA,
               "master_ru": {"path": "MASTER_RU.md", **reader_projection.identity(master)},
               "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **reader_projection.identity(projection_path)},
               "source_toc": {"state": "absent", "source_pdf_sha256": PDF_HASH, "reason": "fixture source"},
               "body_links": [], "asset_choices": [], "hit_points": {"presentation": "numeric"},
               "display_roles": choices}
    options["options_sha256"] = reader_projection.seal(options)
    options_path = options_root / "reader-options.json"
    _write(options_path, options)
    return master, projection_path, options_path


def artwork_transit_fixture(root: Path, *, image_before_left: bool = False):
    master, projection_path, options_path = fixture(root)
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    rows = projection["units"]
    left = _unit("left_prose", "Перед заметкой")
    image_index = next(index for index, row in enumerate(rows) if row["unit_id"] == "facsimile")
    rows.insert(image_index + (1 if image_before_left else 0), left)
    master.write_text("\n\n".join(row["ru_text"] for row in rows) + "\n", encoding="utf-8", newline="\n")
    projection["master_ru"] = {"path": "MASTER_RU.md", **reader_projection.identity(master)}
    projection["unit_order"] = [row["unit_id"] for row in rows]
    projection.pop("projection_sha256")
    projection["projection_sha256"] = reader_projection.seal(projection)
    _write(projection_path, projection)
    by_id = {row["unit_id"]: row for row in rows}
    bind = lambda uid: {key: by_id[uid][key] for key in ("unit_id", "ru_sha256")}
    start = next(index for index, row in enumerate(rows) if row["unit_id"] == "left_prose")
    end = next(index for index, row in enumerate(rows) if row["unit_id"] == "article")
    reflow = {"role": "interrupted_prose_reflow", "units": [bind("left_prose"), bind("article")],
              "intervening_units": [bind(row["unit_id"]) for row in rows[start + 1:end]],
              "join_mode": "space", "source_evidence": "reviewed source with retained facsimile",
              "reason": "restore one sentence around the exact reviewed screenshot"}
    options = json.loads(options_path.read_text(encoding="utf-8"))
    options["master_ru"] = {"path": "MASTER_RU.md", **reader_projection.identity(master)}
    options["ru_projection"] = {"path": "semantic_context/RU_PROJECTION.json",
                                **reader_projection.identity(projection_path)}
    options["display_roles"].insert(0, reflow)
    options.pop("options_sha256")
    options["options_sha256"] = reader_projection.seal(options)
    _write(options_path, options)
    return master, projection_path, options_path


class WholeArtifactTests(unittest.TestCase):
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

    def _project(self):
        projection = json.loads(self.projection.read_text(encoding="utf-8"))
        options = reader_projection.load_options(self.options, self.master, self.projection)
        body, toc, _ = markdown_to_review_html(self.master.read_text(encoding="utf-8"),
                                               source_path=self.master, html_path=self.master.parent / "internal.html",
                                               blockquote_heading_offset=0)
        return reader_projection.project_reader_html(body, toc, projection, options,
                                                     options_path=self.options, master_root=self.master.parent)

    def _build(self):
        with patch("kb_creator.pipeline.five_step_language.verify_language_result",
                   return_value={"state": "verified", "inputs": {"source_pdf": {"identity": {"sha256": PDF_HASH}}}}):
            result = five_step_docx.build_docx_package(self.master, self.root / "package", title="Artifact fixture",
                                                        reader_options=self.options)
        return result["manifest_path"].parent

    def _reseal(self, package):
        path = package / "DOCX_MANIFEST.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["docx"].update(five_step_docx._identity(package / "docx/document.docx", package))
        manifest["inventory"] = five_step_docx._inventory(package)
        manifest.pop("manifest_sha256")
        manifest["manifest_sha256"] = _hash(five_step_docx._canonical(manifest))
        _write(path, manifest)

    def _mutate_docx(self, package, change):
        docx = package / "docx/document.docx"
        with zipfile.ZipFile(docx) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()}
        change(parts)
        with zipfile.ZipFile(docx, "w") as archive:
            for name, data in parts.items():
                archive.writestr(name, data)
        self._reseal(package)

    def test_guarded_artwork_transit_preserves_omissions_image_and_join_in_docx(self):
        self.root = self.root / "transit"
        self.master, self.projection, self.options = artwork_transit_fixture(self.root)
        rendered, _, report = self._project()
        self.assertIn("Перед заметкой Текст статьи сохранён", html.fragment_fromstring(
            rendered, create_parent="main").text_content())
        self.assertNotIn("Wikipedia store", rendered)
        self.assertEqual(len(report["reflow_dependencies"]), 1)
        self.assertEqual(len(report["retained_image_dependencies"]), 2)
        package = self._build()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                         "verified_pending_visual_review")
        with zipfile.ZipFile(package / "docx/document.docx") as archive:
            original = (self.master.parent / "assets/sidebar.png").read_bytes()
            self.assertTrue(any(archive.read(name) == original for name in archive.namelist()
                                if name.startswith("word/media/")))

    def test_guarded_artwork_transit_rejects_unrelated_or_incomplete_routes(self):
        base = self.root
        for name in ("altered_image", "forbidden_role", "endpoint", "absent_guard", "orphan_image"):
            with self.subTest(name=name):
                self.root = base / name
                self.master, self.projection, self.options = artwork_transit_fixture(
                    self.root, image_before_left=name == "orphan_image")
                projection = json.loads(self.projection.read_text(encoding="utf-8"))
                by_id = {row["unit_id"]: row for row in projection["units"]}
                bind = lambda uid: {key: by_id[uid][key] for key in ("unit_id", "ru_sha256")}
                if name == "altered_image":
                    (self.master.parent / "assets/sidebar.png").write_bytes(b"altered image")
                elif name == "forbidden_role":
                    self._change(lambda options: options["body_links"].append({
                        "unit": bind("article"), "target": bind("facsimile"),
                        "text": "статьи", "label": "статьи", "reason": "forbidden extra route"}))
                elif name == "endpoint":
                    self._change(lambda options: options["display_roles"][0].update({
                        "units": [bind("clip_a"), bind("article")],
                        "intervening_units": [bind("clip_b")]}))
                elif name == "absent_guard":
                    self._change(lambda options: options["display_roles"][0].pop("join_mode"))
                with self.assertRaises(ValueError):
                    self._project()

    def test_exact_internal_ascii_spaces_survive_artifact_roundtrip(self):
        self.root = self.root / "internal-spaces"
        self.master, self.projection, self.options = fixture(self.root, internal_spaces=True)
        rendered, _, report = self._project()
        self.assertEqual(len(report["omitted_artifacts"]), 3)
        self.assertNotIn("СЕНСОРНАЯ ПУТАНИЦА", rendered)
        package = self._build()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                         "verified_pending_visual_review")
        self.assertEqual(reader_duplicate_text._rendered("СЕНСОРНАЯ ПУТАНИЦА  МИ-ГО", artifact=True),
                         ("СЕНСОРНАЯ ПУТАНИЦА  МИ-ГО",))
        for bad in (" СЕНСОРНАЯ ПУТАНИЦА  МИ-ГО", "СЕНСОРНАЯ ПУТАНИЦА  МИ-ГО ",
                    "\tСЕНСОРНАЯ ПУТАНИЦА  МИ-ГО", "  СЕНСОРНАЯ ПУТАНИЦА",
                    "СЕНСОРНАЯ ПУТАНИЦА   ", "СЕНСОРНАЯ **ПУТАНИЦА**  МИ-ГО"):
            with self.subTest(raw=bad):
                with self.assertRaises(ValueError):
                    reader_duplicate_text._rendered(bad, artifact=True)

    def test_whole_furniture_and_multiline_facsimile_projection(self):
        body, _, report = self._project()
        self.assertEqual(len(report["omitted_artifacts"]), 3)
        self.assertEqual({row["source_page"] for row in report["duplicate_page_witness"]}, {53, 197})
        self.assertEqual(len(report["retained_image_dependencies"]), 2)
        self.assertNotIn("ontents [hide]", body)
        self.assertIn("Текст статьи сохранён", body)
        self.assertIn("СИЛ 84", body)
        self.assertIn("Полезный текст другой страницы", body)

    def test_real_docx_reopen_and_image_occurrence(self):
        package = self._build()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"], "verified_pending_visual_review")
        report = json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))
        self.assertEqual(len(report["omitted_artifacts"]), 3)
        self.assertTrue((package / "evidence/facsimile.png").is_file())
        self.assertEqual(len({row["anchor"] for row in report["retained_image_dependencies"]}), 1)
        with zipfile.ZipFile(package / "docx/document.docx") as archive:
            xml = archive.read("word/document.xml").decode("utf-8")
        self.assertIn("Текст статьи сохранён", xml)
        self.assertIn("СИЛ 84", xml)

    def test_rendered_equivalent_artifact_cohort_requires_complete_review_and_reopens_docx(self):
        self.root = self.root / "equivalent"
        self.master, self.projection, self.options = fixture(self.root, equivalent_cohort=True)
        rendered, _, report = self._project()
        self.assertEqual(len(report["omitted_artifacts"]), 3)
        self.assertNotIn("content rents rticle Wikipedia store", rendered)
        self.assertIn("Текст статьи сохранён", rendered)
        package = self._build()
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"],
                         "verified_pending_visual_review")
        with zipfile.ZipFile(package / "docx/document.docx") as archive:
            xml = archive.read("word/document.xml").decode("utf-8")
            self.assertIn("Текст статьи сохранён", xml)
            self.assertNotIn("Wikipedia store", xml)
            self.assertTrue(any(archive.read(name) == (self.master.parent / "assets/sidebar.png").read_bytes()
                                for name in archive.namelist() if name.startswith("word/media/")))

        base = self.root
        for name, mutate in (
            ("missing_witness", lambda role: role.pop("rendered_equivalent_cohort")),
            ("missing_member", lambda role: role["rendered_equivalent_cohort"]["members"].pop()),
            ("extra_member", lambda role: role["rendered_equivalent_cohort"]["members"].append(
                copy.deepcopy(role["rendered_equivalent_cohort"]["members"][0]))),
            ("swapped_members", lambda role: role["rendered_equivalent_cohort"]["members"].reverse()),
            ("wrong_hash", lambda role: role["rendered_equivalent_cohort"]["members"][1].update(ru_sha256="0" * 64)),
            ("wrong_raw", lambda role: role["rendered_equivalent_cohort"]["members"][1].update(expected_raw_text="wrong")),
            ("wrong_page", lambda role: role["rendered_equivalent_cohort"].update(source_page=198)),
            ("wrong_ordinal", lambda role: role["unit"].update(match_ordinal=1)),
        ):
            with self.subTest(name=name):
                self.root = base / name
                self.master, self.projection, self.options = fixture(self.root, equivalent_cohort=True)
                self._change(lambda options: mutate(options["display_roles"][1]))
                with self.assertRaises(ValueError):
                    self._project()

        for name in ("extra_rendered", "inline_rendered", "structured_rendered"):
            with self.subTest(name=name):
                self.root = base / name
                self.master, self.projection, self.options = fixture(self.root, equivalent_cohort=True)
                projection = json.loads(self.projection.read_text(encoding="utf-8"))
                options = reader_projection.load_options(self.options, self.master, self.projection)
                body, toc, _ = markdown_to_review_html(self.master.read_text(encoding="utf-8"),
                                                       source_path=self.master,
                                                       html_path=self.master.parent / "internal.html",
                                                       blockquote_heading_offset=0)
                tree = html.fragment_fromstring(body, create_parent="main")
                section = tree.xpath('.//section[@data-page="197"]')[0]
                candidate = next(node for node in section.xpath("./p")
                                 if "Wikipedia store" in node.text_content())
                if name == "extra_rendered":
                    candidate.addnext(copy.deepcopy(candidate))
                elif name == "inline_rendered":
                    candidate.text = None
                    etree.SubElement(candidate, "strong").text = "content rents rticle Wikipedia store"
                else:
                    wrapper = etree.Element("blockquote")
                    candidate.addprevious(wrapper)
                    wrapper.append(candidate)
                with self.assertRaisesRegex(ValueError, "cohort"):
                    reader_projection.project_reader_html(html.tostring(tree, encoding="unicode"), toc,
                                                          projection, options, options_path=self.options,
                                                          master_root=self.master.parent)

    def test_rebind_rejects_changed_peer_in_reviewed_cohort(self):
        self.root = self.root / "cohort-rebind"
        self.master, self.projection, self.options = fixture(self.root, equivalent_cohort=True)
        old = json.loads(self.projection.read_text(encoding="utf-8"))
        old["source_spans"] = {"sha256": "F" * 64}
        new = copy.deepcopy(old)
        current_root = self.root / "current"
        shutil.copytree(self.master.parent, current_root)
        current_master = current_root / "MASTER_RU.md"
        current_projection = current_root / "semantic_context/RU_PROJECTION.json"
        peer = next(row for row in new["units"] if row["unit_id"] == "clip_b")
        peer["ru_text"] += " changed"
        peer["ru_sha256"] = _hash(peer["ru_text"].encode())
        def projections(root):
            return ((old, self.master, self.projection) if root == self.master.parent
                    else (new, current_master, current_projection))
        with (patch.object(reader_options_rebind, "_projection", side_effect=projections),
              patch.object(reader_options_rebind, "_same_assets")):
            with self.assertRaisesRegex(ValueError, "cohort changed operand clip_b"):
                reader_options_rebind.rebind_reader_options(self.master.parent, current_root, self.options,
                                                           self.root / "rebound")

    def test_combined_retained_text_and_artifact_witness(self):
        self.root = self.root / "combined"
        self.master, self.projection, self.options = fixture(self.root, with_duplicate=True)
        package = self._build()
        report = json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))
        self.assertEqual(len(report["omitted_text_duplicates"]), 1)
        self.assertEqual(len(report["omitted_artifacts"]), 3)
        self.assertEqual({row["source_page"] for row in report["duplicate_page_witness"]}, {53, 197, 198})
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"], "verified_pending_visual_review")

    def test_legacy_single_line_artwork_joins_shared_docx_witness(self):
        replacement = "Single source artwork text"
        self.master.write_text(self.master.read_text(encoding="utf-8").replace(CLIP_A, replacement).replace(
            "![Факсимиле](assets/sidebar.png)\n\nПолезный текст другой страницы.",
            "Полезный текст другой страницы."),
                               encoding="utf-8", newline="\n")
        projection = json.loads(self.projection.read_text(encoding="utf-8"))
        projection["units"] = [row for row in projection["units"] if row["unit_id"] != "other_image"]
        projection["unit_order"].remove("other_image")
        unit = next(row for row in projection["units"] if row["unit_id"] == "clip_a")
        unit["ru_text"] = replacement
        unit["ru_sha256"] = _hash(replacement.encode())
        projection["master_ru"] = {"path": "MASTER_RU.md", **reader_projection.identity(self.master)}
        projection.pop("projection_sha256")
        projection["projection_sha256"] = reader_projection.seal(projection)
        _write(self.projection, projection)
        options = json.loads(self.options.read_text(encoding="utf-8"))
        options["master_ru"] = {"path": "MASTER_RU.md", **reader_projection.identity(self.master)}
        options["ru_projection"] = {"path": "semantic_context/RU_PROJECTION.json",
                                    **reader_projection.identity(self.projection)}
        options["display_roles"][1] = {
            "role": "omit_source_artifact", "classification": "duplicate_text_represented_by_retained_artwork",
            "unit": _binding(unit), "retained_image_reference": "assets/sidebar.png",
            "source_evidence": "reviewed source page", "reason": "legacy exact single line",
        }
        options.pop("options_sha256")
        options["options_sha256"] = reader_projection.seal(options)
        _write(self.options, options)
        package = self._build()
        report = json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))
        legacy = next(row for row in report["omitted_artifacts"] if row.get("text_policy") is None)
        self.assertEqual(legacy["actual_source_page"], 197)
        self.assertNotIn(replacement, next(row for row in report["duplicate_page_witness"]
                                           if row["source_page"] == 197)["expected_paragraphs"])
        self.assertEqual(five_step_docx.verify_docx_package(package)["status"], "verified_pending_visual_review")

    def test_rebind_carries_exact_evidence_and_rejects_changed_operands(self):
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
        with (patch.object(reader_options_rebind, "_projection", side_effect=projections),
              patch.object(reader_options_rebind, "_same_assets")):
            reader_options_rebind.rebind_reader_options(self.master.parent, current_root, self.options,
                                                       self.root / "rebound")
        for name in ("page053.png", "facsimile.png"):
            self.assertEqual((self.root / "rebound/evidence" / name).read_bytes(),
                             (self.options.parent / "evidence" / name).read_bytes())
        for uid in ("clip_a", "facsimile"):
            new = copy.deepcopy(old)
            unit = next(row for row in new["units"] if row["unit_id"] == uid)
            unit["ru_text"] += "!"
            unit["ru_sha256"] = _hash(unit["ru_text"].encode())
            with (patch.object(reader_options_rebind, "_projection", side_effect=projections),
                  patch.object(reader_options_rebind, "_same_assets")):
                with self.assertRaisesRegex(ValueError, "changed operand"):
                    reader_options_rebind.rebind_reader_options(self.master.parent, current_root, self.options,
                                                               self.root / f"changed-{uid}")

    def test_reopen_rejects_lost_retained_image_relationship(self):
        package = self._build()
        word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        drawing = "http://schemas.openxmlformats.org/drawingml/2006/main"
        def change(parts):
            xml = etree.fromstring(parts["word/document.xml"])
            name = bookmark_name(json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))["retained_image_dependencies"][0]["anchor"])
            paragraph = next(p for p in xml.iter(f"{{{word}}}p")
                             if any(b.get(f"{{{word}}}name") == name for b in p.iter(f"{{{word}}}bookmarkStart")))
            blip = next(paragraph.iter(f"{{{drawing}}}blip"))
            blip.getparent().remove(blip)
            parts["word/document.xml"] = etree.tostring(xml, encoding="UTF-8", xml_declaration=True)
        self._mutate_docx(package, change)
        with self.assertRaisesRegex(five_step_docx.FiveStepDocxError, "image occurrence"):
            five_step_docx.verify_docx_package(package)

    def test_reopen_rejects_retained_image_crop(self):
        package = self._build()
        word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        drawing = "http://schemas.openxmlformats.org/drawingml/2006/main"
        def change(parts):
            xml = etree.fromstring(parts["word/document.xml"])
            name = bookmark_name(json.loads((package / "READER_PROJECTION.json").read_text(encoding="utf-8"))["retained_image_dependencies"][0]["anchor"])
            paragraph = next(p for p in xml.iter(f"{{{word}}}p")
                             if any(b.get(f"{{{word}}}name") == name for b in p.iter(f"{{{word}}}bookmarkStart")))
            blip = next(paragraph.iter(f"{{{drawing}}}blip"))
            blip.getparent().append(etree.Element(f"{{{drawing}}}srcRect", l="1000"))
            parts["word/document.xml"] = etree.tostring(xml, encoding="UTF-8", xml_declaration=True)
        self._mutate_docx(package, change)
        with self.assertRaisesRegex(five_step_docx.FiveStepDocxError, "cropped"):
            five_step_docx.verify_docx_package(package)

    def test_reopen_rejects_restored_furniture_or_lost_article(self):
        for replacement in ("84", ""):
            self.root = self.root / ("restored" if replacement else "lost")
            self.master, self.projection, self.options = fixture(self.root)
            package = self._build()
            word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            def change(parts):
                xml = etree.fromstring(parts["word/document.xml"])
                node = next(node for node in xml.iter(f"{{{word}}}t")
                            if node.text and ("Текст статьи сохранён" if not replacement else "СИЛ 84") in node.text)
                if replacement:
                    paragraph = next(parent for parent in node.iterancestors() if parent.tag == f"{{{word}}}p")
                    restored = etree.Element(f"{{{word}}}p")
                    etree.SubElement(etree.SubElement(restored, f"{{{word}}}r"), f"{{{word}}}t").text = replacement
                    paragraph.addnext(restored)
                else:
                    node.text = ""
                parts["word/document.xml"] = etree.tostring(xml, encoding="UTF-8", xml_declaration=True)
            self._mutate_docx(package, change)
            with self.assertRaisesRegex(five_step_docx.FiveStepDocxError, "paragraph stream"):
                five_step_docx.verify_docx_package(package)

    def test_exact_text_and_evidence_rejections(self):
        self._change(lambda o: o["display_roles"][1].__setitem__("expected_raw_text", CLIP_A + "!"))
        with self.assertRaisesRegex(ValueError, "preimage"):
            self._project()
        self.master, self.projection, self.options = fixture(self.root)
        self._change(lambda o: o["display_roles"][0]["source_evidence"]["source_region"].__setitem__("bbox", [0, 0, 101, 20]))
        with self.assertRaisesRegex(ValueError, "source region"):
            self._project()
        self.master, self.projection, self.options = fixture(self.root)
        self._change(lambda o: o["display_roles"][1]["unit"].__setitem__("match_ordinal", 1))
        with self.assertRaisesRegex(ValueError, "ordinal"):
            self._project()

    def test_unreviewed_material_and_protected_target_survive(self):
        self._change(lambda o: o.__setitem__("display_roles", []))
        body, _, report = self._project()
        self.assertIn("ontents [hide]", body)
        self.assertEqual(report["omitted_artifacts"], [])
        self.master, self.projection, self.options = fixture(self.root)
        self._change(lambda o: o["body_links"].append({
            "unit": o["display_roles"][1]["unit"], "target": o["display_roles"][1]["unit"],
            "text": "content", "label": "content", "reason": "fixture protected target"}))
        with self.assertRaisesRegex(ValueError, "protected ownership"):
            self._project()

    def test_stale_visual_and_original_image_are_rejected(self):
        visual = self.options.parent / "evidence/facsimile.png"
        visual.write_bytes(b"altered evidence")
        with self.assertRaisesRegex(ValueError, "source visual identity"):
            self._project()
        self.master, self.projection, self.options = fixture(self.root)
        original = self.master.parent / "assets/sidebar.png"
        original.write_bytes(b"altered original")
        with self.assertRaisesRegex(ValueError, "original image|byte identity|source visual"):
            self._project()


if __name__ == "__main__":
    unittest.main()
