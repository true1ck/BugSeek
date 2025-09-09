"""
Test script to debug the search functionality
"""
import sys
sys.path.append('..')
from fast_app import app

def test_search_endpoint():
    """Test the search endpoint directly"""
    with app.test_client() as client:
        # Test search with parameters
        response = client.get('/search?search=error')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.get_data(as_text=True)
            
            # Check if results are in the HTML
            if 'serverResults' in html_content:
                print("✅ serverResults div found in HTML")
                
                # Extract the JSON content between serverResults tags
                start_marker = '<div id="serverResults">'
                end_marker = '</div>'
                
                start_idx = html_content.find(start_marker)
                if start_idx != -1:
                    start_idx += len(start_marker)
                    end_idx = html_content.find(end_marker, start_idx)
                    if end_idx != -1:
                        json_content = html_content[start_idx:end_idx].strip()
                        print(f"JSON content length: {len(json_content)}")
                        if json_content:
                            print(f"First 200 chars of JSON: {json_content[:200]}...")
                        else:
                            print("❌ JSON content is empty!")
                    else:
                        print("❌ Could not find end of serverResults div")
                else:
                    print("❌ Could not find start of serverResults div")
            else:
                print("❌ serverResults div not found in HTML")
                
            # Check if search results div is visible
            if 'style="display: none;"' in html_content:
                print("❌ Search results div is hidden (no results)")
            else:
                print("✅ Search results div should be visible")
        else:
            print(f"❌ Request failed with status {response.status_code}")

if __name__ == "__main__":
    test_search_endpoint()
