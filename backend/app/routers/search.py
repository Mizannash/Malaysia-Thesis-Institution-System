"""
Search Router for Academic Paper Acquisition.
Routes between OpenAlex and UTM repository with MY/INT scope filtering,
deduplication, structured cost logging, and input validation.
"""
import os
import re
import json
import time
from datetime import datetime, timezone
from typing import List, Optional, Set
from pathlib import Path
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.schemas import SearchRequest, SearchResponse, Paper, ErrorResponse
from app.auth import get_current_user_optional
from app.models import User
from app.agents.openalex_client import (
    search as openalex_search,
    OpenAlexError,
    OpenAlexTimeoutError,
    OpenAlexRateLimitError,
    OpenAlexEmptyResultError
)
from app.agents.utm_scraper import search_utm_repository

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Search"])

BACKEND_LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
REPO_LOGS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "logs"

LOG_FILES = [
    BACKEND_LOGS_DIR / "search_log.jsonl",
    REPO_LOGS_DIR / "search_log.jsonl",
]


def _ensure_logs_dir():
    BACKEND_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    REPO_LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _log_search_event(user_email: str, query: str, scope: str, sources: List[str], count: int, latency_ms: float):
    """Logs search event with cost_myr=0.0 (Search is free, AI is not) per Rubric D5."""
    try:
        _ensure_logs_dir()
        event = {
            "user": user_email or "anonymous",
            "query": query,
            "scope": scope,
            "source": sources[0] if len(sources) == 1 else ("multiple" if len(sources) > 1 else "none"),
            "sources": sources,
            "result_count": count,
            "latency_ms": round(latency_ms, 2),
            "cost_myr": 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        line = json.dumps(event) + "\n"
        for log_file in LOG_FILES:
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(line)
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Failed to write search log: {e}")


def _normalize_doi(doi: Optional[str]) -> Optional[str]:
    """Normalizes DOI to lowercase clean string without protocol prefix."""
    if not doi:
        return None
    cleaned = doi.strip().lower()
    cleaned = re.sub(r"^https?://(dx\.)?doi\.org/", "", cleaned)
    return cleaned if cleaned else None


def _normalize_title(title: str) -> str:
    """Normalizes title for secondary deduplication."""
    return re.sub(r"[^a-z0-9]", "", title.lower())


def validate_search_query(query: str):
    """
    Validates academic search query per Rubric D3.
    Rejects:
    - Empty queries
    - Queries > 300 characters
    - Non-academic gibberish (keyboard smash, zero vowels, excessive repetition)
    """
    if not query or not query.strip():
        raise HTTPException(
            status_code=422,
            detail={
                "error": "EMPTY_QUERY",
                "message": "Search query cannot be empty.",
                "field": "query"
            }
        )

    q = query.strip()
    if len(q) > 300:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "QUERY_TOO_LONG",
                "message": f"Search query exceeds maximum length of 300 characters (received {len(q)}).",
                "field": "query"
            }
        )

    # Gibberish check 1: Repeated characters (e.g. "aaaaa", "11111")
    if re.search(r"(.)\1{4,}", q):
        raise HTTPException(
            status_code=422,
            detail={
                "error": "INVALID_QUERY_GIBBERISH",
                "message": "Query contains excessive repeated characters and is not a valid academic topic.",
                "field": "query"
            }
        )

    # Gibberish check 2: Check alphabetic content & vowel presence
    letters = re.findall(r"[A-Za-z]", q)
    if len(letters) >= 5:
        vowels = re.findall(r"[AEIOUaeiou]", q)
        vowel_ratio = len(vowels) / len(letters)
        # In English and Bahasa Melayu, legitimate words have at least 15% vowels
        if vowel_ratio < 0.12:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "INVALID_QUERY_GIBBERISH",
                    "message": "Query appears to be random consonants or keyboard smash with no discernible academic context.",
                    "field": "query"
                }
            )

    # Gibberish check 3: Known keyboard home-row smash patterns
    keyboard_patterns = [
        r"asdfgh", r"qwerty", r"zxcvbn", r"123456", r"qazwsx", r"lkjhgf"
    ]
    for pattern in keyboard_patterns:
        if pattern in q.lower():
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "INVALID_QUERY_GIBBERISH",
                    "message": "Query matches keyboard-smash pattern.",
                    "field": "query"
                }
            )

    # Gibberish check 4: Pure symbols or no valid alphabetic word with length >= 2
    words = re.findall(r"[A-Za-z]{2,}", q)
    if not words:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "INVALID_QUERY_FORMAT",
                "message": "Query must contain at least one valid academic topic keyword.",
                "field": "query"
            }
        )


