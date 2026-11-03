import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {
    "User-Agent": "WeatherAwareTruckRouting/1.0 (contact: support@weather-truck-router.local)"
}

# In-memory cache for common queries
_GEOCODE_CACHE: Dict[str, List[Dict[str, Any]]] = {}

def geocode_address(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Geocode an address or city query using OpenStreetMap Nominatim.
    """
    clean_query = query.strip()
    if not clean_query:
        return []

    cache_key = f"{clean_query.lower()}:{limit}"
    if cache_key in _GEOCODE_CACHE:
        return _GEOCODE_CACHE[cache_key]

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={
                "q": clean_query,
                "format": "jsonv2",
                "limit": limit,
                "addressdetails": 1,
            },
            headers=HEADERS,
            timeout=5.0,
        )
        if response.status_code == 200:
            data = response.json()
            results = []
            for item in data:
                results.append({
                    "display_name": item.get("display_name", ""),
                    "lat": float(item.get("lat")),
                    "lon": float(item.get("lon")),
                    "type": item.get("type", ""),
                    "importance": item.get("importance", 0.0),
                })
            _GEOCODE_CACHE[cache_key] = results
            return results
    except Exception as e:
        print(f"Geocoding error for '{query}': {e}")
        
    return []
