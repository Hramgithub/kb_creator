"""Occurrence-level terminology context shared by language producers."""

from __future__ import annotations

import re
from collections.abc import Collection


_SKILL_FIELDS = frozenset({"skill", "skills", "ability", "abilities", "proficiency", "proficiencies"})
_IDENTITY_FIELDS = frozenset({
    "occupation", "occupations", "profession", "professions", "career", "careers",
    "name", "names", "role", "roles", "cast", "character", "characters",
})
_PROPER_NAME_CONTEXT = re.compile(
    r"(?:Incan History(?: Book)?|Law Enforcement|Frederick Law Olmsted|in Archaeology circles)",
    re.IGNORECASE,
)
_CUE = re.compile(r"\b(?:rolls?|checks?|tests?|success|failure)\b|\d{1,3}%", re.IGNORECASE)
_PROFESSOR_OF_DISCIPLINES = re.compile(
    r"\bprofessor\s+of\s+[A-Za-z]+(?:\s+(?:and|&)\s+[A-Za-z]+)?\b",
    re.IGNORECASE,
)
_REVEALING_ALTERNATIVE = re.compile(
    r"^\s*(?:\(\s*or\s+(?:Hard|Extreme|Regular)?\s*(?:INT|EDU|POW|DEX|CON|STR|SIZ|APP)\s*\)\s*)?"
    r"(?:will\s+)?(?:reveal|reveals|uncover|uncovers|expose|exposes|show|shows|allow|allows|find|finds|notice|notices|detect|detects|identify|identifies|locate|locates)\b",
    re.IGNORECASE,
)
_ARTICLE_REVEAL = re.compile(
    r"^\s+(?:from|by|with|for|among)\b[^.,;:]{0,80}?\bwill\s+"
    r"(?:reveal|reveals|uncover|uncovers|expose|exposes|show|shows|allow|allows|find|finds|notice|notices|detect|detects|identify|identifies|locate|locates)\b",
    re.IGNORECASE,
)
_PARENTHESIZED_SKILL_ACTION = re.compile(
    r"\b(?:planning|navigating|driving|sneaking|sneak|climbing|jumping|searching|listening|tracking|hiding|dodging|fighting|persuading|charming|intimidating|spotting)\b"
    r"(?:\s+(?:the|a|an|up|quickly|carefully|directly|silently|around|through|across|route|path|way|building|vehicle|area)){0,5}\s*\(\s*$",
    re.IGNORECASE,
)
_NARRATIVE_PARENTHESIZED_SKILL_ACTION = re.compile(
    r"\b(?:find|search|inspect|open|notice|examine|look|talk|convince|persuade|"
    r"borrow|liberate|try|attempt|allow)\b(?:[^().]|\([^)]{0,80}\)){0,200}$",
    re.IGNORECASE,
)
_PARENTHESIZED_SKILL_ALTERNATIVE = re.compile(
    r"\(\s*([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*)\s+or\s+"
    r"([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*)\s*\)"
)
_ALTERNATIVE_ACTION = re.compile(
    r"\b(?:attempt(?:s|ing)?|assist(?:s|ing)?|help(?:s|ing)?|"
    r"try|tries|trying|use(?:s|d|ing)?|treat(?:s|ed|ing)?)\b[^()]{0,80}$",
    re.IGNORECASE,
)
_PARENTHESIZED_SKILL_RESULT = re.compile(
    r"^\s*\)\s*(?:,?\s*(?:to\s+(?:notice|reveal|find|show|allow)|"
    r"(?:they\s+)?(?:reveal|reveals|find|give))\b)",
    re.IGNORECASE,
)
_CLUE_LABEL = re.compile(r"^\s*clues\s*:", re.IGNORECASE)
_SKILL_LIST_INTRODUCTION = re.compile(r"\b(?:selection|list)\s+of\s+skills\s*:\s*$", re.IGNORECASE)


def _field_name(line: str) -> str:
    label = re.match(r"^\s*(?:>\s*)?(?:\*\*)?([A-Za-z][A-Za-z _/-]{1,40}):", line)
    return " ".join(label.group(1).casefold().replace("/", " ").split()) if label else ""


