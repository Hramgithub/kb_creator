"""Shared canonical scanner for represented numeric mechanics."""

from __future__ import annotations

import re
from datetime import date


_CLOCK_EN = re.compile(r"(?<![\w])(?P<hour>1[0-2]|[1-9])(?::(?P<minute>[0-5]\d))?\s*(?P<meridiem>am|pm)\b", re.I)
_CLOCK_RU = re.compile(r"(?<![\w])(?P<hour>1[0-2]|[1-9])(?:(?::(?P<minute>[0-5]\d))|(?:\s+час(?:а|ов)?))?\s*(?P<meridiem>утра|дня|вечера|ночи)\b", re.I)
_CLOCK_24 = re.compile(r"(?<![\w])(?P<hour>(?:[01]?\d|2[0-3])):(?P<minute>[0-5]\d)(?!\d)")
_DURATION = re.compile(r"(?<![\w])(?P<value>\d+)\s*(?:-\s*)?(?:h(?:r|ours?)?\b|ч\b|час(?:а|ов)?\b)", re.I)
_ORDINAL = re.compile(r"(?<![\w])(?P<value>\d+)(?:st|nd|rd|th|-(?:й|го|я|е|ю|ым|ом|ую|ая|ое|ые|ых|ими))\b", re.I)
_CENTURY_EN = re.compile(r"(?<![\w])(?P<value>[1-9]\d?)(?:st|nd|rd|th)\s+century\b", re.I)
_WRITTEN_ORDINAL_UNITS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9,
}
_WRITTEN_ORDINAL_TEENS = {
    "tenth": 10, "eleventh": 11, "twelfth": 12, "thirteenth": 13,
    "fourteenth": 14, "fifteenth": 15, "sixteenth": 16, "seventeenth": 17,
    "eighteenth": 18, "nineteenth": 19,
}
_WRITTEN_ORDINAL_TENS = {
    "twentieth": 20, "thirtieth": 30, "fortieth": 40, "fiftieth": 50,
    "sixtieth": 60, "seventieth": 70, "eightieth": 80, "ninetieth": 90,
}
_WRITTEN_ORDINAL_TENS_PREFIXES = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}
_WRITTEN_ORDINAL_CENTURIES = {**_WRITTEN_ORDINAL_UNITS, **_WRITTEN_ORDINAL_TEENS, **_WRITTEN_ORDINAL_TENS}
_WRITTEN_ORDINAL_CENTURIES.update({prefix + "-" + suffix: value + unit for prefix, value in _WRITTEN_ORDINAL_TENS_PREFIXES.items() for suffix, unit in _WRITTEN_ORDINAL_UNITS.items()})
_WRITTEN_ORDINAL_CENTURY_PATTERN = "|".join(sorted(map(re.escape, _WRITTEN_ORDINAL_CENTURIES), key=len, reverse=True))
_CENTURY_EN_WRITTEN = re.compile(
    rf"(?<![\w])(?:(?P<qualifier>early|mid|late)\s+)?"
    rf"(?P<ordinal>{_WRITTEN_ORDINAL_CENTURY_PATTERN})\s+century\b",
    re.I,
)
_CENTURY_RU = re.compile(r"(?<![\w])(?P<roman>[IVXLCDM]+)\s+век(?:а|е|у|ом|ов)?\b", re.I)
_CENTURY_RU_ORDINAL = re.compile(r"(?<![\w])(?P<value>[1-9]\d?)-(?:й|го|м|му)\s+век(?:а|е|у|ом|ов)?\b", re.I)
_YEAR_VALUE_LIMIT = r"[1-9]\d?"
_AGE_EN = re.compile(rf"\bage\s+(?P<value>{_YEAR_VALUE_LIMIT})\b", re.I)
_AGE_EN_APPOSITIVE = re.compile(rf",\s*(?P<value>{_YEAR_VALUE_LIMIT})\s*,\s*(?:a|an|is|was)\b", re.I)
_YEAR_COMPOUND_EN_NUMERIC = re.compile(rf"(?<![\w])(?P<value>{_YEAR_VALUE_LIMIT})\s*-?\s*years?(?:-old)?\b", re.I)
_YEAR_RU_NUMERIC = re.compile(rf"(?<![\w])(?P<value>{_YEAR_VALUE_LIMIT})\s*(?:-\s*)?лет\b", re.I)
_DATE_EN_US = re.compile(r"(?<![\w/])(?P<month>0?[1-9]|1[0-2])/(?P<day>0?[1-9]|[12]\d|3[01])/(?P<year>\d{4})(?![\w/])")
_DATE_RU_DMY = re.compile(r"(?<![\w.])(?P<day>0?[1-9]|[12]\d|3[01])\.(?P<month>0?[1-9]|1[0-2])\.(?P<year>\d{4})(?![\w]|\.\d)")
_DATE_NUMBER = re.compile(r"(?<![\w])(?P<value>\d+)\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\b", re.I)
_QUALIFIED_CENTURY_EN = re.compile(r"(?<![\w])(?P<qualifier>early|mid|late)\s+(?P<base>[1-9]\d?00)s\b", re.I)
_QUALIFIED_CENTURY_RU = re.compile(r"(?<![\w])(?:с\s+)?(?P<qualifier>начала|начале|середины|середине|конца|конце)\s+(?P<roman>[IVXLCDM]+)\s+века\b", re.I)
_DECADE = re.compile(r"(?<![\w])(?P<value>\d{3,4})(?:s\b|-х(?:\s+год(?:ов|а)?)?\b)", re.I)
_PAGE_REFERENCE = re.compile(r"(?<!\w)(?:pp?\.?|с\.|стр\.)\s*(?P<value>\d+)(?!\w)", re.I)
_THOUSANDS = re.compile(r"(?<![\w\d])(?P<value>\d{1,3}(?:[, \u00A0\u202F]\d{3})+)(?![\w\d])")
_BASE = re.compile(r"(?<![\w])(?:\d+d\d+(?:[+\-−]\d+)?|\d+(?:[.,]\d+)?%|\d+(?:[.,]\d+)?)(?![\w])", re.I)


