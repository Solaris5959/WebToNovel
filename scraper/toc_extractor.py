"""
Extracts chapter URLs from a novel's table of contents (ToC) page.
Handles pagination, preview sections, and ensures correct chapter order.
"""

import re
from typing import List, Optional
from urllib.parse import urljoin

from playwright.async_api import async_playwright, Error, Locator


CHAPTER_LINK_CONTAINER_SELECTOR = ".chapter-list, .toc, .chapters, .list-chapters"
CHAPTER_LINK_SELECTOR = "a[href*='chapter'], a[href*='chap'], a[href*='ep']"
PAGINATION_CONTAINER_SELECTOR = "nav.pagination, ul.pagination, div.pagination, .pagination"


def is_valid_chapter_link(href: str) -> bool:
    """Heuristic to exclude preview/latest/etc. links."""
    href = href.lower()
    return all(term not in href for term in ["preview", "latest", "updates", "#"])

def extract_numeric_hint(url: str) -> int:
    """Try to extract a chapter number from a URL for sorting."""
    match = re.search(r'chapter[-_ /]?(\d+)', url.lower())
    if not match:
        match = re.search(r'(\d+)', url)
    return int(match.group(1)) if match else 0

async def find_next_pagination_button(page) -> Optional[Locator]:
    """
    Attempts to locate a reliable "next page" button within pagination controls.
    Handles various formats like rel="next", <li class="next">, or arrow links.
    """
    # Priority 1: rel="next"
    button = page.locator("a[rel='next']")
    if await button.count() > 0:
        return button.first

    # Priority 2: <li class="next"> > a
    button = page.locator("li.next > a")
    if await button.count() > 0:
        return button.first

    # Priority 3: <li class*='skipToNext'> > a
    button = page.locator("li[class*='skipToNext'] > a")
    if await button.count() > 0:
        return button.first

    # Priority 4: fallback on arrow-looking buttons
    for symbol in [">", "›", "→", ">>"]:
        button = page.locator(f"{PAGINATION_CONTAINER_SELECTOR} a:has-text('{symbol}')")
        if await button.count() > 0:
            href = await button.first.get_attribute("href") or ""
            if "chapter" not in href.lower():
                return button.first

    return None

async def extract_all_chapter_urls(toc_url: str) -> List[str]:
    """
    Scrapes all chapter URLs from a table of contents page.
    Supports paginated ToC pages and sorts chapters in ascending order.

    Args:
        toc_url (str): URL to the table of contents.

    Returns:
        List[str]: Ordered list of chapter URLs (first chapter to latest).
    """
    chapter_urls = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"[INFO] Navigating to ToC: {toc_url}")

        try:
            await page.goto(toc_url, timeout=15000)

            while True:
                # Scope scraping to main ToC containers if available
                container = page.locator(CHAPTER_LINK_CONTAINER_SELECTOR)
                if await container.count() == 0:
                    container = page  # fallback to full page

                links = await container.locator(CHAPTER_LINK_SELECTOR).all()
                urls = []

                for link in links:
                    href = await link.get_attribute("href")
                    if href and is_valid_chapter_link(href):
                        full_url = urljoin(toc_url, href)
                        urls.append(full_url)

                print(f"[INFO] Found {len(urls)} valid chapter links on this page.")
                chapter_urls.extend(urls)

                # Detect next pagination button
                next_button = await find_next_pagination_button(page)
                if not next_button:
                    print("[INFO] No next page button found. Pagination complete.")
                    break

                print("[INFO] Navigating to next ToC page...")
                await next_button.click()
                await page.wait_for_timeout(1500)

        except (TimeoutError, Error) as e:
            print(f"[ERROR] Failed during ToC extraction: {e}")

        finally:
            await browser.close()

    # Deduplicate and sort
    unique_urls = list(dict.fromkeys(chapter_urls))
    sorted_urls = sorted(unique_urls, key=extract_numeric_hint)

    print(f"[INFO] Total unique, sorted chapter URLs: {len(sorted_urls)}")
    return sorted_urls
