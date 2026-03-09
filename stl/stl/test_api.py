import requests

url = "http://127.0.0.1:8007/generate-stl/"
params = {
    "roof_length": 100,
    "roof_width": 40,
    "num_panels": 12,
    "tilt_angle": 20
}

response = requests.post(url, params=params)
if response.status_code == 200:
    with open("downloaded_model.glb", "wb") as f:
        f.write(response.content)
    print("GLB file downloaded as downloaded_model.glb")
else:
    print("Error:", response.status_code, response.text)