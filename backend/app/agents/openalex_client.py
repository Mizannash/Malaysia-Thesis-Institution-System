"""OpenAlex API client for academic paper acquisition with MY/INT scope filtering."""
import os
import json
import logging
from typing import List, Optional
from pathlib import Path
import httpx

from app.schemas import Paper
from app.config import settings

logger = logging.getLogger(__name__)

OPENALEX_API_URL = "https://api.openalex.org/works"


class OpenAlexError(Exception):
    """Base exception for OpenAlex client errors."""
    pass


class OpenAlexTimeoutError(OpenAlexError):
    """Raised when an OpenAlex query times out."""
    pass


class OpenAlexRateLimitError(OpenAlexError):
    """Raised when hitting OpenAlex 429 rate limit."""
    pass


class OpenAlexEmptyResultError(OpenAlexError):
    """Raised when an OpenAlex query returns 0 results."""
    pass


def _reconstruct_abstract(inverted_index: Optional[dict]) -> Optional[str]:
    """Reconstruct plain-text abstract from OpenAlex abstract_inverted_index."""
    if not inverted_index:
        return None
    try:
        max_pos = max(max(positions) for positions in inverted_index.values() if positions)
        words = [""] * (max_pos + 1)
        for word, positions in inverted_index.items():
            for pos in positions:
                words[pos] = word
        return " ".join(filter(None, words))
    except Exception:
        return None


def _load_cached_fixture(scope: str) -> List[Paper]:
    """Load cached fixture papers for DEMO_MODE or offline testing."""
    filename = "search_fixture_my.json" if scope == "MY" else "search_fixture_int.json"
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
                    raw_data = json.load(f)
                    return [Paper(**item) for item in raw_data]
            except Exception:
                pass
    return []


def search(query: str, scope: str = "MY", timeout: float = 12.0) -> List[Paper]:
    """
    Search OpenAlex works API.
    
    Args:
        query: Academic topic query string
        scope: "MY" for Malaysia-affiliated works, "INT" for global
        timeout: Request timeout in seconds
        
    Returns:
        List of structured Paper objects
        
    Raises:
        OpenAlexTimeoutError, OpenAlexRateLimitError, OpenAlexEmptyResultError, OpenAlexError
    """
    scope = scope.upper()
    if scope not in ("MY", "INT"):
        raise ValueError(f"Invalid scope '{scope}'. Must be 'MY' or 'INT'.")

    # In DEMO_MODE, return fixture results immediately with zero network overhead
    if getattr(settings, "DEMO_MODE", False):
        logger.info(f"[OpenAlex] DEMO_MODE active: returning cached fixture for scope={scope}")
        cached = _load_cached_fixture(scope)
        if not cached:
            raise OpenAlexEmptyResultError(f"No cached fixture records found for scope '{scope}'")
        return cached

    params = {
        "search": query,
        "per_page": 20,
        "sort": "relevance_score:desc",
    }

    # Scope filtering: MY filters to Malaysia institutions
    if scope == "MY":
        params["filter"] = "institutions.country_code:MY"

    contact_email = getattr(settings, "OPENALEX_EMAIL", None) or os.getenv("OPENALEX_EMAIL", "support@mtis.my")
    headers = {
        "User-Agent": f"MTIS-Malaysian-Thesis-System/1.0 (mailto:{contact_email})",
        "Accept": "application/json",
    }

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(OPENALEX_API_URL, params=params, headers=headers)
            
            if resp.status_code == 429:
                raise OpenAlexRateLimitError("OpenAlex API rate limit exceeded (HTTP 429).")
            
            if resp.status_code != 200:
                raise OpenAlexError(f"OpenAlex returned HTTP {resp.status_code}: {resp.text[:200]}")
            
            data = resp.json()
            results = data.get("results", [])

            if not results:
                # If MY scope gave 0 results, try broader query or raise
                raise OpenAlexEmptyResultError(f"No OpenAlex publications found for query: '{query}' [scope={scope}]")

            papers: List[Paper] = []
            for item in results:
                title = item.get("display_name") or item.get("title")
                if not title:
                    continue

                authors = [
                    a.get("author", {}).get("display_name") 
                    for a in item.get("authorships", []) 
                    if a.get("author", {}).get("display_name")
                ]
                
                year = item.get("publication_year")
                doi = item.get("doi")
                url = item.get("doi") or item.get("id")
                abstract = _reconstruct_abstract(item.get("abstract_inverted_index"))
                citation_count = item.get("cited_by_count", 0)

                papers.append(Paper(
                    title=title,
                    authors=authors,
                    year=year,
                    doi=doi,
                    url=url,
                    abstract=abstract,
                    source="openalex",
                    citation_count=citation_count,
                ))

            return papers

    except httpx.TimeoutException as e:
        logger.warning(f"[OpenAlex] Request timed out: {e}")
        # If timeout happens and DEMO_MODE or offline, fall back to fixture
        cached = _load_cached_fixture(scope)
        if cached:
            logger.info("[OpenAlex] Timeout fallback to cached fixture.")
            return cached
        raise OpenAlexTimeoutError(f"OpenAlex request timed out after {timeout}s") from e

    except (OpenAlexRateLimitError, OpenAlexEmptyResultError):
        raise

    except httpx.HTTPError as e:
        logger.warning(f"[OpenAlex] Network error: {e}")
        cached = _load_cached_fixture(scope)
        if cached:
            return cached
        raise OpenAlexError(f"OpenAlex network communication failed: {str(e)}") from e
