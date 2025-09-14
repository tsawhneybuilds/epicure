#!/usr/bin/env python3
"""
Script to add lat/lng coordinates to all restaurants in the mock data
"""

import re

# NYC coordinates for different areas
coordinates = [
    (40.7580, -73.9855),  # Times Square area
    (40.6782, -73.9442),  # Brooklyn
    (40.7282, -73.7949),  # Queens
    (40.7505, -73.9934),  # Chelsea
    (40.7614, -73.9776),  # Midtown East
    (40.7505, -73.9934),  # Chelsea
    (40.7614, -73.9776),  # Midtown East
    (40.7505, -73.9934),  # Chelsea
    (40.7614, -73.9776),  # Midtown East
    (40.7505, -73.9934),  # Chelsea
]

# Read the file
with open('app/services/menu_item_service.py', 'r') as f:
    content = f.read()

# Find all restaurant addresses and add coordinates
address_pattern = r'address="([^"]+)",'
addresses = re.findall(address_pattern, content)

print(f"Found {len(addresses)} restaurant addresses")

# Replace each address with address + coordinates
for i, address in enumerate(addresses):
    if i < len(coordinates):
        lat, lng = coordinates[i]
        old_pattern = f'address="{address}",'
        new_pattern = f'address="{address}",\n                    lat={lat},\n                    lng={lng},'
        content = content.replace(old_pattern, new_pattern, 1)
        print(f"Updated {address} with coordinates {lat}, {lng}")

# Write the updated content back
with open('app/services/menu_item_service.py', 'w') as f:
    f.write(content)

print("✅ All restaurant coordinates added!")
