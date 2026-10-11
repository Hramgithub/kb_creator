"""Project an accepted RECONSTRUCTED_EN package into the Innsmouth reader master."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
import build_innsmouth_reconstructed_en as reconstructed


RECONSTRUCTED_EN_BYTES = 138426
RECONSTRUCTED_EN_SHA256 = "8f5a35b6fbe545691eef66c52a848f0f04776a247ccaaf40b16140feb0c543bf"
RECONSTRUCTED_EN_QA_BYTES = 75179
RECONSTRUCTED_EN_QA_SHA256 = "8c351053e49ae3546bca5857394ddccba2ff60ae05da75c03acb47e076b06da9"
IMAGE_LINE = re.compile(r"(?m)^!\[\]\(images/([^)]+)\)[ \t]*\n?")
PAGE_TOKEN = re.compile(r"(?i)\bpage +[0-9]+\b")
TECHNICAL_COMMENT = re.compile(
    r"(?m)^<!-- (?:mineru-page: \d+|table-evidence: [^>]+) -->[ \t]*\n?"
)
RETAINED_ASSETS = {
    "203c6dcff8d86c53d99721ad4448caeba0ecb0ecaf129ddefcd3b6811c54c32f.jpg",
    "20cc7e0f3485214dd933ad3996f0ea5a6866b23db12cd22ffa113bfe9314b125.jpg",
    "2a77226d3427fb03aa422fdfa6f5876f584609b3876e26ac83487a67f6759e33.jpg",
    "2f0e82f6dd6f5a9a0ad377a9ad3f34075fda71abbea8f34b8a7401b66eab7f35.jpg",
    "3371d3857129bfbbc48063eaed6e62df90ee0b93f54c98e776c49f57b045c38f.jpg",
    "3ce72daa90f87b979a5bca105e7cd898e130574d0e230e2ba87a5c9a65472782.jpg",
    "497dc1045aa4f06805e86552e2de0207bf15bfbc65856c747e7a88d375212a67.jpg",
    "4c93bb273638108e23cb17b05c30d7026cae7e27769e66ffb7026ae6e87c9bd7.jpg",
    "5534eb2d722a751816b5c0181ca3fdf4fff79073e34dc5ccac9bfeb646faeb7c.jpg",
    "5deabcfccfe44c4186745c57d25dc5e989dbadc549266836391b49ed3179f285.jpg",
    "6303e327b95dd1d5484282e977bb4ba379617e0cbc47505906af6e54c2697e1d.jpg",
    "6beb2e37b45a8f10d343b3f191ab143a3fa115b8234399d6e87a0eea8757f2d5.jpg",
    "74aa40aa2039e4cf4eab3fa6ff9618cdfd16778994bf6bf03c6b4ed5aa0550d6.jpg",
    "81240de97cfb63a63694e28b512857f6b072aa8ed012610a5884923d8d0baffa.jpg",
    "82307baffee51be33d6bf8b95723fbf46d0e34e1a22fd13adc8cb598c8f82172.jpg",
    "8270a8298d11dc6be7a1086e0d891c57982032180c0eeb0ab67e58509d784269.jpg",
    "86daf1c4fa06068c8d767a83fc2951ca012be3189880157167903da715219893.jpg",
    "89042f940a05158789c1f01803732eea3a0a1d6b8dd02bd8284872c23d84147e.jpg",
    "9c85f20d6de3aceaeb294aaf3b6af38ba32d23ee36466d875d292db0f373cf0a.jpg",
    "9ded43678da7bb047cacb1b2ffe80cda584e20341949989a19348595670daa5f.jpg",
    "a824d214f9bbc53324ee4903be7b21d1d86252d2d2d6700ea6807ac1a572b8ed.jpg",
    "b2b7cdbff504429a3705ad93671f6a1a2267237071ad085ad02723e658be80b4.jpg",
    "c4124729ab42077a516b69c66ecb3ae88171353f5deaedc865b8f332a32afa91.jpg",
    "c68b102eb549eaa684f8fb5a3637bc8acd12f8f123cdf8aa4b79bb5b19de103c.jpg",
    "d2556e32e67e388fe5878fcd43a1d50ba5ed1df9e099f3533f4b4b3ec4390d02.jpg",
    "d29dd78603767844a3d3811902958043a3a67dfd0fa809603b1926066c706531.jpg",
    "d58d77c8f9d78a6f7a243191794a958376eb72a3685fb1e86c7814690cecf6f8.jpg",
    "ec8e821fae101fc7196af0b1afb9d74f00377479b0ba7d1a1dc4b8e8f57516b7.jpg",
    "ed88e677e363073b2973212c4f3e44c3bd91c2a91aff7f7ca0e3a8da41c4e224.jpg",
    "f03a1d401aabe96c7433f2775daa155f8e0bdfa17a2bf233ee902fe070c88f91.jpg",
    "f23271b212f11039d58ab81421a36b5f12a0b2f72d8cdb020562cad6fcf872a6.jpg",
    "page19_film_reel.png",
    "source_cover_page_01.jpg",
}
RETAINED_ASSET_INVENTORY_SHA256 = "15485c208825a08b8efa97183606d18bacebb060aa901dca0ec3543f922923e2"
EXCLUDED_LETTER_SEAL_ASSET = (
    "334f14bd517569e118d9445575f8c2bed6a356c7504142c3ac75a6f472e954f5.jpg"
)

# Reader-facing group label, printed source page, stable body anchor.
SECTION_GROUPS = (
    ("INTRODUCTION", "1", "nri-h-1e7c84a4e9f5927381bc3dd4"),
    ("DRAMATIS PERSONAE", "4", "nri-h-b1afc3d2767828f22a3d7b87"),
    ("START: ARKHAM", "7", "nri-h-29da96049102775b4dcc2b3a"),
    ("INNSMOUTH", "11", "nri-h-640be35ee56417677f8750f5"),
    ("INVESTIGATION", "13", "nri-h-579f6cee9279aa85f459d268"),
    ("INTO INNSMOUTH", "22", "nri-h-1e82f0c963d8a023793fa18e"),
    ("THE EPIC FINALE", "25", "nri-h-9e45e6c31b8f513fdfc0cbcb"),
    ("EPILOGUE", "28", "nri-h-784561a8c2d6538c46980f3f"),
    ("CHARACTERS AND MONSTERS", "29", "nri-h-216abf1f13f006ed96ddabfd"),
    ("PRE-GENERATED INVESTIGATORS", "32", "nri-h-cef5699cd74c24cd894040ee"),
    ("HANDOUTS", "38", "nri-h-9eb21ebd1012f4d0e1572e0a"),
)

# Existing leaf labels in the printed contents.  The numeric tail is removed
# because the link replaces navigation that depended on a paper page number.
TOC_ENTRIES = (
    ("Preparing for play 1", "Preparing for play", "nri-h-47551367143746af596d3df2"),
    ("The Innsmouth Terror 3", "The Innsmouth Terror", "nri-h-e1e4abee7d665d664b579640"),
    ("Involving the Investigators 3", "Involving the Investigators", "nri-h-5a1d3f11fa74d5bae7cbc1e7"),
    ("Genevieve 'Ginny' Dubois 4", "Genevieve 'Ginny' Dubois", "nri-h-88dac050ed1ec36f91e4b6fe"),
    ("P.A. Bazzledon 4", "P.A. Bazzledon", "nri-h-4ad8df2678e05f458f288662"),
    ("Anna Díaz 5", "Anna Díaz", "nri-h-cd6a958ad9223013558284e5"),
    ("Christopher McGuire 5", "Christopher McGuire", "nri-h-96bc6a07453b7b19ecf06440"),
    ("Sammy Brewster 6", "Sammy Brewster", "nri-h-e0857213264e131c714fa054"),
    ("The Crew 6", "The Crew", "nri-h-eb898a1c80749cbdbb6a2241"),
    ("Minor NPCs 6", "Minor NPCs", "nri-h-bf21a56d117d74edde8c045e"),
    ("Orne Library 7", "Orne Library", "nri-h-0712e7e461fd02534398a35f"),
    ("The Arkham Advertiser 8", "The Arkham Advertiser", "nri-h-f81478a90f8941232106712e"),
    ("The Miskatonic Playhouse 9", "The Miskatonic Playhouse", "nri-h-27b1ad17b7316f09136b83bc"),
    ("Arrival 11", "Arrival", "nri-h-e6c805ba31dc84425c90fbc6"),
    ("The Gilman House Hotel 12", "The Gilman House Hotel", "nri-h-591edd5bcf58d378b27f28cc"),
    ("The Production Train Car 12", "The Production Train Car", "nri-h-a6cc5383a39e0ec74e8769a8"),
    ("The Producer's Office 13", "The Producer's Office", "nri-h-988fb78c5b2cac516d5570bf"),
    ("Around the Train 14", "Around the Train", "nri-h-62a8c5d75b10782b4e475a55"),
    ("Bazzledon's Office 14", "Bazzledon's Office", "nri-h-1e72d19ab832ccee9c380a67"),
    ("Ginny's Trailer 15", "Ginny's Trailer", "nri-h-9af9701e3f85a91ab3b92009"),
    ("McGuire's Lab 16", "McGuire's Lab", "nri-h-7eae4a85cb793259eb9ed053"),
    ("On Set 17", "On Set", "nri-h-4a3bb4ef4c7d762c63fef3b4"),
    ("The Railway Entrance 18", "The Railway Entrance", "nri-h-6e9d2e67b27162302be156fe"),
    ("The Cave System 18", "The Cave System", "nri-h-0377b0cfaf5eda9da814e2d8"),
    ("Moving Through the Caves 18", "Moving Through the Caves", "nri-h-d5b878609b4bc64831d97150"),
    ("The Brewster Residence 20", "The Brewster Residence", "nri-h-f6184124151c4142421b1af0"),
    ("Stumbling onto Set 21", "Stumbling onto Set", "nri-h-b741e3b3e62d814b592d4419"),
    ("The General Store 22", "The General Store", "nri-h-d012304a399a1e520aefdba5"),
    ("The Fire Station 23", "The Fire Station", "nri-h-1b70234c4ece0af6255492e8"),
    ("The Esoteric Order of Dagon 24", "The Esoteric Order of Dagon", "nri-h-04a91268c2b7afffd26817db"),
    ("Entering through the Caves 24", "Entering through the Caves", "nri-h-03dd1ed10876ac8ee6d9eb7e"),
    ("The Last Train out of Innsmouth 25", "The Last Train out of Innsmouth", "nri-h-7b4e91617daf61336c70a8cf"),
    ("Playing the Hero 27", "Playing the Hero", "nri-h-db7abf043f1d139a51dd4c3f"),
    ("Rewards 28", "Rewards", "nri-h-ee0dadea1c956d399c954d44"),
)

# Source expression, stable target, expected number of occurrences.  Only the
# printed page token is replaced; enclosing punctuation remains untouched.
INTERNAL_REFERENCES = (
    ("Investigation, page 13)", "nri-h-579f6cee9279aa85f459d268", 1),
    ("Born Ginny Brewster, page 4", "nri-h-88dac050ed1ec36f91e4b6fe", 1),
    ("**P.A. Bazzledon** (page 4)", "nri-h-4ad8df2678e05f458f288662", 1),
    ("The Gilman House Hotel (page 12)", "nri-h-591edd5bcf58d378b27f28cc", 2),
    ("This is the Production Train Car (page 12)", "nri-h-a6cc5383a39e0ec74e8769a8", 1),
    ("Ginny's Trailer (page 15)", "nri-h-9af9701e3f85a91ab3b92009", 1),
    ("McGuire's Lab (page 16)", "nri-h-7eae4a85cb793259eb9ed053", 1),
    ("Brewster Residence (page 20)", "nri-h-f6184124151c4142421b1af0", 1),
    ("Stumble onto Set (page 21)", "nri-h-b741e3b3e62d814b592d4419", 1),
    ("The Railway Entrance (page 18)", "nri-h-6e9d2e67b27162302be156fe", 1),
    ("Into Innsmouth (page 22)", "nri-h-1e82f0c963d8a023793fa18e", 2),
    ("On Set (page 17)", "nri-h-4a3bb4ef4c7d762c63fef3b4", 1),
    ("It leads to The Brewster Residence (page 20)", "nri-h-f6184124151c4142421b1af0", 1),
    ("The caves can lead to The Brewster Residence (page 20)", "nri-h-f6184124151c4142421b1af0", 1),
    ("Stumbling onto Set (Page 21)", "nri-h-b741e3b3e62d814b592d4419", 1),
    ("The Esoteric Order of Dagon (page 24)", "nri-h-04a91268c2b7afffd26817db", 2),
    ("Table 2 (page 19)", "nri-t-tbl-p022-001", 1),
    ("Stumbling onto Set (page 21)", "nri-h-b741e3b3e62d814b592d4419", 1),
    ("The Fire Station, page 23)", "nri-h-1b70234c4ece0af6255492e8", 1),
    ("Shoggoth living in the basement (page 31)", "nri-h-f1f10a91537c50581b8ff2a6", 1),
    ("The Epic Finale (page 25)", "nri-h-9e45e6c31b8f513fdfc0cbcb", 2),
    ("Stumbling onto Set scene (page 21)", "nri-h-b741e3b3e62d814b592d4419", 1),
    ("The Brewster Residence (page 20)", "nri-h-f6184124151c4142421b1af0", 1),
    ("Zadok can be found at The Fire Station (page 23)", "nri-h-1b70234c4ece0af6255492e8", 1),
    ("Epic Finale (page 25)", "nri-h-9e45e6c31b8f513fdfc0cbcb", 1),
    ("Playing the Hero (page 27)", "nri-h-db7abf043f1d139a51dd4c3f", 1),
    ("Move to Playing the Hero (page 27)", "nri-h-db7abf043f1d139a51dd4c3f", 1),
    ("see box, page 26", "nri-c-227220bed3222454225d739d", 1),
    ("Mental Suggestion (page 30)", "nri-s-f6b536b49f6dbbac4907bda0", 1),
)

HANDOUT_ANCHORS = {
    "Handout 1-a": "nri-h-94205138fca7aa22510e0aca",
    "Handout 1-b": "nri-h-f8e3b2764c3b8f24c4c83bfa",
    "Handout 2": "nri-h-1701b4c74a5e58fac76c83d3",
}
HANDOUT_BODY_REFERENCE_COUNTS = {
    "Handout 1-a": 2,
    "Handout 1-b": 1,
    "Handout 2": 5,
}

# Stable anchor, source page index, unique prefix of the semantic target line.
# A body prefix is used only for The Innsmouth Terror because the printed
# source has no dedicated body heading for that contents entry.
BODY_HEADING_EXCEPTIONS = frozenset({"nri-h-e1e4abee7d665d664b579640"})
ANCHOR_TARGETS = (
    ("nri-h-1e7c84a4e9f5927381bc3dd4", 4, "## INTRODUCTION"),
    ("nri-h-47551367143746af596d3df2", 4, "### PREPARING FOR PLAY"),
    ("nri-h-5a1d3f11fa74d5bae7cbc1e7", 6, "### INVOLVING THE INVESTIGATORS"),
    ("nri-h-e1e4abee7d665d664b579640", 6, "The Innsmouth Terror assumes that"),
    ("nri-h-b1afc3d2767828f22a3d7b87", 7, "## DRAMATIS PERSONAE"),
    ("nri-h-88dac050ed1ec36f91e4b6fe", 7, "### Genevieve 'Ginny' Dubois"),
    ("nri-h-4ad8df2678e05f458f288662", 7, "### P.A. Bazzledon"),
    ("nri-h-cd6a958ad9223013558284e5", 8, "### Anna Díaz"),
    ("nri-h-96bc6a07453b7b19ecf06440", 8, "### Christopher McGuire"),
    ("nri-h-e0857213264e131c714fa054", 9, "### Sammy Brewster"),
    ("nri-h-eb898a1c80749cbdbb6a2241", 9, "### The Crew"),
    ("nri-h-bf21a56d117d74edde8c045e", 9, "## MINOR NPCs"),
    ("nri-h-29da96049102775b4dcc2b3a", 10, "## START: ARKHAM"),
    ("nri-h-0712e7e461fd02534398a35f", 10, "### ORNE LIBRARY"),
    ("nri-h-f81478a90f8941232106712e", 11, "### THE ARKHAM ADVERTISER"),
    ("nri-h-27b1ad17b7316f09136b83bc", 12, "### THE MISKATONIC PLAYHOUSE"),
    ("nri-h-640be35ee56417677f8750f5", 14, "## INNSMOUTH"),
    ("nri-h-e6c805ba31dc84425c90fbc6", 14, "### ARRIVAL"),
    ("nri-h-a6cc5383a39e0ec74e8769a8", 15, "### THE PRODUCTION TRAIN CAR"),
    ("nri-h-591edd5bcf58d378b27f28cc", 15, "### THE GILMAN HOUSE HOTEL"),
    ("nri-h-579f6cee9279aa85f459d268", 16, "## INVESTIGATION"),
    ("nri-h-988fb78c5b2cac516d5570bf", 16, "### THE PRODUCER'S OFFICE"),
    ("nri-h-62a8c5d75b10782b4e475a55", 17, "### AROUND THE TRAIN"),
    ("nri-h-1e72d19ab832ccee9c380a67", 17, "### Bazzledon's Office"),
    ("nri-h-9af9701e3f85a91ab3b92009", 18, "### Ginny's Trailer"),
    ("nri-h-7eae4a85cb793259eb9ed053", 19, "### McGuire's Lab"),
    ("nri-h-4a3bb4ef4c7d762c63fef3b4", 20, "### On Set"),
    ("nri-h-6e9d2e67b27162302be156fe", 21, "### The Railway Entrance"),
    ("nri-h-d5b878609b4bc64831d97150", 21, "### Moving Through the Caves"),
    ("nri-h-0377b0cfaf5eda9da814e2d8", 21, "### THE CAVE SYSTEM"),
    ("nri-t-tbl-p022-001", 22, "<table>"),
    ("nri-h-f6184124151c4142421b1af0", 23, "### THE BREWSTER RESIDENCE"),
    ("nri-h-b741e3b3e62d814b592d4419", 24, "### STUMBLING ONTO SET"),
    ("nri-h-1e82f0c963d8a023793fa18e", 25, "## INTO INNSMOUTH"),
    ("nri-h-d012304a399a1e520aefdba5", 25, "### The General Store"),
    ("nri-h-1b70234c4ece0af6255492e8", 26, "### The Fire Station"),
    ("nri-h-03dd1ed10876ac8ee6d9eb7e", 27, "### Entering through the Caves"),
    ("nri-h-04a91268c2b7afffd26817db", 27, "### The Esoteric Order of Dagon"),
    ("nri-h-9e45e6c31b8f513fdfc0cbcb", 28, "## THE EPIC FINALE"),
    ("nri-h-7b4e91617daf61336c70a8cf", 28, "### The Last Train out of Innsmouth"),
    ("nri-c-227220bed3222454225d739d", 29, "### MVR Class B1 'Olmstead'"),
    ("nri-h-db7abf043f1d139a51dd4c3f", 30, "### Playing the Hero"),
    ("nri-s-f6b536b49f6dbbac4907bda0", 30, "Bazzledon is on his knees, screaming"),
    ("nri-h-784561a8c2d6538c46980f3f", 31, "## EPILOGUE"),
    ("nri-h-ee0dadea1c956d399c954d44", 31, "### Rewards"),
    ("nri-h-216abf1f13f006ed96ddabfd", 32, "## CHARACTERS AND MONSTERS"),
    ("nri-h-f1f10a91537c50581b8ff2a6", 34, "### Shoggoth"),
    ("nri-h-cef5699cd74c24cd894040ee", 35, "## PRE-GENERATED INVESTIGATORS"),
    ("nri-h-9eb21ebd1012f4d0e1572e0a", 40, "## HANDOUTS"),
    ("nri-h-94205138fca7aa22510e0aca", 40, "### OFFICE OF THE VICE CHANCELLOR"),
    ("nri-h-f8e3b2764c3b8f24c4c83bfa", 41, "### OFFICE OF THE VICE CHANCELLOR"),
    ("nri-h-1701b4c74a5e58fac76c83d3", 42, "### Handout 2: note"),
)


def verify_reconstructed(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"missing RECONSTRUCTED_EN input: {path}")
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if len(raw) != RECONSTRUCTED_EN_BYTES or actual != RECONSTRUCTED_EN_SHA256:
        raise ValueError("RECONSTRUCTED_EN identity mismatch")
    return raw.decode("utf-8")


def verify_reconstructed_package(
    markdown_path: Path, qa_path: Path, images_dir: Path
) -> tuple[str, dict[str, object]]:
    markdown = verify_reconstructed(markdown_path)
    if not qa_path.is_file():
        raise ValueError(f"missing RECONSTRUCTED_EN QA input: {qa_path}")
    qa_raw = qa_path.read_bytes()
    qa_hash = hashlib.sha256(qa_raw).hexdigest()
    if len(qa_raw) != RECONSTRUCTED_EN_QA_BYTES or qa_hash != RECONSTRUCTED_EN_QA_SHA256:
        raise ValueError("RECONSTRUCTED_EN QA identity mismatch")
    source_qa = json.loads(qa_raw)
    if source_qa.get("state") != "RECONSTRUCTED_EN_R0_READY_FOR_QA":
        raise ValueError("RECONSTRUCTED_EN QA state mismatch")
    if source_qa.get("missing_assets") != []:
        raise ValueError("RECONSTRUCTED_EN QA reports missing assets")

    links = reconstructed.IMAGE_LINK.findall(markdown)
    inventory = reconstructed.asset_inventory(links, images_dir)
    expected_inventory = source_qa.get("asset_inventory", {})
    if (
        inventory.get("link_count") != 136
        or inventory.get("asset_count") != 136
        or inventory.get("inventory_sha256") != reconstructed.FINAL_ASSET_INVENTORY_SHA256
        or expected_inventory.get("inventory_sha256") != inventory.get("inventory_sha256")
        or expected_inventory.get("asset_count") != 136
    ):
        raise ValueError("RECONSTRUCTED_EN full asset inventory mismatch")
    return markdown, {
        "markdown": {
            "path": "RECONSTRUCTED_EN.md",
            "byte_count": RECONSTRUCTED_EN_BYTES,
            "sha256": RECONSTRUCTED_EN_SHA256,
        },
        "qa": {
            "path": "RECONSTRUCTED_EN.qa.json",
            "byte_count": RECONSTRUCTED_EN_QA_BYTES,
            "sha256": RECONSTRUCTED_EN_QA_SHA256,
        },
        "asset_inventory": {
            "asset_count": inventory["asset_count"],
            "inventory_sha256": inventory["inventory_sha256"],
        },
    }


def project_reader_art(markdown: str) -> tuple[str, list[str]]:
    retained: list[str] = []

    def project(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in RETAINED_ASSETS:
            return ""
        retained.append(name)
        return f"![](assets/{name})\n"

    projected = IMAGE_LINE.sub(project, markdown)
    if len(retained) != len(RETAINED_ASSETS) or set(retained) != RETAINED_ASSETS:
        raise ValueError("reader-art allowlist projection mismatch")
    return projected, retained


def build_publication_base(markdown: str) -> tuple[str, dict[str, object]]:
    _, pages = reconstructed.split_pages(markdown)
    if set(pages) != set(range(46)):
        raise ValueError("MASTER_EN projection requires source pages 0..45")

    pages[0] = reconstructed.replace_once(
        pages[0], "<!-- mineru-page: 0 -->\nTHE\n\n#", "<!-- mineru-page: 0 -->\n#",
        "page 0 duplicate cover title suppression",
    )
    pages[3] = reconstructed.replace_once(
        pages[3], "CALL OF\nCTHULHU\n\nMiskatonic Repository\n", "",
        "page 3 reader badge suppression",
    )
    scoped = "\n".join(pages[index].rstrip() for index in range(43)) + "\n"
    projected, retained = project_reader_art(scoped)
    counts = {
        "page_markers": len(re.findall(r"(?m)^<!-- mineru-page: \d+ -->$", projected)),
        "image_links": len(re.findall(r"!\[\]\(assets/[^)]+\)", projected)),
        "tables": projected.count("<table>"),
        "headings": len(re.findall(r"(?m)^#{1,6} ", projected)),
    }
    expected = {"page_markers": 43, "image_links": 33, "tables": 51, "headings": 155}
    if counts != expected or "<!-- mineru-page: 43 -->" in projected:
        raise ValueError(f"MASTER_EN publication-base counts mismatch: {counts}")
    if "612cbab6308b805c21f9f4f547e1c19d422e1f1ff62e946693a96d6cf1bff0e9" in projected:
        raise ValueError("failed Karen crop leaked into MASTER_EN")
    if EXCLUDED_LETTER_SEAL_ASSET in projected:
        raise ValueError("letter seal crop leaked into reader-facing MASTER_EN")
    qa: dict[str, object] = {
        "state": "MASTER_EN_PUBLICATION_BASE_READY_FOR_NAVIGATION",
        "stage_contract": "reader_editorial_projection_only",
        "included_page_indices": list(range(43)),
        "excluded_page_indices": [43, 44, 45],
        "retained_assets": [f"assets/{name}" for name in retained],
        "counts": counts,
        "operations": {
            "scenario_scope_exclusions": 3,
            "reader_art_suppressions": 103,
            "retained_reader_assets": 33,
            "service_badge_suppressions": 1,
            "duplicate_cover_title_suppressions": 1,
        },
    }
    return projected, qa


def suppress_content_warnings(markdown: str) -> tuple[str, dict[str, int]]:
    block = (
        "## CONTENT WARNINGS\n\n"
        "Alcoholism, Loss of Control, Sacrifice\n\n"
        "The use of safety tools such as pre-game discussion, the X-card, Lines and Veils, "
        "and an open table policy are encouraged to ensure that the players have an enjoyable game.\n"
    )
    if markdown.count(block) != 1:
        raise ValueError("content-warning publication suppression binding mismatch")
    return markdown.replace(block, "", 1), {"content_warning_blocks_suppressed": 1}


def project_handout_reader_flow(markdown: str) -> tuple[str, dict[str, int]]:
    """Keep full handouts only in the appendix and link scenario references."""
    preamble, pages = reconstructed.split_pages(markdown)
    if preamble.strip():
        raise ValueError("unexpected publication-base preamble")

    letter_pattern = re.compile(
        r"(?ms)^### OFFICE OF THE VICE CHANCELLOR MISKATONIC UNIVERSITY Arkham, Mass\.\n"
        r".*?^\(See page 39 for \*\*Handout 1-b\*\*\)\n?"
    )
    pages[13], letter_suppressions = letter_pattern.subn("", pages[13], count=1)
    if letter_suppressions != 1:
        raise ValueError("body Handout 1-a duplicate binding mismatch")

    keeper_match = re.search(
        r"(?m)^\*\*Keeper note:\*\* LLFRFL are directions .+$", pages[18]
    )
    if keeper_match is None:
        raise ValueError("body Handout 2 Keeper note binding mismatch")
    keeper_note = keeper_match.group(0)
    note_pattern = re.compile(
        r"(?ms)^Hey G,\n.*?^\*\*Keeper note:\*\* LLFRFL are directions [^\n]+\n?"
    )
    pages[18], note_suppressions = note_pattern.subn("", pages[18], count=1)
    if note_suppressions != 1:
        raise ValueError("body Handout 2 duplicate binding mismatch")

    appendix_note = (
        "### Handout 2: note\n\n"
        "Hey G,\n"
        "Wanted to drop in and see you, but your crew weren't thrilled to have me about. "
        "If you want to catch up, the old tunnel route is blocked, so you have to take a "
        "detour. It's LLFRFL.\n\n"
        "Sammy\n\n"
        + keeper_note
    )
    pages[42], appendix_consolidations = re.subn(
        r"(?ms)^Hey G,\n.*\Z",
        appendix_note + "\n",
        pages[42],
        count=1,
    )
    if appendix_consolidations != 1:
        raise ValueError("Handout 2 appendix consolidation binding mismatch")

    linked_references = 0
    for label, expected_count in HANDOUT_BODY_REFERENCE_COUNTS.items():
        before = f"**{label}**"
        after = f"[**{label}**](#{HANDOUT_ANCHORS[label]})"
        actual_count = sum(pages[index].count(before) for index in range(40))
        if actual_count != expected_count:
            raise ValueError(
                f"body handout reference binding mismatch for {label}: "
                f"expected {expected_count}, found {actual_count}"
            )
        for index in range(40):
            pages[index] = pages[index].replace(before, after)
        linked_references += actual_count

    output = "\n".join(pages[index].rstrip() for index in range(43)) + "\n"
    return output, {
        "body_handout_duplicates_suppressed": letter_suppressions + note_suppressions,
        "keeper_notes_relocated_to_appendix": 1,
        "appendix_handout_duplicates_suppressed": appendix_consolidations,
        "body_handout_links": linked_references,
    }


def project_internal_references(markdown: str) -> tuple[str, dict[str, int]]:
    ordinary = 0
    # Longer expressions must bind first because several short labels (for
    # example, ``Brewster Residence``) are contained in a longer reference to
    # the same target.
    for before, anchor, expected_count in sorted(
        INTERNAL_REFERENCES, key=lambda row: len(row[0]), reverse=True
    ):
        actual_count = markdown.count(before)
        if actual_count != expected_count:
            raise ValueError(
                f"internal reference binding mismatch for {before!r}: "
                f"expected {expected_count}, found {actual_count}"
            )
        after, page_count = PAGE_TOKEN.subn(f"[link](#{anchor})", before)
        if page_count != 1:
            raise ValueError(f"internal reference has {page_count} page tokens: {before!r}")
        markdown = markdown.replace(before, after)
        ordinary += expected_count

    if ordinary != 33:
        raise ValueError(f"ordinary internal-reference count mismatch: {ordinary}")
    return markdown, {"ordinary_page_links": ordinary}


def project_contents(markdown: str) -> tuple[str, dict[str, int]]:
    toc_end = markdown.find("<!-- mineru-page: 4 -->")
    if toc_end < 0:
        raise ValueError("contents boundary marker is missing")
    toc = markdown[:toc_end]
    body = markdown[toc_end:]

    for label, page, anchor in SECTION_GROUPS:
        before = f"## {label} {page}"
        after = f"## [{label}](#{anchor})"
        if toc.count(before) != 1:
            raise ValueError(f"TOC group binding mismatch: {before}")
        toc = toc.replace(before, after, 1)
    for before, label, anchor in TOC_ENTRIES:
        if toc.count(before) != 1:
            raise ValueError(f"TOC leaf binding mismatch: {before}")
        toc = toc.replace(before, f"[{label}](#{anchor})", 1)
    return toc + body, {"toc_group_links": 11, "toc_leaf_links": 34, "toc_links": 45}


def _insert_anchor_before_prefix(page: str, anchor: str, prefix: str) -> str:
    lines = page.splitlines(keepends=True)
    matches = [index for index, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(
            f"anchor target binding mismatch for {anchor}: prefix={prefix!r}, matches={len(matches)}"
        )
    index = matches[0]
    lines.insert(index, f'<a id="{anchor}"></a>\n')
    return "".join(lines)


def insert_target_anchors(markdown: str) -> tuple[str, dict[str, int]]:
    preamble, pages = reconstructed.split_pages(markdown)
    if preamble.strip():
        raise ValueError("unexpected publication-base preamble")
    for anchor, page_index, prefix in ANCHOR_TARGETS:
        if f'<a id="{anchor}"></a>' in markdown:
            raise ValueError(f"anchor already exists before projection: {anchor}")
        pages[page_index] = _insert_anchor_before_prefix(pages[page_index], anchor, prefix)
    output = "\n".join(pages[index].rstrip() for index in range(43)) + "\n"
    return output, {"target_anchors": len(ANCHOR_TARGETS)}


def validate_semantic_anchor_alignment(markdown: str) -> None:
    """Require heading-class anchors to land on headings, not nearby prose."""
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        match = re.fullmatch(r'<a id="(nri-h-[^"]+)"></a>', line)
        if not match or match.group(1) in BODY_HEADING_EXCEPTIONS:
            continue
        next_index = index + 1
        while next_index < len(lines) and not lines[next_index].strip():
            next_index += 1
        if next_index >= len(lines) or not re.match(r"^#{1,6} ", lines[next_index]):
            raise ValueError(
                f"heading anchor is not aligned to a heading: {match.group(1)}"
            )


def strip_technical_comments(markdown: str) -> tuple[str, dict[str, int]]:
    page_comments = len(re.findall(r"(?m)^<!-- mineru-page: \d+ -->$", markdown))
    table_comments = markdown.count("<!-- table-evidence:")
    reconstructed_comments = markdown.count("RECONSTRUCTED_EN candidate")
    cleaned = TECHNICAL_COMMENT.sub("", markdown)
    cleaned = re.sub(
        r"(?m)^<!-- Innsmouth RECONSTRUCTED_EN candidate;[^\n]*-->[ \t]*\n?",
        "",
        cleaned,
    )
    cleaned = re.sub(
        r"(?m)^<!-- All source pages 0-45 retained;[^\n]*-->[ \t]*\n?",
        "",
        cleaned,
    )
    cleaned = cleaned.lstrip("\n")
    if "<!-- mineru-page:" in cleaned or "<!-- table-evidence:" in cleaned:
        raise ValueError("technical comments leaked into reader MASTER_EN")
    return cleaned, {
        "page_comments_removed": page_comments,
        "table_comments_removed": table_comments,
        "reconstruction_comments_removed": reconstructed_comments,
    }


def validate_master_en(markdown: str) -> dict[str, int]:
    anchors = re.findall(r'<a id="([^"]+)"></a>', markdown)
    fragments = re.findall(r"\]\(#([^\)]+)\)", markdown)
    broken = sorted(set(fragments) - set(anchors))
    page_refs = PAGE_TOKEN.findall(markdown)
    counts = {
        "page_markers": markdown.count("<!-- mineru-page:"),
        "table_evidence_comments": markdown.count("<!-- table-evidence:"),
        "image_links": len(re.findall(r"!\[\]\(assets/[^)]+\)", markdown)),
        "tables": markdown.count("<table>"),
        "headings": len(re.findall(r"(?m)^#{1,6} ", markdown)),
        "anchors": len(anchors),
        "fragments": len(fragments),
        "broken_fragments": len(broken),
        "ordinary_page_links": markdown.count("[link](#nri-"),
        "external_page_references": len(page_refs),
    }
    expected = {
        "page_markers": 0,
        "table_evidence_comments": 0,
        "image_links": 33,
        "tables": 51,
        "headings": 153,
        "anchors": 52,
        "fragments": 86,
        "broken_fragments": 0,
        "ordinary_page_links": 33,
        "external_page_references": 3,
    }
    if counts != expected:
        raise ValueError(f"final MASTER_EN counts mismatch: {counts}; broken={broken}")
    if len(set(anchors)) != 52:
        raise ValueError("duplicate final MASTER_EN anchors")
    validate_semantic_anchor_alignment(markdown)
    fire_station = "to Zadok Allen (The Fire Station, [link](#nri-h-1b70234c4ece0af6255492e8))."
    if markdown.count(fire_station) != 1:
        raise ValueError("Fire Station punctuation-preservation seed case failed")
    body, boundary, appendix = markdown.partition("## HANDOUTS\n")
    if not boundary:
        raise ValueError("Handout appendix boundary is missing")
    if "### OFFICE OF THE VICE CHANCELLOR MISKATONIC UNIVERSITY" in body:
        raise ValueError("body Handout 1-a duplicate remains")
    if "Wanted to drop in and see you, but your crew weren't thrilled" in body:
        raise ValueError("body Handout 2 duplicate remains")
    for label, expected_count in HANDOUT_BODY_REFERENCE_COUNTS.items():
        linked = f"[**{label}**](#{HANDOUT_ANCHORS[label]})"
        if body.count(linked) != expected_count:
            raise ValueError(f"body {label} link count mismatch")
    if appendix.count("**Keeper note:** LLFRFL are directions") != 1:
        raise ValueError("Handout 2 Keeper note was not conserved in appendix")
    if appendix.count("### Handout 2: note") != 1 or appendix.count("Hey G,") != 1:
        raise ValueError("Handout 2 appendix was not consolidated to one block")
    if "**Handout 2**: note" in appendix or "L L F R F L" in appendix:
        raise ValueError("obsolete duplicate Handout 2 text remains in appendix")
    if markdown.count("Call of Cthulhu: Keeper Rulebook.") != 3:
        raise ValueError("external Keeper Rulebook references were not conserved")
    if "CONTENT WARNINGS" in markdown or "Alcoholism, Loss of Control, Sacrifice" in markdown:
        raise ValueError("content-warning block remains in reader MASTER_EN")
    return counts


def build_master_en(markdown: str) -> tuple[str, dict[str, object]]:
    output, qa = build_publication_base(markdown)
    output, handouts = project_handout_reader_flow(output)
    output, internal = project_internal_references(output)
    output, toc = project_contents(output)
    output, content_warnings = suppress_content_warnings(output)
    output, anchor_counts = insert_target_anchors(output)
    output, comment_counts = strip_technical_comments(output)
    final_counts = validate_master_en(output)
    qa.update(
        {
            "state": "MASTER_EN_READER_PACKAGE_READY",
            "navigation": {**handouts, **internal, **toc, **anchor_counts},
            "editorial_suppressions": content_warnings,
            "technical_comment_cleanup": comment_counts,
            "final_counts": final_counts,
            "rules": {
                "internal_reference_rule": "replace_only_printed_page_token_preserve_outer_punctuation",
                "handout_reference_rule": "link_visible_handout_number_to_appendix",
                "handout_duplicate_rule": "suppress_body_duplicates_and_consolidate_appendix_handout_2",
                "toc_rule": "link_11_groups_and_34_leaf_entries",
                "anchor_rule": "52_explicit_semantic_targets_with_heading_alignment",
                "technical_comment_rule": "strip_from_reader_master_after_page_scoped_projection",
                "content_warning_rule": "suppress_exact_source_block_at_master_en_publication_stage",
            },
        }
    )
    return output, qa


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def retained_asset_inventory(images_dir: Path) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for name in sorted(RETAINED_ASSETS):
        path = images_dir / name
        if not path.is_file():
            raise ValueError(f"missing retained MASTER_EN asset: {path}")
        rows.append(
            {
                "path": f"assets/{name}",
                "byte_count": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    raw = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    inventory_hash = hashlib.sha256(raw).hexdigest()
    if inventory_hash != RETAINED_ASSET_INVENTORY_SHA256:
        raise ValueError(f"retained asset inventory mismatch: {inventory_hash}")
    return {
        "asset_count": len(rows),
        "total_bytes": sum(int(row["byte_count"]) for row in rows),
        "inventory_sha256": inventory_hash,
        "files": rows,
    }


def publish_package(
    reconstructed_md: Path,
    reconstructed_qa: Path,
    reconstructed_images: Path,
    target: Path,
) -> dict[str, object]:
    if target.exists():
        raise ValueError(f"refusing to overwrite existing MASTER_EN package: {target}")
    stage = target.with_name(target.name + ".stage")
    if stage.exists():
        raise ValueError(f"staging directory already exists: {stage}")
    source, source_identity = verify_reconstructed_package(
        reconstructed_md, reconstructed_qa, reconstructed_images
    )
    first = build_master_en(source)
    second = build_master_en(source)
    if first != second:
        raise ValueError("MASTER_EN two-build identity mismatch")
    markdown, qa = first
    inventory = retained_asset_inventory(reconstructed_images)
    markdown_bytes = markdown.encode("utf-8")
    qa["input"] = source_identity
    qa["markdown"] = {
        "path": "MASTER_EN.md",
        "byte_count": len(markdown_bytes),
        "sha256": hashlib.sha256(markdown_bytes).hexdigest(),
    }
    qa["asset_inventory"] = inventory
    stage.mkdir(parents=True)
    try:
        (stage / "MASTER_EN.md").write_bytes(markdown_bytes)
        (stage / "MASTER_EN.qa.json").write_text(
            json.dumps(qa, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        assets = stage / "assets"
        assets.mkdir()
        for name in sorted(RETAINED_ASSETS):
            shutil.copyfile(reconstructed_images / name, assets / name)
        if len(list(assets.iterdir())) != len(RETAINED_ASSETS):
            raise ValueError("published MASTER_EN asset count mismatch")
        stage.rename(target)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise
    return {
        "target": str(target),
        "markdown": qa["markdown"],
        "asset_count": inventory["asset_count"],
        "asset_inventory_sha256": inventory["inventory_sha256"],
        "counts": qa["final_counts"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reconstructed-md", type=Path, required=True)
    parser.add_argument("--reconstructed-qa", type=Path, required=True)
    parser.add_argument("--reconstructed-images", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    args = parser.parse_args()
    result = publish_package(
        args.reconstructed_md,
        args.reconstructed_qa,
        args.reconstructed_images,
        args.target,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    print("INNSMOUTH_MASTER_EN_PUBLISHED")


if __name__ == "__main__":
    main()
