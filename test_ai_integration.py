#!/usr/bin/env python3
"""
Test script for AI analysis integration in BugSeek
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_import():
    """Test if AI analysis module can be imported"""
    print("Testing AI analysis module import...")
    try:
        from backend.ai_analysis import analyze_log_content, extract_error_lines_with_numbers, improved_stress_score
        print("✅ AI analysis module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import AI analysis module: {e}")
        return False

def test_environment_variables():
    """Test if required environment variables are set"""
    print("\nTesting environment variables...")
    required_vars = [
        'AZURE_API_KEY',
        'USER_ID', 
        'ENDPOINT_URL',
        'MODEL_NAME',
        'API_VERSION'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value in ['your_actual_jwt_token_from_mediatek_here', 'your_mtk_employee_id_here']:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: Set")
    
    if missing_vars:
        print(f"❌ Missing or invalid environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_log_analysis_functions():
    """Test individual log analysis functions"""
    print("\nTesting log analysis functions...")
    
    # Sample log content with errors
    sample_log = """
    2025-01-14 10:30:00 INFO Starting application
    2025-01-14 10:30:01 ERROR Database connection failed
    2025-01-14 10:30:02 WARN Retrying connection...
    2025-01-14 10:30:03 CRITICAL System crash detected
    2025-01-14 10:30:04 EXCEPTION NullPointerException in module auth
    """
    
    try:
        from backend.ai_analysis import extract_error_lines_with_numbers, improved_stress_score
        
        # Test error line extraction
        error_lines = extract_error_lines_with_numbers(sample_log)
        print(f"✅ Error lines extracted: {len(error_lines)} errors found")
        
        # Test stress score calculation
        stress_score = improved_stress_score(sample_log)
        print(f"✅ Stress score calculated: {stress_score}%")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test log analysis functions: {e}")
        return False

def test_openai_connection():
    """Test OpenAI connection"""
    print("\nTesting OpenAI connection...")
    
    try:
        from openai import AzureOpenAI
        
        api_key = os.getenv("AZURE_API_KEY")
        endpoint_url = os.getenv("ENDPOINT_URL")
        api_version = os.getenv("API_VERSION")
        
        client = AzureOpenAI(
            azure_endpoint=endpoint_url,
            api_key=api_key,
            api_version=api_version
        )
        
        print("✅ OpenAI client created successfully")
        print("⚠️  Actual API call test skipped to avoid token usage")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create OpenAI client: {e}")
        return False

def test_database_connection():
    """Test database connection and models"""
    print("\nTesting database connection...")
    
    try:
        from backend.models import db, AIAnalysisResult
        from config.settings import config
        from flask import Flask
        
        app = Flask(__name__)
        app.config.from_object(config['development'])
        db.init_app(app)
        
        with app.app_context():
            # Test database connection
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Check if AI analysis table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'ai_analysis_results' in tables:
                print("✅ AI analysis table exists")
            else:
                print("❌ AI analysis table not found")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 BugSeek AI Analysis Integration Test")
    print("=" * 50)
    
    tests = [
        test_ai_import,
        test_environment_variables, 
        test_log_analysis_functions,
        test_openai_connection,
        test_database_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! AI analysis integration is ready.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
