"""
Geocoding Swedish locations using Nominatim (OpenStreetMap).
Rate-limited to 1 req/s per Nominatim ToS.
"""
import asyncio
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

log = logging.getLogger(__name__)

_geocoder = Nominatim(user_agent="sweden-construction-map/1.0")

# Simple in-process cache
_cache: dict[str, tuple[float, float] | None] = {}


async def geocode_location(location: str, region: str = "") -> tuple[float, float] | None:
    """
    Return (lat, lng) for a Swedish location string.
    Tries the full location first, then falls back to just the region.
    Returns None if geocoding fails.
    """
    queries = []
    if location:
        queries.append(f"{location}, Sverige")
    if region and region not in queries:
        queries.append(f"{region}, Sverige")

    for query in queries:
        if query in _cache:
            return _cache[query]

        try:
            result = await asyncio.to_thread(
                _geocoder.geocode, query, country_codes="se", timeout=10
            )
            if result:
                coords = (result.latitude, result.longitude)
                _cache[query] = coords
                return coords
            _cache[query] = None
        except (GeocoderTimedOut, GeocoderServiceError) as exc:
            log.warning("Geocoding failed for %r: %s", query, exc)
            _cache[query] = None

        await asyncio.sleep(1.1)  # Nominatim rate limit

    return None
