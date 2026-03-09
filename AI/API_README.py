"""
🔋 ROOFTOP DETECTION FASTAPI - COMPLETE SETUP
==============================================

📁 FILES CREATED:
1. rooftop_api.py - Main FastAPI application
2. test_api.py - API test client  
3. api_requirements.txt - Dependencies
4. start_api.sh - Startup script

🚀 HOW TO RUN:

1. INSTALL DEPENDENCIES:
   pip install fastapi uvicorn python-multipart opencv-python numpy matplotlib pillow

2. START THE API SERVER:
   uvicorn rooftop_api:app --host 0.0.0.0 --port 8000 --reload

3. ACCESS THE API:
   - API Base: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

📡 API ENDPOINTS:

POST /detect-rooftop
**INPUT:**
- image: Google Maps satellite image file (multipart/form-data)
- num_panels: Number of solar panels to place (form field)

**OUTPUT JSON:**
{
  "success": true,
  "data": {
    "length": 36.6,          // Average roof length in meters
    "breadth": 17.3,         // Average roof breadth in meters  
    "panels_placed": 25,     // Number of panels successfully placed
    "result_image": "base64..." // Base64 encoded result image
  }
}

💡 EXAMPLE USAGE:

CURL:
curl -X POST "http://localhost:8000/detect-rooftop" \
     -F "image=@testcases/image copy 2.png" \
     -F "num_panels=25"

PYTHON:
import requests

with open('test_image.png', 'rb') as f:
    files = {'image': ('test_image.png', f, 'image/png')}
    data = {'num_panels': 25}
    response = requests.post('http://localhost:8000/detect-rooftop', 
                           files=files, data=data)
    result = response.json()
    print(f"Length: {result['data']['length']}m")
    print(f"Breadth: {result['data']['breadth']}m")

🔧 KEY FEATURES:
✅ Accepts Google Maps satellite images
✅ Returns averaged roof dimensions (length & breadth)
✅ Places solar panels with adaptive sizing
✅ Returns result image with panels placed
✅ Automatic error handling and validation
✅ Interactive API documentation at /docs
✅ Health check endpoint
✅ Base64 encoded image output for easy integration

📊 TECHNICAL DETAILS:
- Uses 0.15m per pixel conversion (Google Maps zoom 20)
- Averages measurements from multiple tolerance levels
- Adaptive panel sizing (40x25 → 30x20 → 20x15 → 12x8)
- Full polygon dimension calculation
- OpenCV-based rooftop detection
- FastAPI with automatic validation

🏗️ PERFECT FOR:
- 3D roof visualization apps
- Solar panel planning tools
- Real estate analysis
- Construction planning
- IoT integration
- Mobile applications

The API is now ready for integration with your 3D visualization system! 🏠⚡📊
"""

print(__doc__)