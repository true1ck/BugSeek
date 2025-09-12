from backend.models import db, ErrorLog
from backend.app import create_app

app = create_app()

with app.app_context():
    print("=== Testing get_summary() method ===")
    
    try:
        # Get first log
        log = ErrorLog.query.first()
        if log:
            print(f"Found log: {log.ErrorName}")
            print(f"Files relationship: {log.files}")
            print(f"Files count: {len(log.files) if log.files else 0}")
            
            # Test get_summary
            print("\nTesting get_summary():")
            summary = log.get_summary()
            print(f"Summary generated successfully: {summary}")
        else:
            print("No logs found")
    except Exception as e:
        print(f"Error in get_summary: {e}")
        import traceback
        traceback.print_exc()
