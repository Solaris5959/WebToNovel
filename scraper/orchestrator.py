'''
This module orchestrates the scraping process by delegating tasks to specific scrapers.
It handles the extraction of chapter URLs from a table of contents (ToC) page
and the scraping of individual chapters using different methods.
'''
import asyncio
from typing import List
from scraper.toc_extractor import extract_all_chapter_urls
from scraper.iframe_scraper import scrape_iframe_chapter
from scraper.paragraph_scraper import scrape_paragraph_chapter

CONCURRENT_CHAPTER_LIMIT = 3
SCRAPER_MAP = {
    "iframe": scrape_iframe_chapter,
    "paragraph": scrape_paragraph_chapter,
}

async def scrape_chapter(url: str, method: str, semaphore: asyncio.Semaphore) -> str:
    """
    Delegates chapter scraping to the appropriate method.

    Args:
        url (str): Chapter URL.
        method (str): Either 'iframe' or 'paragraph'.
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests.

    Returns:
        str: Scraped chapter content (or empty string).
    """
    async with semaphore:
        try:
            return await SCRAPER_MAP[method](url)
        except Exception as e: # pylint: disable=broad-except
            print(f"[WARN] Failed to scrape {url}: {e}")
            return ""

async def scrape_all_chapters(toc_url: str, method: str) -> List[str]:
    """
    Orchestrates the full scraping pipeline from a ToC page, scraping chapters concurrently.

    Args:
        toc_url (str): Table of contents page.
        method (str): Which scraper to use for chapters.

    Returns:
        List[str]: List of full chapter texts.
    """
    print(f"[INFO] Starting full scrape using ToC: {toc_url}")
    chapter_urls = await extract_all_chapter_urls(toc_url)
    print(f"[INFO] Total chapters found: {len(chapter_urls)}")

    head_chapter_urls = chapter_urls[:CONCURRENT_CHAPTER_LIMIT]
    print(f"[INFO] Scraping first {CONCURRENT_CHAPTER_LIMIT} chapters: {head_chapter_urls}")

    semaphore = asyncio.Semaphore(CONCURRENT_CHAPTER_LIMIT)
    tasks = [
        scrape_chapter(url, method, semaphore)
        for url in head_chapter_urls
    ]

    return await asyncio.gather(*tasks)
