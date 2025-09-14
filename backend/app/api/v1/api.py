"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import restaurants, users, chat, health, menu_items, conversational_ai, enhanced_conversational_ai, ai_recommendation_engine

api_router = APIRouter()

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "message": "Epicure API is running",
        "version": "1.0.0"
    }

# Include all endpoint routers
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["restaurants"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(menu_items.router, prefix="/menu-items", tags=["menu-items"])
api_router.include_router(conversational_ai.router, prefix="/ai", tags=["conversational-ai"])
api_router.include_router(enhanced_conversational_ai.router, prefix="/ai", tags=["enhanced-ai"])
api_router.include_router(ai_recommendation_engine.router, prefix="/ai", tags=["ai-recommendation"])
