"""
Menu Items API endpoints for the new frontend_new integration
"""
from typing import List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ....models.menu_item import (
    MenuItem,
    MenuItemSearchRequest, 
    MenuItemSearchResponse,
    MenuItemInteraction
)
from ....services.menu_item_service import menu_item_service

router = APIRouter()


@router.post("/search", response_model=MenuItemSearchResponse)
async def search_menu_items(request: MenuItemSearchRequest):
    """
    Search for menu items based on query, filters, and personalization
    
    This is the primary endpoint for the frontend_new SwipeInterface
    """
    try:
        result = await menu_item_service.search_menu_items(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/{menu_item_id}", response_model=MenuItem)
async def get_menu_item(menu_item_id: str):
    """
    Get a specific menu item by ID
    """
    menu_item = await menu_item_service.get_menu_item_by_id(menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item


@router.post("/interactions/swipe")
async def record_menu_item_swipe(interaction: MenuItemInteraction):
    """
    Record user swipe interaction on a menu item
    
    Used when user swipes left/right on menu items in SwipeInterface
    """
    try:
        success = await menu_item_service.record_interaction(interaction)
        if success:
            return {"status": "success", "message": "Interaction recorded"}
        else:
            raise HTTPException(status_code=500, detail="Failed to record interaction")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recording failed: {str(e)}")


@router.get("/users/{user_id}/liked", response_model=List[MenuItem])
async def get_user_liked_menu_items(user_id: str):
    """
    Get menu items liked by a user
    
    Used for the LikedScreen in frontend_new
    """
    try:
        liked_items = await menu_item_service.get_user_liked_items(user_id)
        return liked_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get liked items: {str(e)}")


@router.get("/categories")
async def get_menu_categories():
    """
    Get available menu item categories for filtering
    """
    categories = [
        {"id": "breakfast", "name": "Breakfast", "emoji": "🍳"},
        {"id": "bowls", "name": "Bowls", "emoji": "🥗"},
        {"id": "pizza", "name": "Pizza", "emoji": "🍕"},
        {"id": "sandwiches", "name": "Sandwiches", "emoji": "🥪"},
        {"id": "pasta", "name": "Pasta", "emoji": "🍝"}, 
        {"id": "desserts", "name": "Desserts", "emoji": "🍰"},
        {"id": "snacks", "name": "Snacks", "emoji": "🥨"},
        {"id": "beverages", "name": "Beverages", "emoji": "🥤"}
    ]
    return {"categories": categories}


@router.get("/dietary-options")
async def get_dietary_options():
    """
    Get available dietary options for filtering
    """
    dietary_options = [
        {"id": "vegetarian", "name": "Vegetarian", "emoji": "🥬"},
        {"id": "vegan", "name": "Vegan", "emoji": "🌱"},
        {"id": "gluten-free", "name": "Gluten Free", "emoji": "🌾"},
        {"id": "high-protein", "name": "High Protein", "emoji": "💪"},
        {"id": "keto", "name": "Keto", "emoji": "🥑"},
        {"id": "low-carb", "name": "Low Carb", "emoji": "🥩"},
        {"id": "organic", "name": "Organic", "emoji": "🌿"},
        {"id": "dairy-free", "name": "Dairy Free", "emoji": "🥥"}
    ]
    return {"dietary_options": dietary_options}


@router.get("/stats")
async def get_menu_items_stats():
    """
    Get menu items statistics for dashboard/analytics
    """
    # Mock stats for now
    stats = {
        "total_menu_items": 1247,
        "total_restaurants": 156,
        "categories_available": 8,
        "dietary_options": 8,
        "avg_calories_per_item": 485,
        "avg_protein_per_item": 24.5,
        "popular_categories": [
            {"category": "bowls", "count": 342},
            {"category": "pizza", "count": 198},
            {"category": "breakfast", "count": 167}
        ],
        "popular_dietary": [
            {"dietary": "vegetarian", "count": 428}, 
            {"dietary": "gluten-free", "count": 245},
            {"dietary": "high-protein", "count": 189}
        ]
    }
    return stats


@router.post("/recommend")
async def get_personalized_recommendations(request: dict):
    """
    Get personalized menu item recommendations based on user profile
    
    Enhanced recommendation endpoint with ML-powered suggestions
    """
    user_id = request.get("user_id")
    context = request.get("context", {})
    preferences = request.get("preferences", {})
    
    # Build personalized search request
    search_request = MenuItemSearchRequest(
        query="personalized recommendations",
        location=context.get("location", {"lat": 40.7580, "lng": -73.9855}),
        personalization={
            "user_id": user_id,
            "preferences": preferences,
            "context": context.get("meal_context", "general")
        },
        limit=request.get("limit", 10)
    )
    
    try:
        result = await menu_item_service.search_menu_items(search_request)
        return {
            "recommendations": result.menu_items,
            "reasoning": result.meta.get("recommendations_reason"),
            "personalization_score": result.meta.get("personalization_score"),
            "context_applied": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@router.get("/trending")
async def get_trending_menu_items(
    limit: int = Query(10, ge=1, le=50),
    category: str = Query(None, description="Filter by category"),
    time_period: str = Query("week", description="Trending period: day, week, month")
):
    """
    Get trending menu items based on popularity and interactions
    """
    # Mock trending logic for now
    search_request = MenuItemSearchRequest(
        query="trending items",
        location={"lat": 40.7580, "lng": -73.9855},
        filters={"categories": [category]} if category else {},
        sort_by="relevance",
        limit=limit
    )
    
    try:
        result = await menu_item_service.search_menu_items(search_request)
        trending_items = result.menu_items
        
        # Add trending metadata
        for item in trending_items:
            item.is_popular = True
            # Add trending score (mock)
            if hasattr(item, 'popularity_score'):
                item.popularity_score = min((item.popularity_score or 0.5) + 0.2, 1.0)
        
        return {
            "trending_items": trending_items,
            "period": time_period,
            "category": category,
            "total_found": len(trending_items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trending fetch failed: {str(e)}")
