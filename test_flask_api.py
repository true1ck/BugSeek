import requests
import json

def test_api_endpoint():
    print("=== Testing Flask API Endpoint ===")
    
    base_url = "http://localhost:5000/api/v1"
    
    # Test 1: Health check
    print("\n1. Health check:")
    try:
        response = requests.get(f"{base_url}/health/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test 2: Simple logs request (no parameters)
    print("\n2. Simple logs request (no params):")
    try:
        response = requests.get(f"{base_url}/logs/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            if data.get('success'):
                print(f"Logs count: {len(data['data']['logs'])}")
                print(f"Total items: {data['data']['pagination']['total_items']}")
            else:
                print(f"Error: {data.get('message')}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Simple request failed: {e}")
    
    # Test 3: With pagination parameters
    print("\n3. With pagination parameters:")
    try:
        params = {"page": 1, "per_page": 10}
        response = requests.get(f"{base_url}/logs/", params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            if data.get('success'):
                print(f"Logs count: {len(data['data']['logs'])}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Paginated request failed: {e}")
    
    # Test 4: With search parameters (like the frontend does)
    print("\n4. With search parameters:")
    try:
        params = {"page": 1, "per_page": 20, "search": ""}
        response = requests.get(f"{base_url}/logs/", params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Search request failed: {e}")

if __name__ == "__main__":
    test_api_endpoint()
