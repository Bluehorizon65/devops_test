#!/usr/bin/env python3

"""
Test client for the Rooftop Detection FastAPI
"""

import requests
import json
import os

def test_rooftop_api():
    """Test the rooftop detection API"""
    
    # API endpoint
    base_url = "http://localhost:8005"
    endpoint = f"{base_url}/detect-rooftop"
    
    # Test data
    test_data = {
        "image_path": "testcases/image copy 2.png",
        "num_panels": 3
    }
    
    print("🔋 TESTING ROOFTOP DETECTION API")
    print("=" * 50)
    print(f"📡 API Endpoint: {endpoint}")
    print(f"📸 Image Path: {test_data['image_path']}")
    print(f"🔋 Number of Panels: {test_data['num_panels']}")
    print()
    
    try:
        # Make the API request
        print("🚀 Sending request...")
        response = requests.post(endpoint, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API RESPONSE SUCCESS!")
            print("-" * 30)
            print(f"📏 Length: {result['length']}m")
            print(f"📐 Width: {result['width']}m")
            print(f"📁 Image Location: {result['image_location']}")
            
            # Check if output file exists
            if os.path.exists(result['image_location']):
                print("✅ Output image file verified!")
            else:
                print("❌ Output image file not found")
            
            print(f"\n📋 Complete JSON Response:")
            print(json.dumps(result, indent=2))
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error Details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error!")
        print("Make sure the API server is running:")
        print("   python rooftop_api_server.py")
        print("   OR")
        print("   uvicorn rooftop_api_server:app --host 0.0.0.0 --port 8005 --reload")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_api_health():
    """Test API health endpoint"""
    try:
        response = requests.get("http://localhost:8005/health")
        if response.status_code == 200:
            print("✅ API Health Check: OK")
            print(f"   Status: {response.json()}")
        else:
            print("❌ API Health Check: Failed")
            print(f"   Error: {response.text}")
    except:
        print("❌ API is not running or not accessible")

def test_list_images():
    """Test the list test images endpoint"""
    try:
        response = requests.get("http://localhost:8005/test-images")
        if response.status_code == 200:
            data = response.json()
            print("📁 Available Test Images:")
            for img in data['available_test_images']:
                print(f"   - {img}")
            print(f"   Total: {data['total_count']} images")
        else:
            print("❌ Failed to get test images list")
    except:
        print("❌ Could not fetch test images list")

if __name__ == "__main__":
    print("🔋 ROOFTOP DETECTION API TEST CLIENT")
    print("=" * 50)
    
    # Test health first
    test_api_health()
    print()
    
    # List available test images
    test_list_images()
    print()
    
    # Test main functionality
    test_rooftop_api()