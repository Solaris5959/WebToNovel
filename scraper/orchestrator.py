"""
This module orchestrates the scraping process by delegating tasks to specific scrapers.
It handles the extraction of chapter URLs from a table of contents (ToC) page
and the scraping of individual chapters using different methods.
"""
import asyncio
from typing import List, Dict
from scraper.toc_extractor import extract_toc_info
from scraper.iframe_scraper import scrape_iframe_chapter
from scraper.paragraph_scraper import scrape_paragraph_chapter

CONCURRENT_CHAPTER_LIMIT = 3
SCRAPER_MAP = {
    "iframe": scrape_iframe_chapter,
    "paragraph": scrape_paragraph_chapter,
}

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

async def scrape_all_chapters(toc_url: str, method: str) -> Dict[str, List[Dict[str, str]]]:
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

    # TEMP: limit for testing
    chapter_urls = chapter_urls[:5]
    print(f"[INFO] Total chapters found: {len(chapter_urls)}")

    semaphore = asyncio.Semaphore(CONCURRENT_CHAPTER_LIMIT)
    tasks = [scrape_chapter(url, method, semaphore) for url in chapter_urls]
    chapters = await asyncio.gather(*tasks)

    return {
        "title": novel_title,
        "chapters": chapters
    }
