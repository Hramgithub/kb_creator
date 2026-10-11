"""Pure, fail-closed text selection for an already aligned OCR triangle."""
from __future__ import annotations
import hashlib,json
import re
from typing import Mapping, Any

VIEWS=("original_pipeline_txt","original_pipeline_ocr","raster_pipeline_ocr")
_QUOTE_CLASSES=(frozenset(("'", "\u2018", "\u2019")), frozenset(('"', "\u201c", "\u201d")))
_LETTER_SPACED_RUN=re.compile(r"(?<![A-Za-z])(?:[A-Z] ){3,}[A-Z](?![A-Za-z])")
_ADVISORY_SEMANTIC_KEYS=frozenset(("markdown_heading", "middle_title", "model_title", "v2_title"))
def _sha(text:str)->str:return hashlib.sha256(text.encode()).hexdigest().upper()
def _c0(text:str)->bool:return any(ord(c)<32 and c not in "\t\n\r" for c in text)

def output_semantic_projection(block: Mapping[str, Any]) -> str:
    """Return the semantic evidence that can change emitted reader structure.

    Title hints are preserved in the source alternatives but do not choose a
    Markdown level.  Every other key, including an unknown key, remains bound
    into the projection so a newly introduced signal cannot disappear silently.
    """
    evidence = block.get("semantic_evidence", {})
    if not isinstance(evidence, Mapping):
        raise ValueError("semantic evidence must be an object")
    return json.dumps(
        {key: value for key, value in evidence.items() if key not in _ADVISORY_SEMANTIC_KEYS},
        sort_keys=True,
        separators=(",", ":"),
    )

def _nontext(block:Mapping[str,Any])->tuple[Any,...]:
    return (block.get("type"),tuple(block.get("assets",[])),block.get("table_body",""),output_semantic_projection(block))

def _typographic_quote_equivalent(texts: tuple[str, str, str] | list[str]) -> bool:
    """Return true only for equal-length, positional ASCII/typographic quotes."""
    if len(texts) != 3 or len(set(texts)) == 1 or any(_c0(text) for text in texts):
        return False
    if len({len(text) for text in texts}) != 1:
        return False
    for chars in zip(*texts):
        if len(set(chars)) == 1:
            continue
        if not any(set(chars) <= allowed and (ascii_member := next((ch for ch in allowed if ord(ch) < 128), None)) in chars and any(ch in chars for ch in allowed if ch != ascii_member) for allowed in _QUOTE_CLASSES):
            return False
    return True

def _title_like(block: Mapping[str, Any]) -> bool:
    evidence=block.get("semantic_evidence", {})
    return (block.get("type") in {"header", "footer"} or isinstance(evidence, Mapping) and any(evidence.get(key) is True for key in ("markdown_heading", "middle_title", "model_title", "v2_title")))

def _title_ascii_case_equivalent(texts: tuple[str, str, str] | list[str]) -> bool:
    if len(texts) != 3 or any(_c0(text) for text in texts) or len({len(text) for text in texts}) != 1 or len(set(texts)) == 1:
        return False
    return all(all(a == b or (a.isascii() and b.isascii() and a.isalpha() and b.isalpha() and a.lower() == b.lower()) for a, b in zip(texts[0], text)) for text in texts[1:])

def _collapse_title_letter_spacing(text: str) -> str:
    return _LETTER_SPACED_RUN.sub(lambda match: match.group().replace(" ", ""), text)

def _title_letter_spacing_equivalent(texts: tuple[str, str, str] | list[str]) -> bool:
    if len(texts) != 3 or any(_c0(text) for text in texts) or len(set(texts)) == 1:
        return False
    collapsed=[_collapse_title_letter_spacing(text) for text in texts]
    return len(set(collapsed)) == 1 and any(collapsed_item != original for collapsed_item, original in zip(collapsed, texts))

def select_text(blocks:Mapping[str,Mapping[str,Any]], correction:Mapping[str,Any]|None=None)->dict[str,Any]:
    """Select only exact evidence; returns ``typed_hold`` where no rule applies.

    Correction must already be bound by the caller to the original-OCR block.
    """
    if set(blocks)!=set(VIEWS) or any(not isinstance(blocks[v].get("text"),str) for v in VIEWS):raise ValueError("closed three-view text blocks required")
    texts={v:blocks[v]["text"] for v in VIEWS}; identities={v:{"text_sha256":_sha(texts[v])} for v in VIEWS}
    if len({_nontext(blocks[v]) for v in VIEWS}) != 1:
        if len({tuple(blocks[v].get("assets", [])) for v in VIEWS}) != 1:
            code = "asset_difference"
        elif len({output_semantic_projection(blocks[v]) for v in VIEWS}) != 1:
            code = "semantic_conflict"
        else:
            code = "three_view_content_mismatch"
        return {"typed_hold": code, "per_view": identities}
    native,ocr,raster=texts[VIEWS[0]],texts[VIEWS[1]],texts[VIEWS[2]]
    chosen=output=reason=None; provenance=None
    if correction is not None:
        required={"page","view","raw_index","before","after","reason"}
        if (set(correction) != required or correction["view"] != VIEWS[1]
                or type(correction["page"]) is not int or correction["page"] < 1
                or type(correction["raw_index"]) is not int
                or correction["raw_index"] != blocks[VIEWS[1]].get("raw_index")
                or not all(isinstance(correction[k], str) and correction[k].strip() for k in ("before", "after", "reason"))
                or correction["before"] != ocr or correction["before"] == correction["after"]
                or _c0(correction["after"])):
            raise ValueError("invalid exact reviewed correction")
        chosen=VIEWS[1];output=correction["after"];reason="reviewed_source_correction";provenance=dict(correction)
    elif native==ocr==raster and not _c0(native):chosen=VIEWS[0];output=native;reason="three_view_exact"
    elif _c0(native) and ocr==raster:chosen=VIEWS[1];output=ocr;reason="native_text_corrupt_recovered"
    elif _typographic_quote_equivalent((native, ocr, raster)):
        chosen=VIEWS[0];output=native;reason="three_view_typographic_quote_equivalent"
    elif all(_title_like(blocks[view]) for view in VIEWS) and _title_ascii_case_equivalent((native, ocr, raster)):
        chosen=VIEWS[0];output=native;reason="three_view_title_ascii_case_equivalent.v1"
    elif all(_title_like(blocks[view]) for view in VIEWS) and _title_letter_spacing_equivalent((native, ocr, raster)):
        chosen=VIEWS[0];output=native;reason="three_view_title_letter_spacing_equivalent.v1"
    else:return {"typed_hold":"ocr_text_disagreement" if _c0(native) else "three_view_content_mismatch","per_view":identities}
    if _c0(output):raise ValueError("selected output contains C0 control")
    return {"chosen_view":chosen,"raw_index":blocks[chosen].get("raw_index"),"original_text":texts[chosen],"output_text":output,"reason":reason,"per_view":identities,"correction_provenance":provenance}
