# 🏠 Rooftop Detection & Solar Panel Placement API

A FastAPI-based system that detects rooftops from Google Maps satellite images and places solar panels with real-world measurements.

## 📸 Demo Results

<img width="1779" height="588" alt="image" src="https://github.com/user-attachments/assets/e9b9ff66-d2a8-484a-97cb-b114e74f1622" />

<img width="1779" height="588" alt="Screenshot from 2025-10-08 00-51-55" src="https://github.com/user-attachments/assets/c89b96ad-abb5-4571-b88c-d09893452617" />

<img width="1779" height="594" alt="Screenshot from 2025-10-08 00-50-53" src="https://github.com/user-attachments/assets/6d8ee7f0-c099-41b8-ba3c-d76bbe702295" />

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Bluehorizon65/google_hackathon.git
cd google_hackathon
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn python-multipart opencv-python numpy matplotlib pillow
```

### 3. Start the API Server
```bash
uvicorn rooftop_api:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the API
- **API Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs` ← **Start here!**
- **Health Check**: `http://localhost:8000/health`

## 📡 API Usage

### Endpoint: `POST /detect-rooftop`

**Input:**
- `image`: Google Maps satellite image file
- `num_panels`: Number of solar panels to place

**Output:**
```json
{
  "success": true,
  "data": {
    "length": 36.6,           // Roof length in meters
    "breadth": 17.3,          // Roof breadth in meters
    "panels_placed": 25,      // Panels successfully placed
    "result_image": "base64..." // Result image with panels
  }
}
```

## 💻 Usage Examples

### Using curl
```bash
curl -X POST "http://localhost:8000/detect-rooftop" \
     -F "image=@your_satellite_image.png" \
     -F "num_panels=50"
```

### Using Python
```python
import requests
import base64
from PIL import Image
import io

# Send request
with open('satellite_image.png', 'rb') as f:
    files = {'image': ('image.png', f, 'image/png')}
    data = {'num_panels': 50}
    response = requests.post('http://localhost:8000/detect-rooftop', 
                           files=files, data=data)

# Get results
result = response.json()
print(f"Roof Dimensions: {result['data']['length']}m × {result['data']['breadth']}m")
print(f"Panels Placed: {result['data']['panels_placed']}")

# Save result image
img_data = base64.b64decode(result['data']['result_image'])
img = Image.open(io.BytesIO(img_data))
img.save('result_with_panels.jpg')
```

### Using JavaScript/Fetch
```javascript
const formData = new FormData();
formData.append('image', imageFile);
formData.append('num_panels', 50);

fetch('http://localhost:8000/detect-rooftop', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Roof Length:', data.data.length + 'm');
    console.log('Roof Breadth:', data.data.breadth + 'm');
    console.log('Panels Placed:', data.data.panels_placed);
});
```

## 🛠️ Alternative: Run Without API

You can also run the detection directly:
```bash
python rooftop_detection_gk.py --panels 50
```

## 📁 Project Structure

```
├── rooftop_api.py          # FastAPI application
├── rooftop_detection_gk.py # Core detection script
├── test_api.py             # API test client
├── start_api.sh            # Startup script
├── api_requirements.txt    # API dependencies
├── requirements.txt        # Core dependencies
└── testcases/              # Sample images
```

## 🔧 Key Features

- ✅ **Google Maps Integration**: Works with satellite images from Google Maps
- ✅ **Real-world Measurements**: Converts pixels to meters (0.15m/pixel for zoom level 20)
- ✅ **Adaptive Panel Sizing**: Automatically adjusts panel size based on roof space
- ✅ **Average Calculations**: Combines multiple detection tolerances for accuracy
- ✅ **Base64 Output**: Easy integration with web applications
- ✅ **Interactive Docs**: Built-in API documentation at `/docs`

## 📊 Technical Details

- **Pixel Conversion**: 0.15 meters per pixel (Google Maps zoom level 20)
- **Panel Sizes**: 40×25 → 30×20 → 20×15 → 12×8 (adaptive)
- **Detection**: Multi-tolerance rooftop color detection
- **Measurements**: Averaged from multiple detection methods

## 🌐 Perfect For

- 3D roof visualization applications
- Solar panel planning tools
- Real estate analysis systems
- Construction planning software
- IoT and mobile applications

## 🆘 Need Help?

1. **Visit Interactive Docs**: Go to `http://localhost:8000/docs` after starting the server
2. **Test Health**: Check `http://localhost:8000/health`
3. **Run Test Client**: `python test_api.py`

## 📝 License

MIT License - Feel free to use and modify!


## using the roof top api

`sleep 3 && curl -X POST "http://localhost:8000/detect-rooftop" -H "Content-Type: application/json" -d '{"image_path": "testcases/image copy 2.png", "num_panels": 25}'`

