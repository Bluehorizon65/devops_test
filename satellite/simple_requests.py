"""
SIMPLE SATELLITE IMAGE REQUESTS
===============================

Easy examples showing how to request satellite images using numbered zoom levels (1-7).
Just change coordinates and zoom level - it's that simple!

Requirements:
  pip install requests

Usage:
  1. Start server: python satellite_zoom_server.py
  2. Run this: python simple_requests.py
"""

import requests
import json

# Server URL
SERVER_URL = "http://localhost:8000"

def simple_request_post(latitude, longitude, zoom_level, location_name="My_Location"):
    """
    Simple POST request for satellite image
    
    Args:
        latitude: Your latitude coordinate  
        longitude: Your longitude coordinate
        zoom_level: Number 1-7 (1=wide area, 7=maximum zoom)
        location_name: Name for your location
    """
    
    print(f"🛰️ REQUESTING SATELLITE IMAGE")
    print(f"📍 Location: {location_name}")
    print(f"🌐 Coordinates: {latitude:.6f}, {longitude:.6f}")
    print(f"🔍 Zoom Level: {zoom_level}")
    print("=" * 50)
    
    # Request data
    request_data = {
        "latitude": latitude,
        "longitude": longitude,
        "location_name": location_name,
        "zoom_level": zoom_level
    }
    
    try:
        # Send POST request
        response = requests.post(f"{SERVER_URL}/satellite", json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            
            if result['success']:
                print("✅ SUCCESS!")
                print(f"📐 Resolution: {result['resolution_m_per_pixel']:.3f} m/pixel")
                print(f"📏 Coverage: {result['coverage_description']}")
                print(f"📁 Filename: {result['filename']}")
                print(f"🔗 Download URL: {SERVER_URL}{result['file_url']}")
                print(f"⏱️ Processing time: {result['processing_time_seconds']:.2f} seconds")
                
                return result
            else:
                print(f"❌ ERROR: {result['error_message']}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("   Make sure server is running: python satellite_zoom_server.py")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def simple_request_get(latitude, longitude, zoom_level, location_name="My_Location"):
    """
    Simple GET request for satellite image (alternative method)
    """
    
    print(f"🛰️ REQUESTING SATELLITE IMAGE (GET method)")
    print(f"📍 {location_name}: {latitude:.6f}, {longitude:.6f}")
    print(f"🔍 Zoom Level: {zoom_level}")
    
    # URL parameters
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "zoom_level": zoom_level,
        "location_name": location_name
    }
    
    try:
        response = requests.get(f"{SERVER_URL}/satellite-simple", params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ GET request successful!")
                print(f"📐 {result['resolution_m_per_pixel']:.3f} m/pixel")
                return result
            else:
                print(f"❌ GET error: {result['error_message']}")
        else:
            print(f"❌ GET HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ GET error: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 SIMPLE SATELLITE IMAGE REQUESTS")
    print("=" * 50)
    
    print("📊 ZOOM LEVEL GUIDE:")
    print("   1 = Wide area view (~5m/pixel)")
    print("   2 = District view (~2.5m/pixel)")  
    print("   3 = Buildings visible (~1.2m/pixel)")
    print("   4 = Building details (~0.6m/pixel)")
    print("   5 = Rooftop level (~0.3m/pixel) ⭐")
    print("   6 = High detail (~0.15m/pixel)")
    print("   7 = Maximum zoom (~0.07m/pixel) 🎯")
    print()
    
    # =============================================================================
    # 📍 CHANGE THESE FOR YOUR LOCATION!
    # =============================================================================
    
    # Example 1: Karunya Hostel (your current location)
    my_latitude = 10.933519651332348
    my_longitude = 76.74317650322091
    my_location_name = "unknown"
    my_zoom_level = 6  # Rooftop level - good for analysis
    
    # Example 2: Taj Mahal (uncomment to try)
    # my_latitude = 27.1751
    # my_longitude = 78.0421
    # my_location_name = "Taj_Mahal"
    # my_zoom_level = 6  # High detail
    
    # Example 3: Your custom location (uncomment and modify)
    # my_latitude = 40.7484    # Empire State Building
    # my_longitude = -73.9857
    # my_location_name = "Empire_State_Building"
    # my_zoom_level = 7  # Maximum zoom
    
    # =============================================================================
    # REQUEST THE IMAGE
    # =============================================================================
    
    print("🎯 MAKING REQUEST...")
    result = simple_request_post(my_latitude, my_longitude, my_zoom_level, my_location_name)
    
    if result:
        print(f"\n🎉 Image saved to: satellite_images/{result['filename']}")
        print(f"💡 You can view it at: {SERVER_URL}{result['file_url']}")
        
        # Optional: Test GET method too
        print(f"\n🔄 Testing GET method...")
        simple_request_get(my_latitude, my_longitude, my_zoom_level + 1, f"{my_location_name}_GET")
    
    print(f"\n✨ Done! Check 'satellite_images' folder for your images.")
    
    # =============================================================================
    # QUICK EXAMPLES FOR DIFFERENT ZOOM LEVELS
    # =============================================================================
    
    print(f"\n❓ Want to test different zoom levels?")
    user_input = input("Enter 'y' to test zoom levels 1, 3, 5, 7: ").strip().lower()
    
    if user_input == 'y':
        print(f"\n🔍 TESTING DIFFERENT ZOOM LEVELS")
        print("=" * 40)
        
        test_zooms = [1, 3, 5, 7]  # Wide, Buildings, Rooftop, Maximum
        
        for zoom in test_zooms:
            print(f"\n📐 Testing Zoom Level {zoom}...")
            result = simple_request_post(
                my_latitude, 
                my_longitude, 
                zoom, 
                f"{my_location_name}_Zoom{zoom}"
            )
            if result:
                print(f"   ✅ Zoom {zoom}: {result['resolution_m_per_pixel']:.3f} m/pixel")
            else:
                print(f"   ❌ Zoom {zoom}: Failed")
    
    print(f"\n🌐 WEB INTERFACE: {SERVER_URL}/test-interface")
    print(f"📖 API DOCS: {SERVER_URL}/docs")
    print(f"✅ Complete!")