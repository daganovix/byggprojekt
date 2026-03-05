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
    # Stockholm – city planning news (guaranteed to exist)
    {
        "name": "Stockholms stad – Stadsutveckling",
        "url": "https://www.stockholm.se/stadsutveckling/",
        "parser": "parse_decision_list",
        "default_type": "Offentligt",
        "region": "Stockholm",
    },
    # Göteborg – generic news (nyheter/ proved reachable via redirect)
    {
        "name": "Göteborgs stad – Nyheter",
        "url": "https://goteborg.se/nyheter/",
        "parser": "parse_decision_list",
        "default_type": "Offentligt",
        "region": "Västra Götaland",
    },
    # Malmö – main news section
    {
        "name": "Malmö stad – Nyheter",
        "url": "https://malmo.se/nyheter/",
        "parser": "parse_decision_list",
        "default_type": "Offentligt",
        "region": "Skåne",
    },
    # Uppsala – building news (confirmed 200 OK)
    {
        "name": "Uppsala kommun – Bygg och plan",
        "url": "https://www.uppsala.se/nyheter/?category=bygg",
        "parser": "parse_decision_list",
        "default_type": "Offentligt",
        "region": "Uppsala",
    },
    # Linköping – news
    {
        "name": "Linköpings kommun – Nyheter",
        "url": "https://www.linkoping.se/nyheter/",
        "parser": "parse_decision_list",
        "default_type": "Offentligt",
        "region": "Östergötland",
    },
    # Västerås – news
    {
        "name": "Västerås stad – Nyheter",
        "url": "https://www.vasteras.se/nyheter/",
        "parser": "parse_decision_list",
        "default_type": "Offentligt",
        "region": "Västmanland",
    },
    # Post- och Inrikes Tidningar – official gazette, plan/building categories
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
    """
    Parse Post- och Inrikes Tidningar announcement list.

    PoIT is a Java/.do app whose exact HTML structure has varied; try every
    reasonable layout (tables, lists, any anchor inside a result container).
    """
    projects = []
    base = "https://poit.bolagsverket.se"

    def _add(title: str, description: str, url: str) -> None:
        if not title or len(title) < 5:
            return
        region = _match_region(f"{title} {description}")
        projects.append(_make_project(
            title=title,
            description=description,
            location=region,
            region=region,
            source_url=url,
            source_name=target["name"],
            default_type=target["default_type"],
        ))

    # Pass 1 – any <table> on the page
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            link = row.find("a", href=True)
            url = (link["href"] if link else target["url"])
            if url.startswith("/"):
                url = base + url
            title = (link.get_text(strip=True) if link
                     else cells[0].get_text(strip=True))
            desc = " ".join(c.get_text(strip=True) for c in cells
                            if c != (link.parent if link else None))
            _add(title, desc, url)

    # Pass 2 – <li> or <div> items that contain a link  (common SPA/portal output)
    if not projects:
        for container_sel in ("li", "div.result", "div.item", "div.row"):
            for el in soup.select(container_sel):
                link = el.find("a", href=True)
                if not link:
                    continue
                href = link["href"]
                url = href if href.startswith("http") else base + href
                title = link.get_text(strip=True)
                desc = el.get_text(strip=True)
                _add(title, desc, url)
            if projects:
                break

    # Pass 3 – last resort: every outbound link that goes to a publication detail
    if not projects:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "publikation" not in href.lower() and "poit" not in href.lower():
                continue
            url = href if href.startswith("http") else base + href
            title = a.get_text(strip=True)
            _add(title, title, url)

    if not projects:
        page_title = soup.title.get_text(strip=True) if soup.title else "N/A"
        # Log the first 400 chars of body text to diagnose structure
        body_text = soup.get_text(separator=" ", strip=True)[:400]
        log.warning(
            "PoIT 0 items from %s | page title: %r | body snippet: %r",
            target["url"], page_title, body_text,
        )

    return projects[:30]


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
