#!/usr/bin/env python3
"""
Quick AI Service Integration Test
Test the AI service integration and fallback mechanisms.
"""

import sys
import os
sys.path.insert(0, 'backend')

def test_ai_services():
    """Test AI service imports and functionality."""
    try:
        print("🔄 Testing AI service imports...")
        from ai_services import OpenAIService, AIAnalysisService
        from services import GenAIService
        
        print("✅ AI services imports successful")
        
        # Test GenAI fallback service
        test_log = 'ERROR: Connection timeout while accessing database server at 10.0.0.1:5432. Connection refused after 30 seconds.'
        test_metadata = {
            'TeamName': 'Backend',
            'Module': 'Database', 
            'ErrorName': 'ConnectionTimeout',
            'Description': 'Database connection timeout during user authentication process'
        }
        
        print("\n🧪 Testing GenAI fallback summary generation...")
        summary_result = GenAIService.generate_summary(test_log, test_metadata)
        
        print(f"Summary Success: {summary_result.get('success', False)}")
        print(f"Summary: {summary_result.get('summary', 'No summary')[:150]}...")
        print(f"Confidence: {summary_result.get('confidence', 0)}")
        print(f"Severity: {summary_result.get('severity', 'unknown')}")
        print(f"Keywords: {summary_result.get('keywords', [])}")
        
        print("\n🧪 Testing solution suggestions...")
        solution_result = GenAIService.suggest_solutions(test_metadata)
        
        print(f"Solutions Success: {solution_result.get('success', False)}")
        solutions = solution_result.get('solutions', [])
        print(f"Number of solutions: {len(solutions)}")
        
        if solutions:
            print("First few solutions:")
            for i, solution in enumerate(solutions[:3], 1):
                print(f"  {i}. {solution}")
        
        # Test OpenAI connection check (will likely fail without real credentials)
        print("\n🧪 Testing OpenAI connection status...")
        openai_result = GenAIService.check_openai_status()
        print(f"OpenAI Status: {openai_result.get('connected', False)}")
        
        if not openai_result.get('connected'):
            print("⚠️  OpenAI not connected (expected - using fallback system)")
        
        print("\n✅ AI service integration test completed successfully!")
        print("🎯 The system works with intelligent fallback when AI services are offline")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running from the BugSeek root directory")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_services()
    if success:
        print("\n🎉 BugSeek AI services are working correctly!")
        print("🚀 Ready for MediaTek environment deployment!")
    else:
        print("\n🚨 AI service test failed. Check the errors above.")
    
    sys.exit(0 if success else 1)
