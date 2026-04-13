import requests
import json
import time

# --- CONFIGURATION ---
BLYNK_TEMPLATE_ID   = "TMPL3ce5eQaVJ"
BLYNK_TEMPLATE_NAME = "LED BLINK"
BLYNK_AUTH_TOKEN    = "OaGNlIyoI2FG6xTgLeUY1Flz-7fadvjO"
BLYNK_SERVER        = "https://blynk.cloud/external/api/get?token="
FETCH_INTERVAL      = 10  # seconds

# Mapping Virtual Pins to meaningful names
PINS_TO_FETCH = {
    "V3": "soil_moisture_percent",
    "V4": "ultrasonic_distance_cm",
    "V6": "humidity_percent",
    "V7": "temperature_celsius",
    "V8": "gas_leak_status"
}

def fetch_blynk_data():
    sensor_data = {}

    for pin, label in PINS_TO_FETCH.items():
        try:
            url = f"{BLYNK_SERVER}{BLYNK_AUTH_TOKEN}&pin={pin}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                sensor_data[label] = response.text.strip()
            else:
                print(f"  [{pin}] HTTP {response.status_code}: {response.text.strip()}")
                sensor_data[label] = "Error"
        except requests.exceptions.Timeout:
            print(f"  [{pin}] Timeout")
            sensor_data[label] = "Timeout"
        except Exception as e:
            print(f"  [{pin}] Error: {e}")
            sensor_data[label] = "Error"

    sensor_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return sensor_data

def save_to_json(data):
    filename = "krishi_shakti_data.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# --- CONTINUOUS FETCH LOOP ---
if __name__ == "__main__":
    print(f"Starting continuous Blynk fetch every {FETCH_INTERVAL}s... (Ctrl+C to stop)\n")
    cycle = 1
    while True:
        print(f"[Cycle {cycle}] Fetching at {time.strftime('%H:%M:%S')}...")
        data = fetch_blynk_data()
        save_to_json(data)
        print(f"  soil_moisture   : {data.get('soil_moisture_percent')}")
        print(f"  ultrasonic_dist : {data.get('ultrasonic_distance_cm')}")
        print(f"  humidity        : {data.get('humidity_percent')}")
        print(f"  temperature     : {data.get('temperature_celsius')}")
        print(f"  gas_leak        : {data.get('gas_leak_status')}")
        print(f"  Saved to krishi_shakti_data.json\n")
        cycle += 1
        time.sleep(FETCH_INTERVAL)