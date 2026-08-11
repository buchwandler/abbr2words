from __future__ import annotations

import json
import subprocess
import sys


def test_polynorm_diagnostic_classifies_stage_and_emits_trace(tmp_path) -> None:
    cases = tmp_path / "cases.jsonl"
    cases.write_text(
        "\n".join(
            json.dumps(row, ensure_ascii=False)
            for row in (
                {
                    "id": "lexical",
                    "lang": "fr",
                    "text": "Le Bd. Voltaire",
                    "expected_abbr2words": "Le boulevard Voltaire",
                },
                {
                    "id": "downstream",
                    "lang": "de",
                    "text": "Die Abb. zeigt Tab. 2.",
                    "expected": "Die Abbildung zeigt Tabelle zwei.",
                },
                {
                    "id": "entity",
                    "lang": "fr",
                    "text": "J.-P. Sartre",
                    "expected": "Jean-Paul Sartre",
                },
            )
        )
        + "\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "scripts/diagnose_polynorm_abbreviations.py", str(cases)],
        check=True,
        capture_output=True,
        text=True,
    )
    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert [row["classification"] for row in rows] == [
        "lexical-stage-match",
        "downstream-numeric-structured",
        "unsupported-benchmark-specific/entity",
    ]
    assert rows[0]["replacements"][0]["start"] == 3
    assert rows[0]["replacements"][0]["end"] == 6
