"""
This program scrapes a given URL (a web novel) for all its novel chapters
and stores them in JSON format, ready for conversion.
"""
import argparse
import asyncio
from pathlib import Path
from scraper import run_scrape_pipeline

def main():
    """
    Main function to parse arguments and run the scraping pipeline.
    It requires a URL to the first chapter of the novel and an output directory.
    The output directory will be created if it does not exist.
    The scraped chapters will be saved in JSON format, and an EPUB file will be generated.

    Called by the Flutter GUI to initiate the scraping process.
    """
    parser = argparse.ArgumentParser(description="Web novel scraper")
    parser.add_argument("--url", required=True, help="First chapter URL")
    parser.add_argument("--output", default="output", help="Base output directory")
    args = parser.parse_args()

    output = Path(args.output)
    asyncio.run(run_scrape_pipeline(args.url, output))

if __name__ == "__main__":
    main()
