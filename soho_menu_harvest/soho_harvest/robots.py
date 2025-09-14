"""Robots.txt utilities."""
from __future__ import annotations

import asyncio
from urllib.parse import urlparse

import httpx
from robotexclusionrulesparser import RobotExclusionRulesParser

from .config import connect_timeout, read_timeout

# Simple cache for robots.txt parsers
_robots_cache = {}


async def fetch_robots(host: str) -> RobotExclusionRulesParser:
    if host in _robots_cache:
        return _robots_cache[host]
    
    url = f"https://{host}/robots.txt"
    parser = RobotExclusionRulesParser()
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(connect_timeout, read=read_timeout)) as client:
            r = await client.get(url)
            if r.status_code < 400:
                parser.parse(r.text)
    except Exception:
        pass
    
    _robots_cache[host] = parser
    return parser


async def allowed(url: str, user_agent: str = "*") -> bool:
    parsed = urlparse(url)
    parser = await fetch_robots(parsed.netloc)
    return parser.is_allowed(user_agent, parsed.path or "/")
