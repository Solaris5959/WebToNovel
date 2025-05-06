"""
Handles saving chapters and metadata for a novel in JSON format.
"""
import json
from pathlib import Path

def save_chapters(chapters, urls, output_dir: Path):
    """
    Save chapters to JSON files.
    Args:
        chapters (list): List of chapter data.
        urls (list): List of URLs for each chapter.
        output_dir (Path): Directory to save the chapter files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    for i, chapter in enumerate(chapters, start=1):
        data = {
            "number": i,
            "title": chapter["title"] or f"Chapter {i}",
            "content": chapter["content"],
            "source_url": urls[i - 1]
        }
        path = output_dir / f"{i:03}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Saved {len(chapters)} chapters to {output_dir}")

def save_metadata(title: str, source_url: str, novel_dir: Path):
    """
    Save metadata for the novel in JSON format.
    Automatically counts chapters in the /chapters directory.

    Args:
        title (str): Title of the novel.
        source_url (str): URL of the source.
        novel_dir (Path): Root directory of the novel.
    """
    chapters_dir = novel_dir / "chapters"
    chapter_count = len(list(chapters_dir.glob("*.json")))

    data = {
        "title": title,
        "source": source_url,
        "chapters": chapter_count
    }

    path = novel_dir / "metadata.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Metadata saved at {path} with {chapter_count} chapters")
