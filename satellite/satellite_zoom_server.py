"""
SATELLITE ZOOM SERVER - SIMPLE NUMBERED LEVELS
==============================================

FastAPI server with simple numbered zoom levels (1-7) for easy selection.
Each number corresponds to a different zoom level and image quality.

Installation:
  pip install fastapi uvicorn requests pillow

Usage:
  python satellite_zoom_server.py
  
API: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import math
from PIL import Image
from io import BytesIO
import os
import uuid
from datetime import datetime
from typing import Optional, List
import uvicorn

# Initialize FastAPI
app = FastAPI(
    title="Satellite Zoom Server",
    description="Simple satellite imagery with numbered zoom levels",
    version="1.0.0"
)

# Configuration
OUTPUT_DIR = "satellite_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Simple Zoom Level Configuration (1-7 for easy selection)
ZOOM_OPTIONS = {
    1: {"zoom": 15, "name": "Wide_Area", "description": "Wide area view", "resolution": "~5m/pixel", "coverage": "~5km area"},
    2: {"zoom": 16, "name": "District", "description": "District/neighborhood", "resolution": "~2.5m/pixel", "coverage": "~2.5km area"},
    3: {"zoom": 17, "name": "Buildings", "description": "Buildings visible", "resolution": "~1.2m/pixel", "coverage": "~1.2km area"},
    4: {"zoom": 18, "name": "Building_Detail", "description": "Building details", "resolution": "~0.6m/pixel", "coverage": "~600m area"},
    5: {"zoom": 19, "name": "Rooftop", "description": "Rooftop level", "resolution": "~0.3m/pixel", "coverage": "~300m area"},
    6: {"zoom": 20, "name": "High_Detail", "description": "High detail", "resolution": "~0.15m/pixel", "coverage": "~150m area"},
    7: {"zoom": 21, "name": "Maximum", "description": "Maximum zoom", "resolution": "~0.07m/pixel", "coverage": "~75m area"}
}

# Request/Response Models
class SatelliteRequest(BaseModel):
    latitude: float
    longitude: float
    location_name: Optional[str] = "My_Location"
    zoom_level: int  # 1-7 for easy selection
    
class ImageResponse(BaseModel):
    success: bool
    zoom_level: int
    zoom_description: str
    filename: str
    resolution_m_per_pixel: float
    coverage_description: str
    image_size: dict
    file_url: str
    processing_time_seconds: float
    error_message: Optional[str] = None

# Helper Functions
def deg2num(lat_deg: float, lon_deg: float, zoom: int) -> tuple:
    """Convert lat/lon to tile coordinates"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    x = int((lon_deg + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (x, y)

def calculate_resolution(lat: float, zoom: int) -> float:
    """Calculate resolution in meters per pixel"""
    return 156543.03392 * math.cos(math.radians(lat)) / (2 ** zoom)

def download_satellite_image(lat: float, lon: float, zoom: int) -> tuple:
    """Download and stitch satellite tiles"""
    center_x, center_y = deg2num(lat, lon, zoom)
    
    # Use 3x3 grid for good coverage
    tiles = []
    for dy in [-1, 0, 1]:
        row = []
        for dx in [-1, 0, 1]:
            tile_x = center_x + dx
            tile_y = center_y + dy
            
            url = f"https://mt1.google.com/vt/lyrs=s&x={tile_x}&y={tile_y}&z={zoom}"
            
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                tile_img = Image.open(BytesIO(response.content))
                row.append(tile_img)
            except:
                # Gray fallback tile
                row.append(Image.new('RGB', (256, 256), (128, 128, 128)))
        
        tiles.append(row)
    
    # Stitch tiles into final image
    final_image = Image.new('RGB', (768, 768))  # 3x3 tiles = 768x768
    
    for row_idx, row in enumerate(tiles):
        for col_idx, tile in enumerate(row):
            x = col_idx * 256
            y = row_idx * 256
            final_image.paste(tile, (x, y))
    
    resolution = calculate_resolution(lat, zoom)
    return final_image, resolution

# API Endpoints
@app.get("/")
async def root():
    """Service information"""
    return {
        "service": "Satellite Zoom Server",
        "zoom_levels": ZOOM_OPTIONS,
        "usage": "POST /satellite with zoom_level 1-7",
        "docs": "/docs"
    }

@app.get("/zoom-levels")
async def get_zoom_levels():
    """Get all available zoom levels"""
    return {
        "zoom_levels": ZOOM_OPTIONS,
        "usage": {
            "1-2": "Area overview",
            "3-4": "Building analysis", 
            "5-6": "Rooftop analysis",
            "7": "Maximum detail"
        }
    }

