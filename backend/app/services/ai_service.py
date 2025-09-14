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
            self.primary_model = "llama-3.1-70b-versatile"  # Updated model
            self.fallback_model = "llama-3.1-8b-instant"
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
        """Mock preference extraction - simplified and robust"""
        
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
        
        # Dietary restrictions - simplified to avoid parsing issues
        dietary = []
        if 'vegan' in message_lower:
            dietary.append('vegan')
        if 'vegetarian' in message_lower:
            dietary.append('vegetarian')
        if 'gluten' in message_lower:
            dietary.append('gluten-free')
        
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
        
        context_str = json.dumps(context) if context else "{}"
        prompt = f"""
        Analyze this food preference message with deep reasoning:
        Message: "{message}"
        Context: {context_str}
        
        Extract comprehensive preferences and return valid JSON:
        {{
            "budget": number or null,
            "health_priority": "low" | "medium" | "high",
            "portion_preference": "small" | "medium" | "large" | "filling",
            "dietary_restrictions": [{{"restriction": "string", "confidence": 0.0-1.0}}],
            "cuisine_preferences": ["string"],
            "urgency": "low" | "normal" | "high",
            "emotional_context": "comfort" | "energy" | "social" | "celebration" | "stress",
            "meal_timing_preference": "early" | "normal" | "late",
            "spice_tolerance": "mild" | "medium" | "hot",
            "cooking_method_preferences": ["grilled", "fried", "raw", "steamed"],
            "ingredient_quality_preference": ["organic", "grass-fed", "local"],
            "nutrition_goals": ["weight-loss", "muscle-gain", "maintenance"],
            "allergen_concerns": [{{"allergen": "string", "severity": "low" | "medium" | "high"}}],
            "texture_preferences": ["crunchy", "smooth", "chewy"]
        }}
        
        Analyze implicit preferences, cultural context, and unstated dietary needs.
        Return only valid JSON, no explanation.
        """
        
        try:
            # Try primary model first
            response = await self.client.chat.completions.create(
                model=self.primary_model,  # Use updated Llama 3.1 model
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
    
    async def process_search_refinement(self, refinement_message: str, current_filters: dict, current_results: list) -> dict:
        """Process user refinement of search results"""
        if self.use_mock:
            return {
                "explanation": "I've updated your search to focus more on your preferences.",
                "updated_query": "refined healthy options",
                "updated_filters": {**current_filters, "max_calories": 500},
                "changes_made": ["Reduced calorie limit", "Added healthy focus"]
            }
        else:
            # TODO: Implement real refinement processing with Groq
            return await self._process_refinement_with_groq(refinement_message, current_filters, current_results)
    
    async def explain_recommendation(self, menu_item: dict, user_preferences: dict, search_context: dict) -> dict:
        """Explain why a menu item was recommended"""
        if self.use_mock:
            item_name = menu_item.get('name', 'this item')
            protein = menu_item.get('protein', 0)
            dietary = menu_item.get('dietary', [])
            
            explanation = f"I recommended {item_name} because it "
            factors = []
            
            if protein >= 25:
                factors.append(f"has {protein}g protein (great for your fitness goals)")
            dietary_strings = [d.lower() if isinstance(d, str) else str(d).lower() for d in dietary]
            if 'vegetarian' in dietary_strings and user_preferences.get('dietary') == 'vegetarian':
                factors.append("matches your vegetarian preferences")
            if menu_item.get('calories', 999) <= 500:
                factors.append("is calorie-conscious")
            
            if not factors:
                factors.append("is popular and highly rated in your area")
            
            explanation += ", ".join(factors) + "."
            
            return {
                "explanation": explanation,
                "key_factors": factors,
                "nutrition_highlights": [f"{protein}g protein", f"{menu_item.get('calories')} calories"],
                "score": 0.85
            }
        else:
            # TODO: Implement real explanation with Groq
            return await self._explain_with_groq(menu_item, user_preferences, search_context)
    
    async def compare_menu_items(self, menu_items: list, criteria: list) -> dict:
        """Compare multiple menu items"""
        if self.use_mock:
            if len(menu_items) >= 2:
                item1, item2 = menu_items[0], menu_items[1]
                
                analysis = f"Comparing {item1['name']} vs {item2['name']}:\n\n"
                
                if 'nutrition' in criteria:
                    analysis += f"**Nutrition**: {item1['name']} has {item1.get('protein', 0)}g protein and {item1.get('calories', 0)} calories, "
                    analysis += f"while {item2['name']} has {item2.get('protein', 0)}g protein and {item2.get('calories', 0)} calories.\n"
                
                if 'price' in criteria:
                    analysis += f"**Price**: {item1['name']} costs ${item1.get('price', 0)}, {item2['name']} costs ${item2.get('price', 0)}.\n"
                
                # Simple recommendation logic
                recommended = item1['name'] if item1.get('protein', 0) > item2.get('protein', 0) else item2['name']
                
                return {
                    "analysis": analysis,
                    "recommended_choice": recommended,
                    "pros_cons": {
                        item1['name']: {"pros": ["Higher protein"], "cons": ["Higher calories"]},
                        item2['name']: {"pros": ["Lower calories"], "cons": ["Lower protein"]}
                    },
                    "scores": {
                        "nutrition": {item1['name']: 0.8, item2['name']: 0.7},
                        "price": {item1['name']: 0.6, item2['name']: 0.9}
                    }
                }
        else:
            # TODO: Implement real comparison with Groq
            return await self._compare_with_groq(menu_items, criteria)


# Global service instance
ai_service = AIService()
