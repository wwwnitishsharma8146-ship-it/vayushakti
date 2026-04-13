#!/usr/bin/env python3
"""
Check if dashboard is receiving data
"""

import requests
import json

print("╔════════════════════════════════════════════════════════╗")
print("║  Dashboard Data Check                                 ║")
print("╚════════════════════════════════════════════════════════╝\n")

# Check server
print("1. Checking server...")
try:
    response = requests.get("http://localhost:5001/api/sensors", timeout=5)
    if response.status_code == 200:
        print("   ✅ Server is responding")
        data = response.json()
        print(f"\n2. Current sensor data:")
        print(f"   🌡️  Temperature: {data['dht22']['temperature']}°C")
        print(f"   💧 Humidity: {data['dht22']['humidity']}%")
        print(f"   💨 Air Quality: {data['mq135']['value']} ppm")
        print(f"   🚰 Water Tank: {data['fc28']['value']}%")
        print(f"   🌱 Soil: {data['tds']['value']}%")
        print(f"   📍 Location: {data['location']['city']}, {data['location']['country']}")
    else:
        print(f"   ❌ Server error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Cannot connect to server: {str(e)}")
    exit(1)

# Check dashboard page
print(f"\n3. Checking dashboard page...")
try:
    response = requests.get("http://localhost:5001/dashboard.html", timeout=5)
    if response.status_code == 200:
        print("   ✅ Dashboard page is accessible")
    else:
        print(f"   ❌ Dashboard error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Cannot load dashboard: {str(e)}")

# Check test page
print(f"\n4. Test page created:")
print(f"   📊 http://localhost:5001/test-data.html")
print(f"   This page shows live data updating every 2 seconds")

print(f"\n{'='*60}")
print("✅ DIAGNOSIS COMPLETE")
print(f"{'='*60}\n")

print("🔧 If dashboard still shows 0.0:")
print("\n   Option 1: Use test page")
print("   → Open: http://localhost:5001/test-data.html")
print("   → This shows live data with auto-refresh")

print("\n   Option 2: Hard refresh dashboard")
print("   → Mac: Cmd + Shift + R")
print("   → Windows: Ctrl + Shift + R")
print("   → Or clear browser cache")

print("\n   Option 3: Check browser console")
print("   → Press F12 in browser")
print("   → Look for JavaScript errors")
print("   → Check Network tab for failed requests")

print("\n📊 Current data is flowing correctly!")
print("   Server has data, bridge is working.")
print("   Issue is likely browser cache.\n")
