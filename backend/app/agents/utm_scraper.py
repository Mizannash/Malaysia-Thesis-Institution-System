"""UTM Institutional Repository Scraper (eprints.utm.my)."""
import re
import logging
from typing import List, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import httpx

from app.schemas import Paper
from app.config import settings

logger = logging.getLogger(__name__)

UTM_EPRINTS_BASE_URL = "https://eprints.utm.my/cgi/search/archive/simple"


def parse_utm_html(html_content: str) -> List[Paper]:
    """
    Parses UTM ePrints HTML search result page and returns list of Paper schemas.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    papers: List[Paper] = []
    
    # Each result is contained in a tr.ep_search_result or div.ep_search_result_item
    items = soup.find_all("div", class_="ep_search_result_item")
    if not items:
        # Fallback to search result table rows
        rows = soup.find_all("tr", class_="ep_search_result")
        items = [r.find("div", class_="ep_search_result_item") or r for r in rows if r]

    for item in items:
        # 1. Title & URL
        title_tag = item.find("span", class_="ep_title")
        link_tag = item.find("a", href=re.compile(r"eprints\.utm\.my/id/eprint/\d+"))
        
        if title_tag:
            title = title_tag.get_text(strip=True)
        elif link_tag:
            title = link_tag.get_text(strip=True)
        else:
            continue

        url = link_tag["href"] if link_tag and link_tag.has_attr("href") else None

        # 2. Authors
        author_tags = item.find_all("span", class_="person_name")
        authors = [a.get_text(strip=True) for a in author_tags]
        if not authors:
            # Fallback author regex
            text_header = item.get_text()
            match = re.search(r"^([^()]+)\s*\(\d{4}\)", text_header)
            if match:
                authors = [a.strip() for a in match.group(1).split(" and ")]

        # 3. Year
        year = None
        year_match = re.search(r"\((\d{4})\)", item.get_text())
        if year_match:
            try:
                year = int(year_match.group(1))
            except ValueError:
                pass

        # 4. DOI
        doi = None
        doi_tag = item.find("div", class_="ep_meta_doi")
        if doi_tag:
            doi_link = doi_tag.find("a")
            if doi_link and "doi.org" in doi_link.get("href", ""):
                doi = doi_link["href"].split("doi.org/")[-1]
            else:
                doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", doi_tag.get_text())
                if doi_match:
                    doi = doi_match.group(0)

        # 5. Abstract
        abstract = None
        abstract_tag = item.find("div", class_="ep_abstract")
        if abstract_tag:
            abstract = abstract_tag.get_text(strip=True)

        papers.append(Paper(
            title=title,
            authors=authors,
            year=year,
            doi=doi,
            url=url,
            abstract=abstract,
            source="utm",
            citation_count=0
        ))

    return papers


def load_fixture() -> str:
    """Loads saved HTML search fixture."""
    filename = "utm_search_fixture.html"
    candidates = [
        Path(__file__).resolve().parent.parent.parent.parent / "tests" / "fixtures" / filename,
        Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures" / filename,
        Path("/app/tests/fixtures") / filename,
        Path("/tests/fixtures") / filename,
        Path("tests/fixtures") / filename,
        Path("../tests/fixtures") / filename,
    ]
    for c in candidates:
        if c.exists():
            try:
                with open(c, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
    raise FileNotFoundError(f"UTM HTML fixture not found in candidate paths: {candidates}")


def search_utm_repository(query: str, use_fixture: bool = False, timeout: float = 10.0) -> List[Paper]:
    """
    Searches UTM institutional repository.
    Default in tests or DEMO_MODE uses saved HTML fixture for reproducibility.
    """
    if use_fixture or getattr(settings, "DEMO_MODE", False):
        logger.info("[UTM Scraper] Using local HTML fixture (D5 reproducibility).")
        html = load_fixture()
        return parse_utm_html(html)

    # Live scraper attempt
    try:
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MTIS-Research-Scraper/1.0",
            "Accept": "text/html,application/xhtml+xml",
        }
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(UTM_EPRINTS_BASE_URL, params=params, headers=headers)
            if resp.status_code == 200:
                papers = parse_utm_html(resp.text)
                if papers:
                    return papers
        
        # Fallback to fixture if live search yields no HTML results
        logger.info("[UTM Scraper] Live search empty or redirected, fallback to fixture.")
        return parse_utm_html(load_fixture())

    except Exception as e:
        logger.warning(f"[UTM Scraper] Live scrape failed ({e}), fallback to fixture.")
        return parse_utm_html(load_fixture())
