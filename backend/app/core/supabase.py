"""
Supabase client configuration and utilities
"""

from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Global Supabase client instance
_supabase_client: Client = None

def get_supabase_client() -> Client:
    """Get or create Supabase client"""
    global _supabase_client
    
    if _supabase_client is None:
        try:
            _supabase_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    return _supabase_client

def get_supabase_anon_client() -> Client:
    """Get Supabase client with anon key (for public operations)"""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY
    )

async def test_connection() -> bool:
    """Test Supabase connection"""
    try:
        client = get_supabase_client()
        response = client.table('restaurants').select('id').limit(1).execute()
        return True
    except Exception as e:
        logger.error(f"Supabase connection test failed: {e}")
        return False
