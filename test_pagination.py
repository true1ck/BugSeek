from backend.models import db, ErrorLog
from backend.app import create_app

app = create_app()

with app.app_context():
    print("=== Testing Pagination ===")
    
    try:
        # Test basic query
        query = ErrorLog.query
        print(f"Basic query created: {query}")
        
        # Test ordering
        query = query.order_by(ErrorLog.CreatedAt.desc())
        print(f"Ordered query created: {query}")
        
        # Test pagination
        print("\nTesting pagination:")
        paginated = query.paginate(page=1, per_page=20, error_out=False)
        print(f"Pagination successful: {paginated}")
        print(f"Items: {len(paginated.items)}")
        print(f"Total: {paginated.total}")
        print(f"Pages: {paginated.pages}")
        
        # Test get_summary on each item
        print("\nTesting get_summary on all items:")
        summaries = []
        for i, log in enumerate(paginated.items):
            try:
                summary = log.get_summary()
                summaries.append(summary)
                print(f"Item {i+1}: SUCCESS")
            except Exception as e:
                print(f"Item {i+1}: FAILED - {e}")
                import traceback
                traceback.print_exc()
                break
        
        print(f"\nSuccessfully processed {len(summaries)} summaries")
        
    except Exception as e:
        print(f"Pagination test failed: {e}")
        import traceback
        traceback.print_exc()
