"""
Chat and conversational AI endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from app.services.ai_service import AIService
from app.services.restaurant_service import RestaurantService
from app.schemas.user import ChatMessageRequest, ChatMessageResponse

router = APIRouter()

def get_ai_service() -> AIService:
    """Dependency to get AI service"""
    return AIService()

def get_restaurant_service() -> RestaurantService:
    """Dependency to get restaurant service"""
    return RestaurantService()

@router.post("/message", response_model=ChatMessageResponse)
async def process_chat_message(
    request: ChatMessageRequest,
    ai_service: AIService = Depends(get_ai_service),
    restaurant_service: RestaurantService = Depends(get_restaurant_service)
):
    """
    Process user chat message and extract preferences
    
    This endpoint:
    1. Extracts structured preferences from natural language
    2. Generates a conversational response
    3. Optionally triggers restaurant search if location provided
    """
    try:
        # Extract preferences from user message
        extracted_prefs = await ai_service.extract_preferences(
            request.message, 
            request.context
        )
        
        # Generate conversational response
        response_text = await ai_service.generate_response(
            request.message, 
            extracted_prefs
        )
        
        # Check if we should trigger a search
        search_triggered = False
        search_results = None
        
        if request.context and request.context.get('location'):
            # Trigger restaurant search based on extracted preferences
            from app.schemas.restaurant import RestaurantSearchRequest
            
            search_request = RestaurantSearchRequest(
                query=request.message,
                location=request.context['location'],
                filters={
                    "max_price": 4,  # Default max
                    "dietary_restrictions": [
                        item["restriction"] for item in (extracted_prefs.dietary_restrictions or [])
                        if item.get("confidence", 0) > 0.7
                    ] or None
                },
                limit=10
            )
            
            restaurants, meta = await restaurant_service.search_restaurants(search_request)
            search_results = [r.dict() for r in restaurants]
            search_triggered = True
        
        # Generate proposed profile extensions (mock for now)
        proposed_extensions = []
        if extracted_prefs.budget:
            proposed_extensions.append({
                "key": "preferred_meal_budget",
                "value": extracted_prefs.budget,
                "confidence": 0.90,
                "needs_confirmation": True
            })
        
        return ChatMessageResponse(
            response=response_text,
            extracted_preferences=extracted_prefs,
            proposed_extensions=proposed_extensions,
            search_triggered=search_triggered,
            search_results=search_results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.get("/{user_id}/history")
async def get_chat_history(
    user_id: str,
    limit: Optional[int] = 50
):
    """Get user's chat history"""
    try:
        # Mock implementation for development
        mock_history = [
            {
                "id": "1",
                "role": "user",
                "content": "I want something healthy for lunch",
                "timestamp": "2024-01-01T12:00:00Z"
            },
            {
                "id": "2", 
                "role": "assistant",
                "content": "I found some great healthy lunch options near you!",
                "timestamp": "2024-01-01T12:00:01Z"
            }
        ]
        
        return {
            "messages": mock_history[:limit],
            "total": len(mock_history),
            "mock_data": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat history fetch failed: {str(e)}")

@router.post("/extract-preferences")
async def extract_preferences_only(
    request: ChatMessageRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Extract preferences from text without generating response
    
    Useful for analyzing user input without full conversation flow
    """
    try:
        extracted_prefs = await ai_service.extract_preferences(
            request.message,
            request.context
        )
        
        return {
            "extracted_preferences": extracted_prefs,
            "original_message": request.message,
            "processing_time_ms": 150  # Mock timing
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preference extraction failed: {str(e)}")

@router.post("/analyze-text")
async def analyze_text(
    text: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Analyze any text for food-related properties
    
    Useful for analyzing menu items, restaurant descriptions, etc.
    """
    try:
        analysis = await ai_service.analyze_menu_item(text)
        
        return {
            "text": text,
            "analysis": analysis,
            "processing_time_ms": 200  # Mock timing
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

@router.post("/similarity")
async def calculate_similarity(
    query: str,
    item_text: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Calculate semantic similarity between query and item text
    
    Useful for testing recommendation algorithms
    """
    try:
        similarity = await ai_service.semantic_similarity(query, item_text)
        
        return {
            "query": query,
            "item_text": item_text,
            "similarity_score": similarity,
            "processing_time_ms": 100  # Mock timing
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity calculation failed: {str(e)}")

# Development/Debug endpoints
@router.get("/debug/ai-status")
async def get_ai_status(ai_service: AIService = Depends(get_ai_service)):
    """Get AI service status and configuration"""
    return {
        "ai_service_active": True,
        "using_mock_data": ai_service.use_mock,
        "available_models": ["llama3-70b-8192", "mixtral-8x7b-32768"],
        "note": "DeepSeek-V3 integration ready when available on Groq"
    }
