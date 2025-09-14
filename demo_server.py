#!/usr/bin/env python3
"""
Epicure Demo Server - Uses Real Restaurant Data
Serves the actual restaurant data we collected in a web interface
"""

import json
import csv
import math
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os

# Load the actual restaurant data
def load_restaurant_data():
    """Load the real restaurant data from our harvested files"""
    restaurants = []
    menu_items = []
    
    # Load venues (restaurants)
    venues_file = 'soho_menu_harvest/data/venues_enriched.jsonl'
    if os.path.exists(venues_file):
        with open(venues_file, 'r') as f:
            for line in f:
                if line.strip():
                    venue = json.loads(line)
                    restaurants.append(venue)
    
    # Load menu items
    menu_file = 'soho_menu_harvest/data/menu_items.csv'
    if os.path.exists(menu_file):
        with open(menu_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                menu_items.append(row)
    
    return restaurants, menu_items

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in miles"""
    R = 3959  # Earth's radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_restaurant_menu_items(restaurant_id, menu_items):
    """Get menu items for a specific restaurant"""
    return [item for item in menu_items if item.get('restaurant_id') == restaurant_id]

def transform_restaurant_for_frontend(restaurant, menu_items, user_lat=40.7580, user_lng=-73.9855):
    """Transform backend restaurant data to frontend format"""
    # Calculate distance
    distance = calculate_distance(user_lat, user_lng, restaurant['lat'], restaurant['lng'])
    distance_str = f"{distance:.1f} mi" if distance >= 1 else f"{int(distance * 5280)} ft"
    
    # Get menu items for this restaurant
    restaurant_menu_items = get_restaurant_menu_items(restaurant['id'], menu_items)
    
    # Calculate average price and infer cuisine
    avg_price = 0
    cuisine_keywords = []
    if restaurant_menu_items:
        prices = [float(item.get('price', 0)) for item in restaurant_menu_items if item.get('price')]
        avg_price = sum(prices) / len(prices) if prices else 0
        
        # Infer cuisine from menu items
        all_text = ' '.join([item.get('name', '') + ' ' + item.get('description', '') 
                            for item in restaurant_menu_items[:10]])
        cuisine_keywords = all_text.lower()
    
    # Determine price level
    if avg_price < 15:
        price_level = "$"
    elif avg_price < 30:
        price_level = "$$"
    elif avg_price < 50:
        price_level = "$$$"
    else:
        price_level = "$$$$"
    
    # Infer cuisine type
    cuisine = "Contemporary"
    if any(word in cuisine_keywords for word in ['pizza', 'pasta', 'italian']):
        cuisine = "Italian"
    elif any(word in cuisine_keywords for word in ['sushi', 'ramen', 'asian', 'japanese']):
        cuisine = "Asian"
    elif any(word in cuisine_keywords for word in ['taco', 'burrito', 'mexican']):
        cuisine = "Mexican"
    elif any(word in cuisine_keywords for word in ['burger', 'fries', 'american']):
        cuisine = "American"
    elif any(word in cuisine_keywords for word in ['croissant', 'french', 'baguette']):
        cuisine = "French"
    
    # Generate highlights
    highlights = []
    if restaurant.get('google_rating', 0) > 4.5:
        highlights.append("Highly rated")
    if any('vegan' in item.get('allergens', '').lower() for item in restaurant_menu_items):
        highlights.append("Vegan options")
    if any('gluten-free' in item.get('allergens', '').lower() for item in restaurant_menu_items):
        highlights.append("Gluten-free")
    if avg_price < 20:
        highlights.append("Budget-friendly")
    if len(restaurant_menu_items) > 20:
        highlights.append("Extensive menu")
    
    return {
        'id': restaurant['id'],
        'name': restaurant['name'],
        'cuisine': cuisine,
        'image': f"https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=300&fit=crop&crop=center",  # Placeholder
        'distance': distance_str,
        'price': price_level,
        'rating': restaurant.get('google_rating', restaurant.get('yelp', {}).get('rating', 4.0)) or 4.0,
        'waitTime': f"{5 + len(restaurant['name']) % 15} min",  # Mock wait time
        'calories': 450 + len(restaurant['name']) % 200,  # Mock calories
        'protein': 25 + len(restaurant['name']) % 20,  # Mock protein
        'carbs': 35 + len(restaurant['name']) % 25,  # Mock carbs
        'fat': 15 + len(restaurant['name']) % 15,  # Mock fat
        'dietary': ['Vegetarian'] if 'vegan' in cuisine_keywords else [],
        'highlights': highlights[:3],
        'address': f"{restaurant['lat']:.4f}, {restaurant['lng']:.4f}",
        'phone': restaurant.get('phone', 'N/A'),
        'website': restaurant.get('website', ''),
        'menu_items_count': len(restaurant_menu_items)
    }

class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        if path == '/':
            self.serve_homepage()
        elif path == '/api/restaurants':
            self.serve_restaurants_api(query_params)
        elif path == '/api/stats':
            self.serve_stats_api()
        else:
            self.send_error(404)
    
    def serve_homepage(self):
        """Serve the main demo page"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Epicure Demo - Real Restaurant Data</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white; 
            padding: 40px; 
            text-align: center; 
        }
        .header h1 { font-size: 3em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            padding: 40px; 
            background: #f8f9fa;
        }
        .stat-card { 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            text-align: center; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .stat-number { 
            font-size: 2.5em; 
            font-weight: bold; 
            color: #ff6b6b; 
            margin-bottom: 10px; 
        }
        .restaurants { 
            padding: 40px; 
        }
        .restaurant-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); 
            gap: 30px; 
            margin-top: 30px; 
        }
        .restaurant-card { 
            background: white; 
            border-radius: 20px; 
            overflow: hidden; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .restaurant-card:hover { 
            transform: translateY(-5px); 
        }
        .restaurant-image { 
            height: 200px; 
            background: linear-gradient(45deg, #ff9a9e, #fecfef);
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: white; 
            font-size: 1.2em; 
            font-weight: bold; 
        }
        .restaurant-info { 
            padding: 25px; 
        }
        .restaurant-name { 
            font-size: 1.4em; 
            font-weight: bold; 
            margin-bottom: 5px; 
            color: #2c3e50; 
        }
        .restaurant-cuisine { 
            color: #7f8c8d; 
            margin-bottom: 15px; 
        }
        .restaurant-details { 
            display: flex; 
            justify-content: space-between; 
            margin-bottom: 15px; 
            font-size: 0.9em; 
        }
        .restaurant-highlights { 
            display: flex; 
            flex-wrap: wrap; 
            gap: 8px; 
        }
        .highlight { 
            background: #e3f2fd; 
            color: #1976d2; 
            padding: 4px 12px; 
            border-radius: 20px; 
            font-size: 0.8em; 
        }
        .loading { 
            text-align: center; 
            padding: 40px; 
            color: #7f8c8d; 
        }
        .controls { 
            padding: 20px 40px; 
            background: #f8f9fa; 
            border-top: 1px solid #e9ecef; 
        }
        .btn { 
            background: #ff6b6b; 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 1em; 
            margin-right: 10px; 
        }
        .btn:hover { 
            background: #ee5a24; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍽️ Epicure Demo</h1>
            <p>Real Restaurant Data from SoHo, NoHo, Nolita, Little Italy & Chinatown</p>
        </div>
        
        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-number" id="restaurant-count">-</div>
                <div>Restaurants</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="menu-items-count">-</div>
                <div>Menu Items</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="neighborhoods-count">5</div>
                <div>Neighborhoods</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="cuisines-count">-</div>
                <div>Cuisine Types</div>
            </div>
        </div>
        
        <div class="restaurants">
            <h2 style="margin-bottom: 20px; color: #2c3e50;">Featured Restaurants</h2>
            <div class="restaurant-grid" id="restaurant-grid">
                <div class="loading">Loading restaurants...</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="loadRestaurants()">🔄 Refresh Data</button>
            <button class="btn" onclick="showStats()">📊 Show Stats</button>
            <button class="btn" onclick="window.open('https://github.com/tsawhneybuilds/epicure', '_blank')">🔗 View Code</button>
        </div>
    </div>

    <script>
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                document.getElementById('restaurant-count').textContent = stats.restaurants;
                document.getElementById('menu-items-count').textContent = stats.menu_items;
                document.getElementById('cuisines-count').textContent = stats.cuisines;
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        async function loadRestaurants() {
            const grid = document.getElementById('restaurant-grid');
            grid.innerHTML = '<div class="loading">Loading restaurants...</div>';
            
            try {
                const response = await fetch('/api/restaurants?limit=12');
                const restaurants = await response.json();
                
                grid.innerHTML = restaurants.map(restaurant => `
                    <div class="restaurant-card">
                        <div class="restaurant-image">
                            📍 ${restaurant.name}
                        </div>
                        <div class="restaurant-info">
                            <div class="restaurant-name">${restaurant.name}</div>
                            <div class="restaurant-cuisine">${restaurant.cuisine} • ${restaurant.menu_items_count} items</div>
                            <div class="restaurant-details">
                                <span>⭐ ${restaurant.rating.toFixed(1)}</span>
                                <span>${restaurant.price}</span>
                                <span>📍 ${restaurant.distance}</span>
                                <span>⏱️ ${restaurant.waitTime}</span>
                            </div>
                            <div class="restaurant-highlights">
                                ${restaurant.highlights.map(h => `<span class="highlight">${h}</span>`).join('')}
                            </div>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                grid.innerHTML = '<div class="loading">Error loading restaurants. Please try again.</div>';
                console.error('Error loading restaurants:', error);
            }
        }
        
        function showStats() {
            alert(`Epicure Data Summary:
            
🏪 Restaurants: ${document.getElementById('restaurant-count').textContent}
🍽️ Menu Items: ${document.getElementById('menu-items-count').textContent}
🌆 Neighborhoods: SoHo, NoHo, Nolita, Little Italy, Chinatown
🍕 Cuisine Types: ${document.getElementById('cuisines-count').textContent}

This demo shows real data collected from restaurant websites in NYC!`);
        }
        
        // Load data on page load
        loadStats();
        loadRestaurants();
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_restaurants_api(self, query_params):
        """Serve restaurant data as JSON API"""
        limit = int(query_params.get('limit', [20])[0])
        
        restaurants, menu_items = load_restaurant_data()
        
        # Transform restaurants for frontend
        transformed_restaurants = []
        for restaurant in restaurants[:limit]:
            transformed = transform_restaurant_for_frontend(restaurant, menu_items)
            transformed_restaurants.append(transformed)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(transformed_restaurants).encode())
    
    def serve_stats_api(self):
        """Serve statistics about the data"""
        restaurants, menu_items = load_restaurant_data()
        
        # Count unique cuisines
        cuisines = set()
        for restaurant in restaurants:
            restaurant_menu_items = get_restaurant_menu_items(restaurant['id'], menu_items)
            if restaurant_menu_items:
                all_text = ' '.join([item.get('name', '') + ' ' + item.get('description', '') 
                                   for item in restaurant_menu_items[:10]]).lower()
                if any(word in all_text for word in ['pizza', 'pasta', 'italian']):
                    cuisines.add('Italian')
                elif any(word in all_text for word in ['sushi', 'ramen', 'asian', 'japanese']):
                    cuisines.add('Asian')
                elif any(word in all_text for word in ['taco', 'burrito', 'mexican']):
                    cuisines.add('Mexican')
                elif any(word in all_text for word in ['burger', 'fries', 'american']):
                    cuisines.add('American')
                elif any(word in all_text for word in ['croissant', 'french', 'baguette']):
                    cuisines.add('French')
                else:
                    cuisines.add('Contemporary')
        
        stats = {
            'restaurants': len(restaurants),
            'menu_items': len(menu_items),
            'cuisines': len(cuisines),
            'neighborhoods': 5
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(stats).encode())

def main():
    """Start the demo server"""
    print("🍽️ Starting Epicure Demo Server...")
    print("📊 Loading real restaurant data...")
    
    # Load data to verify it exists
    restaurants, menu_items = load_restaurant_data()
    print(f"✅ Loaded {len(restaurants)} restaurants and {len(menu_items)} menu items")
    
    if not restaurants:
        print("❌ No restaurant data found! Make sure the data files exist.")
        return
    
    # Start server
    server = HTTPServer(('localhost', 8081), DemoHandler)
    print("🚀 Demo server running at: http://localhost:8081")
    print("📱 Open your browser and visit the URL above to see the demo!")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Demo server stopped. Thanks for trying Epicure!")
        server.shutdown()

if __name__ == '__main__':
    main()
