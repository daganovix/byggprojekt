import asyncio
import json
import logging
import os
import re
import urllib.parse
import xml.etree.ElementTree as ET
from contextlib import asynccontextmanager
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Optional

import httpx

import anthropic
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import init_db, get_db, SessionLocal
from app.models import ProjectDB, ProjectOut, ProjectList, StatsOut
from app.scrapers.feed_scraper import scrape_all_feeds
from app.scrapers.permit_scraper import scrape_permits
from app.scrapers.api_scraper import scrape_api_sources
from app.scrapers.company_scraper import scrape_company_pages

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _save_projects(projects: list[dict]) -> int:
    """Upsert projects into DB. Returns count of new rows added."""
    async with SessionLocal() as db:
        new_count = 0
        for p in projects:
            if p["source_url"]:
                existing = await db.scalar(
                    select(ProjectDB).where(ProjectDB.source_url == p["source_url"])
                )
            else:
                existing = await db.scalar(
                    select(ProjectDB).where(
                        ProjectDB.source_name == p["source_name"],
                        ProjectDB.name == p["name"],
                    )
                )
            if existing:
                continue
            p.pop("default_type", None)
            db.add(ProjectDB(**p))
            new_count += 1
        await db.commit()
    return new_count


async def run_scraper():
    """Pull all sources, extract projects, upsert into DB."""
    log.info("Starting scrape run…")
    try:
        # Phase 1: fast sources in parallel — save as soon as done so the UI
        # updates within ~60 s without waiting for the slower company scraper.
        (rss_projects, api_projects), permit_projects = await asyncio.gather(
            asyncio.gather(scrape_all_feeds(), scrape_api_sources()),
            scrape_permits(),
        )
        fast_new = await _save_projects(rss_projects + api_projects + permit_projects)
        log.info(
            "Phase 1 done — %d RSS, %d API, %d permits → %d new saved",
            len(rss_projects), len(api_projects), len(permit_projects), fast_new,
        )

        # Phase 2: company pages (slower — JS-rendered sites return 0 cards quickly;
        # server-rendered ones add real projects).
        company_projects = await scrape_company_pages()
        company_new = await _save_projects(company_projects)
        log.info("Phase 2 done — %d company → %d new saved", len(company_projects), company_new)
    except Exception as exc:
        log.exception("Scraper error: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Schedule scrape every 2 hours
    scheduler.add_job(run_scraper, "interval", hours=2, id="scraper")
    scheduler.start()
    # Run once on startup (non-blocking)
    asyncio.create_task(run_scraper())
    yield
    scheduler.shutdown()


app = FastAPI(title="Swedish Construction Projects API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/api/projects", response_model=ProjectList)
async def list_projects(
    type: Optional[str] = None,
    region: Optional[str] = None,
    status: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
    search: Optional[str] = None,
    limit: int = Query(default=200, le=500),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    q = select(ProjectDB)

    if type:
        q = q.where(ProjectDB.type == type)
    if region:
        q = q.where(ProjectDB.region == region)
    if status:
        q = q.where(ProjectDB.status == status)
    if min_cost is not None:
        q = q.where(ProjectDB.cost_value_msek >= min_cost)
    if max_cost is not None:
        q = q.where(ProjectDB.cost_value_msek <= max_cost)
    if search:
        term = f"%{search}%"
        q = q.where(
            or_(
                ProjectDB.name.ilike(term),
                ProjectDB.description.ilike(term),
                ProjectDB.location.ilike(term),
            )
        )

    total_q = select(func.count()).select_from(q.subquery())
    total = await db.scalar(total_q) or 0

    q = q.order_by(ProjectDB.published_at.desc()).offset(offset).limit(limit)
    rows = (await db.scalars(q)).all()

    return ProjectList(
        total=total,
        projects=[_to_out(r) for r in rows],
    )


@app.get("/api/projects/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(ProjectDB, project_id)
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")
    return _to_out(row)


@app.get("/api/stats", response_model=StatsOut)
async def get_stats(db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(select(ProjectDB))).all()
    by_type: dict = {}
    by_status: dict = {}
    by_region: dict = {}
    for r in rows:
        by_type[r.type] = by_type.get(r.type, 0) + 1
        by_status[r.status] = by_status.get(r.status, 0) + 1
        if r.region:
            by_region[r.region] = by_region.get(r.region, 0) + 1
    return StatsOut(total=len(rows), by_type=by_type, by_status=by_status, by_region=by_region)


@app.post("/api/refresh")
async def trigger_refresh():
    """Manually trigger a scrape run (runs in background)."""
    asyncio.create_task(run_scraper())
    return {"message": "Scrape started"}


# Domain knowledge: typical (role → companies) per project type.
# Based on Swedish construction industry patterns:
# - Beställare/Byggherre: municipalities, public bodies, property companies
# - Totalentreprenör: Skanska, NCC, PEAB, Veidekke, Serneke
# - Arkitekt: White Arkitekter, Sweco Architects, Wingårdhs, Tengbom
# - Konstruktör/teknisk konsult: Sweco, WSP, Ramboll, Tyréns, AFRY
_ROLE_PRIORS: dict[str, list[dict]] = {
    "Infrastruktur": [
        {"role": "Beställare",        "companies": ["Trafikverket", "Jernhusen", "Stockholms stad", "Göteborgs stad", "Malmö stad"]},
        {"role": "Totalentreprenör",  "companies": ["Skanska", "NCC", "PEAB", "Veidekke", "Serneke"]},
        {"role": "Konstruktör",       "companies": ["Sweco", "WSP", "Ramboll", "Tyréns", "AFRY"]},
        {"role": "Projektledare",     "companies": ["Sweco", "WSP", "Tyréns"]},
    ],
    "Bostäder": [
        {"role": "Byggherre",         "companies": ["JM", "Riksbyggen", "HSB", "Bonava", "Wallenstam", "Besqab", "Magnolia"]},
        {"role": "Totalentreprenör",  "companies": ["Skanska", "NCC", "PEAB", "Veidekke", "Serneke"]},
        {"role": "Arkitekt",          "companies": ["White Arkitekter", "Sweco Architects", "Liljewall", "Tengbom", "Fojab"]},
        {"role": "Konstruktör",       "companies": ["Sweco", "WSP", "Ramboll", "Tyréns"]},
    ],
    "Kommersiellt": [
        {"role": "Fastighetsägare",   "companies": ["Fabege", "Castellum", "Vasakronan", "Atrium Ljungberg", "Kungsleden", "Wihlborgs"]},
        {"role": "Byggherre",         "companies": ["Fabege", "Castellum", "Vasakronan", "Skanska", "NCC"]},
        {"role": "Totalentreprenör",  "companies": ["Skanska", "NCC", "PEAB", "Serneke"]},
        {"role": "Arkitekt",          "companies": ["White Arkitekter", "Wingårdhs", "Sweco Architects", "Tengbom"]},
    ],
    "Offentligt": [
        {"role": "Beställare",        "companies": ["Akademiska Hus", "Stockholms stad", "Göteborgs stad", "Malmö stad", "Region Stockholm"]},
        {"role": "Byggherre",         "companies": ["Akademiska Hus", "Stockholms stad", "Region Stockholm"]},
        {"role": "Totalentreprenör",  "companies": ["Skanska", "NCC", "PEAB", "Veidekke"]},
        {"role": "Arkitekt",          "companies": ["White Arkitekter", "Sweco Architects", "Tengbom", "Wingårdhs"]},
    ],
    "Industri": [
        {"role": "Beställare",        "companies": ["Trafikverket", "Stockholms stad", "Göteborgs stad"]},
        {"role": "Totalentreprenör",  "companies": ["Skanska", "NCC", "PEAB", "Serneke"]},
        {"role": "Konstruktör",       "companies": ["Sweco", "WSP", "Ramboll", "Tyréns", "AFRY"]},
    ],
    "Övrigt": [
        {"role": "Byggherre",         "companies": ["Skanska", "NCC", "PEAB", "JM"]},
        {"role": "Totalentreprenör",  "companies": ["Skanska", "NCC", "PEAB", "Veidekke"]},
    ],
}

_TYPICAL_ROLES: dict[str, list[str]] = {
    "Infrastruktur": ["Beställare", "Totalentreprenör", "Konstruktör"],
    "Bostäder":      ["Byggherre", "Totalentreprenör", "Arkitekt", "Konstruktör"],
    "Kommersiellt":  ["Byggherre", "Totalentreprenör", "Arkitekt", "Fastighetsägare"],
    "Offentligt":    ["Beställare", "Totalentreprenör", "Arkitekt"],
    "Industri":      ["Beställare", "Totalentreprenör", "Konstruktör"],
    "Övrigt":        ["Byggherre", "Totalentreprenör"],
}


@app.get("/api/projects/{project_id}/predictions")
async def get_project_predictions(project_id: int, db: AsyncSession = Depends(get_db)):
    """Return likely unconfirmed participants based on historical co-occurrence
    in similar projects (same type) and domain knowledge priors."""
    project = await db.get(ProjectDB, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    known_names: set[str] = {
        p["name"] for p in (project.participants or []) if p.get("name")
    }
    current_roles: set[str] = {
        p.get("role", "") for p in (project.participants or []) if p.get("role")
    }

    # ── Step 1: Co-occurrence from historical data ────────────────────────────
    similar_rows = (
        await db.scalars(
            select(ProjectDB).where(
                ProjectDB.type == project.type,
                ProjectDB.id != project_id,
            )
        )
    ).all()

    # {company: {"count": int, "roles": {role: int}}}
    cooccurrence: dict[str, dict] = {}
    for sim in similar_rows:
        sim_parts = sim.participants or []
        sim_names = {p["name"] for p in sim_parts if p.get("name")}
        if not (sim_names & known_names):
            continue
        for p in sim_parts:
            name = p.get("name", "")
            role = p.get("role", "")
            if not name or name in known_names:
                continue
            if name not in cooccurrence:
                cooccurrence[name] = {"count": 0, "roles": {}}
            cooccurrence[name]["count"] += 1
            if role:
                cooccurrence[name]["roles"][role] = cooccurrence[name]["roles"].get(role, 0) + 1

    # ── Step 2: Identify roles not yet represented ────────────────────────────
    missing_roles: set[str] = set(_TYPICAL_ROLES.get(project.type, [])) - current_roles

    # ── Step 3: Build candidate scores ───────────────────────────────────────
    # {company: {"role": str, "score": int, "basis": str}}
    candidates: dict[str, dict] = {}

    # Co-occurrence carries high weight (real evidence)
    for name, data in cooccurrence.items():
        best_role = (
            max(data["roles"], key=data["roles"].get)
            if data["roles"] else ""
        )
        score = data["count"] * 10
        candidates[name] = {
            "role": best_role,
            "score": score,
            "basis": f"Historisk samförekomst i {data['count']} liknande {'projekt' if data['count'] != 1 else 'projekt'}",
        }

    # Domain priors fill gaps for missing roles
    for entry in _ROLE_PRIORS.get(project.type, []):
        role = entry["role"]
        if role not in missing_roles:
            continue
        for idx, company in enumerate(entry["companies"]):
            if company in known_names:
                continue
            prior_score = max(1, 5 - idx)
            if company in candidates:
                candidates[company]["score"] += prior_score
            else:
                candidates[company] = {
                    "role": role,
                    "score": prior_score,
                    "basis": f"Typisk {role} i {project.type}-projekt",
                }

    # ── Step 4: Rank, label confidence, return top 5 ─────────────────────────
    ranked = sorted(candidates.items(), key=lambda x: x[1]["score"], reverse=True)[:5]

    predictions = []
    for name, info in ranked:
        score = info["score"]
        confidence = "hög" if score >= 10 else ("medel" if score >= 5 else "låg")
        predictions.append({
            "name": name,
            "likely_role": info["role"],
            "confidence": confidence,
            "basis": info["basis"],
        })

    return {
        "predictions": predictions,
        "missing_roles": sorted(missing_roles),
    }


class CoachRequest(BaseModel):
    message: str
    history: list[dict] = []


@app.post("/api/projects/{project_id}/coach")
async def sales_coach(project_id: int, body: CoachRequest, db: AsyncSession = Depends(get_db)):
    row = await db.get(ProjectDB, project_id)
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")

    p = _to_out(row)

    participants_text = "\n".join(
        f"- {pt.name} ({pt.role or 'okänd roll'})"
        for pt in (p.participants or [])
    ) or "Inga bekräftade deltagare"

    timeline = ""
    if p.timeline_start:
        timeline = p.timeline_start
        if p.timeline_end and p.timeline_end != p.timeline_start:
            timeline += f" – {p.timeline_end}"

    system_prompt = f"""Du är en erfaren B2B-säljcoach specialiserad på den svenska byggbranschen. Du hjälper säljare att vinna uppdrag, bygga relationer med rätt beslutsfattare och skapa konkreta nästa steg.

PROJEKTINFORMATION:
Namn: {p.name}
Typ: {p.type}
Status: {p.status}
Plats: {p.location}{f', {p.region}' if p.region and p.region != p.location else ''}
Beräknad kostnad: {p.estimated_cost or 'Okänd'}
Tidplan: {timeline or 'Okänd'}
Beskrivning: {p.description or 'Ingen beskrivning tillgänglig'}

BEKRÄFTADE DELTAGARE:
{participants_text}

COACHING-PRINCIPER:
- Ge konkreta, actionabla råd – inga generella platityder
- Prioritera alltid nästa steg tydligt
- Anpassa approach efter deltagarnas roller (beställare vs. entreprenör vs. arkitekt)
- Hjälp med formuleringar och konkreta mail-/samtalsmanus vid behov
- Svara på svenska, kortfattat och direkt"""

    messages = body.history + [{"role": "user", "content": body.message}]

    ai_client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

    async def stream():
        try:
            async with ai_client.messages.stream(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=system_prompt,
                messages=messages,
            ) as s:
                async for text in s.text_stream:
                    yield f"data: {json.dumps({'text': text})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/projects/{project_id}/updates")
async def get_project_updates(
    project_id: int,
    period: str = Query("week", pattern="^(day|week|month)$"),
    db: AsyncSession = Depends(get_db),
):
    row = await db.get(ProjectDB, project_id)
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")

    query = " ".join(filter(None, [row.name, row.location or row.region]))
    rss_url = (
        f"https://news.google.com/rss/search?"
        f"q={urllib.parse.quote(query)}&hl=sv&gl=SE&ceid=SE:sv"
    )

    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(rss_url)
            resp.raise_for_status()
            xml_text = resp.text
    except Exception as e:
        return {"updates": [], "query": query, "error": str(e)}

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return {"updates": [], "query": query}

    period_days = {"day": 1, "week": 7, "month": 30}.get(period, 7)
    cutoff = __import__("datetime").datetime.now(timezone.utc) - timedelta(days=period_days)

    items = []
    for item in root.findall(".//item")[:40]:
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        desc_raw = item.findtext("description") or ""
        pub_str = item.findtext("pubDate") or ""
        desc = re.sub(r"<[^>]+>", "", desc_raw).strip()

        try:
            pub_dt = parsedate_to_datetime(pub_str)
            if pub_dt < cutoff:
                continue
            pub_fmt = pub_dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            pub_fmt = pub_str

        items.append({
            "title": title,
            "description": desc,
            "url": link,
            "published": pub_fmt,
        })

    return {"updates": items, "query": query}


class UpdateAnalysisRequest(BaseModel):
    title: str
    description: str = ""


@app.post("/api/projects/{project_id}/analyze-update")
async def analyze_update(
    project_id: int,
    body: UpdateAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    row = await db.get(ProjectDB, project_id)
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")

    system_prompt = (
        f'Du är en erfaren B2B-säljcoach specialiserad på den svenska byggbranschen.\n'
        f'En säljare har hittat en nyhet kopplad till projektet "{row.name}" '
        f'({row.type or ""}, {row.status or ""}) i {row.location or row.region or "Sverige"}.\n'
        f'Förklara kort (2–3 meningar) vad nyheten kan innebära för projektet och ge '
        f'ett konkret råd om hur säljaren bör agera. Svara på svenska.'
    )
    message = f"Nyhet: {body.title}\n\n{body.description}"
    ai_client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

    async def stream():
        try:
            async with ai_client.messages.stream(
                model="claude-haiku-4-5-20251001",
                max_tokens=400,
                system=system_prompt,
                messages=[{"role": "user", "content": message}],
            ) as s:
                async for text in s.text_stream:
                    yield f"data: {json.dumps({'text': text})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/filters")
async def get_filter_options(db: AsyncSession = Depends(get_db)):
    rows = (await db.scalars(select(ProjectDB))).all()
    types = sorted({r.type for r in rows if r.type})
    regions = sorted({r.region for r in rows if r.region})
    statuses = sorted({r.status for r in rows if r.status})
    return {"types": types, "regions": regions, "statuses": statuses}


# ── Helper ───────────────────────────────────────────────────────────────────

def _to_out(row: ProjectDB) -> ProjectOut:
    participants = row.participants or []
    # Ensure each participant matches the Participant schema
    clean = []
    for p in participants:
        if isinstance(p, dict):
            clean.append({"name": p.get("name", ""), "role": p.get("role", ""), "contact": p.get("contact", "")})
    return ProjectOut(
        id=row.id,
        name=row.name,
        type=row.type,
        description=row.description or "",
        location=row.location or "",
        region=row.region or "",
        lat=row.lat,
        lng=row.lng,
        participants=clean,
        estimated_cost=row.estimated_cost or "",
        cost_value_msek=row.cost_value_msek,
        timeline_start=row.timeline_start or "",
        timeline_end=row.timeline_end or "",
        status=row.status or "",
        source_url=row.source_url or "",
        source_name=row.source_name or "",
        published_at=row.published_at or __import__("datetime").datetime.utcnow(),
    )


# ── Serve built React frontend (production) ───────────────────────────────────
# The Dockerfile copies the Vite build output to /app/static.
# Any non-API route falls through to index.html (SPA routing).

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")

if os.path.isdir(_STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(_STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        return FileResponse(os.path.join(_STATIC_DIR, "index.html"))
