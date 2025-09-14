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
    
    # Load existing data if it exists
    existing_data = {"elements": []}
    if DATA.exists():
        try:
            existing_data = json.loads(DATA.read_text())
        except json.JSONDecodeError:
            existing_data = {"elements": []}
    
    # Merge new data with existing data
    existing_ids = {el.get('id') for el in existing_data.get('elements', [])}
    new_elements = [el for el in res.get('elements', []) if el.get('id') not in existing_ids]
    
    # Combine elements
    combined_elements = existing_data.get('elements', []) + new_elements
    
    # Update the response with combined elements
    res['elements'] = combined_elements
    res['version'] = 0.6
    res['generator'] = "Overpass API + Soho Menu Harvest"
    
    DATA.write_text(json.dumps(res, indent=2))
    print(f"Added {len(new_elements)} new elements to {DATA} (total: {len(combined_elements)})")

if __name__ == '__main__':
    asyncio.run(main())
