"""
Scrapes iframe-based web novel chapter pages.
Extracts only unencrypted content from the iframe.
"""

from playwright.async_api import async_playwright, Error


async def scrape_iframe_chapter(url: str) -> str:
    """
    Scrapes the chapter text from an iframe-based web novel page.

    Args:
        url (str): The chapter URL to scrape.

    Returns:
        str: The extracted chapter text or an empty string if not found.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print(f"[INFO] Navigating to {url}")

        try:
            await page.goto(url, timeout=15000)

            # Locate iframe and switch context
            iframe_element = await page.wait_for_selector("iframe", timeout=10000)
            iframe = await iframe_element.content_frame()

            if not iframe:
                print("[ERROR] Could not access iframe content.")
                return ""

            await iframe.wait_for_selector("#unencrypted-content", timeout=10000)
            content = await iframe.locator("#unencrypted-content").text_content()

            if content:
                print(f"[INFO] Extracted {len(content)} characters.")
                return content.strip()
            else:
                print("[WARN] Iframe loaded but content was empty.")
                return ""

        except TimeoutError as e:
            print(f"[ERROR] Timeout while scraping: {e}")
        except Error as e:
            print(f"[ERROR] Playwright error: {e}")
        finally:
            await browser.close()

    return ""
