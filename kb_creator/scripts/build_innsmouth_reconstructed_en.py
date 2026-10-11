"""Build a full-source Innsmouth RECONSTRUCTED_EN candidate from MinerU Markdown."""

from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
import shutil


PAGE_MARKER = re.compile(r"(?=<!-- mineru-page: \d+ -->)")
PAGE_INDEX = re.compile(r"^<!-- mineru-page: (\d+) -->")
IMAGE_LINK = re.compile(r"!\[\]\((images/[^)]+)\)")
CARD_TABLE_CAPTION = re.compile(
    r"(!\[\]\([^)]+\)\n\n)([^\n#<][^\n]*(?:\n[^\n#<][^\n]*)?)(\n\n<table>)"
)
STANDARD_CARD_SECTIONS = {"skills", "combat", "sanity", "spells", "backstory"}
HEADING_EDITS = (
    (0, "# INNSMOUTH TERROR", "# THE INNSMOUTH TERROR"),
    (3, "## CONTENTS", "# CONTENTS"),
    (4, "## PREPARING FOR PLAY", "### PREPARING FOR PLAY"),
    (5, "# KEEPER INFORMATION", "### KEEPER INFORMATION"),
    (6, "## THE INNSMOUTH TERROR", "### THE INNSMOUTH TERROR"),
    (6, "# INVOLVING THE INVESTIGATORS", "### INVOLVING THE INVESTIGATORS"),
    (7, "# DRAMATIS PERSONAE", "## DRAMATIS PERSONAE"),
    (7, "## Genevieve 'Ginny' Dubois, age 25, starlet", "### Genevieve 'Ginny' Dubois, age 25, starlet"),
    (7, "## P.A. Bazzledon, age 40, director & conman", "### P.A. Bazzledon, age 40, director & conman"),
    (8, "## Anna Díaz, age 26, producer", "### Anna Díaz, age 26, producer"),
    (8, "## Christopher McGuire, age 37, engineer", "### Christopher McGuire, age 37, engineer"),
    (9, "## Sammy Brewster, age 21, dilettante & sibling", "### Sammy Brewster, age 21, dilettante & sibling"),
    (9, "## The Crew", "### The Crew"),
    (9, "# MINOR NPCs", "## MINOR NPCs"),
    (9, "## Diane Loring", "### Diane Loring"),
    (9, "## Henry Armitage", "### Henry Armitage"),
    (9, "## Karen Jeffries", "### Karen Jeffries"),
    (9, "## Franc Turner", "### Franc Turner"),
    (9, "## Jeremiah Brewster", "### Jeremiah Brewster"),
    (9, "## Pete", "### Pete"),
    (9, "## Zadok Allen", "### Zadok Allen"),
    (10, "# START: ARKHAM", "## START: ARKHAM"),
    (10, "## ORNE LIBRARY (MISKATONIC UNIVERSITY)", "### ORNE LIBRARY (MISKATONIC UNIVERSITY)"),
    (11, "# THE ARKHAM ADVERTISER", "### THE ARKHAM ADVERTISER"),
    (12, "# THE MISKATONIC PLAYHOUSE", "### THE MISKATONIC PLAYHOUSE"),
    (13, "## OFFICE OF THE VICE CHANCELLOR MISKATONIC UNIVERSITY Arkham, Mass.", "### OFFICE OF THE VICE CHANCELLOR MISKATONIC UNIVERSITY Arkham, Mass."),
    (14, "## ARRIVAL", "### ARRIVAL"),
    (15, "# THE GILMAN HOUSE HOTEL", "### THE GILMAN HOUSE HOTEL"),
    (15, "# THE PRODUCTION TRAIN CAR", "### THE PRODUCTION TRAIN CAR"),
    (16, "# INVESTIGATION", "## INVESTIGATION"),
    (16, "## THE PRODUCER'S OFFICE", "### THE PRODUCER'S OFFICE"),
    (17, "## AROUND THE TRAIN", "### AROUND THE TRAIN"),
    (17, "## Bazzledon's Office", "### Bazzledon's Office"),
    (18, "## Ginny's Trailer", "### Ginny's Trailer"),
    (19, "## McGuire's Lab", "### McGuire's Lab"),
    (20, "## On Set", "### On Set"),
    (21, "## The Railway Entrance", "### The Railway Entrance"),
    (21, "## THE CAVE SYSTEM", "### THE CAVE SYSTEM"),
    (21, "## Moving Through the Caves", "### Moving Through the Caves"),
    (23, "## THE BREWSTER RESIDENCE", "### THE BREWSTER RESIDENCE"),
    (24, "## STUMBLING ONTO SET", "### STUMBLING ONTO SET"),
    (25, "## The General Store", "### The General Store"),
    (26, "## The Fire Station", "### The Fire Station"),
    (27, "## The Esoteric Order of Dagon", "### The Esoteric Order of Dagon"),
    (27, "## Entering through the Caves", "### Entering through the Caves"),
    (28, "# THE EPIC FINALE", "## THE EPIC FINALE"),
    (28, "## The Last Train out of Innsmouth", "### The Last Train out of Innsmouth"),
    (29, "## MVR Class B1 'Olmstead', steam locomotive", "### MVR Class B1 'Olmstead', steam locomotive"),
    (30, "## Playing the Hero", "### Playing the Hero"),
    (31, "## Did the investigators escape with the Atlantean Jewel?", "### Did the investigators escape with the Atlantean Jewel?"),
    (31, "## Was the final scene of the movie filmed?", "### Was the final scene of the movie filmed?"),
    (31, "## Rewards", "### Rewards"),
    (32, "# CHARACTERS AND MONSTERS", "## CHARACTERS AND MONSTERS"),
    (35, "# PRE-GENERATED INVESTIGATORS", "## PRE-GENERATED INVESTIGATORS"),
    (40, "# OFFICE OF THE VICE CHANCELLOR", "### OFFICE OF THE VICE CHANCELLOR"),
    (41, "## OFFICE OF THE VICE CHANCELLOR", "### OFFICE OF THE VICE CHANCELLOR"),
    (42, "## Handout 2: note (plain text)", "### Handout 2: note (plain text)"),
)
KEEPER_NOTE_COUNTS = {6: 2, 10: 1, 11: 2, 12: 1, 14: 1, 18: 1, 19: 1, 20: 2, 23: 1, 24: 1, 28: 1}
HANDOUT_ID_COUNTS = {6: 2, 10: 1, 13: 2, 18: 4, 20: 1, 21: 1, 40: 1, 41: 1, 42: 1}
BULLET_COUNTS = {1: 5, 17: 1, 31: 3, 35: 1, 39: 1}
RECOVERED_ASSETS = {
    "6beb2e37b45a8f10d343b3f191ab143a3fa115b8234399d6e87a0eea8757f2d5.jpg":
        "0d5d4aec14536051931ad52a1d48f993a78dd166cd33cd7cc7c60a0bf5e5a47f",
    "d29dd78603767844a3d3811902958043a3a67dfd0fa809603b1926066c706531.jpg":
        "a18f612a95e6784c1a9f4b68af922d87e03f4c72becddb1d136108355c2a3cb8",
    "5534eb2d722a751816b5c0181ca3fdf4fff79073e34dc5ccac9bfeb646faeb7c.jpg":
        "87ecc9879ddde74853f6153bf9419d2f90e8af637726c0b4aaeebdfceccb83d5",
    "f23271b212f11039d58ab81421a36b5f12a0b2f72d8cdb020562cad6fcf872a6.jpg":
        "6b8a562b681975acfe01a45ff97d802b49b7ba558d2f649e6ca47c2d2a5fd01b",
    "3ce72daa90f87b979a5bca105e7cd898e130574d0e230e2ba87a5c9a65472782.jpg":
        "8eb91e717eda3e012376ab7fbaaf949b62b1cf8cf0d364efb257fe34fecd9686",
    "497dc1045aa4f06805e86552e2de0207bf15bfbc65856c747e7a88d375212a67.jpg":
        "fe966e500ef68771b6d6287335015de771e35ac48fdd0e6b2a4a748f4a8587d9",
}
HARBOR_ASSET = "6beb2e37b45a8f10d343b3f191ab143a3fa115b8234399d6e87a0eea8757f2d5.jpg"
SOURCE_CANDIDATE_SHA256 = "1504a9c71ca995748e4125b7303c0d3064e588abb226ebb5ab99a5f5763c993c"
PDF_CONTROL_SHA256 = "5850b26a077390abff4a321e754a3709d6148fa4ac7a9f4d63bdbeff6949b1bb"
READING_ASSET_INVENTORY_SHA256 = "02a1da4f59042bd31b6d101335b13862bbf0397d4af6a21bb36c9e386ffaf45e"
FINAL_ASSET_INVENTORY_SHA256 = "b6f9bf00b01db09ed06723871b97b424206c5a79eb624c8f5768a847b1ce3b39"
SOURCE_COVER_ASSET = "source_cover_page_01.jpg"
SOURCE_COVER_ASSET_SHA256 = "6afabd85d279af4d3051be9b273eb1b00b8cd0456b88c59fd7ff22580ae28229"
PAGE19_ASSET = "page19_film_reel.png"
PAGE19_ASSET_SHA256 = "f8fe3e0eb75d7f10e804383b5cf2034be6678387df038ee847d5c00474fe459e"


