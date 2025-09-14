#!/usr/bin/env python3
"""
BugSeek Setup Verification Script
Verifies that all configurations are properly set up
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    def load_dotenv():
        pass

def verify_setup():
    """Verify BugSeek setup and configuration"""
    
    print("=" * 60)
    print("🔍 BugSeek Setup Verification")
    print("=" * 60)
    
    # Check .env file
    env_path = Path('.env')
    if env_path.exists():
        print("✅ .env file exists")
        load_dotenv()
    else:
        print("❌ .env file missing")
        print("   Run: Copy-Item '.env.mediatek' '.env'")
        return False
    
    # Check required directories
    required_dirs = ['uploads', 'instance', 'logs', 'backend', 'frontend']
    print("\n📁 Directory Check:")
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ missing")
    
    # Check environment variables
    print("\n🔧 Environment Variables:")
    required_vars = {
        'DATABASE_URL': 'Database connection string',
        'SECRET_KEY': 'Flask secret key',
        'AZURE_API_KEY': 'MediaTek Azure OpenAI API key',
        'USER_ID': 'MediaTek employee ID',
        'ENDPOINT_URL': 'MediaTek gateway URL',
        'MODEL_NAME': 'AI model name',
        'API_VERSION': 'API version',
        'BACKEND_API_URL': 'Backend API URL'
    }
    
    all_configured = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != "" and "your_" not in value and "here" not in value:
            print(f"✅ {var}")
        else:
            print(f"⚠️  {var} needs configuration")
            if var in ['AZURE_API_KEY', 'USER_ID']:
                all_configured = False
    
    # Check database path
    db_url = os.getenv('DATABASE_URL', '')
    if db_url.startswith('sqlite:///instance/'):
        print("✅ Database path configured correctly (relative)")
    elif db_url.startswith('sqlite:///./instance/'):
        print("✅ Database path configured correctly (relative)")
    elif 'sqlite:///' in db_url and not db_url[10:].startswith('/'):
        print("✅ Database path configured (relative, will be resolved to absolute)")
    elif 'sqlite:///' in db_url:
        print("✅ Database path configured (absolute)")
    else:
        print("⚠️  Database path may need adjustment")
    
    # Check Python dependencies
    print("\n📦 Python Dependencies:")
    try:
        import flask
        print("✅ Flask available")
    except ImportError:
        print("❌ Flask not installed")
    
    try:
        import requests
        print("✅ Requests available")
    except ImportError:
        print("❌ Requests not installed")
    
    if DOTENV_AVAILABLE:
        print("✅ python-dotenv available")
    else:
        print("❌ python-dotenv not installed")
    
    # Status summary
    print("\n" + "=" * 60)
    if all_configured:
        print("🎉 Setup is complete!")
        print("✅ All critical configurations are set")
        print("\n🚀 Ready to start:")
        print("   python run.py")
    else:
        print("⚙️  Setup needs configuration:")
        print("1. Edit .env file with your actual MediaTek credentials:")
        print("   - AZURE_API_KEY=your_jwt_token_from_organizer")
        print("   - USER_ID=your_mtk_employee_id")
        print("2. Test connection: python test_mediatek_api.py")
        print("3. Start application: python run.py")
    
    print("\n🌐 Application URLs (when running):")
    print("   Frontend: http://localhost:8080")
    print("   Backend:  http://localhost:5000")
    print("   API Docs: http://localhost:5000/api/docs/")
    print("=" * 60)
    
    return all_configured

if __name__ == "__main__":
    verify_setup()
