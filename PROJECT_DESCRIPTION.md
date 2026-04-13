# PollutionWatch — Smart Pollution Monitoring System
### IoT + AI + Java + Flask | Real-Time Environmental Dashboard

---

## 1. Project Overview

PollutionWatch is a real-time pollution and air quality monitoring system built using IoT sensors, a Java-based data simulator (Eclipse), a Python Flask web server, and an AI-powered chatbot. The system collects environmental sensor data, displays it on a live web dashboard, and provides intelligent pollution analysis and health risk advice in English, Hindi, and Punjabi.

The project was originally built as a Smart Agriculture system (KrishiShakti) and has been fully rethemed and repurposed into a Pollution Monitoring System.

---

## 2. Problem Statement

Air pollution is one of the leading environmental health risks globally. Most people have no real-time visibility into the air quality around them, the health risks it poses, or what actions to take. This project solves that by:

- Continuously monitoring air quality, particulate matter, temperature, humidity, and water quality
- Providing an AI chatbot that answers pollution-related questions in multiple languages
- Giving actionable health and safety recommendations based on live sensor data
- Simulating real sensor hardware using Java (Eclipse) for development and testing

---

## 3. System Architecture

```
[ Java Simulator (Eclipse) ]
        |
        | HTTP POST (JSON) every 1 second
        v
[ Flask Server — app.py (Python) ]
        |
        |--- REST API (/api/sensors, /api/chatbot/message, etc.)
        |--- WebSocket (Socket.IO) — live push to browser
        v
[ Web Dashboard (HTML/CSS/JS) ]
        |
        |--- Dashboard (live sensor cards)
        |--- Pollution AI page (AQI analysis, health risks, sources)
        |--- AI Chatbot (multi-language pollution assistant)
        |--- Analytics, History, Alerts, Settings
```

---

## 4. Components

### 4.1 Java Sensor Simulator — `project.java` (Eclipse)

- Written in Java, runs in Eclipse as a standard Java Application
- Generates random realistic sensor values every 1 second
- Sends data to the Flask server via HTTP POST as a JSON payload
- No external libraries needed — uses only `java.net.HttpURLConnection`

Sensors simulated:

| Sensor | Parameter | Range |
|--------|-----------|-------|
| MQ-135 | Air Quality (gas/VOC) | 50–500 ppm |
| PMS5003 | PM2.5 (fine particles) | 5–250 µg/m³ |
| PMS5003 | PM10 (coarse particles) | PM2.5 + 5–80 µg/m³ |
| DHT22 | Temperature | 15–45 °C |
| DHT22 | Humidity | 20–95 % |
| FC-28 | Water Tank Level | 0–100 % |
| TDS | Water Quality | 100–800 ppm |

JSON format sent to Flask:
```json
{
  "temperature": 28.4,
  "humidity": 62.1,
  "mq135": 187,
  "pm25": 43,
  "pm10": 91,
  "fc28": 55,
  "tds": 320
}
```

### 4.2 Flask Backend — `app.py` (Python)

- Built with Flask + Flask-SocketIO + Flask-CORS
- Receives sensor data from Java via `POST /api/sensors`
- Stores data in `data/history.json`
- Broadcasts live updates to all connected browsers via WebSocket
- Hosts the entire frontend (HTML/CSS/JS) as static files
- Contains the AI chatbot logic with multi-language support

Key API endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sensors` | Get current sensor readings |
| POST | `/api/sensors` | Update sensor data (called by Java) |
| GET | `/api/history` | Get historical sensor data |
| POST | `/api/chatbot/message` | Send message to AI chatbot |
| POST | `/api/agriculture/analyze` | Run pollution analysis |
| GET | `/api/health-score` | Get current AQI health score |

### 4.3 Web Dashboard — `public/` (HTML/CSS/JS)

Dark pollution-themed UI (navy + orange-red color scheme).

Pages:

| Page | Description |
|------|-------------|
| `dashboard.html` | Main live sensor dashboard with 5 sensor cards |
| `agriculture.html` | Smart Pollution AI — AQI analysis, health risks, sources, weather |
| `chatbot.html` | AI Chatbot — pollution Q&A in English, Hindi, Punjabi |
| `analytics.html` | Charts and historical data visualization |
| `history.html` | Tabular sensor data history |
| `alerts.html` | Pollution threshold alerts |
| `settings.html` | System configuration |

### 4.4 AI Chatbot

The chatbot responds to pollution-related questions in 3 languages:
- English
- Hindi (हिंदी)
- Punjabi (ਪੰਜਾਬੀ)

Topics it handles:
- AQI levels and what they mean
- PM2.5 / PM10 particulate matter
- Health risks from pollution
- Protection tips (masks, indoor air quality)
- Pollution sources (vehicles, industry, biomass burning)
- Temperature and humidity effects on pollution
- Water quality
- Indoor air quality
- Environmental improvement tips

If an OpenRouter/Gemini API key is configured, it uses a real AI model. Otherwise it falls back to a built-in rule-based demo mode that still gives detailed, useful responses.

---

## 5. Technology Stack

| Layer | Technology |
|-------|-----------|
| Sensor Simulator | Java 17, Eclipse IDE |
| Backend Server | Python 3.x, Flask, Flask-SocketIO, Flask-CORS |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Real-time Communication | WebSocket (Socket.IO) |
| Data Storage | JSON files (local), optional Google Sheets |
| AI Chatbot | Rule-based demo mode / OpenRouter API (optional) |
| AI Disease/Pollution Model | PyTorch (optional, falls back to demo) |

---

## 6. How to Run

### Step 1 — Start the Flask Server
```bash
cd KrishiShakti_local
pip install flask flask-socketio flask-cors
python app.py
```
Server starts at: `http://localhost:5000`

