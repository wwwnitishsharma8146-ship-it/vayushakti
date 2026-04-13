# 🌾 KrishiShakti Data Flow - Complete Explanation

## Where Does All The Data Come From?

This document explains the complete data architecture of the KrishiShakti system - from sensor data generation to display on your screen.

---

## 📊 System Architecture Overview

```
┌─────────────────┐
│  DATA SOURCES   │
│  (2 Options)    │
└────────┬────────┘
         │
         ├─── Option 1: simulator.py (Testing/Demo)
         │    └─> Generates random realistic sensor data
         │
         └─── Option 2: arduino_bridge.py (Real Hardware)
              └─> Reads from actual Arduino sensors
         │
         ▼
┌─────────────────────────────────────────┐
│  FLASK SERVER (app.py)                  │
│  - Receives sensor data via HTTP POST   │
│  - Stores in global sensor_data dict    │
│  - Saves to history.json file           │
│  - Broadcasts via WebSocket             │
│  - Processes chatbot queries            │
│  - Analyzes agriculture AI images       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  FRONTEND (HTML/CSS/JS)                 │
│  - Fetches data via /api/sensors        │
│  - Receives real-time updates via WS    │
│  - Displays in dashboard                │
│  - Shows in chatbot responses           │
│  - Uses in agriculture AI analysis      │
└─────────────────────────────────────────┘
```

---

## 🔄 Detailed Data Flow

### 1. DATA GENERATION (Source Layer)

#### Option A: Simulator (simulator.py) - For Testing
**Location:** `simulator.py`
**Purpose:** Generate realistic random sensor data for testing without hardware

**What it does:**
- Generates random values every 6-8 seconds:
  - `mq135`: 50-200 ppm (Air Quality)
  - `temperature`: 25-28°C (Optimal range)
  - `humidity`: 40-80%
  - `pm25`: 10-50 µg/m³ (Particulate Matter)
  - `pm10`: 20-80 µg/m³
  - `fc28`: 20-30% (Soil Moisture - LOW, needs watering!)
  - `tds`: 100-500 ppm (Water Quality)

- Detects location using IP geolocation (ipapi.co):
  - City name
  - Country name
  - Latitude/Longitude

**How to run:**
```bash
python simulator.py
# OR
./run_simulator.sh
```

**Data format sent to server:**
```json
{
  "mq135": 125.43,
  "temperature": 27.8,
  "humidity": 65.2,
  "pm25": 32.1,
  "pm10": 45.6,
  "fc28": 58.3,
  "tds": 287,
  "location": {
    "city": "Mumbai",
    "country": "India",
    "latitude": 19.0760,
    "longitude": 72.8777
  }
}
```

#### Option B: Arduino Bridge (arduino_bridge.py) - For Real Hardware
**Location:** `arduino_bridge.py`
**Purpose:** Read real sensor data from Arduino hardware

**What it does:**
- Connects to Arduino via serial port (USB)
- Reads JSON data from Arduino sensors
- Adds location information (same as simulator)
- Forwards to Flask server

**Arduino sensors:**
- MQ-135: Air quality sensor
- PMS5003: Particulate matter sensor
- DHT22: Temperature & humidity sensor
- FC-28: Soil moisture sensor
- TDS sensor: Water quality sensor

**How to run:**
```bash
python arduino_bridge.py
```

---

### 2. DATA RECEPTION (Server Layer)

#### Flask Server (app.py)
**Location:** `app.py`
**Port:** 5001

**Endpoint:** `POST /api/sensors`
**What happens when data arrives:**

1. **Receives POST request** with sensor data
2. **Stores in global variable** `sensor_data`:
   ```python
   sensor_data = {
       'mq135': {'value': 125.43, 'unit': 'ppm', 'name': 'Air Quality (MQ-135)'},
       'pms5003': {'pm25': 32.1, 'pm10': 45.6, 'unit': 'µg/m³', 'name': 'Particulate Matter'},
       'dht22': {'temperature': 27.8, 'humidity': 65.2, 'name': 'Temperature & Humidity'},
       'fc28': {'value': 58.3, 'unit': '%', 'name': 'Water Tank Level'},
       'tds': {'value': 287, 'unit': 'ppm', 'name': 'Water Quality'},
       'location': {'city': 'Mumbai', 'country': 'India'},
       'timestamp': '2026-02-19T14:30:45.123456'
   }
   ```

3. **Saves to history file** `data/history.json`:
   - Keeps last 1000 readings
   - Used for historical charts and analysis

4. **Broadcasts via WebSocket**:
   - Sends to all connected clients
   - Real-time updates without page refresh

