#!/usr/bin/env python3

"""
Quick test of the rooftop FastAPI functionality
"""

import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rooftop_fastapi import process_rooftop_detection

def test_api_functionality():
    """Test the core API functionality"""
    
    # Test image path
    image_path = "testcases/image copy 2.png"
    num_panels = 25
    
    print("🔋 TESTING ROOFTOP DETECTION API FUNCTIONALITY")
    print("=" * 50)
    print(f"📸 Image: {image_path}")
    print(f"🔋 Panels: {num_panels}")
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at {image_path}")
        print("Available test images:")
        for file in os.listdir("testcases"):
            if file.endswith(('.png', '.jpg', '.jpeg')):
                print(f"   - testcases/{file}")
        return
    
    try:
        # Test the core processing function
        result = process_rooftop_detection(image_path, num_panels)
        
        if result:
            print("\n✅ PROCESSING SUCCESSFUL!")
            print(f"📏 Length: {result['length']}m")
            print(f"📐 Width: {result['breadth']}m")
            print(f"📁 Image saved: {result['output_path']}")
            
            # Check if output file was created
            if os.path.exists(result['output_path']):
                print("✅ Output image file created successfully")
            else:
                print("❌ Output image file not found")
                
            print(f"\n📋 JSON Output Format:")
            print(f"{{")
            print(f'  "length": {result["length"]},')
            print(f'  "width": {result["breadth"]},')
            print(f'  "image_location": "{result["output_path"]}"')
            print(f"}}")
            
        else:
            print("❌ No rooftops detected")
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")

if __name__ == "__main__":
    test_api_functionality()