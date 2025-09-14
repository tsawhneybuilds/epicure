#!/usr/bin/env python3
"""
Nutrition Inference Service using Llama-3.3-70B
Generate estimated macros and nutritional information for menu items
"""

import os
import json
import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

@dataclass
class NutritionInfo:
    calories: Optional[int]           # Total calories
    protein_g: Optional[float]        # Protein in grams
    carbs_g: Optional[float]         # Carbohydrates in grams
    fat_g: Optional[float]           # Fat in grams
    fiber_g: Optional[float]         # Fiber in grams
    sugar_g: Optional[float]         # Sugar in grams
    sodium_mg: Optional[int]         # Sodium in milligrams
    
    # Nutritional characteristics
    calories_per_100g: Optional[int]  # Caloric density
    protein_ratio: Optional[float]    # Protein as % of calories
    carb_ratio: Optional[float]       # Carbs as % of calories
    fat_ratio: Optional[float]        # Fat as % of calories
    
    # Confidence and metadata
    confidence: float                 # 0.0-1.0 confidence in estimates
    estimation_method: str           # How the estimate was derived
    portion_size_assumption: str     # Assumed portion size

class NutritionInferenceService:
    def __init__(self):
        """Initialize nutrition inference service"""
        self.groq_client = self._get_groq_client()
        print("🥗 Nutrition Inference Service initialized with Llama-3.3-70B")
    
    def _get_groq_client(self) -> Groq:
        """Initialize Groq client"""
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        return Groq(api_key=api_key)
    
    def estimate_nutrition(
        self, 
        item_name: str, 
        description: str = None, 
        price: float = None,
        restaurant_cuisine: str = None
    ) -> NutritionInfo:
        """Estimate nutritional information for a menu item"""
        
        # Build comprehensive context
        context_parts = [f"Menu item: {item_name}"]
        
        if description:
            context_parts.append(f"Description: {description}")
        
        if restaurant_cuisine:
            context_parts.append(f"Cuisine type: {restaurant_cuisine}")
        
        if price:
            context_parts.append(f"Price: ${price}")
        
        item_context = " | ".join(context_parts)
        
        system_prompt = """You are an expert nutritionist and food scientist with extensive knowledge of restaurant portions, cooking methods, and ingredient compositions. Your task is to provide accurate nutritional estimates for menu items.

CRITICAL: Respond with ONLY valid JSON. No explanation, no thinking, no extra text.

Consider these factors in your analysis:
1. Typical restaurant portion sizes for this type of dish
2. Cooking methods and how they affect calories (fried vs grilled vs steamed)
3. Common ingredients and their nutritional profiles
4. Regional cuisine characteristics and typical preparations
5. Price point as an indicator of portion size and quality ingredients
6. Hidden calories from sauces, oils, and preparation methods

IMPORTANT: Provide realistic, specific macro targets - avoid round numbers. Use realistic portions:
- Protein: 15-60g (aim for specific values like 23g, 31g, 47g)
- Carbs: 10-80g (specific values like 28g, 45g, 67g)
- Fat: 8-50g (specific values like 12g, 24g, 38g)
- Calories: Calculate as (protein_g * 4) + (carbs_g * 4) + (fat_g * 9)
- Fiber: 2-15g based on vegetables/grains
- Sodium: 300-1500mg based on preparation

Return this exact JSON structure:
{
    "calories": 450,
    "protein_g": 25.5,
    "carbs_g": 35.0,
    "fat_g": 18.5,
    "fiber_g": 4.0,
    "sugar_g": 8.0,
    "sodium_mg": 650,
    "calories_per_100g": 180,
    "protein_ratio": 0.23,
    "carb_ratio": 0.31,
    "fat_ratio": 0.37,
    "confidence": 0.85,
    "estimation_method": "ingredient-analysis",
    "portion_size_assumption": "standard restaurant serving"
}

Calculate protein_ratio = (protein_g * 4) / calories, carb_ratio = (carbs_g * 4) / calories, fat_ratio = (fat_g * 9) / calories

Estimation methods:
- "ingredient-analysis": Based on detailed ingredient breakdown
- "similar-dish": Based on comparison to similar known dishes
- "cuisine-typical": Based on typical preparations in this cuisine
- "basic-estimate": When limited information available

Confidence levels:
- 0.9-1.0: Very detailed description with cooking method
- 0.7-0.9: Good description with some cooking details
- 0.5-0.7: Basic description, estimated from cuisine type
- 0.3-0.5: Minimal information, rough estimates
- 0.1-0.3: Very uncertain, broad estimates

Portion size assumptions:
- "small-appetizer": 50-100g
- "standard-appetizer": 100-150g
- "large-appetizer": 150-250g
- "small-main": 200-300g
- "standard-main": 300-450g
- "large-main": 450-600g
- "sharing-portion": 600g+

Calculate ratios as decimal (protein_ratio = protein_calories / total_calories).
Be realistic about restaurant portions - they're typically larger than home cooking.
Account for cooking oils, butter, cream, and other calorie-dense additions commonly used in restaurants."""

        user_prompt = f"Analyze nutritional content for: {item_context}"
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse JSON response
            response_text = response.choices[0].message.content.strip()
            
            # Clean up response
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*$', '', response_text)
            response_text = response_text.strip()
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group()
            
            response_text = response_text.replace("'", '"')
            
            try:
                nutrition_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed for nutrition: {item_name}")
                print(f"   Response: {response_text[:100]}...")
                print(f"   Error: {e}")
                # Use intelligent fallback based on item type
                nutrition_data = self._fallback_nutrition_estimation(item_name, description, price)
            
            return NutritionInfo(
                calories=nutrition_data.get('calories'),
                protein_g=nutrition_data.get('protein_g'),
                carbs_g=nutrition_data.get('carbs_g'),
                fat_g=nutrition_data.get('fat_g'),
                fiber_g=nutrition_data.get('fiber_g'),
                sugar_g=nutrition_data.get('sugar_g'),
                sodium_mg=nutrition_data.get('sodium_mg'),
                calories_per_100g=nutrition_data.get('calories_per_100g'),
                protein_ratio=nutrition_data.get('protein_ratio'),
                carb_ratio=nutrition_data.get('carb_ratio'),
                fat_ratio=nutrition_data.get('fat_ratio'),
                confidence=nutrition_data.get('confidence', 0.5),
                estimation_method=nutrition_data.get('estimation_method', 'unknown'),
                portion_size_assumption=nutrition_data.get('portion_size_assumption', 'standard-main')
            )
            
        except Exception as e:
            print(f"❌ Error estimating nutrition for {item_name}: {e}")
            # Return minimal fallback
            return NutritionInfo(
                calories=None, protein_g=None, carbs_g=None, fat_g=None,
                fiber_g=None, sugar_g=None, sodium_mg=None,
                calories_per_100g=None, protein_ratio=None, carb_ratio=None, fat_ratio=None,
                confidence=0.0, estimation_method="error", portion_size_assumption="unknown"
            )
    
    def enhance_health_tags_with_macros(self, nutrition: NutritionInfo, existing_health_tags: list) -> list:
        """Add macro-based health tags to existing tags"""
        enhanced_tags = existing_health_tags.copy()
        
        if nutrition.confidence < 0.3:
            return enhanced_tags  # Don't add tags if nutrition data is very uncertain
        
        # Calorie-based tags
        if nutrition.calories:
            if nutrition.calories < 200:
                enhanced_tags.append('low-calorie')
            elif nutrition.calories > 600:
                enhanced_tags.append('high-calorie')
        
        # Protein-based tags
        if nutrition.protein_g:
            if nutrition.protein_g >= 25:
                enhanced_tags.append('high-protein')
            if nutrition.protein_ratio and nutrition.protein_ratio >= 0.25:
                enhanced_tags.append('protein-rich')
        
        # Carb-based tags
        if nutrition.carbs_g:
            if nutrition.carbs_g <= 10:
                enhanced_tags.append('low-carb')
                enhanced_tags.append('keto-friendly')
            elif nutrition.carbs_g <= 30:
                enhanced_tags.append('moderate-carb')
        
        # Fat-based tags
        if nutrition.fat_g:
            if nutrition.fat_g <= 5:
                enhanced_tags.append('low-fat')
            elif nutrition.fat_ratio and nutrition.fat_ratio >= 0.60:
                enhanced_tags.append('high-fat')
                enhanced_tags.append('keto-friendly')
        
        # Fiber-based tags
        if nutrition.fiber_g:
            if nutrition.fiber_g >= 5:
                enhanced_tags.append('high-fiber')
        
        # Sodium-based tags
        if nutrition.sodium_mg:
            if nutrition.sodium_mg <= 300:
                enhanced_tags.append('low-sodium')
            elif nutrition.sodium_mg >= 1000:
                enhanced_tags.append('high-sodium')
        
        # Macro ratio tags
        if nutrition.protein_ratio and nutrition.carb_ratio and nutrition.fat_ratio:
            if nutrition.fat_ratio >= 0.70 and nutrition.carbs_g and nutrition.carbs_g <= 20:
                enhanced_tags.append('ketogenic')
            elif nutrition.protein_ratio >= 0.30:
                enhanced_tags.append('high-protein-diet')
            elif nutrition.carb_ratio >= 0.60:
                enhanced_tags.append('carb-heavy')
        
        # Remove duplicates and return
        return list(set(enhanced_tags))
    
    def _fallback_nutrition_estimation(self, item_name: str, description: str = None, price: float = None) -> dict:
        """Intelligent fallback nutrition estimation based on food type keywords"""
        
        text = f"{item_name} {description or ''}".lower()
        
        # Base estimates for different food categories
        if any(word in text for word in ['salad', 'greens', 'vegetables']):
            # Light salad
            calories = 320
            protein_g = 18.5
            carbs_g = 24.0
            fat_g = 16.5
            fiber_g = 8.0
            sodium_mg = 480
            
        elif any(word in text for word in ['pizza']):
            # Pizza slice/portion
            calories = 680
            protein_g = 28.0
            carbs_g = 65.0
            fat_g = 32.0
            fiber_g = 4.5
            sodium_mg = 920
            
        elif any(word in text for word in ['burger', 'sandwich']):
            # Burger/sandwich
            calories = 750
            protein_g = 35.0
            carbs_g = 52.0
            fat_g = 38.0
            fiber_g = 3.5
            sodium_mg = 1100
            
        elif any(word in text for word in ['pasta', 'spaghetti', 'linguine']):
            # Pasta dish
            calories = 620
            protein_g = 24.0
            carbs_g = 78.0
            fat_g = 22.0
            fiber_g = 5.0
            sodium_mg = 750
            
        elif any(word in text for word in ['chicken', 'poultry']):
            # Chicken dish
            calories = 520
            protein_g = 45.0
            carbs_g = 18.0
            fat_g = 28.0
            fiber_g = 2.5
            sodium_mg = 680
            
        elif any(word in text for word in ['fish', 'salmon', 'tuna']):
            # Fish dish
            calories = 480
            protein_g = 42.0
            carbs_g = 15.0
            fat_g = 26.0
            fiber_g = 2.0
            sodium_mg = 620
            
        elif any(word in text for word in ['soup', 'broth']):
            # Soup
            calories = 280
            protein_g = 12.0
            carbs_g = 32.0
            fat_g = 11.0
            fiber_g = 4.0
            sodium_mg = 950
            
        elif any(word in text for word in ['dessert', 'cake', 'ice cream', 'chocolate']):
            # Dessert
            calories = 420
            protein_g = 6.5
            carbs_g = 54.0
            fat_g = 21.0
            fiber_g = 2.0
            sodium_mg = 180
            
        else:
            # Generic main dish
            calories = 550
            protein_g = 26.0
            carbs_g = 45.0
            fat_g = 28.0
            fiber_g = 4.0
            sodium_mg = 780
        
        # Adjust based on price if available
        if price:
            if price < 12:  # Smaller/cheaper items
                calories = int(calories * 0.8)
                protein_g = round(protein_g * 0.8, 1)
                carbs_g = round(carbs_g * 0.8, 1)
                fat_g = round(fat_g * 0.8, 1)
            elif price > 25:  # Larger/premium items
                calories = int(calories * 1.3)
                protein_g = round(protein_g * 1.3, 1)
                carbs_g = round(carbs_g * 1.3, 1)
                fat_g = round(fat_g * 1.3, 1)
        
        # Calculate ratios
        total_macro_calories = (protein_g * 4) + (carbs_g * 4) + (fat_g * 9)
        if total_macro_calories > 0:
            protein_ratio = round((protein_g * 4) / total_macro_calories, 2)
            carb_ratio = round((carbs_g * 4) / total_macro_calories, 2)
            fat_ratio = round((fat_g * 9) / total_macro_calories, 2)
        else:
            protein_ratio = 0.20
            carb_ratio = 0.35
            fat_ratio = 0.45
        
        return {
            "calories": calories,
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
            "fiber_g": fiber_g,
            "sugar_g": round(carbs_g * 0.3, 1),  # Estimate sugar as 30% of carbs
            "sodium_mg": sodium_mg,
            "calories_per_100g": int(calories * 0.4),  # Rough estimate
            "protein_ratio": protein_ratio,
            "carb_ratio": carb_ratio,
            "fat_ratio": fat_ratio,
            "confidence": 0.35,  # Lower confidence for fallback
            "estimation_method": "keyword-fallback",
            "portion_size_assumption": "standard-main"
        }

