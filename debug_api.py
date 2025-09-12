from backend.models import db, ErrorLog
from backend.services import ErrorLogService
from backend.app import create_app

app = create_app()

with app.app_context():
    print("=== Debugging API Issue ===")
    
    # Test 1: Check raw database query
    print("\n1. Raw database query:")
    try:
        logs = ErrorLog.query.limit(5).all()
        print(f"Found {len(logs)} logs in database")
        if logs:
            first_log = logs[0]
            print(f"First log: {first_log.ErrorName} - {first_log.TeamName}")
    except Exception as e:
        print(f"Database query error: {e}")
    
    # Test 2: Test ErrorLogService.get_error_logs()
    print("\n2. Testing ErrorLogService.get_error_logs():")
    try:
        result = ErrorLogService.get_error_logs()
        print(f"Service result success: {result['success']}")
        if result['success']:
            print(f"Data count: {len(result['data'])}")
            print(f"Pagination: {result['pagination']}")
        else:
            print(f"Service error: {result['message']}")
    except Exception as e:
        print(f"Service error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test with pagination parameters
    print("\n3. Testing with pagination:")
    try:
        result = ErrorLogService.get_error_logs({}, page=1, per_page=10)
        print(f"Paginated result success: {result['success']}")
        if result['success']:
            print(f"Data count: {len(result['data'])}")
        else:
            print(f"Paginated error: {result['message']}")
    except Exception as e:
        print(f"Pagination error: {e}")
        import traceback
        traceback.print_exc()
