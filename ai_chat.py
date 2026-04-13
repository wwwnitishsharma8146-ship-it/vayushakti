"""
AI-powered chatbot using OpenRouter API
Context-aware agricultural advisor based on real sensor telemetry
"""

import requests
import os

# OpenRouter API Configuration
# Get your free API key from: https://openrouter.ai/keys
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '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')
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def ask_ai(user_message, sensor_data):
    """
    Ask AI for agricultural advice based on sensor data
    
    Args:
        user_message: The farmer's question
        sensor_data: Current sensor readings from the system
    
    Returns:
        AI-generated response in the same language as the question
    """
    
    # Check if API key is set
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == 'YOUR_API_KEY_HERE':
        raise Exception("API key not configured. Run: python3 setup_openrouter.py")
    
    # Extract sensor values safely
    temperature = sensor_data.get('dht22', {}).get('temperature', 25)
    humidity = sensor_data.get('dht22', {}).get('humidity', 60)
    soil_moisture = sensor_data.get('fc28', {}).get('value', 50)
    air_quality = sensor_data.get('mq135', {}).get('value', 100)
    pm25 = sensor_data.get('pms5003', {}).get('pm25', 15)
    pm10 = sensor_data.get('pms5003', {}).get('pm10', 25)
    
    # Get location
    location = sensor_data.get('location', {})
    city = location.get('city', 'Unknown') if location else 'Unknown'
    country = location.get('country', 'Unknown') if location else 'Unknown'
    
    # Build context with real sensor data
    context = f"""You are an expert agricultural advisor helping farmers in India.

Current Farm Sensor Data (REAL-TIME):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Location: {city}, {country}
🌡️  Temperature: {temperature}°C
💧 Humidity: {humidity}%
🌱 Soil Moisture: {soil_moisture}%
💨 Air Quality (MQ-135): {air_quality} ppm
🌫️  PM2.5: {pm25} µg/m³
🌫️  PM10: {pm10} µg/m³
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT INSTRUCTIONS:
1. Give practical, actionable farming advice based on these REAL sensor readings
2. If the farmer asks in Hindi, Punjabi, or any Indian language, reply in the SAME language
3. If the farmer asks in English, reply in English
4. Keep answers concise and farmer-friendly (3-5 sentences)
5. Reference the actual sensor values in your response
6. Focus on immediate actions the farmer can take

Examples:
- If soil moisture is low → suggest irrigation timing and amount
- If temperature is high → suggest shade/cooling methods
- If air quality is poor → warn about crop health impacts
- If humidity is high → warn about fungal diseases and prevention
"""
    
    # Combine context with user question
    full_prompt = context + "\n\nFarmer's Question: " + user_message
    
    try:
        # Make request to OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5001",
            "X-Title": "KrishiShakti AI Assistant"
        }
        
        payload = {
            "model": "openrouter/auto",  # Free model
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Add sensor context footer
            footer = f"\n\n📊 Based on your current readings: {temperature}°C, {humidity}% humidity, {soil_moisture}% soil moisture"
            return ai_response + footer
        else:
            # Silently fail to trigger demo mode fallback
            raise Exception(f"API returned status {response.status_code}")
            
    except requests.exceptions.Timeout:
        raise Exception("Request timeout")
    except requests.exceptions.ConnectionError:
        raise Exception("Connection error")
    except Exception as e:
        # Silently fail to trigger demo mode fallback in app.py
        raise Exception(f"AI service unavailable: {str(e)}")


# Test function
if __name__ == '__main__':
    print("╔════════════════════════════════════════════════════════╗")
    print("║  KrishiShakti AI Chatbot Test                        ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == 'YOUR_API_KEY_HERE':
        print("❌ API key not configured!")
        print("\n📋 To setup:")
        print("   Run: python3 setup_openrouter.py")
        print("\n💡 Or get your free key at: https://openrouter.ai/keys")
        print("   Then edit ai_chat.py and replace 'YOUR_API_KEY_HERE'\n")
    else:
        # Test with sample data
        test_sensor_data = {
            'dht22': {'temperature': 15.0, 'humidity': 65.0},
            'fc28': {'value': 45.0},
            'mq135': {'value': 84.0},
            'pms5003': {'pm25': 35.0, 'pm10': 50.0},
            'location': {'city': 'Landran', 'country': 'India'}
        }
        
        test_question = "What should I do about my soil moisture?"
        
        print(f"📍 Location: {test_sensor_data['location']['city']}, {test_sensor_data['location']['country']}")
        print(f"🌡️  Temperature: {test_sensor_data['dht22']['temperature']}°C")
        print(f"💧 Humidity: {test_sensor_data['dht22']['humidity']}%")
        print(f"🌱 Soil Moisture: {test_sensor_data['fc28']['value']}%")
        print(f"\n❓ Question: {test_question}\n")
        print("🤖 AI Response:")
        print("-" * 60)
        
        try:
            response = ask_ai(test_question, test_sensor_data)
            print(response)
            print("-" * 60)
            print("\n✅ AI chatbot is working!")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("-" * 60)
            print("\n⚠️  AI not available, will use demo mode")
