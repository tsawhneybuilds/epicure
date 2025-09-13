"""Discover venues in SoHo via Overpass and save to data/osm_raw.json."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from soho_harvest import osm, logging_setup

logging_setup.setup_logging()

DATA = Path('data/osm_raw.json')


async def main() -> None:
    res = await osm.discover()
    DATA.write_text(json.dumps(res, indent=2))
    print(f"wrote {DATA}")

if __name__ == '__main__':
    asyncio.run(main())
