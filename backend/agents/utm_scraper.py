"""Bridge export for backend.agents.utm_scraper."""
from app.agents.utm_scraper import (
    parse_utm_html,
    load_fixture,
    search_utm_repository,
)

__all__ = [
    "parse_utm_html",
    "load_fixture",
    "search_utm_repository",
]
