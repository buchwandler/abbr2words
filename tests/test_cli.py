from __future__ import annotations

import io
import sys

import pytest

from abbr2words.__main__ import main


def test_cli_expands_positional_text(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--lang", "de", "Prof. Klein kommt ggf."]) == 0
    assert capsys.readouterr().out == "Professor Klein kommt gegebenenfalls\n"


def test_cli_reads_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("Prof. Klein"))

    assert main(["--lang", "de"]) == 0
    assert capsys.readouterr().out == "Professor Klein\n"


def test_cli_languages(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--languages"]) == 0
    assert capsys.readouterr().out.splitlines() == ["cs", "de", "en", "es", "fr", "it", "pt"]


def test_cli_no_context(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--lang", "de", "--no-context", "Fr. Klein"]) == 0
    assert capsys.readouterr().out == "Freitag Klein\n"


def test_cli_invalid_language_exits_with_parser_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--lang", "xx", "Test"])

    assert exc_info.value.code == 2
    assert "Unsupported language" in capsys.readouterr().err
