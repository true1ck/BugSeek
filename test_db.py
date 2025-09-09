#!/usr/bin/env python3
"""
Simple test script to debug database creation
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from flask import Flask
from backend.models import db, ErrorLog
from config.settings import config

def test_database():
    """Test database creation and operations."""
    print("🔍 Testing Database Operations...")
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure the app
    app.config.from_object(config['development'])
    
    print(f"📊 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    with app.app_context():
        try:
            print("🗑️ Dropping all tables...")
            db.drop_all()
            
            print("📋 Creating all tables...")
            db.create_all()
            
            # Test creating a simple record
            print("➕ Adding test record...")
            test_log = ErrorLog(
                TeamName="Test Team",
                Module="Test Module", 
                Description="Test error log",
                Owner="test@example.com",
                LogFileName="test.log",
                ErrorName="TEST_ERROR",
                LogContent="This is a test error log",
                FileSize=100,
                SolutionPossible=True
            )
            
            db.session.add(test_log)
            print("💾 Committing to database...")
            db.session.commit()
            
            # Query back
            print("🔍 Querying records...")
            count = ErrorLog.query.count()
            print(f"✅ Found {count} records in database")
            
            # Show the record
            record = ErrorLog.query.first()
            if record:
                print(f"📋 Sample record: {record.TeamName} - {record.ErrorName}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    test_database()
