import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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


async def run_scraper():
    """Pull all sources, extract projects, upsert into DB."""
    log.info("Starting scrape run…")
    try:
        # Run RSS feeds and API sources concurrently; company pages separately (slower)
        (rss_projects, api_projects), permit_projects = await asyncio.gather(
            asyncio.gather(scrape_all_feeds(), scrape_api_sources()),
            scrape_permits(),
        )
        company_projects = await scrape_company_pages()
        projects = rss_projects + api_projects + permit_projects + company_projects
        log.info(
            "Scraped: %d RSS, %d API, %d permits, %d company",
            len(rss_projects), len(api_projects),
            len(permit_projects), len(company_projects),
        )
        async with SessionLocal() as db:
            new_count = 0
            for p in projects:
                # Dedup by source_url (if present) or by (source_name, name)
                if p["source_url"]:
                    existing = await db.scalar(
                        select(ProjectDB).where(ProjectDB.source_url == p["source_url"])
                    )
                    if existing:
                        continue
                else:
                    existing = await db.scalar(
                        select(ProjectDB).where(
                            ProjectDB.source_name == p["source_name"],
                            ProjectDB.name == p["name"],
                        )
                    )
                    if existing:
                        continue
                db.add(ProjectDB(**p))
                new_count += 1
            await db.commit()
        log.info("Scrape complete — %d new projects added (total scraped: %d)", new_count, len(projects))
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
