#!/usr/bin/env python3
"""
Blynk to KrishiShakti Bridge
Fetches real sensor data from Blynk and sends to local dashboard
"""

import requests
import time
import json
from datetime import datetime

# Blynk Configuration
BLYNK_TOKEN = "OaGNlIyoI2FG6xTgLeUY1Flz-7fadvjO"
BLYNK_URL = f"https://blynk.cloud/external/api/get?token={BLYNK_TOKEN}&V5&V7&V6&V4&V3"

# Local KrishiShakti Server
LOCAL_SERVER = "http://localhost:5000/api/sensors"

# Mapping Blynk pins to sensor data
# Based on your ACTUAL sensors (CORRECTED v2):
# v3 = Soil Moisture (100%)
# v4 = Water Tank Level (10-14) <- CORRECTED
# v5 = Gas/Air Quality Sensor (1-8) <- CORRECTED  
# v6 = Humidity or Unknown (50)
# v7 = Temperature from DHT22 (25-27°C)
#
# Dashboard Mapping:
# - Air Quality Monitor → v5 (Gas Sensor)
# - Temperature → v7 (DHT22)
# - Humidity → v6 (Unknown sensor)
# - Water Tank Level → v4 (Water Tank)
# - Soil Moisture → v3 (displayed as TDS)
# - Particulate Matter → Not available (set to 0)

def fetch_blynk_data():
    """Fetch data from Blynk"""
    try:
        response = requests.get(BLYNK_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Blynk API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error fetching from Blynk: {str(e)}")
        return None

def convert_to_krishishakti_format(blynk_data):
    """Convert Blynk data to KrishiShakti format"""
    
    # Extract values from Blynk - UPDATED MAPPING
    # V3 = Soil Moisture (100%)
    # V4 = Water Tank Level (10-14)
    # V5 = Gas/Air Quality Sensor (1-8)
    # V6 = Humidity or Unknown (50)
    # V7 = Temperature from DHT22 (25-27°C)
    
    soil_moisture = blynk_data.get('V3', 0)  # Soil moisture sensor
    water_tank = blynk_data.get('V4', 0)     # Water tank level
    gas_sensor = blynk_data.get('V5', 0)     # Gas/Air quality sensor
    humidity_v6 = blynk_data.get('V6', 0)    # Humidity sensor
    temperature = blynk_data.get('V7', 0)    # Temperature sensor (DHT22)
    
    # Convert to KrishiShakti format
    krishishakti_data = {
        'temperature': float(temperature),           # DHT22 temperature (V7)
        'humidity': float(humidity_v6),             # Humidity from V6
        'mq135': float(gas_sensor),                 # Air quality/Gas sensor (V5)
        'pm25': 0,                                  # No PM2.5 sensor - set to 0
        'pm10': 0,                                  # No PM10 sensor - set to 0
        'fc28': float(water_tank),                  # Water tank level (V4)
        'tds': float(soil_moisture),                # Soil moisture as TDS (V3)
        'location': {
            'city': 'Landran',
            'country': 'India',
            'latitude': 30.698,
            'longitude': 76.667
        }
    }
    
    return krishishakti_data

def send_to_krishishakti(data):
    """Send data to local KrishiShakti server"""
    try:
        response = requests.post(LOCAL_SERVER, json=data, timeout=5)
        if response.status_code == 200:
            return True
        else:
            print(f"❌ KrishiShakti API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending to KrishiShakti: {str(e)}")
        return False

def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║  Blynk to KrishiShakti Bridge                         ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    print("📡 Fetching real sensor data from Blynk...")
    print("🔄 Sending to KrishiShakti dashboard...")
    print("📍 Location: Landran, Punjab, India")
    print("💾 Saving backup to sensor_data.json\n")
    print("Press Ctrl+C to stop\n")
    
    success_count = 0
    error_count = 0
    
    while True:
        try:
            # Fetch from Blynk
            blynk_data = fetch_blynk_data()
            
            if blynk_data:
                # Save raw Blynk data to JSON file (backup)
                try:
                    with open("sensor_data.json", "w") as file:
                        json.dump(blynk_data, file, indent=4)
                except Exception as e:
                    print(f"⚠️  Could not save to JSON: {str(e)}")
                
                # Convert format
                krishishakti_data = convert_to_krishishakti_format(blynk_data)
                
                # Send to local server
                if send_to_krishishakti(krishishakti_data):
                    success_count += 1
                    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{current_time}] ✓ "
                          f"Temp: {krishishakti_data['temperature']}°C, "
                          f"Humidity: {krishishakti_data['humidity']}%, "
                          f"Gas/Air: {krishishakti_data['mq135']}, "
                          f"Water Tank: {krishishakti_data['fc28']}, "
                          f"Soil: {krishishakti_data['tds']}% "
                          f"[{success_count} sent]")
                else:
                    error_count += 1
            else:
                error_count += 1
                current_time = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{current_time}] ⚠️  Failed to fetch data [{error_count} errors]")
            
            # Wait 3 seconds before next update (matching your friend's code)
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n\n👋 Data collection stopped")
            print(f"\n📊 Statistics:")
            print(f"   ✅ Successful updates: {success_count}")
            print(f"   ❌ Failed updates: {error_count}")
            break
        except Exception as e:
            error_count += 1
            print(f"❌ Error: {str(e)}")
            time.sleep(3)

if __name__ == '__main__':
    main()
