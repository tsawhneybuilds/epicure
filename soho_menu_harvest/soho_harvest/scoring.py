"""Basic scoring and cleanup of parsed items."""
from __future__ import annotations

from typing import List

from .models import MenuItem


def clean_price(p: float | None) -> float | None:
    if p is None:
        return None
    if p < 1 or p > 200:
        return None
    return p


def apply(items: List[MenuItem], base_conf: float) -> List[MenuItem]:
    for item in items:
        item.price = clean_price(item.price)
        if not item.price:
            item.confidence = max(0, base_conf - 0.1)
    return items
