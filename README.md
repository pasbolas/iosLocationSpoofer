# iPhone Location Simulator (Windows-First PWA)

A high-performance, Windows-first local iPhone location simulation and GPS spoofing application with a modern, glassmorphic Svelte PWA frontend and Python FastAPI backend, communicating with Apple developer services via `pymobiledevice3`.

---

## Features

- **PWA Frontend**:
  - Installable as a native-feeling standalone Windows desktop app (via Edge or Chrome).
  - Built with Svelte and responsive desktop-first layout.
  - Interactive **Leaflet** map with CartoDB dark tiles.
  - Floating live address and landmark search powered by OpenStreetMap Nominatim.
  - Draggable pinpoint marker with real-time coordinate readouts.
  - Quick-teleport **Favorites & Presets** saved in browser `localStorage` (Dublin, Times Square, Eiffel Tower, Tokyo, Big Ben, etc.) with custom bookmarking.
  - Visual status pill: **Real Location** vs pulsing emerald **SIMULATED LOCATION ACTIVE**.
  - Guided glassmorphic modals for device locked, pairing required, and Developer Mode setup.

- **FastAPI Backend**:
  - Bound strictly to `127.0.0.1:8000` (zero exposure to LAN or Internet).
  - Device discovery and lockdown telemetry via `pymobiledevice3`.
  - Seamless cross-iOS compatibility:
    - **iOS 17 & iOS 18**: Apple CoreDevice RemoteXPC/RSD in-process userspace tunnel (`PreferredRsdTunnel`) and DVT `LocationSimulation`.
    - **iOS 14, 15, & 16**: Apple classic lockdown developer service (`DtSimulateLocation`).
  - Automatic clean GPS restore on stop or application shutdown.
  - Zero cloud dependencies, zero analytics, strictly local and private.

- **Supported Hardware**:
  - **iPhone 12, 12 mini, 12 Pro, 12 Pro Max** (and all models from iPhone X to iPhone 16 Pro Max).

---

## Quickstart

### 1. Prerequisites
Ensure you have installed:
1. **Apple Mobile Device Service** (provided by **iTunes** or **Apple Devices** from the Microsoft Store).
2. **Python 3.11 or 3.12** (already installed in `.venv`).

*(See [SETUP.md](SETUP.md) for full Windows 11 prerequisite instructions).*

### 2. Run the Application
Simply double-click:
```
run.bat
```
Or in PowerShell:
```powershell
.\run.ps1
```
The browser will automatically open to `http://127.0.0.1:8000`.

---

## REST API Reference (Localhost Only)

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/status` | `GET` | Returns system connectivity (`usbmuxd`), connected devices, and active simulation status. |
| `/api/devices` | `GET` | Returns list of detected USB iOS devices with model, iOS version, pairing, and Developer Mode state. |
| `/api/location` | `POST` | Sets simulated GPS coordinates: `{"udid": "...", "latitude": 53.3498, "longitude": -6.2603, "location_name": "Dublin"}`. |
| `/api/location` | `DELETE` | Stops location simulation and restores real device GPS. |
| `/api/geocode?q=...` | `GET` | Proxies OpenStreetMap Nominatim search for locations and addresses. |

---

## Project Structure

```
├── backend/
│   ├── api/
│   │   └── routes.py           # REST endpoints
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   ├── services/
│   │   ├── device_service.py   # USB discovery and lockdown info
│   │   ├── location_service.py # Simulation controller across iOS versions
│   │   └── tunnel_service.py   # RSD userspace tunnel manager (iOS 17+)
│   └── main.py                 # FastAPI application and SPA static server
├── frontend/
│   ├── dist/                   # Built production PWA bundle
│   ├── src/
│   │   ├── components/
│   │   │   ├── DeviceCard.svelte
│   │   │   ├── ErrorModal.svelte
│   │   │   ├── FavoritesCard.svelte
│   │   │   ├── Header.svelte
│   │   │   ├── Map.svelte
│   │   │   └── SimulationCard.svelte
│   │   ├── lib/
│   │   │   ├── api.js
│   │   │   └── stores.js
│   │   ├── App.svelte
│   │   ├── index.css           # Glassmorphism dark design system
│   │   └── main.js
│   ├── public/
│   │   ├── icon.svg
│   │   ├── manifest.json       # PWA Web App Manifest
│   │   └── sw.js               # PWA Service Worker
│   ├── package.json
│   └── vite.config.js
├── poc.py                      # Standalone Phase 1 proof-of-concept CLI
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows 1-click launcher
├── run.ps1                     # PowerShell 1-click launcher
├── SETUP.md                    # Windows 11 setup guide
└── README.md
```
