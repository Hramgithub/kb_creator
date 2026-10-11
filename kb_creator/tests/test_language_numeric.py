from kb_creator.pipeline.language_numeric import represented_numbers


def test_page_reference_translation_preserves_visible_page_number():
    for source in ("see p31", "see p.31", "see p. 31", "see pp. 31"):
        assert represented_numbers(source) == represented_numbers("см. с.31") == ["number:31"]
        assert represented_numbers(source) == represented_numbers("см. стр. 31")
        assert represented_numbers(source) != represented_numbers("см. с.32")


def test_page_reference_does_not_consume_dice_identifiers_or_asset_paths():
    assert represented_numbers("p31 1d10+2") == ["dice:1d10+2", "number:31"]
    assert represented_numbers("p31x") == []
    assert represented_numbers("![p31](assets/p31.png)") == []


def test_qualified_english_and_russian_centuries_have_narrow_equivalence():
    assert represented_numbers("late 1500s") == represented_numbers("с конца XVI века") == ["century:16:late"]
    assert represented_numbers("late 1500s") != represented_numbers("с конца XV века")
    assert represented_numbers("late 1500s") != represented_numbers("с конца XVII века")
    assert represented_numbers("late 1500s") != represented_numbers("с начала XVI века")
    assert represented_numbers("late 1500s") != represented_numbers("с середины XVI века")


def test_century_rule_does_not_consume_unqualified_decades_or_other_numbers():
    assert represented_numbers("1500s") == ["number:1500"]
    assert represented_numbers("late 1500s 1924 1d6 70%") == ["century:16:late", "dice:1d6", "number:1924", "percent:70"]


def test_qualified_decades_do_not_equal_whole_centuries():
    for source, broad_ru, token in (
        ("late 1590s", "с конца XVI века", "number:1590"),
        ("late 1520s", "с конца XVI века", "number:1520"),
        ("late 1990s", "с конца XX века", "number:1990"),
        ("early 1520s", "с начала XVI века", "number:1520"),
        ("mid 1990s", "с середины XX века", "number:1990"),
    ):
        assert represented_numbers(source) == [token]
        assert represented_numbers(source) != represented_numbers(broad_ru)


def test_documentary_gate_rejects_decade_to_century_drift(tmp_path):
    import json
    from kb_creator.pipeline.five_step_language import _mechanics
    glossary = tmp_path / "glossary.json"
    glossary.write_text(json.dumps({"terms": [{"source": "Keeper", "target": "Хранитель"}]}))
    for year, roman in ((1590, "XVI"), (1520, "XVI"), (1990, "XX")):
        findings = _mechanics([{"unit_id": "example", "source_text": f"Built in the late {year}s.",
                                "ru_text": f"Построено с конца {roman} века."}], glossary)
        assert {row["code"] for row in findings} == {"markdown_or_mechanics_drift"}


def test_full_us_and_russian_calendar_dates_are_equivalent_only_when_valid():
    assert represented_numbers("The appointment is 1/24/2007.") == represented_numbers("Приём назначен на 24.01.2007.") == ["date:2007-01-24"]
    for changed in ("25.01.2007", "24.02.2007", "24.01.2008"):
        assert represented_numbers("1/24/2007") != represented_numbers(changed)
    # Calendar validation intentionally declines impossible dates rather than
    # inventing a date token from a partial or malformed source value.
    assert not any(token.startswith("date:") for token in represented_numbers("2/30/2007 30.02.2007 1/2"))


def test_single_digit_24_hour_clock_and_numeric_plural_years_are_equivalent():
    assert represented_numbers("Meet at 7:00 and leave at 8:00.") == represented_numbers("Встретимся в 07:00 и уйдём в 08:00.") == ["time:420", "time:480"]
    assert represented_numbers("30 years later") == represented_numbers("30 лет спустя") == ["years:30"]
    assert represented_numbers("7:01") != represented_numbers("7:02")
    assert represented_numbers("30 years") != represented_numbers("31 лет")


def test_date_and_clock_extension_preserves_rolls_percentages_and_amounts():
    assert represented_numbers("Roll 1d6/2 for 70% of $1,200.") == ["dice:1d6", "number:1200", "number:2", "percent:70"]
    assert represented_numbers("24:00 7:60 1/2/07") == ["number:00", "number:07", "number:1", "number:2", "number:24", "number:60", "number:7"]
