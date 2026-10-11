from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any

from PIL import Image


KB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = KB_ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from translator import translator
import freeze_innsmouth_master_ru_repo_input as freeze_ru


DEFAULT_MASTER_RU_ROOT = KB_ROOT / "inputs" / "innsmouth" / "master_ru" / "accepted_20260830_r2"
DEFAULT_MASTER_EN_ROOT = KB_ROOT / "inputs" / "innsmouth" / "master_en" / "accepted_20260830_r2"
DEFAULT_TERMINOLOGY_REGISTRY = (
    REPO_ROOT
    / "CoC"
    / "Project_Reference"
    / "Terminology"
    / "CoC_Terminology_Decisions.csv"
)
DEFAULT_OUTPUT_ROOT = KB_ROOT / "working" / "innsmouth_direct_html" / "accepted_20260830_candidate_r7f"
OUTPUT_HTML_NAME = "The_Innsmouth_Terror_RU.html"

LETTER_SEAL_ASSET = (
    "334f14bd517569e118d9445575f8c2bed6a356c7504142c3ac75a6f472e954f5.jpg"
)
CREDITS_ART_ASSET = (
    "ed88e677e363073b2973212c4f3e44c3bd91c2a91aff7f7ca0e3a8da41c4e224.jpg"
)
SOURCE_COVER_ASSET = freeze_ru.SOURCE_COVER_ASSET
FULL_WIDTH_ASSETS = frozenset(
    {
        SOURCE_COVER_ASSET,
        "c68b102eb549eaa684f8fb5a3637bc8acd12f8f123cdf8aa4b79bb5b19de103c.jpg",
        "6beb2e37b45a8f10d343b3f191ab143a3fa115b8234399d6e87a0eea8757f2d5.jpg",
        "ec8e821fae101fc7196af0b1afb9d74f00377479b0ba7d1a1dc4b8e8f57516b7.jpg",
        "20cc7e0f3485214dd933ad3996f0ea5a6866b23db12cd22ffa113bfe9314b125.jpg",
        "2a77226d3427fb03aa422fdfa6f5876f584609b3876e26ac83487a67f6759e33.jpg",
        "a824d214f9bbc53324ee4903be7b21d1d86252d2d2d6700ea6807ac1a572b8ed.jpg",
        "3371d3857129bfbbc48063eaed6e62df90ee0b93f54c98e776c49f57b045c38f.jpg",
        "9c85f20d6de3aceaeb294aaf3b6af38ba32d23ee36466d875d292db0f373cf0a.jpg",
        "86daf1c4fa06068c8d767a83fc2951ca012be3189880157167903da715219893.jpg",
        "2f0e82f6dd6f5a9a0ad377a9ad3f34075fda71abbea8f34b8a7401b66eab7f35.jpg",
    }
)

