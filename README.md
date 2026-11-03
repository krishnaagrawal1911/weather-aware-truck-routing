# Weather-Aware Truck Routing Web Application

A full-stack **React + Django** web application engineered to help commercial truck drivers and dispatchers select the safest, most efficient driving routes based on high-resolution weather forecasts, dynamic ETA checkpoint tracking, and gross vehicle load weight.

Built according to the Spotter Full-Stack Developer specification.

---

## 🌟 Key Features

1. **3 Route Options Generation**:
   - Queries OSRM (Open Source Routing Machine) to retrieve distinct driving route corridors between any origin and destination.
   - Guaranteed multi-corridor route diversity (e.g. Northern, Interstate Direct, and Southern alternatives).
2. **Dynamic Weather Sampling along Route Checkpoints**:
   - Samples checkpoints every **10 / 25 / 50 miles** along each route.
   - Computes checkpoint-specific **ETAs** ($\text{Departure} + \text{Trip Duration up to checkpoint}$).
   - Queries high-resolution hourly weather forecasts (Open-Meteo API) matched to the truck's exact arrival hour.
3. **Rigorous Multi-Hazard Risk & Load Weight Engine**:
   - Classifies Wind Speed (mph), Rain Rate (in/hr), and Snowfall (in/hr) into Low, Moderate, High, Severe, and No Travel.
   - Incorporates physical vehicle rollover / stability rules based on gross load weight.
4. **Hierarchical Route Recommendation**:
   - Evaluates routes strictly against four prioritized safety rules:
     1. Fewest Severe miles (with mandatory No Travel closure avoidance)
     2. Fewest High risk miles
     3. Lowest average weather hazard score
     4. Shortest travel times
5. **Interactive Leaflet Map & 0–48 Hour Forecast Slider**:
   - Visualizes all 3 routes with color-coded risk segments.
   - Interactive checkpoint pins with popups showing ETA, wind, rain, snow, and load rule triggers.
   - **Corridor Heatmap with 0–48 Hour Slider**: Scrub through the next 48 hours to visually watch weather systems evolve along the entire corridor.
   - Supports switching heatmap views: **Composite Risk**, **Wind (mph)**, **Rain (in/hr)**, and **Snow (in/hr)**.

---

## 📊 Risk & Load Weight Rules

### Condition Thresholds

| Condition | Low | Moderate | High | Severe | No Travel |
|---|---|---|---|---|---|
| **Wind** | `< 25 mph` | `25–34 mph` | `35–44 mph` | `45–54 mph` | `≥ 55 mph` |
| **Rain** | `< 0.10 in/hr` | `0.10–0.25 in/hr` | `0.25–0.50 in/hr` | `0.50–1.00 in/hr` | `> 1.00 in/hr` |
| **Snow** | `< 0.5 in/hr` | `0.5–1.0 in/hr` | `1.0–2.0 in/hr` | `2.0–3.0 in/hr` | `> 3.0 in/hr` |

### Load Rules (Vehicle Rollover & Stability)

- **$\ge 55\text{ mph Wind}$**: Immediate **No Travel** for any load weight.
- **$45\text{--}54\text{ mph Wind} + >30,000\text{ lb Load}$**: Escalates to **No Travel** (high center of gravity rollover hazard).
- **$35\text{--}44\text{ mph Wind} + >40,000\text{ lb Load}$**: Upgrades from High to **Severe**.

### Route Recommendation Hierarchy

When evaluating candidate routes:
1. **Prefer Fewest Severe miles**
2. **Prefer Fewest High miles**
3. **Prefer Lowest average risk**
4. **Prefer Shortest travel times**

---

## 🛠️ Tech Stack & Architecture

- **Backend**:
  - Python 3.11+ / Django 5+ / Django REST Framework
  - `routing_app.services.risk_engine`: Pure unit-tested domain logic for hazard rules.
  - `routing_app.services.routing_service`: OSRM routing client with polyline interpolation.
  - `routing_app.services.weather_service`: Open-Meteo multi-coordinate hourly forecast client.
  - `routing_app.services.recommendation_engine`: Deterministic route ranking logic.
  - `routing_app.services.heatmap_service`: 48-hour spatial weather corridor generator.
- **Frontend**:
  - React 19 + Vite + Tailwind CSS
  - Leaflet & React-Leaflet
  - Lucide React Icons
- **Third-Party APIs** (Zero API keys required):
  - **OSRM**: Driving polyline routing
  - **Open-Meteo**: High-resolution hourly weather forecasts (wind speed in mph, precipitation in inches)
  - **OpenStreetMap Nominatim**: Geocoding and address resolution

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) Docker & Docker Compose

---

### Local Development Setup

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py test routing_app   # Run comprehensive unit tests
python manage.py runserver 0.0.0.0:8000
```
Backend API will be live at `http://127.0.0.1:8000/`.

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will be live at `http://localhost:5173/`.

---

### 🐳 Run with Docker Compose

Run the entire application in isolated containers with one command:
```bash
docker compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

---

## 🧪 Automated Test Suite

Run backend unit tests covering all risk thresholds, load rules, and recommendation edge cases:
```bash
cd backend
python manage.py test routing_app
```
**Test Coverage Includes:**
- Wind risk classification under standard and heavy loads.
- Load weight triggers ($>30,000\text{ lb}$ and $>40,000\text{ lb}$ modifiers).
- Rain and snow boundary thresholds.
- Priority 1 (Fewest Severe miles), Priority 2 (Fewest High miles), Priority 3 (Lowest Average Risk), Priority 4 (Shortest Duration).
- End-to-end API integration tests.

---

## 📹 5–10 Min Loom Walkthrough Outline

Use this recommended structure when recording your submission video:

1. **Introduction (1 min)**:
   - Brief problem overview: Why weather and truck load weight are critical safety factors in commercial dispatching.
   - Project architecture: React (Vite) + Django REST Framework + Open-Meteo + OSRM.
2. **Core Workflow Demo (3 mins)**:
   - Entering Origin & Destination (e.g. Chicago, IL to Denver, CO).
   - Selecting Departure Time, Load Weight (e.g., 35,000 lb vs 45,000 lb), and Sampling Interval (10, 25, 50 miles).
   - Visual inspection of the 3 route options generated.
   - Inspecting the **Recommended Route** badge and the explanation of why it was chosen.
3. **Deep Dive: Risk & Load Rules (2 mins)**:
   - Clicking on checkpoints along the active route to inspect popup details: ETA, wind speed, precipitation, snow, and load weight triggers.
   - Demonstrating how changing load weight from 25,000 lb to 42,000 lb escalates a 40 mph wind segment from High to Severe.
4. **Corridor Heatmap & 48h Slider (2 mins)**:
   - Demonstrating the 0–48 hour timeline slider.
   - Playing the animation to visualize weather systems advancing across the corridor over time.
   - Switching between Composite Risk, Wind, Rain, and Snow views.
5. **Code Quality & Automated Tests (1 min)**:
   - Showing `python manage.py test routing_app` passing 100% of test cases.
   - Clean separation of concerns (`risk_engine`, `routing_service`, `weather_service`, `recommendation_engine`).
