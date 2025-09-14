"""
Enhanced Conversational AI endpoints with tool calling capabilities
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging
from app.services.enhanced_ai_service import EnhancedAIService

logger = logging.getLogger(__name__)

router = APIRouter()

# Enhanced request/response models
class EnhancedConversationalSearchRequest(BaseModel):
    message: str
    user_id: str
    context: Dict[str, Any] = {}
    chat_history: List[Dict[str, str]] = []

class EnhancedConversationalSearchResponse(BaseModel):
    ai_response: str
    menu_items: List[Dict[str, Any]]
    preferences_extracted: Dict[str, Any]
    research_insights: Dict[str, Any]
    search_reasoning: str
    tools_used: List[str]
    conversation_id: Optional[str] = None

# Initialize enhanced AI service
enhanced_ai_service = EnhancedAIService()

@router.post("/enhanced-search", response_model=EnhancedConversationalSearchResponse)
async def enhanced_conversational_search(request: EnhancedConversationalSearchRequest):
    """
    Enhanced conversational search with AI tool calling for research and analysis
    """
    try:
        logger.info(f"🔍 Enhanced conversational search request: {request.message[:100]}...")
        
        # Use enhanced AI service with tool calling
        result = await enhanced_ai_service.enhanced_conversational_search(
            message=request.message,
            user_id=request.user_id,
            context=request.context,
            chat_history=request.chat_history
        )
        
        # Add conversation ID for tracking
        result["conversation_id"] = f"conv_{request.user_id}_{hash(request.message) % 10000}"
        
        logger.info(f"✅ Enhanced search completed: {len(result['menu_items'])} items found")
        
        return EnhancedConversationalSearchResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Enhanced conversational search failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Enhanced conversational search failed: {str(e)}"
        )

@router.post("/research-tools/menu-analysis")
async def menu_research_tool(
    query: str,
    location: Dict[str, float],
    user_id: str
):
    """
    Tool for researching menu items and trends
    """
    try:
        result = await enhanced_ai_service.call_menu_research_tool(query, location)
        return {
            "tool": "menu_research",
            "query": query,
            "location": location,
            "results": result,
            "timestamp": "2024-01-15T10:30:00Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Menu research tool failed: {str(e)}"
        )

@router.post("/research-tools/nutrition-analysis")
async def nutrition_analysis_tool(
    menu_item: str,
    user_id: str
):
    """
    Tool for analyzing nutrition content of menu items
    """
    try:
        result = await enhanced_ai_service.call_nutrition_analysis_tool(menu_item)
        return {
            "tool": "nutrition_analysis",
            "menu_item": menu_item,
            "analysis": result,
            "timestamp": "2024-01-15T10:30:00Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Nutrition analysis tool failed: {str(e)}"
        )

@router.post("/research-tools/restaurant-insights")
async def restaurant_insights_tool(
    restaurant_name: str,
    user_id: str
):
    """
    Tool for getting restaurant insights and information
    """
    try:
        result = await enhanced_ai_service.call_restaurant_insights_tool(restaurant_name)
        return {
            "tool": "restaurant_insights",
            "restaurant": restaurant_name,
            "insights": result,
            "timestamp": "2024-01-15T10:30:00Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Restaurant insights tool failed: {str(e)}"
        )

@router.get("/tools/available")
async def get_available_tools():
    """
    Get list of available AI tools for research
    """
    return {
        "available_tools": [
            {
                "name": "menu_research",
                "description": "Research menu items, trends, and popular dishes",
                "endpoint": "/api/v1/ai/research-tools/menu-analysis"
            },
            {
                "name": "nutrition_analysis", 
                "description": "Analyze nutrition content and health benefits",
                "endpoint": "/api/v1/ai/research-tools/nutrition-analysis"
            },
            {
                "name": "restaurant_insights",
                "description": "Get restaurant ratings, specialties, and insights",
                "endpoint": "/api/v1/ai/research-tools/restaurant-insights"
            }
        ],
        "enhanced_search_endpoint": "/api/v1/ai/enhanced-search"
    }
