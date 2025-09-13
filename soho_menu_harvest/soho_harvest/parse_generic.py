"""Fallback heuristic parser."""
from __future__ import annotations

import re
from bs4 import BeautifulSoup
from typing import List, Tuple

from .models import MenuItem

PRICE_RE = re.compile(r"\$\s?\d{1,2}(\.\d{2})?")


def parse(html: str) -> Tuple[List[MenuItem], float, str]:
    soup = BeautifulSoup(html, "lxml")
    items: List[MenuItem] = []
    for line in soup.select('p, li, div'):
        text = line.get_text(" ", strip=True)
        if not text or len(text) > 120:
            continue
        m = PRICE_RE.search(text)
        if m:
            price_str = m.group().replace('$','').strip()
            try:
                price = float(price_str)
            except Exception:
                price = None
            name = text[:m.start()].strip(' -:\n')
            if name:
                items.append(MenuItem(name=name, price=price, confidence=0.6))
        if len(items) > 50:
            break
    return items, 0.6 if items else 0.0, 'generic'
