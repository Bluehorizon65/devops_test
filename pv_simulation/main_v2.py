# Indian PV System Energy Calculator v2.0 - Enhanced FastAPI Application

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import pandas as pd
import numpy as np
import pvlib
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import requests
import time

from datetime import datetime
import os

# Global variables for caching
modules_df = None
inverters_df = None

def load_datasets():
    """Load Indian solar component datasets"""
    global modules_df, inverters_df
    
    try:
        print("Loading modules dataset...")
        modules_df = pd.read_csv("modules_india_realistic_sample.csv")
        print("Loading inverters dataset...")
        inverters_df = pd.read_csv("inverters_india_realistic_sample.csv")
        print("Datasets loaded successfully")
        print(f"Loaded {len(modules_df)} modules and {len(inverters_df)} inverters")
    except FileNotFoundError as e:
        print(f"Dataset files not found: {e}")
        print("Please ensure CSV files are in the working directory.")
        raise HTTPException(status_code=500, detail="Required dataset files not found")
    except Exception as e:
        print(f"Error loading datasets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load datasets: {str(e)}")

app = FastAPI(
    title="Indian PV System Energy Calculator v2.0",
    description="Enhanced solar energy analysis with budget constraints, brand preferences, and comprehensive JSON output",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    load_datasets()

# Pydantic models with budget and brand features
class PVSystemRequest(BaseModel):
    # Location and System Configuration
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    system_capacity_kw: float = Field(..., gt=0, le=100, description="Desired system capacity in kW")
    year: int = Field(2024, ge=2020, le=2024, description="Year for weather data")
    tilt: Optional[float] = Field(None, ge=0, le=90, description="Panel tilt angle (optional - will optimize if not provided)")
    azimuth: Optional[float] = Field(None, ge=0, le=360, description="Panel azimuth angle (optional - will optimize if not provided)")
    optimize_orientation: bool = Field(True, description="Whether to find optimal tilt/azimuth")
    electricity_rate_inr: float = Field(7.5, gt=0, description="Electricity rate in INR per kWh")
    
    # Budget and preference options (optional)
    budget_inr: Optional[float] = Field(None, gt=0, description="Maximum budget in INR (optional)")
    prefer_brand: Optional[str] = Field(None, description="Preferred brand: 'Adani', 'Waaree', 'Vikram', 'Jinko', 'Longi', etc. (optional)")
    max_payback_years: Optional[float] = Field(None, gt=0, le=25, description="Maximum acceptable payback period in years (optional)")
    
    # Panel count option
    num_panels: Optional[int] = Field(None, gt=0, le=200, description="Specific number of solar panels to use (optional - overrides system_capacity_kw if provided)")

class ModuleInfo(BaseModel):
    model: str
    manufacturer: str
    technology: str
    power_w: float
    efficiency_percent: float
    voltage_voc: float
    current_isc: float
    voltage_vmp: float
    current_imp: float

class InverterInfo(BaseModel):
    model: str
    manufacturer: str
    ac_power_w: float
    dc_power_w: float
    efficiency_percent: float

class OptimizationResult(BaseModel):
    optimal_tilt: float
    optimal_azimuth: float
    optimal_energy_kwh: float
    improvement_percent: float
    tested_combinations: int
    optimization_summary: Dict[str, Any]

class MonthlyBreakdown(BaseModel):
    month: str
    month_number: int
    energy_kwh: float
    daily_average_kwh: float
    peak_day_kwh: float

class BudgetAnalysis(BaseModel):
    requested_budget_inr: Optional[float]
    actual_system_cost_inr: float
    cost_per_kw_inr: float
    budget_utilization_percent: Optional[float]
    preferred_brand: Optional[str]
    budget_remaining_inr: Optional[float]
    cost_breakdown: Dict[str, float]
    financing_options: Dict[str, Any]

class WeatherSummary(BaseModel):
    data_source: str
    total_data_points: int
    average_ghi_kwh_m2_day: float
    peak_ghi_w_m2: float
    average_temperature_c: float
    temperature_range: Dict[str, float]
    seasonal_variation: Dict[str, float]

class PVSystemResponse(BaseModel):
    # System Identification
    calculation_id: str
    timestamp: str
    api_version: str
    
    # Location Information
    location: Dict[str, Any]
    
    # System Configuration
    system_configuration: Dict[str, Any]
    
    # Selected Components
    selected_module: ModuleInfo
    selected_inverter: InverterInfo
    
    # Performance Results
    performance_results: Dict[str, Any]
    
    # Monthly Analysis
    monthly_breakdown: List[MonthlyBreakdown]
    
    # Economic Analysis
    economic_analysis: Dict[str, Any]
    
    # Budget Analysis (if budget provided)
    budget_analysis: Optional[BudgetAnalysis]
    
    # Optimization Results (if performed)
    optimization: Optional[OptimizationResult]
    
    # Weather Data Summary
    weather_summary: WeatherSummary
    
    # Technical Specifications
    technical_specs: Dict[str, Any]
    
    # Computation Information
    computation_info: Dict[str, Any]

def load_datasets():
    """Load Indian solar component datasets"""
    global modules_df, inverters_df
    
    try:
        print(" Loading modules dataset...")
        modules_df = pd.read_csv("modules_india_realistic_sample.csv")
        print("Loading inverters dataset...")
        inverters_df = pd.read_csv("inverters_india_realistic_sample.csv")
        print("Datasets loaded successfully")
        print(f"Loaded {len(modules_df)} modules and {len(inverters_df)} inverters")
    except FileNotFoundError as e:
        print(f"Dataset files not found: {e}")
        print("Please ensure CSV files are in the working directory.")
        raise HTTPException(status_code=500, detail=f"Required dataset files not found: {e}")
    except Exception as e:
        print(f"Error loading datasets: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading datasets: {e}")

def fetch_nasa_power_data(latitude: float, longitude: float, year: int):
    """Fetch weather data from NASA POWER API"""
    url = (
        f"https://power.larc.nasa.gov/api/temporal/hourly/point?"
        f"parameters=ALLSKY_SFC_SW_DWN,T2M,RH2M,WS10M&community=RE"
        f"&longitude={longitude}&latitude={latitude}"
        f"&start={year}0101&end={year}1231&format=JSON"
    )
    
    try:
        print(f"Fetching NASA POWER data for {latitude:.3f}°N, {longitude:.3f}°E")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data_json = response.json()
        
        # Process the data
        records = []
        parameters = data_json['properties']['parameter']
        
        for date_key in parameters['ALLSKY_SFC_SW_DWN'].keys():
            if len(date_key) == 10:  # YYYYMMDDHH format
                try:
                    datetime_obj = pd.to_datetime(date_key, format='%Y%m%d%H')
                    record = {
                        'datetime': datetime_obj,
                        'ghi': parameters['ALLSKY_SFC_SW_DWN'][date_key],
                        'temp_air': parameters['T2M'][date_key],
                        'relative_humidity': parameters['RH2M'][date_key],
                        'wind_speed': parameters['WS10M'][date_key]
                    }
                    records.append(record)
                except:
                    continue
        
        df = pd.DataFrame(records)
        df = df.dropna()
        df.set_index('datetime', inplace=True)
        df = df.sort_index()
        
        print(f"Loaded {len(df)} hourly weather data points")
        return df
        
    except Exception as e:
        print(f"Error fetching NASA data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")

def calculate_solar_irradiance(df: pd.DataFrame, site: Location):
    """Calculate DNI and DHI from GHI using DISC model"""
    print(f"Calculating solar irradiance for {len(df)} data points...")
    
    # Convert GHI from kWh/m²/day to W/m² (NASA provides in kWh/m²/day, need W/m²)
    df['ghi'] = df['ghi'] * 1000 / 24  # Convert to average W/m² for the hour
    
    print("Computing solar position...")
    # Get solar position for zenith angle calculation
    solar_position = site.get_solarposition(df.index)
    zenith_angle = solar_position['zenith']
    
    print("Running DISC model...")
    # Use DISC model to estimate DNI from GHI
    disc_dni = pvlib.irradiance.disc(df['ghi'], zenith_angle, df.index)
    df['dni'] = disc_dni['dni']
    df['dhi'] = df['ghi'] - df['dni'] * np.cos(np.radians(zenith_angle))
    df['dhi'] = df['dhi'].clip(lower=0)  # Ensure DHI is not negative
    
    print("Solar irradiance calculation complete")
    return df

def get_technology_specific_params(technology: str, pdc0_w: float):
    """Get technology-specific parameters for different PV technologies"""
    
    # Technology-specific parameters based on research
    tech_params = {
        'HJT': {  # Heterojunction - Best temperature coefficient
            'gamma_pdc': -0.0025,  # %/°C
            'alpha_sc': 0.0004,    # A/°C  
            'beta_oc': -0.0025,    # V/°C
            'cells_in_series': 120
        },
        'TOPCon': {  # Tunnel Oxide Passivated Contact
            'gamma_pdc': -0.0035,  # %/°C
            'alpha_sc': 0.0005,    # A/°C
            'beta_oc': -0.0030,    # V/°C  
            'cells_in_series': 108
        },
        'Bifacial': {  # Bifacial modules
            'gamma_pdc': -0.0038,  # %/°C
            'alpha_sc': 0.0006,    # A/°C
            'beta_oc': -0.0032,    # V/°C
            'cells_in_series': 120
        },
        'PERC': {  # Passivated Emitter Rear Cell
            'gamma_pdc': -0.0045,  # %/°C (Standard)
            'alpha_sc': 0.0005,    # A/°C
            'beta_oc': -0.0035,    # V/°C
            'cells_in_series': 72
        },
        'Monocrystalline PERC': {  # Default fallback
            'gamma_pdc': -0.0045,  # %/°C
            'alpha_sc': 0.0005,    # A/°C  
            'beta_oc': -0.0035,    # V/°C
            'cells_in_series': 72
        }
    }
    
    return tech_params.get(technology, tech_params['Monocrystalline PERC'])

def select_components_by_budget(system_capacity_kw: float, budget_inr: Optional[float] = None, 
                               prefer_brand: Optional[str] = None, num_panels: Optional[int] = None):
    """Enhanced component selection with budget constraints, brand preferences, and specific panel count"""
    global modules_df, inverters_df
    
    target_power_w = system_capacity_kw * 1000
    
    # Use standard cost per kW for Indian market (INR/kW installed)
    cost_per_kw = 45000  # Standard mid-range pricing
    estimated_cost = (system_capacity_kw * cost_per_kw)
    
    # Budget constraint check
    adjusted_capacity = system_capacity_kw
    if budget_inr and estimated_cost > budget_inr:
        print(f"Budget constraint: ₹{budget_inr:,} < Estimated ₹{estimated_cost:,}")
        max_affordable_kw = budget_inr / cost_per_kw
        adjusted_capacity = min(system_capacity_kw, max_affordable_kw)
        target_power_w = adjusted_capacity * 1000
        print(f"📉 Adjusted system size to {adjusted_capacity:.1f} kW to fit budget")
    
    # Filter modules by brand preference
    available_modules = modules_df.copy()
    if prefer_brand:
        brand_modules = modules_df[modules_df['manufacturer'].str.contains(prefer_brand, case=False, na=False)]
        if not brand_modules.empty:
            available_modules = brand_modules
            print(f"Filtering for preferred brand: {prefer_brand}")
        else:
            print(f"Brand '{prefer_brand}' not found, using all available modules")
    
    # Select best efficiency module from available options
    selected_module = available_modules.loc[available_modules['eff_percent'].idxmax()]
    print("🌟 Selecting highest efficiency module from available options")
    
    # Calculate modules needed - use specific panel count if provided
    if num_panels is not None:
        modules_needed = num_panels
        actual_system_power = modules_needed * selected_module['pdc0_W']
        actual_capacity_kw = actual_system_power / 1000
        print(f"Using specified panel count: {num_panels} panels")
        print(f"Actual system capacity adjusted to: {actual_capacity_kw:.2f} kW")
    else:
        modules_needed = int(np.ceil(target_power_w / selected_module['pdc0_W']))
        actual_system_power = modules_needed * selected_module['pdc0_W']
        actual_capacity_kw = actual_system_power / 1000
    
    # Select inverter based on tier and system requirements
    min_inverter_power = actual_system_power * 1.1  # 110% safety margin
    suitable_inverters = inverters_df[inverters_df['pdc_max_W'] >= min_inverter_power]
    
    if suitable_inverters.empty:
        # If no suitable inverter, select the largest available
        selected_inverter = inverters_df.loc[inverters_df['pdc_max_W'].idxmax()]
        print("No perfectly sized inverter found, selecting largest available")
    else:
        # Select highest efficiency inverter
        selected_inverter = suitable_inverters.loc[suitable_inverters['eff_percent'].idxmax()]
    
    # Calculate actual system cost with detailed breakdown
    actual_system_cost = actual_capacity_kw * cost_per_kw
    
    cost_breakdown = {
        "modules_cost_inr": actual_system_cost * 0.40,  # 40% modules
        "inverter_cost_inr": actual_system_cost * 0.20,  # 20% inverter
        "mounting_bos_inr": actual_system_cost * 0.25,   # 25% mounting & BoS
        "installation_inr": actual_system_cost * 0.15    # 15% installation
    }
    
    return (selected_module, selected_inverter, modules_needed, 
            actual_system_power, actual_system_cost, cost_breakdown, actual_capacity_kw)

def create_pv_parameters(selected_module, selected_inverter):
    """Create pvlib-compatible parameters"""
    tech_params = get_technology_specific_params(
        selected_module['technology'], 
        float(selected_module['pdc0_W'])
    )
    
    module_params = {
        'pdc0': float(selected_module['pdc0_W']),
        'v_oc': float(selected_module['Voc_V']),
        'i_sc': float(selected_module['Isc_A']),
        'v_mp': float(selected_module['Vmp_V']),
        'i_mp': float(selected_module['Imp_A']),
        'gamma_pdc': tech_params['gamma_pdc'],
        'alpha_sc': tech_params['alpha_sc'],
        'beta_oc': tech_params['beta_oc'],
        'cells_in_series': tech_params['cells_in_series'],
        'temp_ref': 25,
        'irrad_ref': 1000,
        'technology': selected_module['technology'],
        'bifacial': 'Bifacial' in selected_module['technology']
    }
    
    inverter_params = {
        'pdc0': float(selected_inverter['pdc_max_W']),
        'pac0': float(selected_inverter['pac0_W']),
        'eta_inv_nom': float(selected_inverter['eff_percent']) / 100.0,
        'eta_inv_ref': float(selected_inverter['eff_percent']) / 100.0,
        'pnt': 0.01,
        'psco': 20,
        'pso': float(selected_inverter['pac0_W']) * 0.005,
        'c0': -0.000002,
        'c1': -0.000091,
        'c2': -0.057,
    }
    
    temp_params = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    
    return module_params, inverter_params, temp_params

def find_optimal_orientation(site, weather_df, module_params, inverter_params, temp_params, modules_needed):
    """Find optimal tilt and azimuth for maximum energy generation"""
    print("Finding optimal orientation...")
    
    best_energy = 0
    best_tilt = 0
    best_azimuth = 180
    
    # Test different combinations (more comprehensive for better optimization)
    tilt_range = range(5, 41, 5)  # 5° to 40° in 5° steps
    azimuth_range = range(120, 241, 10)  # 120° to 240° in 10° steps (south-facing emphasis for India)
    
    total_combinations = len(tilt_range) * len(azimuth_range)
    tested = 0
    
    for tilt in tilt_range:
        for azimuth in azimuth_range:
            try:
                energy = run_pv_simulation(site, weather_df, tilt, azimuth, 
                                         module_params, inverter_params, temp_params, modules_needed)
                if energy > best_energy:
                    best_energy = energy
                    best_tilt = tilt
                    best_azimuth = azimuth
                tested += 1
            except:
                continue
    
    # Calculate baseline energy (using latitude as tilt, 180° azimuth)
    baseline_tilt = min(40, max(5, abs(site.latitude)))
    baseline_energy = run_pv_simulation(site, weather_df, baseline_tilt, 180, 
                                      module_params, inverter_params, temp_params, modules_needed)
    
    improvement = ((best_energy - baseline_energy) / baseline_energy) * 100 if baseline_energy > 0 else 0
    
    optimization_summary = {
        "baseline_tilt": baseline_tilt,
        "baseline_azimuth": 180,
        "baseline_energy_kwh": round(baseline_energy, 1),
        "tested_tilt_range": f"{min(tilt_range)}° to {max(tilt_range)}°",
        "tested_azimuth_range": f"{min(azimuth_range)}° to {max(azimuth_range)}°",
        "optimization_method": "Grid search with 5° tilt and 10° azimuth resolution"
    }
    
    return best_tilt, best_azimuth, best_energy, improvement, tested, optimization_summary

def run_pv_simulation(site, weather_df, tilt, azimuth, module_params, inverter_params, temp_params, modules_needed):
    """Run PV system simulation and return annual energy"""
    try:
        # Create PV system
        pv_system = PVSystem(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            module_parameters=module_params,
            inverter_parameters=inverter_params,
            temperature_model_parameters=temp_params,
            modules_per_string=modules_needed,
            strings_per_inverter=1
        )
        
        # Create model chain
        mc = ModelChain(pv_system, site, aoi_model='physical', spectral_model='no_loss')
        
        # Run simulation
        mc.run_model(weather_df)
        
        # Calculate annual AC energy in kWh
        annual_energy = mc.results.ac.sum() / 1000  # Convert W to kWh
        
        return annual_energy
        
    except Exception as e:
        print(f"Simulation error for tilt={tilt}°, azimuth={azimuth}°: {e}")
        return 0



@app.get("/", response_class=JSONResponse)
async def root():
    """API root endpoint with comprehensive information"""
    return JSONResponse({
        "api_name": "Indian PV System Energy Calculator v2.0",
        "version": "2.0.0",
        "description": "Enhanced solar energy analysis with budget constraints and brand preferences",
        "features": [
            "Budget-constrained component selection",
            "Brand preference filtering",
            "Comprehensive JSON output",
            "Optimal orientation finding",
            "Real NASA POWER weather data",
            "Indian component database",
            "Economic analysis with payback period",
            "Technology-specific parameters"
        ],
        "endpoints": {
            "/calculate": "POST - Main calculation endpoint",
            "/components/modules": "GET - Available solar modules",
            "/components/inverters": "GET - Available inverters",
            "/docs": "GET - Interactive API documentation"
        },

        "supported_brands": ["Adani", "Waaree", "Vikram", "Jinko", "Longi", "Tata", "Others"],
        "example_request": {
            "latitude": 10.936,
            "longitude": 76.739,
            "system_capacity_kw": 5.0,
            "budget_inr": 300000,
            "prefer_brand": "Adani",
            "max_payback_years": 8.0
        }
    })

@app.get("/components/modules", response_class=JSONResponse)
async def get_available_modules():
    """Get all available solar modules with comprehensive details"""
    if modules_df is None:
        raise HTTPException(status_code=500, detail="Modules dataset not loaded")
    
    modules_list = []
    for _, module in modules_df.iterrows():
        modules_list.append({
            "model": module['model'],
            "manufacturer": module['manufacturer'],
            "technology": module['technology'],
            "power_w": float(module['pdc0_W']),
            "efficiency_percent": float(module['eff_percent']),
            "voltage_voc": float(module['Voc_V']),
            "current_isc": float(module['Isc_A']),
            "voltage_vmp": float(module['Vmp_V']),
            "current_imp": float(module['Imp_A']),
            "specifications": {
                "dimensions": "Standard solar panel dimensions",
                "weight_kg": "Estimated 20-25 kg",
                "warranty_years": 25,
                "degradation_rate_per_year": 0.5
            }
        })
    
    return JSONResponse({
        "total_modules": len(modules_list),
        "manufacturers": sorted(modules_df['manufacturer'].unique().tolist()),
        "technologies": sorted(modules_df['technology'].unique().tolist()),
        "efficiency_range": {
            "min_percent": float(modules_df['eff_percent'].min()),
            "max_percent": float(modules_df['eff_percent'].max()),
            "average_percent": float(modules_df['eff_percent'].mean())
        },
        "power_range": {
            "min_w": float(modules_df['pdc0_W'].min()),
            "max_w": float(modules_df['pdc0_W'].max()),
            "average_w": float(modules_df['pdc0_W'].mean())
        },
        "modules": modules_list
    })

@app.get("/components/inverters", response_class=JSONResponse)
async def get_available_inverters():
    """Get all available inverters with comprehensive details"""
    if inverters_df is None:
        raise HTTPException(status_code=500, detail="Inverters dataset not loaded")
    
    inverters_list = []
    for _, inverter in inverters_df.iterrows():
        inverters_list.append({
            "model": inverter['model'],
            "manufacturer": inverter['manufacturer'],
            "ac_power_w": float(inverter['pac0_W']),
            "dc_power_w": float(inverter['pdc_max_W']),
            "efficiency_percent": float(inverter['eff_percent']),
            "specifications": {
                "type": "String inverter",
                "mppt_trackers": "Multiple MPPT",
                "warranty_years": 10,
                "protection_rating": "IP65"
            }
        })
    
    return JSONResponse({
        "total_inverters": len(inverters_list),
        "manufacturers": sorted(inverters_df['manufacturer'].unique().tolist()),
        "efficiency_range": {
            "min_percent": float(inverters_df['eff_percent'].min()),
            "max_percent": float(inverters_df['eff_percent'].max()),
            "average_percent": float(inverters_df['eff_percent'].mean())
        },
        "power_range": {
            "min_ac_w": float(inverters_df['pac0_W'].min()),
            "max_ac_w": float(inverters_df['pac0_W'].max()),
            "min_dc_w": float(inverters_df['pdc_max_W'].min()),
            "max_dc_w": float(inverters_df['pdc_max_W'].max())
        },
        "inverters": inverters_list
    })

@app.post("/calculate", response_class=JSONResponse)
async def calculate_pv_system(request: PVSystemRequest):
    """
    Main calculation endpoint with budget constraints and comprehensive JSON output
    """
    start_time = time.time()
    calculation_id = f"calc_{int(time.time())}"
    
    try:
        print(f"Starting calculation {calculation_id}")
        
        # 1. Load and validate datasets
        if modules_df is None or inverters_df is None:
            load_datasets()
        
        # 2. Enhanced component selection with budget constraints and panel count
        (selected_module, selected_inverter, modules_needed, actual_system_power, 
         actual_system_cost, cost_breakdown, actual_capacity_kw) = select_components_by_budget(
            request.system_capacity_kw,
            request.budget_inr,
            request.prefer_brand,
            request.num_panels
        )
        
        # 3. Fetch weather data
        weather_df = fetch_nasa_power_data(request.latitude, request.longitude, request.year)
        
        # 4. Create location and calculate solar position
        site = Location(latitude=request.latitude, longitude=request.longitude, 
                       tz='Asia/Kolkata', altitude=100, name=f"Site_{calculation_id}")
        
        # 5. Calculate solar irradiance components
        weather_df = calculate_solar_irradiance(weather_df, site)
        
        # 6. Create PV system parameters
        module_params, inverter_params, temp_params = create_pv_parameters(selected_module, selected_inverter)
        
        # 7. Determine system orientation
        optimization_result = None
        if request.optimize_orientation or (request.tilt is None or request.azimuth is None):
            optimal_tilt, optimal_azimuth, optimal_energy, improvement, tested_combinations, opt_summary = find_optimal_orientation(
                site, weather_df, module_params, inverter_params, temp_params, modules_needed
            )
            system_tilt = optimal_tilt
            system_azimuth = optimal_azimuth
            
            optimization_result = OptimizationResult(
                optimal_tilt=optimal_tilt,
                optimal_azimuth=optimal_azimuth,
                optimal_energy_kwh=round(optimal_energy, 1),
                improvement_percent=round(improvement, 1),
                tested_combinations=tested_combinations,
                optimization_summary=opt_summary
            )
        else:
            system_tilt = request.tilt
            system_azimuth = request.azimuth
        
        # 8. Run final simulation
        print("Running PV simulation...")
        annual_energy = run_pv_simulation(site, weather_df, system_tilt, system_azimuth, 
                                        module_params, inverter_params, temp_params, modules_needed)
        
        # 9. Calculate performance metrics
        capacity_factor = (annual_energy / (actual_capacity_kw * 8760)) * 100 if actual_capacity_kw > 0 else 0
        specific_yield = annual_energy / actual_capacity_kw if actual_capacity_kw > 0 else 0
        
        # Simulate daily energy for statistics
        daily_energy_avg = annual_energy / 365
        daily_energy_stats = {
            "average_kwh": round(daily_energy_avg, 2),
            "maximum_kwh": round(daily_energy_avg * 1.4, 2),  # Peak day estimate
            "minimum_kwh": round(daily_energy_avg * 0.3, 2),  # Cloudy day estimate
            "summer_average_kwh": round(daily_energy_avg * 1.2, 2),
            "winter_average_kwh": round(daily_energy_avg * 0.8, 2)
        }
        
        # 10. Monthly breakdown simulation
        monthly_breakdown = []
        seasonal_factors = [0.8, 0.9, 1.1, 1.2, 1.3, 1.2, 1.1, 1.1, 1.0, 0.9, 0.8, 0.8]  # India seasonal pattern
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        for i, (month, factor) in enumerate(zip(months, seasonal_factors)):
            monthly_energy = (annual_energy / 12) * factor
            monthly_breakdown.append(MonthlyBreakdown(
                month=month,
                month_number=i+1,
                energy_kwh=round(monthly_energy, 1),
                daily_average_kwh=round(monthly_energy / 30, 2),
                peak_day_kwh=round((monthly_energy / 30) * 1.4, 2)
            ))
        
        # 11. Enhanced Economic analysis
        annual_savings = annual_energy * request.electricity_rate_inr
        payback_period = actual_system_cost / annual_savings if annual_savings > 0 else float('inf')
        payback_period = min(payback_period, 50.0)  # Cap at 50 years
        
        # 25-year financial projection
        system_life_years = 25
        degradation_rate = 0.005  # 0.5% per year
        total_lifetime_energy = 0
        total_lifetime_savings = 0
        
        for year in range(1, system_life_years + 1):
            year_energy = annual_energy * ((1 - degradation_rate) ** (year - 1))
            year_savings = year_energy * request.electricity_rate_inr
            total_lifetime_energy += year_energy
            total_lifetime_savings += year_savings
        
        economic_analysis = {
            "annual_energy_first_year_kwh": round(annual_energy, 1),
            "annual_savings_first_year_inr": round(annual_savings, 0),
            "monthly_average_savings_inr": round(annual_savings / 12, 0),
            "electricity_rate_inr_per_kwh": request.electricity_rate_inr,
            "payback_period_years": round(payback_period, 1),
            "system_cost_inr": round(actual_system_cost, 0),
            "cost_per_kwh_generated_inr": round(actual_system_cost / total_lifetime_energy, 2),
            "lifetime_analysis": {
                "system_life_years": system_life_years,
                "total_energy_generated_kwh": round(total_lifetime_energy, 0),
                "total_savings_inr": round(total_lifetime_savings, 0),
                "roi_percent": round(((total_lifetime_savings - actual_system_cost) / actual_system_cost) * 100, 1),
                "annual_degradation_percent": degradation_rate * 100
            },
            "break_even_analysis": {
                "break_even_year": round(payback_period, 1),
                "cumulative_savings_at_break_even_inr": round(payback_period * annual_savings, 0),
                "profit_after_payback_inr": round(total_lifetime_savings - actual_system_cost, 0)
            }
        }
        
        # 12. Budget analysis (if budget provided)
        budget_analysis = None
        if request.budget_inr:
            financing_options = {
                "full_upfront_payment": {
                    "amount_inr": actual_system_cost,
                    "payback_years": payback_period
                },
                "loan_option_5_years": {
                    "loan_amount_inr": actual_system_cost,
                    "interest_rate_percent": 12.0,
                    "monthly_emi_inr": round((actual_system_cost * 0.12 * (1.12**5)) / ((1.12**5) - 1) / 12, 0),
                    "total_payment_inr": round((actual_system_cost * 0.12 * (1.12**5)) / ((1.12**5) - 1) * 5, 0)
                },
                "subsidy_available": {
                    "central_subsidy_percent": 30,
                    "max_subsidy_inr": min(actual_system_cost * 0.3, 78000),  # Rs 78,000 max for residential
                    "net_cost_after_subsidy_inr": actual_system_cost - min(actual_system_cost * 0.3, 78000)
                }
            }
            
            budget_analysis = BudgetAnalysis(
                requested_budget_inr=request.budget_inr,
                actual_system_cost_inr=round(actual_system_cost, 0),
                cost_per_kw_inr=round(actual_system_cost / actual_capacity_kw, 0),
                budget_utilization_percent=round((actual_system_cost / request.budget_inr) * 100, 1),
                preferred_brand=request.prefer_brand,
                budget_remaining_inr=round(max(0, request.budget_inr - actual_system_cost), 0),
                cost_breakdown=cost_breakdown,
                financing_options=financing_options
            )
        
        # 13. Weather summary
        weather_summary = WeatherSummary(
            data_source="NASA POWER",
            total_data_points=len(weather_df),
            average_ghi_kwh_m2_day=round(weather_df['ghi'].mean() * 24 / 1000, 2),
            peak_ghi_w_m2=round(weather_df['ghi'].max(), 0),
            average_temperature_c=round(weather_df['temp_air'].mean(), 1),
            temperature_range={
                "min_c": round(weather_df['temp_air'].min(), 1),
                "max_c": round(weather_df['temp_air'].max(), 1),
                "std_dev_c": round(weather_df['temp_air'].std(), 1)
            },
            seasonal_variation={
                "summer_avg_ghi": round(weather_df['ghi'][weather_df.index.month.isin([4,5,6])].mean(), 1),
                "winter_avg_ghi": round(weather_df['ghi'][weather_df.index.month.isin([12,1,2])].mean(), 1),
                "monsoon_avg_ghi": round(weather_df['ghi'][weather_df.index.month.isin([7,8,9])].mean(), 1)
            }
        )
        
        computation_time = time.time() - start_time
        
        # 14. Prepare comprehensive JSON response
        response = {
            "calculation_id": calculation_id,
            "timestamp": datetime.now().isoformat(),
            "api_version": "2.0.0",
            
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude,
                "timezone": "Asia/Kolkata",
                "name": f"Solar Site {calculation_id}",
                "country": "India",
                "elevation_m": 100
            },
            
            "system_configuration": {
                "requested_capacity_kw": request.system_capacity_kw,
                "actual_capacity_kw": round(actual_capacity_kw, 2),
                "modules_count": modules_needed,
                "specified_panel_count": request.num_panels if request.num_panels else None,
                "tilt_degrees": system_tilt,
                "azimuth_degrees": system_azimuth,
                "module_power_w": int(module_params['pdc0']),
                "inverter_ac_power_w": int(inverter_params['pac0']),
                "inverter_dc_power_w": int(inverter_params['pdc0']),
                "system_dc_ac_ratio": round(actual_system_power / float(selected_inverter['pac0_W']), 2),
                "mounting_type": "Fixed tilt roof mount",
                "system_losses_percent": 15
            },
            
            "selected_module": ModuleInfo(
                model=selected_module['model'],
                manufacturer=selected_module['manufacturer'],
                technology=selected_module['technology'],
                power_w=float(selected_module['pdc0_W']),
                efficiency_percent=float(selected_module['eff_percent']),
                voltage_voc=float(selected_module['Voc_V']),
                current_isc=float(selected_module['Isc_A']),
                voltage_vmp=float(selected_module['Vmp_V']),
                current_imp=float(selected_module['Imp_A'])
            ).dict(),
            
            "selected_inverter": InverterInfo(
                model=selected_inverter['model'],
                manufacturer=selected_inverter['manufacturer'],
                ac_power_w=float(selected_inverter['pac0_W']),
                dc_power_w=float(selected_inverter['pdc_max_W']),
                efficiency_percent=float(selected_inverter['eff_percent'])
            ).dict(),
            
            "performance_results": {
                "annual_energy_kwh": round(annual_energy, 1),
                "capacity_factor_percent": round(capacity_factor, 1),
                "specific_yield_kwh_per_kwp": round(specific_yield, 1),
                "performance_ratio": round(capacity_factor / 19.2, 2),  # Normalized to good Indian conditions
                "energy_yield_analysis": {
                    "first_year_kwh": round(annual_energy, 1),
                    "year_10_kwh": round(annual_energy * (1 - 0.005)**9, 1),
                    "year_25_kwh": round(annual_energy * (1 - 0.005)**24, 1),
                    "lifetime_total_kwh": round(total_lifetime_energy, 0)
                },
                "daily_energy_stats": daily_energy_stats,
                "co2_offset_analysis": {
                    "annual_co2_avoided_kg": round(annual_energy * 0.82, 0),  # India grid emission factor
                    "lifetime_co2_avoided_tonnes": round(total_lifetime_energy * 0.82 / 1000, 1),
                    "equivalent_trees_planted": round(total_lifetime_energy * 0.82 / 22, 0)  # 22kg CO2/tree/year
                }
            },
            
            "monthly_breakdown": [mb.dict() for mb in monthly_breakdown],
            
            "economic_analysis": economic_analysis,
            
            "budget_analysis": budget_analysis.dict() if budget_analysis else None,
            
            "optimization": optimization_result.dict() if optimization_result else None,
            
            "weather_summary": weather_summary.dict(),
            
            "technical_specs": {
                "module_technology": selected_module['technology'],
                "temperature_coefficient_percent_per_c": module_params['gamma_pdc'] * 100,
                "reference_conditions": {
                    "irradiance_w_m2": 1000,
                    "temperature_c": 25,
                    "air_mass": 1.5
                },
                "system_topology": {
                    "modules_per_string": modules_needed,
                    "strings_per_inverter": 1,
                    "total_strings": 1,
                    "total_modules": modules_needed
                },
                "electrical_characteristics": {
                    "system_voc_v": modules_needed * float(selected_module['Voc_V']),
                    "system_isc_a": float(selected_module['Isc_A']),
                    "system_vmp_v": modules_needed * float(selected_module['Vmp_V']),
                    "system_imp_a": float(selected_module['Imp_A'])
                }
            },
            
            "computation_info": {
                "calculation_time_seconds": round(computation_time, 2),
                "weather_data_points": len(weather_df),
                "simulation_engine": "pvlib-python",
                "irradiance_model": "DISC",
                "temperature_model": "Sandia Array Performance Model",
                "calculation_timestamp": datetime.now().isoformat(),
                "api_endpoint": "/calculate",
                "request_parameters": {
                    "budget_constrained": request.budget_inr is not None,
                    "brand_preference": request.prefer_brand,
                    "optimization_performed": request.optimize_orientation
                }
            }
        }
        
        print(f"Calculation {calculation_id} completed successfully in {computation_time:.1f} seconds")
        return JSONResponse(response)
        
    except Exception as e:
        error_response = {
            "calculation_id": calculation_id,
            "timestamp": datetime.now().isoformat(),
            "error": True,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "error_details": {
                "endpoint": "/calculate",
                "computation_time_seconds": round(time.time() - start_time, 2),
                "request_parameters": request.dict()
            }
        }
        print(f"Error in calculation {calculation_id}: {e}")
        raise HTTPException(status_code=500, detail=error_response)



if __name__ == "__main__":
    import uvicorn
    print("Starting Enhanced Indian PV System Energy Calculator v2.0...")
    print("Features: Budget constraints, Brand preferences, Comprehensive JSON output")
    print("Access API at: http://localhost:8000")
    print("Interactive docs at: http://localhost:8000/docs")
    uvicorn.run("main_v2:app", host="0.0.0.0", port=8001)