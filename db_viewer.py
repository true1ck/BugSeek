#!/usr/bin/env python3
"""
BugSeek Database Viewer CLI
A simple command-line tool to view and interact with your BugSeek database.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from db_connection import DatabaseConnection, get_database_info
from query_utils import QueryBuilder, get_common_queries
from backend.models import db, ErrorLog, create_tables
from flask import Flask
from config.settings import config

def create_app_context():
    """Create Flask app context for database operations."""
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    return app

def initialize_database():
    """Initialize database tables if they don't exist."""
    print("🔄 Initializing database...")
    try:
        app = create_app_context()
        with app.app_context():
            create_tables(app)
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def show_database_overview():
    """Show complete database overview."""
    print("\n" + "="*60)
    print("🗄️  BUGSEEK DATABASE OVERVIEW")
    print("="*60)
    
    db_info = get_database_info()
    
    if not db_info:
        print("❌ Could not connect to database")
        return
    
    print(f"📊 Database URL: {db_info['database_url']}")
    print(f"🔗 Connection: {db_info['connection_status']}")
    print(f"📋 Total Tables: {db_info['total_tables']}")
    
    if db_info['total_tables'] == 0:
        print("\n⚠️  No tables found. Database might need initialization.")
        return
    
    print("\n" + "-"*60)
    print("📊 TABLE DETAILS:")
    print("-"*60)
    
    for table in db_info['tables']:
        print(f"📋 {table['name']}")
        print(f"   • Rows: {table['row_count']:,}")
        print(f"   • Columns: {table['column_count']}")
        print(f"   • Has Indexes: {'Yes' if table['has_indexes'] else 'No'}")
        print(f"   • Has Foreign Keys: {'Yes' if table['has_foreign_keys'] else 'No'}")
        print()

def show_table_details(table_name):
    """Show detailed information about a specific table."""
    db = DatabaseConnection()
    if not db.connect():
        return
    
    print(f"\n🔍 DETAILED VIEW: {table_name.upper()}")
    print("="*60)
    
    # Get table info
    table_info = db.get_table_info(table_name)
    if not table_info:
        print(f"❌ Table '{table_name}' not found")
        return
    
    # Show columns
    print("📋 COLUMNS:")
    print("-"*40)
    for col in table_info['columns']:
        nullable = "NULL" if col.get('nullable', True) else "NOT NULL"
        print(f"  • {col['name']}: {col['type']} ({nullable})")
    
    # Show row count
    row_count = db.get_table_count(table_name)
    print(f"\n📊 RECORDS: {row_count:,} rows")
    
    # Show sample data if exists
    if row_count > 0:
        print("\n📄 SAMPLE DATA (First 3 rows):")
        print("-"*40)
        sample_query = f"SELECT * FROM {table_name} LIMIT 3"
        sample_data = db.execute_query(sample_query)
        
        if sample_data:
            # Show column headers
            headers = list(sample_data[0].keys())
            print(" | ".join(f"{h[:15]:<15}" for h in headers))
            print("-" * (17 * len(headers)))
            
            # Show data rows
            for row in sample_data:
                values = []
                for header in headers:
                    value = str(row.get(header, ''))
                    if len(value) > 15:
                        value = value[:12] + "..."
                    values.append(f"{value:<15}")
                print(" | ".join(values))
    
    db.close()

