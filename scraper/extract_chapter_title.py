'''
Contains methods related to extracting chapter titles from web pages.
'''
import re
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
