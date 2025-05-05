"""
This program scrapes a given URL (a web novel) for all its novel chapters
and stores them in JSON format, ready for conversion.
"""
import os
import json
import re
import asyncio
from scraper.orchestrator import scrape_all_chapters

TOC_URL = "https://noveltranslation.net/public/novel/14"
CHAPTERS_SUBDIR = "chapters"

def slugify(text: str) -> str:
    """
    Creates a safe folder name from a string.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text

def ensure_dirs(base_dir: str) -> str:
    """
    Ensures the output directory exists.

    Returns the path to the chapter subdirectory.
    """
    chapters_path = os.path.join(base_dir, CHAPTERS_SUBDIR)
    os.makedirs(chapters_path, exist_ok=True)
    print(f"[INFO] Output directory: '{chapters_path}'")
    return chapters_path

async def main():
    """
    Main function to run the scraping process and save chapters.
    """
    scrape_result = await scrape_all_chapters(TOC_URL, method="iframe")
    novel_title = scrape_result["title"]
    chapters = scrape_result["chapters"]

    folder_name = slugify(novel_title)
    base_output_dir = os.path.join("output", folder_name)
    chapters_path = ensure_dirs(base_output_dir)

    print(f"[INFO] Total chapters scraped: {len(chapters)}")

    for i, chapter in enumerate(chapters, start=1):
        chapter_data = {
            "number": i,
            "title": chapter["title"] or f"Chapter {i}",
            "content": chapter["content"]
        }

        filename = os.path.join(chapters_path, f"{i:03}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(chapter_data, f, ensure_ascii=False, indent=2)

        print(f"[INFO] Saved Chapter {i}: '{chapter_data['title']}' → {filename}")

    # Save metadata stub
    metadata_path = os.path.join(base_output_dir, "metadata.json")
    metadata = {
        "title": novel_title,
        "source": TOC_URL,
        "chapters": len(chapters)
    }
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Metadata saved at '{metadata_path}'")

if __name__ == "__main__":
    asyncio.run(main())
