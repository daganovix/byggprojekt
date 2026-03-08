"""
Geocoding Nordic locations (Sweden, Norway, Denmark) using a local lookup table.
Falls back to None (frontend handles approximate placement via MapView CITY_COORDS).
No external API calls — instant, no rate-limits.
"""

# Coordinate table for Nordic cities and regions (lat, lng)
_CITY_COORDS: dict[str, tuple[float, float]] = {
    "Stockholm":         (59.3326, 18.0649),
    "Göteborg":          (57.7089, 11.9746),
    "Malmö":             (55.6050, 13.0038),
    "Uppsala":           (59.8586, 17.6389),
    "Linköping":         (58.4108, 15.6214),
    "Örebro":            (59.2741, 15.2066),
    "Västerås":          (59.6099, 16.5448),
    "Helsingborg":       (56.0465, 12.6945),
    "Norrköping":        (58.5942, 16.1826),
    "Jönköping":         (57.7826, 14.1618),
    "Umeå":              (63.8258, 20.2630),
    "Lund":              (55.7047, 13.1910),
    "Borås":             (57.7210, 12.9401),
    "Eskilstuna":        (59.3666, 16.5077),
    "Gävle":             (60.6749, 17.1413),
    "Sundsvall":         (62.3908, 17.3069),
    "Halmstad":          (56.6745, 12.8578),
    "Växjö":             (56.8777, 14.8091),
    "Karlstad":          (59.3793, 13.5036),
    "Kristianstad":      (56.0294, 14.1567),
    "Kalmar":            (56.6634, 16.3568),
    "Falun":             (60.6065, 15.6355),
    "Skellefteå":        (64.7507, 20.9528),
    "Luleå":             (65.5848, 22.1547),
    "Östersund":         (63.1792, 14.6357),
    "Södertälje":        (59.1955, 17.6253),
    "Nacka":             (59.3085, 18.1631),
    "Täby":              (59.4440, 18.0689),
    "Huddinge":          (59.2367, 17.9808),
    "Botkyrka":          (59.2000, 17.8310),
    "Sollentuna":        (59.4279, 17.9503),
    "Järfälla":          (59.4327, 17.8322),
    "Upplands Väsby":    (59.5197, 17.9130),
    "Haninge":           (59.1652, 18.1560),
    "Tyresö":            (59.2442, 18.2286),
    "Lidingö":           (59.3639, 18.1539),
    "Solna":             (59.3598, 17.9979),
    "Sundbyberg":        (59.3620, 17.9713),
    "Danderyd":          (59.4000, 18.0328),
    "Vallentuna":        (59.5344, 18.0779),
    "Kiruna":            (67.8558, 20.2253),
    "Piteå":             (65.3172, 21.4791),
    "Boden":             (65.8250, 21.6896),
    "Gällivare":         (67.1333, 20.6500),
    "Haparanda":         (65.8333, 24.1333),
    "Skövde":            (58.3903, 13.8450),
    "Trollhättan":       (58.2836, 12.2886),
    "Mölndal":           (57.6558, 12.0136),
    "Kungsbacka":        (57.4896, 12.0764),
    "Varberg":           (57.1059, 12.2506),
    "Uddevalla":         (58.3489, 11.9388),
    # Regions
    "Västra Götaland":   (57.7089, 11.9746),
    "Skåne":             (55.9897, 13.5958),
    "Östergötland":      (58.4108, 15.6214),
    "Södermanland":      (59.1833, 17.4000),
    "Västmanland":       (59.6099, 16.5448),
    "Dalarna":           (60.6065, 15.6355),
    "Halland":           (56.6745, 12.8578),
    "Jämtland":          (63.1792, 14.6357),
    "Norrbotten":        (65.5848, 22.1547),
    "Västerbotten":      (63.8258, 20.2630),
    "Gävleborg":         (60.6749, 17.1413),
    "Västernorrland":    (62.3908, 17.3069),
    "Värmland":          (59.3793, 13.5036),
    "Kronoberg":         (56.8777, 14.8091),
    "Blekinge":          (56.1667, 15.5833),
    "Gotland":           (57.4684, 18.4867),
    "Uppland":           (59.8586, 17.6389),

    # ── Norway ───────────────────────────────────────────────────────────────
    "Oslo":              (59.9139, 10.7522),
    "Bergen":            (60.3913, 5.3221),
    "Trondheim":         (63.4305, 10.3951),
    "Stavanger":         (58.9700, 5.7331),
    "Tromsø":            (69.6489, 18.9551),
    "Drammen":           (59.7440, 10.2045),
    "Fredrikstad":       (59.2181, 10.9298),
    "Kristiansand":      (58.1467, 7.9956),
    "Sandnes":           (58.8520, 5.7353),
    "Sarpsborg":         (59.2836, 11.1097),
    "Skien":             (59.2082, 9.5536),
    "Ålesund":           (62.4721, 6.1549),
    "Bodø":              (67.2804, 14.4049),
    "Hamar":             (60.7945, 11.0679),
    "Lillestrøm":        (59.9553, 11.0530),
    "Asker":             (59.8340, 10.4390),
    "Bærum":             (59.8940, 10.5290),
    # Norwegian regions (fylker)
    "Viken":             (59.9139, 10.7522),
    "Innlandet":         (61.1172, 10.4669),
    "Vestfold og Telemark": (59.4500, 9.4000),
    "Agder":             (58.3000, 7.9000),
    "Rogaland":          (59.1489, 6.0144),
    "Vestland":          (60.3913, 5.3221),
    "Møre og Romsdal":   (62.7222, 7.0104),
    "Trøndelag":         (63.4305, 10.3951),
    "Nordland":          (67.2804, 14.4049),
    "Troms og Finnmark": (69.6489, 18.9551),

    # ── Denmark ──────────────────────────────────────────────────────────────
    "København":         (55.6761, 12.5683),
    "Aarhus":            (56.1629, 10.2039),
    "Odense":            (55.4038, 10.4024),
    "Aalborg":           (57.0488, 9.9217),
    "Esbjerg":           (55.4667, 8.4500),
    "Randers":           (56.4607, 10.0363),
    "Kolding":           (55.4904, 9.4722),
    "Horsens":           (55.8607, 9.8448),
    "Vejle":             (55.7093, 9.5360),
    "Roskilde":          (55.6415, 12.0803),
    "Helsingør":         (56.0370, 12.6136),
    "Silkeborg":         (56.1716, 9.5484),
    "Næstved":           (55.2292, 11.7612),
    "Fredericia":        (55.5640, 9.7530),
    "Viborg":            (56.4520, 9.4023),
    # Danish regions
    "Hovedstaden":       (55.7500, 12.3500),
    "Sjælland":          (55.4000, 11.8000),
    "Syddanmark":        (55.3600, 9.9000),
    "Midtjylland":       (56.3000, 9.5000),
    "Nordjylland":       (57.0500, 9.9200),
    "Cope":              (55.6761, 12.5683),  # short alias
}


async def geocode_location(location: str, region: str = "") -> tuple[float, float] | None:
    """
    Return (lat, lng) for a Nordic location string via local lookup.
    Tries exact match, then partial match against location and region.
    Returns None if unknown — frontend handles fallback placement.
    """
    for text in [location, region]:
        if not text:
            continue
        # Exact match
        if text in _CITY_COORDS:
            return _CITY_COORDS[text]
        # Partial: a known city name appears inside the location string
        for city, coords in _CITY_COORDS.items():
            if city.lower() in text.lower():
                return coords
    return None
