"""
Epicure Backend API
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.supabase import get_supabase_client

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle app startup and shutdown"""
    # Startup
    print("🍽️ Starting Epicure Backend API...")
    
    # Test Supabase connection
    try:
        supabase = get_supabase_client()
        # Simple health check query
        response = supabase.table('restaurants').select('id').limit(1).execute()
        print("✅ Supabase connection successful")
    except Exception as e:
        print(f"⚠️ Supabase connection failed: {e}")
        print("📝 Running in mock data mode")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Epicure Backend API...")

# Create FastAPI app
app = FastAPI(
    title="Epicure API",
    description="Backend API for Epicure food recommendation system",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Epicure API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        supabase = get_supabase_client()
        # Test database connection
        response = supabase.table('restaurants').select('id').limit(1).execute()
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "environment": settings.ENVIRONMENT
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
