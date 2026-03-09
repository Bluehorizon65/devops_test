import React, { useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000'

export default function FormPanel({ location, onResults }){
  const [systemCapacity, setSystemCapacity] = useState('7.5')
  const [optimizeOrientation, setOptimizeOrientation] = useState('true')
  const [electricityRate, setElectricityRate] = useState('7.5')
  const [budget, setBudget] = useState('600000')
  const [preferredBrand, setPreferredBrand] = useState('Jinko')
  const [maxPayback, setMaxPayback] = useState('7')
  const [locationName, setLocationName] = useState('Karunya')
  const [zoomLevel, setZoomLevel] = useState('6')
  const [status, setStatus] = useState('Ready')
  const [loading, setLoading] = useState(false)

  const handleSolarCalculation = async () => {
    if (!location) {
      setStatus('Please select a location on the map first')
      return
    }

    setLoading(true)
    setStatus('Calculating solar system...')

    try {
      const payload = {
        latitude: parseFloat(location.lat),
        longitude: parseFloat(location.lng),
        system_capacity_kw: parseFloat(systemCapacity),
        year: 2024, // Constant value as requested
        optimize_orientation: optimizeOrientation === 'true',
        electricity_rate_inr: parseFloat(electricityRate),
        budget_inr: parseFloat(budget),
        prefer_brand: preferredBrand,
        max_payback_years: parseFloat(maxPayback),
        location_name: locationName,
        zoom_level: parseInt(zoomLevel)
      }

      console.log('Sending payload to backend:', payload)

      const response = await fetch(`${API_BASE_URL}/solar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

      const data = await response.json()
      console.log('Solar calculation response:', data)
      
      setStatus('Solar analysis completed successfully!')
      if (onResults) onResults(data)

    } catch (error) {
      console.error('Solar calculation error:', error)
      
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        setStatus(`Connection failed: Cannot reach backend server at ${API_BASE_URL}`)
      } else {
        setStatus(`Calculation failed: ${error.message}`)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card shadow-sm">
      <div className="card-header bg-gradient text-white">
        <h4 className="mb-0 d-flex align-items-center gap-2">
          <i className="bi bi-sun-fill"></i>
          Solar System Configuration
        </h4>
      </div>
      
      <div className="card-body p-4">
        <div className="mb-3">
          <label className="form-label fw-medium">
            <i className="bi bi-lightning-charge-fill text-warning me-2"></i>
            System Capacity (kW)
          </label>
          <input 
            type="number" 
            className="form-control form-control-lg rounded-pill" 
            value={systemCapacity} 
            onChange={e => setSystemCapacity(e.target.value)}
            placeholder="e.g., 7.5"
            step="0.1"
            min="1"
            max="100"
          />
          <div className="form-text">Recommended: 5-15 kW for residential properties</div>
        </div>

        <div className="mb-3">
          <label className="form-label fw-medium">
            <i className="bi bi-currency-rupee text-success me-2"></i>
            Budget (INR)
          </label>
          <input 
            type="number" 
            className="form-control form-control-lg rounded-pill" 
            value={budget} 
            onChange={e => setBudget(e.target.value)}
            placeholder="e.g., 600000"
            step="1000"
            min="100000"
          />
          <div className="form-text">Total budget for solar system installation</div>
        </div>

        <div className="mb-3">
          <label className="form-label fw-medium">
            <i className="bi bi-award-fill text-primary me-2"></i>
            Preferred Brand
          </label>
          <select 
            className="form-select form-select-lg rounded-pill" 
            value={preferredBrand} 
            onChange={e => setPreferredBrand(e.target.value)}
          >
            <option value="Jinko">Jinko</option>
            <option value="Waaree">Waaree</option>
            <option value="Trina">Trina Solar</option>
            <option value="Canadian">Canadian Solar</option>
            <option value="Vikram">Vikram Solar</option>
            <option value="Adani">Adani Solar</option>
            <option value="Luminous">Luminous</option>
          </select>
          <div className="form-text">Choose your preferred solar panel manufacturer</div>
        </div>

        <div className="mb-3">
          <label className="form-label fw-medium">
            <i className="bi bi-clock-fill text-info me-2"></i>
            Maximum Payback Period (Years)
          </label>
          <input 
            type="number" 
            className="form-control form-control-lg rounded-pill" 
            value={maxPayback} 
            onChange={e => setMaxPayback(e.target.value)}
            placeholder="e.g., 7"
            step="1"
            min="3"
            max="15"
          />
          <div className="form-text">Maximum years to recover investment</div>
        </div>

        <div className="mb-3">
          <label className="form-label fw-medium">
            <i className="bi bi-lightning-fill text-danger me-2"></i>
            Electricity Rate (INR per kWh)
          </label>
          <input 
            type="number" 
            className="form-control form-control-lg rounded-pill" 
            value={electricityRate} 
            onChange={e => setElectricityRate(e.target.value)}
            placeholder="e.g., 7.5"
            step="0.1"
            min="1"
            max="20"
          />
          <div className="form-text">Current electricity rate you pay</div>
        </div>

        <div className="mb-3">
          <label className="form-label fw-medium">
            <i className="bi bi-geo-alt-fill text-secondary me-2"></i>
            Location Name
          </label>
          <input 
            type="text" 
            className="form-control form-control-lg rounded-pill" 
            value={locationName} 
            onChange={e => setLocationName(e.target.value)}
            placeholder="e.g., Karunya"
          />
          <div className="form-text">Name for your location</div>
        </div>

        <div className="mb-3">
          <label className="form-label fw-medium">
            <i className="bi bi-zoom-in text-info me-2"></i>
            Zoom Level
          </label>
          <select 
            className="form-select form-select-lg rounded-pill" 
            value={zoomLevel} 
            onChange={e => setZoomLevel(e.target.value)}
          >
            <option value="1">1 - Very Low</option>
            <option value="2">2 - Low</option>
            <option value="3">3 - Medium-Low</option>
            <option value="4">4 - Medium</option>
            <option value="5">5 - Medium-High</option>
            <option value="6">6 - High</option>
            <option value="7">7 - Very High</option>
            <option value="8">8 - Ultra High</option>
          </select>
          <div className="form-text">Satellite image detail level</div>
        </div>

        <div className="mb-4">
          <div className="form-check form-switch">
            <input 
              className="form-check-input" 
              type="checkbox" 
              role="switch" 
              id="optimizeSwitch"
              checked={optimizeOrientation === 'true'}
              onChange={e => setOptimizeOrientation(e.target.checked ? 'true' : 'false')}
            />
            <label className="form-check-label fw-medium" htmlFor="optimizeSwitch">
              <i className="bi bi-compass text-warning me-2"></i>
              Optimize Panel Orientation
            </label>
            <div className="form-text">Automatically find the best tilt and azimuth angles</div>
          </div>
        </div>

        <div className="d-grid">
          <button 
            className="btn btn-gradient btn-lg rounded-pill" 
            onClick={handleSolarCalculation}
            disabled={loading || !location}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Calculating...
              </>
            ) : (
              <>
                <i className="bi bi-calculator me-2"></i>
                Calculate Solar System
              </>
            )}
          </button>
        </div>

        <div className="mt-3">
          <div className={`small ${status.includes('failed') || status.includes('Cannot') ? 'text-danger' : status.includes('successfully') ? 'text-success' : 'text-muted'}`}>
            {status}
          </div>
        </div>

        {location && (
          <div className="mt-3 p-3 bg-light bg-opacity-50 rounded-3">
            <div className="small fw-medium text-muted mb-1">Selected Location:</div>
            <div className="font-monospace small">
              <i className="bi bi-geo-alt-fill text-primary me-1"></i>
              {location.lat.toFixed(6)}, {location.lng.toFixed(6)}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
