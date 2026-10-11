"""Explicit review roots must reach APIs through the operator commands."""
import sys
from pathlib import Path

from kb_creator.scripts import continue_language, continue_source_choices


def test_source_choice_v2_cli_forwards_binding_root(monkeypatch, capsys):
    observed = []

    def prepare(master, candidate, output, *, binding_root=None):
        observed.append((master, candidate, output, binding_root))
        return {"state": "prepared"}

    monkeypatch.setattr(continue_source_choices, "prepare_v2", prepare)
    monkeypatch.setattr(sys, "argv", ["continue_source_choices", "prepare-v2",
        "book/master", "book/mechanical", "book/queue", "--binding-root", "book"])
    assert continue_source_choices.main() == 0
    assert observed == [(Path("book/master"), Path("book/mechanical"), Path("book/queue"), Path("book"))]
    assert '"prepared"' in capsys.readouterr().out


def test_language_prepare_cli_forwards_binding_root(monkeypatch, capsys):
    observed = []

    def prepare(master, glossary, output, **kwargs):
        observed.append(kwargs.get("review_binding_root"))
        return {"phase": "documentary_draft"}

    monkeypatch.setattr(continue_language, "prepare_continuation", prepare)
    monkeypatch.setattr(sys, "argv", ["continue_language", "prepare",
        "--predecessor-run", "book/master", "--glossary", "book/terms.json",
        "--output", "book/language", "--binding-root", "book"])
    assert continue_language.main() == 0
    assert observed == [Path("book")]
    assert '"documentary_draft"' in capsys.readouterr().out
