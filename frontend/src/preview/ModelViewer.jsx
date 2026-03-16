import React, { useEffect } from 'react'

export default function ModelViewer() {
  const qp = new URLSearchParams(window.location.search)
  const modelUrl = qp.get('url')

  useEffect(() => {
    // Load model-viewer web component only once.
    const existing = document.querySelector('script[data-model-viewer="1"]')
    if (existing) return

    const script = document.createElement('script')
    script.type = 'module'
    script.src = 'https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js'
    script.setAttribute('data-model-viewer', '1')
    document.head.appendChild(script)
  }, [])

  if (!modelUrl) {
    return (
      <div className="container py-4">
        <h4>3D Model Viewer</h4>
        <div className="alert alert-secondary mb-0">
          No model URL provided. Generate a model from the main page first.
        </div>
      </div>
    )
  }

  return (
    <div className="container py-4">
      <h4>3D Model Viewer</h4>
      <div className="card shadow-sm p-3">
        <model-viewer
          src={modelUrl}
          alt="Generated solar rooftop 3D model"
          camera-controls
          auto-rotate
          ar={false}
          style={{ width: '100%', height: '75vh', background: '#111' }}
        />
      </div>
      <div className="small text-muted mt-2">Model source: {modelUrl}</div>
    </div>
  )
}
