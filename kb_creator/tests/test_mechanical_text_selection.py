import pytest
import json
from pathlib import Path
from kb_creator.pipeline.mechanical_text_selection import select_text,VIEWS
def b(text,**x):return {"text":text,"type":"text","assets":[],"table_body":"","semantic_evidence":{},**x}
def tri(a,bv,c):return dict(zip(VIEWS,[b(a,raw_index=1),b(bv,raw_index=2),b(c,raw_index=3)]))
def test_clean_identical():assert select_text(tri("x","x","x"))["reason"]=="three_view_exact"
def test_corrupt_equal_ocr():assert select_text(tri("x\0","x","x"))["reason"]=="native_text_corrupt_recovered"
def test_corrupt_unequal_ocr():assert select_text(tri("x\0","x","y"))["typed_hold"]=="ocr_text_disagreement"
def test_correction_all_equal():
 r=select_text(tri("x","x","x"),{"page":1,"view":VIEWS[1],"raw_index":2,"before":"x","after":"z","reason":"r"});assert r["output_text"]=="z"
def test_correction_raster_diff():assert select_text(tri("x","x","y"),{"page":1,"view":VIEWS[1],"raw_index":2,"before":"x","after":"z","reason":"r"})["reason"]=="reviewed_source_correction"
def test_orthogonal_mismatch():
 x=tri("x\0","x","x");x[VIEWS[2]]["assets"]=["a.png"];assert select_text(x)["typed_hold"]=="asset_difference"
def test_bad_correction():
 with pytest.raises(ValueError):select_text(tri("x","x","x"),{"page":1,"view":VIEWS[1],"raw_index":2,"before":"bad","after":"z","reason":"r"})

@pytest.mark.parametrize("update", [{"raw_index": 3}, {"page": True}, {"after": "z\x01"}, {"after": "x"}])
def test_correction_selector_and_output_are_exact(update):
 row={"page":1,"view":VIEWS[1],"raw_index":2,"before":"x","after":"z","reason":"r"}
 row.update(update)
 with pytest.raises(ValueError):select_text(tri("x","x","x"), row)

def test_recovered_offsets_refer_to_each_actual_text():
 result=select_text(tri("bad\x01", "readable", "readable"))
 assert result["raw_index"]==2 and result["original_text"]=="readable"
 assert result["per_view"][VIEWS[0]]["text_sha256"]!=result["per_view"][VIEWS[1]]["text_sha256"]

def test_semantic_disagreement_is_not_text_recovery():
 blocks=tri("bad\x01", "readable", "readable")
 blocks[VIEWS[2]]["semantic_evidence"]={"text_level":1}
 assert select_text(blocks)["typed_hold"]=="semantic_conflict"

def test_advisory_semantic_signals_do_not_block_equal_emitted_structure():
 blocks=tri("readable", "readable", "readable")
 blocks[VIEWS[0]]["semantic_evidence"]={"text_level":2,"markdown_heading":True,"middle_title":False}
 blocks[VIEWS[1]]["semantic_evidence"]={"text_level":2,"markdown_heading":False,"middle_title":True}
 blocks[VIEWS[2]]["semantic_evidence"]={"text_level":2,"v2_title":True}
 assert select_text(blocks)["reason"]=="three_view_exact"

def test_unknown_semantic_signal_remains_a_fail_closed_hold():
 blocks=tri("readable", "readable", "readable")
 blocks[VIEWS[2]]["semantic_evidence"]={"text_level":None,"future_emitter_signal":True}
 assert select_text(blocks)["typed_hold"]=="semantic_conflict"

@pytest.mark.parametrize(
    ("native", "ocr", "raster"),
    [
        ("Alice's book", "Alice’s book", "Alice'" + "s book"),
        ('He said "go"', 'He said “go”', 'He said "go"'),
    ],
)
def test_typographic_quote_equivalence_selects_exact_native_bytes(native, ocr, raster):
    result = select_text(tri(native, ocr, raster))
    assert result["reason"] == "three_view_typographic_quote_equivalent"
    assert result["chosen_view"] == VIEWS[0]
    assert result["original_text"] == native
    assert result["output_text"] == native

