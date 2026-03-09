Solar Premium — React + Vite

This folder contains a React + Vite frontend scaffold with Leaflet map integration and a colourful premium UI.

Getting started (PowerShell):

1) Change into the project folder:

```powershell
cd C:\Users\abels\Documents\ghacks\react-app
```

2) Install dependencies:

```powershell
npm install
```

3) Start the dev server:

```powershell
npm run dev
```

4) Open the URL printed by Vite (usually http://localhost:5173)

Notes:
- The frontend expects the following backend endpoints:
  - POST /api/location  -> receives { lat, lon }
  - POST /api/generate-solar -> receives form + location, returns JSON (optionally { fileUrl })
  - POST /api/generate-invoice -> receives form + location, returns JSON { fileUrl } or a PDF blob
- Invoice previews open at /preview?url=...
- The project uses Bootstrap for quick styling. You can replace with Tailwind or another design system if preferred.
