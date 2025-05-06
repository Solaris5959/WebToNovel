"""
Handles the scraping pipeline for a given URL.
This includes scraping chapters, saving them, and generating an EPUB file.
"""
from pathlib import Path
from saver import save_chapters, save_metadata
from scraper.orchestrator import scrape_all_chapters
from scraper.utils import slugify, download_image
from converter import generate_epub

async def run_scrape_pipeline(url: str, output_base: Path):
    """
    Kicks off the scraping process for a given URL.
    Args:
        url (str): The URL of the first chapter of the novel.
        output_base (Path): The base directory where the output will be saved.
    """
    result = await scrape_all_chapters(url, method="paragraph", output_base_dir=output_base)
    title = result["title"]
    folder_name = slugify(title)
    novel_dir = output_base / folder_name

    # Save cover image if available
    if (cover := result.get("cover_image_url")):
        ext = Path(cover).suffix or ".jpg"
        cover_path = novel_dir / f"cover{ext}"
        download_image(cover, cover_path)

    # Save chapter files
    chapter_dir = novel_dir / "chapters"
    save_chapters(result["scraped_chapters"], result["scraped_urls"], chapter_dir)

    # Save metadata
    save_metadata(title, url, len(result["scraped_chapters"]), novel_dir)

    # Generate EPUB
    generate_epub(novel_dir)

    return novel_dir
