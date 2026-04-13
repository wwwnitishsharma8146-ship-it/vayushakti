# 🔍 Debug Quick Stats Cards

## Problem

Quick stats cards still showing placeholders:
- Temperature: `--°C`
- Water Level: `--%`

But large cards show real values (25.0°C, 13.0%, etc.)

## Debug Steps

### Step 1: Use the Test Page

Open the debug test page:
```
http://localhost:5000/test_dashboard_data.html
```

This will:
1. Fetch data from `/api/sensors`
2. Show the raw JSON response
3. Parse the values exactly like dashboard.js does
4. Display detailed logs showing why values pass or fail validation
5. Update test quick stats cards

**Look for:**
- ✓ Green messages = values are valid
- ✗ Red messages = values failed validation
- Check the "type" of each value (should be "number")

### Step 2: Check Browser Console on Dashboard

1. Open dashboard: `http://localhost:5000/dashboard.html`
2. Press F12 → Console tab
3. Look for these logs:

```
=== UPDATING QUICK STATS ===
mq135Value: 200 type: number
tempValue: 25 type: number
fc28Value: 13 type: number
Setting quick-air to: Moderate
Setting quick-temp to: 25.0°C
Setting quick-water to: 13%
=== QUICK STATS UPDATE COMPLETE ===
```

**If you see:**
- `Temperature invalid, showing fallback` → The value is null/undefined/NaN
- `Water level invalid, showing fallback` → The value is null/undefined/NaN

### Step 3: Force Cache Clear

The browser might be caching the old JavaScript file.

**Try these in order:**

1. **Hard Refresh**
   - Windows/Linux: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **Clear Cache and Hard Reload**
   - Press F12 (open DevTools)
   - Right-click the refresh button
   - Select "Empty Cache and Hard Reload"

3. **Clear All Cache**
   - Press F12
   - Go to Application tab
   - Click "Clear storage"
   - Click "Clear site data"
   - Refresh page

4. **Incognito/Private Window**
   - Open new incognito window
   - Go to `http://localhost:5000/dashboard.html`
   - Check if quick stats work there

### Step 4: Check File Version

The dashboard.html now loads:
```html
<script src="dashboard.js?v=4"></script>
```

**Verify in browser:**
1. Press F12 → Network tab
2. Refresh page
3. Look for `dashboard.js?v=4` in the list
4. Should show status 200 (not 304 cached)

### Step 5: Manual API Test

Test the API directly:

```bash
curl http://localhost:5000/api/sensors
```

**Expected response:**
```json
{
  "mq135": {"value": 200, "unit": "ppm"},
  "dht22": {"temperature": 25, "humidity": 42},
  "fc28": {"value": 13, "unit": "%"},
  "tds": {"value": 100, "unit": "%"},
  "timestamp": "2026-03-08T..."
}
```

**Or flat format:**
```json
{
  "mq135": 200,
  "temperature": 25,
  "humidity": 42,
  "fc28": 13,
  "tds": 100,
  "timestamp": "2026-03-08T..."
}
```

Both formats should work with the current code.

## Common Issues

### Issue 1: Old JavaScript Cached

**Symptoms:**
- Console shows old logs (no "=== UPDATING QUICK STATS ===" messages)
- Quick stats don't update

**Fix:**
- Clear cache completely (see Step 3)
- Check Network tab shows `dashboard.js?v=4`

### Issue 2: WebSocket Not Connected

**Symptoms:**
- Initial load shows values, but they don't update
- Connection status shows red dot

**Fix:**
```bash
# Restart Flask server
/storage/Desktop/sem2/t5env/bin/python app.py
```

### Issue 3: Blynk Bridge Not Sending Data

**Symptoms:**
- Large cards show 0 or old values
- Quick stats show fallbacks

**Fix:**
```bash
# Check if bridge is running
ps aux | grep blynk_bridge

# Restart if needed
/storage/Desktop/sem2/t5env/bin/python blynk_bridge.py
```

### Issue 4: Data Format Mismatch

**Symptoms:**
- Console shows: `tempValue: undefined type: undefined`
- Or: `tempValue: [object Object] type: object`

**Fix:**
- Check the test page to see exact data format
- The code handles both nested and flat formats
- If format is different, we need to adjust parsing

## What Should Happen

### On Page Load
```
1. Fetch /api/sensors
2. Parse data
3. Update large cards (working ✓)
4. Update quick stats (should work now)
5. Connect WebSocket
6. Receive updates every 3 seconds
```

### Every 3 Seconds
```
1. WebSocket receives data
2. updateDashboard() called
3. Console logs show values
4. Large cards update
5. Quick stats update
```

## Files Modified

1. ✅ `public/dashboard.js` - Added detailed logging
2. ✅ `public/dashboard.html` - Changed to `?v=4` for cache busting
3. ✅ `test_dashboard_data.html` - Created debug test page

## Next Steps

1. **Open test page** to see detailed logs
2. **Check browser console** on dashboard for logs
3. **Clear cache** and hard refresh
4. **Report back** what you see in the console

The test page will show exactly why the values are or aren't being displayed!
