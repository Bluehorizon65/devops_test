"""
🔋 ROOFTOP DETECTION FASTAPI USAGE EXAMPLES
==========================================

This file shows different ways to use the Rooftop Detection FastAPI.

🚀 TO START THE SERVER:
uvicorn rooftop_fastapi:app --host 0.0.0.0 --port 8000

📡 API ENDPOINT: POST /detect-rooftop

📥 INPUT JSON:
{
  "image_path": "path/to/your/image.png",
  "num_panels": 25
}

📤 OUTPUT JSON:
{
  "length": 36.6,
  "width": 17.3,
  "image_location": "output_images/rooftop_result_20251008_143022.jpg"
}
"""

import requests
import json

# Example 1: Basic usage
def example_basic_usage():
    """Basic API usage example"""
    
    url = "http://localhost:8000/detect-rooftop"
    
    data = {
        "image_path": "testcases/image copy 2.png",
        "num_panels": 30
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Roof Dimensions: {result['length']}m × {result['width']}m")
        print(f"📁 Result Image: {result['image_location']}")
    else:
        print(f"❌ Error: {response.text}")

# Example 2: Using different images
def example_multiple_images():
    """Process multiple images"""
    
    url = "http://localhost:8000/detect-rooftop"
    
    test_images = [
        {"path": "testcases/image copy 2.png", "panels": 20},
        {"path": "testcases/image copy 3.png", "panels": 40},
        {"path": "testcases/image.png", "panels": 15}
    ]
    
    for test in test_images:
        data = {
            "image_path": test["path"],
            "num_panels": test["panels"]
        }
        
        print(f"\n🔍 Processing: {test['path']} with {test['panels']} panels")
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   📏 Dimensions: {result['length']}m × {result['width']}m")
            print(f"   📁 Saved: {result['image_location']}")
        else:
            print(f"   ❌ Error: {response.text}")

# Example 3: cURL equivalent
def show_curl_example():
    """Show how to use with cURL"""
    
    curl_command = '''
curl -X POST "http://localhost:8000/detect-rooftop" \\
     -H "Content-Type: application/json" \\
     -d '{
       "image_path": "testcases/image copy 2.png",
       "num_panels": 25
     }'
    '''
    
    print("📋 cURL Example:")
    print(curl_command)

# Example 4: Error handling
def example_error_handling():
    """Example with error handling"""
    
    url = "http://localhost:8000/detect-rooftop"
    
    # Test with invalid image path
    data = {
        "image_path": "nonexistent_image.png",
        "num_panels": 10
    }
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success:", result)
        elif response.status_code == 404:
            print("❌ Image not found")
        elif response.status_code == 400:
            print("❌ Invalid input")
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with:")
        print("uvicorn rooftop_fastapi:app --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    print(__doc__)
    
    print("\n🔧 EXAMPLE FUNCTIONS:")
    print("1. example_basic_usage()")
    print("2. example_multiple_images()") 
    print("3. show_curl_example()")
    print("4. example_error_handling()")
    
    print("\n💡 Run any function to test the API!")
    print("Example: python -c \"from usage_examples import *; example_basic_usage()\"")
    
    # Uncomment to run an example automatically:
    # example_basic_usage()