5. **Returns success response**:
   ```json
   {"success": true, "data": {...}}
   ```

---

### 3. DATA CONSUMPTION (Frontend Layer)

#### Dashboard (public/dashboard.html + dashboard.js)

**How it gets data:**

1. **Initial Load** - HTTP GET request:
   ```javascript
   fetch('/api/sensors')
     .then(response => response.json())
     .then(data => updateDashboard(data))
   ```

2. **Real-time Updates** - WebSocket connection:
   ```javascript
   ws = new WebSocket('ws://localhost:5001');
   ws.onmessage = (event) => {
     const data = JSON.parse(event.data);
     updateDashboard(data);
   }
   ```

3. **Historical Data** - HTTP GET request:
   ```javascript
   fetch('/api/history')
     .then(response => response.json())
     .then(data => updateHistoryTable(data))
   ```

**What it displays:**
- Current sensor readings with progress bars
- Status indicators (Good/Moderate/Poor)
- Location information
- Historical data table
- Quick stats cards
- System uptime and data points

---

### 4. CHATBOT DATA FLOW

#### Chatbot (public/chatbot.html + chatbot.js)

**How it works:**

1. **User sends message** in chatbot interface

2. **Frontend sends request** to Flask:
   ```javascript
   fetch('/api/chatbot/message', {
     method: 'POST',
     body: JSON.stringify({
       message: "What is the current temperature?",
       sensorData: currentSensorData,  // ← Uses live sensor data!
       history: conversationHistory
     })
   })
   ```

3. **Flask processes request** (app.py):
   - Detects language (English/Hindi/Punjabi)
   - Detects topic from keywords
   - Uses LIVE sensor data in response
   - Generates comprehensive response (2000-5000 characters)

4. **Response includes live data**:
   ```
   📊 Current Sensor Readings:
   🌡️ Temperature: 27.8°C - Optimal
   💧 Humidity: 65.2% - Good
   🌿 Air Quality: 125 ppm - Good
   💦 Soil Moisture: 58.3% - Perfect
   🚰 Water Quality: 287 ppm TDS - Pure
   ```

**Data source:** Same `sensor_data` global variable updated by simulator/Arduino!

---

### 5. AGRICULTURE AI DATA FLOW

#### Agriculture AI (public/agriculture.html + agriculture.js)

**How it works:**

1. **User uploads crop image**

2. **Frontend sends to Flask**:
   ```javascript
   fetch('/api/agriculture/analyze', {
     method: 'POST',
     body: formData  // Contains image file
   })
   ```

3. **Flask analyzes image** (app.py):
   - Simulates AI disease detection
   - Generates random disease profile:
     - Healthy Crop (40% chance)
     - Early Blight (30% chance)
     - Nutrient Deficiency (20% chance)
     - Pest Infestation (10% chance)

4. **Returns comprehensive analysis**:
   - 14 detailed sections
   - Treatment schedule (6-step plan)
   - Natural remedies (5+ recipes)
   - Chemical options (4-5 with dosages)
   - Cost estimates (₹200-1200)
   - Recovery timeline

**Note:** Currently uses simulated AI. Can be enhanced with real ML models (TensorFlow, PyTorch).

---

### 6. SMART ADVISORY DATA FLOW

#### Smart Advisory System (app.py)

**Endpoints:**
- `/api/agriculture/irrigation-advice` - Water recommendations
- `/api/agriculture/fertilizer-advice` - Fertilizer suggestions
- `/api/agriculture/pest-advice` - Pest control guidance
- `/api/agriculture/weather-advice` - Weather-based tips

**How it works:**

1. **Frontend requests advice** with current sensor data:
   ```javascript
   fetch('/api/agriculture/irrigation-advice', {
     method: 'POST',
     body: JSON.stringify({
       temperature: 27.8,
       humidity: 65.2,
       soilMoisture: 58.3,
       location: {city: 'Mumbai', country: 'India'}
     })
   })
   ```

2. **Flask calculates recommendations**:
   - Uses live sensor data
   - Calculates evapotranspiration (ET) rate
   - Considers environmental factors
   - Generates specific advice

3. **Returns AI-powered insights**:
   - Exact water amounts (liters per sq meter)
   - Timing recommendations
   - Frequency calculations
   - Cost estimates

**Data source:** Live sensor data from simulator/Arduino!

---

## 📁 Data Storage

### 1. In-Memory Storage (RAM)
**Location:** `sensor_data` global variable in app.py
**Lifetime:** While Flask server is running
**Purpose:** Fast access for real-time display

