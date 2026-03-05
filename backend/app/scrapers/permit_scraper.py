"""
Municipality building permit scraper.

Fetches building permit decisions (bygglov) from Swedish municipality websites
and from Post- och Inrikes Tidningar (PIN / Bolagsverket official gazette).

Each municipality target specifies:
  url     – the permit listing page
  name    – display name for source_name field
  parser  – which parser function to use
"""
import asyncio
import logging
import re
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.scrapers.sources import SWEDISH_REGIONS, TYPE_KEYWORDS
from app.scrapers.geocoder import geocode_location

log = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ByggprojektBot/1.0; +https://byggprojekt.se)"
    )
}

# ── Municipality target list ──────────────────────────────────────────────────

MUNICIPALITY_TARGETS = [
    # Stockholm – actual weekly permit decision notice list
    {
        "name": "Stockholms stad – Kungörelser",
        "url": "https://www.stockholm.se/OmStockholm/Stadsbyggnadskontoret/Kungorelser/",
        "parser": "parse_stockholm",
        "default_type": "Offentligt",
        "region": "Stockholm",
    },
    # Göteborg – stadsbyggnad news (includes permit decisions)
    {
        "name": "Göteborgs stad – Stadsbyggnad",
        "url": "https://www.goteborg.se/nyheter/stadsbyggnad/",
        "parser": "parse_decision_list",
        "default_type": "Offentligt",
        "region": "Västra Götaland",
    },
    # Malmö – planning and building permit section
    {
        "name": "Malmö stad – Stadsbyggnad",
        "url": "https://malmo.se/Stadsbyggnad.html",
        "parser": "parse_decision_list",
        "default_type": "Offentligt",
        "region": "Skåne",
    },
    # Uppsala – nybyggnad and permit page
    {
        "name": "Uppsala kommun – Bygg och plan",
        "url": "https://www.uppsala.se/nyheter/?category=bygg",
        "parser": "parse_decision_list",
        "default_type": "Offentligt",
        "region": "Uppsala",
    },
    # Linköping – building permit news
    {
        "name": "Linköpings kommun – Bygglov",
        "url": "https://www.linkoping.se/bo-bygga-miljo/bygglov/",
        "parser": "parse_decision_list",
        "default_type": "Offentligt",
        "region": "Östergötland",
    },
    # Västerås – building permits
    {
        "name": "Västerås stad – Bygglov",
        "url": "https://www.vasteras.se/bygga-bo-miljo/bygglov-och-anmalan.html",
        "parser": "parse_decision_list",
        "default_type": "Offentligt",
        "region": "Västmanland",
    },
    # Post- och Inrikes Tidningar – official gazette, plan/building category
    {
        "name": "Post- och Inrikes Tidningar – Plan & Bygg",
        "url": "https://poit.bolagsverket.se/poit/PublikPublicering.do?kategoriId=44",
        "parser": "parse_poit",
        "default_type": "Offentligt",
        "region": "",
    },
    {
        "name": "Post- och Inrikes Tidningar – Tillstånd",
        "url": "https://poit.bolagsverket.se/poit/PublikPublicering.do?kategoriId=45",
        "parser": "parse_poit",
        "default_type": "Offentligt",
        "region": "",
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────

_YEAR_RE = re.compile(r"\b(20[2-9]\d)\b")
_COST_RE = re.compile(
    r"(\d[\d\s]*(?:[,\.]\d+)?)\s*(miljon(?:er)?|miljard(?:er)?|mkr|msek|mdr|mnkr)\b",
    re.IGNORECASE,
)


def _infer_type(text: str, default: str) -> str:
    lower = text.lower()
    for project_type, keywords in TYPE_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return project_type
    return default


def _match_region(text: str) -> str:
    for region in SWEDISH_REGIONS:
        if region.lower() in text.lower():
            return region
    return ""


def _extract_cost(text: str):
    m = _COST_RE.search(text)
    if not m:
        return "", None
    amount = float(m.group(1).replace(" ", "").replace(",", "."))
    unit = m.group(2).lower()
    if unit in ("miljard", "miljarder", "mdr"):
        return f"{m.group(1)} miljarder kr", amount * 1000
    return f"{m.group(1)} mkr", amount


def _extract_years(text: str):
    years = _YEAR_RE.findall(text)
    if not years:
        return "", ""
    return years[0], years[-1] if len(years) > 1 else ""


def _infer_status(start: str, end: str) -> str:
    now = datetime.utcnow().year
    if end and int(end) < now:
        return "Klart"
    if start and int(start) <= now:
        return "Pågående"
    return "Planerat"


def _make_project(title, description, location, region, source_url, source_name,
                  default_type, pub=None, lat=None, lng=None) -> dict:
    full = f"{title} {description}"
    cost_label, cost_msek = _extract_cost(full)
    start, end = _extract_years(full)
    project_type = _infer_type(full, default_type)
    status = _infer_status(start, end)
    return {
        "name": title[:200],
        "type": project_type,
        "description": description[:1000],
        "location": location,
        "region": region,
        "lat": lat,
        "lng": lng,
        "participants": [],
        "estimated_cost": cost_label,
        "cost_value_msek": cost_msek,
        "timeline_start": start,
        "timeline_end": end,
        "status": status,
        "source_url": source_url,
        "source_name": source_name,
        "published_at": pub or datetime.utcnow(),
    }


# ── Parsers ───────────────────────────────────────────────────────────────────

def parse_stockholm(soup: BeautifulSoup, target: dict) -> list[dict]:
    """Parse Stockholm stadsbyggnadskontoret kungörelser page."""
    projects = []
    # Try multiple selectors — the page structure varies across deployments
    selectors = [
        "article", ".listing__item", "li.item",
        ".teaser", ".news-item", ".article-teaser",
        "li[class*='item']", "div[class*='teaser']",
    ]
    items = []
    for sel in selectors:
        items = soup.select(sel)
        if len(items) >= 2:
            break

    # Fall back: any <a> inside an <li> or <article>
    if not items:
        items = soup.find_all(["article", "li"], limit=50)

    for item in items:
        heading = item.find(["h2", "h3", "h4", "a"])
        if not heading:
            continue
        title = heading.get_text(strip=True)
        if not title or len(title) < 8:
            continue
        link_tag = item.find("a", href=True)
        url = (link_tag["href"] if link_tag else target["url"])
        if url.startswith("/"):
            url = "https://www.stockholm.se" + url
        desc_tag = item.find(["p", "div"])
        description = desc_tag.get_text(strip=True) if desc_tag else title
        projects.append(_make_project(
            title=title,
            description=description,
            location="Stockholm",
            region="Stockholm",
            source_url=url,
            source_name=target["name"],
            default_type=target["default_type"],
        ))
    return projects[:20]


def parse_decision_list(soup: BeautifulSoup, target: dict) -> list[dict]:
    """
    Generic parser for municipality news/decision pages.
    Picks up article teasers, news cards, and table rows that describe
    planning or building-related decisions.
    """
    projects = []
    region = target.get("region", "")
    base = "/".join(target["url"].split("/")[:3])  # https://www.example.se

    # Collect candidate elements: articles, news teasers, table rows
    candidates = []
    for sel in ("article", ".news-item", ".teaser", ".article-teaser",
                "[class*='news']", "[class*='article']", "tr"):
        found = soup.select(sel)
        if found:
            candidates.extend(found)
        if len(candidates) >= 5:
            break

    # If nothing structure-like found, fall through to paragraph-level scan
    if not candidates:
        candidates = soup.find_all(["h2", "h3", "h4"], limit=40)

    seen: set[str] = set()
    for el in candidates[:40]:
        heading = el.find(["h1", "h2", "h3", "h4", "th", "strong"]) or (
            el if el.name in ("h2", "h3", "h4") else None
        )
        if not heading:
            continue
        title = heading.get_text(strip=True)
        if not title or len(title) < 8 or title in seen:
            continue
        seen.add(title)

        link_tag = el.find("a", href=True) or heading.find("a", href=True)
        source_url = target["url"]
        if link_tag:
            href = link_tag["href"]
            source_url = href if href.startswith("http") else base + href

        desc_el = el.find(["p", "td", "div"])
        description = desc_el.get_text(strip=True) if desc_el else title

        projects.append(_make_project(
            title=title,
            description=description,
            location=region,
            region=region,
            source_url=source_url,
            source_name=target["name"],
            default_type=target["default_type"],
        ))

    return projects[:20]


def parse_poit(soup: BeautifulSoup, target: dict) -> list[dict]:
    """Parse Post- och Inrikes Tidningar announcement list."""
    projects = []
    for row in soup.select("tr.publikation, table.resultat tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        title = cells[0].get_text(strip=True)
        if not title or len(title) < 5:
            continue
        link_tag = cells[0].find("a", href=True)
        url = link_tag["href"] if link_tag else target["url"]
        if url.startswith("/"):
            url = "https://poit.bolagsverket.se" + url
        description = " ".join(c.get_text(strip=True) for c in cells[1:])
        region = _match_region(f"{title} {description}")
        location = region
        projects.append(_make_project(
            title=title,
            description=description,
            location=location,
            region=region,
            source_url=url,
            source_name=target["name"],
            default_type=target["default_type"],
        ))
    return projects


def parse_generic(soup: BeautifulSoup, target: dict) -> list[dict]:
    """
    Fallback parser: picks up any heading+paragraph pairs that look like
    building permit entries. Works reasonably well across most municipality
    page layouts.
    """
    projects = []
    permit_kw = [
        "bygglov", "byggnadslov", "rivningslov", "marklov", "attefallsåtgärd",
        "planbesked", "startbesked", "slutbesked", "bygganmälan",
    ]
    for heading in soup.find_all(["h2", "h3", "h4"]):
        title = heading.get_text(strip=True)
        if not any(kw in title.lower() for kw in permit_kw):
            continue
        # Grab nearby paragraph as description
        next_p = heading.find_next_sibling(["p", "div"])
        description = next_p.get_text(strip=True) if next_p else title
        link_tag = heading.find("a", href=True) or heading.find_next("a", href=True)
        url = target["url"]
        if link_tag:
            url = link_tag["href"]
            if url.startswith("/"):
                base = "/".join(target["url"].split("/")[:3])
                url = base + url
        region = target.get("region") or _match_region(f"{title} {description}")
        location = region
        projects.append(_make_project(
            title=title,
            description=description,
            location=location,
            region=region,
            source_url=url,
            source_name=target["name"],
            default_type=target["default_type"],
        ))
    return projects


_PARSERS = {
    "parse_stockholm": parse_stockholm,
    "parse_poit": parse_poit,
    "parse_generic": parse_generic,
    "parse_decision_list": parse_decision_list,
}

# ── Main entry point ──────────────────────────────────────────────────────────

async def scrape_permits() -> list[dict]:
    """Fetch municipality building permit pages and return structured projects."""
    all_projects: list[dict] = []

    async with httpx.AsyncClient(headers=_HEADERS, timeout=20, follow_redirects=True) as client:
        for target in MUNICIPALITY_TARGETS:
            try:
                resp = await client.get(target["url"])
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")
                parser_fn = _PARSERS[target["parser"]]
                projects = parser_fn(soup, target)
                log.info("Permit scrape %s — %d items", target["name"], len(projects))

                # Geocode entries that lack coordinates
                for p in projects:
                    if p["lat"] is None and p["location"]:
                        coords = await geocode_location(p["location"], p["region"])
                        if coords:
                            p["lat"], p["lng"] = coords

                all_projects.extend(projects)
            except Exception as exc:
                log.warning("Permit scrape failed for %s: %s", target["name"], exc)
                continue

    return all_projects
