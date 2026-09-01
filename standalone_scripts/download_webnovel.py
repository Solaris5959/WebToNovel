"""
This program scrapes a given URL (a web novel) for all its novel chapters
and stores them in JSON format, ready for conversion.

It is designed to be called from the Flutter GUI or CLI.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from scraper import run_scrape_pipeline


def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Web novel scraper")
    parser.add_argument(
        "--url",
        required=True,
        help="First chapter or TOC URL of the novel"
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Base output directory (default: ./output/)"
    )
    return parser.parse_args()


def main():
    """
    Main function to run the web novel scraper.
    """
    args = parse_args()
    output = Path(args.output)

    print(f"[INFO] Starting scrape from: {args.url}")
    print(f"[INFO] Output base directory: {output.resolve()}")

    try:
        asyncio.run(run_scrape_pipeline(args.url, output))
        print("[INFO] Scraping completed successfully.")
        sys.exit(0)
    except Exception as e: # pylint: disable=broad-except
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
