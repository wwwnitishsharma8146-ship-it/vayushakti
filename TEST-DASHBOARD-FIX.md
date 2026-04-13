# 🧪 Test Dashboard Fix - Quick Guide

## Prerequisites

Make sure these are running:

1. ✅ Flask server on port 5000
2. ✅ Blynk bridge sending data every 3 seconds

## Test Steps

### Test 1: Check Quick Stats Cards

1. **Open Dashboard**
   ```
   http://localhost:5000/dashboard.html
   ```

2. **Look at the 4 small cards at the top:**
   - 💨 Air Quality
   - 🌡️ Temperature
   - 💧 Water Level
   - 📊 Active Sensors

3. **Expected Results:**
   - Air Quality: Should show "Good", "Moderate", or "Poor"
   - Temperature: Should show actual value like "26.5°C" (not --°C)
   - Water Level: Should show actual percentage like "12%" (not --%)
   - Active Sensors: Should show "5/5"

4. **Watch for Updates:**
   - Values should update every 3 seconds
   - Watch the "Last Update" time change

### Test 2: Compare with Large Cards

1. **Scroll down to large sensor cards**

2. **Compare values:**
   - Quick Temp (top) should match Climate Monitor temp (large card)
   - Quick Water (top) should match Water Tank Level (large card)
   - Quick Air Quality (top) should match Air Quality Monitor (large card)

3. **Expected Result:**
   - All values should be identical
   - All should update at the same time

### Test 3: Check Analytics Page

1. **Open Analytics**
   ```
   http://localhost:5000/analytics.html
   ```

2. **Check the 4 stat cards at top:**
   - Avg Air Quality
   - Water Collected
   - Avg Temperature
   - Total Readings

3. **Expected Result:**
   - Should show calculated averages from historical data
   - Charts should display properly

### Test 4: Check Browser Console

1. **Press F12 to open Developer Tools**

2. **Go to Console tab**

3. **Look for logs:**
   ```
   updateDashboard called with data: {mq135: {...}, dht22: {...}, ...}
   MQ-135 value: 5
   Temperature: 26.5 Humidity: 50
   Water level: 12
   Soil moisture: 100
   ```

4. **Expected Result:**
   - No errors in console
   - Data logs appear every 3 seconds
   - Values match what's displayed on page

### Test 5: Test Fallback Behavior

1. **Stop the Blynk bridge** (Ctrl+C in terminal)

2. **Wait 10 seconds**

3. **Refresh dashboard**

4. **Expected Result:**
   - Temperature: Shows `--°C`
   - Water Level: Shows `--%`
   - Soil Moisture: Shows "Waiting for data..."
   - No JavaScript errors

5. **Restart Blynk bridge**

6. **Expected Result:**
   - Values should start updating again within 3 seconds

### Test 6: Check Soil Moisture Handling

Since soil moisture sensor is not connected:

1. **Look at Soil Moisture card** (large card with 🌱 icon)

2. **Expected Result:**
   - Value: Shows `--` or `0.0`
   - Status: Shows "Waiting for data..."
   - Progress bar: Empty (0%)

## Success Criteria

✅ Quick stats cards show real values (not placeholders)  
✅ Values update every 3 seconds  
✅ Dashboard and Analytics show consistent data  
✅ Fallbacks work when no data available  
✅ Soil moisture shows "Waiting for data..."  
✅ No JavaScript errors in console  
✅ WebSocket connection status shows "Connected"

## Troubleshooting

### Quick Stats Still Show --°C and --%

**Check:**
1. Is Flask server running?
   ```bash
   curl http://localhost:5000/api/sensors
   ```

2. Is Blynk bridge running?
   ```bash
   ps aux | grep blynk_bridge
   ```

3. Check browser console for errors (F12)

**Fix:**
```bash
# Restart Flask server
/storage/Desktop/sem2/t5env/bin/python app.py

# Restart Blynk bridge
/storage/Desktop/sem2/t5env/bin/python blynk_bridge.py
```

### Values Not Updating

**Check:**
1. WebSocket connection status (should show green dot)
2. "Last Update" time (should change every 3 seconds)
3. Browser console for WebSocket errors

**Fix:**
- Refresh the page (F5)
- Clear browser cache (Ctrl+Shift+R)
- Check Flask server logs for errors

### Analytics Shows Data but Dashboard Doesn't

**Check:**
1. Both pages use different endpoints:
   - Dashboard: `/api/sensors` (real-time)
   - Analytics: `/api/history` (historical)

2. Test both endpoints:
   ```bash
   curl http://localhost:5000/api/sensors
   curl http://localhost:5000/api/history
   ```

**Fix:**
- Make sure Blynk bridge is sending data to `/api/sensors`
- Check Flask logs for POST requests

### Soil Moisture Shows Wrong Value

**Expected Behavior:**
- Since sensor is not connected, should show "Waiting for data..."
- If showing a value, it's from test data (ignore it)

## Quick Test Command

Run this to check if everything is working:

```bash
echo "=== Dashboard Fix Test ==="
echo ""
echo "1. Flask Server:"
curl -s http://localhost:5000/api/sensors | head -c 100
echo "..."
echo ""
echo "2. Blynk Bridge:"
ps aux | grep blynk_bridge | grep -v grep && echo "✅ Running" || echo "❌ Not running"
echo ""
echo "3. Open Dashboard:"
echo "   http://localhost:5000/dashboard.html"
echo ""
echo "4. Check quick stats cards at top"
echo "   Should show real values, not --°C or --%"
```

## Visual Verification

### Before Fix
```
┌─────────────────────────────────────────┐
│ Quick Stats (Top of Dashboard)         │
├─────────────────────────────────────────┤
│ 💨 Air Quality: Good                    │
│ 🌡️ Temperature: --°C        ❌ STUCK   │
│ 💧 Water Level: --%         ❌ STUCK   │
│ 📊 Active Sensors: 5/5                  │
└─────────────────────────────────────────┘
```

### After Fix
```
┌─────────────────────────────────────────┐
│ Quick Stats (Top of Dashboard)         │
├─────────────────────────────────────────┤
│ 💨 Air Quality: Good                    │
│ 🌡️ Temperature: 26.5°C     ✅ UPDATING │
│ 💧 Water Level: 12%        ✅ UPDATING │
│ 📊 Active Sensors: 5/5                  │
└─────────────────────────────────────────┘
```

## Final Check

Open both pages side by side:

**Left:** `http://localhost:5000/dashboard.html`  
**Right:** `http://localhost:5000/analytics.html`

Both should show:
- ✅ Real sensor values
- ✅ Updating every 3 seconds (dashboard)
- ✅ Charts with historical data (analytics)
- ✅ No errors in console

**Status:** 🎉 **FIX VERIFIED**
