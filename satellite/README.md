# 🛰️ Satellite Zoom Server

A FastAPI-based satellite imagery service with simple numbered zoom levels (1-7) for easy high-resolution satellite image acquisition. Perfect for rooftop analysis, building detection, and area mapping.

## 🚀 Features

### Core Functionality
- **Simple Zoom Levels**: Easy numbered levels 1-7 instead of complex zoom values
- **High-Resolution Imagery**: Google Satellite tiles with up to 0.07m/pixel resolution
- **Tile Stitching**: Automatic 3x3 tile stitching for larger coverage areas
- **Multiple APIs**: Both POST and GET endpoints for flexibility
- **Web Interface**: Built-in HTML interface for testing

### Zoom Level Guide
| Level | Description | Resolution | Coverage | Best For |
|-------|-------------|------------|----------|----------|
| **1** | Wide Area | ~5m/pixel | ~5km area | Regional overview |
| **2** | District | ~2.5m/pixel | ~2.5km area | Neighborhood mapping |
| **3** | Buildings | ~1.2m/pixel | ~1.2km area | Building identification |
| **4** | Building Detail | ~0.6m/pixel | ~600m area | Building analysis |
| **5** | Rooftop | ~0.3m/pixel | ~300m area | ⭐ Rooftop analysis |
| **6** | High Detail | ~0.15m/pixel | ~150m area | Detailed structure analysis |
| **7** | Maximum | ~0.07m/pixel | ~75m area | 🎯 Maximum detail |

## 📋 System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows/Linux/macOS
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 100MB for dependencies + image storage
- **Internet**: Required for Google Satellite API access

## 🛠️ Installation

### 1. Navigate to Directory
```bash
cd google_hackathon_satellite
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
python simple_requests.py
```

## 🚀 Quick Start

### 1. Start the Server
```bash
python satellite_zoom_server.py
```
Server runs on: `http://localhost:8000`

### 2. Access Services
- **Interactive Docs**: `http://localhost:8000/docs`
- **Web Interface**: `http://localhost:8000/test-interface`
- **Zoom Levels**: `http://localhost:8000/zoom-levels`

### 3. Basic Usage
```python
import requests

# Simple satellite image request
data = {
    "latitude": 10.933519,
    "longitude": 76.743176,
    "location_name": "My_Location",
    "zoom_level": 5  # Rooftop level
}

response = requests.post("http://localhost:8000/satellite", json=data)
result = response.json()

print(f"Resolution: {result['resolution_m_per_pixel']:.3f} m/pixel")
print(f"Download: http://localhost:8000{result['file_url']}")
```

## 📡 API Endpoints

### Main Satellite Endpoint
**POST** `/satellite`

Get high-resolution satellite imagery with numbered zoom levels.

#### Request Body:
```json
{
  "latitude": 10.933519,
  "longitude": 76.743176,
  "location_name": "My_Location",
  "zoom_level": 5
}
```

#### Response:
```json
{
  "success": true,
  "zoom_level": 5,
  "zoom_description": "Rooftop level",
  "filename": "My_Location_level5_abc123.png",
  "resolution_m_per_pixel": 0.298,
  "coverage_description": "~300m area",
  "image_size": {"width": 768, "height": 768},
  "file_url": "/download/My_Location_level5_abc123.png",
  "processing_time_seconds": 2.45
}
```

### Alternative GET Endpoint
**GET** `/satellite-simple`

Simple URL-based satellite image requests.

```
GET /satellite-simple?latitude=10.933519&longitude=76.743176&zoom_level=5&location_name=My_Location
```

### Utility Endpoints
- **GET** `/` - Service information
- **GET** `/zoom-levels` - Available zoom levels
- **GET** `/download/{filename}` - Download generated images
- **GET** `/test-interface` - Web testing interface

## 📊 API Parameters

### Required Parameters
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `latitude` | float | Location latitude (decimal degrees) | 10.933519 |
| `longitude` | float | Location longitude (decimal degrees) | 76.743176 |
| `zoom_level` | int | Zoom level (1-7) | 5 |

### Optional Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `location_name` | string | "My_Location" | Custom name for saved image |

## 💡 Usage Examples

### 1. Rooftop Analysis (Recommended)
```python
import requests

# Perfect for solar panel analysis
data = {
    "latitude": 28.6139,    # New Delhi
    "longitude": 77.2090,
    "location_name": "Delhi_Rooftop",
    "zoom_level": 5         # Rooftop level - 0.3m/pixel
}

response = requests.post("http://localhost:8000/satellite", json=data)
result = response.json()

if result['success']:
    print(f"Rooftop image saved: {result['filename']}")
    print(f"Resolution: {result['resolution_m_per_pixel']:.3f} m/pixel")
```

### 2. Building Analysis
```python
# Identify building structures
data = {
    "latitude": 13.0827,    # Chennai
    "longitude": 80.2707,
    "location_name": "Chennai_Buildings",
    "zoom_level": 3         # Buildings visible - 1.2m/pixel
}

response = requests.post("http://localhost:8000/satellite", json=data)
```

