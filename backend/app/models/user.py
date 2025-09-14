"""
User and Profile data models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4, EmailStr
from datetime import datetime

class User(BaseModel):
    """Database user model"""
    id: UUID4
    email: Optional[EmailStr] = None
    apple_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserProfile(BaseModel):
    """Database user profile model"""
    user_id: UUID4
    age: Optional[int] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    goals: Optional[List[str]] = None
    budget_usd_per_meal: Optional[float] = None
    max_walk_time_minutes: Optional[int] = None
    dietary_restrictions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    profile_extensions: Optional[Dict[str, Any]] = None
    schema_version: Optional[int] = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class FrontendUserProfile(BaseModel):
    """User profile for frontend (matches frontend interface)"""
    age: str
    height: str  # e.g., "5'9\""
    weight: str  # e.g., "159"
    gender: str
    activityLevel: str
    goals: List[str]
    appleId: Optional[str] = None
    healthData: Optional[Dict[str, Any]] = None

class UserInteraction(BaseModel):
    """User interaction with restaurants/menu items"""
    id: UUID4
    user_id: UUID4
    restaurant_id: Optional[UUID4] = None
    menu_item_id: Optional[UUID4] = None
    interaction_type: str  # 'like', 'dislike', 'view', 'order'
    context: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

class ChatMessage(BaseModel):
    """Chat message model"""
    id: UUID4
    user_id: UUID4
    role: str  # 'user', 'assistant'
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

class HealthConnection(BaseModel):
    """Health data connection"""
    user_id: UUID4
    source: str  # 'apple_health', 'google_fit'
    scopes: List[str]
    sync_token: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    status: str = 'active'  # 'active', 'paused', 'revoked'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ExtractedPreferences(BaseModel):
    """Preferences extracted by AI from user input"""
    budget: Optional[float] = None
    health_priority: Optional[str] = None  # low/medium/high
    portion_preference: Optional[str] = None  # small/medium/large/filling
    dietary_restrictions: Optional[List[Dict[str, Any]]] = None  # with confidence
    cuisine_preferences: Optional[List[str]] = None
    food_items: Optional[List[str]] = None  # specific food items requested
    urgency: Optional[str] = None  # low/normal/high
    emotional_context: Optional[str] = None
    meal_timing_preference: Optional[str] = None
    spice_tolerance: Optional[str] = None
    cooking_method_preferences: Optional[List[str]] = None
    ingredient_quality_preference: Optional[List[str]] = None
    nutrition_goals: Optional[List[str]] = None
    allergen_concerns: Optional[List[Dict[str, Any]]] = None
    texture_preferences: Optional[List[str]] = None

class LearnedInsights(BaseModel):
    """Insights learned about the user from interactions and conversations"""
    lifestyle_patterns: Optional[Dict[str, Any]] = None  # e.g., {"active_lifestyle": True, "night_owl": False}
    food_preferences: Optional[Dict[str, Any]] = None  # e.g., {"loves_spicy": True, "prefers_healthy": True}
    dining_habits: Optional[Dict[str, Any]] = None  # e.g., {"quick_meals": True, "social_dining": False}
    health_goals: Optional[Dict[str, Any]] = None  # e.g., {"weight_loss": True, "muscle_gain": False}
    budget_behavior: Optional[Dict[str, Any]] = None  # e.g., {"budget_conscious": True, "splurges_weekends": True}
    time_preferences: Optional[Dict[str, Any]] = None  # e.g., {"morning_person": True, "late_dinner": False}
    social_context: Optional[Dict[str, Any]] = None  # e.g., {"dines_alone": True, "family_dining": False}
    emotional_triggers: Optional[Dict[str, Any]] = None  # e.g., {"stress_eating": True, "celebration_food": True}
    confidence_scores: Optional[Dict[str, float]] = None  # Confidence in each insight (0-1)
    last_updated: Optional[datetime] = None
    source: Optional[str] = None  # "apple_health", "conversation", "behavior", "manual"

class PersonalizationData(BaseModel):
    """Comprehensive personalization data for a user"""
    user_id: UUID4
    extracted_preferences: Optional[ExtractedPreferences] = None
    learned_insights: Optional[LearnedInsights] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None  # Key conversation points
    interaction_patterns: Optional[Dict[str, Any]] = None  # Swipe patterns, time patterns, etc.
    fallback_questions_asked: Optional[List[str]] = None  # Questions asked when health data unavailable
    health_data_available: Optional[bool] = None
    last_personalization_update: Optional[datetime] = None
    schema_version: Optional[int] = 2
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