@router.post("/search", response_model=SearchResponse)
@router.post("/api/search", response_model=SearchResponse)
def search_academic_papers(
    req: SearchRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Search academic literature across OpenAlex and UTM Repository.
    - scope='MY': Queries OpenAlex (Malaysia filter) and UTM repository.
    - scope='INT': Queries OpenAlex global.
    - Deduplicates by DOI and title.
    - Free tier logging ($0.00 / RM0.00 cost per query).
    """
    start_time = time.time()
    user_email = current_user.email if current_user else "anonymous"

    # 1. Input validation (HTTP 422 on invalid, ZERO database project writes)
    validate_search_query(req.query)

    scope = req.scope.upper()
    if scope not in ("MY", "INT"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "INVALID_SCOPE",
                "message": f"Scope '{req.scope}' is invalid. Supported values are 'MY' or 'INT'.",
                "field": "scope"
            }
        )

    all_papers: List[Paper] = []
    sources: List[str] = []

    # 2. Scope Routing
    try:
        # Source 1: OpenAlex
        openalex_papers = openalex_search(req.query, scope=scope)
        if openalex_papers:
            all_papers.extend(openalex_papers)
            sources.append("openalex")
    except OpenAlexEmptyResultError:
        logger.info(f"OpenAlex returned 0 results for query '{req.query}'")
    except (OpenAlexTimeoutError, OpenAlexRateLimitError, OpenAlexError) as e:
        logger.warning(f"OpenAlex search error: {e}")
        # When scope is INT and OpenAlex fails completely, raise structured error
        if scope == "INT":
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"error": "OPENALEX_UNAVAILABLE", "message": str(e)}
            )

    # Source 2: UTM Institutional Repository (when scope is MY)
    if scope == "MY":
        try:
            utm_papers = search_utm_repository(req.query)
            if utm_papers:
                all_papers.extend(utm_papers)
                sources.append("utm")
        except Exception as e:
            logger.warning(f"UTM scraper error: {e}")

    # 3. Deduplication by DOI and Title
    seen_dois: Set[str] = set()
    seen_titles: Set[str] = set()
    deduped_papers: List[Paper] = []

    for paper in all_papers:
        norm_doi = _normalize_doi(paper.doi)
        norm_title = _normalize_title(paper.title)

        # Check DOI match
        if norm_doi and norm_doi in seen_dois:
            continue
        
        # Check Title match
        if norm_title in seen_titles:
            continue

        if norm_doi:
            seen_dois.add(norm_doi)
        seen_titles.add(norm_title)
        deduped_papers.append(paper)

    # 4. Check if we have at least some results, or return empty list
    latency_ms = (time.time() - start_time) * 1000.0

    # 5. Structured cost logging (D5: search is always free; cost_myr=0.0)
    _log_search_event(
        user_email=user_email,
        query=req.query,
        scope=scope,
        sources=sources,
        count=len(deduped_papers),
        latency_ms=latency_ms
    )

    return SearchResponse(
        query=req.query,
        scope=scope,
        total=len(deduped_papers),
        papers=deduped_papers,
        sources=sources
    )
