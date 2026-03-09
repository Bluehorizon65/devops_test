from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Area Pipeline API", version="1.0")

# --- Input Schema ---
class AreaInput(BaseModel):
    roof_pixels: int
    meters_per_pixel: float
    solar_panel_area: float


class AreaOutput(BaseModel):
    roof_area: float
    usable_area: float
    no_of_panels: int


@app.post("/calculate_area", response_model=AreaOutput)
def calculate_area(data: AreaInput):
    """
    Calculate roof area, usable area, and number of solar panels.
    """
    # Calculate areas
    roof_area = data.roof_pixels * (data.meters_per_pixel ** 2)
    usable_area = roof_area * 0.75
    no_of_panels = int(usable_area / data.solar_panel_area)

    return AreaOutput(
        roof_area=round(roof_area, 2),
        usable_area=round(usable_area, 2),
        no_of_panels=no_of_panels
    )
