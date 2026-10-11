from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html as html_lib
import json
import re
from pathlib import Path
from typing import Any


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def unescape_statblock_paragraphs(html: str) -> tuple[str, list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []

    def replace(match: re.Match[str]) -> str:
        inner = match.group(1)
        decoded = html_lib.unescape(inner).strip()
        if 'class="statblock-card"' not in decoded and "class='statblock-card'" not in decoded:
            return match.group(0)
        card_id_match = re.search(r'data-statblock-id=["\']([^"\']+)["\']', decoded)
        records.append(
            {
                "card_id": card_id_match.group(1) if card_id_match else None,
                "input_chars": len(inner),
                "output_chars": len(decoded),
            }
        )
        return "\n" + decoded + "\n"

    pattern = re.compile(r"<p>((?:(?!</p>).)*?&lt;div class=&quot;statblock-card&quot;(?:(?!</p>).)*?)</p>", re.I | re.S)
    return pattern.sub(replace, html), records


def unescape_anchor_paragraphs(html: str) -> tuple[str, list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []

    def replace(match: re.Match[str]) -> str:
        anchor_id = html_lib.unescape(match.group(1)).strip()
        records.append({"anchor_id": anchor_id})
        return f'\n<a id="{html_lib.escape(anchor_id, quote=True)}"></a>\n'

    pattern = re.compile(
        r"<p>\s*&lt;a\s+id=&quot;([A-Za-z0-9_-]+)&quot;&gt;&lt;/a&gt;\s*</p>",
        re.I,
    )
    return pattern.sub(replace, html), records


def class_token_count(text: str, token: str) -> int:
    count = 0
    for match in re.finditer(r'class=["\']([^"\']*)["\']', text, flags=re.I):
        if token in match.group(1).split():
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected-cards", type=int, default=22)
    args = parser.parse_args()

    original = args.html.read_text(encoding="utf-8")
    projected, records = unescape_statblock_paragraphs(original)
    projected, anchor_records = unescape_anchor_paragraphs(projected)
    card_count = class_token_count(projected, "statblock-card")
    structured_count = class_token_count(projected, "statblock-structured")
    escaped_remaining = len(re.findall(r"&lt;div class=&quot;statblock-card&quot;", projected, re.I))
    escaped_anchor_remaining = len(re.findall(r"&lt;a\s+id=&quot;", projected, re.I))
    findings: list[dict[str, Any]] = []
    if len(records) != args.expected_cards:
        findings.append(
            {
                "code": "unexpected_unescaped_statblock_count",
                "expected": args.expected_cards,
                "actual": len(records),
            }
        )
    if card_count < args.expected_cards:
        findings.append({"code": "statblock_card_count_below_expected", "expected": args.expected_cards, "actual": card_count})
    if structured_count < args.expected_cards:
        findings.append(
            {"code": "statblock_structured_count_below_expected", "expected": args.expected_cards, "actual": structured_count}
        )
    if escaped_remaining:
        findings.append({"code": "escaped_statblock_html_remaining", "count": escaped_remaining})
    if escaped_anchor_remaining:
        findings.append({"code": "escaped_anchor_html_remaining", "count": escaped_anchor_remaining})

    status = "pass" if not findings else "blocked"
    if status == "pass":
        args.html.write_text(projected, encoding="utf-8", newline="\n")

    report = {
        "schema": "kb_creator.unescape_projected_statblock_html.v1",
        "generated_at_utc": now_utc(),
        "status": status,
        "html": str(args.html).replace("\\", "/"),
        "input_sha256": sha256_text(original),
        "output_sha256": sha256_text(projected),
        "expected_cards": args.expected_cards,
        "unescaped_cards": len(records),
        "unescaped_anchors": len(anchor_records),
        "card_count": card_count,
        "structured_count": structured_count,
        "escaped_remaining": escaped_remaining,
        "escaped_anchor_remaining": escaped_anchor_remaining,
        "records": records,
        "anchor_records": anchor_records,
        "findings": findings,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"status={status} unescaped={len(records)} cards={card_count} "
        f"structured={structured_count} remaining={escaped_remaining} anchors={len(anchor_records)} report={args.report}"
    )
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
