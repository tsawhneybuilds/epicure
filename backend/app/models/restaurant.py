"""
Restaurant and Menu Item data models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4
from datetime import datetime

class Restaurant(BaseModel):
    """Database restaurant model"""
    id: UUID4
    name: str
    cuisine: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    price_level: Optional[int] = None  # 1-4
    rating: Optional[float] = None
    review_count: Optional[int] = None
    image_url: Optional[str] = None
    open_hours: Optional[Dict[str, Any]] = None
    delivery_providers: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MenuItem(BaseModel):
    """Database menu item model"""
    id: UUID4
    restaurant_id: UUID4
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    sodium_mg: Optional[int] = None
    sugar_g: Optional[float] = None
    dietary_tags: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class FrontendRestaurant(BaseModel):
    """Restaurant model for frontend consumption (matches frontend interface)"""
    id: str
    name: str
    cuisine: str
    image: str
    distance: str  # e.g., "0.3 mi"
    price: str     # e.g., "$$" 
    rating: float
    waitTime: Optional[str] = None  # e.g., "15 min"
    calories: Optional[int] = None
    protein: Optional[int] = None
    carbs: Optional[int] = None
    fat: Optional[int] = None
    dietary: Optional[List[str]] = None
    highlights: List[str] = []
    address: Optional[str] = None
    phone: Optional[str] = None

class RestaurantWithMenu(BaseModel):
    """Restaurant with associated menu items"""
    restaurant: Restaurant
    menu_items: List[MenuItem]

class RestaurantAnalysis(BaseModel):
    """AI analysis of restaurant/menu"""
    restaurant_id: UUID4
    dietary_tags: Dict[str, Dict[str, Any]]  # tag -> {confidence, reason}
    nutrition_profile: Dict[str, str]
    cooking_methods: List[str]
    allergen_info: Dict[str, List[str]]
    meal_contexts: List[str]
    ingredient_quality: List[str]
    cuisine_influence: List[str]
    analysis_date: datetime
