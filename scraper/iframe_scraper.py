"""
Scrapes iframe-based web novel chapter pages.
Extracts unencrypted content and attempts to identify the chapter title.
"""

from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from scraper.browser_utils import create_stealth_context
from scraper.extract_chapter_title import extract_chapter_title


async def scrape_iframe_chapter(url: str) -> dict:
    """
    Scrapes the chapter text and title from an iframe-based web novel page.

    Args:
        url (str): The chapter URL to scrape.

    Returns:
        dict: {
            "title": str or None,
            "content": str
        }
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await create_stealth_context(browser)
        page = await context.new_page()

        await stealth_async(page)
        print(f"[INFO] Navigating to {url}")

        try:
            await page.goto(url, timeout=15000)

            iframe_element = await page.wait_for_selector("iframe", timeout=10000)
            iframe = await iframe_element.content_frame()

            if not iframe:
                print("[ERROR] Could not access iframe content.")
                return {"title": None, "content": ""}

            await iframe.wait_for_selector("#unencrypted-content", timeout=10000)
            content = await iframe.locator("#unencrypted-content").inner_html()

            title = await extract_chapter_title(page)

            if content:
                print(f"[INFO] Extracted {len(content)} characters with title: {title or '[None]'}")
                return {
                    "title": title,
                    "content": content.strip()
                }
            else:
                print("[WARN] Iframe loaded but content was empty.")
                return {"title": title, "content": ""}

        except TimeoutError as e:
            print(f"[ERROR] Timeout while scraping: {e}")
        finally:
            await browser.close()

    return {"title": None, "content": ""}
