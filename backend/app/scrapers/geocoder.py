"""
Geocoding Swedish locations using a local city/region lookup table.
Falls back to None (frontend handles approximate placement via MapView CITY_COORDS).
No external API calls — instant, no rate-limits.
"""

# Coordinate table for Swedish cities and regions (lat, lng)
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
}


async def geocode_location(location: str, region: str = "") -> tuple[float, float] | None:
    """
    Return (lat, lng) for a Swedish location string via local lookup.
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
