import sqlite3
import os

def check_db(db_path, name):
    print(f"\n=== Checking {name}: {db_path} ===")
    if not os.path.exists(db_path):
        print(f"❌ Database does not exist: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if error_logs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='error_logs'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print(f"❌ error_logs table does not exist in {name}")
        else:
            # Count records
            cursor.execute("SELECT COUNT(*) FROM error_logs")
            count = cursor.fetchone()[0]
            print(f"✅ error_logs table exists with {count} records in {name}")
            
            # Show first few records
            if count > 0:
                cursor.execute("SELECT TeamName, ErrorName, CreatedAt FROM error_logs LIMIT 3")
                records = cursor.fetchall()
                print("Sample records:")
                for i, (team, error, created) in enumerate(records, 1):
                    print(f"  {i}. {team} - {error} ({created})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking {name}: {e}")

# Check both databases
check_db("bugseek.db", "Root Database")
check_db("instance/bugseek.db", "Instance Database")
