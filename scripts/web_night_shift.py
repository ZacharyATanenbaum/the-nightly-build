#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "beautifulsoup4>=4.12",
#   "feedparser>=6.0",
#   "pypdf>=5.0",
#   "requests>=2.32",
#   "trafilatura>=2.0",
# ]
# ///
"""Run the repository-native night shift's deterministic stages."""

from __future__ import annotations

import argparse

from nb_web.article import render
from nb_web.collect import prepare
from nb_web.research import research


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--library", required=True)

    research_parser = sub.add_parser("research")
    research_parser.add_argument("--selection", required=True)

    render_parser = sub.add_parser("render")
    render_parser.add_argument("--draft", required=True)

    args = parser.parse_args()
    if args.command == "prepare":
        return prepare(args.library)
    if args.command == "research":
        return research(args.selection)
    return render(args.draft)


if __name__ == "__main__":
    raise SystemExit(main())
