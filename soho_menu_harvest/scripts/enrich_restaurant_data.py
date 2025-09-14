"""Enrich restaurant data with Google Places, phone numbers, delivery links, and hours."""
from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from soho_harvest import logging_setup

logging_setup.setup_logging()

VENUES_FILE = Path('data/venues.jsonl')
ENRICHED_VENUES_FILE = Path('data/venues_enriched.jsonl')


class RestaurantEnricher:
    def __init__(self):
        self.session = None
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            headers={"User-Agent": self.user_agents[0]},
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    def extract_phone_from_text(self, text: str) -> Optional[str]:
        """Extract phone number from text using regex."""
        # Common phone number patterns
        patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890 or 123-456-7890
            r'\+\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1 (123) 456-7890
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # 123 456 7890
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Clean up the phone number
                phone = re.sub(r'[^\d+]', '', matches[0])
                if len(phone) >= 10:
                    return phone
        return None
    
    def extract_delivery_links(self, html: str, base_url: str) -> Dict[str, str]:
        """Extract DoorDash, Uber Eats, and other delivery links from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        delivery_links = {}
        
        # Common delivery platform patterns
        delivery_patterns = {
            'doordash': ['doordash', 'door-dash'],
            'ubereats': ['ubereats', 'uber-eats', 'uber eats'],
            'grubhub': ['grubhub', 'grub-hub'],
            'seamless': ['seamless'],
            'postmates': ['postmates'],
            'caviar': ['caviar'],
        }
        
        # Look for links
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            text = link.get_text().lower()
            
            for platform, keywords in delivery_patterns.items():
                if any(keyword in href or keyword in text for keyword in keywords):
                    full_url = urljoin(base_url, link['href'])
                    delivery_links[platform] = full_url
                    break
        
        return delivery_links
    
    def extract_hours_from_html(self, html: str) -> Dict[str, str]:
        """Extract operating hours from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        hours = {}
        
        # Common patterns for hours
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_abbrevs = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        
        # Look for hours in various formats
        text = soup.get_text().lower()
        
        # Pattern 1: "Monday: 9:00 AM - 5:00 PM"
        for i, day in enumerate(days):
            pattern = rf'{day}:\s*([^\\n]+)'
            match = re.search(pattern, text)
            if match:
                hours[day_abbrevs[i]] = match.group(1).strip()
        
        # Pattern 2: "Mon-Fri: 9:00 AM - 5:00 PM"
        range_pattern = r'(mon|tue|wed|thu|fri|sat|sun)\s*-\s*(mon|tue|wed|thu|fri|sat|sun):\s*([^\\n]+)'
        match = re.search(range_pattern, text)
        if match:
            start_day, end_day, time_range = match.groups()
            start_idx = day_abbrevs.index(start_day)
            end_idx = day_abbrevs.index(end_day)
            for i in range(start_idx, end_idx + 1):
                hours[day_abbrevs[i]] = time_range.strip()
        
        return hours
    
    async def scrape_restaurant_website(self, restaurant: Dict) -> Dict:
        """Scrape additional data from restaurant website."""
        website = restaurant.get('website')
        if not website:
            return {}
        
        try:
            response = await self.session.get(website)
            if response.status_code != 200:
                return {}
            
            html = response.text
            
            # Extract phone number
            phone = self.extract_phone_from_text(html)
            
            # Extract delivery links
            delivery_links = self.extract_delivery_links(html, website)
            
            # Extract hours
            hours = self.extract_hours_from_html(html)
            
            return {
                'phone': phone,
                'delivery_links': delivery_links,
                'hours': hours,
                'website_scraped': True
            }
            
        except Exception as e:
            print(f"Error scraping {website}: {e}")
            return {'website_scraped': False, 'error': str(e)}
    
    async def search_google_places(self, restaurant: Dict) -> Dict:
        """Search for restaurant on Google Places (simulated - would need API key)."""
        # This is a placeholder for Google Places API integration
        # In a real implementation, you would:
        # 1. Use Google Places API to search for the restaurant
        # 2. Get place_id, rating, review_count, phone, hours, etc.
        # 3. Return the enriched data
        
        name = restaurant.get('name', '')
        lat = restaurant.get('lat')
        lng = restaurant.get('lng')
        
        # For now, return placeholder data
        return {
            'google_place_id': None,
            'google_rating': None,
            'google_review_count': None,
            'google_phone': None,
            'google_hours': None,
            'google_photos': [],
            'google_place_url': f"https://www.google.com/maps/search/{name.replace(' ', '+')}/@{lat},{lng},15z" if lat and lng else None
        }
    
    async def enrich_restaurant(self, restaurant: Dict) -> Dict:
        """Enrich a single restaurant with additional data."""
        print(f"Enriching {restaurant.get('name', 'Unknown')}...")
        
        # Start with existing data
        enriched = restaurant.copy()
        
        # Scrape website data
        website_data = await self.scrape_restaurant_website(restaurant)
        enriched.update(website_data)
        
        # Search Google Places (placeholder)
        google_data = await self.search_google_places(restaurant)
        enriched.update(google_data)
        
        # Add enrichment metadata
        enriched['enriched_at'] = asyncio.get_event_loop().time()
        
        return enriched


async def main():
    """Main function to enrich all restaurant data."""
    # Load existing venues
    venues = []
    if VENUES_FILE.exists():
        for line in VENUES_FILE.read_text().splitlines():
            if line.strip():
                try:
                    venues.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    print(f"Loaded {len(venues)} restaurants to enrich")
    
    # Enrich restaurants
    enriched_venues = []
    async with RestaurantEnricher() as enricher:
        for i, venue in enumerate(venues):
            try:
                enriched = await enricher.enrich_restaurant(venue)
                enriched_venues.append(enriched)
                
                # Progress update
                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(venues)} restaurants")
                
                # Rate limiting - be respectful
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error enriching {venue.get('name', 'Unknown')}: {e}")
                enriched_venues.append(venue)  # Keep original data
    
    # Save enriched data
    with ENRICHED_VENUES_FILE.open('w') as f:
        for venue in enriched_venues:
            f.write(json.dumps(venue) + '\n')
    
    print(f"Saved {len(enriched_venues)} enriched restaurants to {ENRICHED_VENUES_FILE}")
    
    # Print summary statistics
    phones_found = sum(1 for v in enriched_venues if v.get('phone'))
    delivery_links_found = sum(1 for v in enriched_venues if v.get('delivery_links'))
    hours_found = sum(1 for v in enriched_venues if v.get('hours'))
    
    print(f"\nEnrichment Summary:")
    print(f"- Restaurants with phone numbers: {phones_found}")
    print(f"- Restaurants with delivery links: {delivery_links_found}")
    print(f"- Restaurants with hours: {hours_found}")


if __name__ == '__main__':
    asyncio.run(main())
