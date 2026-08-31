"""Measure bulk and repeated abbreviation registration at glossary sizes."""

from __future__ import annotations

import tracemalloc
from time import perf_counter

from abbr2words import AbbreviationEntry, get_expander


def make_entries(size: int) -> tuple[AbbreviationEntry, ...]:
    return tuple(
        AbbreviationEntry(
            f"Term{index}",
            f"term expansion {index}",
            origin="custom",
        )
        for index in range(size)
    )


def measure_bulk(entries: tuple[AbbreviationEntry, ...]) -> tuple[float, float, float, int]:
    expander = get_expander("en")
    source = " ".join(entry.abbreviation for entry in entries)
    tracemalloc.start()
    started = perf_counter()
    expander.add_many(entries)
    registration = perf_counter() - started
    started = perf_counter()
    expander.expand(source)
    first_expansion = perf_counter() - started
    started = perf_counter()
    expander.expand(source)
    steady_expansion = perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return registration, first_expansion, steady_expansion, peak


def measure_repeated(entries: tuple[AbbreviationEntry, ...]) -> float:
    expander = get_expander("en")
    started = perf_counter()
    for entry in entries:
        expander.add_abbreviation(entry)
    return perf_counter() - started


def main() -> None:
    for size in (20, 500, 2000):
        entries = make_entries(size)
        bulk_registration, first, steady, peak = measure_bulk(entries)
        repeated_registration = measure_repeated(entries)
        print(
            f"{size:4d} entries: bulk={bulk_registration:.6f}s "
            f"repeated={repeated_registration:.6f}s first={first:.6f}s "
            f"steady={steady:.6f}s peak={peak / 1024:.1f}KiB"
        )


if __name__ == "__main__":
    main()
