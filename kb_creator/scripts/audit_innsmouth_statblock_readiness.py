from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html as html_lib
import json
import re
from pathlib import Path
from typing import Any


EXPECTED_NAMES = [
    "Diane Loring",
    "Henry Armitage",
    "Karen Jeffries",
    "Franc Turner",
    "Genevieve",
    "Ginny",
    "Anna Díaz",
    "Bazzledon",
    "Christopher McGuire",
    "Average Crew Member",
    "Sammy Brewster",
    "Jeremiah Brewster",
    "Zadok Allen",
    "Average Human Resident",
    "Average Hybrid Resident",
    "Shoggoth",
    "Star Spawn",
    "Deep One",
    "Hugo",
    "Patty Gillian",
    "Ian Torres",
    "Tiffany Quispe",
    "Margaret",
]


CORE_RE = re.compile(
    r"\b(?:STR|CON|SIZ|DEX|INT|APP|POW|EDU|SAN|СИЛ|ТЕЛ|РАЗМ?|ЛОВ|ЛВК|ВНЕШ?|МОЩ|ОБР|РАСС?)\b",
    re.I,
)
DERIVED_RE = re.compile(r"\b(?:HP|DB|MP|Build|Move|Luck|ЗД|БУ|БМ|МЗ|Телосложение|Движение|Удача)\b", re.I)


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_tags(fragment: str) -> str:
    fragment = re.sub(r"<script\b[\s\S]*?</script>", " ", fragment, flags=re.I)
    fragment = re.sub(r"<style\b[\s\S]*?</style>", " ", fragment, flags=re.I)
    return html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))


def paragraph_texts(html: str) -> list[str]:
    fragments = re.findall(r"<(?:p|li)\b[^>]*>([\s\S]*?)</(?:p|li)>", html, flags=re.I)
    return [normalize_space(strip_tags(fragment)) for fragment in fragments if normalize_space(strip_tags(fragment))]


def flattened_statblock_candidates(paragraphs: list[str]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for index, paragraph in enumerate(paragraphs, start=1):
        core_hits = len(CORE_RE.findall(paragraph))
        derived_hits = len(DERIVED_RE.findall(paragraph))
        if core_hits >= 5 and derived_hits >= 3:
            candidates.append(
                {
                    "paragraph_index": index,
                    "chars": len(paragraph),
                    "core_hits": core_hits,
                    "derived_hits": derived_hits,
                    "sample": paragraph[:260],
                }
            )
    return candidates


def name_presence(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in EXPECTED_NAMES:
        rows.append(
            {
                "name": name,
                "count": len(re.findall(re.escape(name), text, flags=re.I)),
            }
        )
    return rows


def class_token_count(text: str, token: str) -> int:
    count = 0
    for match in re.finditer(r'class=["\']([^"\']*)["\']', text, flags=re.I):
        if token in match.group(1).split():
            count += 1
    return count


def audit(html_path: Path, report_path: Path, expected_cards: int) -> int:
    html = html_path.read_text(encoding="utf-8")
    paragraphs = paragraph_texts(html)
    cards = class_token_count(html, "statblock-card")
    structured = class_token_count(html, "statblock-structured")
    tables = len(re.findall(r"<table\b", html, flags=re.I))
    flattened = flattened_statblock_candidates(paragraphs)
    names = name_presence(strip_tags(html))
    visible_anchor_paragraphs = re.findall(r"<p>\s*&lt;a\s+id=&quot;[^&]+&quot;&gt;&lt;/a&gt;\s*</p>", html, flags=re.I)
    visible_escaped_comments = re.findall(r"&lt;!--[^&]*(?:unit-id|source-hash)[\s\S]*?--&gt;", html, flags=re.I)

    findings: list[dict[str, Any]] = []
    if cards < expected_cards:
        findings.append(
            {
                "code": "statblock_cards_below_expected",
                "expected": expected_cards,
                "actual": cards,
            }
        )
    if structured < expected_cards:
        findings.append(
            {
                "code": "structured_statblocks_below_expected",
                "expected": expected_cards,
                "actual": structured,
            }
        )
    if flattened:
        findings.append(
            {
                "code": "flattened_statblock_paragraphs_detected",
                "count": len(flattened),
                "samples": flattened[:8],
            }
        )
    if visible_anchor_paragraphs:
        findings.append(
            {
                "code": "visible_technical_anchor_paragraphs",
                "count": len(visible_anchor_paragraphs),
                "samples": visible_anchor_paragraphs[:8],
            }
        )
    if visible_escaped_comments:
        findings.append(
            {
                "code": "visible_escaped_source_comments",
                "count": len(visible_escaped_comments),
                "samples": visible_escaped_comments[:8],
            }
        )

    status = "pass" if not findings else "blocked"
    report = {
        "schema": "kb_creator.innsmouth_statblock_readiness.v1",
        "generated_at_utc": now_utc(),
        "status": status,
        "html": str(html_path).replace("\\", "/"),
        "html_sha256": sha256_text(html),
        "expected_cards": expected_cards,
        "counts": {
            "statblock_cards": cards,
            "structured_statblocks": structured,
            "tables": tables,
            "paragraphs": len(paragraphs),
            "flattened_statblock_candidates": len(flattened),
            "visible_technical_anchor_paragraphs": len(visible_anchor_paragraphs),
            "visible_escaped_source_comments": len(visible_escaped_comments),
        },
        "expected_name_presence": names,
        "flattened_candidates": flattened,
        "findings": findings,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"status={status} expected={expected_cards} cards={cards} "
        f"structured={structured} flattened={len(flattened)} report={report_path}"
    )
    return 0 if status == "pass" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected-cards", type=int, default=22)
    args = parser.parse_args()
    return audit(args.html, args.report, args.expected_cards)


if __name__ == "__main__":
    raise SystemExit(main())
