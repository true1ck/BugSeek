#!/usr/bin/env python3
"""
Database migration script to add AI analysis tables to existing BugSeek database.

This script safely adds the new AI-related tables without affecting existing data.
Run this after updating to the new version with AI features.
"""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.models import db, AIAnalysisResult, OpenAIStatus, SimilarLogMatch
from backend.app import create_app
from sqlalchemy import inspect, text


def check_table_exists(engine, table_name):
    """Check if a table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def migrate_database():
    """Add AI analysis tables to existing database."""
    print("=" * 60)
    print("BugSeek AI Tables Migration Script")
    print("=" * 60)
    print()
    
    # Create Flask app to get database context
    app = create_app('development')
    
    with app.app_context():
        try:
            # Check database connection
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Check existing tables
            engine = db.engine
            existing_tables = []
            new_tables = []
            
            # Check for AI analysis tables
            ai_tables = {
                'ai_analysis_results': AIAnalysisResult,
                'openai_status': OpenAIStatus,
                'similar_log_matches': SimilarLogMatch
            }
            
            for table_name, model in ai_tables.items():
                if check_table_exists(engine, table_name):
                    existing_tables.append(table_name)
                    print(f"ℹ️  Table '{table_name}' already exists")
                else:
                    new_tables.append(table_name)
                    print(f"📋 Table '{table_name}' will be created")
            
            if not new_tables:
                print("\n✅ All AI tables already exist. No migration needed.")
                return
            
            # Create new tables
            print("\n🔄 Creating new AI analysis tables...")
            
            # Create only the new tables
            for table_name, model in ai_tables.items():
                if table_name in new_tables:
                    try:
                        model.__table__.create(engine)
                        print(f"✅ Created table: {table_name}")
                    except Exception as e:
                        print(f"❌ Failed to create table {table_name}: {e}")
            
            # Verify all tables were created
            print("\n🔍 Verifying migration...")
            all_success = True
            for table_name in new_tables:
                if check_table_exists(engine, table_name):
                    print(f"✅ Table '{table_name}' successfully created")
                else:
                    print(f"❌ Table '{table_name}' was not created")
                    all_success = False
            
            if all_success:
                print("\n✅ Migration completed successfully!")
                
                # Initialize OpenAI status record
                try:
                    status = OpenAIStatus.get_current_status()
                    if not status:
                        print("\n📝 Creating initial OpenAI status record...")
                        status = OpenAIStatus(
                            IsConnected=False,
                            LastConnectionCheck=datetime.utcnow(),
                            TotalApiCalls=0,
                            TotalTokensUsed=0,
                            EstimatedTotalCost=0.0
                        )
                        db.session.add(status)
                        db.session.commit()
                        print("✅ OpenAI status record created")
                except Exception as e:
                    print(f"⚠️  Warning: Could not create initial status record: {e}")
            else:
                print("\n⚠️  Migration completed with some issues. Please check the errors above.")
            
            # Show summary
            print("\n" + "=" * 60)
            print("Migration Summary:")
            print(f"  - Tables already existed: {len(existing_tables)}")
            print(f"  - Tables created: {len(new_tables)}")
            print(f"  - Total AI tables: {len(ai_tables)}")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            print("\nPlease ensure:")
            print("  1. The database is accessible")
            print("  2. You have proper permissions")
            print("  3. The database configuration is correct")
            return False
    
    return True


def check_migration_status():
    """Check the current migration status."""
    app = create_app('development')
    
    with app.app_context():
        try:
            engine = db.engine
            
            print("\n📊 Current Database Status:")
            print("-" * 40)
            
            # Check core tables
            core_tables = ['error_logs', 'error_log_files']
            for table in core_tables:
                exists = check_table_exists(engine, table)
                status = "✅" if exists else "❌"
                print(f"{status} Core table: {table}")
            
            # Check AI tables
            ai_tables = ['ai_analysis_results', 'openai_status', 'similar_log_matches']
            for table in ai_tables:
                exists = check_table_exists(engine, table)
                status = "✅" if exists else "❌"
                print(f"{status} AI table: {table}")
            
            # Check for records
            print("\n📈 Record Counts:")
            print("-" * 40)
            
            try:
                from backend.models import ErrorLog
                log_count = ErrorLog.query.count()
                print(f"  Error Logs: {log_count}")
            except:
                print("  Error Logs: Unable to count")
            
            try:
                analysis_count = AIAnalysisResult.query.count()
                print(f"  AI Analyses: {analysis_count}")
            except:
                print("  AI Analyses: Unable to count")
            
            try:
                status = OpenAIStatus.get_current_status()
                if status:
                    print(f"  OpenAI Status: Connected={status.IsConnected}")
                else:
                    print("  OpenAI Status: No status record")
            except:
                print("  OpenAI Status: Unable to check")
            
        except Exception as e:
            print(f"❌ Failed to check status: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="BugSeek AI Tables Migration")
    parser.add_argument('--check', action='store_true', help='Check migration status without making changes')
    parser.add_argument('--force', action='store_true', help='Force migration even if tables exist')
    
    args = parser.parse_args()
    
    if args.check:
        check_migration_status()
    else:
        if migrate_database():
            print("\n✨ Your BugSeek database is now ready for AI features!")
            print("\nNext steps:")
            print("  1. Set your OpenAI API key in the .env file or environment variables")
            print("  2. Restart the BugSeek application")
            print("  3. Test the OpenAI connection from the dashboard")
        else:
            print("\n❌ Migration failed. Please check the errors and try again.")
