"""
Restaurant API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.services.restaurant_service import RestaurantService
from app.schemas.restaurant import (
    RestaurantSearchRequest, 
    RestaurantSearchResponse,
    RestaurantStatsResponse,
    NearbyRestaurantsRequest,
    LocationRequest
)
from app.models.restaurant import FrontendRestaurant

router = APIRouter()

def get_restaurant_service() -> RestaurantService:
    """Dependency to get restaurant service"""
    return RestaurantService()

@router.post("/search", response_model=RestaurantSearchResponse)
async def search_restaurants(
    request: RestaurantSearchRequest,
    service: RestaurantService = Depends(get_restaurant_service)
):
    """
    Search restaurants based on user preferences and location
    
    This is the main endpoint used by the frontend SwipeInterface
    """
    try:
        restaurants, meta = await service.search_restaurants(request)
        
        return RestaurantSearchResponse(
            restaurants=restaurants,
            meta=meta
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/stats", response_model=RestaurantStatsResponse)
async def get_restaurant_stats(
    service: RestaurantService = Depends(get_restaurant_service)
):
    """Get statistics about restaurants in the database"""
    try:
        stats = await service.get_restaurant_stats()
        return RestaurantStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats query failed: {str(e)}")

@router.get("/{restaurant_id}")
async def get_restaurant(
    restaurant_id: str,
    service: RestaurantService = Depends(get_restaurant_service)
):
    """Get detailed information about a specific restaurant"""
    try:
        restaurant = await service.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/nearby")
async def get_nearby_restaurants(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"), 
    radius: float = Query(2.0, description="Radius in miles"),
    limit: int = Query(50, description="Maximum number of results"),
    service: RestaurantService = Depends(get_restaurant_service)
):
    """Get restaurants within specified radius of location"""
    try:
        restaurants = await service.get_nearby_restaurants(lat, lng, radius, limit)
        return {"restaurants": restaurants, "count": len(restaurants)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nearby query failed: {str(e)}")

@router.get("/categories")
async def get_categories():
    """Get available restaurant categories/cuisines"""
    # TODO: Implement based on actual database data
    return {
        "cuisines": [
            "Italian", "Asian", "American", "Mexican", "Indian", 
            "French", "Mediterranean", "Japanese", "Chinese", "Thai",
            "Healthy", "Vegan", "Fast Casual", "Fine Dining"
        ],
        "dietary_options": [
            "Vegetarian", "Vegan", "Gluten-free", "Dairy-free", 
            "Keto", "Paleo", "Low-carb", "High-protein"
        ],
        "price_levels": ["$", "$$", "$$$", "$$$$"]
    }

@router.post("/filter")
async def filter_restaurants(
    request: RestaurantSearchRequest,
    service: RestaurantService = Depends(get_restaurant_service)
):
    """Apply specific filters to restaurant search"""
    try:
        # This is essentially the same as search but emphasizes filtering
        restaurants, meta = await service.search_restaurants(request)
        
        return {
            "restaurants": restaurants,
            "meta": meta,
            "applied_filters": list(request.filters.keys()) if request.filters else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter failed: {str(e)}")

# Development/Debug endpoints
@router.get("/debug/mock-data")
async def get_mock_data():
    """Get sample mock data for frontend development"""
    return {
        "sample_restaurants": [
            {
                "id": "1",
                "name": "Green Bowl Kitchen",
                "cuisine": "Healthy Bowls",
                "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400",
                "distance": "0.3 mi",
                "price": "$$",
                "rating": 4.8,
                "waitTime": "15 min",
                "calories": 420,
                "protein": 28,
                "carbs": 35,
                "fat": 18,
                "dietary": ["Vegetarian", "Gluten-free"],
                "highlights": ["High protein", "Fresh ingredients", "Quick service"]
            }
        ],
        "note": "This is mock data for development"
    }
