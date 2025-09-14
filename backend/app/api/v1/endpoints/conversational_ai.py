"""
Conversational AI endpoints for enhanced chat integration with menu item search
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ....models.menu_item import MenuItemSearchRequest, MenuItem
from ....services.menu_item_service import menu_item_service
from ....services.ai_service import ai_service

router = APIRouter()


class ConversationalSearchRequest(BaseModel):
    """Request for conversational food search"""
    message: str
    context: Optional[Dict[str, Any]] = {}
    chat_history: Optional[List[Dict[str, str]]] = []
    user_id: Optional[str] = None


class ConversationalSearchResponse(BaseModel):
    """Response for conversational food search"""
    ai_response: str
    suggested_search: Optional[Dict[str, Any]] = None
    menu_items: List[MenuItem] = []
    conversation_id: str
    preferences_extracted: Dict[str, Any] = {}
    search_reasoning: str = ""


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[str] = None


class ConversationSession(BaseModel):
    """Conversation session management"""
    session_id: str
    user_id: str
    messages: List[ChatMessage]
    extracted_preferences: Dict[str, Any] = {}
    context: Dict[str, Any] = {}


@router.post("/search", response_model=ConversationalSearchResponse)
async def conversational_food_search(request: ConversationalSearchRequest):
    """
    Main conversational AI endpoint that processes natural language and returns menu items
    
    This endpoint:
    1. Processes the user's natural language message
    2. Extracts food preferences and intent
    3. Converts to a structured search request
    4. Returns AI response + menu items
    """
    try:
        # Extract preferences and intent from the message
        preferences_result = await ai_service.extract_preferences(
            request.message, 
            request.context
        )
        
        # Convert ExtractedPreferences to dict for processing
        if hasattr(preferences_result, 'model_dump'):
            # Pydantic v2
            preferences_dict = preferences_result.model_dump()
        elif hasattr(preferences_result, 'dict'):
            # Pydantic v1
            preferences_dict = preferences_result.dict()
        else:
            preferences_dict = preferences_result
        
        # Use the AI recommendation engine instead of basic search
        from app.services.ai_query_translator import AIQueryTranslator
        ai_translator = AIQueryTranslator()
        
        # Translate the user message into structured parameters for the recommendation engine
        translation = await ai_translator.translate_user_query(
            user_message=request.message,
            context=request.context,
            chat_history=request.chat_history
        )
        
        # Use AI response from the translation (which uses the recommendation engine)
        ai_response = translation.get("ai_response", "I found some great options for you!")
        
        # Build menu search request from AI translation
        # Use original user message for semantic search, translation for tagging/filters
        menu_search_request = MenuItemSearchRequest(
            query=request.message,  # Use original user message for semantic search
            location=request.context.get("location", {"lat": 40.7580, "lng": -73.9855}),
            filters=translation.get("filters", {}),
            personalization={
                **translation.get("personalization", {}),
                "translated_query": translation["search_query"],  # Store translated query for tagging
                "original_message": request.message  # Store original message
            }
        )
        
        # Search for menu items using the recommendation engine
        search_result = await menu_item_service.search_menu_items(menu_search_request)
        
        # Generate search reasoning
        search_reasoning = _generate_search_reasoning(preferences_dict, search_result)
        
        return ConversationalSearchResponse(
            ai_response=ai_response,
            suggested_search={
                "query": menu_search_request.query,
                "filters": menu_search_request.filters
            },
            menu_items=search_result.menu_items,
            conversation_id=f"conv-{request.user_id}-{len(request.chat_history)}",
            preferences_extracted=preferences_dict,
            search_reasoning=search_reasoning
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversational search failed: {str(e)}")


@router.post("/refine-search")
async def refine_menu_search(request: Dict[str, Any]):
    """
    Refine menu item search based on follow-up conversation
    """
    refinement_message = request.get("message", "")
    current_filters = request.get("current_filters", {})
    current_results = request.get("current_results", [])
    
    try:
        # Process refinement request
        refinement = await ai_service.process_search_refinement(
            refinement_message,
            current_filters,
            current_results
        )
        
        # Build updated search request
        updated_search = MenuItemSearchRequest(
            query=refinement.get("updated_query", "refined search"),
            location=request.get("location", {"lat": 40.7580, "lng": -73.9855}),
            filters=refinement.get("updated_filters", {}),
            personalization=request.get("personalization", {}),
            limit=request.get("limit", 20)
        )
        
        # Execute refined search
        search_result = await menu_item_service.search_menu_items(updated_search)
        
        return {
            "ai_response": refinement.get("explanation", "I've updated your search based on your feedback."),
            "updated_filters": refinement.get("updated_filters"),
            "menu_items": search_result.menu_items,
            "refinement_applied": refinement.get("changes_made", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search refinement failed: {str(e)}")


@router.post("/explain-recommendation")
async def explain_menu_item_recommendation(request: Dict[str, Any]):
    """
    Explain why a specific menu item was recommended to the user
    """
    menu_item_id = request.get("menu_item_id")
    user_preferences = request.get("user_preferences", {})
    search_context = request.get("search_context", {})
    
    try:
        # Get the menu item
        menu_item = await menu_item_service.get_menu_item_by_id(menu_item_id)
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        
        # Generate explanation using AI
        explanation = await ai_service.explain_recommendation(
            menu_item.dict(),
            user_preferences,
            search_context
        )
        
        return {
            "menu_item_id": menu_item_id,
            "explanation": explanation.get("explanation", "This item matches your preferences."),
            "key_factors": explanation.get("key_factors", []),
            "nutrition_highlights": explanation.get("nutrition_highlights", []),
            "personalization_score": explanation.get("score", 0.8)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@router.post("/compare-items")
async def compare_menu_items(request: Dict[str, Any]):
    """
    Compare multiple menu items and provide AI analysis
    """
    menu_item_ids = request.get("menu_item_ids", [])
    comparison_criteria = request.get("criteria", ["nutrition", "price", "taste_profile"])
    
    try:
        # Get all menu items
        menu_items = []
        for item_id in menu_item_ids:
            item = await menu_item_service.get_menu_item_by_id(item_id)
            if item:
                menu_items.append(item)
        
        if len(menu_items) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 items to compare")
        
        # Generate AI comparison
        comparison = await ai_service.compare_menu_items(
            [item.dict() for item in menu_items],
            comparison_criteria
        )
        
        return {
            "comparison": comparison.get("analysis", "Here's how these items compare..."),
            "winner": comparison.get("recommended_choice"),
            "pros_cons": comparison.get("pros_cons", {}),
            "criteria_scores": comparison.get("scores", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


# Helper functions
async def _generate_contextual_response(
    message: str, 
    preferences: Dict[str, Any],
    chat_history: List[Dict[str, str]]
) -> str:
    """Generate contextual AI response based on extracted preferences"""
    
    # Analyze the message type
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['protein', 'workout', 'gym', 'muscle']):
        min_protein = preferences.get('min_protein', 25)
        return f"Perfect! I found high-protein options that align with your fitness goals. I'm showing dishes with {min_protein}g+ protein to fuel your workouts."
    
    elif any(word in message_lower for word in ['healthy', 'clean', 'nutrition']):
        return "Great choice! I've curated healthy menu items with balanced nutrition and clean ingredients. Each item shows detailed nutrition facts to help you make informed decisions."
    
    elif any(word in message_lower for word in ['quick', 'fast', 'hurry', 'meeting']):
        return "I understand you're in a rush! Here are quick-prep options with short wait times, perfect for your busy schedule."
    
    elif any(word in message_lower for word in ['budget', 'cheap', 'affordable']):
        max_price = preferences.get('max_price', 15)
        return f"I've found great value options under ${max_price} that don't compromise on quality or taste. Smart choices for your budget!"
    
    elif any(word in message_lower for word in ['vegan', 'vegetarian', 'plant']):
        dietary_restrictions = preferences.get('dietary_restrictions', [])
        if dietary_restrictions and len(dietary_restrictions) > 0:
            # Handle simplified string format
            dietary = ', '.join(dietary_restrictions)
        else:
            dietary = 'plant-based'
        return f"Excellent! I'm showing you delicious {dietary} options with rich flavors and complete nutrition."
    
    # Check for food-specific requests
    food_items = preferences.get('food_items', [])
    if food_items:
        food_list = ', '.join(food_items)
        return f"Perfect! I found delicious {food_list} options for you. These dishes feature the ingredients you're craving."
    
    else:
        return "I've found some amazing dishes based on your preferences! Swipe right on items you love, and I'll learn your taste preferences to show better recommendations."


def _build_menu_search_from_preferences(
    preferences: Dict[str, Any],
    context: Dict[str, Any],
    user_id: Optional[str]
) -> MenuItemSearchRequest:
    """Convert extracted preferences to MenuItemSearchRequest"""
    
    # Build query string
    query_parts = []
    
    # Add food-specific items first (highest priority)
    food_items = preferences.get('food_items', [])
    if food_items:
        query_parts.extend(food_items)
    
    dietary_restrictions = preferences.get('dietary_restrictions', [])
    if dietary_restrictions:
        if isinstance(dietary_restrictions, list):
            # Handle simplified string format
            query_parts.extend(dietary_restrictions)
        else:
            query_parts.append(str(dietary_restrictions))
    
    if preferences.get('health_priority') == 'high':
        query_parts.append('healthy')
    if preferences.get('urgency') == 'high':
        query_parts.append('quick')
    
    query = ' '.join(query_parts) if query_parts else "recommended for you"
    
    # Build filters
    filters = {}
    if max_calories := preferences.get('max_calories'):
        filters['max_calories'] = max_calories
    if min_protein := preferences.get('min_protein'):
        filters['min_protein'] = min_protein
    if max_price := preferences.get('max_price'):
        filters['max_price'] = max_price
    if dietary_restrictions:
        filters['dietary_restrictions'] = dietary_restrictions
    
    # Build personalization
    personalization = {
        "user_id": user_id,
        "preferences": preferences,
        "context": context.get('meal_context', 'general')
    }
    
    return MenuItemSearchRequest(
        query=query,
        location=context.get('location', {"lat": 40.7580, "lng": -73.9855}),
        filters=filters,
        personalization=personalization,
        limit=20
    )


def _generate_search_reasoning(
    preferences: Dict[str, Any],
    search_result
) -> str:
    """Generate explanation for why these specific menu items were shown"""
    
    reasoning_parts = []
    
    # Check for food-specific requests
    food_items = preferences.get('food_items', [])
    if food_items:
        if isinstance(food_items, list):
            food_list = ', '.join(food_items)
        else:
            food_list = str(food_items)
        reasoning_parts.append(f"Food items: {food_list}")
    
    # Check for cuisine preferences
    cuisine = preferences.get('cuisine')
    if cuisine:
        reasoning_parts.append(f"{cuisine.title()} cuisine")
    
    # Check for meal type
    meal_type = preferences.get('meal_type')
    if meal_type:
        reasoning_parts.append(f"{meal_type} options")
    
    dietary_restrictions = preferences.get('dietary_restrictions', [])
    if dietary_restrictions:
        if isinstance(dietary_restrictions, list):
            # Handle simplified string format
            dietary = ', '.join(dietary_restrictions)
        else:
            dietary = str(dietary_restrictions)
        reasoning_parts.append(f"Filtered for {dietary} options")
    
    min_protein = preferences.get('min_protein')
    if min_protein:
        reasoning_parts.append(f"High protein content ({min_protein}g+)")
    
    max_calories = preferences.get('max_calories')
    if max_calories:
        reasoning_parts.append(f"Calorie-conscious ({max_calories} cal max)")
    
    if preferences.get('urgency') == 'high':
        reasoning_parts.append("Quick preparation time")
    
    if preferences.get('budget_friendly'):
        reasoning_parts.append("Budget-friendly options")
    
    if not reasoning_parts:
        reasoning_parts.append("Popular items in your area")
    
    total_results = getattr(search_result, 'meta', {}).get('total_results', 0)
    reasoning = f"Showing {total_results} items based on: " + ', '.join(reasoning_parts)
    
    return reasoning
