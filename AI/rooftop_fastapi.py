from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cv2
import numpy as np
import os
import json
from datetime import datetime
from typing import Optional

app = FastAPI(title="Rooftop Detection API", version="1.0.0")

# Configuration
TOLERANCE_VALUES = [3, 2]
METERS_PER_PIXEL = 0.15  # For Google Maps zoom level 20
OUTPUT_FOLDER = "output_images"

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

class RooftopRequest(BaseModel):
    image_path: str
    num_panels: int

class RooftopResponse(BaseModel):
    length: float
    width: float
    image_location: str

def detect_rooftops_targeted(image, target_colors, tolerance=12):
    """Detect rooftops in the image using targeted color detection"""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    combined_mask = np.zeros(image_rgb.shape[:2], dtype=np.uint8)
    
    for i, (r, g, b) in enumerate(target_colors):
        lower = np.array([max(0, r-tolerance), max(0, g-tolerance), max(0, b-tolerance)])
        upper = np.array([min(255, r+tolerance), min(255, g+tolerance), min(255, b+tolerance)])
        
        color_mask = cv2.inRange(image_rgb, lower, upper)
        combined_mask = cv2.bitwise_or(combined_mask, color_mask)
    
    kernel = np.ones((4, 4), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    final_mask = np.zeros_like(combined_mask)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        if 150 < area < 50000:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            if 0.1 <= aspect_ratio <= 10.0:
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                solidity = area / hull_area if hull_area > 0 else 0
                
                if solidity > 0.4:
                    cv2.fillPoly(final_mask, [contour], 255)
    
    return final_mask

def place_solar_panels_custom(image, rooftop_mask, target_count):
    """Place solar panels on detected rooftops with adaptive sizing"""
    result_image = image.copy()
    
    contours, _ = cv2.findContours(rooftop_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    # Panel size configurations
    panel_configs = [
        {"size": (40, 25), "gap": 3, "coverage": 0.4},
        {"size": (30, 20), "gap": 2, "coverage": 0.3},
        {"size": (20, 15), "gap": 2, "coverage": 0.25},
        {"size": (12, 8), "gap": 1, "coverage": 0.15}
    ]
    
    for config in panel_configs:
        panel_width, panel_height = config["size"]
        gap = config["gap"]
        min_coverage = config["coverage"]
        
        possible_positions = []
        
        for contour in contours:
            x_cont, y_cont, w_cont, h_cont = cv2.boundingRect(contour)
            
            for y in range(y_cont, y_cont + h_cont - panel_height + 1, panel_height + gap):
                for x in range(x_cont, x_cont + w_cont - panel_width + 1, panel_width + gap):
                    panel_roi = rooftop_mask[y:y+panel_height, x:x+panel_width]
                    
                    if panel_roi.size > 0:
                        rooftop_pixels = np.sum(panel_roi == 255)
                        total_pixels = panel_roi.size
                        coverage = rooftop_pixels / total_pixels
                        
                        if coverage >= min_coverage:
                            possible_positions.append((x, y, coverage))
        
        if len(possible_positions) >= target_count:
            # Place panels
            possible_positions.sort(key=lambda pos: pos[2], reverse=True)
            
            panels_placed = 0
            used_positions = set()
            
            # Adjust text size based on panel size
            if panel_width >= 30:
                font_scale = 0.7
                font_thickness = 2
                text_offset = 8
            elif panel_width >= 20:
                font_scale = 0.5
                font_thickness = 1
                text_offset = 6
            else:
                font_scale = 0.3
                font_thickness = 1
                text_offset = 4
            
            for x, y, coverage in possible_positions:
                if panels_placed >= target_count:
                    break
                    
                overlap = False
                for used_x, used_y in used_positions:
                    if (abs(x - used_x) < panel_width + gap and 
                        abs(y - used_y) < panel_height + gap):
                        overlap = True
                        break
                
                if not overlap:
                    cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (255, 0, 0), -1)
                    cv2.rectangle(result_image, (x, y), (x + panel_width, y + panel_height), (0, 0, 0), 1)
                    
                    panel_num = panels_placed + 1
                    text_x = x + panel_width // 2 - text_offset
                    text_y = y + panel_height // 2 + 3
                    
                    if panel_width >= 20:
                        cv2.rectangle(result_image, (text_x-text_offset, text_y-10), 
                                    (text_x+text_offset*2, text_y+2), (0, 0, 0), -1)
                    
                    cv2.putText(result_image, str(panel_num), (text_x, text_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
                    
                    used_positions.add((x, y))
                    panels_placed += 1
            
            return result_image, panels_placed
    
    return result_image, 0

def calculate_roof_measurements(rooftop_mask):
    """Calculate roof measurements from the mask"""
    contours, _ = cv2.findContours(rooftop_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    # Get ALL contours to find the full polygon dimensions
    all_points = []
    for contour in contours:
        for point in contour:
            all_points.append(point[0])
    
    if not all_points:
        return None
    
    all_points = np.array(all_points)
    # Get the full bounding rectangle of ALL rooftop areas
    x_min = np.min(all_points[:, 0])
    x_max = np.max(all_points[:, 0])
    y_min = np.min(all_points[:, 1])
    y_max = np.max(all_points[:, 1])
    
    # Full polygon dimensions
    full_width = x_max - x_min
    full_height = y_max - y_min
    length = max(full_width, full_height)
    breadth = min(full_width, full_height)
    
    # Convert to meters
    length_m = length * METERS_PER_PIXEL
    breadth_m = breadth * METERS_PER_PIXEL
    
    return {
        'length_m': length_m,
        'breadth_m': breadth_m
    }

def process_rooftop_detection(image_path, num_panels):
    """Main processing function"""
    # Target colors for rooftop detection
    target_colors = [
        (60, 49, 55), (55, 40, 45), (72, 53, 55), (81, 59, 64),
        (86, 63, 69), (79, 60, 66), (92, 70, 76), (74, 52, 58),
        (85, 64, 70), (78, 57, 63), (68, 50, 55), (89, 66, 72),
        (82, 61, 66), (58, 45, 51), (96, 73, 79), (70, 52, 57),
        (120, 100, 90), (110, 95, 85), (130, 110, 100), (100, 85, 75),
        (140, 120, 110), (125, 105, 95), (115, 100, 90), (135, 115, 105),
        (150, 120, 100), (160, 130, 110), (140, 110, 90), (155, 125, 105),
        (90, 85, 80), (105, 100, 95), (95, 90, 85), (110, 105, 100)
    ]
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    results = []
    
    # Process with different tolerances
    for tolerance in TOLERANCE_VALUES:
        rooftop_mask = detect_rooftops_targeted(image, target_colors, tolerance)
        measurements = calculate_roof_measurements(rooftop_mask)
        
        if measurements:
            result_image, panels_placed = place_solar_panels_custom(image, rooftop_mask, num_panels)
            
            results.append({
                'tolerance': tolerance,
                'measurements': measurements,
                'result_image': result_image,
                'panels_placed': panels_placed
            })
    
    # Calculate average measurements
    if results:
        valid_measurements = [r['measurements'] for r in results if r['measurements'] is not None]
        if valid_measurements:
            avg_length = sum(m['length_m'] for m in valid_measurements) / len(valid_measurements)
            avg_breadth = sum(m['breadth_m'] for m in valid_measurements) / len(valid_measurements)
            
            # Get best result (highest panel placement)
            best_result = max(results, key=lambda x: x['panels_placed'])
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"rooftop_result_{timestamp}.jpg"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            # Save result image
            cv2.imwrite(output_path, best_result['result_image'])
            
            return {
                'length': round(avg_length, 1),
                'breadth': round(avg_breadth, 1),
                'output_path': output_path
            }
    
    return None

@app.post("/detect-rooftop", response_model=RooftopResponse)
async def detect_rooftop(request: RooftopRequest):
    """
    Detect rooftops and place solar panels
    
    **Input:**
    - image_path: Path to the satellite image file
    - num_panels: Number of solar panels to place
    
    **Output:**
    - length: Roof length in meters
    - width: Roof breadth in meters  
    - image_location: Path to the generated result image
    """
    
    try:
        # Validate inputs
        if request.num_panels <= 0:
            raise HTTPException(status_code=400, detail="Number of panels must be positive")
        
        if not os.path.exists(request.image_path):
            raise HTTPException(status_code=404, detail=f"Image file not found: {request.image_path}")
        
        # Process the image
        result = process_rooftop_detection(request.image_path, request.num_panels)
        
        if result is None:
            raise HTTPException(status_code=404, detail="No rooftops detected in the image")
        
        return RooftopResponse(
            length=result['length'],
            width=result['breadth'], 
            image_location=result['output_path']
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Rooftop Detection API",
        "version": "1.0.0",
        "endpoints": {
            "/detect-rooftop": "POST - Main detection endpoint",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)