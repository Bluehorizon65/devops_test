# generate_model.py
import trimesh
import numpy as np

# -------------------------------
# Step 1: Get input from user
# -------------------------------
roof_length = float(input("Enter roof length (meters): "))
roof_width = float(input("Enter roof width (meters): "))
num_panels = int(input("Enter number of solar panels: "))
tilt_angle = float(input("Enter tilt angle of solar panels (degrees): "))

# -------------------------------
# Step 2: Create roof (slanted)
# -------------------------------
roof_thickness = 0.3
roof_slope_angle = 15  # roof tilt in degrees
roof_slope_height = np.tan(np.radians(roof_slope_angle)) * roof_width  # height difference

# Create rectangular roof box
roof = trimesh.creation.box(extents=(roof_length, roof_width, roof_thickness))
roof.apply_translation((roof_length / 2, roof_width / 2, roof_thickness / 2))

# Tilt the roof along x-axis (slant along y-axis)
rotation_matrix = trimesh.transformations.rotation_matrix(
    np.radians(-roof_slope_angle), [1, 0, 0], [0, 0, 0]
)
roof.apply_transform(rotation_matrix)

# Lift roof to visible height
roof.apply_translation((0, 0, 2))

# Give roof a color (brown)
roof.visual.vertex_colors = [139, 69, 19, 255]  # RGBA - brown color

# -------------------------------
# Step 3: Create solar panels
# -------------------------------
panel_length = roof_length / num_panels
panel_width = roof_width / 2
panel_thickness = 0.1
panel_offset = 0.15  # above roof surface

panels = []
for i in range(num_panels):
    # Create one panel box
    panel = trimesh.creation.box(extents=(panel_length - 0.3, panel_width - 0.3, panel_thickness))
    
    # Position of the panel on the roof
    x_pos = (i + 0.5) * panel_length
    y_pos = roof_width / 2
    z_pos = roof_slope_height + roof_thickness + panel_offset + 2  # lifted above roof
    
    panel.apply_translation((x_pos, y_pos, z_pos))
    
    # Apply tilt angle to panel (around x-axis)
    tilt_matrix = trimesh.transformations.rotation_matrix(
        np.radians(-tilt_angle), [1, 0, 0], [x_pos, y_pos, z_pos]
    )
    panel.apply_transform(tilt_matrix)
    
    # Set color to blue
    panel.visual.vertex_colors = [0, 100, 255, 255]
    
    panels.append(panel)

# -------------------------------
# Step 4: Combine meshes and export
# -------------------------------
scene = roof.copy()
for panel in panels:
    scene = trimesh.util.concatenate([scene, panel])

# Save as STL (geometry only) and GLB (for colors)
scene.export("model.stl")
scene.export("model.glb")

print("\n✅ Models successfully created!")
print("Files generated:")
print(" - model.stl (geometry only)")
print(" - model.glb (with colors for viewing in browser)")
print("\nNow run 'view_model.py' to view the colored 3D model.")
