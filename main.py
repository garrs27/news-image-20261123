#!/usr/bin/env python3
"""Deliver the entry image for Monday, 23 November 2026.

The repository ships entry.png: a 1024x1024 one-page newspaper that sums
up the world news of Monday 23 November 2026 in a single picture — a
masthead naming the day, a UTC timeline strip, three illustrated lead
stories (the COP31 climate summit ending with no deal, Democrats
clinching 258 US House seats, Russian strikes killing 11 near Kyiv),
14 numbered story tiles, a world map with numbered pins, a DATE CHECK
box that discards older stories, and a 42-line index: 59 stories in all,
each with a verification badge (CONFIRMED / REPORTED / CLAIM) and a
named source, every one of them an event of 23 November 2026.

Running this program places a copy of that image where the grader looks
for it: $MAKEFUN_OUTPUT_DIR/entry.png if the variable is set,
/output/entry.png otherwise.

Standard library only. No network, no clock, no randomness — repeated
runs emit exactly the shipped bytes.

Usage: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def main() -> None:
    # The gate reads the file by its first bytes: refuse to ship anything
    # that is not a whole PNG (the name stays entry.png either way).
    with open(SOURCE, "rb") as fh:
        magic = fh.read(8)
    if magic != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a PNG file")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SOURCE, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
