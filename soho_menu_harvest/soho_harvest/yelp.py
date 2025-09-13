"""Yelp Fusion API helpers."""
from __future__ import annotations

import httpx
from typing import Any, Dict, List

from .config import YELP_API_KEY, connect_timeout, read_timeout

BASE = "https://api.yelp.com/v3"


async def search(lat: float, lng: float, term: str) -> Dict[str, Any]:
    if not YELP_API_KEY:
        return {}
    params = {
        "latitude": lat,
        "longitude": lng,
        "radius": 900,
        "categories": "restaurants,food,coffee",
        "limit": 20,
        "term": term,
    }
    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}
    async with httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(connect_timeout, read=read_timeout)) as client:
        r = await client.get(f"{BASE}/businesses/search", params=params)
        r.raise_for_status()
        return r.json()