def _roll_clause(line: str, start: int, end: int) -> bool:
    """Recognize a bounded skill/characteristic list ending in a mechanic cue."""
    before = line[max(0, start - 120):start]
    after = line[end:min(len(line), end + 120)]
    if _REVEALING_ALTERNATIVE.match(after):
        return True
    if _ARTICLE_REVEAL.match(after):
        return True
    if re.match(r"^\s*using\b", line, re.I) and re.search(r"\broles?\b", line, re.I):
        return True
    if re.search(r"\b(?:rolls?|checks?|tests?)\b[^.;:]{0,100}$", before, re.I):
        return True
    if re.search(r"\b(?:using|use)\s*$", before, re.I):
        return True
    if re.match(r"^\s+with\s+(?:a\s+)?bonus die\b", after, re.I):
        return True
    cue = _CUE.search(after)
    if cue is None:
        return False
    return not re.search(r"[.!?]", after[:cue.start()])


def _exact_markdown_skill_heading(line: str, visible: str) -> bool:
    """Recognize only a standalone Markdown heading whose body is the skill."""
    body = re.sub(r"[*_]", "", line).strip()
    return re.fullmatch(rf"#{{1,6}}\s+{re.escape(visible)}\s*#*", body, re.IGNORECASE) is not None


def _academic_professorship(line: str, start: int, end: int) -> bool:
    """Keep a bounded academic-discipline phrase out of skill terminology."""
    return any(match.start() <= start and end <= match.end() for match in _PROFESSOR_OF_DISCIPLINES.finditer(line))


def _authorized_skills(values: Collection[str]) -> set[str]:
    return {value.casefold() for value in values if isinstance(value, str)}


def _explicit_authorized_alternative(line: str, term: str, authorized: set[str]) -> bool:
    """Recognize an action followed by a parenthesized pair of authorized skills."""
    if term.casefold() not in authorized:
        return False
    for alternative in _PARENTHESIZED_SKILL_ALTERNATIVE.finditer(line):
        names = {alternative.group(1).casefold(), alternative.group(2).casefold()}
        if term.casefold() in names and names <= authorized and _ALTERNATIVE_ACTION.search(line[:alternative.start()]):
            return True
    return False


def _explicit_authorized_parenthetical_skill(
    line: str, term: str, start: int, end: int, authorized: set[str], *, previous_line: str,
) -> bool:
    """Recognize local parenthetical skill notation only in a bounded mechanic clause."""
    if term.casefold() not in authorized:
        return False
    before, after = line[:start], line[end:]
    opening = re.search(r"\(\s*$", before)
    closing = re.match(r"\s*(?:[+-]\s*)?\d*%?\s*\)", after)
    if opening is None or closing is None:
        return False
    if re.fullmatch(r"\s*[+-]\s*\d+%\s*\)", closing.group(0)):
        return True
    if _PARENTHESIZED_SKILL_RESULT.match(after) or _CLUE_LABEL.match(line):
        return True
    action = before[:opening.start()]
    return (_PARENTHESIZED_SKILL_ACTION.search(action) is not None
            or _NARRATIVE_PARENTHESIZED_SKILL_ACTION.search(action) is not None)


def _authorized_skill_list_occurrence(line: str, term: str, authorized: set[str], *, previous_line: str) -> bool:
    """Recognize a skill list only after an explicit skills-list label."""
    return term.casefold() in authorized and bool(_SKILL_LIST_INTRODUCTION.search(previous_line)) and re.fullmatch(
        r"\s*(?:[A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*\s*,\s*)+"
        r"(?:and\s+)?[A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*\.\s*", line,
    ) is not None


