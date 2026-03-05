"""
API-based scrapers for Swedish construction project data.

Sources:
1. Trafikverket Open API  — road/rail infrastructure projects (coordinates included)
2. Göteborg Open Data     — building permits via CKAN REST API
3. Stockholm Open Data    — building permits via CKAN REST API
"""
import asyncio
import logging
import re
from datetime import datetime
from typing import Optional

import httpx

from app.scrapers.geocoder import geocode_location
from app.scrapers.sources import TYPE_KEYWORDS

log = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ByggprojektBot/1.0; +https://byggprojekt.se)",
    "Accept": "application/json",
}

# ── Trafikverket Open API ─────────────────────────────────────────────────────

_TV_ENDPOINT = "https://api.trafikinfo.trafikverket.se/v2/data.json"

# Empty authenticationkey = public/anonymous access for most object types
_TV_QUERY = """<REQUEST>
  <LOGIN authenticationkey=""/>
  <QUERY objecttype="Project" schemaversion="1" limit="500">
    <INCLUDE>Name,Description,County,Geometry.WGS84,StartDate,EndDate,Status,Contractor</INCLUDE>
  </QUERY>
</REQUEST>"""

_WKT_POINT_RE = re.compile(r"POINT\s*\((-?\d+\.?\d*)\s+(-?\d+\.?\d*)\)")

_COUNTY_MAP = {
    "Stockholms län": "Stockholm",
    "Uppsala län": "Uppsala",
    "Södermanlands län": "Södermanland",
    "Östergötlands län": "Östergötland",
    "Jönköpings län": "Jönköping",
    "Kronobergs län": "Kronoberg",
    "Kalmar län": "Kalmar",
    "Gotlands län": "Gotland",
    "Blekinge län": "Blekinge",
    "Skåne län": "Skåne",
    "Hallands län": "Halland",
    "Västra Götalands län": "Västra Götaland",
    "Värmlands län": "Värmland",
    "Örebro län": "Örebro",
    "Västmanlands län": "Västmanland",
    "Dalarnas län": "Dalarna",
    "Gävleborgs län": "Gävleborg",
    "Västernorrlands län": "Västernorrland",
    "Jämtlands län": "Jämtland",
    "Västerbottens län": "Västerbotten",
    "Norrbottens län": "Norrbotten",
}


def _tv_status(raw: str) -> str:
    s = raw.lower()
    if any(x in s for x in ("pågående", "genomförande", "byggskede")):
        return "Pågående"
    if any(x in s for x in ("avslutat", "klart", "färdigt", "öppnat")):
        return "Klart"
    return "Planerat"


def _infer_type(text: str) -> str:
    lower = text.lower()
    for project_type, keywords in TYPE_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return project_type
    return "Infrastruktur"


async def scrape_trafikverket() -> list[dict]:
    projects: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                _TV_ENDPOINT,
                content=_TV_QUERY.strip(),
                headers={"Content-Type": "application/xml", **_HEADERS},
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        log.warning("Trafikverket API error: %s", exc)
        return []

    raw = (
        data.get("RESPONSE", {})
        .get("RESULT", [{}])[0]
        .get("Project", [])
    )
    log.info("Trafikverket API — %d raw projects", len(raw))

    for p in raw:
        name = (p.get("Name") or "").strip()
        if not name:
            continue

        status = _tv_status(p.get("Status") or "")
        if status == "Klart":
            continue  # Skip completed projects

        desc = (p.get("Description") or "").strip()
        county = p.get("County") or ""
        region = _COUNTY_MAP.get(county, county.replace(" län", "") if " län" in county else county)

        # Parse WGS84 geometry: WKT "POINT (lng lat)"
        lat = lng = None
        geom = (p.get("Geometry") or {}).get("WGS84") or ""
        if geom:
            m = _WKT_POINT_RE.search(geom)
            if m:
                lng = float(m.group(1))
                lat = float(m.group(2))

        start = (p.get("StartDate") or "")[:4]
        end = (p.get("EndDate") or "")[:4]
        contractor = (p.get("Contractor") or "").strip()
        participants = [{"name": contractor, "role": "Entreprenör", "contact": ""}] if contractor else []

        # Stable dedup key (no page URL available)
        safe_name = re.sub(r"[^a-z0-9]+", "-", name.lower())[:80]
        source_url = f"https://www.trafikverket.se/vara-projekt/{safe_name}"

        projects.append({
            "name": name[:200],
            "type": _infer_type(f"{name} {desc}"),
            "description": desc[:1000],
            "location": region,
            "region": region,
            "lat": lat,
            "lng": lng,
            "participants": participants,
            "estimated_cost": "",
            "cost_value_msek": None,
            "timeline_start": start,
            "timeline_end": end,
            "status": status,
            "source_url": source_url,
            "source_name": "Trafikverket",
            "published_at": datetime.utcnow(),
        })

    return projects


# ── CKAN open data (Göteborg, Stockholm building permits) ─────────────────────