def _leading_modifier_sign(text: str, start: int) -> str:
    """Retain unary signs without interpreting ranges or list bullets as signs."""
    found = re.search(r"([+\-−–])([ \t]*)$", text[:start])
    if not found:
        return ""
    sign = found.group(1)
    before = text[:found.start()]
    # A spaced en dash is prose punctuation, e.g. "money – 50,000 rubles".
    # Mathematical minus U+2212 remains a sign even when spaced.
    if sign == "–" and found.group(2):
        return ""
    if sign != "+":
        # Connected names/areas (A-10, 1-2), numeric ranges (300 - 400),
        # and Markdown bullets (- 10 people) do not declare negative values.
        if before and re.match(r"\w", before[-1]):
            return ""
        if re.search(r"\d[ \t]*$", before):
            return ""
        line_prefix = before.rsplit("\n", 1)[-1]
        if sign == "-" and found.group(2) and not line_prefix.strip():
            return ""
    return "+" if sign == "+" else "-"


_RUSSIAN_YEAR_UNITS = {
    "одн": 1, "двух": 2, "трёх": 3, "трех": 3, "четырёх": 4, "четырех": 4,
    "пяти": 5, "шести": 6, "семи": 7, "восьми": 8, "девяти": 9,
}
_RUSSIAN_YEAR_TEENS = {
    "десяти": 10, "одиннадцати": 11, "двенадцати": 12, "тринадцати": 13,
    "четырнадцати": 14, "пятнадцати": 15, "шестнадцати": 16,
    "семнадцати": 17, "восемнадцати": 18, "девятнадцати": 19,
}
_RUSSIAN_YEAR_TENS = {
    "двадцати": 20, "тридцати": 30, "сорока": 40, "пятидесяти": 50,
    "шестидесяти": 60, "семидесяти": 70, "восьмидесяти": 80, "девяносто": 90,
}
_RUSSIAN_YEAR_STEMS = {**_RUSSIAN_YEAR_UNITS, **_RUSSIAN_YEAR_TEENS, **_RUSSIAN_YEAR_TENS}
_RUSSIAN_YEAR_STEMS.update({prefix + suffix: value + unit for prefix, value in _RUSSIAN_YEAR_TENS.items() for suffix, unit in _RUSSIAN_YEAR_UNITS.items()})
_RUSSIAN_YEAR_STEM_PATTERN = "|".join(sorted(map(re.escape, _RUSSIAN_YEAR_STEMS), key=len, reverse=True))
_YEAR_COMPOUND_RU = re.compile(rf"(?<![\w])(?P<stem>{_RUSSIAN_YEAR_STEM_PATTERN})летн[а-яё]*\b", re.I)

_ENGLISH_YEAR_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}
_ENGLISH_YEAR_WORDS.update({prefix + "-" + suffix: value + unit for prefix, value in list(_ENGLISH_YEAR_WORDS.items()) if value >= 20 and value % 10 == 0 for suffix, unit in list(_ENGLISH_YEAR_WORDS.items()) if 1 <= unit <= 9})
_ENGLISH_YEAR_WORD_PATTERN = "|".join(sorted(map(re.escape, _ENGLISH_YEAR_WORDS), key=len, reverse=True))
_YEAR_COMPOUND_EN_WORD = re.compile(rf"(?<![\w])(?P<word>{_ENGLISH_YEAR_WORD_PATTERN})\s*-?\s*year(?:-old)?\b", re.I)


def _roman_value(value: str) -> int:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    previous = 0
    for character in reversed(value.upper()):
        current = values[character]
        if current < previous:
            total -= current
        else:
            total += current
            previous = current
    return total


def _calendar_date(match: re.Match[str]) -> str | None:
    try:
        value = date(int(match.group('year')), int(match.group('month')), int(match.group('day')))
    except ValueError:
        return None
    return f'date:{value.isoformat()}'


