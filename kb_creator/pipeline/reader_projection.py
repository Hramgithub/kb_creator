"""Reviewed presentation decisions, applied after semantic Markdown transport.

The language master is immutable here. Every decision binds a unit preimage;
ambiguous HTML matches stop the build instead of guessing a nearby heading.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import unicodedata
from pathlib import Path
from typing import Any

from lxml import etree, html
from translator.translator import markdown_to_review_html

SCHEMA = "kb_creator.five_step_reader_options.v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def seal(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def norm(text: str) -> str:
    return " ".join(text.split())


def guarded_reflow(decision: dict, roles: list[dict]) -> bool:
    """Whether an interrupted interval needs archived page and media witnesses."""
    if not isinstance(decision, dict) or decision.get("role") != "interrupted_prose_reflow":
        return False
    intervening = decision.get("intervening_units")
    interval = ({row.get("unit_id") for row in intervening if isinstance(row, dict)}
                if isinstance(intervening, list) else set())
    return ("intervening_asset_labels" in decision or "join_mode" in decision
            or any(isinstance(role, dict) and role is not decision
                   and isinstance(role.get("unit"), dict)
                   and role["unit"].get("unit_id") in interval
                   and (role.get("role") == "repeated_title" or
                        (role.get("role") == "omit_source_artifact"
                         and role.get("text_policy") == "reviewed_whole_plain_block_v2"
                         and role.get("classification") == "source_furniture_text"))
                   for role in roles))


def _toc_label(source_row: str) -> str:
    """Remove Markdown list syntax and source page leaders from a reviewed row."""
    label = re.sub(r"^(?:[-+*]|\d+[.)])\s+", "", source_row)
    label, removed = re.subn(r"(?:\s*[.·](?:\s*[.·])+|\s*…+)\s*\d+(?:\s*[-–]\s*\d+)?$", "", label)
    if removed:
        return label.strip()
    return re.sub(r"\s+\d+(?:\s*[-–]\s*\d+)?$", "", label).strip()


def identity(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": sha(path)}


def _local(root: Path, ref: str) -> Path:
    if not isinstance(ref, str) or not ref or Path(ref).is_absolute() or ":" in ref:
        raise ValueError("reader asset path must be relative")
    path = root / ref
    if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
        raise ValueError("reader asset symlink is forbidden")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("reader asset escapes root")
    return path


def load_options(path: Path, master: Path, projection_path: Path, *,
                 master_name: str = "MASTER_RU.md",
                 projection_name: str = "semantic_context/RU_PROJECTION.json") -> dict:
    options = json.loads(path.read_text(encoding="utf-8-sig"))
    digest = options.pop("options_sha256", None)
    required = {"schema", "master_ru", "ru_projection", "source_toc", "body_links", "asset_choices", "hit_points", "display_roles"}
    if set(options) != required or options["schema"] != SCHEMA or digest != seal(options):
        raise ValueError("reader options schema or seal mismatch")
    if options["master_ru"] != {"path": master_name, **identity(master)} or options["ru_projection"] != {"path": projection_name, **identity(projection_path)}:
        raise ValueError("reader options master/projection binding mismatch")
    for item in options["asset_choices"]:
        original = _local(master.parent, item["original_ref"])
        selected = _local(path.parent, item["selected_ref"])
        if identity(original) != item["original"] or identity(selected) != item["selected"]:
            raise ValueError("reader asset identity mismatch")
        if not item.get("provenance") or not item.get("reason"):
            raise ValueError("reader asset provenance and reason required")
    for decision in options["display_roles"]:
        if not isinstance(decision, dict) or decision.get("role") != "interrupted_prose_reflow":
            continue
        for label in decision.get("intervening_asset_labels", []):
            if not isinstance(label, dict) or "reviewed_asset_choice" not in label:
                continue
            choice = label["reviewed_asset_choice"]
            fields = {"original_ref", "original", "selected_ref", "selected", "provenance", "reason"}
            if (not isinstance(choice, dict) or set(choice) != fields
                    or sum(item == choice for item in options["asset_choices"]) != 1
                    or sum(item.get("original_ref") == choice["original_ref"]
                           for item in options["asset_choices"]) != 1
                    or sum(item.get("selected_ref") == choice["selected_ref"]
                           for item in options["asset_choices"]) != 1):
                raise ValueError("retained map reviewed asset choice is missing, stale, or ambiguous")
    for decision in options["display_roles"]:
        if isinstance(decision, dict) and decision.get("role") == "omit_extraction_duplicate_text":
            from kb_creator.pipeline import reader_duplicate_text as duplicates
            duplicates._evidence(decision, options, path, _local, identity)
            continue
        if (isinstance(decision, dict) and decision.get("role") == "omit_source_artifact"
                and decision.get("text_policy") == "reviewed_whole_plain_block_v2"):
            from kb_creator.pipeline import reader_duplicate_text as duplicates
            duplicates._artifact_evidence(decision, options, path, _local, identity)
            continue
        if not isinstance(decision, dict) or decision.get("role") != "source_figure_regions":
            continue
        regions = decision.get("regions")
        if not isinstance(regions, list):
            raise ValueError("source figure regions must declare a regions list")
        for region in regions:
            if not isinstance(region, dict) or not isinstance(region.get("selected_ref"), str) or not isinstance(region.get("selected"), dict):
                raise ValueError("source figure region selected identity is invalid")
            selected = _local(path.parent, region["selected_ref"])
            if identity(selected) != region["selected"]:
                raise ValueError("source figure region selected bytes are stale")
    options["options_sha256"] = digest
    return options


def project_reader_html(body: str, generated_toc: list[dict], projection: dict, options: dict,
                        *, options_path: Path | None = None,
                        master_root: Path | None = None) -> tuple[str, list[dict], dict]:
    grouping_options = options
    # Pagination is deferred and may read units already owned by presentation roles.
    options = {**options, "display_roles": [row for row in options["display_roles"]
                if row.get("role") != "reviewed_statblock_group"]}
    tree = html.fragment_fromstring(body, create_parent="main")
    units = {u["unit_id"]: u for u in projection["units"]}
    pages = {}
    current = None
    for unit in projection["units"]:
        marker = re.fullmatch(r"<!--\s*(?:source|pdf)-page-(\d+)\s*-->", unit["ru_text"].strip())
        if marker:
            current = int(marker[1])
        pages[unit["unit_id"]] = current

    def bound(binding: dict) -> dict:
        unit = units.get(binding.get("unit_id"))
        if not unit or binding.get("ru_sha256") != unit["ru_sha256"]:
            raise ValueError("reader decision unit preimage mismatch")
        return unit

    cache = {}

    def heading_shape(node) -> str:
        clone = copy.deepcopy(node)
        clone.attrib.pop("id", None)  # Generated slugs may gain a collision suffix.
        clone.tail = None
        return html.tostring(clone, encoding="unicode", with_tail=False)

    def source_heading(text: str):
        fragment, _, _ = markdown_to_review_html(text, source_path=Path("unit.md"),
                                                   html_path=Path("unit.html"),
                                                   blockquote_heading_offset=0)
        blocks = html.fragment_fromstring(fragment, create_parent="main")
        return blocks[0] if len(blocks) == 1 and blocks[0].tag in {
            "h1", "h2", "h3", "h4", "h5", "h6"} else None

    def locate(binding: dict):
        unit = bound(binding)
        uid = unit["unit_id"]
        if uid in cache:
            return cache[uid]
        section = tree.xpath(f'.//section[@data-page="{pages[uid]:03d}"]') if pages[uid] is not None else [tree]
        if len(section) != 1:
            raise ValueError(f"reader source page missing/ambiguous: {uid}")
        text = unit["ru_text"]
        image = re.fullmatch(r'!\[[^\]]*\]\(([^)]+)\)', text.strip())
        if image:
            found = section[0].xpath('.//img[@src=$ref]', ref=image[1])
            matches = [e.getparent() if e.getparent().tag == "figure" else e for e in found]
        else:
            heading = source_heading(text)
            if heading is not None:
                shape = heading_shape(heading)
                candidates = [e for e in section[0].iterdescendants()
                              if isinstance(e.tag, str) and e.tag == heading.tag
                              and heading_shape(e) == shape]
            else:
                fragment, _, _ = markdown_to_review_html(text, source_path=Path("unit.md"), html_path=Path("unit.html"), blockquote_heading_offset=0)
                want = norm(html.fragment_fromstring(fragment, create_parent="main").text_content())
                candidates = [e for e in section[0].iterdescendants() if isinstance(e.tag, str) and e.tag in {"h1","h2","h3","h4","h5","h6","p","li","ul","ol","blockquote","table"} and norm(e.text_content()) == want]
            # A list item may be wrapped in a blockquote: select the smallest exact block.
            matches = [e for e in candidates if not any(child in candidates for child in e.iterdescendants())]
        if len(matches) != 1:
            raise ValueError(f"reader target {uid} has {len(matches)} exact HTML matches")
        cache[uid] = matches[0]
        return matches[0]

    def bind_heading_occurrence(binding, witness):
        if (not isinstance(witness, dict) or set(witness) != {"ordinal", "cohort"}
                or type(witness["ordinal"]) is not int or witness["ordinal"] < 0
                or not isinstance(witness["cohort"], list)):
            raise ValueError("heading occurrence witness is malformed")
        if not isinstance(binding, dict) or set(binding) != {"unit_id", "ru_sha256"}:
            raise ValueError("heading occurrence requires an exact unit binding")
        unit = bound(binding)
        uid = unit["unit_id"]
        page = pages[uid]
        heading = source_heading(unit["ru_text"])
        if page is None or heading is None:
            raise ValueError("heading occurrence requires one source-page heading")
        cohort = [candidate for candidate in projection["units"]
                  if pages[candidate["unit_id"]] == page
                  and candidate["ru_text"] == unit["ru_text"]]
        bindings = [{key: candidate[key] for key in ("unit_id", "ru_sha256")}
                    for candidate in cohort]
        if (len(cohort) < 2 or witness["cohort"] != bindings
                or witness["ordinal"] >= len(cohort)
                or cohort[witness["ordinal"]]["unit_id"] != uid):
            raise ValueError("heading occurrence cohort differs from exact source order")
        if any(hashlib.sha256(candidate["ru_text"].encode("utf-8")).hexdigest().upper()
               != candidate["ru_sha256"] for candidate in cohort):
            raise ValueError("heading occurrence source bytes differ from bound hashes")
        sections = tree.xpath(f'.//section[@data-page="{page:03d}"]')
        if len(sections) != 1:
            raise ValueError("heading occurrence source page is missing")
        shape = heading_shape(heading)
        matches = [node for node in sections[0].iterdescendants()
                   if isinstance(node.tag, str) and node.tag == heading.tag
                   and heading_shape(node) == shape]
        if len(matches) != len(cohort):
            raise ValueError("heading occurrence DOM count differs from source cohort")
        for candidate, node in zip(cohort, matches):
            existing = cache.get(candidate["unit_id"])
            if existing is not None and existing is not node:
                raise ValueError("heading occurrence conflicts with a prior owner")
            cache[candidate["unit_id"]] = node
        return matches

    # Bind against untouched DOM; repeating this proof later forbids remapping.
    for decision in options["display_roles"]:
        if not isinstance(decision, dict) or "heading_occurrence" not in decision:
            continue
        role = decision.get("role")
        if (role not in {"repeated_title", "prose_presentation", "reviewed_block_relocation"}
                or (role == "repeated_title"
                    and decision.get("standalone_running_heading") is not True)):
            raise ValueError("heading occurrence requires a standalone repeated title, prose presentation or relocation destination")
        if role == "reviewed_block_relocation" and not isinstance(decision.get("destination"), dict):
            raise ValueError("heading occurrence relocation destination is malformed")
        binding = (decision.get("destination", {}).get("unit")
                   if role == "reviewed_block_relocation" else decision.get("unit"))
        bind_heading_occurrence(binding, decision["heading_occurrence"])

    anchors = {}

    def anchor(binding: dict) -> str:
        uid = bound(binding)["unit_id"]
        if uid not in anchors:
            node = locate(binding)
            # Keep existing slug IDs because source-authored links may use them.
            anchors[uid] = node.get("id") or f"reader-{uid}"
            node.set("id", anchors[uid])
        return anchors[uid]

    rich_fragments = {}

    def rich_fragment(unit):
        uid = unit["unit_id"]
        if uid not in rich_fragments:
            fragment, _, _ = markdown_to_review_html(unit["ru_text"], source_path=Path("unit.md"), html_path=Path("unit.html"), blockquote_heading_offset=0)
            blocks = html.fragment_fromstring(fragment, create_parent="main")
            rich_fragments[uid] = blocks[0] if len(blocks) == 1 and blocks[0].tag in {"h1","h2","h3","h4","h5","h6","p"} else None
        return rich_fragments[uid]

    def rich_node(binding: dict):
        if set(binding) != {"unit_id", "ru_sha256", "match_ordinal"} or type(binding["match_ordinal"]) is not int or binding["match_ordinal"] < 0:
            raise ValueError("rich TOC node binding is malformed")
        unit = bound(binding); page = pages[unit["unit_id"]]
        section = tree.xpath(f'.//section[@data-page="{page:03d}"]') if page is not None else [tree]
        if len(section) != 1:
            raise ValueError("rich TOC source page is missing")
        block = rich_fragment(unit)
        if block is None or unit["ru_text"].lstrip().startswith("<"):
            raise ValueError("rich TOC unit must contain one Markdown block")
        want = norm(block.text_content())
        choices = [e for e in section[0].iterdescendants() if isinstance(e.tag, str)
                   and e.tag in {"h1","h2","h3","h4","h5","h6","p"} and norm(e.text_content()) == want]
        matching_units = []
        for candidate in projection["units"]:
            if pages[candidate["unit_id"]] != page:
                continue
            candidate_block = rich_fragment(candidate)
            if candidate_block is not None and norm(candidate_block.text_content()) == want:
                matching_units.append(candidate["unit_id"])
        if (len(matching_units) != len(choices) or binding["match_ordinal"] >= len(choices)
                or matching_units.index(unit["unit_id"]) != binding["match_ordinal"]):
            raise ValueError("rich TOC node ordinal differs from projection order")
        return unit, choices[binding["match_ordinal"]]

    def rich_anchor(binding: dict) -> str:
        unit, node = rich_node(binding)
        if node.tag not in {"h1","h2","h3","h4","h5","h6"}:
            raise ValueError("rich TOC title target must be a heading")
        uid = unit["unit_id"]
        if uid not in anchors:
            anchors[uid] = node.get("id") or f"reader-{uid}"
            node.set("id", anchors[uid])
        return anchors[uid]

    def rendered(component: dict, *, role: str) -> tuple[dict, Any, str]:
        required = ({"node", "source_markdown", "rendered_markdown", "page_suffix_removal"}
                    if role == "byline" else {"node", "source_markdown"})
        if set(component) != required:
            raise ValueError("rich TOC component fields are invalid")
        unit, node = rich_node(component["node"])
        source = component["source_markdown"]
        if not isinstance(source, str) or source != unit["ru_text"]:
            raise ValueError("rich TOC source markdown preimage mismatch")
        value = component.get("rendered_markdown", source)
        removal = component.get("page_suffix_removal")
        if removal is None:
            if value != source: raise ValueError("rich TOC changed source without reviewed suffix removal")
        else:
            if role != "byline" or set(removal) != {"operation","source_suffix","printed_page","reason"} or removal["operation"] != "remove_exact_terminal_printed_page_suffix" or type(removal["printed_page"]) is not int or removal["printed_page"] < 1 or not isinstance(removal["reason"], str) or not removal["reason"].strip():
                raise ValueError("rich TOC suffix removal is invalid")
            suffix = removal["source_suffix"]
            if not isinstance(suffix, str) or not source.endswith(suffix) or source.count(suffix) != 1 or not re.fullmatch(r"(?:\s*[.·…][.·…\s]*|\s+)" + re.escape(str(removal["printed_page"])), suffix):
                raise ValueError("rich TOC suffix removal does not match terminal printed page")
            if value != source.removesuffix(suffix).rstrip(): raise ValueError("rich TOC suffix removal changed additional text")
        return unit, node, value

    def copy_inline(destination: Any, source: Any, replacement: str | None = None) -> None:
        """Preserve reviewed inline Markdown unless a sealed suffix transform applies."""
        if replacement is not None and replacement != source.text_content():
            fragment, _, _ = markdown_to_review_html(replacement, source_path=Path("unit.md"), html_path=Path("unit.html"), blockquote_heading_offset=0)
            blocks = html.fragment_fromstring(fragment, create_parent="main")
            if len(blocks) != 1 or blocks[0].tag != "p":
                raise ValueError("rich TOC metadata must render to one paragraph")
            source = blocks[0]
        destination.text = source.text
        for child in source:
            destination.append(copy.deepcopy(child))

    toc = options["source_toc"]
    state = toc.get("state")
    report: dict[str, Any] = {
        "toc_mode": state, "links": [], "display_roles": [], "hit_points": [],
        "asset_choices": [], "asset_legends": [], "omitted_artifacts": [], "review_anchors": [],
        "source_figure_regions": [], "omitted_text_duplicates": [], "retained_image_dependencies": [],
        "reflow_page_witness": [], "reflow_dependencies": [], "retained_link_dependencies": [],
        "standalone_running_headings": [],
    }
    if state == "unresolved" or state not in {"present", "absent"}:
        raise ValueError("source TOC classification unresolved")
    if not toc.get("source_pdf_sha256") or not toc.get("reason"):
        raise ValueError("source TOC requires source evidence")
    if state == "present":
        presentation = toc.get("presentation")
        if presentation is not None:
            if set(toc) != {"state","source_pdf_sha256","reason","presentation"} or set(presentation) != {"schema","heading","entries","duplicate_byline_omissions"} or presentation["schema"] != "kb_creator.source_toc_presentation.rich_entries.v1":
                raise ValueError("rich TOC presentation is invalid")
            heading = presentation["heading"]
            if set(heading) != {"node","source_markdown"}:
                raise ValueError("rich TOC heading is invalid")
            heading_unit, first = rich_node(heading["node"])
            if heading["source_markdown"] != heading_unit["ru_text"] or first.tag not in {"h1","h2","h3","h4","h5","h6"}:
                raise ValueError("rich TOC heading preimage is invalid")
            entries = presentation["entries"]
            if not isinstance(entries, list) or not entries or not isinstance(presentation["duplicate_byline_omissions"], list): raise ValueError("rich TOC entries are invalid")
            nav = etree.Element("nav", id="toc", **{"data-toc-layout":"rich-source","data-toc-numbering":"none"})
            nav_heading = etree.SubElement(nav, "h1"); copy_inline(nav_heading, first); listing = etree.SubElement(nav, "ol")
            claimed = [first]; claimed_pages = {id(first): pages[heading_unit["unit_id"]]}; effective = []; entry_ids = set(); synopsis_nodes = {}; byline_display = {}; display_rows = []; previous_page = -1
            component_ids = [heading_unit["unit_id"]]
            target_ids = []
            components = []
            for entry in entries:
                if set(entry) != {"entry_id","source_page","title","byline","synopsis"} or not isinstance(entry["entry_id"], str) or not entry["entry_id"] or entry["entry_id"] in entry_ids or type(entry["source_page"]) is not int or entry["source_page"] < previous_page:
                    raise ValueError("rich TOC entry order or identity is invalid")
                entry_ids.add(entry["entry_id"]); previous_page = entry["source_page"]
                title = entry["title"]
                if set(title) != {"node","source_markdown","target","level"} or type(title["level"]) is not int or title["level"] not in range(1, 7): raise ValueError("rich TOC title is invalid")
                title_unit, title_node = rich_node(title["node"])
                if title["source_markdown"] != title_unit["ru_text"] or title_node.tag not in {"h1","h2","h3","h4","h5","h6"} or pages[title_unit["unit_id"]] != entry["source_page"]: raise ValueError("rich TOC title preimage is invalid")
                by_unit, by_node, by_text = rendered(entry["byline"], role="byline"); sy_unit, sy_node, sy_text = rendered(entry["synopsis"], role="synopsis")
                if pages[by_unit["unit_id"]] != entry["source_page"] or pages[sy_unit["unit_id"]] != entry["source_page"] or by_node.tag != "p" or sy_node.tag != "p": raise ValueError("rich TOC metadata role is invalid")
                claimed.extend((title_node, by_node, sy_node)); claimed_pages.update({id(title_node): entry["source_page"], id(by_node): entry["source_page"], id(sy_node): entry["source_page"]}); target = rich_anchor(title["target"])
                component_ids.extend((title_unit["unit_id"], by_unit["unit_id"], sy_unit["unit_id"]))
                target_ids.append(title["target"]["unit_id"])
                components.append({"entry_id": entry["entry_id"], "title": title_unit["unit_id"], "byline": by_unit["unit_id"], "synopsis": sy_unit["unit_id"], "page_suffix_removal": entry["byline"]["page_suffix_removal"]})
                synopsis_nodes[entry["entry_id"]] = sy_node
                byline_display[entry["entry_id"]] = by_node.text_content().removesuffix(entry["byline"]["page_suffix_removal"]["source_suffix"] if entry["byline"]["page_suffix_removal"] else "").rstrip()
                li = etree.SubElement(listing, "li"); a = etree.SubElement(li, "a", href="#" + target); copy_inline(a, title_node)
                by = etree.SubElement(li, "p", **{"class":"byline"}); copy_inline(by, by_node, by_text)
                synopsis = etree.SubElement(li, "p", **{"class":"synopsis"}); copy_inline(synopsis, sy_node, sy_text)
                display_rows.append({"title": "".join(a.itertext()), "byline": "".join(by.itertext()), "synopsis": "".join(synopsis.itertext())})
                effective.append({"level": title["level"], "title": title_node.text_content(), "href": target})
                report["links"].append({"kind":"toc", "label":title_node.text_content(), "target":target, "unit_id":title["target"]["unit_id"]})
            omissions = presentation["duplicate_byline_omissions"]
            omitted_display = []
            for omission in omissions:
                if set(omission) != {"node","source_markdown","page_suffix_removal","duplicate_of_entry_id","reason","source_evidence"} or omission["duplicate_of_entry_id"] not in entry_ids or not omission["reason"] or not omission["source_evidence"]:
                    raise ValueError("rich TOC duplicate omission is invalid")
                omitted_unit, omitted_node, omitted_text = rendered({"node": omission["node"], "source_markdown": omission["source_markdown"], "rendered_markdown": omission["source_markdown"].removesuffix(omission["page_suffix_removal"].get("source_suffix", "")).rstrip(), "page_suffix_removal": omission["page_suffix_removal"]}, role="byline")
                retained = next(entry for entry in entries if entry["entry_id"] == omission["duplicate_of_entry_id"])
                retained_text = byline_display[omission["duplicate_of_entry_id"]]
                normalize_credit = lambda text: norm(unicodedata.normalize("NFKC", text)).casefold()
                if pages[omitted_unit["unit_id"]] != retained["source_page"] or normalize_credit(omitted_text) != normalize_credit(retained_text) or omitted_node.getprevious() is not synopsis_nodes[omission["duplicate_of_entry_id"]]:
                    raise ValueError("rich TOC duplicate omission is not adjacent/equal")
                if any(isinstance(node.tag, str) for node in omitted_node.itersiblings()):
                    raise ValueError("rich TOC duplicate omission must end its source page")
                claimed.append(omitted_node)
                component_ids.append(omitted_unit["unit_id"])
                claimed_pages[id(omitted_node)] = retained["source_page"]
                omitted_display.append(omitted_node.text_content())
            # Source-page sections keep projected Markdown blocks as direct
            # children.  Every visible block between the first and last rich
            # claim must be declared, otherwise replacing the range could
            # retain an unreviewed TOC fragment.
            if len(set(component_ids)) != len(component_ids) or len({id(node) for node in claimed}) != len(claimed) or len(set(target_ids)) != len(target_ids) or set(target_ids).intersection(component_ids):
                raise ValueError("rich TOC components or targets have duplicate ownership")
            for page in set(claimed_pages.values()):
                section = tree.xpath(f'.//section[@data-page="{page:03d}"]')
                page_claimed = [node for node in claimed if claimed_pages[id(node)] == page]
                visible = [node for node in section[0] if isinstance(node.tag, str)]
                if any(node not in visible for node in page_claimed):
                    raise ValueError("rich TOC source blocks must be direct page children")
                positions = [visible.index(node) for node in page_claimed]
                ordered_components = [node for node in page_claimed if node not in [rich_node(omission["node"])[1] for omission in omissions]]
                if [visible.index(node) for node in ordered_components] != sorted(visible.index(node) for node in ordered_components):
                    raise ValueError("rich TOC components differ from DOM order")
                if not positions or any(node not in page_claimed for node in visible[min(positions):max(positions) + 1]):
                    raise ValueError("rich TOC source page has an undeclared interstitial visible block")
            parent = first.getparent(); parent.insert(parent.index(first), nav)
            for node in claimed:
                node.getparent().remove(node)
            report["rich_source_toc"] = {"source_pages": sorted({entry["source_page"] for entry in entries}), "entry_count": len(entries), "display_rows": display_rows, "omitted_display": omitted_display, "components": components, "duplicate_byline_omissions": copy.deepcopy(omissions)}
        else:
            source_units = toc["units"]
            nodes = [locate(binding) for binding in source_units]
            if len(nodes) < 2 or len({id(node) for node in nodes}) != len(nodes):
                raise ValueError("source TOC span is invalid")
            parent = nodes[0].getparent()
            if any(node.getparent() is not parent for node in nodes):
                raise ValueError("source TOC nodes must share a parent")
            positions = [parent.index(node) for node in nodes]
            if positions != list(range(positions[0], positions[0] + len(nodes))):
                raise ValueError("source TOC span must be contiguous")
            raw_rows = [re.sub(r"^#{1,6}\s+", "", line.strip()) for item in source_units[1:] for line in bound(item)["ru_text"].splitlines() if line.strip()]
            if len(raw_rows) != len(toc["entries"]):
                raise ValueError("source TOC row coverage mismatch")
            nav = etree.Element("nav", id="toc", **{"data-toc-layout": "hierarchical", "data-toc-numbering": "none"})
            title = etree.SubElement(nav, "h1"); title.text = nodes[0].text_content()
            listing = etree.SubElement(nav, "ol")
            effective = []
            for raw, entry in zip(raw_rows, toc["entries"]):
                if entry["source_text"] != raw or entry["level"] not in (1, 2, 3, 4, 5, 6):
                    raise ValueError("source TOC row preimage/level mismatch")
                label = _toc_label(raw)
                target = anchor(entry["target"])
                li = etree.SubElement(listing, "li", **{"class": f"toc-level-{entry['level']}"})
                a = etree.SubElement(li, "a", href=f"#{target}"); a.text = label
                effective.append({"level": entry["level"], "title": label, "href": target})
                report["links"].append({"kind": "toc", "label": label, "target": target, "unit_id": entry["target"]["unit_id"]})
            parent.insert(positions[0], nav)
            for node in nodes:
                parent.remove(node)
    else:
        # Explicit source-absence classification is the only generated-TOC route.
        effective = generated_toc
        if effective:
            from kb_creator.pipeline.five_step_docx import _toc_html
            tree.insert(0, html.fragment_fromstring(_toc_html(effective)))

    from kb_creator.pipeline import reader_duplicate_text as duplicates
    reflow_guarded_intervals = {}
    guarded_decisions = set()
    unit_order = [unit["unit_id"] for unit in projection["units"]]
    for role in options["display_roles"]:
        if not guarded_reflow(role, options["display_roles"]):
            continue
        required = {"role", "units", "intervening_units", "source_evidence", "reason"}
        optional = {"intervening_handout_groups", "intervening_asset_labels", "join_mode"}
        bindings = ([*role["units"], *role["intervening_units"]]
                    if isinstance(role.get("units"), list)
                    and isinstance(role.get("intervening_units"), list) else [])
        if (not required <= set(role) or set(role) - required - optional
                or not isinstance(role.get("source_evidence"), str) or not role["source_evidence"].strip()
                or not isinstance(role.get("reason"), str) or not role["reason"].strip()
                or not isinstance(role.get("units"), list) or len(role["units"]) != 2
                or not isinstance(role.get("intervening_units"), list) or not role["intervening_units"]
                or any(not isinstance(binding, dict) or set(binding) != {"unit_id", "ru_sha256"}
                       for binding in bindings)
                or role.get("join_mode", "space") not in {"space", "word"}
                or ("intervening_asset_labels" in role and
                    (not isinstance(role["intervening_asset_labels"], list)
                     or not role["intervening_asset_labels"]))):
            raise ValueError("guarded reflow requires exact reviewed fields and nonempty supplied labels")
        units_for_role = [bound(binding) for binding in bindings]
        left, right = [unit_order.index(unit["unit_id"]) for unit in units_for_role[:2]]
        if (right <= left or [unit["unit_id"] for unit in units_for_role[2:]]
                != unit_order[left + 1:right]):
            raise ValueError("guarded reflow interval differs from authoritative projection")
        guarded_decisions.add(id(role))
        for unit in units_for_role[2:]:
            uid = unit["unit_id"]
            if uid in reflow_guarded_intervals:
                raise ValueError("guarded reflow intermediate ownership overlaps")
            reflow_guarded_intervals[uid] = id(role)
    duplicate_rows = duplicates.prepare(tree, projection, options, pages, bound,
                                        options_path=options_path, local=_local, identity=identity)
    artifact_rows = duplicates.prepare_artifacts(tree, projection, options, pages, bound, duplicate_rows,
                                                 options_path=options_path, master_root=master_root,
                                                 local=_local, identity=identity,
                                                 guarded_transit=reflow_guarded_intervals)
    if guarded_decisions:
        positions = {uid: index for index, uid in enumerate(unit_order)}
        artifact_rows.sort(key=lambda row: positions[row["omitted"]["unit_id"]])
    for row in duplicate_rows:
        cache[row["omitted"]["unit_id"]] = row["omitted_node"]
        cache[row["retained"]["unit_id"]] = row["retained_node"]
    for row in artifact_rows:
        cache[row["omitted"]["unit_id"]] = row["omitted_node"]
        if row["kind"] == "artwork":
            cache[row["image_unit"]["unit_id"]] = row["image_node"]

    extended_reflows = {}
    participating_titles = {}
    claimed_intermediate_ids = set()
    artifact_by_id = {row["omitted"]["unit_id"]: row for row in artifact_rows}
    artwork_by_image_id = {}
    for row in artifact_rows:
        if row["kind"] == "artwork":
            artwork_by_image_id.setdefault(row["image_unit"]["unit_id"], []).append(row)
    for decision in options["display_roles"]:
        if id(decision) not in guarded_decisions:
            continue
        labels = decision.get("intervening_asset_labels", [])
        bindings = decision.get("intervening_units")
        if not isinstance(bindings, list):
            raise ValueError("guarded reflow interval bindings are missing")
        interval = [bound(binding) for binding in bindings]
        interval_ids = [unit["unit_id"] for unit in interval]
        if len(interval_ids) != len(set(interval_ids)) or claimed_intermediate_ids.intersection(interval_ids):
            raise ValueError("extended reflow intermediate ownership overlaps")
        claimed_intermediate_ids.update(interval_ids)
        asset_indexes = set()
        asset_pairs = []
        for label in labels:
            label_required = {"unit", "image", "source_evidence", "reason"}
            if (not isinstance(label, dict) or not label_required <= set(label)
                    or set(label) - label_required - {"reviewed_asset_choice"}
                    or any(not isinstance(label[key], str) or not label[key].strip()
                           for key in ("source_evidence", "reason"))
                    or any(not isinstance(label[key], dict) or set(label[key]) != {"unit_id", "ru_sha256"}
                           for key in ("unit", "image"))):
                raise ValueError("retained asset labels require exact reviewed fields")
            list_unit, image_unit = bound(label["unit"]), bound(label["image"])
            if (list_unit["unit_id"] not in interval_ids or image_unit["unit_id"] not in interval_ids
                    or interval_ids.index(image_unit["unit_id"]) != interval_ids.index(list_unit["unit_id"]) + 1
                    or pages[list_unit["unit_id"]] != pages[image_unit["unit_id"]]
                    or any(unit.get("parent_unit_id") is not None for unit in (list_unit, image_unit))):
                raise ValueError("retained label list and image must be adjacent original units on one page")
            list_node, image_node = locate(label["unit"]), locate(label["image"])
            # A one-item Markdown list has the same text on its li and ul.  The
            # generic locator selects the smaller li; this route owns the whole
            # source list, so lift only an exact singleton to its ul container.
            if list_node.tag == "li":
                parent = list_node.getparent()
                if (parent is None or parent.tag != "ul" or len(parent) != 1
                        or parent[0] is not list_node
                        or any(uid != list_unit["unit_id"] and node in (parent, list_node)
                               for uid, node in cache.items())
                        or pages[list_unit["unit_id"]] is None
                        or len(parent.xpath("ancestor::section[@data-page]")) != 1
                        or parent.xpath("ancestor::section[@data-page]")[0].get("data-page")
                           != f"{pages[list_unit['unit_id']]:03d}"):
                    raise ValueError("retained asset labels require a whole flat list and original image")
                list_node = parent
                cache[list_unit["unit_id"]] = parent
            if (list_node.tag != "ul" or not len(list_node) or any(child.tag != "li"
                    or any(desc.tag not in {"strong", "em", "b", "i", "code", "span"}
                           or desc.get("id") for desc in child.iterdescendants())
                    or child.xpath(".//a[@href]") for child in list_node)
                    or image_node.tag != "figure" or len(image_node.xpath("./img")) != 1
                    or any(node.xpath("ancestor::*[@data-semantic-kind] | ancestor::blockquote") for node in (list_node, image_node))
                    or any(unit["unit_id"] in span.get("unit_ids", []) for span in projection.get("spans", [])
                           for unit in (list_unit, image_unit))):
                raise ValueError("retained asset labels require a whole flat list and original image")
            fragment, _, _ = markdown_to_review_html(list_unit["ru_text"], source_path=Path("unit.md"),
                                                       html_path=Path("unit.html"), blockquote_heading_offset=0)
            source_list = html.fragment_fromstring(fragment, create_parent="main")
            if (len(source_list) != 1 or source_list[0].tag != "ul"
                    or [html.tostring(item, encoding="unicode") for item in source_list[0]]
                    != [html.tostring(item, encoding="unicode") for item in list_node]):
                raise ValueError("retained asset labels differ from the exact source list")
            image_match = re.fullmatch(r"!\[[^\]]*\]\(([^)\s]+)\)", image_unit["ru_text"].strip())
            if (not image_match or master_root is None
                    or duplicates._image_signature(image_unit["ru_text"]) != duplicates._actual_image_signature(image_node)):
                raise ValueError("retained asset map is not one original image")
            source_image = _local(master_root, image_match[1])
            if not source_image.is_file():
                raise ValueError("retained asset original map image is missing")
            choices = [choice for choice in options["asset_choices"]
                       if choice.get("original_ref") == image_match[1]]
            selected_choice = label.get("reviewed_asset_choice")
            if selected_choice is not None:
                choice_fields = {"original_ref", "original", "selected_ref", "selected", "provenance", "reason"}
                if (not isinstance(selected_choice, dict) or set(selected_choice) != choice_fields
                        or len(choices) != 1 or selected_choice != choices[0]
                        or sum(choice.get("selected_ref") == selected_choice["selected_ref"]
                               for choice in options["asset_choices"]) != 1
                        or options_path is None
                        or identity(source_image) != selected_choice["original"]
                        or identity(_local(options_path.parent, selected_choice["selected_ref"]))
                           != selected_choice["selected"]):
                    raise ValueError("retained map reviewed asset choice is missing, stale, or ambiguous")
            elif choices:
                raise ValueError("retained map needs an exact reviewed asset choice opt-in")
            if any(reference in {list_unit["unit_id"], image_unit["unit_id"]}
                   for other in options["display_roles"] if other is not decision
                   for reference in duplicates._refs(other)) or any(
                       reference in {list_unit["unit_id"], image_unit["unit_id"]}
                       for item in (options["source_toc"], options["body_links"], options["hit_points"], options["asset_choices"])
                       for reference in duplicates._refs(item)) or any(
                       other is not decision and other.get("source_reference") == image_match[1]
                   for other in options["display_roles"] if isinstance(other, dict)):
                raise ValueError("retained asset list or image conflicts with another reader route")
            indexes = {interval_ids.index(list_unit["unit_id"]), interval_ids.index(image_unit["unit_id"])}
            if indexes & asset_indexes:
                raise ValueError("retained asset label groups overlap")
            asset_indexes.update(indexes)
            anchor(label["unit"]); anchor(label["image"])
            rendered_path = ("assets/reader/" + Path(selected_choice["selected_ref"]).name
                             if selected_choice is not None else image_match[1])
            final_image = copy.deepcopy(image_node)
            if selected_choice is not None:
                final_image.xpath("./img")[0].set("src", rendered_path)
            asset_pairs.append({"list_unit": list_unit, "image_unit": image_unit,
                                "list_node": list_node, "image_node": image_node,
                                "list_snapshot": html.tostring(list_node, encoding="unicode"),
                                "image_snapshot": html.tostring(final_image, encoding="unicode"),
                                "reference": rendered_path,
                                "identity": (selected_choice["selected"] if selected_choice is not None
                                             else identity(source_image)),
                                "reviewed_asset_choice": selected_choice})
        artifact_indexes = {index for index, uid in enumerate(interval_ids) if uid in artifact_by_id}
        title_indexes = set()
        retained_title_anchors = []
        retained_title_owners = []
        standalone_figures = []
        for title in options["display_roles"]:
            if title.get("role") != "repeated_title" or not isinstance(title.get("unit"), dict):
                continue
            uid = title["unit"].get("unit_id")
            if uid not in interval_ids:
                continue
            node, retained_node = locate(title["unit"]), locate(title["retained"])
            retained_uid = bound(title["retained"])["unit_id"]
            text_match = title.get("text_match", "exact")
            level_mismatch = title.get("heading_level_mismatch")
            title_fields = set(title)
            if title.get("standalone_running_heading") is True:
                # Compose the existing standalone witness with interval ownership;
                # the standalone route below still validates all of its evidence.
                title_fields -= {"standalone_running_heading", "heading_occurrence"}
            if level_mismatch is not None:
                if (not isinstance(level_mismatch, dict)
                        or set(level_mismatch) != {"removed_level", "retained_level", "source_evidence"}
                        or any(type(level_mismatch[key]) is not int or level_mismatch[key] not in range(1, 7)
                               for key in ("removed_level", "retained_level"))
                        or level_mismatch["removed_level"] == level_mismatch["retained_level"]
                        or not isinstance(level_mismatch["source_evidence"], str)
                        or not level_mismatch["source_evidence"].strip()):
                    raise ValueError("repeated title heading-level mismatch requires exact reviewed evidence")
            if (title_fields not in ({"role", "unit", "retained", "reason"},
                                   {"role", "unit", "retained", "reason", "source_evidence"},
                                   {"role", "unit", "retained", "reason", "source_evidence", "text_match"},
                                   {"role", "unit", "retained", "reason", "source_evidence", "text_match", "heading_level_mismatch"},
                                   {"role", "unit", "retained", "reason", "source_evidence", "heading_level_mismatch"})
                    or text_match not in {"exact", "casefold"}
                    or (text_match == "casefold" and
                        (not isinstance(title.get("source_evidence"), str) or not title["source_evidence"].strip()))):
                raise ValueError("participating repeated title requires reviewed text match evidence")
            if level_mismatch is not None:
                removed_unit, retained_unit = bound(title["unit"]), bound(title["retained"])
                if (node.tag != f'h{level_mismatch["removed_level"]}'
                        or retained_node.tag != f'h{level_mismatch["retained_level"]}'
                        or not re.fullmatch(r'#{' + str(level_mismatch["removed_level"]) + r'} [^\n]+',
                                            removed_unit["ru_text"])
                        or not re.fullmatch(r'#{' + str(level_mismatch["retained_level"]) + r'} [^\n]+',
                                            retained_unit["ru_text"])
                        or unit_order.index(retained_uid) >= unit_order.index(decision["units"][0]["unit_id"])
                        or pages[retained_uid] is None
                        or pages[retained_uid] >= pages[decision["units"][0]["unit_id"]]):
                    raise ValueError("repeated title heading-level mismatch differs from retained source heading")
            same_title = (norm(node.text_content()) == norm(retained_node.text_content()) if text_match == "exact"
                          else norm(node.text_content()).casefold() == norm(retained_node.text_content()).casefold())
            if (uid in participating_titles or retained_uid in interval_ids
                    or pages[retained_uid] is None or pages[retained_uid] > pages[uid]
                    or node is retained_node or node.tag not in {"h1", "h2", "h3", "h4", "h5", "h6"}
                    or (retained_node.tag != node.tag and level_mismatch is None) or not same_title
                    or any(uid in span.get("unit_ids", []) for span in projection.get("spans", []))
                    or any(reference == uid for other in options["display_roles"] if other is not title and other is not decision
                           for reference in duplicates._refs(other))
                    or any(reference == uid for item in (options["source_toc"], options["body_links"], options["hit_points"])
                           for reference in duplicates._refs(item))
                    or any(link.get("href") == "#" + node.get("id", "")
                           and not link.xpath('ancestor::nav[@id="toc"]')
                           for link in tree.xpath(".//a[@href]") if node.get("id"))):
                raise ValueError("participating repeated title is not an independent safe removal")
            participating_titles[uid] = {"decision": title, "node": node, "retained": retained_node,
                                         "text_match": text_match, "reflow_decision": decision}
            title_indexes.add(interval_ids.index(uid))
            title_anchor = anchor(title["retained"])
            retained_title_anchors.append(title_anchor)
            retained_title_owners.append({"anchor": title_anchor, "text": duplicates._inline(retained_node),
                                          "source_page": pages[retained_uid]})
        if asset_indexes & (artifact_indexes | title_indexes) or artifact_indexes & title_indexes:
            raise ValueError("extended reflow intermediate routes overlap")
        for index, unit in enumerate(interval):
            if index in asset_indexes | artifact_indexes | title_indexes:
                continue
            match = re.fullmatch(r"!\[[^\]]*\]\(([^)\s]+)\)", unit["ru_text"].strip())
            if match is None:
                continue
            artwork_owners = artwork_by_image_id.get(unit["unit_id"], [])
            if artwork_owners:
                if any(reflow_guarded_intervals.get(row["omitted"]["unit_id"]) != id(decision)
                       for row in artwork_owners):
                    raise ValueError("retained artwork image has unrelated guarded reflow ownership")
                # The whole-artifact route already verifies and archives this original image.
                continue
            binding = bindings[index]
            figure = locate(binding)
            if (master_root is None or figure.tag != "figure" or len(figure.xpath("./img")) != 1
                    or duplicates._image_signature(unit["ru_text"]) != duplicates._actual_image_signature(figure)
                    or any(unit["unit_id"] in span.get("unit_ids", []) for span in projection.get("spans", []))
                    or any(unit["unit_id"] in duplicates._refs(other)
                           for other in options["display_roles"] if other is not decision)
                    or any(choice.get("original_ref") == match[1] for choice in options["asset_choices"])):
                raise ValueError("guarded reflow retained figure conflicts with another route")
            source = _local(master_root, match[1])
            if not source.is_file():
                raise ValueError("guarded reflow original figure is missing")
            figure_anchor = anchor(binding)
            standalone_figures.append({"unit": unit, "node": figure,
                                       "snapshot": html.tostring(figure, encoding="unicode"),
                                       "reference": match[1], "identity": identity(source),
                                       "anchor": figure_anchor})
        extended_reflows[id(decision)] = {"asset_pairs": asset_pairs, "asset_indexes": asset_indexes,
                                          "artifact_indexes": artifact_indexes,
                                          "title_indexes": title_indexes,
                                          "standalone_figures": standalone_figures,
                                          "retained_title_anchors": retained_title_anchors,
                                          "retained_title_owners": retained_title_owners,
                                          "interval_ids": interval_ids}

    prose_targets = {}
    for decision in options["display_roles"]:
        if decision.get("role") != "prose_presentation":
            continue
        required = {"role", "unit", "source_evidence", "reason"}
        if (set(decision) not in (required, required | {"heading_occurrence"})
                or any(not isinstance(decision.get(key), str) or not decision[key].strip()
                       for key in ("source_evidence", "reason"))
                or not isinstance(decision.get("unit"), dict)
                or set(decision["unit"]) != {"unit_id", "ru_sha256"}):
            raise ValueError("prose presentation requires exact reviewed fields")
        unit = bound(decision["unit"])
        uid = unit["unit_id"]
        if (uid in prose_targets or unit.get("parent_unit_id") is not None
                or any(other.get("parent_unit_id") == uid for other in projection["units"])):
            raise ValueError("prose presentation requires one whole unsplit heading")
        node = locate(decision["unit"])
        if (node.tag not in {"h1", "h2", "h3", "h4", "h5", "h6"}
                or node.xpath('ancestor::blockquote | ancestor::*[@data-semantic-kind] | ancestor::table | ancestor::figure')
                or any(child.tag not in {"strong", "em", "b", "i", "code", "a", "span"}
                       for child in node.iterdescendants())):
            raise ValueError("prose presentation requires one unstructured heading")
        for other in options["display_roles"]:
            if other is decision or other.get("role") == "source_issue_review_anchor":
                continue
            # A prose cohort witness binds siblings without transforming them.
            if (other.get("role") == "prose_presentation"
                    and other.get("unit", {}).get("unit_id") != uid):
                continue
            if uid in set(duplicates._refs(other)):
                raise ValueError("prose presentation conflicts with another reader role")
        prose_targets[uid] = node

    presented_tables: set[int] = set()
    deferred_omissions: list[dict] = []
    deferred_source_anchors: list[dict] = []
    deferred_labels: list[dict] = []
    for decision in options["display_roles"]:
        if decision.get("role") in {"reviewed_block_relocation", "reviewed_statblock_group"}:
            continue  # Applied after exact retained reflow and furniture decisions.
        if decision.get("role") == "semantic_label":
            deferred_labels.append(decision)
            continue
        if decision.get("role") == "source_issue_review_anchor":
            deferred_source_anchors.append(decision)
            continue
        if decision.get("role") == "omit_source_artifact":
            # Omission runs after all presentation transforms so an image used by
            # another reviewed decision cannot silently disappear first.
            deferred_omissions.append(decision)
            continue
        if decision.get("role") == duplicates.ROLE:
            continue
        if decision.get("role") == "prose_presentation":
            node = prose_targets[decision["unit"]["unit_id"]]
            if tree not in node.iterancestors() or node.tag not in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                raise ValueError("prose presentation heading changed before display")
            original_text = node.text_content()
            target = anchor(decision["unit"])
            node.tag = "p"
            if node.text_content() != original_text:
                raise ValueError("prose presentation changed heading text")
            if state == "absent":
                for link in tree.xpath('.//nav[@id="toc"]//a[@href=$ref]', ref="#" + target):
                    listing = next((parent for parent in link.iterancestors() if parent.tag == "li"), None)
                    if listing is None:
                        raise ValueError("generated TOC false-heading link has unsupported structure")
                    listing.getparent().remove(listing)
                effective = [entry for entry in effective if entry.get("href") != target]
            report["display_roles"].append(decision)
            continue
        if decision.get("role") == "heading_prose_split":
            required = {"role", "unit", "heading_text", "source_evidence", "reason"}
            if set(decision) != required or not decision.get("source_evidence") or not decision.get("reason"):
                raise ValueError("heading split requires reviewed source evidence")
            node = locate(decision["unit"])
            label = decision["heading_text"]
            original = node.text or ""
            if (node.tag not in {"h1", "h2", "h3", "h4", "h5", "h6"} or len(node)
                    or node.xpath('ancestor::blockquote | ancestor::*[@data-semantic-kind]')
                    or not isinstance(label, str) or not label or label.strip() != label
                    or not original.startswith(label + " ") or not original[len(label):].strip()):
                raise ValueError("heading split requires an exact plain heading prefix and prose")
            target = anchor(decision["unit"])
            paragraph = html.Element("p")
            paragraph.text = original[len(label):].lstrip()
            paragraph.tail = node.tail
            node.tail = "\n"
            node.text = label
            node.addnext(paragraph)
            if norm(node.text_content() + " " + paragraph.text) != norm(original):
                raise ValueError("heading split changed visible text")
            # Only automatically generated TOC labels mirror the corrected heading.
            if state == "absent":
                for row in effective:
                    if row["href"] == target:
                        row["title"] = label
                for link in tree.xpath('.//nav//a[@href=$ref]', ref="#" + target):
                    link.text = label
            report["display_roles"].append(decision)
            continue
        if decision.get("role") == "table_presentation":
            required = {
                "role", "unit", "suppress_empty_transport_header", "source_header_rows",
                "source_evidence", "reason",
            }
            if set(decision) != required:
                raise ValueError("table presentation has unknown or missing fields")
            if (not isinstance(decision["suppress_empty_transport_header"], bool)
                    or not isinstance(decision["source_evidence"], str) or not decision["source_evidence"].strip()
                    or not isinstance(decision["reason"], str) or not decision["reason"].strip()
                    or not isinstance(decision["source_header_rows"], list)):
                raise ValueError("table presentation requires reviewed fields")
            table = locate(decision["unit"])
            if table.tag != "table":
                raise ValueError("table presentation target is not a table")
            if id(table) in presented_tables:
                raise ValueError("duplicate table presentation decision")
            rows = table.xpath("./thead/tr|./tbody/tr|./tr")
            if not rows:
                raise ValueError("table presentation requires table rows")
            header_rows = decision["source_header_rows"]
            if (any(isinstance(index, bool) or not isinstance(index, int) or index <= 0 for index in header_rows)
                    or header_rows != sorted(set(header_rows))
                    or any(index > len(rows) for index in header_rows)):
                raise ValueError("table presentation header rows are invalid")
            if decision["suppress_empty_transport_header"]:
                first = rows[0]
                cells = first.xpath("./th|./td")
                if (first.get("id") or first.get("name") or not cells
                        or any(norm(cell.text_content()) or len(cell) or cell.get("id") or cell.get("name") for cell in cells)):
                    raise ValueError("transport header is not truly empty")
                parent = first.getparent()
                parent.remove(first)
                rows = table.xpath("./thead/tr|./tbody/tr|./tr")
            if not rows:
                raise ValueError("table presentation removed every row")
            retained_source_rows = list(range(1, len(rows) + 1))
            if any(index not in retained_source_rows for index in header_rows):
                raise ValueError("table presentation header row was not retained")
            if len(header_rows) == len(rows):
                raise ValueError("table presentation requires a data row")
            table.set("data-table-header-policy", "explicit")
            table.set("data-table-source-header-rows", ",".join(str(index) for index in header_rows))
            presented_tables.add(id(table))
            for source_row, row in zip(retained_source_rows, rows):
                row.set("data-table-source-row", str(source_row))
                row.set("data-table-header", "true" if source_row in header_rows else "false")
            report["display_roles"].append(decision)
            continue
        if decision["role"] == "paragraph_continuation":
            required = {"role", "units", "reason", "source_evidence"}
            if set(decision) not in (required, required | {"join_mode"}):
                raise ValueError("paragraph continuation decision fields are invalid")
            join_mode = decision.get("join_mode", "space")
            if join_mode not in ("space", "word"):
                raise ValueError("paragraph continuation join mode is unsupported")
            bindings = decision["units"]
            if len(bindings) != 2 or not decision.get("reason") or not decision.get("source_evidence"):
                raise ValueError("paragraph continuation requires two reviewed source fragments")
            left_unit, right_unit = [bound(item) for item in bindings]
            order = [unit["unit_id"] for unit in projection["units"]]
            a, b = [order.index(unit["unit_id"]) for unit in (left_unit, right_unit)]
            between = projection["units"][a + 1:b]
            if b <= a or len(between) > 1 or any(not re.fullmatch(r"<!--\s*(?:source|pdf)-page-\d+\s*-->", u["ru_text"].strip()) for u in between):
                raise ValueError("paragraph fragments are not adjacent source prose")
            left, right = [locate(item) for item in bindings]
            if any(node.tag != "p" or node.xpath('ancestor::blockquote | ancestor::*[@data-semantic-kind] | ancestor::li | ancestor::table | ancestor::figure | .//img') or (node.tail or "").strip() for node in (left, right)):
                raise ValueError("paragraph continuation cannot join structured blocks")
            if left.getparent() is right.getparent():
                adjacent = left.getnext() is right
            else:
                lp, rp = left.getparent(), right.getparent()
                next_node = lp.getnext()
                next_page = pages[right_unit["unit_id"]]
                if isinstance(next_node, etree._Comment) and norm(next_node.text or "") == f"pdf-page-{next_page:03d}":
                    next_node = next_node.getnext()
                leading_marker = (len(rp) > 1 and rp[0].tag == "div"
                                  and rp[0].get("class") == "page-marker"
                                  and norm(rp[0].text_content()) == f"source page {next_page:03d}")
                first_prose = rp[1] if leading_marker else rp[0]
                adjacent = (lp.tag == rp.tag == "section" and next_node is rp
                            and lp[-1] is left and first_prose is right
                            and pages[right_unit["unit_id"]] == pages[left_unit["unit_id"]] + 1)
            if not adjacent:
                raise ValueError("paragraph continuation would cross unrelated content")
            left_text, right_text = left.text_content(), right.text_content()
            if join_mode == "word" and (not left_text or not right_text
                    or left_unit["ru_text"][-1:].isspace()
                    or right_unit["ru_text"][:1].isspace()
                    or not unicodedata.category(left_text[-1]).startswith("L")
                    or not unicodedata.category(right_text[0]).startswith("L")):
                raise ValueError("paragraph continuation word join requires letter boundaries")
            separator = " " if join_mode == "space" else ""
            before = norm(left_text + separator + right_text)
            anchor(bindings[0])
            right_id = anchor(bindings[1])
            boundary = etree.SubElement(left, "span", id=right_id,
                                        **{"data-source-page": str(pages[right_unit["unit_id"]])})
            boundary.tail = separator + (right.text or "")
            for child in list(right):
                left.append(child)
            right.getparent().remove(right)
            cache[right_unit["unit_id"]] = boundary
            if norm(left.text_content()) != before:
                raise ValueError("paragraph continuation changed visible text")
            report["display_roles"].append(decision)
            continue
        if decision["role"] == "interrupted_prose_reflow":
            required = {"role", "units", "intervening_units", "source_evidence", "reason"}
            optional = {"intervening_handout_groups", "intervening_asset_labels", "join_mode"}
            if (not required <= set(decision) or set(decision) - required - optional
                    or not decision["source_evidence"] or not decision["reason"]):
                raise ValueError("interrupted prose reflow requires reviewed source evidence")
            bindings = decision["units"]
            between_bindings = decision["intervening_units"]
            if (not isinstance(bindings, list) or len(bindings) != 2
                    or not isinstance(between_bindings, list) or not between_bindings
                    or any(not isinstance(item, dict) or set(item) != {"unit_id", "ru_sha256"}
                           for item in [*bindings, *between_bindings])):
                raise ValueError("interrupted prose reflow requires exact unit bindings")
            left_unit, right_unit = [bound(item) for item in bindings]
            order = [unit["unit_id"] for unit in projection["units"]]
            a, b = [order.index(unit["unit_id"]) for unit in (left_unit, right_unit)]
            actual_between = projection["units"][a + 1:b]
            expected_between = [{"unit_id": unit["unit_id"], "ru_sha256": unit["ru_sha256"]}
                                for unit in actual_between]
            if b <= a or between_bindings != expected_between:
                raise ValueError("interrupted prose reflow intervening source coverage mismatch")
            join_mode = decision.get("join_mode", "space")
            if join_mode not in {"space", "word"}:
                raise ValueError("interrupted prose reflow join mode is unsupported")

            def intervening_kind(unit: dict) -> str | None:
                text = unit["ru_text"].strip()
                if re.fullmatch(r"<!--\s*(?:source|pdf)-page-\d+\s*-->", text):
                    return "page_marker"
                if re.fullmatch(r"!\[[^\]]*\]\([^)]+\)", text):
                    return "figure"
                if text.startswith(">"):
                    return "sidebar"
                return None

            kinds = [intervening_kind(unit) for unit in actual_between]
            extended = extended_reflows.get(id(decision))
            if guarded_reflow(decision, options["display_roles"]) and extended is None:
                raise ValueError("guarded reflow was not preflighted")
            handout_groups = decision.get("intervening_handout_groups")
            ordinary_indexes = {index for index, kind in enumerate(kinds) if kind is None}
            group_indexes: set[int] = set()
            handout_nodes: list[tuple[etree._Element, str]] = []
            if handout_groups is not None:
                if not isinstance(handout_groups, list) or not handout_groups:
                    raise ValueError("interrupted prose reflow handout groups must be nonempty")
                for group in handout_groups:
                    group_required = {"units", "title", "source_evidence", "reason"}
                    if (not isinstance(group, dict)
                            or not group_required <= set(group)
                            or set(group) - group_required - {"title_kind"}
                            or not isinstance(group.get("title_kind", "heading"), str)
                            or group.get("title_kind", "heading") not in {"heading", "plain_paragraph"}
                            or not isinstance(group["units"], list) or not group["units"]
                            or not isinstance(group["title"], dict)
                            or any(not isinstance(value, str) or not value.strip()
                                   for value in (group["source_evidence"], group["reason"]))
                            or any(not isinstance(item, dict) or set(item) != {"unit_id", "ru_sha256"}
                                   for item in [*group["units"], group["title"]])):
                        raise ValueError("interrupted prose reflow handout group requires exact reviewed fields")
                    group_units = [bound(item) for item in group["units"]]
                    title = bound(group["title"])
                    if (title["unit_id"] not in {unit["unit_id"] for unit in group_units}
                            or len({unit["unit_id"] for unit in group_units}) != len(group_units)):
                        raise ValueError("interrupted prose reflow handout group title/units are invalid")
                    indexes = [actual_between.index(unit) if unit in actual_between else -1 for unit in group_units]
                    if (any(index < 0 for index in indexes)
                            or indexes != list(range(indexes[0], indexes[0] + len(indexes)))
                            or any(index in group_indexes for index in indexes)):
                        raise ValueError("interrupted prose reflow handout groups must be contiguous and nonoverlapping")
                    group_indexes.update(indexes)
                    nodes = [locate(binding) for binding in group["units"]]
                    title_node = locate(group["title"])
                    title_kind = group.get("title_kind", "heading")
                    if ((title_kind == "heading" and title_node.tag not in {"h1", "h2", "h3", "h4", "h5", "h6"})
                            or (title_kind == "plain_paragraph" and
                                (title_node.tag != "p" or len(title_node) or not title_node.text_content().strip()))
                            or any(node.tag not in {"h1", "h2", "h3", "h4", "h5", "h6", "p", "table", "li", "ul", "ol"}
                                   or node.xpath("ancestor::blockquote | ancestor::*[@data-semantic-kind] | ancestor::figure")
                                   for node in nodes)):
                        raise ValueError("interrupted prose reflow handout group has unsupported rendered content")
                    lists = []
                    for node in nodes:
                        if node.tag not in {"li", "ul", "ol"}:
                            continue
                        listing = node.getparent() if node.tag == "li" else node
                        items = list(listing)
                        if (listing.tag not in {"ul", "ol"} or not items
                                or any(item.tag != "li" for item in items)
                                or listing.xpath('.//ul | .//ol | ancestor::ul | ancestor::ol')
                                or (node.tag == "li" and any(item not in nodes for item in items))):
                            raise ValueError("interrupted prose reflow handout group requires exact full flat list ownership")
                        if listing not in lists:
                            lists.append(listing)
                    handout_nodes.extend((listing, html.tostring(listing, encoding="unicode")) for listing in lists)
                    if title_kind == "plain_paragraph":
                        anchor(group["title"])
                    root_nodes = list(tree.iter())
                    if any(root_nodes.index(nodes[index]) >= root_nodes.index(nodes[index + 1])
                           for index in range(len(nodes) - 1)):
                        raise ValueError("interrupted prose reflow handout group rendered order mismatch")
                    handout_nodes.extend((node, html.tostring(node, encoding="unicode")) for node in nodes)
            covered = group_indexes
            if extended is not None:
                covered = covered | extended["asset_indexes"] | extended["artifact_indexes"] | extended["title_indexes"]
                if (group_indexes & (extended["asset_indexes"] | extended["artifact_indexes"] | extended["title_indexes"])
                        or covered != ordinary_indexes | extended["asset_indexes"]):
                    raise ValueError("extended reflow has overlapping or unrelated unreviewed intermediate content")
            if covered != ordinary_indexes | (extended["asset_indexes"] if extended else set()):
                raise ValueError("interrupted prose reflow would cross unrelated source content")
            # Confirm the rendered non-marker blocks are the reviewed types.  Markers
            # are represented by page sections/comments rather than one block node.
            for binding, kind in zip(between_bindings, kinds):
                if kind == "page_marker":
                    continue
                node = locate(binding)
                if ((kind == "figure" and node.tag != "figure")
                        or (kind == "sidebar" and node.tag != "blockquote" and not node.xpath("ancestor::blockquote"))):
                    raise ValueError("interrupted prose reflow intervening HTML kind mismatch")

            original_order = list(tree.iter())
            original_nodes = [locate(binding) for binding, kind in zip(between_bindings, kinds)
                              if kind != "page_marker"]
            if any(original_order.index(first) >= original_order.index(second)
                   for first, second in zip(original_nodes, original_nodes[1:])):
                raise ValueError("interrupted prose reflow rendered order differs from source interval")

            left, right = [locate(item) for item in bindings]
            structured = 'ancestor::blockquote | ancestor::*[@data-semantic-kind] | ancestor::table | ancestor::figure | .//img'
            if (left.tag not in {"p", "li"} or right.tag != "p"
                    or left.xpath(structured) or right.xpath(structured)
                    or right.xpath("ancestor::li")
                    or any((node.tail or "").strip() for node in (left, right))):
                raise ValueError("interrupted prose reflow cannot join structured blocks")
            left_text, right_text = left.text_content(), right.text_content()
            if join_mode == "word" and (not left_text or not right_text
                    or left_unit["ru_text"][-1:].isspace()
                    or right_unit["ru_text"][:1].isspace()
                    or not unicodedata.category(left_text[-1]).startswith("L")
                    or not unicodedata.category(right_text[0]).startswith("L")):
                raise ValueError("interrupted prose word join requires letter boundaries")
            separator = " " if join_mode == "space" else ""
            before = left_text + separator + right_text
            anchor(bindings[0])
            right_id = anchor(bindings[1])
            boundary = etree.SubElement(left, "span", id=right_id,
                                        **{"data-source-page": str(pages[right_unit["unit_id"]])})
            boundary.tail = separator + (right.text or "")
            for child in list(right):
                left.append(child)
            right.getparent().remove(right)
            cache[right_unit["unit_id"]] = boundary
            if left.text_content() != before:
                raise ValueError("interrupted prose reflow changed visible text")
            root_order = list(tree.iter())
            if any(node not in root_order or root_order.index(node) <= root_order.index(left)
                   for binding, kind in zip(between_bindings, kinds) if kind != "page_marker"
                   for node in [locate(binding)]):
                raise ValueError("interrupted prose reflow lost intervening rendered content")
            if any(node not in root_order or html.tostring(node, encoding="unicode") != snapshot
                   for node, snapshot in handout_nodes):
                raise ValueError("interrupted prose reflow changed handout content or bookmarks")
            if extended is not None:
                page_domain = {pages[unit["unit_id"]] for unit in [left_unit, right_unit, *actual_between]}
                page_domain.update(owner["source_page"] for owner in extended["retained_title_owners"])
                if None in page_domain:
                    raise ValueError("extended reflow source page topology is incomplete")
                touched = sorted(page_domain)
                dependency = {"source_pages": touched, "left_page": pages[left_unit["unit_id"]],
                              "right_page": pages[right_unit["unit_id"]],
                              "left_anchor": anchor(bindings[0]), "right_anchor": right_id,
                              "joined_owner": {"text": duplicates._inline(left)},
                              "retained_title_anchors": extended["retained_title_anchors"],
                              "retained_title_owners": extended["retained_title_owners"],
                              "asset_pairs": []}
                for pair in extended["asset_pairs"]:
                    dependency["asset_pairs"].append({
                        "source_page": pages[pair["list_unit"]["unit_id"]],
                        "list_unit": {key: pair["list_unit"][key] for key in ("unit_id", "ru_sha256")},
                        "image_unit": {key: pair["image_unit"][key] for key in ("unit_id", "ru_sha256")},
                        "list_anchor": pair["list_node"].get("id"), "image_anchor": pair["image_node"].get("id"),
                        "list_owner_text": duplicates._inline(pair["list_node"][0]),
                        "reference": pair["reference"], "identity": pair["identity"],
                        **({"reviewed_asset_choice": pair["reviewed_asset_choice"]}
                           if pair["reviewed_asset_choice"] is not None else {}),
                    })
                    report["retained_image_dependencies"].append({
                        "source_page": pages[pair["image_unit"]["unit_id"]],
                        "image_unit": {key: pair["image_unit"][key] for key in ("unit_id", "ru_sha256")},
                        "reference": pair["reference"], "identity": pair["identity"],
                        "anchor": pair["image_node"].get("id"),
                    })
                for figure in extended["standalone_figures"]:
                    report["retained_image_dependencies"].append({
                        "source_page": pages[figure["unit"]["unit_id"]],
                        "image_unit": {key: figure["unit"][key] for key in ("unit_id", "ru_sha256")},
                        "reference": figure["reference"], "identity": figure["identity"],
                        "anchor": figure["anchor"],
                    })
                report["reflow_dependencies"].append(dependency)
            report["display_roles"].append(decision)
            continue
        if decision["role"] == "inline_ordered_list":
            node = locate(decision["unit"])
            entries = decision["items"]
            if (node.tag != "p" or len(node) or node.xpath('ancestor::blockquote | ancestor::*[@data-semantic-kind]')
                    or not isinstance(entries, list) or len(entries) < 2
                    or not all(isinstance(s, str) and s.strip() == s and s for s in entries)
                    or not decision.get("reason") or not decision.get("source_evidence")):
                raise ValueError("inline list requires reviewed plain paragraph items")
            expected = " ".join(f"{index}) {item}" for index, item in enumerate(entries, 1))
            if norm(node.text_content()) != expected:
                raise ValueError("inline list text/numbering preimage mismatch")
            listing = etree.Element("ol", start="1")
            if node.get("id"):
                listing.set("id", node.get("id"))
            for item in entries:
                etree.SubElement(listing, "li").text = item
            listing.tail = node.tail
            node.getparent().replace(node, listing)
            cache[decision["unit"]["unit_id"]] = listing
            report["display_roles"].append(decision)
            continue
        if decision["role"] == "review_anchor":
            required = {"role", "unit", "target_text", "source_evidence", "reason"}
            if (set(decision) != required or not isinstance(decision["target_text"], str)
                    or not decision["target_text"].strip() or not isinstance(decision["source_evidence"], str)
                    or not decision["source_evidence"].strip() or not isinstance(decision["reason"], str)
                    or not decision["reason"].strip()):
                raise ValueError("review anchor requires exact reviewed target evidence")
            unit = bound(decision["unit"])
            scope = locate(decision["unit"])
            paragraphs = [scope] if scope.tag == "p" else scope.xpath(".//p")
            target_text = decision["target_text"]
            matches = [node for node in paragraphs if node.text_content().count(target_text) == 1]
            if len(matches) != 1:
                raise ValueError("review anchor target is absent or ambiguous within reviewed unit")
            paragraph = matches[0]
            if paragraph.xpath(
                    "ancestor::table | ancestor::figure | .//img | "
                    "ancestor::*[@data-semantic-kind and @data-semantic-kind != 'statblock']"):
                raise ValueError("review anchor target must be a plain rendered paragraph")
            anchor_value = "review-" + hashlib.sha256(
                (unit["unit_id"] + "\0" + target_text).encode("utf-8")
            ).hexdigest()[:24]
            existing = paragraph.get("id")
            if existing not in {None, anchor_value} or any(row["anchor"] == anchor_value for row in report["review_anchors"]):
                raise ValueError("review anchor would conflict with an existing HTML target")
            paragraph.set("id", anchor_value)
            report["review_anchors"].append({**decision, "anchor": anchor_value})
            report["display_roles"].append(decision)
            continue
        if decision["role"] == "source_figure_regions":
            required = {"role", "unit", "retained_text_units", "after_unit", "classification", "regions", "source_evidence", "reason"}
            if (set(decision) != required or decision.get("classification") not in {"translated_text_only", "text_with_retained_art"}
                    or not isinstance(decision.get("source_evidence"), str) or not decision["source_evidence"].strip()
                    or not isinstance(decision.get("reason"), str) or not decision["reason"].strip()
                    or not isinstance(decision.get("retained_text_units"), list) or not decision["retained_text_units"]
                    or not isinstance(decision.get("regions"), list)):
                raise ValueError("source figure regions require reviewed bindings, classification, and evidence")
            unit = bound(decision["unit"])
            uid = unit["unit_id"]
            image = re.fullmatch(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)", unit["ru_text"].strip())
            node = locate(decision["unit"])
            images = node.xpath(".//img")
            if image is None or node.tag != "figure" or len(images) != 1 or images[0].get("src") != image[1]:
                raise ValueError("source figure regions require one exact image-only source figure")
            retained = [bound(binding) for binding in decision["retained_text_units"]]
            retained_ids = [item["unit_id"] for item in retained]
            if len(retained_ids) != len(set(retained_ids)) or uid in retained_ids:
                raise ValueError("source figure regions require distinct retained text units")
            retained_nodes = [locate(binding) for binding in decision["retained_text_units"]]
            if any(candidate.tag == "figure" or candidate.xpath(".//img") for candidate in retained_nodes):
                raise ValueError("source figure regions retained units must be text")
            after = bound(decision["after_unit"])
            if after["unit_id"] not in retained_ids:
                raise ValueError("source figure regions after_unit must be a retained text unit")
            after_node = locate(decision["after_unit"])
            if after_node not in retained_nodes:
                raise ValueError("source figure regions after_unit is not retained")
            conflicts = {"omit_source_artifact", "asset_legend"}
            if any(item is not decision and item.get("role") in conflicts and isinstance(item.get("unit"), dict)
                   and item["unit"].get("unit_id") == uid for item in options["display_roles"]):
                raise ValueError("source figure regions conflicts with another figure route")
            if any(item.get("original_ref") == image[1] for item in options["asset_choices"] if isinstance(item, dict)):
                raise ValueError("source figure regions conflicts with another asset decision")
            if any(row["unit"]["unit_id"] == uid for row in report["source_figure_regions"]):
                raise ValueError("source figure regions requires one distinct source occurrence")
            regions = decision["regions"]
            if ((decision["classification"] == "translated_text_only" and regions)
                    or (decision["classification"] == "text_with_retained_art" and not regions)):
                raise ValueError("source figure regions classification does not match region coverage")
            rendered_regions: list[dict[str, Any]] = []
            from kb_creator.scripts.production_docx import _figure_policy
            for region in regions:
                fields = {"id", "selected_ref", "selected", "caption", "figure_policy"}
                if (not isinstance(region, dict) or set(region) != fields or not isinstance(region.get("id"), str)
                        or not re.fullmatch(r"[A-Za-z0-9_-]+", region["id"])
                        or not isinstance(region.get("selected_ref"), str) or not region["selected_ref"].strip()
                        or "\\" in region["selected_ref"] or ":" in region["selected_ref"]
                        or any(part in {"", ".", ".."} for part in Path(region["selected_ref"]).parts)
                        or not isinstance(region.get("caption"), str) or not region["caption"].strip()
                        or not isinstance(region.get("selected"), dict) or set(region["selected"]) != {"bytes", "sha256"}
                        or isinstance(region["selected"]["bytes"], bool) or not isinstance(region["selected"]["bytes"], int) or region["selected"]["bytes"] <= 0
                        or not isinstance(region["selected"]["sha256"], str) or not re.fullmatch(r"[0-9A-F]{64}", region["selected"]["sha256"])):
                    raise ValueError("source figure region has invalid reviewed fields")
                _figure_policy(region["figure_policy"], f"source figure region {region['id']!r}")
                if "crop_fraction" not in region["figure_policy"]:
                    raise ValueError("source figure region requires crop_fraction")
                rendered_path = "assets/reader/source-regions/" + region["id"] + "-" + Path(region["selected_ref"]).name
                rendered_regions.append({**region, "rendered_path": rendered_path})
            destinations = [row["rendered_path"] for row in rendered_regions]
            ids = [row["id"] for row in rendered_regions]
            prior_regions = [row for group in report["source_figure_regions"] for row in group["regions"]]
            if len(ids) != len(set(ids)) or len(destinations) != len(set(destinations)) or any(
                    row["id"] in {old["id"] for old in prior_regions} or row["rendered_path"] in {old["rendered_path"] for old in prior_regions}
                    for row in rendered_regions):
                raise ValueError("source figure regions require distinct region ids and destinations")
            group = html.Element("div", **{"class": "source-figure-regions", "data-source-reference": image[1]})
            for region in rendered_regions:
                figure = etree.SubElement(group, "figure", **{"class": "source-figure-region", "data-region-id": region["id"]})
                etree.SubElement(figure, "img", src=region["rendered_path"], alt=region["caption"])
                etree.SubElement(figure, "figcaption").text = region["caption"]
            after_node.addnext(group)
            node.getparent().remove(node)
            if any(candidate not in tree.iter() or not norm(candidate.text_content()) for candidate in retained_nodes):
                raise ValueError("source figure regions removed retained text")
            report["source_figure_regions"].append({
                **decision, "source_reference": image[1], "source_image_occurrences": 1,
                "regions": rendered_regions,
            })
            report["display_roles"].append(decision)
            continue
        if decision["role"] == "asset_legend":
            required = {"role", "unit", "title", "entries", "source_evidence", "reason"}
            if (set(decision) != required or not isinstance(decision["title"], str) or not decision["title"].strip()
                    or decision["title"].strip() != decision["title"]
                    or not isinstance(decision["source_evidence"], str) or not decision["source_evidence"].strip()
                    or not isinstance(decision["reason"], str) or not decision["reason"].strip()
                    or not isinstance(decision["entries"], list) or not decision["entries"]):
                raise ValueError("asset legend requires reviewed title, entries, and evidence")
            unit = bound(decision["unit"])
            image = re.fullmatch(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)", unit["ru_text"].strip())
            if image is None:
                raise ValueError("asset legend requires an image-only unit")
            node = locate(decision["unit"])
            images = node.xpath(".//img")
            source_reference = image[1]
            if node.tag != "figure" or len(images) != 1 or images[0].get("src") != source_reference:
                raise ValueError("asset legend requires one exact source figure")
            entries = decision["entries"]
            if (any(not isinstance(row, dict) or set(row) != {"source", "translation"}
                    or not isinstance(row["source"], str) or not row["source"].strip() or row["source"].strip() != row["source"]
                    or not isinstance(row["translation"], str) or not row["translation"].strip() or row["translation"].strip() != row["translation"]
                    for row in entries)
                    or len({row["source"] for row in entries}) != len(entries)):
                raise ValueError("asset legend entries require distinct non-empty source and translation labels")
            if any(
                    item.get("role") == "omit_source_artifact"
                    and isinstance(item.get("unit"), dict)
                    and item["unit"].get("unit_id") == unit["unit_id"]
                    for item in options["display_roles"]):
                raise ValueError("asset legend conflicts with source artifact omission")
            legend = html.Element("div", **{"class": "asset-legend", "data-source-reference": source_reference})
            etree.SubElement(legend, "p", **{"class": "asset-legend-title"}).text = decision["title"]
            table = etree.SubElement(legend, "table", **{"class": "asset-legend-table"})
            header = etree.SubElement(etree.SubElement(table, "thead"), "tr")
            etree.SubElement(header, "th").text = "На карте"
            etree.SubElement(header, "th").text = "По-русски"
            body = etree.SubElement(table, "tbody")
            for row in entries:
                rendered = etree.SubElement(body, "tr")
                etree.SubElement(rendered, "td").text = row["source"]
                etree.SubElement(rendered, "td").text = row["translation"]
            node.addnext(legend)
            report["asset_legends"].append({**decision, "source_reference": source_reference})
            report["display_roles"].append(decision)
            continue
        if decision["role"] == "shared_figure_heading":
            bindings = decision["units"]
            nodes = [locate(binding) for binding in bindings]
            if len(nodes) < 2 or len({id(node) for node in nodes}) != len(nodes) or not decision.get("label") or not decision.get("reason"):
                raise ValueError("shared figure heading requires distinct reviewed headings")
            parent = nodes[0].getparent()
            if any(node.getparent() is not parent or node.tag not in {"h1","h2","h3","h4","h5","h6"} for node in nodes):
                raise ValueError("shared figure headings must be headings on the same source page")
            figures = parent.xpath('.//figure[img[@src=$ref]]', ref=decision["source_reference"])
            if len(figures) != 1:
                raise ValueError("shared figure heading requires one exact source figure")
            targets = [anchor(binding) for binding in bindings]
            first = nodes[0]
            first.text = decision["label"]
            for child in list(first):
                first.remove(child)
            for node, target in zip(nodes[1:], targets[1:]):
                alias = etree.SubElement(first, "span", id=target)
                alias.text = ""
                node.getparent().remove(node)
            report["display_roles"].append(decision)
            continue
        if decision["role"] == "asset_alt_metadata":
            # Alt text remains on the image; it is not necessarily an authored caption.
            images = tree.xpath('.//figure/img[@src=$ref]', ref=decision["source_reference"])
            if not images or not decision.get("reason"):
                raise ValueError("asset metadata caption target missing")
            for image in images:
                captions = image.getparent().xpath('./figcaption')
                if len(captions) != 1 or captions[0].text_content() != decision["caption"] or image.get("alt") != decision["caption"]:
                    raise ValueError("asset metadata caption preimage mismatch")
                image.getparent().remove(captions[0])
            report["display_roles"].append(decision)
            continue
        if decision["role"] != "repeated_title" or not decision.get("reason"):
            raise ValueError("unsupported display role")
        standalone = decision.get("standalone_running_heading")
        if "standalone_running_heading" in decision and standalone is not True:
            raise ValueError("standalone running heading opt-in must be true")
        if standalone is True:
            required = {"role", "unit", "retained", "reason", "source_evidence",
                        "standalone_running_heading"}
            optional = {"text_match", "heading_level_mismatch", "heading_occurrence"}
            removed_unit, retained_unit = bound(decision["unit"]), bound(decision["retained"])
            removed_uid, retained_uid = removed_unit["unit_id"], retained_unit["unit_id"]
            participating = participating_titles.get(removed_uid)
            node, retained = locate(decision["unit"]), locate(decision["retained"])
            match_kind = decision.get("text_match", "exact")
            mismatch = decision.get("heading_level_mismatch")
            heading = re.fullmatch(r"(#{1,6}) ([^\n]+)", removed_unit["ru_text"])
            retained_heading = re.fullmatch(r"(#{1,6}) ([^\n]+)", retained_unit["ru_text"])
            removed_level = len(heading[1]) if heading else None
            retained_level = len(retained_heading[1]) if retained_heading else None
            if (not required <= set(decision) or set(decision) - required - optional
                    or not isinstance(decision["source_evidence"], str)
                    or not decision["source_evidence"].strip()
                    or not isinstance(decision["reason"], str) or not decision["reason"].strip()
                    or match_kind not in {"exact", "casefold"}
                    or removed_uid == retained_uid
                    or removed_unit.get("parent_unit_id") is not None
                    or retained_unit.get("parent_unit_id") is not None
                    or removed_level is None or retained_level is None
                    or node.tag != f"h{removed_level}" or retained.tag != f"h{retained_level}"
                    or pages[retained_uid] is None or pages[removed_uid] is None
                    or pages[retained_uid] >= pages[removed_uid]
                    or unit_order.index(retained_uid) >= unit_order.index(removed_uid)
                    or any(removed_uid in span.get("unit_ids", []) for span in projection.get("spans", []))):
                raise ValueError("standalone running heading requires exact earlier whole heading evidence")
            if ((removed_level == retained_level and mismatch is not None)
                    or (removed_level != retained_level and
                        (not isinstance(mismatch, dict)
                         or set(mismatch) != {"removed_level", "retained_level", "source_evidence"}
                         or type(mismatch["removed_level"]) is not int
                         or type(mismatch["retained_level"]) is not int
                         or mismatch["removed_level"] != removed_level
                         or mismatch["retained_level"] != retained_level
                         or not isinstance(mismatch["source_evidence"], str)
                         or not mismatch["source_evidence"].strip()))):
                raise ValueError("standalone running heading level witness is missing or incorrect")
            same_title = (norm(node.text_content()) == norm(retained.text_content())
                          if match_kind == "exact" else
                          norm(node.text_content()).casefold() == norm(retained.text_content()).casefold())
            if (not same_title
                    or any(removed_uid in duplicates._refs(other)
                           for other in options["display_roles"] if other is not decision
                           and (participating is None or other is not participating["reflow_decision"]))
                    or any(removed_uid in duplicates._refs(item)
                           for item in (options["source_toc"], options["body_links"],
                                        options["hit_points"], options["asset_choices"]))
                    or (node.get("id") and any(
                        not link.xpath('ancestor::nav[@id="toc"]')
                        for link in tree.xpath('.//a[@href=$ref]', ref="#" + node.get("id"))))):
                raise ValueError("standalone running heading is protected or differs from retained title")
            retained_anchor = anchor(decision["retained"])
            if node.get("id"):
                for link in tree.xpath('.//nav[@id="toc"]//a[@href=$ref]', ref="#" + node.get("id")):
                    listing = next((parent for parent in link.iterancestors() if parent.tag == "li"), None)
                    if listing is None:
                        raise ValueError("standalone running heading TOC link has unsupported structure")
                    listing.getparent().remove(listing)
                effective = [entry for entry in effective if entry.get("href") != node.get("id")]
            report["standalone_running_headings"].append({
                "removed": decision["unit"], "retained": decision["retained"],
                "removed_page": pages[removed_uid], "retained_page": pages[retained_uid],
                "retained_anchor": retained_anchor, "retained_text": duplicates._inline(retained),
                "source_evidence": decision["source_evidence"],
                **({"heading_occurrence": decision["heading_occurrence"]}
                   if "heading_occurrence" in decision else {}),
            })
            if participating is None:
                node.getparent().remove(node)
                report["display_roles"].append(decision)
            continue
        if ("text_match" in decision and
                bound(decision["unit"])["unit_id"] not in participating_titles):
            raise ValueError("casefold repeated title requires a guarded reflow interval")
        if ("heading_level_mismatch" in decision and
                bound(decision["unit"])["unit_id"] not in participating_titles):
            raise ValueError("heading-level mismatch requires a guarded reflow interval")
        node = locate(decision["unit"])
        retained = locate(decision["retained"])
        same_title = (norm(node.text_content()) == norm(retained.text_content())
                      if decision.get("text_match", "exact") == "exact" else
                      norm(node.text_content()).casefold() == norm(retained.text_content()).casefold())
        if node is retained or not same_title:
            raise ValueError("repeated title must have an exact retained counterpart")
        if bound(decision["unit"])["unit_id"] in participating_titles:
            continue
        node.getparent().remove(node)
        report["display_roles"].append(decision)

    for uid, row in participating_titles.items():
        node = row["node"]
        if (tree not in node.iterancestors() or tree not in row["retained"].iterancestors()
                or (norm(node.text_content()).casefold() != norm(row["retained"].text_content()).casefold()
                    if row["text_match"] == "casefold" else
                    norm(node.text_content()) != norm(row["retained"].text_content()))):
            raise ValueError("participating repeated title changed before reviewed removal")
        if node.get("id"):
            for link in tree.xpath('.//nav[@id="toc"]//a[@href=$ref]', ref="#" + node.get("id")):
                listing = next((parent for parent in link.iterancestors() if parent.tag == "li"), None)
                if listing is None:
                    raise ValueError("generated TOC repeated-title link has unsupported structure")
                listing.getparent().remove(listing)
            effective = [entry for entry in effective if entry.get("href") != node.get("id")]
        node.getparent().remove(node)
        report["display_roles"].append(row["decision"])

    duplicates.apply(tree, duplicate_rows, report)
    duplicates.apply_artifacts(tree, artifact_rows, report)

    protected_units: set[str] = set()
    for row in options["body_links"]:
        for key in ("unit", "target"):
            binding = row.get(key)
            if isinstance(binding, dict) and isinstance(binding.get("unit_id"), str):
                protected_units.add(binding["unit_id"])
    if state == "present":
        for row in toc.get("units", []):
            if isinstance(row, dict) and isinstance(row.get("unit_id"), str):
                protected_units.add(row["unit_id"])
        for row in toc.get("entries", []):
            target = row.get("target") if isinstance(row, dict) else None
            if isinstance(target, dict) and isinstance(target.get("unit_id"), str):
                protected_units.add(target["unit_id"])
    for decision in options["display_roles"]:
        if decision.get("role") in {"review_anchor", "source_issue_review_anchor"}:
            bindings = decision.get("units") if isinstance(decision.get("units"), list) else [decision.get("unit")]
            for binding in bindings:
                if isinstance(binding, dict) and isinstance(binding.get("unit_id"), str):
                    protected_units.add(binding["unit_id"])

    omitted_units: set[str] = set()
    replacement_refs = {row.get("original_ref") for row in options["asset_choices"] if isinstance(row, dict)}
    for decision in deferred_omissions:
        if decision.get("text_policy") == "reviewed_whole_plain_block_v2":
            continue
        classification = decision.get("classification")
        base = {"role", "unit", "classification", "source_evidence", "reason"}
        duplicate = base | {"retained_image_reference"}
        required = duplicate if classification == "duplicate_text_represented_by_retained_artwork" else base
        if (set(decision) != required or classification not in {"ornamental_page_number", "duplicate_text_represented_by_retained_artwork"}
                or not isinstance(decision.get("source_evidence"), str) or not decision["source_evidence"].strip()
                or not isinstance(decision.get("reason"), str) or not decision["reason"].strip()):
            raise ValueError("source artifact omission requires typed reviewed evidence")
        unit = bound(decision["unit"])
        uid = unit["unit_id"]
        image = re.fullmatch(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)", unit["ru_text"].strip())
        if uid in omitted_units:
            raise ValueError("source artifact omission requires one distinct unit")
        node = locate(decision["unit"])
        if node.get("id") or node.xpath(".//*[@id]") or uid in protected_units:
            raise ValueError("source artifact omission conflicts with a structural or anchor route")
        source_reference: str | None = None
        image_occurrences = 0
        legacy_text_page = None
        legacy_text_before = None
        if classification == "duplicate_text_represented_by_retained_artwork":
            retained = decision["retained_image_reference"]
            if (image is not None or node.tag != "p" or len(node) or "\n" in unit["ru_text"]
                    or node.text_content() != unit["ru_text"]
                    or not isinstance(retained, str) or not retained
                    or len(tree.xpath('.//img[@src=$ref]', ref=retained)) != 1):
                raise ValueError("duplicate text omission requires one plain-text unit and retained source image")
            legacy_text_page, legacy_text_section = duplicates._page(node)
            legacy_text_before = duplicates.page_paragraphs(legacy_text_section)
        else:
            images = node.xpath(".//img")
            if image is None or node.tag != "figure" or len(images) != 1 or images[0].get("src") != image[1]:
                raise ValueError("ornamental artifact omission requires one image-only unit")
            source_reference = image[1]
            image_occurrences = 1
            if source_reference in replacement_refs:
                raise ValueError("source artifact omission conflicts with another asset decision")
        node.getparent().remove(node)
        omitted_units.add(uid)
        omission_report = {
            **decision, "source_reference": source_reference, "image_occurrences": image_occurrences,
        }
        if legacy_text_page is not None:
            legacy_text_after = duplicates.page_paragraphs(legacy_text_section)
            if not any(legacy_text_before[:index] + legacy_text_before[index + 1:] == legacy_text_after
                       for index, value in enumerate(legacy_text_before) if value == node.text_content()):
                raise ValueError("legacy duplicate text omission changed unrelated page text")
            omission_report.update({
                "actual_source_page": legacy_text_page,
                "omitted_rendered_text": node.text_content(),
                "affected_page_before": legacy_text_before,
                "affected_page_after": legacy_text_after,
            })
            duplicates.append_page_witness(tree, report, legacy_text_page, legacy_text_after)
        report["omitted_artifacts"].append(omission_report)
        report["display_roles"].append(decision)

    for decision in options["body_links"]:
        node = locate(decision["unit"])
        target = anchor(decision["target"])
        before, label = decision["text"], decision["label"]
        if not before or not label or not decision.get("reason") or node.text_content().count(before) != 1:
            raise ValueError("body link exact text preimage mismatch")
        slots = [(e, key) for e in node.iter() for key in ("text", "tail") if before in (getattr(e, key) or "")]
        if len(slots) != 1:
            raise ValueError("body link crosses inline boundaries")
        element, key = slots[0]
        left, right = getattr(element, key).split(before)
        link = etree.Element("a", href=f"#{target}"); link.text = label; link.tail = right
        setattr(element, key, left)
        if key == "text":
            element.insert(0, link)
        else:
            element.addnext(link)
        report["links"].append({"kind": "body", "label": label, "target": target, "unit_id": decision["target"]["unit_id"]})
        retained = next((row for row in duplicate_rows
                         if row["retained"]["unit_id"] == decision["target"]["unit_id"]), None)
        if retained is not None:
            report["retained_link_dependencies"].append({
                "source_anchor": anchor(decision["unit"]), "target_anchor": target,
                "label": label, "retained_text": duplicates._inline(retained["retained_node"]),
                "retained_page": retained["decision"]["source_page"],
            })

    hp = options["hit_points"]
    if hp["presentation"] not in {"numeric", "boxes"}:
        raise ValueError("unsupported hit point presentation")
    pattern = re.compile(r"(ПЗ:\s*)((?:[□☐◻]\s*)+)")
    for card in tree.xpath('.//*[@data-semantic-kind="statblock"]'):
        if hp["presentation"] in {"numeric", "boxes"}:
            for br in list(card.iter("br")):
                previous = br.getprevious()
                parent = br.getparent()
                prefix = previous.tail if previous is not None else parent.text
                if re.search(r"ПЗ:\s*[□☐◻\s]*$", prefix or "") and re.match(r"\s*[□☐◻]", br.tail or ""):
                    if previous is None:
                        parent.text = (prefix or "") + " " + br.tail.strip()
                    else:
                        previous.tail = (prefix or "") + " " + br.tail.strip()
                    parent.remove(br)
        for element in card.iter():
            for key in ("text", "tail"):
                value = getattr(element, key)
                if not value:
                    continue
                def substitute(match):
                    count = sum(match[2].count(c) for c in "□☐◻")
                    report["hit_points"].append({"semantic_id": card.get("data-semantic-id"), "count": count})
                    return match[1] + str(count) + (" " if match[2][-1:].isspace() else "") if hp["presentation"] == "numeric" else match[0]
                setattr(element, key, pattern.sub(substitute, value))
    actual = report["hit_points"]
    if "expected_counts" in hp and [row["count"] for row in actual] != hp["expected_counts"]:
        raise ValueError(f"hit point tracker count mismatch: {[row['count'] for row in actual]}")

    for choice in options["asset_choices"]:
        matches = tree.xpath('.//img[@src=$ref]', ref=choice["original_ref"])
        if not matches:
            raise ValueError("selected reader asset is not referenced")
        destination = "assets/reader/" + Path(choice["selected_ref"]).name
        if any(row["rendered_path"] == destination for row in report["asset_choices"]):
            raise ValueError("duplicate reader asset destination")
        for node in matches:
            node.set("src", destination)
        report["asset_choices"].append({**choice, "rendered_path": destination, "occurrences": len(matches)})

    source_issue_ids: set[str] = set()
    for decision in deferred_source_anchors:
        base = {"role", "issue_id", "source_page", "en_excerpt", "source_evidence", "reason", "placement"}
        optional_raw = {"raw_source_excerpt_en"} if "raw_source_excerpt_en" in decision else set()
        has_unit = isinstance(decision.get("unit"), dict)
        has_units = isinstance(decision.get("units"), list)
        required = base | ({"unit"} if has_unit and not has_units else {"units"})
        if (set(decision) != required | optional_raw or has_unit == has_units
                or decision.get("placement") != "first_visible_text_block_v1"
                or any(not isinstance(decision.get(key), str) or not decision[key].strip()
                       for key in ("issue_id", "en_excerpt", "source_evidence", "reason"))
                or (optional_raw and (not isinstance(decision["raw_source_excerpt_en"], str)
                                     or not decision["raw_source_excerpt_en"].strip()))
            or type(decision.get("source_page")) is not int or decision["source_page"] < 1
            or (has_unit and set(decision["unit"]) != {"unit_id", "ru_sha256"})
            or (has_units and (
                not decision["units"]
                or any(not isinstance(item, dict) or set(item) != {"unit_id", "ru_sha256"}
                       for item in decision["units"])
            ))):
            raise ValueError("source issue anchor requires exact provenance and placement")
        if decision["issue_id"] in source_issue_ids:
            raise ValueError("duplicate source issue anchor identity")
        source_issue_ids.add(decision["issue_id"])
        bindings = [decision["unit"]] if has_unit else decision["units"]
        bound_units = [bound(binding) for binding in bindings]
        if len({unit["unit_id"] for unit in bound_units}) != len(bound_units):
            raise ValueError("source issue anchor has duplicate RU units")
        if any(pages[unit["unit_id"]] != decision["source_page"] for unit in bound_units):
            raise ValueError("source issue anchor source page mismatch")
        if has_units:
            # Split siblings render as one assembled parent scope.  Resolving
            # each fragment independently would invite a first-fragment guess.
            from kb_creator.pipeline.five_step_language import _assemble_map
            assembled = _assemble_map(bound_units)["text"].strip()
            page = pages[bound_units[0]["unit_id"]]
            section = tree.xpath(f'.//section[@data-page="{page:03d}"]') if page is not None else [tree]
            candidates = [node for node in section[0].iterdescendants()
                          if isinstance(node.tag, str) and node.tag in {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "ul", "ol", "blockquote", "table"}
                          and norm(node.text_content()) == norm(assembled)]
            candidates = [node for node in candidates if not any(child in candidates for child in node.iterdescendants())]
            if len(candidates) != 1:
                raise ValueError("source issue split group has no unique assembled rendered scope")
            scopes = candidates
        else:
            scopes = [locate(binding) for binding in bindings]
        if any(tree not in scope.iterancestors() for scope in scopes):
            raise ValueError("source issue anchor target was removed by presentation")
        supported = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "figcaption", "li"}
        candidates = []
        for scope in scopes:
            for node in scope.iter():
                if node.tag not in supported or not node.text_content().strip():
                    continue
                lineage = [node, *node.iterancestors()]
                if any(item.get("hidden") is not None or item.get("aria-hidden") == "true"
                       or re.search(r"(?:display\s*:\s*none|visibility\s*:\s*hidden)", item.get("style", ""), re.I)
                       for item in lineage):
                    continue
                # A table cell is one Word paragraph in the existing builder. For
                # other containers prefer its first supported leaf text block.
                if node.tag not in {"td", "th"} and any(child.tag in supported for child in node.iterdescendants()):
                    continue
                candidates.append(node)
        if not candidates:
            raise ValueError("source issue anchor has no visible supported text block")
        target = candidates[0]
        target_text = target.text_content().strip()
        anchor_value = target.get("id") or "source-review-" + hashlib.sha256(
            ("\0".join(unit["unit_id"] for unit in bound_units) + "\0" + target_text).encode("utf-8")
        ).hexdigest()[:24]
        target.set("id", anchor_value)
        report["review_anchors"].append({**decision, "anchor": anchor_value, "target_text": target_text})
        report["display_roles"].append(decision)

    from kb_creator.pipeline import reader_block_relocation as relocations
    relocation_rows = relocations.apply(tree, projection, options, pages, bound, locate, anchor,
                                       bind_heading_occurrence=bind_heading_occurrence)
    ids = [e.get("id") for e in tree.iter() if e.get("id")]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate reader HTML IDs")
    for link in report["links"]:
        if link["target"] not in ids:
            raise ValueError("reader link target missing after projection")
    duplicates.finalize(tree, duplicate_rows, report, artifact_rows)
    for witness in report["standalone_running_headings"]:
        retained = locate(witness["retained"])
        if (tree not in retained.iterancestors()
                or retained.get("id") != witness["retained_anchor"]
                or duplicates._inline(retained) != witness["retained_text"]):
            raise ValueError("standalone running heading retained chapter changed or disappeared")
    for dependency in report["reflow_dependencies"]:
        matches = tree.xpath('.//*[@id=$anchor]', anchor=dependency["left_anchor"])
        if len(matches) != 1:
            raise ValueError("chained reflow left anchor is missing or ambiguous")
        owner = next((node for node in (matches[0], *matches[0].iterancestors())
                      if node.tag in {"p", "li"}), None)
        section = next((node for node in owner.iterancestors() if node.tag == "section"
                        and node.get("data-page")), None) if owner is not None else None
        if section is None:
            raise ValueError("chained reflow joined owner is outside a source page")
        final_page = int(section.get("data-page"))
        if final_page != dependency["left_page"]:
            if not any(other is not dependency and other["right_anchor"] == dependency["left_anchor"]
                       for other in report["reflow_dependencies"]):
                raise ValueError("reflow joined owner moved without an exact chained continuation")
            dependency["left_page"] = final_page
            dependency["source_pages"] = sorted({*dependency["source_pages"], final_page})
        dependency["joined_owner"]["text"] = duplicates._inline(owner)
    if extended_reflows:
        for spec in extended_reflows.values():
            for pair in spec["asset_pairs"]:
                if (tree not in pair["list_node"].iterancestors()
                        or tree not in pair["image_node"].iterancestors()
                        or html.tostring(pair["list_node"], encoding="unicode") != pair["list_snapshot"]
                        or html.tostring(pair["image_node"], encoding="unicode") != pair["image_snapshot"]):
                    raise ValueError("extended reflow changed retained map labels or original image")
            for figure in spec["standalone_figures"]:
                if (tree not in figure["node"].iterancestors()
                        or html.tostring(figure["node"], encoding="unicode") != figure["snapshot"]):
                    raise ValueError("guarded reflow changed retained original figure")
        touched_pages = {page for row in report["reflow_dependencies"] for page in row["source_pages"]}
        for page in sorted(touched_pages):
            sections = tree.xpath('.//section[@data-page=$page]', page=f"{page:03d}")
            if len(sections) != 1:
                raise ValueError("extended reflow source-page section changed")
            duplicates.append_page_witness(tree, report, page, duplicates.page_paragraphs(sections[0]),
                                           key="reflow_page_witness")
        omitted = {row["source_page"]: row["expected_paragraphs"] for row in report.get("duplicate_page_witness", [])}
        if any(row["source_page"] in omitted and row["expected_paragraphs"] != omitted[row["source_page"]]
               for row in report["reflow_page_witness"]):
            raise ValueError("reflow and omission page witnesses disagree")
    def paragraph_ordinal(page, anchor_value, *, first_list_item=False, chained_owner=False):
        sections = tree.xpath('.//section[@data-page=$page]', page=f"{page:03d}")
        matches = tree.xpath('.//*[@id=$anchor]', anchor=anchor_value)
        if len(sections) != 1 or len(matches) != 1:
            raise ValueError("reader native owner anchor has no unique source page")
        node = matches[0][0] if first_list_item else matches[0]
        if chained_owner and node.tag not in {"p", "li"}:
            node = next((ancestor for ancestor in node.iterancestors()
                         if ancestor.tag in {"p", "li"}), node)
        paragraphs = [item for item, _ in duplicates._page_paragraph_nodes(sections[0])]
        if node not in paragraphs:
            raise ValueError("reader native owner is not a source-page paragraph")
        return paragraphs.index(node)
    for row in report["retained_link_dependencies"]:
        row["retained_ordinal"] = paragraph_ordinal(row["retained_page"], row["target_anchor"])
    for dependency in report["reflow_dependencies"]:
        dependency["joined_owner"]["paragraph_ordinal"] = paragraph_ordinal(
            dependency["left_page"], dependency["left_anchor"], chained_owner=True)
        for owner in dependency["retained_title_owners"]:
            owner["paragraph_ordinal"] = paragraph_ordinal(owner.get("source_page", dependency["left_page"]), owner["anchor"])
        for pair in dependency["asset_pairs"]:
            pair["list_paragraph_ordinal"] = paragraph_ordinal(pair["source_page"], pair["list_anchor"],
                                                                 first_list_item=True)
    # Resolve adjacency after reviewed furniture omissions. A label is a plain
    # paragraph, not a navigational heading or a request to bind all body text.
    label_owners: set[str] = set()
    label_nodes = []
    for decision in deferred_labels:
        required = {"role", "unit", "next_unit", "source_evidence", "reason"}
        if (set(decision) != required
                or any(not isinstance(decision.get(key), str) or not decision[key].strip()
                       for key in ("source_evidence", "reason"))
                or any(not isinstance(decision.get(key), dict)
                       or set(decision[key]) != {"unit_id", "ru_sha256"}
                       for key in ("unit", "next_unit"))):
            raise ValueError("semantic label requires exact reviewed fields")
        label_unit, next_unit = (bound(decision[key]) for key in ("unit", "next_unit"))
        uids = {label_unit["unit_id"], next_unit["unit_id"]}
        if (len(uids) != 2 or label_unit["unit_id"] in label_owners
                or any(unit.get("parent_unit_id") is not None for unit in (label_unit, next_unit))
                or any(unit.get("parent_unit_id") in uids for unit in projection["units"])):
            raise ValueError("semantic label requires distinct whole unsplit units")
        for other in options["display_roles"]:
            if other is decision or other.get("role") == "source_issue_review_anchor":
                continue
            if uids.intersection(duplicates._refs(other)):
                raise ValueError("semantic label conflicts with another reader role")
        fragment, _, _ = markdown_to_review_html(
            label_unit["ru_text"], source_path=Path("label.md"),
            html_path=Path("label.html"), blockquote_heading_offset=0)
        blocks = html.fragment_fromstring(fragment, create_parent="main")
        if len(blocks) != 1 or blocks[0].tag != "p":
            raise ValueError("semantic label requires one plain source paragraph")
        # Repeated plain labels (for example two attack sections on one source
        # page) bind by their complete source cohort, never by the first match.
        page = pages[label_unit["unit_id"]]
        cohort = [unit for unit in projection["units"]
                  if pages[unit["unit_id"]] == page and unit["ru_text"] == label_unit["ru_text"]]
        section = tree.xpath('.//section[@data-page=$page]', page=f"{page:03d}") if page is not None else [tree]
        matches = ([node for node in section[0].xpath('.//p')
                    if heading_shape(node) == heading_shape(blocks[0])] if len(section) == 1 else [])
        if len(matches) != len(cohort):
            raise ValueError("semantic label source cohort differs from retained paragraphs")
        label = matches[[unit["unit_id"] for unit in cohort].index(label_unit["unit_id"])]
        successor = locate(decision["next_unit"])
        if (label.tag != "p" or not label.text_content().strip()
                or label.xpath('ancestor::blockquote | ancestor::table | ancestor::figure | ancestor::*[@data-semantic-kind] | .//img')
                or any(child.tag not in {"strong", "em", "b", "i", "code", "a", "span"}
                       for child in label.iterdescendants())
                or successor.tag not in {"p", "blockquote", "ul", "ol"}
                or successor.xpath('.//img')
                or tree not in label.iterancestors() or tree not in successor.iterancestors()
                or pages[label_unit["unit_id"]] != pages[next_unit["unit_id"]]
                or label.getparent() is not successor.getparent()
                or label.getnext() is not successor):
            raise ValueError("semantic label requires an adjacent retained text successor on the same page")
        label_nodes.append(label)
        label_owners.add(label_unit["unit_id"])
        report["display_roles"].append(decision)
    for label in label_nodes:
        label.set("data-semantic-kind", "label")
        label.set("data-keep-with-next", "true")
    relocations.finalize(tree, relocation_rows, report, master_root)
    from kb_creator.pipeline import reader_statblock_grouping
    reader_statblock_grouping.apply(tree, projection, grouping_options, pages, bound, report)
    return "\n".join(etree.tostring(e, encoding="unicode", method="html") for e in tree), effective, report


def copy_reader_assets(report: dict, options_path: Path, stage: Path, profile: dict) -> dict:
    effective = copy.deepcopy(profile)
    if report.get("omitted_text_duplicates") or report.get("duplicate_page_witness"):
        # Reopening replays every reader decision from archived inputs, including
        # selected image identities owned by otherwise unrelated reader roles.
        selected = {}
        for choice in report["asset_choices"]:
            selected[choice["selected_ref"]] = choice["selected"]
        for group in report.get("source_figure_regions", []):
            for region in group["regions"]:
                ref, expected = region["selected_ref"], region["selected"]
                if ref in selected and selected[ref] != expected:
                    raise ValueError("reader selected input has conflicting identities")
                selected[ref] = expected
        for ref, expected in selected.items():
            source = _local(options_path.parent, ref)
            target = _local(stage, ref)
            if not source.is_file() or identity(source) != expected:
                raise ValueError("reader selected input identity changed before archive")
            if target.exists():
                if not target.is_file() or identity(target) != expected:
                    raise ValueError("reader selected input archive collision")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            if identity(target) != expected:
                raise ValueError("reader selected input changed during archive")
    if report.get("source_figure_regions") and "figures" not in effective:
        effective["figures"] = {
            "default": {"max_width_mm": 176.0, "max_height_mm": 220.0, "keep_with_next": False},
            "overrides": {},
        }
    overrides = effective.get("figures", {}).get("overrides", {})
    visuals = {}
    for row in report.get("omitted_text_duplicates", []):
        visual = row["source_evidence"]["source_visual"]
        ref = visual["path"]
        if ref in visuals and visuals[ref] != visual:
            raise ValueError("duplicate text visual path has conflicting identities")
        visuals[ref] = visual
    for row in report.get("omitted_artifacts", []):
        evidence = row.get("source_evidence")
        if not isinstance(evidence, dict):
            continue
        visual = evidence["source_visual"]
        ref = visual["path"]
        if ref in visuals and visuals[ref] != visual:
            raise ValueError("whole artifact visual path has conflicting identities")
        visuals[ref] = visual
    for ref, visual in visuals.items():
        source = _local(options_path.parent, ref)
        target = _local(stage, ref)
        if target.exists() or not source.is_file() or identity(source) != {key: visual[key] for key in ("bytes", "sha256")}:
            raise ValueError("duplicate text evidence copy collision or stale identity")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if identity(target) != {key: visual[key] for key in ("bytes", "sha256")}:
            raise ValueError("duplicate text evidence changed while copying")
    for choice in report["asset_choices"]:
        target = _local(stage, choice["rendered_path"])
        if target.exists():
            raise ValueError("reader asset destination already exists")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(_local(options_path.parent, choice["selected_ref"]), target)
        if identity(target) != choice["selected"]:
            raise ValueError("reader asset changed while copying")
        if choice["original_ref"] in overrides and choice["rendered_path"] not in overrides:
            overrides[choice["rendered_path"]] = copy.deepcopy(overrides[choice["original_ref"]])
    for group in report.get("source_figure_regions", []):
        for region in group["regions"]:
            target = _local(stage, region["rendered_path"])
            if target.exists():
                raise ValueError("source figure region destination already exists")
            selected = _local(options_path.parent, region["selected_ref"])
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(selected, target)
            if identity(target) != region["selected"]:
                raise ValueError("source figure region changed while copying")
            overrides[region["rendered_path"]] = copy.deepcopy(region["figure_policy"])
    return effective
