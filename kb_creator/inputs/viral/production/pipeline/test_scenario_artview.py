from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from kb_creator.scripts import scenario_artview


REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE = REPO_ROOT / "kb_creator/reference/viral/artview_review_policy_v2.json"


class ScenarioArtViewTests(unittest.TestCase):
    def test_html_bundle_keeps_export_newline_inside_javascript_string(self) -> None:
        manifest = {
            "rows": [],
            "scenario_id": "viral",
            "bindings": {},
            "candidate_files_inventory_sha256": "B" * 64,
            "decision_contract": {"binding_sources": []},
        }

        html = scenario_artview.html_bundle(manifest, "A" * 64)

        self.assertIn('JSON.stringify(documentValue,null,2)+"\\n"', html)
        self.assertNotIn('JSON.stringify(documentValue,null,2)+"\n"', html)
        self.assertIn("Предварительный макет", html)
        self.assertIn("Обтекать обычным текстом", html)
        self.assertIn("Разрешить обтекание таблицами", html)
        self.assertIn('id="exportAccepted" disabled', html)
        self.assertIn('image.style.marginLeft="";image.style.marginRight=""', html)
        self.assertIn('.layout-grid .control:first-child{grid-column:1/-1}', html)
        self.assertIn('grid-template-columns:repeat(4,minmax(0,1fr))', html)
        self.assertIn('direct_xobject:"Из PDF напрямую"', html)
        self.assertIn('embedded_page_composite_crop:"Crop из PDF-композита"', html)
        self.assertIn('direct_composite_parts:"Композиция PDF-объектов"', html)
        self.assertIn('row.alternatives.some(item=>directKinds.has(item.kind))', html)
        self.assertIn('function missingCard(title,text)', html)
        self.assertIn('PDF XObject ${locator.object_id||"?"}', html)

    def test_bbox_iou_and_safe_bundle_paths(self) -> None:
        self.assertEqual(scenario_artview.bbox_iou([0, 0, 10, 10], [0, 0, 10, 10]), 1.0)
        self.assertAlmostEqual(scenario_artview.bbox_iou([0, 0, 10, 10], [5, 0, 15, 10]), 1 / 3)
        self.assertEqual(scenario_artview.safe_relative("assets/current/a.jpg"), "assets/current/a.jpg")
        for unsafe in ("C:/a.jpg", "../a.jpg", "/a.jpg", "https://example.test/a.jpg"):
            with self.assertRaises(ValueError):
                scenario_artview.safe_relative(unsafe)

    def test_direct_occurrence_allows_one_tight_container_but_not_page_background(self) -> None:
        target = [2.448, 36.432, 607.716, 386.496]
        background = {"x0": -9.0, "top": -9.0, "x1": 612.12, "bottom": 801.0, "name": "R13"}
        native_art = {"x0": -1.08, "top": -1.08, "x1": 612.12, "bottom": 469.081, "name": "R148"}

        occurrence, mode, _iou, _delta, warnings = scenario_artview.select_direct_occurrence(
            [background, native_art], target, 612.0, 792.0
        )

        self.assertEqual(occurrence["name"], "R148")
        self.assertEqual(mode, "containing_region")
        self.assertEqual(warnings, ["direct_containing_region_review_required"])
        missing, mode, _iou, _delta, warnings = scenario_artview.select_direct_occurrence(
            [background], target, 612.0, 792.0
        )
        self.assertIsNone(missing)
        self.assertIsNone(mode)
        self.assertEqual(warnings, ["direct_no_unique_occurrence"])

    def test_direct_occurrence_allows_reviewable_fuller_art_but_not_page_background(self) -> None:
        target = [279.684, 28.512, 604.656, 545.112]
        fuller = {"x0": 0.0, "top": -1.08, "x1": 613.2, "bottom": 545.4, "name": "R180"}
        background = {"x0": -1.08, "top": -1.08, "x1": 613.2, "bottom": 793.08, "name": "R1"}

        occurrence, mode, _iou, _delta, warnings = scenario_artview.select_direct_occurrence(
            [background, fuller], target, 612.0, 792.0
        )

        self.assertEqual(occurrence["name"], "R180")
        self.assertEqual(mode, "containing_fuller_art")
        self.assertEqual(warnings, ["direct_fuller_art_review_required"])

    def test_cached_image_copy_requires_matching_recorded_identity(self) -> None:
        with tempfile.TemporaryDirectory() as previous_name, tempfile.TemporaryDirectory() as candidate_name:
            previous = Path(previous_name)
            candidate = Path(candidate_name)
            relative = "context/page-006.jpg"
            source = previous / relative
            source.parent.mkdir(parents=True)
            scenario_artview.Image.new("RGB", (8, 5), "green").save(source, "JPEG")
            record = scenario_artview.image_record(source, relative)

            copied = scenario_artview.copy_cached_image(previous, candidate, record, relative)

            self.assertEqual(copied, record)
            self.assertTrue((candidate / relative).is_file())
            broken = copy.deepcopy(record)
            broken["sha256"] = "0" * 64
            self.assertIsNone(scenario_artview.copy_cached_image(previous, candidate, broken, relative))

    def test_markdown_reference_region_join_is_fail_closed(self) -> None:
        asset = {
            "source_page": 8,
            "binary": {"sha256": "ABC"},
            "provenance": {"kind": "markdown_image_reference"},
        }
        manifest = {"ABC": [{"view": "v", "source_path": "images/a.jpg"}]}
        comparison = {"views": {"v": {"blocks": [{"type": "image", "source_page": 8, "raw_index": 7, "bbox": [1, 2, 3, 4], "assets": ["images/a.jpg"]}]}}}
        region, warnings = scenario_artview.recover_region(asset, manifest, comparison)
        self.assertEqual(warnings, [])
        self.assertEqual(region["bbox"], [1.0, 2.0, 3.0, 4.0])
        comparison["views"]["v"]["blocks"].append(copy.deepcopy(comparison["views"]["v"]["blocks"][0]))
        region, warnings = scenario_artview.recover_region(asset, manifest, comparison)
        self.assertIsNone(region)
        self.assertEqual(warnings, ["markdown_reference_comparison_matches_2"])

    def test_candidate_id_is_deterministic(self) -> None:
        first = scenario_artview.make_candidate_id("asset", "direct_xobject", {"page": 1}, {"raw": True}, "ABC")
        second = scenario_artview.make_candidate_id("asset", "direct_xobject", {"page": 1}, {"raw": True}, "ABC")
        changed = scenario_artview.make_candidate_id("asset", "direct_xobject", {"page": 2}, {"raw": True}, "ABC")
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)

    def test_presentation_defaults_are_role_aware_and_validation_is_strict(self) -> None:
        self.assertEqual(
            scenario_artview.default_presentation("body"),
            {"width_percent": 25, "alignment": "right", "wrap_text": True, "wrap_tables": False},
        )
        self.assertEqual(scenario_artview.default_presentation("handout")["width_percent"], 80)
        self.assertEqual(scenario_artview.default_presentation("pregen")["width_percent"], 100)
        self.assertEqual(
            scenario_artview.presentation_findings(
                {"width_percent": 25, "alignment": "right", "wrap_text": True, "wrap_tables": True},
                "asset",
            ),
            [],
        )
        self.assertEqual(
            scenario_artview.presentation_findings(
                {"width_percent": 25, "alignment": "center", "wrap_text": True, "wrap_tables": False},
                "asset",
            )[0]["code"],
            "center_alignment_cannot_wrap",
        )

    def test_production_asset_states_distinguish_included_and_suppressed(self) -> None:
        included = "a" * 64
        suppressed = "b" * 64
        states = scenario_artview.production_asset_states(
            {"files": [{"path": f"assets/{included}.jpg"}]},
            {
                "suppressed_redundant_text_facsimiles": [f"{suppressed}.jpg"],
                "suppressed_duplicate_narrative_art": None,
            },
        )

        self.assertEqual(states[f"viral-accepted-{included}"]["status"], "included")
        self.assertEqual(states[f"viral-accepted-{suppressed}"]["status"], "excluded")

    def test_real_viral_bundle_contract_and_decision_validation(self) -> None:
        profile = scenario_artview.read_json(PROFILE)
        root = scenario_artview.resolve_repo(profile["output_root"]) / "candidate"
        manifest = scenario_artview.read_json(root / "candidate_manifest.json")
        qa = scenario_artview.read_json(root / "qa.json")
        self.assertEqual(qa["status"], "pass")
        self.assertEqual(len(manifest["rows"]), 94)
        self.assertEqual(manifest["summary"]["region_rows"], 84)
        self.assertEqual(manifest["summary"]["full_page_rows"], 10)
        self.assertEqual(manifest["summary"]["derived_candidates"], 84)
        self.assertEqual(manifest["summary"]["direct_candidates"], 84)
        self.assertEqual(manifest["summary"]["direct_single_candidates"], 78)
        self.assertEqual(manifest["summary"]["embedded_page_composite_candidates"], 5)
        self.assertEqual(manifest["summary"]["direct_composite_candidates"], 1)
        self.assertEqual([row["page"] for row in manifest["skipped_source_pages"]], [123, 124])
        self.assertTrue(all("exclude" in row["allowed_binary_decisions"] for row in manifest["rows"]))
        self.assertTrue(all(set(row["presentation_defaults"]) == {
            "width_percent", "alignment", "wrap_text", "wrap_tables"
        } for row in manifest["rows"]))
        self.assertEqual(sum(row["production_state"]["status"] == "excluded" for row in manifest["rows"]), 6)
        introduction = next(row for row in manifest["rows"] if row["anchor"] == "viral-introduction")
        self.assertEqual(
            {candidate["kind"] for candidate in introduction["alternatives"]},
            {"direct_xobject", "derived_page_crop"},
        )
        direct = next(candidate for candidate in introduction["alternatives"] if candidate["kind"] == "direct_xobject")
        self.assertEqual(direct["source_locator"]["object_id"], 1068)
        self.assertEqual(direct["source_locator"]["match_mode"], "containing_region")
        self.assertTrue(direct["recipe"]["no_mineru_binary"])
        self.assertEqual(direct["binary"]["colorspace"], "RGB")
        self.assertEqual(direct["source_binary"]["colorspace"], "CMYK")
        self.assertNotEqual(direct["binary"]["path"], direct["source_binary"]["path"])
        self.assertIn("invert PDF CMYK", direct["recipe"]["selectable_emitted_transform"])
        self.assertIn("direct_containing_region_review_required", introduction["warnings"])
        credits = next(row for row in manifest["rows"] if row["anchor"] == "viral-credits")
        credits_direct = next(candidate for candidate in credits["alternatives"] if candidate["kind"] == "direct_xobject")
        self.assertEqual(credits_direct["variant"], "masked")
        self.assertEqual({item["role"] for item in credits_direct["source_components"]}, {"base", "soft_mask"})
        marco = next(row for row in manifest["rows"] if row["anchor"] == "viral-spektral-krew-marco-proudfoot-maglioni")
        marco_direct = next(candidate for candidate in marco["alternatives"] if candidate["kind"] == "direct_xobject")
        self.assertEqual(marco_direct["source_locator"]["object_id"], 930)
        self.assertEqual(marco_direct["source_locator"]["match_mode"], "containing_fuller_art")
        self.assertEqual(marco_direct["variant"], "fuller")
        enoch = next(row for row in manifest["rows"] if row["anchor"] == "viral-spektral-krew-enoch-jeremiah-eakins")
        enoch_direct = next(candidate for candidate in enoch["alternatives"] if candidate["kind"] == "direct_xobject")
        self.assertEqual(enoch_direct["source_locator"]["object_id"], 935)
        self.assertEqual(enoch_direct["variant"], "masked")
        self.assertIn("direct_smask_resampled_one_pixel", enoch["warnings"])
        page_composites = {
            row["anchor"]: next(
                candidate for candidate in row["alternatives"]
                if candidate["kind"] == "embedded_page_composite_crop"
            )["source_locator"]["object_id"]
            for row in manifest["rows"]
            if any(candidate["kind"] == "embedded_page_composite_crop" for candidate in row["alternatives"])
        }
        self.assertEqual(page_composites, {
            "viral-one-night-in-perla": 1091,
            "viral-one-night-in-perla-signs-and-portents": 1139,
            "viral-one-night-in-perla-burning-of-the-disease": 1143,
            "viral-epilogue-cinematic-ending": 1110,
            "viral-epilogue-expanded-ending": 1127,
        })
        mythos = next(row for row in manifest["rows"] if row["anchor"] == "viral-appendix-new-mythos-horrors")
        mythos_direct = next(candidate for candidate in mythos["alternatives"] if candidate["kind"] == "direct_composite_parts")
        self.assertEqual(set(mythos_direct["source_locator"]["object_ids"]), {1389, 1394})
        template_path = root / "artview-decisions.template.json"
        template = scenario_artview.read_json(template_path)
        self.assertEqual(template["state"], "draft")
        self.assertEqual(len(template["decisions"]), 94)
        self.assertTrue(all(item["binary"]["choice"] is None for item in template["decisions"]))
        self.assertTrue(all(item["reviewed"] is False for item in template["decisions"]))
        self.assertEqual(scenario_artview.validate_decisions(PROFILE, template_path, False)["status"], "pass")
        bindings = scenario_artview.decision_bindings(
            manifest,
            scenario_artview.sha256_file(root / "candidate_manifest.json"),
        )
        decisions = {
            "schema": scenario_artview.DECISION_SCHEMA,
            "scenario_id": "viral",
            "state": "accepted",
            "bindings": bindings,
            "decisions": [{
                "asset_id": row["asset_id"],
                "binary": {"choice": "keep_current", "candidate_id": None},
                "presentation": row["presentation_defaults"],
                "reviewed": True,
                "notes": "",
            } for row in manifest["rows"]],
        }
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "decisions.json"
            path.write_text(json.dumps(decisions), encoding="utf-8")
            self.assertEqual(scenario_artview.validate_decisions(PROFILE, path, True)["status"], "pass")
            decisions["bindings"]["master_ru_sha256"] = "0" * 64
            path.write_text(json.dumps(decisions), encoding="utf-8")
            self.assertEqual(scenario_artview.validate_decisions(PROFILE, path, True)["status"], "fail")
            decisions["bindings"] = bindings
            decisions["decisions"][0]["presentation"]["width_percent"] = 5
            path.write_text(json.dumps(decisions), encoding="utf-8")
            result = scenario_artview.validate_decisions(PROFILE, path, True)
            self.assertEqual(result["status"], "fail")
            self.assertIn("presentation_width_invalid", [item["code"] for item in result["findings"]])


if __name__ == "__main__":
    unittest.main()
