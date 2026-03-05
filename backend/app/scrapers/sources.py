"""
Swedish construction news RSS sources.
Each entry describes a feed and how to classify its projects.
"""

RSS_SOURCES = [
    {
        "name": "Byggindustrin",
        "url": "https://www.byggindustrin.se/feed/",
        "default_type": "Övrigt",
    },
    {
        "name": "Trafikverket",
        "url": "https://www.trafikverket.se/om-oss/press/pressmeddelanden/rss/",
        "default_type": "Infrastruktur",
    },
    {
        "name": "Fastighetsnytt",
        "url": "https://fastighetsnytt.se/feed/",
        "default_type": "Kommersiellt",
    },
    {
        "name": "Byggnyheter",
        "url": "https://byggnyheter.se/rss.xml",
        "default_type": "Övrigt",
    },
    {
        "name": "Upphandlingsmyndigheten",
        "url": "https://www.upphandlingsmyndigheten.se/rss/nyheter",
        "default_type": "Offentligt",
    },
    {
        "name": "Riksbyggen",
        "url": "https://www.riksbyggen.se/feed/",
        "default_type": "Bostäder",
    },
    # ── Additional sources ────────────────────────────────────────────────────
    {
        "name": "Fastighetstidningen",
        "url": "https://fastighetstidningen.se/feed/",
        "default_type": "Kommersiellt",
    },
    {
        "name": "Ny Teknik",
        "url": "https://www.nyteknik.se/rss",
        "default_type": "Övrigt",
    },
    {
        "name": "Samhällsbyggaren",
        "url": "https://samhallsbyggaren.se/feed/",
        "default_type": "Offentligt",
    },
    {
        "name": "Husbyggaren",
        "url": "https://husbyggaren.se/feed/",
        "default_type": "Bostäder",
    },
    {
        "name": "Arkitekten",
        "url": "https://arkitekten.se/feed/",
        "default_type": "Kommersiellt",
    },
    {
        "name": "Boverket",
        "url": "https://www.boverket.se/rss/nyheter/",
        "default_type": "Offentligt",
    },
    {
        "name": "Energifokus",
        "url": "https://energifokus.se/feed/",
        "default_type": "Industri",
    },
    # ── Municipality news feeds (include planning/permit announcements) ────────
    {
        "name": "Stockholms stad – Nyheter",
        "url": "https://www.stockholm.se/OmStockholm/Nyheter/rss/",
        "default_type": "Offentligt",
    },
    {
        "name": "Göteborgs stad – Nyheter",
        "url": "https://goteborg.se/wps/portal/start/om-goteborg/nyheter/rss",
        "default_type": "Offentligt",
    },
    {
        "name": "Malmö stad – Nyheter",
        "url": "https://malmo.se/rss/nyheter.xml",
        "default_type": "Offentligt",
    },
]

# Swedish county (region) name mapping — used to detect region from text
SWEDISH_REGIONS = [
    "Stockholm", "Uppsala", "Södermanland", "Östergötland", "Jönköping",
    "Kronoberg", "Kalmar", "Gotland", "Blekinge", "Skåne", "Halland",
    "Västra Götaland", "Värmland", "Örebro", "Västmanland", "Dalarna",
    "Gävleborg", "Västernorrland", "Jämtland", "Västerbotten", "Norrbotten",
    # Cities also used as region labels
    "Göteborg", "Malmö", "Helsingborg", "Linköping", "Västerås",
    "Örebro", "Norrköping", "Umeå", "Lund", "Gävle", "Borås",
]

# Participant roles to look for in Swedish text
PARTICIPANT_ROLES = {
    "beställare": "Beställare",
    "byggherre": "Byggherre",
    "totalentreprenör": "Totalentreprenör",
    "totalentreprenad": "Totalentreprenör",
    "generalentreprenör": "Generalentreprenör",
    "generalentreprenad": "Generalentreprenör",
    "arkitekt": "Arkitekt",
    "konstruktör": "Konstruktör",
    "projektledare": "Projektledare",
    "projektledning": "Projektledning",
    "underentreprenör": "Underentreprenör",
    "fastighetsägare": "Fastighetsägare",
    "developer": "Exploatör",
    "exploatör": "Exploatör",
    "förvaltare": "Förvaltare",
    "investerare": "Investerare",
}

# Known large Swedish construction companies (for participant extraction)
KNOWN_COMPANIES = [
    "Skanska", "NCC", "PEAB", "JM", "Veidekke", "Besqab", "Bonava",
    "Fabege", "Castellum", "Vasakronan", "Akademiska Hus", "Riksbyggen",
    "HSB", "ByggVesta", "Serneke", "Magnolia", "Balder", "Atrium Ljungberg",
    "Klövern", "Diös", "Wallenstam", "Stena Fastigheter", "Akelius",
    "Wihlborgs", "Catena", "Platzer", "Sagax", "Corem", "Kungsleden",
    "Trafikverket", "Jernhusen", "Tillväxtverket", "Region Stockholm",
    "Stockholms stad", "Göteborgs stad", "Malmö stad",
]

# Keywords used to classify project type
TYPE_KEYWORDS = {
    "Bostäder": [
        "bostäder", "lägenheter", "bostadshus", "hyresrätter", "bostadsrätter",
        "villor", "radhus", "studentbostäder", "LSS-boende", "äldreboende",
        "flerbostadshus", "bostadsområde",
    ],
    "Infrastruktur": [
        "väg", "järnväg", "tunnel", "bro", "viadukt", "motorväg", "tåg",
        "spår", "kollektivtrafik", "hamn", "flygplats", "E4", "E6", "E18",
        "E20", "riksväg", "europaväg", "pendeltåg", "spårväg",
    ],
    "Kommersiellt": [
        "kontor", "handel", "köpcentrum", "hotell", "restaurang", "galleria",
        "affärshus", "kontorsbyggnad", "affärsfastighet",
    ],
    "Offentligt": [
        "sjukhus", "skola", "förskola", "gymnasium", "kulturhus", "bibliotek",
        "idrottshall", "simhall", "stadshus", "kommunhus", "vårdinrättning",
        "resecentrum", "station",
    ],
    "Industri": [
        "industri", "logistik", "lager", "fabrik", "produktion", "verkstad",
        "datacenter", "energi", "vindkraft", "solcell",
    ],
}
