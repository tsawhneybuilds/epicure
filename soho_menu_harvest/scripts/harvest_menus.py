"""Crawl websites to extract menus."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from urllib.parse import urlparse

from soho_harvest import logging_setup
from soho_harvest.http import fetch
from soho_harvest.url_discovery import discover_menu_urls
from soho_harvest.robots import allowed
from soho_harvest.parse_jsonld import parse as parse_jsonld
from soho_harvest.parse_cms import parse as parse_cms
from soho_harvest.parse_generic import parse as parse_generic
from soho_harvest.scoring import apply
from soho_harvest.dedupe import dedupe_items
from soho_harvest.storage import CSVStore, save_snapshot
from soho_harvest.models import Menu, MenuItem
from soho_harvest.timer import expired

logging_setup.setup_logging()

VENUES = Path('data/venues.jsonl')


def read_venues():
    for line in VENUES.read_text().splitlines():
        yield json.loads(line)


async def process() -> None:
    store = CSVStore()
    pages_per_host = {}
    total_menus = 0
    total_items = 0
    try:
        for row in read_venues():
            if expired():
                break
            website = row.get('website')
            if not website:
                continue
            host = urlparse(website).netloc
            pages_per_host.setdefault(host, 0)
            if pages_per_host[host] >= 2:
                continue
            urls = await discover_menu_urls(website)
            for url in urls:
                if expired() or pages_per_host[host] >= 2:
                    break
                if not await allowed(url):
                    continue
                try:
                    r = await fetch(url)
                except Exception:
                    continue
                pages_per_host[host] += 1
                html = r.text
                snapshot = save_snapshot(host, r.content, '.html.gz')
                items, conf, source = parse_jsonld(html)
                if not items:
                    items, conf, source = parse_cms(html)
                if not items:
                    items, conf, source = parse_generic(html)
                items = apply(dedupe_items(items), conf)
                if not items:
                    continue
                menu = Menu(restaurant_id=row['id'], url=url, source=source, raw_snapshot_path=snapshot)
                store.write_menu(menu)
                for it in items:
                    it.menu_id = menu.id
                store.write_items(items)
                total_menus += 1
                total_items += len(items)
    finally:
        store.close()
    print(f"menus: {total_menus} items:{total_items}")


if __name__ == '__main__':
    asyncio.run(process())
