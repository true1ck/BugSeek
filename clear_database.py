#!/usr/bin/env python3
"""
BugSeek - Database Clear Script
This script safely clears all data from the BugSeek database while preserving the schema.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def print_header():
    """Print script header."""
    print("=" * 70)
    print("🗑️  BugSeek - Database Clear Script")
    print("=" * 70)
    print("This script will clear all data from your BugSeek database.")
    print("The database schema will be preserved for future use.")
    print()

def print_success(message):
    """Print success message."""
    print(f"✅ {message}")

def print_error(message):
    """Print error message."""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message."""
    print(f"⚠️  {message}")

def print_info(message):
    """Print info message."""
    print(f"ℹ️  {message}")

def backup_database():
    """Create a backup of the current database."""
    try:
        db_paths = [
            Path("instance/bugseek.db"),
            Path("bugseek.db")
        ]
        
        backup_created = False
        for db_path in db_paths:
            if db_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = db_path.parent / f"{db_path.stem}_backup_{timestamp}{db_path.suffix}"
                
                shutil.copy2(db_path, backup_path)
                print_success(f"Database backed up to: {backup_path}")
                backup_created = True
        
        if not backup_created:
            print_warning("No database files found to backup")
        
        return backup_created
    
    except Exception as e:
        print_error(f"Failed to create backup: {e}")
        return False

def clear_database_tables():
    """Clear all data from database tables using SQLAlchemy."""
    try:
        # Import BugSeek components
        from backend.models import db, ErrorLog, ErrorLogFile, AIAnalysisResult, SimilarLogMatch, UserSolution, OpenAIStatus
        from backend.app import create_app
        
        # Create app context
        app = create_app()
        
        with app.app_context():
            print_info("Connecting to database...")
            
            # Get table counts before clearing
            counts = {}
            tables = [
                ("Error Logs", ErrorLog),
                ("Error Log Files", ErrorLogFile), 
                ("AI Analysis Results", AIAnalysisResult),
                ("Similar Log Matches", SimilarLogMatch),
                ("User Solutions", UserSolution),
                ("OpenAI Status", OpenAIStatus)
            ]
            
            for name, model in tables:
                try:
                    count = model.query.count()
                    counts[name] = count
                except Exception as e:
                    counts[name] = f"Error: {e}"
            
            print_info("Current database contents:")
            for name, count in counts.items():
                print(f"   • {name}: {count}")
            
            if sum(count for count in counts.values() if isinstance(count, int)) == 0:
                print_info("Database is already empty")
                return True
            
            print()
            print_warning("This will permanently delete all data from the database!")
            response = input("Are you sure you want to continue? (type 'yes' to confirm): ")
            
            if response.lower() != 'yes':
                print_info("Operation cancelled")
                return False
            
            print_info("Clearing database tables...")
            
            # Clear tables in correct order (respecting foreign key constraints)
            clear_order = [
                ("User Solutions", UserSolution),
                ("Similar Log Matches", SimilarLogMatch),
                ("AI Analysis Results", AIAnalysisResult),
                ("Error Log Files", ErrorLogFile),
                ("Error Logs", ErrorLog),
                ("OpenAI Status", OpenAIStatus)
            ]
            
            cleared_count = 0
            for name, model in clear_order:
                try:
                    count = model.query.count()
                    if count > 0:
                        model.query.delete()
                        cleared_count += count
                        print_success(f"Cleared {count} records from {name}")
                    else:
                        print_info(f"{name} was already empty")
                except Exception as e:
                    print_error(f"Failed to clear {name}: {e}")
            
            # Commit all changes
            db.session.commit()
            print_success(f"Successfully cleared {cleared_count} total records from database")
            
            return True
            
    except ImportError as e:
        print_error(f"Failed to import BugSeek modules: {e}")
        print_info("Make sure you're running this from the BugSeek project directory")
        return False
    except Exception as e:
        print_error(f"Database operation failed: {e}")
        return False

def clear_uploaded_files():
    """Clear uploaded files from the uploads directory."""
    try:
        uploads_dir = Path("uploads")
        
        if not uploads_dir.exists():
            print_info("No uploads directory found")
            return True
        
        files = list(uploads_dir.iterdir())
        if not files:
            print_info("Uploads directory is already empty")
            return True
        
        print_info(f"Found {len(files)} uploaded files")
        response = input("Do you want to delete uploaded files too? (y/n): ")
        
        if response.lower() in ['y', 'yes']:
            deleted_count = 0
            for file_path in files:
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        print_warning(f"Could not delete {file_path.name}: {e}")
            
            print_success(f"Deleted {deleted_count} uploaded files")
        else:
            print_info("Uploaded files were not deleted")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to clear uploaded files: {e}")
        return False

def verify_clear():
    """Verify that the database has been cleared."""
    try:
        from backend.models import db, ErrorLog, ErrorLogFile, AIAnalysisResult, SimilarLogMatch, UserSolution
        from backend.app import create_app
        
        app = create_app()
        
        with app.app_context():
            tables = [
                ("Error Logs", ErrorLog),
                ("Error Log Files", ErrorLogFile),
                ("AI Analysis Results", AIAnalysisResult),
                ("Similar Log Matches", SimilarLogMatch),
                ("User Solutions", UserSolution)
            ]
            
            print_info("Verifying database is clear:")
            all_empty = True
            
            for name, model in tables:
                try:
                    count = model.query.count()
                    if count == 0:
                        print_success(f"{name}: Empty ✅")
                    else:
                        print_error(f"{name}: Still has {count} records ❌")
                        all_empty = False
                except Exception as e:
                    print_warning(f"{name}: Could not verify ({e})")
            
            if all_empty:
                print_success("✅ Database successfully cleared!")
            else:
                print_error("❌ Some data may still remain in the database")
            
            return all_empty
            
    except Exception as e:
        print_error(f"Verification failed: {e}")
        return False

def main():
    """Main function."""
    print_header()
    
    # Check if we're in the right directory
    if not Path("run.py").exists():
        print_error("This script must be run from the BugSeek project root directory")
        print_info("Current directory: " + str(Path.cwd()))
        print_info("Expected files: run.py, backend/, frontend/")
        return False
    
    print_info("Script will perform the following actions:")
    print("   1. Create a backup of the current database")
    print("   2. Clear all data from database tables")
    print("   3. Optionally clear uploaded files")
    print("   4. Verify the database is empty")
    print()
    
    # Step 1: Backup
    print("Step 1: Creating backup...")
    backup_success = backup_database()
    
    if not backup_success:
        response = input("Backup failed. Continue anyway? (y/n): ")
        if response.lower() not in ['y', 'yes']:
            print_info("Operation cancelled")
            return False
    
    # Step 2: Clear database
    print("\nStep 2: Clearing database...")
    if not clear_database_tables():
        return False
    
    # Step 3: Clear uploaded files
    print("\nStep 3: Handling uploaded files...")
    clear_uploaded_files()
    
    # Step 4: Verify
    print("\nStep 4: Verification...")
    verify_clear()
    
    print("\n" + "=" * 70)
    print("🎉 Database clear operation completed!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("   • To add sample data: python 2_load_sample_data.py")
    print("   • To start fresh: python 1_initialize_database.py")
    print("   • To start BugSeek: python run.py")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
