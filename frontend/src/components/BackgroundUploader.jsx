import React, { useEffect } from 'react'

export default function BackgroundUploader(){
  useEffect(()=>{
    // on mount, load saved bg from localStorage if present
    const saved = localStorage.getItem('bgImage')
    if (saved) document.documentElement.style.setProperty('--page-bg-image', `url('${saved}')`)
  }, [])

  const handleFile = (e)=>{
    const f = e.target.files && e.target.files[0]
    if (!f) return
    const reader = new FileReader()
    reader.onload = () => {
      const data = reader.result
      // set CSS var and save
      document.documentElement.style.setProperty('--page-bg-image', `url('${data}')`)
      try{ localStorage.setItem('bgImage', data) } catch(e){ console.warn('Cannot save bg to localStorage', e) }
    }
    reader.readAsDataURL(f)
  }

  const clearBg = ()=>{
    document.documentElement.style.setProperty('--page-bg-image', 'none')
    localStorage.removeItem('bgImage')
  }

  return (
    <div className="bg-uploader d-flex align-items-center gap-2">
      <label className="btn btn-sm btn-light rounded-pill mb-0" title="Upload background">
        <input type="file" accept="image/*" onChange={handleFile} style={{display:'none'}} />
        <i className="bi bi-image" />
      </label>
      <button className="btn btn-sm btn-outline-light rounded-pill" onClick={clearBg} title="Clear background">Clear</button>
    </div>
  )
}
