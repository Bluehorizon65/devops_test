import React from 'react'

export default function Preview(){
  const qp = new URLSearchParams(window.location.search)
  const url = qp.get('url')
  return (
    <div className="container py-4">
      <h4>Invoice Preview</h4>
      {url ? (
        <iframe src={url} style={{width:'100%', height:'80vh', border:0}} title="Invoice preview" />
      ) : (
        <div className="alert alert-secondary">No preview URL provided. Generate an invoice from the main page to preview it here.</div>
      )}
    </div>
  )
}
