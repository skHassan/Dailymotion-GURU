import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re

BASE_URL = "https://developers.dailymotion.com"
START_PAGE = "/docs/welcome"

OUTPUT_DIR = Path("data/docs_raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

visited = set()

def clean_text(text: str) -> str:
    """
    Clean documentation text while preserving readability.
    """
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)

    # Remove common UI noise
    noise_patterns = [
        r'Updated\s+\d+.*?ago',
        r'Ask AI',
        r'Welcome$',
    ]

    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text.strip()

def extract_content(soup: BeautifulSoup):
    """
    Extract the main documentation content only.
    """
    content = soup.find("article")

    if not content:
        content = soup.find("main")

    if not content:
        return None

    # Remove navigation and layout elements
    for tag in content.find_all([
        "nav",
        "aside",
        "footer",
        "header",
        "form",
        "button"
    ]):
        tag.decompose()

    # Remove table of contents blocks (common in docs)
    for div in content.find_all("div"):
        class_name = " ".join(div.get("class", []))
        if "toc" in class_name.lower():
            div.decompose()

    return content

def fetch_page(path: str):
    url = BASE_URL + path
    if url in visited:
        return
    visited.add(url)

    print(f"Fetching {url}")
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "lxml")

    content = extract_content(soup)
    if not content:
        return

    raw_text = content.get_text("\n")
    text = clean_text(raw_text)

    title = soup.title.string.strip() if soup.title else "untitled"

    file_name = path.replace("/", "_").strip("_") + ".txt"
    file_path = OUTPUT_DIR / file_name

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"TITLE: {title}\n")
        f.write(f"URL: {url}\n\n")
        f.write(text)

    # Crawl internal documentation links only
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/docs/"):
            fetch_page(href)

if __name__ == "__main__":
    fetch_page(START_PAGE)
    print("Ingestion complete.")
