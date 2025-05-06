"""
This module orchestrates the scraping process by delegating tasks to specific scrapers.
It handles the extraction of chapter URLs from a table of contents (ToC) page
and the scraping of individual chapters using different methods.
"""
import asyncio
import json
from pathlib import Path
from typing import Dict
from scraper.utils import slugify
from scraper.toc_extractor import extract_toc_info
from scraper.iframe_scraper import scrape_iframe_chapter
from scraper.paragraph_scraper import scrape_paragraph_chapter

CONCURRENT_CHAPTER_LIMIT = 3
SCRAPER_MAP = {
    "iframe": scrape_iframe_chapter,
    "paragraph": scrape_paragraph_chapter,
}

def get_existing_chapter_urls(chapters_dir: Path) -> set:
    """
    Returns a set of chapter URLs that already exist and have content.
    Assumes chapter files are named with numeric keys (001.json, 002.json, etc.)
    """
    completed = set()
    for path in chapters_dir.glob("*.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("content") and len(data["content"].strip()) > 50:
                    completed.add(data.get("source_url"))
        except FileNotFoundError as e:
            print(f"[WARN] Couldn't read {path.name}: {e}")
    return completed

async def scrape_chapter(url: str, method: str, semaphore: asyncio.Semaphore) -> Dict[str, str]:
    """
    Delegates chapter scraping to the appropriate method.

    Args:
        url (str): Chapter URL.
        method (str): Either 'iframe' or 'paragraph'.
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests.

    Returns:
        dict: { "title": str or None, "content": str }
    """
    async with semaphore:
        try:
            return await SCRAPER_MAP[method](url)
        except Exception as e:  # pylint: disable=broad-except
            print(f"[WARN] Failed to scrape {url}: {e}")
            return {"title": None, "content": ""}

async def scrape_all_chapters(toc_url: str, method: str, output_base_dir: Path) -> Dict:
    """
    Orchestrates the full scraping pipeline from a ToC page, scraping chapters concurrently.

    Args:
        toc_url (str): Table of contents page.
        method (str): Which scraper to use for chapters.

    Returns:
        dict: {
            "title": str,
            "chapters": List[ { "title": str, "content": str } ]
        }
    """
    print(f"[INFO] Starting full scrape using ToC: {toc_url}")
    toc_info = await extract_toc_info(toc_url)
    chapter_urls = toc_info["chapter_urls"]
    novel_title = toc_info["title"]
    slug = slugify(novel_title)
    chapters_dir = output_base_dir / slug / "chapters"

    # Load completed URLs to skip
    completed_urls = get_existing_chapter_urls(chapters_dir)
    print(f"[INFO] Skipping {len(completed_urls)} already-downloaded chapters.")

    filtered_urls = [url for url in chapter_urls if url not in completed_urls]

    print(f"[INFO] Chapters to scrape: {len(filtered_urls)}")
    semaphore = asyncio.Semaphore(CONCURRENT_CHAPTER_LIMIT)
    tasks = [scrape_chapter(url, method, semaphore) for url in filtered_urls]
    chapters = await asyncio.gather(*tasks)

    return {
        "title": novel_title,
        "chapter_urls": chapter_urls,
        "cover_image_url": toc_info.get("cover_image_url"),
        "scraped_chapters": chapters,
        "scraped_urls": filtered_urls,
    }
