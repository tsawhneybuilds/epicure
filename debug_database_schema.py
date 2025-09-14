#!/usr/bin/env python3
"""
Debug the database schema to see what fields are available for semantic search
"""

import sys
import os
sys.path.append('backend')

from backend.app.core.supabase import get_supabase_client
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_database_schema():
    """Debug the database schema"""
    try:
        logger.info("🔍 Debugging database schema...")
        
        client = get_supabase_client()
        
        # Get a sample item to see all available fields
        logger.info("Getting sample menu item to see all fields...")
        response = client.table('menu_items').select('*').limit(1).execute()
        
        if response.data:
            sample_item = response.data[0]
            logger.info("Available fields in menu_items table:")
            for field, value in sample_item.items():
                logger.info(f"  {field}: {type(value).__name__} = {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
        
        # Check if there are any vector/embedding fields
        logger.info("\nChecking for vector/embedding fields...")
        vector_fields = [field for field in sample_item.keys() if 'vector' in field.lower() or 'embedding' in field.lower() or 'semantic' in field.lower()]
        if vector_fields:
            logger.info(f"Found vector/embedding fields: {vector_fields}")
        else:
            logger.info("No vector/embedding fields found")
        
        # Check for tagging fields
        logger.info("\nChecking for tagging fields...")
        tag_fields = [field for field in sample_item.keys() if 'tag' in field.lower() or 'inferred' in field.lower()]
        if tag_fields:
            logger.info(f"Found tagging fields: {tag_fields}")
            for field in tag_fields:
                logger.info(f"  {field}: {sample_item.get(field)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_database_schema()
