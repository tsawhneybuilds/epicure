"""
Restaurant API schemas for requests and responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.models.restaurant import FrontendRestaurant

class RestaurantSearchRequest(BaseModel):
    """Request schema for restaurant search"""
    query: Optional[str] = None
    location: Dict[str, float]  # {"lat": 40.7580, "lng": -73.9855}
    filters: Optional[Dict[str, Any]] = None
    user_context: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 20

class RestaurantSearchResponse(BaseModel):
    """Response schema for restaurant search"""
    restaurants: List[FrontendRestaurant]
    meta: Dict[str, Any]

class RestaurantFilters(BaseModel):
    """Available filters for restaurant search"""
    max_price: Optional[int] = None  # 1-4
    max_distance_miles: Optional[float] = None
    dietary_restrictions: Optional[List[str]] = None
    max_calories: Optional[int] = None
    min_protein: Optional[int] = None
    cuisine_types: Optional[List[str]] = None
    max_wait_time: Optional[int] = None

class LocationRequest(BaseModel):
    """Location coordinates"""
    lat: float
    lng: float

class RestaurantStatsResponse(BaseModel):
    """Statistics about restaurants in database"""
    restaurants: int
    menu_items: int
    cuisines: int
    neighborhoods: int

class NearbyRestaurantsRequest(BaseModel):
    """Request for nearby restaurants"""
    location: LocationRequest
    radius_miles: Optional[float] = 2.0
    limit: Optional[int] = 50
