# 📡 Blynk Integration - Show Real Sensor Data

## ✅ What This Does

Fetches real sensor data from your Blynk device (LED BLINK) and displays it on your KrishiShakti dashboard in real-time.

## 🔌 Your Blynk Setup

Based on your data, here's what we detected:

```
Blynk Device: LED BLINK (Offline/Online)
Token: OaGNlIyoI2FG6xTgLeUY1Flz-7fadvjO

Pin Mapping:
├── v3: Soil Moisture (100%)
├── v4: Humidity (10-14%)
├── v5: Water Tank Level (1-8)
├── v6: Unknown Sensor (50)
└── v7: Temperature (25-27°C)
```

## 🚀 Quick Start

### Step 1: Start Your KrishiShakti Server

```bash
python3 app.py
```

Keep this running in one terminal.

### Step 2: Start the Blynk Bridge

Open a NEW terminal and run:

```bash
python3 blynk_bridge.py
```

Or use the shortcut:

```bash
./start_blynk_bridge.sh
```

### Step 3: View Your Dashboard

Open: **http://localhost:5001/dashboard.html**

You'll see your REAL sensor data updating every 5 seconds!

## 📊 Data Flow

```
Blynk Device (Arduino/ESP32)
        ↓
Blynk Cloud API
        ↓
blynk_bridge.py (This script)
        ↓
KrishiShakti Server
        ↓
Your Dashboard (Browser)
```

## 🔄 What Gets Updated

### From Blynk → Dashboard:

| Blynk Pin | Value Range | Dashboard Display |
|-----------|-------------|-------------------|
| v7 | 25-27°C | Temperature (DHT22) |
| v4 | 10-14% | Humidity (DHT22) |
| v3 | 0-100% | Soil Moisture (FC-28) |
| v5 | 1-8 | Water Tank Level |
| v6 | ~50 | Water Quality (TDS) |

### Derived Values:

- **Air Quality (MQ-135)**: Calculated from soil moisture
- **PM2.5**: Derived from environmental conditions
- **PM10**: Derived from environmental conditions

## 📝 Example Output

```
╔════════════════════════════════════════════════════════╗
║  Blynk to KrishiShakti Bridge                         ║
╚════════════════════════════════════════════════════════╝

📡 Fetching real sensor data from Blynk...
🔄 Sending to KrishiShakti dashboard...
📍 Location: Landran, Punjab, India

Press Ctrl+C to stop

✓ 10:40:37 - Temp: 26°C, Humidity: 50%, Soil: 100% [1 sent]
✓ 10:40:43 - Temp: 27°C, Humidity: 50%, Soil: 100% [2 sent]
✓ 10:40:48 - Temp: 27°C, Humidity: 50%, Soil: 100% [3 sent]
```

## ⚙️ Configuration

### Change Update Frequency

Edit `blynk_bridge.py`, find:

```python
time.sleep(5)  # Wait 5 seconds
```

Change to:
- `time.sleep(3)` - Update every 3 seconds (faster)
- `time.sleep(10)` - Update every 10 seconds (slower)

### Adjust Pin Mapping

If your Blynk pins are different, edit `blynk_bridge.py`:

```python
# Current mapping
soil_moisture = blynk_data.get('v3', 0)
humidity = blynk_data.get('v4', 0)
water_level = blynk_data.get('v5', 0)
temperature = blynk_data.get('v7', 0)
```

Change the pin numbers (v3, v4, v5, v7) to match your setup.

### Change Blynk Token

Edit `blynk_bridge.py`, find:

```python
BLYNK_TOKEN = "OaGNlIyoI2FG6xTgLeUY1Flz-7fadvjO"
```

Replace with your token if different.

## 🔧 Troubleshooting

### "Connection refused" or "Cannot connect"

**Problem**: KrishiShakti server not running

**Solution**: 
```bash
# Start the server first
python3 app.py
```

### "Blynk API error: 401"

**Problem**: Invalid Blynk token

**Solution**: Check your token in Blynk console and update `blynk_bridge.py`

### "Blynk API error: 404"

**Problem**: Blynk device offline or pins don't exist

**Solution**: 
- Check if your Arduino/ESP32 is online in Blynk console
- Verify pin numbers (v3, v4, v5, v7) exist in your Blynk project

### Dashboard shows 0 values

**Problem**: Bridge not running or data not being sent

**Solution**:
1. Check bridge is running: `python3 blynk_bridge.py`
2. Look for "✓" success messages
3. Refresh dashboard: http://localhost:5001/dashboard.html

### Data not updating

**Problem**: Old data cached

**Solution**: Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

## 📱 Run Both Together

### Terminal 1 (Server):
```bash
python3 app.py
```

### Terminal 2 (Bridge):
```bash
python3 blynk_bridge.py
```

### Browser:
```
http://localhost:5001/dashboard.html
```

## 🎯 What You'll See

Your dashboard will show:
- ✅ Real temperature from your Blynk device (25-27°C)
- ✅ Real humidity from your Blynk device (10-14%)
- ✅ Real soil moisture from your Blynk device (100%)
- ✅ Real water tank level from your Blynk device
- ✅ Location: Landran, Punjab, India
- ✅ Updates every 5 seconds

## 🔄 Auto-Start on Boot (Optional)

To start automatically when your computer boots:

### macOS/Linux:

Create a startup script:

```bash
# Create startup script
cat > ~/start_krishishakti.sh << 'EOF'
#!/bin/bash
cd ~/Downloads/KrishiShakti_local-main
python3 app.py &
sleep 5
python3 blynk_bridge.py &
EOF

chmod +x ~/start_krishishakti.sh
```

Then add to startup applications.

## 📊 Monitor Both Systems

You can monitor both:

1. **Blynk Console**: https://blynk.cloud/dashboard/
   - See your Arduino/ESP32 status
   - View raw pin values
   - Check device online/offline

2. **KrishiShakti Dashboard**: http://localhost:5001/dashboard.html
   - See formatted sensor data
   - View charts and graphs
   - Access AI chatbot
   - Check history

## 🎉 Benefits

- ✅ Real sensor data from your hardware
- ✅ Beautiful dashboard visualization
- ✅ Historical data tracking
- ✅ Google Sheets integration
- ✅ AI chatbot with real data
- ✅ Multi-language support
- ✅ No code changes to your Arduino
- ✅ Works with existing Blynk setup

## 🚀 Next Steps

1. Start server: `python3 app.py`
2. Start bridge: `python3 blynk_bridge.py`
3. Open dashboard: http://localhost:5001/dashboard.html
4. Watch your real sensor data appear!
5. Try the AI chatbot with your real data
6. Check Google Sheets for data logging

---

**Your real sensor data is now powering your KrishiShakti dashboard!** 🌾✨
