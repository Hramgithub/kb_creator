"""Reviewed relocations preserve rich blocks and reject source/HTML/Word drift."""
import copy
import hashlib
import json
import zipfile
from pathlib import Path

import tempfile
import unittest
from lxml import etree, html
from PIL import Image

from kb_creator.pipeline import reader_block_relocation as relocation
from kb_creator.pipeline import reader_projection as reader
from kb_creator.pipeline import five_step_docx
from kb_creator.scripts.production_docx import build_docx, bookmark_name


def fixture(root, kind="label"):
    root.mkdir(exist_ok=True)
    (root / "assets").mkdir(exist_ok=True)
    Image.new("RGB", (24, 16), "red").save(root / "assets/map.png")
    if kind == "news":
        heading = "## BREAKING **STORY**"
        groups = [[("h0", heading, '<h2>BREAKING <strong>STORY</strong></h2>'),
                   ("p0", "First **panel**.", '<p>First <strong>panel</strong>.</p>'),
                   ("h1", heading, '<h2>BREAKING <strong>STORY</strong></h2>'),
                   ("p1", "Second panel.", '<p>Second panel.</p>'),
                   ("h2", heading, '<h2>BREAKING <strong>STORY</strong></h2>'),
                   ("caption", "Investigator handout1", '<p>Investigator handout1</p>'),
                   ("p2", "Third panel.", '<p>Third panel.</p>')],
                  [("other", heading, '<h2>BREAKING <strong>STORY</strong></h2>')]]
        moving, destination, position = ["caption"], "h0", "before"
    elif kind == "figure":
        groups = [[("stats", "London **attributes**", '<p>London <strong>attributes</strong></p>'),
                   ("image", "![Map](assets/map.png)", '<figure><img src="assets/map.png" alt="Map"><figcaption>Map</figcaption></figure>')],
                  [("skills", "Skills retained.", '<p>Skills retained.</p>'),
                   ("blood1", "Blood contact is lethal.", '<p>Blood contact is lethal.</p>'),
                   ("blood2", "Blood contact is lethal.", '<p>Blood contact is lethal.</p>'),
                   ("jess", "## Jess", '<h2>Jess</h2>')]]
        moving, destination, position = ["image"], "jess", "before"
    elif kind == "captions":
        groups = [[("legend", "- First room\n- Second room", '<ul><li>First room</li>\n<li>Second room</li></ul>'),
                   ("image", "![Map](assets/map.png)", '<figure><img src="assets/map.png" alt="Map"><figcaption>Map</figcaption></figure>'),
                   ("caption1", "**Ravenscar**", '<p><strong>Ravenscar</strong></p>'),
                   ("caption2", "Ravenscar map", '<p>Ravenscar map</p>')]]
        moving, destination, position = ["caption1", "caption2"], "legend", "before"
    else:
        groups = [[("label", "Handout4", '<p>Handout4</p>'),
                   ("chang", "Chang **narrative**.", '<p>Chang <strong>narrative</strong>.</p>'),
                   ("memo", "## Memo", '<h2>Memo</h2>'),
                   ("end", "Memo reference", '<p>Memo reference</p>'),
                   ("later", "Unrelated narrative.", '<p>Unrelated narrative.</p>'),
                   ("motto1", "LAPD", '<p>LAPD</p>'),
                   ("motto2", "Protect and serve", '<p>Protect and serve</p>')]]
        moving, destination, position = (["motto1", "motto2"], "end", "after") if kind == "motto" else (["label"], "memo", "before")
    units, sections = [], []
    for page, group in enumerate(groups, 1):
        section = html.Element("section", {"data-page": f"{page:03d}", "id": f"page-{page:03d}"})
        for uid, text, fragment in [(f"page{page}", f"<!-- source-page-{page:03d} -->", None), *group]:
            units.append(dict(unit_id=uid, ru_text=text, ru_sha256=hashlib.sha256(text.encode()).hexdigest().upper(), parent_unit_id=None))
            if fragment is not None:
                node = html.fragment_fromstring(fragment)
                node.set("id", uid)
                section.append(node)
        sections.append(section)
    body = "".join(html.tostring(node, encoding="unicode") for node in sections)
    tree = html.fragment_fromstring(body, create_parent="main")
    blocks = relocation._blocks(tree)
    unit_map = {row["unit_id"]: row for row in units}
    bind = lambda uid: {key: unit_map[uid][key] for key in ("unit_id", "ru_sha256")}
    node = lambda uid: tree.xpath('.//*[@id=$uid]', uid=uid)[0]
    ns, target = [node(uid) for uid in moving], node(destination)
    a, b, d = blocks.index(ns[0]), blocks.index(ns[-1]), blocks.index(target)
    crossed = blocks[b+1:d] if b < d else blocks[d+1:a]
    order = [row["unit_id"] for row in units]
    mi = [order.index(uid) for uid in moving]; di = order.index(destination)
    start, end = (mi[-1] + 1, di) if mi[-1] < di else (di + 1, mi[0])
    role = dict(role=relocation.ROLE, units=[bind(uid) for uid in moving],
                destination=dict(unit=bind(destination), position=position),
                crossed_units=[bind(uid) for uid in order[start:end]],
                rendered_preimage=dict(units=[relocation.fingerprint(n) for n in ns],
                                      destination=relocation.fingerprint(target),
                                      crossed=[relocation.fingerprint(n) for n in crossed]),
                source_evidence="Independent fixture review", reason="Exact reviewed semantic association")
    if kind == "captions":
        role["keep_with_next"] = True
    if kind == "news":
        role["keep_with_next"] = True
        role["heading_occurrence"] = dict(ordinal=0, cohort=[bind(f"h{i}") for i in range(3)])
    options = dict(schema=reader.SCHEMA, source_toc=dict(state="absent", source_pdf_sha256="A"*64, reason="fixture"),
                   body_links=[], asset_choices=[], hit_points=dict(presentation="numeric"), display_roles=[role])
    projection = dict(units=units, unit_order=order, spans=[])
    return body, projection, options


