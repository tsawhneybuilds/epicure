"""Async HTTP utilities with throttling."""
from __future__ import annotations

import asyncio
import random
from typing import Dict
from urllib.parse import urlparse

import httpx
from aiolimiter import AsyncLimiter

from .config import USER_AGENTS, connect_timeout, read_timeout, per_host_concurrency

_limiters: Dict[str, AsyncLimiter] = {}


def _limiter(host: str) -> AsyncLimiter:
    if host not in _limiters:
        _limiters[host] = AsyncLimiter(per_host_concurrency, 1)
    return _limiters[host]


async def fetch(url: str) -> httpx.Response:
    parsed = urlparse(url)
    async with _limiter(parsed.netloc):
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        async with httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(connect_timeout, read=read_timeout), follow_redirects=True) as client:
            return await client.get(url)
