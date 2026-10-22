"""UTM e-repository (theses.lib.utm.my) is a DSpace instance with no public API.
Acquisition strategy: Playwright headless browser fills the search form, extracts
title/authors/abstract/URL per result, returns Paper[] with source='utm'.
Tests use saved HTML fixtures by default; live scraping is @pytest.mark.live only.
On scraper failure: typed ScraperError raised, OpenAlex results still served.
"""
from app.agents.utm_scraper import (
    parse_utm_html,
    load_fixture,
    search_utm_repository,
    ScraperError,
)

__all__ = [
    "parse_utm_html",
    "load_fixture",
    "search_utm_repository",
    "ScraperError",
]
