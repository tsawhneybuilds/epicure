"""Load harvested CSVs into Supabase tables."""
from __future__ import annotations

import csv
from pathlib import Path

from soho_harvest.storage import upsert_supabase

DATA_DIR = Path('data')


def load_csv(name: str):
    path = DATA_DIR / name
    with path.open() as f:
        reader = csv.DictReader(f)
        return list(reader)


def main() -> None:
    upsert_supabase('restaurants', load_csv('restaurants.csv'))
    upsert_supabase('menus', load_csv('menus.csv'))
    upsert_supabase('menu_items', load_csv('menu_items.csv'))
    print('uploaded')

if __name__ == '__main__':
    main()
