"""
MenuItem data models for the new menu-item focused frontend
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class RestaurantInfo(BaseModel):
    """Restaurant information nested within MenuItem"""
    id: str
    name: str
    cuisine: str
    distance: str
    rating: float
    price_range: str  # $, $$, $$$, $$$$
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    phone: Optional[str] = None


class MenuItem(BaseModel):
    """
    Complete MenuItem model matching frontend_new interface
    """
    id: str
    name: str
    description: str
    image: str
    
    # Restaurant context
    restaurant: RestaurantInfo
    
    # Pricing
    price: float  # Individual item price
    
    # Complete Nutrition Profile
    calories: int
    protein: float
    carbs: float
    fat: float
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None  # in mg
    
    # Dietary & Ingredients
    dietary: List[str] = Field(default_factory=list)  # ['vegan', 'gluten-free', 'keto']
    ingredients: List[str] = Field(default_factory=list)
    allergens: List[str] = Field(default_factory=list)  # ['nuts', 'dairy', 'gluten']
    
    # UI & Metadata
    highlights: List[str] = Field(default_factory=list)  # ['High protein', 'Quick prep']
    category: str  # 'breakfast', 'lunch', 'dinner', 'snack', 'dessert'
    preparation_time: Optional[str] = None  # '15 min', '5-10 min'
    is_popular: Optional[bool] = False
    
    # ML & Search Features
    cuisine_tags: List[str] = Field(default_factory=list)  # ['italian', 'healthy', 'comfort']
    spice_level: Optional[str] = None  # 'mild', 'medium', 'hot'
    meal_time: List[str] = Field(default_factory=list)  # ['breakfast', 'lunch', 'post-workout']
    
    # Availability
    is_available: bool = True
    availability_schedule: Optional[dict] = None  # Time-based availability
    
    # Analytics
    popularity_score: Optional[float] = None
    last_updated: Optional[datetime] = None


class MenuItemSearchRequest(BaseModel):
    """Request model for menu item search"""
    query: Optional[str] = None
    location: dict  # {"lat": float, "lng": float}
    
    filters: Optional[dict] = Field(default_factory=dict)
    # filters can include:
    # - max_calories: int
    # - min_protein: float  
    # - max_price: float
    # - dietary_restrictions: List[str]
    # - categories: List[str]
    # - allergen_free: List[str]
    # - max_prep_time: int (minutes)
    # - spice_level: str
    # - meal_time: str
    
    personalization: Optional[dict] = Field(default_factory=dict)
    # personalization can include:
    # - user_id: str
    # - preferences: dict
    # - context: str ('post_workout', 'late_night', 'quick_lunch')
    # - health_goals: List[str]
    
    sort_by: Optional[str] = "relevance"  # "relevance", "price", "calories", "protein", "rating"
    sort_order: Optional[str] = "desc"  # "asc", "desc"
    limit: Optional[int] = 20
    offset: Optional[int] = 0


class MenuItemSearchResponse(BaseModel):
    """Response model for menu item search"""
    menu_items: List[MenuItem]
    meta: dict
    # meta includes:
    # - total_results: int
    # - search_time_ms: int
    # - personalization_score: float
    # - filters_applied: List[str]
    # - recommendations_reason: str
    # - mock_data: bool


class MenuItemInteraction(BaseModel):
    """Model for tracking user interactions with menu items"""
    user_id: str
    menu_item_id: str
    action: str  # 'like', 'dislike', 'order', 'save', 'view'
    
    # Context
    search_query: Optional[str] = None
    position: Optional[int] = None  # Position in search results
    conversation_context: Optional[dict] = None
    time_spent_viewing: Optional[float] = None  # seconds
    
    # Additional metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = None


class NutritionAnalysis(BaseModel):
    """Model for AI-powered nutrition analysis"""
    menu_item_description: str
    extracted_nutrition: dict
    confidence_scores: dict
    dietary_tags: List[str]
    allergen_warnings: List[str]
    health_insights: List[str]
    
    # AI processing metadata
    model_used: str
    processing_time_ms: int
    extraction_date: datetime = Field(default_factory=datetime.now)
