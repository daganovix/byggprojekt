"""
HTML scrapers for construction/real estate company project listing pages.

Targets server-rendered CMS pages (EPiServer/Optimizely/WordPress).
Uses a two-pass approach: listing page -> detail page per project.

Companies:
- Riksbyggen   (cooperative housing, EPiServer)
- HSB          (cooperative housing, Optimizely)
- Peab Bostad  (private developer, WordPress)
- Veidekke     (construction + housing)
- Serneke      (construction + housing)
- JM           (private developer)
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.scrapers.geocoder import geocode_location
from app.scrapers.sources import SWEDISH_REGIONS

log = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "sv-SE,sv;q=0.9,en;q=0.8",
}

COMPANY_TARGETS = [
    {
        "name": "Riksbyggen – Nyproduktion",
        "url": "https://www.riksbyggen.se/nyproduktion/",
        "base_url": "https://www.riksbyggen.se",
        "default_type": "Bostäder",
        "parser": "generic",
    },
    {
        "name": "HSB – Nyproduktion",
        "url": "https://www.hsb.se/nyproduktion/",
        "base_url": "https://www.hsb.se",
        "default_type": "Bostäder",
        "parser": "generic",
    },
    {
        "name": "JM – Nya hem",
        "url": "https://www.jm.se/nya-hem/",
        "base_url": "https://www.jm.se",
        "default_type": "Bostäder",
        "parser": "generic",
    },
    {
        "name": "Serneke – Projekt",
        "url": "https://www.serneke.se/projekt/",
        "base_url": "https://www.serneke.se",
        "default_type": "Övrigt",
        "parser": "generic",
    },
    {
        "name": "Veidekke – Bostäder",
        "url": "https://www.veidekke.se/bostad/",
        "base_url": "https://www.veidekke.se",
        "default_type": "Bostäder",
        "parser": "generic",
    },
    {
        "name": "Skanska Bostad",
        "url": "https://www.skanska.se/vad-vi-bygger/bostader/",
        "base_url": "https://www.skanska.se",
        "default_type": "Bostäder",
        "parser": "generic",
    },
    {
        "name": "Peab Bostad",
        "url": "https://www.peab.se/bostad/",
        "base_url": "https://www.peab.se",
        "default_type": "Bostäder",
        "parser": "generic",
    },
    {
        "name": "Bonava",
        "url": "https://www.bonava.se/nyproduktion/",
        "base_url": "https://www.bonava.se",
        "default_type": "Bostäder",
        "parser": "generic",
    },
]


# ── Location helpers ──────────────────────────────────────────────────────────

def _find_region(text: str) -> str:
    for region in SWEDISH_REGIONS:
        if region.lower() in text.lower():
            return region
    return ""


# ── Card extraction ───────────────────────────────────────────────────────────

# CSS selectors tried in order to find project cards
_CARD_SELECTORS = [
    "article.project", "article.project-card",
    "li.project", "li.project-card", "li.project-item",
    "div.project-card", "div.project-item", "div.project-listing__item",
    "[class*='project-card']", "[class*='project-item']",
    "[class*='ProjectCard']", "[class*='ProjectItem']",
    "article",  # broad fallback
]

_TITLE_SELECTORS = ["h1", "h2", "h3", "h4", ".title", "[class*='title']", "[class*='heading']"]
_LOC_SELECTORS = [
    ".location", ".city", ".ort", ".adress", ".address",
    "[class*='location']", "[class*='city']", "[class*='ort']",
]
_DESC_SELECTORS = [
    ".description", ".preamble", ".ingress", ".intro", ".excerpt",
    "[class*='description']", "[class*='preamble']", "p",
]


def _first_text(soup_el, selectors: list[str]) -> str:
    for sel in selectors:
        el = soup_el.select_one(sel)
        if el:
            t = el.get_text(separator=" ", strip=True)
            if t:
                return t
    return ""


def _extract_cards(soup: BeautifulSoup, target: dict) -> list[tuple[str, dict]]:
    """
    Find project cards on a listing page.
    Returns list of (detail_url, partial_project_dict).
    """
    cards = []
    for sel in _CARD_SELECTORS:
        found = soup.select(sel)
        if len(found) >= 2:
            cards = found
            break

    # If no structured cards, look for any <a> tags pointing to project pages
    if not cards:
        cards = [
            a.parent for a in soup.find_all("a", href=True)
            if any(k in (a.get("href") or "") for k in ["/projekt/", "/nyproduktion/", "/bostad/", "/hem/"])
        ][:30]

    items: list[tuple[str, dict]] = []
    seen_urls: set[str] = set()

    for card in cards[:40]:
        link = card.find("a", href=True)
        if not link:
            continue
        href: str = link["href"]
        if href.startswith("/"):
            href = target["base_url"] + href
        if not href.startswith("http"):
            continue
        if href in seen_urls or href == target["url"]:
            continue
        seen_urls.add(href)

        title = _first_text(card, _TITLE_SELECTORS) or link.get_text(strip=True)
        if not title or len(title) < 3:
            continue

        location_text = _first_text(card, _LOC_SELECTORS)
        desc = _first_text(card, _DESC_SELECTORS)
        region = _find_region(f"{title} {location_text} {desc}")

        items.append((href, {
            "name": title[:200],
            "type": target["default_type"],
            "description": desc[:500],
            "location": location_text[:100] or region,
            "region": region,
            "source_name": target["name"],
            "default_type": target["default_type"],
        }))

    return items


# ── Detail page enrichment ────────────────────────────────────────────────────

async def _enrich_from_detail(
    client: httpx.AsyncClient,
    url: str,
    partial: dict,
) -> Optional[dict]:
    """Fetch detail page, improve description/location, infer status."""
    try:
        await asyncio.sleep(1.0)
        resp = await client.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Better description
        desc = _first_text(soup, _DESC_SELECTORS[:5])
        if desc and len(desc) > len(partial.get("description", "")):
            partial["description"] = desc[:1000]

        # Better location
        loc = _first_text(soup, _LOC_SELECTORS)
        if loc:
            region = _find_region(loc)
            if region:
                partial["location"] = loc[:100]
                partial["region"] = region

        # Status inference
        full_text = soup.get_text(separator=" ").lower()
        if any(w in full_text for w in ("inflyttning klar", "klart", "färdigställt", "infl. klar")):
            status = "Klart"
        elif any(w in full_text for w in ("planeras", "kommande", "tidigt skede", "projekteras")):
            status = "Planerat"
        else:
            status = "Pågående"

        # Timeline
        import re
        years = re.findall(r"\b(20[2-9]\d)\b", full_text)
        start = years[0] if years else ""
        end = years[-1] if len(years) > 1 else ""

        partial.update({
            "status": status,
            "timeline_start": start,
            "timeline_end": end,
            "source_url": url,
            "lat": None,
            "lng": None,
            "participants": [],
            "estimated_cost": "",
            "cost_value_msek": None,
            "published_at": datetime.utcnow(),
        })
        return partial

    except Exception as exc:
        log.debug("Detail fetch failed for %s: %s", url, exc)
        # Return partial with defaults even if detail fetch fails
        partial.update({
            "status": "Pågående",
            "timeline_start": "",
            "timeline_end": "",
            "source_url": url,
            "lat": None,
            "lng": None,
            "participants": [],
            "estimated_cost": "",
            "cost_value_msek": None,
            "published_at": datetime.utcnow(),
        })
        return partial


# ── Main entry point ──────────────────────────────────────────────────────────

async def _scrape_one_company(client: httpx.AsyncClient, target: dict) -> list[dict]:
    try:
        resp = await client.get(target["url"])
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        items = _extract_cards(soup, target)
        log.info("Company listing %s — %d cards found", target["name"], len(items))

        projects: list[dict] = []
        for detail_url, partial in items:
            project = await _enrich_from_detail(client, detail_url, partial)
            if not project:
                continue
            loc = project.get("location") or project.get("region") or ""
            if loc:
                coords = await geocode_location(loc, project.get("region", ""))
                if coords:
                    project["lat"], project["lng"] = coords
            projects.append(project)
        return projects
    except Exception as exc:
        log.warning("Company scrape failed for %s: %s", target["name"], exc)
        return []


async def scrape_company_pages() -> list[dict]:
    async with httpx.AsyncClient(
        headers=_HEADERS, timeout=20, follow_redirects=True,
    ) as client:
        results = await asyncio.gather(
            *[_scrape_one_company(client, t) for t in COMPANY_TARGETS],
            return_exceptions=True,
        )
    all_projects: list[dict] = []
    for r in results:
        if isinstance(r, list):
            all_projects.extend(r)
    log.info("Company scraper total — %d projects", len(all_projects))
    return all_projects
