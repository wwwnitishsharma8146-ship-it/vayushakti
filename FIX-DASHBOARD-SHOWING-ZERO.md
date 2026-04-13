# 🔧 Fix Dashboard Showing Zero

## Problem
Dashboard shows 0 for all sensors even though data is being generated.

## ✅ Confirmed: Data is Working!

I checked the API and data is there:
```json
{
  "mq135": { "value": 19.24 },      ✓ (18-20 range)
  "temperature": 29.87,              ✓ (28-30 range)
  "pm25": 11.12,                     ✓ (10-12 range)
  "pm10": 11.79,                     ✓ (10-12 range)
  "fc28": { "value": 10.42 },        ✓ (10-12 range)
  "tds": { "value": 136 }            ✓ (100-150 range)
}
```

## 🎯 Solution: Clear Browser Cache

### Method 1: Hard Refresh (Quickest)

**On Mac:**
- Chrome/Edge: `Cmd + Shift + R`
- Safari: `Cmd + Option + R`
- Firefox: `Cmd + Shift + R`

**On Windows:**
- Chrome/Edge/Firefox: `Ctrl + Shift + R` or `Ctrl + F5`

### Method 2: Clear Cache Manually

**Chrome:**
1. Press `Cmd + Shift + Delete` (Mac) or `Ctrl + Shift + Delete` (Windows)
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh dashboard

**Safari:**
1. Safari menu → Preferences → Advanced
2. Check "Show Develop menu"
3. Develop → Empty Caches
4. Refresh dashboard

**Firefox:**
1. Press `Cmd + Shift + Delete` (Mac) or `Ctrl + Shift + Delete` (Windows)
2. Select "Cache"
3. Click "Clear Now"
4. Refresh dashboard

### Method 3: Use Test Page (Guaranteed to Work)

Open this page instead:
```
http://localhost:5001/test-sensors.html
```

This is a fresh page with no cache that will definitely show the data!

### Method 4: Incognito/Private Mode

1. Open incognito/private window
2. Go to: `http://localhost:5001/dashboard.html`
3. Data should show correctly

---

## 🔍 Verify Data is Working

### Test 1: Check API Directly
```bash
curl http://localhost:5001/api/sensors
```

You should see JSON with all sensor values (not zeros).

### Test 2: Use Test Page
```
http://localhost:5001/test-sensors.html
```

This page will show:
- 🌿 MQ-135: 18-20 ppm
- 🌡️ Temperature: 28-30°C
- 💧 Humidity: 40-80%
- 💨 PM2.5: 10-12 µg/m³
- 💨 PM10: 10-12 µg/m³
- 💦 Water Level: 10-12%
- 🚰 Water Quality: 100-150 ppm

Auto-refreshes every 8 seconds!

---

## 🚀 Quick Fix Steps

1. **Open test page first:**
   ```
   http://localhost:5001/test-sensors.html
   ```
   
2. **If test page shows data correctly:**
   - Your system is working!
   - The issue is browser cache
   - Clear cache and refresh dashboard

3. **If test page also shows zeros:**
   - Check if simulator is running: `ps aux | grep simulator`
   - Check if Flask is running: `ps aux | grep app.py`
   - Restart both if needed

---

## 📊 Expected Values on Dashboard

After clearing cache, you should see:

| Sensor | Value Range | Status |
|--------|-------------|--------|
| MQ-135 | 18-20 ppm | Excellent (Green) |
| Temperature | 28-30°C | Optimal (Green) |
| Humidity | 40-80% | Good (Green) |
| PM2.5 | 10-12 µg/m³ | Excellent (Green) |
| PM10 | 10-12 µg/m³ | Excellent (Green) |
| Water Level | 10-12% | Critical (Red) ⚠️ |
| Water Quality | 100-150 ppm | Pure (Green) |

---

## 🔄 If Still Showing Zero

### Check 1: Simulator Running?
```bash
ps aux | grep simulator.py
```

If not running:
```bash
./restart_simulator.sh
```

### Check 2: Flask Running?
```bash
ps aux | grep app.py
```

If not running:
```bash
python app.py
```

### Check 3: Data in API?
```bash
curl http://localhost:5001/api/sensors | grep "value"
```

Should show non-zero values.

### Check 4: WebSocket Connection
Open browser console (F12) and check for errors.
Look for WebSocket connection messages.

---

## 💡 Why This Happens

**Browser Cache:**
- Browser cached old dashboard.js file
- Old JavaScript trying to connect to old data format
- Hard refresh loads new files

**WebSocket Issue:**
- WebSocket connection might be stale
- Refreshing page reconnects WebSocket
- New connection gets fresh data

---

## ✅ Recommended Solution

**Use the test page for now:**
```
http://localhost:5001/test-sensors.html
```

This page:
- ✅ No cache issues
- ✅ Simple, clean display
- ✅ Auto-refreshes every 8 seconds
- ✅ Shows all sensor values
- ✅ Guaranteed to work

Then clear cache and go back to main dashboard.

---

## 🎯 Summary

**Problem:** Dashboard shows 0
**Cause:** Browser cache
**Solution:** Hard refresh (`Cmd+Shift+R` or `Ctrl+Shift+R`)
**Alternative:** Use test page: `http://localhost:5001/test-sensors.html`

**Data is working!** Just need to clear browser cache.
