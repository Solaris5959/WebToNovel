'''
    This program scrapes a given URL (a web novel) for all its novel chapters and converts it into a
    kindle-compatible file format.
'''
import os
from scraper.scraper import scrape_iframe, scrape_paragraph

# === Constants ===
IFRAME_URL = "https://noveltranslation.net/public/novel/1/chapter/1101"
PTAG_URL = "https://example.com"
OUTPUT_DIR = "output"
IFRAME_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "iframe_chapter.txt")
PTAG_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ptag_chapter.txt")


def ensure_output_dir():
    '''
    Ensures the output directory exists. If not, creates it.
    '''
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[INFO] Created output directory at '{OUTPUT_DIR}'")


def save_text_to_file(filepath: str, content: str):
    '''
    Saves given scraped content to a text file. Used for dev.
    '''
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[INFO] Saved output to {filepath}")


def main():
    '''
    Main function to run the scraper.
    '''
    ensure_output_dir()

    # 1. Scrape iframe-based chapter
    chapter_text = scrape_iframe(IFRAME_URL)

    if chapter_text:
        print(f"[INFO] Scraped {len(chapter_text)} characters from {IFRAME_URL}")
        save_text_to_file(IFRAME_OUTPUT_FILE, chapter_text)
    else:
        print("[WARN] No iframe chapter text found.")

    # 2. Scrape <p> tags from regular site
    paragraphs = scrape_paragraph(PTAG_URL, return_format="text")

    if paragraphs:
        print(f"[INFO] Scraped {len(paragraphs)} <p> tags from {PTAG_URL}")
        content = "\n\n".join(paragraphs)
        save_text_to_file(PTAG_OUTPUT_FILE, content)
    else:
        print("[WARN] No <p> tag content found.")


if __name__ == "__main__":
    main()
