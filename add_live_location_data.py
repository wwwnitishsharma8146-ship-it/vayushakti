#!/usr/bin/env python3
"""
Add test sensor data with LIVE LOCATION detection
"""

import requests
import json
from datetime import datetime, timedelta
import random
import time

SERVER_URL = "http://localhost:5001"

def get_live_location():
    """Get live location from IP address"""
    try:
        print("🌍 Detecting your live location...")
        response = requests.get('https://ipapi.co/json/', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            location = {
                'city': data.get('city', 'Unknown'),
                'country': data.get('country_name', 'Unknown'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'region': data.get('region', ''),
                'timezone': data.get('timezone', '')
            }
            print(f"✅ Location detected: {location['city']}, {location['country']}")
            print(f"   Coordinates: {location['latitude']}, {location['longitude']}")
            print(f"   Region: {location['region']}")
            print(f"   Timezone: {location['timezone']}\n")
            return location
        else:
            print("⚠️ Could not detect location from IP")
            return None
            
    except Exception as e:
        print(f"❌ Error detecting location: {str(e)}")
        return None

def generate_realistic_sensor_data(timestamp, location):
    """Generate realistic sensor data based on time and location"""
    hour = timestamp.hour
    
    # Temperature: realistic for Landran, Punjab in late February
    # Night: 10-15°C, Day: 20-28°C
    if 6 <= hour <= 18:  # Daytime
        temp = 20 + random.uniform(0, 8)  # 20-28°C during day
    else:  # Nighttime
        temp = 10 + random.uniform(0, 5)  # 10-15°C at night
    
    # Humidity: inverse relationship with temperature
    humidity = 80 - (temp - 20) * 2 + random.uniform(-5, 5)
    humidity = max(30, min(90, humidity))
    
    # Soil moisture
    soil_moisture = random.uniform(35, 75)
    
    # Air quality: better at night
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
        'location': location
    }

def send_sensor_data(data):
    """Send sensor data to the server"""
    try:
        response = requests.post(
            f"{SERVER_URL}/api/sensors",
            json=data,
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error sending data: {str(e)}")
        return False

def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║  KrishiShakti - Live Location Data Generator         ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{SERVER_URL}/api/sensors", timeout=2)
        print("✅ Server is running\n")
    except:
        print("❌ Server is not running!")
        print("Please start the server first: python3 app.py\n")
        return
    
    # Get live location
    location = get_live_location()
    
    if not location:
        print("⚠️ Using default location: Delhi, India")
        location = {
            'city': 'Delhi',
            'country': 'India',
            'latitude': 28.6139,
            'longitude': 77.2090
        }
    
    # Generate data for the last 48 hours
    print(f"📊 Generating 48 hours of test data with location: {location['city']}, {location['country']}\n")
    
    now = datetime.now()
    success_count = 0
    
    for i in range(96):  # 48 hours * 2 readings per hour
        timestamp = now - timedelta(minutes=30 * (96 - i))
        data = generate_realistic_sensor_data(timestamp, location)
        
        if send_sensor_data(data):
            success_count += 1
            print(f"✓ {i+1}/96 - {timestamp.strftime('%Y-%m-%d %H:%M')} - {location['city']} - Temp: {data['temperature']}°C, Soil: {data['fc28']}%")
        else:
            print(f"✗ Failed {i+1}/96")
        
        time.sleep(0.1)
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully added {success_count}/96 readings!")
    print(f"📍 Location: {location['city']}, {location['country']}")
    print(f"{'='*60}\n")
    
    print("📊 View your data:")
    print(f"   Dashboard: {SERVER_URL}/dashboard.html")
    print(f"   History: {SERVER_URL}/history.html")
    print(f"   Google Sheet: https://docs.google.com/spreadsheets/d/17FoN1d2P59MjaPIXD868wNYLq18HxBkq6DeQz46A-54")
    
    # Show current readings
    try:
        response = requests.get(f"{SERVER_URL}/api/sensors")
        current = response.json()
        print(f"\n📡 Current Sensor Readings:")
        print(f"   📍 Location: {current.get('location', {}).get('city', 'Unknown')}, {current.get('location', {}).get('country', 'Unknown')}")
        print(f"   🌡️  Temperature: {current['dht22']['temperature']}°C")
        print(f"   💧 Humidity: {current['dht22']['humidity']}%")
        print(f"   🌱 Soil Moisture: {current['fc28']['value']}%")
        print(f"   💨 Air Quality: {current['mq135']['value']} ppm")
    except:
        pass

if __name__ == '__main__':
    main()
