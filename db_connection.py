"""
Database Connection Utility Module
Provides database connection and configuration management for the CLI database viewer.
"""

import os
import sqlite3
import sys
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()

# Build absolute default path to use Flask instance directory (same as the app)
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(PROJECT_ROOT, 'instance')
DEFAULT_SQLITE_PATH = os.path.join(INSTANCE_DIR, 'bugseek.db')
# Normalize Windows paths for SQLite URI
if os.name == 'nt':  # Windows
    DEFAULT_SQLITE_URI = f"sqlite:///{DEFAULT_SQLITE_PATH.replace(chr(92), '/')}"
else:
    DEFAULT_SQLITE_URI = f"sqlite:///{DEFAULT_SQLITE_PATH}"

# Ensure instance directory exists
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR)

class DatabaseConnection:
    """Database connection manager with support for multiple database types."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database connection manager.
        
        Args:
            database_url: Optional database URL. If None, loads from environment.
        """
        # Force use of instance database if no explicit URL provided
        if database_url:
            self.database_url = database_url
        elif os.getenv('DATABASE_URL'):
            self.database_url = os.getenv('DATABASE_URL')
        else:
            self.database_url = DEFAULT_SQLITE_URI
        self.engine: Optional[Engine] = None
        self.session_factory = None
        self._metadata = None
        
    def connect(self) -> bool:
        """Establish database connection.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            self.engine = create_engine(self.database_url, echo=False)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.session_factory = sessionmaker(bind=self.engine)
            self._metadata = MetaData()
            self._metadata.reflect(bind=self.engine)
            
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return False
    
    def get_session(self):
        """Get a new database session."""
        if not self.session_factory:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.session_factory()
    
    def get_tables(self) -> List[str]:
        """Get list of all tables in the database.
        
        Returns:
            List[str]: List of table names.
        """
        if not self.engine:
            return []
        
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except Exception as e:
            print(f"❌ Error getting tables: {e}")
            return []
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table.
        
        Args:
            table_name: Name of the table.
            
        Returns:
            Dict containing table information.
        """
        if not self.engine:
            return {}
        
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            try:
                primary_key = inspector.get_primary_keys(table_name)
            except AttributeError:
                # For newer SQLAlchemy versions
                primary_key = inspector.get_pk_constraint(table_name).get('constrained_columns', [])
            
            return {
                'columns': columns,
                'indexes': indexes,
                'foreign_keys': foreign_keys,
                'primary_key': primary_key,
                'table_name': table_name
            }
        except Exception as e:
            print(f"❌ Error getting table info for {table_name}: {e}")
            return {}
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute a SQL query and return results.
        
        Args:
            query: SQL query to execute.
            params: Optional parameters for the query.
            
        Returns:
            List of dictionaries representing query results.
        """
        if not self.engine:
            return []
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                
                # For SELECT queries, fetch all results
                if query.strip().upper().startswith('SELECT'):
                    rows = result.fetchall()
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in rows]
                else:
                    # For other queries (INSERT, UPDATE, DELETE), commit and return affected row count
                    conn.commit()
                    return [{'affected_rows': result.rowcount}]
                    
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            return []
    
    def get_table_count(self, table_name: str) -> int:
        """Get the number of rows in a table.
        
        Args:
            table_name: Name of the table.
            
        Returns:
            Number of rows in the table.
        """
        try:
            result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
            return result[0]['count'] if result else 0
        except Exception:
            return 0
    
    def test_connection(self) -> bool:
        """Test if database connection is working.
        
        Returns:
            bool: True if connection is working, False otherwise.
        """
        if not self.engine:
            return False
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.session_factory = None
            self._metadata = None

def get_database_info() -> Dict[str, Any]:
    """Get general database information.
    
    Returns:
        Dict containing database information.
    """
    db = DatabaseConnection()
    if not db.connect():
        return {}
    
    info = {
        'database_url': db.database_url,
        'tables': [],
        'total_tables': 0,
        'connection_status': 'Connected' if db.test_connection() else 'Disconnected'
    }
    
    tables = db.get_tables()
    for table_name in tables:
        table_info = db.get_table_info(table_name)
        row_count = db.get_table_count(table_name)
        
        info['tables'].append({
            'name': table_name,
            'row_count': row_count,
            'column_count': len(table_info.get('columns', [])),
            'has_indexes': len(table_info.get('indexes', [])) > 0,
            'has_foreign_keys': len(table_info.get('foreign_keys', [])) > 0
        })
    
    info['total_tables'] = len(tables)
    db.close()
    
    return info

if __name__ == "__main__":
    # Quick test of database connection
    print("🔍 Testing Database Connection...")
    db = DatabaseConnection()
    
    print(f"🔗 Using database URL: {db.database_url}")
    
    if db.connect():
        print("✅ Database connection successful!")
        tables = db.get_tables()
        print(f"📊 Found {len(tables)} tables: {', '.join(tables)}")
        
        for table in tables:
            count = db.get_table_count(table)
            print(f"  • {table}: {count} rows")
        
        db.close()
    else:
        print("❌ Database connection failed!")
        sys.exit(1)
