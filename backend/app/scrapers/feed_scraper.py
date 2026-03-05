"""
RSS feed scraper for Swedish construction news.
Parses feeds, extracts structured project fields, geocodes locations.
"""
import re
import logging
from datetime import datetime
from typing import Optional

import feedparser
import httpx
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from app.scrapers.sources import (
    RSS_SOURCES, SWEDISH_REGIONS, PARTICIPANT_ROLES,
    KNOWN_COMPANIES, TYPE_KEYWORDS,
)
from app.scrapers.geocoder import geocode_location

log = logging.getLogger(__name__)

# ── Regex patterns ───────────────────────────────────────────────────────────

# Cost: "250 mkr", "1,2 miljarder", "350 MSEK", "2 Mdr", "4,5 Gsek"
_COST_RE = re.compile(
    r"(\d[\d\s]*(?:[,\.]\d+)?)\s*"
    r"(miljon(?:er)?|miljard(?:er)?|mkr|msek|mdr|mdkr|gsek|mnkr)\b",
    re.IGNORECASE,
)

# Year ranges: "2024–2028", "2025-2030", "2025 till 2029"
_YEAR_RANGE_RE = re.compile(r"\b(20\d{2})\s*[–\-–till]+\s*(20\d{2})\b", re.IGNORECASE)
_SINGLE_YEAR_RE = re.compile(r"\b(20[2-9]\d)\b")

# Location: "i Stockholm", "i Göteborg", "i Malmö", "utanför Uppsala"
_CITY_RE = re.compile(
    r"\b(?:i|vid|utanför|nära|intill)\s+([A-ZÅÄÖ][a-zåäö]+(?:\s[A-ZÅÄÖ][a-zåäö]+)?)\b"
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _clean_html(raw: str) -> str:
    if not raw:
        return ""
    return BeautifulSoup(raw, "lxml").get_text(separator=" ").strip()


def _classify_type(text: str, default: str) -> str:
    lower = text.lower()
    for project_type, keywords in TYPE_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return project_type
    return default


def _extract_cost(text: str) -> tuple[str, Optional[float]]:
    """Return human-readable cost string and numeric MSEK value."""
    match = _COST_RE.search(text)
    if not match:
        return "", None
    amount_str, unit = match.group(1), match.group(2).lower()
    amount = float(amount_str.replace(" ", "").replace(",", "."))

    # Normalise to MSEK
    if unit in ("miljard", "miljarder", "mdr", "mdkr", "gsek"):
        msek = amount * 1000
        label = f"{amount_str} miljarder kr"
    else:
        msek = amount
        label = f"{amount_str} mkr"

    return label, msek


def _extract_timeline(text: str) -> tuple[str, str]:
    rng = _YEAR_RANGE_RE.search(text)
    if rng:
        return rng.group(1), rng.group(2)
    years = _SINGLE_YEAR_RE.findall(text)
    if years:
        return years[0], years[-1] if len(years) > 1 else ""
    return "", ""


def _extract_location(text: str) -> tuple[str, str]:
    """Return (city, region) — region is the matched Swedish region."""
    # First look for explicit city mentions
    for match in _CITY_RE.finditer(text):
        city = match.group(1)
        region = _match_region(city) or _match_region(text)
        return city, region or ""

    # Fall back to region scan
    region = _match_region(text)
    return region, region


def _match_region(text: str) -> str:
    for region in SWEDISH_REGIONS:
        if region.lower() in text.lower():
            return region
    return ""


def _extract_participants(text: str) -> list[dict]:
    participants = []
    seen = set()
    lower = text.lower()

    for company in KNOWN_COMPANIES:
        if company.lower() in lower:
            # Try to find the role that follows this company name
            pattern = re.compile(
                rf"{re.escape(company)}\s+(?:är\s+|som\s+|agerar\s+)?(\w+(?:\w+)?)",
                re.IGNORECASE,
            )
            m = pattern.search(text)
            role = ""
            if m:
                word = m.group(1).lower()
                for key, label in PARTICIPANT_ROLES.items():
                    if key.startswith(word[:6]):
                        role = label
                        break
            if company not in seen:
                seen.add(company)
                participants.append({"name": company, "role": role or "Okänd roll", "contact": ""})

    return participants[:6]  # cap at 6


def _build_title(entry: feedparser.FeedParserDict, text: str) -> str:
    title = _clean_html(getattr(entry, "title", ""))
    if not title or len(title) < 5:
        title = text[:80].split(".")[0]
    return title[:200]


# ── Main scraper ─────────────────────────────────────────────────────────────

async def scrape_all_feeds() -> list[dict]:
    projects = []
    for source in RSS_SOURCES:
        try:
            # feedparser fetches with its own headers; falls back gracefully on errors
            feed = await asyncio.to_thread(
                feedparser.parse,
                source["url"],
                agent="FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)",
            )
            if feed.bozo and not feed.entries:
                raise ValueError(f"bozo: {feed.bozo_exception}")
            log.info("Scraped %s — %d entries", source["name"], len(feed.entries))
        except Exception as exc:
            log.warning("Failed to fetch %s: %s", source["name"], exc)
            continue

            for entry in feed.entries[:20]:  # max 20 per feed
                raw = _clean_html(
                    getattr(entry, "summary", "") or getattr(entry, "content", [{}])[0].get("value", "")
                )
                full_text = f"{getattr(entry, 'title', '')} {raw}"

                # Filter: skip articles unlikely to be about construction projects
                construction_kw = [
                    "bygg", "konstruktion", "projekt", "fastighet", "renovering",
                    "exploatering", "infrastruktur", "bostäder", "kontor", "fabrik",
                ]
                if not any(kw in full_text.lower() for kw in construction_kw):
                    continue

                title = _build_title(entry, full_text)
                cost_label, cost_msek = _extract_cost(full_text)
                start, end = _extract_timeline(full_text)
                location, region = _extract_location(full_text)
                participants = _extract_participants(full_text)
                project_type = _classify_type(full_text, source["default_type"])

                # Geocode
                coords = await geocode_location(location, region)
                lat = coords[0] if coords else None
                lng = coords[1] if coords else None

                # Published date
                try:
                    pub = dateparser.parse(
                        getattr(entry, "published", "") or str(datetime.utcnow())
                    )
                except Exception:
                    pub = datetime.utcnow()

                # Infer status from years
                now_year = datetime.utcnow().year
                status = "Planerat"
                if start and int(start) <= now_year:
                    status = "Pågående"
                if end and int(end) < now_year:
                    status = "Klart"

                projects.append({
                    "name": title,
                    "type": project_type,
                    "description": raw[:1000],
                    "location": location,
                    "region": region,
                    "lat": lat,
                    "lng": lng,
                    "participants": participants,
                    "estimated_cost": cost_label,
                    "cost_value_msek": cost_msek,
                    "timeline_start": start,
                    "timeline_end": end,
                    "status": status,
                    "source_url": getattr(entry, "link", ""),
                    "source_name": source["name"],
                    "published_at": pub or datetime.utcnow(),
                })

    return projects
