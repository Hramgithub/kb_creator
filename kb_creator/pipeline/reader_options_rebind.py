"""Rebind reviewed reader decisions only when their exact language preimages survive."""
from __future__ import annotations

import copy
import json
import re
import shutil
from pathlib import Path
from typing import Any

from . import five_step_language as language
from . import reader_projection as reader
from .identity import assert_existing_path_components_are_not_reparse


def _local(root: Path, reference: str) -> Path:
    return reader._local(root, reference)


def _bindings(value: Any):
    if isinstance(value, dict):
        if set(("unit_id", "ru_sha256")) <= set(value):
            yield value
        for item in value.values():
            yield from _bindings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _bindings(item)


def _projection(root: Path) -> tuple[dict, Path, Path]:
    verified = language.verify_language_result(root)
    master = root / verified["master_ru"]["path"]
    manifest = language._read(root / "MASTER_RU.manifest.json")
    projection = root / manifest["ru_projection"]["path"]
    return language._read(projection), master, projection


def _same_source(old: dict, new: dict) -> None:
    if old["master_en"] != new["master_en"] or old["source_spans"] != new["source_spans"]:
        raise ValueError("reader rebind requires byte-identical archived MASTER_EN and source spans")
    fields = ("unit_id", "source_hash", "parent_unit_id", "part_index", "part_count")
    if [[row.get(key) for key in fields] for row in old["units"]] != [[row.get(key) for key in fields] for row in new["units"]]:
        raise ValueError("reader rebind requires identical ordered source unit metadata")


def _same_assets(old_root: Path, new_root: Path, old: dict) -> None:
    master = old_root / old["master_en"]["path"]
    for reference in language.legacy._structure_signature(master.read_text(encoding="utf-8"))["image_targets"]:
        if reader.identity(_local(old_root, reference)) != reader.identity(_local(new_root, reference)):
            raise ValueError("reader rebind requires byte-identical referenced assets")


def _reviewed_bindings(path: Path | None, old_units: dict, new_units: dict) -> tuple[dict[str, dict], dict | None]:
    if path is None:
        return {}, None
    assert_existing_path_components_are_not_reparse(path)
    path = path.resolve()
    if not path.is_file():
        raise ValueError("reviewed bindings must be a JSON file")
    try:
        rows = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError("reviewed bindings must be valid JSON") from exc
    if not isinstance(rows, list):
        raise ValueError("reviewed bindings must be a JSON list")
    result: dict[str, dict] = {}
    for row in rows:
        if (not isinstance(row, dict) or set(row) != {"unit_id", "prior_ru_sha256", "current_ru_sha256", "reason"}
                or not isinstance(row.get("unit_id"), str) or not row["unit_id"]
                or not isinstance(row.get("prior_ru_sha256"), str) or not isinstance(row.get("current_ru_sha256"), str)
                or not isinstance(row.get("reason"), str) or not row["reason"].strip()):
            raise ValueError("reviewed binding has unknown or missing fields")
        unit_id = row["unit_id"]
        if unit_id in result:
            raise ValueError("reviewed bindings must use distinct unit ids")
        if (unit_id not in old_units or unit_id not in new_units
                or old_units[unit_id]["ru_sha256"] != row["prior_ru_sha256"]
                or new_units[unit_id]["ru_sha256"] != row["current_ru_sha256"]):
            raise ValueError("reviewed binding identity is stale or unknown")
        if row["prior_ru_sha256"] == row["current_ru_sha256"]:
            raise ValueError("reviewed binding must authorize a changed unit")
        result[unit_id] = row
    return result, {"path": path.name, **reader.identity(path)}


def _selected_assets(options: dict):
    for choice in options["asset_choices"]:
        yield choice["selected_ref"], choice["selected"]
    for decision in options["display_roles"]:
        if isinstance(decision, dict) and decision.get("role") == "omit_extraction_duplicate_text":
            visual = decision["source_evidence"]["source_visual"]
            yield visual["path"], {key: visual[key] for key in ("bytes", "sha256")}
        if (isinstance(decision, dict) and decision.get("role") == "omit_source_artifact"
                and decision.get("text_policy") == "reviewed_whole_plain_block_v2"):
            visual = decision["source_evidence"]["source_visual"]
            yield visual["path"], {key: visual[key] for key in ("bytes", "sha256")}
        if isinstance(decision, dict) and decision.get("role") == "source_figure_regions":
            for region in decision.get("regions", []):
                if not isinstance(region, dict) or not isinstance(region.get("selected_ref"), str) or not isinstance(region.get("selected"), dict):
                    raise ValueError("source figure region selected asset is invalid")
                yield region["selected_ref"], region["selected"]


