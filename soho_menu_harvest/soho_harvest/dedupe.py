"""Deduplication helpers."""
from __future__ import annotations

from typing import Iterable, List

from rapidfuzz import fuzz

from .models import MenuItem, Restaurant


def dedupe_items(items: List[MenuItem]) -> List[MenuItem]:
    seen = set()
    out: List[MenuItem] = []
    for item in items:
        key = (item.section or "", item.name.lower())
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def restaurant_match(r1: Restaurant, r2: Restaurant) -> bool:
    return fuzz.token_sort_ratio(r1.name, r2.name) >= 85 and ((r1.lat-r2.lat)**2 + (r1.lng-r2.lng)**2)**0.5*111000 <= 60
