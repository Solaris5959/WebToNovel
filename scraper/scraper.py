'''
    This module provides the functions to scrape a given url (a web novel) for all it's novel
    chapters.
'''
from typing import Optional, List, Literal
from playwright.sync_api import sync_playwright

def scrape_iframe(url: str) -> Optional[str]:
    """
    Uses Playwright to scrape only the unencrypted chapter content from a webpage with an iframe.

    Args:
        url (str): The chapter URL to scrape.

    Returns:
        Optional[str]: The extracted chapter text, or None if not found.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"[INFO] Navigating to {url}")
        try:
            page.goto(url, timeout=15000)

            # Wait for iframe to appear and get its handle
            iframe_element = page.wait_for_selector("iframe", timeout=10000)
            iframe = iframe_element.content_frame()

            if iframe is None:
                print("[ERROR] Could not get iframe content frame.")
                return None

            # Wait for the content in iframe to load
            iframe.wait_for_selector("#unencrypted-content", timeout=10000)
            content = iframe.locator("#unencrypted-content").text_content()

            if content:
                print(f"[INFO] Scraped {len(content)} characters of content.")
            else:
                print("[WARN] Found content block but it's empty.")
            return content

        except Exception as e:
            print(f"[ERROR] Failed to scrape content: {e}")
            return None

        finally:
            browser.close()

def scrape_paragraph(
    url: str,
    return_format: Literal["text", "html"] = "text"
) -> List[str]:
    """
    Scrapes all <p> tags from a given webpage.

    Args:
        url (str): The URL of the page to scrape.
        return_format (str): 'text' to get paragraph content only, 'html' to get full HTML of <p> tags.

    Returns:
        List[str]: A list of strings containing each paragraph.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"[INFO] Visiting: {url}")

        try:
            page.goto(url, timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)  # Wait for network to be idle

            # Collect all <p> elements
            paragraphs = page.locator("p")
            count = paragraphs.count()

            results = []
            for i in range(count):
                element = paragraphs.nth(i)
                if return_format == "html":
                    html = element.inner_html()
                    results.append(html.strip())
                else:
                    text = element.inner_text()
                    results.append(text.strip())

            print(f"[INFO] Found {count} <p> tags")
            return results

        except Exception as e:
            print(f"[ERROR] Failed to scrape paragraphs: {e}")
            return []

        finally:
            browser.close()