def project(root, kind="label", mutate=None):
    body, projection, options = fixture(root, kind)
    if mutate:
        body = mutate(body, projection, options) or body
    result, _, report = reader.project_reader_html(body, [], projection, options, master_root=root)
    return result, report, projection, options


def render(root, kind):
    result, report, projection, options = project(root, kind)
    source = root / "internal.html"
    source.write_text('<html><body><main>'+result+'</main></body></html>', encoding="utf-8")
    docx = root / "document.docx"
    build_docx(source, docx)
    relocation.verify_docx(report, docx)
    return result, report, docx


def check_reviewed_whole_block_order_survives_actual_word(tmp_path, kind):
    result, report, docx = render(tmp_path, kind)
    assert len(report["block_relocations"]) == 1
    assert "<strong>" in result
    if kind == "figure":
        assert result.count("Blood contact is lethal.") == 2
        tree = html.fragment_fromstring(result, create_parent="main")
        assert tree.xpath('.//*[@id="image"]')[0].getparent().get("data-page") == "002"
    if kind == "captions":
        tree = html.fragment_fromstring(result, create_parent="main")
        assert all(tree.xpath('.//*[@id=$uid]', uid=uid)[0].get("data-keep-with-next") == "true"
                   for uid in ("caption1", "caption2"))


def check_relocation_fails_closed_before_any_move(tmp_path, mutation):
    body, projection, options = fixture(tmp_path)
    role = options["display_roles"][0]
    if mutation == "source_hash":
        role["units"][0]["ru_sha256"] = "A"*64
    elif mutation == "source_bytes":
        projection["units"][1]["ru_text"] = "Changed source"
    elif mutation == "crossed_interval":
        role["crossed_units"].clear()
    elif mutation == "target_hash":
        role["destination"]["unit"]["ru_sha256"] = "A"*64
    elif mutation == "destination":
        role["rendered_preimage"]["destination"] = "A"*64
    elif mutation == "moved_html":
        body = body.replace("Handout4", "Handout5")
    elif mutation == "crossed_html":
        body = body.replace("narrative</strong>", "altered</strong>")
    elif mutation == "nested":
        body = body.replace('<p id="label">Handout4</p>', '<blockquote><p id="label">Handout4</p></blockquote>')
    elif mutation == "partial":
        projection["units"][1]["parent_unit_id"] = "parent"
    elif mutation == "overlap":
        options["display_roles"].append(copy.deepcopy(role))
    elif mutation == "extra":
        role["unchecked"] = True
    elif mutation == "cohort":
        projection["units"].insert(2, {**projection["units"][1], "unit_id": "duplicate"})
    with unittest.TestCase().assertRaises(ValueError):
        reader.project_reader_html(body, [], projection, options, master_root=tmp_path)


