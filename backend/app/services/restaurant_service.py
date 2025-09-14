"""
Restaurant service with real Supabase and mock implementations
"""

import uuid
import math
import random
from typing import List, Optional, Dict, Any, Tuple
from app.core.config import settings
from app.core.supabase import get_supabase_client
from app.models.restaurant import Restaurant, FrontendRestaurant, MenuItem
from app.schemas.restaurant import RestaurantSearchRequest, RestaurantFilters
import logging

logger = logging.getLogger(__name__)

class RestaurantService:
    """Service for restaurant operations"""
    
    def __init__(self):
        self.use_mock = settings.MOCK_DATA
        if self.use_mock:
            logger.info("Using mock restaurant data")
        
    async def search_restaurants(
        self, 
        request: RestaurantSearchRequest,
        user_id: Optional[str] = None
    ) -> Tuple[List[FrontendRestaurant], Dict[str, Any]]:
        """Search restaurants based on criteria"""
        
        if self.use_mock:
            return await self._mock_search_restaurants(request, user_id)
        else:
            return await self._real_search_restaurants(request, user_id)
    
    async def get_restaurant_by_id(self, restaurant_id: str) -> Optional[Restaurant]:
        """Get restaurant by ID"""
        
        if self.use_mock:
            return await self._mock_get_restaurant(restaurant_id)
        else:
            return await self._real_get_restaurant(restaurant_id)
    
    async def get_nearby_restaurants(
        self, 
        lat: float, 
        lng: float, 
        radius_miles: float = 2.0,
        limit: int = 50
    ) -> List[Restaurant]:
        """Get restaurants within radius"""
        
        if self.use_mock:
            return await self._mock_nearby_restaurants(lat, lng, radius_miles, limit)
        else:
            return await self._real_nearby_restaurants(lat, lng, radius_miles, limit)
    
    async def get_restaurant_stats(self) -> Dict[str, int]:
        """Get statistics about restaurants"""
        
        if self.use_mock:
            return {
                "restaurants": 2000,
                "menu_items": 6039,
                "cuisines": 25,
                "neighborhoods": 5
            }
        else:
            return await self._real_restaurant_stats()
    
    # Mock implementations for parallel development
    async def _mock_search_restaurants(
        self, 
        request: RestaurantSearchRequest,
        user_id: Optional[str] = None
    ) -> Tuple[List[FrontendRestaurant], Dict[str, Any]]:
        """Mock restaurant search for development"""
        
        # Mock restaurant data that matches frontend interface
        mock_restaurants = [
            FrontendRestaurant(
                id='1',
                name='Green Bowl Kitchen',
                cuisine='Healthy Bowls',
                image='https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
                distance='0.3 mi',
                price='$$',
                rating=4.8,
                waitTime='15 min',
                calories=420,
                protein=28,
                carbs=35,
                fat=18,
                dietary=['Vegetarian', 'Gluten-free'],
                highlights=['High protein', 'Fresh ingredients', 'Quick service']
            ),
            FrontendRestaurant(
                id='2',
                name='Muscle Fuel',
                cuisine='Protein-focused',
                image='https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400',
                distance='0.5 mi',
                price='$$$',
                rating=4.6,
                waitTime='10 min',
                calories=580,
                protein=45,
                carbs=22,
                fat=15,
                dietary=['High protein'],
                highlights=['45g protein', 'Keto-friendly', 'Post-workout']
            ),
            FrontendRestaurant(
                id='3',
                name='Zen Garden',
                cuisine='Vegan',
                image='https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400',
                distance='1.2 mi',
                price='$$',
                rating=4.7,
                waitTime='25 min',
                calories=380,
                protein=18,
                carbs=42,
                fat=12,
                dietary=['Vegan', 'Organic'],
                highlights=['Plant-based', 'Organic', 'Low calorie']
            )
        ]
        
        # Apply basic filtering for demo
        filtered = mock_restaurants
        if request.filters:
            if request.filters.get('dietary_restrictions'):
                dietary_filter = request.filters['dietary_restrictions']
                filtered = [r for r in filtered if any(d.lower() in [tag.lower() for tag in r.dietary or []] for d in dietary_filter)]
        
        # Limit results
        limited = filtered[:request.limit or 20]
        
        meta = {
            "total_results": len(filtered),
            "search_time_ms": 120,
            "filters_applied": list(request.filters.keys()) if request.filters else [],
            "personalization_score": 0.87,
            "mock_data": True
        }
        
        return limited, meta
    
    async def _mock_get_restaurant(self, restaurant_id: str) -> Optional[Restaurant]:
        """Mock get restaurant by ID"""
        return Restaurant(
            id=uuid.UUID(restaurant_id) if restaurant_id.count('-') == 4 else uuid.uuid4(),
            name="Mock Restaurant",
            cuisine="Test Cuisine",
            latitude=40.7580,
            longitude=-73.9855,
            rating=4.5,
            price_level=2
        )
    
    async def _mock_nearby_restaurants(
        self, lat: float, lng: float, radius_miles: float, limit: int
    ) -> List[Restaurant]:
        """Mock nearby restaurants"""
        restaurants = []
        for i in range(min(limit, 10)):
            # Generate random nearby coordinates
            lat_offset = random.uniform(-0.01, 0.01)
            lng_offset = random.uniform(-0.01, 0.01)
            
            restaurants.append(Restaurant(
                id=uuid.uuid4(),
                name=f"Mock Restaurant {i+1}",
                cuisine=random.choice(["Italian", "Asian", "American", "Mexican"]),
                latitude=lat + lat_offset,
                longitude=lng + lng_offset,
                rating=round(random.uniform(3.5, 5.0), 1),
                price_level=random.randint(1, 4)
            ))
        
        return restaurants
    
    # Real Supabase implementations
    async def _real_search_restaurants(
        self, 
        request: RestaurantSearchRequest,
        user_id: Optional[str] = None
    ) -> Tuple[List[FrontendRestaurant], Dict[str, Any]]:
        """Real restaurant search using Supabase"""
        
        try:
            supabase = get_supabase_client()
            
            # Build query
            query = supabase.table('restaurants').select('*')
            
            # Apply location filter if provided
            if request.location:
                # Use PostGIS for location queries
                lat, lng = request.location['lat'], request.location['lng']
                radius_meters = 3218.7  # 2 miles in meters (default)
                
                query = query.filter(
                    'location',
                    'dwithin',
                    f'POINT({lng} {lat})',
                    radius_meters
                )
            
            # Apply other filters
            if request.filters:
                if request.filters.get('max_price'):
                    query = query.lte('price_level', request.filters['max_price'])
                
                if request.filters.get('cuisine_types'):
                    query = query.in_('cuisine', request.filters['cuisine_types'])
            
            # Execute query
            response = query.limit(request.limit or 20).execute()
            restaurants = response.data
            
            # Transform to frontend format
            frontend_restaurants = []
            for restaurant in restaurants:
                frontend_restaurant = await self._transform_to_frontend(
                    restaurant, 
                    request.location
                )
                frontend_restaurants.append(frontend_restaurant)
            
            meta = {
                "total_results": len(restaurants),
                "search_time_ms": 150,
                "filters_applied": list(request.filters.keys()) if request.filters else [],
                "personalization_score": 0.85,
                "mock_data": False
            }
            
            return frontend_restaurants, meta
            
        except Exception as e:
            logger.error(f"Restaurant search failed: {e}")
            # Fallback to mock data
            return await self._mock_search_restaurants(request, user_id)
    
    async def _real_get_restaurant(self, restaurant_id: str) -> Optional[Restaurant]:
        """Real get restaurant by ID"""
        try:
            supabase = get_supabase_client()
            response = supabase.table('restaurants').select('*').eq('id', restaurant_id).execute()
            
            if response.data:
                return Restaurant(**response.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Get restaurant failed: {e}")
            return await self._mock_get_restaurant(restaurant_id)
    
    async def _real_nearby_restaurants(
        self, lat: float, lng: float, radius_miles: float, limit: int
    ) -> List[Restaurant]:
        """Real nearby restaurants using PostGIS"""
        try:
            supabase = get_supabase_client()
            radius_meters = radius_miles * 1609.34  # Convert miles to meters
            
            response = supabase.table('restaurants').select('*').filter(
                'location',
                'dwithin',
                f'POINT({lng} {lat})',
                radius_meters
            ).limit(limit).execute()
            
            return [Restaurant(**r) for r in response.data]
            
        except Exception as e:
            logger.error(f"Nearby restaurants query failed: {e}")
            return await self._mock_nearby_restaurants(lat, lng, radius_miles, limit)
    
    async def _real_restaurant_stats(self) -> Dict[str, int]:
        """Real restaurant statistics"""
        try:
            supabase = get_supabase_client()
            
            # Count restaurants
            restaurants_response = supabase.table('restaurants').select('id', count='exact').execute()
            restaurants_count = restaurants_response.count
            
            # Count menu items
            menu_response = supabase.table('menu_items').select('id', count='exact').execute()
            menu_count = menu_response.count
            
            # Count unique cuisines
            cuisines_response = supabase.table('restaurants').select('cuisine', count='exact').execute()
            cuisines_count = len(set(r['cuisine'] for r in cuisines_response.data if r['cuisine']))
            
            return {
                "restaurants": restaurants_count,
                "menu_items": menu_count,
                "cuisines": cuisines_count,
                "neighborhoods": 5  # Hardcoded for now
            }
            
        except Exception as e:
            logger.error(f"Restaurant stats query failed: {e}")
            return {
                "restaurants": 0,
                "menu_items": 0,
                "cuisines": 0,
                "neighborhoods": 0
            }
    
    async def _transform_to_frontend(
        self, 
        restaurant: Dict[str, Any], 
        user_location: Optional[Dict[str, float]] = None
    ) -> FrontendRestaurant:
        """Transform database restaurant to frontend format"""
        
        # Calculate distance if user location provided
        distance_str = "Unknown"
        if user_location and restaurant.get('latitude') and restaurant.get('longitude'):
            distance_miles = self._calculate_distance(
                user_location['lat'], user_location['lng'],
                restaurant['latitude'], restaurant['longitude']
            )
            distance_str = f"{distance_miles:.1f} mi" if distance_miles >= 0.1 else f"{int(distance_miles * 5280)} ft"
        
        # Convert price level to string
        price_map = {1: '$', 2: '$$', 3: '$$$', 4: '$$$$'}
        price_str = price_map.get(restaurant.get('price_level', 2), '$$')
        
        # Generate estimated wait time (simple algorithm)
        wait_time = f"{15 + hash(restaurant['id']) % 20} min"
        
        return FrontendRestaurant(
            id=str(restaurant['id']),
            name=restaurant['name'],
            cuisine=restaurant.get('cuisine', 'Restaurant'),
            image=restaurant.get('image_url', f"https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=300&fit=crop&crop=center&sig={str(restaurant['id'])[:8]}"),
            distance=distance_str,
            price=price_str,
            rating=restaurant.get('rating', 4.0),
            waitTime=wait_time,
            highlights=['Fresh ingredients', 'Popular choice'],  # TODO: Generate from AI analysis
            address=restaurant.get('address'),
            phone=restaurant.get('phone')
        )
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in miles"""
        R = 3959  # Earth's radius in miles
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlng/2) * math.sin(dlng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