def run_common_queries(table_name):
    """Run common queries for a table."""
    db = DatabaseConnection()
    if not db.connect():
        return
    
    queries = get_common_queries(table_name)
    
    print(f"\n🔍 COMMON QUERIES FOR: {table_name.upper()}")
    print("="*60)
    
    for i, (query_name, query) in enumerate(queries.items(), 1):
        print(f"\n{i}. {query_name}")
        print("-" * len(query_name))
        
        try:
            results = db.execute_query(query)
            if results:
                if len(results) == 1 and 'total_count' in str(results[0]).lower():
                    # Count query
                    count_key = next(k for k in results[0].keys() if 'count' in k.lower())
                    print(f"   Result: {results[0][count_key]:,}")
                else:
                    # Regular query
                    print(f"   Found {len(results)} records")
                    if len(results) <= 5:
                        for result in results:
                            print(f"   • {result}")
                    else:
                        print(f"   • Showing first 3 of {len(results)}:")
                        for result in results[:3]:
                            print(f"     - {result}")
            else:
                print("   No results found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    db.close()

def show_menu():
    """Show main menu options."""
    print("\n" + "="*60)
    print("🔍 BUGSEEK DATABASE VIEWER")
    print("="*60)
    print("1. 📊 Show Database Overview")
    print("2. 🔧 Initialize Database (create tables)")
    print("3. 📋 View Table Details")
    print("4. 🔍 Run Common Queries")
    print("5. 💻 Custom SQL Query")
    print("6. 📤 Export Data")
    print("0. 🚪 Exit")
    print("-"*60)

def custom_query():
    """Execute a custom SQL query."""
    db = DatabaseConnection()
    if not db.connect():
        return
    
    print("\n💻 CUSTOM SQL QUERY")
    print("="*40)
    print("Enter your SQL query (or 'back' to return):")
    
    while True:
        query = input("\nSQL> ").strip()
        
        if query.lower() == 'back':
            break
        
        if not query:
            continue
        
        try:
            results = db.execute_query(query)
            if results:
                print(f"\n✅ Query executed successfully! Found {len(results)} result(s)")
                
                # Show results
                if len(results) <= 10:
                    for i, result in enumerate(results, 1):
                        print(f"{i}. {result}")
                else:
                    print("Showing first 10 results:")
                    for i, result in enumerate(results[:10], 1):
                        print(f"{i}. {result}")
                    print(f"... and {len(results) - 10} more")
            else:
                print("✅ Query executed successfully! No results returned.")
        except Exception as e:
            print(f"❌ Error executing query: {e}")
    
    db.close()

def export_data():
    """Export table data to file."""
    db = DatabaseConnection()
    if not db.connect():
        return
    
    tables = db.get_tables()
    if not tables:
        print("❌ No tables found to export")
        return
    
    print("\n📤 EXPORT DATA")
    print("="*30)
    print("Available tables:")
    for i, table in enumerate(tables, 1):
        row_count = db.get_table_count(table)
        print(f"{i}. {table} ({row_count:,} rows)")
    
    try:
        choice = int(input("\nSelect table to export (number): ")) - 1
        if 0 <= choice < len(tables):
            table_name = tables[choice]
            format_choice = input("Export format (csv/json): ").lower()
            
            if format_choice in ['csv', 'json']:
                # Get all data
                query = f"SELECT * FROM {table_name}"
                data = db.execute_query(query)
                
                if data:
                    from query_utils import QueryBuilder
                    qb = QueryBuilder(db)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{table_name}_export_{timestamp}.{format_choice}"
                    
                    if format_choice == 'csv':
                        success = qb.export_to_csv(data, filename)
                    else:
                        success = qb.export_to_json(data, filename)
                    
                    if success:
                        print(f"✅ Data exported to: {filename}")
                    else:
                        print("❌ Export failed")
                else:
                    print("❌ No data to export")
            else:
                print("❌ Invalid format. Choose 'csv' or 'json'")
        else:
            print("❌ Invalid table selection")
    except ValueError:
        print("❌ Invalid input")
    
    db.close()

def main():
    """Main CLI loop."""
    print("🔍 BugSeek Database Viewer")
    print("Current Database:", os.getenv('DATABASE_URL', 'sqlite:///bugseek.db'))
    
    while True:
        show_menu()
        
        try:
            choice = input("Choose an option: ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                show_database_overview()
            elif choice == '2':
                initialize_database()
            elif choice == '3':
                db = DatabaseConnection()
                if db.connect():
                    tables = db.get_tables()
                    if tables:
                        print("\nAvailable tables:")
                        for i, table in enumerate(tables, 1):
                            print(f"{i}. {table}")
                        try:
                            table_choice = int(input("Select table (number): ")) - 1
                            if 0 <= table_choice < len(tables):
                                show_table_details(tables[table_choice])
                            else:
                                print("❌ Invalid table selection")
                        except ValueError:
                            print("❌ Invalid input")
                    else:
                        print("❌ No tables found. Try initializing the database first.")
                    db.close()
                else:
                    print("❌ Could not connect to database")
            elif choice == '4':
                db = DatabaseConnection()
                if db.connect():
                    tables = db.get_tables()
                    if tables:
                        print("\nAvailable tables:")
                        for i, table in enumerate(tables, 1):
                            print(f"{i}. {table}")
                        try:
                            table_choice = int(input("Select table (number): ")) - 1
                            if 0 <= table_choice < len(tables):
                                run_common_queries(tables[table_choice])
                            else:
                                print("❌ Invalid table selection")
                        except ValueError:
                            print("❌ Invalid input")
                    else:
                        print("❌ No tables found. Try initializing the database first.")
                    db.close()
            elif choice == '5':
                custom_query()
            elif choice == '6':
                export_data()
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