def test_nutrition_inference():
    """Test nutrition inference service"""
    
    print("🧪 Testing Nutrition Inference Service")
    print("=" * 50)
    
    service = NutritionInferenceService()
    
    test_items = [
        ("Margherita Pizza", "Fresh mozzarella, tomato sauce, basil", 18.0, "Italian"),
        ("Grilled Chicken Caesar Salad", "Romaine lettuce, grilled chicken, parmesan, croutons, caesar dressing", 16.0, "American"),
        ("Spicy Tuna Roll", "Fresh tuna, avocado, spicy mayo, seaweed", 14.0, "Japanese"),
        ("Quinoa Buddha Bowl", "Quinoa, roasted vegetables, chickpeas, tahini dressing", 15.0, "Mediterranean"),
        ("Double Cheeseburger", "Two beef patties, cheese, lettuce, tomato, special sauce", 22.0, "American")
    ]
    
    for name, description, price, cuisine in test_items:
        print(f"\n🍽️ Analyzing: {name}")
        print(f"Description: {description}")
        
        nutrition = service.estimate_nutrition(name, description, price, cuisine)
        
        print(f"📊 Nutrition (confidence: {nutrition.confidence:.2f}):")
        print(f"   Calories: {nutrition.calories}")
        print(f"   Protein: {nutrition.protein_g}g ({nutrition.protein_ratio:.1%} of calories)")
        print(f"   Carbs: {nutrition.carbs_g}g ({nutrition.carb_ratio:.1%} of calories)")
        print(f"   Fat: {nutrition.fat_g}g ({nutrition.fat_ratio:.1%} of calories)")
        print(f"   Fiber: {nutrition.fiber_g}g | Sodium: {nutrition.sodium_mg}mg")
        print(f"   Method: {nutrition.estimation_method}")
        print(f"   Portion: {nutrition.portion_size_assumption}")
        
        # Test health tag enhancement
        base_tags = ['vegetarian'] if 'vegetarian' in name.lower() else []
        enhanced_tags = service.enhance_health_tags_with_macros(nutrition, base_tags)
        print(f"   Enhanced health tags: {enhanced_tags}")

if __name__ == "__main__":
    test_nutrition_inference()
