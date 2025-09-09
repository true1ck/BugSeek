#!/usr/bin/env python3
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(PROJECT_ROOT, 'instance')
DEFAULT_SQLITE_PATH = os.path.join(INSTANCE_DIR, 'bugseek.db')

if os.name == 'nt':  # Windows
    DEFAULT_SQLITE_URI = f"sqlite:///{DEFAULT_SQLITE_PATH.replace(chr(92), '/')}"
else:
    DEFAULT_SQLITE_URI = f"sqlite:///{DEFAULT_SQLITE_PATH}"

print(f"Project Root: {PROJECT_ROOT}")
print(f"Instance Dir: {INSTANCE_DIR}")
print(f"SQLite Path: {DEFAULT_SQLITE_PATH}")
print(f"SQLite URI: {DEFAULT_SQLITE_URI}")
print(f"File exists: {os.path.exists(DEFAULT_SQLITE_PATH)}")
print(f"File size: {os.path.getsize(DEFAULT_SQLITE_PATH) if os.path.exists(DEFAULT_SQLITE_PATH) else 'N/A'}")

# Test connection
from db_connection import DatabaseConnection

db = DatabaseConnection(DEFAULT_SQLITE_URI)
if db.connect():
    tables = db.get_tables()
    print(f"Tables found: {tables}")
    for table in tables:
        count = db.get_table_count(table)
        print(f"  {table}: {count} records")
    db.close()
else:
    print("Connection failed!")
