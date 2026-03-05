# Byggprojekt Sverige

Aggregates Swedish construction project news from RSS feeds and displays them on an interactive map and sortable list.

## Features

- **Map view** — OpenStreetMap/Leaflet with colour-coded markers by project type
- **List view** — sortable table with all 8 fields
- **Filter panel** — filter by type, region, status, or free-text search
- **Project detail modal** — full info including participants with contact details
- **Auto-scrape** — RSS feeds scraped on startup and every 2 hours
- **Manual refresh** — "Uppdatera" button triggers an immediate scrape

## Data sources (RSS)

| Source | Type |
|---|---|
| Byggindustrin | General construction |
| Trafikverket | Infrastructure |
| Fastighetsnytt | Real estate / commercial |
| Byggnyheter | General construction |
| Upphandlingsmyndigheten | Public procurement |
| Riksbyggen | Residential |

## Quick start

```bash
./start.sh
```

Requires: Python 3.10+, Node.js 18+

Opens at **http://localhost:5173**

## Manual setup

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py                          # load 15 demo projects
uvicorn app.main:app --reload           # http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                             # http://localhost:5173
```

## API

| Endpoint | Description |
|---|---|
| `GET /api/projects` | List projects (filters: type, region, status, search, min_cost, max_cost) |
| `GET /api/projects/{id}` | Single project |
| `GET /api/stats` | Counts by type / status / region |
| `GET /api/filters` | Available filter values |
| `POST /api/refresh` | Trigger scrape now |
| `GET /docs` | Swagger UI |

## Project fields

| Field | Source |
|---|---|
| **Name** | Article title |
| **Type** | Classified by keywords (Bostäder / Infrastruktur / Kommersiellt / Offentligt / Industri) |
| **Participants** | Extracted known companies + roles from article text |
| **Contact** | Included where seed data provides it; RSS articles rarely list contacts |
| **Estimated cost** | Regex-extracted (mkr / miljarder) |
| **Timeline** | Regex-extracted year ranges |

## Notes

- Geocoding uses Nominatim (OpenStreetMap) — free, no API key needed, 1 req/s rate limit
- Projects without coordinates are shown in list view only
- Contact information comes from seed data; live RSS articles rarely include it — you can enrich via the API
