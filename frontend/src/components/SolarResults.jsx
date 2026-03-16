import React, { useState } from 'react'

export default function SolarResults({ data }) {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000'
  const MODEL_SERVER_URL = import.meta.env.VITE_MODEL_SERVER_URL || 'http://localhost:8007/docs'
  const AI_SERVER_URL = import.meta.env.VITE_AI_SERVER_URL || 'http://localhost:8005/docs'
  const MODEL_OUTPUT_URL = data?.stl_model_url ? `${API_BASE_URL}${data.stl_model_url}` : null
  const MODEL_VIEW_PAGE = MODEL_OUTPUT_URL
    ? `/model?url=${encodeURIComponent(MODEL_OUTPUT_URL)}`
    : null
  const [activeTab, setActiveTab] = useState('overview')

  if (!data || !data.success) {
    return (
      <div className="card shadow-sm p-4 text-center">
        <i className="bi bi-info-circle-fill text-muted mb-2" style={{ fontSize: '2rem' }}></i>
        <h5 className="text-muted">No Solar Analysis Yet</h5>
        <p className="text-muted mb-0">Fill in the solar inputs and click "Calculate Solar System" to see your analysis results.</p>
      </div>
    )
  }

  const calc = data.calculator_result
  const satellite = data.satellite_result
  const rooftop = data.rooftop_result

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount)
  }

  const formatNumber = (num, decimals = 2) => {
    return new Intl.NumberFormat('en-IN', {
      maximumFractionDigits: decimals
    }).format(num)
  }

  const TabButton = ({ tabId, label, icon, isActive, onClick }) => (
    <button
      className={`btn ${isActive ? 'btn-gradient' : 'btn-outline-secondary'} rounded-pill flex-grow-1 d-flex align-items-center justify-content-center gap-2`}
      onClick={() => onClick(tabId)}
    >
      <i className={`bi ${icon}`}></i>
      <span className="small fw-medium">{label}</span>
    </button>
  )

  return (
    <div className="card shadow-sm">
      <div className="card-header bg-gradient text-white">
        <h4 className="mb-0 d-flex align-items-center gap-2">
          <i className="bi bi-sun-fill"></i>
          Solar System Analysis Results
        </h4>
        <div className="small opacity-75 mt-1">
          {calc?.location?.name} • {formatNumber(calc?.system_configuration?.actual_capacity_kw)} kW System
        </div>
      </div>

      <div className="card-body p-0">
        {data.warning && (
          <div className="alert alert-warning m-3 mb-0" role="alert">
            <i className="bi bi-exclamation-triangle me-2"></i>
            {data.warning}
          </div>
        )}

        {/* Tab Navigation */}
        <div className="p-3 border-bottom">
          <div className="d-flex gap-2 flex-wrap">
            <TabButton
              tabId="overview"
              label="Overview"
              icon="bi-speedometer2"
              isActive={activeTab === 'overview'}
              onClick={setActiveTab}
            />
            <TabButton
              tabId="performance"
              label="Performance"
              icon="bi-lightning-fill"
              isActive={activeTab === 'performance'}
              onClick={setActiveTab}
            />
            <TabButton
              tabId="economics"
              label="Economics"
              icon="bi-currency-rupee"
              isActive={activeTab === 'economics'}
              onClick={setActiveTab}
            />
            <TabButton
              tabId="technical"
              label="Technical"
              icon="bi-gear-fill"
              isActive={activeTab === 'technical'}
              onClick={setActiveTab}
            />
            <TabButton
              tabId="satellite"
              label="Satellite"
              icon="bi-globe2"
              isActive={activeTab === 'satellite'}
              onClick={setActiveTab}
            />
          </div>
        </div>

        <div className="p-4">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="row g-4">
              <div className="col-md-6">
                <div className="card bg-success bg-opacity-10 border-success border-opacity-25 h-100">
                  <div className="card-body text-center">
                    <i className="bi bi-lightning-charge-fill text-success mb-2" style={{ fontSize: '2.5rem' }}></i>
                    <h3 className="text-success mb-1">{formatNumber(calc?.performance_results?.annual_energy_kwh)} kWh</h3>
                    <div className="fw-medium text-success">Annual Energy Production</div>
                    <div className="small text-muted mt-2">
                      Daily Average: {formatNumber(calc?.performance_results?.daily_energy_stats?.average_kwh)} kWh
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="col-md-6">
                <div className="card bg-primary bg-opacity-10 border-primary border-opacity-25 h-100">
                  <div className="card-body text-center">
                    <i className="bi bi-currency-rupee text-primary mb-2" style={{ fontSize: '2.5rem' }}></i>
                    <h3 className="text-primary mb-1">{formatCurrency(calc?.economic_analysis?.annual_savings_first_year_inr)}</h3>
                    <div className="fw-medium text-primary">Annual Savings (Year 1)</div>
                    <div className="small text-muted mt-2">
                      Monthly: {formatCurrency(calc?.economic_analysis?.monthly_average_savings_inr)}
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-md-4">
                <div className="card bg-warning bg-opacity-10 border-warning border-opacity-25 h-100">
                  <div className="card-body text-center">
                    <i className="bi bi-clock-fill text-warning mb-2" style={{ fontSize: '2rem' }}></i>
                    <h4 className="text-warning mb-1">{formatNumber(calc?.economic_analysis?.payback_period_years, 1)} years</h4>
                    <div className="fw-medium text-warning">Payback Period</div>
                  </div>
                </div>
              </div>

              <div className="col-md-4">
                <div className="card bg-info bg-opacity-10 border-info border-opacity-25 h-100">
                  <div className="card-body text-center">
                    <i className="bi bi-percent text-info mb-2" style={{ fontSize: '2rem' }}></i>
                    <h4 className="text-info mb-1">{formatNumber(calc?.economic_analysis?.lifetime_analysis?.roi_percent)}%</h4>
                    <div className="fw-medium text-info">25-Year ROI</div>
                  </div>
                </div>
              </div>

              <div className="col-md-4">
                <div className="card bg-success bg-opacity-10 border-success border-opacity-25 h-100">
                  <div className="card-body text-center">
                    <i className="bi bi-tree-fill text-success mb-2" style={{ fontSize: '2rem' }}></i>
                    <h4 className="text-success mb-1">{formatNumber(calc?.performance_results?.co2_offset_analysis?.equivalent_trees_planted)}</h4>
                    <div className="fw-medium text-success">Trees Equivalent</div>
                  </div>
                </div>
              </div>

              <div className="col-12">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0 d-flex align-items-center gap-2">
                      <i className="bi bi-gear"></i>
                      System Configuration
                    </h6>
                  </div>
                  <div className="card-body">
                    <div className="row g-3">
                      <div className="col-sm-6 col-lg-3">
                        <div className="small text-muted">System Capacity</div>
                        <div className="fw-medium">{formatNumber(calc?.system_configuration?.actual_capacity_kw)} kW</div>
                      </div>
                      <div className="col-sm-6 col-lg-3">
                        <div className="small text-muted">Number of Panels</div>
                        <div className="fw-medium">{calc?.system_configuration?.modules_count}</div>
                      </div>
                      <div className="col-sm-6 col-lg-3">
                        <div className="small text-muted">Panel Brand</div>
                        <div className="fw-medium">{calc?.selected_module?.manufacturer}</div>
                      </div>
                      <div className="col-sm-6 col-lg-3">
                        <div className="small text-muted">System Cost</div>
                        <div className="fw-medium">{formatCurrency(calc?.economic_analysis?.system_cost_inr)}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Performance Tab */}
          {activeTab === 'performance' && (
            <div className="row g-4">
              <div className="col-12">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0 d-flex align-items-center gap-2">
                      <i className="bi bi-bar-chart-fill"></i>
                      Monthly Energy Production
                    </h6>
                  </div>
                  <div className="card-body">
                    <div className="row g-2">
                      {calc?.monthly_breakdown?.map((month, idx) => (
                        <div key={idx} className="col-sm-6 col-lg-4 col-xl-3">
                          <div className="card bg-light border-0">
                            <div className="card-body text-center py-3">
                              <div className="small text-muted">{month.month}</div>
                              <div className="fw-bold text-primary">{formatNumber(month.energy_kwh)} kWh</div>
                              <div className="small text-muted">Daily avg: {formatNumber(month.daily_average_kwh)}</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0">Performance Metrics</h6>
                  </div>
                  <div className="card-body">
                    <div className="row g-3">
                      <div className="col-6">
                        <div className="small text-muted">Capacity Factor</div>
                        <div className="fw-medium text-success">{formatNumber(calc?.performance_results?.capacity_factor_percent)}%</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Specific Yield</div>
                        <div className="fw-medium">{formatNumber(calc?.performance_results?.specific_yield_kwh_per_kwp)} kWh/kWp</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Performance Ratio</div>
                        <div className="fw-medium">{formatNumber(calc?.performance_results?.performance_ratio)}</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">System Losses</div>
                        <div className="fw-medium text-warning">{calc?.system_configuration?.system_losses_percent}%</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0">Environmental Impact</h6>
                  </div>
                  <div className="card-body">
                    <div className="row g-3">
                      <div className="col-12">
                        <div className="small text-muted">Annual CO2 Avoided</div>
                        <div className="fw-medium text-success">{formatNumber(calc?.performance_results?.co2_offset_analysis?.annual_co2_avoided_kg)} kg</div>
                      </div>
                      <div className="col-12">
                        <div className="small text-muted">Lifetime CO2 Avoided</div>
                        <div className="fw-medium text-success">{formatNumber(calc?.performance_results?.co2_offset_analysis?.lifetime_co2_avoided_tonnes)} tonnes</div>
                      </div>
                      <div className="col-12">
                        <div className="small text-muted">Equivalent Trees Planted</div>
                        <div className="fw-medium text-success">{formatNumber(calc?.performance_results?.co2_offset_analysis?.equivalent_trees_planted)}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Economics Tab */}
          {activeTab === 'economics' && (
            <div className="row g-4">
              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0 d-flex align-items-center gap-2">
                      <i className="bi bi-currency-rupee"></i>
                      Cost Breakdown
                    </h6>
                  </div>
                  <div className="card-body">
                    <div className="row g-3">
                      <div className="col-6">
                        <div className="small text-muted">Modules Cost</div>
                        <div className="fw-medium">{formatCurrency(calc?.budget_analysis?.cost_breakdown?.modules_cost_inr)}</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Inverter Cost</div>
                        <div className="fw-medium">{formatCurrency(calc?.budget_analysis?.cost_breakdown?.inverter_cost_inr)}</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Mounting & BOS</div>
                        <div className="fw-medium">{formatCurrency(calc?.budget_analysis?.cost_breakdown?.mounting_bos_inr)}</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Installation</div>
                        <div className="fw-medium">{formatCurrency(calc?.budget_analysis?.cost_breakdown?.installation_inr)}</div>
                      </div>
                      <div className="col-12 border-top pt-3">
                        <div className="small text-muted">Total System Cost</div>
                        <div className="fw-bold h5 text-primary mb-0">{formatCurrency(calc?.budget_analysis?.actual_system_cost_inr)}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0 d-flex align-items-center gap-2">
                      <i className="bi bi-graph-up"></i>
                      Financial Returns
                    </h6>
                  </div>
                  <div className="card-body">
                    <div className="row g-3">
                      <div className="col-12">
                        <div className="small text-muted">Payback Period</div>
                        <div className="fw-bold h5 text-success mb-0">{formatNumber(calc?.economic_analysis?.payback_period_years, 1)} years</div>
                      </div>
                      <div className="col-12">
                        <div className="small text-muted">25-Year Total Savings</div>
                        <div className="fw-bold h5 text-primary mb-0">{formatCurrency(calc?.economic_analysis?.lifetime_analysis?.total_savings_inr)}</div>
                      </div>
                      <div className="col-12">
                        <div className="small text-muted">Return on Investment (ROI)</div>
                        <div className="fw-bold h5 text-warning mb-0">{formatNumber(calc?.economic_analysis?.lifetime_analysis?.roi_percent)}%</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-12">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0 d-flex align-items-center gap-2">
                      <i className="bi bi-credit-card"></i>
                      Financing Options
                    </h6>
                  </div>
                  <div className="card-body">
                    <div className="row g-4">
                      <div className="col-md-4">
                        <div className="card bg-success bg-opacity-10 border-success border-opacity-25">
                          <div className="card-body text-center">
                            <i className="bi bi-cash-coin text-success mb-2" style={{ fontSize: '1.5rem' }}></i>
                            <h6 className="text-success">Full Payment</h6>
                            <div className="fw-bold">{formatCurrency(calc?.budget_analysis?.financing_options?.full_upfront_payment?.amount_inr)}</div>
                            <div className="small text-muted">Payback: {formatNumber(calc?.budget_analysis?.financing_options?.full_upfront_payment?.payback_years, 1)} years</div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="col-md-4">
                        <div className="card bg-info bg-opacity-10 border-info border-opacity-25">
                          <div className="card-body text-center">
                            <i className="bi bi-bank text-info mb-2" style={{ fontSize: '1.5rem' }}></i>
                            <h6 className="text-info">5-Year Loan</h6>
                            <div className="fw-bold">{formatCurrency(calc?.budget_analysis?.financing_options?.loan_option_5_years?.monthly_emi_inr)}/month</div>
                            <div className="small text-muted">Total: {formatCurrency(calc?.budget_analysis?.financing_options?.loan_option_5_years?.total_payment_inr)}</div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="col-md-4">
                        <div className="card bg-warning bg-opacity-10 border-warning border-opacity-25">
                          <div className="card-body text-center">
                            <i className="bi bi-gift text-warning mb-2" style={{ fontSize: '1.5rem' }}></i>
                            <h6 className="text-warning">With Subsidy</h6>
                            <div className="fw-bold">{formatCurrency(calc?.budget_analysis?.financing_options?.subsidy_available?.net_cost_after_subsidy_inr)}</div>
                            <div className="small text-muted">Subsidy: {formatCurrency(calc?.budget_analysis?.financing_options?.subsidy_available?.max_subsidy_inr)}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Technical Tab */}
          {activeTab === 'technical' && (
            <div className="row g-4">
              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0 d-flex align-items-center gap-2">
                      <i className="bi bi-cpu"></i>
                      Solar Module Details
                    </h6>
                  </div>
                  <div className="card-body">
                    <div className="row g-3">
                      <div className="col-12">
                        <div className="small text-muted">Model</div>
                        <div className="fw-medium">{calc?.selected_module?.model}</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Manufacturer</div>
                        <div className="fw-medium">{calc?.selected_module?.manufacturer}</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Technology</div>
                        <div className="fw-medium">{calc?.selected_module?.technology}</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Power Rating</div>
                        <div className="fw-medium">{calc?.selected_module?.power_w}W</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Efficiency</div>
                        <div className="fw-medium text-success">{calc?.selected_module?.efficiency_percent}%</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0 d-flex align-items-center gap-2">
                      <i className="bi bi-lightning"></i>
                      Inverter Details
                    </h6>
                  </div>
                  <div className="card-body">
                    <div className="row g-3">
                      <div className="col-12">
                        <div className="small text-muted">Model</div>
                        <div className="fw-medium">{calc?.selected_inverter?.model}</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Manufacturer</div>
                        <div className="fw-medium">{calc?.selected_inverter?.manufacturer}</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Efficiency</div>
                        <div className="fw-medium text-success">{calc?.selected_inverter?.efficiency_percent}%</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">AC Power</div>
                        <div className="fw-medium">{formatNumber(calc?.selected_inverter?.ac_power_w/1000, 1)}kW</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">DC Power</div>
                        <div className="fw-medium">{formatNumber(calc?.selected_inverter?.dc_power_w/1000, 1)}kW</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0 d-flex align-items-center gap-2">
                      <i className="bi bi-compass"></i>
                      System Orientation
                    </h6>
                  </div>
                  <div className="card-body">
                    <div className="row g-3">
                      <div className="col-6">
                        <div className="small text-muted">Optimal Tilt</div>
                        <div className="fw-medium text-primary">{calc?.system_configuration?.tilt_degrees}°</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Optimal Azimuth</div>
                        <div className="fw-medium text-primary">{calc?.system_configuration?.azimuth_degrees}°</div>
                      </div>
                      <div className="col-12">
                        <div className="small text-muted">Mounting Type</div>
                        <div className="fw-medium">{calc?.system_configuration?.mounting_type}</div>
                      </div>
                      <div className="col-12">
                        <div className="small text-success">
                          <i className="bi bi-check-circle me-1"></i>
                          Optimization improved energy by {formatNumber(calc?.optimization?.improvement_percent)}%
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0 d-flex align-items-center gap-2">
                      <i className="bi bi-thermometer-sun"></i>
                      Weather Summary
                    </h6>
                  </div>
                  <div className="card-body">
                    <div className="row g-3">
                      <div className="col-6">
                        <div className="small text-muted">Avg GHI</div>
                        <div className="fw-medium">{formatNumber(calc?.weather_summary?.average_ghi_kwh_m2_day)} kWh/m²/day</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Avg Temperature</div>
                        <div className="fw-medium">{calc?.weather_summary?.average_temperature_c}°C</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Data Points</div>
                        <div className="fw-medium">{formatNumber(calc?.weather_summary?.total_data_points)}</div>
                      </div>
                      <div className="col-6">
                        <div className="small text-muted">Data Source</div>
                        <div className="fw-medium">{calc?.weather_summary?.data_source}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Satellite Tab */}
          {activeTab === 'satellite' && (
            <div className="row g-4">
              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0 d-flex align-items-center gap-2">
                      <i className="bi bi-satellite"></i>
                      Satellite Image Analysis
                    </h6>
                  </div>
                  <div className="card-body">
                    {satellite && satellite.success ? (
                      <div className="row g-3">
                        <div className="col-6">
                          <div className="small text-muted">Zoom Level</div>
                          <div className="fw-medium">{satellite.zoom_level} ({satellite.zoom_description})</div>
                        </div>
                        <div className="col-6">
                          <div className="small text-muted">Resolution</div>
                          <div className="fw-medium">{formatNumber(satellite.resolution_m_per_pixel, 3)} m/pixel</div>
                        </div>
                        <div className="col-6">
                          <div className="small text-muted">Coverage</div>
                          <div className="fw-medium">{satellite.coverage_description}</div>
                        </div>
                        <div className="col-6">
                          <div className="small text-muted">Image Size</div>
                          <div className="fw-medium">{satellite.image_size?.width}×{satellite.image_size?.height}px</div>
                        </div>
                        <div className="col-12">
                          <div className="small text-muted">Filename</div>
                          <div className="fw-medium font-monospace small">{satellite.filename}</div>
                        </div>
                        {(satellite.preview_url || satellite.download_url || satellite.file_url) && (
                          <div className="col-12">
                            <a 
                              href={`${API_BASE_URL}${satellite.download_url || satellite.preview_url || satellite.file_url}`}
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="btn btn-outline-primary btn-sm"
                            >
                              <i className="bi bi-download me-2"></i>
                              Download Satellite Image
                            </a>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-center text-muted">
                        <i className="bi bi-exclamation-triangle mb-2" style={{ fontSize: '2rem' }}></i>
                        <p>Satellite image analysis not available</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="col-md-6">
                <div className="card">
                  <div className="card-header">
                    <h6 className="mb-0 d-flex align-items-center gap-2">
                      <i className="bi bi-house"></i>
                      Rooftop Analysis
                    </h6>
                  </div>
                  <div className="card-body">
                    {rooftop && rooftop.success ? (
                      <div className="row g-3">
                        {rooftop.length && (
                          <>
                            <div className="col-6">
                              <div className="small text-muted">Rooftop Length</div>
                              <div className="fw-medium text-primary">{formatNumber(rooftop.length)} m</div>
                            </div>
                            <div className="col-6">
                              <div className="small text-muted">Rooftop Width</div>
                              <div className="fw-medium text-primary">{formatNumber(rooftop.width)} m</div>
                            </div>
                            <div className="col-12">
                              <div className="small text-muted">Estimated Rooftop Area</div>
                              <div className="fw-bold h6 text-success mb-0">{formatNumber(rooftop.length * rooftop.width)} m²</div>
                            </div>
                          </>
                        )}
                        {rooftop.image_location && (
                          <div className="col-12">
                            <div className="small text-muted">Analysis Image</div>
                            <div className="fw-medium font-monospace small">{rooftop.image_location}</div>
                          </div>
                        )}
                        {rooftop.file_url && (
                          <div className="col-12">
                            <a 
                              href={`${API_BASE_URL}${rooftop.file_url}`} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="btn btn-outline-success btn-sm"
                            >
                              <i className="bi bi-download me-2"></i>
                              Download Rooftop Analysis
                            </a>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-center text-muted">
                        <i className="bi bi-exclamation-triangle mb-2" style={{ fontSize: '2rem' }}></i>
                        <p>Rooftop analysis not available</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {satellite && (satellite.preview_url || satellite.download_url || satellite.file_url) && (
                <div className="col-12">
                  <div className="card">
                    <div className="card-header">
                      <h6 className="mb-0 d-flex align-items-center gap-2">
                        <i className="bi bi-image"></i>
                        Satellite Image Preview
                      </h6>
                    </div>
                    <div className="card-body text-center">
                      <img
                        src={`${API_BASE_URL}${satellite.preview_url || satellite.download_url || satellite.file_url}`}
                        alt="Satellite view of location"
                        className="img-fluid rounded shadow-sm"
                        style={{ maxHeight: '400px' }}
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'block';
                        }}
                      />

                      <div style={{ display: 'none' }} className="text-muted">
                        <i className="bi bi-exclamation-triangle mb-2" style={{ fontSize: '2rem' }}></i>
                        <p>Unable to load satellite image</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="col-12 mt-4 text-center">
                <a 
                  href={MODEL_VIEW_PAGE || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`btn ${MODEL_VIEW_PAGE ? 'btn-primary' : 'btn-secondary disabled'}`}
                  onClick={(e) => {
                    if (!MODEL_VIEW_PAGE) e.preventDefault()
                  }}
                >
                  <i className="bi bi-robot me-2"></i>
                  {data?.stl_model_url ? 'Open 3D Model Viewer' : '3D Model Unavailable (Demo Mode)'}
                </a>
                <a
                  href={MODEL_SERVER_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-outline-secondary ms-2"
                >
                  <i className="bi bi-box me-2"></i>
                  Open STL API Docs
                </a>
                <a
                  href={AI_SERVER_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-outline-secondary ms-2 mt-2 mt-sm-0"
                >
                  <i className="bi bi-cpu me-2"></i>
                  Open Rooftop AI Docs
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}