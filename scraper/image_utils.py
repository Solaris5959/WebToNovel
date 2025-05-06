"""
Module to handle image related tasks, such as downloading and saving images.
"""
from pathlib import Path
import requests

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
    except Exception as e:
        print(f"[WARN] Failed to download cover image: {e}")
        return False
