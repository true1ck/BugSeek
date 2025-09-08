"""
Query Builder Utility Module
Provides utility functions for building and executing common database queries.
"""

import json
import csv
import os
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from db_connection import DatabaseConnection

class QueryBuilder:
    """Utility class for building and executing database queries."""
    
    def __init__(self, db_connection: DatabaseConnection):
        """Initialize QueryBuilder with a database connection.
        
        Args:
            db_connection: Active database connection instance.
        """
        self.db = db_connection
    
    def build_select_query(self, table: str, columns: Optional[List[str]] = None, 
                          where_conditions: Optional[Dict[str, Any]] = None,
                          order_by: Optional[str] = None, 
                          limit: Optional[int] = None,
                          offset: Optional[int] = None) -> str:
        """Build a SELECT query with various options.
        
        Args:
            table: Table name to query.
            columns: List of columns to select. If None, selects all (*).
            where_conditions: Dict of column:value conditions for WHERE clause.
            order_by: Column name to order by.
            limit: Maximum number of rows to return.
            offset: Number of rows to skip.
            
        Returns:
            SQL query string.
        """
        # Build column list
        if columns:
            column_str = ", ".join(columns)
        else:
            column_str = "*"
        
        query = f"SELECT {column_str} FROM {table}"
        
        # Add WHERE clause
        if where_conditions:
            conditions = []
            for column, value in where_conditions.items():
                if isinstance(value, str):
                    conditions.append(f"{column} = '{value}'")
                elif value is None:
                    conditions.append(f"{column} IS NULL")
                else:
                    conditions.append(f"{column} = {value}")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        # Add ORDER BY
        if order_by:
            query += f" ORDER BY {order_by}"
        
        # Add LIMIT and OFFSET
        if limit:
            query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"
        
        return query
    
    def search_table(self, table: str, search_term: str, 
                    search_columns: Optional[List[str]] = None) -> List[Dict]:
        """Search for a term across specified columns in a table.
        
        Args:
            table: Table name to search in.
            search_term: Term to search for.
            search_columns: Columns to search in. If None, searches all text columns.
            
        Returns:
            List of matching rows.
        """
        if not search_columns:
            # Get table info to find text columns
            table_info = self.db.get_table_info(table)
            text_types = ['VARCHAR', 'TEXT', 'CHAR', 'STRING']
            search_columns = []
            
            for col in table_info.get('columns', []):
                col_type = str(col.get('type', '')).upper()
                if any(text_type in col_type for text_type in text_types):
                    search_columns.append(col['name'])
        
        if not search_columns:
            return []
        
        # Build search conditions
        search_conditions = []
        for column in search_columns:
            search_conditions.append(f"{column} LIKE '%{search_term}%'")
        
        query = f"SELECT * FROM {table} WHERE {' OR '.join(search_conditions)}"
        return self.db.execute_query(query)
    
    def get_recent_records(self, table: str, date_column: str = 'CreatedAt',
                          days: int = 7, limit: int = 100) -> List[Dict]:
        """Get recent records from a table.
        
        Args:
            table: Table name.
            date_column: Column name containing the date.
            days: Number of days to look back.
            limit: Maximum number of records to return.
            
        Returns:
            List of recent records.
        """
        # Calculate date threshold
        threshold_date = datetime.now() - timedelta(days=days)
        threshold_str = threshold_date.strftime('%Y-%m-%d %H:%M:%S')
        
        query = f"""
        SELECT * FROM {table} 
        WHERE {date_column} >= '{threshold_str}'
        ORDER BY {date_column} DESC
        LIMIT {limit}
        """
        
        return self.db.execute_query(query)
    
    def get_table_statistics(self, table: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a table.
        
        Args:
            table: Table name.
            
        Returns:
            Dict containing table statistics.
        """
        stats = {
            'table_name': table,
            'total_rows': 0,
            'column_stats': {},
            'sample_data': []
        }
        
        # Get total row count
        stats['total_rows'] = self.db.get_table_count(table)
        
        # Get table info
        table_info = self.db.get_table_info(table)
        columns = table_info.get('columns', [])
        
        # Get sample data (first 5 rows)
        sample_query = f"SELECT * FROM {table} LIMIT 5"
        stats['sample_data'] = self.db.execute_query(sample_query)
        
        # Get column statistics
        for column in columns:
            col_name = column['name']
            col_type = str(column['type']).upper()
            
            col_stats = {
                'type': col_type,
                'nullable': column.get('nullable', True),
                'unique_count': 0,
                'null_count': 0
            }
            
            # Count unique values
            unique_query = f"SELECT COUNT(DISTINCT {col_name}) as unique_count FROM {table}"
            unique_result = self.db.execute_query(unique_query)
            if unique_result:
                col_stats['unique_count'] = unique_result[0]['unique_count']
            
            # Count null values
            null_query = f"SELECT COUNT(*) as null_count FROM {table} WHERE {col_name} IS NULL"
            null_result = self.db.execute_query(null_query)
            if null_result:
                col_stats['null_count'] = null_result[0]['null_count']
            
            # For numeric columns, get min/max/avg
            if any(num_type in col_type for num_type in ['INTEGER', 'FLOAT', 'DECIMAL', 'NUMERIC']):
                stats_query = f"""
                SELECT 
                    MIN({col_name}) as min_value,
                    MAX({col_name}) as max_value,
                    AVG({col_name}) as avg_value
                FROM {table} 
                WHERE {col_name} IS NOT NULL
                """
                numeric_stats = self.db.execute_query(stats_query)
                if numeric_stats:
                    col_stats.update(numeric_stats[0])
            
            stats['column_stats'][col_name] = col_stats
        
        return stats
    
    def export_to_csv(self, query_result: List[Dict], filename: str) -> bool:
        """Export query results to CSV file.
        
        Args:
            query_result: List of dictionaries from query result.
            filename: Output CSV filename.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not query_result:
            print("❌ No data to export")
            return False
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = query_result[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for row in query_result:
                    # Handle datetime objects and other non-serializable types
                    processed_row = {}
                    for key, value in row.items():
                        if isinstance(value, datetime):
                            processed_row[key] = value.isoformat()
                        elif value is None:
                            processed_row[key] = ''
                        else:
                            processed_row[key] = str(value)
                    writer.writerow(processed_row)
                
                print(f"✅ Data exported to {filename}")
                return True
                
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return False
    
    def export_to_json(self, query_result: List[Dict], filename: str) -> bool:
        """Export query results to JSON file.
        
        Args:
            query_result: List of dictionaries from query result.
            filename: Output JSON filename.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not query_result:
            print("❌ No data to export")
            return False
        
        try:
            # Handle datetime objects and other non-serializable types
            processed_data = []
            for row in query_result:
                processed_row = {}
                for key, value in row.items():
                    if isinstance(value, datetime):
                        processed_row[key] = value.isoformat()
                    else:
                        processed_row[key] = value
                processed_data.append(processed_row)
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(processed_data, jsonfile, indent=2, ensure_ascii=False)
                
            print(f"✅ Data exported to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to JSON: {e}")
            return False

def get_common_queries(table_name: str) -> Dict[str, str]:
    """Get a dictionary of common queries for a table.
    
    Args:
        table_name: Name of the table.
        
    Returns:
        Dict of query name -> query string.
    """
    queries = {
        f"All {table_name} records": f"SELECT * FROM {table_name}",
        f"Count {table_name} records": f"SELECT COUNT(*) as total_count FROM {table_name}",
        f"Recent {table_name} (last 7 days)": f"""
            SELECT * FROM {table_name} 
            WHERE CreatedAt >= datetime('now', '-7 days')
            ORDER BY CreatedAt DESC
        """,
        f"Top 10 {table_name}": f"SELECT * FROM {table_name} LIMIT 10",
    }
    
    # Add table-specific queries for ErrorLog
    if table_name.lower() == 'error_logs':
        queries.update({
            "Errors by Team": """
                SELECT TeamName, COUNT(*) as error_count 
                FROM error_logs 
                GROUP BY TeamName 
                ORDER BY error_count DESC
            """,
            "Errors by Module": """
                SELECT Module, COUNT(*) as error_count 
                FROM error_logs 
                GROUP BY Module 
                ORDER BY error_count DESC
            """,
            "Recent Errors with Solutions": """
                SELECT Cr_ID, ErrorName, TeamName, Module, SolutionPossible, CreatedAt
                FROM error_logs 
                WHERE SolutionPossible = 1
                ORDER BY CreatedAt DESC
                LIMIT 20
            """,
            "Large Log Files": """
                SELECT Cr_ID, LogFileName, FileSize, ErrorName, TeamName
                FROM error_logs 
                WHERE FileSize > 10000
                ORDER BY FileSize DESC
            """
        })
    
    return queries

if __name__ == "__main__":
    # Test the query builder
    print("🔍 Testing Query Builder...")
    
    db = DatabaseConnection()
    if db.connect():
        qb = QueryBuilder(db)
        
        # Test getting table statistics
        tables = db.get_tables()
        if tables:
            table_name = tables[0]
            print(f"📊 Getting statistics for table: {table_name}")
            stats = qb.get_table_statistics(table_name)
            print(f"  • Total rows: {stats['total_rows']}")
            print(f"  • Columns: {len(stats['column_stats'])}")
        
        db.close()
        print("✅ Query builder test completed!")
    else:
        print("❌ Failed to connect to database!")
