"""
AI service for DeepSeek-V3 integration and text analysis
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from groq import AsyncGroq
from app.core.config import settings
from app.models.user import ExtractedPreferences
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered text analysis and preference extraction"""
    
    def __init__(self):
        self.use_mock = settings.MOCK_DATA or not settings.GROQ_API_KEY
        
        if not self.use_mock:
            self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            self.primary_model = "deepseek-v3"  # When available on Groq
            self.fallback_model = "llama3-70b-8192"
            self.speed_fallback = "mixtral-8x7b-32768"
            logger.info("AI Service initialized with Groq")
        else:
            logger.info("AI Service initialized with mock data")
    
    async def extract_preferences(self, message: str, context: Optional[Dict[str, Any]] = None) -> ExtractedPreferences:
        """Extract structured preferences from user message"""
        
        if self.use_mock:
            return await self._mock_extract_preferences(message, context)
        else:
            return await self._real_extract_preferences(message, context)
    
    async def analyze_menu_item(self, item_text: str) -> Dict[str, Any]:
        """Analyze menu item for dietary tags and properties"""
        
        if self.use_mock:
            return await self._mock_analyze_menu_item(item_text)
        else:
            return await self._real_analyze_menu_item(item_text)
    
    async def semantic_similarity(self, query: str, item_text: str) -> float:
        """Calculate semantic similarity between query and item"""
        
        if self.use_mock:
            return await self._mock_semantic_similarity(query, item_text)
        else:
            return await self._real_semantic_similarity(query, item_text)
    
    async def generate_response(self, user_message: str, extracted_prefs: ExtractedPreferences) -> str:
        """Generate conversational response"""
        
        if self.use_mock:
            return "I found some great options that match your preferences! Let me show you the results."
        else:
            return await self._real_generate_response(user_message, extracted_prefs)
    
    # Mock implementations for development
    async def _mock_extract_preferences(self, message: str, context: Optional[Dict[str, Any]] = None) -> ExtractedPreferences:
        """Mock preference extraction"""
        
        # Simple keyword-based mock extraction
        message_lower = message.lower()
        
        mock_prefs = ExtractedPreferences()
        
        # Budget detection
        if '$' in message:
            import re
            budget_match = re.search(r'\$(\d+)', message)
            if budget_match:
                mock_prefs.budget = float(budget_match.group(1))
        
        # Health priority
        if any(word in message_lower for word in ['healthy', 'nutrition', 'clean']):
            mock_prefs.health_priority = 'high'
        elif any(word in message_lower for word in ['comfort', 'indulge']):
            mock_prefs.health_priority = 'low'
        else:
            mock_prefs.health_priority = 'medium'
        
        # Dietary restrictions
        dietary = []
        if 'vegan' in message_lower:
            dietary.append({'restriction': 'vegan', 'confidence': 0.9})
        if 'vegetarian' in message_lower:
            dietary.append({'restriction': 'vegetarian', 'confidence': 0.9})
        if 'gluten' in message_lower:
            dietary.append({'restriction': 'gluten-free', 'confidence': 0.8})
        
        mock_prefs.dietary_restrictions = dietary if dietary else None
        
        # Urgency
        if any(word in message_lower for word in ['quick', 'fast', 'asap']):
            mock_prefs.urgency = 'high'
        elif any(word in message_lower for word in ['slow', 'leisurely']):
            mock_prefs.urgency = 'low'
        else:
            mock_prefs.urgency = 'normal'
        
        return mock_prefs
    
    async def _mock_analyze_menu_item(self, item_text: str) -> Dict[str, Any]:
        """Mock menu item analysis"""
        
        item_lower = item_text.lower()
        
        return {
            "dietary_tags": {
                "high_protein": {"confidence": 0.8 if 'protein' in item_lower or 'beef' in item_lower else 0.2},
                "vegan": {"confidence": 0.9 if 'vegan' in item_lower else 0.1},
                "gluten_free": {"confidence": 0.7 if 'quinoa' in item_lower or 'rice' in item_lower else 0.3}
            },
            "nutrition_profile": {
                "protein_level": "high" if any(word in item_lower for word in ['beef', 'chicken', 'protein']) else "medium",
                "carb_type": "complex" if 'quinoa' in item_lower else "simple"
            },
            "cooking_methods": ["grilled" if 'grilled' in item_lower else "mixed"],
            "meal_contexts": ["lunch", "healthy"],
            "mock_analysis": True
        }
    
    async def _mock_semantic_similarity(self, query: str, item_text: str) -> float:
        """Mock semantic similarity"""
        
        # Simple word overlap similarity
        query_words = set(query.lower().split())
        item_words = set(item_text.lower().split())
        
        overlap = len(query_words.intersection(item_words))
        union = len(query_words.union(item_words))
        
        return overlap / union if union > 0 else 0.0
    
    # Real AI implementations
    async def _real_extract_preferences(self, message: str, context: Optional[Dict[str, Any]] = None) -> ExtractedPreferences:
        """Real preference extraction using DeepSeek-V3/Llama3"""
        
        prompt = f"""
        Analyze this food preference message with deep reasoning:
        Message: "{message}"
        Context: {json.dumps(context) if context else "{}"}
        
        Extract comprehensive preferences and return valid JSON:
        {{
            "budget": number or null,
            "health_priority": "low" | "medium" | "high",
            "portion_preference": "small" | "medium" | "large" | "filling",
            "dietary_restrictions": [{"restriction": "string", "confidence": 0.0-1.0}],
            "cuisine_preferences": ["string"],
            "urgency": "low" | "normal" | "high",
            "emotional_context": "comfort" | "energy" | "social" | "celebration" | "stress",
            "meal_timing_preference": "early" | "normal" | "late",
            "spice_tolerance": "mild" | "medium" | "hot",
            "cooking_method_preferences": ["grilled", "fried", "raw", "steamed"],
            "ingredient_quality_preference": ["organic", "grass-fed", "local"],
            "nutrition_goals": ["weight-loss", "muscle-gain", "maintenance"],
            "allergen_concerns": [{"allergen": "string", "severity": "low" | "medium" | "high"}],
            "texture_preferences": ["crunchy", "smooth", "chewy"]
        }}
        
        Analyze implicit preferences, cultural context, and unstated dietary needs.
        Return only valid JSON, no explanation.
        """
        
        try:
            # Try primary model first
            response = await self.client.chat.completions.create(
                model=self.fallback_model,  # Use Llama3-70B since DeepSeek-V3 may not be available yet
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1024
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return ExtractedPreferences(**result)
            
        except Exception as e:
            logger.error(f"AI preference extraction failed: {e}")
            # Fallback to mock
            return await self._mock_extract_preferences(message, context)
    
    async def _real_analyze_menu_item(self, item_text: str) -> Dict[str, Any]:
        """Real menu item analysis using AI"""
        
        prompt = f"""
        Analyze this menu item description for detailed properties:
        Item: "{item_text}"
        
        Return JSON with analysis:
        {{
            "dietary_tags": {{
                "high_protein": {{"confidence": 0.0-1.0, "reason": "string"}},
                "vegan": {{"confidence": 0.0-1.0, "reason": "string"}},
                "gluten_free": {{"confidence": 0.0-1.0, "reason": "string"}},
                "keto_friendly": {{"confidence": 0.0-1.0, "reason": "string"}},
                "anti_inflammatory": {{"confidence": 0.0-1.0, "reason": "string"}}
            }},
            "nutrition_profile": {{
                "protein_level": "low" | "medium" | "high",
                "carb_type": "simple" | "complex" | "low",
                "fat_type": "saturated" | "healthy" | "mixed"
            }},
            "cooking_methods": ["string"],
            "allergen_info": {{
                "contains": ["string"],
                "free_from": ["string"]
            }},
            "meal_contexts": ["breakfast", "lunch", "dinner", "snack", "post_workout"],
            "ingredient_quality": ["organic", "grass_fed", "local", "processed"],
            "cuisine_influence": ["string"]
        }}
        
        Return only valid JSON.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.speed_fallback,  # Use Mixtral for speed
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            return json.loads(response.choices[0].message.content.strip())
            
        except Exception as e:
            logger.error(f"AI menu analysis failed: {e}")
            return await self._mock_analyze_menu_item(item_text)
    
    async def _real_semantic_similarity(self, query: str, item_text: str) -> float:
        """Real semantic similarity using AI"""
        
        prompt = f"""
        Rate semantic similarity between user query and menu item (0.0 to 1.0):
        
        User Query: "{query}"
        Menu Item: "{item_text}"
        
        Consider dietary preferences, cooking methods, nutritional goals, cuisine type.
        Return only a number between 0.0 and 1.0.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.speed_fallback,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            similarity = float(response.choices[0].message.content.strip())
            return max(0.0, min(1.0, similarity))  # Ensure bounds
            
        except Exception as e:
            logger.error(f"AI similarity calculation failed: {e}")
            return await self._mock_semantic_similarity(query, item_text)
    
    async def _real_generate_response(self, user_message: str, extracted_prefs: ExtractedPreferences) -> str:
        """Generate conversational response"""
        
        prompt = f"""
        Generate a friendly, helpful response to this user message about food preferences.
        
        User Message: "{user_message}"
        Extracted Preferences: {extracted_prefs.dict() if extracted_prefs else {}}
        
        Acknowledge their preferences and let them know you're finding matching restaurants.
        Keep it conversational and under 50 words.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.speed_fallback,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return "I found some great options that match your preferences! Let me show you the results."
