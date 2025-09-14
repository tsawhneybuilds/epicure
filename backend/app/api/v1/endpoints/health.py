"""
Health data and Apple Health integration endpoints
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from app.schemas.user import HealthDataImportRequest, HealthDataImportResponse

router = APIRouter()

@router.post("/import", response_model=HealthDataImportResponse)
async def import_health_data(request: HealthDataImportRequest):
    """
    Import health data from Apple Health or Google Fit
    
    This endpoint processes health data and proposes profile updates
    """
    try:
        # Mock implementation for development
        profile_updates = {}
        proposed_extensions = []
        
        if request.source == "apple_health" and request.data:
            # Process Apple Health data
            basic_info = request.data.get("basic_info", {})
            activity = request.data.get("activity", {})
            nutrition = request.data.get("nutrition", {})
            
            # Update canonical fields
            if basic_info.get("age"):
                profile_updates["age"] = basic_info["age"]
            if basic_info.get("height_cm"):
                profile_updates["height_cm"] = basic_info["height_cm"]
            if basic_info.get("weight_kg"):
                profile_updates["weight_kg"] = basic_info["weight_kg"]
            if activity.get("activity_level"):
                profile_updates["activity_level"] = activity["activity_level"]
            
            # Generate proposed extensions
            if nutrition.get("avg_protein_g") and basic_info.get("weight_kg"):
                weight = basic_info["weight_kg"]
                target_protein = weight * 1.6  # 1.6g per kg for moderate activity
                
                proposed_extensions.append({
                    "key": "protein_target_g",
                    "value": target_protein,
                    "confidence": 0.85,
                    "reasoning": f"Based on your weight ({weight}kg) and activity level",
                    "status": "proposed"
                })
            
            if nutrition.get("avg_sodium_mg", 0) > 2300:
                proposed_extensions.append({
                    "key": "sodium_awareness",
                    "value": True,
                    "confidence": 0.70,
                    "reasoning": "Your sodium intake is above recommended limits",
                    "status": "proposed"
                })
        
        return HealthDataImportResponse(
            profile_updates={
                "canonical_fields": profile_updates,
                "proposed_extensions": proposed_extensions
            },
            proposed_extensions=proposed_extensions,
            requires_confirmation=len(proposed_extensions) > 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health data import failed: {str(e)}")

@router.get("/{user_id}/connections")
async def get_health_connections(user_id: str):
    """Get user's health data connections"""
    try:
        # Mock implementation
        mock_connections = [
            {
                "source": "apple_health",
                "status": "active",
                "scopes": ["basic_info", "activity", "nutrition"],
                "last_sync": "2024-01-01T12:00:00Z",
                "sync_frequency": "daily"
            }
        ]
        
        return {
            "connections": mock_connections,
            "total": len(mock_connections),
            "mock_data": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health connections fetch failed: {str(e)}")

@router.post("/{user_id}/sync")
async def sync_health_data(user_id: str, source: str = "apple_health"):
    """Trigger manual health data sync"""
    try:
        # Mock implementation
        return {
            "message": f"Health data sync initiated for {source}",
            "user_id": user_id,
            "source": source,
            "sync_id": "sync_12345",
            "estimated_completion": "2024-01-01T12:01:00Z",
            "mock_data": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health sync failed: {str(e)}")

@router.delete("/{user_id}/connections/{source}")
async def disconnect_health_source(user_id: str, source: str):
    """Disconnect health data source"""
    try:
        # Mock implementation
        return {
            "message": f"Health data source {source} disconnected",
            "user_id": user_id,
            "source": source,
            "status": "disconnected",
            "mock_data": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health disconnect failed: {str(e)}")

@router.get("/{user_id}/status")
async def get_health_sync_status(user_id: str):
    """Get health data sync status"""
    try:
        # Mock implementation
        return {
            "user_id": user_id,
            "last_sync": "2024-01-01T12:00:00Z",
            "sync_status": "completed",
            "next_sync": "2024-01-02T12:00:00Z",
            "data_freshness": "recent",
            "issues": [],
            "mock_data": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health status fetch failed: {str(e)}")

@router.post("/preview")
async def preview_health_import(request: HealthDataImportRequest):
    """
    Preview what would be imported from health data without saving
    
    Useful for onboarding flow to show user what will be imported
    """
    try:
        # Mock preview data
        preview = {
            "canonical_updates": {
                "age": 28,
                "weight_kg": 70.0,
                "height_cm": 175,
                "activity_level": "moderate"
            },
            "proposed_extensions": [
                {
                    "field": "protein_target_g", 
                    "value": 112,
                    "explanation": "Based on weight and activity level"
                },
                {
                    "field": "meal_timing_preference",
                    "value": "regular",
                    "explanation": "Based on typical eating patterns"
                }
            ],
            "data_quality": {
                "completeness": 0.85,
                "freshness": "last_7_days",
                "confidence": 0.90
            },
            "mock_data": True
        }
        
        return preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health preview failed: {str(e)}")

# Development/Debug endpoints
@router.get("/debug/mock-health-data")
async def get_mock_health_data():
    """Get sample health data for testing"""
    return {
        "basic_info": {
            "age": 28,
            "height_cm": 175,
            "weight_kg": 70.0,
            "biological_sex": "male"
        },
        "activity": {
            "activity_level": "moderate",
            "avg_daily_calories_burned": 2400,
            "workout_frequency": 4
        },
        "nutrition": {
            "avg_daily_calories": 2200,
            "avg_protein_g": 120,
            "avg_carbs_g": 250,
            "avg_fat_g": 75,
            "avg_sodium_mg": 2100
        },
        "note": "This is mock health data for development"
    }
