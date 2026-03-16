import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App'
import Preview from './preview/Preview'
import ModelViewer from './preview/ModelViewer'
import './styles.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'leaflet/dist/leaflet.css'

// fix leaflet icon paths for Vite
import L from 'leaflet'
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
})

// ensure saved background image opacity is correctly applied
const savedBg = localStorage.getItem('bgImage')
if (savedBg) {
  document.documentElement.style.setProperty('--page-bg-image', `url('${savedBg}')`)
  document.documentElement.style.setProperty('--page-bg-opacity', '1')
}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App/>} />
        <Route path="/preview" element={<Preview/>} />
        <Route path="/model" element={<ModelViewer/>} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
)