_CKAN_SOURCES = [
    # Göteborg – their CKAN open-data portal
    {
        "name": "Göteborg Open Data – Bygglov",
        "base_url": "https://data.goteborg.se",
        "search_queries": ["bygglov", "beviljade bygglov", "plan och bygg", "nybyggnad"],
        "region": "Västra Götaland",
        "default_type": "Offentligt",
    },
    # Stockholm – their open-data portal (original confirmed hostname)
    {
        "name": "Stockholm Open Data – Bygglov",
        "base_url": "https://dataportalen.stockholm.se",
        "search_queries": ["bygglov", "beviljade bygglov", "plan", "nybyggnad"],
        "region": "Stockholm",
        "default_type": "Offentligt",
    },
    # Swedish national open-data portal (aggregates all municipalities)
    {
        "name": "Sveriges dataportal – Bygglov",
        "base_url": "https://www.dataportal.se",
        "search_queries": ["bygglov", "bygglovsstatistik", "beviljade bygglov"],
        "region": "",
        "default_type": "Offentligt",
    },
]

_PERMIT_KW = [
    "nybyggnad", "tillbyggnad", "ombyggnad", "påbyggnad",
    "bostäder", "kontor", "skola", "handel", "industri", "lager",
    "hotell", "sjukhus", "kyrka", "garage",
]


async def _find_ckan_resource(client: httpx.AsyncClient, base_url: str, queries: list[str]) -> Optional[str]:
    """Try multiple CKAN package_search queries; return first datastore resource ID found."""
    for query in queries:
        try:
            r = await client.get(
                f"{base_url}/api/3/action/package_search",
                params={"q": query, "rows": 10},
                timeout=20,
            )
            r.raise_for_status()
            for pkg in r.json().get("result", {}).get("results", []):
                for res in pkg.get("resources", []):
                    rid = res.get("id")
                    if rid:
                        return rid
        except Exception as exc:
            log.warning("CKAN package_search failed at %s (q=%r): %s", base_url, query, exc)
    return None


async def _scrape_one_ckan(client: httpx.AsyncClient, source: dict) -> list[dict]:
    queries = source.get("search_queries") or [source.get("search_query", "bygglov")]
    resource_id = await _find_ckan_resource(client, source["base_url"], queries)
    if not resource_id:
        log.warning("CKAN: no resource found for %s", source["name"])
        return []

    try:
        r = await client.get(
            f"{source['base_url']}/api/3/action/datastore_search",
            params={"resource_id": resource_id, "limit": 300},
            timeout=30,
        )
        r.raise_for_status()
        records = r.json().get("result", {}).get("records", [])
    except Exception as exc:
        log.warning("CKAN datastore_search failed for %s: %s", source["name"], exc)
        return []

    log.info("CKAN %s — %d records", source["name"], len(records))
    projects: list[dict] = []

    for rec in records:
        # Field names vary per dataset — try common variants
        address = (
            rec.get("adress") or rec.get("address") or
            rec.get("gatuadress") or rec.get("fastighets_beteckning") or
            rec.get("fastighetsbeteckning") or ""
        )
        desc = (
            rec.get("atgard") or rec.get("åtgärd") or
            rec.get("beskrivning") or rec.get("description") or
            rec.get("anmarkning") or rec.get("åtgärdsbeskrivning") or ""
        )
        rec_id = str(
            rec.get("arendenummer") or rec.get("diarie_nummer") or
            rec.get("dnr") or rec.get("_id") or rec.get("id") or ""
        )
        date_str = (
            rec.get("beslutsdatum") or rec.get("datum") or
            rec.get("date") or rec.get("inkomstdatum") or ""
        )

        if not address and not desc:
            continue

        full_text = f"{address} {desc}".lower()
        if not any(kw in full_text for kw in _PERMIT_KW):
            continue

        pub = datetime.utcnow()
        if date_str:
            try:
                pub = datetime.fromisoformat(str(date_str)[:10])
            except Exception:
                pass

        source_url = (
            f"{source['base_url']}/dataset/bygglov?record={rec_id}"
            if rec_id else ""
        )
        geocode_query = f"{address}, Sverige" if address else source["region"]
        coords = await geocode_location(geocode_query, source["region"])
        lat = coords[0] if coords else None
        lng = coords[1] if coords else None

        title = (desc or address)[:200]
        projects.append({
            "name": title,
            "type": source["default_type"],
            "description": desc[:1000],
            "location": address or source["region"],
            "region": source["region"],
            "lat": lat,
            "lng": lng,
            "participants": [],
            "estimated_cost": "",
            "cost_value_msek": None,
            "timeline_start": "",
            "timeline_end": "",
            "status": "Pågående",
            "source_url": source_url,
            "source_name": source["name"],
            "published_at": pub,
        })

    return projects


async def scrape_ckan_sources() -> list[dict]:
    async with httpx.AsyncClient(headers=_HEADERS, follow_redirects=True, timeout=30) as client:
        results = await asyncio.gather(
            *[_scrape_one_ckan(client, src) for src in _CKAN_SOURCES],
            return_exceptions=True,
        )
    projects: list[dict] = []
    for r in results:
        if isinstance(r, list):
            projects.extend(r)
    return projects


# ── Entry point ───────────────────────────────────────────────────────────────

async def scrape_api_sources() -> list[dict]:
    tv, ckan = await asyncio.gather(
        scrape_trafikverket(),
        scrape_ckan_sources(),
    )
    return tv + ckan
