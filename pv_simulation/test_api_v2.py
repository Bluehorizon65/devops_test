#!/usr/bin/env python3
"""
Test client for Enhanced Indian PV System Energy Calculator v2.0 API
Tests budget constraints, brand preferences, and comprehensive JSON output
"""

import requests
import json
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8001"

def test_api_connection():
    """Test if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Connection error: {e}")
        return False

def calculate_pv_system_v2(
    latitude: float,
    longitude: float,
    system_capacity_kw: float,
    year: int = 2024,
    tilt: float = None,
    azimuth: float = None,
    optimize_orientation: bool = True,
    electricity_rate_inr: float = 7.5,
    # NEW BUDGET AND PREFERENCE OPTIONS
    budget_inr: float = None,
    prefer_brand: str = None,
    max_payback_years: float = None,
    # NEW PANEL COUNT OPTION
    num_panels: int = None
) -> Dict[Any, Any]:
    """
    Calculate PV system performance with budget constraints and brand preferences
    """
    
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "system_capacity_kw": system_capacity_kw,
        "year": year,
        "optimize_orientation": optimize_orientation,
        "electricity_rate_inr": electricity_rate_inr
    }
    
    # Add optional parameters
    if tilt is not None:
        payload["tilt"] = tilt
    if azimuth is not None:
        payload["azimuth"] = azimuth
    if budget_inr is not None:
        payload["budget_inr"] = budget_inr
    if prefer_brand is not None:
        payload["prefer_brand"] = prefer_brand
    if max_payback_years is not None:
        payload["max_payback_years"] = max_payback_years
    if num_panels is not None:
        payload["num_panels"] = num_panels
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/calculate",
            json=payload,
            timeout=300
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error in calculation: {e}")
        return None

def print_comprehensive_results(results: Dict[Any, Any]):
    """Print comprehensive calculation results in a formatted way"""
    if not results:
        print("❌ No results to display")
        return
    
    print("\n" + "="*80)
    print("🇮🇳 ENHANCED INDIAN PV SYSTEM CALCULATION RESULTS v2.0")
    print("="*80)
    
    # Calculation Info
    print(f"🆔 Calculation ID: {results['calculation_id']}")
    print(f"⏰ Timestamp: {results['timestamp']}")
    print(f"🔧 API Version: {results['api_version']}")
    
    # Location Info
    location = results['location']
    print(f"\n📍 LOCATION DETAILS:")
    print(f"   Coordinates: {location['latitude']:.3f}°N, {location['longitude']:.3f}°E")
    print(f"   Country: {location['country']}")
    print(f"   Timezone: {location['timezone']}")
    
    # System Configuration
    config = results['system_configuration']
    print(f"\n⚡ SYSTEM CONFIGURATION:")
    print(f"   Requested Capacity: {config['requested_capacity_kw']} kW")
    print(f"   Actual Capacity: {config['actual_capacity_kw']} kW")
    print(f"   Modules Count: {config['modules_count']}")
    if config.get('specified_panel_count'):
        print(f"   Specified Panel Count: {config['specified_panel_count']} (user-defined)")
    print(f"   Orientation: {config['tilt_degrees']}° tilt, {config['azimuth_degrees']}° azimuth")
    print(f"   DC/AC Ratio: {config['system_dc_ac_ratio']}")
    
    # Selected Components
    module = results['selected_module']
    inverter = results['selected_inverter']
    print(f"\n🔆 SELECTED MODULE:")
    print(f"   Model: {module['manufacturer']} {module['model']}")
    print(f"   Technology: {module['technology']}")
    print(f"   Power: {module['power_w']}W")
    print(f"   Efficiency: {module['efficiency_percent']}%")
    
    print(f"\n🔌 SELECTED INVERTER:")
    print(f"   Model: {inverter['manufacturer']} {inverter['model']}")
    print(f"   AC Power: {inverter['ac_power_w']}W")
    print(f"   Efficiency: {inverter['efficiency_percent']}%")
    
    # Performance Results
    performance = results['performance_results']
    daily_stats = performance['daily_energy_stats']
    print(f"\n📊 PERFORMANCE RESULTS:")
    print(f"   Annual Energy: {performance['annual_energy_kwh']:,.1f} kWh")
    print(f"   Capacity Factor: {performance['capacity_factor_percent']:.1f}%")
    print(f"   Specific Yield: {performance['specific_yield_kwh_per_kwp']:.1f} kWh/kWp")
    print(f"   Daily Average: {daily_stats['average_kwh']:.2f} kWh")
    print(f"   Daily Maximum: {daily_stats['maximum_kwh']:.2f} kWh")
    
    # CO2 Impact
    co2_data = performance['co2_offset_analysis']
    print(f"   Annual CO2 Avoided: {co2_data['annual_co2_avoided_kg']:,.0f} kg")
    print(f"   Lifetime CO2 Avoided: {co2_data['lifetime_co2_avoided_tonnes']:,.1f} tonnes")
    
    # Economic Analysis
    economic = results['economic_analysis']
    print(f"\n💰 ECONOMIC ANALYSIS:")
    print(f"   Annual Savings: ₹{economic['annual_savings_first_year_inr']:,.0f}")
    print(f"   Monthly Average: ₹{economic['monthly_average_savings_inr']:,.0f}")
    
    # Lifetime Analysis
    lifetime = economic['lifetime_analysis']
    print(f"   25-Year Total Energy: {lifetime['total_energy_generated_kwh']:,.0f} kWh")
    print(f"   25-Year Total Savings: ₹{lifetime['total_savings_inr']:,.0f}")
    print(f"   Return on Investment: {lifetime['roi_percent']:.1f}%")
    
    # Budget Analysis (if provided)
    if results.get('budget_analysis'):
        budget = results['budget_analysis']
        print(f"\n💳 BUDGET ANALYSIS:")
        print(f"   Requested Budget: ₹{budget['requested_budget_inr']:,.0f}")
        print(f"   Actual Cost: ₹{budget['actual_system_cost_inr']:,.0f}")
        print(f"   Budget Utilization: {budget['budget_utilization_percent']:.1f}%")
        print(f"   Budget Remaining: ₹{budget['budget_remaining_inr']:,.0f}")
        print(f"   Cost per kW: ₹{budget['cost_per_kw_inr']:,.0f}/kW")
        
        if budget['preferred_brand']:
            print(f"   Preferred Brand: {budget['preferred_brand']}")
        
        # Cost Breakdown
        breakdown = budget['cost_breakdown']
        print(f"   Cost Breakdown:")
        print(f"     Modules: ₹{breakdown['modules_cost_inr']:,.0f} (40%)")
        print(f"     Inverter: ₹{breakdown['inverter_cost_inr']:,.0f} (20%)")
        print(f"     Mounting/BoS: ₹{breakdown['mounting_bos_inr']:,.0f} (25%)")
        print(f"     Installation: ₹{breakdown['installation_inr']:,.0f} (15%)")
        
        # Financing Options
        financing = budget['financing_options']
        if 'subsidy_available' in financing:
            subsidy = financing['subsidy_available']
            print(f"   Government Subsidy Available:")
            print(f"     Max Subsidy: ₹{subsidy['max_subsidy_inr']:,.0f} ({subsidy['central_subsidy_percent']}%)")
            print(f"     Net Cost After Subsidy: ₹{subsidy['net_cost_after_subsidy_inr']:,.0f}")
    
    # Optimization Results (if performed)
    if results.get('optimization'):
        opt = results['optimization']
        print(f"\n🎯 OPTIMIZATION RESULTS:")
        print(f"   Optimal Tilt: {opt['optimal_tilt']:.1f}°")
        print(f"   Optimal Azimuth: {opt['optimal_azimuth']:.1f}°")
        print(f"   Optimal Energy: {opt['optimal_energy_kwh']:,.1f} kWh")
        print(f"   Energy Improvement: +{opt['improvement_percent']:.1f}%")
        print(f"   Tested Combinations: {opt['tested_combinations']}")
        
        opt_summary = opt['optimization_summary']
        print(f"   Baseline: {opt_summary['baseline_tilt']}° tilt, {opt_summary['baseline_azimuth']}° azimuth")
        print(f"   Baseline Energy: {opt_summary['baseline_energy_kwh']:,.1f} kWh")
    
    # Weather Summary
    weather = results['weather_summary']
    print(f"\n🌤️ WEATHER DATA SUMMARY:")
    print(f"   Data Source: {weather['data_source']}")
    print(f"   Total Data Points: {weather['total_data_points']:,}")
    print(f"   Average GHI: {weather['average_ghi_kwh_m2_day']:.2f} kWh/m²/day")
    print(f"   Peak GHI: {weather['peak_ghi_w_m2']:,.0f} W/m²")
    print(f"   Average Temperature: {weather['average_temperature_c']:.1f}°C")
    print(f"   Temperature Range: {weather['temperature_range']['min_c']:.1f}°C to {weather['temperature_range']['max_c']:.1f}°C")
    
    # Seasonal Variation
    seasonal = weather['seasonal_variation']
    print(f"   Summer Avg GHI: {seasonal['summer_avg_ghi']:.1f} W/m²")
    print(f"   Winter Avg GHI: {seasonal['winter_avg_ghi']:.1f} W/m²")
    print(f"   Monsoon Avg GHI: {seasonal['monsoon_avg_ghi']:.1f} W/m²")
    
    # Monthly Breakdown (all 12 months)
    print(f"\n📅 MONTHLY BREAKDOWN:")
    for month_data in results['monthly_breakdown']:
        print(f"      {month_data['month']:>9}: {month_data['energy_kwh']:>8.1f} kWh")
    
    # Technical Specifications
    tech = results['technical_specs']
    print(f"\n🔧 TECHNICAL SPECIFICATIONS:")
    print(f"   Module Technology: {tech['module_technology']}")
    print(f"   Temperature Coefficient: {tech['temperature_coefficient_percent_per_c']:.3f}%/°C")
    print(f"   System Topology: {tech['system_topology']['total_modules']} modules in {tech['system_topology']['total_strings']} string(s)")
    
    electrical = tech['electrical_characteristics']
    print(f"   System Voc: {electrical['system_voc_v']:.1f}V")
    print(f"   System Vmp: {electrical['system_vmp_v']:.1f}V")
    print(f"   System Current: {electrical['system_imp_a']:.1f}A")
    
    # Computation Time and Data Points (more prominent)
    comp_info = results['computation_info']
    print(f"\n⏱️ Computation Time: {comp_info['calculation_time_seconds']:.1f} seconds")
    print(f"📊 Weather Data Points: {comp_info['weather_data_points']:,}")
    
    print("="*80)

def main():
    """Main test function with enhanced features"""
    print("🧪 Testing Enhanced Indian PV System Energy Calculator v2.0 API")
    print("💰 Features: Budget constraints, Brand preferences, Comprehensive JSON output")
    print("-" * 70)
    
    print("🔍 Checking API connection...")
    if not test_api_connection():
        print("❌ API is not running. Please start the server first:")
        print("   python main_v2.py")
        return
    
    print("✅ API v2.0 is running")
    
    # Enhanced test cases with budget and brand preferences
    test_cases = [
        {
            "name": "🏠 Budget-Conscious Homeowner - Adani Preference",
            "latitude": 10.936,
            "longitude": 76.739,
            "system_capacity_kw": 5.0,
            "budget_inr": 200000,  # 2 Lakh budget
            "prefer_brand": "Adani",
            "max_payback_years": 10.0,
            "optimize_orientation": True
        },
        {
            "name": "🏭 Mid-Range Commercial - Waaree Preference", 
            "latitude": 19.0760,
            "longitude": 72.8777,
            "system_capacity_kw": 10.0,
            "budget_inr": 500000,  # 5 Lakh budget
            "prefer_brand": "Waaree",
            "max_payback_years": 8.0,
            "optimize_orientation": True
        },
        {
            "name": "🌟 Premium Installation - Jinko Preference",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "system_capacity_kw": 7.5,
            "budget_inr": 600000,  # 6 Lakh budget
            "prefer_brand": "Jinko",
            "max_payback_years": 7.0,
            "optimize_orientation": True
        },
        {
            "name": "🔥 No Budget Limit - Best Performance",
            "latitude": 26.9124,
            "longitude": 75.7873,  # Jaipur - Hot climate
            "system_capacity_kw": 15.0,
            "optimize_orientation": True
        },
        {
            "name": "🌊 Coastal Installation - Vikram Solar",
            "latitude": 15.2993,
            "longitude": 74.1240,  # Goa
            "system_capacity_kw": 8.0,
            "budget_inr": 400000,
            "prefer_brand": "Vikram",
            "optimize_orientation": True
        },
        {
            "name": "🔢 Specific Panel Count - 20 Panels",
            "latitude": 28.7041,
            "longitude": 77.1025,  # Delhi
            "system_capacity_kw": 5.0,  # This will be overridden by num_panels
            "num_panels": 20,  # NEW PARAMETER - specify exact number of panels
            "prefer_brand": "Adani",
            "optimize_orientation": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 TEST CASE {i}: {test_case['name']}")
        print("-" * 50)
        
        # Remove name from test_case for API call
        api_params = {k: v for k, v in test_case.items() if k != 'name'}
        
        results = calculate_pv_system_v2(**api_params)
        
        if results:
            print_comprehensive_results(results)
            

            
            # Add insights based on test case
            if test_case.get('budget_inr'):
                budget_used = results.get('budget_analysis', {}).get('budget_utilization_percent', 0)
                if budget_used > 100:
                    print("🚨 INSIGHT: System cost exceeds budget - consider smaller system")
                elif budget_used < 80:
                    print("💡 INSIGHT: Budget has room for larger system")
                else:
                    print("✅ INSIGHT: System cost well-matched to budget")
            
            if test_case.get('prefer_brand'):
                selected_module = results.get('selected_module', {})
                if test_case['prefer_brand'].lower() in selected_module.get('manufacturer', '').lower():
                    print(f"✅ INSIGHT: Successfully matched preferred brand {test_case['prefer_brand']}")
                else:
                    print(f"⚠️ INSIGHT: Preferred brand {test_case['prefer_brand']} not available, selected best alternative")
            
        else:
            print(f"❌ Test case {i} failed")
        
        print("\n" + "="*80)



def demonstrate_json_output_for_frontend():
    """Demonstrate that API returns pure JSON format suitable for frontend"""
    print("\n🌐 JSON OUTPUT FORMAT DEMONSTRATION FOR FRONTEND:")
    print("-" * 60)
    
    # Simple test case with num_panels
    payload = {
        "latitude": 28.7041,
        "longitude": 77.1025,
        "system_capacity_kw": 5.0,
        "num_panels": 15,  # Using num_panels parameter
        "prefer_brand": "Adani",
        "optimize_orientation": False
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/calculate", json=payload, timeout=120)
        
        if response.status_code == 200:
            # Get the raw JSON response
            json_result = response.json()
            
            print("✅ API Response Format: Pure JSON Dictionary")
            print(f"📊 Response Type: {type(json_result)}")
            print(f"🗂️ Main Keys Available for Frontend:")
            for key in json_result.keys():
                print(f"   • {key}")
            
            print(f"\n🔢 Panel Count Verification:")
            config = json_result.get('system_configuration', {})
            print(f"   Requested Panels: {payload['num_panels']}")
            print(f"   Actual Modules Count: {config.get('modules_count')}")
            print(f"   Specified Panel Count: {config.get('specified_panel_count')}")
            print(f"   ✅ Match: {config.get('modules_count') == payload['num_panels']}")
            
            print(f"\n📱 Frontend Usage Example:")
            print("   // JavaScript/React example")
            print("   const result = await fetch('/api/calculate', {")
            print("     method: 'POST',")
            print("     headers: { 'Content-Type': 'application/json' },")
            print(f"     body: JSON.stringify({json.dumps(payload, indent=6)})")
            print("   }).then(res => res.json());")
            print()
            print("   // Access key data")
            print(f"   console.log('Annual Energy:', result.performance_results.annual_energy_kwh);")
            print(f"   console.log('Monthly Data:', result.monthly_breakdown);")
            print(f"   console.log('Panel Count:', result.system_configuration.modules_count);")
            
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_api_endpoints():
    """Test additional API endpoints"""
    print("\n🔍 Testing Additional API Endpoints:")
    print("-" * 40)
    
    # Test modules endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/components/modules")
        if response.status_code == 200:
            modules_data = response.json()
            print(f"✅ Modules endpoint: {modules_data['total_modules']} modules available")
            print(f"   Manufacturers: {', '.join(modules_data['manufacturers'][:5])}...")
            print(f"   Efficiency range: {modules_data['efficiency_range']['min_percent']:.1f}% - {modules_data['efficiency_range']['max_percent']:.1f}%")
        else:
            print("❌ Modules endpoint failed")
    except Exception as e:
        print(f"❌ Modules endpoint error: {e}")
    
    # Test inverters endpoint  
    try:
        response = requests.get(f"{API_BASE_URL}/components/inverters")
        if response.status_code == 200:
            inverters_data = response.json()
            print(f"✅ Inverters endpoint: {inverters_data['total_inverters']} inverters available")
            print(f"   Manufacturers: {', '.join(inverters_data['manufacturers'][:5])}...")
            print(f"   Efficiency range: {inverters_data['efficiency_range']['min_percent']:.1f}% - {inverters_data['efficiency_range']['max_percent']:.1f}%")
        else:
            print("❌ Inverters endpoint failed")
    except Exception as e:
        print(f"❌ Inverters endpoint error: {e}")

if __name__ == "__main__":
    main()
    demonstrate_json_output_for_frontend()
    test_api_endpoints()