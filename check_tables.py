from backend.models import db
from backend.app import create_app
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Get all tables
    result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
    tables = [r[0] for r in result]
    print(f"Tables in database: {tables}")
    
    # Check record counts for each table
    for table in tables:
        try:
            count = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"Table '{table}': {count} records")
        except Exception as e:
            print(f"Table '{table}': Error - {e}")
