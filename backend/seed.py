"""
Seed the database with realistic Swedish construction projects for demo purposes.
Run once: python seed.py
"""
import asyncio
from datetime import datetime
from app.database import init_db, SessionLocal
from app.models import ProjectDB

PROJECTS = [
    {
        "name": "Slussen – Södra Station ombyggnad",
        "type": "Infrastruktur",
        "description": (
            "Genomgripande ombyggnad av Slussen i Stockholm med ny kollektivtrafikbro, "
            "bussterminaler och torg. Projektet syftar till att skapa ett modernt och "
            "hållbart trafiknav för södra Stockholm."
        ),
        "location": "Slussen, Stockholm",
        "region": "Stockholm",
        "lat": 59.3196, "lng": 18.0715,
        "participants": [
            {"name": "Stockholms stad", "role": "Byggherre", "contact": "stadsbyggnadskontoret@stockholm.se"},
            {"name": "Skanska", "role": "Totalentreprenör", "contact": "info@skanska.se"},
            {"name": "Foster + Partners", "role": "Arkitekt", "contact": ""},
        ],
        "estimated_cost": "6,5 miljarder kr",
        "cost_value_msek": 6500.0,
        "timeline_start": "2013",
        "timeline_end": "2025",
        "status": "Pågående",
        "source_url": "https://vaxer.stockholm/projekt/slussen/",
        "source_name": "Stockholms stad",
        "published_at": datetime(2024, 1, 15),
    },
    {
        "name": "West Link – Västlänken Göteborg",
        "type": "Infrastruktur",
        "description": (
            "Ny tågtunnel under Göteborg som förbinder Olskroken i öster med Almedal i söder "
            "via tre nya stationer: Centralen, Korsvägen och Haga. Kapaciteten för tågtrafik "
            "i regionen fördubblas."
        ),
        "location": "Göteborg",
        "region": "Västra Götaland",
        "lat": 57.7089, "lng": 11.9746,
        "participants": [
            {"name": "Trafikverket", "role": "Byggherre", "contact": "trafikverket@trafikverket.se"},
            {"name": "Skanska", "role": "Generalentreprenör", "contact": "info@skanska.se"},
            {"name": "NCC", "role": "Generalentreprenör", "contact": "info@ncc.se"},
            {"name": "Sweco", "role": "Konstruktör", "contact": "info@sweco.se"},
        ],
        "estimated_cost": "20 miljarder kr",
        "cost_value_msek": 20000.0,
        "timeline_start": "2018",
        "timeline_end": "2026",
        "status": "Pågående",
        "source_url": "https://www.trafikverket.se/vastlanken",
        "source_name": "Trafikverket",
        "published_at": datetime(2024, 2, 10),
    },
    {
        "name": "Nya Karolinska Solna – NKS",
        "type": "Offentligt",
        "description": (
            "Ett av Europas mest moderna universitetssjukhus, uppfört i Solna utanför Stockholm. "
            "Sjukhuset har kapacitet för över 600 vårdplatser och är specialiserat på "
            "svåra och ovanliga sjukdomar."
        ),
        "location": "Solna",
        "region": "Stockholm",
        "lat": 59.3518, "lng": 18.0218,
        "participants": [
            {"name": "Region Stockholm", "role": "Byggherre", "contact": "regionstockholm@sll.se"},
            {"name": "Skanska", "role": "Totalentreprenör", "contact": "info@skanska.se"},
            {"name": "White Arkitekter", "role": "Arkitekt", "contact": "info@white.se"},
        ],
        "estimated_cost": "24 miljarder kr",
        "cost_value_msek": 24000.0,
        "timeline_start": "2010",
        "timeline_end": "2018",
        "status": "Klart",
        "source_url": "https://www.karolinska.se/for-vardgivare/nks/",
        "source_name": "Region Stockholm",
        "published_at": datetime(2024, 3, 1),
    },
    {
        "name": "Bostadsprojekt Råsunda – 1 200 lägenheter",
        "type": "Bostäder",
        "description": (
            "Stadsomvandling av det gamla Råsundastadion-området i Solna. "
            "Totalt 1 200 nya bostadsrätter och hyresrätter i ett nytt blandstadskvarter "
            "med park, handel och service."
        ),
        "location": "Råsunda, Solna",
        "region": "Stockholm",
        "lat": 59.3621, "lng": 18.0001,
        "participants": [
            {"name": "Skanska", "role": "Byggherre", "contact": "bostad@skanska.se"},
            {"name": "Solna stad", "role": "Exploatör", "contact": "stadsbyggnad@solna.se"},
            {"name": "Wingårdhs", "role": "Arkitekt", "contact": "info@wingardhs.se"},
        ],
        "estimated_cost": "3,5 miljarder kr",
        "cost_value_msek": 3500.0,
        "timeline_start": "2020",
        "timeline_end": "2027",
        "status": "Pågående",
        "source_url": "",
        "source_name": "Byggindustrin",
        "published_at": datetime(2024, 4, 5),
    },
    {
        "name": "Nyhamnen – Malmös nya stadsdel",
        "type": "Bostäder",
        "description": (
            "Omvandling av det tidigare hamnområdet Nyhamnen i Malmö till en ny levande stadsdel "
            "med 8 000 bostäder, kontor, hotell och en ny station vid Malmö C. "
            "Projektet löper fram till 2050."
        ),
        "location": "Nyhamnen, Malmö",
        "region": "Skåne",
        "lat": 55.6087, "lng": 13.0006,
        "participants": [
            {"name": "Malmö stad", "role": "Byggherre", "contact": "stadsbyggnad@malmo.se"},
            {"name": "Peab", "role": "Generalentreprenör", "contact": "info@peab.se"},
            {"name": "Henning Larsen", "role": "Arkitekt", "contact": ""},
        ],
        "estimated_cost": "40 miljarder kr",
        "cost_value_msek": 40000.0,
        "timeline_start": "2022",
        "timeline_end": "2050",
        "status": "Pågående",
        "source_url": "https://malmo.se/Stadsplanering--trafik/Stadsplanering--visioner/Utbyggnadsomraden/Nyhamnen.html",
        "source_name": "Malmö stad",
        "published_at": datetime(2024, 1, 20),
    },
    {
        "name": "E4 Förbifart Stockholm",
        "type": "Infrastruktur",
        "description": (
            "En 21 km lång motorväg varav 17 km i tunnel, som avlastar centrala Stockholm "
            "och kopplar samman E4 norr och söder om Mälaren. Projektet är ett av de "
            "största vägprojekten i Sverige."
        ),
        "location": "Stockholm",
        "region": "Stockholm",
        "lat": 59.4021, "lng": 17.8872,
        "participants": [
            {"name": "Trafikverket", "role": "Byggherre", "contact": "forbifart@trafikverket.se"},
            {"name": "Skanska", "role": "Totalentreprenör", "contact": "info@skanska.se"},
            {"name": "NCC", "role": "Totalentreprenör", "contact": "info@ncc.se"},
            {"name": "PEAB", "role": "Underentreprenör", "contact": "info@peab.se"},
        ],
        "estimated_cost": "31 miljarder kr",
        "cost_value_msek": 31000.0,
        "timeline_start": "2015",
        "timeline_end": "2030",
        "status": "Pågående",
        "source_url": "https://www.trafikverket.se/forbifart",
        "source_name": "Trafikverket",
        "published_at": datetime(2024, 2, 28),
    },
    {
        "name": "Kongahälla Köpstad – logistikcenter",
        "type": "Industri",
        "description": (
            "Nytt 60 000 kvm logistik- och industricenter i Kungälv nära E6. "
            "Anläggningen inrymmer lager, distribution och lätta verkstadslokaler "
            "med direkt anslutning till riksvägnätet."
        ),
        "location": "Kungälv",
        "region": "Västra Götaland",
        "lat": 57.8714, "lng": 11.9825,
        "participants": [
            {"name": "Catena", "role": "Fastighetsägare", "contact": "info@catenafastigheter.se"},
            {"name": "Veidekke", "role": "Totalentreprenör", "contact": "info@veidekke.se"},
        ],
        "estimated_cost": "450 mkr",
        "cost_value_msek": 450.0,
        "timeline_start": "2024",
        "timeline_end": "2026",
        "status": "Planerat",
        "source_url": "",
        "source_name": "Fastighetsnytt",
        "published_at": datetime(2024, 5, 10),
    },
    {
        "name": "Kiruna stadsflytt – ny stadskärna",
        "type": "Offentligt",
        "description": (
            "Flytt av hela Kiruna centrum 3 km österut på grund av gruvdrift. "
            "Ny stadskärna byggs med stadsbibliotek, kommunhus, hotell, bostäder "
            "och kommersiella lokaler. Unikt projekt i världsklass."
        ),
        "location": "Kiruna",
        "region": "Norrbotten",
        "lat": 67.8558, "lng": 20.2253,
        "participants": [
            {"name": "LKAB", "role": "Byggherre", "contact": "info@lkab.com"},
            {"name": "Kiruna kommun", "role": "Beställare", "contact": "info@kiruna.se"},
            {"name": "Henning Larsen", "role": "Arkitekt", "contact": ""},
            {"name": "Skanska", "role": "Generalentreprenör", "contact": "info@skanska.se"},
        ],
        "estimated_cost": "3 miljarder kr",
        "cost_value_msek": 3000.0,
        "timeline_start": "2012",
        "timeline_end": "2035",
        "status": "Pågående",
        "source_url": "https://www.kiruna.se/stadsflytten/",
        "source_name": "Kiruna kommun",
        "published_at": datetime(2024, 1, 5),
    },
    {
        "name": "Uppsala Resecentrum – ny stationsbyggnad",
        "type": "Offentligt",
        "description": (
            "Nytt resecentrum i Uppsala med utökat stationsområde, bussterminal och "
            "kommersiella ytor. Projektet syftar till att förbereda Uppsala för "
            "ökad tågtrafik och starka pendlingsflöden."
        ),
        "location": "Uppsala",
        "region": "Uppsala",
        "lat": 59.8588, "lng": 17.6389,
        "participants": [
            {"name": "Jernhusen", "role": "Fastighetsägare", "contact": "info@jernhusen.se"},
            {"name": "Uppsala kommun", "role": "Exploatör", "contact": "stadsbyggnad@uppsala.se"},
            {"name": "NCC", "role": "Generalentreprenör", "contact": "info@ncc.se"},
            {"name": "Sweco", "role": "Arkitekt", "contact": "info@sweco.se"},
        ],
        "estimated_cost": "1,2 miljarder kr",
        "cost_value_msek": 1200.0,
        "timeline_start": "2023",
        "timeline_end": "2028",
        "status": "Planerat",
        "source_url": "",
        "source_name": "Byggindustrin",
        "published_at": datetime(2024, 3, 20),
    },
    {
        "name": "Hyllie Stationsområde – 2 500 bostäder",
        "type": "Bostäder",
        "description": (
            "Nytt stadsområde vid Hyllie station i södra Malmö med 2 500 bostäder, "
            "hotell, kontor och handel. Läget vid Öresundsbron ger direkt "
            "förbindelse till Köpenhamn."
        ),
        "location": "Hyllie, Malmö",
        "region": "Skåne",
        "lat": 55.5618, "lng": 12.9733,
        "participants": [
            {"name": "Malmö stad", "role": "Exploatör", "contact": "stadsbyggnad@malmo.se"},
            {"name": "JM", "role": "Byggherre", "contact": "info@jm.se"},
            {"name": "Bonava", "role": "Byggherre", "contact": "info@bonava.se"},
        ],
        "estimated_cost": "5 miljarder kr",
        "cost_value_msek": 5000.0,
        "timeline_start": "2019",
        "timeline_end": "2030",
        "status": "Pågående",
        "source_url": "https://malmo.se/hyllie",
        "source_name": "Malmö stad",
        "published_at": datetime(2024, 2, 14),
    },
    {
        "name": "Energihamnen – vindkraftspark Göteborg",
        "type": "Industri",
        "description": (
            "Havsbaserad vindkraftspark utanför Göteborgs hamn med upp till 20 turbiner "
            "som producerar förnybar el till industri och hushåll. "
            "En del av Göteborgs klimatstrategi 2030."
        ),
        "location": "Göteborg",
        "region": "Västra Götaland",
        "lat": 57.6741, "lng": 11.8372,
        "participants": [
            {"name": "Göteborgs Energi", "role": "Byggherre", "contact": "info@goteborgenergi.se"},
            {"name": "Vattenfall", "role": "Investerare", "contact": "info@vattenfall.se"},
        ],
        "estimated_cost": "2,8 miljarder kr",
        "cost_value_msek": 2800.0,
        "timeline_start": "2025",
        "timeline_end": "2028",
        "status": "Planerat",
        "source_url": "",
        "source_name": "Byggnyheter",
        "published_at": datetime(2024, 6, 1),
    },
    {
        "name": "Kista Galleria – utbyggnad och renovering",
        "type": "Kommersiellt",
        "description": (
            "Utbyggnad och modernisering av Kista Galleria med 15 000 kvm ny yta "
            "för handel, restaurang och kontorslokaler. Projektet stärker Kista "
            "som Stockholms norra handels- och teknikcentrum."
        ),
        "location": "Kista, Stockholm",
        "region": "Stockholm",
        "lat": 59.4042, "lng": 17.9504,
        "participants": [
            {"name": "Unibail-Rodamco", "role": "Fastighetsägare", "contact": ""},
            {"name": "Peab", "role": "Totalentreprenör", "contact": "info@peab.se"},
            {"name": "Sweco", "role": "Arkitekt", "contact": "info@sweco.se"},
        ],
        "estimated_cost": "800 mkr",
        "cost_value_msek": 800.0,
        "timeline_start": "2024",
        "timeline_end": "2026",
        "status": "Planerat",
        "source_url": "",
        "source_name": "Fastighetsnytt",
        "published_at": datetime(2024, 4, 22),
    },
    {
        "name": "Luleå Science Park – teknikbyggnad",
        "type": "Kommersiellt",
        "description": (
            "Ny 12 000 kvm teknik- och innovationsbyggnad vid Luleå tekniska universitet. "
            "Huset samlar forskning, näringsliv och inkubatorverksamhet under ett tak "
            "med fokus på grön teknik och AI."
        ),
        "location": "Luleå",
        "region": "Norrbotten",
        "lat": 65.6178, "lng": 22.1543,
        "participants": [
            {"name": "Luleå kommun", "role": "Beställare", "contact": "info@lulea.se"},
            {"name": "Serneke", "role": "Totalentreprenör", "contact": "info@serneke.se"},
            {"name": "Luleå tekniska universitet", "role": "Byggherre", "contact": "info@ltu.se"},
        ],
        "estimated_cost": "350 mkr",
        "cost_value_msek": 350.0,
        "timeline_start": "2024",
        "timeline_end": "2027",
        "status": "Planerat",
        "source_url": "",
        "source_name": "Byggindustrin",
        "published_at": datetime(2024, 5, 30),
    },
    {
        "name": "Östra Sala backe – 3 000 bostäder Uppsala",
        "type": "Bostäder",
        "description": (
            "Nytt bostadsområde i östra Uppsala med 3 000 lägenheter i varierande storlekar. "
            "Området planeras med kollektivtrafikfokus, cykelvägar och grönstråk. "
            "Byggs etappvis fram till 2030."
        ),
        "location": "Uppsala",
        "region": "Uppsala",
        "lat": 59.8700, "lng": 17.6790,
        "participants": [
            {"name": "Uppsala kommun", "role": "Exploatör", "contact": "stadsbyggnad@uppsala.se"},
            {"name": "Riksbyggen", "role": "Byggherre", "contact": "info@riksbyggen.se"},
            {"name": "HSB", "role": "Byggherre", "contact": "info@hsb.se"},
            {"name": "JM", "role": "Byggherre", "contact": "info@jm.se"},
        ],
        "estimated_cost": "6 miljarder kr",
        "cost_value_msek": 6000.0,
        "timeline_start": "2018",
        "timeline_end": "2030",
        "status": "Pågående",
        "source_url": "",
        "source_name": "Uppsala kommun",
        "published_at": datetime(2024, 1, 30),
    },
    {
        "name": "Nya gymnasiet Linköping – Berzeliusskolan",
        "type": "Offentligt",
        "description": (
            "Nytt gymnasium i centrala Linköping med plats för 1 200 elever. "
            "Moderna undervisningslokaler, idrottshall och utemiljöer. "
            "Certifieras enligt Miljöbyggnad Silver."
        ),
        "location": "Linköping",
        "region": "Östergötland",
        "lat": 58.4108, "lng": 15.6214,
        "participants": [
            {"name": "Linköpings kommun", "role": "Beställare", "contact": "utbildning@linkoping.se"},
            {"name": "NCC", "role": "Totalentreprenör", "contact": "info@ncc.se"},
            {"name": "Arkitema", "role": "Arkitekt", "contact": "info@arkitema.com"},
        ],
        "estimated_cost": "420 mkr",
        "cost_value_msek": 420.0,
        "timeline_start": "2023",
        "timeline_end": "2026",
        "status": "Pågående",
        "source_url": "",
        "source_name": "Byggindustrin",
        "published_at": datetime(2024, 3, 10),
    },
    # ── Norway ───────────────────────────────────────────────────────────────
    {
        "name": "Fornebubanen – ny T-banelinje Oslo",
        "type": "Infrastruktur",
        "description": (
            "Ny T-banelinje fra Majorstuen til Fornebu med seks nye stasjoner. "
            "Prosjektet er et samarbeid mellom Oslo kommune og Akershus fylkeskommune "
            "og vil betjene 50 000 daglige passasjerer."
        ),
        "location": "Oslo",
        "region": "Oslo",
        "country": "Norge",
        "lat": 59.9139, "lng": 10.7522,
        "participants": [
            {"name": "Ruter AS", "role": "Beställare", "contact": "post@ruter.no"},
            {"name": "Skanska Norge", "role": "Totalentreprenör", "contact": ""},
            {"name": "Norconsult", "role": "Konstruktör", "contact": ""},
        ],
        "estimated_cost": "19 miljarder kr",
        "cost_value_msek": 19000.0,
        "timeline_start": "2022",
        "timeline_end": "2029",
        "status": "Pågående",
        "source_url": "",
        "source_name": "Statsbygg – Nyheter",
        "published_at": datetime(2024, 2, 15),
    },
    {
        "name": "Stavanger universitetssykehus – nybygg",
        "type": "Offentligt",
        "description": (
            "Stort nybygg ved Stavanger universitetssykehus med moderne operasjons- "
            "og intensivavdelinger. Prosjektet skal øke kapasiteten og modernisere "
            "sykehustilbudet for Rogaland-regionen."
        ),
        "location": "Stavanger",
        "region": "Rogaland",
        "country": "Norge",
        "lat": 58.9700, "lng": 5.7331,
        "participants": [
            {"name": "Helse Vest RHF", "role": "Beställare", "contact": ""},
            {"name": "PEAB Norge", "role": "Totalentreprenör", "contact": ""},
            {"name": "Sweco Norge", "role": "Konstruktör", "contact": ""},
        ],
        "estimated_cost": "8 miljarder kr",
        "cost_value_msek": 8000.0,
        "timeline_start": "2023",
        "timeline_end": "2030",
        "status": "Planerat",
        "source_url": "",
        "source_name": "Bygg.no",
        "published_at": datetime(2024, 4, 1),
    },
    {
        "name": "Bergen Bybane – forlengelse til Åsane",
        "type": "Infrastruktur",
        "description": (
            "Forlengelse av Bergens bybane nordover til Åsane bydel. "
            "Prosjektet inkluderer ny tunnel under Bryggen og seks nye stopp. "
            "Vil knytte nordre bydeler tettere til sentrum."
        ),
        "location": "Bergen",
        "region": "Vestland",
        "country": "Norge",
        "lat": 60.3913, "lng": 5.3221,
        "participants": [
            {"name": "Bergen kommune", "role": "Beställare", "contact": ""},
            {"name": "NCC Norge", "role": "Totalentreprenör", "contact": ""},
            {"name": "Rambøll Norge", "role": "Konstruktör", "contact": ""},
        ],
        "estimated_cost": "12 miljarder kr",
        "cost_value_msek": 12000.0,
        "timeline_start": "2026",
        "timeline_end": "2032",
        "status": "Planerat",
        "source_url": "",
        "source_name": "Bygg.no",
        "published_at": datetime(2024, 5, 20),
    },
    # ── Denmark ──────────────────────────────────────────────────────────────
    {
        "name": "Lynetteholm – ny bydel i København",
        "type": "Bostäder",
        "description": (
            "Lynetteholm er et nyt kunstigt ø-projekt i Københavns havn med plads til "
            "35 000 boliger og 35 000 arbejdspladser. Projektet inkluderer en ny metro "
            "og vejforbindelser og skal aflaste den eksisterende by."
        ),
        "location": "København",
        "region": "Hovedstaden",
        "country": "Danmark",
        "lat": 55.6900, "lng": 12.6100,
        "participants": [
            {"name": "By & Havn", "role": "Byggherre", "contact": ""},
            {"name": "MT Højgaard", "role": "Totalentreprenör", "contact": ""},
            {"name": "Rambøll Danmark", "role": "Konstruktör", "contact": ""},
        ],
        "estimated_cost": "90 miljarder kr",
        "cost_value_msek": 90000.0,
        "timeline_start": "2025",
        "timeline_end": "2070",
        "status": "Planerat",
        "source_url": "",
        "source_name": "Byggeforum",
        "published_at": datetime(2024, 1, 10),
    },
    {
        "name": "Aarhus Letbane – etape 2 forlængelse",
        "type": "Infrastruktur",
        "description": (
            "Forlængelse af Aarhus Letbane med nye linjeføringer mod nord og syd. "
            "Projektet skal øge den kollektive trafik og reducere CO2-udledning "
            "i Østjylland med 15 000 passagerer dagligt."
        ),
        "location": "Aarhus",
        "region": "Midtjylland",
        "country": "Danmark",
        "lat": 56.1629, "lng": 10.2039,
        "participants": [
            {"name": "Midttrafik", "role": "Beställare", "contact": ""},
            {"name": "Aarsleff", "role": "Totalentreprenör", "contact": ""},
            {"name": "COWI Danmark", "role": "Konstruktör", "contact": ""},
        ],
        "estimated_cost": "4,2 miljarder kr",
        "cost_value_msek": 4200.0,
        "timeline_start": "2025",
        "timeline_end": "2030",
        "status": "Planerat",
        "source_url": "",
        "source_name": "Vejdirektoratet – Nyheder",
        "published_at": datetime(2024, 6, 5),
    },
    {
        "name": "Odense Universitetshospital – nyt OUH",
        "type": "Offentligt",
        "description": (
            "Nyt Odense Universitetshospital er et af de største byggeprojekter i "
            "dansk hospitalhistorie. Det nye supersygehus skal samle speciallæger "
            "og avanceret medicinsk udstyr under ét tag."
        ),
        "location": "Odense",
        "region": "Syddanmark",
        "country": "Danmark",
        "lat": 55.3800, "lng": 10.3600,
        "participants": [
            {"name": "Region Syddanmark", "role": "Beställare", "contact": ""},
            {"name": "Skanska Danmark", "role": "Totalentreprenör", "contact": ""},
            {"name": "Henning Larsen Architects", "role": "Arkitekt", "contact": ""},
        ],
        "estimated_cost": "11,5 miljarder kr",
        "cost_value_msek": 11500.0,
        "timeline_start": "2020",
        "timeline_end": "2027",
        "status": "Pågående",
        "source_url": "",
        "source_name": "Byggeforum",
        "published_at": datetime(2024, 2, 28),
    },
]


async def seed():
    await init_db()
    async with SessionLocal() as db:
        from sqlalchemy import select
        from app.models import ProjectDB
        added = 0
        for p in PROJECTS:
            # Upsert by name — skip if already exists
            existing = await db.scalar(select(ProjectDB).where(ProjectDB.name == p["name"]))
            if existing:
                continue
            db.add(ProjectDB(**p))
            added += 1
        await db.commit()
        if added:
            print(f"Seeded {added} new projects.")
        else:
            print("All seed projects already exist — nothing added.")


if __name__ == "__main__":
    asyncio.run(seed())
