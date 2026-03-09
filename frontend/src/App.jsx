import React, { useState } from 'react'
import MapPicker from './components/MapPicker'
import FormPanel from './components/FormPanel'
import SolarResults from './components/SolarResults'

export default function App(){
  const [location, setLocation] = useState(null)
  const [lastInvoiceUrl, setLastInvoiceUrl] = useState(null)
  const [solarResults, setSolarResults] = useState(null)

  return (
    <div className="app-root">
      <nav className="navbar custom-nav">
        <div className="container d-flex justify-content-between align-items-center">
          <span className="brand">Solar</span>
        </div>
      </nav>

      <main className="container py-4">
        <div className="row g-4">
          <div className="col-lg-7">
            <div className="card shadow-sm p-3">
              <h4>Location</h4>
              <MapPicker onLocation={(latlng)=> setLocation(latlng)} initialLocation={location} />
              <div className="mt-2 small text-muted">Selected: {location? `${location.lat.toFixed(6)}, ${location.lng.toFixed(6)}` : 'none'}</div>
            </div>

            <div className="card shadow-sm p-3 mt-3">
              <h4>Invoice preview</h4>
              <div className="d-flex gap-2">
                <a className="btn btn-outline-primary rounded-pill" href={lastInvoiceUrl? `/preview?url=${encodeURIComponent(lastInvoiceUrl)}` : '/preview'} target="_blank" rel="noreferrer">Open preview</a>
              </div>
            </div>
          </div>

          <div className="col-lg-5">
            <FormPanel 
              location={location} 
              onInvoice={(url)=> setLastInvoiceUrl(url)}
              onResults={(results)=> setSolarResults(results)}
            />
          </div>
        </div>

        {/* Solar Results Section */}
        {solarResults && (
          <div className="row g-4 mt-2">
            <div className="col-12">
              <SolarResults data={solarResults} />
            </div>
          </div>
        )}
      </main>

      <footer className="footer text-center py-3">© Solar</footer>
    </div>
  )
}
