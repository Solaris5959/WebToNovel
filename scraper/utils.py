"""
Contains utility functions for the web scraper
"""
import re
from pathlib import Path
import requests
from playwright.async_api import Page

TITLE_SELECTORS = [
    "h1", "h2", "h3",
    ".chapter-title", "#chapter-title",
    "p strong", "p", "div.title"
]

TITLE_REGEX = re.compile(r"(Chapter|Ch\.|Episode|Ep\.)\s*(\d+)(?:\s*[-–:]?\s*(.*))?", re.IGNORECASE)


async def extract_chapter_title(page: Page) -> str | None:
    '''
    Extracts the chapter title from the page using various selectors.
    '''
    candidates = []

    for selector in TITLE_SELECTORS:
        elements = await page.query_selector_all(selector)
        for el in elements:
            text = (await el.text_content() or "").strip()
            if TITLE_REGEX.search(text):
                candidates.append(text)

    if candidates:
        # Return the first matching high-confidence result
        return candidates[0]

    # Fallback: check first few text lines from page body
    body_text = await page.content()
    lines = [line.strip() for line in body_text.splitlines() if line.strip()]
    for line in lines[:5]:
        if TITLE_REGEX.search(line):
            return line

    return None

def slugify(text: str) -> str:
    """
    Convert a string into a URL-friendly slug.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text

def download_image(url: str, output_path: Path) -> bool:
    """
    Downloads an image from a URL to a local file.

    Args:
        url (str): Image URL.
        output_path (Path): Path to save the file.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        print(f"[INFO] Downloading image from {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"[INFO] Cover image saved to {output_path}")
        return True
    except FileNotFoundError as e:
        print(f"[WARN] Failed to download cover image: {e}")
        return False
