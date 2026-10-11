"""Focused B1 tests for the fail-closed real-input Viral v2 author foundation."""
from __future__ import annotations

import importlib.util
import copy
import json
import tempfile
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("viral_v2_author", ROOT / "scripts" / "author_viral_master_en_v2_config.py")
assert SPEC and SPEC.loader
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)


class ViralV2AuthorFoundationTests(unittest.TestCase):
    def test_real_inputs_are_bound_and_partition_every_reader_byte(self):
        result = A.foundation()
        partition = result["source_partition"]
        self.assertEqual([row["page"] for row in partition["pages"]], list(range(1, 123)))
        self.assertGreaterEqual(len(partition["spans"]), 122)
        self.assertEqual(sum(row["bytes"] for row in partition["pages"]), 346793)
        self.assertEqual(sum(row["eol_profile"]["line_slots"] for row in partition["pages"]), 4860)
        self.assertEqual(sum(row["eol_profile"]["nonblank_line_slots"] for row in partition["pages"]), 2040)
        for page in partition["pages"]:
            spans = [span for span in partition["spans"] if span["page"] == page["page"]]
            self.assertEqual(spans[0]["start_byte"], 0)
            self.assertEqual(spans[-1]["end_byte"], page["bytes"])
            self.assertEqual(page["span_ids"], [span["span_id"] for span in spans])

    def test_real_input_foundations_are_byte_identical_and_canonical(self):
        first, second = A.canonical_json(A.foundation()), A.canonical_json(A.foundation())
        self.assertEqual(first, second)
        self.assertEqual(first[-1:], b"\n")
        self.assertEqual(json.loads(first), json.loads(second))

    def test_all_v1_domains_have_exactly_one_sealed_migration_row(self):
        migration = A.foundation()["migration"]
        self.assertEqual({key: len(migration[key]) for key, _, _ in A.MIGRATION_DOMAINS}, {"hierarchy_rows": 168, "asset_rows": 123, "xref_rows": 237, "structured_rows": 29, "handout_rows": 41, "source_disposition_rows": 124})
        for key, _, _ in A.MIGRATION_DOMAINS:
            rows = migration[key]
            self.assertEqual(len(rows), len({row["source_id"] for row in rows}))
            self.assertTrue(all(len(row["source_row_sha256"]) == 64 for row in rows))

    def test_b1c_asset_xref_inventory_is_exact_but_refuses_unsealed_targets(self):
        readiness = A.asset_xref_readiness()
        self.assertEqual(readiness["asset_count"], 123)
        self.assertEqual(readiness["xref_count"], 237)
        self.assertEqual(readiness["reader_asset_count"] + readiness["evidence_asset_count"] + len(readiness["excluded_advertising_asset_ids"]), 123)
        self.assertTrue(readiness["excluded_advertising_asset_ids"])
        self.assertEqual(readiness["asset_owned_span_count"], 16)
        self.assertEqual(len(readiness["asset_span_bindings"]), 16)
        self.assertEqual(len({row["asset_id"] for row in readiness["asset_span_bindings"]}), 16)
        self.assertEqual({row["source_page"] for row in readiness["asset_span_bindings"]}, {3, 6, 7, 13, 25, 31, 32, 34, 40})
        self.assertEqual(len(readiness["pending_asset_targets"]), 123)
        self.assertEqual(len(readiness["pending_xref_targets"]), 237)
        self.assertEqual(len(set(readiness["pending_asset_targets"])), 123)
        self.assertEqual(len(set(readiness["pending_xref_targets"])), 237)

    def test_b1c4_asset_audit_recomputes_the_closed_frozen_partition(self):
        audit = A.asset_b1c4_audit()
        self.assertEqual(audit["counts"], {"retained_unchanged": 99, "retained_rebound": 2, "reclassified": 16, "excluded_advertising": 6})
        self.assertEqual(len(audit["rows"]), 123)
        self.assertEqual(sum(row["disposition"] == "reader" for row in audit["rows"]), 85)
        self.assertEqual(sum(row["disposition"] == "evidence_only" for row in audit["rows"]), 32)
        self.assertEqual(sum(row["binary"] is not None for row in audit["rows"]), 121)
        self.assertEqual({row["source_page"] for row in audit["rows"] if row["outcome"] == "excluded_advertising"}, {123, 124})

    def test_output_writer_is_atomic_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "v2.json"; payload = b'{"stable":true}\n'
            A.write_atomic_absent(target, payload)
            self.assertEqual(target.read_bytes(), payload)
            with self.assertRaisesRegex(A.AuthoringError, "OUTPUT_EXISTS"):
                A.write_atomic_absent(target, payload)
            self.assertEqual(list(Path(temporary).glob(".*.tmp")), [])

    def test_checkout_temporary_config_refuses_collision_and_cleans_up_gate_failure(self):
        token = str(uuid.uuid4())
        target = A.checkout_temporary_config_path(token)
        self.assertFalse(target.exists())
        with self.assertRaisesRegex(RuntimeError, "forced public preflight failure"):
            A.with_checkout_temporary_config(b'{"foundation":true}\n', lambda _: (_ for _ in ()).throw(RuntimeError("forced public preflight failure")), token)
        self.assertFalse(target.exists())
        target.write_bytes(b"pre-existing")
        try:
            with self.assertRaisesRegex(A.AuthoringError, "OUTPUT_EXISTS"):
                A.with_checkout_temporary_config(b"{}\n", lambda _: None, token)
            self.assertEqual(target.read_bytes(), b"pre-existing")
        finally:
            target.unlink(missing_ok=True)

    def test_real_author_writes_deterministic_closed_top_level_projection(self):
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first.json"
            second = Path(temporary) / "second.json"
            A.author_to(first); A.author_to(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            projection = json.loads(first.read_text(encoding="utf-8"))
            self.assertEqual(set(projection), {"schema", "scenario_id", "document", "hierarchy", "events", "assets", "xrefs", "source_recoveries", "source_disposition", "source_partition", "migration", "visual_review_units", "metrics"})
            self.assertEqual((len(projection["hierarchy"]), len(projection["assets"]), len(projection["xrefs"])), (185, 125, 42))
            self.assertEqual(sum(row["emit_link"] for row in projection["xrefs"]), 41)
            self.assertEqual([row["xref_id"] for row in projection["xrefs"] if row["xref_id"].startswith("p037-handout-21")], ["p037-handout-21-segment-01", "p037-handout-21-segment-02"])
            generated = [row for row in projection["events"] if row["type"] == "generated_navigation"]
            self.assertEqual([(row["content"]["family"], row["content"]["entry_count"]) for row in generated], [("toc", 135), ("handout_index", 41), ("map_index", 6), ("pregen_index", 12)])
            self.assertEqual(sum(row["content"]["entry_count"] for row in generated), 194)
            for event in generated:
                heading = [row for row in projection["events"] if row["type"] == "heading" and row["anchor"] == event["anchor"]]
                self.assertEqual(len(heading), 1)
                self.assertEqual(event["page"], heading[0]["page"])
                self.assertEqual(event["generated_placement"], {"after_event": heading[0]["event_id"]})
                self.assertEqual(event["order_key"][:3], [heading[0]["page"], heading[0]["order_key"][1], 5])

    def test_closed_projection_passes_both_public_top_level_schema_gates(self):
        builder_spec = importlib.util.spec_from_file_location("viral_v2_builder", ROOT / "scripts" / "build_scenario_master_en.py")
        verifier_spec = importlib.util.spec_from_file_location("viral_v2_verifier", ROOT / "scripts" / "verify_scenario_master_en.py")
        assert builder_spec and builder_spec.loader and verifier_spec and verifier_spec.loader
        builder = importlib.util.module_from_spec(builder_spec); builder_spec.loader.exec_module(builder)
        verifier = importlib.util.module_from_spec(verifier_spec); verifier_spec.loader.exec_module(verifier)
        projection = A.author()
        builder.v2_config(projection)
        verifier.v2_contract(projection)
        for mutate in (
            lambda value: value["visual_review_units"][0].__setitem__("review_id", "review:forged"),
            lambda value: value["visual_review_units"][0]["source_pages"].append(122),
            lambda value: value["visual_review_units"][-1].__setitem__("priority", True),
        ):
            altered = copy.deepcopy(projection); mutate(altered)
            with self.assertRaisesRegex(ValueError, "declaration|E_V2_REVIEW: declaration"):
                builder.v2_config(altered)
            with self.assertRaisesRegex(ValueError, "E_V2_REVIEW: declaration"):
                verifier.v2_contract(altered)

    def test_b1c4_closed_provenance_and_identity_mutations_fail_before_review(self):
        builder_spec = importlib.util.spec_from_file_location("viral_v2_builder_mutations", ROOT / "scripts" / "build_scenario_master_en.py")
        verifier_spec = importlib.util.spec_from_file_location("viral_v2_verifier_mutations", ROOT / "scripts" / "verify_scenario_master_en.py")
        builder = importlib.util.module_from_spec(builder_spec); builder_spec.loader.exec_module(builder)
        verifier = importlib.util.module_from_spec(verifier_spec); verifier_spec.loader.exec_module(verifier)
        projection = A.author()
        self.assertEqual({kind: sum(row["provenance"]["kind"] == kind for row in projection["assets"]) for kind in ("markdown_image_reference", "visual_region", "reviewed_provisional_full_page")}, {"markdown_image_reference": 16, "visual_region": 100, "reviewed_provisional_full_page": 9})
        mutations = (
            lambda value: value["assets"][0].pop("provenance"),
            lambda value: value["assets"][0]["provenance"].__setitem__("kind", "forged"),
            lambda value: next(row for row in value["assets"] if row["binary"])["binary"].__setitem__("sha256", "0" * 64),
            lambda value: value["migration"]["asset_rows"].reverse(),
            lambda value: value["migration"]["new_reviewed_targets"].reverse(),
        )
        for mutate in mutations:
            altered = copy.deepcopy(projection); mutate(altered)
            with self.assertRaisesRegex(ValueError, "B1c4|E_V2_(ASSET|MIGRATION)"):
                builder.v2_config(altered)
            with self.assertRaisesRegex(ValueError, "E_V2_(ASSET|MIGRATION)"):
                verifier.v2_contract(altered)

    def test_b1b_graph_splits_at_ledgers_and_retains_all_other_source(self):
        graph = A.source_graph(); partition = graph["source_partition"]
        self.assertEqual(graph["ledger_unit_count"], 186)
        self.assertEqual(len(graph["hierarchy"]), 168)
        self.assertGreater(len(partition["spans"]), 122)
        self.assertEqual(sum(row["end_byte"] - row["start_byte"] for row in partition["spans"]), 346793)
        for page in partition["pages"]:
            spans = [span for span in partition["spans"] if span["page"] == page["page"]]
            self.assertEqual(spans[0]["start_byte"], 0)
            self.assertEqual(spans[-1]["end_byte"], page["bytes"])
            self.assertEqual([span["span_id"] for span in spans], page["span_ids"])
            self.assertTrue(all(left["end_byte"] == right["start_byte"] for left, right in zip(spans, spans[1:])))
        ordinary = [event for event in graph["events"] if event["reviewed_unit_id"] is None]
        self.assertTrue(ordinary, "ordinary source prose must survive ledger overlays")
        self.assertEqual([event["order_key"] for event in graph["events"]], sorted(event["order_key"] for event in graph["events"]))

    def test_b1b_preserves_full_hierarchy_and_sealed_recoveries(self):
        graph = A.source_graph()
        titles = {row["reader_title"] for row in graph["hierarchy"]}
        self.assertIn("Viral", titles)
        self.assertTrue(all(row["parent_anchor"] is None or row["parent_anchor"] in {item["anchor"] for item in graph["hierarchy"]} for row in graph["hierarchy"]))
        self.assertTrue(all(123 not in row["source_pages"] and 124 not in row["source_pages"] for row in graph["hierarchy"]))
        self.assertEqual({row["source_text"] for row in graph["source_recoveries"]}, {"Cursed Plague Zombies", "New Mythos Tome"})
        kinds = {row["kind"] for row in graph["typed_units"]}
        self.assertTrue({"callout", "table", "equipment_card", "creature_statblock", "full_page_map", "physical_page_pair"} <= kinds)

    def test_ledger_schema_variants_are_normalized_before_interval_consumers(self):
        ledgers = A.approved_ledgers()
        self.assertEqual({row["ledger_schema"] for row in ledgers}, {"kb_creator.viral_boundary_ledger.v1", "kb_creator.viral.boundary_ledger.v2"})
        self.assertTrue(all(row["source_segments"] for row in ledgers))
        self.assertTrue(all("final_owner_anchor" not in row for row in ledgers if row["ledger_schema"].endswith(".v2")))
        self.assertTrue(any(row.get("reviewed_owner_label") == "Keeper Maps" for row in ledgers))
        intervals = A._ledger_intervals(A.PACKAGE)
        self.assertTrue(any(intervals[page] for page in range(41, 123)), "v2 ledgers must not silently disappear")
        typed = A.source_graph()["typed_units"]
        self.assertTrue({"logical_table", "callout_series", "run_in_series"} <= {row["ledger_kind"] for row in typed})

    def test_source_order_resolver_uses_selected_view_and_reports_internal_split(self):
        result = A.resolve_asset_source_order(
            comparison={"views": {
                "selected": {"blocks": [
                    {"raw_index": 9, "source_page": 2, "type": "image", "assets": ["images/a.jpg"]},
                    {"raw_index": 10, "source_page": 2, "type": "text", "text": "Target title"},
                ]},
                "other": {"blocks": [
                    {"raw_index": 1, "source_page": 2, "type": "text", "text": "Target title"},
                    {"raw_index": 2, "source_page": 2, "type": "image", "assets": ["images/a.jpg"]},
                ]},
            }},
            manifest_assets=[{"sha256": "A" * 64, "view": "selected", "source_path": "images/a.jpg"}],
            reader_assets=[{"asset_id": "asset-a", "source_page": 2, "binary": {"sha256": "A" * 64}}],
            events=[{"event_id": "event-target", "page": 2, "type": "text_fragment", "content": "Preceding prose.\n\n![old marker](x.jpg)\n\nTarget title\n\nFollowing prose."}],
        )
        row = result["rows"][0]
        self.assertEqual(row["status"], "needs_event_split")
        self.assertEqual(row["source_order"], [2, 9])
        self.assertIsNone(row["placement"])
        self.assertEqual(row["anchor_evidence"]["event_id"], "event-target")
        self.assertGreater(row["anchor_evidence"]["start_byte"], 0)

    def test_source_order_resolver_rejects_repeat_and_scopes_reused_binary(self):
        comparison = {"views": {"selected": {"blocks": [
            {"raw_index": 1, "source_page": 2, "type": "image", "assets": ["images/a.jpg"]},
            {"raw_index": 2, "source_page": 2, "type": "text", "text": "Repeated title"},
            {"raw_index": 3, "source_page": 3, "type": "image", "assets": ["images/b.jpg"]},
            {"raw_index": 4, "source_page": 3, "type": "text", "text": "Other title"},
        ]}}}
        rows = [
            {"asset_id": "repeat", "source_page": 2, "binary": {"sha256": "A" * 64}, "provenance": {"kind": "visual_region", "source_page": 2, "selected_view": "selected", "source_asset_reference": "images/a.jpg"}},
            {"asset_id": "reuse", "source_page": 3, "binary": {"sha256": "A" * 64}, "provenance": {"kind": "visual_region", "source_page": 3, "selected_view": "selected", "source_asset_reference": "images/b.jpg"}},
            {"asset_id": "front", "source_page": 4, "binary": {"sha256": "B" * 64}},
        ]
        result = A.resolve_asset_source_order(
            comparison=comparison,
            manifest_assets=[{"sha256": "A" * 64, "view": "selected", "source_path": "images/a.jpg"}, {"sha256": "A" * 64, "view": "selected", "source_path": "images/b.jpg"}],
            reader_assets=rows,
            events=[{"event_id": "repeat-event", "page": 2, "type": "text_fragment", "content": "Repeated title; Repeated title"}, {"event_id": "other-event", "page": 3, "type": "text_fragment", "content": "Other title"}],
            physical_units=[{"unit_id": "pair-4-5", "pages": [4, 5]}],
        )
        by_id = {row["asset_id"]: row for row in result["rows"]}
        self.assertEqual(by_id["repeat"]["reason"], "repeated_exact_text_within_event")
        self.assertEqual(by_id["reuse"]["placement"], {"before_event": "other-event"})
        self.assertEqual(by_id["front"]["status"], "resolved_physical_unit")
        self.assertEqual(by_id["front"]["physical_unit"], {"unit_id": "pair-4-5", "slot": 0})

    def test_real_input_source_order_audit_reports_conservative_readiness(self):
        readiness = A.asset_source_order_readiness()
        self.assertEqual(sum(readiness["counts"].values()), 93)
        self.assertGreater(readiness["counts"]["needs_event_split"], 0)
        self.assertGreater(readiness["counts"]["resolved_physical_unit"], 0)
        self.assertGreater(readiness["counts"]["ambiguous"], 0)
        rows = {row["asset_id"]: row for row in readiness["rows"]}
        cremation = next(row for asset_id, row in rows.items() if "f0ecf365" in asset_id)
        self.assertEqual(cremation["source_order"], [46, 784])
        self.assertEqual(cremation["status"], "needs_event_split")
        self.assertIsNone(cremation["placement"])
        self.assertGreater(cremation["anchor_evidence"]["start_byte"], 0)
        handout = next(row for asset_id, row in rows.items() if "8dfcf412" in asset_id)
        self.assertEqual(handout["source_order"], [78, 1236])
        self.assertNotEqual(handout["reason"], "no_exact_following_text_anchor")
        # The frozen Plots/Prologue decision stays authoritative, but this
        # conservative metadata resolver must not invent an anchor while the
        # current graph has several same-page exact Prologue occurrences.
        for prefix in ("b90cb9a3", "da0cac1c"):
            row = next(row for asset_id, row in rows.items() if prefix in asset_id)
            self.assertEqual(row["reason"], "ambiguous_exact_immediate_text_anchor")

    def test_exact_asset_anchor_splits_convert_only_proven_internal_offsets(self):
        readiness = A.asset_source_order_after_exact_splits()
        self.assertEqual(readiness["initial_counts"], {"placement_ready": 16, "needs_event_split": 50, "resolved_physical_unit": 14, "ambiguous": 13})
        self.assertEqual(readiness["counts"], {"placement_ready": 66, "needs_event_split": 0, "resolved_physical_unit": 14, "ambiguous": 13})
        self.assertGreater(readiness["refined_event_count"], 630)
        cremation = next(row for row in readiness["rows"] if "f0ecf365" in row["asset_id"])
        self.assertEqual(cremation["status"], "placement_ready")
        self.assertEqual(cremation["source_order"], [46, 784])
        self.assertIn("-asset-split-", cremation["placement"]["before_event"])

    def test_remaining_asset_cases_use_reviewed_standalone_or_physical_facts(self):
        base = A._author_b1c3()
        refined = A.split_events_at_asset_anchor_evidence(base["events"], A.asset_source_order_readiness()["rows"])
        resolved = A.reviewed_remaining_asset_anchors(refined)
        self.assertEqual(len(resolved), 13)
        self.assertEqual(resolved["viral-accepted-bc2ae2b3751eaf9754f625794f2d4648a03308dc3dc1042add097cc3649306b0"]["anchor"], "viral-one-night-in-perla-npcs-padre-angelo")
        self.assertEqual(resolved["viral-accepted-b90cb9a3752383888c733905588e9c3859b113e47f1f457057c72e33689a7585"]["placement_event_id"], resolved["viral-accepted-da0cac1c9c0c880a75d3be69c59e965d0b7b0f223f16a077072786c8af30083e"]["placement_event_id"])
        self.assertEqual(resolved["viral-accepted-9edcd9b27c46e8d689d4baeff43a55497376a581d87cf1e9ad8a0ea9dd63c28a"]["physical_unit_id"], "viral-map-ground-floor-basement")


if __name__ == "__main__":
    unittest.main()
