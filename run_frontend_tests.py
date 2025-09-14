#!/usr/bin/env python3
"""
Frontend Test Runner
Runs comprehensive tests to verify the conversational search functionality works properly
"""

import subprocess
import sys
import json
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_backend_running():
    """Check if the backend is running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Backend is running")
            return True
        else:
            logger.error(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Backend is not running: {str(e)}")
        return False

def run_test_script(script_name: str, description: str):
    """Run a test script and return results"""
    logger.info(f"\n🧪 Running {description}...")
    logger.info("=" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} PASSED")
            return True, result.stdout
        else:
            logger.error(f"❌ {description} FAILED")
            logger.error(f"Error output: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ {description} TIMED OUT")
        return False, "Test timed out after 2 minutes"
    except Exception as e:
        logger.error(f"💥 {description} CRASHED: {str(e)}")
        return False, str(e)

def main():
    """Main test runner"""
    logger.info("🚀 Starting Frontend Conversational Search Tests")
    logger.info("=" * 80)
    
    # Check if backend is running
    if not check_backend_running():
        logger.error("❌ Backend is not running. Please start the backend server first:")
        logger.error("   cd backend && python main.py")
        return 1
    
    # Test scripts to run
    tests = [
        ("test_frontend_conversational_search.py", "Frontend Integration Tests"),
        ("test_frontend_user_journey.py", "Frontend User Journey Tests"),
    ]
    
    results = []
    total_passed = 0
    
    for script_name, description in tests:
        if not Path(script_name).exists():
            logger.error(f"❌ Test script {script_name} not found")
            continue
            
        passed, output = run_test_script(script_name, description)
        results.append({
            "script": script_name,
            "description": description,
            "passed": passed,
            "output": output
        })
        
        if passed:
            total_passed += 1
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info(f"📊 Test Summary: {total_passed}/{len(tests)} test suites passed")
    
    if total_passed == len(tests):
        logger.info("🎉 ALL TESTS PASSED! The conversational search is working perfectly!")
        logger.info("\n✨ What this means:")
        logger.info("   • Users can type in the 'Continue the conversation' input")
        logger.info("   • The AI properly processes their requests")
        logger.info("   • Search results update based on the conversation")
        logger.info("   • Chat history is maintained correctly")
        logger.info("   • The frontend displays everything properly")
    else:
        logger.warning("⚠️  Some tests failed. Check the logs above for details.")
        logger.info("\n🔧 Troubleshooting tips:")
        logger.info("   • Make sure the backend is running on http://localhost:8000")
        logger.info("   • Check that the conversational AI endpoint is working")
        logger.info("   • Verify the database has menu items")
        logger.info("   • Check the backend logs for errors")
    
    # Save results
    with open("frontend_test_summary.json", "w") as f:
        json.dump({
            "timestamp": time.time(),
            "total_tests": len(tests),
            "passed": total_passed,
            "results": results
        }, f, indent=2)
    
    logger.info(f"\n📄 Test summary saved to frontend_test_summary.json")
    
    return 0 if total_passed == len(tests) else 1

if __name__ == "__main__":
    exit(main())
