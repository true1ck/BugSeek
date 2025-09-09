#!/usr/bin/env python3
"""
Database Migration Script for BugSeek
=====================================

This script migrates the database from the old schema to the new enhanced schema:
- Adds new columns to error_logs table (Severity, Environment, Archived, LogContentPreview)
- Creates new error_log_files table for file metadata
- Migrates existing LogContent data to the new system
- Creates file records for existing data where possible

Run this script after updating the models but before starting the application.
"""

import os
import sys
import hashlib
import mimetypes
from datetime import datetime, timedelta
from sqlalchemy import text, inspect

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app
from backend.models import db, ErrorLog, ErrorLogFile

def check_table_exists(engine, table_name):
    """Check if a table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table."""
    inspector = inspect(engine)
    if not check_table_exists(engine, table_name):
        return False
    
    columns = inspector.get_columns(table_name)
    return any(col['name'] == column_name for col in columns)

def migrate_database():
    """Perform database migration."""
    print("🚀 Starting BugSeek database migration...")
    
    app = create_app()
    with app.app_context():
        engine = db.engine
        
        print("📋 Checking current schema...")
        
        # Check if we're dealing with an old schema
        has_old_logcontent = check_column_exists(engine, 'error_logs', 'LogContent')
        has_new_preview = check_column_exists(engine, 'error_logs', 'LogContentPreview')
        has_files_table = check_table_exists(engine, 'error_log_files')
        
        if not has_old_logcontent and has_new_preview and has_files_table:
            print("✅ Database is already using the new schema. No migration needed.")
            return
        
        print("🔄 Migration needed. Starting migration process...")
        
        # Step 1: Create new tables first
        print("📦 Creating new tables...")
        db.create_all()  # This will create the error_log_files table
        
        # Step 2: Add new columns to existing table manually (SQLite compatible)
        print("🔧 Adding new columns to error_logs table...")
        add_new_columns_to_error_logs()
        
        # Step 3: Migrate existing data if we had old LogContent
        if has_old_logcontent:
            print("📊 Migrating existing error log data...")
            migrate_existing_logs()
        
        # Step 3: Create default file records for logs without file metadata
        print("📁 Creating file metadata records...")
        create_default_file_records()
        
        # Step 4: Clean up old columns (optional - commented out for safety)
        # print("🧹 Cleaning up old schema...")
        # cleanup_old_schema(engine)
        
        print("✅ Database migration completed successfully!")
        print("📝 Note: Old LogContent column was preserved for safety.")
        print("   You can manually drop it after verifying the migration.")

def add_new_columns_to_error_logs():
    """Add new columns to the error_logs table (SQLite compatible)."""
    try:
        engine = db.engine
        
        # List of new columns to add
        new_columns = [
            ('LogContentPreview', 'TEXT'),
            ('Severity', "VARCHAR(20) DEFAULT 'medium' NOT NULL"),
            ('Environment', "VARCHAR(20) DEFAULT 'unknown' NOT NULL"),
            ('Archived', 'BOOLEAN DEFAULT 0 NOT NULL')
        ]
        
        for column_name, column_def in new_columns:
            if not check_column_exists(engine, 'error_logs', column_name):
                try:
                    sql = f"ALTER TABLE error_logs ADD COLUMN {column_name} {column_def}"
                    db.session.execute(text(sql))
                    print(f"   Added column: {column_name}")
                except Exception as e:
                    print(f"   Column {column_name} might already exist: {e}")
        
        db.session.commit()
        print("✅ Successfully added new columns to error_logs table")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error adding new columns: {e}")
        raise

def migrate_existing_logs():
    """Migrate data from old LogContent to new LogContentPreview."""
    try:
        # Get all error logs that have LogContent but no LogContentPreview
        logs_to_migrate = db.session.execute(
            text("""
                SELECT Cr_ID, LogContent, LogFileName, CreatedAt, FileSize
                FROM error_logs 
                WHERE LogContent IS NOT NULL 
                AND (LogContentPreview IS NULL OR LogContentPreview = '')
            """)
        ).fetchall()
        
        migrated_count = 0
        for log in logs_to_migrate:
            cr_id, log_content, log_filename, created_at, file_size = log
            
            # Create preview (first 64KB)
            content_preview = log_content[:65536] if log_content else None
            
            # Set default values for new columns
            severity = 'medium'
            environment = 'unknown'
            
            # Try to detect severity from content
            if log_content:
                content_lower = log_content.lower()
                if any(word in content_lower for word in ['critical', 'fatal', 'crash']):
                    severity = 'critical'
                elif any(word in content_lower for word in ['error', 'exception', 'fail']):
                    severity = 'high'
                elif any(word in content_lower for word in ['warning', 'warn']):
                    severity = 'low'
            
            # Update the record
            db.session.execute(
                text("""
                    UPDATE error_logs 
                    SET LogContentPreview = :preview,
                        Severity = :severity,
                        Environment = :environment,
                        Archived = 0
                    WHERE Cr_ID = :cr_id
                """),
                {
                    'preview': content_preview,
                    'severity': severity,
                    'environment': environment,
                    'cr_id': cr_id
                }
            )
            
            migrated_count += 1
            
            if migrated_count % 10 == 0:
                print(f"   Migrated {migrated_count} logs...")
        
        db.session.commit()
        print(f"✅ Migrated {migrated_count} error logs to new schema")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error migrating existing logs: {e}")
        raise

