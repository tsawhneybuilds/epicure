"""
User management API endpoints
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user import (
    UserCreateRequest,
    UserProfileUpdateRequest, 
    UserProfileResponse,
    SwipeRequest,
    PreferencesUpdateRequest
)

router = APIRouter()

# Mock user store for development (replace with actual database)
mock_users = {}
mock_profiles = {}
mock_preferences = {}
mock_interactions = []

@router.post("/create")
async def create_user(request: UserCreateRequest):
    """Create a new user account"""
    try:
        # Mock implementation
        import uuid
        user_id = str(uuid.uuid4())
        
        mock_users[user_id] = {
            "id": user_id,
            "email": request.email,
            "apple_id": request.apple_id,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        return {
            "user_id": user_id,
            "message": "User created successfully",
            "mock_data": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User creation failed: {str(e)}")

@router.get("/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Get user profile and preferences"""
    try:
        # Mock implementation - return default profile
        mock_profile = {
            "age": "28",
            "height": "5'9\"",
            "weight": "159",
            "gender": "male", 
            "activityLevel": "moderate",
            "goals": ["Track macros", "Muscle gain"],
            "appleId": "user@icloud.com"
        }
        
        mock_prefs = {
            "budgetFriendly": False,
            "dietary": None,
            "quickService": False,
            "healthPriority": "medium"
        }
        
        return UserProfileResponse(
            profile=mock_profile,
            preferences=mock_prefs
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile fetch failed: {str(e)}")

@router.put("/{user_id}/profile")
async def update_user_profile(
    user_id: str,
    request: UserProfileUpdateRequest
):
    """Update user profile"""
    try:
        # Mock implementation
        mock_profiles[user_id] = request.dict(exclude_unset=True)
        
        return {
            "message": "Profile updated successfully",
            "updated_fields": list(request.dict(exclude_unset=True).keys()),
            "mock_data": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile update failed: {str(e)}")

@router.patch("/{user_id}/preferences")
async def update_preferences(
    user_id: str,
    request: PreferencesUpdateRequest
):
    """Update user preferences"""
    try:
        # Mock implementation
        if user_id not in mock_preferences:
            mock_preferences[user_id] = {}
        
        mock_preferences[user_id].update(request.preferences)
        
        return {
            "message": "Preferences updated successfully",
            "preferences": mock_preferences[user_id],
            "mock_data": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preferences update failed: {str(e)}")

@router.post("/{user_id}/interactions/swipe")
async def record_swipe(
    user_id: str,
    request: SwipeRequest
):
    """Record user swipe interaction"""
    try:
        # Mock implementation
        interaction = {
            "user_id": user_id,
            "restaurant_id": request.restaurant_id,
            "action": request.action,
            "context": request.context,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        mock_interactions.append(interaction)
        
        return {
            "message": f"Swipe {request.action} recorded",
            "interaction_id": len(mock_interactions),
            "mock_data": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Swipe recording failed: {str(e)}")

@router.get("/{user_id}/interactions/liked")
async def get_liked_restaurants(user_id: str):
    """Get user's liked restaurants"""
    try:
        # Mock implementation
        liked_interactions = [
            i for i in mock_interactions 
            if i["user_id"] == user_id and i["action"] == "like"
        ]
        
        # For demo, return some mock liked restaurants
        mock_liked = [
            {
                "id": "1",
                "name": "Green Bowl Kitchen",
                "cuisine": "Healthy Bowls",
                "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400",
                "rating": 4.8,
                "price": "$$",
                "distance": "0.3 mi"
            }
        ]
        
        return {
            "liked_restaurants": mock_liked,
            "count": len(mock_liked),
            "mock_data": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Liked restaurants fetch failed: {str(e)}")

@router.delete("/{user_id}/interactions/liked/{restaurant_id}")
async def remove_liked_restaurant(user_id: str, restaurant_id: str):
    """Remove restaurant from liked list"""
    try:
        # Mock implementation
        global mock_interactions
        mock_interactions = [
            i for i in mock_interactions 
            if not (i["user_id"] == user_id and i["restaurant_id"] == restaurant_id and i["action"] == "like")
        ]
        
        return {
            "message": "Restaurant removed from liked list",
            "restaurant_id": restaurant_id,
            "mock_data": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Remove liked failed: {str(e)}")

@router.get("/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user interaction statistics"""
    try:
        user_interactions = [i for i in mock_interactions if i["user_id"] == user_id]
        
        stats = {
            "total_interactions": len(user_interactions),
            "likes": len([i for i in user_interactions if i["action"] == "like"]),
            "dislikes": len([i for i in user_interactions if i["action"] == "dislike"]),
            "views": len([i for i in user_interactions if i["action"] == "view"]),
            "mock_data": True
        }
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User stats failed: {str(e)}")
