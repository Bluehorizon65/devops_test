#!/usr/bin/env python3

"""
Example usage of the Rooftop Detection FastAPI
"""

import requests
import json

def example_api_usage():
    """Example of how to use the rooftop detection API"""
    
    # API configuration
    api_url = "http://localhost:8000/detect-rooftop"
    
    # Example 1: Basic usage
    print("📋 EXAMPLE 1: Basic API Usage")
    print("-" * 40)
    
    request_data = {
        "image_path": "testcases/image copy 2.png",
        "num_panels": 30
    }
    
    print(f"Request: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(api_url, json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Extract specific values
            print(f"\n🏠 Roof Dimensions: {result['length']}m × {result['width']}m")
            print(f"📁 Output Image: {result['image_location']}")
            
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Different parameters
    print("📋 EXAMPLE 2: Different Parameters")
    print("-" * 40)
    
    request_data2 = {
        "image_path": "testcases/image copy 3.png",
        "num_panels": 50
    }
    
    print(f"Request: {json.dumps(request_data2, indent=2)}")
    
    try:
        response = requests.post(api_url, json=request_data2)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def curl_examples():
    """Show curl command examples"""
    print("💻 CURL COMMAND EXAMPLES")
    print("-" * 40)
    
    print("Example 1:")
    print("""curl -X POST "http://localhost:8000/detect-rooftop" \\
     -H "Content-Type: application/json" \\
     -d '{
       "image_path": "testcases/image copy 2.png",
       "num_panels": 25
     }'""")
    
    print("\nExample 2:")
    print("""curl -X POST "http://localhost:8000/detect-rooftop" \\
     -H "Content-Type: application/json" \\
     -d '{
       "image_path": "testcases/image copy 3.png", 
       "num_panels": 40
     }'""")
    
    print("\nHealth check:")
    print("curl http://localhost:8000/health")
    
    print("\nList test images:")
    print("curl http://localhost:8000/test-images")

if __name__ == "__main__":
    print("🔋 ROOFTOP DETECTION API - USAGE EXAMPLES")
    print("=" * 60)
    print("Make sure the API server is running first:")
    print("   python rooftop_api_server.py")
    print("=" * 60)
    print()
    
    # Show Python examples
    example_api_usage()
    
    print()
    
    # Show curl examples
    curl_examples()