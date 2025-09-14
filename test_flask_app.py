#!/usr/bin/env python3
"""
Test Flask app startup
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_flask_app():
    """Test Flask app creation and database connectivity."""
    print("🧪 Testing Flask App Startup")
    print("=" * 40)
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        print(f"✅ Environment loaded")
        print(f"📊 Database URL: {os.getenv('DATABASE_URL', 'Not set')}")
        
        # Test Flask app creation
        from backend.app import create_app
        
        print("🚀 Creating Flask app...")
        app = create_app()
        
        print("✅ Flask app created successfully!")
        print(f"📊 Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
        
        # Test database connectivity within app context
        with app.app_context():
            from backend.models import db
            from sqlalchemy import text, inspect
            
            print("🔍 Testing database connection...")
            result = db.session.execute(text('SELECT 1')).scalar()
            print(f"✅ Database connectivity test: {result}")
            
            # Check tables
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Database has {len(tables)} tables: {tables[:5]}{'...' if len(tables) > 5 else ''}")
        
        print("\n🎉 Flask app is working correctly!")
        print("✅ Ready to start with: python run.py")
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_flask_app()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)
