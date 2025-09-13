#!/usr/bin/env python3
"""
Simple database creation script for BugSeek
Creates the database and tables without dropping existing ones
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def create_database():
    """Create the BugSeek database and tables."""
    print("=" * 50)
    print("🔧 BugSeek Database Creation")
    print("=" * 50)
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        print(f"✅ Environment loaded from .env file")
        print(f"📊 Database URL: {os.getenv('DATABASE_URL', 'Not set')}")
        
        # Import Flask app and models
        from flask import Flask
        from backend.models import db, create_tables
        from config.settings import config
        
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(config['development'])
        
        # Initialize SQLAlchemy
        db.init_app(app)
        
        with app.app_context():
            print("🏗️  Creating database tables...")
            
            # Use create_all instead of drop_all to avoid errors if DB doesn't exist
            create_tables(app)
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"✅ Successfully created {len(tables)} tables:")
                for i, table in enumerate(tables, 1):
                    print(f"   {i}. {table}")
                
                print("\n🎉 Database creation completed successfully!")
                return True
            else:
                print("❌ No tables were created!")
                return False
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False

def test_database_connection():
    """Test the database connection."""
    print("\n" + "=" * 30)
    print("🧪 Testing Database Connection")
    print("=" * 30)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from flask import Flask
        from backend.models import db
        from config.settings import config
        
        app = Flask(__name__)
        app.config.from_object(config['development'])
        db.init_app(app)
        
        with app.app_context():
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1')).scalar()
            print(f"✅ Database connectivity test: {result}")
            
            # Check if we can create a simple table
            db.session.execute(text('CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY)'))
            db.session.execute(text('DROP TABLE IF EXISTS test_table'))
            db.session.commit()
            
            print("✅ Database read/write operations working")
            return True
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def main():
    """Main function."""
    print("🚀 BugSeek Database Setup")
    print("This script will create the database and verify it's working\n")
    
    # Step 1: Create database
    if not create_database():
        print("\n❌ Database creation failed!")
        return False
    
    # Step 2: Test connection
    if not test_database_connection():
        print("\n❌ Database connection test failed!")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 DATABASE SETUP COMPLETE!")
    print("=" * 50)
    print("✅ Your BugSeek database is ready to use!")
    print("\n📍 Database location:")
    print(f"   {os.path.abspath('instance/bugseek.db')}")
    print("\n🚀 Next steps:")
    print("   1. Start the application: python run.py")
    print("   2. Access frontend: http://localhost:8080")
    print("   3. Upload error logs via the web interface")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed! Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ Ready to go!")
        sys.exit(0)