def test_typographic_quote_equivalence_accepts_mixed_positions():
    result = select_text(tri("A's \"book\"", "A’s “book”", "A’s \"book\""))
    assert result["reason"] == "three_view_typographic_quote_equivalent"

@pytest.mark.parametrize("texts", [
    ("A's", "As", "A's"),
    ('A"', "A'", 'A"'),
    ("A‘", "A’", "A‘"),
    ("A–B", "A-B", "A–B"),
    ("A B", "AB", "A B"),
    ("Alpha", "Alpah", "Alpha"),
])
def test_typographic_quote_equivalence_rejects_non_declared_or_ambiguous_changes(texts):
    assert select_text(tri(*texts))["typed_hold"] == "three_view_content_mismatch"

def title_tri(a, bv, c, *, kind="text"):
    evidence = {"markdown_heading": True}
    return dict(zip(VIEWS, [b(a, raw_index=1, type=kind, semantic_evidence=evidence), b(bv, raw_index=1, type=kind, semantic_evidence=evidence), b(c, raw_index=1, type=kind, semantic_evidence=evidence)]))

def test_title_ascii_case_equivalence_selects_exact_native_bytes():
    result = select_text(title_tri("Chapter Two", "chapter two", "CHAPTER TWO"))
    assert result["reason"] == "three_view_title_ascii_case_equivalent.v1"
    assert result["output_text"] == "Chapter Two"

def test_title_letter_spacing_equivalence_selects_exact_native_bytes():
    result = select_text(title_tri("SECRETS", "S E C R E T S", "SECRETS"))
    assert result["reason"] == "three_view_title_letter_spacing_equivalent.v1"
    assert result["output_text"] == "SECRETS"

@pytest.mark.parametrize("blocks", [
    tri("Chapter Two", "chapter two", "CHAPTER Three"),
    tri("US", "us", "Us"),
    title_tri("A B", "AB", "A B"),
    title_tri("S E C", "SEC", "S E C"),
    tri("SECRETS", "S E C R E T S", "SECRETS"),
])
def test_title_rules_reject_scope_or_boundary_violations(blocks):
    assert select_text(blocks)["typed_hold"] == "three_view_content_mismatch"

def test_residual_census_rederives_bounded_title_rule_counts():
    root = Path(__file__).resolve().parents[1]
    census = json.loads((root / "working/night-three-books/n66-fear-residual-analysis/residual-census-v01.json").read_text(encoding="utf-8"))
    candidate = root / "working/fears-sharp-little-needles/reviewed/mechanical-n66-v01"
    pages = {}
    for page in range(1, 201):
        value = json.loads((candidate / "pages" / f"page-{page:03d}.json").read_text(encoding="utf-8"))
        for entry in value["entries"]:
            pages[(page, tuple(sorted((key["view"], key["raw_index"]) for key in entry["source_keys"])))]=entry
    counts = {"provable_title_ascii_case_equivalence": 0, "provable_title_letter_spacing_equivalence": 0}
    for row in census["rows"]:
        if row["classification"] not in counts:
            continue
        key = (row["source_page"], tuple(sorted((key["view"], key["raw_index"]) for key in row["source_keys"])))
        entry = pages[key]
        blocks = {alternative["view"]: alternative["blocks"][0] for alternative in entry["alternatives"]}
        result = select_text(blocks)
        expected = "three_view_title_ascii_case_equivalent.v1" if row["classification"].endswith("ascii_case_equivalence") else "three_view_title_letter_spacing_equivalent.v1"
        assert result["reason"] == expected
        counts[row["classification"]] += 1
    assert counts == {"provable_title_ascii_case_equivalence": 136, "provable_title_letter_spacing_equivalence": 2}
