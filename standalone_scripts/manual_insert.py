import argparse
import asyncio
import json
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from saver.novel_saver import save_metadata
from scraper.iframe_scraper import scrape_iframe_chapter
from scraper.paragraph_scraper import scrape_paragraph_chapter

SCRAPER_MAP = {
    "iframe": scrape_iframe_chapter,
    "paragraph": scrape_paragraph_chapter,
}

def extract_number_from_title(title: str) -> int | None:
    match = re.search(r"(?:chapter|ch)\s*[-:]?\s*(\d+)", title.lower())
    return int(match.group(1)) if match else None

async def main(toc_url: str, chapter_url: str, method: str):
    novel_dir = resolve_novel_dir_from_toc_url(toc_url)
    if not novel_dir:
        print("[ERROR] Could not locate novel directory for the given ToC URL. " \
        "Make sure the novel was scraped first.")
        return
    chapters_dir = novel_dir / "chapters"

    # Scrape the manual chapter
    chapter_data = await SCRAPER_MAP[method](chapter_url)
    if not chapter_data["content"].strip():
        print("[ERROR] Chapter content is empty. Aborting.")
        return

    # Determine insert index (auto or manual fallback)
    index = extract_number_from_title(chapter_data["title"] or "") or (
        len(list(chapters_dir.glob("*.json"))) + 1
    )
    print(f"[INFO] Inserting chapter at position: {index}")

    existing_path = chapters_dir / f"{index:03}.json"
    if existing_path.exists():
        with open(existing_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

        # Check for match based on URL or title
        if existing.get("source_url") == chapter_url or existing.get("" \
            "title") == chapter_data["title"]:
            print(f"[INFO] Chapter already exists at position {index}. Skipping insert.")
            return
        print(f"[WARN] Chapter {index} already exists with different content. Proceeding to shift.")

    new_path = chapters_dir / f"{index:03}.json"

    if new_path.exists():
        with open(new_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

        if existing.get("source_url") == chapter_url or existing.get("" \
            "title") == chapter_data["title"]:
            print(f"[INFO] Chapter already exists at position {index}. Skipping insert.")
            return
        else:
            print(f"[WARN] Chapter {index} already exists with different content. " \
                  "Proceeding to shift.")

        # Shift later chapters forward starting from index
        existing_files = sorted(chapters_dir.glob("*.json"), key=lambda f: int(f.stem))
        for file in reversed(existing_files):
            num = int(file.stem)
            if num >= index:
                shifted_path = chapters_dir / f"{num + 1:03}.json"
                with open(file, "r", encoding="utf-8") as f:
                    shift_data = json.load(f)
                shift_data["number"] = num + 1
                with open(shifted_path, "w", encoding="utf-8") as f:
                    json.dump(shift_data, f, ensure_ascii=False, indent=2)
                file.unlink()
    else:
        print(f"[INFO] No file exists at {index:03}.json, inserting without shift.")


    # Save new chapter
    new_path = chapters_dir / f"{index:03}.json"
    with open(new_path, "w", encoding="utf-8") as f:
        json.dump({
            "number": index,
            "title": chapter_data["title"] or f"Chapter {index}",
            "content": chapter_data["content"],
            "source_url": chapter_url
        }, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Saved new chapter to {new_path}")

    metadata_path = novel_dir / "metadata.json"
    if not metadata_path.exists():
        print("[ERROR] Metadata file is missing. Cannot update metadata.")
        return

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    title = metadata.get("title", "Unknown Title")

    save_metadata(title=title, source_url=toc_url, novel_dir=novel_dir)

def resolve_novel_dir_from_toc_url(toc_url: str,
                                   base_output_dir: Path = Path("output")) -> Path | None:
    """
    Given a ToC URL, find the matching novel directory by checking metadata.json in each output
    subfolder.
    """
    for subdir in base_output_dir.iterdir():
        if subdir.is_dir():
            metadata_path = subdir / "metadata.json"
            if metadata_path.exists():
                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    if metadata.get("source") == toc_url:
                        return subdir
                except FileNotFoundError as e:
                    print(f"[WARN] Could not read metadata from {metadata_path}: {e}")
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--toc-url", required=True, help="The URL of the novel's ToC")
    parser.add_argument("--chapter-url", required=True, help="The URL of the chapter to scrape")
    parser.add_argument("--method", choices=["iframe", "paragraph"], default="iframe")
    args = parser.parse_args()

    asyncio.run(main(args.toc_url, args.chapter_url, args.method))
