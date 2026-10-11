from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE_PDF = Path(
    r"D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\1923_The Innsmouth Terror\The Innsmouth terror.pdf"
)
REFERENCE_KEEPER = Path(
    r"D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\1_Сценарии\Компания\1928 Побег из Инсмута\Террор в инсмуте\For_Keeper\KeeperBook_v6.md"
)
REFERENCE_PDF = Path(
    r"D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\1_Сценарии\Компания\1928 Побег из Инсмута\Террор в инсмуте\Pdf\The_Innsmouth_Terror_RU.pdf"
)
EXPECTED_SOURCE_SHA256 = "CFD72DD3B8702C07750DCBB9F721A704793D6D474167B288922E6F7EBEEA561F"
EXPECTED_KEEPER_SHA256 = "E1C889ADB5676798D7E296E4231040FA730029A7BA40AD515BF97059F5F78BA7"
EXPECTED_PDF_SHA256 = "D89BA390B296211692419D08F8E8F84CB0D393B54E94489531542BB5A0E08FC5"
OLD_INNSMOUTH_ROOTS = (
    "CoC/Working/Scenarios/The_Innsmouth_Terror",
    "CoC/Output/Scenarios/The_Innsmouth_Terror",
)
STRUCTURED_TEXT_PARAGRAPH_GAP = 5.25
STRUCTURED_TEXT_LINE_TOLERANCE = 2.4


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path).replace("\\", "/")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_record(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256_file(path) if path.exists() else None,
        "last_write_time_utc": dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat()
        if path.exists()
        else None,
    }


def run_command(command: list[str]) -> dict[str, Any]:
    started = now_utc()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "command": command,
        "started_at_utc": started,
        "finished_at_utc": now_utc(),
        "returncode": completed.returncode,
        "stdout": completed.stdout[-8000:],
        "stderr": completed.stderr[-8000:],
    }


def command_is_expected_gate(record: dict[str, Any]) -> bool:
    stdout = str(record.get("stdout") or "")
    command = " ".join(str(part) for part in record.get("command", []))
    if "normalize-source-text" in command and "status=needs_review" in stdout:
        return True
    if "source-text-qa" in command and "status=needs_review" in stdout:
        return True
    if "reconstruct-column-ocr" in command and "status=needs_review" in stdout:
        return True
    if "classify-images" in command and "status=needs_review" in stdout:
        return True
    if "prepare-image-approval" in command and ("status=needs_review" in stdout or "status=pending" in stdout):
        return True
    if "build-art-placement-manifest" in command and "status=needs_review" in stdout:
        return True
    return False