### 3. Maximum Detail Analysis
```python
# Highest resolution for detailed analysis
data = {
    "latitude": 12.9716,    # Bangalore
    "longitude": 77.5946,
    "location_name": "Bangalore_MaxDetail",
    "zoom_level": 7         # Maximum zoom - 0.07m/pixel
}

response = requests.post("http://localhost:8000/satellite", json=data)
```

### 4. Multiple Zoom Levels
```python
# Compare different zoom levels
location = {"latitude": 19.0760, "longitude": 72.8777}  # Mumbai

for zoom in [3, 5, 7]:  # Buildings, Rooftop, Maximum
    data = {
        **location,
        "location_name": f"Mumbai_Zoom{zoom}",
        "zoom_level": zoom
    }
    
    response = requests.post("http://localhost:8000/satellite", json=data)
    result = response.json()
    
    if result['success']:
        print(f"Zoom {zoom}: {result['resolution_m_per_pixel']:.3f} m/pixel")
```

## 🔧 Configuration

### Image Output
- **Directory**: `satellite_images/` (auto-created)
- **Format**: PNG (768x768 pixels)
- **Naming**: `{location_name}_level{zoom}_{unique_id}.png`

### Server Settings
- **Host**: 0.0.0.0 (accessible from network)
- **Port**: 8000
- **Timeout**: 10 seconds per tile request

### Input Validation
- **Latitude**: -90 to 90 degrees
- **Longitude**: -180 to 180 degrees
- **Zoom Level**: 1 to 7 only
- **Location Name**: Any valid filename string

## 📁 Project Structure

```
google_hackathon_satellite/
├── satellite_zoom_server.py    # Main FastAPI server
├── simple_requests.py          # Example client usage
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── satellite_images/           # Generated images (auto-created)
    ├── My_Location_level5_abc123.png
    └── ...
```

## 🧪 Testing

### Run Example Client
```bash
python simple_requests.py
```

### Test Different Locations
Edit coordinates in `simple_requests.py`:
```python
# Change these coordinates for your location
my_latitude = 10.933519    # Your latitude
my_longitude = 76.743176   # Your longitude
my_location_name = "My_Custom_Location"
my_zoom_level = 5          # 1-7
```

### Web Interface Testing
1. Start server: `python satellite_zoom_server.py`
2. Open browser: `http://localhost:8000/test-interface`
3. Enter coordinates and select zoom level
4. Click "Get Satellite Image"

## ⚡ Performance

- **Response Time**: 2-10 seconds depending on zoom level
- **Image Size**: 768x768 pixels (3x3 tile grid)
- **Tile Download**: Parallel downloading for speed
- **Fallback**: Gray tiles for failed downloads
- **Memory Usage**: ~50MB per request

## 🌍 Use Cases

### Solar Energy Applications
- **Rooftop Analysis**: Use zoom level 5-6 for solar panel planning
- **Shading Analysis**: Identify trees and obstacles
- **Area Calculation**: Measure available roof space

### Urban Planning
- **Building Detection**: Use zoom level 3-4 for structure mapping
- **Infrastructure**: Identify roads, utilities, buildings
- **Change Detection**: Compare images over time

### Research & Analysis
- **Geographic Studies**: High-resolution area mapping
- **Environmental Monitoring**: Land use analysis
- **Property Assessment**: Building and land evaluation

## 🔄 Integration Examples

### With Solar PV Calculator
```python
# Get satellite image first
satellite_data = {
    "latitude": 11.0183,
    "longitude": 76.9725,
    "zoom_level": 5,
    "location_name": "Solar_Site"
}

satellite_response = requests.post("http://localhost:8000/satellite", json=satellite_data)

# Then use coordinates for PV calculation
pv_data = {
    "latitude": 11.0183,
    "longitude": 76.9725,
    "roof_area": 100,  # Determined from satellite image
    "budget": 500000
}

pv_response = requests.post("http://localhost:8000/calculate_pv_system_v2", json=pv_data)
```

## 🛠️ Troubleshooting

### Common Issues
1. **Connection Error**: Ensure server is running
2. **Invalid Zoom**: Use only levels 1-7
3. **Coordinate Issues**: Check latitude/longitude format
4. **Image Not Found**: Verify filename in response
5. **Slow Response**: Normal for high zoom levels

### Error Responses
```json
{
  "success": false,
  "error_message": "Invalid zoom level. Use 1-7.",
  "zoom_level": 8,
  "processing_time_seconds": 0
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Maps**: Satellite imagery source
- **FastAPI**: Web framework
- **PIL/Pillow**: Image processing
- **Python Community**: Essential libraries

---

**🛰️ High-Resolution Satellite Imagery Made Simple** 📍

*Perfect for rooftop analysis, building detection, and geographic research with easy-to-use numbered zoom levels.*
