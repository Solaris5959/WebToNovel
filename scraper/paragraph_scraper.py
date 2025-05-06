"""
Scrapes chapter content from pages using <p> tags for text structure.
Returns a dictionary with the title and content.
"""

from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from scraper.browser_utils import create_stealth_context
from scraper.extract_chapter_title import extract_chapter_title

async def scrape_paragraph_chapter(url: str) -> dict:
    """
    Scrapes all <p> tags from a given webpage and returns structured chapter data.

    Args:
        url (str): The chapter page URL.

    Returns:
        dict: {
            "title": str | None,
            "content": str (HTML-formatted)
        }
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await create_stealth_context(browser)
        page = await context.new_page()

        await stealth_async(page)
        print(f"[INFO] Visiting: {url}")

        try:
            await page.goto(url, timeout=15000)
            await page.wait_for_load_state("networkidle", timeout=10000)

            # Extract title
            title = await extract_chapter_title(page)

            # Extract paragraphs
            paragraphs = page.locator("p")
            count = await paragraphs.count()
            results = []

            for i in range(count):
                text = await paragraphs.nth(i).inner_text()
                cleaned = text.strip()
                if cleaned:
                    results.append(f"<p>{cleaned}</p>")

            print(f"[INFO] Found {len(results)} paragraphs. Title: {title or '[None]'}")

            return {
                "title": title,
                "content": "\n".join(results)
            }

        except TimeoutError as e:
            print(f"[ERROR] Timeout while scraping: {e}")
        finally:
            await browser.close()

    return {"title": None, "content": ""}
