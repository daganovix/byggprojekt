"""
API-based scrapers for Swedish construction project data.

Sources:
1. Trafikverket Open API  — road/rail infrastructure projects (coordinates included)
   Requires env var TRAFIKVERKET_API_KEY; skipped if not set.

NOTE: CKAN open-data portals (Göteborg, Stockholm, dataportal.se) have been
removed — their /api/3/action/ endpoints return 404 and the portals no longer
expose a standard CKAN API at those base URLs.
"""
import asyncio
import logging
import os
import re
from datetime import datetime
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

_TV_QUERY_TEMPLATE = """<REQUEST>
  <LOGIN authenticationkey="{api_key}"/>
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
    api_key = os.environ.get("TRAFIKVERKET_API_KEY", "").strip()
    if not api_key:
        log.info("Trafikverket API skipped — set TRAFIKVERKET_API_KEY to enable")
        return []

    projects: list[dict] = []
    query = _TV_QUERY_TEMPLATE.format(api_key=api_key)
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                _TV_ENDPOINT,
                content=query.strip(),
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


# ── Entry point ───────────────────────────────────────────────────────────────

async def scrape_api_sources() -> list[dict]:
    return await scrape_trafikverket()
