"""
Scrapes chapter content from pages using <p> tags for text structure.
"""

from playwright.async_api import async_playwright, Error


async def scrape_paragraph_chapter(url: str) -> str:
    """
    Scrapes all <p> tags from a given webpage and returns combined chapter text.

    Args:
        url (str): The chapter page URL.

    Returns:
        str: The concatenated paragraph text or empty string.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"[INFO] Visiting: {url}")

        try:
            await page.goto(url, timeout=15000)
            await page.wait_for_load_state("networkidle", timeout=10000)

            paragraphs = page.locator("p")
            count = await paragraphs.count()
            results = []

            for i in range(count):
                text = await paragraphs.nth(i).inner_text()
                cleaned = text.strip()
                if cleaned:
                    results.append(cleaned)

            print(f"[INFO] Found {len(results)} paragraphs.")
            return "\n\n".join(results)

        except TimeoutError as e:
            print(f"[ERROR] Timeout while scraping: {e}")
        except Error as e:
            print(f"[ERROR] Playwright error: {e}")
        finally:
            await browser.close()

    return ""
