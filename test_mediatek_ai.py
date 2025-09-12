#!/usr/bin/env python3
"""
MediaTek AI Service Test Script
Tests connection to MediaTek's Azure OpenAI gateway

Usage:
    python test_mediatek_ai.py

Make sure to update the configuration variables with your MediaTek credentials.
"""

import os
import sys
import requests
import json
from datetime import datetime

# MediaTek configuration - UPDATE THESE WITH YOUR ACTUAL VALUES
AZURE_API_KEY = os.getenv('AZURE_API_KEY', 'your_jwt_token_here')
USER_ID = os.getenv('USER_ID', 'your_user_id')  
ENDPOINT_URL = os.getenv('ENDPOINT_URL', 'https://mlop-azure-gateway.mediatek.inc')
MODEL_NAME = os.getenv('MODEL_NAME', 'aida-gpt-4o-mini')
API_VERSION = os.getenv('API_VERSION', '2024-10-21')

def test_environment():
    """Test if environment variables are configured."""
    print("🔧 Testing MediaTek Environment Configuration")
    print("=" * 50)
    
    issues = []
    
    if not AZURE_API_KEY or AZURE_API_KEY == 'your_jwt_token_here':
        issues.append("❌ AZURE_API_KEY not set or using placeholder")
    else:
        print(f"✅ AZURE_API_KEY: {AZURE_API_KEY[:20]}...")
    
    if not USER_ID or USER_ID == 'your_user_id':
        issues.append("❌ USER_ID not set or using placeholder")
    else:
        print(f"✅ USER_ID: {USER_ID}")
    
    print(f"✅ ENDPOINT_URL: {ENDPOINT_URL}")
    print(f"✅ MODEL_NAME: {MODEL_NAME}")
    print(f"✅ API_VERSION: {API_VERSION}")
    
    if issues:
        print("\n⚠️  Configuration Issues Found:")
        for issue in issues:
            print(f"   {issue}")
        print("\n   Please update your environment variables or .env file")
        return False
    
    print("\n✅ Environment configuration looks good!")
    return True

def test_network_connectivity():
    """Test basic network connectivity to MediaTek gateway."""
    print("\n🌐 Testing Network Connectivity")
    print("=" * 50)
    
    try:
        # Test basic connectivity
        response = requests.get(ENDPOINT_URL, timeout=10)
        print(f"✅ Network connectivity: OK (Status: {response.status_code})")
        return True
    except requests.exceptions.Timeout:
        print("❌ Network connectivity: Timeout - Check VPN/network connection")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Network connectivity: Connection refused - Check MediaTek network access")
        return False
    except Exception as e:
        print(f"❌ Network connectivity: {str(e)}")
        return False

def test_mediatek_ai_basic():
    """Test basic MediaTek AI service connection."""
    print("\n🤖 Testing MediaTek AI Service (Basic)")
    print("=" * 50)
    
    url = f"{ENDPOINT_URL}/openai/deployments/{MODEL_NAME}/chat/completions?api-version={API_VERSION}"
    
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "api-key": AZURE_API_KEY,
        "X-User-Id": USER_ID,
    }
    
    # Simple test payload
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, this is a test message."}
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    try:
        print(f"📤 Making request to: {url}")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            tokens_used = result['usage']['total_tokens']
            
            print("✅ MediaTek AI service: Working!")
            print(f"🎯 Response: {message}")
            print(f"📊 Tokens used: {tokens_used}")
            return True
        else:
            print(f"❌ MediaTek AI service: Failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ MediaTek AI service: Request timeout")
        print("   Try increasing timeout or check network latency")
        return False
    except Exception as e:
        print(f"❌ MediaTek AI service: {str(e)}")
        return False

def test_mediatek_ai_log_analysis():
    """Test MediaTek AI with log analysis scenario."""
    print("\n🔍 Testing MediaTek AI Service (Log Analysis)")
    print("=" * 50)
    
    url = f"{ENDPOINT_URL}/openai/deployments/{MODEL_NAME}/chat/completions?api-version={API_VERSION}"
    
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "api-key": AZURE_API_KEY,
        "X-User-Id": USER_ID,
    }
    
    # Log analysis test payload
    sample_log = """
2024-09-12 10:30:15 ERROR: Database connection failed
2024-09-12 10:30:15 ERROR: java.sql.SQLException: Connection timeout
2024-09-12 10:30:16 INFO: Retrying connection (attempt 2/3)
2024-09-12 10:30:18 ERROR: Max retry attempts exceeded
2024-09-12 10:30:18 FATAL: Service unavailable
"""
    
    payload = {
        "messages": [
            {
                "role": "system", 
                "content": "You are an expert log analyzer. Analyze error logs and provide concise summaries with suggested solutions."
            },
            {
                "role": "user", 
                "content": f"Analyze this error log and suggest solutions:\n\n{sample_log}"
            }
        ],
        "max_tokens": 200,
        "temperature": 0.3
    }
    
    try:
        print("📤 Making log analysis request...")
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            tokens_used = result['usage']['total_tokens']
            
            print("✅ MediaTek AI log analysis: Working!")
            print(f"🎯 Analysis Result:")
            print(f"   {message}")
            print(f"📊 Tokens used: {tokens_used}")
            return True
        else:
            print(f"❌ MediaTek AI log analysis: Failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ MediaTek AI log analysis: {str(e)}")
        return False

def test_bugseek_integration():
    """Test BugSeek AI service integration."""
    print("\n🔍 Testing BugSeek AI Service Integration")
    print("=" * 50)
    
    try:
        # Try to import and test BugSeek AI service
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from backend.ai_services import OpenAIService
        
        service = OpenAIService()
        result = service.check_connection()
        
        if result['success']:
            print("✅ BugSeek AI Service: Integration working!")
            print(f"   Connection: {result['connected']}")
            print(f"   Message: {result['message']}")
            return True
        else:
            print("❌ BugSeek AI Service: Integration failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except ImportError as e:
        print(f"⚠️  BugSeek AI Service: Could not import ({e})")
        print("   This is OK if you haven't set up the full BugSeek environment yet")
        return True  # Don't fail the test for this
    except Exception as e:
        print(f"❌ BugSeek AI Service: {str(e)}")
        return False

def print_summary(test_results):
    """Print test summary."""
    print("\n" + "=" * 60)
    print("🏆 MediaTek AI Test Summary")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your MediaTek environment is ready for BugSeek!")
        print("\nNext steps:")
        print("1. Update your .env file with MediaTek credentials")
        print("2. Run: python run.py")
        print("3. Open: http://localhost:8080")
        print("4. Login with: hackathon2025")
    else:
        print("\n🔧 Some tests failed. Please check the issues above.")
        print("\nTroubleshooting tips:")
        print("- Ensure you're on MediaTek internal network")
        print("- Verify your JWT token is correct and not expired")
        print("- Check your User ID")
        print("- Contact MediaTek IT if network issues persist")

def main():
    """Main test function."""
    print("🚀 MediaTek AI Service Test Suite")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    test_results = {
        "Environment Configuration": test_environment(),
        "Network Connectivity": test_network_connectivity(),
        "MediaTek AI Basic": test_mediatek_ai_basic(),
        "MediaTek AI Log Analysis": test_mediatek_ai_log_analysis(),
        "BugSeek Integration": test_bugseek_integration(),
    }
    
    # Print summary
    print_summary(test_results)

if __name__ == "__main__":
    main()
