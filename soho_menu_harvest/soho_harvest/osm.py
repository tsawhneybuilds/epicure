"""Overpass helpers."""
from __future__ import annotations

import json
from typing import Iterable
import httpx

from .config import BBOX, OSM_OVERPASS_URL, connect_timeout, read_timeout


QUERY = (
    "[out:json][timeout:30];("
    "node[\"amenity\"~\"restaurant|fast_food|cafe\"]({min_lat},{min_lng},{max_lat},{max_lng});"
    "way[\"amenity\"~\"restaurant|fast_food|cafe\"]({min_lat},{min_lng},{max_lat},{max_lng});"
    "rel[\"amenity\"~\"restaurant|fast_food|cafe\"]({min_lat},{min_lng},{max_lat},{max_lng});"  # corrected fast_fast -> fast_food
    ");out center tags;"
)


async def discover() -> dict:
    q = QUERY.format(
        min_lat=BBOX.min_lat,
        min_lng=BBOX.min_lng,
        max_lat=BBOX.max_lat,
        max_lng=BBOX.max_lng,
    )
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect_timeout, read=read_timeout)) as client:
        r = await client.post(OSM_OVERPASS_URL, data={"data": q})
        r.raise_for_status()
        return r.json()
