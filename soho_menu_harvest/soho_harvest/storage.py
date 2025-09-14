"""Storage helpers for CSV and optional Supabase."""
from __future__ import annotations

import csv
import gzip
import json
import os
from pathlib import Path
from typing import Iterable, Optional

from .models import Menu, MenuItem, Restaurant
from .config import snapshot_html as SNAPSHOT_HTML, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_SCHEMA

try:
    from supabase import create_client, Client  # type: ignore
except Exception:  # pragma: no cover
    create_client = None
    Client = None

DATA_DIR = Path("data")
SNAP_DIR = Path("snapshots")
DATA_DIR.mkdir(exist_ok=True)
SNAP_DIR.mkdir(exist_ok=True)


class CSVStore:
    def __init__(self) -> None:
        self.restaurants = open(DATA_DIR / "restaurants.csv", "a", newline="")
        self.menus = open(DATA_DIR / "menus.csv", "a", newline="")
        self.items = open(DATA_DIR / "menu_items.csv", "a", newline="")
        self.rw = csv.writer(self.restaurants)
        self.mw = csv.writer(self.menus)
        self.iw = csv.writer(self.items)
        # headers if file empty
        if self.restaurants.tell() == 0:
            self.rw.writerow([
                "id","name","lat","lng","website","price_level","rating","review_count","source_json","created_at","updated_at",
            ])
        if self.menus.tell() == 0:
            self.mw.writerow(["id","restaurant_id","url","scraped_at","source","version","raw_snapshot_path"])
        if self.items.tell() == 0:
            self.iw.writerow(["id","menu_id","section","name","description","price","currency","tags","allergens","confidence","last_seen"])

    def write_restaurant(self, r: Restaurant) -> None:
        self.rw.writerow([
            r.id,r.name,r.lat,r.lng,r.website,r.price_level,r.rating,r.review_count,json.dumps(r.source),r.created_at,r.updated_at
        ])

    def write_menu(self, m: Menu) -> None:
        self.mw.writerow([m.id,m.restaurant_id,m.url,m.scraped_at,m.source,m.version,m.raw_snapshot_path])

    def write_items(self, items: Iterable[MenuItem]) -> None:
        for it in items:
            self.iw.writerow([
                it.id,it.menu_id,it.section,it.name,it.description,it.price,it.currency,
                "|".join(it.tags),"|".join(it.allergens),it.confidence,it.last_seen
            ])

    def close(self) -> None:
        self.restaurants.close()
        self.menus.close()
        self.items.close()


_supabase_client: Optional["Client"] = None
if SUPABASE_URL and (SUPABASE_ANON_KEY or SUPABASE_SERVICE_ROLE_KEY) and create_client:
    try:  # pragma: no cover
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY)
    except Exception:
        _supabase_client = None


def upsert_supabase(table: str, rows: list[dict]) -> None:
    if not _supabase_client:
        return
    try:
        _supabase_client.table(table).upsert(rows, on_conflict="id").execute()
    except Exception:
        pass


def save_snapshot(host: str, content: bytes, suffix: str) -> str:
    if not SNAPSHOT_HTML:
        return ""
    digest = abs(hash(content)) & 0xFFFFFFFF
    fname = f"{host}_{digest}{suffix}"
    path = SNAP_DIR / fname
    with gzip.open(path, "wb") as f:
        f.write(content)
    return str(path)
