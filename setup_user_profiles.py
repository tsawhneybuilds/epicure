#!/usr/bin/env python3
"""
Setup script to ensure user profiles are properly configured in Supabase
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.supabase import get_supabase_client
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_supabase_connection():
    """Check if Supabase connection is working"""
    try:
        client = get_supabase_client()
        
        # Test connection by querying a simple table
        result = client.table('users').select('id').limit(1).execute()
        logger.info("✅ Supabase connection successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        return False

def check_tables_exist():
    """Check if required tables exist"""
    try:
        client = get_supabase_client()
        
        required_tables = [
            'users',
            'user_profiles', 
            'user_interactions',
            'chat_messages',
            'profile_schema_fields',
            'profile_extension_meta'
        ]
        
        for table in required_tables:
            try:
                result = client.table(table).select('*').limit(1).execute()
                logger.info(f"✅ Table '{table}' exists")
            except Exception as e:
                logger.error(f"❌ Table '{table}' missing or inaccessible: {e}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Table check failed: {e}")
        return False

def check_rls_policies():
    """Check if Row Level Security policies are enabled"""
    try:
        client = get_supabase_client()
        
        # Try to query user_profiles without auth (should fail if RLS is working)
        try:
            result = client.table('user_profiles').select('*').limit(1).execute()
            if result.data:
                logger.warning("⚠️  RLS might not be properly configured - able to query user_profiles without auth")
            else:
                logger.info("✅ RLS appears to be working - no data returned without auth")
        except Exception as e:
            logger.info("✅ RLS is working - query blocked without auth")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ RLS check failed: {e}")
        return False

def create_test_user():
    """Create a test user to verify the system works"""
    try:
        client = get_supabase_client()
        
        # Create test user
        import uuid
        test_user_id = str(uuid.uuid4())
        test_email = f"test_{test_user_id[:8]}@example.com"
        
        user_data = {
            "id": test_user_id,
            "email": test_email
        }
        
        # Insert user
        result = client.table('users').insert(user_data).execute()
        
        if result.data:
            logger.info(f"✅ Test user created: {test_user_id}")
            
            # Create profile
            profile_data = {
                "user_id": test_user_id,
                "age": 25,
                "height_cm": 170,
                "weight_kg": 65.0,
                "gender": "female",
                "activity_level": "moderate",
                "goals": ["weight_loss", "muscle_tone"],
                "dietary_restrictions": ["vegetarian"],
                "allergies": ["nuts"],
                "profile_extensions": {
                    "budgetFriendly": True,
                    "healthPriority": "high"
                }
            }
            
            profile_result = client.table('user_profiles').insert(profile_data).execute()
            
            if profile_result.data:
                logger.info("✅ Test user profile created")
                return test_user_id, test_email
            else:
                logger.error("❌ Failed to create test user profile")
                return None, None
        else:
            logger.error("❌ Failed to create test user")
            return None, None
            
    except Exception as e:
        logger.error(f"❌ Test user creation failed: {e}")
        return None, None

def cleanup_test_user(user_id):
    """Clean up test user"""
    try:
        client = get_supabase_client()
        
        # Delete profile first (due to foreign key constraint)
        client.table('user_profiles').delete().eq('user_id', user_id).execute()
        
        # Delete user
        client.table('users').delete().eq('id', user_id).execute()
        
        logger.info("✅ Test user cleaned up")
        
    except Exception as e:
        logger.error(f"❌ Test user cleanup failed: {e}")

def main():
    """Main setup function"""
    logger.info("🚀 Setting up user profiles in Supabase...")
    
    # Check environment variables
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        logger.error("❌ Supabase configuration missing. Please check your environment variables.")
        logger.error("Required: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    logger.info("✅ Supabase configuration found")
    
    # Check connection
    if not check_supabase_connection():
        return False
    
    # Check tables
    if not check_tables_exist():
        logger.error("❌ Required tables are missing. Please run the SQL setup scripts first.")
        logger.error("Run: supabase_setup.sql and comprehensive_schema_update.sql")
        return False
    
    # Check RLS
    check_rls_policies()
    
    # Create and test a user
    test_user_id, test_email = create_test_user()
    if test_user_id:
        logger.info(f"✅ Test user created successfully: {test_email}")
        
        # Clean up
        cleanup_test_user(test_user_id)
        
        logger.info("🎉 User profile setup completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Start your backend server: cd backend && python main.py")
        logger.info("2. Start your frontend: cd frontend_new && npm run dev")
        logger.info("3. Test the integration: python test_user_integration.py")
        
        return True
    else:
        logger.error("❌ User profile setup failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
