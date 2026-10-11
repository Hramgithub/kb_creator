from __future__ import annotations

import copy
import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from jsonschema import Draft202012Validator

from kb_creator.scripts import scenario_artview, scenario_artview_apply


SAFE_V3_PATHS = (
    "profile.json",
    "assets/map-01.jpg",
    "кисти/карта 01.webp",
    "a.b/c-d_1.png",
)
UNSAFE_V3_PATHS = (
    "",
    "/abs",
    "\\abs",
    "C:/x",
    "C:\\x",
    "//server/share",
    "\\\\server\\share",
    ".",
    "..",
    "../x",
    "a/../x",
    "./x",
    "a/./x",
    "x/./y",
    "x/../y",
    "x/..",
    "a//b",
    "a/",
    "a\\b",
    "file:stream",
    "a.json:stream",
    "https://example.test/image.png",
    "https://host/x",
    " leading.png",
    "trailing.png ",
    "a./b",
    "a /b",
    "a/trail.",
    "a/trail ",
    "CON",
    "con.txt",
    "aux/image.png",
    "a/COM1.json",
    "images/LPT9.webp",
    "NUL",
    "bad\x00path",
    "bad\tpath",
    "bad\npath",
    "bad\x01path",
)


def v3_profile_schema() -> dict[str, object]:
    path = Path(__file__).resolve().parents[1] / "contracts" / "scenario_artview_profile.v3.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def identity(path: Path, root: Path) -> dict[str, object]:
    return {"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)}


def image_identity(path: Path, root: Path) -> dict[str, object]:
    return {
        **identity(path, root),
        "media_type": "image/png",
        "dimensions": {"width": 16, "height": 12},
    }


def seal(value: dict[str, object], key: str) -> dict[str, object]:
    result = {name: item for name, item in value.items() if name != key}
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    result[key] = hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()
    return result


class ScenarioArtViewV3Tests(unittest.TestCase):
    def test_rebind_v4_decisions_preserves_exact_pdf_derived_review_graph(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            source_pdf = root / "source.pdf"
            Image.new("RGB", (40, 30), (10, 20, 30)).save(source_pdf, "PDF")
            source_identity = root / "SOURCE_IDENTITY.json"
            source_identity.write_text(json.dumps({
                "source": {"bytes": source_pdf.stat().st_size, "sha256": sha(source_pdf), "page_count": 1},
            }), encoding="utf-8")
            input_records = {}
            for name in ("master_ru", "master_ru_acceptance", "master_ru_asset_manifest", "reconstruction_inventory"):
                path = root / f"{name}.json"
                path.write_text("{}", encoding="utf-8")
                input_records[name] = identity(path, root)
            input_records.update({
                "source_pdf": identity(source_pdf, root),
                "source_identity": identity(source_identity, root),
            })

            def candidate(name: str) -> tuple[Path, Path]:
                profile_path = root / f"{name}-profile.json"
                profile = {
                    "schema": scenario_artview.PROFILE_SCHEMA_V4,
                    "scenario_id": "sample", "output_root": f"{name}-run",
                    "inputs": copy.deepcopy(input_records),
                    "render": {"dpi": 150, "format": "png"},
                }
                profile_path.write_text(json.dumps(profile), encoding="utf-8")
                candidate_root = root / f"{name}-run" / "candidate"
                current = candidate_root / "assets" / "current" / "cover.png"
                context = candidate_root / "context" / "cover.png"
                current.parent.mkdir(parents=True); context.parent.mkdir(parents=True)
                Image.new("RGB", (16, 12), (1, 2, 3)).save(current, "PNG")
                Image.new("RGB", (16, 12), (1, 2, 3)).save(context, "PNG")
                inventory_doc, inventory_sha = scenario_artview.inventory(candidate_root)
                scenario_artview.write_json(candidate_root / "candidate_files.inventory.json", {
                    "schema": "kb_creator.scenario_artview_candidate_files.v1", **inventory_doc,
                })
                row = {
                    "asset_id": "pdf-page-001-cover", "review_id": "pdf-page-001-cover",
                    "placement_id": "source-cover-page-001", "anchor": "source-page-001",
                    "label": "Source page 001 cover", "source_page": 1,
                    "source_region": "full_page", "group": "cover", "semantic_role": "cover",
                    "placement_target": "source_page_cover", "required": True,
                    "provenance_kind": "clean_page_render", "component_raw_ids": ["raw-1"],
                    "current": scenario_artview.image_record(current, "assets/current/cover.png"),
                    "context": scenario_artview.image_record(context, "context/cover.png"),
                    "alternatives": [], "allowed_binary_decisions": ["keep_current"],
                    "presentation_defaults": {"width_percent": 100, "alignment": "center", "wrap_text": False, "wrap_tables": False},
                }
                manifest = {
                    "schema": scenario_artview.CANDIDATE_SCHEMA_V4, "scenario_id": "sample",
                    "state": "candidate_needs_user_decisions",
                    "bindings": {"profile": identity(profile_path, root), **copy.deepcopy(input_records)},
                    "derived_expected": {"review_rows": 1, "raw_objects": 1, "technical_raw_objects": 0, "source_pages": 1},
                    "rows": [row], "candidate_files_inventory_sha256": inventory_sha,
                    "decision_contract": {
                        "schema": scenario_artview.DECISION_SCHEMA_V4,
                        "binding_sources": ["profile", "master_ru", "master_ru_acceptance", "master_ru_asset_manifest", "reconstruction_inventory", "source_pdf", "source_identity"],
                        "accepted_requires_all_reviewed": True,
                    },
                }
                manifest_path = candidate_root / "candidate_manifest.json"
                scenario_artview.write_json(manifest_path, manifest)
                return profile_path, manifest_path

            source_profile, source_manifest = candidate("source")
            target_profile, target_manifest = candidate("target")
            manifest = json.loads(source_manifest.read_text(encoding="utf-8"))
            decisions = scenario_artview.seal_v3_decisions({
                "schema": scenario_artview.DECISION_SCHEMA_V4, "scenario_id": "sample",
                "state": "accepted", "bindings": scenario_artview.decision_bindings(manifest, sha(source_manifest)),
                "decisions": [{
                    "asset_id": "pdf-page-001-cover", "binary": {"choice": "keep_current", "candidate_id": None},
                    "presentation": {"width_percent": 100, "alignment": "center", "wrap_text": False, "wrap_tables": False},
                    "reviewed": True, "notes": "",
                }],
                "review": {"state": "closed", "reviewed_count": 1, "unresolved_asset_ids": []},
            })
            source_decisions = root / "source-decisions.json"
            scenario_artview.write_json(source_decisions, decisions)
            destination = root / "rebound-decisions.json"

            result = scenario_artview.rebind_decisions(
                source_profile.relative_to(root), source_manifest.relative_to(root), root,
                source_decisions.relative_to(root), target_profile.relative_to(root),
                target_manifest.relative_to(root), root, destination.relative_to(root),
            )

            self.assertEqual(result["status"], "pass")
            rebound = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(rebound["decisions"], decisions["decisions"])
            self.assertNotEqual(rebound["bindings"], decisions["bindings"])
            self.assertEqual(
                scenario_artview.validate_v4_decisions(
                    target_profile, destination, True,
                    target_manifest.relative_to(root), root,
                )["status"],
                "pass",
            )

    def test_v4_profile_is_discovery_only_and_required_cover_cannot_close_excluded(self) -> None:
        """v4 has no hand-authored reader rows and protects the cover decision."""
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            # A raster-backed PDF is enough to exercise the raw-object ledger.
            source_pdf = root / "source.pdf"
            Image.new("RGB", (40, 30), (10, 20, 30)).save(source_pdf, "PDF")
            source_identity = root / "SOURCE_IDENTITY.json"
            source_identity.write_text(json.dumps({"source": {"bytes": source_pdf.stat().st_size, "sha256": sha(source_pdf), "page_count": 1}}), encoding="utf-8")
            placeholders = {}
            for name in ("master_ru", "master_ru_acceptance", "master_ru_asset_manifest"):
                path = root / f"{name}.json"; path.write_text("{}", encoding="utf-8"); placeholders[name] = identity(path, root)
            decisions_root = root / "evidence" / "review" / "pages"; decisions_root.mkdir(parents=True)
            page_decision = decisions_root / "page-001.json"; page_decision.write_text(json.dumps({"source_page": 1, "semantic_role": "cover"}), encoding="utf-8")
            reconstruction_manifest = root / "RECONSTRUCTION_MANIFEST.json"
            reconstruction_manifest.write_text(json.dumps({"schema": "kb_creator.reconstruction_upstream_manifest.v1", "review": {"decisions": [identity(page_decision, root)]}}), encoding="utf-8")
            reconstruction_inventory = root / "reconstruction_inventory.json"
            reconstruction_inventory.write_text(json.dumps({"schema": "kb_creator.reconstruction_upstream_inventory.v1", "artifacts": [{"role": "reconstruction_manifest", **identity(reconstruction_manifest, root)}]}), encoding="utf-8")
            placeholders["reconstruction_inventory"] = identity(reconstruction_inventory, root)
            profile = {
                "schema": scenario_artview.PROFILE_SCHEMA_V4, "scenario_id": "sample", "output_root": "v4-run",
                "inputs": {**placeholders, "source_pdf": identity(source_pdf, root), "source_identity": identity(source_identity, root)},
                "render": {"dpi": 150, "format": "png"},
            }
            profile_path = root / "profile.json"; profile_path.write_text(json.dumps(profile), encoding="utf-8")
            self.assertEqual(scenario_artview._v4_profile(profile_path)[0]["schema"], scenario_artview.PROFILE_SCHEMA_V4)
            invalid = dict(profile); invalid["page_roles"] = []
            profile_path.write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaises(ValueError): scenario_artview._v4_profile(profile_path)
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            pages, raw, _ = scenario_artview._v4_raw_inventory(source_pdf)
            self.assertEqual(pages, 1); self.assertTrue(raw)
            self.assertTrue(all(item["disposition"] in {"technical_pdf_mechanic", "component_of_visual_unit"} for item in raw))
            candidate = root / "v4-run" / "candidate"; candidate.mkdir(parents=True)
            row = {"asset_id": "pdf-page-001-visual", "required": True, "placement_id": "source-cover-page-001", "allowed_binary_decisions": ["keep_current", "exclude", "needs_manual_work", "reopen_masters"]}
            manifest = {"schema": scenario_artview.CANDIDATE_SCHEMA_V4, "scenario_id": "sample", "bindings": {"profile": identity(profile_path, root), **{name: value for name, value in profile["inputs"].items()}}, "candidate_files_inventory_sha256": "A" * 64, "rows": [row], "decision_contract": {"binding_sources": ["profile", "master_ru", "master_ru_acceptance", "master_ru_asset_manifest", "reconstruction_inventory", "source_pdf", "source_identity"]}}
            manifest_path = candidate / "candidate_manifest.json"; manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            decision = {"schema": scenario_artview.DECISION_SCHEMA_V4, "scenario_id": "sample", "state": "accepted", "bindings": scenario_artview.decision_bindings(manifest, sha(manifest_path)), "decisions": [{"asset_id": row["asset_id"], "binary": {"choice": "exclude", "candidate_id": None}, "presentation": {"width_percent": 100, "alignment": "center", "wrap_text": False, "wrap_tables": False}, "reviewed": True, "notes": "no"}], "review": {"state": "closed", "reviewed_count": 1, "unresolved_asset_ids": []}}
            decision["decisions_sha256"] = hashlib.sha256(json.dumps(decision, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest().upper()
            decision_path = root / "decisions.json"; decision_path.write_text(json.dumps(decision), encoding="utf-8")
            result = scenario_artview.validate_v4_decisions(profile_path, decision_path, True)
            self.assertEqual(result["status"], "fail")
            self.assertIn("required_placement_not_included", [item["code"] for item in result["findings"]])

    def test_v4_duplicate_xobject_occurrences_remain_page_distinct(self) -> None:
        """The same PDF object on pages 4/5/9 remains three reviewable occurrences."""
        from pypdf import PdfReader, PdfWriter

        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name); one = root / "one.pdf"; Image.new("RGB", (24, 18), "teal").save(one, "PDF")
            reader = PdfReader(str(one)); writer = PdfWriter()
            for _ in range(9): writer.add_page(reader.pages[0])
            repeated = root / "repeated.pdf"
            with repeated.open("wb") as handle: writer.write(handle)
            _pages, rows, _masks = scenario_artview._v4_raw_inventory(repeated)
            selected = [row for row in rows if row["source_page"] in {4, 5, 9} and row["disposition"] == "component_of_visual_unit"]
            self.assertEqual({row["source_page"] for row in selected}, {4, 5, 9})
            self.assertEqual(len({row["raw_id"] for row in selected}), 3)

    def test_v4_soft_mask_is_bound_to_its_owner_without_becoming_a_review_row(self) -> None:
        """A PDF soft mask is inventoried as a technical component of its base image."""
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import DecodedStreamObject, NameObject, NumberObject

        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            source = root / "source.pdf"
            Image.new("RGB", (24, 18), "navy").save(source, "PDF")
            reader = PdfReader(str(source))
            writer = PdfWriter()
            writer.add_page(reader.pages[0])
            page = writer.pages[0]
            xobjects = page["/Resources"]["/XObject"]
            image_ref = next(iter(xobjects.values()))
            image = image_ref.get_object()
            mask = DecodedStreamObject()
            mask.set_data(bytes([255]) * 24 * 18)
            mask.update(
                {
                    NameObject("/Type"): NameObject("/XObject"),
                    NameObject("/Subtype"): NameObject("/Image"),
                    NameObject("/Width"): NumberObject(24),
                    NameObject("/Height"): NumberObject(18),
                    NameObject("/ColorSpace"): NameObject("/DeviceGray"),
                    NameObject("/BitsPerComponent"): NumberObject(8),
                }
            )
            mask_ref = writer._add_object(mask)
            image[NameObject("/SMask")] = mask_ref
            masked = root / "masked.pdf"
            with masked.open("wb") as handle:
                writer.write(handle)

            _pages, rows, _masks = scenario_artview._v4_raw_inventory(masked)
            ordinary = [row for row in rows if row["disposition"] == "component_of_visual_unit"]
            masks = [row for row in rows if row["technical_reason"] == "soft_mask"]
            self.assertEqual(len(ordinary), 1)
            self.assertEqual(len(masks), 1)
            self.assertEqual(masks[0]["bound_component_of"], [ordinary[0]["raw_id"]])

    def test_v3_schemas_are_closed_and_scenario_neutral(self) -> None:
        contracts = Path(__file__).resolve().parents[1] / "contracts"
        for name in ("scenario_artview_profile.v3.schema.json", "scenario_artview_decisions.v3.schema.json"):
            schema = json.loads((contracts / name).read_text(encoding="utf-8"))
            self.assertFalse(schema["additionalProperties"])
            serialized = json.dumps(schema).lower()
            self.assertNotIn("viral", serialized)
            self.assertNotIn("innsmouth", serialized)

    def test_v3_safe_path_schema_compiles_and_matches_runtime_contract(self) -> None:
        schema = v3_profile_schema()
        Draft202012Validator.check_schema(schema)
        pattern = schema["$defs"]["safePath"]["pattern"]
        self.assertEqual(pattern, scenario_artview.V3_SAFE_PATH_PATTERN)
        compiled = re.compile(pattern)
        lexical_validator = Draft202012Validator(schema["$defs"]["safePath"])
        for value in SAFE_V3_PATHS:
            with self.subTest(value=value, expected="safe"):
                self.assertIsNotNone(compiled.fullmatch(value))
                self.assertTrue(lexical_validator.is_valid(value))
                self.assertEqual(scenario_artview._v3_safe_path(value, "test path"), value)
        for value in UNSAFE_V3_PATHS:
            with self.subTest(value=repr(value), expected="unsafe"):
                self.assertIsNone(compiled.fullmatch(value))
                self.assertFalse(lexical_validator.is_valid(value))
                with self.assertRaisesRegex(ValueError, "normalized portable relative path"):
                    scenario_artview._v3_safe_path(value, "test path")

    def test_v3_safe_path_rejects_every_schema_use_site(self) -> None:
        validator = Draft202012Validator(v3_profile_schema())
        base = json.loads(self.profile.read_text(encoding="utf-8"))
        setters = {
            "output_root": lambda value, path: value.__setitem__("output_root", path),
            "input_path": lambda value, path: value["inputs"]["master_ru"].__setitem__("path", path),
            "image_path": lambda value, path: value["rows"][0]["current"].__setitem__("path", path),
        }
        for site, setter in setters.items():
            for path in UNSAFE_V3_PATHS:
                with self.subTest(site=site, path=repr(path)):
                    profile = copy.deepcopy(base)
                    setter(profile, path)
                    self.assertTrue(list(validator.iter_errors(profile)))

    def test_v3_runtime_rejects_unsafe_paths_before_filesystem_access(self) -> None:
        for value in UNSAFE_V3_PATHS:
            with self.subTest(helper="resolve", value=repr(value)):
                before = tuple(sorted(path.name for path in self.root.iterdir()))
                with self.assertRaisesRegex(ValueError, "normalized portable relative path"):
                    scenario_artview._v3_resolve(
                        self.root,
                        {"path": value, "bytes": 1, "sha256": "A" * 64},
                        "input",
                    )
                self.assertEqual(tuple(sorted(path.name for path in self.root.iterdir())), before)
            with self.subTest(helper="output_root", value=repr(value)):
                before = tuple(sorted(path.name for path in self.root.iterdir()))
                with self.assertRaisesRegex(ValueError, "normalized portable relative path"):
                    scenario_artview._v3_output_root(self.root, value, "output", must_exist=False)
                self.assertEqual(tuple(sorted(path.name for path in self.root.iterdir())), before)

    def test_authored_dissociation_profile_validates_byte_unchanged(self) -> None:
        profile_path = (
            Path(__file__).resolve().parents[1]
            / "inputs"
            / "dissociation"
            / "publication"
            / "v1"
            / "configs"
            / "artview"
            / "profile.json"
        )
        before = profile_path.read_bytes()
        profile = json.loads(before.decode("utf-8"))
        errors = sorted(Draft202012Validator(v3_profile_schema()).iter_errors(profile), key=lambda item: list(item.path))
        self.assertEqual(errors, [])
        paths = [profile["output_root"]]
        paths.extend(record["path"] for record in profile["inputs"].values())
        for row in profile["rows"]:
            paths.extend((row["current"]["path"], row["context"]["path"]))
            paths.extend(item["binary"]["path"] for item in row["alternatives"])
        for value in paths:
            self.assertEqual(scenario_artview._v3_safe_path(value, "authored path"), value)
        self.assertEqual(profile_path.read_bytes(), before)

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.inputs = self.root / "inputs"
        self.inputs.mkdir()
        self.current = self.inputs / "current.png"
        self.context = self.inputs / "context.png"
        self.alternative = self.inputs / "alternative.png"
        for path, color in (
            (self.current, (10, 20, 30)),
            (self.context, (40, 50, 60)),
            (self.alternative, (70, 80, 90)),
        ):
            Image.new("RGB", (16, 12), color).save(path, format="PNG")
        self.master_ru = self.root / "MASTER_RU.md"
        self.master_ru.write_text('# Сцена\n\n![Карта](assets/map.png)\n', encoding="utf-8")
        producer = self.root / "master-ru-stage.json"
        evidence = self.root / "master-ru-qa.json"
        producer.write_text("{}\n", encoding="utf-8")
        evidence.write_text("{}\n", encoding="utf-8")
        acceptance = {
            "schema": "kb_creator.artifact_acceptance.v1",
            "scenario_id": "sample",
            "artifact_kind": "master_ru",
            "candidate": identity(self.master_ru, self.root),
            "producer_stage": identity(producer, self.root),
            "evidence": [identity(evidence, self.root)],
            "decision": "accepted",
            "decision_at_utc": "2026-09-14T00:00:00Z",
            "user_decision_reference": "synthetic fixture",
            "recorder_role": "main_orchestrator",
        }
        self.master_ru_acceptance = self.root / "master-ru.acceptance.json"
        self.master_ru_acceptance.write_text(
            json.dumps(seal(acceptance, "receipt_sha256"), ensure_ascii=False), encoding="utf-8"
        )
        self.asset_manifest = self.root / "master-ru-assets.json"
        self.asset_manifest.write_text(
            json.dumps({"schema": "fixture", "assets": [{"role": "reader_asset", **identity(self.current, self.root)}]}), encoding="utf-8"
        )
        self.reconstruction = self.root / "reconstruction-inventory.json"
        self.reconstruction.write_text(
            json.dumps(
                {
                    "schema": "fixture",
                    "artifacts": [
                        {"role": "page_context", **identity(self.context, self.root)},
                        {"role": "reconstruction_candidate", **identity(self.alternative, self.root)},
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.profile = self.root / "profile.json"
        profile = {
            "schema": scenario_artview.PROFILE_SCHEMA_V3,
            "scenario_id": "sample",
            "output_root": "artview-run",
            "inputs": {
                "master_ru": identity(self.master_ru, self.root),
                "master_ru_acceptance": identity(self.master_ru_acceptance, self.root),
                "master_ru_asset_manifest": identity(self.asset_manifest, self.root),
                "reconstruction_inventory": identity(self.reconstruction, self.root),
            },
            "excluded_source_pages": [99],
            "rows": [
                {
                    "asset_id": "map",
                    "anchor": "scene",
                    "label": "Карта",
                    "source_page": 1,
                    "group": "maps",
                    "current": image_identity(self.current, self.root),
                    "context": image_identity(self.context, self.root),
                    "alternatives": [
                        {
                            "candidate_id": "map-clean",
                            "kind": "reconstruction_candidate",
                            "binary": image_identity(self.alternative, self.root),
                        }
                    ],
                    "presentation_defaults": {
                        "width_percent": 60,
                        "alignment": "center",
                        "wrap_text": False,
                        "wrap_tables": False,
                    },
                }
            ],
        }
        self.profile.write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
        self.build_result = scenario_artview.build(self.profile, None, False, None)
        self.candidate_root = self.root / "artview-run" / "candidate"
        template = json.loads((self.candidate_root / "artview-decisions.template.json").read_text(encoding="utf-8"))
        template["state"] = "accepted"
        template["decisions"][0].update(
            {
                "binary": {"choice": "use_candidate", "candidate_id": "map-clean"},
                "reviewed": True,
                "notes": "synthetic review",
            }
        )
        template["review"] = {"state": "closed", "reviewed_count": 1, "unresolved_asset_ids": []}
        self.decisions = self.root / "decisions.json"
        self.decisions.write_text(
            json.dumps(scenario_artview.seal_v3_decisions(template), ensure_ascii=False), encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _build_rebind_target(self, name: str, mutate=None) -> tuple[Path, Path]:
        profile = json.loads(self.profile.read_text(encoding="utf-8"))
        profile["output_root"] = f"{name}-artview-run"
        if mutate is not None:
            mutate(profile)
        profile_path = self.root / f"{name}-profile.json"
        profile_path.write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
        scenario_artview.build(profile_path, None, False, None)
        manifest_path = self.root / profile["output_root"] / "candidate" / "candidate_manifest.json"
        return profile_path, manifest_path

    def _rebind(
        self,
        target_profile: Path,
        target_manifest: Path,
        destination: Path,
        *,
        source_manifest: Path | None = None,
        source_decisions: Path | None = None,
    ) -> dict[str, object]:
        return scenario_artview.rebind_v3_decisions(
            self.profile.relative_to(self.root),
            (source_manifest or (self.candidate_root / "candidate_manifest.json")).relative_to(self.root),
            self.root,
            (source_decisions or self.decisions).relative_to(self.root),
            target_profile.relative_to(self.root),
            target_manifest.relative_to(self.root),
            self.root,
            destination.relative_to(self.root),
        )

    def _artview_acceptance(self, candidate: Path | None = None) -> Path:
        producer = self.root / "artview-stage.json"
        producer.write_text("{}\n", encoding="utf-8")
        acceptance = {
            "schema": "kb_creator.artifact_acceptance.v1",
            "scenario_id": "sample",
            "artifact_kind": "artview",
            "candidate": identity(candidate or (self.candidate_root / "candidate_manifest.json"), self.root),
            "producer_stage": identity(producer, self.root),
            "evidence": [identity(self.decisions, self.root)],
            "decision": "accepted",
            "decision_at_utc": "2026-09-14T00:00:00Z",
            "user_decision_reference": "synthetic fixture",
            "recorder_role": "main_orchestrator",
        }
        acceptance_path = self.root / "artview.acceptance.json"
        acceptance_path.write_text(
            json.dumps(seal(acceptance, "receipt_sha256"), ensure_ascii=False), encoding="utf-8"
        )
        return acceptance_path

    def test_bundle_validation_and_application_are_closed_and_hash_bound(self) -> None:
        self.assertEqual(self.build_result["status"], "awaiting_artview_decisions")
        validation = scenario_artview.validate_v3_decisions(self.profile, self.decisions, True)
        self.assertEqual(validation["status"], "pass")
        manifest = json.loads((self.candidate_root / "candidate_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["derived_expected"],
            {
                "review_rows": 1,
                "alternative_binaries": 1,
                "portable_binaries": 3,
                "source_pages": 1,
                "excluded_source_pages": [99],
            },
        )
        self.assertTrue((self.candidate_root / "context" / "map.png").is_file())
        serialized = json.dumps(manifest).lower()
        self.assertNotIn("viral", serialized)
        self.assertNotIn("innsmouth", serialized)
        self.assertEqual(manifest["rows"][0]["current"]["source_graph_membership"][0]["role"], "reader_asset")

        acceptance_path = self._artview_acceptance()
        output = self.root / "applied"
        result = scenario_artview_apply.apply(self.profile, self.decisions, acceptance_path, Path("applied"), self.root)
        self.assertEqual(result["status"], "ready_for_html_candidate")
        self.assertEqual((output / "assets" / "map.png").read_bytes(), self.alternative.read_bytes())
        self.assertTrue((output / "effective_visual_config.json").is_file())
        self.assertTrue((output / "ARTVIEW_APPLIED.json").is_file())

    def test_rebind_v3_decisions_preserves_review_and_replaces_only_target_bindings(self) -> None:
        target_profile, target_manifest = self._build_rebind_target("fresh")
        destination = self.root / "fresh.accepted-decisions.json"

        result = self._rebind(target_profile, target_manifest, destination)

        self.assertEqual(result["status"], "pass")
        source = json.loads(self.decisions.read_text(encoding="utf-8"))
        rebound = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(rebound["decisions"], source["decisions"])
        self.assertNotEqual(rebound["bindings"], source["bindings"])
        self.assertEqual(
            rebound["review"],
            {"state": "closed", "reviewed_count": 1, "unresolved_asset_ids": []},
        )
        self.assertEqual(
            rebound["decisions_sha256"],
            scenario_artview.seal_v3_decisions(rebound)["decisions_sha256"],
        )
        validation = scenario_artview.validate_v3_decisions(
            target_profile,
            destination,
            True,
            target_manifest.relative_to(self.root),
            self.root,
        )
        self.assertEqual(validation["status"], "pass")

    def test_rebind_v3_decisions_rejects_changed_visible_or_binary_evidence(self) -> None:
        def change_binary(profile: dict[str, object]) -> None:
            changed = self.inputs / "alternative-changed.png"
            Image.new("RGB", (16, 12), (90, 80, 70)).save(changed, format="PNG")
            reconstruction = self.root / "target-reconstruction-inventory.json"
            reconstruction.write_text(
                json.dumps(
                    {
                        "schema": "fixture",
                        "artifacts": [
                            {"role": "page_context", **identity(self.context, self.root)},
                            {"role": "reconstruction_candidate", **identity(changed, self.root)},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            profile["inputs"]["reconstruction_inventory"] = identity(reconstruction, self.root)
            profile["rows"][0]["alternatives"][0]["binary"] = image_identity(changed, self.root)

        mutations = {
            "label": lambda profile: profile["rows"][0].__setitem__("label", "Изменённая карта"),
            "presentation": lambda profile: profile["rows"][0]["presentation_defaults"].__setitem__(
                "width_percent", 70
            ),
            "selected_binary": change_binary,
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                target_profile, target_manifest = self._build_rebind_target(name, mutate)
                destination = self.root / f"{name}.accepted-decisions.json"
                with self.assertRaisesRegex(ValueError, "decision evidence differs"):
                    self._rebind(target_profile, target_manifest, destination)
                self.assertFalse(destination.exists())

    def test_rebind_v3_decisions_rejects_stale_source_seal_and_target_graph(self) -> None:
        target_profile, target_manifest = self._build_rebind_target("strict")
        stale_decisions = self.root / "stale-decisions.json"
        stale = json.loads(self.decisions.read_text(encoding="utf-8"))
        stale["decisions"][0]["notes"] = "changed after acceptance"
        stale_decisions.write_text(json.dumps(stale, ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "failed strict validation"):
            self._rebind(
                target_profile,
                target_manifest,
                self.root / "stale-output.json",
                source_decisions=stale_decisions,
            )

        target_binary = target_manifest.parent / "assets" / "candidates" / "map-clean.png"
        Image.new("RGB", (16, 12), (1, 2, 3)).save(target_binary, format="PNG")
        destination = self.root / "tampered-target-output.json"
        with self.assertRaisesRegex(ValueError, "target candidate graph failed strict validation"):
            self._rebind(target_profile, target_manifest, destination)
        self.assertFalse(destination.exists())

    def test_rebind_v3_decisions_rejects_unsafe_or_existing_destination(self) -> None:
        target_profile, target_manifest = self._build_rebind_target("destination")
        with self.assertRaisesRegex(ValueError, "safe authority-relative"):
            scenario_artview.rebind_v3_decisions(
                self.profile.relative_to(self.root),
                (self.candidate_root / "candidate_manifest.json").relative_to(self.root),
                self.root,
                self.decisions.relative_to(self.root),
                target_profile.relative_to(self.root),
                target_manifest.relative_to(self.root),
                self.root,
                Path("..") / "escape.json",
            )
        existing = self.root / "existing.json"
        existing.write_text("{}\n", encoding="utf-8")
        with self.assertRaisesRegex(FileExistsError, "must be absent"):
            self._rebind(target_profile, target_manifest, existing)
        self.assertEqual(existing.read_text(encoding="utf-8"), "{}\n")

    def test_v3_html_uses_clickable_art_cards_and_blocks_incomplete_acceptance(self) -> None:
        html = (self.candidate_root / "artview.html").read_text(encoding="utf-8")

        self.assertIn('id="exportDraft"', html)
        self.assertIn('id="exportAccepted" disabled', html)
        self.assertIn('id="importConfig"', html)
        self.assertIn('id="importDialog"', html)
        self.assertIn('id="importFile"', html)
        self.assertIn('Импорт прошлого конфига ArtView', html)
        self.assertIn('input.type="radio"', html)
        self.assertIn('input.name="image-choice-"+selection.row.asset_id', html)
        self.assertIn('classList.toggle("selected",selected)', html)
        self.assertIn('.image-card.selected:focus-within', html)
        self.assertIn('outline-color:var(--ok)', html)
        self.assertIn('current.reviewed=true;refresh()', html)
        self.assertIn('refs.status.textContent=ready?"Выбор сделан":"Выберите вариант"', html)
        self.assertIn('width.type="number"', html)
        self.assertIn('alignment=el("select")', html)
        self.assertIn('input.type="checkbox"', html)
        self.assertNotIn('review.type="checkbox"', html)
        self.assertNotIn('Строка проверена человеком', html)
        self.assertNotIn('Бинарное решение', html)
        self.assertNotIn('Примечания', html)
        self.assertNotIn('notes=el("textarea")', html)
        self.assertIn('presentation:{...row.presentation_defaults}', html)
        self.assertIn('width.value=String(current.presentation.width_percent)', html)
        self.assertIn('option.selected=current.presentation.alignment===value', html)
        self.assertIn('input.checked=current.presentation[key]', html)
        self.assertIn('if(input.checked&&current.presentation.alignment==="center")', html)
        self.assertIn('current.presentation.alignment="right";alignment.value="right"', html)
        self.assertIn('if(key==="wrap_tables"&&input.checked)', html)
        self.assertIn('current.presentation.wrap_text=true;wrapInputs.wrap_text.checked=true', html)
        self.assertIn('if(key==="wrap_text"&&!input.checked)', html)
        self.assertIn('current.presentation.wrap_tables=false;wrapInputs.wrap_tables.checked=false', html)
        self.assertIn('if(alignment.value==="center"&&(current.presentation.wrap_text||current.presentation.wrap_tables))', html)
        self.assertIn('acceptedButton.disabled=!isAcceptedReady()', html)
        self.assertIn('if(accepted&&unresolved.length)throw new Error', html)
        self.assertIn('row.allowed_binary_decisions.includes(choice)', html)
        self.assertIn('const decisionSchema=manifest.decision_contract.schema', html)
        self.assertIn('schema:decisionSchema', html)
        self.assertIn('notes:""', html)
        self.assertIn('state:accepted?"accepted":"draft"', html)
        self.assertIn('review:{state:accepted?"closed":"open"', html)
        self.assertIn('decisions_sha256:await sha256Hex(canonicalJson(documentValue))', html)
        self.assertIn('async function copyExportLocator(filename)', html)
        self.assertIn('navigator.clipboard.writeText(filename)', html)
        self.assertIn('return link.download', html)
        self.assertIn('Полный путь определяет браузер и не сообщает странице.', html)
        self.assertIn('async function prepareImport(documentValue)', html)
        self.assertIn('documentValue.decisions_sha256!==await sha256Hex(canonicalJson(unsigned))', html)
        self.assertIn('const exactBindings=canonicalJson(documentValue.bindings)===canonicalJson(expectedBindings)', html)
        self.assertIn('reviewed:preserveReviewed&&item.reviewed', html)
        self.assertIn('Отметки проверки будут сброшены', html)
        self.assertIn('applyImportButton.addEventListener("click"', html)
        self.assertIn('window.artviewV3={manifest,expectedBindings,decisions,buildDecisionDocument,sealDocument,isAcceptedReady,prepareImport}', html)

        decision_schema = json.loads(
            (Path(__file__).resolve().parents[1] / "contracts" / "scenario_artview_decisions.v3.schema.json").read_text(
                encoding="utf-8"
            )
        )
        accepted = json.loads(self.decisions.read_text(encoding="utf-8"))
        self.assertEqual(list(Draft202012Validator(decision_schema).iter_errors(accepted)), [])
        self.assertEqual(scenario_artview.validate_v3_decisions(self.profile, self.decisions, True)["status"], "pass")
        embedded_bindings = re.search(
            r'<script type="application/json" id="bindings">([^<]+)</script>', html
        )
        self.assertIsNotNone(embedded_bindings)
        self.assertEqual(json.loads(embedded_bindings.group(1)), accepted["bindings"])

    def test_v3_html_escapes_manifest_labels_and_never_injects_them_as_markup(self) -> None:
        manifest = json.loads((self.candidate_root / "candidate_manifest.json").read_text(encoding="utf-8"))
        hostile = '</script><img src=x onerror="window.injected=true">'
        manifest["scenario_id"] = hostile
        manifest["rows"][0]["label"] = hostile

        html = scenario_artview._v3_review_html(manifest, "A" * 64)

        self.assertNotIn(hostile, html)
        self.assertIn(r'\u003c/script\u003e\u003cimg src=x onerror=\"window.injected=true\"\u003e', html)
        self.assertNotIn("innerHTML", html)
        self.assertIn('identity.append(el("h2","",row.label)', html)

    def test_explicit_stage30_manifest_authority_supports_apply_without_copy_or_link(self) -> None:
        stage30 = self.root / "outputs" / "30-artview-bundle" / "artifacts"
        stage30.parent.mkdir(parents=True)
        self.candidate_root.replace(stage30)
        explicit = Path("outputs/30-artview-bundle/artifacts/candidate_manifest.json")
        validation = scenario_artview.validate_v3_decisions(
            self.profile, self.decisions, True, explicit, self.root
        )
        self.assertEqual(validation["status"], "pass")
        acceptance = self._artview_acceptance(stage30 / "candidate_manifest.json")
        output = self.root / "explicit-applied"
        result = scenario_artview_apply.apply(
            self.profile,
            self.decisions,
            acceptance,
            Path("explicit-applied"),
            self.root,
            explicit,
        )
        self.assertEqual(result["status"], "ready_for_html_candidate")
        self.assertTrue((output / "ARTVIEW_APPLIED.json").is_file())
        with self.assertRaises(ValueError):
            scenario_artview.validate_v3_decisions(self.profile, self.decisions, True)

    def test_closed_decisions_reject_extra_field_and_incomplete_acceptance(self) -> None:
        value = json.loads(self.decisions.read_text(encoding="utf-8"))
        value["unknown"] = True
        self.decisions.write_text(
            json.dumps(scenario_artview.seal_v3_decisions(value), ensure_ascii=False), encoding="utf-8"
        )
        result = scenario_artview.validate_v3_decisions(self.profile, self.decisions, True)
        self.assertEqual(result["status"], "fail")
        self.assertIn("decision_closed_schema_mismatch", {row["code"] for row in result["findings"]})

        template = json.loads((self.candidate_root / "artview-decisions.template.json").read_text(encoding="utf-8"))
        template["state"] = "accepted"
        self.decisions.write_text(
            json.dumps(scenario_artview.seal_v3_decisions(template), ensure_ascii=False), encoding="utf-8"
        )
        result = scenario_artview.validate_v3_decisions(self.profile, self.decisions, True)
        self.assertEqual(result["status"], "fail")
        self.assertIn("accepted_full_closure_required", {row["code"] for row in result["findings"]})

    def test_tampered_profile_binding_invalidates_existing_decisions(self) -> None:
        profile = json.loads(self.profile.read_text(encoding="utf-8"))
        profile["rows"][0]["label"] = "Другая карта"
        self.profile.write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
        result = scenario_artview.validate_v3_decisions(self.profile, self.decisions, True)
        self.assertEqual(result["status"], "fail")
        codes = {row["code"] for row in result["findings"]}
        self.assertTrue({"candidate_manifest_binding_mismatch", "binding_mismatch"} & codes)

    def test_tampered_portable_binary_blocks_even_if_inventory_is_not_consulted_by_user(self) -> None:
        target = self.candidate_root / "assets" / "candidates" / "map-clean.png"
        Image.new("RGB", (16, 12), (1, 2, 3)).save(target, format="PNG")
        result = scenario_artview.validate_v3_decisions(self.profile, self.decisions, True)
        self.assertEqual(result["status"], "fail")
        codes = {row["code"] for row in result["findings"]}
        self.assertTrue({"candidate_manifest_projection_mismatch", "candidate_binary_inventory_mismatch"} & codes)

    def test_v3_build_rejects_absolute_output_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as outside_temp:
            outside = Path(outside_temp) / "outside-artview"
            with self.assertRaisesRegex(ValueError, "normalized portable relative path"):
                scenario_artview.build(self.profile, None, False, outside)
            self.assertFalse(outside.exists())

    def test_v3_apply_rejects_absolute_output_before_write(self) -> None:
        acceptance_path = self._artview_acceptance()
        with tempfile.TemporaryDirectory() as outside_temp:
            outside = Path(outside_temp) / "outside-applied"
            with self.assertRaisesRegex(scenario_artview_apply.ArtViewApplyError, "normalized portable relative path"):
                scenario_artview_apply.apply(self.profile, self.decisions, acceptance_path, outside, self.root)
            self.assertFalse(outside.exists())

    def test_master_ru_acceptance_is_exact_closed_and_fully_resolved(self) -> None:
        original_acceptance = json.loads(self.master_ru_acceptance.read_text(encoding="utf-8"))
        original_profile = json.loads(self.profile.read_text(encoding="utf-8"))
        cases = {
            "extra": lambda value: value.__setitem__("extra", True),
            "schema": lambda value: value.__setitem__("schema", "kb_creator.artifact_acceptance.v0"),
            "scenario": lambda value: value.__setitem__("scenario_id", "other"),
            "producer": lambda value: value.__setitem__("producer_stage", {"path": "missing-producer.json", "bytes": 1, "sha256": "A" * 64}),
            "evidence": lambda value: value.__setitem__("evidence", [{"path": "missing-evidence.json", "bytes": 1, "sha256": "A" * 64}]),
            "empty_evidence": lambda value: value.__setitem__("evidence", []),
            "kind": lambda value: value.__setitem__("artifact_kind", "master_en"),
            "role": lambda value: value.__setitem__("recorder_role", "worker"),
            "candidate": lambda value: value.__setitem__("candidate", identity(self.asset_manifest, self.root)),
            "decision": lambda value: value.__setitem__("decision", "rejected"),
            "user_reference": lambda value: value.__setitem__("user_decision_reference", ""),
        }
        for index, (name, mutate) in enumerate(cases.items()):
            with self.subTest(name=name):
                acceptance = copy.deepcopy(original_acceptance)
                mutate(acceptance)
                self.master_ru_acceptance.write_text(json.dumps(seal(acceptance, "receipt_sha256"), ensure_ascii=False), encoding="utf-8")
                profile = copy.deepcopy(original_profile)
                profile["inputs"]["master_ru_acceptance"] = identity(self.master_ru_acceptance, self.root)
                self.profile.write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
                output = Path(f"invalid-acceptance-{index}")
                with self.assertRaises(ValueError):
                    scenario_artview.build(self.profile, None, False, output)
                self.assertFalse((self.root / output).exists())
        self.master_ru_acceptance.write_text(json.dumps(original_acceptance, ensure_ascii=False), encoding="utf-8")
        self.profile.write_text(json.dumps(original_profile, ensure_ascii=False), encoding="utf-8")

    def test_same_bytes_alternate_path_is_rejected_for_each_binary_class(self) -> None:
        original = json.loads(self.profile.read_text(encoding="utf-8"))
        selectors = {
            "current": lambda profile, record: profile["rows"][0].__setitem__("current", record),
            "context": lambda profile, record: profile["rows"][0].__setitem__("context", record),
            "alternative": lambda profile, record: profile["rows"][0]["alternatives"][0].__setitem__("binary", record),
        }
        sources = {"current": self.current, "context": self.context, "alternative": self.alternative}
        for index, (name, select) in enumerate(selectors.items()):
            with self.subTest(name=name):
                duplicate = self.inputs / f"duplicate-{name}.png"
                duplicate.write_bytes(sources[name].read_bytes())
                profile = copy.deepcopy(original)
                select(profile, image_identity(duplicate, self.root))
                self.profile.write_text(json.dumps(profile, ensure_ascii=False), encoding="utf-8")
                output = Path(f"spoof-{index}")
                with self.assertRaisesRegex(ValueError, "outside exact bound source graph"):
                    scenario_artview.build(self.profile, None, False, output)
                self.assertFalse((self.root / output).exists())
                duplicate.unlink()
        self.profile.write_text(json.dumps(original, ensure_ascii=False), encoding="utf-8")
