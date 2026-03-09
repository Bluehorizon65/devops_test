# google_hackathon
solar based web application


example input :-
```
{
  "roof_pixels": 25000,
  "meters_per_pixel": 0.1,
  "solar_panel_area": 1.6
}
```

# 3D Roof and Solar Panel Model Generator

This project allows you to generate and visualize a 3D model of a sloped roof with solar panels using Python, FastAPI, Flask, and Trimesh. You can generate models via a web interface or API and view them interactively in your browser.

## Features
- Generate 3D models of roofs with customizable solar panel layouts
- REST API for model generation (`/generate-stl/`)
- Web interface for interactive input and 3D visualization
- Download models in `.glb` and `.stl` formats

## Requirements
- Python 3.8+
- See `requirements.txt` for dependencies

## Installation
1. Clone this repository or copy the files to your project directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Start the FastAPI Backend
This serves the model generation API on port 8000.
```bash
uvicorn api:app --reload
```

### 2. Start the Flask Web App
This provides a web form and 3D viewer on port 5000.
```bash
python web.py
```

### 3. Generate and View Models
- Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.
- Enter roof and panel parameters, submit, and view the 3D model interactively.

### 4. API Usage Example
Send a POST request to generate a model:
```python
import requests
url = "http://127.0.0.1:8000/generate-stl/"
params = {
    "roof_length": 10,
    "roof_width": 5,
    "num_panels": 4,
    "tilt_angle": 20
}
response = requests.post(url, params=params)
if response.status_code == 200:
    with open("model.glb", "wb") as f:
        f.write(response.content)
```

## File Overview
- `api.py` - FastAPI backend for model generation
- `web.py` - Flask web app for user input and 3D visualization
- `create.py` - Standalone script for generating models from the command line
- `test_api.py` - Example script for testing the API
- `model.stl`, `model.glb`, `output_model.glb` - Generated 3D model files

## Notes
- Ensure both FastAPI and Flask servers are running for full functionality.
- Models are generated using Trimesh and exported in both STL and GLB formats.
- The web viewer uses Plotly for interactive 3D visualization.

## License
MIT License
