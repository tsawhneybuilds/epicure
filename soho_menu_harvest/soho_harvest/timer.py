"""Global runtime timer."""
from __future__ import annotations

import time
from .config import runtime_minutes

start = time.time()

def expired() -> bool:
    return (time.time() - start) > runtime_minutes * 60
