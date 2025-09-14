"""Enhanced restaurant enrichment using Google Places API."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import httpx

from soho_harvest import logging_setup

logging_setup.setup_logging()

VENUES_FILE = Path('data/venues.jsonl')
ENRICHED_VENUES_FILE = Path('data/venues_google_enriched.jsonl')


class GooglePlacesEnricher:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_PLACES_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.session = None
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=httpx.Timeout(15.0))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def search_place(self, name: str, lat: float, lng: float) -> Optional[Dict]:
        """Search for a place using Google Places API."""
        if not self.api_key:
            print("No Google Places API key provided. Skipping Google Places enrichment.")
            return None
        
        try:
            # Use Nearby Search to find the place
            url = f"{self.base_url}/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': 100,  # 100 meters
                'type': 'restaurant',
                'keyword': name,
                'key': self.api_key
            }
            
            response = await self.session.get(url, params=params)
            if response.status_code != 200:
                return None
            
            data = response.json()
            if data.get('status') != 'OK' or not data.get('results'):
                return None
            
            # Find the best match
            best_match = None
            best_score = 0
            
            for place in data['results']:
                place_name = place.get('name', '').lower()
                if name.lower() in place_name or place_name in name.lower():
                    # Simple scoring based on name similarity and rating
                    score = place.get('rating', 0) * 10
                    if score > best_score:
                        best_score = score
                        best_match = place
            
            return best_match
            
        except Exception as e:
            print(f"Error searching for {name}: {e}")
            return None
    
    async def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a place."""
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,rating,user_ratings_total,formatted_phone_number,opening_hours,photos,website,url',
                'key': self.api_key
            }
            
            response = await self.session.get(url, params=params)
            if response.status_code != 200:
                return None
            
            data = response.json()
            if data.get('status') != 'OK':
                return None
            
            return data.get('result', {})
            
        except Exception as e:
            print(f"Error getting place details for {place_id}: {e}")
            return None
    
    async def enrich_restaurant(self, restaurant: Dict) -> Dict:
        """Enrich a restaurant with Google Places data."""
        name = restaurant.get('name', '')
        lat = restaurant.get('lat')
        lng = restaurant.get('lng')
        
        if not lat or not lng:
            return restaurant
        
        print(f"Enriching {name} with Google Places...")
        
        # Start with existing data
        enriched = restaurant.copy()
        
        # Search for the place
        place = await self.search_place(name, lat, lng)
        if not place:
            enriched['google_places_found'] = False
            return enriched
        
        # Get detailed information
        place_id = place.get('place_id')
        if place_id:
            details = await self.get_place_details(place_id)
            if details:
                enriched.update({
                    'google_place_id': place_id,
                    'google_rating': details.get('rating'),
                    'google_review_count': details.get('user_ratings_total'),
                    'google_phone': details.get('formatted_phone_number'),
                    'google_website': details.get('website'),
                    'google_place_url': details.get('url'),
                    'google_places_found': True,
                })
                
                # Handle opening hours
                opening_hours = details.get('opening_hours', {})
                if opening_hours:
                    enriched['google_hours'] = {
                        'weekday_text': opening_hours.get('weekday_text', []),
                        'open_now': opening_hours.get('open_now'),
                    }
                
                # Handle photos
                photos = details.get('photos', [])
                if photos:
                    photo_urls = []
                    for photo in photos[:5]:  # Limit to 5 photos
                        photo_ref = photo.get('photo_reference')
                        if photo_ref:
                            photo_url = f"{self.base_url}/photo?maxwidth=400&photoreference={photo_ref}&key={self.api_key}"
                            photo_urls.append(photo_url)
                    enriched['google_photos'] = photo_urls
            else:
                enriched['google_places_found'] = False
        else:
            enriched['google_places_found'] = False
        
        return enriched


async def main():
    """Main function to enrich restaurants with Google Places data."""
    # Load existing venues
    venues = []
    if VENUES_FILE.exists():
        for line in VENUES_FILE.read_text().splitlines():
            if line.strip():
                try:
                    venues.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    print(f"Loaded {len(venues)} restaurants to enrich with Google Places")
    
    # Check for API key
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not api_key:
        print("Warning: No GOOGLE_PLACES_API_KEY found in environment variables.")
        print("To use Google Places API, set your API key:")
        print("export GOOGLE_PLACES_API_KEY='your_api_key_here'")
        print("Continuing with basic enrichment...")
    
    # Enrich restaurants
    enriched_venues = []
    async with GooglePlacesEnricher(api_key) as enricher:
        for i, venue in enumerate(venues):
            try:
                enriched = await enricher.enrich_restaurant(venue)
                enriched_venues.append(enriched)
                
                # Progress update
                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(venues)} restaurants")
                
                # Rate limiting for Google Places API
                await asyncio.sleep(0.1)  # 10 requests per second max
                
            except Exception as e:
                print(f"Error enriching {venue.get('name', 'Unknown')}: {e}")
                enriched_venues.append(venue)  # Keep original data
    
    # Save enriched data
    with ENRICHED_VENUES_FILE.open('w') as f:
        for venue in enriched_venues:
            f.write(json.dumps(venue) + '\n')
    
    print(f"Saved {len(enriched_venues)} enriched restaurants to {ENRICHED_VENUES_FILE}")
    
    # Print summary statistics
    google_found = sum(1 for v in enriched_venues if v.get('google_places_found'))
    ratings_found = sum(1 for v in enriched_venues if v.get('google_rating'))
    phones_found = sum(1 for v in enriched_venues if v.get('google_phone'))
    hours_found = sum(1 for v in enriched_venues if v.get('google_hours'))
    photos_found = sum(1 for v in enriched_venues if v.get('google_photos'))
    
    print(f"\nGoogle Places Enrichment Summary:")
    print(f"- Restaurants found on Google Places: {google_found}")
    print(f"- Restaurants with Google ratings: {ratings_found}")
    print(f"- Restaurants with Google phone numbers: {phones_found}")
    print(f"- Restaurants with Google hours: {hours_found}")
    print(f"- Restaurants with Google photos: {photos_found}")


if __name__ == '__main__':
    asyncio.run(main())
