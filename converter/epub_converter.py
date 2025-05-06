"""
This module contains the function to convert a structured novel directory into an EPUB file.
"""
import json
from pathlib import Path
from ebooklib import epub
from scraper.utils import slugify

def generate_epub(novel_dir: Path) -> Path:
    metadata_path = novel_dir / "metadata.json"
    chapters_dir = novel_dir / "chapters"
    cover_path = next(novel_dir.glob("cover.*"), None)

    # Load metadata
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    title = metadata["title"]
    safe_title = slugify(title)
    output_path = novel_dir / f"{safe_title}.epub"

    book = epub.EpubBook()
    book.set_identifier(metadata.get("source", "unknown"))
    book.set_title(title)
    book.set_language("en")
    book.add_author(metadata.get("author", "Unknown"))

    # Add cover image
    if cover_path:
        with open(cover_path, "rb") as img_file:
            book.set_cover(cover_path.name, img_file.read())

    spine = ['nav']
    toc = []

    chapter_files = sorted(
        chapters_dir.glob("*.json"),
        key=lambda f: int(f.stem)
    )

    for file in chapter_files:
        with open(file, "r", encoding="utf-8") as f:
            chapter = json.load(f)

        chap = epub.EpubHtml(
            title=chapter["title"],
            file_name=f"{file.stem}.xhtml",
            lang="en"
        )
        chap.content = f"<h1>{chapter['title']}</h1>\n{chapter['content']}"
        book.add_item(chap)
        toc.append(chap)
        spine.append(chap)

    book.toc = tuple(toc)
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(str(output_path), book)
    print(f"[INFO] EPUB written to: {output_path}")
    return output_path
