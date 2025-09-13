"""Robots.txt utilities."""
from __future__ import annotations

import asyncio
from functools import lru_cache
from urllib.parse import urlparse

import httpx
from robotexclusionrulesparser import RobotExclusionRulesParser

from .config import connect_timeout, read_timeout


@lru_cache(maxsize=128)
async def fetch_robots(host: str) -> RobotExclusionRulesParser:
    url = f"https://{host}/robots.txt"
    parser = RobotExclusionRulesParser()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(connect_timeout, read=read_timeout)) as client:
            r = await client.get(url)
            if r.status_code < 400:
                parser.parse(r.text)
    except Exception:
        pass
    return parser


async def allowed(url: str, user_agent: str = "*") -> bool:
    parsed = urlparse(url)
    parser = await fetch_robots(parsed.netloc)
    return parser.is_allowed(user_agent, parsed.path or "/")