def rewrite_docx(path, change):
    with zipfile.ZipFile(path) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    change(members)
    with zipfile.ZipFile(path, "w") as archive:
        for name, value in members.items():
            archive.writestr(name, value)


def check_actual_word_drift_is_rejected(tmp_path, mutation):
    _, report, document = render(tmp_path, "figure")
    word = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    def change(members):
        tree = etree.fromstring(members["word/document.xml"])
        if mutation == "text":
            next(node for node in tree.iter(f"{{{word}}}t") if node.text == "Skills retained.").text = "Changed skills."
        elif mutation in {"bookmark", "bookmark_end"}:
            mark = next(node for node in tree.iter(f"{{{word}}}bookmarkStart")
                        if node.get(f"{{{word}}}name") == bookmark_name("image"))
            if mutation == "bookmark_end":
                mark = next(node for node in tree.iter(f"{{{word}}}bookmarkEnd")
                            if node.get(f"{{{word}}}id") == mark.get(f"{{{word}}}id"))
            mark.getparent().remove(mark)
        elif mutation == "media":
            name = next(name for name in members if name.startswith("word/media/"))
            members[name] = b"changed image bytes"
        elif mutation == "image_order":
            mark = next(node for node in tree.iter(f"{{{word}}}bookmarkStart")
                        if node.get(f"{{{word}}}name") == bookmark_name("image"))
            p = next(node for node in mark.iterancestors() if node.tag == f"{{{word}}}p")
            target = next(node for node in tree.iter(f"{{{word}}}p")
                          if any(text.text == "Skills retained." for text in node.iter(f"{{{word}}}t")))
            p.getparent().remove(p); target.addprevious(p)
        members["word/document.xml"] = etree.tostring(tree)
    rewrite_docx(document, change)
    with unittest.TestCase().assertRaises(five_step_docx.FiveStepDocxError):
        relocation.verify_docx(report, document)


def check_crossed_evidence_is_not_an_omission_owner():
    from kb_creator.pipeline.reader_duplicate_text import _refs
    row = {"role": relocation.ROLE, "units": [{"unit_id": "moved", "ru_sha256": "A"*64}],
           "destination": {"unit": {"unit_id": "target", "ru_sha256": "A"*64}},
           "crossed_units": [{"unit_id": "furniture", "ru_sha256": "A"*64}]}
    assert set(_refs(row)) == {"moved", "target"}


def check_helper_is_bound_by_build_implementation_inventory():
    from kb_creator.pipeline import five_step, five_step_successor
    assert "pipeline/reader_block_relocation.py" in five_step.DEPENDENCIES[5]
    snapshot = five_step_successor._code_snapshot()
    assert any(row["path"].endswith("reader_block_relocation.py") for row in snapshot["files"])


def check_checkpoint_builder_enforces_actual_guard(root, reject=False):
    from kb_creator.scripts import build_bilingual_checkpoint
    from translator.translator import markdown_to_review_html
    from unittest.mock import patch
    root.mkdir()
    pages = root / "pages"; pages.mkdir()
    ru = "Handout4\n\nChang **narrative**.\n\n## Memo\n\nMemo reference"
    (pages / "page-001.json").write_text(json.dumps(dict(source_page=1,en_markdown="Fixture",ru_markdown=ru)),encoding="utf-8")
    source = root / "source.pdf"; source.write_bytes(b"%PDF-1.4 fixture")
    prepared = root / "prepared"
    build_bilingual_checkpoint.prepare(pages, root, source, prepared)
    options = json.loads((prepared / "reader_options.template.json").read_text(encoding="utf-8"))
    options["source_toc"]["state"] = "absent"
    options["source_toc"]["reason"] = "Reviewed fixture"
    options["hit_points"] = {"presentation": "numeric", "expected_counts": []}
    projection = json.loads((prepared / "PRELIMINARY_RU_PROJECTION.json").read_text(encoding="utf-8"))
    bind = lambda index: {key: projection["units"][index][key] for key in ("unit_id", "ru_sha256")}
    body, _, _ = markdown_to_review_html((prepared / "PRELIMINARY_RU.md").read_text(encoding="utf-8"),source_path=prepared / "PRELIMINARY_RU.md",html_path=prepared / "internal.html",blockquote_heading_offset=0)
    blocks = [node for node in relocation._blocks(html.fragment_fromstring(body,create_parent="main")) if node.tag != "div"]
    options["display_roles"] = [dict(role=relocation.ROLE, units=[bind(1)],
        destination=dict(unit=bind(3),position="before"),crossed_units=[bind(2)],
        rendered_preimage=dict(units=[relocation.fingerprint(blocks[0])],destination=relocation.fingerprint(blocks[2]),crossed=[relocation.fingerprint(blocks[1])]),
        source_evidence="Fixture reviewed source",reason="Associate exact label with memo")]
    options.pop("options_sha256"); options["options_sha256"] = reader.seal(options)
    option_path = root / "options.json"; option_path.write_text(json.dumps(options),encoding="utf-8")
    config = root / "config.json"; config.write_text(json.dumps(five_step_docx._default_config("Fixture")),encoding="utf-8")
    call = dict(side_effect=five_step_docx.FiveStepDocxError("guard fixture rejection")) if reject else dict(wraps=relocation.verify_docx)
    with patch.object(build_bilingual_checkpoint,"verify_relocated_docx",**call) as guard:
        if reject:
            with unittest.TestCase().assertRaisesRegex(five_step_docx.FiveStepDocxError,"guard fixture rejection"):
                build_bilingual_checkpoint.build(pages,root,config,root / "output",prepared=prepared,reader_options=option_path,source_pdf=source)
        else:
            result = build_bilingual_checkpoint.build(pages,root,config,root / "output",prepared=prepared,reader_options=option_path,source_pdf=source)
            assert result["text_closure"]["missing_blocks"] == []
        assert guard.call_count == 1