def skill_context(
    term: str, text: str, *, authorized_skills: Collection[str] = (), predecessor_text: str = "",
) -> dict[str, object]:
    words = re.escape(term).replace("\\ ", r"\s+")
    pattern = re.compile(rf"(?<!\w)(?:\*{{2}}|__)?{words}(?:\*{{2}}|__)?(?!\w|-+\s*[a-z])", re.I)
    authorized = _authorized_skills(authorized_skills)
    rows = []
    for match in pattern.finditer(text):
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        if line_end < 0:
            line_end = len(text)
        line = text[line_start:line_end]
        previous_line_end = max(0, line_start - 1)
        previous_line_start = text.rfind("\n", 0, previous_line_end) + 1
        previous_line = text[previous_line_start:previous_line_end]
        while not previous_line.strip() and previous_line_start > 0:
            previous_line_end = max(0, previous_line_start - 1)
            previous_line_start = text.rfind("\n", 0, previous_line_end) + 1
            previous_line = text[previous_line_start:previous_line_end]
        if not previous_line.strip() and predecessor_text:
            previous_line = next((item for item in reversed(predecessor_text.splitlines()) if item.strip()), "")
        visible = re.sub(r"[*_]", "", match.group(0))
        label_name = _field_name(line)
        right = text[match.end():min(line_end, match.end() + 120)]
        line_match_start = match.start() - line_start
        line_match_end = match.end() - line_start
        explicit_suffix = visible.casefold().endswith((" roll", " check"))
        explicit_heading = _exact_markdown_skill_heading(line, visible)
        explicit = explicit_suffix or explicit_heading or _roll_clause(line, line_match_start, line_match_end)
        heading_after_table = explicit_heading and previous_line.lstrip().startswith("|")
        before = line[:match.start() - line_start]
        parenthesized = (
            _explicit_authorized_alternative(line, visible, authorized)
            or _explicit_authorized_parenthetical_skill(
                line, visible, line_match_start, line_match_end, authorized, previous_line=previous_line,
            )
            or _authorized_skill_list_occurrence(line, visible, authorized, previous_line=previous_line)
            or re.search(r"(?:navigation skills|driving ability)\s*\(", line, re.I)
            or _PARENTHESIZED_SKILL_ACTION.search(before)
            or _NARRATIVE_PARENTHESIZED_SKILL_ACTION.search(before)
            or re.search(r"knowledge of[^\n()]{0,100}\((?:or\s+)?[^)]*(?:check|roll|test)\b", right, re.I)
        )
        split_lowercase = re.match(r"-\s+[a-z]", right) is not None or re.match(r"[a-z]\s*-", line[max(0, match.start() - line_start - 4):match.start() - line_start]) is not None
        name_occurrence = any(
            named.start() <= match.start() - line_start
            and match.end() - line_start <= named.end()
            for named in _PROPER_NAME_CONTEXT.finditer(line)
        )
        academic_occurrence = _academic_professorship(line, line_match_start, line_match_end)
        if heading_after_table:
            kind = "excluded_non_skill_context"
        elif name_occurrence and label_name not in _SKILL_FIELDS:
            kind = "excluded_non_skill_context"
        elif academic_occurrence and not explicit:
            kind = "excluded_non_skill_context"
        elif visible[:1].islower() and not (explicit_suffix or explicit_heading):
            kind = "excluded_non_skill_context"
        elif label_name in _SKILL_FIELDS or explicit or parenthesized:
            kind = "required_skill"
        elif _PROPER_NAME_CONTEXT.search(line) and not explicit:
            kind = "excluded_non_skill_context"
        elif label_name in _IDENTITY_FIELDS or split_lowercase:
            kind = "excluded_non_skill_context"
        elif re.search(r"\b(?:works?|employed|hired|occupation|profession|career|job)\s*$", text[max(line_start, match.start() - 120):match.start()], re.I):
            kind = "excluded_non_skill_context"
        else:
            kind = "ambiguous"
        rows.append({"line": text.count("\n", 0, match.start()), "classification": kind, "start": match.start(), "end": match.end(), "text": visible})
    counts = {kind: sum(row["classification"] == kind for row in rows) for kind in ("required_skill", "excluded_non_skill_context", "ambiguous")}
    return {"applicability": "ambiguous" if counts["ambiguous"] else ("required_skill" if counts["required_skill"] else "excluded_non_skill_context"), "occurrences": len(rows), "required_occurrences": counts["required_skill"], "excluded_occurrences": counts["excluded_non_skill_context"], "ambiguous_occurrences": counts["ambiguous"], "source_lines": [row["line"] for row in rows], "occurrence_rows": rows}
