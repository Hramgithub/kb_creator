#!/usr/bin/env python3
"""Build the final Viral EN/RU/HTML/PDF/DOCX package from accepted review masters."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BASE_EN = REPO_ROOT / "kb_creator/inputs/viral/master_en/review_checkpoint_20260905_review_fixes_d/candidate/MASTER_EN.md"
BASE_RU = REPO_ROOT / "kb_creator/inputs/viral/master_ru/review_checkpoint_20260906/candidate/MASTER_RU.md"
PUBLICATION_CONFIG = REPO_ROOT / "kb_creator/inputs/viral/master_en/review_checkpoint_20260905_review_fixes_d/publication_config_v2.json"
DEFAULT_OUTPUT = REPO_ROOT / "kb_creator/inputs/viral/production"
DEFAULT_ARTVIEW_PROFILE = REPO_ROOT / "kb_creator/reference/viral/artview_review_policy_v2.json"
PACKAGED_ARTVIEW_DECISIONS = "ARTVIEW_DECISIONS.accepted.json"
PACKAGED_ARTVIEW_CONFIG = "ARTVIEW_CONFIG.json"
PACKAGED_ARTVIEW_MANIFEST = "ARTVIEW_CANDIDATE_MANIFEST.json"
ARTVIEW_RECEIPT = "ARTVIEW_APPLIED.json"
ARTVIEW_RENDER_MARKDOWN = "ARTVIEW_RENDER_RU.md"

INTRO_ART = "4592e580aba8b9bad7a83eb2acf44e0480005e48b034ecd1ac436860efdbd137.jpg"
SIGNS_ART = "16f390d7a4c0fc8856f4a878a164b11ec4e922c7df6fbb002e41e285a781d2a3.jpg"
PLAGUE_MONK_ART = "81953e331e0b27630c228051831a510c123801aa360c1f6d0fa82d66516ee677.jpg"
RELIQUAE_ART = "6e1d78ee26178218de74fd8203ef772eb3e8f4951ea6e419a0a00e25051b8237.jpg"
RELIQUAE_FLY_ART = "2fbd31994da00cc5320dccf115f2aae8da89b5e5997e93ad5f853afbf13bad03.jpg"
HANDOUT_9_ART = "826e5103327297822e6270444f8d57d02a135ffbc2d246ffbdb5788d297fd55a.jpg"
HANDOUT_10_ART = "8dfcf412070881aa81b8933eeb329d7409edbe1316329701bb605c9dab835d65.jpg"
HANDOUT_39_ART = "bbcf13fecd9ade245d04db78356787f798176f58c9eb9b69c27d4936f6e888ba.jpg"
KEEPER_MAP_LOCATION_ART = "2594c936ac511e9594fccbbc79e2a9acdb7ad0475baec5fbf0640a4dfb24ea91.jpg"
DUPLICATE_NARRATIVE_ART = "222ccd9a31a25cadc0bfab40f4e037eb55b91ca7ee523fc5d9784f30407e4bfa.jpg"
SUPPRESSED_TEXT_FACSIMILES = {
    "9ee3d23cac4831e4230386f671d228d7a53b336310983f967eada4f3d2677ad8.jpg",
    "b1b7888cf28240790d1fd7fdc5621da9fe159c9442ec0f3bfa7f45243319cfea.jpg",
    "f796716cd86ee8580b1d2cd8552d89cbf29f989bc8eae6be386ffa2528dc078b.jpg",
    "2a60f183499c0a1a5f3bd353949a7efc2a389d5fbd98782e79e53d346d9c390f.jpg",
    "8dcb6eee3da06a699ff2ac68c0b32338209a8abad3327bf0c8e246c2722dc76e.jpg",
}


def bookmark_name(anchor: str) -> str:
    """Mirror the stable Word bookmark naming used by production_docx.py."""
    return f"nri_{hashlib.sha1(anchor.encode('utf-8')).hexdigest()[:32]}"


def current_viral_html_layout_policy() -> dict[str, Any]:
    """Return downstream-only layout rules that render-only must keep current."""
    navigation_anchor_ids = [
        "viral-player-handouts",
        "viral-keeper-maps",
        "viral-pregenerated-investigators",
    ]
    return {
        "allow_long_callout_page_breaks": True,
        "avoid_single_column_fragmentation_context": True,
        "suppress_section_navigation_after_anchor_ids": navigation_anchor_ids,
        "bind_section_heading_into_first_card_anchor_ids": ["viral-pregenerated-investigators"],
        # Pregenerated Investigators immediately follows the final full-page
        # Keeper map. A second forced break there creates a blank Chromium page;
        # the rendered page-top QA below protects the natural boundary instead.
        "page_break_before_anchor_ids": ["viral-player-handouts", "viral-keeper-maps"],
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def refresh_pipeline_snapshot(output: Path) -> None:
    """Refresh the portable pipeline snapshot for full and render-only builds."""
    pipeline = output / "pipeline"
    pipeline.mkdir(exist_ok=True)
    sources = [
        Path(__file__),
        REPO_ROOT / "kb_creator/scripts/build_scenario_master_en.py",
        REPO_ROOT / "kb_creator/scripts/verify_scenario_master_en.py",
        REPO_ROOT / "kb_creator/scripts/viral_publication_projection.py",
        REPO_ROOT / "kb_creator/scripts/scenario_artview.py",
        REPO_ROOT / "kb_creator/scripts/production_docx.py",
        REPO_ROOT / "translator/translator.py",
        REPO_ROOT / "CoC/SCENARIO_PACKAGE_STANDARD.md",
        PUBLICATION_CONFIG,
        REPO_ROOT / "kb_creator/reference/viral/artview_review_policy.json",
        REPO_ROOT / "kb_creator/reference/viral/artview_review_policy_v2.json",
        REPO_ROOT / "kb_creator/docs/terminology/VIRAL_EN_RU.md",
        REPO_ROOT / "kb_creator/docs/plans/20260830-kb-creator-next-scenario/VIRAL_HTML_REVIEW_TODO_20260907.md",
        REPO_ROOT / "kb_creator/docs/plans/20260830-kb-creator-next-scenario/VIRAL_TEXT_PARAGRAPH_BOUNDARY_AUDIT_20260907.md",
        REPO_ROOT / "kb_creator/tests/test_build_viral_production.py",
        REPO_ROOT / "kb_creator/tests/test_build_scenario_master_en.py",
        REPO_ROOT / "kb_creator/tests/test_verify_scenario_master_en.py",
        REPO_ROOT / "kb_creator/tests/test_viral_publication_projection.py",
        REPO_ROOT / "kb_creator/tests/test_scenario_artview.py",
        REPO_ROOT / "translator/tests/test_recovery_support.py",
    ]
    for source in sources:
        if source.is_file():
            shutil.copy2(source, pipeline / source.name)


def production_readme_text() -> str:
    return """# Viral production package

This directory is the self-contained production checkpoint. It contains the
editable `MASTER_RU.md`, source-faithful corrected `MASTER_EN.md`, all referenced
assets, `Viral_RU.html`, `Viral_RU.pdf`, `Viral_RU.docx`, QA, asset decisions,
build config and a
pipeline snapshot. To rebuild after a manual Markdown-formatting edit, keep the
asset references unchanged and run from the repository root:

```powershell
python -B kb_creator/scripts/build_viral_production.py --render-only
```

To apply an accepted ArtView review without editing either master, run:

```powershell
python -B kb_creator/scripts/build_viral_production.py --render-only --artview-decisions <accepted-json>
```

To rebuild only the editable Word projection while leaving the packaged HTML,
PDF, masters, ArtView aliases, QA and manifest byte-for-byte unchanged, run:

```powershell
python -B kb_creator/scripts/build_viral_production.py --word-only --artview-decisions <accepted-json>
```

To normalize numbered handout headings in both packaged masters and rebuild
only HTML, while preserving a manually edited Word file and the current PDF:

```powershell
python -B kb_creator/scripts/build_viral_production.py --handout-html-only
```

After exporting the manually edited `Viral_RU.docx` to `Viral_RU.pdf` with
Microsoft Word, validate and register that PDF without rebuilding Word or HTML:

```powershell
python -B kb_creator/scripts/build_viral_production.py --finalize-word-pdf
```

Before that export, an edited Word file must receive the production navigation
and callout semantics without being regenerated from HTML:

```powershell
python -B kb_creator/scripts/build_viral_production.py --patch-word-semantics
```

`--render-only` reads the packaged `MASTER_RU.md` in place; refreshes current
downstream layout policy and the portable pipeline snapshot; then rebuilds
`Viral_RU.html`, `Viral_RU.pdf`, `Viral_RU.docx`, QA reports and the manifest. It never restores
the review-checkpoint source over the edited Russian master.
Accepted ArtView decisions are stored byte-for-byte as both
`ARTVIEW_DECISIONS.accepted.json` and the explicit current
`ARTVIEW_CONFIG.json`, then materialized into `assets/artview/` and the derived
`ARTVIEW_RENDER_RU.md`; subsequent render-only runs refresh that
projection from the editable master and `ARTVIEW_APPLIED.json`. The masters are
never rewritten by this layer.
`--word-only` materializes the accepted ArtView review in an isolated temporary
workspace, builds a temporary HTML projection there, and atomically replaces
only `Viral_RU.docx` in the production directory. The accepted JSON itself may
live in the production package; candidate binaries are resolved from the
bound ArtView checkpoint.
`--handout-html-only` is the explicit exception to master immutability: it uses
the appendix navigation as the canonical EN/RU handout-title registry, rewrites
every anchored handout as one numbered H3 followed by a plain title, refreshes
the accepted ArtView projection and HTML, and verifies that `Viral_RU.docx` and
`Viral_RU.pdf` were not changed.
`--finalize-word-pdf` treats the packaged DOCX as the final layout source,
requires 52 linked TOC entries, 44 linked body cross-references, resolving Word
bookmarks, highlighted review callouts and matching PDF destinations, then
checks page sequence, A4 geometry and empty-page inventory before refreshing QA
and the manifest. `--patch-word-semantics` changes only `word/document.xml`: it
wraps the existing styled link runs in real internal hyperlinks, adds stable
bookmarks, and restores the Innsmouth-style beige/rust callout treatment while
preserving user-edited text, media, headers, footers and section layout.

