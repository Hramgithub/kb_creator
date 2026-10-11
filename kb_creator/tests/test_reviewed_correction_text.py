import pytest

from kb_creator.pipeline.reviewed_correction_text import (
    UnsupportedMarkdownError,
    VisibleCorrectionError,
    verify_visible_correction,
)


def span(start, end):
    return {"start_line": start, "end_line": end}


def test_projects_heading_list_quote_and_emphasis_without_normalizing_text():
    markdown = "# **AGE** of CTHULHU\n- Keep *1.2* exactly\n> # Объединённое управление\n"

    assert verify_visible_correction(markdown, "AGE", span(1, 1))["span_start_line"] == 1
    assert verify_visible_correction(markdown, "Keep 1.2 exactly", span(2, 2))["span_start_line"] == 2
    assert verify_visible_correction(markdown, "Объединённое управление", span(3, 3))["span_start_line"] == 3


def test_preserves_heading_content_that_looks_like_a_list():
    markdown = "# - 1. Text\n"

    assert verify_visible_correction(markdown, "- 1. Text", span(1, 1))["match_offset"] == 0


def test_rejects_ambiguous_nested_block_markers_instead_of_recursively_stripping():
    with pytest.raises(UnsupportedMarkdownError, match="nested block"):
        verify_visible_correction("- 1. 2. Text\n", "Text", span(1, 1))


def test_asterisk_list_parser_divergence_cannot_approve_a_correction():
    markdown = "* literal *\n"

    with pytest.raises(UnsupportedMarkdownError, match="differs between reader parsers"):
        verify_visible_correction(markdown, "literal *", span(1, 1))


def test_does_not_treat_12_as_exact_1_point_2():
    with pytest.raises(VisibleCorrectionError, match="absent"):
        verify_visible_correction("- Version 12\n", "1.2", span(1, 1))


def test_rejects_missing_word_and_cross_blank_line_concatenation():
    with pytest.raises(VisibleCorrectionError, match="absent"):
        verify_visible_correction("# Only two words\n", "Only three words", span(1, 1))
    with pytest.raises(VisibleCorrectionError, match="absent"):
        verify_visible_correction("Alpha\n\nBeta\n", "Alpha\nBeta", span(1, 3))


def test_link_destination_is_hidden_but_label_is_visible():
    markdown = "Read [the public label](https://hidden.example/correction) now.\n"

    assert verify_visible_correction(markdown, "the public label", span(1, 1))["match_offset"] == 5
    with pytest.raises(VisibleCorrectionError, match="absent"):
        verify_visible_correction(markdown, "https://hidden.example/correction", span(1, 1))


def test_literal_code_markers_are_preserved_and_not_mistaken_for_emphasis():
    markdown = "Use `a*b_c` and 2*3*4 exactly.\n"

    assert verify_visible_correction(markdown, "a*b_c", span(1, 1))["match_offset"] == 4
    assert verify_visible_correction(markdown, "2*3*4", span(1, 1))["match_offset"] == 14


def test_nested_code_delimiters_preserve_literal_inline_markdown():
    markdown = "Use ``a ` [not a link](https://literal.example)`` exactly.\n"

    assert verify_visible_correction(markdown, "a ` [not a link](https://literal.example)", span(1, 1))["match_offset"] == 4
    assert verify_visible_correction(markdown, "https://literal.example", span(1, 1))["match_offset"] == 21


def test_rejects_unsupported_or_malformed_inline_syntax_without_projecting_it():
    with pytest.raises(UnsupportedMarkdownError, match="nested inline link"):
        verify_visible_correction("[outer [inner]](https://example.test)\n", "inner", span(1, 1))
    with pytest.raises(UnsupportedMarkdownError, match="unclosed inline link"):
        verify_visible_correction("[missing](https://example.test\n", "missing", span(1, 1))
    with pytest.raises(UnsupportedMarkdownError, match="unclosed inline code"):
        verify_visible_correction("`unfinished code\n", "unfinished", span(1, 1))


def test_duplicate_visible_text_is_ambiguous_within_the_reviewed_unit():
    with pytest.raises(VisibleCorrectionError, match="ambiguous"):
        verify_visible_correction("- Exact\n- Exact\n", "Exact", span(1, 2))


def test_rejects_syntax_outside_the_contracted_visible_projection():
    with pytest.raises(UnsupportedMarkdownError, match="fenced"):
        verify_visible_correction("```\nExact\n```\n", "Exact", span(1, 3))
    with pytest.raises(UnsupportedMarkdownError, match="HTML"):
        verify_visible_correction("<span>Exact</span>\n", "Exact", span(1, 1))


@pytest.mark.parametrize(
    ("markdown", "corrected_text"),
    [
        ("- Source [public label](https://hidden.example/path)\n", "public label"),
        ("> # **AGE** of CTHULHU\n", "AGE"),
    ],
)
def test_portable_synthetic_reader_projection_fixtures(markdown, corrected_text):
    assert verify_visible_correction(markdown, corrected_text, span(1, 1))["span_start_line"] == 1
