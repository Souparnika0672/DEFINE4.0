# EmergencyPass — Smart Emergency Private Vehicle Assistance System
## Comprehensive System Architecture, Design Specification & Technical Documentation

---

### 1. Executive Summary & Objective

**EmergencyPass** is a mission-critical web application and real-time coordination platform designed to bridge the severe informational and operational gaps that occur when private vehicles are used to transport patients during acute medical emergencies.

During life-threatening emergencies (e.g., cardiac arrests, strokes, acute respiratory failure, high-impact road trauma), ambulances may not always be immediately accessible due to transit delays or geographic constraints. In such circumstances, relatives or bystanders frequently utilize private automobiles. However, private emergency transits encounter severe challenges:
1. **Uninformed Hospital Selection:** Drivers frequently head to distant or inappropriate medical facilities (e.g. eye clinics or outpatient dispensaries) lacking specialized cardiac, trauma, or ICU capabilities.
2. **Unprepared Hospital Emergency Departments:** Receiving hospitals have zero prior notice regarding the incoming patient's status, condition, or estimated time of arrival (ETA), delaying resuscitation setup.
3. **Traffic Congestion & Road Danger:** Ordinary motorists in the vehicle's path are unaware of the emergency transit, creating bottlenecks and hazardous overtaking scenarios.
4. **Law Enforcement Blind Spots:** Traffic authorities cannot differentiate genuine emergency vehicles from reckless driving or misuse.

**EmergencyPass resolves these challenges** by providing an end-to-end digital corridor:
- **Clinical Emergency Specialty Discovery:** Rapidly identifies nearby verified hospitals equipped for the exact medical emergency (Cardiac, Trauma, Stroke, Maternity, Pediatric, General Critical), strictly excluding non-emergency clinics (eye, dental, cosmetic).
- **Pre-Arrival Hospital ER Triage:** Dispatches real-time telemetry to hospital triage desks to ready trauma bays, cath labs, and surgical teams before the patient arrives.
- **Vicinity Driver Alerts:** In-app safety broadcasts inform nearby road users in the vehicle's transit corridor to stay alert and yield safely.
- **Tactical Police Traffic Clearance & Green-Wave:** Grants traffic police situational awareness to clear signals and deploy traffic interceptors while enforcing auditable misuse review workflows.

---

### 2. System Architecture & High-Level Design

The system is constructed using a robust, modular 3-tier architecture:

```
+-----------------------------------------------------------------------------------+
|                                PRESENTATION TIER                                  |
|   Bootstrap 5 + Custom Modern Theme | Leaflet.js Interactive Maps | Socket.IO     |
|   +-------------------+  +-------------------+  +-------------------------------+ |
|   |  Driver Dashboard |  |  Hospital Portal  |  | Police Command & Admin Center | |
|   +-------------------+  +-------------------+  +-------------------------------+ |
+-----------------------------------------------------------------------------------+
                                         │▲  ▼│ (REST APIs & WebSockets)
                                         ▼│  │▲
+-----------------------------------------------------------------------------------+
|                                APPLICATION TIER (Flask)                           |
|   +------------------+  +-------------------+  +------------------------------+   |
|   |   Auth & RBAC    |  |  Emergency Engine |  |    Vicinity Alert Service    |   |
|   +------------------+  +-------------------+  +------------------------------+   |
|   +------------------+  +-------------------+  +------------------------------+   |
|   | Hospital Triage  |  |  OSRM Routing     |  |    Audit & Incident Review   |   |
|   +------------------+  +-------------------+  +------------------------------+   |
+-----------------------------------------------------------------------------------+
                                         │▲  ▼│
                                         ▼│  │▲
+-----------------------------------------------------------------------------------+
|                         DATA & EXTERNAL SERVICES TIER                             |
|   +-----------------------+ +-------------------------+ +-----------------------+ |
|   | SQLite Database       | | OpenStreetMap Overpass  | | OSRM Road Routing API | |
|   | (emergency_pass.db)   | | (Zero-Key Mirrors)      | | (Road Geometry & ETA) | |
|   +-----------------------+ +-------------------------+ +-----------------------+ |
+-----------------------------------------------------------------------------------+
```

---

### 3. Core Modules & Medical Triage Engine

#### A. Clinical Emergency Triage & Hospital Filtering Engine (`services/hospital_service.py`)
- **Non-Emergency Blacklist Filter:** Automatically discards non-acute facilities such as eye clinics, dental clinics, dermatology, cosmetology, ayurveda, homeopathy, and physiotherapy centers.
- **Specialty Matching:**
  - **Cardiac Arrest / Chest Pain:** Matches 24/7 Interventional Cardiology, Cath Labs, and Level 1 Comprehensive ERs with CCU.
  - **Severe Trauma / Road Accident:** Matches Level 1 & Level 2 Trauma Centers with 24/7 emergency surgical suites and blood banks.
  - **Acute Stroke / Neurological:** Matches Comprehensive Stroke Centers with 24/7 neuro-intervention and CT/MRI thrombolysis.
  - **Obstetric / Maternity:** Matches 24/7 Labor Suites, High-Risk Delivery ERs, and Neonatal ICUs (NICU).
  - **Pediatric Emergencies:** Matches Pediatric ICUs (PICU) and Children's Hospitals.
  - **General Acute Emergencies:** Matches 24/7 Multi-Specialty ERs with available ICU beds.

#### B. Watermark-Free Leaflet Map Integration (`static/js/emergency_map.js`)
- Standardized on official zero-key OpenStreetMap tiles (`https://tile.openstreetmap.org/{z}/{x}/{y}.png`) with 100% clean rendering and zero watermarks.
- Custom dynamic SVG beacon markers tailored to emergency type with glowing pulses.
- Interactive road route preview and live real-time vehicle GPS tracking.

#### C. Real-Time Telemetry & Alert Dispatch (`services/alert_service.py`)
- Broadcasts multi-party notifications upon trip activation:
  - Hospital ER desk receives pre-arrival notification with patient severity and expected ETA.
  - Police traffic command receives corridor location to activate green-waves.
  - Nearby drivers receive safety proximity broadcasts.

---

### 4. Running the Application Locally

1. **Start Server:**
   Run `run_localhost.bat` or `py app.py`.
2. **Access Web App:**
   Open [http://localhost:5000](http://localhost:5000) in any browser.
3. **Demo Credentials:**
   - **Driver:** `driver@emergency.org` / `DemoUser123!`
   - **Hospital ER Desk:** `hospital@emergency.org` / `DemoHospital123!`
   - **Police Command:** `police@emergency.org` / `DemoPolice123!`
   - **Administrator:** `admin@emergency.org` / `DemoAdmin123!`