@app.post("/satellite", response_model=ImageResponse)
async def get_satellite_image(request: SatelliteRequest):
    """Get satellite image with numbered zoom level (1-7)"""
    
    start_time = datetime.now()
    
    # Validate zoom level
    if request.zoom_level not in ZOOM_OPTIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid zoom level. Use 1-7. Available: {list(ZOOM_OPTIONS.keys())}"
        )
    
    try:
        zoom_config = ZOOM_OPTIONS[request.zoom_level]
        actual_zoom = zoom_config["zoom"]
        
        # Download satellite image
        image, resolution = download_satellite_image(
            request.latitude, 
            request.longitude, 
            actual_zoom
        )
        
        # Generate filename
        filename = f"{request.location_name}_level{request.zoom_level}_{uuid.uuid4().hex[:8]}.png"
        file_path = os.path.join(OUTPUT_DIR, filename)
        
        # Save image
        image.save(file_path)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ImageResponse(
            success=True,
            zoom_level=request.zoom_level,
            zoom_description=zoom_config["description"],
            filename=filename,
            resolution_m_per_pixel=resolution,
            coverage_description=zoom_config["coverage"],
            image_size={"width": image.size[0], "height": image.size[1]},
            file_url=f"/download/{filename}",
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        return ImageResponse(
            success=False,
            zoom_level=request.zoom_level,
            zoom_description="Error",
            filename="",
            resolution_m_per_pixel=0,
            coverage_description="",
            image_size={},
            file_url="",
            processing_time_seconds=0,
            error_message=str(e)
        )

@app.get("/satellite-simple")
async def get_satellite_simple(
    latitude: float = Query(..., description="Latitude coordinate"),
    longitude: float = Query(..., description="Longitude coordinate"),
    zoom_level: int = Query(..., description="Zoom level (1-7)"),
    location_name: str = Query("My_Location", description="Location name")
):
    """Simple GET endpoint for satellite images"""
    
    request = SatelliteRequest(
        latitude=latitude,
        longitude=longitude,
        zoom_level=zoom_level,
        location_name=location_name
    )
    
    return await get_satellite_image(request)

@app.get("/download/{filename}")
async def download_image(filename: str):
    """Download the generated image"""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Image not found")

@app.get("/test-interface")
async def test_interface():
    """Simple HTML test interface"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Satellite Zoom Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            .result { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            .zoom-info { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 10px 0; }
            img { max-width: 100%; border-radius: 5px; margin: 10px 0; }
            .loading { color: #007bff; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛰️ Satellite Zoom Server</h1>
            <p>Get high-resolution satellite images with simple numbered zoom levels!</p>
            
            <div class="zoom-info">
                <h3>📊 Zoom Levels:</h3>
                <p><strong>1-2:</strong> Area overview (2-5m/pixel)</p>  
                <p><strong>3-4:</strong> Building analysis (0.6-1.2m/pixel)</p>
                <p><strong>5-6:</strong> Rooftop analysis (0.15-0.3m/pixel) ⭐</p>
                <p><strong>7:</strong> Maximum detail (0.07m/pixel) 🎯</p>
            </div>
            
            <form id="satelliteForm">
                <div class="form-group">
                    <label>📍 Latitude:</label>
                    <input type="number" id="latitude" step="any" value="10.94022744551817" required>
                </div>
                
                <div class="form-group">
                    <label>📍 Longitude:</label>
                    <input type="number" id="longitude" step="any" value="76.74503248558553" required>
                </div>
                
                <div class="form-group">
                    <label>🏷️ Location Name:</label>
                    <input type="text" id="locationName" value="My_Location">
                </div>
                
                <div class="form-group">
                    <label>🔍 Zoom Level:</label>
                    <select id="zoomLevel">
                        <option value="1">1 - Wide Area (~5m/pixel)</option>
                        <option value="2">2 - District (~2.5m/pixel)</option>
                        <option value="3">3 - Buildings (~1.2m/pixel)</option>
                        <option value="4">4 - Building Detail (~0.6m/pixel)</option>
                        <option value="5" selected>5 - Rooftop (~0.3m/pixel) ⭐</option>
                        <option value="6">6 - High Detail (~0.15m/pixel)</option>
                        <option value="7">7 - Maximum (~0.07m/pixel) 🎯</option>
                    </select>
                </div>
                
                <button type="submit">🛰️ Get Satellite Image</button>
            </form>
            
            <div id="loading" style="display:none;" class="loading">
                🛰️ Downloading satellite tiles... Please wait...
            </div>
            
            <div id="result"></div>
        </div>
        
        <script>
            document.getElementById('satelliteForm').onsubmit = async function(e) {
                e.preventDefault();
                
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                
                loading.style.display = 'block';
                result.innerHTML = '';
                
                const formData = {
                    latitude: parseFloat(document.getElementById('latitude').value),
                    longitude: parseFloat(document.getElementById('longitude').value),
                    location_name: document.getElementById('locationName').value,
                    zoom_level: parseInt(document.getElementById('zoomLevel').value)
                };
                
                try {
                    const response = await fetch('/satellite', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        result.innerHTML = `
                            <div class="result">
                                <h3>✅ Success!</h3>
                                <p><strong>Zoom Level:</strong> ${data.zoom_level} - ${data.zoom_description}</p>
                                <p><strong>Resolution:</strong> ${data.resolution_m_per_pixel.toFixed(3)} m/pixel</p>
                                <p><strong>Coverage:</strong> ${data.coverage_description}</p>
                                <p><strong>Image Size:</strong> ${data.image_size.width} × ${data.image_size.height} pixels</p>
                                <p><strong>Processing Time:</strong> ${data.processing_time_seconds.toFixed(2)} seconds</p>
                                <img src="${data.file_url}" alt="Satellite Image">
                                <p><a href="${data.file_url}" download="📥 Download Image" style="color: #007bff;">📥 Download Image</a></p>
                            </div>
                        `;
                    } else {
                        result.innerHTML = `
                            <div class="result">
                                <h3>❌ Error</h3>
                                <p>${data.error_message}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    result.innerHTML = `
                        <div class="result">
                            <h3>❌ Network Error</h3>
                            <p>${error.message}</p>
                        </div>
                    `;
                }
                
                loading.style.display = 'none';
            };
        </script>
    </body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html)

if __name__ == "__main__":
    print("🚀 SATELLITE ZOOM SERVER")
    print("=" * 40)
    print("🌐 Server: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🖥️ Test Interface: http://localhost:8000/test-interface")
    print("🔍 Zoom Levels: 1-7 (1=wide, 7=maximum detail)")
    print("📁 Images saved to: satellite_images/")
    print()
    print("✨ Starting server...")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)