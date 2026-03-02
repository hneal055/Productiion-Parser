"""
API Key Testing Script
Test your API endpoints with authentication
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8080"
API_KEY = "your_api_key_here"  # Replace with your actual API key

def test_without_api_key():
    """Test accessing protected endpoint without API key"""
    print("\n" + "=" * 80)
    print("TEST 1: Accessing protected endpoint WITHOUT API key")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/secure")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ PASS: Correctly blocked unauthorized request")
        else:
            print("❌ FAIL: Should have blocked request")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_with_header():
    """Test with API key in header"""
    print("\n" + "=" * 80)
    print("TEST 2: API key in HEADER")
    print("=" * 80)
    
    headers = {'X-API-Key': API_KEY}
    
    try:
        response = requests.get(f"{BASE_URL}/api/secure", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ PASS: Successfully authenticated")
        else:
            print("❌ FAIL: Authentication failed")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_with_query_param():
    """Test with API key as query parameter"""
    print("\n" + "=" * 80)
    print("TEST 3: API key in QUERY PARAMETER")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/secure?api_key={API_KEY}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ PASS: Successfully authenticated")
        else:
            print("❌ FAIL: Authentication failed")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_with_json_body():
    """Test with API key in JSON body"""
    print("\n" + "=" * 80)
    print("TEST 4: API key in JSON BODY")
    print("=" * 80)
    
    data = {'api_key': API_KEY, 'data': 'test'}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/secure",
            json=data,
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ PASS: Successfully authenticated")
        else:
            print("❌ FAIL: Authentication failed")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_invalid_key():
    """Test with invalid API key"""
    print("\n" + "=" * 80)
    print("TEST 5: INVALID API key")
    print("=" * 80)
    
    headers = {'X-API-Key': 'invalid_key_12345'}
    
    try:
        response = requests.get(f"{BASE_URL}/api/secure", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 403:
            print("✅ PASS: Correctly rejected invalid key")
        else:
            print("❌ FAIL: Should have rejected invalid key")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_rate_limiting():
    """Test rate limiting (if enabled)"""
    print("\n" + "=" * 80)
    print("TEST 6: RATE LIMITING (optional)")
    print("=" * 80)
    
    headers = {'X-API-Key': API_KEY}
    
    print("Making 10 rapid requests...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/api/secure", headers=headers)
            print(f"Request {i+1}: {response.status_code}")
            
            if response.status_code == 429:
                print(f"✅ Rate limit triggered at request {i+1}")
                break
        except Exception as e:
            print(f"❌ Error on request {i+1}: {e}")
            break

# ============================================================================
# CURL EXAMPLES
# ============================================================================

def print_curl_examples():
    """Print curl command examples"""
    print("\n" + "=" * 80)
    print("CURL EXAMPLES")
    print("=" * 80)
    print()
    
    print("1. API key in header:")
    print(f'   curl -H "X-API-Key: {API_KEY}" {BASE_URL}/api/secure')
    print()
    
    print("2. API key in query parameter:")
    print(f'   curl "{BASE_URL}/api/secure?api_key={API_KEY}"')
    print()
    
    print("3. API key in JSON body (POST):")
    print(f'   curl -X POST {BASE_URL}/api/secure \\')
    print(f'        -H "Content-Type: application/json" \\')
    print(f'        -d \'{{"api_key": "{API_KEY}", "data": "test"}}\'')
    print()

# ============================================================================
# MAIN SCRIPT
# ============================================================================

if __name__ == '__main__':
    import sys
    
    print("=" * 80)
    print("🧪 API KEY TESTING SUITE")
    print("=" * 80)
    
    if len(sys.argv) > 1 and sys.argv[1] != 'your_api_key_here':
        API_KEY = sys.argv[1]
        print(f"Using API key: {API_KEY[:8]}...")
    else:
        print()
        print("⚠️  WARNING: Using default API key")
        print("   Set your API key: python test_api.py YOUR_API_KEY")
        print()
        print("   Or edit this file and change:")
        print(f'   API_KEY = "{API_KEY}"  # Replace with your actual key')
        print()
    
    # Check if server is running
    print("\n🔍 Checking if server is running...")
    try:
        response = requests.get(BASE_URL, timeout=2)
        print(f"✅ Server is running at {BASE_URL}")
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("   Make sure your Flask app is running!")
        print("   Run: python web_app_COMPLETE_WITH_COMPARISON.py")
        sys.exit(1)
    
    # Run tests
    test_without_api_key()
    test_with_header()
    test_with_query_param()
    # test_with_json_body()  # Uncomment if your endpoint accepts POST
    test_invalid_key()
    # test_rate_limiting()  # Uncomment if rate limiting is enabled
    
    # Show curl examples
    print_curl_examples()
    
    print("\n" + "=" * 80)
    print("✅ Testing complete!")
    print("=" * 80)