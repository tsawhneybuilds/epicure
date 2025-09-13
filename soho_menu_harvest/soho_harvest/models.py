"""Dataclasses representing harvested entities."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import uuid

ISO = "%Y-%m-%dT%H:%M:%SZ"


def now_iso() -> str:
    return datetime.utcnow().strftime(ISO)


@dataclass
class Restaurant:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    lat: float = 0.0
    lng: float = 0.0
    website: Optional[str] = None
    phone: Optional[str] = None
    price_level: Optional[int] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    source: dict = field(default_factory=dict)
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)


@dataclass
class Menu:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    restaurant_id: str = ""
    url: str = ""
    scraped_at: str = field(default_factory=now_iso)
    source: str = "generic"
    version: int = 1
    raw_snapshot_path: Optional[str] = None


@dataclass
class MenuItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    menu_id: str = ""
    section: Optional[str] = None
    name: str = ""
    description: Optional[str] = None
    price: Optional[Decimal] = None
    currency: str = "USD"
    tags: List[str] = field(default_factory=list)
    allergens: List[str] = field(default_factory=list)
    confidence: float = 0.0
    last_seen: str = field(default_factory=now_iso)
