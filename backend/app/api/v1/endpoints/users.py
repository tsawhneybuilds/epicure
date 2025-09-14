"""
User management API endpoints
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from app.schemas.user import (
    UserCreateRequest,
    UserProfileUpdateRequest, 
    UserProfileResponse,
    SwipeRequest,
    PreferencesUpdateRequest
)
from app.core.supabase import get_supabase_client
from app.models.user import User, UserProfile, FrontendUserProfile
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def get_user_id_from_auth(authorization: Optional[str] = Header(None)) -> str:
    """Extract user ID from authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # For now, we'll use a simple format: "Bearer user_id"
    # In production, this would be a JWT token
    try:
        if authorization.startswith("Bearer "):
            user_id = authorization[7:]  # Remove "Bearer " prefix
            # Validate UUID format
            uuid.UUID(user_id)
            return user_id
        else:
            raise HTTPException(status_code=401, detail="Invalid authorization format")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID format")

@router.post("/create")
async def create_user(request: UserCreateRequest):
    """Create a new user account"""
    try:
        # Validate required fields
        if not request.email and not request.apple_id:
            raise HTTPException(status_code=400, detail="Either email or Apple ID is required")
        
        # Validate email format if provided
        if request.email and not request.email.strip():
            raise HTTPException(status_code=400, detail="Email cannot be empty")
        
        supabase = get_supabase_client()
        
        # Check if user already exists
        if request.email:
            existing_user = supabase.table('users').select('id').eq('email', request.email).execute()
            if existing_user.data:
                raise HTTPException(status_code=400, detail="User with this email already exists")
        
        if request.apple_id:
            existing_user = supabase.table('users').select('id').eq('apple_id', request.apple_id).execute()
            if existing_user.data:
                raise HTTPException(status_code=400, detail="User with this Apple ID already exists")
        
        # Create new user
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "email": request.email,
            "apple_id": request.apple_id
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Create empty profile
        profile_data = {
            "user_id": user_id,
            "schema_version": 1
        }
        
        supabase.table('user_profiles').insert(profile_data).execute()
        
        return {
            "user_id": user_id,
            "message": "User created successfully",
            "auth_token": user_id  # In production, this would be a JWT
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"User creation failed: {str(e)}")