# Reader art is emitted after the source paragraph that originally preceded it.
# Floating that block in place makes it wrap the next section instead of its
# semantic owner.  These exact bindings relocate only inline reader art; the
# accepted Markdown and every full-width placement remain unchanged.
INLINE_ART_PLACEMENTS = (
    ("82307baffee51be33d6bf8b95723fbf46d0e34e1a22fd13adc8cb598c8f82172.jpg", "privlechenie-syschikov", None, False),
    ("81240de97cfb63a63694e28b512857f6b072aa8ed012610a5884923d8d0baffa.jpg", "genevieve-ginny-dubois-25-let-starletka", "Genevieve &#x27;Ginny&#x27; Dubois", False),
    ("89042f940a05158789c1f01803732eea3a0a1d6b8dd02bd8284872c23d84147e.jpg", "p-a-bazzledon-40-let-rezhisser-i-moshennik", "P.A. Bazzledon", False),
    ("5deabcfccfe44c4186745c57d25dc5e989dbadc549266836391b49ed3179f285.jpg", "anna-d-az-26-let-prodyuser", "Anna Díaz", False),
    ("f03a1d401aabe96c7433f2775daa155f8e0bdfa17a2bf233ee902fe070c88f91.jpg", "christopher-mcguire-37-let-inzhener", "Christopher McGuire", False),
    ("b2b7cdbff504429a3705ad93671f6a1a2267237071ad085ad02723e658be80b4.jpg", "sammy-brewster-21-god-diletant-i-brat", "Sammy Brewster", False),
    ("d29dd78603767844a3d3811902958043a3a67dfd0fa809603b1926066c706531.jpg", "biblioteka-orna-miskatonikskii-universitet", "Diane Loring", False),
    ("5534eb2d722a751816b5c0181ca3fdf4fff79073e34dc5ccac9bfeb646faeb7c.jpg", "biblioteka-orna-miskatonikskii-universitet", "Dr. Henry Armitage", False),
    ("497dc1045aa4f06805e86552e2de0207bf15bfbc65856c747e7a88d375212a67.jpg", "arkhem-advertaizer", "Karen Jeffries", True),
    ("d58d77c8f9d78a6f7a243191794a958376eb72a3685fb1e86c7814690cecf6f8.jpg", "miskatonikskii-teatr", "Ryan Turner", False),
    ("74aa40aa2039e4cf4eab3fa6ff9618cdfd16778994bf6bf03c6b4ed5aa0550d6.jpg", "semochnyi-vagon", None, False),
    ("9ded43678da7bb047cacb1b2ffe80cda584e20341949989a19348595670daa5f.jpg", "kabinet-bazzledon", None, False),
    ("page19_film_reel.png", "laboratoriya-mcguire", None, False),
    ("d2556e32e67e388fe5878fcd43a1d50ba5ed1df9e099f3533f4b4b3ec4390d02.jpg", "v-innsmut", "Pete", False),
    ("f23271b212f11039d58ab81421a36b5f12a0b2f72d8cdb020562cad6fcf872a6.jpg", "pozharnaya-stantsiya", "Zadok Allen", False),
    ("3ce72daa90f87b979a5bca105e7cd898e130574d0e230e2ba87a5c9a65472782.jpg", "pozharnaya-stantsiya", "Jeremiah Brewster", False),
    ("4c93bb273638108e23cb17b05c30d7026cae7e27769e66ffb7026ae6e87c9bd7.jpg", "hugo-shrimpy-hargreaves", None, False),
    ("6303e327b95dd1d5484282e977bb4ba379617e0cbc47505906af6e54c2697e1d.jpg", "patty-gillian", None, False),
    ("8270a8298d11dc6be7a1086e0d891c57982032180c0eeb0ab67e58509d784269.jpg", "ian-torres", None, False),
    ("c4124729ab42077a516b69c66ecb3ae88171353f5deaedc865b8f332a32afa91.jpg", "tiffany-quispe", None, False),
    ("203c6dcff8d86c53d99721ad4448caeba0ecb0ecaf129ddefcd3b6811c54c32f.jpg", "margaret-maggie-myers", None, False),
)

