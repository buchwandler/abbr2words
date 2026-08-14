"""Validate source/version metadata attached to benchmark failure reports."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

REQUIRED_METADATA = (
    "abbr2words_version",
    "spokenform_version",
    "abbr2words_source_commit",
    "spokenform_source_commit",
    "dataset_commit",
    "benchmark_profile",
    "normalization_options",
)


class FreshnessError(ValueError):
    """Raised when a benchmark report cannot be tied to a reproducible source."""


def current_source_commit(repository: str | Path = ".") -> str:
    """Return the repository commit used for freshness comparisons."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def report_metadata(report: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return nested report metadata, accepting summary or metadata JSON roots."""
    metadata = report.get("metadata", report)
    if not isinstance(metadata, Mapping):
        raise FreshnessError("benchmark metadata must be a JSON object")
    return metadata


def validate_metadata(
    report: Mapping[str, Any],
    *,
    expected_abbr2words_version: str | None = None,
    expected_abbr2words_source_commit: str | None = None,
    expected_spokenform_version: str | None = None,
    expected_spokenform_source_commit: str | None = None,
) -> Mapping[str, Any]:
    """Validate required metadata and optional current-source expectations."""
    metadata = report_metadata(report)
    missing = [
        key
        for key in REQUIRED_METADATA
        if key not in metadata or metadata[key] in (None, "", {})
    ]
    errors: list[str] = []
    if missing:
        errors.append("missing metadata: " + ", ".join(missing))
    options = metadata.get("normalization_options")
    if options is not None and not isinstance(options, Mapping):
        errors.append("normalization_options must be a JSON object")

    expected = {
        "abbr2words_version": expected_abbr2words_version,
        "abbr2words_source_commit": expected_abbr2words_source_commit,
        "spokenform_version": expected_spokenform_version,
        "spokenform_source_commit": expected_spokenform_source_commit,
    }
    for key, value in expected.items():
        if value is not None and metadata.get(key) != value:
            errors.append(f"{key} mismatch: report={metadata.get(key)!r}, expected={value!r}")
    if errors:
        raise FreshnessError("; ".join(errors))
    return metadata


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="summary.json or failures.json metadata report")
    parser.add_argument("--repository", type=Path, default=Path("."))
    parser.add_argument("--expect-abbr2words-version")
    parser.add_argument("--expect-abbr2words-source-commit")
    parser.add_argument("--expect-spokenform-version")
    parser.add_argument("--expect-spokenform-source-commit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = json.loads(args.report.read_text(encoding="utf-8"))
    if not isinstance(report, Mapping):
        raise FreshnessError("benchmark report must be a JSON object")
    expected_commit = args.expect_abbr2words_source_commit
    if expected_commit is None:
        expected_commit = current_source_commit(args.repository)
    expected_version = args.expect_abbr2words_version
    if expected_version is None:
        import abbr2words

        expected_version = abbr2words.__version__
    metadata = validate_metadata(
        report,
        expected_abbr2words_version=expected_version,
        expected_abbr2words_source_commit=expected_commit,
        expected_spokenform_version=args.expect_spokenform_version,
        expected_spokenform_source_commit=args.expect_spokenform_source_commit,
    )
    print(
        "fresh benchmark metadata: "
        f"abbr2words={metadata['abbr2words_version']} "
        f"spokenform={metadata['spokenform_version']} "
        f"profile={metadata['benchmark_profile']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FreshnessError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        raise SystemExit(f"benchmark freshness error: {error}") from error
