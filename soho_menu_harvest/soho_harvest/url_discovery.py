"""Discover potential menu URLs for a venue."""
from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse
from typing import List

from bs4 import BeautifulSoup

from .http import fetch
from .robots import allowed

GUESS_PATHS = [
    "/menu","/menus","/our-menu","/food-menu","/lunch","/dinner","/brunch","/order","/order-online"
]

ANCHOR_RE = re.compile(r"(menu|order|our menu|food)", re.I)


async def discover_menu_urls(base_url: str) -> List[str]:
    urls: List[str] = []
    parsed = urlparse(base_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    # guessed paths
    for path in GUESS_PATHS:
        candidate = base + path
        if not await allowed(candidate):
            continue
        try:
            r = await fetch(candidate)
            if r.status_code < 400:
                urls.append(candidate)
        except Exception:
            pass
        if len(urls) >= 2:
            return urls
    # scan homepage
    if await allowed(base_url):
        try:
            r = await fetch(base_url)
            if r.status_code < 400:
                soup = BeautifulSoup(r.text, "lxml")
                for a in soup.find_all("a", href=True):
                    if ANCHOR_RE.search(a.get_text(" ")):
                        href = urljoin(base_url, a["href"])
                        if urlparse(href).netloc == parsed.netloc and href not in urls:
                            urls.append(href)
                    if len(urls) >= 2:
                        break
        except Exception:
            pass
    return urls[:2]