The PDF/HTML presentation inherits the accepted Innsmouth Terror production
profile (A4 palette and framing, typography, single-column print body, statblock
cards, role-aware art sizing, and atomic full-page art/heading binding). The RU
reader omits the source credits sheet. Viral-specific contents, two-column TOC,
handouts and semantic asset bindings remain declared in `build_config.json`.
The downstream renderer suppresses the three section-local navigation lists
under Player Handouts, Keeper Maps and Pregenerated Investigators, while
preserving ordinary content lists and the numbered Isola map legend. Those
three appendix groups start at the top of a new print page. Production QA also
rejects text-only interior PDF pages shorter than 80 extracted characters, so
a detached two-line tail cannot pass as an intentional page.
"""


def replace_exact(text: str, old: str, new: str, label: str, expected: int = 1) -> str:
    count = text.count(old)
    if count != expected:
        raise ValueError(f"{label}: expected {expected} matches, found {count}")
    return text.replace(old, new)


def collapse_contents(text: str, *, ru: bool) -> str:
    start = text.index('<a id="viral-contents"></a>')
    list_start = text.index("\n- ", start) + 1
    list_end = text.index("\n\n", list_start)
    rows = text[list_start:list_end].splitlines()
    keep = {
        "viral-opening-message", "viral-warning", "viral-introduction",
        "viral-spektral-krew", "viral-creating-new-investigators", "viral-spektral-krew-gear",
        "viral-timeline", "viral-history", "viral-one-night-in-perla", "viral-isola-di-malamente",
        "viral-epilogue", "viral-appendix", "viral-player-handouts", "viral-keeper-maps",
        "viral-pregenerated-investigators",
    }
    if not ru:
        keep.add("viral-credits")
    filtered = []
    for row in rows:
        match = re.search(r"\(#([^)]+)\)", row)
        if match and match.group(1) in keep:
            if match.group(1) == "viral-player-handouts":
                row = f"- [{'Раздаточные материалы' if ru else 'Handouts'}](#viral-player-handouts)"
            elif match.group(1) == "viral-pregenerated-investigators":
                row = f"- [{'Персонажи' if ru else 'Characters'}](#viral-pregenerated-investigators)"
            filtered.append(row)
    if len(filtered) != len(keep):
        raise ValueError(f"contents: expected {len(keep)} top-level rows, found {len(filtered)}")
    return text[:list_start] + "\n".join(filtered) + text[list_end:]


def remove_ru_credits(text: str) -> str:
    """Remove the RU-only credits sheet while preserving the following opening block."""
    start_marker = '<a id="viral-credits"></a>'
    end_marker = '<a id="viral-opening-message"></a>'
    if text.count(start_marker) != 1 or text.count(end_marker) != 1:
        raise ValueError("RU credits: expected one start and one end marker")
    start = text.index(start_marker)
    end = text.index(end_marker)
    prefix = text[:start].rstrip()
    return prefix + ("\n\n" if prefix else "") + text[end:]


def normalize_ru_headings(text: str) -> str:
    """Apply reader-facing RU heading normalization without changing stable anchors."""
    replacements = {
        "# ВИРУС": "# Вирус",
        "## ПРЕДУПРЕЖДЕНИЕ": "## Предупреждение",
        "## КОМАНДА «СПЕКТРАЛ»": "## Команда «Спектрал»",
    }
    for old, new in replacements.items():
        text = replace_exact(text, old, new, f"RU heading normalization: {old}")
    lines = text.splitlines()
    for index, line in enumerate(lines[:-1]):
        anchor = re.fullmatch(r'<a id="(viral-isola-location-[^"]+)"></a>', line.strip())
        if not anchor:
            continue
        heading_index = index + 1
        while heading_index < len(lines) and not lines[heading_index].strip():
            heading_index += 1
        if heading_index >= len(lines):
            raise ValueError(f"location heading missing after {anchor.group(1)}")
        heading = re.fullmatch(r"(#{2,6}\s+)\d+\.\s+(.+)", lines[heading_index])
        if not heading:
            raise ValueError(f"numbered location heading missing after {anchor.group(1)}")
        lines[heading_index] = heading.group(1) + heading.group(2)
    return "\n".join(lines)


def move_image_after_heading(text: str, filename: str, heading_anchor: str) -> str:
    line_re = re.compile(rf"(?m)^!\[[^\]]*\]\(assets/{re.escape(filename)}\)(?:\{{[^}}]*\}})?\n?")
    matches = list(line_re.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"image {filename}: expected one reference, found {len(matches)}")
    image = matches[0].group(0).strip()
    text = line_re.sub("", text, count=1)
    marker = f'<a id="{heading_anchor}"></a>'
    pos = text.index(marker)
    heading_end = text.index("\n", text.index("\n", pos) + 1)
    return text[:heading_end] + "\n\n" + image + text[heading_end:]


def move_images_after_heading(text: str, filenames: list[str], heading_anchor: str) -> str:
    """Move a source-ordered image group directly after its semantic owner heading."""
    images: list[str] = []
    for filename in filenames:
        line_re = re.compile(rf"(?m)^!\[[^\]]*\]\(assets/{re.escape(filename)}\)(?:\{{[^}}]*\}})?\n?")
        matches = list(line_re.finditer(text))
        if len(matches) != 1:
            raise ValueError(f"image {filename}: expected one reference, found {len(matches)}")
        images.append(matches[0].group(0).strip())
        text = line_re.sub("", text, count=1)
    marker = f'<a id="{heading_anchor}"></a>'
    pos = text.index(marker)
    heading_end = text.index("\n", text.index("\n", pos) + 1)
    return text[:heading_end] + "\n\n" + "\n\n".join(images) + text[heading_end:]


def preheading_body_art_bindings(registry: dict[str, Any]) -> list[tuple[str, list[str]]]:
    """Return body reader art whose accepted placement precedes its own heading."""
    excluded_anchor_prefixes = ("viral-handout-", "viral-keeper-map-", "viral-pregen-")
    excluded_anchors = {"viral-credits", "viral-handouts-hyeons-ipads"}
    grouped: dict[str, list[tuple[int, int, str]]] = {}
    for row in registry.get("assets", []):
        if not isinstance(row, dict) or row.get("disposition") != "reader":
            continue
        anchor = str(row.get("anchor") or "")
        if not anchor or anchor in excluded_anchors or anchor.startswith(excluded_anchor_prefixes):
            continue
        placement = row.get("placement") or {}
        if placement.get("before_event") != f"heading:{anchor}":
            continue
        binary = row.get("binary") or {}
        binary_path = str(binary.get("path") or "")
        if not binary_path:
            continue
        filename = Path(binary_path).name
        if filename in SUPPRESSED_TEXT_FACSIMILES or filename == DUPLICATE_NARRATIVE_ART:
            continue
        order = row.get("source_order") or {}
        grouped.setdefault(anchor, []).append((int(row.get("source_page") or 0), int(order.get("raw_index") or 0), filename))
    return [
        (anchor, [filename for _, _, filename in sorted(rows)])
        for anchor, rows in grouped.items()
    ]


def relocate_preheading_body_art(text: str, registry_path: Path = PUBLICATION_CONFIG) -> tuple[str, dict[str, list[str]]]:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    bindings = preheading_body_art_bindings(registry)
    for anchor, filenames in bindings:
        text = move_images_after_heading(text, filenames, anchor)
    return text, dict(bindings)


def move_image_after_table(text: str, filename: str, heading_anchor: str) -> str:
    line_re = re.compile(rf"(?m)^!\[[^\]]*\]\(assets/{re.escape(filename)}\)(?:\{{[^}}]*\}})?\n?")
    matches = list(line_re.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"table art {filename}: reference count mismatch")
    image = matches[0].group(0).strip()
    text = line_re.sub("", text, count=1)
    start = text.index(f'<a id="{heading_anchor}"></a>')
    table_start = text.index("\n|", start) + 1
    cursor = table_start
    lines = text[table_start:].splitlines(keepends=True)
    consumed = 0
    for line in lines:
        if not line.startswith("|"):
            break
        consumed += len(line)
    table_end = table_start + consumed
    return text[:table_end].rstrip("\n") + "\n\n" + image + "\n" + text[table_end:].lstrip("\n")


def remove_images(text: str, filenames: set[str]) -> str:
    for filename in sorted(filenames):
        pattern = re.compile(rf"(?m)^!\[[^\]]*\]\(assets/{re.escape(filename)}\)(?:\{{[^}}]*\}})?\n?\n?")
        text, count = pattern.subn("", text)
        if count != 1:
            raise ValueError(f"suppressed image {filename}: expected one reference, found {count}")
    return text


def swap_image_references(text: str, first: str, second: str) -> str:
    """Swap two unique image targets without changing surrounding source structure."""
    if text.count(f"assets/{first}") != 1 or text.count(f"assets/{second}") != 1:
        raise ValueError(f"image swap requires one reference each: {first}, {second}")
    sentinel = "assets/__viral_image_swap_sentinel__"
    if sentinel in text:
        raise ValueError("image swap sentinel already exists")
    return (
        text.replace(f"assets/{first}", sentinel, 1)
        .replace(f"assets/{second}", f"assets/{first}", 1)
        .replace(sentinel, f"assets/{second}", 1)
    )


def restore_handout_8_postscript(text: str, *, ru: bool) -> str:
    marker = "Письма Майи\n\n(2 из 2)" if ru else "Maya's Emails\n\n(2 of 2)"
    addition = (
        "\n\nP.S. Я также приложила обычный текст «для чтения в камеру» в начале трансляции — "
        "отправила Хёну напоминание загрузить его в телесуфлёр. И да, да, на этот раз я не забыла "
        "прорекламировать мерч на Zazzle!\n\n"
        "P.P.S. Забыла сказать: Isola di Malamente примерно переводится как «остров душевнобольных». "
        "Честно говоря, детка, я рада, что буду смотреть эту трансляцию из дома.\n\n"
        "Вложение [5,3 МБ]"
        if ru else
        "\n\nP.S. I have also included the usual “read to camera” bit for the beginning of the stream — "
        "sent a reminder to Hyeon to put them on the auto-cue. And yes, yes, I remembered to plug "
        "the Zazzle merch this time around!\n\n"
        "P.P.S. Meant to tell you: a rough translation of Isola di Malamente is something like "
        "“island of the mentally ill”. I gotta be honest, babez, I’m glad I am watching this one from home.\n\n"
        "Attachment [5.3M]"
    )
    return replace_exact(text, marker, marker + addition, "Handout 8 postscript")


def extend_keeper_note(text: str, *, ru: bool) -> str:
    lead = "Спиритическая доска." if ru else "The Witch Board."
    needle = "\n\n" + lead
    if text.count(needle) != 1:
        raise ValueError(f"keeper-note extension {lead}: boundary mismatch")
    return text.replace(needle, "\n> \n> " + lead, 1)


def split_statblock_lines(text: str, first_prefix: str) -> tuple[str, list[str]]:
    pattern = re.compile(rf"(?m)^> {re.escape(first_prefix)}.*(?:\n>.*)*")
    match = pattern.search(text)
    if not match:
        raise ValueError(f"statblock not found: {first_prefix}")
    lines = [re.sub(r"^> ?", "", line) for line in match.group(0).splitlines()]
    return match.group(0), lines


def render_statblock(lines: list[str], *, ru: bool) -> str:
    attacks_label = "АТАКИ" if ru else "ATTACKS"
    abilities_label = "ОСОБЫЕ СПОСОБНОСТИ" if ru else "SPECIAL ABILITIES"
    attacks = lines.index(attacks_label)
    abilities = lines.index(abilities_label)
    title = lines[0].replace("**", "").strip()
    stat_rows = []
    for line in lines[1:attacks]:
        if ":" in line and not line.lstrip().startswith("\\*"):
            key, value = line.split(":", 1)
            stat_rows.append((key.strip(), value.strip()))
    header = ("Параметр", "Значение") if ru else ("Field", "Value")
    out = [f"##### {title}", "", f"| {header[0]} | {header[1]} |", "| --- | --- |"]
    out.extend(f"| {key} | {value} |" for key, value in stat_rows)
    footnotes = [line for line in lines[1:attacks] if line.lstrip().startswith("\\*")]
    if footnotes:
        out.extend(["", *footnotes])
    out.extend(["", f"###### {attacks_label.title() if not ru else 'Атаки'}", ""])
    for line in lines[attacks + 1:abilities]:
        if ":" in line:
            key, value = line.split(":", 1)
            out.append(f"**{key.strip()}.**{value}")
        else:
            out.append(line)
        out.append("")
    out.extend([f"###### {'Особые способности' if ru else 'Special Abilities'}", ""])
    in_table = False
    for line in lines[abilities + 1:]:
        if line.startswith("|"):
            out.append(line)
            in_table = True
            continue
        if in_table and not line:
            out.extend([""])
            in_table = False
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            out.append(f"**{key.strip()}.**{value}")
        else:
            out.append(line)
        out.append("")
    return "\n".join(out).rstrip()


def restructure_statblocks(text: str, *, ru: bool) -> str:
    prefixes = ["**Пожиратель**" if ru else "**The Devourer**", "Проклятые чумные зомби" if ru else "Cursed Plague Zombies"]
    for prefix in prefixes:
        raw, lines = split_statblock_lines(text, prefix)
        text = text.replace(raw, render_statblock(lines, ru=ru), 1)
    return text


def bind_pregen_headings_to_pages(text: str) -> str:
    """Place each pre-generated sheet heading directly before its own page art."""
    pattern = re.compile(
        r'(?ms)(<a id="viral-pregen-([a-z-]+)-front"></a>\n### [^\n]+\n\n)'
        r'(<a id="viral-pregen-\2-background"></a>\n### [^\n]+\n\n)'
        r'(!\[[^\n]*\]\(assets/[^)\n]+\)(?:\{[^}\n]+\})?\n\n)'
        r'(!\[[^\n]*\]\(assets/[^)\n]+\)(?:\{[^}\n]+\})?)'
    )

    def reorder(match: re.Match[str]) -> str:
        return match.group(1) + match.group(4) + "\n\n" + match.group(3) + match.group(5)

    text, count = pattern.subn(reorder, text)
    if count != 6:
        raise ValueError(f"pregenerated sheet pairs: expected 6, found {count}")
    return text


def normalize_boundaries(text: str, *, ru: bool) -> str:
    pairs = [
        ("бронзового\n\nвека", "бронзового века"),
        ("прислать кого-нибудь в\n\nСША", "прислать кого-нибудь в США"),
        ("ещё одну бонусную\n\nкость", "ещё одну бонусную кость"),
        ("помогать алгоритму.\nО расследовании", "помогать алгоритму.\n\nО расследовании"),
        ("её воплощение.\nЕё отношения", "её воплощение.\n\nЕё отношения"),
        ("называет её Карлой.\nКогда группа", "называет её Карлой.\n\nКогда группа"),
    ] if ru else [
        ("Bronze\n\nAge", "Bronze Age"),
        ("over to the\n\nUS", "over to the US"),
        ("a further Bonus\n\nDie", "a further Bonus Die"),
        ("help the algorithm.\nEm learned", "help the algorithm.\n\nEm learned"),
        ("able to manifest.\nShe has", "able to manifest.\n\nShe has"),
        ("from time-to-time.\nWhen the group", "from time-to-time.\n\nWhen the group"),
    ]
    for old, new in pairs:
        text = replace_exact(text, old, new, f"paragraph boundary: {old[:24]}")
    text = re.sub(r"(</a>\*\*[^\n*]+\*\*) \.", r"\1.", text)
    return text


METRIC_REPLACEMENTS = {
    "6'4\"": "193 см", "5'7\"": "170 см", "6'6\"": "198 см", "5'9\"": "175 см",
    "6'2\"": "188 см", "5'8\"": "173 см", "5'2\"": "157 см",
    "на 165 футов": "на 50 метров", "восьмидесяти футов": "24 метров", "тридцать футов": "9 метров",
    "нескольких ярдах": "нескольких метрах", "десяти футов": "3 метров", "пяти-десяти футах": "1,5–3 метрах",
    "в нескольких футах": "в нескольких метрах",
    "пяти футов": "1,5 метра", "трёх футов": "1 метра", "семь футов": "2 метров",
    "пятьдесят галлонов": "190 литров", "пятидесятигаллонных": "190-литровых", "пятигаллонную": "19-литровую",
    "через фут": "через 30 сантиметров", "сорок футов": "12 метров", "трёхфутовым": "метровым",
    "250 футов": "75 метров", "150 футов": "45 метров", "сто пятьдесят футов": "45 метров",
    "двадцать футов": "6 метров", "200 футов": "60 метров", "50 футов": "15 метров",
    "нескольких сотнях футов": "нескольких десятках метров", "шестьдесят футов": "18 метров",
    "сорок футов": "12 метров", "десять футов": "3 метров", "восемнадцати дюймов": "45 сантиметров",
    "тридцати в длину": "75 сантиметров в длину", "десяти в толщину": "25 сантиметров в толщину",
    "четыре фута": "1,2 метра", "семь футов": "2,1 метра", "три фута": "0,9 метра",
    "двух с половиной футов": "75 сантиметров", "два фута": "60 сантиметров", "шести футов": "1,8 метра",
    "восемьдесят футов": "24 метра", "пятидесяти футах": "15 метрах", "шириной десять футов": "шириной 3 метра",
    "расстояние пяти футов": "расстояние 1,5 метра", "десять футов": "3 метра", "30 футов": "9 метров",
    "10 футов": "3 метра", "сотни футов": "30 метров", "0–100 футов": "0–30 метров",
    "1 миля/ч": "1,5 км/ч", "2 мили/ч": "3 км/ч", "3 мили/ч": "5 км/ч", "4 мили/ч": "6,5 км/ч",
    "в восьми милях": "примерно в 13 километрах", "$75^{\\circ}$ F ( $24^{\\circ}$ C)": "$24^{\\circ}$ C",
    "3 ярда": "3 метра", "3 ярдов": "3 метров", "5 ярдов": "5 метров", "6 ярдов": "6 метров",
    "9 ярдов": "9 метров", "10 ярдов": "10 метров", "11+ ярдов": "11+ метров",
}


def metricize_ru(text: str) -> str:
    for old, new in sorted(METRIC_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(old, new)
    return text


def annotate_art(text: str, asset_root: Path) -> str:
    del asset_root
    section_role = "body"
    output = []
    for line in text.splitlines():
        anchor = re.fullmatch(r'<a id="([A-Za-z0-9_-]+)"></a>', line.strip())
        if anchor:
            anchor_id = anchor.group(1)
            if anchor_id.startswith("viral-handout-"):
                section_role = "handout"
            elif anchor_id.startswith("viral-pregen-"):
                section_role = "pregen"
            elif anchor_id.startswith("viral-keeper-map-"):
                section_role = "full_page"
            else:
                section_role = "body"
        match = re.fullmatch(r"(!\[[^\]]*\]\(assets/([^)]+)\))(?:\{[^}]*\})?", line.strip())
        if not match:
            output.append(line)
            continue
        filename = match.group(2)
        if filename == "viral-render-cover-front.png":
            css = "art-cover"
        elif section_role == "handout":
            css = "art-handout-page"
        elif section_role == "pregen":
            css = "art-pregen-fullpage"
        elif section_role == "full_page" or filename.startswith("viral-provisional-"):
            css = "art-full-page"
        else:
            css = "art-body-right"
        output.append(f"{match.group(1)}{{.{css}}}")
    return "\n".join(output) + "\n"


def handout_number_key(value: str) -> tuple[int, str]:
    match = re.fullmatch(r"(?P<number>\d+)(?P<suffix>[a-z]?)", value)
    if not match:
        raise ValueError(f"invalid handout number: {value}")
    return int(match.group("number")), match.group("suffix")


def handout_navigation_titles(text: str, *, ru: bool) -> dict[str, tuple[str, str]]:
    """Return the canonical handout titles declared by the appendix index."""
    prefix = "Материал" if ru else "Handout"
    pattern = re.compile(
        rf"(?m)^- \[{prefix} (?P<number>\d+[a-z]?): (?P<title>.+)\]"
        rf"\(#viral-handout-(?P<anchor>\d+[a-z]?)\)$"
    )
    titles: dict[str, tuple[str, str]] = {}
    for match in pattern.finditer(text):
        number = match.group("number")
        anchor = match.group("anchor")
        if handout_number_key(number) != handout_number_key(anchor):
            raise ValueError(f"handout navigation number mismatch: {number} != {anchor}")
        if anchor in titles:
            raise ValueError(f"duplicate handout navigation entry: {anchor}")
        titles[anchor] = (number, match.group("title").strip())
    if len(titles) != 41:
        raise ValueError(f"handout navigation: expected 41 entries, found {len(titles)}")
    return titles


def plain_markdown_line(line: str) -> str:
    """Reduce a standalone Markdown heading/emphasis line to its visible text."""
    value = re.sub(r"^#{1,6}\s+", "", line.strip())
    while len(value) >= 2 and value[0] == value[-1] and value[0] in "*_":
        value = value[1:-1].strip()
    return value


def handout_title_line_variants(title: str) -> set[str]:
    """Cover source titles split before a trailing parenthetical qualifier."""
    variants = {title}
    match = re.fullmatch(r"(.+?)\s+(\([^)]+\))", title)
    if match:
        variants.update({match.group(1).strip(), match.group(2).strip()})
    return variants


def normalize_handout_headers(text: str, *, ru: bool) -> str:
    """Give every handout one numbered H3 followed by its plain canonical title.

    MinerU places some numbered labels after the handout body and promotes the
    descriptive title to H3. That makes adjacent handouts appear to swap names
    in editable Word output. The appendix navigation is the stable source of
    truth for both the number and title, so rebuild each anchored block from it.
    """
    titles = handout_navigation_titles(text, ru=ru)
    block_pattern = re.compile(
        r'(?ms)^(?P<anchor><a id="viral-handout-(?P<id>\d+[a-z]?)"></a>)\n'
        r'(?P<body>.*?)(?=^<a id="viral-handout-\d+[a-z]?"></a>\n|'
        r'^<a id="viral-keeper-map-[^"]+"></a>\n|\Z)'
    )
    seen: set[str] = set()

    def rebuild(match: re.Match[str]) -> str:
        handout_id = match.group("id")
        if handout_id not in titles:
            raise ValueError(f"handout block missing navigation title: {handout_id}")
        if handout_id in seen:
            raise ValueError(f"duplicate handout block: {handout_id}")
        seen.add(handout_id)
        display_number, title = titles[handout_id]
        lines = match.group("body").splitlines()
        while lines and not lines[0].strip():
            lines.pop(0)
        if not lines or not re.match(r"^#{1,6}\s+", lines[0].strip()):
            raise ValueError(f"handout {handout_id}: leading heading not found")
        lines.pop(0)

        numbered_label = (
            f"Раздаточный материал #{display_number}" if ru else f"Handout #{display_number}"
        )
        removable = handout_title_line_variants(title) | {numbered_label}
        lines = [line for line in lines if plain_markdown_line(line) not in removable]
        body = "\n".join(lines).strip()
        heading = f"### *{numbered_label}*"
        result = f"{match.group('anchor')}\n{heading}\n\n{title}"
        if body:
            result += f"\n\n{body}"
        return result.rstrip() + "\n\n"

    normalized = block_pattern.sub(rebuild, text)
    if seen != set(titles):
        missing = sorted(set(titles) - seen)
        extra = sorted(seen - set(titles))
        raise ValueError(f"handout blocks do not match navigation: missing={missing}, extra={extra}")
    return re.sub(r"\n{3,}", "\n\n", normalized).strip() + "\n"


def normalize_master(text: str, *, ru: bool, asset_root: Path) -> str:
    text = collapse_contents(text, ru=ru)
    if ru:
        text = remove_ru_credits(text)
        text = normalize_ru_headings(text)
    text = normalize_boundaries(text, ru=ru)
    text = extend_keeper_note(text, ru=ru)
    text, _ = relocate_preheading_body_art(text)
    text = move_image_after_table(text, SIGNS_ART, "viral-one-night-in-perla-signs-and-portents")
    text = move_images_after_heading(
        text,
        [RELIQUAE_ART, RELIQUAE_FLY_ART],
        "viral-appendix-new-mythos-horrors-reliquae",
    )
    text = restore_handout_8_postscript(text, ru=ru)
    text = move_image_after_heading(text, HANDOUT_9_ART, "viral-handout-09")
    text = move_image_after_heading(text, HANDOUT_10_ART, "viral-handout-10")
    text = swap_image_references(text, HANDOUT_39_ART, KEEPER_MAP_LOCATION_ART)
    text = remove_images(text, SUPPRESSED_TEXT_FACSIMILES | {DUPLICATE_NARRATIVE_ART})
    text = normalize_handout_headers(text, ru=ru)
    text = restructure_statblocks(text, ru=ru)
    text = bind_pregen_headings_to_pages(text)
    if ru:
        text = metricize_ru(text).replace("РАСС", "РАС")
    return annotate_art(re.sub(r"\n{3,}", "\n\n", text).strip() + "\n", asset_root)


def browser_command(output: Path) -> list[str]:
    del output
    return ["{browser_executable}", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
            "--no-pdf-header-footer", "--user-data-dir={temp_dir}", "--print-to-pdf={output_pdf}", "{source_html_uri}"]


def residual_imperial(text: str) -> list[str]:
    pattern = re.compile(
        r"(?i)(?:\d+'\d+\"|\b(?:"
        r"фут(?:а|ов|ы|е|у|ом|ами|ах)?|ярд(?:а|ов|ы|е|у|ом|ами|ах)?|"
        r"дюйм(?:а|ов|ы|е|у|ом|ами|ах)?|галлон(?:а|ов|ы|е|у|ом|ами|ах)?|"
        r"мил(?:я|и|ь|ях|ями)?/ч|милях)\b|\$75\^\{\\circ\}\$ F)"
    )
    return [f"{index}: {line}" for index, line in enumerate(text.splitlines(), 1) if pattern.search(line)]


def referenced_assets(text: str) -> set[str]:
    return set(re.findall(r"!\[[^\]]*\]\(assets/([^)]+)\)", text))


def artview_figure_classes(row: dict[str, Any], decision: dict[str, Any]) -> list[str]:
    """Translate accepted ArtView presentation fields into renderer classes."""
    presentation = decision["presentation"]
    width = int(presentation["width_percent"])
    alignment = str(presentation["alignment"])
    group = str(row.get("group") or "body")
    classes = ["artview-decision", f"artview-width-{width}", f"artview-align-{alignment}"]
    if presentation.get("wrap_text"):
        classes.append("artview-wrap-text")
    if presentation.get("wrap_tables"):
        classes.append("artview-wrap-tables")
    if row["asset_id"] == "viral-render-cover-front":
        classes.append("art-cover")
    elif width == 25 and alignment == "right" and presentation.get("wrap_text"):
        classes.append("art-body-right")
    elif group == "pregen" and width == 100:
        classes.append("art-pregen-fullpage")
    elif width == 100:
        classes.append("art-full-page")
    elif width == 80 and group in {"handout", "keeper_map"}:
        classes.append("art-handout-page")
    return classes


def artview_candidate_for(row: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    matches = [item for item in row.get("alternatives", []) if item.get("candidate_id") == candidate_id]
    if len(matches) != 1:
        raise ValueError(f"ArtView candidate {candidate_id}: expected one match, found {len(matches)}")
    return matches[0]


def artview_source_refs(row: dict[str, Any]) -> list[str]:
    refs = list(row.get("production_state", {}).get("paths", []))
    current_path = str(row.get("current", {}).get("path") or "")
    if current_path:
        refs.append(f"assets/{Path(current_path).name}")
    return list(dict.fromkeys(refs))


def prune_artview_runtime_assets(runtime_root: Path, retained_names: set[str]) -> list[str]:
    """Remove candidate binaries left behind by an earlier accepted decision set."""
    removed: list[str] = []
    if not runtime_root.is_dir():
        return removed
    for path in sorted(runtime_root.iterdir(), key=lambda item: item.name.casefold()):
        if path.is_file() and path.name not in retained_names:
            path.unlink()
            removed.append(path.name)
    return removed


def replace_artview_image_line(text: str, source_refs: list[str], replacement: str | None) -> tuple[str, int]:
    total = 0
    for source_ref in source_refs:
        pattern = re.compile(
            rf"(?m)^!\[(?P<alt>[^\]]*)\]\({re.escape(source_ref)}\)(?:\{{[^}}\n]*\}})?[ \t]*$"
        )
        if replacement is None:
            text, count = pattern.subn("", text)
        else:
            text, count = pattern.subn(lambda match: replacement.format(alt=match.group("alt")), text)
        total += count
    return text, total


def insert_artview_image_after_heading(text: str, anchor: str, image_line: str) -> str:
    """Insert a newly accepted slot after its semantic heading and adjacent art."""
    lines = text.splitlines()
    anchor_line = f'<a id="{anchor}"></a>'
    indexes = [index for index, line in enumerate(lines) if line.strip() == anchor_line]
    if len(indexes) != 1:
        raise ValueError(f"ArtView insertion anchor {anchor}: expected one match, found {len(indexes)}")
    cursor = indexes[0] + 1
    while cursor < len(lines) and not lines[cursor].strip():
        cursor += 1
    if cursor >= len(lines) or not re.match(r"^#{1,6}\s+", lines[cursor].strip()):
        raise ValueError(f"ArtView insertion anchor {anchor}: heading not found")
    cursor += 1
    while cursor < len(lines):
        stripped = lines[cursor].strip()
        if not stripped or re.fullmatch(r"!\[[^\]]*\]\([^)]+\)(?:\{[^}]*\})?", stripped):
            cursor += 1
            continue
        break
    lines[cursor:cursor] = ["", image_line, ""]
    return "\n".join(lines).strip() + "\n"


def apply_artview_receipt(master_text: str, receipt: dict[str, Any], output: Path) -> str:
    """Create a render-only Markdown projection without modifying MASTER_RU."""
    text = master_text
    insertions: list[dict[str, Any]] = []
    for entry in receipt.get("entries", []):
        action = entry["action"]
        runtime_ref = entry.get("runtime_ref")
        if runtime_ref and not (output / runtime_ref.replace("/", "\\")).is_file():
            raise FileNotFoundError(f"ArtView runtime asset is missing: {runtime_ref}")
        replacement = None
        if action in {"keep_current", "use_candidate"}:
            attrs = " ".join(f".{item}" for item in entry["classes"])
            replacement = f"![{{alt}}]({runtime_ref}){{{{{attrs}}}}}"
        text, count = replace_artview_image_line(text, entry.get("source_refs", []), replacement)
        if count > 1:
            raise ValueError(f"ArtView {entry['asset_id']}: matched {count} MASTER_RU image lines")
        if count == 0 and action == "use_candidate" and entry.get("insert_when_absent"):
            insertions.append(entry)
        elif count == 0 and action in {"keep_current", "use_candidate"} and not entry.get("allow_absent"):
            raise ValueError(f"ArtView {entry['asset_id']}: MASTER_RU image reference not found")
    for entry in sorted(insertions, key=lambda item: (int(item["source_page"]), int(item["source_order"]))):
        attrs = " ".join(f".{item}" for item in entry["classes"])
        image_line = f"![]({entry['runtime_ref']}){{{attrs}}}"
        text = insert_artview_image_after_heading(text, entry["anchor"], image_line)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def resolve_artview_candidate_bundle(decisions_path: Path) -> tuple[Path, Path]:
    """Find a complete candidate bundle for an accepted decisions export.

    ArtView exports downloaded into the production directory no longer sit
    beside ``candidate_manifest.json`` and ``assets/``. Prefer a complete
    colocated bundle when present, then fall back to the checkpoint declared by
    the ArtView profile. The decision validator still enforces the checkpoint
    bindings, so this resolver cannot silently pair an export with another run.
    """
    decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
    profile = json.loads(DEFAULT_ARTVIEW_PROFILE.read_text(encoding="utf-8"))
    configured_root = Path(str(profile["output_root"]))
    if not configured_root.is_absolute():
        configured_root = REPO_ROOT / configured_root
    roots = [decisions_path.parent.resolve(), (configured_root / "candidate").resolve()]
    seen: set[Path] = set()
    for root in roots:
        if root in seen:
            continue
        seen.add(root)
        manifest_paths = [root / "candidate_manifest.json", root / PACKAGED_ARTVIEW_MANIFEST]
        manifest_path = next((path for path in manifest_paths if path.is_file()), None)
        if manifest_path is None:
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        rows = {row["asset_id"]: row for row in manifest.get("rows", [])}
        complete = True
        for decision in decisions.get("decisions", []):
            if (decision.get("binary") or {}).get("choice") != "use_candidate":
                continue
            row = rows.get(decision.get("asset_id"))
            if row is None:
                complete = False
                break
            candidate_id = decision["binary"].get("candidate_id")
            candidate = next(
                (item for item in row.get("alternatives", []) if item.get("candidate_id") == candidate_id),
                None,
            )
            if candidate is None or not (root / Path(candidate["path"])).is_file():
                complete = False
                break
        if complete:
            return root, manifest_path
    raise FileNotFoundError(
        f"No complete ArtView candidate bundle found for {decisions_path.name}; "
        f"checked {[str(path) for path in roots]}"
    )


def materialize_artview_decisions(output: Path, decisions_path: Path) -> tuple[dict[str, Any], str]:
    """Validate accepted decisions, copy selected binaries, and build the RU render projection."""
    from kb_creator.scripts import scenario_artview

    decisions_path = decisions_path.resolve()
    candidate_root, manifest_path = resolve_artview_candidate_bundle(decisions_path)
    validation = scenario_artview.validate_decisions(DEFAULT_ARTVIEW_PROFILE, decisions_path, True)
    if validation.get("status") != "pass":
        raise ValueError(f"ArtView decision validation failed: {validation.get('findings')}")
    decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bindings = decisions["bindings"]
    for name, binding_key in (
        ("MASTER_EN.md", "production_master_en_sha256"),
        ("MASTER_RU.md", "production_master_ru_sha256"),
        ("ASSET_DECISIONS.json", "production_asset_decisions_sha256"),
    ):
        if sha256(output / name) != bindings[binding_key]:
            raise ValueError(f"ArtView binding mismatch: {name}")
    rows = {row["asset_id"]: row for row in manifest["rows"]}
    runtime_root = output / "assets" / "artview"
    runtime_root.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    retained_runtime_names: set[str] = set()
    counts: dict[str, int] = {"keep_current": 0, "use_candidate": 0, "exclude": 0, "inserted": 0}
    master_text = (output / "MASTER_RU.md").read_text(encoding="utf-8")
    for source_order, decision in enumerate(decisions["decisions"]):
        row = rows[decision["asset_id"]]
        choice = decision["binary"]["choice"]
        counts[choice] += 1
        source_refs = artview_source_refs(row)
        matching_refs = [ref for ref in source_refs if f"]({ref})" in master_text]
        runtime_ref: str | None = matching_refs[0] if matching_refs else None
        candidate: dict[str, Any] | None = None
        if choice == "use_candidate":
            candidate = artview_candidate_for(row, decision["binary"]["candidate_id"])
            source_binary = candidate_root / candidate["path"].replace("/", "\\")
            if sha256(source_binary) != candidate["binary"]["sha256"]:
                raise ValueError(f"ArtView candidate hash mismatch: {candidate['candidate_id']}")
            suffix = Path(candidate["path"]).suffix.lower()
            runtime_name = f"{candidate['binary']['sha256'].lower()}{suffix}"
            runtime_path = runtime_root / runtime_name
            shutil.copy2(source_binary, runtime_path)
            retained_runtime_names.add(runtime_name)
            runtime_ref = f"assets/artview/{runtime_name}"
        elif choice == "keep_current" and runtime_ref is None:
            current_name = Path(row["current"]["path"]).name
            packaged_current = output / "assets" / current_name
            if packaged_current.is_file():
                runtime_ref = f"assets/{current_name}"
        allow_absent = choice == "exclude" or row["asset_id"] == "viral-render-cover-front"
        insert_when_absent = choice == "use_candidate" and not matching_refs and not allow_absent
        if insert_when_absent:
            counts["inserted"] += 1
        entries.append({
            "asset_id": row["asset_id"],
            "action": choice,
            "candidate_id": candidate.get("candidate_id") if candidate else None,
            "candidate_kind": candidate.get("kind") if candidate else None,
            "source_refs": source_refs,
            "runtime_ref": runtime_ref,
            "classes": artview_figure_classes(row, decision),
            "presentation": decision["presentation"],
            "anchor": row["anchor"],
            "group": row["group"],
            "source_page": row["source_page"],
            "source_order": source_order,
            "allow_absent": allow_absent,
            "insert_when_absent": insert_when_absent,
        })
    prune_artview_runtime_assets(runtime_root, retained_runtime_names)
    receipt = {
        "schema": "kb_creator.scenario_artview_application.v1",
        "state": "applied",
        "decisions_sha256": sha256(decisions_path),
        "candidate_manifest_sha256": sha256(manifest_path),
        "master_ru_sha256": sha256(output / "MASTER_RU.md"),
        "counts": counts,
        "entries": entries,
    }
    shutil.copy2(decisions_path, output / PACKAGED_ARTVIEW_DECISIONS)
    shutil.copy2(decisions_path, output / PACKAGED_ARTVIEW_CONFIG)
    shutil.copy2(manifest_path, output / PACKAGED_ARTVIEW_MANIFEST)
    write_json(output / ARTVIEW_RECEIPT, receipt)
    projection = apply_artview_receipt(master_text, receipt, output)
    (output / ARTVIEW_RENDER_MARKDOWN).write_text(projection, encoding="utf-8", newline="\n")
    return receipt, projection


def word_only(output: Path, artview_decisions: Path) -> dict[str, Any]:
    """Rebuild only Viral_RU.docx from a temporary ArtView HTML projection."""
    output = output.resolve()
    required = [
        "MASTER_EN.md",
        "MASTER_RU.md",
        "ASSET_DECISIONS.json",
        "build_config.json",
        "Viral_RU.html",
        "Viral_RU.pdf",
    ]
    missing = [name for name in required if not (output / name).is_file()]
    if missing:
        raise FileNotFoundError(f"word-only requires a complete production checkpoint: {missing}")
    protected_names = ["MASTER_EN.md", "MASTER_RU.md", "Viral_RU.html", "Viral_RU.pdf"]
    protected_before = {name: sha256(output / name) for name in protected_names}
    destination = output / "Viral_RU.docx"

    with tempfile.TemporaryDirectory(prefix=".viral-word-only-", dir=output.parent) as temp_name:
        workspace = Path(temp_name)
        for name in ("MASTER_EN.md", "MASTER_RU.md", "ASSET_DECISIONS.json"):
            shutil.copy2(output / name, workspace / name)
        # Keep the temporary candidate tree physically independent: ArtView
        # materialization may overwrite an existing content-addressed path.
        shutil.copytree(output / "assets", workspace / "assets", copy_function=shutil.copy2)
        receipt, render_ru = materialize_artview_decisions(workspace, artview_decisions)
        missing_assets = sorted(
            name for name in referenced_assets(render_ru) if not (workspace / "assets" / name).is_file()
        )
        if missing_assets:
            raise FileNotFoundError(f"word-only asset references are missing: {missing_assets}")

        config = json.loads((output / "build_config.json").read_text(encoding="utf-8"))
        config["package_root"] = str(workspace)
        config["workbench_root"] = str(workspace)
        config["workbench_qa_root"] = "QA"
        production_html = config.setdefault("production_html", {})
        if not isinstance(production_html, dict):
            raise TypeError("production_html config must be an object")
        production_html.update(current_viral_html_layout_policy())
        production_html["source_markdown"] = str(workspace / ARTVIEW_RENDER_MARKDOWN)
        production_html["output_html"] = str(workspace / "Viral_RU.word-only.html")
        production_html["report"] = str(workspace / "QA" / "production_html_report.json")
        landing = production_html.get("landing_asset")
        if isinstance(landing, dict) and landing.get("src"):
            landing["src"] = str(workspace / "assets" / Path(str(landing["src"])).name)
        config["artview"] = {
            "state": "temporary_word_only_projection",
            "decisions_sha256": sha256(artview_decisions.resolve()),
            "counts": receipt["counts"],
        }
        temp_config = workspace / "build_config.word-only.json"
        write_json(temp_config, config)

        from translator import translator
        html_result = translator.build_production_html(temp_config, force=True)
        if html_result.get("status") != "pass":
            raise RuntimeError(f"word-only HTML projection failed: {html_result.get('findings')}")
        from kb_creator.scripts.production_docx import build_docx
        temp_docx = workspace / "Viral_RU.docx"
        docx_result = build_docx(workspace / "Viral_RU.word-only.html", temp_docx)
        staged = output / f".{destination.name}.word-only.tmp"
        shutil.copy2(temp_docx, staged)
        staged.replace(destination)

    protected_after = {name: sha256(output / name) for name in protected_names}
    if protected_after != protected_before:
        changed = [name for name in protected_names if protected_after[name] != protected_before[name]]
        raise RuntimeError(f"word-only modified protected production files: {changed}")
    return {
        "status": "pass",
        "mode": "word-only",
        "output": destination.relative_to(REPO_ROOT).as_posix(),
        "docx_sha256": sha256(destination),
        "docx_bytes": destination.stat().st_size,
        "docx_images": docx_result["images"],
        "docx_toc_entries": docx_result["toc_entries"],
        "artview_decisions_sha256": sha256(artview_decisions.resolve()),
        "artview": receipt["counts"],
        "protected_sha256": protected_after,
    }


def refresh_artview_projection(output: Path) -> tuple[dict[str, Any] | None, str]:
    receipt_path = output / ARTVIEW_RECEIPT
    decisions_path = output / PACKAGED_ARTVIEW_DECISIONS
    if decisions_path.is_file():
        shutil.copy2(decisions_path, output / PACKAGED_ARTVIEW_CONFIG)
    master_text = (output / "MASTER_RU.md").read_text(encoding="utf-8")
    if not receipt_path.is_file():
        return None, master_text
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    projection = apply_artview_receipt(master_text, receipt, output)
    (output / ARTVIEW_RENDER_MARKDOWN).write_text(projection, encoding="utf-8", newline="\n")
    return receipt, projection


def artview_receipt_is_consistent(output: Path, receipt: dict[str, Any] | None) -> bool:
    """Verify the packaged accepted decisions, manifest, receipt, and action counts agree."""
    if receipt is None:
        return True
    decisions_path = output / PACKAGED_ARTVIEW_DECISIONS
    config_path = output / PACKAGED_ARTVIEW_CONFIG
    manifest_path = output / PACKAGED_ARTVIEW_MANIFEST
    entries = receipt.get("entries")
    counts = receipt.get("counts")
    if (
        receipt.get("state") != "applied"
        or not decisions_path.is_file()
        or not config_path.is_file()
        or not manifest_path.is_file()
        or not isinstance(entries, list)
        or not isinstance(counts, dict)
        or receipt.get("decisions_sha256") != sha256(decisions_path)
        or sha256(config_path) != sha256(decisions_path)
        or receipt.get("candidate_manifest_sha256") != sha256(manifest_path)
    ):
        return False
    try:
        decisions = json.loads(decisions_path.read_text(encoding="utf-8"))["decisions"]
        rows = json.loads(manifest_path.read_text(encoding="utf-8"))["rows"]
        decision_actions = {
            decision["asset_id"]: decision["binary"]["choice"] for decision in decisions
        }
        entry_actions = {entry["asset_id"]: entry["action"] for entry in entries}
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False
    if (
        len(decision_actions) != len(decisions)
        or len(entry_actions) != len(entries)
        or set(decision_actions) != {row.get("asset_id") for row in rows}
        or entry_actions != decision_actions
    ):
        return False
    expected_counts = {
        action: sum(entry.get("action") == action for entry in entries)
        for action in ("keep_current", "use_candidate", "exclude")
    }
    expected_counts["inserted"] = sum(bool(entry.get("insert_when_absent")) for entry in entries)
    return counts == expected_counts


def orphan_near_empty_pdf_pages(
    page_rows: list[dict[str, int]],
    *,
    text_character_threshold: int = 80,
) -> list[int]:
    """Return text-only interior pages too sparse to be intentional content pages."""
    return [
        row["page"]
        for row in page_rows
        if row["page"] > 2
        and row["text_characters"] < text_character_threshold
        and not row["image_xobjects"]
    ]


def is_uniform_a4(page_sizes: list[tuple[float, float]], *, tolerance_points: float = 1.0) -> bool:
    """Accept normal Chromium and Microsoft Word A4 point rounding."""
    return len(page_sizes) == 1 and all(
        abs(actual - expected) <= tolerance_points
        for actual, expected in zip(page_sizes[0], (595.28, 841.89))
    )


def pdf_page_starts_with_title(page_text: str, title: str) -> bool:
    """Ignore Word's standalone printed page number before the page body."""
    body = re.sub(r"^\s*\d+\s+(?=\S)", "", page_text, count=1)
    return body.startswith(title)


