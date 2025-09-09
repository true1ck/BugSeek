#!/usr/bin/env python3
"""Test script to verify backend search API functionality."""

from backend.app import create_app

def test_search_api():
    print('Testing backend API search endpoint...')
    app = create_app()
    
    with app.test_client() as client:
        # Test search with various parameters
        tests = [
            {'search': 'authentication'},
            {'TeamName': 'Frontend'},
            {'Module': 'Database'},
            {'search': 'timeout', 'TeamName': 'Frontend'},
            {'SolutionPossible': 'true'}
        ]
        
        for i, test_params in enumerate(tests, 1):
            response = client.get('/api/v1/logs/', query_string=test_params)
            data = response.get_json()
            print(f'Test {i}: {test_params}')
            print(f'  Status: {response.status_code}')
            print(f'  Success: {data.get("success", False)}')
            print(f'  Results: {len(data.get("data", {}).get("logs", []))} logs found')
            
            if data.get('success') and data.get('data', {}).get('logs'):
                sample = data['data']['logs'][0]
                print(f'  Sample: {sample.get("TeamName")} - {sample.get("Module")} - {sample.get("ErrorName")}')
            print()

    print('Backend search API tests completed!')

if __name__ == '__main__':
    test_search_api()