### Step 2 — Run the Java Simulator in Eclipse
1. Open Eclipse
2. Open `project.java`
3. Right-click → Run As → Java Application
4. Console will show sensor values being sent every second

### Step 3 — Open the Dashboard
Go to: `http://localhost:5000/dashboard.html`

The dashboard will update in real time as Java sends data.

---

## 7. Project File Structure

```
KrishiShakti_local/
├── app.py                    # Main Flask server + AI chatbot logic
├── project.java              # Java sensor simulator (run in Eclipse)
├── simulator.py              # Python simulator (alternative to Java)
├── requirements.txt          # Python dependencies
├── public/
│   ├── dashboard.html        # Live sensor dashboard
│   ├── dashboard.css         # Dark pollution theme styles
│   ├── dashboard.js          # Dashboard real-time logic
│   ├── agriculture.html      # Pollution AI analysis page
│   ├── agriculture.js        # Pollution AI logic
│   ├── agriculture.css       # Pollution AI styles
│   ├── chatbot.html          # AI chatbot interface
│   ├── chatbot.js            # Chatbot frontend logic
│   ├── chatbot.css           # Chatbot styles
│   ├── analytics.html        # Data analytics page
│   ├── history.html          # Historical data table
│   ├── alerts.html           # Alerts page
│   ├── settings.html         # Settings page
│   ├── login.html            # Login page
│   └── index.html            # Landing page
├── data/
│   ├── history.json          # Stored sensor readings
│   └── sensor_data_export.csv
└── arduino/
    └── sensor_reader.ino     # Arduino code (for real hardware)
```

---

## 8. Data Flow (Step by Step)

```
1. Java (Eclipse) generates random sensor values
2. Java sends HTTP POST to http://localhost:5000/api/sensors with JSON
3. Flask receives the JSON and updates in-memory sensor_data dict
4. Flask saves the reading to data/history.json
5. Flask broadcasts the update to all browsers via WebSocket
6. Browser dashboard receives the update and refreshes all sensor cards
7. User can ask the AI chatbot about the current readings
8. Chatbot reads the sensor data and gives pollution advice
```

---

## 9. AQI Classification Used

| AQI Range | Category | Color | Action |
|-----------|----------|-------|--------|
| 0–50 | Good | Green | Safe for all |
| 51–100 | Moderate | Yellow | Sensitive groups cautious |
| 101–150 | Unhealthy for Sensitive Groups | Orange | Sensitive groups stay indoors |
| 151–200 | Unhealthy | Red | Everyone limit outdoor activity |
| 201–300 | Very Unhealthy | Purple | Avoid outdoors, wear N95 |
| 301+ | Hazardous | Maroon | Emergency conditions |

---

## 10. Optional Integrations

- **Google Sheets**: Automatically log all sensor readings to a Google Sheet (requires `gspread` and service account credentials)
- **OpenRouter / Gemini AI**: Replace the rule-based chatbot with a real LLM for smarter responses
- **Real Arduino Hardware**: Replace the Java simulator with actual MQ-135, PMS5003, DHT22, FC-28, and TDS sensors connected to an Arduino Uno

---

## 11. Authors & Credits

- Project built and themed as a Pollution Monitoring System
- Originally scaffolded as KrishiShakti (Smart Agriculture IoT)
- Backend: Python / Flask
- Frontend: Custom dark-themed HTML/CSS/JS
- Simulator: Java (Eclipse)
- AI Chatbot: Multi-language rule-based + optional LLM integration