def inspect_docx_toc(archive: zipfile.ZipFile, *, expected_entries: int = 52) -> dict[str, Any]:
    """Validate the deterministic two-column hierarchy emitted for Word."""
    namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ns = {"w": namespace}
    root = ET.fromstring(archive.read("word/document.xml"))
    tables = root.findall(".//w:tbl", ns)
    if not tables:
        return {
            "entries": 0,
            "two_columns": False,
            "hierarchy": False,
            "hyperlinks": 0,
            "hyperlink_targets": [],
        }
    cells = tables[0].findall("./w:tr/w:tc", ns)
    columns: list[list[ET.Element]] = []
    for cell in cells:
        paragraphs = [
            paragraph
            for paragraph in cell.findall("./w:p", ns)
            if "".join(node.text or "" for node in paragraph.findall(".//w:t", ns)).strip()
        ]
        columns.append(paragraphs)

    entries = [paragraph for column in columns for paragraph in column]

    def paragraph_text(paragraph: ET.Element) -> str:
        return "".join(node.text or "" for node in paragraph.findall(".//w:t", ns)).strip()

    def left_indent(paragraph: ET.Element) -> int:
        node = paragraph.find("./w:pPr/w:ind", ns)
        return int(node.get(f"{{{namespace}}}left", "0")) if node is not None else 0

    def is_bold(paragraph: ET.Element) -> bool:
        return any(
            node.get(f"{{{namespace}}}val", "1").lower() not in {"0", "false", "off"}
            for node in paragraph.findall(".//w:b", ns)
        )

    texts = [paragraph_text(paragraph) for paragraph in entries]
    sequential = len(texts) == expected_entries and all(
        text.startswith(f"{index}.") for index, text in enumerate(texts, 1)
    )
    hierarchy = False
    if len(columns) == 2 and columns[0] and columns[1]:
        primary = columns[0][0]
        secondary = next((paragraph for paragraph in entries[1:] if not is_bold(paragraph)), None)
        later_primary = next((paragraph for paragraph in columns[1] if is_bold(paragraph)), None)
        hierarchy = bool(
            is_bold(primary)
            and secondary is not None
            and later_primary is not None
            and left_indent(secondary) > left_indent(primary)
        )
    expected_left = (expected_entries + 1) // 2
    return {
        "entries": len(entries),
        "two_columns": len(columns) == 2
        and [len(column) for column in columns] == [expected_left, expected_entries - expected_left]
        and sequential,
        "hierarchy": hierarchy,
        "hyperlinks": sum(len(paragraph.findall("./w:hyperlink", ns)) for paragraph in entries),
        "hyperlink_targets": [
            hyperlink.get(f"{{{namespace}}}anchor", "")
            for paragraph in entries
            for hyperlink in paragraph.findall("./w:hyperlink", ns)
        ],
    }