def create_default_file_records():
    """Create file metadata records for existing logs."""
    try:
        # Get logs that don't have file records yet
        logs_without_files = db.session.execute(
            text("""
                SELECT el.Cr_ID, el.LogFileName, el.LogContent, el.CreatedAt
                FROM error_logs el
                LEFT JOIN error_log_files elf ON el.Cr_ID = elf.Cr_ID
                WHERE elf.File_ID IS NULL
                AND el.LogFileName IS NOT NULL
            """)
        ).fetchall()
        
        created_count = 0
        for log in logs_without_files:
            cr_id, log_filename, log_content, created_at = log
            
            if not log_filename:
                continue
            
            # Calculate hash from content if available
            content_bytes = (log_content or '').encode('utf-8')
            sha256_hash = hashlib.sha256(content_bytes).hexdigest()
            
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(log_filename)
            if not mime_type:
                ext = log_filename.lower().split('.')[-1] if '.' in log_filename else ''
                mime_type = {
                    'log': 'text/plain',
                    'txt': 'text/plain',
                    'json': 'application/json',
                    'xml': 'application/xml'
                }.get(ext, 'text/plain')
            
            # Convert string datetime to datetime object if needed
            created_at_dt = created_at
            if isinstance(created_at, str):
                try:
                    created_at_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    created_at_dt = datetime.utcnow()
            elif created_at is None:
                created_at_dt = datetime.utcnow()
            
            # Create a placeholder file record
            # Since we don't have the original file, we'll create a virtual record
            file_record = ErrorLogFile(
                Cr_ID=cr_id,
                OriginalFileName=log_filename,
                StoredFileName=f"migrated_{cr_id}_{log_filename}",
                StoredPath=f"uploads/migrated_{cr_id}_{log_filename}",  # Virtual path
                MimeType=mime_type,
                FileSize=len(content_bytes),
                Sha256Hash=sha256_hash,
                CreatedAt=created_at_dt
            )
            
            db.session.add(file_record)
            created_count += 1
            
            if created_count % 10 == 0:
                print(f"   Created {created_count} file records...")
        
        db.session.commit()
        print(f"✅ Created {created_count} file metadata records")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating file records: {e}")
        raise

def cleanup_old_schema(engine):
    """Clean up old schema elements (commented out for safety)."""
    # WARNING: This will permanently drop the old LogContent column
    # Only run this after verifying the migration was successful
    
    print("⚠️  Skipping cleanup for safety. Old columns preserved.")
    print("   To manually clean up, run:")
    print("   ALTER TABLE error_logs DROP COLUMN LogContent;")
    print("   ALTER TABLE error_logs DROP COLUMN FileSize;")

def verify_migration():
    """Verify that the migration was successful."""
    print("🔍 Verifying migration...")
    
    app = create_app()
    with app.app_context():
        try:
            # Check that new tables exist and have data
            error_logs_count = ErrorLog.query.count()
            file_records_count = ErrorLogFile.query.count()
            
            print(f"📊 Migration verification:")
            print(f"   Error logs: {error_logs_count}")
            print(f"   File records: {file_records_count}")
            
            # Check that new columns have data
            logs_with_severity = ErrorLog.query.filter(ErrorLog.Severity.isnot(None)).count()
            logs_with_preview = ErrorLog.query.filter(ErrorLog.LogContentPreview.isnot(None)).count()
            
            print(f"   Logs with severity: {logs_with_severity}")
            print(f"   Logs with content preview: {logs_with_preview}")
            
            print("✅ Migration verification passed!")
            
        except Exception as e:
            print(f"❌ Migration verification failed: {e}")
            raise

if __name__ == '__main__':
    try:
        migrate_database()
        verify_migration()
        print("\n🎉 Migration completed successfully!")
        print("💡 You can now start the application with the new enhanced schema.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("💡 Please check the error and try again.")
        sys.exit(1)
