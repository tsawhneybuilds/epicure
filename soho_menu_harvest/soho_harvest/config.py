"""Configuration management for Soho menu harvest."""
from __future__ import annotations

from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class BBox:
    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float


def _getfloat(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, default))
    except ValueError:
        return default

def _getint(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except ValueError:
        return default

BBOX = BBox(
    min_lat=_getfloat("BBOX_MIN_LAT", 40.7180),
    max_lat=_getfloat("BBOX_MAX_LAT", 40.7280),
    min_lng=_getfloat("BBOX_MIN_LNG", -74.0100),
    max_lng=_getfloat("BBOX_MAX_LNG", -73.9960),
)

OSM_OVERPASS_URL = os.getenv("OSM_OVERPASS_URL", "https://overpass-api.de/api/interpreter")
YELP_API_KEY = os.getenv("YELP_API_KEY")

# Crawl controls
global_concurrency = _getint("GLOBAL_CONCURRENCY", 12)
per_host_concurrency = _getint("PER_HOST_CONCURRENCY", 2)
connect_timeout = _getfloat("CONNECT_TIMEOUT_S", 8.0)
read_timeout = _getfloat("READ_TIMEOUT_S", 12.0)
max_pages_per_domain = _getint("MAX_PAGES_PER_DOMAIN", 2)
max_bytes_per_page = _getint("MAX_BYTES_PER_PAGE", 2621440)
runtime_minutes = _getint("RUNTIME_MINUTES", 55)
snapshot_html = bool(int(os.getenv("SNAPSHOT_HTML", "1")))
use_playwright = bool(int(os.getenv("USE_PLAYWRIGHT", "0")))

# Optional Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_SCHEMA = os.getenv("SUPABASE_SCHEMA", "public")

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17 Safari/605.1.15",
]
