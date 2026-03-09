import React, { useState, useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet'

function ClickHandler({ onClick }){
  useMapEvents({ click(e){ onClick(e.latlng) } })
  return null
}

function MapInstanceHandler({ onMapReady }){
  const map = useMap()
  
  useEffect(() => {
    if (map && onMapReady) {
      onMapReady(map)
    }
  }, [map, onMapReady])
  
  return null
}

export default function MapPicker({ onLocation, initialLocation }){
  const [open, setOpen] = useState(false)
  const [marker, setMarker] = useState(initialLocation || null)
  const [mapInstance, setMapInstance] = useState(null)
  const pendingTargetRef = useRef(null)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [satellite, setSatellite] = useState(false)
  const [zoomLevel, setZoomLevel] = useState(2)
  const wrapperRef = useRef(null)
  const debounceRef = useRef(null)

  useEffect(()=>{ if (initialLocation) setMarker(initialLocation) }, [initialLocation])

  useEffect(()=>{
    if (!mapInstance) return
    const onZoom = ()=> setZoomLevel(mapInstance.getZoom())
    mapInstance.on('zoomend', onZoom)
    return ()=> mapInstance.off('zoomend', onZoom)
  }, [mapInstance])

  // if there was a pending target (search returned before map finished initializing), go there now
  useEffect(()=>{
    if (!mapInstance) return
    if (!pendingTargetRef.current) return
    
    console.log('Map instance ready, processing pending target:', pendingTargetRef.current)
    const t = setTimeout(()=>{
      try{
        const p = pendingTargetRef.current
        if (p) {
          console.log('Setting pending view to:', p.lat, p.lng, p.zoom)
          mapInstance.setView([p.lat, p.lng], p.zoom || 16, { animate: true, duration: 1.5 })
          setZoomLevel(p.zoom || 16)
        }
      }catch(e){
        console.error('Error setting pending view:', e)
      }
      pendingTargetRef.current = null
    }, 300)
    return ()=> clearTimeout(t)
  }, [mapInstance])

  const zoomToLatLng = (lat, lon, zoom=16)=>{
    console.log('zoomToLatLng called with:', lat, lon, zoom)
    if (mapInstance){
      try{ 
        mapInstance.setView([lat, lon], zoom, { animate: true, duration: 1.5 });
        setZoomLevel(zoom);
        console.log('Successfully zoomed to:', lat, lon, zoom)
      } catch(e){ 
        console.error('Error zooming map:', e);
      }
    } else {
      console.log('Map not ready, storing target:', lat, lon, zoom)
      pendingTargetRef.current = { lat, lng: lon, zoom }
    }
  }

  // ensure Leaflet recalculates size when the panel opens
  useEffect(()=>{
    if (!mapInstance) return
    if (!open) return
    const t = setTimeout(()=>{ try { mapInstance.invalidateSize() } catch(e){} }, 200)
    return ()=> clearTimeout(t)
  }, [open, mapInstance])

  const notifyBackend = (latlng)=>{
    fetch('/api/location', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ lat: latlng.lat, lon: latlng.lng }) })
    .catch(e=> console.error('send location failed', e))
  }

  const handleMapClick = (latlng)=>{
    setMarker({ lat: latlng.lat, lng: latlng.lng })
    if (onLocation) onLocation({ lat: latlng.lat, lng: latlng.lng })
    notifyBackend(latlng)
    if (mapInstance) {
      const currentZoom = mapInstance.getZoom()
      const targetZoom = Math.max(14, currentZoom)
      mapInstance.setView([latlng.lat, latlng.lng], targetZoom, { animate: true })
      setZoomLevel(targetZoom)
    }
  }

  const calculateZoomLevel = (boundingBox) => {
    // Convert bounding box string array to numbers
    const bbox = boundingBox.map(coord => parseFloat(coord));
    const [south, north, west, east] = bbox;
    
    // Calculate the distance
    const latDiff = Math.abs(north - south);
    const lngDiff = Math.abs(east - west);
    const maxDiff = Math.max(latDiff, lngDiff);
    
    // Enhanced zoom levels for better auto-zoom experience
    if (maxDiff < 0.0001) return 18;      // Building/address level
    if (maxDiff < 0.0005) return 17;      // Block level
    if (maxDiff < 0.001) return 16;       // Street level
    if (maxDiff < 0.005) return 15;       // Neighborhood
    if (maxDiff < 0.01) return 14;        // District
    if (maxDiff < 0.05) return 13;        // Small city area
    if (maxDiff < 0.1) return 12;         // City district
    if (maxDiff < 0.5) return 11;         // City
    if (maxDiff < 2) return 10;           // Metropolitan area
    if (maxDiff < 5) return 8;            // Region
    return 6;                             // Country/large region
  }

  const doSearch = async (q)=>{
    if (!q || !q.trim()) { setResults([]); return }
    setSearching(true)
    try{
      const url = `https://nominatim.openstreetmap.org/search?format=json&limit=8&q=${encodeURIComponent(q)}&addressdetails=1&extratags=1&bounded=1`
      const res = await fetch(url, { headers:{ 'Accept':'application/json' } })
      const json = await res.json()
      setResults(json || [])
      
      // Auto-zoom to the first (most relevant) result immediately when search completes
      if (json && json.length > 0) {
        const first = json[0]
        const lat = parseFloat(first.lat)
        const lon = parseFloat(first.lon)
        
        // Calculate appropriate zoom level based on the bounding box
        const boundingBox = [first.boundingbox[0], first.boundingbox[1], first.boundingbox[2], first.boundingbox[3]]
        const zoomLevel = calculateZoomLevel(boundingBox)
        
        // Set marker to the best result
        const latlng = { lat, lng: lon }
        setMarker(latlng)
        
        // Auto-zoom to the location with smooth animation
        if (mapInstance) {
          console.log('Auto-zooming to:', lat, lon, 'with zoom level:', zoomLevel)
          try {
            mapInstance.setView([lat, lon], zoomLevel, { 
              animate: true, 
              duration: 1.5
            })
            setZoomLevel(zoomLevel)
          } catch (e) {
            console.error('Error setting map view:', e)
          }
        } else {
          console.log('Map not ready, storing target for later:', lat, lon, zoomLevel)
          // Store for when map becomes ready
          pendingTargetRef.current = { lat, lng: lon, zoom: zoomLevel }
        }
        
        // Notify parent components
        if (onLocation) onLocation(latlng)
        notifyBackend(latlng)
      }
    }catch(err){
      console.error('Search failed:', err)
      setResults([])
    }finally{ 
      setSearching(false) 
    }
  }

  const pickResult = (r)=>{
    const lat = parseFloat(r.lat)
    const lon = parseFloat(r.lon)
    const latlng = { lat, lng: lon }
    setMarker(latlng)
    
    // Calculate appropriate zoom level based on the bounding box
    const boundingBox = [r.boundingbox[0], r.boundingbox[1], r.boundingbox[2], r.boundingbox[3]]
    const zoomLevel = calculateZoomLevel(boundingBox)
    
    zoomToLatLng(lat, lon, zoomLevel)
    if (onLocation) onLocation(latlng)
    notifyBackend({ lat, lng: lon })
    setResults([])
  }

  return (
    <div>
      <div className="d-flex gap-3 align-items-center">
        <button className="btn btn-gradient rounded-pill btn-lg d-flex align-items-center gap-2 shadow-sm" onClick={()=> setOpen(true)}>
          <i className="bi bi-geo-alt-fill"></i>
          Pick Location
        </button>
        <button className="btn btn-outline-secondary rounded-pill btn-lg d-flex align-items-center gap-2" onClick={()=> { setMarker(null); onLocation && onLocation(null) }}>
          <i className="bi bi-x-circle"></i>
          Clear
        </button>
        {marker && (
          <div className="badge bg-success-subtle text-success d-flex align-items-center gap-1 px-3 py-2">
            <i className="bi bi-check-circle-fill"></i>
            Location Selected
          </div>
        )}
      </div>

      {open && (
        <div className="map-panel card mt-4 shadow-lg border-0" ref={wrapperRef}>
          <div className="map-panel-header d-flex align-items-center justify-content-between bg-gradient p-4 rounded-top">
            <div>
              <h5 className="mb-1 text-white d-flex align-items-center gap-2">
                <i className="bi bi-map-fill"></i>
                Location Picker
              </h5>
              <div className="small text-white-50 d-flex align-items-center gap-1">
                <i className="bi bi-info-circle"></i>
                Search for an address (auto-zooms) or click anywhere on the map
              </div>
            </div>
            <div className="d-flex gap-2">
              <button className="btn btn-sm btn-outline-light rounded-pill d-flex align-items-center gap-1" onClick={()=> { setMarker(null); onLocation && onLocation(null) }}>
                <i className="bi bi-arrow-clockwise"></i>
                Reset
              </button>
              <button className="btn btn-sm btn-light rounded-pill d-flex align-items-center gap-1" onClick={()=> setOpen(false)}>
                <i className="bi bi-x-lg"></i>
                Close
              </button>
            </div>
          </div>

          <div className="d-flex align-items-center gap-3 p-3 bg-light bg-opacity-50" style={{ borderBottom: '1px solid var(--border-default)' }}>
            <div className="position-relative flex-grow-1">
              <i className="bi bi-search" style={{
                position: 'absolute',
                left: '16px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)',
                fontSize: '1.1rem',
                zIndex: 10
              }}></i>
              <input
                className="form-control map-search-input pe-5"
                placeholder="🌍 Search for any location worldwide..."
                value={query}
                onChange={(e)=>{
                  setQuery(e.target.value)
                  // Clear previous debounce
                  if (debounceRef.current) clearTimeout(debounceRef.current)
                  // Auto-search after user stops typing for 500ms
                  debounceRef.current = setTimeout(()=> doSearch(e.target.value), 500)
                }}
                onKeyDown={(e)=> { 
                  if (e.key === 'Enter') { 
                    // Clear debounce and search immediately
                    if (debounceRef.current) clearTimeout(debounceRef.current)
                    doSearch(query)
                  }
                }}
                style={{ paddingLeft: '48px', paddingRight: '48px', height: '48px' }}
              />
              {query && (
                <button 
                  className="btn btn-sm btn-outline-secondary position-absolute"
                  style={{ right: '8px', top: '50%', transform: 'translateY(-50%)', zIndex: 10 }}
                  onClick={() => { setQuery(''); setResults([]) }}
                >
                  <i className="bi bi-x"></i>
                </button>
              )}
            </div>
            <button 
              className="btn btn-gradient d-flex align-items-center gap-2 px-4" 
              onClick={()=> { 
                if (debounceRef.current) clearTimeout(debounceRef.current)
                doSearch(query) 
              }}
              disabled={!query.trim() || searching}
              style={{ height: '48px', minWidth: '140px' }}
            >
              {searching ? (
                <>
                  <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                  Searching...
                </>
              ) : (
                <>
                  <i className="bi bi-search"></i>
                  Search & Zoom
                </>
              )}
            </button>
          </div>

          {results && results.length > 0 && (
            <div className="mx-3 mb-3">
              <div className="small text-muted mb-2 d-flex align-items-center gap-1">
                <i className="bi bi-list-ul"></i>
                Search Results ({results.length})
              </div>
              <div style={{maxHeight: '180px', overflowY: 'auto'}} className="list-group shadow-sm">
                {results.map((r,i)=> (
                  <button key={i} className="list-group-item list-group-item-action border-0 d-flex align-items-start gap-3 py-3" onClick={()=> pickResult(r)}>
                    <div className="bg-primary bg-opacity-10 rounded-circle p-2 flex-shrink-0">
                      <i className="bi bi-geo-alt-fill text-primary"></i>
                    </div>
                    <div className="flex-grow-1 text-start">
                      <div className="fw-semibold text-dark mb-1">{r.display_name.split(',').slice(0,2).join(',')}</div>
                      <div className="small text-muted">{r.display_name}</div>
                    </div>
                    <i className="bi bi-chevron-right text-muted"></i>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="position-relative p-3">
            <div className="position-relative overflow-hidden rounded-3 shadow-lg" style={{ height: '520px' }}>
              <MapContainer center={[20,0]} zoom={2} style={{height: '100%', width: '100%', borderRadius: '1rem'}}>
                <MapInstanceHandler onMapReady={setMapInstance} />
                <ClickHandler onClick={handleMapClick} />
                {marker && <Marker position={[marker.lat, marker.lng]} />}
                {satellite ? (
                  <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" attribution={'Tiles © Esri'} />
                ) : (
                  <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="© OpenStreetMap contributors" />
                )}
              </MapContainer>
              
              {marker && (
                <div className="position-absolute bottom-0 start-0 m-3 bg-dark bg-opacity-75 text-white rounded-3 px-3 py-2 shadow-lg backdrop-blur">
                  <div className="small fw-medium d-flex align-items-center gap-2 mb-1">
                    <i className="bi bi-geo-alt-fill text-warning"></i>
                    Selected Location
                  </div>
                  <div className="font-monospace small">
                    <div>Lat: {marker.lat.toFixed(6)}</div>
                    <div>Lng: {marker.lng.toFixed(6)}</div>
                  </div>
                </div>
              )}

              <div className="position-absolute top-0 end-0 m-3" style={{ zIndex: 1000 }}>
                <div className="btn-group-vertical shadow-lg" role="group">
                  <button 
                    className="btn btn-light btn-sm d-flex align-items-center justify-content-center" 
                    onClick={()=> mapInstance && mapInstance.zoomIn()}
                    style={{ width: '40px', height: '40px' }}
                    title="Zoom In"
                  >
                    <i className="bi bi-plus-lg"></i>
                  </button>
                  <button 
                    className="btn btn-light btn-sm d-flex align-items-center justify-content-center" 
                    onClick={()=> mapInstance && mapInstance.zoomOut()}
                    style={{ width: '40px', height: '40px' }}
                    title="Zoom Out"
                  >
                    <i className="bi bi-dash-lg"></i>
                  </button>
                  <button 
                    className="btn btn-light btn-sm d-flex align-items-center justify-content-center" 
                    onClick={()=> setSatellite(s=> !s)}
                    style={{ width: '40px', height: '40px' }}
                    title={satellite ? 'Street View' : 'Satellite View'}
                  >
                    {satellite ? <i className="bi bi-map"></i> : <i className="bi bi-globe2"></i>}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-light bg-opacity-75 border-top px-4 py-3 d-flex align-items-center justify-content-between rounded-bottom">
            <div className="d-flex align-items-center gap-3">
              <div className="d-flex align-items-center gap-2">
                <div className="bg-primary bg-opacity-10 rounded-circle p-1">
                  <i className="bi bi-geo text-primary"></i>
                </div>
                <div>
                  <div className="fw-medium small">Selected Location</div>
                  <div className="text-muted font-monospace" style={{ fontSize: '0.8rem' }}>
                    {marker ? `${marker.lat.toFixed(6)}, ${marker.lng.toFixed(6)}` : 'No location selected'}
                  </div>
                </div>
              </div>
              {marker && (
                <div className="badge bg-success-subtle text-success border border-success-subtle">
                  <i className="bi bi-check-circle me-1"></i>
                  Ready
                </div>
              )}
            </div>
            <div className="d-flex gap-2">
              <button 
                className="btn btn-sm btn-outline-secondary rounded-pill d-flex align-items-center gap-1" 
                onClick={()=> { setMarker(null); onLocation && onLocation(null) }}
                disabled={!marker}
              >
                <i className="bi bi-arrow-clockwise"></i>
                Reset
              </button>
              <button 
                className="btn btn-sm btn-gradient rounded-pill d-flex align-items-center gap-1" 
                onClick={()=> { setOpen(false) }}
              >
                <i className="bi bi-check-lg"></i>
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