def retarget_news(body, projection, role, ordinal):
    tree = html.fragment_fromstring(body, create_parent="main")
    blocks = relocation._blocks(tree)
    binding = role["heading_occurrence"]["cohort"][ordinal]
    target = tree.xpath('.//*[@id=$uid]', uid=binding["unit_id"])[0]
    moving = tree.xpath('.//*[@id="caption"]')[0]
    role["destination"]["unit"] = copy.deepcopy(binding)
    role["heading_occurrence"]["ordinal"] = ordinal
    order = projection["unit_order"]
    role["crossed_units"] = [{key: row[key] for key in ("unit_id", "ru_sha256")}
                             for row in projection["units"][order.index(binding["unit_id"])+1:order.index("caption")]]
    role["rendered_preimage"]["destination"] = relocation.fingerprint(target)
    role["rendered_preimage"]["crossed"] = [relocation.fingerprint(n)
                                            for n in blocks[blocks.index(target)+1:blocks.index(moving)]]


class HeadingDestinationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_each_exact_destination_and_stable_replay(self):
        for ordinal in range(3):
            with self.subTest(ordinal=ordinal):
                body, projection, options = fixture(self.root / str(ordinal), "news")
                retarget_news(body, projection, options["display_roles"][0], ordinal)
                outputs = [reader.project_reader_html(body, [], projection, options, master_root=self.root / str(ordinal))
                           for _ in range(2)]
                self.assertEqual(outputs[0], outputs[1])
                rendered, _, report = outputs[0]
                tree = html.fragment_fromstring(rendered, create_parent="main")
                section = tree.xpath('.//section[@data-page="001"]')[0]
                self.assertEqual([n.get("id") for n in section if n.tag == "h2"], ["h0", "h1", "h2"])
                self.assertEqual([n.text_content() for n in section if n.tag == "p" and n.get("id") != "caption"],
                                 ["First panel.", "Second panel.", "Third panel."])
                caption = tree.xpath('.//*[@id="caption"]')[0]
                self.assertEqual(caption.getnext().get("id"), f"h{ordinal}")
                self.assertEqual(len(tree.xpath('.//h2/strong')), 4)
                self.assertEqual(tree.xpath('.//*[@id="other"]')[0].getparent().get("data-page"), "002")
                self.assertEqual(report["block_relocations"][0]["decision"], options["display_roles"][0])

    def test_bad_source_witnesses_and_ownership(self):
        cases = ("absent", "cached_absent", "unique", "prose", "moving", "destination_id",
                 "negative", "range", "bool", "fields", "missing", "extra", "order", "duplicate",
                 "page", "hash", "bytes", "stale_cohort_hash", "parent", "parts", "child", "span",
                 "demotion", "omission", "dependent", "dependent_reverse", "callback")
        for case in cases:
            with self.subTest(case=case):
                body, projection, options = fixture(self.root / case, "news")
                role = options["display_roles"][0]; witness = role["heading_occurrence"]
                units = {row["unit_id"]: row for row in projection["units"]}
                if case in {"absent", "cached_absent"}:
                    role.pop("heading_occurrence")
                    if case == "cached_absent":
                        options["display_roles"].append(dict(role="prose_presentation", unit=witness["cohort"][1],
                            heading_occurrence={**witness, "ordinal": 1}, reason="fixture", source_evidence="fixture"))
                if case in {"unique", "prose"}:
                    role["destination"]["unit"] = {key: units["p0"][key] for key in ("unit_id", "ru_sha256")}
                    if case == "unique":
                        units["p0"]["ru_text"] = "## Unique"
                        units["p0"]["ru_sha256"] = hashlib.sha256(b"## Unique").hexdigest().upper()
                        role["destination"]["unit"]["ru_sha256"] = units["p0"]["ru_sha256"]
                        witness["cohort"] = [role["destination"]["unit"]]
                if case == "moving":
                    role["units"] = [copy.deepcopy(witness["cohort"][2])]
                if case == "destination_id": role["destination"]["unit"] = copy.deepcopy(witness["cohort"][1])
                if case == "negative": witness["ordinal"] = -1
                if case == "range": witness["ordinal"] = 3
                if case == "bool": witness["ordinal"] = False
                if case == "fields": witness["guess"] = True
                if case == "missing": witness["cohort"].pop()
                if case == "extra": witness["cohort"].append({key: units["other"][key] for key in ("unit_id", "ru_sha256")})
                if case == "order": witness["cohort"].reverse()
                if case == "duplicate": witness["cohort"][2] = copy.deepcopy(witness["cohort"][1])
                if case == "page": witness["cohort"][2] = {key: units["other"][key] for key in ("unit_id", "ru_sha256")}
                if case == "hash": witness["cohort"][1]["ru_sha256"] = "A"*64
                if case == "bytes": units["h1"]["ru_text"] += " changed"
                if case == "stale_cohort_hash":
                    units["h1"]["ru_sha256"] = "A"*64; witness["cohort"][1]["ru_sha256"] = "A"*64
                if case == "parent": units["h1"]["parent_unit_id"] = "parent"
                if case == "parts": units["h1"]["part_index"] = 0
                if case == "child": projection["units"].append({**units["p1"], "unit_id":"child", "parent_unit_id":"h1"})
                if case == "span": projection["spans"] = [{"unit_ids":["h1"]}]
                if case in {"demotion", "omission"}:
                    other = dict(role="prose_presentation", unit=witness["cohort"][1],
                                 heading_occurrence={**copy.deepcopy(witness), "ordinal":1},
                                 source_evidence="fixture", reason="fixture")
                    if case == "omission": other.update(role="repeated_title", standalone_running_heading=True,
                        retained={key:units["other"][key] for key in ("unit_id", "ru_sha256")})
                    options["display_roles"].insert(0, other)
                if case.startswith("dependent"):
                    other = copy.deepcopy(role)
                    retarget_news(body, projection, other, 2)
                    options["display_roles"].append(other)
                    if case.endswith("reverse"): options["display_roles"].reverse()
                if case == "callback":
                    tree = html.fragment_fromstring(body, create_parent="main")
                    with self.assertRaisesRegex(ValueError, "callback"):
                        relocation.apply(tree, projection, options, {uid:1 for uid in units},
                                         lambda binding:units[binding["unit_id"]], lambda binding:None, lambda binding:None)
                    continue
                with self.assertRaises(ValueError):
                    reader.project_reader_html(body, [], projection, options, master_root=self.root / case)

    def test_bad_dom_and_failed_preflight_never_moves_blocks(self):
        from unittest.mock import patch
        for case in ("missing", "extra", "level", "markup", "text", "nested", "tail", "replaced", "moved"):
            with self.subTest(case=case):
                body, projection, options = fixture(self.root / case, "news")
                tree = html.fragment_fromstring(body, create_parent="main")
                n = tree.xpath('.//*[@id="h1"]')[0]
                if case == "missing": n.getparent().remove(n)
                if case == "extra": n.getparent().append(copy.deepcopy(n))
                if case == "level": n.tag = "h3"
                if case == "markup": n[0].tag = "em"
                if case == "text": n.text = "ALTERED "
                if case == "nested":
                    wrapper = html.Element("blockquote"); n.addprevious(wrapper); wrapper.append(n)
                if case == "tail": n.tail = "unowned text"
                changed = "".join(html.tostring(node, encoding="unicode") for node in tree)
                original = relocation.apply
                def preflight(current, *args, **kwargs):
                    member = current.xpath('.//*[@id="h1"]')[0]
                    if case == "replaced":
                        member.getparent().replace(member, copy.deepcopy(member))
                    if case == "moved": member.getparent().append(member)
                    snapshot = etree.tostring(current)
                    try:
                        return original(current, *args, **kwargs)
                    except ValueError:
                        self.assertEqual(etree.tostring(current), snapshot)
                        raise
                with patch.object(relocation, "apply", preflight), self.assertRaises(ValueError):
                    reader.project_reader_html(changed, [], projection, options, master_root=self.root / case)

    def test_exact_actual_word_destination_and_negative_guards(self):
        ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        for mutation in ("bookmark_sibling", "caption_sibling", "paired", "alter", "delete", "keep"):
            with self.subTest(mutation=mutation):
                _, report, document = render(self.root / mutation, "news")
                def change(members):
                    tree = etree.fromstring(members["word/document.xml"])
                    ps = list(tree.iter(f"{{{ns}}}p"))
                    heading = next(p for p in ps if any(m.get(f"{{{ns}}}name") == bookmark_name("h0")
                                                      for m in p.iter(f"{{{ns}}}bookmarkStart")))
                    sibling = next(p for p in ps if any(m.get(f"{{{ns}}}name") == bookmark_name("h1")
                                                      for m in p.iter(f"{{{ns}}}bookmarkStart")))
                    caption = next(p for p in ps if any(t.text == "Investigator handout1" for t in p.iter(f"{{{ns}}}t")))
                    start = next(m for m in heading.iter(f"{{{ns}}}bookmarkStart")
                                 if m.get(f"{{{ns}}}name") == bookmark_name("h0"))
                    end = next(m for m in heading.iter(f"{{{ns}}}bookmarkEnd") if m.get(f"{{{ns}}}id") == start.get(f"{{{ns}}}id"))
                    if mutation == "bookmark_sibling":
                        for mark in (start,end):mark.getparent().remove(mark)
                        sibling.insert(0,start); sibling.append(end)
                    if mutation == "caption_sibling":
                        caption.getparent().remove(caption);sibling.addprevious(caption)
                    if mutation == "paired":end.getparent().remove(end)
                    if mutation == "alter": next(heading.iter(f"{{{ns}}}t")).text = "Changed banner"
                    if mutation == "delete":heading.getparent().remove(heading)
                    if mutation == "keep":
                        keep=next(caption.iter(f"{{{ns}}}keepNext"));keep.getparent().remove(keep)
                    members["word/document.xml"] = etree.tostring(tree)
                rewrite_docx(document, change)
                with self.assertRaises(five_step_docx.FiveStepDocxError):relocation.verify_docx(report, document)


class BlockRelocationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_positive_actual_word(self):
        for kind in ("label", "motto", "figure", "captions"):
            with self.subTest(kind=kind):
                check_reviewed_whole_block_order_survives_actual_word(self.root / kind, kind)

    def test_reject_source_html_contract_drift(self):
        for mutation in ("source_hash", "source_bytes", "crossed_interval", "target_hash", "destination",
                         "moved_html", "crossed_html", "nested", "partial", "overlap", "extra", "cohort"):
            with self.subTest(mutation=mutation):
                check_relocation_fails_closed_before_any_move(self.root / mutation, mutation)

    def test_reject_actual_word_drift(self):
        for mutation in ("text", "bookmark", "bookmark_end", "media", "image_order"):
            with self.subTest(mutation=mutation):
                check_actual_word_drift_is_rejected(self.root / mutation, mutation)

    def test_caption_word_keep_next_is_guarded(self):
        _, report, document = render(self.root / "captions", "captions")
        ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        def change(members):
            tree = etree.fromstring(members["word/document.xml"])
            keep = next(tree.iter(f"{{{ns}}}keepNext"))
            keep.getparent().remove(keep)
            members["word/document.xml"] = etree.tostring(tree)
        rewrite_docx(document,change)
        with self.assertRaisesRegex(five_step_docx.FiveStepDocxError,"keep-with-next"):
            relocation.verify_docx(report,document)

    def test_crossed_evidence_ownership(self):
        check_crossed_evidence_is_not_an_omission_owner()

    def test_implementation_inventory(self):
        check_helper_is_bound_by_build_implementation_inventory()

    def test_checkpoint_guard_wired(self):
        for reject in (False, True):
            with self.subTest(reject=reject):
                check_checkpoint_builder_enforces_actual_guard(self.root / str(reject),reject)
