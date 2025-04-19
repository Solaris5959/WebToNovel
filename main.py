'''
    This program scrapes a given URL (a web novel) for all its novel chapters and converts it into a
    kindle-compatible file format.
'''
import os
import asyncio
from scraper.orchestrator import scrape_all_chapters

# === Constants ===
OUTPUT_DIR = "output"
TOC_URL = "https://novgo.net/lord-of-the-mysteries.html"


def ensure_output_dir():
    '''
    Ensures the output directory exists. If not, creates it.
    '''
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[INFO] Created output directory at '{OUTPUT_DIR}'")

async def main():
    '''
    Main function to run the scraping process.
    '''
    ensure_output_dir()

    chapters = await scrape_all_chapters(TOC_URL, method="iframe")

    for i, chapter in enumerate(chapters):
        with open(f"output/chapter_{i+1}.txt", "w", encoding="utf-8") as f:
            f.write(chapter)


if __name__ == "__main__":
    asyncio.run(main())