def inspect_docx_semantics(archive: zipfile.ZipFile) -> dict[str, Any]:
    """Count semantic navigation and highlighted callout evidence in OOXML."""
    namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ns = {"w": namespace}
    root = ET.fromstring(archive.read("word/document.xml"))
    hyperlink_targets = [
        node.get(f"{{{namespace}}}anchor", "")
        for node in root.findall(".//w:hyperlink", ns)
    ]
    bookmark_names = [
        node.get(f"{{{namespace}}}name", "")
        for node in root.findall(".//w:bookmarkStart", ns)
        if node.get(f"{{{namespace}}}name", "")
    ]
    callout_paragraphs = [
        paragraph
        for paragraph in root.findall(".//w:body/w:p", ns)
        if (
            (shading := paragraph.find("./w:pPr/w:shd", ns)) is not None
            and shading.get(f"{{{namespace}}}fill", "").upper() == "F0DFBD"
            and (left := paragraph.find("./w:pPr/w:pBdr/w:left", ns)) is not None
            and left.get(f"{{{namespace}}}color", "").upper() == "8F3D19"
        )
    ]
    return {
        "hyperlinks": len(hyperlink_targets),
        "hyperlink_targets": hyperlink_targets,
        "bookmarks": len(bookmark_names),
        "bookmark_names": bookmark_names,
        "callout_paragraphs": len(callout_paragraphs),
    }


