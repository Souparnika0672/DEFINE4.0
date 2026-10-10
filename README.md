# EmergencyPass — Smart Emergency Private Vehicle Assistance System

> 🌐 **Live Interactive Hackathon Demo:** [https://souparnika0672.github.io/DEFINE4.0/](https://souparnika0672.github.io/DEFINE4.0/)  
> 🏆 **DEFINE 4.0 Hackathon Submission — The World's Realest Hackathon**

An advanced Flask & Leaflet web application that coordinates private vehicles transporting patients during medical emergencies with nearby hospitals, traffic authorities, and road users.

---

## 🚀 Key Features

- 🚨 **One-Tap Emergency SOS Activation** with confirmation modal & high-accuracy GPS capture.
- 🏥 **Instant Nearby Hospital Discovery** utilizing OpenStreetMap Overpass API & curated database fallback with Haversine distance.
- 🗺️ **Live Turn-by-Turn Navigation Map** powered by Leaflet.js & OSRM (Open Source Routing Machine) public routing engine.
- 👨‍⚕️ **Hospital ER Command Portal** with real-time incoming patient queue, Web Audio chime, and 1-click triage bay preparation.
- 👮 **Police Tactical Command Center** with live multi-vehicle city map surveillance and misuse reporting.
- 🚗 **Road Vicinity Driver Alerts** notifying surrounding motorists to yield safely.
- ⚡ **Interactive Demo Simulator** allowing complete animated testing of emergency runs at 1x, 2.5x, and 5x speeds.
- 🛡️ **Role-Based Access Control (RBAC)**, session security, password hashing, and audit logging.

---

## 📋 Pre-Configured Demonstration Accounts

| Role | Email | Password | Access / Function |
| :--- | :--- | :--- | :--- |
| **Driver / Vehicle Owner** | `driver@emergency.org` | `DemoUser123!` | Activate SOS, select hospitals, live navigation |
| **Hospital ER Desk** | `hospital@emergency.org` | `DemoHospital123!` | Incoming emergency triage, ER bay readiness |
| **Police Traffic Command** | `police@emergency.org` | `DemoPolice123!` | Tactical city map, active vehicle tracking |
| **Administrator** | `admin@emergency.org` | `DemoAdmin123!` | User accounts, vehicle verifications, audits |

*Note: The login page includes convenient 1-click demo buttons to automatically populate these credentials.*

---

## 💻 Installation & Execution (Windows PowerShell)

### 1. Open Windows PowerShell in the project directory:
```powershell
cd "D:\Tom\College\DEFINE\DEFINE 2"
```

### 2. Install dependencies:
```powershell
py -m pip install -r requirements.txt
```

### 3. Run the application:
```powershell
py app.py
```
*Or execute the included helper script:*
```powershell
.\run_app.ps1
```

### 4. Access the web application:
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests

Run the full pytest suite:
```powershell
py -m pytest tests -v
```

---

## 📁 Project Structure

```
D:\Tom\College\DEFINE\DEFINE 2├── app.py                      # Application factory & Socket.IO server startup
├── config.py                   # Configuration classes (Dev, Test, Prod)
├── models.py                   # SQLAlchemy models (User, Trip, Hospital, etc.)
├── database.py                 # Database initialization
├── seed_data.py                # Database population with demo users & hospitals
├── auth.py                     # Authentication routes & RBAC decorators
├── services/
│   ├── hospital_service.py     # Overpass API / database fallback hospital discovery
│   ├── routing_service.py      # OSRM routing engine & ETA calculation
│   ├── alert_service.py        # Proximity driver alert & hospital notification dispatch
│   ├── audit_service.py        # Structured audit logger
│   └── demo_simulator.py       # Simulation engine for demo runs
├── routes/
│   ├── main_routes.py          # Landing page, terms, privacy
│   ├── user_routes.py          # Driver dashboard & vehicle management
│   ├── emergency_routes.py     # SOS trigger, hospital selection, live trip
│   ├── hospital_routes.py      # Hospital ER triage dashboard
│   ├── police_routes.py        # Police tactical map & audit view
│   ├── admin_routes.py         # Administrator console
│   ├── incident_routes.py      # Misuse incident reporting & review
│   └── api_routes.py           # REST APIs for AJAX/JSON calls
├── sockets.py                  # Socket.IO WebSocket handlers
├── static/
│   ├── css/style.css           # Custom dark navy & emergency theme design system
│   └── js/                     # Modular JavaScript (Leaflet map, live trip, triage, audio)
├── templates/                  # Jinja2 HTML templates
├── tests/                      # Automated pytest suite
├── SYSTEM_DESCRIPTION.md       # Comprehensive system architecture & manual
├── requirements.txt            # Python dependencies
└── run_app.ps1                 # PowerShell startup script
```
