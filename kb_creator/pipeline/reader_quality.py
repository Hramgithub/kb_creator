"""Reader-facing diagnostics and exact, reviewed proofreading amendments."""
from __future__ import annotations

import copy
import hashlib
import re
from typing import Any

LETTERS = r"A-Za-zА-Яа-яЁё"
SPACED = re.compile(rf"(?<!\w)(?:[{LETTERS}][ \t]+){{2,}}[{LETTERS}](?!\w)")


def text_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def scan_reader_units(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Emit review candidates; source facsimiles and prose need different decisions."""
    findings = []
    for row in units:
        text = row.get("final_ru_text", row.get("ru_text", ""))
        if text.startswith("<!--") or text.startswith("!["):
            continue
        for match in SPACED.finditer(text):
            findings.append({"unit_id": row["unit_id"], "kind": "literal_letter_spacing",
                             "text": match.group(), "offset": match.start()})
        if re.search(r"[ \t]{2,}\n", text):
            findings.append({"unit_id": row["unit_id"], "kind": "hard_break_requires_role_review"})
        if re.search(r"(?:стр\.|страниц[аеу]|(?<!\w)с\.)\s*\d+", text, re.I):
            findings.append({"unit_id": row["unit_id"], "kind": "source_page_reference"})
    return findings


def amend_proofread_submission(task: dict, submission: dict, corrections: list[dict]) -> tuple[dict, dict]:
    """Keep task authority and unchanged rows; never patch a sealed final package."""
    if submission.get("schema") != "kb_creator.five_step_language_proofread_submission.v2":
        raise ValueError("unsupported proofreading submission")
    expected, rows = task.get("units", []), submission.get("units", [])
    if not expected or len(expected) != len(rows):
        raise ValueError("full task coverage required")
    indexed = {}
    for e, row in zip(expected, rows):
        if any(row.get(k) != e.get(k) for k in ("unit_id", "source_hash", "draft_ru_sha256")):
            raise ValueError("task unit identity/order mismatch")
        if row["unit_id"] in indexed:
            raise ValueError("duplicate unit")
        indexed[row["unit_id"]] = row
    out = copy.deepcopy(submission)
    out.pop("submission_sha256", None)
    result = {row["unit_id"]: row for row in out["units"]}
    seen, ledger = set(), []
    for change in corrections:
        required = {"unit_id", "expected_final_ru_sha256", "final_ru_text", "reason"}
        if set(change) != required:
            raise ValueError("correction has unsupported fields")
        uid = change["unit_id"]
        if uid not in indexed or uid in seen:
            raise ValueError("unknown or duplicate correction unit")
        seen.add(uid)
        prior = indexed[uid]
        if text_sha(prior["final_ru_text"]) != change["expected_final_ru_sha256"]:
            raise ValueError("stale correction preimage")
        text, reason = change["final_ru_text"], change["reason"]
        if not isinstance(text, str) or not text.strip() or not isinstance(reason, str) or not reason.strip():
            raise ValueError("correction text and reason required")
        text = text.strip()
        if text == prior["final_ru_text"]:
            raise ValueError("no-op correction")
        row = result[uid]
        changed = text_sha(text) != row["draft_ru_sha256"]
        row.update(final_ru_text=text, disposition="changed" if changed else "checked_unchanged",
                   reason=reason if changed else "", unresolved=[])
        ledger.append({"unit_id": uid, "before_sha256": change["expected_final_ru_sha256"],
                       "after_sha256": text_sha(text), "reason": reason})
    return out, {"schema": "kb_creator.reader_correction_ledger.v1", "corrections": ledger,
                 "unchanged_units": len(rows) - len(ledger), "remaining_candidates": scan_reader_units(out["units"])}
