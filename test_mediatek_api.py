#!/usr/bin/env python3
"""
Quick test script for MediaTek Azure OpenAI API connection
Run this after setting up your .env file to test the connection
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mediatek_api():
    """Test MediaTek Azure OpenAI API connection"""
    
    # Get configuration from environment
    api_key = os.getenv('AZURE_API_KEY')
    user_id = os.getenv('USER_ID')
    endpoint = os.getenv('ENDPOINT_URL', 'https://mlop-azure-gateway.mediatek.inc')
    model = os.getenv('MODEL_NAME', 'aida-gpt-4o-mini')
    api_version = os.getenv('API_VERSION', '2024-10-21')
    
    if not api_key or not user_id:
        print("❌ ERROR: AZURE_API_KEY and USER_ID must be set in .env file")
        print("Contact the hackathon organizer to get your API key")
        return False
    
    print("🔧 Testing MediaTek Azure OpenAI API connection...")
    print(f"   Endpoint: {endpoint}")
    print(f"   Model: {model}")
    print(f"   User ID: {user_id}")
    print(f"   API Version: {api_version}")
    
    # Build API URL
    url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version={api_version}"
    
    # Prepare headers
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'api-key': api_key,
        'User-Agent': 'BugSeek/1.0 MediaTek-Compatible'
    }
    
    if user_id:
        headers['X-User-Id'] = user_id
    
    # Test payload
    test_payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! This is a connection test from BugSeek."}
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    try:
        print("🚀 Sending test request...")
        response = requests.post(url, headers=headers, json=test_payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            tokens = result.get('usage', {}).get('total_tokens', 0)
            
            print("✅ SUCCESS! MediaTek API is connected and working!")
            print(f"   Response: {message}")
            print(f"   Tokens used: {tokens}")
            return True
        else:
            print(f"❌ API Error: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timeout. Check network connection.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Network error - {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error - {e}")
        return False

if __name__ == "__main__":
    success = test_mediatek_api()
    if success:
        print("\n🎉 You can now use AI features in BugSeek!")
        print("   Run: python run.py")
    else:
        print("\n🔧 Troubleshooting:")
        print("   1. Verify your API key from the hackathon organizer")
        print("   2. Check your USER_ID (MediaTek employee ID)")
        print("   3. Ensure network access to mlop-azure-gateway.mediatek.inc")
        print("   4. Contact hackathon support if issues persist")
