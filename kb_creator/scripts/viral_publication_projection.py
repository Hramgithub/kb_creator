"""Source-coordinate projection of Viral's reviewed publication boundaries.

This is authoring, not post-processing: source lines are partitioned once and
typed events own their exact source spans before the Markdown renderer runs.
"""
from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class SourceText:
    text: str
    slices: list[dict]
    joiner: str = ""


class Projection:
    def __init__(self, author):
        self.a = author
        self.base = author._author_b1c3()
        self.v1 = author.verify_inputs()["v1"]
        self.assets = author.asset_b1c4_projection()
        self.raw = {p: (author.PACKAGE / f"pages/page-{p:03d}.md").read_bytes() for p in range(1, 123)}
        self.lines = []
        self.spans = []
        self.events = []
        self.hierarchy = []
        self.heading_lines = {}
        self.assigned = set()
        self.old_xrefs = self.base["xrefs"]
        self.old_spans = {s["span_id"]: s for s in self.base["source_partition"]["spans"]}
        self.units = author.approved_ledgers()
        self.intervals = author._ledger_intervals(author.PACKAGE)
        self.partition_lines()

    def partition_lines(self):
        markers = {(a["source_page"], a["provenance"]["start_byte"]): a for a in self.assets if a["provenance"]["kind"] == "markdown_image_reference"}
        for page, raw in self.raw.items():
            cuts = {0, len(raw)}
            for left, right in self.a._line_boundaries(raw):
                cuts.update((left, right))
            for (p, start), asset in markers.items():
                if p != page:
                    continue
                end = asset["provenance"]["end_byte"]
                cuts = {c for c in cuts if not start < c < end} | {start, end}
            # p60 contains an epigraph and its following prose in one source
            # line. Split only at the reviewed closing quote.
            if page == 60:
                marker = b'"I See Dead People. When? All The Time... Unless I\'m Drunk."'
                start = raw.find(marker)
                if start >= 0:
                    cuts.add(start + len(marker))
            for start, end in zip(sorted(cuts), sorted(cuts)[1:]):
                asset = markers.get((page, start))
                sid = asset["provenance"]["span_id"] if asset else f"span-p{page:03d}-b{start:06d}"
                text = raw[start:end].decode("utf-8")
                char_start = len(raw[:start].decode("utf-8"))
                classification = "layout_separator" if not text.strip() else "technical_marker_suppression" if text.strip().startswith("<!--") else "retained_text"
                span = {"span_id": sid, "page": page, "source_path": f"pages/page-{page:03d}.md", "start_byte": start, "end_byte": end, "start_char": char_start, "end_char": char_start + len(text), "raw_sha256": self.a.sha256_bytes(raw[start:end]), "raw_text_sha256": self.a.sha256_bytes(text.encode()), "classification": "asset_reference_source" if asset else classification, "owner_kind": "asset" if asset else "suppression", "owner_id": asset["asset_id"] if asset else f"suppression:{sid}", "decision_ref": "OUT-001" if classification == "technical_marker_suppression" else None}
                self.spans.append(span)
                self.lines.append({"span": span, "text": text, "asset": asset})

    def piece(self, line, start=0, end=None):
        text = line["text"]
        end = len(text) if end is None else end
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
        if start == end:
            return SourceText("", [])
        span = line["span"]
        return SourceText(text[start:end], [{"span_id": span["span_id"], "start_char": span["start_char"] + start, "end_char": span["start_char"] + end}])

    def plain(self, line):
        match = re.match(r"\s*#{1,6}\s+", line["text"])
        return self.piece(line, match.end() if match else 0)

    def joined(self, values, joiner="\n"):
        values = [v for v in values if v.text]
        if any(v.joiner and len(v.slices) > 1 for v in values):
            raise self.a.AuthoringError("E_V2_AUTHOR_NESTED_JOIN")
        return SourceText(joiner.join(v.text for v in values), [s for v in values for s in v.slices], joiner)

    def paragraph_text(self, lines):
        """Keep source paragraph separation without inventing binding bytes."""
        values, separators = [], []
        for index, line in enumerate(lines):
            if index:
                previous = lines[index - 1]["span"]
                current = line["span"]
                gaps = [l for l in self.lines if l["span"]["page"] == current["page"] == previous["page"] and previous["end_byte"] <= l["span"]["start_byte"] < current["start_byte"] and not l["text"].strip() and "\n" in l["text"] and l["span"]["span_id"] not in self.assigned]
                if gaps:
                    gap = gaps[0]
                    start = gap["span"]["start_char"] + gap["text"].index("\n")
                    values.append(SourceText("\n", [{"span_id": gap["span"]["span_id"], "start_char": start, "end_char": start + 1}]))
                    separators.append(gap)
            values.append(self.piece(line))
        return self.joined(values), separators

    def paragraph_joiner(self, lines):
        """Return the reviewed Markdown separator encoded by source gaps."""
        boundaries = []
        for previous, current in zip(lines, lines[1:]):
            if previous["span"]["page"] != current["span"]["page"]:
                boundaries.append(False)
                continue
            gaps = [
                line for line in self.lines
                if line["span"]["page"] == current["span"]["page"]
                and previous["span"]["end_byte"] <= line["span"]["start_byte"] < current["span"]["start_byte"]
                and not line["text"].strip()
                and "\n" in line["text"]
            ]
            boundaries.append(bool(gaps))
        if any(boundaries) and not all(boundaries):
            raise self.a.AuthoringError("E_V2_AUTHOR_MIXED_PARAGRAPH_BOUNDARIES")
        return "\n\n" if boundaries and all(boundaries) else "\n"

    def payload(self, data, pointer="/content"):
        bindings = []
        def walk(value, path):
            if isinstance(value, SourceText):
                if value.text:
                    bindings.append({"json_pointer": path, "source_slices": value.slices, "joiner": value.joiner, "recovery_id": None})
                return value.text
            if isinstance(value, list):
                return [walk(v, f"{path}/{i}") for i, v in enumerate(value)]
            if isinstance(value, dict):
                return {k: walk(v, f"{path}/{k}") for k, v in value.items()}
            return value
        return walk(data, pointer), bindings

    def event(self, eid, kind, lines, anchor, data):
        lines = sorted(lines, key=lambda l: (l["span"]["page"], l["span"]["start_byte"]))
        if not lines or any(l["span"]["span_id"] in self.assigned for l in lines):
            raise self.a.AuthoringError(f"E_V2_AUTHOR_EVENT_OVERLAP: {eid}")
        ids = [l["span"]["span_id"] for l in lines]
        if kind == "structured_unit":
            data["contains"] = ids
            if data["kind"] in {"callout", "ordered_list_callout", "equipment_card", "creature_statblock"}:
                data["end_after"] = ids[-1]
        content, bindings = self.payload(data)
        first = lines[0]["span"]
        event = {"event_id": eid, "type": kind, "page": first["page"], "order_key": [first["page"], first["start_byte"], {"heading": 0, "anchor_only": 1, "text_fragment": 2, "structured_unit": 3, "asset": 4}[kind], 0], "anchor": anchor, "content": content, "fragment_id": ids[0], "source_span_ids": ids, "source_operation": {"heading": "emit_exact", "anchor_only": "emit_anchor_only", "text_fragment": "emit_exact", "structured_unit": "semantic_restructure", "asset": "asset_reference"}[kind], "payload_bindings": bindings}
        if kind == "structured_unit":
            event["contains"] = ids
        for line in lines:
            span = line["span"]
            self.assigned.add(span["span_id"])
            if kind != "asset":
                span.update(owner_kind="event", owner_id=eid, classification="retained_heading" if kind == "heading" else "reviewed_structured_source" if kind == "structured_unit" else "retained_text")
        self.events.append(event)
        return event

    def unit_lines(self, unit):
        selected = []
        for page, intervals in self.intervals.items():
            ranges = [(start, end) for start, end, u in intervals if u["id"] == unit["id"]]
            selected.extend(l for l in self.lines if l["span"]["page"] == page and any(a <= l["span"]["start_byte"] and l["span"]["end_byte"] <= b for a, b in ranges))
        return selected

    @staticmethod
    def normal(text):
        return re.sub(r"\s+", " ", re.sub(r"^#{1,6}\s+", "", text.strip())).casefold()

    def available(self, lines):
        return [l for l in lines if l["span"]["span_id"] not in self.assigned and not l["asset"] and l["text"].strip() and not l["text"].strip().startswith("<!--")]

    def anchor_at(self, line):
        key = (line["span"]["page"], line["span"]["start_byte"])
        preceding = [e for e in self.events if e["type"] == "heading" and (e["page"], e["order_key"][1]) <= key]
        return max(preceding, key=lambda e: tuple(e["order_key"]))["anchor"] if preceding else "viral"

    def headings(self):
        rows = [h for h in self.base["hierarchy"]]
        original = {h["anchor"]: h for h in self.v1["hierarchy"]}
        explicit = {}
        for row in rows:
            frozen = original[row["anchor"]]
            locators = frozen["assembly_binding"]["locators"]
            if frozen["assembly_binding"]["kind"] == "owned_page_unit" and min(row["source_pages"]) >= 69:
                candidates = [l for l in self.lines if l["span"]["page"] == min(row["source_pages"]) and re.match(r"^#{1,6}\s", l["text"])]
                if candidates:
                    explicit[row["anchor"]] = (candidates[0], {"action": "replace_heading"})
            for loc in locators:
                if not loc.get("selector"):
                    continue
                wanted = self.normal(loc["selector"])
                matches = [l for l in self.lines if l["span"]["page"] == loc["page"] and (self.normal(l["text"]).startswith(wanted) if loc["selector_kind"] == "line_prefix" else self.normal(l["text"]) == wanted)]
                if matches:
                    explicit[row["anchor"]] = (matches[loc.get("occurrence", 1) - 1], loc)
                    break
        # Reviewed standalone headings absent from the inherited outline are
        # added; stale ledger aliases resolve through exact source coordinates.
        for unit in self.units:
            if unit["kind"] not in {"heading", "section_with_run_ins", "location_section"}:
                continue
            lines = self.available(self.unit_lines(unit))
            title = unit.get("title_or_label")
            matching = [l for l in lines if title and self.normal(l["text"]) == self.normal(title)]
            if not matching:
                continue
            line = matching[0]
            anchors = [a for a, (candidate, _) in explicit.items() if candidate is line]
            anchor = anchors[0] if anchors else unit.get("final_owner_anchor") or unit["id"]
            if anchor not in {h["anchor"] for h in rows}:
                parent = "viral-isola-hospital-locations" if "hospital" in anchor else "viral-one-night-in-perla-npcs" if "npcs-" in anchor else "viral"
                rows.append({"anchor": anchor, "parent_anchor": parent, "level": 5 if "Hospital," in title else 4, "toc_entry": False, "semantic_role": "section", "source_pages": [line["span"]["page"]], "source_title": title, "reader_title": title, "representation": "heading", "reviewed_title_transformation": None, "migration_row_id": f"hierarchy:{anchor}"})
            explicit[anchor] = (line, {"action": "replace_heading"})
            if unit.get("outline_representation", "").startswith("h") and unit["outline_representation"][1:].isdigit():
                next(h for h in rows if h["anchor"] == anchor)["level"] = int(unit["outline_representation"][1:])
        # Root title has an existing reviewed source heading, not a generated label.
        root = next(l for l in self.lines if l["span"]["page"] == 1 and self.normal(l["text"]) == "viral")
        explicit["viral"] = (root, {"action": "replace_heading"})
        generated = {"viral-contents", "viral-player-handouts", "viral-keeper-maps", "viral-pregenerated-investigators"}
        for row in rows:
            anchor = row["anchor"]
            found = explicit.get(anchor)
            if found and found[0]["span"]["span_id"] in self.assigned and original.get(anchor, {}).get("assembly_binding", {}).get("kind") == "owned_page_unit":
                found = None
            if found and found[1]["action"] == "replace_heading":
                line = found[0]
                if line["span"]["span_id"] in self.assigned:
                    raise self.a.AuthoringError(f"E_V2_AUTHOR_HEADING_DUPLICATE: {anchor}")
                text = self.plain(line)
                row.update(source_title=text.text, reader_title=text.text, representation="heading", level=row["level"] or original.get(anchor, {}).get("level", 4))
                self.event(f"heading:{anchor}", "heading", [line], anchor, text)
                self.heading_lines[anchor] = line
            elif found and found[1]["action"] == "replace_label_retain_remainder" and "cold-spot" not in anchor:
                line, loc = found
                text = self.plain(line)
                delimiter = re.search(r"\s+[–—]\s*", text.text)
                if delimiter is None:
                    raise self.a.AuthoringError(f"E_V2_AUTHOR_RUNIN_SEPARATOR: {anchor}")
                offset = line["text"].find(text.text)
                label = self.piece(line, offset, offset + delimiter.start())
                remainder = self.piece(line, offset + delimiter.start())
                row.update(source_title=label.text, reader_title=label.text, representation="inline_run_in", level=None)
                self.event(f"run-in:{anchor}", "structured_unit", [line], anchor, {"kind": "inline_run_in", "anchor": anchor, "label": label, "xref": remainder})
            else:
                page = min(row["source_pages"])
                # Addressability is not an invented visible source heading.
                candidates = [l for l in self.lines if l["span"]["page"] == page and l["span"]["span_id"] not in self.assigned and not l["asset"] and (not l["text"].strip() or l["text"].strip().startswith("<!--"))]
                if not candidates:
                    raise self.a.AuthoringError(f"E_V2_AUTHOR_ANCHOR_SLOT: {anchor}")
                line = candidates[0]
                kind = "heading" if anchor in generated else "anchor_only"
                row.update(representation="heading" if kind == "heading" else "anchor_only", level=original[anchor]["level"] if kind == "heading" else None)
                self.event(f"heading:{anchor}" if kind == "heading" else f"anchor:{anchor}", kind, [line], anchor, "")
            self.hierarchy.append(row)

        # Only the two sealed source recoveries are supplied. The missing tome
        # heading belongs immediately before the book, not at the page start.
        row = next(h for h in self.hierarchy if h["anchor"] == "viral-appendix-new-mythos-tome")
        event = next(e for e in self.events if e["anchor"] == row["anchor"])
        old = next(l for l in self.lines if l["span"]["span_id"] == event["source_span_ids"][0])
        self.events.remove(event)
        self.assigned.remove(old["span"]["span_id"])
        old["span"].update(owner_kind="suppression", owner_id="suppression:" + old["span"]["span_id"], classification="technical_marker_suppression")
        title_line = next(l for l in self.lines if l["span"]["page"] == 67 and l["text"].strip() == "Iuramentum Corruptionis")
        slots = [l for l in self.lines if l["span"]["page"] == 67 and l["span"]["end_byte"] <= title_line["span"]["start_byte"] and not l["text"].strip() and l["span"]["span_id"] not in self.assigned]
        recovery = next(r for r in self.a.source_graph()["source_recoveries"] if r["source_text"] == "New Mythos Tome")
        event = self.event("heading:" + row["anchor"], "heading", [slots[-1]], row["anchor"], "")
        recovery["target_event_id"] = event["event_id"]
        self.base["source_recoveries"].append(recovery)
        event["content"] = recovery["source_text"]
        event["payload_bindings"] = [{"json_pointer": "/content", "source_slices": None, "joiner": "", "recovery_id": recovery["recovery_id"]}]
        row.update(representation="heading", level=3, source_title=recovery["source_text"], reader_title=recovery["source_text"])

    def table(self, unit, lines):
        pipe_lines = [l for l in lines if l["text"].strip().startswith("|")]
        rows, header = [], None
        owned = []
        if pipe_lines:
            for line in pipe_lines:
                boundaries = [m.start() for m in re.finditer(r"(?<!\\)\|", line["text"])]
                cells = [self.piece(line, left + 1, right) for left, right in zip(boundaries, boundaries[1:])]
                owned.append(line)
                if all(re.fullmatch(r":?-+:?", c.text) for c in cells):
                    continue
                if header is None:
                    header = cells
                elif [c.text for c in cells] != [c.text for c in header]:
                    rows.append(cells)
        else:
            header_line = next((l for l in lines if l["text"].strip() in {"Roll Phenomenon Encountered", "D10 Roll Result"}), None)
            if header_line is None:
                raise self.a.AuthoringError(f"E_V2_AUTHOR_TABLE_HEADER: {unit['id']}")
            text = header_line["text"]
            cut = text.index(" Result") if "D10" in text else text.index(" Phenomenon")
            header = [self.piece(header_line, 0, cut), self.piece(header_line, cut)]
            owned.append(header_line)
            for line in lines[lines.index(header_line) + 1:]:
                match = re.match(r"\s*(\d+)\s+", line["text"])
                if match:
                    rows.append([self.piece(line, match.start(1), match.end(1)), self.piece(line, match.end())])
                    owned.append(line)
                elif rows:
                    rows[-1][-1] = self.joined([rows[-1][-1], self.piece(line)], " ")
                    owned.append(line)
        expected = unit.get("structured") or {}
        count = expected.get("expected_row_count", expected.get("expected_item_count"))
        if count is not None and count != len(rows):
            raise self.a.AuthoringError(f"E_V2_AUTHOR_TABLE_ROWS: {unit['id']}: {len(rows)} != {count}")
        keys = expected.get("ordered_keys")
        if keys and [r[0].text for r in rows] != list(map(str, keys)):
            raise self.a.AuthoringError(f"E_V2_AUTHOR_TABLE_KEYS: {unit['id']}")
        # Repeated continuation labels are source apparatus, not another table.
        for line in lines:
            if "(continued)" in line["text"] and line not in owned:
                owned.append(line)
        return self.event(f"structure:{unit['id']}", "structured_unit", owned, self.anchor_at(owned[0]), {"kind": "table", "header": header, "rows": rows, "row_count": len(rows), "cell_count": sum(len(r) for r in rows)})

    def containers(self):
        # Tables first: a reviewed callout can contain a table but cannot steal
        # its rows. Series segments are independent bounded inserts.
        for unit in self.units:
            if unit["kind"] in {"table", "logical_table"}:
                self.table(unit, self.available(self.unit_lines(unit)))
        for unit in self.units:
            kind = unit["kind"]
            if kind not in {"callout", "callout_series", "ordered_callout", "equipment_card"}:
                continue
            groups = [self.unit_lines(unit)]
            if kind == "callout_series":
                groups = []
                for page, ranges in self.intervals.items():
                    for start, end, candidate in ranges:
                        if candidate["id"] == unit["id"]:
                            groups.append([l for l in self.lines if l["span"]["page"] == page and start <= l["span"]["start_byte"] and l["span"]["end_byte"] <= end])
                if unit["id"] == "viral-keepers-notes-series-p041-p061":
                    def group_with(prefix):
                        matches = [group for group in groups if any(line["text"].strip().startswith(prefix) for line in group)]
                        if len(matches) != 1:
                            raise self.a.AuthoringError(f"E_V2_AUTHOR_REVIEWED_NOTE: {prefix}")
                        return matches[0]

                    # Overlook Point is one reviewed gray box across p46/p47.
                    overlook = group_with("The path over the rocks is difficult")
                    continuation = group_with("Reaching the end has the reward")
                    overlook.extend(continuation)
                    groups.remove(continuation)

                    # The Witch Board paragraph is part of the same visually
                    # closed Keeper's Notes inset as the Crypt altar text.
                    group_with("The crypt altar is where Maya recommended")

                    # The Catacombs note continues at the top of p49.
                    catacombs = group_with("If the Investigators attempt to steal any grave goods")
                    for page, prefix in ((49, "At this point, the Reliquae"), (49, "Scattered throughout the catacombs")):
                        matches = [line for line in self.lines if line["span"]["page"] == page and line["text"].strip().startswith(prefix)]
                        if len(matches) != 1:
                            raise self.a.AuthoringError(f"E_V2_AUTHOR_REVIEWED_NOTE: {prefix}")
                        catacombs.append(matches[0])
            for index, raw_group in enumerate(groups):
                lines = [line for line in self.available(raw_group) if not line["text"].strip().startswith("![")]
                if not lines:
                    continue
                if kind == "equipment_card":
                    data = {"kind": "equipment_card", "title": self.plain(lines[0]), "stats": "", "footnote": "", "body": self.joined([self.plain(l) for l in lines[1:]])}
                    if "dss-incendiary" in unit["id"]:
                        data.update(stats=self.piece(lines[1]), footnote=self.piece(lines[2]), body="")
                elif kind == "ordered_callout":
                    items = []
                    for line in lines:
                        # A marker owned by a separate asset event is never
                        # serialized into a structured body.
                        if line["text"].strip().startswith("!["):
                            continue
                        match = re.match(r"\s*\d+\.\s+", line["text"])
                        if not match:
                            raise self.a.AuthoringError(f"E_V2_AUTHOR_ORDERED_ITEM: {unit['id']}")
                        items.append(self.piece(line, match.end()))
                    if len(items) != unit["structured"]["expected_item_count"]:
                        raise self.a.AuthoringError("E_V2_AUTHOR_ORDERED_COUNT")
                    data = {"kind": "ordered_list_callout", "items": items, "item_count": len(items)}
                else:
                    # Blank quote lines preserve paragraphs while explicit
                    # contains/end_after stop the insert before parent prose.
                    body = []
                    for line in lines:
                        if body:
                            body.append("")
                        body.append(self.plain(line))
                    data = {"kind": "callout", "body": body}
                self.event(f"structure:{unit['id']}:{index:02d}", "structured_unit", lines, self.anchor_at(lines[0]), data)

        def reviewed_callout(page, event_id, prefixes):
            """Materialize one visually reviewed inset without widening its bounds."""
            lines = []
            for prefix in prefixes:
                matches = [
                    line for line in self.lines
                    if line["span"]["page"] == page
                    and line["span"]["span_id"] not in self.assigned
                    and line["text"].strip().startswith(prefix)
                ]
                if len(matches) != 1:
                    raise self.a.AuthoringError(f"E_V2_AUTHOR_REVIEWED_CALLOUT: {page}:{prefix}")
                lines.append(matches[0])
            body = []
            for line in lines:
                if body:
                    body.append("")
                body.append(self.plain(line))
            return self.event(event_id, "structured_unit", lines, self.anchor_at(lines[0]), {"kind": "callout", "body": body})

        # OUT-039: these visually closed panels were flattened by the reviewed
        # merge even though their source order and exact text survived.  Keep
        # the finite, user-reviewed boundaries here; surrounding prose remains
        # outside each inset.
        reviewed_callout(
            48,
            "structure:viral-live-stream-callout-p048",
            (
                "Live Stream",
                "At this point, the live stream has been cut",
                "Maya is aware that the feed is cut",
                "During all of this, the DSS has been in communication",
            ),
        )
        for slug, title, body_prefix in (
            ("open-the-sight", "Open the Sight", "This means opening the mind"),
            ("close-the-sight", "Close the Sight", "This means shutting out all external psychic forces"),
            ("sensing-a-presence", "Sensing a Presence", "The Sighted Investigator tries to sense"),
            ("echoes-of-the-past", "Echoes of the Past", "By touching an object or location"),
            ("precognition", "Precognition", "By opening The Sight just a little"),
            ("calm-the-mind", "Calm the Mind", "If the Investigator experiences a vision or entity"),
        ):
            reviewed_callout(
                61,
                f"structure:viral-sight-{slug}-callout-p061",
                (title, body_prefix),
            )

        climb = []
        for prefix in ("Why Not Use the Climb Skill?", "There are a number of reasons."):
            matches = [line for line in self.lines if line["span"]["page"] == 51 and line["text"].strip().startswith(prefix)]
            if len(matches) != 1:
                raise self.a.AuthoringError(f"E_V2_AUTHOR_REVIEWED_CLIMB: {prefix}")
            climb.append(matches[0])
        if any(line["span"]["span_id"] in self.assigned for line in climb):
            raise self.a.AuthoringError("E_V2_AUTHOR_REVIEWED_CLIMB: overlap")
        self.event(
            "structure:viral-why-not-use-the-climb-skill-p051",
            "structured_unit",
            climb,
            self.anchor_at(climb[0]),
            {"kind": "callout", "body": [self.plain(climb[0]), "", self.plain(climb[1])]},
        )

        for unit in self.units:
            if unit["kind"] != "inline_run_in":
                continue
            lines = self.available(self.unit_lines(unit))
            if not lines:
                continue
            title = unit.get("title_or_label")
            first = self.plain(lines[0])
            if not title or not first.text.startswith(title):
                raise self.a.AuthoringError(f"E_V2_AUTHOR_REVIEWED_RUNIN: {unit['id']}")
            offset = lines[0]["text"].find(first.text)
            label = self.piece(lines[0], offset, offset + len(title))
            remainder = [self.piece(lines[0], offset + len(title))] + [self.plain(l) for l in lines[1:]]
            parent = self.anchor_at(lines[0])
            anchor = unit["id"]
            self.hierarchy.append({"anchor": anchor, "parent_anchor": parent, "level": None, "toc_entry": False, "semantic_role": "run_in", "source_pages": sorted({l["span"]["page"] for l in lines}), "source_title": label.text, "reader_title": label.text, "representation": "inline_run_in", "reviewed_title_transformation": None, "migration_row_id": "hierarchy:" + anchor})
            self.event(
                "run-in:" + anchor,
                "structured_unit",
                lines,
                anchor,
                {
                    "kind": "inline_run_in",
                    "anchor": anchor,
                    "label": label,
                    "xref": self.joined(remainder, self.paragraph_joiner(lines)),
                },
            )

    def creatures(self):
        for unit in self.units:
            if unit["kind"] != "creature_statblock":
                continue
            lines = self.available(self.unit_lines(unit))
            # The Reliquae introduction remains ordinary section text before
            # the stat card; the original duplicated title was absent in v4.
            if "reliquae" in unit["id"]:
                lines = lines[next(i for i, l in enumerate(lines) if l["text"].startswith("STR:")):]
            values = {k: [] for k in ("title", "subtitle", "characteristics", "derived_stats", "attacks", "abilities", "nested_tables")}
            phase = "title"
            for line in lines:
                text = line["text"].strip()
                if re.match(r"^(STR|CON|SIZ|POW|DEX|INT|APP):", text):
                    phase = "characteristics"
                elif text.startswith("HP:"):
                    phase = "derived_stats"
                elif text == "ATTACKS":
                    phase = "attacks"
                elif text == "SPECIAL ABILITIES":
                    phase = "abilities"
                elif text.startswith("|"):
                    phase = "nested_tables"
                elif text.startswith("Aspect of"):
                    phase = "subtitle"
                values[phase].append(self.piece(line))
            data = {"kind": "creature_statblock", **{k: self.joined(v) for k, v in values.items()}}
            nested = [l for l in lines if l["text"].strip().startswith("|")]
            if nested:
                data["nested_tables"], gaps = self.paragraph_text(nested)
                lines.extend(gaps)
            event = self.event(f"structure:{unit['id']}", "structured_unit", lines, self.anchor_at(lines[0]), data)
            if "reliquae" in unit["id"]:
                recovery = next(r for r in self.a.source_graph()["source_recoveries"] if r["source_text"] == "Cursed Plague Zombies")
                recovery["target_event_id"] = event["event_id"]
                self.base["source_recoveries"].append(recovery)
                event["content"]["subtitle"] = recovery["source_text"]
                event["payload_bindings"].append({"json_pointer": "/content/subtitle", "source_slices": None, "joiner": "", "recovery_id": recovery["recovery_id"]})

    def physical_units(self):
        for unit in self.units:
            if unit["kind"] not in {"full_page_map", "physical_page_pair"}:
                continue
            lines = self.available(self.unit_lines(unit))
            pages = sorted({s["page"] for s in unit["source_segments"]})
            reader = [a for a in self.assets if a["source_page"] in pages and a["disposition"] == "reader"]
            if unit["kind"] == "physical_page_pair":
                # The front remains a full page; only the back has separately
                # translatable semantics. Preserve its paragraph breaks.
                back = [l for l in lines if l["span"]["page"] == pages[1] and not l["text"].strip().startswith("![")]
                semantics, gaps = self.paragraph_text(back)
                data = {"kind": "physical_page_pair", "front_page": pages[0], "back_page": pages[1], "front_reader_asset_ids": [a["asset_id"] for a in reader if a["source_page"] == pages[0]], "back_reader_asset_ids": [a["asset_id"] for a in reader if a["source_page"] == pages[1]], "back_semantics": semantics}
                owned = back + gaps
            else:
                key = [l for l in lines if re.match(r"^[A-V]\. ", l["text"])]
                legend = next(l for l in lines if l["text"].startswith("Legend:"))
                scale_start = legend["text"].index("Scale:")
                data = {"kind": "full_page_map", "pages": pages, "reader_asset_ids": [a["asset_id"] for a in reader], "accessible_key": self.joined([self.piece(l) for l in key]), "legend": self.piece(legend, len("Legend:"), scale_start), "scale": self.piece(legend, scale_start + len("Scale:"))}
                owned = key + [legend]
            # Reviewed full-page replacement also owns obsolete child-crop
            # markers inside its source range. They do not become prose or
            # duplicate image events, but cannot be foreign gaps in the unit.
            first, last = owned[0]["span"], max(owned, key=lambda l: (l["span"]["page"], l["span"]["start_byte"]))["span"]
            for line in lines:
                span = line["span"]
                if line not in owned and (first["page"], first["start_byte"]) <= (span["page"], span["start_byte"]) <= (last["page"], last["start_byte"]) and line["text"].strip().startswith("!["):
                    owned.append(line)
            event = self.event(f"structure:{unit['id']}", "structured_unit", owned, self.anchor_at(owned[0]), data)
            for asset in reader:
                asset.update(anchor=event["anchor"], placement={"before_event": event["event_id"]}, source_order={"kind": "physical_unit_page_slot", "unit_id": unit["id"], "page_slot": pages.index(asset["source_page"])})

    def remaining_text(self):
        # MinerU image descriptions are metadata, not narrative. Require an
        # exact same-page image-alt match, never a general prose heuristic.
        descriptions = {}
        for p, raw in self.raw.items():
            descriptions[p] = set(re.findall(r"!\[([^\]]+)\]\(", raw.decode("utf-8")))
        for line in self.available(self.lines):
            text = line["text"].strip()
            span = line["span"]
            hud = span["page"] == 1 and text in {"## UNREDACTED", "## HD", "## 22:13:35", "●", "## REC"}
            if text.startswith("![") or text in descriptions[span["page"]] or span["page"] == 5 or hud:
                span.update(classification="authorized_suppression", decision_ref="OUT-002" if span["page"] == 5 else "PROC-010")
                continue
            self.event(f"text:{span['span_id']}", "text_fragment", [line], self.anchor_at(line), self.plain(line))

    def cross_references(self):
        by_span = {sid: e for e in self.events for sid in e["source_span_ids"]}
        frozen = {r["xref_id"]: r for r in self.v1["xrefs"]}
        result = []
        for row in self.old_xrefs:
            slices = []
            owners = []
            for old_slice in row["source_slices"]:
                matches = [s for s in self.spans if s["page"] == row["source_page"] and s["start_char"] <= old_slice["start_char"] and old_slice["end_char"] <= s["end_char"]]
                if len(matches) != 1:
                    raise self.a.AuthoringError("E_V2_AUTHOR_XREF_REBIND_RANGE")
                span = matches[0]
                slices.append({**old_slice, "span_id": span["span_id"]})
                owners.append(by_span[span["span_id"]])
            if len({e["event_id"] for e in owners}) != 1:
                raise self.a.AuthoringError("E_V2_AUTHOR_XREF_REBIND_OWNER")
            event = owners[0]
            original_id = re.sub(r"-segment-\d+$", "", row["xref_id"])
            expected_owner = frozen[original_id]["owner_anchor"]
            event["anchor"] = expected_owner
            result.append({**row, "source_event_id": event["event_id"], "source_slices": slices})
        self.base["xrefs"] = result

    def art(self):
        import json
        old_events = {e["event_id"]: e for e in self.base["events"]}
        by_span = {sid: e for e in self.events for sid in e["source_span_ids"]}
        order = self.a.resolve_asset_source_order(comparison=json.loads(self.a.COMPARISON.read_text(encoding="utf-8")), manifest_assets=json.loads((self.a.PACKAGE / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))["assets"], reader_assets=[a for a in self.assets if a["disposition"] == "reader"], events=self.base["events"], physical_units=self.a._physical_units())
        resolutions = {r["asset_id"]: r for r in order["rows"]}
        reviewed = self.a.reviewed_remaining_asset_anchors(self.events)
        event_by_id = {e["event_id"]: e for e in self.events}
        for asset in self.assets:
            page = asset["source_page"]
            asset.setdefault("anchor", None)
            asset.setdefault("placement", None)
            asset.setdefault("source_order", None)
            if asset["disposition"] != "reader":
                continue
            resolution = resolutions[asset["asset_id"]]
            if not asset["placement"]:
                if asset["asset_id"] in reviewed:
                    proof = reviewed[asset["asset_id"]]
                    anchor = proof["anchor"]
                    if page in {31, 32}:
                        anchor = "viral-isola-plots-and-schemes"
                    if page in {108, 109}:
                        anchor = "viral-keeper-map-second-third-floors" if page == 108 else "viral-keeper-map-administrators-house-east-wing-attic"
                    target = event_by_id.get(proof.get("placement_event_id"))
                    if target is None:
                        target = next(e for e in self.events if e["anchor"] == anchor and e["type"] in {"heading", "anchor_only"})
                    # Reviewed declarations state semantic reader order
                    # explicitly; the historical physical-page cases retain
                    # their established relation.
                    relation = proof.get("relation", "after_event" if page in {100, 102, 108, 109, 110} else "before_event")
                    asset.update(anchor=anchor, placement={relation: target["event_id"]})
                elif resolution.get("anchor_evidence"):
                    proof = resolution["anchor_evidence"]
                    old_event = old_events[proof["event_id"]]
                    old_span = self.old_spans[old_event["source_span_ids"][0]]
                    point = old_span["start_char"] + proof["start_char"]
                    spans = [s for s in self.spans if s["page"] == old_event["page"] and s["start_char"] <= point < s["end_char"]]
                    if len(spans) != 1 or spans[0]["span_id"] not in by_span:
                        raise self.a.AuthoringError(f"E_V2_AUTHOR_ASSET_TARGET: {asset['asset_id']}")
                    target = by_span[spans[0]["span_id"]]
                    asset.update(anchor=target["anchor"], placement={"before_event": target["event_id"]})
                else:
                    raise self.a.AuthoringError(f"E_V2_AUTHOR_ASSET_UNRESOLVED: {asset['asset_id']}")
                raw_order = resolution.get("source_order")
                reviewed_order = reviewed.get(asset["asset_id"], {}).get("source_order")
                asset["source_order"] = reviewed_order or ({"kind": "selected_view_raw_index", "view": resolution.get("selected_view", "original_hybrid"), "raw_index": raw_order[1], "gap_ordinal": resolution.get("gap_ordinal", 0)} if raw_order else {"kind": "physical_unit_page_slot", "unit_id": "cover", "page_slot": 0})
            provenance = asset["provenance"]
            if provenance["kind"] == "markdown_image_reference":
                line = next(l for l in self.lines if l["span"]["span_id"] == provenance["span_id"])
                self.event("asset:" + asset["asset_id"], "asset", [line], asset["anchor"], asset["asset_id"])
            else:
                target = event_by_id[next(iter(asset["placement"].values()))]
                event_page = target["page"] if asset["asset_id"] in reviewed else page
                point = target["order_key"][1] if target["page"] == event_page else len(self.raw[event_page]) if target["page"] > event_page else 0
                relation = next(iter(asset["placement"]))
                if relation == "before_event":
                    point = max(0, point - 1)
                self.events.append({"event_id": "asset:" + asset["asset_id"], "type": "asset", "page": event_page, "order_key": [event_page, point, 4, 0], "anchor": asset["anchor"], "content": asset["asset_id"], "fragment_id": "asset:" + asset["asset_id"], "source_span_ids": [], "source_operation": "asset_reference", "payload_bindings": []})

    def finish(self):
        generated = [e for e in self.base["events"] if e["type"] == "generated_navigation"]
        for event in generated:
            heading = next(e for e in self.events if e["type"] == "heading" and e["anchor"] == event["anchor"])
            event.update(page=heading["page"], order_key=[heading["page"], heading["order_key"][1], 5, 0], generated_placement={"after_event": heading["event_id"]})
        self.events.extend(generated)
        assets = {a["asset_id"]: a for a in self.assets}
        def order_key(event):
            extra = assets[event["content"]]["source_order"] if event["type"] == "asset" else {}
            return (*event["order_key"][:3], extra.get("raw_index", extra.get("page_slot", 0)), event["event_id"])
        self.events.sort(key=order_key)
        for ordinal, event in enumerate(self.events):
            event["order_key"][3] = ordinal
        positions = {(e["content"]["anchor"] if e["type"] == "structured_unit" else e["anchor"]): i for i, e in enumerate(self.events) if e["type"] in {"heading", "anchor_only"} or e["type"] == "structured_unit" and e["content"]["kind"] == "inline_run_in"}
        self.hierarchy.sort(key=lambda h: positions[h["anchor"]])
        self.base.update(hierarchy=self.hierarchy, events=self.events, assets=self.assets, source_partition={"pages": [{**p, "span_ids": [s["span_id"] for s in self.spans if s["page"] == p["page"]]} for p in self.base["source_partition"]["pages"]], "spans": self.spans})
        migration = self.a.asset_b1c4_migration()
        self.base["migration"].update(asset_rows=migration["frozen_rows"], new_reviewed_targets=migration["new_reviewed_targets"] + [{"target_id": "hierarchy:" + h["anchor"], "decision_ref": "OUT-003"} for h in self.hierarchy if h["anchor"] not in {r["anchor"] for r in self.v1["hierarchy"]}])
        for row in self.base["migration"]["source_disposition_rows"]:
            if row["source_id"] in {"source_disposition:123", "source_disposition:124"}:
                row.update(outcome="excluded_advertising", final_target_ids=[], decision_ref="OUT-026")
        review = []
        for event in self.events:
            kind = "heading_outline" if event["type"] == "heading" else event["content"]["kind"] if event["type"] == "structured_unit" else None
            if kind:
                review.append({"review_id": f"review:{kind}:{event['event_id']}", "kind": kind, "source_pages": sorted({s["page"] for s in self.spans if s["span_id"] in event["source_span_ids"]}), "event_ids": [event["event_id"]], "asset_ids": [], "priority": kind == "heading_outline", "contact_sheet_group": "outline" if kind == "heading_outline" else "structured"})
        required = {x["source_event_id"] for x in self.base["xrefs"]} | {r["target_event_id"] for r in self.base["source_recoveries"]}
        for event in self.events:
            if event["event_id"] in required:
                review.append({"review_id": "review:xref_recovery:" + event["event_id"], "kind": "xref_recovery", "source_pages": sorted({s["page"] for s in self.spans if s["span_id"] in event["source_span_ids"]}), "event_ids": [event["event_id"]], "asset_ids": [], "priority": True, "contact_sheet_group": "xref_recovery"})
        for asset in self.assets:
            if asset["disposition"] == "reader":
                review.append({"review_id": "review:asset_placement:" + asset["asset_id"], "kind": "asset_placement", "source_pages": [asset["source_page"]], "event_ids": [], "asset_ids": [asset["asset_id"]], "priority": False, "contact_sheet_group": "reader_assets"})
        self.base["visual_review_units"] = review
        return self.base


def project(author):
    projection = Projection(author)
    projection.headings()
    return projection


def materialize(author):
    projection = project(author)
    projection.containers()
    projection.creatures()
    projection.physical_units()
    projection.remaining_text()
    projection.cross_references()
    projection.art()
    return projection.finish()