INNSMOUTH_PRESENTATION_CSS = r"""
<style id="innsmouth-presentation-r7">
.title-page { position: relative; isolation: isolate; clear: both; width: 100%; aspect-ratio: 210 / 297; margin: 0 0 2rem; overflow: hidden; background: #161321; color: #fff; }
.title-page figure.art-title-cover { position: absolute; z-index: 0; inset: 0; width: 100%; height: 100%; margin: 0; overflow: hidden; }
.title-page figure.art-title-cover img { width: 100%; height: 100%; max-width: none; max-height: none !important; object-fit: cover; }
.title-page figure.art-title-cover::before { content: ""; position: absolute; z-index: 1; inset: 0 0 auto; height: 38%; background: #161321; }
.title-page figure.art-title-cover::after { content: ""; position: absolute; z-index: 1; inset: auto 0 0; height: 14%; background: linear-gradient(to bottom, rgba(22, 19, 33, .72), #161321 35%); }
.title-page .title-overlay { position: absolute; z-index: 3; top: 7%; left: 6%; right: 6%; margin: 0; padding: .7em .5em; color: #f8f3e9; background: rgba(22, 19, 33, .78); border: 2px solid rgba(248, 243, 233, .62); text-align: center; font-size: clamp(2rem, 6.5vw, 5rem); line-height: .95; letter-spacing: .035em; text-shadow: 0 3px 5px #09070d; }
.source-toc-section { clear: both; margin: 1.5rem 0 2rem; }
.source-toc-columns { columns: 2; column-gap: 3rem; column-fill: balance; }
.source-toc-group { display: inline-block; width: 100%; break-inside: avoid; margin: 0 0 .8rem; }
.source-toc-group h2 { margin: 0 0 .35rem; }
.source-toc-group p { margin: .2rem 0; }
figure.art-float-right { float: right; clear: right; width: 48%; max-width: none; margin: .2rem 0 1rem 1.25rem; text-align: right; }
figure.art-float-right img { width: 100%; max-width: 100%; height: auto; }
figure.art-full-width { clear: both; width: 100%; margin: .8rem 0 1.2rem; }
figure.art-full-width img { width: 100%; max-width: 100%; height: auto; }
.statblock-card::after { content: ""; display: block; clear: both; }
#soderzhanie, #personazhi-i-chudovischa, #razdatochnye-materialy { clear: both; }
@media (max-width: 820px) {
  .source-toc-columns { columns: 1; }
  figure.art-float-right { float: none; clear: both; width: 100%; margin: .8rem 0 1.2rem; text-align: center; }
}
@media print {
  .source-toc-columns { columns: 2; }
  .title-page { height: 257mm; aspect-ratio: auto; margin: 0; break-after: page; page-break-after: always; }
  .title-page .title-overlay { font-size: 34pt; }
  figure.art-float-right { float: right !important; clear: right !important; width: 48% !important; max-width: none !important; margin: .2rem 0 1rem 1.25rem !important; text-align: right !important; }
}
</style>
"""


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def config_path_value(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def make_config(output_root: Path) -> dict[str, Any]:
    return {
        "project_key": "kb_creator_innsmouth_accepted_master_ru_html",
        "scenario_title_en": "The Innsmouth Terror",
        "scenario_title_ru": "Ужас Иннсмута",
        "html_lang": "ru",
        "workbench_qa_root": str((output_root / "QA").resolve()),
        "scenario_gates": {"accepted_master_ru_verified": True},
        "production_html": {
            "source_markdown": config_path_value(output_root / "MASTER_RU.md"),
            "output_html": config_path_value(output_root / OUTPUT_HTML_NAME),
            "report": "production_html_report.json",
            "required_gates": ["accepted_master_ru_verified"],
            # MASTER_RU already contains the user-accepted linked contents.
            # Do not generate a second TOC or rewrite its stable destinations.
            "toc_policy": {"mode": "disabled"},
            "print_columns": 1,
            # The first level-3 heading in each stat-block section starts a
            # card run.  The generic renderer then closes/reopens cards at
            # each following level-3 heading until the next level-2 section.
            "statblock_section_policy": {
                "heading_ids": [
                    "diane-loring-50-let-bibliotekar-spravochnogo-otdela",
                    "genevieve-ginny-dubois-25-let-soblaznitelnaya-kinozvezda",
                    "sammy-brewster-21-god-lyubyaschii-brat",
                    "shoggot",
                    "hugo-shrimpy-hargreaves",
                ]
            },
            "typography": {
                "body_font_size": "12pt",
                "body_line_height": "1.45",
                "print_body_font_size": "9.75pt",
                "print_body_line_height": "1.24",
            },
        },
        "positive_content_audit": {
            "html": config_path_value(output_root / OUTPUT_HTML_NAME),
            "report": "positive_content_audit.json",
            "expected": {
                "html_tables": {"exact": 51},
                "html_images": {"exact": 32},
                "html_escaped_raw_markup": {"exact": 0},
                "html_visible_plus_list_markers": {"exact": 0},
                "html_visible_visual_only_placeholders": {"exact": 0},
            },
        },
    }


def transform_title_page(html: str) -> tuple[str, dict[str, int]]:
    pattern = re.compile(
        r'<h1 id="uzhas-innsmuta">[\s\S]*?</h1>\n'
        rf'(?P<art><figure class="art-title-cover art-full-width"><img src="assets/{re.escape(SOURCE_COVER_ASSET)}" alt=""></figure>)',
    )
    match = pattern.search(html)
    if match is None:
        raise ValueError("Innsmouth source title-page binding mismatch")
    replacement = (
        '<section id="title-page" class="title-page production-page page-type-title">\n'
        + match.group("art")
        + '\n<h1 id="uzhas-innsmuta" class="title-overlay">УЖАС ИННСМУТА</h1>\n'
        + "</section>"
    )
    return html[: match.start()] + replacement + html[match.end() :], {
        "title_pages": 1,
        "title_overlays": 1,
    }


def transform_source_toc(html: str) -> tuple[str, dict[str, int]]:
    pattern = re.compile(
        r'(?P<heading><h1 id="soderzhanie">[\s\S]*?</h1>)\n'
        r'(?P<body>[\s\S]*?)'
        r'(?=<h1 id="uzhas-innsmuta-2">)',
    )
    match = pattern.search(html)
    if match is None:
        raise ValueError("Innsmouth source TOC binding mismatch")
    body = match.group("body")
    starts = list(re.finditer(r'(?m)^<h2 id="', body))
    if len(starts) != 11 or body[: starts[0].start()].strip():
        raise ValueError("Innsmouth source TOC group count mismatch")
    groups: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(body)
        group = body[start.start() : end].strip()
        if not group.startswith("<h2 "):
            raise ValueError("Innsmouth source TOC group structure mismatch")
        groups.append('<section class="source-toc-group">\n' + group + "\n</section>")
    replacement = (
        '<section id="source-toc" class="source-toc-section">\n'
        + match.group("heading")
        + '\n<div class="source-toc-columns">\n'
        + "\n".join(groups)
        + "\n</div>\n</section>\n"
    )
    return html[: match.start()] + replacement + html[match.end() :], {
        "source_toc_sections": 1,
        "source_toc_groups": len(groups),
        "source_toc_columns": 2,
    }


def classify_figures(html: str) -> tuple[str, dict[str, int]]:
    all_assets = freeze_ru.RU_RETAINED_ASSETS
    if LETTER_SEAL_ASSET in all_assets:
        raise ValueError("letter seal remains in canonical reader assets")
    if not FULL_WIDTH_ASSETS < all_assets:
        raise ValueError("Innsmouth full-width art allowlist is not a strict reader subset")
    seen: list[str] = []

    def replace(match: re.Match[str]) -> str:
        name = match.group("name")
        if name not in all_assets:
            raise ValueError(f"unclassified Innsmouth figure: {name}")
        seen.append(name)
        if name == SOURCE_COVER_ASSET:
            css_class = "art-title-cover art-full-width"
        elif name in FULL_WIDTH_ASSETS:
            css_class = "art-full-width"
        else:
            css_class = "art-float-right art-inline-half"
        return f'<figure class="{css_class}"><img src="assets/{name}" alt=""></figure>'

    output, substitutions = re.subn(
        r'<figure><img src="assets/(?P<name>[^"<>]+)" alt=""></figure>',
        replace,
        html,
    )
    if (
        substitutions != len(all_assets)
        or len(seen) != len(all_assets)
        or set(seen) != all_assets
        or len(set(seen)) != len(seen)
    ):
        raise ValueError("Innsmouth figure inventory/classification mismatch")
    return output, {
        "figures": substitutions,
        "full_width_figures": len(FULL_WIDTH_ASSETS),
        "inline_half_figures": len(all_assets - FULL_WIDTH_ASSETS),
    }


def relocate_inline_figures(html: str) -> tuple[str, dict[str, int]]:
    expected_inline = freeze_ru.RU_RETAINED_ASSETS - FULL_WIDTH_ASSETS
    placement_assets = {item[0] for item in INLINE_ART_PLACEMENTS}
    if placement_assets != expected_inline or len(placement_assets) != len(
        INLINE_ART_PLACEMENTS
    ):
        raise ValueError("Innsmouth inline-art placement policy mismatch")

    grouped: dict[str, list[str]] = {}
    captions = 0
    output = html
    for name, heading_id, caption, inline_prefix in INLINE_ART_PLACEMENTS:
        figure_pattern = re.compile(
            rf'<figure class="art-float-right art-inline-half">'
            rf'<img src="assets/{re.escape(name)}" alt=""></figure>'
        )
        match = figure_pattern.search(output)
        if match is None or figure_pattern.search(output, match.end()) is not None:
            raise ValueError(f"Innsmouth inline-art identity mismatch: {name}")
        figure = match.group(0)
        before = output[: match.start()]
        after = output[match.end() :]
        if caption is not None:
            if inline_prefix:
                prefix = f"\n<p>{caption} "
                if not after.startswith(prefix):
                    raise ValueError(f"Innsmouth inline caption prefix mismatch: {name}")
                after = "\n<p>" + after[len(prefix) :]
            else:
                paragraph = f"\n<p>{caption}</p>"
                if not after.startswith(paragraph):
                    raise ValueError(f"Innsmouth inline caption mismatch: {name}")
                after = after[len(paragraph) :]
            figure = figure.replace(
                "</figure>", f"<figcaption>{caption}</figcaption></figure>", 1
            )
            captions += 1
        output = before + after
        figure = figure.replace(
            '<figure class="',
            f'<figure data-layout-owner="{heading_id}" class="',
            1,
        )
        grouped.setdefault(heading_id, []).append(figure)

    for heading_id, figures in grouped.items():
        heading_pattern = re.compile(
            rf'(?P<heading><h[23] id="{re.escape(heading_id)}">[\s\S]*?</h[23]>)'
        )
        match = heading_pattern.search(output)
        if match is None or heading_pattern.search(output, match.end()) is not None:
            raise ValueError(f"Innsmouth inline-art owner mismatch: {heading_id}")
        insertion = match.group("heading") + "\n" + "\n".join(figures)
        output = output[: match.start()] + insertion + output[match.end() :]

    return output, {
        "relocated_inline_figures": len(INLINE_ART_PLACEMENTS),
        "inline_figure_owners": len(grouped),
        "figure_captions": captions,
    }


def apply_innsmouth_presentation_layout(html_path: Path) -> dict[str, int]:
    html = html_path.read_text(encoding="utf-8")
    html, toc = transform_source_toc(html)
    html, figures = classify_figures(html)
    html, title = transform_title_page(html)
    html, relocations = relocate_inline_figures(html)
    if html.count("</head>") != 1 or 'id="innsmouth-presentation-r7"' in html:
        raise ValueError("Innsmouth presentation stylesheet binding mismatch")
    html = html.replace("</head>", INNSMOUTH_PRESENTATION_CSS + "</head>", 1)
    html_path.write_text(html, encoding="utf-8", newline="\n")
    return {**title, **toc, **figures, **relocations, "stylesheets": 1}


def html_integrity_report(html_path: Path, asset_names: set[str]) -> dict[str, Any]:
    raw = html_path.read_bytes()
    text = raw.decode("utf-8")
    ids = re.findall(r'\bid="([A-Za-z0-9_-]+)"', text)
    fragments = re.findall(r'href="#([A-Za-z0-9_-]+)"', text)
    broken_fragments = sorted(set(fragments) - set(ids))
    image_refs = re.findall(r'<img\b[^>]*\bsrc="assets/([^"<>]+)"', text)
    missing_assets = sorted(set(image_refs) - asset_names)
    unused_assets = sorted(asset_names - set(image_refs))
    counts = {
        "html_bytes": len(raw),
        "stable_anchors": len(re.findall(r'<a id="nri-[A-Za-z0-9_-]+"></a>', text)),
        "tables": len(re.findall(r"<table(?:\s|>)", text)),
        "image_refs": len(image_refs),
        "internal_fragments": len(fragments),
        "broken_fragments": len(broken_fragments),
        "missing_assets": len(missing_assets),
        "unused_assets": len(unused_assets),
        "statblock_cards": len(re.findall(r'class="statblock-card"', text)),
        "escaped_anchors": text.count("&lt;a id=&quot;nri-"),
        "escaped_tables": text.count("&lt;table&gt;"),
        "technical_comments": len(re.findall(r"mineru-page:|table-evidence:", text)),
        "full_width_figures": len(
            re.findall(r'<figure\b[^>]*class="[^"]*\bart-full-width\b[^"]*">', text)
        ),
        "inline_half_figures": len(
            re.findall(r'<figure\b[^>]*class="[^"]*\bart-inline-half\b[^"]*">', text)
        ),
        "source_toc_sections": text.count('id="source-toc"'),
        "source_toc_groups": text.count('class="source-toc-group"'),
        "title_pages": text.count('id="title-page"'),
        "title_overlays": text.count('class="title-overlay"'),
        "credits_sections": text.count('id="credits"'),
        "presentation_stylesheets": text.count('id="innsmouth-presentation-r7"'),
        "letter_seal_refs": text.count(LETTER_SEAL_ASSET),
        "inline_owner_bindings": text.count('data-layout-owner="'),
        "figure_captions": text.count("<figcaption>"),
    }
    expected = {
        "stable_anchors": 52,
        "tables": 51,
        "image_refs": 32,
        "internal_fragments": 86,
        "broken_fragments": 0,
        "missing_assets": 0,
        "unused_assets": 0,
        "statblock_cards": 22,
        "escaped_anchors": 0,
        "escaped_tables": 0,
        "technical_comments": 0,
        "full_width_figures": 11,
        "inline_half_figures": 21,
        "source_toc_sections": 1,
        "source_toc_groups": 11,
        "title_pages": 1,
        "title_overlays": 1,
        "credits_sections": 0,
        "presentation_stylesheets": 1,
        "letter_seal_refs": 0,
        "inline_owner_bindings": 21,
        "figure_captions": 12,
    }
    actual = {key: counts[key] for key in expected}
    if actual != expected:
        raise ValueError(
            f"generated HTML structural counts mismatch: {actual}; "
            f"broken={broken_fragments}; missing_assets={missing_assets}; "
            f"unused_assets={unused_assets}"
        )
    return {
        "path": OUTPUT_HTML_NAME,
        "byte_count": len(raw),
        "sha256": sha256(raw),
        "counts": counts,
    }


def build(
    master_ru_root: Path,
    master_en_root: Path,
    terminology_registry: Path,
    output_root: Path,
) -> dict[str, Any]:
    accepted = freeze_ru.verify_promoted(
        master_ru_root, terminology_registry, master_en_root
    )
    if output_root.exists():
        raise ValueError(f"refusing to overwrite HTML candidate: {output_root}")

    output_root.mkdir(parents=True)
    try:
        source_raw = (master_ru_root / "MASTER_RU.md").read_bytes()
        (output_root / "MASTER_RU.md").write_bytes(source_raw)
        (output_root / "MASTER_RU.acceptance.json").write_bytes(
            (master_ru_root / "MASTER_RU.acceptance.json").read_bytes()
        )
        shutil.copytree(master_ru_root / "assets", output_root / "assets")

        image_formats: dict[str, int] = {}
        for image_path in sorted((output_root / "assets").iterdir(), key=lambda path: path.name):
            with Image.open(image_path) as image:
                image_formats[str(image.format)] = image_formats.get(str(image.format), 0) + 1
                image.verify()

        config = make_config(output_root)
        config_path = output_root / "innsmouth_master_ru_html.package.json"
        config_path.write_bytes(canonical_json(config))
        html_result = translator.build_production_html(config_path, force=False)
        if html_result.get("status") != "pass":
            raise ValueError(f"production HTML build failed: {html_result.get('findings')}")
        presentation = apply_innsmouth_presentation_layout(output_root / OUTPUT_HTML_NAME)
        positive_content = translator.run_positive_content_audit(config_path)
        if positive_content.get("status") != "pass":
            raise ValueError(
                f"positive-content audit failed: {positive_content.get('findings')}"
            )

        asset_names = {path.name for path in (output_root / "assets").iterdir() if path.is_file()}
        html = html_integrity_report(output_root / OUTPUT_HTML_NAME, asset_names)
        if sha256((output_root / "MASTER_RU.md").read_bytes()) != freeze_ru.PROMOTED_MASTER_RU_SHA256:
            raise ValueError("HTML candidate source copy differs from accepted MASTER_RU")

        manifest = {
            "schema": "kb_creator.innsmouth_master_ru_html_build.v1",
            "state": "INNSMOUTH_MASTER_RU_HTML_CANDIDATE_BUILT",
            "accepted_master_ru": accepted,
            "source_copy": {
                "path": "MASTER_RU.md",
                "byte_count": len(source_raw),
                "sha256": sha256(source_raw),
            },
            "assets": {
                "path": "assets",
                "count": len(asset_names),
                "inventory_sha256": accepted["asset_inventory"]["inventory_sha256"],
                "verified_decodable": len(asset_names),
                "formats": image_formats,
            },
            "html": html,
            "presentation": presentation,
            "positive_content_audit": {
                "status": positive_content["status"],
                "counts": positive_content["counts"],
                "findings": positive_content["findings"],
            },
            "rules": {
                "source_is_frozen_accepted_master_ru": True,
                "generated_html_manual_edit_forbidden": True,
                "historical_v6_inputs_forbidden": True,
                "duplicate_generated_toc_forbidden": True,
            },
        }
        (output_root / "MASTER_RU_HTML.build.json").write_bytes(canonical_json(manifest))
        return manifest
    except Exception:
        shutil.rmtree(output_root)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master-ru-root", type=Path, default=DEFAULT_MASTER_RU_ROOT)
    parser.add_argument("--master-en-root", type=Path, default=DEFAULT_MASTER_EN_ROOT)
    parser.add_argument(
        "--terminology-registry",
        type=Path,
        default=DEFAULT_TERMINOLOGY_REGISTRY,
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    result = build(
        args.master_ru_root.resolve(),
        args.master_en_root.resolve(),
        args.terminology_registry.resolve(),
        args.output_root.resolve(),
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    print("INNSMOUTH_MASTER_RU_HTML_CANDIDATE_OK")


if __name__ == "__main__":
    main()
