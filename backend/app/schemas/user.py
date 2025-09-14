"""
User API schemas for requests and responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from app.models.user import FrontendUserProfile, ExtractedPreferences

class UserCreateRequest(BaseModel):
    """Request to create new user"""
    email: Optional[EmailStr] = None
    apple_id: Optional[str] = None

class UserProfileUpdateRequest(BaseModel):
    """Request to update user profile"""
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

class UserProfileResponse(BaseModel):
    """Response with user profile"""
    profile: FrontendUserProfile
    preferences: Dict[str, Any]

class ChatMessageRequest(BaseModel):
    """Request to send chat message"""
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    """Response from chat message"""
    response: str
    extracted_preferences: Optional[ExtractedPreferences] = None
    proposed_extensions: Optional[List[Dict[str, Any]]] = None
    search_triggered: bool = False
    search_results: Optional[List[Dict[str, Any]]] = None

class SwipeRequest(BaseModel):
    """Request for swipe action"""
    restaurant_id: str
    action: str  # 'like', 'dislike', 'skip'
    context: Optional[Dict[str, Any]] = None

class PreferencesUpdateRequest(BaseModel):
    """Request to update user preferences"""
    preferences: Dict[str, Any]

class HealthDataImportRequest(BaseModel):
    """Request to import health data"""
    source: str  # 'apple_health', 'google_fit'
    data: Dict[str, Any]
    sync_token: Optional[str] = None

class HealthDataImportResponse(BaseModel):
    """Response from health data import"""
    profile_updates: Dict[str, Any]
    proposed_extensions: List[Dict[str, Any]]
    requires_confirmation: bool
