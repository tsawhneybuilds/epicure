"""Parse JSON-LD menu structures."""
from __future__ import annotations

import rapidjson as json
from bs4 import BeautifulSoup
from typing import List, Tuple

from .models import MenuItem


def _iter_items(data):
    if isinstance(data, dict):
        if data.get("@type") == "MenuItem":
            yield data
        for v in data.values():
            yield from _iter_items(v)
    elif isinstance(data, list):
        for v in data:
            yield from _iter_items(v)


def parse(html: str) -> Tuple[List[MenuItem], float, str]:
    soup = BeautifulSoup(html, "lxml")
    items: List[MenuItem] = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
        except Exception:
            continue
        for obj in _iter_items(data):
            name = obj.get("name")
            if not name:
                continue
            item = MenuItem(
                name=name.strip(),
                description=obj.get("description"),
                price=None,
                currency="USD",
                confidence=0.95,
            )
            offers = obj.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            price = offers.get("price") or offers.get("priceSpecification", {}).get("price")
            if price:
                try:
                    item.price = float(price)
                except Exception:
                    pass
            items.append(item)
    return items, 0.95 if items else 0.0, "jsonld"