def rebind_reader_options(prior_result: Path, result: Path, options: Path, output: Path, reviewed_bindings: Path | None = None) -> dict:
    for path in (prior_result, result, options, output, *(() if reviewed_bindings is None else (reviewed_bindings,))):
        assert_existing_path_components_are_not_reparse(path)
    prior_result, result, options, output = (path.resolve() for path in (prior_result, result, options, output))
    if output.exists() or not output.parent.is_dir() or any(output.is_relative_to(path) for path in (prior_result, result)):
        raise ValueError("rebind output must be absent and outside inputs")
    old, old_master, old_projection = _projection(prior_result)
    new, new_master, new_projection = _projection(result)
    _same_source(old, new); _same_assets(prior_result, result, old)
    prior = reader.load_options(options, old_master, old_projection)
    old_units = {row["unit_id"]: row for row in old["units"]}; new_units = {row["unit_id"]: row for row in new["units"]}
    approved, evidence = _reviewed_bindings(reviewed_bindings, old_units, new_units)
    from . import reader_duplicate_text as duplicates
    def page_map(projection):
        import re
        current = None; pages = {}
        for unit in projection["units"]:
            marker = re.fullmatch(r"<!--\s*(?:source|pdf)-page-(\d+)\s*-->", unit["ru_text"].strip())
            if marker: current = int(marker[1])
            pages[unit["unit_id"]] = current
        return pages
    old_pages, new_pages = page_map(old), page_map(new)
    for decision in prior["display_roles"]:
        if not isinstance(decision, dict) or decision.get("role") != duplicates.ROLE:
            continue
        for key in ("unit", "retained"):
            uid = decision[key]["unit_id"]
            if uid not in old_units or uid not in new_units:
                raise ValueError(f"reader duplicate text operand {uid} is unknown in successor")
            if old_units[uid]["ru_sha256"] != new_units[uid]["ru_sha256"]:
                raise ValueError(f"reader duplicate text changed operand {uid}; fresh decision required")
            page = decision["source_page"]
            signature = duplicates._rendered(old_units[uid]["ru_text"])
            def cohort(projection, pages):
                return [row["unit_id"] for row in projection["units"] if pages[row["unit_id"]] == page
                        and row.get("parent_unit_id") is None and duplicates._candidate_signature(row) == signature]
            if (old_pages[uid] != page or new_pages[uid] != page
                    or cohort(old, old_pages) != cohort(new, new_pages)
                    or cohort(new, new_pages).index(uid) != decision[key]["match_ordinal"]):
                raise ValueError("reader duplicate text occurrence cohort changed; fresh decision required")
    for decision in prior["display_roles"]:
        if (not isinstance(decision, dict) or decision.get("role") != "omit_source_artifact"
                or decision.get("text_policy") != "reviewed_whole_plain_block_v2"):
            continue
        keys = ("unit", "retained_image_unit") if "retained_image_unit" in decision else ("unit",)
        for key in keys:
            uid = decision[key]["unit_id"]
            if (uid not in old_units or uid not in new_units
                    or old_units[uid]["ru_sha256"] != new_units[uid]["ru_sha256"]):
                raise ValueError(f"reader whole artifact changed operand {uid}; fresh decision required")
        cohort = decision.get("rendered_equivalent_cohort")
        if cohort is not None:
            for member in cohort["members"]:
                uid = member["unit_id"]
                if (uid not in old_units or uid not in new_units
                        or old_units[uid]["ru_sha256"] != new_units[uid]["ru_sha256"]
                        or old_units[uid]["ru_text"] != new_units[uid]["ru_text"]
                        or old_pages[uid] != new_pages[uid]):
                    raise ValueError(f"reader whole artifact cohort changed operand {uid}; fresh decision required")
    for decision in prior["display_roles"]:
        if not reader.guarded_reflow(decision, prior["display_roles"]):
            continue
        bindings = [*decision.get("units", []), *decision.get("intervening_units", [])]
        old_order = [row["unit_id"] for row in old["units"]]
        new_order = [row["unit_id"] for row in new["units"]]
        left_uid, right_uid = [row["unit_id"] for row in decision["units"]]
        if (left_uid not in new_order or right_uid not in new_order
                or old_order[old_order.index(left_uid) + 1:old_order.index(right_uid)]
                != new_order[new_order.index(left_uid) + 1:new_order.index(right_uid)]):
            raise ValueError("reader guarded reflow interval topology changed; fresh decision required")
        interval = {row["unit_id"] for row in decision["intervening_units"]}
        for role in prior["display_roles"]:
            if (not isinstance(role, dict) or role.get("role") != "repeated_title"
                    or not isinstance(role.get("unit"), dict)
                    or role["unit"].get("unit_id") not in interval):
                continue
            bindings.extend((role["unit"], role["retained"]))
        for pair in decision.get("intervening_asset_labels", []):
            bindings.extend((pair["unit"], pair["image"]))
            image_uid = pair["image"]["unit_id"]
            match = re.fullmatch(r"!\[[^\]]*\]\(([^)\s]+)\)", old_units[image_uid]["ru_text"].strip())
            if not match:
                raise ValueError("reader extended reflow map image operand is invalid")
            reference = match[1]
            if reader.identity(_local(prior_result, reference)) != reader.identity(_local(result, reference)):
                raise ValueError("reader extended reflow original map bytes changed; fresh decision required")
        for binding in decision["intervening_units"]:
            uid = binding["unit_id"]
            match = re.fullmatch(r"!\[[^\]]*\]\(([^)\s]+)\)", old_units[uid]["ru_text"].strip())
            if match and reader.identity(_local(prior_result, match[1])) != reader.identity(_local(result, match[1])):
                raise ValueError("reader guarded reflow original figure bytes changed; fresh decision required")
        for binding in bindings:
            uid = binding["unit_id"]
            if (uid not in old_units or uid not in new_units
                    or old_units[uid]["ru_sha256"] != new_units[uid]["ru_sha256"]):
                raise ValueError(f"reader extended reflow changed operand {uid}; fresh decision required")
    rebound = copy.deepcopy(prior); rebound.pop("options_sha256")
    reused = []
    authorized_occurrences: dict[str, int] = {}
    for binding in _bindings(rebound):
        unit_id, digest = binding["unit_id"], binding["ru_sha256"]
        if unit_id not in old_units or old_units[unit_id]["ru_sha256"] != digest:
            raise ValueError("reader option binding does not match prior projection")
        if new_units[unit_id]["ru_sha256"] != digest:
            authorization = approved.get(unit_id)
            if authorization is None:
                raise ValueError(f"reader option binding affected by changed unit: {unit_id}; fresh review required")
            binding["ru_sha256"] = authorization["current_ru_sha256"]
            authorized_occurrences[unit_id] = authorized_occurrences.get(unit_id, 0) + 1
        reused.append(unit_id)
    unused = set(approved) - set(authorized_occurrences)
    if unused:
        raise ValueError("reviewed binding is unused by reader options")
    rebound["master_ru"] = {"path": "MASTER_RU.md", **reader.identity(new_master)}
    rebound["ru_projection"] = {"path": "semantic_context/RU_PROJECTION.json", **reader.identity(new_projection)}
    rebound["options_sha256"] = reader.seal(rebound)
    if any(isinstance(row, dict) and (row.get("role") == duplicates.ROLE
                                     or reader.guarded_reflow(row, rebound["display_roles"])
                                     or (row.get("role") == "omit_source_artifact"
                                         and row.get("text_policy") == "reviewed_whole_plain_block_v2"))
           for row in rebound["display_roles"]):
        from . import five_step_docx as docx
        from translator.translator import markdown_to_review_html
        text = new_master.read_text(encoding="utf-8")
        semantic = docx._semantic_projection(new_master.parent, new_master, text)
        transport, _ = docx._transport_semantic_spans(text, semantic, semantic["spans"])
        body, toc, _ = markdown_to_review_html(transport, source_path=new_master,
                                               html_path=result / ".word-projection-base", blockquote_heading_offset=0)
        reader.project_reader_html(body, toc, new, rebound, options_path=options,
                                   master_root=new_master.parent)
    report = {"schema": "kb_creator.reader_options_rebind.v1", "state": "candidate_only", "review_transferred": False,
              "prior_result": {"master_ru": reader.identity(old_master), "ru_projection": reader.identity(old_projection)},
              "current_result": {"master_ru": reader.identity(new_master), "ru_projection": reader.identity(new_projection)},
              "options": reader.identity(options), "reused_unit_ids": sorted(set(reused)),
              "reviewed_bindings_evidence": evidence,
              "authorized_rebindings": [{**approved[unit_id], "occurrences": count}
                                      for unit_id, count in sorted(authorized_occurrences.items())]}
    def build(stage: Path) -> None:
        selected: dict[str, dict] = {}
        for reference, expected in _selected_assets(rebound):
            if reference in selected and selected[reference] != expected:
                raise ValueError("selected reader assets have conflicting references")
            selected[reference] = expected
        for reference, expected in selected.items():
            source = _local(options.parent, reference); target = _local(stage, reference)
            relative = target.relative_to(stage)
            reserved = (Path("reader_options.json"), Path("rebind-report.json"))
            if any(path == relative or path in relative.parents for path in reserved):
                raise ValueError("selected reader asset collides with generated rebind evidence")
            if not source.is_file() or reader.identity(source) != expected: raise ValueError("selected reader asset identity mismatch")
            target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
            if reader.identity(target) != expected: raise ValueError("selected reader asset changed while copying")
        language._write(stage / "reader_options.json", rebound)
        language._write(stage / "rebind-report.json", report)
    language._atomic(output, build)
    return report
