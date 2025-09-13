"""Enrich OSM venues with Yelp data and dedupe."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Dict, List

from rapidfuzz import fuzz

from soho_harvest import logging_setup, yelp
from soho_harvest.models import Restaurant
from soho_harvest.dedupe import restaurant_match

logging_setup.setup_logging()

RAW = Path('data/osm_raw.json')
OUT = Path('data/venues.jsonl')


def parse_osm(raw: dict) -> List[Restaurant]:
    out: List[Restaurant] = []
    for el in raw.get('elements', []):
        tags = el.get('tags', {})
        name = tags.get('name')
        if not name:
            continue
        lat = el.get('lat') or el.get('center', {}).get('lat')
        lng = el.get('lon') or el.get('center', {}).get('lon')
        if lat is None or lng is None:
            continue
        website = tags.get('website') or tags.get('contact:website')
        phone = tags.get('phone')
        r = Restaurant(name=name, lat=float(lat), lng=float(lng), website=website, phone=phone, source={'osm_id': el.get('id')})
        out.append(r)
    return out


async def enrich(r: Restaurant) -> None:
    data = await yelp.search(r.lat, r.lng, r.name)
    best = None
    best_score = 0
    for biz in data.get('businesses', []):
        score = fuzz.token_sort_ratio(r.name, biz.get('name', ''))
        if score > best_score:
            best_score = score
            best = biz
    if best and best_score >= 85:
        r.rating = best.get('rating')
        r.review_count = best.get('review_count')
        price = best.get('price')
        if price:
            r.price_level = len(price)
        r.source['yelp_id'] = best.get('id')


async def main() -> None:
    raw = json.loads(RAW.read_text())
    restaurants = parse_osm(raw)
    # dedupe by name+distance
    unique: List[Restaurant] = []
    for r in restaurants:
        if not any(restaurant_match(r, u) for u in unique):
            unique.append(r)
    for r in unique:
        await enrich(r)
    with OUT.open('w') as f:
        for r in unique:
            row = {
                'id': r.id,
                'name': r.name,
                'lat': r.lat,
                'lng': r.lng,
                'website': r.website,
                'yelp': {
                    'id': r.source.get('yelp_id'),
                    'rating': r.rating,
                    'review_count': r.review_count,
                    'price': '$' * r.price_level if r.price_level else None,
                },
            }
            f.write(json.dumps(row) + '\n')
    print(f"wrote {OUT}")

if __name__ == '__main__':
    asyncio.run(main())
