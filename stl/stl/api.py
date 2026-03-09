from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import trimesh
import numpy as np
import os       

app = FastAPI()

@app.post("/generate-stl/")
def generate_stl(
    roof_length: float = Query(..., gt=0),
    roof_width: float = Query(..., gt=0),
    num_panels: int = Query(..., gt=0),
    tilt_angle: float = Query(...),
):
    roof_thickness = 0.3
    roof_slope_angle = 15
    roof_slope_height = np.tan(np.radians(roof_slope_angle)) * roof_width

    # Create roof
    roof = trimesh.creation.box(extents=(roof_length, roof_width, roof_thickness))
    roof.apply_translation((roof_length / 2, roof_width / 2, roof_thickness / 2))
    rotation_matrix = trimesh.transformations.rotation_matrix(
        np.radians(-roof_slope_angle), [1, 0, 0], [0, 0, 0]
    )
    roof.apply_transform(rotation_matrix)
    roof.apply_translation((0, 0, 2))
    roof.visual.vertex_colors = [139, 69, 19, 255]


    panel_length = roof_length / num_panels
    panel_width = roof_width / 2
    panel_thickness = 0.1
    panel_offset = 0.15

    panels = []
    for i in range(num_panels):
        panel = trimesh.creation.box(extents=(panel_length - 0.3, panel_width - 0.3, panel_thickness))
        x_pos = (i + 0.5) * panel_length
        y_pos = roof_width / 2
        z_pos = roof_slope_height + roof_thickness + panel_offset + 2
        panel.apply_translation((x_pos, y_pos, z_pos))
        tilt_matrix = trimesh.transformations.rotation_matrix(
            np.radians(-tilt_angle), [1, 0, 0], [x_pos, y_pos, z_pos]
        )
        panel.apply_transform(tilt_matrix)
        panel.visual.vertex_colors = [0, 100, 255, 255]
        panels.append(panel)

    scene = roof.copy()
    for panel in panels:
        scene = trimesh.util.concatenate([scene, panel])

    out_path = "output_model.glb"
    scene.export(out_path)

    return FileResponse(out_path, media_type="model/gltf-binary", filename="model.glb")