@router.get("/{user_id}/profile")
async def get_user_profile(user_id: str, current_user_id: str = Depends(get_user_id_from_auth)):
    """Get user profile and preferences"""
    try:
        # Verify user can access this profile
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        supabase = get_supabase_client()
        
        # Get user profile
        profile_result = supabase.table('user_profiles').select('*').eq('user_id', user_id).execute()
        
        if not profile_result.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile_data = profile_result.data[0]
        
        # Convert to frontend format
        height_cm = profile_data.get('height_cm')
        if height_cm and height_cm > 0:
            feet = int(height_cm // 30.48)
            inches = int((height_cm % 30.48) / 2.54)
            height_str = f"{feet}'{inches}\""
        else:
            height_str = ""
        
        frontend_profile = FrontendUserProfile(
            age=str(profile_data.get('age', '')),
            height=height_str,
            weight=str(profile_data.get('weight_kg', '')),
            gender=profile_data.get('gender') or '',
            activityLevel=profile_data.get('activity_level') or '',
            goals=profile_data.get('goals') or [],
            appleId=profile_data.get('apple_id') or '',
            healthData=profile_data.get('profile_extensions') or {}
        )
        
        # Get preferences from profile extensions
        preferences = profile_data.get('profile_extensions', {})
        
        return UserProfileResponse(
            profile=frontend_profile,
            preferences=preferences
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Profile fetch failed: {str(e)}")

@router.put("/{user_id}/profile")
async def update_user_profile(
    user_id: str,
    request: UserProfileUpdateRequest,
    current_user_id: str = Depends(get_user_id_from_auth)
):
    """Update user profile"""
    try:
        # Verify user can update this profile
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        supabase = get_supabase_client()
        
        # Convert request to database format
        update_data = {}
        if request.age is not None:
            update_data['age'] = request.age
        if request.height_cm is not None:
            update_data['height_cm'] = request.height_cm
        if request.weight_kg is not None:
            update_data['weight_kg'] = request.weight_kg
        if request.gender is not None:
            update_data['gender'] = request.gender
        if request.activity_level is not None:
            update_data['activity_level'] = request.activity_level
        if request.goals is not None:
            update_data['goals'] = request.goals
        if request.budget_usd_per_meal is not None:
            update_data['budget_usd_per_meal'] = request.budget_usd_per_meal
        if request.max_walk_time_minutes is not None:
            update_data['max_walk_time_minutes'] = request.max_walk_time_minutes
        if request.dietary_restrictions is not None:
            update_data['dietary_restrictions'] = request.dietary_restrictions
        if request.allergies is not None:
            update_data['allergies'] = request.allergies
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update profile
        result = supabase.table('user_profiles').update(update_data).eq('user_id', user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return {
            "message": "Profile updated successfully",
            "updated_fields": list(update_data.keys())
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Profile update failed: {str(e)}")

@router.patch("/{user_id}/preferences")
async def update_preferences(
    user_id: str,
    request: PreferencesUpdateRequest,
    current_user_id: str = Depends(get_user_id_from_auth)
):
    """Update user preferences"""
    try:
        # Verify user can update this profile
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        supabase = get_supabase_client()
        
        # Get current profile extensions
        profile_result = supabase.table('user_profiles').select('profile_extensions').eq('user_id', user_id).execute()
        
        if not profile_result.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        current_extensions = profile_result.data[0].get('profile_extensions', {})
        
        # Merge new preferences with existing extensions
        updated_extensions = {**current_extensions, **request.preferences}
        
        # Update profile extensions
        result = supabase.table('user_profiles').update({
            'profile_extensions': updated_extensions
        }).eq('user_id', user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return {
            "message": "Preferences updated successfully",
            "preferences": updated_extensions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preferences update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preferences update failed: {str(e)}")

@router.post("/{user_id}/interactions/swipe")
async def record_swipe(
    user_id: str,
    request: SwipeRequest,
    current_user_id: str = Depends(get_user_id_from_auth)
):
    """Record user swipe interaction"""
    try:
        # Verify user can record interactions for this profile
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        supabase = get_supabase_client()
        
        # Record interaction
        interaction_data = {
            "user_id": user_id,
            "restaurant_id": request.restaurant_id,
            "interaction_type": request.action,
            "context": request.context or {}
        }
        
        result = supabase.table('user_interactions').insert(interaction_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to record interaction")
        
        return {
            "message": f"Swipe {request.action} recorded",
            "interaction_id": result.data[0]['id']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Swipe recording failed: {e}")
        raise HTTPException(status_code=500, detail=f"Swipe recording failed: {str(e)}")

@router.get("/{user_id}/interactions/liked")
async def get_liked_restaurants(user_id: str, current_user_id: str = Depends(get_user_id_from_auth)):
    """Get user's liked restaurants"""
    try:
        # Verify user can access this data
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        supabase = get_supabase_client()
        
        # Get liked interactions with restaurant details
        result = supabase.table('user_interactions').select('''
            *,
            restaurants (
                id,
                name,
                cuisine,
                image_url,
                rating,
                price_level,
                address
            )
        ''').eq('user_id', user_id).eq('interaction_type', 'like').execute()
        
        liked_restaurants = []
        for interaction in result.data:
            restaurant = interaction.get('restaurants')
            if restaurant:
                liked_restaurants.append({
                    "id": restaurant['id'],
                    "name": restaurant['name'],
                    "cuisine": restaurant['cuisine'],
                    "image": restaurant.get('image_url', ''),
                    "rating": restaurant.get('rating', 0),
                    "price": "$" * (restaurant.get('price_level', 1)),
                    "address": restaurant.get('address', ''),
                    "liked_at": interaction['created_at']
                })
        
        return {
            "liked_restaurants": liked_restaurants,
            "count": len(liked_restaurants)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Liked restaurants fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Liked restaurants fetch failed: {str(e)}")

@router.delete("/{user_id}/interactions/liked/{restaurant_id}")
async def remove_liked_restaurant(
    user_id: str, 
    restaurant_id: str,
    current_user_id: str = Depends(get_user_id_from_auth)
):
    """Remove restaurant from liked list"""
    try:
        # Verify user can modify this data
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        supabase = get_supabase_client()
        
        # Remove the like interaction
        result = supabase.table('user_interactions').delete().eq('user_id', user_id).eq('restaurant_id', restaurant_id).eq('interaction_type', 'like').execute()
        
        return {
            "message": "Restaurant removed from liked list",
            "restaurant_id": restaurant_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove liked failed: {e}")
        raise HTTPException(status_code=500, detail=f"Remove liked failed: {str(e)}")

@router.get("/{user_id}/stats")
async def get_user_stats(user_id: str, current_user_id: str = Depends(get_user_id_from_auth)):
    """Get user interaction statistics"""
    try:
        # Verify user can access this data
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        supabase = get_supabase_client()
        
        # Get interaction counts
        interactions_result = supabase.table('user_interactions').select('interaction_type').eq('user_id', user_id).execute()
        
        interactions = interactions_result.data
        stats = {
            "total_interactions": len(interactions),
            "likes": len([i for i in interactions if i["interaction_type"] == "like"]),
            "dislikes": len([i for i in interactions if i["interaction_type"] == "dislike"]),
            "views": len([i for i in interactions if i["interaction_type"] == "view"])
        }
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"User stats failed: {str(e)}")

@router.post("/login")
async def login_user(request: UserCreateRequest):
    """Login user and return auth token"""
    try:
        supabase = get_supabase_client()
        
        # Find user by email or apple_id
        user_query = supabase.table('users').select('id, email, apple_id')
        
        if request.email:
            user_query = user_query.eq('email', request.email)
        elif request.apple_id:
            user_query = user_query.eq('apple_id', request.apple_id)
        else:
            raise HTTPException(status_code=400, detail="Email or Apple ID required")
        
        result = user_query.execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = result.data[0]
        
        return {
            "user_id": user['id'],
            "message": "Login successful",
            "auth_token": user['id']  # In production, this would be a JWT
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
