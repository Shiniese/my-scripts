# /// script
# dependencies = [
#   "ddgs",
#   "zendriver",
#   "readability-lxml",
# ]
# ///

"""
DDGS text search CLI tool
"""

import argparse
from ddgs import DDGS
import json
import asyncio


def search(args):
    results = DDGS().text(
        query=args.query,
        region=args.region,
        safesearch=args.safesearch,
        timelimit=args.timelimit,
        max_results=args.max_results,
        page=args.page,
        backend=args.backend,
    )
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Performs a web search using multiple search engine backends."
    )

    parser.add_argument(
        "query",
        type=str,
        help="Search query text"
    )

    parser.add_argument(
        "--region",
        default="us-en",
        help="Region code (default: us-en)"
    )

    parser.add_argument(
        "--safesearch",
        default="off",
        choices=["on", "moderate", "off"],
        help="Safe search level (default: off)"
    )

    parser.add_argument(
        "--timelimit",
        choices=["d", "w", "m", "y"],
        default=None,
        help="Time limit: d, w, m, y (default: None)"
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)"
    )

    parser.add_argument(
        "--page",
        type=int,
        default=1,
        help="Page number (default: 1)"
    )

    parser.add_argument(
        "--backend",
        choices=["auto", "bing", "brave", "duckduckgo", "google", "grokipedia", "mojeek", "yandex", "yahoo", "wikipedia"],
        default="auto",
        help="Backend engine (default: auto)"
    )

    parser.add_argument(
        "--detailed_content",
        action="store_true",
        help="Will fetch and extract readable content using a headless browser."
    )

    parser.add_argument(
        "--readable_text",
        action="store_true",
        help="Print results as readable text"
    )

    args = parser.parse_args()

    results = search(args)

    if args.detailed_content:
        from web_fetch import fetch_relevant_web_pages
        results = asyncio.run(fetch_relevant_web_pages([r.get('href') for r in results]))

    if args.readable_text:
        for i, r in enumerate(results, 1):
            print(f"{i}. {r.get('title')}")
            print(f"   URL: {r.get('href')}")
            print(f"   Content: {r.get('body')}")
            print()
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()