def normalize_reader_text(text: str) -> str:
    text = re.sub(r"<!--\s*source-page-\d{3}\s*-->", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def compare_markdown(candidate: Path, reference: Path) -> dict[str, Any]:
    if not candidate.exists() or not reference.exists():
        return {"candidate": rel(candidate), "reference": str(reference), "status": "missing_input"}
    candidate_text = candidate.read_text(encoding="utf-8", errors="replace")
    reference_text = reference.read_text(encoding="utf-8", errors="replace")
    candidate_norm = normalize_reader_text(candidate_text)
    reference_norm = normalize_reader_text(reference_text)
    return {
        "candidate": rel(candidate),
        "reference": str(reference),
        "byte_identical": sha256_file(candidate) == sha256_file(reference),
        "normalized_reader_text_identical": candidate_norm == reference_norm,
        "candidate_sha256": sha256_file(candidate),
        "reference_sha256": sha256_file(reference),
        "candidate_normalized_sha256": sha256_text(candidate_norm),
        "reference_normalized_sha256": sha256_text(reference_norm),
        "candidate_chars": len(candidate_text),
        "reference_chars": len(reference_text),
        "candidate_source_pages": len(re.findall(r"<!--\s*source-page-\d{3}\s*-->", candidate_text)),
        "reference_source_pages": len(re.findall(r"<!--\s*source-page-\d{3}\s*-->", reference_text)),
    }


def cleanup_source_candidate(source: Path, target: Path, report: Path) -> dict[str, Any]:
    started = now_utc()
    applied: list[dict[str, Any]] = []
    returncode = 0
    stdout = ""
    stderr = ""
    result_findings: list[dict[str, Any]] = []
    replacements = [
        {
            "code": "remove_page_007_ocr_noise",
            "old": "\n(G YBER’ NO L7H)\nDerr or (i 2 Wis ty ee\n\n<!-- source-page-008 -->",
            "new": "\n\n<!-- source-page-008 -->",
            "required": True,
        },
        {
            "code": "remove_page_008_ocr_noise",
            "old": (
                "\n\n4 _ ” \"\n. »\n\n- rs »\n\n4 f\nam\n\ny\n"
                "Genevieve ‘Ginny’ Dubois\nvi\ni Y - i*) :\nP.A. Bazzledon\n\n<!-- source-page-009 -->"
            ),
            "new": "\n\n<!-- source-page-009 -->",
            "required": True,
        },
        {
            "code": "join_bazzledon_leader_line",
            "old": "broken. At night his dreams are wracked by Mother Hydra, the\n\n. leader of the Deep Ones.",
            "new": "broken. At night his dreams are wracked by Mother Hydra, the\nleader of the Deep Ones.",
            "required": True,
        },
        {
            "code": "repair_patty_statline_spacing",
            "old": "STR50 CON55_ SIZ65 DEX 75 INT70",
            "new": "STR50 CON55 SIZ65 DEX 75 INT70",
            "required": True,
        },
        {
            "code": "remove_page_037_ocr_noise",
            "old": "\nFor a further scenario featuring Patty, see Secret Santa by TA\nNewman.\n4 ‘ sg x\n5 om\n\n<!-- source-page-038 -->",
            "new": "\nFor a further scenario featuring Patty, see Secret Santa by TA\nNewman.\n\n<!-- source-page-038 -->",
            "required": True,
        },
        {
            "code": "repair_quechua",
            "old": "Language (Quechuah)",
            "new": "Language (Quechua)",
            "required": True,
        },
    ]
    try:
        text = source.read_text(encoding="utf-8")
        input_text_sha256 = sha256_text(text)
        for replacement in replacements:
            count = text.count(replacement["old"])
            if count != 1 and replacement["required"]:
                raise RuntimeError(f"{replacement['code']} expected 1 match, found {count}")
            if count:
                text = text.replace(replacement["old"], replacement["new"], 1)
            applied.append({"code": replacement["code"], "count": count})
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        status = "pass"
        stdout = f"status=pass output={rel(target)} replacements={len(applied)}\n"
    except Exception as exc:
        returncode = 1
        status = "blocked"
        input_text_sha256 = sha256_file(source) if source.exists() else None
        stderr = f"{type(exc).__name__}: {exc}"
        result_findings.append({"code": "source_cleanup_failed", "message": stderr})
    write_json(
        report,
        {
            "schema": "kb_creator.source_cleanup.v1",
            "generated_at_utc": now_utc(),
            "status": status,
            "input": file_record(source),
            "output": file_record(target),
            "input_text_sha256": input_text_sha256,
            "applied": applied,
            "findings": result_findings,
        },
    )
    return {
        "command": [sys.executable, rel(Path(__file__)), "--internal-source-cleanup", rel(source), rel(target)],
        "started_at_utc": started,
        "finished_at_utc": now_utc(),
        "returncode": returncode,
        "stdout": stdout[-8000:],
        "stderr": stderr[-8000:],
    }


def pdf_word_value(word: dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(word.get(key, default))
    except (TypeError, ValueError):
        return default


def is_pdf_text_noise(text: str) -> bool:
    stripped = re.sub(r"\s+", " ", text).strip()
    if not stripped:
        return True
    if re.fullmatch(r"\d{1,3}", stripped):
        return True
    if re.fullmatch(r"[|.·•_ -]+", stripped):
        return True
    tokens = stripped.split()
    if len(tokens) >= 12:
        single_letter = sum(1 for token in tokens if re.fullmatch(r"[A-Za-z]", token))
        if single_letter / len(tokens) > 0.55:
            return True
    return False


def is_running_header_noise(text: str, top: float) -> bool:
    if top > 65:
        return False
    normalized = re.sub(r"[^A-Za-z:]+", "", text).lower()
    return normalized in {"investigation", "dramatis", "personae", "start:"}


def words_to_structured_lines(words: list[dict[str, Any]], page_width: float, page_height: float) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for word in words:
        text = str(word.get("text") or "").strip()
        if not text:
            continue
        if word.get("upright") is False:
            continue
        top = pdf_word_value(word, "top")
        bottom = pdf_word_value(word, "bottom")
        if bottom < 28 or top > page_height - 34:
            continue
        filtered.append(word)

    lines: list[dict[str, Any]] = []
    midpoint = page_width / 2
    for word in sorted(filtered, key=lambda item: (round(pdf_word_value(item, "top"), 1), pdf_word_value(item, "x0"))):
        top = pdf_word_value(word, "top")
        word_center = (pdf_word_value(word, "x0") + pdf_word_value(word, "x1")) / 2
        word_column = "right" if word_center >= midpoint else "left"
        placed = False
        for line in lines:
            if line["column"] == word_column and abs(line["top"] - top) <= STRUCTURED_TEXT_LINE_TOLERANCE:
                line["words"].append(word)
                line["top"] = min(line["top"], top)
                line["bottom"] = max(line["bottom"], pdf_word_value(word, "bottom"))
                line["x0"] = min(line["x0"], pdf_word_value(word, "x0"))
                line["x1"] = max(line["x1"], pdf_word_value(word, "x1"))
                placed = True
                break
        if not placed:
            lines.append(
                {
                    "words": [word],
                    "top": top,
                    "bottom": pdf_word_value(word, "bottom"),
                    "x0": pdf_word_value(word, "x0"),
                    "x1": pdf_word_value(word, "x1"),
                    "column": word_column,
                }
            )

    structured: list[dict[str, Any]] = []
    for line in lines:
        ordered_words = sorted(line["words"], key=lambda item: pdf_word_value(item, "x0"))
        text = " ".join(str(item.get("text") or "").strip() for item in ordered_words).strip()
        if is_pdf_text_noise(text):
            continue
        if is_running_header_noise(text, pdf_word_value(line, "top")):
            continue
        column = line["column"]
        if line["x0"] < page_width * 0.18 and line["x1"] > page_width * 0.82:
            column = "full"
        structured.append(
            {
                "text": text,
                "top": round(line["top"], 2),
                "bottom": round(line["bottom"], 2),
                "x0": round(line["x0"], 2),
                "x1": round(line["x1"], 2),
                "column": column,
            }
        )
    return structured


def structured_line_kind(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith(("•", "-", "* ")):
        return "bullet"
    if stripped.lower().startswith("keeper note:"):
        return "keeper_note"
    alpha = re.sub(r"[^A-Za-z]", "", stripped)
    if alpha and len(alpha) >= 4 and alpha.upper() == alpha and len(stripped) <= 80:
        return "heading"
    return "paragraph"


def join_structured_lines(lines: list[str]) -> str:
    text = " ".join(line.strip() for line in lines if line.strip())
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"([A-Za-z])-\s+([a-z])", r"\1\2", text)
    return text


def lines_to_structured_blocks(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    current: list[str] = []
    current_kind = "paragraph"
    current_column = ""
    current_top: float | None = None
    current_bottom: float | None = None
    previous: dict[str, Any] | None = None

    def flush() -> None:
        nonlocal current, current_kind, current_column, current_top, current_bottom
        if not current:
            return
        text = join_structured_lines(current)
        if text and not is_pdf_text_noise(text):
            blocks.append(
                {
                    "kind": current_kind,
                    "text": text,
                    "column": current_column,
                    "top": current_top,
                    "bottom": current_bottom,
                }
            )
        current = []
        current_kind = "paragraph"
        current_column = ""
        current_top = None
        current_bottom = None

    for line in lines:
        text = str(line.get("text") or "").strip()
        kind = structured_line_kind(text)
        gap = 999.0
        if previous is not None:
            gap = pdf_word_value(line, "top") - pdf_word_value(previous, "bottom")
        starts_new = False
        if not current:
            starts_new = True
        elif line.get("column") != current_column:
            starts_new = True
        elif kind in {"heading", "bullet", "keeper_note"}:
            starts_new = True
        elif current_kind == "heading":
            starts_new = True
        elif kind == "paragraph" and current_kind in {"bullet", "keeper_note"}:
            starts_new = gap >= STRUCTURED_TEXT_PARAGRAPH_GAP
        elif gap >= STRUCTURED_TEXT_PARAGRAPH_GAP:
            starts_new = True
        if starts_new:
            flush()
            current_kind = kind
            current_column = str(line.get("column") or "")
            current_top = pdf_word_value(line, "top")
        current.append(text)
        current_bottom = pdf_word_value(line, "bottom")
        previous = line
    flush()
    return blocks


def ordered_structured_page_lines(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    full = [line for line in lines if line.get("column") == "full"]
    left = [line for line in lines if line.get("column") == "left"]
    right = [line for line in lines if line.get("column") == "right"]
    if left and right:
        return sorted(full, key=lambda line: line["top"]) + sorted(left, key=lambda line: line["top"]) + sorted(
            right, key=lambda line: line["top"]
        )
    return sorted(lines, key=lambda line: (line["top"], line["x0"]))


def render_structured_blocks_markdown(blocks: list[dict[str, Any]]) -> str:
    rendered: list[str] = []
    for block in blocks:
        text = str(block.get("text") or "").strip()
        if not text:
            continue
        kind = block.get("kind")
        if kind == "bullet":
            rendered.append("- " + text.lstrip("•*- ").strip())
        elif kind == "keeper_note":
            rendered.append("> " + text)
        else:
            rendered.append(text)
    return "\n\n".join(rendered)


def split_source_pages(text: str) -> dict[str, str]:
    parts = re.split(r"<!--\s*source-page-(\d{3})\s*-->", text)
    pages: dict[str, str] = {}
    for index in range(1, len(parts), 2):
        pages[parts[index]] = parts[index + 1]
    return pages


def strip_printed_page_number_residue(text: str) -> tuple[str, dict[str, Any]]:
    """Remove old source-PDF printed page numbers from extracted text pages."""
    parts = re.split(r"(<!--\s*source-page-(\d{3})\s*-->)", text)
    if len(parts) < 4:
        return text, {"count": 0, "items": []}
    rebuilt = [parts[0]]
    removed: list[dict[str, Any]] = []
    for index in range(1, len(parts), 3):
        marker = parts[index]
        page = parts[index + 1]
        body = parts[index + 2]
        old_page_number = int(page) - 4
        if page != "004" and old_page_number > 0:
            new_lines: list[str] = []
            for line_number, line in enumerate(body.splitlines(), start=1):
                if line.strip() == str(old_page_number):
                    removed.append({"source_page": page, "printed_page": old_page_number, "line": line_number})
                    continue
                new_lines.append(line)
            body = "\n".join(new_lines)
            if parts[index + 2].endswith("\n"):
                body += "\n"
        rebuilt.extend([marker, body])
    fixed = "".join(rebuilt)
    if text.endswith("\n") and not fixed.endswith("\n"):
        fixed += "\n"
    return fixed, {"count": len(removed), "items": removed}


INNSMOUTH_SOURCE_PAGE_OVERRIDES = {
    "005": """“We shall swim out to that brooding reef in the sea and dive down through black abysses to Cyclopean and many-columned Y’ha-nthlei, and in that lair of the Deep Ones we shall dwell amidst wonder and glory for ever.”

—H.P. Lovecraft, The Shadow over Innsmouth

INTRODUCTION

Lights, Camera, Action! It is 1923 and the era of silent film is in full swing. ‘The Innsmouth Terror’ will be a full-length three-act moving picture of a glamorous dame kidnapped by a tentacled monstrosity. In Technicolor!

But when a valuable tiara is loaned to, and then summarily lost by, the production company, the investigators are sent to find it. They meet a disenfranchised film crew plagued by delays, a high-strung starlet desperate to get filming over with, and a new-fangled camera that keeps breaking. The sense of simmering boredom and frustration grows as the film crew find little mirth or distraction in the creaking town of Innsmouth. Just a sea of stoic, salty, scornful faces wishing these city folks would leave them in peace.

Can the investigators uncover the truth before the stakes get raised and the Innsmouth Terror shifts into something more horrifying than what is captured through the lens of a camera?

PREPARING FOR PLAY

The Innsmouth Terror borrows heavily from the story The Shadow over Innsmouth (1936) by H.P. Lovecraft and utilizes some of the extended world building from Chaosium’s Escape from Innsmouth (1992). However, knowledge of these books is not required to play in, or run this investigation.

This scenario is intended to follow on from the scenario Stage Fright at the Playhouse, itself a sequel to Edge of Darkness. However, the scenario stands on its own and can be thought of as sharing a universe and some NPCs with these other scenarios, rather than being a direct sequel.

Short on time? The investigation can start in Innsmouth (Investigation, page 13). You’ll just need to quickly explain how the investigators got to this point.""",
    "006": """Keeper

KEEPER INFORMATION

The town of Innsmouth is a strange place. New England society has done its level best to ignore and forget this decrepit seaside village. Once a thriving port town, these days the harbor is full of silt, and only local fishing boats come and go with the tide. The train connection was abandoned not long after it was opened, the operators calling it the ‘least profitable line’ they had ever serviced. No one wanted to go to Innsmouth. And no one ever seemed to leave.

Back in the 1830s, Captain Obed Marsh of Innsmouth made a deal with the creatures that live below the Devil Reef, a dangerous set of shallows offshore from the harbor. The creatures supplied him with golden-alloy trinkets in exchange for glass and rubber jewelry. Marsh smelted down the trinkets and sold the pure gold, bringing wealth into the town and making the Marsh family rich and powerful. Those who benefited from the gold trade started a church they called the ‘Esoteric Order of Dagon’, a cult worshiping Dagon, god of the sea. The Esoteric Order slowly conquered the town of Innsmouth, driving out or converting everyone. But the embattled authorities fought back, jailing Obed Marsh and his disciples. The creatures, known as Deep Ones, then moved in to protect their worshipers, killing local law enforcement, and cementing Obed Marsh as the unspoken leader of the town of Innsmouth. This support came at a cost, and the members of the order were forced to take three oaths:

The First Oath: “Iä! Dagon! I, (speaker’s name), do solemnly swear that I will neither interfere with, nor inform upon, the activities of the Deep Ones. Iä! Dagon!”

The Second Oath: “Iä! Dagon! I, (speaker’s name) do solemnly swear that, if requested to do so, I will render aid to the Deep Ones to the best of my ability, and in whatever form or manner is required of me. Iä! Dagon!”

The Third Oath: “Iä! Dagon! I, (speaker’s name) do solemnly swear that I take this entity [a Deep One] as my wife/husband, that I shall take them to my home, and that with them I will endeavor to have and raise children, so that the race, and the faith, can continue to prosper. Iä! Dagon! Iä! Hydra!”

And so, with the third oath, Hybrids were born—offspring from the union between Deep One and human. Hybrids are born looking entirely human, but as they reach adulthood and mature, they begin to take on Deep One traits, such as enlarged eyes, webbed fingers and other markers of their heritage. This tends to be called the ‘Innsmouth look’. Eventually, most of the Hybrids become able to breathe underwater, and they slip into the sea and join their people down in the depths below.

Ginny Dubois (Born Ginny Brewster, page 4) is one such child. Precocious and unreasonable, as many children are, Ginny ran away to study theatre. In doing so, she set a new standard in outrageously awful acting. Ginny is the prototypical starlet: she bought her way into various roles using stolen family money, but eventually even that wasn’t enough to convince Directors to let her anywhere near a paying audience.

It is now 1923, and Ginny has struck luck once more. She is to play the leading role in an experimental new film, The Innsmouth Terror, and it’s going to make her a star! Sure, she has to go back home for filming, but she’s made a few adjustments to the script to poke fun at her backwards little village and their backwards ways.

When a Deep One artifact turned up on set, Ginny was asked to wear it as part of her costume. Disgusted by the idea, Ginny stole it and hid it in her old bedroom in Innsmouth.

Ginny doesn’t know that the Director of the film, P.A. Bazzledon (page 4) is himself in league with Mother Hydra. He hasn’t hired Ginny for her looks, her money, or her talent. He has hired her to be sacrificed to a Star Spawn of the god emperor Cthulhu in front of the citizenry of Innsmouth, to be an unwitting stooge in a terrifying ritual, and to let all of Innsmouth know the fate of those that would betray their oaths.

Table 1: timeline of events

| Time | Event |
| --- | --- |
| 1922 | Mother Hydra haunts the dreams of P.A. Bazzledon, driving him to Arkham. |
| 3 weeks ago | P.A Bazzledon arrives in Arkham. |
| 2 weeks ago | P.A Bazzledon convinces Henry Armitage to give him the Atlantean Jewel. |
| 10 days ago | The Production heads off to Innsmouth by train. |
| 9 days ago | Shooting begins, but is plagued by camera failures. |
| 3 days ago | Ginny Dubois steals the Jewel from McGuire’s lab. |
| Now | The investigators are dispatched to Innsmouth to recover the Jewel. |
| Evening of the 2nd day | The Epic finale begins filming. |""",
    "023": """Table 2: encounters in the caves

| 1D100 | Description |
| --- | --- |
| 1-5 | What Luck: The Investigators discover a quick and easy route to wherever they are trying to get to. It feels like a great little caper scampering up and down between all these rocks. |
| 6-10 | Footprints: The investigators spot fresh footprints, clear as day. On a successful Track roll, it’s clear they were made by someone wearing feminine shoes, likely of a similar build to Ginny or Anna. |
| 11-20 | A Cracked Clue: Investigators uncover a discarded piece of metal on the ground. Clearing it of dust, they realize it has a similar sheen to the pictures of the Jewel. But it’s the wrong shape. On a successful Appraise roll, they determine it is gold alloy, likely valuable. |
| 21-30 | A Foreboding Beach: The investigators get turned around and find themselves on a foreboding beach front. They’ve taken a wrong turn and the weather outside is getting worse. They can see a storm brewing directly over the half-submerged island, just offshore from Innsmouth. They’ll need to roll again. |
| 31-40 | A Hole in the Wall: There is a hole in the wall and some dim light on the other side. Just big enough for someone to peep through with their eyes. Any investigators looking through is confronted with an unforgettable image of eyes and tentacles and teeth, it is confused and horrifying, prompting a Sanity roll (1/1D4 loss). |
| 41-50 | A Blocked Path: The way forward is blocked by rubble. While investigators with a SIZ under 60 can crawl through, larger investigators must succeed on a DEX roll or take 1D4 damage from a sharp rock. |
| 51-60 | A Crumbled Cavern: There is a gap in the cave floor, a fishy smell rises up from it. While the gap is too small to fit down, an investigator could get stuck in it. Investigators need to pass a Jump or Climb roll, or risk falling in. Helping each other gives bonus die. Investigators getting stuck take 1D3 damage. |
| 61-70 | A Rancid Odor: Investigators gag as the tunnel is filled with the most vile stench. A smell of eggs and mold and death closes their windpipes. Investigators must succeed on a CON roll or take 1D3 points of damage as they cough up their insides. |
| 71-80 | Appalling Sounds: The horrendous sound of some unnatural creature noisily eating can be heard coming through the walls. It sounds as if it is ripping flesh from bone. This prompts a Sanity roll (0/1D2 loss). |
| 81-90 | Sudden Slap: As if from nowhere, something long and slithery whips out from between two large rocks and slaps at whatever light source the investigators are using. Everything suddenly goes dark, prompting a Sanity roll (0/1D3 loss). The investigator holding the light has a penalty die on the roll. |
| 91-95 | Watching Eyes: The investigator at the back of the group could swear they saw glowing eyes watching them from the shadows. They make a Sanity roll (0/1D4 loss) as they try to convince the others they are being followed. |
| 96-100 | Close encounters: Stepping out onto a ledge, below the investigators the cave fills with water. Some creature is swimming down there lazily in the water. The investigators must quietly cross the ledge or risk disturbing the Deep One in the water. One investigator must pass a Stealth roll for the group or they must find another route and roll again. On failing the Stealth roll, a Deep One emerges from the water and attempts to eat the investigators. |""",
    "031": """Playing the Hero

Investigators making their way determinedly up to the cliffs to the sacrifice experience no violent retribution from the Star- Spawn. In fact, the road clears ahead of them, as they rush up the winding path towards the climatic moment. The same events unfold if they are captured and brought up against their will.

As they approach, they see Christopher McGuire slowly turning the handle of the camera. His eyes are glazed and he is completely unresponsive. Ginny has been torn from the rock where she was tied, leaving behind a pentagram, clearly drawn in blood smeared across it. She is now in the clutches of the tentacles above, screaming for help. A number of Crew members lie in pieces around the site, their bodies seemingly torn to shreds by tentacles whilst attempting to save her.

Bazzledon is on his knees, screaming along to the chant from the town below. When the investigators arrive, his eyes snap open and he turns to them, rushing over to whichever investigator seems to most closely fit with the stereotype of the hero who saves the day. Failing that, he moves towards the investigator with the highest APP and casts the spell Mental Suggestion (page 30).

“You’ve always wanted to be on the silver screen haven’t you. I know you have, kid. This is your big moment, your time to shine. You’re gonna be a movie star. Take this,…” He hands the investigator a packet of Tum-Eez antacid “… run up that tentacle, and drop it in the things mouth. It’ll overwhelm it, sending it back to its watery grave.”

The investigator needs to pass a POW roll to resist the urge to do exactly what Bazzledon suggests. Though their fellow investigators may also attempt to stop them, by grappling with them. If the investigator fails the roll, they run towards the Star- Spawn, attempting to climb up one of the tentacles towards the creature’s terrifying mouth.

Allow the investigator a Hard DEX or Throw roll to determine if they manage to drop the Tum-Eez into the creature’s mouth before they are torn to shreds and eaten by the Star-Spawn. If they fail, then Bazzledon turns to the next investigator and repeats the lines verbatim:

“You’ve always wanted to be on the silver screen haven’t you. I know you have, kid…”

If the investigators succeed, they are, unfortunately, still torn to shreds by the monster. It turns out that antacids have no effect on the Star-Spawn. However, in achieving the final shot, the movie is completed, and Bazzledon turns around, cuts McGuire’s throat, and lopes off into the wilderness with the film under his arm.

Investigators who overcome Bazzledon’s charms see him for what he truly is, a madman, sending innocents to die. As they turn to flee, there is a sudden calm in the storm and the chanting ceases. With a cry of despair, Ginny Brewster is torn to shreds in front of the silent denizens of Innsmouth. Her body is dropped carelessly down into the ocean, not even given the honor of being food for the god shard. This prompts a Sanity roll (1/1D6).

Investigators may flee over the open ground away from Innsmouth, or come down to the train to find everyone dead, torn to shreds as they made a valiant attempt to escape from the monster on the train. By one way or another, the surviving investigators return to Arkham.""",
}


INNSMOUTH_OCCLUDED_TEXT_LAYER_RECOVERED_CONTENT = [
    {
        "id": "innsmouth-p031-occluded-epic-finale-captured",
        "page": "031",
        "source": "pdf_text_layer_only",
        "classification": "occluded_text_layer_recovered_content",
        "policy": "excluded_from_main_source",
        "reason": (
            "The block is present in the PDF text layer and is returned by multiple text extractors, "
            "but it is not visible in the rendered source page. It is retained as QA evidence and "
            "must not enter the accepted EN source unless explicitly included as an editorial/recovered-content note."
        ),
        "text": (
            "What if they’re captured?\n"
            "Captured investigators wake up tied-up on the cliff-face and see the Epic Finale playing out in front of them. "
            "The Star Spawn appears, Ginny tied to the rock. But instead of trudging up and being approached by Bazzledon, "
            "their bindings are cut loose by Bazzledon as he gives his pep talk and hands them the Tum-Eez."
        ),
    }
]


def apply_innsmouth_source_page_overrides(text: str) -> tuple[str, list[dict[str, Any]]]:
    parts = re.split(r"(<!--\s*source-page-(\d{3})\s*-->)", text)
    if len(parts) < 4:
        return text, []
    applied: list[dict[str, Any]] = []
    rebuilt = [parts[0]]
    for index in range(1, len(parts), 3):
        marker = parts[index]
        page = parts[index + 1]
        body = parts[index + 2]
        replacement = INNSMOUTH_SOURCE_PAGE_OVERRIDES.get(page)
        if replacement is not None:
            before = body.strip()
            after = replacement.strip()
            if before != after:
                applied.append(
                    {
                        "code": "innsmouth_source_page_layout_override",
                        "page": page,
                        "before_sha256": sha256_text(before),
                        "after_sha256": sha256_text(after),
                    }
                )
            body = f"\n\n{after}\n"
        rebuilt.extend([marker, body])
    fixed = "".join(rebuilt)
    if text.endswith("\n") and not fixed.endswith("\n"):
        fixed += "\n"
    return fixed, applied


def write_innsmouth_occluded_text_layer_artifact(path: Path) -> dict[str, Any]:
    data = {
        "schema": "kb_creator.occluded_text_layer_recovered_content.v1",
        "generated_at_utc": now_utc(),
        "policy": {
            "main_source": "exclude",
            "qa_retention": "required",
            "publication": "only_with_explicit_editorial_recovered_content_decision",
        },
        "items": INNSMOUTH_OCCLUDED_TEXT_LAYER_RECOVERED_CONTENT,
    }
    write_json(path, data)
    return {
        "code": "occluded_text_layer_recovered_content_recorded",
        "path": rel(path),
        "count": len(INNSMOUTH_OCCLUDED_TEXT_LAYER_RECOVERED_CONTENT),
    }


def source_anchor_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return slug or "anchor"


def line_anchor_id(page: str, kind: str, text: str) -> str:
    return f"src-p{page}-{kind}-{source_anchor_slug(text)}"


def compact_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def leading_source_phrase(line: str) -> str | None:
    line = compact_ws(line)
    if not line or line.startswith(("-", ">", "|")):
        return None
    if len(line) <= 90:
        return line
    sentence = re.split(r"(?<=[.!?])\s+", line, maxsplit=1)[0]
    if 18 <= len(sentence) <= 90:
        return sentence
    words = line.split()
    if len(words) < 3:
        return None
    return " ".join(words[: min(8, len(words))]).rstrip(",:;")


def source_page_anchor(page: str) -> dict[str, Any]:
    return {
        "source_anchor_id": f"src-p{page}-page",
        "source_page": page,
        "source_anchor_kind": "page",
        "source_anchor_text": f"source-page-{page}",
        "line_index": None,
    }


def source_art_anchor_candidates(source_text: str) -> dict[str, list[dict[str, Any]]]:
    """Build deterministic EN-source anchors before translation starts."""
    pages = split_source_pages(source_text)
    candidates: dict[str, list[dict[str, Any]]] = {}
    for page, body in pages.items():
        page_candidates: list[dict[str, Any]] = [source_page_anchor(page)]
        seen = {page_candidates[0]["source_anchor_id"]}
        lines = body.splitlines()
        for line_index, raw_line in enumerate(lines):
            line = raw_line.strip()
            if not line or line.startswith("|") or line.startswith("<!--"):
                continue
            next_significant = ""
            for follow_line in lines[line_index + 1 : line_index + 5]:
                follow = follow_line.strip()
                if follow:
                    next_significant = follow
                    break
            character_match = re.match(
                r"^([A-Z][A-Za-zÀ-ÖØ-öø-ÿ0-9.'‘’& -]{2,80}),\s*age\s+\d+\b",
                line,
            )
            if character_match:
                name = character_match.group(1).strip()
                anchor = {
                    "source_anchor_id": line_anchor_id(page, "character", name),
                    "source_page": page,
                    "source_anchor_kind": "character_lead",
                    "source_anchor_text": name,
                    "line_index": line_index,
                    "source_line": line,
                }
            elif (
                re.match(r"^[A-Z][A-Z0-9À-ÖØ-Þ &'‘’.-]{3,90}$", line)
                and re.match(r"^Age:\s*\d+\b", next_significant, flags=re.IGNORECASE)
            ):
                name = line
                anchor = {
                    "source_anchor_id": line_anchor_id(page, "character", name),
                    "source_page": page,
                    "source_anchor_kind": "character_lead",
                    "source_anchor_text": name,
                    "line_index": line_index,
                    "source_line": line,
                }
            elif re.match(r"^[A-Z0-9][A-Z0-9 &'’.,:;!?()/-]{3,90}$", line) and len(line.split()) <= 8:
                anchor = {
                    "source_anchor_id": line_anchor_id(page, "heading", line),
                    "source_page": page,
                    "source_anchor_kind": "heading_line",
                    "source_anchor_text": line,
                    "line_index": line_index,
                    "source_line": line,
                }
            elif re.match(r"^[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ0-9'‘’(). -]{2,}", line):
                phrase = leading_source_phrase(line)
                if not phrase:
                    continue
                anchor = {
                    "source_anchor_id": line_anchor_id(page, "lead", phrase),
                    "source_page": page,
                    "source_anchor_kind": "paragraph_lead",
                    "source_anchor_text": phrase,
                    "line_index": line_index,
                    "source_line": line,
                }
            else:
                continue
            if anchor["source_anchor_id"] not in seen:
                page_candidates.append(anchor)
                seen.add(anchor["source_anchor_id"])
        candidates[page] = page_candidates
    return candidates


def sorted_reader_art_placements(art_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    placements = [
        dict(placement)
        for placement in art_manifest.get("placements", [])
        if placement.get("emit_reader_art_block") is True
    ]

    def key(placement: dict[str, Any]) -> tuple[str, int, str]:
        page = str(placement.get("source_page") or "999")
        xref = str(placement.get("asset_id") or placement.get("placement_id") or "")
        xref_match = re.search(r"(\d+)", xref)
        return (page, int(xref_match.group(1)) if xref_match else 999999, xref)

    return sorted(placements, key=key)


def rect_center(rect: list[float]) -> tuple[float, float]:
    return ((float(rect[0]) + float(rect[2])) / 2.0, (float(rect[1]) + float(rect[3])) / 2.0)


def rect_distance(a: list[float], b: list[float]) -> float:
    ax, ay = rect_center(a)
    bx, by = rect_center(b)
    return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5


def art_anchor_bbox_score(image_rect: list[float], candidate_rect: list[float]) -> float:
    image_x, _ = rect_center(image_rect)
    candidate_x, _ = rect_center(candidate_rect)
    horizontal_penalty = abs(image_x - candidate_x) * 0.1
    image_top = float(image_rect[1])
    if float(candidate_rect[1]) <= image_top:
        return abs(image_top - float(candidate_rect[3])) + horizontal_penalty
    return 500.0 + abs(float(candidate_rect[1]) - image_top) + horizontal_penalty


def rect_horizontal_overlap(a: list[float], b: list[float]) -> float:
    left = max(float(a[0]), float(b[0]))
    right = min(float(a[2]), float(b[2]))
    return max(0.0, right - left)


def source_caption_text(text: str) -> str:
    return compact_ws(text).strip(" .,:;")


def likely_identity_caption(text: str) -> bool:
    text = source_caption_text(text)
    if not text or len(text) > 80:
        return False
    if re.search(r"\d", text):
        return False
    words = text.split()
    if not 1 <= len(words) <= 5:
        return False
    return all(
        word in {"Dr.", "Mr.", "Mrs.", "Ms."}
        or re.match(r"^[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ.'‘’&-]+$", word)
        for word in words
    )


def caption_identity_anchor(page: str, caption: dict[str, Any]) -> dict[str, Any]:
    text = source_caption_text(str(caption.get("text") or ""))
    return {
        "source_anchor_id": line_anchor_id(page, "caption", text),
        "source_page": page,
        "source_anchor_kind": "caption_identity",
        "source_anchor_text": text,
        "line_index": None,
        "source_anchor_caption_bbox": caption.get("bbox"),
        "source_anchor_caption_text": text,
    }


def image_caption_blocks(
    image_rect: list[float],
    text_blocks: list[dict[str, Any]],
    *,
    max_gap: float = 36.0,
) -> list[dict[str, Any]]:
    captions: list[dict[str, Any]] = []
    image_width = max(1.0, float(image_rect[2]) - float(image_rect[0]))
    image_center_x, _ = rect_center(image_rect)
    for block in text_blocks:
        bbox = block.get("bbox")
        text = source_caption_text(str(block.get("text") or ""))
        if not bbox or not text:
            continue
        gap = float(bbox[1]) - float(image_rect[3])
        overlap = rect_horizontal_overlap(image_rect, bbox)
        block_center_x, _ = rect_center(bbox)
        centered = abs(image_center_x - block_center_x) <= image_width * 0.35
        if -2.0 <= gap <= max_gap and (overlap > image_width * 0.12 or centered):
            captions.append({"text": text, "bbox": bbox, "gap": gap, "overlap": overlap, "position": "below"})
            continue
        vertical_overlap = max(0.0, min(float(image_rect[3]), float(bbox[3])) - max(float(image_rect[1]), float(bbox[1])))
        image_height = max(1.0, float(image_rect[3]) - float(image_rect[1]))
        right_gap = float(bbox[0]) - float(image_rect[2])
        left_gap = float(image_rect[0]) - float(bbox[2])
        side_overlap_tolerance = 8.0
        side_gap = min(
            max(0.0, right_gap) if right_gap >= -side_overlap_tolerance else 9999.0,
            max(0.0, left_gap) if left_gap >= -side_overlap_tolerance else 9999.0,
        )
        side_label_shape = (float(bbox[2]) - float(bbox[0])) <= 34.0 or len(text) <= 24
        if side_gap <= max_gap and vertical_overlap >= image_height * 0.12 and side_label_shape:
            captions.append(
                {
                    "text": text,
                    "bbox": bbox,
                    "gap": side_gap,
                    "overlap": vertical_overlap,
                    "position": "side",
                }
            )
    captions.sort(key=lambda item: (0 if item.get("position") == "below" else 1, float(item["gap"]), -float(item["overlap"])))
    return captions


def caption_candidate(
    placement: dict[str, Any],
    candidates: list[dict[str, Any]],
    pdf_layout: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not pdf_layout:
        return None
    page = str(placement.get("source_page") or "")
    xref = placement.get("source_xref") or re.sub(r"\D+", "", str(placement.get("asset_id") or ""))
    if not page or not xref:
        return None
    page_layout = (pdf_layout.get("pages") or {}).get(page, {})
    image_rects = (page_layout.get("images") or {}).get(str(int(xref)) if str(xref).isdigit() else str(xref), [])
    text_blocks = page_layout.get("text_blocks") or []
    if not image_rects or not text_blocks:
        return None
    character_candidates = [item for item in candidates if item.get("source_anchor_kind") == "character_lead"]
    for caption in image_caption_blocks(image_rects[0], text_blocks):
        caption_fold = source_caption_text(caption["text"]).casefold()
        for candidate in character_candidates:
            candidate_text = source_caption_text(str(candidate.get("source_anchor_text") or ""))
            if not candidate_text:
                continue
            candidate_fold = candidate_text.casefold()
            if caption_fold == candidate_fold or caption_fold.startswith(candidate_fold):
                matched = dict(candidate)
                matched["source_anchor_caption_bbox"] = caption.get("bbox")
                matched["source_anchor_caption_text"] = caption.get("text")
                return matched
        if likely_identity_caption(caption["text"]):
            return caption_identity_anchor(page, caption)
    return None


def build_pdf_layout_evidence(source_pdf: Path, xrefs: set[int]) -> dict[str, Any]:
    import fitz

    pages: dict[str, dict[str, Any]] = {}
    with fitz.open(source_pdf) as doc:
        for page_number, page in enumerate(doc, start=1):
            page_id = f"{page_number:03d}"
            page_record = {
                "page": page_id,
                "dimensions": [float(page.rect.width), float(page.rect.height)],
                "images": {},
                "text_blocks": [],
            }
            for image_info in page.get_images(full=True):
                xref = int(image_info[0])
                if xref not in xrefs:
                    continue
                rects = page.get_image_rects(xref)
                if rects:
                    page_record["images"][str(xref)] = [
                        [float(rect.x0), float(rect.y0), float(rect.x1), float(rect.y1)] for rect in rects
                    ]
            for block in page.get_text("blocks"):
                x0, y0, x1, y1, text, *_ = block
                clean = compact_ws(str(text))
                if not clean:
                    continue
                page_record["text_blocks"].append(
                    {
                        "bbox": [float(x0), float(y0), float(x1), float(y1)],
                        "text": clean,
                    }
                )
            if page_record["images"]:
                pages[page_id] = page_record
    return {
        "schema": "kb_creator.pdf_source_layout_evidence.v1",
        "source_pdf": str(source_pdf),
        "pages": pages,
    }


def attach_pdf_bboxes_to_source_candidates(
    candidates: dict[str, list[dict[str, Any]]], pdf_layout: dict[str, Any] | None
) -> dict[str, list[dict[str, Any]]]:
    if not pdf_layout:
        return candidates
    pages = pdf_layout.get("pages", {}) if isinstance(pdf_layout, dict) else {}
    enriched: dict[str, list[dict[str, Any]]] = {}
    for page, page_candidates in candidates.items():
        text_blocks = pages.get(page, {}).get("text_blocks", []) if isinstance(pages.get(page), dict) else []
        enriched_page: list[dict[str, Any]] = []
        for candidate in page_candidates:
            enriched_candidate = dict(candidate)
            text = compact_ws(str(candidate.get("source_anchor_text") or ""))
            if text and candidate.get("source_anchor_kind") != "page":
                needle = text.casefold()
                for block in text_blocks:
                    block_text = compact_ws(str(block.get("text") or ""))
                    block_folded = block_text.casefold()
                    if needle and (block_folded.startswith(needle) or needle in block_folded[:160]):
                        enriched_candidate["source_anchor_bbox"] = block.get("bbox")
                        enriched_candidate["source_anchor_bbox_text"] = block_text[:160]
                        break
            enriched_page.append(enriched_candidate)
        enriched[page] = enriched_page
    return enriched


def nearest_bbox_candidate(
    placement: dict[str, Any],
    candidates: list[dict[str, Any]],
    pdf_layout: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not pdf_layout:
        return None
    page = str(placement.get("source_page") or "")
    xref = placement.get("source_xref") or re.sub(r"\D+", "", str(placement.get("asset_id") or ""))
    if not page or not xref:
        return None
    page_layout = (pdf_layout.get("pages") or {}).get(page, {})
    image_rects = (page_layout.get("images") or {}).get(str(int(xref)) if str(xref).isdigit() else str(xref), [])
    if not image_rects:
        return None
    image_rect = image_rects[0]
    bbox_candidates = [item for item in candidates if item.get("source_anchor_bbox")]
    if not bbox_candidates:
        return None
    return min(bbox_candidates, key=lambda item: art_anchor_bbox_score(image_rect, item["source_anchor_bbox"]))


def placement_heading_character_candidate(
    placement: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Use a curated heading_id as semantic identity evidence for character art.

    This is not a final-layout coordinate rule. It only says the reviewed art
    placement belongs to the same semantic character heading in the accepted EN
    source. The downstream Keeper/HTML/PDF renderer can then place it in the
    rebuilt layout wherever that heading lands.
    """
    heading_id = str(placement.get("heading_id") or "").strip()
    if not heading_id:
        return None
    for candidate in candidates:
        if candidate.get("source_anchor_kind") != "character_lead":
            continue
        if source_anchor_slug(str(candidate.get("source_anchor_text") or "")) == heading_id:
            return candidate
    return None


def build_source_art_anchor_manifest(
    source_text: str,
    art_manifest: dict[str, Any],
    pdf_layout: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    source_candidates = attach_pdf_bboxes_to_source_candidates(source_art_anchor_candidates(source_text), pdf_layout)
    reader_placements = sorted_reader_art_placements(art_manifest)
    placements_by_page: dict[str, list[dict[str, Any]]] = {}
    for placement in reader_placements:
        placements_by_page.setdefault(str(placement.get("source_page") or ""), []).append(placement)

    findings: list[dict[str, Any]] = []
    anchored: list[dict[str, Any]] = []
    page_fallbacks = 0
    missing_runtime_src = 0
    for page, page_placements in sorted(placements_by_page.items()):
        candidates = source_candidates.get(page, [source_page_anchor(page)])
        character_candidates = [item for item in candidates if item["source_anchor_kind"] == "character_lead"]
        heading_candidates = [item for item in candidates if item["source_anchor_kind"] == "heading_line"]
        source_text_candidates = [item for item in candidates if item["source_anchor_kind"] in {"heading_line", "paragraph_lead"}]
        npc_index = 0
        heading_index = 0
        for placement in page_placements:
            role = str(placement.get("runtime_role") or placement.get("semantic_role") or "")
            caption = caption_candidate(placement, candidates, pdf_layout)
            role_promoted_from = None
            if caption is not None:
                anchor = caption
                method = "npc_caption_match"
                if role and role != "npc":
                    role_promoted_from = role
                    role = "npc"
            elif role == "npc" and (heading_match := placement_heading_character_candidate(placement, candidates)) is not None:
                anchor = heading_match
                method = "npc_heading_id_match"
            elif role == "npc" and npc_index < len(character_candidates):
                anchor = character_candidates[npc_index]
                method = "npc_order_on_source_page"
                npc_index += 1
            elif (nearest := nearest_bbox_candidate(placement, source_text_candidates, pdf_layout)) is not None:
                anchor = nearest
                method = "nearest_source_text_bbox"
            elif heading_index < len(heading_candidates):
                anchor = heading_candidates[heading_index]
                method = "source_heading_order_on_page"
                heading_index += 1
            elif source_text_candidates:
                anchor = source_text_candidates[0]
                method = "source_text_order_on_page"
            else:
                anchor = source_page_anchor(page)
                method = "page_fallback"
                page_fallbacks += 1
            runtime_src = placement.get("runtime_src")
            if not runtime_src:
                missing_runtime_src += 1
                findings.append(
                    {
                        "code": "reader_art_missing_runtime_src",
                        "placement_id": placement.get("placement_id"),
                        "source_page": page,
                    }
                )
            enriched = dict(placement)
            if role_promoted_from:
                enriched["source_identity_role_promoted_from"] = role_promoted_from
                enriched["runtime_role"] = "npc"
                enriched["semantic_role"] = "npc"
                enriched["production_role"] = "npc"
            enriched.update(
                {
                    "source_anchor_id": anchor["source_anchor_id"],
                    "source_anchor_kind": anchor["source_anchor_kind"],
                    "source_anchor_text": anchor["source_anchor_text"],
                    "source_anchor_method": method,
                    "source_anchor_line_index": anchor.get("line_index"),
                    "source_anchor_bbox": anchor.get("source_anchor_bbox"),
                    "source_anchor_caption_bbox": anchor.get("source_anchor_caption_bbox"),
                    "source_anchor_caption_text": anchor.get("source_anchor_caption_text"),
                }
            )
            anchored.append(enriched)

    accepted_npc_identity_methods = {"npc_caption_match", "npc_heading_id_match", "manual_identity_override"}
    npc_identity_findings = [
        {
            "code": "npc_art_identity_not_semantically_proven",
            "placement_id": item.get("placement_id"),
            "source_page": item.get("source_page"),
            "source_xref": item.get("source_xref"),
            "source_anchor_method": item.get("source_anchor_method"),
            "source_anchor_text": item.get("source_anchor_text"),
        }
        for item in anchored
        if str(item.get("runtime_role") or item.get("semantic_role") or "") == "npc"
        and item.get("source_anchor_method") not in accepted_npc_identity_methods
    ]
    findings.extend(npc_identity_findings)
    status = "fail" if missing_runtime_src or npc_identity_findings else "pass"
    manifest = {
        "schema": "kb_creator.source_art_anchor_manifest.v1",
        "generated_at_utc": now_utc(),
        "status": status,
        "source": {
            "anchor_authority": "accepted_en_source",
            "publication_contract": "source anchors are restored downstream into RU Keeper, HTML, and PDF",
            "bbox_evidence": bool(pdf_layout),
        },
        "counts": {
            "reader_placements": len(reader_placements),
            "anchored_placements": len(anchored),
            "page_fallbacks": page_fallbacks,
            "missing_runtime_src": missing_runtime_src,
            "npc_identity_checked": sum(
                1 for item in anchored if str(item.get("runtime_role") or item.get("semantic_role") or "") == "npc"
            ),
            "npc_identity_unverified": len(npc_identity_findings),
        },
        "source_anchor_candidates": source_candidates,
        "placements": anchored,
        "findings": findings,
    }
    report = {
        "schema": "kb_creator.source_art_anchor_report.v1",
        "generated_at_utc": manifest["generated_at_utc"],
        "status": status,
        "counts": manifest["counts"],
        "findings": findings,
        "sample": anchored[:10],
    }
    return manifest, report


def keeper_art_block_en(placement: dict[str, Any]) -> str | None:
    src = placement.get("runtime_src")
    placement_id = placement.get("placement_id")
    if not src or not placement_id:
        return None
    source_page = placement.get("source_page") or ""
    source_xref = placement.get("source_xref") or placement.get("asset_id") or ""
    anchor = placement.get("source_anchor_id") or ""
    role = placement.get("runtime_role") or placement.get("semantic_role") or "source_image"
    alt = str(placement_id)
    return (
        f'<div class="keeper-art-block source-art-anchor" data-placement-id="{placement_id}" '
        f'data-source-anchor-id="{anchor}" data-source-page="{source_page}" '
        f'data-source-xref="{source_xref}" data-role="{role}">\n'
        f'  <img src="../{src}" alt="{alt}">\n'
        "</div>"
    )


def build_keeperbook_en_with_source_art_anchors(source_text: str, anchor_manifest: dict[str, Any]) -> str:
    by_page: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for placement in anchor_manifest.get("placements", []):
        page = str(placement.get("source_page") or "")
        anchor = str(placement.get("source_anchor_id") or "")
        if not page or not anchor:
            continue
        by_page.setdefault(page, {}).setdefault(anchor, []).append(placement)

    parts = re.split(r"(<!--\s*source-page-(\d{3})\s*-->)", source_text)
    if len(parts) < 4:
        return source_text
    rebuilt = [parts[0]]
    emitted: set[str] = set()
    for index in range(1, len(parts), 3):
        marker = parts[index]
        page = parts[index + 1]
        body = parts[index + 2]
        anchors = source_art_anchor_candidates(f"<!-- source-page-{page} -->{body}").get(page, [source_page_anchor(page)])
        anchor_by_line = {item.get("line_index"): item for item in anchors if item.get("line_index") is not None}
        page_anchor = source_page_anchor(page)
        page_lines = body.splitlines()
        new_lines: list[str] = []
        page_level_blocks = by_page.get(page, {}).get(page_anchor["source_anchor_id"], [])
        if page_level_blocks:
            new_lines.append(f'<a id="{page_anchor["source_anchor_id"]}"></a>')
            for placement in page_level_blocks:
                block = keeper_art_block_en(placement)
                if block:
                    new_lines.append(block)
                    emitted.add(str(placement.get("placement_id")))
        for line_index, line in enumerate(page_lines):
            new_lines.append(line)
            anchor = anchor_by_line.get(line_index)
            if not anchor:
                continue
            placements = by_page.get(page, {}).get(anchor["source_anchor_id"], [])
            if placements:
                new_lines.append(f'<a id="{anchor["source_anchor_id"]}"></a>')
            for placement in placements:
                block = keeper_art_block_en(placement)
                if block:
                    new_lines.append(block)
                    emitted.add(str(placement.get("placement_id")))
        body_out = "\n".join(new_lines)
        if body.endswith("\n") and not body_out.endswith("\n"):
            body_out += "\n"
        rebuilt.extend([marker, body_out])
    text = "".join(rebuilt)
    if source_text.endswith("\n") and not text.endswith("\n"):
        text += "\n"
    return text


def build_source_art_anchor_layer(
    *,
    source_markdown: Path,
    art_manifest_path: Path,
    keeper_en_path: Path,
    source_anchor_manifest_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    started = now_utc()
    command = ["internal", "build-source-art-anchor-layer"]
    try:
        source_text = source_markdown.read_text(encoding="utf-8", errors="replace")
        art_manifest = read_json(art_manifest_path)
        xrefs = {
            int(placement.get("source_xref"))
            for placement in sorted_reader_art_placements(art_manifest)
            if str(placement.get("source_xref") or "").isdigit()
        }
        pdf_layout = build_pdf_layout_evidence(SOURCE_PDF, xrefs) if SOURCE_PDF.exists() else None
        anchor_manifest, report = build_source_art_anchor_manifest(source_text, art_manifest, pdf_layout)
        keeper_en = build_keeperbook_en_with_source_art_anchors(source_text, anchor_manifest)
        write_json(source_anchor_manifest_path, anchor_manifest)
        write_json(report_path, report)
        keeper_en_path.parent.mkdir(parents=True, exist_ok=True)
        keeper_en_path.write_text(keeper_en, encoding="utf-8")
        return {
            "command": command,
            "started_at_utc": started,
            "finished_at_utc": now_utc(),
            "returncode": 0 if report["status"] == "pass" else 1,
            "stdout": (
                f"status={report['status']} reader_placements={report['counts']['reader_placements']} "
                f"anchored={report['counts']['anchored_placements']} "
                f"page_fallbacks={report['counts']['page_fallbacks']}"
            ),
            "stderr": "",
        }
    except Exception as exc:
        return {
            "command": command,
            "started_at_utc": started,
            "finished_at_utc": now_utc(),
            "returncode": 1,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
        }


def source_structure_hazard_audit(source_markdown: Path, keeper_markdown: Path, report_path: Path) -> dict[str, Any]:
    started = now_utc()
    findings: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    try:
        source_text = source_markdown.read_text(encoding="utf-8", errors="replace")
        keeper_text = keeper_markdown.read_text(encoding="utf-8", errors="replace")
        source_pages = split_source_pages(source_text)
        keeper_pages = split_source_pages(keeper_text)

        expected_pages = {f"{page:03d}" for page in range(1, 47)}
        missing_pages = sorted(expected_pages - set(source_pages))
        unexpected_pages = sorted(set(source_pages) - expected_pages)
        checks.append(
            {
                "name": "source_page_marker_count",
                "source_pages": len(source_pages),
                "keeper_pages": len(keeper_pages),
                "missing_pages": missing_pages,
                "unexpected_pages": unexpected_pages,
            }
        )
        if missing_pages or unexpected_pages:
            findings.append(
                {"code": "source_page_marker_mismatch", "missing": missing_pages, "unexpected": unexpected_pages}
            )

        order_checks = [
            ("009", r"Anna D[ií]az, age 26", r"Christopher McGuire, age 37"),
            ("012", r"ORNE LIBRARY|Loring is not aware", r"THE ARKHAM ADVERTISER"),
            ("024", "THE BREWSTER RESIDENCE", "Asking Sammy about Ginny"),
            ("024", "Asking Sammy about Ginny", "Keeper note: in most cases"),
        ]
        for page_id, first, second in order_checks:
            page_text = source_pages.get(page_id, "")
            first_match = re.search(first, page_text)
            second_match = re.search(second, page_text)
            first_pos = first_match.start() if first_match else -1
            second_pos = second_match.start() if second_match else -1
            passed = first_pos >= 0 and second_pos >= 0 and first_pos < second_pos
            checks.append(
                {
                    "name": "reading_order",
                    "page": page_id,
                    "first": first,
                    "second": second,
                    "first_pos": first_pos,
                    "second_pos": second_pos,
                    "status": "pass" if passed else "blocked",
                }
            )
            if not passed:
                findings.append(
                    {
                        "code": "reading_order_anchor_failed",
                        "page": page_id,
                        "first": first,
                        "second": second,
                    }
                )

        long_blocks: list[dict[str, Any]] = []
        scrambled_blocks: list[dict[str, Any]] = []
        unquoted_keeper_notes: list[dict[str, Any]] = []
        for page_id, page_text in source_pages.items():
            blocks = [block.strip() for block in re.split(r"\n\s*\n+", page_text) if block.strip()]
            for block_index, block in enumerate(blocks, start=1):
                table_lines = [line.strip() for line in block.splitlines() if line.strip()]
                is_markdown_table = bool(table_lines) and all(line.startswith("|") and line.endswith("|") for line in table_lines)
                if len(block) > 2800 and not is_markdown_table:
                    long_blocks.append({"page": page_id, "block": block_index, "chars": len(block)})
                tokens = block.split()
                if len(tokens) >= 12:
                    single_letters = sum(1 for token in tokens if re.fullmatch(r"[A-Za-z]", token))
                    if single_letters / len(tokens) > 0.45:
                        scrambled_blocks.append(
                            {"page": page_id, "block": block_index, "sample": block[:160], "single_letter_ratio": single_letters / len(tokens)}
                        )
                if "Keeper note:" in block and not block.startswith(">"):
                    unquoted_keeper_notes.append({"page": page_id, "block": block_index, "sample": block[:160]})
        checks.append({"name": "long_paragraph_blocks", "threshold_chars": 2800, "items": long_blocks[:20]})
        checks.append({"name": "scrambled_visual_text_blocks", "items": scrambled_blocks[:20]})
        checks.append({"name": "keeper_note_blockquote_format", "items": unquoted_keeper_notes[:20]})
        if long_blocks:
            findings.append({"code": "long_paragraph_blocks", "count": len(long_blocks), "sample": long_blocks[:10]})
        if scrambled_blocks:
            findings.append({"code": "scrambled_visual_text_blocks", "count": len(scrambled_blocks), "sample": scrambled_blocks[:10]})
        if unquoted_keeper_notes:
            findings.append(
                {"code": "keeper_note_not_isolated_as_blockquote", "count": len(unquoted_keeper_notes), "sample": unquoted_keeper_notes[:10]}
            )

        status = "pass" if not findings else "blocked"
        stdout = f"status={status} findings={len(findings)} report={rel(report_path)}\n"
        returncode = 0 if status == "pass" else 1
    except Exception as exc:
        status = "blocked"
        returncode = 1
        stdout = ""
        findings.append({"code": "source_structure_audit_failed", "message": f"{type(exc).__name__}: {exc}"})
    write_json(
        report_path,
        {
            "schema": "kb_creator.source_structure_hazard_audit.v1",
            "generated_at_utc": now_utc(),
            "status": status,
            "source_markdown": file_record(source_markdown),
            "keeper_markdown": file_record(keeper_markdown),
            "checks": checks,
            "findings": findings,
        },
    )
    return {
        "command": [sys.executable, rel(Path(__file__)), "--internal-source-structure-audit", rel(source_markdown)],
        "started_at_utc": started,
        "finished_at_utc": now_utc(),
        "returncode": returncode,
        "stdout": stdout[-8000:],
        "stderr": "",
    }


def build_pymupdf_text_layer_source(config_path: Path, config: dict[str, Any], target: Path, report: Path) -> dict[str, Any]:
    started = now_utc()
    returncode = 0
    stdout = ""
    stderr = ""
    findings: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    try:
        import pdfplumber

        chunks: list[str] = []
        with pdfplumber.open(SOURCE_PDF) as doc:
            for index, page in enumerate(doc.pages, start=1):
                words = page.extract_words(
                    x_tolerance=2,
                    y_tolerance=3,
                    keep_blank_chars=False,
                    use_text_flow=False,
                    extra_attrs=["upright"],
                )
                lines = words_to_structured_lines(words, float(page.width), float(page.height))
                ordered_lines = ordered_structured_page_lines(lines)
                blocks = lines_to_structured_blocks(ordered_lines)
                page_text = render_structured_blocks_markdown(blocks)
                pages.append(
                    {
                        "page": index,
                        "lines": len(lines),
                        "blocks": len(blocks),
                        "columns": sorted({str(line.get("column")) for line in lines}),
                        "chars": len(page_text),
                    }
                )
                chunks.append(f"\n\n<!-- source-page-{index:03d} -->\n\n{page_text.strip()}\n")
        text = "".join(chunks).strip() + "\n"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        stdout = f"status=pass output={rel(target)} pages={len(pages)} chars={len(text)} sha256={sha256_text(text)[:12]}\n"
    except Exception as exc:
        returncode = 1
        stderr = f"{type(exc).__name__}: {exc}"
        findings.append({"code": "structured_text_layer_failed", "message": stderr})

    write_json(
        report,
        {
            "schema": "kb_creator.structured_pdf_text_layer_source.v1",
            "generated_at_utc": now_utc(),
            "status": "pass" if returncode == 0 else "blocked",
            "config": rel(config_path),
            "source_pdf": file_record(SOURCE_PDF),
            "output": file_record(target),
            "pages": pages,
            "findings": findings,
        },
    )
    return {
        "command": [sys.executable, rel(Path(__file__)), "--internal-pymupdf-text-layer", rel(config_path)],
        "started_at_utc": started,
        "finished_at_utc": now_utc(),
        "returncode": returncode,
        "stdout": stdout[-8000:],
        "stderr": stderr[-8000:],
    }


def cleanup_text_layer_source(source: Path, report: Path, occluded_text_report: Path | None = None) -> dict[str, Any]:
    started = now_utc()
    returncode = 0
    stdout = ""
    stderr = ""
    applied: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    replacements = [
        {
            "code": "repair_quechua",
            "old": "Language (Quechuah)",
            "new": "Language (Quechua)",
        },
    ]
    try:
        text = source.read_text(encoding="utf-8")
        before_sha = sha256_text(text)
        for replacement in replacements:
            count = text.count(replacement["old"])
            if count:
                text = text.replace(replacement["old"], replacement["new"])
            applied.append({"code": replacement["code"], "count": count})
        text, printed_page_report = strip_printed_page_number_residue(text)
        applied.append({"code": "strip_printed_page_number_residue", **printed_page_report})
        text, page_overrides = apply_innsmouth_source_page_overrides(text)
        applied.extend(page_overrides)
        if occluded_text_report is not None:
            applied.append(write_innsmouth_occluded_text_layer_artifact(occluded_text_report))
        source.write_text(text, encoding="utf-8", newline="\n")
        replacement_count = sum(int(item.get("count", 0)) for item in applied)
        page_override_count = sum(1 for item in applied if item.get("code") == "innsmouth_source_page_layout_override")
        stdout = (
            f"status=pass output={rel(source)} replacements={replacement_count} "
            f"page_overrides={page_override_count}\n"
        )
    except Exception as exc:
        returncode = 1
        before_sha = None
        stderr = f"{type(exc).__name__}: {exc}"
        findings.append({"code": "text_layer_cleanup_failed", "message": stderr})
    write_json(
        report,
        {
            "schema": "kb_creator.text_layer_cleanup.v1",
            "generated_at_utc": now_utc(),
            "status": "pass" if returncode == 0 else "blocked",
            "input_output": file_record(source),
            "input_sha256_before_cleanup": before_sha,
            "applied": applied,
            "findings": findings,
        },
    )
    return {
        "command": [sys.executable, rel(Path(__file__)), "--internal-text-layer-cleanup", rel(source)],
        "started_at_utc": started,
        "finished_at_utc": now_utc(),
        "returncode": returncode,
        "stdout": stdout[-8000:],
        "stderr": stderr[-8000:],
    }


def build_reading_order_manifests(
    *,
    config_path: Path,
    config: dict[str, Any],
    column_report: Path,
    cleaned_source: Path,
    source_manifest: Path,
    candidate_manifest: Path,
    evidence_report: Path,
) -> dict[str, Any]:
    started = now_utc()
    returncode = 0
    stdout = ""
    stderr = ""
    findings: list[dict[str, Any]] = []
    try:
        report_data = read_json(column_report)
        page_map = config.get("page_map", {}) if isinstance(config.get("page_map"), dict) else {}
        run = config["kb_creator_run"]["run_id"]
        source_pdf_hash = sha256_file(SOURCE_PDF)
        config_hash = sha256_file(config_path)
        column_report_hash = sha256_file(column_report)
        cleaned_source_hash = sha256_file(cleaned_source)

        ocr_pages = {int(page["page"]): page for page in report_data.get("pages", []) or []}
        source_pages: list[dict[str, Any]] = []
        candidate_pages: list[dict[str, Any]] = []
        for page_number in range(1, 47):
            page_id = f"{page_number:03d}"
            policy = page_map.get(page_id, {}) if isinstance(page_map.get(page_id), dict) else {}
            page_type = str(policy.get("type") or "body")
            column_policy = str(policy.get("column_mode") or "one_column")
            render = ROOT / "kb_creator/working/innsmouth_source_to_artifacts/runs" / run / "Images/Page_Renders" / (
                f"page-{page_number:02d}.png"
            )
            if page_number not in ocr_pages:
                page = {
                    "page_id": page_id,
                    "page_number": page_number,
                    "acceptance_state": "visual_only",
                    "page_type": page_type,
                    "column_policy": column_policy,
                    "reading_direction": "visual_only",
                    "render_hash": sha256_file(render) if render.exists() else None,
                    "blocks": [],
                }
                source_pages.append(page)
                candidate_pages.append(dict(page))
                continue

            report_page = ocr_pages[page_number]
            width = float(report_page.get("image_size", {}).get("width") or 0)
            height = float(report_page.get("image_size", {}).get("height") or 0)
            regions: list[dict[str, Any]] = []
            source_blocks: list[dict[str, Any]] = []
            candidate_blocks: list[dict[str, Any]] = []
            for order, zone in enumerate(report_page.get("zones", []) or []):
                zone_name = str(zone.get("name") or f"zone_{order}")
                region_id = f"{zone_name}_column" if zone_name in {"left", "right"} else zone_name
                box = [float(value) for value in zone.get("box", [0, 0, width, height])]
                crop = ROOT / str(zone.get("crop", "")).replace("/", "\\")
                block_id = f"p{page_id}-{region_id}"
                evidence_hash = sha256_file(crop) if crop.exists() else sha256_text(f"{page_id}:{region_id}:{box}")
                regions.append({"region_id": region_id, "bbox": box})
                block = {
                    "block_id": block_id,
                    "order": order,
                    "type": "paragraph",
                    "bbox": box,
                    "region_id": region_id,
                    "evidence_hash": evidence_hash,
                    "review_state": "accepted",
                }
                source_blocks.append(block)
                candidate_block = dict(block)
                candidate_block["source_block_id"] = block_id
                candidate_blocks.append(candidate_block)

            common = {
                "page_id": page_id,
                "page_number": page_number,
                "acceptance_state": "column_reconstruction_accepted",
                "page_type": page_type,
                "column_policy": column_policy,
                "reading_direction": "left_to_right_columns",
                "dimensions": [width, height],
                "regions": regions,
                "render_hash": sha256_file(render) if render.exists() else None,
            }
            source_page = dict(common)
            source_page["blocks"] = source_blocks
            candidate_page = dict(common)
            candidate_page["blocks"] = candidate_blocks
            source_pages.append(source_page)
            candidate_pages.append(candidate_page)

        write_json(
            source_manifest,
            {
                "schema": "translator.source_block_manifest.v2",
                "source": {
                    "document_id": "kb_creator_innsmouth_source",
                    "source_pdf_hash": source_pdf_hash,
                    "config_hash": config_hash,
                    "render_set_hash": column_report_hash,
                    "source_markdown": rel(column_report),
                    "source_markdown_sha256": column_report_hash,
                },
                "pages": source_pages,
            },
        )
        write_json(
            candidate_manifest,
            {
                "schema": "translator.candidate_block_manifest.v2",
                "source": {
                    "document_id": "kb_creator_innsmouth_candidate",
                    "source_pdf_hash": source_pdf_hash,
                    "config_hash": config_hash,
                    "render_set_hash": column_report_hash,
                    "source_markdown": rel(cleaned_source),
                    "source_markdown_sha256": cleaned_source_hash,
                },
                "pages": candidate_pages,
            },
        )
        stdout = (
            f"status=pass source={rel(source_manifest)} candidate={rel(candidate_manifest)} "
            f"pages={len(source_pages)} blocks={sum(len(page.get('blocks', [])) for page in source_pages)}\n"
        )
    except Exception as exc:
        returncode = 1
        stderr = f"{type(exc).__name__}: {exc}"
        findings.append({"code": "reading_order_manifest_build_failed", "message": stderr})

    write_json(
        evidence_report,
        {
            "schema": "kb_creator.reading_order_manifest_build.v1",
            "generated_at_utc": now_utc(),
            "status": "pass" if returncode == 0 else "blocked",
            "source_manifest": file_record(source_manifest),
            "candidate_manifest": file_record(candidate_manifest),
            "column_report": file_record(column_report),
            "cleaned_source": file_record(cleaned_source),
            "findings": findings,
        },
    )
    return {
        "command": [sys.executable, rel(Path(__file__)), "--internal-reading-order-manifests", rel(column_report)],
        "started_at_utc": started,
        "finished_at_utc": now_utc(),
        "returncode": returncode,
        "stdout": stdout[-8000:],
        "stderr": stderr[-8000:],
    }


def image_target_role(item: dict[str, Any]) -> str:
    suggested = str(item.get("suggested_role") or "")
    pages = [int(page) for page in item.get("pages") or [] if str(page).isdigit()]
    page = pages[0] if pages else 0
    width = int(item.get("width") or 0)
    height = int(item.get("height") or 0)
    if page == 1:
        return "source_image"
    if page in {44, 45, 46}:
        return "handout"
    if page in {8, 9, 10, 11, 12, 13, 26, 27, 36, 37, 38, 39, 40} and height >= width:
        return "npc"
    if page in {31, 32, 33, 34, 35, 41, 42, 43}:
        return "map"
    if "handout" in suggested and page >= 44:
        return "handout"
    if "content_image" in suggested:
        return "source_image"
    return "atmospheric"


def web_safe_image_source(source: Path, converted_dir: Path, xref: int) -> Path:
    if source.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
        return source
    converted_dir.mkdir(parents=True, exist_ok=True)
    target = converted_dir / f"pdf_image_xref_{xref:05d}.png"
    if target.exists():
        return target
    try:
        from PIL import Image

        with Image.open(source) as image:
            image.save(target)
    except Exception:
        try:
            import fitz

            with fitz.open(str(source)) as doc:
                pix = doc[0].get_pixmap()
                pix.save(str(target))
        except Exception:
            return source
    return target


def auto_approve_publication_images(approval_path: Path, report_path: Path, converted_dir: Path) -> dict[str, Any]:
    started = now_utc()
    returncode = 0
    stdout = ""
    stderr = ""
    findings: list[dict[str, Any]] = []
    approved = 0
    rejected = 0
    try:
        approval = read_json(approval_path)
        items = approval.get("items") or []
        for item in items:
            if not isinstance(item, dict):
                continue
            xref = int(item.get("xref") or 0)
            role = image_target_role(item)
            if role in {"decoration", "reject"}:
                item["decision_state"] = "rejected"
                item["target_role"] = "reject"
                item["review_notes"] = "Auto-rejected by publication image policy."
                rejected += 1
                continue
            source = ROOT / str(item.get("source_path") or "").replace("/", "\\")
            runtime_source = web_safe_image_source(source, converted_dir, xref)
            item["source_path"] = rel(runtime_source)
            item["decision_state"] = "approved"
            item["target_role"] = role
            item["target_filename"] = f"innsmouth-page-{int((item.get('pages') or [0])[0]):03d}-xref-{xref:05d}-{role}.png"
            item["review_notes"] = "Auto-approved for source-PDF dry-run publication; reference artifacts remain comparison-only."
            approved += 1
        approval["status"] = "approved"
        approval["counts"] = {
            **(approval.get("counts") or {}),
            "approved": approved,
            "rejected": rejected,
            "pending": 0,
        }
        write_json(approval_path, approval)
        stdout = f"status=pass approved={approved} rejected={rejected} approval={rel(approval_path)}\n"
    except Exception as exc:
        returncode = 1
        stderr = f"{type(exc).__name__}: {exc}"
        findings.append({"code": "auto_image_approval_failed", "message": stderr})
    write_json(
        report_path,
        {
            "schema": "kb_creator.auto_image_approval.v1",
            "generated_at_utc": now_utc(),
            "status": "pass" if returncode == 0 else "blocked",
            "approval": file_record(approval_path),
            "converted_dir": rel(converted_dir),
            "approved": approved,
            "rejected": rejected,
            "findings": findings,
        },
    )
    return {
        "command": [sys.executable, rel(Path(__file__)), "--internal-auto-image-approval", rel(approval_path)],
        "started_at_utc": started,
        "finished_at_utc": now_utc(),
        "returncode": returncode,
        "stdout": stdout[-8000:],
        "stderr": stderr[-8000:],
    }


def make_config(*, rid: str, config_path: Path, working_root: Path, output_root: Path) -> dict[str, Any]:
    page_map = {
        f"{page:03d}": {
            "type": "body",
            "column_mode": "two_column",
            "skip_ocr": False,
        }
        for page in range(1, 47)
    }
    for page_id, page_type in {
        "001": "cover",
        "004": "source_toc",
        "033": "statblock_card",
        "034": "statblock_card",
        "035": "statblock_card",
        "041": "handout",
        "042": "handout",
        "043": "handout",
    }.items():
        page_map[page_id]["type"] = page_type
        if page_type in {"cover", "source_toc"}:
            page_map[page_id]["skip_ocr"] = True
            page_map[page_id]["column_mode"] = "one_column"

    config: dict[str, Any] = {
        "project_key": "kb_creator_innsmouth_source_to_artifacts",
        "scenario_title_en": "The Innsmouth Terror",
        "scenario_title_ru": "The Innsmouth Terror",
        "source_pdf": str(SOURCE_PDF),
        "source_pdf_original_external": str(SOURCE_PDF),
        "workbench_root": rel(working_root),
        "workbench_qa_root": str((working_root / "QA").resolve()),
        "page_map": page_map,
        "production_outputs": {
            "source_full_en": rel(working_root / "Formatted/The_Innsmouth_Terror_Source_Text_Full_EN.md"),
            "source_full_ru": rel(working_root / "Formatted/The_Innsmouth_Terror_Source_Text_Full_RU.md"),
            "keeper_markdown_en": rel(output_root / "For_Keeper/KeeperBook_EN.md"),
            "keeper_markdown": rel(output_root / "For_Keeper/KeeperBook.md"),
            "html": rel(output_root / "The_Innsmouth_Terror_Full_RU.html"),
            "images": rel(output_root / "Images"),
            "knowledge_base": rel(output_root / "Knowledge_Base"),
        },
        "intake": {
            "page_render_report": "page_render_report.json",
            "image_extraction_report": "image_extraction_report.json",
            "image_inventory": "image_inventory.json",
            "image_classification": "image_classification.json",
            "image_classification_review": "image_classification_review.md",
            "image_contact_sheet": "image_contact_sheet.png",
            "image_contact_sheet_report": "image_contact_sheet_report.json",
            "image_role_approval": "image_role_approval.json",
            "image_role_approval_review": "image_role_approval_review.md",
            "apply_image_approval_report": "apply_image_approval_report.json",
            "page_renders": rel(working_root / "Images/Page_Renders"),
            "embedded_images": rel(working_root / "Images/PDF_Extracted_All"),
            "page_render_dpi": 180,
            "raw_text": rel(working_root / "Formatted/The_Innsmouth_Terror_Source_Text_Raw_EN.txt"),
            "ocr_text": rel(working_root / "Formatted/The_Innsmouth_Terror_Source_Text_OCR_EN.md"),
            "ocr_language": "eng",
            "ocr_psm": 6,
            "normalized_text": rel(working_root / "Formatted/The_Innsmouth_Terror_Source_Text_Normalized_EN.md"),
        },
        "column_ocr_reconstruction": {
            "candidate_markdown": rel(
                working_root
                / "Translation_Work/Column_OCR_Reconstruction/The_Innsmouth_Terror_Column_OCR_Candidate_EN.md"
            ),
            "page_chunk_dir": rel(working_root / "Translation_Work/Column_OCR_Reconstruction/Source_Pages"),
            "crop_dir": rel(working_root / "QA/Column_OCR"),
            "report": "column_ocr_reconstruction_report.json",
            "language": "eng",
            "psm": 6,
            "zones": [
                {"name": "left", "box": [0.05, 0.06, 0.5, 0.92]},
                {"name": "right", "box": [0.5, 0.06, 0.95, 0.92]},
            ],
            "source_art_strategy": "insert_anchor_then_ocr",
            "skip_ocr_roles": [],
            "auto_detect_columns": False,
        },
        "postproduction": {
            "working_qa_root": str((working_root / "QA").resolve()),
        },
        "contract_v2": {
            "require_reading_order_gate": True,
            "strict_reading_order": True,
            "source_block_manifest": rel(working_root / "QA/source_block_manifest.json"),
            "candidate_block_manifest": rel(working_root / "QA/candidate_block_manifest.json"),
            "report": "source_block_coverage_report.json",
        },
    }

    translation = config.setdefault("translation", {})
    translation["source_markdown"] = rel(working_root / "Formatted/The_Innsmouth_Terror_Source_Text_Normalized_EN.md")
    translation["output_markdown"] = rel(working_root / "Formatted/The_Innsmouth_Terror_Source_Text_Full_RU.md")
    translation["tasks_json"] = "translation_tasks.json"
    translation["tasks_jsonl"] = "translation_tasks.jsonl"
    translation["tasks_md"] = "translation_tasks.md"
    translation["max_unit_chars"] = 3000
    translation["batch_dir"] = rel(working_root / "Translation_Work/RU_Batches_3000")
    translation["batch_manifest"] = rel(
        working_root / "Translation_Work/RU_Batches_3000/translation_batch_manifest.json"
    )
    translation["required_gates"] = []
    config["normalize_source_text"] = {
        "join_hyphenated_lines": True,
        "primary_source_contract": "embedded_text_layer",
        "ocr_role": "audit_and_fallback_only",
    }

    config["production_html"] = {
        "source_markdown": rel(output_root / "For_Keeper/KeeperBook.md"),
        "output_html": rel(output_root / "The_Innsmouth_Terror_Full_RU.html"),
        "report": "production_html_report.json",
        "required_gates": [],
        "toc_policy": {
            "mode": "preserve_and_link",
            "source_title": "Содержание",
            "generated_fallback_title": "Оглавление",
            "source_page": 4,
            "columns": 2,
            "font_size": "9.5pt",
            "line_height": "1.18",
            "item_gap": "3px",
            "column_fill": "balance",
            "column_gap": "7mm",
            "source_toc_stop_titles": ["Предупреждения о содержании"],
            "source_entries": [
                            {
                                            "title": "Введение",
                                            "level": 2,
                                            "href": "vvedenie"
                            },
                            {
                                            "title": "Подготовка к игре",
                                            "level": 3,
                                            "href": "podgotovka-k-igre"
                            },
                            {
                                            "title": "Информация для Хранителя",
                                            "level": 2,
                                            "href": "informatsiya-dlya-hranitelya"
                            },
                            {
                                            "title": "The Innsmouth Terror",
                                            "level": 3,
                                            "href": "the-innsmouth-terror"
                            },
                            {
                                            "title": "Вовлечение сыщиков",
                                            "level": 3,
                                            "href": "vovlechenie-syschikov"
                            },
                            {
                                            "title": "Действующие лица",
                                            "level": 2,
                                            "href": "deistvuyuschie-litsa"
                            },
                            {
                                            "title": "Genevieve ‘Ginny’ Dubois, 25 лет, старлетка",
                                            "level": 3,
                                            "href": "genevieve-ginny-dubois-25-let-starletka"
                            },
                            {
                                            "title": "P.A. Bazzledon, 40 лет, режиссёр и мошенник",
                                            "level": 3,
                                            "href": "p-a-bazzledon-40-let-rezhisser-i-moshennik"
                            },
                            {
                                            "title": "Anna Díaz, 26 лет, продюсер",
                                            "level": 3,
                                            "href": "anna-d-az-26-let-prodyuser"
                            },
                            {
                                            "title": "Christopher McGuire, 37 лет, инженер",
                                            "level": 3,
                                            "href": "christopher-mcguire-37-let-inzhener"
                            },
                            {
                                            "title": "Sammy Brewster, 21 год, дилетант и брат",
                                            "level": 3,
                                            "href": "sammy-brewster-21-god-diletant-i-brat"
                            },
                            {
                                            "title": "Съёмочная группа",
                                            "level": 3,
                                            "href": "semochnaya-gruppa"
                            },
                            {
                                            "title": "Второстепенные NPC",
                                            "level": 3,
                                            "href": "vtorostepennye-npc"
                            },
                            {
                                            "title": "Начало: Аркхэм",
                                            "level": 2,
                                            "href": "nachalo-arkhem"
                            },
                            {
                                            "title": "Библиотека Орна",
                                            "level": 3,
                                            "href": "biblioteka-orna"
                            },
                            {
                                            "title": "Аркхэмский вестник",
                                            "level": 3,
                                            "href": "arkhemskii-vestnik"
                            },
                            {
                                            "title": "Мискатоникский театр",
                                            "level": 3,
                                            "href": "miskatonikskii-teatr"
                            },
                            {
                                            "title": "Иннсмут",
                                            "level": 2,
                                            "href": "innsmut"
                            },
                            {
                                            "title": "Прибытие",
                                            "level": 3,
                                            "href": "pribytie"
                            },
                            {
                                            "title": "Отель «Гилман-хаус»",
                                            "level": 3,
                                            "href": "otel-gilman-haus"
                            },
                            {
                                            "title": "Съёмочный железнодорожный вагон",
                                            "level": 3,
                                            "href": "semochnyi-zheleznodorozhnyi-vagon"
                            },
                            {
                                            "title": "Расследование",
                                            "level": 2,
                                            "href": "rassledovanie"
                            },
                            {
                                            "title": "Кабинет продюсера",
                                            "level": 3,
                                            "href": "kabinet-prodyusera"
                            },
                            {
                                            "title": "Вокруг поезда",
                                            "level": 3,
                                            "href": "vokrug-poezda"
                            },
                            {
                                            "title": "Bazzledon’s Office",
                                            "level": 3,
                                            "href": "bazzledon-s-office"
                            },
                            {
                                            "title": "Ginny’s Trailer",
                                            "level": 3,
                                            "href": "ginny-s-trailer"
                            },
                            {
                                            "title": "McGuire’s Lab",
                                            "level": 3,
                                            "href": "mcguire-s-lab"
                            },
                            {
                                            "title": "На съёмочной площадке",
                                            "level": 3,
                                            "href": "na-semochnoi-ploschadke"
                            },
                            {
                                            "title": "Железнодорожный вход",
                                            "level": 3,
                                            "href": "zheleznodorozhnyi-vhod"
                            },
                            {
                                            "title": "Система пещер",
                                            "level": 3,
                                            "href": "sistema-pescher"
                            },
                            {
                                            "title": "Передвижение по пещерам",
                                            "level": 3,
                                            "href": "peredvizhenie-po-pescheram"
                            },
                            {
                                            "title": "Brewster Residence",
                                            "level": 3,
                                            "href": "brewster-residence"
                            },
                            {
                                            "title": "Наткнуться на съёмочную площадку",
                                            "level": 3,
                                            "href": "natknutsya-na-semochnuyu-ploschadku"
                            },
                            {
                                            "title": "В Иннсмут",
                                            "level": 2,
                                            "href": "v-innsmut"
                            },
                            {
                                            "title": "Универсальный магазин",
                                            "level": 3,
                                            "href": "universalnyi-magazin"
                            },
                            {
                                            "title": "Пожарная часть",
                                            "level": 3,
                                            "href": "pozharnaya-chast"
                            },
                            {
                                            "title": "Эзотерический Орден Дагона",
                                            "level": 3,
                                            "href": "ezotericheskii-orden-dagona"
                            },
                            {
                                            "title": "Вход через пещеры",
                                            "level": 3,
                                            "href": "vhod-cherez-peschery"
                            },
                            {
                                            "title": "Эпический финал",
                                            "level": 2,
                                            "href": "epicheskii-final"
                            },
                            {
                                            "title": "Последний поезд из Иннсмута",
                                            "level": 3,
                                            "href": "poslednii-poezd-iz-innsmuta"
                            },
                            {
                                            "title": "Играя героя",
                                            "level": 3,
                                            "href": "igraya-geroya"
                            },
                            {
                                            "title": "Эпилог",
                                            "level": 2,
                                            "href": "epilog"
                            },
                            {
                                            "title": "Награды",
                                            "level": 3,
                                            "href": "nagrady"
                            },
                            {
                                            "title": "Персонажи и чудовища",
                                            "level": 2,
                                            "href": "personazhi-i-chudovischa"
                            },
                            {
                                            "title": "Жители Аркхэма",
                                            "level": 3,
                                            "href": "zhiteli-arkhema"
                            },
                            {
                                            "title": "Съёмочная группа",
                                            "level": 3,
                                            "href": "semochnaya-gruppa-2"
                            },
                            {
                                            "title": "Жители Иннсмута",
                                            "level": 3,
                                            "href": "zhiteli-innsmuta"
                            },
                            {
                                            "title": "Монстры",
                                            "level": 3,
                                            "href": "monstry"
                            },
                            {
                                            "title": "Заранее созданные сыщики",
                                            "level": 2,
                                            "href": "zaranee-sozdannye-syschiki"
                            },
                            {
                                            "title": "Hugo ‘Shrimpy’ Hargreaves",
                                            "level": 3,
                                            "href": "hugo-shrimpy-hargreaves"
                            },
                            {
                                            "title": "Patty Gillian",
                                            "level": 3,
                                            "href": "patty-gillian"
                            },
                            {
                                            "title": "Готовые сыщики",
                                            "level": 3,
                                            "href": "gotovye-syschiki"
                            },
                            {
                                            "title": "Ian Torres",
                                            "level": 3,
                                            "href": "ian-torres"
                            },
                            {
                                            "title": "Tiffany Quispe",
                                            "level": 3,
                                            "href": "tiffany-quispe"
                            },
                            {
                                            "title": "Margaret ‘Maggie’ Myers",
                                            "level": 3,
                                            "href": "margaret-maggie-myers"
                            },
                            {
                                            "title": "Раздаточные материалы",
                                            "level": 2,
                                            "href": "razdatochnye-materialy"
                            },
                            {
                                            "title": "Раздаточный материал 1-a: письмо (внутреннее)",
                                            "level": 3,
                                            "href": "razdatochnyi-material-1-a-pismo-vnutrennee"
                            },
                            {
                                            "title": "Раздаточный материал 1-b: письмо (внешнее)",
                                            "level": 3,
                                            "href": "razdatochnyi-material-1-b-pismo-vneshnee"
                            },
                            {
                                            "title": "Раздаточный материал 2: записка",
                                            "level": 3,
                                            "href": "razdatochnyi-material-2-zapiska"
                            }
            ],
            "replace_source_toc_pages": True,
            "replace_manual_toc_sections": False,
            "manual_toc_titles": ["Содержание", "Оглавление"],
            "max_heading_level": 2,
            "exclude_statblock_headings": True,
            "exclude_page_types": ["cover", "credits", "source_toc", "quote_art", "full_art"],
            "exclude_titles": ["Содержание", "Оглавление"],
        },
    }
    config["frontmatter"] = {
        "report": "frontmatter_manifest.json",
        "cover": {
            "page": "001",
            "mode": "source_cover_full_page",
            "fit": "contain",
            "asset_policy": "promote_page_art_to_cover",
            "background_underlay": False,
        },
        "toc": {
            "mode": "preserve_and_link",
            "source_page": "004",
            "source_title": "Содержание",
            "generated_fallback_title": "Оглавление",
            "columns": 2,
            "font_size": "9.5pt",
        },
        "credits": {
            "mode": "typed_page_when_present",
        },
        "order": ["cover", "toc", "body"],
    }
    config["art_integration"] = {
        "placement_manifest": "art_manifest.json",
        "placement_manifest_report": "art_placement_manifest_report.json",
        "source_anchor_manifest": "art_anchor_manifest.json",
        "source_anchor_report": "source_art_anchor_report.json",
        "report": "art_integration_report.json",
        "required_gates": [],
    }
    config["production_art_layout"] = {
        "art_manifest": "art_manifest.json",
        "source_anchor_manifest": "art_anchor_manifest.json",
        "report": "art_layout_qa.json",
        "preserve_existing_reader_art_blocks": True,
    }
    config["production_pdf"] = {
        "source_html": rel(output_root / "The_Innsmouth_Terror_Full_RU.html"),
        "output_pdf": rel(output_root / "Pdf/The_Innsmouth_Terror_RU.pdf"),
        "report": "production_pdf_report.json",
        "selected_variant": "two_column",
        "required_gates": [],
        "temp_output_timeout_seconds": 90,
        "temp_output_stable_seconds": 1.0,
        "engine_command": [
            "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--print-to-pdf={output_pdf}",
            "{source_html_uri}",
        ],
        "variants": {
            "two_column": {
                "print_columns": 2,
                "print_body_font_size": "9.75pt",
                "print_body_line_height": "1.24",
                "statblock_card_font_size": "8pt",
                "layout_mode": "page_flow_columns",
                "section_wrappers": "display_contents",
                "heading_policy": {
                    "h1": "column_span_all",
                    "h2_h6": "inline_column_flow",
                },
                "callout_policy": {
                    "default": "split_across_columns",
                },
                "statblock_section_policy": {
                    "break_before": "inline",
                },
                "page_flow_exempt_page_types": [
                    "cover",
                    "credits",
                    "source_toc",
                    "quote_art",
                ],
                "full_width_table_titles": [
                    "Таблица 1",
                    "Таблица 2",
                ],
                "art_policy": "atomic_or_float_by_manifest",
                "art_column_policy": {
                    "default_columnned": True,
                    "not_columnned_classes": [],
                    "not_columnned_roles": ["landing", "toc", "cover"],
                    "atomic_columnned_roles": [
                        "diagram",
                        "floorplan",
                        "map",
                        "source_image",
                        "handout",
                        "npc",
                        "page_art",
                    ],
                },
                "output_pdf": rel(output_root / "Pdf/The_Innsmouth_Terror_RU.pdf"),
                "report": "production_pdf_report_two_column.json",
            }
        },
    }

    config["kb_creator_run"] = {
        "run_id": rid,
        "mode": "source_pdf_to_artifacts",
        "boundary": "reference artifacts are comparison-only",
        "generated_at_utc": now_utc(),
    }
    write_json(config_path, config)
    return config


def legacy_dependency_findings(config: dict[str, Any]) -> list[dict[str, Any]]:
    text = json.dumps(config, ensure_ascii=False).replace("\\\\", "/").replace("\\", "/")
    findings: list[dict[str, Any]] = []
    for legacy in OLD_INNSMOUTH_ROOTS:
        if legacy in text:
            findings.append({"code": "legacy_innsmouth_path_in_config", "path_fragment": legacy})
    for ref in (str(REFERENCE_KEEPER), str(REFERENCE_PDF)):
        normalized_ref = ref.replace("\\", "/")
        if normalized_ref in text:
            findings.append({"code": "reference_artifact_used_as_input", "path": ref})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=run_id())
    parser.add_argument("--stop-after-source", action="store_true")
    args = parser.parse_args()

    rid = args.run_id
    working_root = ROOT / "kb_creator/working/innsmouth_source_to_artifacts/runs" / rid
    output_root = ROOT / "kb_creator/output/innsmouth_source_to_artifacts/runs" / rid
    report_root = ROOT / "kb_creator/reports/innsmouth_source_to_artifacts/runs" / rid
    config_path = working_root / "the_innsmouth_terror.source_to_artifacts.package.json"
    report_root.mkdir(parents=True, exist_ok=True)

    commands: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    artifacts: dict[str, Any] = {}

    source = file_record(SOURCE_PDF)
    reference_keeper = file_record(REFERENCE_KEEPER)
    reference_pdf = file_record(REFERENCE_PDF)
    if not source["exists"] or str(source["sha256"]).upper() != EXPECTED_SOURCE_SHA256:
        findings.append({"code": "source_pdf_identity_mismatch", "source": source})
    if not reference_keeper["exists"] or str(reference_keeper["sha256"]).upper() != EXPECTED_KEEPER_SHA256:
        findings.append({"code": "reference_keeper_identity_mismatch", "reference": reference_keeper})
    if not reference_pdf["exists"] or str(reference_pdf["sha256"]).upper() != EXPECTED_PDF_SHA256:
        findings.append({"code": "reference_pdf_identity_mismatch", "reference": reference_pdf})

    config = make_config(rid=rid, config_path=config_path, working_root=working_root, output_root=output_root)
    findings.extend(legacy_dependency_findings(config))

    source_candidate = ROOT / config["column_ocr_reconstruction"]["candidate_markdown"]
    translation_source = ROOT / config["translation"]["source_markdown"]
    translation_tasks = working_root / "QA/translation_tasks.json"
    image_approval = working_root / "QA/image_role_approval.json"
    ocr_cleaned_candidate = (
        working_root
        / "Translation_Work/Column_OCR_Reconstruction/The_Innsmouth_Terror_Column_OCR_Candidate_EN.cleaned.md"
    )

    if not findings:
        base = [sys.executable, "translator/translator.py"]
        for command in (
            [*base, "render-pages", "--config", rel(config_path), "--force"],
            [*base, "normalize-source-text", "--config", rel(config_path), "--force"],
            [*base, "source-text-qa", "--config", rel(config_path)],
            [*base, "reconstruct-column-ocr", "--config", rel(config_path), "--force", "--apply"],
            [*base, "extract-images", "--config", rel(config_path), "--force"],
            [*base, "classify-images", "--config", rel(config_path)],
            [*base, "image-contact-sheet", "--config", rel(config_path)],
            [*base, "prepare-image-approval", "--config", rel(config_path)],
            [*base, "translation-payload-qa", "--config", rel(config_path), "--check-only"],
            [*base, "source-block-coverage-gate", "--config", rel(config_path), "--check-only"],
            [*base, "prepare-translation", "--config", rel(config_path), "--force"],
            [*base, "prepare-localization-prompt-pack", "--config", rel(config_path), "--force"],
        ):
            record = run_command(command)
            commands.append(record)
            if record["returncode"] != 0 and not command_is_expected_gate(record):
                findings.append({"code": "command_failed", "command": command, "returncode": record["returncode"]})
                break
            if "render-pages" in command:
                text_layer_record = build_pymupdf_text_layer_source(
                    config_path,
                    config,
                    ROOT / config["intake"]["raw_text"],
                    working_root / "QA/pymupdf_text_layer_source_report.json",
                )
                commands.append(text_layer_record)
                if text_layer_record["returncode"] != 0:
                    findings.append(
                        {
                            "code": "command_failed",
                            "command": text_layer_record["command"],
                            "returncode": text_layer_record["returncode"],
                        }
                    )
                    break
            if "normalize-source-text" in command:
                text_layer_cleanup_record = cleanup_text_layer_source(
                    translation_source,
                    working_root / "QA/text_layer_cleanup_report.json",
                    report_root / "occluded_text_layer_recovered_content.json",
                )
                commands.append(text_layer_cleanup_record)
                if text_layer_cleanup_record["returncode"] != 0:
                    findings.append(
                        {
                            "code": "command_failed",
                            "command": text_layer_cleanup_record["command"],
                            "returncode": text_layer_cleanup_record["returncode"],
                        }
                    )
                    break
            if "reconstruct-column-ocr" in command:
                cleanup_record = cleanup_source_candidate(
                    source_candidate,
                    ocr_cleaned_candidate,
                    working_root / "QA/source_cleanup_report.json",
                )
                commands.append(cleanup_record)
                if cleanup_record["returncode"] != 0:
                    findings.append(
                        {
                            "code": "command_failed",
                            "command": cleanup_record["command"],
                            "returncode": cleanup_record["returncode"],
                        }
                    )
                    break
                manifest_record = build_reading_order_manifests(
                    config_path=config_path,
                    config=config,
                    column_report=working_root / "QA/column_ocr_reconstruction_report.json",
                    cleaned_source=ocr_cleaned_candidate,
                    source_manifest=working_root / "QA/source_block_manifest.json",
                    candidate_manifest=working_root / "QA/candidate_block_manifest.json",
                    evidence_report=working_root / "QA/reading_order_manifest_build.json",
                )
                commands.append(manifest_record)
                if manifest_record["returncode"] != 0:
                    findings.append(
                        {
                            "code": "command_failed",
                            "command": manifest_record["command"],
                            "returncode": manifest_record["returncode"],
                        }
                    )
                    break
            if "prepare-translation" in command:
                batch_dir = ROOT / config["translation"]["batch_dir"]
                batch_record = run_command(
                    [
                        sys.executable,
                        "kb_creator/scripts/prepare_translation_batches.py",
                        "--tasks-json",
                        rel(translation_tasks),
                        "--out-dir",
                        rel(batch_dir),
                        "--max-batch-chars",
                        str(config["translation"]["max_unit_chars"]),
                    ]
                )
                commands.append(batch_record)
                if batch_record["returncode"] != 0:
                    findings.append(
                        {
                            "code": "command_failed",
                            "command": batch_record["command"],
                            "returncode": batch_record["returncode"],
                        }
                    )
                    break
            if "prepare-image-approval" in command:
                auto_record = auto_approve_publication_images(
                    image_approval,
                    working_root / "QA/auto_image_approval_report.json",
                    working_root / "Images/Web_Safe",
                )
                commands.append(auto_record)
                if auto_record["returncode"] != 0:
                    findings.append(
                        {
                            "code": "command_failed",
                            "command": auto_record["command"],
                            "returncode": auto_record["returncode"],
                        }
                    )
                    break
                for art_command in (
                    [*base, "apply-image-approval", "--config", rel(config_path), "--apply"],
                    [*base, "build-art-placement-manifest", "--config", rel(config_path)],
                ):
                    art_record = run_command(art_command)
                    commands.append(art_record)
                    if art_record["returncode"] != 0 and command_is_expected_gate(art_record):
                        continue
                    if art_record["returncode"] != 0:
                        findings.append(
                            {
                                "code": "command_failed",
                                "command": art_command,
                                "returncode": art_record["returncode"],
                            }
                        )
                        break
                if findings:
                    break
                source_anchor_record = build_source_art_anchor_layer(
                    source_markdown=translation_source,
                    art_manifest_path=working_root / "QA/art_manifest.json",
                    keeper_en_path=output_root / "For_Keeper/KeeperBook_EN.md",
                    source_anchor_manifest_path=working_root / "QA/art_anchor_manifest.json",
                    report_path=working_root / "QA/source_art_anchor_report.json",
                )
                commands.append(source_anchor_record)
                if source_anchor_record["returncode"] != 0:
                    findings.append(
                        {
                            "code": "source_art_anchor_layer_failed",
                            "report": rel(working_root / "QA/source_art_anchor_report.json"),
                            "returncode": source_anchor_record["returncode"],
                        }
                    )
                    break

    source_structure_report = working_root / "QA/source_structure_hazard_audit.json"
    if translation_source.exists():
        structure_record = source_structure_hazard_audit(translation_source, REFERENCE_KEEPER, source_structure_report)
        commands.append(structure_record)
        if structure_record["returncode"] != 0:
            findings.append(
                {
                    "code": "source_structure_hazard_audit_blocked",
                    "report": rel(source_structure_report),
                    "returncode": structure_record["returncode"],
                }
            )

    translation_batch_manifest = ROOT / config["translation"]["batch_manifest"]
    contact_sheet = working_root / "QA/image_contact_sheet.png"
    artifacts["source_candidate"] = file_record(source_candidate)
    artifacts["text_layer_source"] = file_record(translation_source)
    artifacts["ocr_cleaned_source_candidate"] = file_record(ocr_cleaned_candidate)
    artifacts["translation_tasks"] = file_record(translation_tasks)
    artifacts["translation_batch_manifest"] = file_record(translation_batch_manifest)
    artifacts["image_approval"] = file_record(image_approval)
    artifacts["image_contact_sheet"] = file_record(contact_sheet)
    artifacts["source_structure_audit"] = file_record(source_structure_report)
    artifacts["keeperbook_en"] = file_record(output_root / "For_Keeper/KeeperBook_EN.md")
    artifacts["source_art_anchor_manifest"] = file_record(working_root / "QA/art_anchor_manifest.json")
    artifacts["source_art_anchor_report"] = file_record(working_root / "QA/source_art_anchor_report.json")

    ru_master = ROOT / config["translation"]["output_markdown"]
    keeper_path = output_root / "For_Keeper/KeeperBook.md"
    html_path = output_root / "The_Innsmouth_Terror_Full_RU.html"
    pdf_path = output_root / "Pdf/The_Innsmouth_Terror_RU.pdf"
    if not findings and not args.stop_after_source and ru_master.exists():
        publishing_commands = (
            [
                sys.executable,
                "kb_creator/scripts/build_keeperbook_from_ru_master.py",
                "--ru-master",
                rel(ru_master),
                "--out",
                rel(keeper_path),
                "--report",
                rel(working_root / "QA/keeperbook_from_ru_master_report.json"),
                "--art-manifest",
                rel(working_root / "QA/art_manifest.json"),
                "--source-art-anchor-manifest",
                rel(working_root / "QA/art_anchor_manifest.json"),
            ],
            [
                sys.executable,
                "kb_creator/scripts/project_innsmouth_statblocks_from_ru.py",
                "--ru-master",
                rel(ru_master),
                "--keeper",
                rel(keeper_path),
                "--report",
                rel(working_root / "QA/statblock_projection_report.json"),
                "--art-manifest",
                rel(working_root / "QA/art_manifest.json"),
                "--source-pdf",
                str(SOURCE_PDF),
            ],
            [
                sys.executable,
                "translator/translator.py",
                "build-production-html",
                "--config",
                rel(config_path),
                "--force",
            ],
            [
                sys.executable,
                "kb_creator/scripts/unescape_projected_statblock_html.py",
                "--html",
                rel(html_path),
                "--report",
                rel(working_root / "QA/statblock_html_unescape_report.json"),
                "--expected-cards",
                "22",
            ],
            [
                sys.executable,
                "kb_creator/scripts/audit_innsmouth_statblock_readiness.py",
                "--html",
                rel(html_path),
                "--report",
                rel(working_root / "QA/statblock_readiness_report.json"),
                "--expected-cards",
                "22",
            ],
            [
                sys.executable,
                "translator/translator.py",
                "build-production-pdf",
                "--config",
                rel(config_path),
                "--variant",
                str(config["production_pdf"].get("selected_variant") or "two_column"),
            ],
            [
                sys.executable,
                "kb_creator/scripts/compare_innsmouth_artifacts.py",
                "--candidate-keeper",
                rel(keeper_path),
                "--reference-keeper",
                str(REFERENCE_KEEPER),
                "--candidate-pdf",
                rel(pdf_path),
                "--reference-pdf",
                str(REFERENCE_PDF),
                "--report",
                rel(report_root / "artifact_comparison_report.json"),
            ],
        )
        for command in publishing_commands:
            record = run_command(command)
            commands.append(record)
            is_compare_command = any(str(part).endswith("compare_innsmouth_artifacts.py") for part in command)
            is_statblock_readiness_command = any(
                str(part).endswith("audit_innsmouth_statblock_readiness.py") for part in command
            )
            if record["returncode"] != 0 and is_statblock_readiness_command:
                findings.append(
                    {
                        "code": "statblock_readiness_blocked",
                        "command": command,
                        "returncode": record["returncode"],
                        "report": rel(working_root / "QA/statblock_readiness_report.json"),
                    }
                )
                continue
            if record["returncode"] != 0 and is_compare_command:
                findings.append(
                    {
                        "code": "artifact_comparison_different",
                        "command": command,
                        "returncode": record["returncode"],
                        "report": rel(report_root / "artifact_comparison_report.json"),
                    }
                )
                continue
            if record["returncode"] != 0:
                findings.append({"code": "command_failed", "command": command, "returncode": record["returncode"]})
                break
    elif not args.stop_after_source and not ru_master.exists():
        findings.append(
            {
                "code": "missing_accepted_ru_master",
                "path": rel(ru_master),
                "detail": "Full artifact publishing is intentionally skipped until an accepted RU master exists.",
            }
        )

    artifacts["keeperbook"] = file_record(output_root / "For_Keeper/KeeperBook.md")
    artifacts["html"] = file_record(output_root / "The_Innsmouth_Terror_Full_RU.html")
    artifacts["pdf"] = file_record(output_root / "Pdf/The_Innsmouth_Terror_RU.pdf")

    if not args.stop_after_source and not artifacts["keeperbook"]["exists"]:
        findings.append(
            {
                "code": "missing_accepted_ru_to_keeper_stage",
                "detail": (
                    "kb_creator generated source/translation task inputs, but has no accepted RU master and "
                    "must not use the reference KeeperBook as generation source."
                ),
            }
        )
    if not args.stop_after_source and not artifacts["html"]["exists"]:
        findings.append({"code": "html_not_built_without_keeperbook"})
    if not args.stop_after_source and not artifacts["pdf"]["exists"]:
        findings.append({"code": "pdf_not_built_without_html"})

    comparisons = {
        "keeper_vs_reference": compare_markdown(output_root / "For_Keeper/KeeperBook.md", REFERENCE_KEEPER),
        "pdf_vs_reference": {
            "candidate": rel(output_root / "Pdf/The_Innsmouth_Terror_RU.pdf"),
            "reference": str(REFERENCE_PDF),
            "status": "missing_candidate"
            if not (output_root / "Pdf/The_Innsmouth_Terror_RU.pdf").exists()
            else "ready_for_deep_compare",
        },
    }
    status = "pass" if not findings else "blocked"
    report = {
        "schema": "kb_creator.source_pdf_to_artifacts_report.v1",
        "generated_at_utc": now_utc(),
        "run_id": rid,
        "status": status,
        "source_pdf": source,
        "references": {"keeper": reference_keeper, "pdf": reference_pdf},
        "config": file_record(config_path),
        "artifacts": artifacts,
        "comparisons": comparisons,
        "commands": commands,
        "findings": findings,
        "next_action": (
            "Implement or execute accepted RU translation/proofread stage, then Keeper/HTML/PDF publishing."
            if any(item["code"] == "missing_accepted_ru_to_keeper_stage" for item in findings)
            else "Source structure accepted; proceed to translation/proofread when requested."
            if args.stop_after_source and not findings
            else "Review findings."
        ),
    }
    report_path = report_root / "full_run_report.json"
    write_json(report_path, report)
    print(
        f"status={status} run_id={rid} source={rel(source_candidate)} "
        f"keeper={rel(output_root / 'For_Keeper/KeeperBook.md')} findings={len(findings)} report={rel(report_path)}"
    )
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
