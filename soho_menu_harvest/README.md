# Soho Menu Harvest

Collect official restaurant menus in SoHo, NYC for a small food‑recommendation MVP.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit keys
python scripts/discover_osm.py
python scripts/enrich_yelp.py
python scripts/harvest_menus.py
# optional
python scripts/load_supabase.py
```

## Notes
- Only official restaurant websites are crawled.
- robots.txt and Terms of Service are respected.
- Aggregator pages (Yelp, Google, delivery apps) are skipped.
- HTML snapshots stored in `snapshots/` for debugging.
- Data is for hackathon demonstration purposes only.
