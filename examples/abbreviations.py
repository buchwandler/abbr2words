#!/usr/bin/env python3
"""Demonstrate English abbreviation expansion without audio generation."""

from __future__ import annotations

import argparse

from abbr2words import abbr2words

TEXT = """
Good morning! Let me introduce you to some people.

Meet Mr. Schmidt, Mrs. Johnson, Ms. Anderson, and Dr. Brown.
Prof. Williams and Rev. Martinez will join us at 3:00 p.m..
St. Patrick's Cathedral is located on 5th Ave. in New York, N.Y..

The meeting is scheduled for Mon., Jan. 15th at the company headquarters.
Please arrive by 9:30 a.m. and bring your I.D. card.

Our office is at 123 Main St., Apt. 4B, Washington, D.C., U.S.A..
For questions, contact us via email at info@example.com or call us ASAP.

The package weighs 5 lbs. and measures 10 ft. by 3 in..
The temperature reached 98°F, or approximately 37°C.

Lt. Commander Harris served in the U.S. Navy for 15 yrs..
He earned a Ph.D. in Computer Science from MIT in Sept. 2010.

The company, founded in 1995 A.D., operates in the U.K., Canada, etc..
Our CEO, Mr. Thompson Jr., will present the Q&A session.

Please R.S.V.P. by Fri., Dec. 1st.
P.S. Don't forget to bring your laptop!

Sincerely,
Dr. Emily Clarke, M.D.
Vice President, Research & Development
ABC Corp., Inc.
"""


def parse_args() -> argparse.Namespace:
    """Parse the abbreviation-only example options."""
    parser = argparse.ArgumentParser(
        description="Expand abbreviations in the supplied English demonstration text."
    )
    parser.add_argument("--lang", default="en-us")
    parser.add_argument("--no-context", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Print the source text and its abbreviation-only expansion."""
    args = parse_args()
    result = abbr2words(TEXT, lang=args.lang, context=not args.no_context)
    if args.compact:
        print(result.strip())
    else:
        print("=== Source ===")
        print(TEXT.strip())
        print("\n=== Abbreviations only ===")
        print(result.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
