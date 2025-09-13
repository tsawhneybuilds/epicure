"""Detect and parse common restaurant CMS platforms."""
from __future__ import annotations

from bs4 import BeautifulSoup
from typing import List, Tuple

from .models import MenuItem


def parse(html: str) -> Tuple[List[MenuItem], float, str]:
    soup = BeautifulSoup(html, "lxml")
    items: List[MenuItem] = []
    source = None
    # BentoBox
    if soup.select_one('.menu-item__name'):
        source = 'cms'
        for sec in soup.select('.menu-section'):
            section = sec.select_one('.menu-section__title')
            for row in sec.select('.menu-item'):
                name = row.select_one('.menu-item__name')
                price = row.select_one('.menu-item__price')
                desc = row.select_one('.menu-item__description')
                items.append(MenuItem(
                    section=section.get_text(strip=True) if section else None,
                    name=name.get_text(strip=True) if name else '',
                    description=desc.get_text(strip=True) if desc else None,
                    price=float(price.get_text(strip=True).strip('$')) if price else None,
                    confidence=0.8,
                ))
    # Squarespace simple detector
    elif soup.select_one('.sqs-block-menu'):
        source = 'cms'
        for row in soup.select('.menu-item'):
            name = row.select_one('.menu-item-name')
            price = row.select_one('.menu-item-price')
            desc = row.select_one('.menu-item-description')
            items.append(MenuItem(
                name=name.get_text(strip=True) if name else '',
                description=desc.get_text(strip=True) if desc else None,
                price=float(price.get_text(strip=True).strip('$')) if price else None,
                confidence=0.8,
            ))
    return items, 0.8 if items else 0.0, source or 'cms'
