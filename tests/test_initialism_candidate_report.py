from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.report_initialism_candidates import analyze_records, load_records


def test_analyze_records_groups_reasons_registry_and_flags() -> None:
    rows = analyze_records(
        [
            {
                "lang": "en",
                "text": "The DNA sample was stored.",
                "actual": "The DNA sample was stored.",
                "expected": "The D N A sample was stored.",
            },
            {
                "lang": "en",
                "text": "The FBI memo leaked.",
                "actual": "The FBI memo leaked.",
                "expected": "The F B I memo leaked.",
                "semantic_failure": False,
            },
            {
                "lang": "en",
                "text": "WORLD FIRST FILM",
                "actual": "WORLD FIRST FILM",
                "expected": "WORLD F I R S T FILM",
            },
            {
                "lang": "en",
                "text": "Keep TST hidden.",
                "actual": "Keep TST hidden.",
                "expected": "Keep T S T hidden.",
                "protected_spans": [[5, 8]],
            },
            {
                "lang": "en",
                "text": "Model IV was delayed.",
                "actual": "Model IV was delayed.",
                "expected": "Model I V was delayed.",
            },
            {
                "lang": "en",
                "text": "The QX arrived.",
                "actual": "The QX arrived.",
                "expected": "The Q X arrived.",
            },
            {
                "lang": "en",
                "text": "The DNA archive was moved.",
                "actual": "The DNA archive was moved.",
                "expected": "The D N A archive was moved.",
            },
        ]
    )

    assert [row["token"] for row in rows] == ["DNA", "FIRST", "IV", "QX", "TST", "FBI"]

    by_token = {row["token"]: row for row in rows}

    assert by_token["DNA"]["count"] == 2
    assert by_token["DNA"]["reason"] == "vowel-bearing-unknown"
    assert by_token["DNA"]["semantic_failures"] == 2
    assert by_token["DNA"]["registered"] is False
    assert by_token["DNA"]["actual_compact"] is True
    assert by_token["DNA"]["samples"] == [
        "The DNA sample was stored.",
        "The DNA archive was moved.",
    ]

    assert by_token["FBI"]["reason"] == "registered-semantic"
    assert by_token["FBI"]["registered"] is True
    assert by_token["FBI"]["registered_in_observed_locale"] is True
    assert "en" in by_token["FBI"]["registered_locales"]
    assert by_token["FBI"]["presentation_only"] == 1

    assert by_token["FIRST"]["uppercase_run"] is True
    assert by_token["FIRST"]["reason"] == "uppercase-run"

    assert by_token["TST"]["protected"] is True
    assert by_token["TST"]["reason"] == "protected-span"

    assert by_token["IV"]["roman_like"] is True
    assert by_token["IV"]["reason"] == "roman-like"

    assert by_token["QX"]["two_letter"] is True
    assert by_token["QX"]["reason"] == "two-letter-unknown"


def test_load_records_accepts_json_object_root_and_default_actual(tmp_path: Path) -> None:
    path = tmp_path / "failures.json"
    path.write_text(
        json.dumps(
            {
                "metadata": {"benchmark_profile": "proteno-en"},
                "failures": [
                    {
                        "lang": "en",
                        "text": "The DNA sample was stored.",
                        "expected": "The D N A sample was stored.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    records = load_records(path)
    rows = analyze_records(records)
    assert len(rows) == 1
    assert rows[0]["token"] == "DNA"
    assert rows[0]["reason"] == "vowel-bearing-unknown"
    assert rows[0]["actual_compact"] is True


def test_report_script_emits_csv_output(tmp_path: Path) -> None:
    path = tmp_path / "failures.jsonl"
    path.write_text(
        "\n".join(
            json.dumps(row)
            for row in (
                {
                    "lang": "en",
                    "text": "The DNA sample was stored.",
                    "actual": "The DNA sample was stored.",
                    "expected": "The D N A sample was stored.",
                },
                {
                    "lang": "en",
                    "text": "Keep TST hidden.",
                    "actual": "Keep TST hidden.",
                    "expected": "Keep T S T hidden.",
                    "protected_spans": [[5, 8]],
                },
            )
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "scripts/report_initialism_candidates.py", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    rows = list(csv.DictReader(result.stdout.splitlines()))
    assert [row["token"] for row in rows] == ["DNA", "TST"]
    assert rows[0]["reason"] == "vowel-bearing-unknown"
    assert rows[0]["registered"] == "False"
    assert rows[1]["protected"] == "True"
    assert rows[1]["samples"] == "Keep TST hidden."


def test_analyze_records_rejects_invalid_protected_spans() -> None:
    with pytest.raises(ValueError, match="protected_spans"):
        analyze_records(
            [
                {
                    "lang": "en",
                    "text": "Keep TST hidden.",
                    "actual": "Keep TST hidden.",
                    "expected": "Keep T S T hidden.",
                    "protected_spans": ["bad"],
                }
            ]
        )
