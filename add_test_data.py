#!/usr/bin/env python3
"""
Add test sensor data to the system
This will add data to local storage and attempt to sync with Google Sheets
"""

import requests
import json
from datetime import datetime, timedelta
import random
import time

# Server URL
SERVER_URL = "http://localhost:5001"

def generate_realistic_sensor_data(timestamp):
    """Generate realistic sensor data"""
    # Time-based variations (simulate day/night cycles)
    hour = timestamp.hour
    
    # Temperature: cooler at night, warmer during day
    base_temp = 25
    if 6 <= hour <= 18:  # Daytime
        temp = base_temp + random.uniform(2, 8)
    else:  # Nighttime
        temp = base_temp - random.uniform(2, 5)
    
    # Humidity: inverse relationship with temperature
    humidity = 80 - (temp - 20) * 2 + random.uniform(-5, 5)
    humidity = max(30, min(90, humidity))
    
    # Soil moisture: gradually decreases, then spikes after "watering"
    soil_moisture = random.uniform(35, 75)
    
    # Air quality: better at night, worse during day
    if 6 <= hour <= 18:
        air_quality = random.uniform(80, 180)
    else:
        air_quality = random.uniform(50, 120)
    
    # Particulate matter
    pm25 = random.uniform(10, 45)
    pm10 = pm25 + random.uniform(10, 25)
    
    # Water quality
    tds = random.uniform(200, 400)
    
    return {
        'temperature': round(temp, 1),
        'humidity': round(humidity, 1),
        'mq135': round(air_quality, 1),
        'pm25': round(pm25, 1),
        'pm10': round(pm10, 1),
        'fc28': round(soil_moisture, 1),
        'tds': round(tds, 0),
        'location': {
            'city': 'Mumbai',
            'country': 'India',
            'latitude': 19.0760,
            'longitude': 72.8777
        }
    }

def send_sensor_data(data):
    """Send sensor data to the server"""
    try:
        response = requests.post(
            f"{SERVER_URL}/api/sensors",
            json=data,
            timeout=5
        )
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending data: {str(e)}")
        return False

def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║  KrishiShakti - Test Data Generator                  ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{SERVER_URL}/api/sensors", timeout=2)
        print("✅ Server is running\n")
    except:
        print("❌ Server is not running!")
        print("Please start the server first: python3 app.py\n")
        return
    
    # Generate data for the last 24 hours (one reading every 30 minutes = 48 readings)
    print("📊 Generating 48 hours of test data (one reading every 30 minutes)...\n")
    
    now = datetime.now()
    success_count = 0
    
    for i in range(96):  # 48 hours * 2 readings per hour
        # Calculate timestamp (going backwards from now)
        timestamp = now - timedelta(minutes=30 * (96 - i))
        
        # Generate sensor data
        data = generate_realistic_sensor_data(timestamp)
        
        # Send to server
        if send_sensor_data(data):
            success_count += 1
            print(f"✓ Added reading {i+1}/96 - {timestamp.strftime('%Y-%m-%d %H:%M')} - Temp: {data['temperature']}°C, Humidity: {data['humidity']}%, Soil: {data['fc28']}%")
        else:
            print(f"✗ Failed to add reading {i+1}/96")
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully added {success_count}/96 readings!")
    print(f"{'='*60}\n")
    
    print("📊 View your data:")
    print(f"   Dashboard: {SERVER_URL}/dashboard.html")
    print(f"   History: {SERVER_URL}/history.html")
    print(f"   Analytics: {SERVER_URL}/analytics.html")
    print(f"   Data Viewer: {SERVER_URL}/data-viewer.html")
    
    # Show current sensor status
    try:
        response = requests.get(f"{SERVER_URL}/api/sensors")
        current = response.json()
        print(f"\n📡 Current Sensor Readings:")
        print(f"   🌡️  Temperature: {current['dht22']['temperature']}°C")
        print(f"   💧 Humidity: {current['dht22']['humidity']}%")
        print(f"   🌱 Soil Moisture: {current['fc28']['value']}%")
        print(f"   💨 Air Quality: {current['mq135']['value']} ppm")
        print(f"   🌫️  PM2.5: {current['pms5003']['pm25']} µg/m³")
        print(f"   🚰 Water Quality: {current['tds']['value']} ppm")
    except:
        pass

if __name__ == '__main__':
    main()
