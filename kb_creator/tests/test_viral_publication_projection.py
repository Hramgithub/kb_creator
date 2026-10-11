"""Regression cases from the completed Viral reader review."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import author_viral_master_en_v2_config as author


@pytest.fixture(scope="module")
def publication():
    return author.author()


def test_reviewed_headings_keep_complete_source_titles(publication):
    titles = {h["reader_title"]: h for h in publication["hierarchy"] if h["representation"] == "heading"}
    for title in ("Welcome to Perla", "Santina Maria Salvatore", "Padre Angelo", "Hospital, Cellar", "Hospital, Ground Floor", "New Mythos Horrors", "New Mythos Tome", "New Spell"):
        assert title in titles
    assert "Welcome" not in titles
    assert "Infection" not in titles
    assert any("(Lead Investigator)" in title for title in titles)


def test_tables_join_continuations_and_preserve_order(publication):
    tables = {e["event_id"]: e["content"] for e in publication["events"] if e["type"] == "structured_unit" and e["content"]["kind"] == "table"}
    for unit, count in (("viral-table-rumors", 10), ("viral-table-signs", 10), ("viral-encounters-outdoor-table-p058-p059", 12), ("viral-encounters-hospital-table-p059", 12), ("viral-insanity-d10-table-p063", 10), ("viral-paranormal-phenomena-d10-table-p064", 10)):
        table = tables["structure:" + unit]
        assert table["row_count"] == count
        assert [row[0] for row in table["rows"]] == list(map(str, range(1, count + 1)))


def test_appendix_events_are_source_ordered(publication):
    events = publication["events"]
    positions = {e["event_id"]: i for i, e in enumerate(events)}
    assert positions["heading:viral-appendix-encounters"] < positions["heading:viral-appendix-encounters-outdoor"]
    assert positions["structure:viral-encounters-outdoor-table-p058-p059"] < positions["heading:viral-appendix-new-rules"]
    assert positions["structure:viral-encounters-catacomb-table-p060"] < positions["heading:viral-appendix-new-rules"]
    assert positions["structure:viral-advice-for-the-keeper-callout-p068:00"] < positions["heading:viral-player-handouts"]


def test_callout_ends_before_parent_prose_and_rooms_stay_inline(publication):
    events = {e["event_id"]: e for e in publication["events"]}
    appearance = events["structure:viral-em-app1:00"]
    assert appearance["content"]["kind"] == "callout"
    assert not any("Another Ghost Hunter Option" in line for line in appearance["content"]["body"])
    room = events["run-in:viral-isola-hospital-room-2e-isolation-ward"]
    assert room["content"]["label"] == "2E. Isolation Ward"
    assert "See 1J" in room["content"]["xref"]


def test_art_ownership_and_physical_pages(publication):
    assets = {a["asset_id"]: a for a in publication["assets"]}
    for digest in ("b90cb9a3752383888c733905588e9c3859b113e47f1f457057c72e33689a7585", "da0cac1c9c0c880a75d3be69c59e965d0b7b0f223f16a077072786c8af30083e"):
        asset = assets["viral-accepted-" + digest]
        assert asset["anchor"] == "viral-isola-plots-and-schemes"
        assert asset["placement"] == {"before_event": "heading:viral-isola-prologue"}
    full_pages = [a["source_page"] for a in assets.values() if a["provenance"]["kind"] == "reviewed_provisional_full_page"]
    assert sorted(full_pages) == [1, 26, 106, 107, 112, 114, 116, 118, 120, 122]
    assert all(a["source_page"] <= 122 for a in assets.values())


def test_reviewed_seed_asset_anchors_and_hud_suppression(publication):
    import build_scenario_master_en as builder

    events = publication["events"]
    positions = {event["event_id"]: index for index, event in enumerate(events)}
    reader_positions = {chunk.event["event_id"]: index for index, chunk in enumerate(builder.v2_typed_chunks(publication))}
    assets = {asset["asset_id"]: asset for asset in publication["assets"]}
    hero = assets["viral-accepted-4592e580aba8b9bad7a83eb2acf44e0480005e48b034ecd1ac436860efdbd137"]
    isola = assets["viral-provisional-isola-di-malamente-opening-page-26"]
    handout = assets["viral-accepted-9cddc3fc484dffdcce7654b3ebc058b362dbb265508a64d64d7485b33dc600c8"]
    assert hero["placement"] == {"before_event": "heading:viral-introduction"}
    assert reader_positions["asset:" + hero["asset_id"]] < reader_positions["heading:viral-introduction"] < reader_positions["heading:viral-introduction-summary"]
    assert isola["placement"] == {"before_event": "heading:viral-isola-di-malamente"}
    assert reader_positions["asset:" + isola["asset_id"]] < reader_positions["heading:viral-isola-di-malamente"]
    assert handout["anchor"] == "viral-handout-01"
    assert reader_positions["heading:viral-handout-01"] < reader_positions["asset:" + handout["asset_id"]] < reader_positions["heading:viral-handout-02a"]
    portrait_digests = {
        "aa51315c65b2339c22c6928a566dd2ade498b2afc817f9632cf30c09c5def4df",
        "d65de690f2341a83f4360d658e72d5fb916e7ae5bae952e366262017959f7fa6",
        "1ae78ddfdbcbd36dda84dcf3e34852206355f15827052b2714401493c4765bcb",
        "a5a54caa96d84e7f6df573ce0c5faa2e52e03213b89f22da03d043087b797201",
        "739a84561947691338ea011d7950446144e6156a4b5aba7924ab24a13b2c6d5f",
        "f76ae66f2313c44b030bb9cacce1023a95663ed4072a2d93ef8feca74c829004",
        "44587a041b63942e4703761b2c3065f459e5637a06e790447d0e0899c1d9a3f6",
        "4fd93a36f8650d97b80a9bde287442646eb741abefad7f520761332c4ec28834",
        "bc2ae2b3751eaf9754f625794f2d4648a03308dc3dc1042add097cc3649306b0",
    }
    portraits = [assets["viral-accepted-" + digest] for digest in portrait_digests]
    for asset in portraits:
        assert asset["placement"]["after_event"] == "heading:" + asset["anchor"]
        assert reader_positions["heading:" + asset["anchor"]] < reader_positions["asset:" + asset["asset_id"]]
    assert assets["viral-accepted-2a4ae067e92473cdad591d86e4d67066cb82094fc1251c23223a9c6561fb7089"]["placement"] != {"after_event": "heading:viral-spektral-krew-enoch-jeremiah-eakins"}
    assert assets["viral-accepted-cfb0587698f77c07987b9d5d50de4bf64d42b0bd5fa13e7276a5163ba787faf1"]["placement"] != {"after_event": "heading:viral-spektral-krew-emily-em-lavigne"}
    fly = assets["viral-accepted-2fbd31994da00cc5320dccf115f2aae8da89b5e5997e93ad5f853afbf13bad03"]
    book = assets["viral-accepted-dbe93023f78f2a8181d333207f407d3ada63c8f33a6f53889b4f3df7bc76a416"]
    assert reader_positions["asset:" + fly["asset_id"]] < reader_positions["heading:viral-appendix-new-mythos-tome"] < reader_positions["asset:" + book["asset_id"]]
    assert fly["anchor"] == "viral-appendix-new-mythos-horrors-reliquae"
    assert book["anchor"] == "viral-appendix-new-mythos-tome"
    assert assets["viral-accepted-c34aabc5bd16dfcb318cad3a11df583f9f15d4778f488832af69d182dc9d8201"]["anchor"] == "viral-handout-33"
    rendered = "\n".join(event["content"] for event in events if event["type"] == "text_fragment")
    assert "UNREDACTED" not in rendered and "22:13:35" not in rendered
    assert any(event["type"] == "heading" and event["content"] == "VIRAL" for event in events)


def test_reviewed_callout_boundaries_and_sight_split(publication):
    structures = [event for event in publication["events"] if event["type"] == "structured_unit"]
    notes = [event for event in structures if event["event_id"].startswith("structure:viral-keepers-notes-series-p041-p061")]
    bodies = [(event, "\n".join(event["content"].get("body", []))) for event in notes]
    overlook = [(event, body) for event, body in bodies if "The path over the rocks is difficult" in body]
    assert len(overlook) == 1
    assert "Reaching the end has the reward" in overlook[0][1]
    assert "The crew of the Vedetta" in overlook[0][1]
    crypt = [(event, body) for event, body in bodies if "The crypt altar is where Maya recommended" in body]
    assert len(crypt) == 1 and "The Witch Board connects" in crypt[0][1]
    catacombs = [(event, body) for event, body in bodies if "If the Investigators attempt to steal any grave goods" in body]
    assert len(catacombs) == 1
    assert "At this point, the Reliquae" in catacombs[0][1]
    assert "Scattered throughout the catacombs" in catacombs[0][1]
    climb = next(event for event in structures if event["event_id"] == "structure:viral-why-not-use-the-climb-skill-p051")
    assert climb["content"]["body"][0] == "Why Not Use the Climb Skill?"
    assert "Hastalÿk Unleashed" not in "\n".join(climb["content"]["body"])
    sight = [event for event in publication["events"] if event["page"] == 60 and event["type"] == "text_fragment" and "I See Dead People" in event["content"]]
    assert len(sight) == 1
    assert sight[0]["content"] == '"I See Dead People. When? All The Time... Unless I\'m Drunk."'
    angelo = "7a9686ecb0457b695002ce7b7daddcb9598b27e0d1501e10155e0c51f4eac85b"
    assert sum(event["type"] == "asset" and angelo in event["content"] for event in publication["events"]) == 1
    assert all(angelo not in str(event.get("content")) for event in structures)

    live = next(event for event in structures if event["event_id"] == "structure:viral-live-stream-callout-p048")
    live_body = "\n".join(live["content"]["body"])
    assert live_body.startswith("Live Stream\n\nAt this point")
    assert "During all of this" in live_body
    assert "12. Catacombs" not in live_body

    sight_panels = [event for event in structures if event["event_id"].startswith("structure:viral-sight-") and event["page"] == 61]
    assert [event["content"]["body"][0] for event in sight_panels] == [
        "Open the Sight", "Close the Sight", "Sensing a Presence",
        "Echoes of the Past", "Precognition", "Calm the Mind",
    ]
    sight_body = "\n".join("\n".join(event["content"]["body"]) for event in sight_panels)
    for cost in ("[Cost: 1 MP]", "[Cost: Special]", "[Cost: 3 MP]", "[Cost: 4 MP]", "[Cost: 5 MP]"):
        assert cost in sight_body
    assert "Drinking and hard drugs" not in sight_body
    assert "Keeper's Notes" not in sight_body


def test_multispan_run_ins_preserve_source_paragraph_boundaries(publication):
    events = {event["event_id"]: event for event in publication["events"]}
    super_fan = events["run-in:viral-runin-super"]
    ghost_hunter = events["run-in:viral-runin-ghost"]

    assert super_fan["content"]["xref"].count("\n\n") == 1
    assert ghost_hunter["content"]["xref"].count("\n\n") == 2
    assert next(binding for binding in super_fan["payload_bindings"] if binding["json_pointer"] == "/content/xref")["joiner"] == "\n\n"
    assert next(binding for binding in ghost_hunter["payload_bindings"] if binding["json_pointer"] == "/content/xref")["joiner"] == "\n\n"


def test_handout_index_precedes_first_handout_and_lists_are_compact(publication):
    import build_scenario_master_en as builder

    chunks = builder.v2_typed_chunks(publication)
    positions = {chunk.event["event_id"]: index for index, chunk in enumerate(chunks)}
    navigation = next(chunk for chunk in chunks if chunk.event["type"] == "generated_navigation" and chunk.event["content"]["family"] == "handout_index")
    assert positions["heading:viral-player-handouts"] < positions[navigation.event["event_id"]] < positions["heading:viral-handout-01"]

    text, _ = builder.v2_join_ledger(chunks)
    assert "- Maya cuts between the various feeds, showing different views of the grove.\n- All of the devices are looking good." in text
    assert "• Maya cuts between the various feeds" not in text
    assert "- BrutusBong: \\$30\n- Harvey3189: \\$10 ...Get closer!" in text


def test_all_source_bytes_and_xrefs_have_exact_bindings(publication):
    import build_scenario_master_en as builder
    totals = builder.v2_source_partition(publication["source_partition"], author.PACKAGE)
    assert totals["pages"] == 122
    builder.v2_b1c3_xref_closure(publication, author.ROOT)
    assert len(publication["xrefs"]) == 42


def test_two_source_recoveries_are_really_bound(publication):
    assert {r["source_text"] for r in publication["source_recoveries"]} == {"New Mythos Tome", "Cursed Plague Zombies"}
    events = {e["event_id"]: e for e in publication["events"]}
    for recovery in publication["source_recoveries"]:
        assert any(b["recovery_id"] == recovery["recovery_id"] for b in events[recovery["target_event_id"]]["payload_bindings"])


def test_complete_reader_projection_has_no_layout_or_internal_id_leaks(publication):
    import build_scenario_master_en as builder
    import verify_scenario_master_en as verifier
    text, rows = builder.v2_join_ledger(builder.v2_typed_chunks(publication))
    ledger = {r["event_id"]: r for r in rows}
    verifier.verify_v2_document(publication, text)
    verifier.v2_hierarchy_slices(publication, text, ledger)
    verifier.v2_structured_slices(publication, text, ledger)
    assert "\r" not in text and "\n\n\n" not in text
    assert "> Front:" not in text and "> Back:" not in text
    assert "](#None)" not in text
    for xref in publication["xrefs"]:
        row = ledger[xref["source_event_id"]]
        excerpt = text[row["start_char"]:row["end_char"]]
        expected = f"[{xref['reader_text']}](#{xref['target_anchor']})" if xref["emit_link"] else xref["reader_text"]
        assert expected in excerpt


def test_real_evidence_schemas_are_closed_and_blocking_closure_is_rejected(tmp_path):
    import json
    import build_scenario_master_en as builder
    import verify_scenario_master_en as verifier
    for name in ("semantic_unit_review.json", "closure_report.json"):
        original = json.loads((author.EVIDENCE / name).read_text(encoding="utf-8"))
        path = tmp_path / name
        for mutation in (None, "unknown_field", "invalid_content"):
            value = json.loads(json.dumps(original))
            if mutation == "unknown_field":
                value["unknown"] = True
            elif mutation == "invalid_content":
                if name == "closure_report.json":
                    value["unresolved_blocking_count"] = 1
                else:
                    value["decisions"][0]["decision"] = "invented"
            raw = (json.dumps(value) + "\n").encode()
            path.write_bytes(raw)
            inputs = {"decision_evidence": [{"path": name, "bytes": len(raw), "sha256": author.sha256_bytes(raw), "kind": original["schema"]}]}
            for check in (builder.v2_decision_catalogs, verifier.v2_decision_catalogs):
                if mutation is None:
                    assert check(inputs, tmp_path)
                else:
                    with pytest.raises(ValueError):
                        check(inputs, tmp_path)
