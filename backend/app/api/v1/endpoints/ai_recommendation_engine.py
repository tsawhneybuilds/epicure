"""
AI-Powered Recommendation Engine Endpoint
Translates user input and calls the recommendation engine to display results in the app
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging
from app.services.ai_query_translator import AIQueryTranslator
from app.services.menu_item_service import MenuItemService
from app.models.menu_item import MenuItemSearchRequest

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/response models
class AIRecommendationRequest(BaseModel):
    message: str
    user_id: str
    context: Dict[str, Any] = {}
    chat_history: List[Dict[str, str]] = []

class AIRecommendationResponse(BaseModel):
    ai_response: str
    menu_items: List[Dict[str, Any]]
    search_query: str
    filters_applied: Dict[str, Any]
    translation_confidence: float
    search_reasoning: str
    conversation_id: Optional[str] = None
    preferences_extracted: Optional[Dict[str, Any]] = None

# Initialize services
ai_translator = AIQueryTranslator()
menu_service = MenuItemService()

@router.post("/recommend", response_model=AIRecommendationResponse)
async def ai_powered_recommendation(request: AIRecommendationRequest):
    """
    AI-powered recommendation: translates user input and calls recommendation engine
    
    The AI acts as a query translator - it takes natural language input and converts it
    into structured parameters for the recommendation engine, which then displays results
    in the swipe interface.
    """
    try:
        logger.info(f"🤖 AI Recommendation request: {request.message[:100]}...")
        
        # Step 1: AI translates user input into structured parameters
        translation = await ai_translator.translate_user_query(
            user_message=request.message,
            context=request.context,
            chat_history=request.chat_history
        )
        
        logger.info(f"📝 Translation result: {translation['search_query']}")
        
        # Step 2: Use translated parameters to call the recommendation engine
        search_request = MenuItemSearchRequest(
            query=translation["search_query"],
            location=request.context.get("location", {"lat": 40.7580, "lng": -73.9855}),
            filters=translation.get("filters", {}),
            personalization=translation.get("personalization", {})
        )
        
        # Step 3: Get menu items from recommendation engine
        menu_response = await menu_service.search_menu_items(search_request)
        
        # Step 4: Format response for the app
        response = AIRecommendationResponse(
            ai_response=translation["ai_response"],
            menu_items=[item.model_dump() for item in menu_response.menu_items],
            search_query=translation["search_query"],
            filters_applied=translation.get("filters", {}),
            translation_confidence=translation.get("translation_confidence", 0.9),
            search_reasoning=menu_response.meta.get("recommendations_reason", "AI-powered recommendation based on your preferences"),
            conversation_id=f"conv_{request.user_id}_{hash(request.message) % 10000}",
            preferences_extracted=translation.get("preferences_extracted", {})
        )
        
        logger.info(f"✅ AI Recommendation completed: {len(response.menu_items)} items found")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ AI Recommendation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AI Recommendation failed: {str(e)}"
        )

@router.post("/translate-query")
async def translate_query_only(request: AIRecommendationRequest):
    """
    Just translate the user query without calling the recommendation engine
    Useful for debugging and understanding what the AI is extracting
    """
    try:
        translation = await ai_translator.translate_user_query(
            user_message=request.message,
            context=request.context,
            chat_history=request.chat_history
        )
        
        return {
            "original_message": request.message,
            "translation": translation,
            "extracted_parameters": {
                "search_query": translation["search_query"],
                "filters": translation.get("filters", {}),
                "personalization": translation.get("personalization", {})
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query translation failed: {str(e)}"
        )

@router.get("/translation-examples")
async def get_translation_examples():
    """
    Get examples of how the AI translates different user inputs
    """
    return {
        "examples": [
            {
                "user_input": "High protein meals for workout recovery",
                "translation": {
                    "search_query": "high protein",
                    "filters": {"min_protein": 25},
                    "ai_response": "Perfect! I'm searching for high-protein options that align with your fitness goals."
                }
            },
            {
                "user_input": "Healthy vegetarian options under $15",
                "translation": {
                    "search_query": "vegetarian budget-friendly",
                    "filters": {"dietary_restrictions": ["vegetarian"], "max_price": 15},
                    "ai_response": "Great! I'm finding delicious vegetarian options for you."
                }
            },
            {
                "user_input": "Quick lunch, I'm in a rush",
                "translation": {
                    "search_query": "quick",
                    "personalization": {"urgency": "high"},
                    "ai_response": "I understand you're in a rush! Finding quick-prep options for you."
                }
            }
        ],
        "how_it_works": [
            "1. User enters natural language (e.g., 'High protein meals for workout recovery')",
            "2. AI translates this into structured parameters (search_query, filters, personalization)",
            "3. Recommendation engine uses these parameters to find menu items",
            "4. Results are displayed in the swipe interface",
            "5. AI provides a friendly response to the user"
        ]
    }
