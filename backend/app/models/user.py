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
    urgency: Optional[str] = None  # low/normal/high
    emotional_context: Optional[str] = None
    meal_timing_preference: Optional[str] = None
    spice_tolerance: Optional[str] = None
    cooking_method_preferences: Optional[List[str]] = None
    ingredient_quality_preference: Optional[List[str]] = None
    nutrition_goals: Optional[List[str]] = None
    allergen_concerns: Optional[List[Dict[str, Any]]] = None
    texture_preferences: Optional[List[str]] = None
