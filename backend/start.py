#!/usr/bin/env python3
"""
Epicure Backend Startup Script
Easy development server startup with environment checks
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3.8, 0):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]}")

def check_environment():
    """Check environment variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ No .env file found. Using env.example as template...")
        if Path("env.example").exists():
            print("📝 Please copy env.example to .env and configure your keys:")
            print("   cp env.example .env")
            print("   # Edit .env with your API keys")
        return False
    
    # Load .env
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["SUPABASE_URL", "GROQ_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Set MOCK_DATA=true to run without external APIs")
        return False
    
    print("✅ Environment variables configured")
    return True

def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def test_imports():
    """Test if all imports work"""
    try:
        import fastapi
        import uvicorn
        import supabase
        import groq
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        return False

def start_server(host="0.0.0.0", port=8000, reload=True):
    """Start the FastAPI server"""
    print(f"🚀 Starting Epicure Backend API on {host}:{port}")
    print(f"📱 API Documentation: http://localhost:{port}/docs")
    print(f"🔧 Health Check: http://localhost:{port}/health")
    print("🛑 Press Ctrl+C to stop\n")
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")

def main():
    """Main startup sequence"""
    print("🍽️ Epicure Backend Startup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Run this script from the backend directory.")
        sys.exit(1)
    
    # Install dependencies if needed
    if not test_imports():
        if not install_dependencies():
            sys.exit(1)
        if not test_imports():
            sys.exit(1)
    
    # Check environment
    env_ok = check_environment()
    if not env_ok:
        print("\n💡 You can still run with mock data by setting MOCK_DATA=true")
        os.environ["MOCK_DATA"] = "true"
    
    print("\n🎯 Starting server...")
    start_server()

if __name__ == "__main__":
    main()