def represented_numbers(text: str) -> list[str]:
    """Return sorted canonical tokens while consuming compound values once."""
    masked = re.sub(r"<!--.*?-->|(?:!?)\[[^\]]*\]\([^)]*\)", " ", text, flags=re.S)
    masked = re.sub(r"(?<![\w])1\s+(?:am|have|asked)\b", lambda m: m.group(0).replace("1", "I", 1), masked, flags=re.I)
    # Preserve numeric values attached to stat/unit labels while keeping dice
    # compounds intact; paths and source markers were masked above.
    masked = re.sub(r"(?<!\w)(\d+)(?=[A-Za-zА-Яа-я]{2,})(?!(?:st|nd|rd|th)\b)", r"\1 ", masked)
    masked = re.sub(r"([A-Za-zА-Яа-я]{2,})(\d+)", r"\1 \2", masked)
    spans: list[tuple[int, int, str]] = []

    def take(pattern: re.Pattern[str], convert) -> None:
        for match in pattern.finditer(masked):
            if any(match.start() < end and match.end() > start for start, end, _ in spans):
                continue
            token = convert(match)
            if token is not None:
                spans.append((match.start(), match.end(), token))

    def clock(match: re.Match[str]) -> str:
        hour = int(match.group("hour")); minute = int(match.group("minute") or 0)
        marker = match.groupdict().get("meridiem", "").casefold()
        if marker in {"pm", "вечера", "дня"} and hour != 12: hour += 12
        if marker in {"am", "утра", "ночи"} and hour == 12: hour = 0
        return f"time:{hour * 60 + minute}"

    take(_CLOCK_EN, clock); take(_CLOCK_RU, clock)
    take(_CLOCK_24, lambda m: f"time:{int(m.group('hour')) * 60 + int(m.group('minute'))}")
    take(_DATE_EN_US, _calendar_date); take(_DATE_RU_DMY, _calendar_date)
    take(_DURATION, lambda m: f"duration_hours:{int(m.group('value'))}")
    take(_QUALIFIED_CENTURY_EN, lambda m: f"century:{int(m.group('base')) // 100 + 1}:{m.group('qualifier').casefold()}")
    take(_QUALIFIED_CENTURY_RU, lambda m: f"century:{_roman_value(m.group('roman'))}:{ {'начала': 'early', 'начале': 'early', 'середины': 'mid', 'середине': 'mid', 'конца': 'late', 'конце': 'late'}[m.group('qualifier').casefold()] }")
    take(_CENTURY_EN_WRITTEN, lambda m: f"century:{_WRITTEN_ORDINAL_CENTURIES[m.group('ordinal').casefold()]}" + (f":{m.group('qualifier').casefold()}" if m.group('qualifier') else ""))
    take(_CENTURY_EN, lambda m: f"century:{int(m.group('value'))}")
    take(_CENTURY_RU, lambda m: f"century:{_roman_value(m.group('roman'))}")
    take(_CENTURY_RU_ORDINAL, lambda m: f"century:{int(m.group('value'))}")
    take(_AGE_EN, lambda m: f"years:{int(m.group('value'))}")
    take(_AGE_EN_APPOSITIVE, lambda m: f"years:{int(m.group('value'))}")
    take(_YEAR_COMPOUND_EN_NUMERIC, lambda m: f"years:{int(m.group('value'))}")
    take(_YEAR_COMPOUND_EN_WORD, lambda m: f"years:{_ENGLISH_YEAR_WORDS[m.group('word').casefold()]}")
    take(_YEAR_RU_NUMERIC, lambda m: f"years:{int(m.group('value'))}")
    take(_YEAR_COMPOUND_RU, lambda m: f"years:{_RUSSIAN_YEAR_STEMS[m.group('stem').casefold()]}")
    take(_ORDINAL, lambda m: f"number:{int(m.group('value'))}")
    take(_DATE_NUMBER, lambda m: f"number:{int(m.group('value'))}")
    take(_DECADE, lambda m: f"number:{int(m.group('value'))}")
    take(_PAGE_REFERENCE, lambda m: f"number:{int(m.group('value'))}")
    take(_THOUSANDS, lambda m: f"number:{_leading_modifier_sign(masked, m.start())}{m.group('value').replace(',', '').replace(' ', '').replace(chr(0x00A0), '').replace(chr(0x202F), '')}")
    for match in _BASE.finditer(masked):
        if any(match.start() < end and match.end() > start for start, end, _ in spans):
            continue
        value = _leading_modifier_sign(masked, match.start()) + match.group(0).replace(",", ".").replace("−", "-")
        if "d" in value.casefold(): token = f"dice:{value.casefold()}"
        elif value.endswith("%"): token = f"percent:{value[:-1]}"
        else: token = f"number:{value}"
        spans.append((match.start(), match.end(), token))
    return sorted(token for _, _, token in spans)
