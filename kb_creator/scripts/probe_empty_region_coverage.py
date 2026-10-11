"""Find local reader witnesses for visually recorded excerpts; never accept coverage."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from kb_creator.scripts.build_empty_region_visual_review import identity


def excerpt_matches(excerpt: str, text: str) -> list[dict]:
    """Only collapse whitespace; retain original text coordinates and punctuation."""
    if not isinstance(excerpt, str) or not excerpt.strip():
        raise ValueError("empty excerpt cannot prove a witness")
    normalized, starts, ends = [], [], []
    for token in re.finditer(r"\s+|\S", text):
        normalized.append(" " if token.group().isspace() else token.group())
        starts.append(token.start())
        ends.append(token.end())
    haystack, needle = "".join(normalized), " ".join(excerpt.split())
    result, start = [], 0
    while (offset := haystack.find(needle, start)) >= 0:
        end = offset + len(needle)
        result.append({"start_char": starts[offset], "end_char": ends[end-1], "text": text[starts[offset]:ends[end-1]]})
        start = offset + 1
    return result


def probe(manifest_path: Path, triage_path: Path, drafts: Path, packets: Path, output: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    triage = json.loads(triage_path.read_text(encoding="utf-8"))
    if sorted(row["region_id"] for row in triage["rows"]) != sorted(row["region_id"] for row in manifest["rows"]):
        raise ValueError("triage must account for every region exactly once")
    index = {row["region_id"]: row for row in manifest["rows"]}
    result_rows, authorities = [], {}
    for observation in triage["rows"]:
        region = index[observation["region_id"]]
        page = region["source_page"]
        candidates = []
        for neighbor in range(max(1, page-1), page+2):
            for kind, folder in (("reader", drafts), ("packet", packets)):
                path = folder / f"page-{neighbor:03d}.json"
                if not path.is_file():
                    continue
                data = json.loads(path.read_text(encoding="utf-8"))
                authorities[str(path)] = identity(path)
                if kind == "reader":
                    candidates.append({"kind": kind, "source_page": neighbor, "path": str(path), "text": data["markdown"]})
                else:
                    for block in data["views"][region["source_key"]["view"]]["blocks"]:
                        if block.get("text"):
                            candidates.append({"kind": kind, "source_page": neighbor, "path": str(path), "raw_index": block["raw_index"], "text": block["text"]})
        probes = []
        for excerpt in observation.get("excerpts", []):
            matches = []
            for candidate in candidates:
                spans = excerpt_matches(excerpt, candidate["text"])
                if spans:
                    matches.append({k: v for k, v in candidate.items() if k != "text"} | {"spans": spans})
            probes.append({"excerpt": excerpt, "matches": matches})
        result_rows.append({"region_id": observation["region_id"], "source_page": page,
                            "probes": probes, "all_excerpts_have_reader_candidate": bool(probes) and all(any(m["kind"] == "reader" for m in p["matches"]) for p in probes)})
    result = {"schema": "kb_creator.empty_region_excerpt_probe.v1", "state": "candidate_evidence_only",
              "limitation": "Matches prove only recorded excerpts; no complete region, layout, graphic, source correctness or final MASTER acceptance. Page scope is source page +/-1, never the whole book.",
              "visual_manifest": identity(manifest_path), "triage": identity(triage_path), "inputs": list(authorities.values()), "rows": result_rows}
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("visual-manifest", "triage", "drafts", "packets", "output"):
        parser.add_argument("--"+arg, type=Path, required=True)
    args = parser.parse_args()
    result = probe(args.visual_manifest, args.triage, args.drafts, args.packets, args.output)
    print(json.dumps({"regions": len(result["rows"]), "with_reader_candidates": sum(r["all_excerpts_have_reader_candidate"] for r in result["rows"])}))