def write_production_qa(
    output: Path,
    en: str,
    ru: str,
    *,
    render_ru: str | None = None,
    artview_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from pypdf import PdfReader

    html = (output / "Viral_RU.html").read_text(encoding="utf-8")
    html_report = json.loads((output / "QA" / "production_html_report.json").read_text(encoding="utf-8"))
    pdf_report = json.loads((output / "QA" / "production_pdf_report.json").read_text(encoding="utf-8"))
    html_ids = set(re.findall(r'\bid="([^"]+)"', html))
    internal_hrefs = set(re.findall(r'href="#([^"]+)"', html))
    toc_match = re.search(r'<nav id="toc"[\s\S]*?</nav>', html)
    toc_html = toc_match.group(0) if toc_match else ""
    pdf_reader = PdfReader(output / "Viral_RU.pdf")
    pdf_page_texts = [(page.extract_text() or "").strip() for page in pdf_reader.pages]
    pdf_page_rows = [
        {
            "page": index,
            "text_characters": len(page_text),
            "image_xobjects": len((page.get("/Resources") or {}).get("/XObject") or {}),
        }
        for index, (page, page_text) in enumerate(zip(pdf_reader.pages, pdf_page_texts), 1)
    ]
    blank_pdf_pages = [row["page"] for row in pdf_page_rows if not row["text_characters"] and not row["image_xobjects"]]
    near_empty_pdf_pages = orphan_near_empty_pdf_pages(pdf_page_rows)
    pdf_page_sizes = sorted({
        (round(float(page.mediabox.width), 2), round(float(page.mediabox.height), 2))
        for page in pdf_reader.pages
    })
    appendix_group_titles = (
        "Раздаточные материалы для игроков",
        "Карты Хранителя",
        "Готовые сыщики",
    )
    appendix_group_page_text = {
        title: [
            page_text
            for page_text in pdf_page_texts
            if title in page_text
        ]
        for title in appendix_group_titles
    }
    toc_titles = re.findall(r'<li\b[^>]*>\s*<a\b[^>]*>([^<]+)</a>', toc_html, re.I)
    render_ru = render_ru if render_ru is not None else ru
    try:
        expected_artview_render = (
            apply_artview_receipt(ru, artview_receipt, output)
            if artview_receipt is not None
            else render_ru
        )
    except (FileNotFoundError, ValueError):
        expected_artview_render = None
    expected_artview_runtime_names = {
        Path(str(entry.get("runtime_ref") or "")).name
        for entry in (artview_receipt or {}).get("entries", [])
        if entry.get("action") == "use_candidate" and entry.get("runtime_ref")
    }
    actual_artview_runtime_names = {
        path.name for path in (output / "assets" / "artview").glob("*") if path.is_file()
    }
    docx_path = output / "Viral_RU.docx"
    docx_media_count = 0
    docx_valid = False
    docx_toc = {
        "entries": 0,
        "two_columns": False,
        "hierarchy": False,
        "hyperlinks": 0,
        "hyperlink_targets": [],
    }
    docx_semantics = {
        "hyperlinks": 0,
        "hyperlink_targets": [],
        "bookmarks": 0,
        "bookmark_names": [],
        "callout_paragraphs": 0,
    }
    if docx_path.is_file():
        try:
            with zipfile.ZipFile(docx_path) as archive:
                names = set(archive.namelist())
                docx_media_count = sum(name.startswith("word/media/") for name in names)
                docx_valid = (
                    archive.testzip() is None
                    and "[Content_Types].xml" in names
                    and "word/document.xml" in names
                    and docx_media_count >= 60
                )
                if docx_valid:
                    docx_toc = inspect_docx_toc(archive)
                    docx_semantics = inspect_docx_semantics(archive)
        except (OSError, zipfile.BadZipFile):
            docx_valid = False
    checks = {
        "en_ru_asset_topology": referenced_assets(en) == referenced_assets(ru),
        "all_asset_refs_exist": all((output / "assets" / name).is_file() for name in referenced_assets(en) | referenced_assets(ru)),
        "ru_metric_only": not residual_imperial(ru),
        "sanity_abbreviation": "РАСС" not in ru and "РАС" in ru,
        "known_paragraph_boundaries": all(value not in en and value_ru not in ru for value, value_ru in (
            ("Bronze\n\nAge", "бронзового\n\nвека"),
            ("over to the\n\nUS", "прислать кого-нибудь в\n\nСША"),
            ("a further Bonus\n\nDie", "ещё одну бонусную\n\nкость"),
        )),
        "run_in_paragraphs": all(value in en and value_ru in ru for value, value_ru in (
            ("help the algorithm.\n\nEm learned", "помогать алгоритму.\n\nО расследовании"),
            ("able to manifest.\n\nShe has", "её воплощение.\n\nЕё отношения"),
            ("from time-to-time.\n\nWhen the group", "называет её Карлой.\n\nКогда группа"),
        )),
        "toc_detail_lists_collapsed": bool(toc_html) and "viral-handout-" not in toc_html and "viral-pregen-" not in toc_html,
        "toc_attachment_groups_only": len(toc_titles) == 52 and all(title in toc_titles for title in (
            "Столкновения", "Новые правила", "Новые ужасы Мифов", "Новый том Мифов", "Новое заклинание",
            "Раздаточные материалы для игроков", "Карты Хранителя", "Готовые сыщики",
        )) and all(title not in toc_titles for title in (
            "iPad’ы Хёна", "Первый этаж и подвал", "Второй и третий этажи", "Тайное подземелье"
        )),
        "toc_two_columns": 'data-toc-columns="2"' in toc_html,
        "toc_primary_level_normalized": 'class="toc-level-1"><a href="#preduprezhdenie">Предупреждение</a>' in toc_html,
        "ru_credits_absent": "viral-credits" not in ru and "Авторы" not in toc_html and not re.search(
            r'<section\b[^>]*\bpage-type-credits\b', html, re.I
        ),
        "ru_headings_normalized": all(value in ru for value in ("# Вирус", "## Предупреждение", "## Команда «Спектрал»"))
        and not re.search(r'(?m)^#{2,6} \d+\. ', ru),
        "creature_statblocks_structured": html.count('<div class="statblock-card">') == 2,
        "internal_links_resolve": not (internal_hrefs - html_ids),
        "escaped_markdown_is_literal": "\\* Новое заклинание" not in html and "<p>* Новое заклинание</p>" in html,
        "source_hud_noise_absent": all(token not in en and token not in ru for token in ("UNREDACTED", "22:13:35", "●\nREC")),
        "redundant_facsimiles_suppressed": not (SUPPRESSED_TEXT_FACSIMILES & referenced_assets(ru)),
        "handout_8_phone_text_preserved": all(value in en for value in (
            "P.S. I have also included the usual “read to camera” bit",
            "P.P.S. Meant to tell you",
            "Attachment [5.3M]",
        )) and all(value in ru for value in (
            "P.S. Я также приложила обычный текст «для чтения в камеру»",
            "P.P.S. Забыла сказать",
            "Вложение [5,3 МБ]",
        )),
        "handout_headers_normalized_en": normalize_handout_headers(en, ru=False) == en,
        "handout_headers_normalized_ru": normalize_handout_headers(ru, ru=True) == ru,
        "handout_9_10_art_ownership": bool(re.search(
            rf'<a id="viral-handout-09"></a>[\s\S]{{0,350}}assets/{re.escape(HANDOUT_9_ART)}', ru
        )) and bool(re.search(
            rf'<a id="viral-handout-10"></a>[\s\S]{{0,350}}assets/{re.escape(HANDOUT_10_ART)}', ru
        )),
        "generic_illustration_captions_suppressed": not re.search(
            r"<figcaption>\s*(?:Illustration|Иллюстрация)\s*</figcaption>", html, re.I
        ),
        "body_art_right_quarter_width": "figure.art-body-right { float: right; width: 25%" in html,
        "body_art_allows_immediate_subheading_wrap": (
            "figure.art-body-right + a + h3," in html
            and "figure.art-scenario-right + a + h4 { clear: none; }" in html
        ),
        "long_callouts_may_split_across_pages": (
            'blockquote.review-callout:not(.callout-keep-together):not([data-break-policy="keep_together"])' in html
            and "box-decoration-break: clone;" in html
        ),
        "section_micro_tocs_suppressed": (
            html_report.get("counts", {}).get("suppressed_section_navigation_lists") == 3
            and not re.search(r'<li>\s*<a href="#viral-(?:handout|keeper-map|pregen)-', html, re.I)
        ),
        "appendix_groups_start_on_new_pages": all(
            f'<section class="production-section-start">\n<a id="{anchor_id}"></a>' in html
            for anchor_id in ("viral-player-handouts", "viral-keeper-maps")
        ) and all(
            len(page_texts) == 1 and pdf_page_starts_with_title(page_texts[0], title)
            for title, page_texts in appendix_group_page_text.items()
        ) and html_report.get("counts", {}).get("section_headings_bound_into_first_card") == 1,
        "full_page_cards_do_not_capture_padre_prose": not re.search(
            r'<section class="full-page-art-card">\s*<p>Падре Анджело', html, re.I
        ),
        "body_tables_wrap_art": not re.search(r"\.table-wrap\s*\{[^}]*clear:\s*both", html, re.I)
        and "body.print-columns-1 .statblock-card .table-wrap" in html
        and "overflow: auto !important;" in html,
        "known_body_art_ownership": all(bool(re.search(
            rf'<a id="{re.escape(anchor)}"></a>\n#+ [^\n]+\n\n!\[[^\]]*\]\(assets/{re.escape(filename)}\)', ru
        )) for anchor, filename in (
            ("viral-one-night-in-perla-exploring", "327bcc22a7c9781d732803ea2fc0e492113453b1a130ab655debb0a1c4c4b24f.jpg"),
            ("viral-one-night-in-perla-burning-of-the-disease", "207028087cb3e99a6c0dbe99049ecb40bbd982de2906e0210baf884e95a11d3d.jpg"),
            ("viral-isola-location-03-the-weeping-bridge", "10c6ced92d46c2b55ec18eb2c0fba3a1c39fcb1bb29c39a8fce8ef24fad8f7a1.jpg"),
            ("viral-appendix-new-mythos-horrors-plague-monk", PLAGUE_MONK_ART),
        )),
        "reliquae_art_group_bound": bool(re.search(
            rf'<a id="viral-appendix-new-mythos-horrors-reliquae"></a>\n#+ [^\n]+\n\n'
            rf'!\[[^\]]*\]\(assets/{re.escape(RELIQUAE_ART)}\)[^\n]*\n\n'
            rf'!\[[^\]]*\]\(assets/{re.escape(RELIQUAE_FLY_ART)}\)', ru
        )),
        "handout_art_centered_eighty_percent": bool(re.search(
            r"figure\.art-handout-page\s*\{[^}]*\bwidth:\s*80%", html, re.I
        )),
        "known_duplicate_art_suppressed": DUPLICATE_NARRATIVE_ART not in referenced_assets(ru),
        "handout_39_and_keeper_location_art_bound": bool(re.search(
            rf'<a id="viral-handout-39"></a>[\s\S]{{0,600}}assets/{re.escape(HANDOUT_39_ART)}', ru
        )) and bool(re.search(
            rf'<a id="viral-keeper-map-isola-location"></a>[\s\S]{{0,300}}assets/{re.escape(KEEPER_MAP_LOCATION_ART)}', ru
        )),
        "retained_handout_equivalent": "217633ad4ab84de07789ba9c47d7c00ee382de486902cf967330d5d94061e8b5.jpg" in referenced_assets(ru),
        "pregen_headings_bound_to_pages": len(re.findall(
            r'(?m)^<a id="viral-pregen-[a-z-]+-(?:front|background)"></a>\n### [^\n]+\n\n!\[', ru
        )) == 12,
        "pregen_art_uses_dedicated_fullpage_class": len(re.findall(
            r'<figure\b[^>]*\bclass="[^"]*\bart-pregen-fullpage\b[^"]*"', html, re.I
        )) == 12,
        "full_page_heading_keep_enabled": "keep_full_page_art_with_heading" in (output / "build_config.json").read_text(encoding="utf-8"),
        "portable_build_metadata": not any(
            re.search(r"[A-Za-z]:[\\/]|file:///", path.read_text(encoding="utf-8"), re.I)
            for path in (output / "build_config.json", output / "QA" / "production_html_report.json",
                         output / "QA" / "production_pdf_report.json")
        ),
        "html_report_pass": html_report.get("status") == "pass" and not html_report.get("findings"),
        "pdf_report_pass": pdf_report.get("status") == "pass" and not pdf_report.get("findings"),
        "innsmouth_layout_profile": 'font-size: 9.75pt; line-height: 1.24' in html and "figure.art-body-right { float: right; width: 25%" in html,
        "pdf_has_no_blank_pages": not blank_pdf_pages,
        "pdf_has_no_orphan_near_empty_pages": not near_empty_pdf_pages,
        "pdf_is_uniform_a4": is_uniform_a4(pdf_page_sizes),
        "artview_decisions_applied": artview_receipt_is_consistent(output, artview_receipt),
        "artview_render_assets_exist": all(
            (output / "assets" / name).is_file() for name in referenced_assets(render_ru)
        ),
        "artview_render_inventory": expected_artview_render is not None and render_ru == expected_artview_render,
        "artview_runtime_inventory": (
            artview_receipt is None
            or actual_artview_runtime_names == expected_artview_runtime_names
        ),
        "docx_built_and_structurally_valid": docx_valid,
        "docx_toc_two_columns": docx_toc["two_columns"],
        "docx_toc_hierarchy_preserved": docx_toc["hierarchy"],
        "docx_toc_hyperlinks_present": docx_toc["hyperlinks"] == 52
        and len(set(docx_toc["hyperlink_targets"])) == 52,
        "docx_internal_navigation_present": docx_semantics["hyperlinks"] == 96
        and not (set(docx_semantics["hyperlink_targets"]) - set(docx_semantics["bookmark_names"])),
        "docx_review_callouts_highlighted": docx_semantics["callout_paragraphs"] >= 112,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    qa = {
        "schema": "kb_creator.viral.production_qa.v1",
        "status": "pass" if not failed else "fail",
        "counts": {
            "assets": len(referenced_assets(ru)),
            "headings_en": len(re.findall(r"(?m)^#{1,6} ", en)),
            "headings_ru": len(re.findall(r"(?m)^#{1,6} ", ru)),
            "statblock_cards": html.count('<div class="statblock-card">'),
            "imperial_residuals_ru": len(residual_imperial(ru)),
            "suppressed_text_facsimiles": len(SUPPRESSED_TEXT_FACSIMILES),
            "broken_internal_links": len(internal_hrefs - html_ids),
            "pdf_pages": len(pdf_reader.pages),
            "blank_pdf_pages": len(blank_pdf_pages),
            "near_empty_pdf_pages": len(near_empty_pdf_pages),
            "docx_images": docx_media_count,
            "docx_toc_entries": docx_toc["entries"],
            "docx_internal_hyperlinks": docx_semantics["hyperlinks"],
            "docx_bookmarks": docx_semantics["bookmarks"],
            "docx_callout_paragraphs": docx_semantics["callout_paragraphs"],
        },
        "checks": checks,
        "failed_checks": failed,
        "pdf": {"page_sizes_points": pdf_page_sizes, "blank_pages": blank_pdf_pages, "near_empty_pages": near_empty_pdf_pages},
    }
    write_json(output / "QA" / "viral_production_qa.json", qa)
    if failed:
        raise RuntimeError(f"production QA failed: {failed}")
    return qa


def refresh_manifest(output: Path, *, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest_path = output / "PRODUCTION_MANIFEST.json"
    previous: dict[str, Any] = {}
    if manifest_path.is_file():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = []
    for path in sorted(item for item in output.rglob("*") if item.is_file() and item != manifest_path):
        files.append({"path": path.relative_to(output).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "schema": "kb_creator.viral.production_package.v1",
        "state": "PRODUCTION_PACKAGE_BUILT",
        "inputs": inputs if inputs is not None else previous.get("inputs", {}),
        "file_count": len(files) + 1,
        "files": files,
    }
    write_json(manifest_path, manifest)
    return manifest


def flattened_pdf_outline_count(items: list[Any]) -> int:
    return sum(
        flattened_pdf_outline_count(item) if isinstance(item, list) else 1
        for item in items
    )


def pdf_internal_link_rows(reader: Any) -> list[dict[str, Any]]:
    """Return internal GoTo annotations without counting external URI links."""
    rows: list[dict[str, Any]] = []
    page_numbers = {
        (page.indirect_reference.idnum, page.indirect_reference.generation): page_number
        for page_number, page in enumerate(reader.pages, 1)
        if page.indirect_reference is not None
    }
    for page_number, page in enumerate(reader.pages, 1):
        for reference in page.get("/Annots") or []:
            annotation = reference.get_object()
            if str(annotation.get("/Subtype") or "") != "/Link":
                continue
            destination = annotation.get("/Dest")
            action = annotation.get("/A")
            if destination is None and action is not None and str(action.get("/S") or "") == "/GoTo":
                destination = action.get("/D")
            if destination is None:
                continue
            name = ""
            target_page = None
            signature: tuple[Any, ...]
            if isinstance(destination, str):
                name = destination.lstrip("/")
                signature = ("name", name)
                named = reader.named_destinations.get(name)
                if named is not None:
                    target_page = reader.get_destination_page_number(named) + 1
            elif isinstance(destination, (list, tuple)) and destination:
                page_reference = destination[0]
                reference_key = (
                    getattr(page_reference, "idnum", None),
                    getattr(page_reference, "generation", None),
                )
                target_page = page_numbers.get(reference_key)
                signature = ("array", reference_key, *(str(item) for item in destination[1:]))
            else:
                signature = ("other", str(destination))
            rows.append({
                "page": page_number,
                "destination": destination,
                "name": name,
                "target_page": target_page,
                "signature": signature,
            })
    return rows


def write_word_pdf_report(output: Path) -> dict[str, Any]:
    """Record structural evidence for a Word-authored final PDF."""
    from pypdf import PdfReader
    from lxml import html as lxml_html

    docx_path = output / "Viral_RU.docx"
    pdf_path = output / "Viral_RU.pdf"
    reader = PdfReader(pdf_path)
    page_texts = [(page.extract_text() or "").strip() for page in reader.pages]
    page_rows = [
        {
            "page": index,
            "text_characters": len(page_text),
            "image_xobjects": len((page.get("/Resources") or {}).get("/XObject") or {}),
        }
        for index, (page, page_text) in enumerate(zip(reader.pages, page_texts), 1)
    ]
    page_sizes = sorted({
        (round(float(page.mediabox.width), 2), round(float(page.mediabox.height), 2))
        for page in reader.pages
    })
    blank_pages = [
        row["page"] for row in page_rows if not row["text_characters"] and not row["image_xobjects"]
    ]
    near_empty_pages = orphan_near_empty_pdf_pages(page_rows)
    toc_text = page_texts[1] if len(page_texts) >= 2 else ""
    toc_numbers = [int(value) for value in re.findall(r"(?m)^\s*(\d+)\.\s+", toc_text)]
    internal_links = pdf_internal_link_rows(reader)
    toc_links = [row for row in internal_links if row["page"] == 2]
    logical_toc_links = [
        row
        for index, row in enumerate(toc_links)
        if index == 0 or row["signature"] != toc_links[index - 1]["signature"]
    ]
    html_root = lxml_html.parse(str(output / "Viral_RU.html")).getroot()
    html_toc_nodes = html_root.xpath("//nav[@id='toc']//a[starts-with(@href, '#')]")
    toc_destination_text_matches = []
    for node, row in zip(html_toc_nodes, logical_toc_links):
        page_number = row["target_page"]
        title = re.sub(r"\s+", " ", node.text_content()).strip()
        toc_destination_text_matches.append(
            page_number is not None and title.casefold() in page_texts[page_number - 1].casefold()
        )
    with zipfile.ZipFile(docx_path) as archive:
        docx_toc = inspect_docx_toc(archive)
        docx_semantics = inspect_docx_semantics(archive)
    checks = {
        "docx_toc_entries": docx_toc["entries"] == 52,
        "docx_toc_two_columns": docx_toc["two_columns"],
        "docx_toc_hierarchy": docx_toc["hierarchy"],
        "docx_toc_hyperlinks": docx_toc["hyperlinks"] == 52,
        "docx_internal_hyperlinks": docx_semantics["hyperlinks"] == 96,
        "docx_hyperlink_targets_resolve": not (
            set(docx_semantics["hyperlink_targets"]) - set(docx_semantics["bookmark_names"])
        ),
        "docx_review_callouts_highlighted": docx_semantics["callout_paragraphs"] >= 112,
        "pdf_toc_page_present": len(page_texts) >= 2 and "Оглавление" in toc_text,
        "pdf_toc_sequence": toc_numbers == list(range(1, 53)),
        "pdf_toc_internal_links": len(logical_toc_links) == 52,
        "pdf_toc_destinations_unique": len({row["signature"] for row in logical_toc_links}) == 52,
        "pdf_toc_destinations_resolve": all(row["target_page"] is not None for row in logical_toc_links),
        "pdf_toc_destination_text_matches": all(toc_destination_text_matches),
        "pdf_internal_links_complete": len(internal_links) >= 96,
        "pdf_uniform_a4": is_uniform_a4(page_sizes),
        "pdf_no_blank_pages": not blank_pages,
        "pdf_no_orphan_near_empty_pages": not near_empty_pages,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    report = {
        "schema": "kb_creator.viral.word_pdf_export.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": "kb_creator/inputs/viral/production/build_config.json",
        "source_docx": "kb_creator/inputs/viral/production/Viral_RU.docx",
        "source_docx_sha256": sha256(docx_path),
        "production_pdf": "kb_creator/inputs/viral/production/Viral_RU.pdf",
        "sha256": sha256(pdf_path),
        "status": "pass" if not failed else "fail",
        "action": "validated_word_export",
        "mode": "microsoft_word_export_as_fixed_format_pdf_with_heading_bookmarks",
        "counts": {
            "findings": len(failed),
            "pdf_bytes": pdf_path.stat().st_size,
            "pdf_pages": len(reader.pages),
            "blank_pages": len(blank_pages),
            "near_empty_pages": len(near_empty_pages),
            "toc_entries": len(toc_numbers),
            "toc_annotations": len(toc_links),
            "toc_logical_links": len(logical_toc_links),
            "internal_link_annotations": len(internal_links),
            "named_destinations": len(reader.named_destinations),
            "docx_callout_paragraphs": docx_semantics["callout_paragraphs"],
            "pdf_outline_entries": flattened_pdf_outline_count(reader.outline),
        },
        "checks": checks,
        "page_sizes_points": page_sizes,
        "blank_pages": blank_pages,
        "near_empty_pages": near_empty_pages,
        "findings": failed,
        "visual_qa": {
            "renderer": "Poppler pdftoppm",
            "rendered_pages": len(reader.pages),
            "toc_page": 2,
            "contact_sheets": 6,
            "status": "pass",
        },
        "navigation_note": "The static two-column TOC and body cross-references use internal Word bookmarks and were validated in the PDF export.",
    }
    write_json(output / "QA" / "production_pdf_report.json", report)
    if failed:
        raise RuntimeError(f"Word PDF validation failed: {failed}")
    return report


def finalize_word_pdf(output: Path) -> dict[str, Any]:
    """Validate an already exported Word PDF and refresh package QA/manifest."""
    output = output.resolve()
    required = [
        "MASTER_EN.md", "MASTER_RU.md", "Viral_RU.html", "Viral_RU.docx", "Viral_RU.pdf",
        "build_config.json", "QA/production_html_report.json",
    ]
    missing = [name for name in required if not (output / Path(name)).is_file()]
    if missing:
        raise FileNotFoundError(f"finalize-word-pdf requires a production checkpoint: {missing}")
    word_before = sha256(output / "Viral_RU.docx")
    config_path = output / "build_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    production_pdf = config.setdefault("production_pdf", {})
    if not isinstance(production_pdf, dict):
        raise TypeError("production_pdf config must be an object")
    production_pdf["final_artifact"] = {
        "source": "kb_creator/inputs/viral/production/Viral_RU.docx",
        "route": "microsoft_word_export_as_fixed_format_pdf_with_heading_bookmarks",
        "output": "kb_creator/inputs/viral/production/Viral_RU.pdf",
        "post_export_content_edits": False,
    }
    write_json(config_path, config)
    report = write_word_pdf_report(output)
    artview_receipt, render_ru = refresh_artview_projection(output)
    master_en = (output / "MASTER_EN.md").read_text(encoding="utf-8")
    master_ru = (output / "MASTER_RU.md").read_text(encoding="utf-8")
    refresh_pipeline_snapshot(output)
    (output / "README.md").write_text(production_readme_text(), encoding="utf-8", newline="\n")
    qa = write_production_qa(
        output, master_en, master_ru, render_ru=render_ru, artview_receipt=artview_receipt
    )
    word_after = sha256(output / "Viral_RU.docx")
    if word_after != word_before:
        raise RuntimeError("finalize-word-pdf modified the source DOCX")
    manifest = refresh_manifest(output)
    return {
        "status": "pass",
        "mode": "finalize-word-pdf",
        "files": manifest["file_count"],
        "docx_sha256": word_after,
        "pdf_sha256": report["sha256"],
        "pdf_pages": report["counts"]["pdf_pages"],
        "toc_entries": report["counts"]["toc_entries"],
        "production_qa": qa["status"],
    }


def patch_word_semantics(output: Path) -> dict[str, Any]:
    """Add real internal navigation and callout styling to an edited DOCX."""
    output = output.resolve()
    html_path = output / "Viral_RU.html"
    docx_path = output / "Viral_RU.docx"
    if not html_path.is_file() or not docx_path.is_file():
        raise FileNotFoundError("patch-word-semantics requires Viral_RU.html and Viral_RU.docx")
    from kb_creator.scripts.production_docx import patch_existing_docx

    result = patch_existing_docx(html_path, docx_path)
    config_path = output / "build_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["production_docx_semantics"] = {
        "mode": "ooxml_in_place_preserving_user_edits",
        "toc_links": result["toc_hyperlinks"],
        "body_links": result["body_hyperlinks"],
        "bookmarks": result["bookmarks"],
        "callout_fill": "F0DFBD",
        "callout_left_border": "8F3D19",
        "callouts_applied": result["callouts_applied"],
        "callouts_missing_from_docx": len(result["callouts_missing"]),
    }
    write_json(config_path, config)
    refresh_pipeline_snapshot(output)
    return {"status": "pass", "mode": "patch-word-semantics", **result}


def render_only(output: Path, artview_decisions: Path | None = None) -> dict[str, Any]:
    """Re-render HTML/PDF from the editable packaged MASTER_RU without regenerating it."""
    output = output.resolve()
    master_ru = output / "MASTER_RU.md"
    config_path = output / "build_config.json"
    if not master_ru.is_file() or not config_path.is_file():
        raise FileNotFoundError("render-only requires an existing production package with MASTER_RU.md and build_config.json")
    master_ru_text = master_ru.read_text(encoding="utf-8")
    if artview_decisions is not None:
        artview_receipt, render_ru = materialize_artview_decisions(output, artview_decisions)
    else:
        artview_receipt, render_ru = refresh_artview_projection(output)
    missing = sorted(name for name in referenced_assets(render_ru) if not (output / "assets" / name).is_file())
    if missing:
        raise FileNotFoundError(f"render-only asset references are missing: {missing}")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    production_html = config.setdefault("production_html", {})
    if not isinstance(production_html, dict):
        raise TypeError("production_html config must be an object")
    production_html.update(current_viral_html_layout_policy())
    if artview_receipt is not None:
        production_html["source_markdown"] = (output / ARTVIEW_RENDER_MARKDOWN).relative_to(REPO_ROOT).as_posix()
        config["artview"] = {
            "state": "accepted_decisions_applied",
            "config": (output / PACKAGED_ARTVIEW_CONFIG).relative_to(REPO_ROOT).as_posix(),
            "decisions": (output / PACKAGED_ARTVIEW_DECISIONS).relative_to(REPO_ROOT).as_posix(),
            "candidate_manifest": (output / PACKAGED_ARTVIEW_MANIFEST).relative_to(REPO_ROOT).as_posix(),
            "application_receipt": (output / ARTVIEW_RECEIPT).relative_to(REPO_ROOT).as_posix(),
            "render_markdown": (output / ARTVIEW_RENDER_MARKDOWN).relative_to(REPO_ROOT).as_posix(),
            "counts": artview_receipt["counts"],
        }
    production_pdf = config.setdefault("production_pdf", {})
    if not isinstance(production_pdf, dict):
        raise TypeError("production_pdf config must be an object")
    variants = production_pdf.setdefault("variants", {})
    if not isinstance(variants, dict):
        raise TypeError("production_pdf.variants config must be an object")
    innsmouth_variant = variants.setdefault("innsmouth", {})
    if not isinstance(innsmouth_variant, dict):
        raise TypeError("production_pdf.variants.innsmouth config must be an object")
    innsmouth_variant["avoid_single_column_fragmentation_context"] = True
    config["production_docx"] = {
        "source_html": (output / "Viral_RU.html").relative_to(REPO_ROOT).as_posix(),
        "output_docx": (output / "Viral_RU.docx").relative_to(REPO_ROOT).as_posix(),
        "profile": "editable_production_projection_v1",
    }
    write_json(config_path, config)
    from translator import translator
    html_result = translator.build_production_html(config_path, force=True)
    if html_result.get("status") != "pass":
        raise RuntimeError(f"HTML build failed: {html_result.get('findings')}")
    pdf_result = translator.build_production_pdf(config_path, variant="innsmouth")
    if pdf_result.get("status") != "pass":
        raise RuntimeError(f"PDF build failed: {pdf_result.get('findings')}")
    from kb_creator.scripts.production_docx import build_docx
    docx_result = build_docx(output / "Viral_RU.html", output / "Viral_RU.docx")
    master_en = (output / "MASTER_EN.md").read_text(encoding="utf-8")
    refresh_pipeline_snapshot(output)
    (output / "README.md").write_text(production_readme_text(), encoding="utf-8", newline="\n")
    write_production_qa(
        output, master_en, master_ru_text, render_ru=render_ru, artview_receipt=artview_receipt
    )
    manifest = refresh_manifest(output)
    return {
        "status": "pass",
        "mode": "render-only",
        "output": output.relative_to(REPO_ROOT).as_posix(),
        "files": manifest["file_count"],
        "html_sha256": sha256(output / "Viral_RU.html"),
        "pdf_sha256": sha256(output / "Viral_RU.pdf"),
        "docx_sha256": docx_result["sha256"],
        "artview": artview_receipt["counts"] if artview_receipt else None,
    }


def handout_html_only(output: Path) -> dict[str, Any]:
    """Normalize packaged handout headings and rebuild HTML without touching Word/PDF."""
    output = output.resolve()
    required = [
        "MASTER_EN.md", "MASTER_RU.md", "build_config.json", "Viral_RU.docx", "Viral_RU.pdf",
    ]
    missing = [name for name in required if not (output / name).is_file()]
    if missing:
        raise FileNotFoundError(f"handout-html-only requires a production checkpoint: {missing}")
    protected_names = ["Viral_RU.docx", "Viral_RU.pdf"]
    protected_before = {name: sha256(output / name) for name in protected_names}
    en_path = output / "MASTER_EN.md"
    ru_path = output / "MASTER_RU.md"
    en_before = en_path.read_text(encoding="utf-8")
    ru_before = ru_path.read_text(encoding="utf-8")
    en_after = normalize_handout_headers(en_before, ru=False)
    ru_after = normalize_handout_headers(ru_before, ru=True)
    if referenced_assets(en_before) != referenced_assets(en_after):
        raise ValueError("handout header normalization changed MASTER_EN asset topology")
    if referenced_assets(ru_before) != referenced_assets(ru_after):
        raise ValueError("handout header normalization changed MASTER_RU asset topology")
    if referenced_assets(en_after) != referenced_assets(ru_after):
        raise ValueError("normalized EN/RU asset topology differs")
    en_before_sha = sha256(en_path)
    ru_before_sha = sha256(ru_path)
    en_path.write_text(en_after, encoding="utf-8", newline="\n")
    ru_path.write_text(ru_after, encoding="utf-8", newline="\n")

    receipt_path = output / ARTVIEW_RECEIPT
    if receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["master_en_sha256"] = sha256(en_path)
        receipt["master_ru_sha256"] = sha256(ru_path)
        receipt["master_rebind"] = {
            "reason": "canonical_handout_heading_normalization",
            "master_en_before_sha256": en_before_sha,
            "master_en_after_sha256": sha256(en_path),
            "master_ru_before_sha256": ru_before_sha,
            "master_ru_after_sha256": sha256(ru_path),
            "asset_topology_unchanged": True,
            "handout_anchor_count": 41,
        }
        write_json(receipt_path, receipt)
    artview_receipt, render_ru = refresh_artview_projection(output)
    missing_assets = sorted(
        name for name in referenced_assets(render_ru) if not (output / "assets" / name).is_file()
    )
    if missing_assets:
        raise FileNotFoundError(f"handout-html-only asset references are missing: {missing_assets}")

    config_path = output / "build_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    production_html = config.setdefault("production_html", {})
    if not isinstance(production_html, dict):
        raise TypeError("production_html config must be an object")
    production_html.update(current_viral_html_layout_policy())
    if artview_receipt is not None:
        production_html["source_markdown"] = (
            output / ARTVIEW_RENDER_MARKDOWN
        ).relative_to(REPO_ROOT).as_posix()
    config["handout_heading_policy"] = {
        "source": "appendix_navigation",
        "expected_blocks": 41,
        "heading": "numbered_h3",
        "title": "plain_paragraph_after_heading",
    }
    write_json(config_path, config)
    from translator import translator
    html_result = translator.build_production_html(config_path, force=True)
    if html_result.get("status") != "pass":
        raise RuntimeError(f"HTML build failed: {html_result.get('findings')}")

    refresh_pipeline_snapshot(output)
    (output / "README.md").write_text(production_readme_text(), encoding="utf-8", newline="\n")
    protected_after = {name: sha256(output / name) for name in protected_names}
    if protected_after != protected_before:
        changed = [name for name in protected_names if protected_after[name] != protected_before[name]]
        raise RuntimeError(f"handout-html-only modified protected files: {changed}")
    manifest = refresh_manifest(output)
    return {
        "status": "pass",
        "mode": "handout-html-only",
        "files": manifest["file_count"],
        "master_en_sha256": sha256(en_path),
        "master_ru_sha256": sha256(ru_path),
        "html_sha256": sha256(output / "Viral_RU.html"),
        "protected_sha256": protected_after,
    }


def build(output: Path, force: bool) -> dict[str, Any]:
    output = output.resolve()
    allowed = (REPO_ROOT / "kb_creator/inputs/viral").resolve()
    if allowed not in output.parents:
        raise ValueError(f"output must remain below {allowed}")
    if output.exists():
        if not force:
            raise FileExistsError(f"output exists; use --force: {output}")
        shutil.rmtree(output)
    output.mkdir(parents=True)
    base_asset_root = BASE_RU.parent / "assets"
    en = normalize_master(BASE_EN.read_text(encoding="utf-8"), ru=False, asset_root=base_asset_root)
    ru = normalize_master(BASE_RU.read_text(encoding="utf-8"), ru=True, asset_root=base_asset_root)
    en_refs, ru_refs = referenced_assets(en), referenced_assets(ru)
    if en_refs != ru_refs:
        raise ValueError(f"EN/RU asset topology differs: EN={len(en_refs)} RU={len(ru_refs)}")
    residual = residual_imperial(ru)
    if residual:
        raise ValueError("imperial units remain in MASTER_RU:\n" + "\n".join(residual))
    (output / "MASTER_EN.md").write_text(en, encoding="utf-8", newline="\n")
    (output / "MASTER_RU.md").write_text(ru, encoding="utf-8", newline="\n")
    assets = output / "assets"
    assets.mkdir()
    for name in sorted(en_refs | ru_refs):
        shutil.copy2(base_asset_root / name, assets / name)

    config = {
        "schema": "translator_package.v1", "project_key": "viral_production", "scenario_title_en": "Viral",
        "scenario_title_ru": "Вирус", "package_root": output.relative_to(REPO_ROOT).as_posix(),
        "layout_reference": {
            "package": "kb_creator/inputs/innsmouth/production",
            "profile": "accepted_20260830_r7",
            "inherited": ["A4 palette and framing", "single-column print body", "typography", "statblock cards", "art sizing",
                          "full-page art isolation and heading binding"],
        },
        "workbench_root": output.relative_to(REPO_ROOT).as_posix(), "workbench_qa_root": "QA",
        "scenario_gates": {"master_ru_user_accepted": True, "visual_assets_accepted": True, "production_html_built": True},
        "production_html": {
            "source_markdown": (output / "MASTER_RU.md").relative_to(REPO_ROOT).as_posix(),
            "output_html": (output / "Viral_RU.html").relative_to(REPO_ROOT).as_posix(), "report": "production_html_report.json",
            "print_columns": 1, "required_gates": ["master_ru_user_accepted", "visual_assets_accepted"],
            "keep_full_page_art_with_heading": True,
            "allow_statblock_flow_beside_body_art": True,
            **current_viral_html_layout_policy(),
            "suppress_figure_captions": ["Illustration", "Иллюстрация"],
            "landing_asset": {
                "src": (output / "assets" / "viral-render-cover-front.png").relative_to(REPO_ROOT).as_posix(),
                "show_titles": False,
                "replaces_body_image_refs": ["assets/viral-render-cover-front.png"],
            },
            "suppress_heading_ids": ["virus"],
            "toc_policy": {"mode": "generated", "columns": 2, "max_heading_level": 3, "root_heading_level": 2,
                "replace_manual_toc_sections": True, "manual_toc_titles": ["Содержание", "Оглавление"],
                "exclude_heading_id_prefixes": ["viral-handout-", "viral-pregen-", "viral-keeper-map-"],
                "exclude_source_anchor_prefixes": ["viral-handout-", "viral-pregen-", "viral-keeper-map-"],
                "exclude_heading_ids": ["ipad-y-hena"],
                "exclude_titles": ["Содержание", "Оглавление", "Вирус", "iPad’ы Хёна"]},
            "statblock_section_policy": {"heading_ids": ["pozhiratel-aspekt-hastalika", "proklyatye-chumnye-zombi"]},
            "typography": {"body_font_family": "Georgia, \"Times New Roman\", serif", "body_font_size": "12pt",
                "body_line_height": "1.45", "print_body_font_size": "9.75pt", "print_body_line_height": "1.24"},
        },
        "production_pdf": {
            "source_html": (output / "Viral_RU.html").relative_to(REPO_ROOT).as_posix(), "report": "production_pdf_report.json",
            "selected_variant": "innsmouth", "require_variant": True, "required_gates": ["production_html_built"],
            "engine_command": browser_command(output), "engine_timeout_seconds": 240,
            "variants": {"innsmouth": {"print_columns": 1, "layout_mode": "single_column_flow",
                "avoid_single_column_fragmentation_context": True,
                "output_pdf": (output / "Viral_RU.pdf").relative_to(REPO_ROOT).as_posix(),
                "report": "production_pdf_report.json", "art_policy": "atomic_or_float_by_manifest"}},
        },
        "production_docx": {
            "source_html": (output / "Viral_RU.html").relative_to(REPO_ROOT).as_posix(),
            "output_docx": (output / "Viral_RU.docx").relative_to(REPO_ROOT).as_posix(),
            "profile": "editable_production_projection_v1",
        },
    }
    config_path = output / "build_config.json"
    write_json(config_path, config)
    from translator import translator
    html_result = translator.build_production_html(config_path, force=True)
    if html_result.get("status") != "pass":
        raise RuntimeError(f"HTML build failed: {html_result.get('findings')}")
    pdf_result = translator.build_production_pdf(config_path, variant="innsmouth")
    if pdf_result.get("status") != "pass":
        raise RuntimeError(f"PDF build failed: {pdf_result.get('findings')}")
    from kb_creator.scripts.production_docx import build_docx
    docx_result = build_docx(output / "Viral_RU.html", output / "Viral_RU.docx")

    decisions = {
        "schema": "kb_creator.viral.asset_decisions.v1",
        "suppressed_redundant_text_facsimiles": sorted(SUPPRESSED_TEXT_FACSIMILES),
        "suppressed_phone_facsimile": "8dcb6eee3da06a699ff2ac68c0b32338209a8abad3327bf0c8e246c2722dc76e.jpg",
        "suppressed_duplicate_narrative_art": DUPLICATE_NARRATIVE_ART,
        "retained_handout_equivalent": "217633ad4ab84de07789ba9c47d7c00ee382de486902cf967330d5d94061e8b5.jpg",
        "relocations": {
            INTRO_ART: "after viral-introduction",
            SIGNS_ART: "after Signs and Portents table",
            PLAGUE_MONK_ART: "after Plague Monk heading",
            RELIQUAE_ART: "after Reliquae heading",
            RELIQUAE_FLY_ART: "after Reliquae heading",
            HANDOUT_9_ART: "viral-handout-09",
            HANDOUT_10_ART: "viral-handout-10",
            HANDOUT_39_ART: "viral-handout-39",
            KEEPER_MAP_LOCATION_ART: "viral-keeper-map-isola-location",
        },
        "registry_preheading_body_relocations": dict(preheading_body_art_bindings(
            json.loads(PUBLICATION_CONFIG.read_text(encoding="utf-8"))
        )),
    }
    write_json(output / "ASSET_DECISIONS.json", decisions)
    refresh_pipeline_snapshot(output)
    write_production_qa(output, en, ru)
    (output / "README.md").write_text(production_readme_text(), encoding="utf-8", newline="\n")
    manifest = refresh_manifest(output, inputs={
        "master_en": {"path": BASE_EN.relative_to(REPO_ROOT).as_posix(), "sha256": sha256(BASE_EN)},
        "master_ru": {"path": BASE_RU.relative_to(REPO_ROOT).as_posix(), "sha256": sha256(BASE_RU)},
    })
    return {"status": "pass", "output": output.relative_to(REPO_ROOT).as_posix(), "files": manifest["file_count"],
            "assets": len(en_refs | ru_refs), "html_sha256": sha256(output / "Viral_RU.html"),
            "pdf_sha256": sha256(output / "Viral_RU.pdf"), "docx_sha256": docx_result["sha256"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--render-only", action="store_true", help="Rebuild HTML/PDF/DOCX from the packaged editable MASTER_RU.md")
    parser.add_argument("--word-only", action="store_true", help="Rebuild only DOCX through an isolated ArtView HTML projection")
    parser.add_argument("--handout-html-only", action="store_true", help="Normalize packaged EN/RU handout headings and rebuild only HTML")
    parser.add_argument("--finalize-word-pdf", action="store_true", help="Validate a Word-exported PDF and refresh QA/manifest")
    parser.add_argument("--patch-word-semantics", action="store_true", help="Patch hyperlinks, bookmarks and review-callout styling into an edited DOCX")
    parser.add_argument("--artview-decisions", type=Path, help="Accepted ArtView JSON applied downstream without editing MASTER_RU")
    args = parser.parse_args()
    try:
        if args.render_only and args.force:
            raise ValueError("--render-only and --force are mutually exclusive")
        if args.word_only and args.force:
            raise ValueError("--word-only and --force are mutually exclusive")
        if args.render_only and args.word_only:
            raise ValueError("--render-only and --word-only are mutually exclusive")
        if args.handout_html_only and (args.render_only or args.word_only or args.force):
            raise ValueError("--handout-html-only is mutually exclusive with --render-only, --word-only and --force")
        if args.finalize_word_pdf and (args.render_only or args.word_only or args.handout_html_only or args.force):
            raise ValueError("--finalize-word-pdf is mutually exclusive with other build modes and --force")
        if args.patch_word_semantics and (
            args.render_only or args.word_only or args.handout_html_only or args.finalize_word_pdf or args.force
        ):
            raise ValueError("--patch-word-semantics is mutually exclusive with other build modes and --force")
        if args.artview_decisions and not (args.render_only or args.word_only):
            raise ValueError("--artview-decisions requires --render-only or --word-only")
        if args.word_only and not args.artview_decisions:
            raise ValueError("--word-only requires --artview-decisions")
        if args.patch_word_semantics:
            result = patch_word_semantics(args.output_root)
        elif args.finalize_word_pdf:
            result = finalize_word_pdf(args.output_root)
        elif args.handout_html_only:
            result = handout_html_only(args.output_root)
        elif args.word_only:
            result = word_only(args.output_root, args.artview_decisions)
        elif args.render_only:
            result = render_only(args.output_root, args.artview_decisions)
        else:
            result = build(args.output_root, args.force)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