### 2. File Storage (Disk)
**Location:** `data/history.json`
**Lifetime:** Permanent (until deleted)
**Purpose:** Historical analysis, charts, trends
**Size limit:** Last 1000 readings

### 3. Browser Storage (Client)
**Location:** localStorage in browser
**Data stored:**
- User authentication (`krishishakti_user`)
- Location cache (24 hours)
- Conversation history

---

## 🔍 Data Flow Summary

### Real-time Flow (Every 6-8 seconds):
```
Simulator/Arduino → HTTP POST → Flask Server → WebSocket → Dashboard
                                      ↓
                                 history.json
```

### Chatbot Flow:
```
User Message → Frontend → Flask → Detect Language → Detect Topic
                                        ↓
                                  Use Live Sensor Data
                                        ↓
                                Generate Response (2000-5000 chars)
                                        ↓
                                  Return to Frontend
```

### Agriculture AI Flow:
```
User Image → Frontend → Flask → Simulate AI Analysis
                                      ↓
                              Generate Disease Profile
                                      ↓
                              14 Detailed Sections
                                      ↓
                              Return to Frontend
```

---

## 🚀 How to Start the System

### Step 1: Start Flask Server
```bash
python app.py
# Server runs on http://localhost:5001
```

### Step 2: Start Data Source (Choose One)

**Option A: Simulator (Recommended for testing)**
```bash
python simulator.py
# Sends data every 2 seconds
```

**Option B: Arduino Bridge (For real hardware)**
```bash
python arduino_bridge.py
# Reads from Arduino via USB
```

### Step 3: Open Dashboard
```
http://localhost:5001/dashboard.html
```

---

## 🎯 Key Points

1. **All sensor data** comes from either:
   - `simulator.py` (random realistic values)
   - `arduino_bridge.py` (real Arduino sensors)

2. **Flask server** (`app.py`) is the central hub:
   - Receives data via HTTP POST
   - Stores in memory and file
   - Broadcasts via WebSocket
   - Serves to frontend

3. **Frontend** gets data via:
   - HTTP GET requests (`/api/sensors`)
   - WebSocket real-time updates
   - Historical data (`/api/history`)

4. **Chatbot** uses live sensor data:
   - Same data shown in dashboard
   - Integrated into responses
   - Updated every 2 seconds

5. **Agriculture AI** uses:
   - Simulated disease detection
   - Can be enhanced with real ML models

---

## 🔧 Troubleshooting

### "All values showing 0"
**Problem:** Simulator/Arduino not running
**Solution:** Start simulator: `python simulator.py`

### "No data available"
**Problem:** Flask server not receiving data
**Solution:** 
1. Check Flask is running: `http://localhost:5001`
2. Check simulator is running and sending data
3. Check console for errors

### "Location not showing"
**Problem:** IP geolocation API blocked
**Solution:** 
1. Check internet connection
2. Try browser geolocation (dashboard.js)
3. Manually set location in code

---

## 📊 Data Update Frequency

| Component | Update Frequency | Method |
|-----------|-----------------|--------|
| Simulator | Every 6-8 seconds | HTTP POST |
| Arduino | Every 5 seconds | Serial → HTTP POST |
| Dashboard | Real-time | WebSocket |
| History Table | Every 10 seconds | HTTP GET |
| Chatbot | On demand | HTTP POST |
| Agriculture AI | On demand | HTTP POST |

---

## 🎓 Summary

**The complete data journey:**

1. **Simulator/Arduino** generates sensor values
2. **Sends to Flask** via HTTP POST to `/api/sensors`
3. **Flask stores** in memory (`sensor_data`) and file (`history.json`)
4. **Flask broadcasts** via WebSocket to all connected clients
5. **Dashboard receives** and displays in real-time
6. **Chatbot uses** same data in responses
7. **Agriculture AI** provides analysis based on conditions

**Everything is connected!** The same sensor data flows through the entire system - from generation to display to chatbot to AI analysis.

---

## 📝 Files Involved

| File | Purpose | Data Flow |
|------|---------|-----------|
| `simulator.py` | Generate test data | SOURCE → Flask |
| `arduino_bridge.py` | Read Arduino sensors | SOURCE → Flask |
| `app.py` | Central server | Receive → Store → Broadcast |
| `data/history.json` | Historical storage | Flask → File |
| `public/dashboard.js` | Display data | Flask → Browser |
| `public/chatbot.js` | Chat interface | Flask ↔ Browser |
| `public/agriculture.js` | AI analysis | Flask ↔ Browser |

---

**Created:** February 19, 2026
**Project:** KrishiShakti (कृषि शक्ति)
**Version:** 1.0