def replace_once(text: str, before: str, after: str, label: str) -> str:
    count = text.count(before)
    if count != 1:
        raise ValueError(f"{label}: expected one exact match, found {count}")
    return text.replace(before, after, 1)


def split_pages(markdown: str) -> tuple[str, dict[int, str]]:
    first_marker = markdown.find("<!-- mineru-page:")
    if first_marker < 0:
        raise ValueError("input has no MinerU page markers")
    preamble = markdown[:first_marker]
    pages: dict[int, str] = {}
    for segment in PAGE_MARKER.split(markdown[first_marker:]):
        if not segment.strip():
            continue
        match = PAGE_INDEX.match(segment)
        if not match:
            raise ValueError("page segment does not start with a MinerU page marker")
        index = int(match.group(1))
        if index in pages:
            raise ValueError(f"duplicate MinerU page marker: {index}")
        pages[index] = segment.rstrip() + "\n"
    return preamble, pages


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_source_candidate(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"missing retained source candidate: {path}")
    actual_hash = sha256(path)
    if actual_hash != SOURCE_CANDIDATE_SHA256:
        raise ValueError(f"retained source candidate hash mismatch: {path}")
    return actual_hash


def asset_inventory(links: list[str], images_dir: Path) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for link in sorted(set(links)):
        if not link.startswith("images/") or Path(link).name != link.removeprefix("images/"):
            raise ValueError(f"invalid image link: {link}")
        path = images_dir / Path(link).name
        if not path.is_file():
            raise ValueError(f"missing linked asset: {path}")
        rows.append(
            {
                "path": link,
                "byte_count": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "link_count": len(links),
        "asset_count": len(rows),
        "total_bytes": sum(int(row["byte_count"]) for row in rows),
        "inventory_sha256": hashlib.sha256(canonical).hexdigest(),
        "files": rows,
    }


def copy_reading_assets(
    source_links: list[str],
    final_links: list[str],
    reading_assets: Path,
    output_images: Path,
) -> dict[str, object]:
    source_inventory = asset_inventory(source_links, reading_assets)
    if source_inventory["link_count"] != 132 or source_inventory["asset_count"] != 132:
        raise ValueError(f"reading asset count mismatch: {source_inventory['asset_count']}")
    if source_inventory["inventory_sha256"] != READING_ASSET_INVENTORY_SHA256:
        raise ValueError("reading asset inventory hash mismatch")

    source_names = {Path(link).name for link in source_links}
    recovery_names = set(RECOVERED_ASSETS) | {SOURCE_COVER_ASSET, PAGE19_ASSET}
    output_images.mkdir(parents=True, exist_ok=True)
    copied = 0
    for link in sorted(set(final_links)):
        name = Path(link).name
        if name in recovery_names:
            continue
        if name not in source_names:
            raise ValueError(f"final asset has no reading/recovery source: {link}")
        source = reading_assets / name
        target = output_images / name
        source_hash = sha256(source)
        if target.exists() and sha256(target) != source_hash:
            raise ValueError(f"existing reading asset target has wrong hash: {target}")
        if not target.exists():
            shutil.copyfile(source, target)
        copied += 1
    return {"source_inventory": source_inventory, "copied_asset_count": copied}


def recover_assets(ocr_assets: Path, output_images: Path) -> list[str]:
    output_images.mkdir(parents=True, exist_ok=True)
    recovered: list[str] = []
    for name, expected_hash in RECOVERED_ASSETS.items():
        source = ocr_assets / name
        target = output_images / name
        if not source.is_file():
            raise ValueError(f"missing pinned OCR recovery asset: {source}")
        actual_hash = sha256(source)
        if actual_hash != expected_hash:
            raise ValueError(f"OCR recovery asset hash mismatch: {source}")
        if target.exists() and sha256(target) != expected_hash:
            raise ValueError(f"existing recovery target has wrong hash: {target}")
        if not target.exists():
            shutil.copyfile(source, target)
        recovered.append(f"images/{name}")
    return recovered


def recover_page19_pdf_asset(control_pdf: Path, output_images: Path) -> str:
    if sha256(control_pdf) != PDF_CONTROL_SHA256:
        raise ValueError(f"control PDF hash mismatch: {control_pdf}")
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise RuntimeError("pypdf is required; use the bundled Codex PDF runtime") from error
    image = PdfReader(control_pdf).pages[19].images[3].image
    stream = BytesIO()
    image.save(stream, format="PNG", optimize=False)
    data = stream.getvalue()
    if hashlib.sha256(data).hexdigest() != PAGE19_ASSET_SHA256:
        raise ValueError("page 19 extracted image hash mismatch")
    output_images.mkdir(parents=True, exist_ok=True)
    target = output_images / PAGE19_ASSET
    if target.exists() and sha256(target) != PAGE19_ASSET_SHA256:
        raise ValueError(f"existing page 19 asset has wrong hash: {target}")
    if not target.exists():
        target.write_bytes(data)
    return f"images/{PAGE19_ASSET}"


def recover_source_cover_pdf_asset(control_pdf: Path, output_images: Path) -> str:
    if sha256(control_pdf) != PDF_CONTROL_SHA256:
        raise ValueError(f"control PDF hash mismatch: {control_pdf}")
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise RuntimeError("pypdf is required; use the bundled Codex PDF runtime") from error
    image = PdfReader(control_pdf).pages[0].images[0].image.convert("RGB")
    stream = BytesIO()
    image.save(
        stream,
        format="JPEG",
        quality=95,
        subsampling=0,
        optimize=False,
        progressive=False,
    )
    data = stream.getvalue()
    if hashlib.sha256(data).hexdigest() != SOURCE_COVER_ASSET_SHA256:
        raise ValueError("source cover extracted image hash mismatch")
    output_images.mkdir(parents=True, exist_ok=True)
    target = output_images / SOURCE_COVER_ASSET
    if target.exists() and sha256(target) != SOURCE_COVER_ASSET_SHA256:
        raise ValueError(f"existing source cover asset has wrong hash: {target}")
    if not target.exists():
        target.write_bytes(data)
    return f"images/{SOURCE_COVER_ASSET}"


def promote_card_captions(page: str) -> str:
    def promote(match: re.Match[str]) -> str:
        prefix, caption, suffix = match.groups()
        lines = [line.strip() for line in caption.splitlines() if line.strip()]
        first = lines[0]
        if first.casefold() in STANDARD_CARD_SECTIONS:
            rendered = f"#### {first.title()}"
            if len(lines) > 1:
                rendered += "\n" + "\n".join(lines[1:])
        else:
            rendered = f"### {first}"
            if len(lines) > 1:
                if lines[1].casefold().startswith("age:"):
                    rendered += "\n\n" + "\n".join(lines[1:])
                else:
                    rendered += " " + " ".join(lines[1:])
        return prefix + rendered + suffix

    page = CARD_TABLE_CAPTION.sub(promote, page)
    for heading in ("Skills", "Combat", "Sanity", "Spells", "Backstory"):
        page = re.sub(rf"(?m)^##+ {heading}$", f"#### {heading}", page)
    return page


def replace_all_exact(text: str, before: str, after: str, count: int, label: str) -> str:
    actual = text.count(before)
    if actual != count:
        raise ValueError(f"{label}: expected {count} exact matches, found {actual}")
    return text.replace(before, after)


def bold_handout_ids(page: str, expected_count: int, label: str) -> str:
    rendered: list[str] = []
    applied = 0
    for line in page.splitlines(keepends=True):
        if line.lstrip().startswith("#"):
            rendered.append(line)
            continue
        line, count = re.subn(
            r"(?<!\*)(Handout (?:1-a|1-b|2))(?!\*)", r"**\1**", line
        )
        applied += count
        rendered.append(line)
    if applied != expected_count:
        raise ValueError(f"{label}: expected {expected_count} matches, found {applied}")
    return "".join(rendered)


def apply_source_structure_repairs(pages: dict[int, str]) -> None:
    for page_index, before, after in HEADING_EDITS:
        pages[page_index] = replace_once(
            pages[page_index], before, after, f"page {page_index} heading projection"
        )

    oath_lines = (
        "“Iä! Dagon! I, (speaker’s name), do solemnly swear that I will neither interfere with, nor inform upon, the activities of the Deep Ones. Iä! Dagon!”",
        "“Iä! Dagon! I, (speaker’s name) do solemnly swear that, if requested to do so, I will render aid to the Deep Ones to the best of my ability, and in whatever form or manner is required of me. Iä! Dagon!”",
        "“Iä! Dagon! I, (speaker’s name) do solemnly swear that I take this entity [a Deep One] as my wife/husband, that I shall take them to my home, and that with them I will endeavor to have and raise children, so that the race, and the faith, can continue to prosper. Iä! Dagon! Iä! Hydra!”",
    )
    for oath in oath_lines:
        pages[5] = replace_once(pages[5], oath, f"*{oath}*", "page 5 reviewed oath emphasis")
    page5_emphasis = (
        ("Ginny Dubois (Born", "**Ginny Dubois** (Born", "Ginny Dubois"),
        ("film, P.A. Bazzledon (page 4)", "film, **P.A. Bazzledon** (page 4)", "P.A. Bazzledon"),
        ("Table 1: timeline of events", "**Table 1: timeline of events**", "timeline title"),
    )
    for before, after, label in page5_emphasis:
        pages[5] = replace_once(pages[5], before, after, f"page 5 {label} emphasis")

    for page_index, count in KEEPER_NOTE_COUNTS.items():
        pages[page_index] = replace_all_exact(
            pages[page_index], "Keeper note:", "**Keeper note:**", count,
            f"page {page_index} keeper-note emphasis",
        )
    for page_index, count in HANDOUT_ID_COUNTS.items():
        pages[page_index] = bold_handout_ids(
            pages[page_index], count, f"page {page_index} handout-id emphasis"
        )
    for page_index, count in BULLET_COUNTS.items():
        pages[page_index] = replace_all_exact(
            pages[page_index], "• ", "", count, f"page {page_index} duplicate bullet removal"
        )

    joins = (
        (6, "both at once?\n\nMadness.", "both at once? Madness."),
        (18, "by the\n\nBrewster Residence (page 20).", "by the Brewster Residence (page 20)."),
        (23, "identified, The\n\nEpic Finale scene should begin.", "identified, The Epic Finale scene should begin."),
    )
    for page_index, before, after in joins:
        pages[page_index] = replace_once(
            pages[page_index], before, after, f"page {page_index} source paragraph join"
        )

    page13_before = (
        "It will not be a surprise to the Society for the Exploration of\n"
        "the Unexplained that the Board has taken an interest in their\n"
        "work and that the curiosity and adventurous spirit of the Soci-\n"
        "ety aligns well with the value of Miskatonic University. It is due\n"
        "to these factors that the Board has always been proud to sponsor\n"
        "the Society's work. We must now, however, ask something from the\n"
        "Society.\n\n"
        "A priceless artifact, the Atlantean Jewel, was loaned to a local production company by the name of Bazzledon Productions. An in-ternal investigation is underway to determine how exactly the film company was able to get hold of the item. However, that need not concern you all. The Producer of the production company has sadly reported the jewelry missing from their set earlier this week. We are charging the Society with the investigation and recovery of this artifact. In addition, the Society is requested to gather any evidence regarding the possible culprit to be handed over to the local constabulary."
    )
    page13_after = (
        "It will not be a surprise to the Society for the Exploration of the Unexplained that the Board has taken an interest in their work and that the curiosity and adventurous spirit of the Society aligns well with the value of Miskatonic University. It is due to these factors that the Board has always been proud to sponsor the Society's work. We must now, however, ask something from the Society.\n\n"
        "A priceless artifact, the Atlantean Jewel, was loaned to a local production company by the name of Bazzledon Productions. An internal investigation is underway to determine how exactly the film company was able to get hold of the item. However, that need not concern you all. The Producer of the production company has sadly reported the jewelry missing from their set earlier this week. We are charging the Society with the investigation and recovery of this artifact. In addition, the Society is requested to gather any evidence regarding the possible culprit to be handed over to the local constabulary."
    )
    pages[13] = replace_once(pages[13], page13_before, page13_after, "page 13 handout reflow")
    page18_before = (
        "Hey G,\nWanted to drop in and see you, but your crew\nweren't thrilled to have me about. If you want\n"
        "to catch up, the old tunnel route is blocked, so\nyou have to take a detour. It's LLFRTL.\nSammy"
    )
    page18_after = (
        "Hey G,\n\nWanted to drop in and see you, but your crew weren't thrilled to have me about. "
        "If you want to catch up, the old tunnel route is blocked, so you have to take a detour. It's LLFRFL.\n\nSammy"
    )
    pages[18] = replace_once(pages[18], page18_before, page18_after, "page 18 handout reflow")


def build_reconstructed_en(markdown: str) -> tuple[str, dict[str, object]]:
    _, pages = split_pages(markdown)
    expected = set(range(46))
    missing = sorted(expected - pages.keys())
    unexpected = sorted(pages.keys() - expected)
    if missing:
        raise ValueError(f"missing expected scenario pages: {missing}")
    if unexpected:
        raise ValueError(f"unexpected source pages: {unexpected}")

    pages[0] = replace_once(
        pages[0],
        "# INNSMOUTH TERROR\n",
        f"# INNSMOUTH TERROR\n\n![](images/{SOURCE_COVER_ASSET})\n",
        "page 0 source cover recovery",
    )

    pages[3] = replace_once(
        pages[3],
        "CALL OF\nTHULHU",
        "CALL OF\nCTHULHU",
        "page 3 Call of Cthulhu OCR correction",
    )
    pages[5] = replace_once(
        pages[5],
        "Evening of the 2ndday",
        "Evening of the 2nd day",
        "page 5 timeline spacing",
    )
    pages[4] = pages[4].rstrip() + f"\n\n![](images/{HARBOR_ASSET})\n"

    anna_block = (
        "![](images/5deabcfccfe44c4186745c57d25dc5e989dbadc549266836391b49ed3179f285.jpg)\n\n"
        "Anna Díaz\n\n"
    )
    pages[8] = replace_once(pages[8], anna_block, "", "page 8 Anna block removal")
    pages[8] = replace_once(
        pages[8],
        "## Christopher McGuire, age 37, engineer\n",
        anna_block + "## Christopher McGuire, age 37, engineer\n",
        "page 8 Anna re-anchor",
    )

    ginny_block = (
        "![](images/81240de97cfb63a63694e28b512857f6b072aa8ed012610a5884923d8d0baffa.jpg)\n\n"
        "Genevieve 'Ginny' Dubois\n\n"
    )
    pages[7] = replace_once(pages[7], ginny_block, "", "page 7 Ginny block removal")
    pages[7] = replace_once(
        pages[7],
        "## P.A. Bazzledon, age 40, director & conman\n",
        ginny_block + "## P.A. Bazzledon, age 40, director & conman\n",
        "page 7 Ginny re-anchor",
    )

    sammy_block = (
        "![](images/b2b7cdbff504429a3705ad93671f6a1a2267237071ad085ad02723e658be80b4.jpg)\n\n"
        "Sammy Brewster\n\n"
    )
    pages[9] = replace_once(pages[9], sammy_block, "", "page 9 Sammy block removal")
    pages[9] = replace_once(
        pages[9],
        "## The Crew\n",
        sammy_block + "## The Crew\n",
        "page 9 Sammy re-anchor",
    )

    pages[10] = replace_once(
        pages[10],
        "![](images/1cb607cf2d0527ec9f9fb21f8ebb43d8f736c5c1214551b409d259f2c8425e49.jpg)\n",
        "![](images/d29dd78603767844a3d3811902958043a3a67dfd0fa809603b1926066c706531.jpg)\n\n"
        "Diane Loring\n\n"
        "![](images/5534eb2d722a751816b5c0181ca3fdf4fff79073e34dc5ccac9bfeb646faeb7c.jpg)\n\n"
        "Dr. Henry Armitage\n",
        "page 10 compound portrait labels",
    )
    pages[11] = replace_once(
        pages[11],
        "![](images/612cbab6308b805c21f9f4f547e1c19d422e1f1ff62e946693a96d6cf1bff0e9.jpg)\n",
        "![](images/497dc1045aa4f06805e86552e2de0207bf15bfbc65856c747e7a88d375212a67.jpg)\n\n"
        "Karen Jeffries\n",
        "page 11 clean Karen portrait recovery and label",
    )
    pages[19] = replace_once(
        pages[19],
        "![](images/dfbedc62b6ceeae951a47865ec743a90e043f627cada6a1eb7ca2db97d96821e.jpg)\n",
        f"![](images/{PAGE19_ASSET})\n",
        "page 19 clean PDF image recovery",
    )
    pages[22] = replace_once(
        pages[22],
        "![](images/e5ac52345fe7431fc61257432b1935883ad33d55ef5613eb689d355a30802294.jpg)\n",
        "### Table 2: encounters in the caves\n\n"
        "![](images/e5ac52345fe7431fc61257432b1935883ad33d55ef5613eb689d355a30802294.jpg)\n",
        "page 22 table title",
    )
    pages[26] = replace_once(
        pages[26],
        "![](images/4d905ce09d130e45c54923ae1c70e364935eac7deb257f3577de16d0bc0d1cd9.jpg)\n\n"
        "Jeremiah Breuster\n",
        "![](images/f23271b212f11039d58ab81421a36b5f12a0b2f72d8cdb020562cad6fcf872a6.jpg)\n\n"
        "Zadok Allen\n\n"
        "![](images/3ce72daa90f87b979a5bca105e7cd898e130574d0e230e2ba87a5c9a65472782.jpg)\n\n"
        "Jeremiah Brewster\n",
        "page 26 compound portrait labels",
    )

    pages[32] = replace_once(
        pages[32],
        "## Genevieve 'Ginny' Dubois, age 25,\n\n## sultry starlet of the film\n",
        "### Genevieve 'Ginny' Dubois, age 25, sultry starlet of the film\n",
        "page 32 split identity heading",
    )
    for index in range(32, 40):
        pages[index] = promote_card_captions(pages[index])

    pages[34] = replace_once(
        pages[34],
        "damage 10D6A Star Spawn may attack",
        "damage 10D6<br>A Star Spawn may attack",
        "page 34 Star Spawn table line break",
    )
    pages[34] = replace_once(
        pages[34],
        "o/1D6 loss for seeing a Deep One.",
        "0/1D6 loss for seeing a Deep One.",
        "page 34 Deep One sanity zero",
    )
    apply_source_structure_repairs(pages)

    body = "\n".join(pages[index].rstrip() for index in range(46)) + "\n"
    output = (
        "<!-- Innsmouth RECONSTRUCTED_EN candidate; reconstructed from retained MinerU evidence. -->\n"
        "<!-- All source pages 0-45 retained; no publication page suppression applied. -->\n\n"
        + body
    )
    image_links = IMAGE_LINK.findall(output)
    counts = {
        "page_markers": len(re.findall(r"(?m)^<!-- mineru-page: \d+ -->$", output)),
        "first_page": min(pages),
        "last_page": max(pages),
        "image_links": len(image_links),
        "tables": output.count("<table>"),
        "headings": len(re.findall(r"(?m)^#{1,6} ", output)),
        "table_evidence_comments": output.count("<!-- table-evidence:"),
    }
    expected_counts = {
        "page_markers": 46,
        "first_page": 0,
        "last_page": 45,
        "image_links": 136,
        "tables": 53,
        "headings": 169,
        "table_evidence_comments": 0,
    }
    if counts != expected_counts:
        raise ValueError(f"RECONSTRUCTED_EN structural counts mismatch: {counts}")
    qa: dict[str, object] = {
        "state": "RECONSTRUCTED_EN_R0_READY_FOR_QA",
        "stage_contract": "full_source_reconstruction_without_publication_suppression",
        "included_page_indices": list(range(46)),
        "excluded_page_indices": [],
        "image_link_count": len(image_links),
        "counts": counts,
        "page_inventory": [
            {
                "page_index": index,
                "byte_count": len(pages[index].encode("utf-8")),
                "sha256": hashlib.sha256(pages[index].encode("utf-8")).hexdigest(),
                "image_links": len(IMAGE_LINK.findall(pages[index])),
                "tables": pages[index].count("<table>"),
                "headings": len(re.findall(r"(?m)^#{1,6} ", pages[index])),
            }
            for index in range(46)
        ],
        "corrections": [
            "page 3 CALL OF CTHULHU OCR correction from visual disposition",
            "page 5 timeline 2nd day spacing restored",
            "page 4 harbor artwork recovered from full OCR geometry diff",
            "page 0 source cover artwork recovered from embedded PDF image",
            "page 8 Anna Diaz portrait re-anchored to her profile",
            "page 10 compound portrait labels transcribed from visual evidence",
            "page 11 Karen Jeffries label transcribed from visual evidence",
            "page 19 clean film-reel art recovered from embedded PDF image",
            "page 22 table title transcribed from visual evidence",
            "page 26 compound portrait labels transcribed and spelling corrected",
            "pages 32-39 card identities and standard subsections promoted",
            "page 34 Star Spawn table line break restored",
            "page 34 Deep One sanity zero corrected from PDF text control",
            "57 scenario heading levels/titles restored from the accepted source hierarchy",
            "40 reviewed source-semantic markup operations restored",
            "three false paragraph boundaries joined",
            "two handout text blocks reflowed from source visual evidence",
            "pages 43-45 retained as source backmatter; no publication filtering applied",
        ],
        "non_blocking_asset_debt": [
            "art captions require final editorial style decision",
        ],
        "source_visible_anomalies_preserved": [
            "Christoper McGuire spelling on page 8",
            "Innmouth spelling on pages 11 and 31",
            "Deep One 45% (12/9) values on page 34",
            "Maggie Spot Hidden 60% (307/12) value on page 39",
        ],
    }
    return output, qa


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_md", type=Path)
    parser.add_argument("output_md", type=Path)
    parser.add_argument("qa_json", type=Path)
    parser.add_argument(
        "--reading-assets",
        type=Path,
        required=True,
        help="pinned MinerU Hybrid/high images directory referenced by the reading candidate",
    )
    parser.add_argument(
        "--ocr-assets",
        type=Path,
        required=True,
        help="pinned full-document OCR images directory for approved asset recovery",
    )
    parser.add_argument(
        "--control-pdf",
        type=Path,
        required=True,
        help="pinned PDF used to recover the clean page-19 embedded artwork",
    )
    args = parser.parse_args()

    source_hash = verify_source_candidate(args.input_md)
    source = args.input_md.read_text(encoding="utf-8")
    if args.output_md.parent != args.qa_json.parent:
        raise ValueError("RECONSTRUCTED_EN Markdown and QA sidecar must share one package directory")
    if args.output_md.exists() or args.qa_json.exists():
        raise ValueError("refusing to overwrite an existing RECONSTRUCTED_EN package root")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    first = build_reconstructed_en(source)
    second = build_reconstructed_en(source)
    if first != second:
        raise ValueError("RECONSTRUCTED_EN two-build identity mismatch")
    master, qa = first
    qa["source_candidate_sha256"] = source_hash
    qa["source_pdf_sha256"] = sha256(args.control_pdf)
    output_images = args.output_md.parent / "images"
    source_links = IMAGE_LINK.findall(source)
    final_links = IMAGE_LINK.findall(master)
    qa["asset_materialization"] = copy_reading_assets(
        source_links,
        final_links,
        args.reading_assets,
        output_images,
    )
    qa["recovered_assets"] = recover_assets(args.ocr_assets, output_images)
    qa["recovered_assets"].append(
        recover_source_cover_pdf_asset(
            args.control_pdf,
            output_images,
        )
    )
    qa["recovered_assets"].append(
        recover_page19_pdf_asset(
            args.control_pdf,
            output_images,
        )
    )
    missing_assets = sorted(
        link for link in final_links if not (args.output_md.parent / link).is_file()
    )
    qa["missing_assets"] = missing_assets
    if missing_assets:
        qa["state"] = "REJECTED_MISSING_ASSETS"
        raise ValueError(f"missing linked assets: {missing_assets[:5]}")
    qa["asset_inventory"] = asset_inventory(final_links, output_images)
    if qa["asset_inventory"]["link_count"] != 136 or qa["asset_inventory"]["asset_count"] != 136:
        raise ValueError("final RECONSTRUCTED_EN asset count mismatch")
    if qa["asset_inventory"]["inventory_sha256"] != FINAL_ASSET_INVENTORY_SHA256:
        raise ValueError("final RECONSTRUCTED_EN asset inventory hash mismatch")
    master_bytes = master.encode("utf-8")
    qa["markdown"] = {
        "path": args.output_md.name,
        "byte_count": len(master_bytes),
        "sha256": hashlib.sha256(master_bytes).hexdigest(),
    }
    args.output_md.write_text(master, encoding="utf-8", newline="\n")
    args.qa_json.write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
