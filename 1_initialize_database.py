#!/usr/bin/env python3
"""
1_initialize_database.py
Initialize BugSeek database with proper schema and tables
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def initialize_database():
    """Initialize the BugSeek database with all required tables."""
    print("=" * 60)
    print("BugSeek Database Initialization")
    print("=" * 60)
    print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from flask import Flask
        from backend.models import db, create_tables, ErrorLog, ErrorLogFile, AIAnalysisResult, OpenAIStatus, SimilarLogMatch
        from config.settings import config
        
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(config['development'])
        
        print(f"[INFO] Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Initialize SQLAlchemy
        db.init_app(app)
        
        with app.app_context():
            print("[INFO] Dropping existing tables...")
            db.drop_all()
            
            print("[INFO] Creating all database tables...")
            create_tables(app)
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"[OK] Successfully created {len(tables)} tables:")
                for i, table in enumerate(tables, 1):
                    print(f"   {i}. {table}")
                    
                    # Show table details
                    columns = inspector.get_columns(table)
                    indexes = inspector.get_indexes(table)
                    print(f"      - Columns: {len(columns)}")
                    print(f"      - Indexes: {len(indexes)}")
                    
                    # Show some column details
                    key_columns = [col['name'] for col in columns if col.get('primary_key') or col['name'].endswith('_ID')]
                    if key_columns:
                        print(f"      - Key columns: {', '.join(key_columns)}")
                    print()
                
                print("[SUCCESS] Database initialization completed successfully!")
                return True
            else:
                print("[ERROR] No tables were created!")
                return False
                
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_database_structure():
    """Verify the database structure is correct."""
    print("\n" + "=" * 40)
    print("Database Structure Verification")
    print("=" * 40)
    
    try:
        from flask import Flask
        from backend.models import db
        from config.settings import config
        
        app = Flask(__name__)
        app.config.from_object(config['development'])
        db.init_app(app)
        
        with app.app_context():
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            
            # Test basic connectivity
            result = db.session.execute(text('SELECT 1')).scalar()
            print(f"[OK] Database connectivity test: {result}")
            
            # Check required tables
            required_tables = [
                'error_logs',
                'error_log_files', 
                'ai_analysis_results',
                'openai_status',
                'similar_log_matches'
            ]
            
            existing_tables = inspector.get_table_names()
            print(f"\n[INFO] Found {len(existing_tables)} tables:")
            
            for table in required_tables:
                if table in existing_tables:
                    print(f"   [OK] {table}")
                else:
                    print(f"   [MISSING] {table}")
            
            # Check for any unexpected tables
            extra_tables = [t for t in existing_tables if t not in required_tables]
            if extra_tables:
                print(f"\n[INFO] Additional tables found: {', '.join(extra_tables)}")
            
            return len([t for t in required_tables if t in existing_tables]) == len(required_tables)
            
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return False

def create_directories():
    """Create necessary directories for the application."""
    print("\n" + "=" * 40)
    print("Creating Required Directories")
    print("=" * 40)
    
    directories = [
        "backend/instance",
        "uploads",
        "logs",
        "exports",
        "temp"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"[OK] Created directory: {directory}")
        else:
            print(f"[OK] Directory exists: {directory}")

def main():
    """Main initialization function."""
    print("BugSeek Database Initializer")
    print("This script will initialize your database with proper schema")
    print()
    
    # Step 1: Create directories
    create_directories()
    
    # Step 2: Initialize database
    if not initialize_database():
        print("\n[ERROR] Database initialization failed!")
        return False
    
    # Step 3: Verify structure
    if not verify_database_structure():
        print("\n[ERROR] Database structure verification failed!")
        return False
    
    print("\n" + "=" * 60)
    print("INITIALIZATION COMPLETE")
    print("=" * 60)
    print("[SUCCESS] Your BugSeek database is ready!")
    print("\nNext steps:")
    print("1. Run: python 2_load_sample_data.py")
    print("2. Or load your own data with the API")
    print("3. Start the application: python run.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n[ERROR] Initialization failed! Please check the errors above.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Database is ready for use!")
        sys.exit(0)
