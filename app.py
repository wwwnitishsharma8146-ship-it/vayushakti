from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import os
from datetime import datetime

# Import AI disease detection (optional - will use demo mode if not available)
try:
    from ai_disease_model import predict_disease
    AI_MODEL_AVAILABLE = True
    print("✅ AI Disease Detection Model loaded")
except Exception as e:
    AI_MODEL_AVAILABLE = False
    print(f"⚠️  AI Model not available: {str(e)}")
    print("   Using demo mode for disease detection")

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = 'krishishakti-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Google Sheets Integration (optional)
google_sheets_manager = None
try:
    from google_sheets_setup import GoogleSheetsManager
    google_sheets_manager = GoogleSheetsManager()
    if google_sheets_manager.connect():
        print("✅ Google Sheets connected!")
        print(f"📊 Spreadsheet: {google_sheets_manager.get_spreadsheet_url()}")
    else:
        google_sheets_manager = None
        print("⚠️  Google Sheets not configured (using local storage only)")
except Exception as e:
    google_sheets_manager = None
    print(f"⚠️  Google Sheets not available: {str(e)}")

# Store sensor data
sensor_data = {
    'mq135': {'value': 0, 'unit': 'ppm', 'name': 'Air Quality (MQ-135)'},
    'pms5003': {'pm25': 0, 'pm10': 0, 'unit': 'µg/m³', 'name': 'Particulate Matter (PMS5003)'},
    'dht22': {'temperature': 0, 'humidity': 0, 'name': 'Temperature & Humidity (DHT22)'},
    'fc28': {'value': 0, 'unit': '%', 'name': 'Water Tank Level (FC-28)'},
    'tds': {'value': 0, 'unit': 'ppm', 'name': 'Water Quality (TDS Sensor)'},
    'location': None,
    'timestamp': datetime.now().isoformat()
}

# Data directory
DATA_DIR = 'data'
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Load history
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_to_history(data):
    try:
        history = load_history()
        history.append(data)
        
        # Keep only last 1000 readings
        if len(history) > 1000:
            history = history[-1000:]
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f'Error saving history: {e}')

# Routes
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('public', path)

@app.route('/api/blynk-data', methods=['GET'])
def get_blynk_data():
    try:
        with open('krishi_shakti_data.json', 'r') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify({'error': 'No data yet, fetcher may not be running'}), 404

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    return jsonify(sensor_data)

@app.route('/api/sensors', methods=['POST'])
def update_sensors():
    global sensor_data
    data = request.json
    
    sensor_data = {
        'mq135': {'value': data.get('mq135', 0), 'unit': 'ppm', 'name': 'Air Quality (MQ-135)'},
        'pms5003': {'pm25': data.get('pm25', 0), 'pm10': data.get('pm10', 0), 'unit': 'µg/m³', 'name': 'Particulate Matter (PMS5003)'},
        'dht22': {'temperature': data.get('temperature', 0), 'humidity': data.get('humidity', 0), 'name': 'Temperature & Humidity (DHT22)'},
        'fc28': {'value': data.get('fc28', 0), 'unit': '%', 'name': 'Water Tank Level (FC-28)'},
        'tds': {'value': data.get('tds', 0), 'unit': 'ppm', 'name': 'Water Quality (TDS Sensor)'},
        'location': data.get('location'),
        'timestamp': datetime.now().isoformat()
    }
    
    # Save to history
    save_to_history(sensor_data)
    
    # Save to Google Sheets if available
    if google_sheets_manager:
        try:
            google_sheets_manager.add_sensor_data(sensor_data)
        except Exception as e:
            print(f"⚠️  Google Sheets error: {str(e)}")
    
    # Broadcast to WebSocket clients
    try:
        socketio.emit('sensor_update', sensor_data, broadcast=True)
    except:
        pass
    
    return jsonify({'success': True, 'data': sensor_data})

@app.route('/api/history', methods=['GET'])
def get_history():
    history = load_history()
    
    # Convert to format expected by frontend
    formatted_history = []
    for item in history[-100:]:  # Last 100 readings
        formatted_history.append({
            'timestamp': item.get('timestamp'),
            'mq135': item.get('mq135', {}).get('value', 0),
            'temperature': item.get('dht22', {}).get('temperature', 0),
            'humidity': item.get('dht22', {}).get('humidity', 0),
            'pm25': item.get('pms5003', {}).get('pm25', 0),
            'pm10': item.get('pms5003', {}).get('pm10', 0),
            'fc28': item.get('fc28', {}).get('value', 0),
            'tds': item.get('tds', {}).get('value', 0)
        })
    
    return jsonify(formatted_history)

@app.route('/api/sheets/data', methods=['GET'])
def get_sheets_data():
    # For now, return local history
    return get_history()

# AI Disease Prediction Endpoint
@app.route('/api/predict-disease', methods=['POST'])
def predict_disease_api():
    """
    AI-powered crop disease prediction from uploaded image
    Accepts: multipart/form-data with 'image' file
    Returns: JSON with disease prediction and recommendations
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided',
                'message': 'Please upload an image file'
            }), 400
        
        file = request.files['image']
        
        # Check if file is empty
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename',
                'message': 'Please select a valid image file'
            }), 400
        
        # Check file extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': 'Invalid file type',
                'message': f'Please upload an image file ({", ".join(allowed_extensions)})'
            }), 400
        
        # Use AI model if available, otherwise use demo mode
        if AI_MODEL_AVAILABLE:
            try:
                # Save file temporarily
                temp_path = os.path.join(DATA_DIR, 'temp_crop_image.jpg')
                file.save(temp_path)
                
                # Reset file pointer for model processing
                with open(temp_path, 'rb') as img_file:
                    result = predict_disease(img_file)
                
                # Clean up temp file
                try:
                    os.remove(temp_path)
                except:
                    pass
                
                return jsonify(result)
            except Exception as e:
                print(f"AI Model error: {str(e)}")
                import traceback
                traceback.print_exc()
                # Fall back to demo mode
                return get_demo_disease_prediction()
        else:
            # Demo mode - return simulated results
            return get_demo_disease_prediction()
            
    except Exception as e:
        print(f"Error in disease prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error processing image. Please try again.'
        }), 500

def get_demo_disease_prediction():
    """
    Demo mode disease prediction (when AI model is not available)
    Returns simulated results for testing
    """
    import random
    
    # Simulate different disease scenarios
    scenarios = [
        {
            "success": True,
            "disease": "Tomato - Healthy",
            "confidence": 94.5,
            "is_healthy": True,
            "recommendations": [
                "✅ Your crop appears healthy!",
                "Continue regular monitoring",
                "Maintain proper watering schedule",
                "Ensure adequate sunlight and nutrients"
            ]
        },
        {
            "success": True,
            "disease": "Tomato - Early Blight",
            "confidence": 87.3,
            "is_healthy": False,
            "recommendations": [
                "Remove infected leaves immediately",
                "Apply fungicide (Chlorothalonil or Mancozeb)",
                "Improve air circulation around plants",
                "Avoid overhead watering",
                "Rotate crops next season"
            ]
        },
        {
            "success": True,
            "disease": "Potato - Late Blight",
            "confidence": 91.2,
            "is_healthy": False,
            "recommendations": [
                "Remove and destroy infected plants",
                "Apply copper-based fungicide immediately",
                "Avoid working with wet plants",
                "Improve drainage in field",
                "Use resistant varieties next season"
            ]
        }
    ]
    
    # Return a random scenario for demo
    result = random.choice(scenarios)
    result['mode'] = 'demo'
    result['message'] = '⚠️ Demo Mode: Using simulated results. Upload plant_disease_model.h5 for real AI predictions.'
    
    return jsonify(result)


@app.route('/api/sheets/setup', methods=['POST'])
def setup_sheets():
    return jsonify({'success': False, 'message': 'Google Sheets not configured'})

# ChatGPT Chatbot endpoint
@app.route('/api/chatbot/message', methods=['POST'])
def chatbot_message():
    """Handle chatbot messages - AI-powered with Gemini API + Fallback to demo mode"""
    try:
        data = request.json
        user_message = data.get('message', '')
        sensor_data = data.get('sensorData', {})
        history = data.get('history', [])
        
        # Try AI-powered response first
        try:
            from ai_chat import ask_ai
            ai_response = ask_ai(user_message, sensor_data)
            return jsonify({'response': ai_response, 'mode': 'ai'})
        except Exception as ai_error:
            print(f'AI Error (falling back to demo mode): {str(ai_error)}')
            # Fallback to original demo chatbot if AI fails
            detected_lang = detect_language(user_message)
            demo_response = generate_demo_response(user_message, sensor_data, detected_lang)
            return jsonify({'response': demo_response, 'language': detected_lang, 'mode': 'demo'})
            
    except Exception as e:
        print(f'Chatbot error: {str(e)}')
        import traceback
        traceback.print_exc()
        # Even on error, return a helpful response in multiple languages
        return jsonify({
            'response': '🌾 I\'m here to help! / मैं मदद के लिए यहाँ हूँ! / ਮੈਂ ਮਦਦ ਲਈ ਇੱਥੇ ਹਾਂ!\n\nAsk me about farming in English, Hindi, or Punjabi!'
        })

def detect_language(text):
    """Detect language from text - supports Hindi, Punjabi, and English"""
    # Hindi Unicode range: \u0900-\u097F
    # Punjabi (Gurmukhi) Unicode range: \u0A00-\u0A7F
    
    hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
    punjabi_chars = sum(1 for char in text if '\u0A00' <= char <= '\u0A7F')
    
    if hindi_chars > 0:
        return 'hindi'
    elif punjabi_chars > 0:
        return 'punjabi'
    else:
        return 'english'

def generate_demo_response(message, sensor_data, language='english'):
    """Generate intelligent pollution-focused responses - Multi-language support (Hindi, Punjabi, English)"""
    message_lower = message.lower()
    
    # Extract sensor values
    temp = sensor_data.get('temperature', 25) if sensor_data else 25
    humidity = sensor_data.get('humidity', 60) if sensor_data else 60
    air_quality = sensor_data.get('airQuality', 100) if sensor_data else 100
    moisture = sensor_data.get('soilMoisture', 50) if sensor_data else 50
    tds = sensor_data.get('waterQuality', 300) if sensor_data else 300
    
    # Get translations
    t = get_translations(language)
    
    # Detect topic from keywords (works across languages)
    topic = detect_topic(message_lower, message)
    
    # Generate response based on topic
    if topic == 'sensor':
        return generate_sensor_response(temp, humidity, air_quality, moisture, tds, t)
    elif topic == 'health':
        return generate_health_response(temp, humidity, air_quality, moisture, t)
    elif topic == 'aqi':
        return generate_aqi_response(air_quality, t)
    elif topic == 'pm25':
        return generate_pm25_response(air_quality, t)
    elif topic == 'protection':
        return generate_protection_response(air_quality, t)
    elif topic == 'sources':
        return generate_sources_response(t)
    elif topic == 'temperature':
        return generate_temperature_response(temp, t)
    elif topic == 'humidity':
        return generate_humidity_response(humidity, t)
    elif topic == 'weather':
        return generate_weather_response(temp, humidity, t)
    elif topic == 'water':
        return generate_water_response(tds, temp, humidity, t)
    elif topic == 'indoor':
        return generate_indoor_response(air_quality, t)
    elif topic == 'environment':
        return generate_environment_response(t)
    else:
        return generate_general_response(temp, humidity, air_quality, t)

def detect_topic(message_lower, original_message):
    """Detect pollution-related topic from message - works with Hindi, Punjabi, English"""
    # Sensor readings
    if any(word in message_lower for word in ['sensor', 'reading', 'current', 'data', 'show me']):
        return 'sensor'
    if any(word in original_message for word in ['सेंसर', 'रीडिंग', 'डेटा', 'दिखाओ']):
        return 'sensor'
    if any(word in original_message for word in ['ਸੈਂਸਰ', 'ਰੀਡਿੰਗ', 'ਡਾਟਾ', 'ਦਿਖਾਓ']):
        return 'sensor'

    # Health risks
    if any(word in message_lower for word in ['health', 'sick', 'disease', 'symptom', 'lung', 'breathe', 'asthma', 'risk']):
        return 'health'
    if any(word in original_message for word in ['स्वास्थ्य', 'बीमारी', 'सांस', 'फेफड़े', 'खांसी']):
        return 'health'
    if any(word in original_message for word in ['ਸਿਹਤ', 'ਬਿਮਾਰੀ', 'ਸਾਹ', 'ਫੇਫੜੇ', 'ਖੰਘ']):
        return 'health'

    # AQI
    if any(word in message_lower for word in ['aqi', 'air quality', 'air quality index', 'pollution level']):
        return 'aqi'
    if any(word in original_message for word in ['वायु गुणवत्ता', 'एक्यूआई', 'प्रदूषण स्तर']):
        return 'aqi'
    if any(word in original_message for word in ['ਹਵਾ ਗੁਣਵੱਤਾ', 'ਏਕਿਊਆਈ', 'ਪ੍ਰਦੂਸ਼ਣ ਪੱਧਰ']):
        return 'aqi'

    # PM2.5 / particulate matter
    if any(word in message_lower for word in ['pm2.5', 'pm10', 'particulate', 'dust', 'smog', 'smoke']):
        return 'pm25'
    if any(word in original_message for word in ['धूल', 'धुआं', 'कण', 'स्मॉग']):
        return 'pm25'
    if any(word in original_message for word in ['ਧੂੜ', 'ਧੂੰਆਂ', 'ਕਣ', 'ਸਮੌਗ']):
        return 'pm25'

    # Protection / mask
    if any(word in message_lower for word in ['protect', 'mask', 'safe', 'precaution', 'avoid', 'outdoor']):
        return 'protection'
    if any(word in original_message for word in ['सुरक्षा', 'मास्क', 'बचाव', 'सावधानी']):
        return 'protection'
    if any(word in original_message for word in ['ਸੁਰੱਖਿਆ', 'ਮਾਸਕ', 'ਬਚਾਅ', 'ਸਾਵਧਾਨੀ']):
        return 'protection'

    # Sources of pollution
    if any(word in message_lower for word in ['source', 'cause', 'factory', 'vehicle', 'emission', 'industry']):
        return 'sources'
    if any(word in original_message for word in ['स्रोत', 'कारण', 'कारखाना', 'वाहन', 'उत्सर्जन']):
        return 'sources'
    if any(word in original_message for word in ['ਸਰੋਤ', 'ਕਾਰਨ', 'ਕਾਰਖਾਨਾ', 'ਵਾਹਨ', 'ਨਿਕਾਸ']):
        return 'sources'

    # Temperature
    if any(word in message_lower for word in ['hot', 'cold', 'temperature', 'heat', 'cool']):
        return 'temperature'
    if any(word in original_message for word in ['गर्मी', 'ठंड', 'तापमान']):
        return 'temperature'
    if any(word in original_message for word in ['ਗਰਮੀ', 'ਠੰਡ', 'ਤਾਪਮਾਨ']):
        return 'temperature'

    # Humidity
    if any(word in message_lower for word in ['humid', 'humidity', 'moisture', 'dry', 'wet']):
        return 'humidity'
    if any(word in original_message for word in ['नमी', 'आर्द्रता', 'सूखा']):
        return 'humidity'
    if any(word in original_message for word in ['ਨਮੀ', 'ਆਰਦਰਤਾ', 'ਸੁੱਕਾ']):
        return 'humidity'

    # Weather
    if any(word in message_lower for word in ['weather', 'rain', 'wind', 'forecast']):
        return 'weather'
    if any(word in original_message for word in ['मौसम', 'बारिश', 'हवा']):
        return 'weather'
    if any(word in original_message for word in ['ਮੌਸਮ', 'ਮੀਂਹ', 'ਹਵਾ']):
        return 'weather'

    # Water quality
    if any(word in message_lower for word in ['water', 'tds', 'drinking', 'contamina']):
        return 'water'
    if any(word in original_message for word in ['पानी', 'जल', 'पीने']):
        return 'water'
    if any(word in original_message for word in ['ਪਾਣੀ', 'ਜਲ', 'ਪੀਣ']):
        return 'water'

    # Indoor air quality
    if any(word in message_lower for word in ['indoor', 'inside', 'home', 'office', 'room', 'ventilat']):
        return 'indoor'
    if any(word in original_message for word in ['घर', 'अंदर', 'कमरा', 'वेंटिलेशन']):
        return 'indoor'
    if any(word in original_message for word in ['ਘਰ', 'ਅੰਦਰ', 'ਕਮਰਾ', 'ਹਵਾਦਾਰੀ']):
        return 'indoor'

    # Environment / green tips
    if any(word in message_lower for word in ['environment', 'green', 'tree', 'plant', 'reduce', 'improve']):
        return 'environment'
    if any(word in original_message for word in ['पर्यावरण', 'पेड़', 'हरियाली', 'सुधार']):
        return 'environment'
    if any(word in original_message for word in ['ਵਾਤਾਵਰਣ', 'ਰੁੱਖ', 'ਹਰਿਆਲੀ', 'ਸੁਧਾਰ']):
        return 'environment'

    return 'general'

def get_translations(language):
    """Get translation dictionary for the specified language - Pollution focused"""
    translations = {
        'english': {
            'sensor_title': '📊 **Current Sensor Readings:**',
            'temperature': 'Temperature',
            'humidity': 'Humidity',
            'air_quality': 'Air Quality (MQ-135)',
            'pm25': 'PM2.5',
            'pm10': 'PM10',
            'water_quality': 'Water Quality (TDS)',
            'optimal': 'Clean',
            'good': 'Good',
            'excellent': 'Excellent',
            'poor': 'Polluted',
            'low': 'Low',
            'high': 'High',
            'too_high': 'Hazardous',
            'too_low': 'Too low',
            'perfect': 'Safe',
            'pure': 'Pure',
            'health_title': '😷 **Health Risk Assessment:**',
            'excellent_condition': '✅ Air quality is excellent — safe for all activities!',
            'need_attention': '⚠️ Moderate pollution — sensitive groups should take care.',
            'immediate_care': '🚨 Dangerous pollution levels — take immediate precautions!',
            'current_status': '**Current Status:**',
            'aqi_title': '🌫️ **Air Quality Index (AQI):**',
            'pm25_title': '🔬 **Particulate Matter Analysis:**',
            'protection_title': '🛡️ **Protection Recommendations:**',
            'sources_title': '🏭 **Pollution Sources:**',
            'urgent': '� **URGENT:**',
            'stay_indoors': 'Stay indoors!',
            'temp_title': '🌡️ **Temperature & Pollution Impact:**',
            'humidity_title': '💧 **Humidity & Air Quality:**',
            'weather_title': '🌤️ **Weather & Pollution Forecast:**',
            'water_title': '💧 **Water Quality Analysis:**',
            'indoor_title': '🏠 **Indoor Air Quality:**',
            'environment_title': '� **Environmental Improvement Tips:**',
            'general_title': '�️ **Pollution Assistant:**',
        },
        'hindi': {
            'sensor_title': '📊 **वर्तमान सेंसर रीडिंग:**',
            'temperature': 'तापमान',
            'humidity': 'नमी',
            'air_quality': 'वायु गुणवत्ता (MQ-135)',
            'pm25': 'PM2.5',
            'pm10': 'PM10',
            'water_quality': 'पानी की गुणवत्ता (TDS)',
            'optimal': 'स्वच्छ',
            'good': 'अच्छा',
            'excellent': 'बेहतरीन',
            'poor': 'प्रदूषित',
            'low': 'कम',
            'high': 'ज्यादा',
            'too_high': 'खतरनाक',
            'too_low': 'बहुत कम',
            'perfect': 'सुरक्षित',
            'pure': 'शुद्ध',
            'health_title': '😷 **स्वास्थ्य जोखिम मूल्यांकन:**',
            'excellent_condition': '✅ वायु गुणवत्ता उत्कृष्ट है — सभी गतिविधियों के लिए सुरक्षित!',
            'need_attention': '⚠️ मध्यम प्रदूषण — संवेदनशील लोग सावधान रहें।',
            'immediate_care': '🚨 खतरनाक प्रदूषण स्तर — तुरंत सावधानी बरतें!',
            'current_status': '**वर्तमान स्थिति:**',
            'aqi_title': '�️ **वायु गुणवत्ता सूचकांक (AQI):**',
            'pm25_title': '� **कण पदार्थ विश्लेषण:**',
            'protection_title': '�️ **सुरक्षा सिफारिशें:**',
            'sources_title': '� **प्रदूषण के स्रोत:**',
            'urgent': '🚨 **जरूरी:**',
            'stay_indoors': 'घर के अंदर रहें!',
            'temp_title': '�️ **तापमान और प्रदूषण प्रभाव:**',
            'humidity_title': '💧 **नमी और वायु गुणवत्ता:**',
            'weather_title': '�️ **मौसम और प्रदूषण पूर्वानुमान:**',
            'water_title': '💧 **जल गुणवत्ता विश्लेषण:**',
            'indoor_title': '🏠 **इनडोर वायु गुणवत्ता:**',
            'environment_title': '🌱 **पर्यावरण सुधार सुझाव:**',
            'general_title': '🌫️ **प्रदूषण सहायक:**',
        },
        'punjabi': {
            'sensor_title': '📊 **ਮੌਜੂਦਾ ਸੈਂਸਰ ਰੀਡਿੰਗ:**',
            'temperature': 'ਤਾਪਮਾਨ',
            'humidity': 'ਨਮੀ',
            'air_quality': 'ਹਵਾ ਗੁਣਵੱਤਾ (MQ-135)',
            'pm25': 'PM2.5',
            'pm10': 'PM10',
            'water_quality': 'ਪਾਣੀ ਦੀ ਗੁਣਵੱਤਾ (TDS)',
            'optimal': 'ਸਾਫ਼',
            'good': 'ਚੰਗਾ',
            'excellent': 'ਬਹੁਤ ਵਧੀਆ',
            'poor': 'ਪ੍ਰਦੂਸ਼ਿਤ',
            'low': 'ਘੱਟ',
            'high': 'ਜ਼ਿਆਦਾ',
            'too_high': 'ਖ਼ਤਰਨਾਕ',
            'too_low': 'ਬਹੁਤ ਘੱਟ',
            'perfect': 'ਸੁਰੱਖਿਅਤ',
            'pure': 'ਸ਼ੁੱਧ',
            'health_title': '� **ਸਿਹਤ ਜੋਖਮ ਮੁਲਾਂਕਣ:**',
            'excellent_condition': '✅ ਹਵਾ ਦੀ ਗੁਣਵੱਤਾ ਸ਼ਾਨਦਾਰ ਹੈ — ਸਾਰੀਆਂ ਗਤੀਵਿਧੀਆਂ ਲਈ ਸੁਰੱਖਿਅਤ!',
            'need_attention': '⚠️ ਦਰਮਿਆਨਾ ਪ੍ਰਦੂਸ਼ਣ — ਸੰਵੇਦਨਸ਼ੀਲ ਲੋਕ ਸਾਵਧਾਨ ਰਹਿਣ।',
            'immediate_care': '🚨 ਖ਼ਤਰਨਾਕ ਪ੍ਰਦੂਸ਼ਣ ਪੱਧਰ — ਤੁਰੰਤ ਸਾਵਧਾਨੀ ਵਰਤੋ!',
            'current_status': '**ਮੌਜੂਦਾ ਸਥਿਤੀ:**',
            'aqi_title': '🌫️ **ਹਵਾ ਗੁਣਵੱਤਾ ਸੂਚਕਾਂਕ (AQI):**',
            'pm25_title': '🔬 **ਕਣ ਪਦਾਰਥ ਵਿਸ਼ਲੇਸ਼ਣ:**',
            'protection_title': '🛡️ **ਸੁਰੱਖਿਆ ਸਿਫਾਰਸ਼ਾਂ:**',
            'sources_title': '� **ਪ੍ਰਦੂਸ਼ਣ ਦੇ ਸਰੋਤ:**',
            'urgent': '🚨 **ਜ਼ਰੂਰੀ:**',
            'stay_indoors': 'ਘਰ ਦੇ ਅੰਦਰ ਰਹੋ!',
            'temp_title': '�️ **ਤਾਪਮਾਨ ਅਤੇ ਪ੍ਰਦੂਸ਼ਣ ਪ੍ਰਭਾਵ:**',
            'humidity_title': '💧 **ਨਮੀ ਅਤੇ ਹਵਾ ਗੁਣਵੱਤਾ:**',
            'weather_title': '�️ **ਮੌਸਮ ਅਤੇ ਪ੍ਰਦੂਸ਼ਣ ਪੂਰਵ-ਅਨੁਮਾਨ:**',
            'water_title': '💧 **ਜਲ ਗੁਣਵੱਤਾ ਵਿਸ਼ਲੇਸ਼ਣ:**',
            'indoor_title': '🏠 **ਅੰਦਰੂਨੀ ਹਵਾ ਗੁਣਵੱਤਾ:**',
            'environment_title': '🌱 **ਵਾਤਾਵਰਣ ਸੁਧਾਰ ਸੁਝਾਅ:**',
            'general_title': '🌫️ **ਪ੍ਰਦੂਸ਼ਣ ਸਹਾਇਕ:**',
        }
    }
    return translations.get(language, translations['english'])

def generate_sensor_response(temp, humidity, air_quality, moisture, tds, t):
    """Generate comprehensive sensor reading response with detailed analysis"""
    response = f"{t['sensor_title']}\n\n"
    
    # Temperature analysis
    response += f"🌡️ {t['temperature']}: {temp}°C - "
    if 20 <= temp <= 30:
        response += f"{t['optimal']}\n   ✓ Perfect for most crops\n   ✓ Good photosynthesis rate\n   ✓ Optimal enzyme activity\n"
    elif temp > 35:
        response += f"{t['too_high']}\n   ⚠️ Heat stress risk - provide shade\n   ⚠️ Increase watering frequency\n   ⚠️ Mist leaves in extreme heat\n   ⚠️ Mulch to keep roots cool\n"
    elif temp > 30:
        response += f"{t['too_high']}\n   ⚠️ Monitor for heat stress\n   ⚠️ Water early morning/evening\n   ⚠️ Consider shade cloth (30-50%)\n"
    elif temp < 15:
        response += f"{t['too_low']}\n   ❄️ Cold stress risk - protect plants\n   ❄️ Use row covers/plastic tunnels\n   ❄️ Reduce watering frequency\n   ❄️ Protect from frost\n"
    elif temp < 20:
        response += f"{t['too_low']}\n   ⚠️ Slow growth expected\n   ⚠️ Reduce fertilizer application\n   ⚠️ Water in morning only\n"
    
    # Humidity analysis
    response += f"\n💧 {t['humidity']}: {humidity}% - "
    if 50 <= humidity <= 70:
        response += f"{t['good']}\n   ✓ Ideal for plant growth\n   ✓ Low disease risk\n   ✓ Good transpiration rate\n"
    elif humidity > 80:
        response += f"{t['high']}\n   ⚠️ High fungal disease risk\n   ⚠️ Improve air circulation\n   ⚠️ Reduce watering frequency\n   ⚠️ Apply preventive fungicide\n   ⚠️ Remove dense foliage\n"
    elif humidity > 70:
        response += f"{t['high']}\n   ⚠️ Monitor for fungal diseases\n   ⚠️ Ensure good ventilation\n   ⚠️ Avoid overhead watering\n"
    elif humidity < 40:
        response += f"{t['low']}\n   ⚠️ Increase watering\n   ⚠️ Mist leaves regularly\n   ⚠️ Use mulch to retain moisture\n   ⚠️ Group plants together\n"
    elif humidity < 50:
        response += f"{t['low']}\n   ⚠️ Monitor plant stress\n   ⚠️ Water more frequently\n   ⚠️ Consider misting\n"
    
    # Air quality analysis
    response += f"\n🌿 {t['air_quality']}: {air_quality} ppm - "
    if air_quality < 100:
        response += f"{t['excellent']}\n   ✓ Clean air, healthy environment\n   ✓ Good for plant respiration\n   ✓ No air pollution stress\n"
    elif air_quality < 150:
        response += f"{t['good']}\n   ✓ Acceptable air quality\n   ✓ Minor impact on plants\n   ⚠️ Monitor sensitive crops\n"
    elif air_quality < 200:
        response += f"{t['poor']}\n   ⚠️ Moderate pollution\n   ⚠️ May affect sensitive plants\n   ⚠️ Increase ventilation\n   ⚠️ Consider air purifying plants\n"
    else:
        response += f"{t['poor']}\n   🚨 High pollution levels\n   🚨 Serious plant stress risk\n   🚨 Improve ventilation urgently\n   🚨 Use air filters if indoor\n   🚨 Relocate sensitive plants\n"
    
    # Soil moisture analysis
    response += f"\n💦 {t['soil_moisture']}: {moisture}% - "
    if 50 <= moisture <= 70:
        response += f"{t['perfect']}\n   ✓ Optimal moisture level\n   ✓ Good root health\n   ✓ Efficient nutrient uptake\n   ✓ Continue current schedule\n"
    elif moisture < 30:
        response += f"{t['low']}\n   🚨 URGENT: Water immediately!\n   🚨 Deep watering needed (15-20 min)\n   🚨 Water early morning (6-8 AM)\n   🚨 Apply 20-25mm water\n   🚨 Check again in 6 hours\n   🚨 Mulch to retain moisture\n"
    elif moisture < 50:
        response += f"{t['low']}\n   ⚠️ Water within 4-6 hours\n   ⚠️ Apply 15-20mm water\n   ⚠️ Water early morning\n   ⚠️ Avoid midday watering\n   ⚠️ Monitor daily\n"
    elif moisture > 80:
        response += f"{t['high']}\n   ⚠️ Overwatering risk\n   ⚠️ Stop watering for 2-3 days\n   ⚠️ Improve drainage\n   ⚠️ Check for root rot\n   ⚠️ Reduce watering frequency\n"
    elif moisture > 70:
        response += f"{t['high']}\n   ⚠️ Slightly too wet\n   ⚠️ Skip next watering\n   ⚠️ Ensure good drainage\n   ⚠️ Monitor for fungal issues\n"
    
    # Water quality analysis
    response += f"\n🚰 {t['water_quality']}: {tds} ppm TDS - "
    if tds < 300:
        response += f"{t['pure']}\n   ✓ Excellent water quality\n   ✓ Safe for all crops\n   ✓ Low salt content\n   ✓ Good for irrigation\n"
    elif tds < 500:
        response += f"{t['good']}\n   ✓ Acceptable for most crops\n   ⚠️ Monitor salt-sensitive plants\n   ⚠️ Flush soil occasionally\n"
    elif tds < 800:
        response += f"{t['high']}\n   ⚠️ High mineral content\n   ⚠️ May affect sensitive crops\n   ⚠️ Flush soil with clean water\n   ⚠️ Consider water treatment\n   ⚠️ Monitor for salt buildup\n"
    else:
        response += f"{t['high']}\n   🚨 Very high TDS - not suitable\n   🚨 Use alternative water source\n   🚨 Install water filter\n   🚨 Flush soil thoroughly\n   🚨 May cause nutrient lockout\n"
    
    # Overall assessment
    response += f"\n\n📊 **Overall Assessment:**\n"
    issues = []
    if temp < 20 or temp > 30:
        issues.append("Temperature")
    if humidity < 50 or humidity > 70:
        issues.append("Humidity")
    if moisture < 50:
        issues.append("Soil Moisture")
    if air_quality > 150:
        issues.append("Air Quality")
    if tds > 500:
        issues.append("Water Quality")
    
    if not issues:
        response += "✅ All parameters are optimal! Your crops are in excellent condition.\n"
        response += "Continue current management practices."
    else:
        response += f"⚠️ Attention needed: {', '.join(issues)}\n"
        response += "Take corrective actions as recommended above."
    
    return response

def generate_health_response(temp, humidity, air_quality, moisture, t):
    """Generate comprehensive crop health response"""
    score = 100
    issues = []
    
    if temp < 20 or temp > 30:
        score -= 15
        issues.append(f"Temperature ({temp}°C)")
    if humidity < 50 or humidity > 70:
        score -= 10
        issues.append(f"Humidity ({humidity}%)")
    if moisture < 50:
        score -= 20
        issues.append(f"Soil Moisture ({moisture}%)")
    if air_quality > 150:
        score -= 10
        issues.append(f"Air Quality ({air_quality} ppm)")
    
    response = f"{t['health_title']} {score}/100**\n\n"
    
    if score >= 80:
        response += f"{t['excellent_condition']}\n\n"
        response += "**Why your crops are thriving:**\n"
        response += "✓ Optimal environmental conditions\n"
        response += "✓ Good water and nutrient availability\n"
        response += "✓ Low stress factors\n"
        response += "✓ Healthy root development\n"
        response += "✓ Strong disease resistance\n\n"
        response += "**Keep doing:**\n"
        response += "• Regular monitoring (2-3 times weekly)\n"
        response += "• Consistent watering schedule\n"
        response += "• Weekly pest inspections\n"
        response += "• Balanced fertilizer application\n"
        response += "• Remove dead/yellowing leaves\n"
        response += "• Maintain good air circulation\n\n"
        response += "**Expected outcomes:**\n"
        response += "• Vigorous growth\n"
        response += "• High yield potential\n"
        response += "• Good fruit/flower quality\n"
        response += "• Strong pest resistance\n"
    elif score >= 60:
        response += f"{t['need_attention']}\n\n"
        response += f"**Issues detected:** {', '.join(issues)}\n\n"
        response += "**Immediate actions:**\n"
        if temp > 30:
            response += "🌡️ Temperature: Provide shade, increase watering\n"
        if temp < 20:
            response += "🌡️ Temperature: Use covers, reduce watering\n"
        if moisture < 40:
            response += "💧 Moisture: Water immediately, deep watering needed\n"
        if moisture < 50:
            response += "💧 Moisture: Water within 6 hours\n"
        if humidity < 50:
            response += "💨 Humidity: Mist leaves, use mulch\n"
        if humidity > 70:
            response += "💨 Humidity: Improve ventilation, reduce watering\n"
        if air_quality > 150:
            response += "🌿 Air Quality: Improve ventilation, check pollution sources\n"
        response += "\n**Recovery plan:**\n"
        response += "• Day 1-2: Address immediate issues\n"
        response += "• Day 3-5: Monitor improvements\n"
        response += "• Day 6-7: Adjust care routine\n"
        response += "• Week 2: Reassess health score\n\n"
        response += "**Expected recovery:** 7-14 days with proper care\n"
    else:
        response += f"{t['immediate_care']}\n\n"
        response += f"**Critical issues:** {', '.join(issues)}\n\n"
        response += "🚨 **URGENT ACTIONS REQUIRED:**\n"
        if moisture < 30:
            response += "1. Water immediately - deep watering for 15-20 minutes\n"
        if temp > 35:
            response += "2. Provide immediate shade - use cloth/net\n"
        if temp < 15:
            response += "2. Protect from cold - use covers/tunnels\n"
        if humidity > 80:
            response += "3. Improve air circulation - prune dense foliage\n"
        if air_quality > 200:
            response += "4. Relocate plants if possible - improve ventilation\n"
        response += "\n**Emergency care:**\n"
        response += "• Check plants every 4-6 hours\n"
        response += "• Document changes with photos\n"
        response += "• Be prepared to take drastic measures\n"
        response += "• Consider consulting agricultural expert\n"
        response += "• Remove severely damaged plants\n\n"
        response += "**Warning:** Without immediate action, crop loss is likely!\n"
    
    return response

def generate_water_response(moisture, temp, humidity, t):
    """Generate comprehensive irrigation advice"""
    response = f"{t['water_title']}\n\n"
    
    # Calculate evapotranspiration rate
    et_rate = 0.5  # Base rate
    if temp > 30:
        et_rate += 0.3
    if humidity < 50:
        et_rate += 0.2
    
    # Current status
    if moisture < 30:
        response += f"{t['urgent']} {t['soil_moisture']} {moisture}% - {t['water_now']}\n\n"
        response += "**IMMEDIATE WATERING PROTOCOL:**\n"
        response += f"💧 Amount: 20-25mm (2-2.5 liters per sq meter)\n"
        response += "⏰ Time: NOW - Early morning (6-8 AM) is best\n"
        response += "⏱️ Duration: 15-20 minutes deep watering\n"
        response += "🔄 Method: Drip irrigation or soil-level watering\n"
        response += "📍 Focus: Root zone, avoid leaves\n\n"
        response += "**After watering:**\n"
        response += "• Check soil moisture in 6 hours\n"
        response += "• Apply mulch (5-7cm thick)\n"
        response += "• Monitor for wilting recovery\n"
        response += "• Adjust schedule based on response\n\n"
        response += "**Next 3 days:**\n"
        response += "• Day 1: Water deeply (done)\n"
        response += "• Day 2: Check moisture, water if below 40%\n"
        response += "• Day 3: Establish regular schedule\n"
    elif moisture < 50:
        response += f"⚠️ {t['soil_moisture']} {moisture}% - Water within 4-6 hours\n\n"
        response += "**WATERING SCHEDULE:**\n"
        response += f"💧 Amount: 15-20mm (1.5-2 liters per sq meter)\n"
        response += "⏰ Best time: Early morning (6-8 AM)\n"
        response += "⏱️ Duration: 10-15 minutes\n"
        response += "🔄 Method: Drip or soil-level watering\n\n"
        response += "**Watering tips:**\n"
        response += "• Water slowly for deep penetration\n"
        response += "• Avoid overhead watering (disease risk)\n"
        response += "• Water at soil level, not on leaves\n"
        response += "• Use mulch to retain moisture\n"
        response += "• Check soil 10cm deep before watering\n\n"
        response += "**Frequency guide:**\n"
        response += f"• Current temp: {temp}°C, Humidity: {humidity}%\n"
        response += f"• Estimated ET rate: {et_rate:.1f}mm/day\n"
        response += f"• Recommended: Water every {int(20/et_rate)} days\n"
    else:
        response += f"✅ {t['soil_moisture']} {moisture}% - {t['good']}!\n\n"
        response += "**MAINTENANCE SCHEDULE:**\n"
        response += f"💧 Amount: 10-15mm (1-1.5 liters per sq meter)\n"
        response += f"⏰ Next watering: In {int(30/et_rate)} days\n"
        response += "⏱️ Duration: 8-12 minutes\n"
        response += "🔄 Method: Continue current method\n\n"
        response += "**Monitoring:**\n"
        response += "• Check soil moisture daily\n"
        response += "• Water when moisture drops below 50%\n"
        response += "• Adjust based on weather changes\n"
        response += "• Increase frequency in hot weather\n"
        response += "• Reduce frequency in cool/rainy weather\n\n"
        response += "**Signs you need to water:**\n"
        response += "• Soil feels dry 5-10cm deep\n"
        response += "• Leaves start to droop slightly\n"
        response += "• Soil pulls away from pot edges\n"
        response += "• Lighter soil color\n"
    
    # Environmental factors
    response += f"\n**Environmental factors:**\n"
    response += f"🌡️ Temperature: {temp}°C - "
    if temp > 30:
        response += "High (increase watering by 30%)\n"
    elif temp < 20:
        response += "Low (reduce watering by 20%)\n"
    else:
        response += "Optimal (maintain schedule)\n"
    
    response += f"💨 Humidity: {humidity}% - "
    if humidity < 50:
        response += "Low (water more frequently)\n"
    elif humidity > 70:
        response += "High (reduce watering)\n"
    else:
        response += "Good (maintain schedule)\n"
    
    # Water quality tips
    response += "\n**Water quality tips:**\n"
    response += "• Use room temperature water\n"
    response += "• Let tap water sit 24hrs (chlorine evaporation)\n"
    response += "• Rainwater is best (if available)\n"
    response += "• Avoid hard water (high minerals)\n"
    response += "• pH should be 6.0-7.0\n"
    
    return response

def generate_fertilizer_response(t):
    """Generate comprehensive fertilizer advice"""
    response = f"{t.get('fertilizer_title', '🌿 **Fertilizer Recommendation:**')}\n\n"
    
    response += "**RECOMMENDED FERTILIZERS:**\n\n"
    response += "**1. Balanced NPK (10-10-10 or 20-20-20)**\n"
    response += "   • Best for: General purpose, all crops\n"
    response += "   • Amount: 50-100 kg per hectare OR 5-10g per plant\n"
    response += "   • Frequency: Every 4-6 weeks\n"
    response += "   • Cost: ₹300-600 per application\n\n"
    
    response += "**2. Nitrogen-Rich (Urea 46-0-0)**\n"
    response += "   • Best for: Leafy vegetables, vegetative growth\n"
    response += "   • Amount: 50-75 kg per hectare OR 5-7g per plant\n"
    response += "   • Frequency: Every 3-4 weeks during growth\n"
    response += "   • Cost: ₹200-400 per application\n"
    response += "   • Warning: Don't over-apply (causes burning)\n\n"
    
    response += "**3. Phosphorus-Rich (DAP 18-46-0)**\n"
    response += "   • Best for: Root development, flowering\n"
    response += "   • Amount: 40-60 kg per hectare OR 4-6g per plant\n"
    response += "   • Frequency: At planting, then every 6-8 weeks\n"
    response += "   • Cost: ₹250-500 per application\n\n"
    
    response += "**4. Potassium-Rich (MOP 0-0-60)**\n"
    response += "   • Best for: Fruit development, disease resistance\n"
    response += "   • Amount: 30-50 kg per hectare OR 3-5g per plant\n"
    response += "   • Frequency: During fruiting stage\n"
    response += "   • Cost: ₹200-400 per application\n\n"
    
    response += "**ORGANIC OPTIONS:**\n\n"
    response += "**1. Compost**\n"
    response += "   • Amount: 2-3 kg per plant\n"
    response += "   • Application: Mix into soil, top dressing\n"
    response += "   • Frequency: Every 2-3 months\n"
    response += "   • Benefits: Improves soil structure, slow release\n"
    response += "   • Cost: ₹100-200 per application\n\n"
    
    response += "**2. Vermicompost**\n"
    response += "   • Amount: 1-2 kg per plant\n"
    response += "   • Application: Top dressing, soil mix\n"
    response += "   • Frequency: Every 6-8 weeks\n"
    response += "   • Benefits: Rich in microorganisms, NPK\n"
    response += "   • Cost: ₹150-300 per application\n\n"
    
    response += "**3. Cow Manure**\n"
    response += "   • Amount: 3-5 kg per plant (well-rotted)\n"
    response += "   • Application: Mix into soil before planting\n"
    response += "   • Frequency: Once per season\n"
    response += "   • Benefits: Slow release, soil conditioning\n"
    response += "   • Cost: ₹50-150 per application\n\n"
    
    response += "**APPLICATION METHOD:**\n"
    response += "1. **Broadcasting:** Spread evenly around plant base\n"
    response += "2. **Side Dressing:** Apply 10-15cm away from stem\n"
    response += "3. **Foliar Spray:** Dilute and spray on leaves (quick results)\n"
    response += "4. **Drip Irrigation:** Mix water-soluble fertilizer\n\n"
    
    response += "**TIMING:**\n"
    response += "• Best time: Early morning (6-8 AM) or late evening (5-7 PM)\n"
    response += "• Avoid: Hot midday sun (causes burning)\n"
    response += "• After rain: Wait 1-2 days\n"
    response += "• Before rain: Avoid (fertilizer washes away)\n\n"
    
    response += "**IMPORTANT TIPS:**\n"
    response += "✓ Always water after fertilizer application\n"
    response += "✓ Apply to moist soil (never dry soil)\n"
    response += "✓ Keep fertilizer away from stem (5-10cm)\n"
    response += "✓ Use split doses (half now, half after 2 weeks)\n"
    response += "✓ Soil test every 6 months for accuracy\n"
    response += "✗ Don't over-fertilize (causes toxicity)\n"
    response += "✗ Don't apply to stressed plants\n"
    response += "✗ Don't mix incompatible fertilizers\n\n"
    
    response += "**SIGNS OF DEFICIENCY:**\n"
    response += "• Nitrogen: Yellow older leaves, slow growth\n"
    response += "• Phosphorus: Purple leaves, poor root growth\n"
    response += "• Potassium: Brown leaf edges, weak stems\n"
    response += "• Calcium: Blossom end rot, tip burn\n"
    response += "• Magnesium: Yellow between leaf veins\n"
    
    return response

def generate_pest_response(t):
    """Generate comprehensive pest control advice"""
    response = f"{t.get('pest_title', '🐛 **Pest Control Guide:**')}\n\n"
    
    response += "**COMMON PESTS & IDENTIFICATION:**\n\n"
    response += "**1. 🦗 Aphids (Chepti/ਚੇਪੀ)**\n"
    response += "   • Appearance: Small (1-3mm), green/black/brown insects\n"
    response += "   • Location: Undersides of leaves, new growth\n"
    response += "   • Damage: Curled leaves, sticky honeydew, stunted growth\n"
    response += "   • Severity: Moderate to High\n\n"
    
    response += "**2. 🐛 Caterpillars (Suundi/ਸੂੰਡੀ)**\n"
    response += "   • Appearance: Green/brown worms, 2-5cm long\n"
    response += "   • Location: On leaves, stems, fruits\n"
    response += "   • Damage: Large holes in leaves, eaten fruits\n"
    response += "   • Severity: High\n\n"
    
    response += "**3. 🦟 Whiteflies (Safed Makhi/ਸਫੇਦ ਮੱਖੀ)**\n"
    response += "   • Appearance: Tiny white flying insects\n"
    response += "   • Location: Undersides of leaves\n"
    response += "   • Damage: Yellow leaves, sooty mold, virus transmission\n"
    response += "   • Severity: Moderate to High\n\n"
    
    response += "**4. 🕷️ Spider Mites (Laal Makdi/ਲਾਲ ਮੱਕੜੀ)**\n"
    response += "   • Appearance: Tiny red/brown dots, fine webbing\n"
    response += "   • Location: Undersides of leaves\n"
    response += "   • Damage: Stippled leaves, yellowing, webbing\n"
    response += "   • Severity: Moderate\n\n"
    
    response += "**5. 🪲 Beetles (Bhringraj/ਭ੍ਰਿੰਗਰਾਜ)**\n"
    response += "   • Appearance: Hard-shelled insects, various colors\n"
    response += "   • Location: Leaves, flowers, fruits\n"
    response += "   • Damage: Holes in leaves, eaten flowers\n"
    response += "   • Severity: Moderate\n\n"
    
    response += "**NATURAL CONTROL METHODS:**\n\n"
    response += "**1. Neem Oil Spray (Most Effective)**\n"
    response += "   Recipe: 10ml neem oil + 5ml liquid soap + 1 liter water\n"
    response += "   • Application: Spray thoroughly, especially undersides\n"
    response += "   • Frequency: Every 7-10 days\n"
    response += "   • Best time: Evening (avoid hot sun)\n"
    response += "   • Effective against: Aphids, whiteflies, mites, caterpillars\n"
    response += "   • Cost: ₹100-200 per bottle (multiple uses)\n\n"
    
    response += "**2. Garlic-Chili Spray**\n"
    response += "   Recipe: 10 garlic cloves + 5 chilies + 1 liter water\n"
    response += "   • Preparation: Blend, strain, add soap\n"
    response += "   • Application: Spray on affected areas\n"
    response += "   • Frequency: Every 5-7 days\n"
    response += "   • Effective against: Aphids, caterpillars, beetles\n"
    response += "   • Cost: ₹20-50 per batch\n\n"
    
    response += "**3. Soap Water Spray**\n"
    response += "   Recipe: 5ml dish soap + 1 liter water\n"
    response += "   • Application: Spray directly on pests\n"
    response += "   • Frequency: Every 3-5 days\n"
    response += "   • Effective against: Aphids, whiteflies, mites\n"
    response += "   • Cost: ₹10-20 per batch\n\n"
    
    response += "**4. Manual Removal**\n"
    response += "   • Method: Hand-pick visible pests\n"
    response += "   • Best for: Caterpillars, beetles, large insects\n"
    response += "   • Frequency: Daily inspection\n"
    response += "   • Time: Early morning (pests less active)\n"
    response += "   • Dispose: Drop in soapy water\n\n"
    
    response += "**CHEMICAL OPTIONS (If Natural Methods Fail):**\n\n"
    response += "**1. Imidacloprid (Systemic)**\n"
    response += "   • Dosage: 0.5ml per liter water\n"
    response += "   • Application: Soil drench or spray\n"
    response += "   • Effective against: Aphids, whiteflies, beetles\n"
    response += "   • Harvest wait: 7-14 days\n"
    response += "   • Cost: ₹200-400\n\n"
    
    response += "**2. Malathion (Contact)**\n"
    response += "   • Dosage: 2ml per liter water\n"
    response += "   • Application: Thorough spray\n"
    response += "   • Effective against: Most insects\n"
    response += "   • Harvest wait: 7 days\n"
    response += "   • Cost: ₹150-300\n\n"
    
    response += "**3. Spinosad (Organic-approved)**\n"
    response += "   • Dosage: As per label\n"
    response += "   • Application: Spray on affected areas\n"
    response += "   • Effective against: Caterpillars, beetles\n"
    response += "   • Harvest wait: 1-3 days\n"
    response += "   • Cost: ₹300-500\n\n"
    
    response += "**BENEFICIAL INSECTS (Natural Predators):**\n"
    response += "🐞 Ladybugs: Eat 50-100 aphids per day (₹500-1000 for 100)\n"
    response += "🦗 Praying Mantis: Eat various insects (₹200-400 each)\n"
    response += "🕷️ Spiders: Natural pest control (encourage, don't kill)\n"
    response += "🐝 Parasitic Wasps: Attack caterpillars, aphids (₹300-600)\n"
    response += "💚 Green Lacewings: Larvae eat aphids, mites (₹400-800)\n\n"
    
    response += "**PREVENTION STRATEGIES:**\n"
    response += "✓ Inspect plants 2-3 times weekly\n"
    response += "✓ Remove dead leaves and debris\n"
    response += "✓ Maintain proper plant spacing (air circulation)\n"
    response += "✓ Use yellow sticky traps (₹50-100 per trap)\n"
    response += "✓ Companion planting (marigolds, basil repel pests)\n"
    response += "✓ Rotate crops annually\n"
    response += "✓ Keep area weed-free\n"
    response += "✓ Use row covers for protection\n"
    response += "✓ Encourage birds (natural predators)\n\n"
    
    response += "**TREATMENT SCHEDULE:**\n"
    response += "Day 1: Identify pest, apply first treatment\n"
    response += "Day 3: Check for improvement, hand-pick remaining pests\n"
    response += "Day 5: Second treatment application\n"
    response += "Day 7: Assess results, continue if needed\n"
    response += "Day 10: Third treatment (if necessary)\n"
    response += "Day 14: Final assessment, switch method if no improvement\n"
    
    return response

def generate_disease_response(t):
    """Generate comprehensive disease management advice"""
    response = f"{t.get('disease_title', '🔬 **Plant Disease Guide:**')}\n\n"
    
    response += "**COMMON PLANT DISEASES:**\n\n"
    response += "**1. FUNGAL DISEASES (Most Common - 70% of diseases)**\n\n"
    response += "**A. Early Blight (Alternaria)**\n"
    response += "   • Symptoms: Dark brown spots with concentric rings on leaves\n"
    response += "   • Affected crops: Tomatoes, potatoes, peppers\n"
    response += "   • Conditions: Warm (24-29°C), humid weather\n"
    response += "   • Treatment: Copper fungicide, remove infected leaves\n"
    response += "   • Prevention: Crop rotation, avoid overhead watering\n\n"
    
    response += "**B. Powdery Mildew**\n"
    response += "   • Symptoms: White powdery coating on leaves\n"
    response += "   • Affected crops: Cucurbits, roses, grapes\n"
    response += "   • Conditions: Moderate temp (20-25°C), high humidity\n"
    response += "   • Treatment: Sulfur spray, baking soda solution\n"
    response += "   • Prevention: Good air circulation, resistant varieties\n\n"
    
    response += "**C. Downy Mildew**\n"
    response += "   • Symptoms: Yellow patches on top, gray fuzz underneath\n"
    response += "   • Affected crops: Cucumbers, lettuce, grapes\n"
    response += "   • Conditions: Cool (15-20°C), wet conditions\n"
    response += "   • Treatment: Copper fungicide, improve drainage\n"
    response += "   • Prevention: Avoid wet leaves, use resistant varieties\n\n"
    
    response += "**D. Root Rot (Pythium, Phytophthora)**\n"
    response += "   • Symptoms: Wilting, yellowing, soft brown roots\n"
    response += "   • Affected crops: Most plants, especially in wet soil\n"
    response += "   • Conditions: Overwatering, poor drainage\n"
    response += "   • Treatment: Improve drainage, reduce watering, fungicide drench\n"
    response += "   • Prevention: Well-draining soil, proper watering\n\n"
    
    response += "**2. BACTERIAL DISEASES (15% of diseases)**\n\n"
    response += "**A. Bacterial Wilt**\n"
    response += "   • Symptoms: Sudden wilting, slimy stem interior\n"
    response += "   • Affected crops: Tomatoes, cucurbits, potatoes\n"
    response += "   • Spread: Insects, contaminated tools\n"
    response += "   • Treatment: Remove infected plants immediately\n"
    response += "   • Prevention: Control insects, disinfect tools\n\n"
    
    response += "**B. Bacterial Leaf Spot**\n"
    response += "   • Symptoms: Small dark spots with yellow halos\n"
    response += "   • Affected crops: Peppers, tomatoes, beans\n"
    response += "   • Spread: Water splash, contaminated seeds\n"
    response += "   • Treatment: Copper spray, remove infected leaves\n"
    response += "   • Prevention: Avoid overhead watering, use clean seeds\n\n"
    
    response += "**3. VIRAL DISEASES (10% of diseases)**\n\n"
    response += "**A. Mosaic Virus**\n"
    response += "   • Symptoms: Mottled yellow-green patterns on leaves\n"
    response += "   • Affected crops: Tomatoes, cucumbers, peppers\n"
    response += "   • Spread: Aphids, contaminated tools\n"
    response += "   • Treatment: NO CURE - remove infected plants\n"
    response += "   • Prevention: Control aphids, use resistant varieties\n\n"
    
    response += "**B. Leaf Curl Virus**\n"
    response += "   • Symptoms: Curled, distorted leaves, stunted growth\n"
    response += "   • Affected crops: Tomatoes, chili, papaya\n"
    response += "   • Spread: Whiteflies\n"
    response += "   • Treatment: NO CURE - remove infected plants\n"
    response += "   • Prevention: Control whiteflies, use resistant varieties\n\n"
    
    response += "**TREATMENT OPTIONS:**\n\n"
    response += "**Fungicides:**\n"
    response += "1. Copper-based (Bordeaux mixture, Copper oxychloride)\n"
    response += "   • Dosage: 2-3g per liter water\n"
    response += "   • Application: Spray every 7-10 days\n"
    response += "   • Cost: ₹200-400 per treatment\n\n"
    
    response += "2. Sulfur-based (Wettable sulfur)\n"
    response += "   • Dosage: 2-3g per liter water\n"
    response += "   • Application: Spray every 7-14 days\n"
    response += "   • Cost: ₹150-300 per treatment\n\n"
    
    response += "3. Systemic fungicides (Carbendazim, Mancozeb)\n"
    response += "   • Dosage: As per label instructions\n"
    response += "   • Application: Spray or soil drench\n"
    response += "   • Cost: ₹300-600 per treatment\n\n"
    
    response += "**Natural Remedies:**\n"
    response += "1. Baking Soda Spray: 5g baking soda + 5ml oil + 1L water\n"
    response += "2. Milk Spray: 1 part milk + 9 parts water (powdery mildew)\n"
    response += "3. Garlic Extract: Blend 10 cloves in 1L water, strain\n"
    response += "4. Neem Oil: 10ml + 5ml soap + 1L water\n\n"
    
    response += "**PREVENTION IS KEY:**\n"
    response += "✓ Choose disease-resistant varieties\n"
    response += "✓ Rotate crops every season (3-year rotation)\n"
    response += "✓ Maintain proper plant spacing (30-60cm)\n"
    response += "✓ Water at soil level, avoid wetting leaves\n"
    response += "✓ Water in morning (leaves dry during day)\n"
    response += "✓ Remove infected plant parts immediately\n"
    response += "✓ Disinfect tools between plants (10% bleach solution)\n"
    response += "✓ Improve air circulation (prune dense foliage)\n"
    response += "✓ Mulch to prevent soil splash\n"
    response += "✓ Don't work with wet plants\n"
    response += "✓ Remove plant debris at season end\n"
    response += "✓ Use clean, certified seeds\n\n"
    
    response += "**WHEN TO TAKE ACTION:**\n"
    response += "🟢 Early stage (few spots): Natural remedies, remove affected parts\n"
    response += "🟡 Moderate (spreading): Fungicide treatment, increase frequency\n"
    response += "🔴 Severe (widespread): Systemic fungicide, consider removing plant\n"
    response += "⚫ Critical (entire plant): Remove and destroy, don't compost\n\n"
    
    response += "**IMPORTANT NOTES:**\n"
    response += "• Viral diseases have NO CURE - prevention is critical\n"
    response += "• Bacterial diseases spread fast - act immediately\n"
    response += "• Fungal diseases are manageable with early treatment\n"
    response += "• Always follow fungicide label instructions\n"
    response += "• Wear protective gear when applying chemicals\n"
    response += "• Respect harvest waiting periods\n"
    
    return response

def generate_temperature_response(temp, t):
    """Generate comprehensive temperature management advice"""
    response = f"{t['temp_title']}\n\n"
    response += f"**Current:** {t['temperature']}: {temp}°C\n"
    response += f"**Optimal range:** 20-30°C for most crops\n\n"
    
    if temp > 35:
        response += "🔥 **EXTREME HEAT - EMERGENCY MEASURES:**\n\n"
        response += "**Immediate actions (next 2 hours):**\n"
        response += "1. Provide shade immediately - use cloth/net (50% shade)\n"
        response += "2. Water deeply - soil level, avoid leaves\n"
        response += "3. Mist leaves lightly (not in direct sun)\n"
        response += "4. Move potted plants to shade\n"
        response += "5. Apply thick mulch (7-10cm) around plants\n\n"
        
        response += "**Daily care during heat wave:**\n"
        response += "• Water twice daily (early morning + evening)\n"
        response += "• Mist leaves 2-3 times (avoid midday)\n"
        response += "• Check soil moisture every 4-6 hours\n"
        response += "• Avoid fertilizing (stresses plants)\n"
        response += "• Postpone pruning/transplanting\n\n"
        
        response += "**Cooling strategies:**\n"
        response += "• Shade cloth: 30-50% shade (₹200-500 per sq meter)\n"
        response += "• White paint on pots: Reflects heat\n"
        response += "• Evaporative cooling: Wet burlap around pots\n"
        response += "• Group plants: Creates microclimate\n"
        response += "• Windbreaks: Reduce hot wind damage\n\n"
        
        response += "**Signs of heat stress:**\n"
        response += "⚠️ Wilting during day (recovers at night)\n"
        response += "⚠️ Leaf edges turning brown/crispy\n"
        response += "⚠️ Flowers dropping\n"
        response += "⚠️ Fruit sunscald (white/brown patches)\n"
        response += "⚠️ Slow growth, small leaves\n\n"
        
        response += "**Recovery:** 3-7 days after temperature normalizes\n"
        
    elif temp > 30:
        response += "🔥 **HIGH TEMPERATURE - PROTECTIVE MEASURES:**\n\n"
        response += "**Actions needed:**\n"
        response += "• Increase watering frequency by 30-50%\n"
        response += "• Water early morning (6-7 AM) and evening (6-7 PM)\n"
        response += "• Apply mulch 5-7cm thick\n"
        response += "• Provide afternoon shade (2-6 PM)\n"
        response += "• Mist leaves in evening\n\n"
        
        response += "**Shade options:**\n"
        response += "• Shade cloth: 30% shade (₹150-300 per sq meter)\n"
        response += "• Natural shade: Plant tall crops on south side\n"
        response += "• Temporary: Old bedsheets, bamboo mats\n\n"
        
        response += "**Heat-tolerant crops:**\n"
        response += "✓ Okra, eggplant, peppers, tomatoes\n"
        response += "✓ Melons, squash, beans\n"
        response += "✓ Amaranth, basil, mint\n"
        
    elif temp < 15:
        response += "❄️ **EXTREME COLD - EMERGENCY PROTECTION:**\n\n"
        response += "**Immediate actions (before nightfall):**\n"
        response += "1. Cover plants with plastic/cloth (don't touch leaves)\n"
        response += "2. Use row covers, cloches, or tunnels\n"
        response += "3. Mulch heavily around base (10-15cm)\n"
        response += "4. Move potted plants indoors/sheltered area\n"
        response += "5. Water in morning (wet soil holds heat)\n\n"
        
        response += "**Frost protection:**\n"
        response += "• Plastic tunnels: Best protection (₹500-1000)\n"
        response += "• Row covers: Lightweight fabric (₹200-400)\n"
        response += "• Cloches: Individual plant covers (₹50-100 each)\n"
        response += "• Straw/hay: Thick layer around plants\n"
        response += "• Water: Spray before frost (ice protects)\n\n"
        
        response += "**Cold weather care:**\n"
        response += "• Reduce watering by 50%\n"
        response += "• Water only in morning (10-11 AM)\n"
        response += "• Stop fertilizing until warm weather\n"
        response += "• Prune dead/damaged parts in spring\n"
        response += "• Don't disturb frozen plants\n\n"
        
        response += "**Signs of cold damage:**\n"
        response += "⚠️ Blackened, mushy leaves\n"
        response += "⚠️ Wilting (despite moist soil)\n"
        response += "⚠️ Stem splitting/cracking\n"
        response += "⚠️ Fruit damage (soft spots)\n\n"
        
        response += "**Recovery:** 2-4 weeks, prune damage in spring\n"
        
    elif temp < 20:
        response += "❄️ **COOL TEMPERATURE - PROTECTIVE CARE:**\n\n"
        response += "**Actions needed:**\n"
        response += "• Use row covers at night\n"
        response += "• Reduce watering by 20-30%\n"
        response += "• Water in morning only (10 AM-12 PM)\n"
        response += "• Apply mulch 5-7cm thick\n"
        response += "• Reduce fertilizer application\n\n"
        
        response += "**Cold-tolerant crops:**\n"
        response += "✓ Lettuce, spinach, kale, cabbage\n"
        response += "✓ Peas, broad beans, carrots\n"
        response += "✓ Broccoli, cauliflower, radish\n\n"
        
        response += "**Growth expectations:**\n"
        response += "• Slower growth (50-70% of normal)\n"
        response += "• Longer time to maturity\n"
        response += "• Reduced nutrient uptake\n"
        
    else:
        response += f"✅ **OPTIMAL TEMPERATURE - {t['optimal']}!**\n\n"
        response += "**Why this is perfect:**\n"
        response += "• Maximum photosynthesis rate\n"
        response += "• Optimal enzyme activity\n"
        response += "• Best nutrient uptake\n"
        response += "• Strong root development\n"
        response += "• Good flowering and fruiting\n"
        response += "• Low disease pressure\n\n"
        
        response += "**Maintain optimal conditions:**\n"
        response += "• Continue current care routine\n"
        response += "• Monitor daily temperature changes\n"
        response += "• Be prepared for sudden changes\n"
        response += "• Keep shade materials ready\n"
        response += "• Keep row covers available\n\n"
        
        response += "**Expected results:**\n"
        response += "• Vigorous growth\n"
        response += "• High yield potential\n"
        response += "• Good quality produce\n"
        response += "• Strong disease resistance\n"
    
    response += f"\n**Temperature monitoring tips:**\n"
    response += "• Check temperature 3 times daily (morning, noon, evening)\n"
    response += "• Use min-max thermometer (₹200-500)\n"
    response += "• Record daily temperatures\n"
    response += "• Watch weather forecasts\n"
    response += "• Be prepared for sudden changes\n"
    
    return response

def generate_soil_response(moisture, t):
    """Generate comprehensive soil management advice"""
    response = f"{t['soil_title']}\n\n"
    response += f"**Current {t['soil_moisture']}:** {moisture}%\n"
    response += f"**Optimal range:** 50-70%\n\n"
    
    response += "**SOIL HEALTH ESSENTIALS:**\n\n"
    response += "**1. pH LEVEL (Most Important)**\n"
    response += "   • Optimal range: 6.0-7.0 (slightly acidic to neutral)\n"
    response += "   • Testing: Use pH meter (₹200-500) or test kit (₹100-200)\n"
    response += "   • Frequency: Test every 6 months\n\n"
    
    response += "   **If pH too low (< 6.0 - Acidic):**\n"
    response += "   • Add agricultural lime: 200-500g per sq meter\n"
    response += "   • Add wood ash: 100-200g per sq meter\n"
    response += "   • Add dolomite: 150-300g per sq meter\n"
    response += "   • Wait 2-3 weeks before planting\n\n"
    
    response += "   **If pH too high (> 7.0 - Alkaline):**\n"
    response += "   • Add sulfur: 50-100g per sq meter\n"
    response += "   • Add peat moss: Mix into soil\n"
    response += "   • Add compost: 2-3 kg per sq meter\n"
    response += "   • Use acidic fertilizers (ammonium sulfate)\n\n"
    
    response += "**2. ORGANIC MATTER (Soil Food)**\n"
    response += "   • Target: 5-10% organic content\n"
    response += "   • Benefits: Water retention, nutrients, microbes\n\n"
    
    response += "   **How to add organic matter:**\n"
    response += "   • Compost: 3-5 kg per sq meter annually\n"
    response += "   • Vermicompost: 2-3 kg per sq meter\n"
    response += "   • Cow manure: 4-6 kg per sq meter (well-rotted)\n"
    response += "   • Green manure: Grow legumes, till into soil\n"
    response += "   • Mulch: 5-7cm layer (breaks down over time)\n\n"
    
    response += "**3. SOIL TEXTURE & STRUCTURE**\n\n"
    response += "   **Sandy Soil (Drains too fast):**\n"
    response += "   • Problem: Low water/nutrient retention\n"
    response += "   • Solution: Add compost (5-10 kg per sq meter)\n"
    response += "   • Add clay: 2-3 kg per sq meter\n"
    response += "   • Mulch heavily: 7-10cm\n"
    response += "   • Water more frequently\n\n"
    
    response += "   **Clay Soil (Drains too slow):**\n"
    response += "   • Problem: Waterlogging, poor aeration\n"
    response += "   • Solution: Add sand (3-5 kg per sq meter)\n"
    response += "   • Add compost: 5-10 kg per sq meter\n"
    response += "   • Add gypsum: 200-400g per sq meter\n"
    response += "   • Raise beds: 15-30cm height\n"
    response += "   • Improve drainage\n\n"
    
    response += "   **Loamy Soil (Perfect - balanced):**\n"
    response += "   • Characteristics: Good drainage, water retention\n"
    response += "   • Maintenance: Add compost annually\n"
    response += "   • This is ideal soil!\n\n"
    
    response += "**4. DRAINAGE TEST**\n"
    response += "   • Dig hole: 30cm deep, 30cm wide\n"
    response += "   • Fill with water, let drain\n"
    response += "   • Fill again, measure time to drain\n\n"
    
    response += "   **Results:**\n"
    response += "   • 1-2 hours: Perfect drainage\n"
    response += "   • < 1 hour: Too fast (sandy) - add compost\n"
    response += "   • > 4 hours: Too slow (clay) - add sand, raise beds\n\n"
    
    response += "**5. SOIL AERATION**\n"
    response += "   • Why: Roots need oxygen\n"
    response += "   • How: Till or fork soil 15-20cm deep\n"
    response += "   • When: Before planting, seasonally\n"
    response += "   • Avoid: Compaction (don't walk on beds)\n"
    response += "   • Tools: Garden fork (₹200-500), tiller (₹5000-15000)\n\n"
    
    response += "**6. NUTRIENT MANAGEMENT**\n\n"
    response += "   **Major Nutrients (NPK):**\n"
    response += "   • Nitrogen (N): Leaf growth, green color\n"
    response += "   • Phosphorus (P): Root, flower, fruit development\n"
    response += "   • Potassium (K): Overall health, disease resistance\n\n"
    
    response += "   **Secondary Nutrients:**\n"
    response += "   • Calcium (Ca): Cell walls, prevents blossom end rot\n"
    response += "   • Magnesium (Mg): Chlorophyll, photosynthesis\n"
    response += "   • Sulfur (S): Protein synthesis\n\n"
    
    response += "   **Micronutrients:**\n"
    response += "   • Iron, Zinc, Manganese, Copper, Boron, Molybdenum\n"
    response += "   • Needed in tiny amounts but essential\n"
    response += "   • Use complete fertilizer or compost\n\n"
    
    response += "**7. SOIL TESTING**\n"
    response += "   • Professional test: ₹500-1000 (recommended)\n"
    response += "   • Tests for: pH, NPK, organic matter, micronutrients\n"
    response += "   • Frequency: Every 6-12 months\n"
    response += "   • Where: Agricultural universities, private labs\n\n"
    
    response += "**8. CROP ROTATION**\n"
    response += "   • Why: Prevents nutrient depletion, disease buildup\n"
    response += "   • How: Don't plant same family in same spot\n"
    response += "   • Cycle: 3-4 year rotation\n\n"
    
    response += "   **Example rotation:**\n"
    response += "   Year 1: Tomatoes (heavy feeders)\n"
    response += "   Year 2: Beans (nitrogen fixers)\n"
    response += "   Year 3: Carrots (light feeders)\n"
    response += "   Year 4: Lettuce (light feeders)\n\n"
    
    response += "**9. MULCHING**\n"
    response += "   • Benefits: Moisture retention, weed control, temperature regulation\n"
    response += "   • Materials: Straw, hay, leaves, grass clippings, wood chips\n"
    response += "   • Thickness: 5-7cm (not touching stems)\n"
    response += "   • Cost: ₹50-200 per sq meter\n\n"
    
    response += "**10. COMMON SOIL PROBLEMS**\n\n"
    response += "   **Compaction:**\n"
    response += "   • Signs: Hard surface, poor drainage, stunted roots\n"
    response += "   • Fix: Aerate, add compost, avoid walking on beds\n\n"
    
    response += "   **Salt Buildup:**\n"
    response += "   • Signs: White crust, poor growth, leaf burn\n"
    response += "   • Fix: Flush with water, improve drainage, use low-salt fertilizer\n\n"
    
    response += "   **Nutrient Deficiency:**\n"
    response += "   • Signs: Yellow leaves, poor growth, discoloration\n"
    response += "   • Fix: Soil test, add appropriate fertilizer\n\n"
    
    response += "**SOIL IMPROVEMENT TIMELINE:**\n"
    response += "Week 1: Test soil, identify issues\n"
    response += "Week 2: Add amendments (lime, sulfur, compost)\n"
    response += "Week 3-4: Let amendments work, till lightly\n"
    response += "Week 5: Retest pH, plant if optimal\n"
    response += "Ongoing: Add compost, mulch, monitor\n"
    
    return response

def generate_weather_response(temp, humidity, t):
    """Generate comprehensive weather-based farming advice"""
    response = f"{t['weather_title']}\n\n"
    response += f"**Current conditions:**\n"
    response += f"• {t['temperature']}: {temp}°C\n"
    response += f"• {t['humidity']}: {humidity}%\n\n"
    
    response += "**WEATHER-BASED FARMING GUIDE:**\n\n"
    response += "**1. DAILY WEATHER MONITORING**\n"
    response += "   • Check forecast: Morning and evening\n"
    response += "   • Monitor: Temperature, rainfall, wind, humidity\n"
    response += "   • Apps: IMD Weather, Mausam, Weather Underground\n"
    response += "   • Local signs: Clouds, wind direction, animal behavior\n\n"
    
    response += "**2. SEASONAL FARMING CALENDAR:**\n\n"
    response += "   **SUMMER (March-May)**\n"
    response += "   • Temperature: 30-40°C\n"
    response += "   • Challenges: Heat stress, water scarcity\n"
    response += "   • Actions:\n"
    response += "     - Increase watering (2x daily)\n"
    response += "     - Provide shade (30-50%)\n"
    response += "     - Mulch heavily (7-10cm)\n"
    response += "     - Harvest early morning\n"
    response += "   • Best crops: Okra, eggplant, peppers, melons, cucumbers\n"
    response += "   • Avoid: Leafy greens, cool-season crops\n\n"
    
    response += "   **MONSOON (June-September)**\n"
    response += "   • Temperature: 25-35°C\n"
    response += "   • Challenges: Excess water, fungal diseases, flooding\n"
    response += "   • Actions:\n"
    response += "     - Improve drainage\n"
    response += "     - Reduce watering\n"
    response += "     - Apply preventive fungicide\n"
    response += "     - Stake plants (wind protection)\n"
    response += "     - Harvest before heavy rains\n"
    response += "   • Best crops: Rice, maize, millets, gourds\n"
    response += "   • Avoid: Root vegetables (rot risk)\n\n"
    
    response += "   **POST-MONSOON (October-November)**\n"
    response += "   • Temperature: 20-30°C\n"
    response += "   • Challenges: Pest buildup, disease carryover\n"
    response += "   • Actions:\n"
    response += "     - Clean up debris\n"
    response += "     - Pest control\n"
    response += "     - Soil preparation\n"
    response += "     - Plant winter crops\n"
    response += "   • Best crops: Tomatoes, cauliflower, cabbage, peas\n"
    response += "   • Perfect season: Moderate temperature, low disease\n\n"
    
    response += "   **WINTER (December-February)**\n"
    response += "   • Temperature: 10-25°C\n"
    response += "   • Challenges: Frost, cold damage, slow growth\n"
    response += "   • Actions:\n"
    response += "     - Frost protection (covers)\n"
    response += "     - Reduce watering (50%)\n"
    response += "     - Water in morning only\n"
    response += "     - Mulch for insulation\n"
    response += "   • Best crops: Lettuce, spinach, carrots, radish, peas\n"
    response += "   • Avoid: Heat-loving crops (tomatoes, peppers)\n\n"
    
    response += "**3. WEATHER EVENT PREPARATION:**\n\n"
    response += "   **Before Heavy Rain:**\n"
    response += "   • Harvest ripe produce\n"
    response += "   • Stake tall plants\n"
    response += "   • Improve drainage channels\n"
    response += "   • Cover delicate plants\n"
    response += "   • Don't fertilize (washes away)\n\n"
    
    response += "   **Before Heatwave:**\n"
    response += "   • Water deeply\n"
    response += "   • Install shade cloth\n"
    response += "   • Apply thick mulch\n"
    response += "   • Harvest ready produce\n"
    response += "   • Prepare misting system\n\n"
    
    response += "   **Before Cold Snap/Frost:**\n"
    response += "   • Cover plants before sunset\n"
    response += "   • Water in morning (wet soil holds heat)\n"
    response += "   • Harvest sensitive crops\n"
    response += "   • Move pots to shelter\n"
    response += "   • Mulch heavily\n\n"
    
    response += "   **Before Strong Winds:**\n"
    response += "   • Stake plants securely\n"
    response += "   • Harvest ripe fruits\n"
    response += "   • Remove dead branches\n"
    response += "   • Secure row covers\n"
    response += "   • Move lightweight pots\n\n"
    
    response += "**4. WEATHER-BASED ACTIVITIES:**\n\n"
    response += "   **Sunny Days:**\n"
    response += "   ✓ Transplanting\n"
    response += "   ✓ Harvesting\n"
    response += "   ✓ Pest control spraying\n"
    response += "   ✓ Soil preparation\n"
    response += "   ✗ Avoid midday work (heat stress)\n\n"
    
    response += "   **Cloudy Days:**\n"
    response += "   ✓ Transplanting (less stress)\n"
    response += "   ✓ Pruning\n"
    response += "   ✓ Fertilizing\n"
    response += "   ✓ All-day work possible\n\n"
    
    response += "   **Rainy Days:**\n"
    response += "   ✗ No fertilizing\n"
    response += "   ✗ No spraying\n"
    response += "   ✗ No transplanting\n"
    response += "   ✓ Planning, record keeping\n\n"
    
    response += "**5. CLIMATE ADAPTATION:**\n"
    response += "   • Choose climate-appropriate varieties\n"
    response += "   • Use season extension techniques\n"
    response += "   • Implement water conservation\n"
    response += "   • Build resilient soil (organic matter)\n"
    response += "   • Diversify crops (risk management)\n"
    response += "   • Use weather forecasts for planning\n\n"
    
    response += "**WEATHER WISDOM:**\n"
    response += "• \"Plant by the weather, not the calendar\"\n"
    response += "• \"A dry May, a wet June, makes the farmer whistle a merry tune\"\n"
    response += "• \"Evening red and morning gray, sends the traveler on his way\"\n"
    response += "• Monitor local weather patterns\n"
    response += "• Learn from experienced local farmers\n"
    
    return response

def generate_planting_response(t):
    """Generate comprehensive planting advice"""
    response = f"{t['planting_title']}\n\n"

    response += "🌱 **COMPLETE PLANTING GUIDE**\n\n"

    response += "📅 **1. PLANTING CALENDAR (Month-wise)**\n"
    response += "• January-February: Tomato, Brinjal, Chilli, Cabbage, Cauliflower\n"
    response += "• March-April: Cucumber, Bottle Gourd, Ridge Gourd, Pumpkin, Watermelon\n"
    response += "• May-June: Okra, Bitter Gourd, Sponge Gourd, Cowpea\n"
    response += "• July-August: Radish, Carrot, Beans, Peas, Spinach\n"
    response += "• September-October: Onion, Garlic, Coriander, Fenugreek\n"
    response += "• November-December: Potato, Peas, Broad Beans, Lettuce\n\n"

    response += "🌾 **2. SEED PREPARATION (Before Planting)**\n"
    response += "• Seed Selection: Choose certified, disease-free seeds from reliable sources\n"
    response += "• Seed Treatment: Soak in water for 6-12 hours (beans, peas, corn)\n"
    response += "• Fungicide Treatment: Mix 2g Thiram per kg seeds to prevent fungal diseases\n"
    response += "• Bio-treatment: Coat with Trichoderma (5g/kg) or Pseudomonas (10g/kg)\n"
    response += "• Germination Test: Test 100 seeds - if 80+ germinate, seeds are good\n"
    response += "• Priming: Soak in 1% KNO3 solution for faster germination\n\n"

    response += "🏗️ **3. SOIL PREPARATION (2-3 Weeks Before)**\n"
    response += "• Deep Plowing: Plow 20-25cm deep to break hard soil layers\n"
    response += "• Add Organic Matter: Mix 10-15 tons FYM or compost per acre\n"
    response += "• pH Adjustment: Add lime if pH < 6.0, sulfur if pH > 7.5\n"
    response += "• Leveling: Level field properly for uniform water distribution\n"
    response += "• Bed Preparation: Make raised beds (15cm high, 1m wide) for better drainage\n"
    response += "• Mulching: Apply 5-7cm organic mulch to retain moisture\n"
    response += "• Solarization: Cover with plastic for 4-6 weeks to kill pests/weeds\n\n"

    response += "📏 **4. PLANTING SPECIFICATIONS**\n"
    response += "Crop-wise Depth, Spacing & Seed Rate:\n\n"
    response += "• Tomato: Depth 1-2cm, Spacing 60×45cm, Rate 200g/acre\n"
    response += "• Chilli: Depth 1cm, Spacing 60×45cm, Rate 250g/acre\n"
    response += "• Cabbage: Depth 1cm, Spacing 45×45cm, Rate 300g/acre\n"
    response += "• Cucumber: Depth 2-3cm, Spacing 100×60cm, Rate 1kg/acre\n"
    response += "• Okra: Depth 2-3cm, Spacing 45×30cm, Rate 5kg/acre\n"
    response += "• Radish: Depth 1-2cm, Spacing 30×10cm, Rate 4kg/acre\n"
    response += "• Carrot: Depth 1cm, Spacing 30×7cm, Rate 3kg/acre\n"
    response += "• Onion: Depth 2cm, Spacing 15×10cm, Rate 8kg/acre\n"
    response += "• Potato: Depth 5-7cm, Spacing 60×20cm, Rate 1000kg/acre\n\n"

    response += "🌿 **5. PLANTING METHODS**\n"
    response += "A. Direct Seeding:\n"
    response += "   • Best for: Radish, Carrot, Beans, Peas, Spinach\n"
    response += "   • Make furrows at proper spacing\n"
    response += "   • Drop seeds at recommended distance\n"
    response += "   • Cover with fine soil and press gently\n\n"
    response += "B. Transplanting:\n"
    response += "   • Best for: Tomato, Chilli, Cabbage, Cauliflower\n"
    response += "   • Raise nursery 4-6 weeks before transplanting\n"
    response += "   • Transplant in evening or cloudy day\n"
    response += "   • Water immediately after transplanting\n"
    response += "   • Provide shade for 2-3 days\n\n"
    response += "C. Dibbling:\n"
    response += "   • Best for: Okra, Cucumber, Pumpkin\n"
    response += "   • Make holes at proper spacing\n"
    response += "   • Drop 2-3 seeds per hole\n"
    response += "   • Thin to 1 plant after germination\n\n"

    response += "🤝 **6. COMPANION PLANTING (Plant Together)**\n"
    response += "• Tomato + Basil: Basil repels aphids and whiteflies\n"
    response += "• Carrot + Onion: Onion repels carrot fly\n"
    response += "• Cabbage + Marigold: Marigold repels cabbage worms\n"
    response += "• Cucumber + Radish: Radish repels cucumber beetles\n"
    response += "• Beans + Corn: Beans fix nitrogen for corn\n"
    response += "• Potato + Horseradish: Horseradish repels potato beetles\n\n"

    response += "🚫 **7. AVOID PLANTING TOGETHER**\n"
    response += "• Tomato + Potato: Share same diseases\n"
    response += "• Onion + Beans: Inhibit each other's growth\n"
    response += "• Cabbage + Tomato: Compete for nutrients\n"
    response += "• Cucumber + Sage: Sage stunts cucumber growth\n\n"

    response += "💧 **8. POST-PLANTING CARE (First 2 Weeks)**\n"
    response += "• Watering: Light irrigation daily for first week\n"
    response += "• Mulching: Apply 5cm mulch to retain moisture\n"
    response += "• Thinning: Remove weak seedlings after 10-15 days\n"
    response += "• Gap Filling: Replant in empty spots within 7 days\n"
    response += "• Weeding: Remove weeds carefully without disturbing roots\n"
    response += "• Protection: Use bird nets or scarecrows if needed\n\n"

    response += "🌡️ **9. OPTIMAL CONDITIONS**\n"
    response += "• Temperature: 20-30°C for most vegetables\n"
    response += "• Soil Moisture: 60-70% field capacity\n"
    response += "• Sunlight: 6-8 hours direct sunlight daily\n"
    response += "• Humidity: 50-70% for best germination\n"
    response += "• Wind Protection: Use windbreaks for tender seedlings\n\n"

    response += "⚠️ **10. COMMON MISTAKES TO AVOID**\n"
    response += "• Planting too deep or too shallow\n"
    response += "• Overcrowding - leads to disease and poor growth\n"
    response += "• Planting in wrong season\n"
    response += "• Using untreated or old seeds\n"
    response += "• Not preparing soil properly\n"
    response += "• Overwatering immediately after planting\n"
    response += "• Ignoring pest protection in early stage\n\n"

    response += "📊 **11. SUCCESS INDICATORS**\n"
    response += "• Germination: 70-90% within 7-14 days\n"
    response += "• Seedling Color: Bright green, not yellow\n"
    response += "• Growth Rate: 1-2cm per week initially\n"
    response += "• Root Development: White, spreading roots\n"
    response += "• No Wilting: Plants stand upright\n\n"

    response += "💰 **12. COST ESTIMATE (Per Acre)**\n"
    response += "• Seeds: ₹500-2000 (depending on crop)\n"
    response += "• Soil Preparation: ₹3000-5000\n"
    response += "• Organic Manure: ₹5000-8000\n"
    response += "• Seed Treatment: ₹200-500\n"
    response += "• Labor: ₹2000-4000\n"
    response += "• Total: ₹10,700-19,500\n\n"

    response += "📞 **Need Help?** Ask me about specific crops, soil types, or planting problems!"

    return response

def generate_harvest_response(t):
    """Generate comprehensive harvest advice"""
    response = f"{t['harvest_title']}\n\n"

    response += "🌾 **COMPLETE HARVESTING GUIDE**\n\n"

    response += "⏰ **1. HARVEST TIMING (Crop-wise)**\n"
    response += "• Tomato: 60-80 days, when fruits turn red/pink\n"
    response += "• Chilli: 80-100 days, when fruits are firm and glossy\n"
    response += "• Cabbage: 70-90 days, when heads are firm and compact\n"
    response += "• Cauliflower: 60-80 days, when curds are 15-20cm diameter\n"
    response += "• Cucumber: 50-60 days, when fruits are 15-20cm long\n"
    response += "• Okra: 45-60 days, when pods are 7-10cm long\n"
    response += "• Radish: 25-30 days, when roots are 2-3cm diameter\n"
    response += "• Carrot: 70-90 days, when roots are 2-3cm diameter\n"
    response += "• Onion: 120-150 days, when tops fall over and dry\n"
    response += "• Potato: 90-120 days, when foliage turns yellow\n"
    response += "• Beans: 50-60 days, when pods snap easily\n"
    response += "• Peas: 60-70 days, when pods are plump but tender\n\n"

    response += "🌅 **2. BEST TIME OF DAY**\n"
    response += "• Morning Harvest (6-9 AM): Best for leafy vegetables\n"
    response += "  - Spinach, Lettuce, Cabbage, Coriander\n"
    response += "  - Reason: Maximum moisture content, crisp texture\n"
    response += "• Evening Harvest (4-6 PM): Best for fruits\n"
    response += "  - Tomato, Cucumber, Pumpkin, Watermelon\n"
    response += "  - Reason: Maximum sugar content, better flavor\n"
    response += "• Avoid: Mid-day (11 AM-3 PM) - too hot, wilting risk\n"
    response += "• Avoid: After rain - increases disease spread\n\n"

    response += "🔍 **3. MATURITY INDICATORS**\n"
    response += "Visual Signs:\n"
    response += "• Color Change: Green to red/yellow/orange (tomato, pepper)\n"
    response += "• Size: Reached expected size for variety\n"
    response += "• Firmness: Firm but not hard (cucumber, okra)\n"
    response += "• Gloss: Shiny surface (brinjal, chilli)\n"
    response += "• Foliage: Yellowing/drying (onion, potato, garlic)\n\n"
    response += "Physical Tests:\n"
    response += "• Snap Test: Pods snap cleanly (beans, peas)\n"
    response += "• Thumb Test: Slight pressure leaves mark (tomato)\n"
    response += "• Pull Test: Easy to detach from plant (cucumber)\n"
    response += "• Sound Test: Hollow sound when tapped (watermelon)\n\n"

    response += "✂️ **4. HARVESTING TECHNIQUES**\n"
    response += "A. Hand Picking:\n"
    response += "   • Best for: Tomato, Chilli, Okra, Beans\n"
    response += "   • Hold stem with one hand, twist fruit gently\n"
    response += "   • Leave small stem attached to fruit\n"
    response += "   • Avoid pulling - may damage plant\n\n"
    response += "B. Cutting:\n"
    response += "   • Best for: Cabbage, Cauliflower, Broccoli\n"
    response += "   • Use sharp, clean knife or secateurs\n"
    response += "   • Cut 2-3cm below head\n"
    response += "   • Make clean cut to prevent disease\n\n"
    response += "C. Pulling:\n"
    response += "   • Best for: Radish, Carrot, Onion, Garlic\n"
    response += "   • Loosen soil around plant first\n"
    response += "   • Hold leaves near base, pull gently\n"
    response += "   • Shake off excess soil\n\n"
    response += "D. Digging:\n"
    response += "   • Best for: Potato, Sweet Potato, Ginger\n"
    response += "   • Use spade or fork 15cm away from plant\n"
    response += "   • Dig carefully to avoid damage\n"
    response += "   • Collect all tubers from soil\n\n"

    response += "📦 **5. HANDLING AFTER HARVEST**\n"
    response += "Immediate Care:\n"
    response += "• Handle gently - avoid bruising and cuts\n"
    response += "• Keep in shade - direct sun causes wilting\n"
    response += "• Sort immediately - separate damaged produce\n"
    response += "• Clean gently - remove soil with soft brush\n"
    response += "• Don't wash - unless consuming immediately\n\n"
    response += "Grading:\n"
    response += "• Grade A: Perfect shape, no damage, uniform size\n"
    response += "• Grade B: Minor defects, good for local market\n"
    response += "• Grade C: Damaged, use for processing/home use\n\n"

    response += "🧊 **6. STORAGE METHODS**\n"
    response += "A. Cool Storage (0-5°C):\n"
    response += "   • Leafy vegetables: 3-7 days\n"
    response += "   • Cabbage, Cauliflower: 2-3 weeks\n"
    response += "   • Carrot, Radish: 2-4 weeks\n"
    response += "   • Store in perforated plastic bags\n\n"
    response += "B. Room Temperature (15-25°C):\n"
    response += "   • Tomato (ripe): 3-5 days\n"
    response += "   • Cucumber: 5-7 days\n"
    response += "   • Okra: 2-3 days\n"
    response += "   • Keep in cool, ventilated area\n\n"
    response += "C. Curing & Long Storage:\n"
    response += "   • Onion: Cure 2-3 weeks, store 4-6 months\n"
    response += "   • Garlic: Cure 2-3 weeks, store 6-8 months\n"
    response += "   • Potato: Cure 10-14 days, store 3-4 months\n"
    response += "   • Pumpkin: Cure 2 weeks, store 2-3 months\n\n"

    response += "🌡️ **7. CURING PROCESS (For Storage Crops)**\n"
    response += "Onion & Garlic:\n"
    response += "• Spread in single layer in shade\n"
    response += "• Turn daily for even drying\n"
    response += "• Cure until tops are completely dry\n"
    response += "• Cut tops leaving 2-3cm stem\n"
    response += "• Store in mesh bags in cool, dry place\n\n"
    response += "Potato:\n"
    response += "• Keep in dark at 15-20°C for 10-14 days\n"
    response += "• Allows skin to thicken\n"
    response += "• Heals minor cuts and bruises\n"
    response += "• Then store at 4-8°C in dark\n\n"

    response += "📊 **8. YIELD EXPECTATIONS (Per Acre)**\n"
    response += "• Tomato: 8-12 tons\n"
    response += "• Chilli: 2-3 tons\n"
    response += "• Cabbage: 15-20 tons\n"
    response += "• Cauliflower: 10-15 tons\n"
    response += "• Cucumber: 8-10 tons\n"
    response += "• Okra: 4-6 tons\n"
    response += "• Radish: 6-8 tons\n"
    response += "• Carrot: 10-12 tons\n"
    response += "• Onion: 10-15 tons\n"
    response += "• Potato: 8-12 tons\n\n"

    response += "🔄 **9. MULTIPLE HARVESTS**\n"
    response += "Crops with Multiple Pickings:\n"
    response += "• Tomato: Harvest every 3-4 days for 2-3 months\n"
    response += "• Chilli: Harvest every 7-10 days for 3-4 months\n"
    response += "• Okra: Harvest every 2-3 days for 2 months\n"
    response += "• Beans: Harvest every 3-4 days for 1 month\n"
    response += "• Cucumber: Harvest every 2-3 days for 1.5 months\n\n"
    response += "Tips for Continuous Harvest:\n"
    response += "• Pick regularly - don't let fruits over-mature\n"
    response += "• Remove damaged/diseased fruits immediately\n"
    response += "• Feed plants after each harvest\n"
    response += "• Maintain proper irrigation\n\n"

    response += "⚠️ **10. COMMON HARVESTING MISTAKES**\n"
    response += "• Harvesting too early - poor flavor, low yield\n"
    response += "• Harvesting too late - tough, bitter, seeds mature\n"
    response += "• Rough handling - bruising reduces shelf life\n"
    response += "• Harvesting in rain - spreads diseases\n"
    response += "• Not cleaning tools - disease transmission\n"
    response += "• Mixing damaged with good produce\n"
    response += "• Storing in direct sunlight\n"
    response += "• Washing before storage (except leafy vegetables)\n\n"

    response += "🧰 **11. TOOLS & EQUIPMENT**\n"
    response += "Essential Tools:\n"
    response += "• Sharp knife or secateurs (₹200-500)\n"
    response += "• Harvesting baskets (₹150-300 each)\n"
    response += "• Gloves (₹50-100)\n"
    response += "• Crates/boxes for transport (₹200-400 each)\n"
    response += "• Weighing scale (₹500-2000)\n\n"
    response += "Tool Maintenance:\n"
    response += "• Clean tools after each use\n"
    response += "• Disinfect with 70% alcohol or bleach solution\n"
    response += "• Sharpen cutting tools regularly\n"
    response += "• Store in dry place to prevent rust\n\n"

    response += "💰 **12. POST-HARVEST ECONOMICS**\n"
    response += "Cost Breakdown:\n"
    response += "• Harvesting Labor: ₹3000-5000 per acre\n"
    response += "• Grading & Sorting: ₹1000-2000\n"
    response += "• Packaging: ₹500-1500\n"
    response += "• Transport: ₹1000-3000\n"
    response += "• Storage (if needed): ₹500-2000/month\n\n"
    response += "Reducing Losses:\n"
    response += "• Proper timing: Reduces 10-15% loss\n"
    response += "• Gentle handling: Reduces 5-10% loss\n"
    response += "• Quick cooling: Extends shelf life 2-3x\n"
    response += "• Proper storage: Reduces 20-30% loss\n\n"

    response += "📈 **13. QUALITY STANDARDS**\n"
    response += "For Market Sale:\n"
    response += "• Uniform size and color\n"
    response += "• Free from pests and diseases\n"
    response += "• No mechanical damage\n"
    response += "• Proper maturity\n"
    response += "• Clean and dry\n"
    response += "• Meets food safety standards\n\n"

    response += "🔬 **14. FOOD SAFETY**\n"
    response += "• Harvest at least 7 days after pesticide spray\n"
    response += "• Wash hands before harvesting\n"
    response += "• Use clean containers and tools\n"
    response += "• Avoid contamination from soil/water\n"
    response += "• Keep away from animals\n"
    response += "• Follow pre-harvest interval (PHI) for chemicals\n\n"

    response += "📞 **Need Help?** Ask me about specific crop harvesting, storage problems, or market preparation!"

    return response

def generate_general_response(temp, humidity, moisture, t):
    """Generate comprehensive general farming advice"""
    response = f"{t['general_title']}\n\n"
    response += f"🌡️ {temp}°C | 💧 {humidity}% | 💦 {moisture}%\n\n"
    response += "I can help with: Watering, Fertilizers, Pests, Diseases, Temperature, Soil, Weather, Planting, Harvesting\n"
    response += "Ask in English, Hindi, or Punjabi!"
    return response

# Agriculture AI endpoints
@app.route('/api/agriculture/analyze', methods=['POST'])
def analyze_crop():
    """AI-powered crop disease detection with comprehensive analysis"""
    try:
        # In a real implementation, this would process the uploaded image
        # and run it through an AI model (TensorFlow, PyTorch, etc.)
        
        # Get current sensor data for context
        temp = sensor_data.get('dht22', {}).get('temperature', 25)
        humidity = sensor_data.get('dht22', {}).get('humidity', 60)
        soil_moisture = sensor_data.get('fc28', {}).get('value', 50)
        
        # Simulated comprehensive AI analysis results
        diseases = [
            {
                'name': 'Healthy Crop',
                'icon': '✅',
                'confidence': 95,
                'severity': 'None',
                'description': 'Your crop appears healthy with no visible signs of disease or pest damage. Leaves show good color and structure.',
                'detailed_analysis': {
                    'leaf_health': 'Excellent - vibrant green color, no discoloration',
                    'growth_stage': 'Vegetative growth - normal development',
                    'stress_indicators': 'None detected',
                    'soil_condition': 'Good moisture level, adequate nutrients visible'
                },
                'recommendations': [
                    'Maintain current irrigation schedule',
                    'Continue regular nutrient application (NPK 10-10-10)',
                    'Monitor for early signs of stress or pest activity',
                    'Ensure adequate spacing for air circulation'
                ],
                'preventive_measures': [
                    'Weekly inspection of leaves (top and bottom)',
                    'Remove any dead or yellowing leaves promptly',
                    'Maintain soil pH between 6.0-7.0',
                    'Apply organic mulch to retain moisture'
                ],
                'next_steps': [
                    'Continue monitoring every 2-3 days',
                    'Take photos weekly to track growth progress',
                    'Check soil moisture daily',
                    'Apply balanced fertilizer in 2 weeks'
                ]
            },
            {
                'name': 'Early Blight',
                'icon': '⚠️',
                'confidence': 87,
                'severity': 'Moderate',
                'description': 'Early signs of fungal infection detected. Dark spots with concentric rings visible on leaves. This is a common fungal disease affecting tomatoes and potatoes.',
                'detailed_analysis': {
                    'leaf_health': 'Moderate - dark brown spots with yellow halos present',
                    'growth_stage': 'Mid-season - infection spreading from lower leaves',
                    'stress_indicators': 'Fungal spores visible, leaf yellowing around spots',
                    'soil_condition': f'Moisture: {soil_moisture}% - May be contributing to fungal growth',
                    'environmental_factors': f'Temp: {temp}°C, Humidity: {humidity}% - Favorable for fungal development'
                },
                'recommendations': [
                    '🚨 IMMEDIATE: Remove and destroy infected leaves (do not compost)',
                    '💊 Apply copper-based fungicide (Bordeaux mixture) every 7-10 days',
                    '🌬️ Improve air circulation - prune dense foliage, increase plant spacing',
                    '💧 Avoid overhead watering - water at soil level in morning',
                    '🧹 Clean up fallen leaves and debris around plants',
                    '🔄 Rotate crops next season - do not plant in same location'
                ],
                'treatment_schedule': [
                    'Day 1: Remove infected leaves, apply first fungicide treatment',
                    'Day 3: Check for new spots, remove if found',
                    'Day 7: Second fungicide application',
                    'Day 10: Assess improvement, continue treatment if needed',
                    'Day 14: Third fungicide application',
                    'Day 21: Final assessment and preventive measures'
                ],
                'preventive_measures': [
                    'Use disease-resistant varieties in future plantings',
                    'Mulch around plants to prevent soil splash',
                    'Space plants 60-90cm apart for better airflow',
                    'Water early morning (6-8 AM) to allow leaves to dry',
                    'Apply preventive fungicide before rainy season',
                    'Remove lower leaves touching soil'
                ],
                'warning_signs': [
                    '🔴 Rapid spread to upper leaves - increase treatment frequency',
                    '🔴 Fruit showing spots - harvest affected fruits immediately',
                    '🔴 Entire leaves turning yellow - may need systemic fungicide',
                    '🔴 Stem lesions appearing - disease progressing, consult expert'
                ],
                'cost_estimate': {
                    'fungicide': '₹200-400 per treatment',
                    'total_treatment': '₹600-1200 for full course',
                    'prevention': '₹100-200 per month'
                }
            },
            {
                'name': 'Nutrient Deficiency',
                'icon': '🟡',
                'confidence': 82,
                'severity': 'Mild',
                'description': 'Signs of nitrogen deficiency detected. Older leaves showing yellowing (chlorosis) while veins remain green.',
                'detailed_analysis': {
                    'leaf_health': 'Mild chlorosis - yellowing from leaf tips and edges',
                    'growth_stage': 'Vegetative - growth may be stunted',
                    'stress_indicators': 'Pale green to yellow older leaves, slow growth',
                    'soil_condition': 'Likely nitrogen-depleted, may need organic matter',
                    'deficiency_type': 'Nitrogen (N) - mobile nutrient, affects older leaves first'
                },
                'recommendations': [
                    '🌿 Apply nitrogen-rich fertilizer immediately (Urea 46-0-0 or 20-20-20)',
                    '💚 Use organic options: compost, manure, or blood meal',
                    '💧 Water thoroughly after fertilizer application',
                    '📊 Soil test recommended to confirm nutrient levels',
                    '🔄 Apply in split doses - half now, half after 2 weeks'
                ],
                'fertilizer_guide': [
                    'Urea (46-0-0): 50-100 kg per hectare or 5-10g per plant',
                    'NPK (20-20-20): 100-150 kg per hectare or 10-15g per plant',
                    'Organic compost: 2-3 kg per plant, mix into soil',
                    'Blood meal: 100-200g per plant, high nitrogen content',
                    'Fish emulsion: Dilute 1:10, apply as foliar spray weekly'
                ],
                'application_method': [
                    'Broadcast method: Spread evenly around plant base',
                    'Side dressing: Apply 10-15cm away from stem',
                    'Foliar spray: For quick results, spray on leaves',
                    'Drip irrigation: Mix water-soluble fertilizer',
                    'Timing: Early morning or late evening, avoid hot sun'
                ],
                'preventive_measures': [
                    'Regular soil testing (every 6 months)',
                    'Crop rotation with legumes (fix nitrogen naturally)',
                    'Add compost or manure before planting',
                    'Use slow-release fertilizers for steady supply',
                    'Maintain soil pH 6.0-7.0 for optimal nutrient uptake'
                ],
                'recovery_timeline': [
                    'Week 1: New growth shows improved color',
                    'Week 2: Older leaves may not recover (normal)',
                    'Week 3: Overall plant vigor improves',
                    'Week 4: Full recovery, normal growth rate'
                ],
                'cost_estimate': {
                    'chemical_fertilizer': '₹300-600 per application',
                    'organic_options': '₹200-400 per application',
                    'soil_test': '₹500-1000 one-time'
                }
            },
            {
                'name': 'Pest Infestation',
                'icon': '🐛',
                'confidence': 79,
                'severity': 'Moderate',
                'description': 'Signs of insect damage detected. Holes in leaves and chewing marks visible. Likely aphids or caterpillars.',
                'detailed_analysis': {
                    'leaf_health': 'Damaged - irregular holes and chewed edges',
                    'growth_stage': 'Active infestation - multiple leaves affected',
                    'stress_indicators': 'Visible insects, honeydew residue, curled leaves',
                    'pest_type': 'Likely aphids (small green insects) or caterpillars',
                    'infestation_level': 'Moderate - 20-40% of leaves affected'
                },
                'recommendations': [
                    '🔍 INSPECT: Check undersides of leaves for pests and eggs',
                    '🚿 Spray with strong water jet to dislodge aphids',
                    '🌿 Apply neem oil spray (10ml per liter water)',
                    '🧼 Use insecticidal soap for soft-bodied insects',
                    '✋ Hand-pick larger pests like caterpillars',
                    '🐞 Introduce beneficial insects (ladybugs eat aphids)'
                ],
                'natural_remedies': [
                    'Neem oil spray: 10ml neem oil + 5ml liquid soap per liter water',
                    'Garlic spray: Crush 10 cloves in 1 liter water, strain, spray',
                    'Chili pepper spray: Blend 5 chilies in water, strain, spray',
                    'Soap water: 5ml dish soap per liter water',
                    'Tobacco water: Soak cigarette butts, strain (use carefully)'
                ],
                'chemical_options': [
                    'Imidacloprid: Systemic insecticide, 0.5ml per liter',
                    'Malathion: Contact insecticide, 2ml per liter',
                    'Spinosad: Organic option, safe for beneficial insects',
                    'Pyrethrin: Natural insecticide from chrysanthemums',
                    'Note: Rotate pesticides to prevent resistance'
                ],
                'preventive_measures': [
                    'Companion planting: Marigolds, basil repel pests',
                    'Yellow sticky traps: Catch flying insects',
                    'Row covers: Physical barrier against pests',
                    'Regular inspection: Check plants 2-3 times weekly',
                    'Remove weeds: Eliminate pest hiding places',
                    'Encourage birds: Natural pest predators'
                ],
                'treatment_schedule': [
                    'Day 1: Spray neem oil in evening',
                    'Day 3: Hand-pick visible pests, spray again',
                    'Day 5: Check for improvement, repeat if needed',
                    'Day 7: Apply different treatment if no improvement',
                    'Day 10: Assess results, continue monitoring'
                ],
                'beneficial_insects': [
                    '🐞 Ladybugs: Eat aphids, mealybugs (50-100 per plant)',
                    '🦗 Praying mantis: Eat various insects',
                    '🕷️ Spiders: Natural pest control',
                    '🐝 Parasitic wasps: Attack caterpillars and aphids',
                    '💚 Green lacewings: Larvae eat aphids, mites'
                ],
                'cost_estimate': {
                    'neem_oil': '₹100-200 per bottle (multiple uses)',
                    'insecticidal_soap': '₹150-300',
                    'chemical_pesticide': '₹200-500 per treatment',
                    'beneficial_insects': '₹500-1000 (one-time)'
                }
            }
        ]
        
        import random
        result = random.choice(diseases)
        
        return jsonify({
            'success': True,
            'analysis': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/agriculture/health-score', methods=['GET'])
def get_health_score():
    """Calculate farm health score based on sensor data"""
    try:
        score = 100
        
        # Get current sensor data
        mq135 = sensor_data.get('mq135', {}).get('value', 0)
        temp = sensor_data.get('dht22', {}).get('temperature', 0)
        humidity = sensor_data.get('dht22', {}).get('humidity', 0)
        tds = sensor_data.get('tds', {}).get('value', 0)
        
        # Calculate score based on optimal ranges
        if mq135 > 200: score -= 20
        elif mq135 > 100: score -= 10
        
        if temp < 15 or temp > 35: score -= 15
        elif temp < 20 or temp > 30: score -= 5
        
        if humidity < 40 or humidity > 80: score -= 10
        elif humidity < 50 or humidity > 70: score -= 5
        
        if tds > 500: score -= 15
        elif tds > 300: score -= 5
        
        return jsonify({
            'score': max(0, score),
            'factors': {
                'air_quality': 'Good' if mq135 < 100 else 'Moderate' if mq135 < 200 else 'Poor',
                'temperature': 'Optimal' if 20 <= temp <= 30 else 'Moderate',
                'humidity': 'Good' if 50 <= humidity <= 70 else 'Moderate',
                'water_quality': 'Pure' if tds < 300 else 'Good' if tds < 500 else 'Fair'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/agriculture/recommendations', methods=['GET'])
def get_recommendations():
    """AI-powered smart farming recommendations"""
    try:
        # Get current sensor data
        fc28 = sensor_data.get('fc28', {}).get('value', 0)
        temp = sensor_data.get('dht22', {}).get('temperature', 25)
        humidity = sensor_data.get('dht22', {}).get('humidity', 60)
        air_quality = sensor_data.get('mq135', {}).get('value', 0)
        tds = sensor_data.get('tds', {}).get('value', 0)
        pm25 = sensor_data.get('pms5003', {}).get('pm25', 0)
        
        # Debug: Print values
        print(f"DEBUG - Sensor values: moisture={fc28}, temp={temp}, humidity={humidity}, air_quality={air_quality}, tds={tds}")
        
        # AI-powered irrigation recommendation
        irrigation = ai_irrigation_advisor(fc28, temp, humidity)
        
        # AI-powered fertilizer recommendation
        fertilizer = ai_fertilizer_advisor(temp, humidity, air_quality)
        
        # AI-powered pest control recommendation
        pest = ai_pest_advisor(temp, humidity, air_quality, pm25)
        
        # AI-powered weather-based recommendation
        weather = ai_weather_advisor(temp, humidity)
        
        # Generate AI insights
        ai_insights_list = generate_ai_insights(fc28, temp, humidity, air_quality, tds)
        print(f"DEBUG - Generated {len(ai_insights_list)} insights")
        
        recommendations = {
            'irrigation': irrigation,
            'fertilizer': fertilizer,
            'pest': pest,
            'weather': weather,
            'ai_insights': ai_insights_list
        }
        
        return jsonify(recommendations)
    except Exception as e:
        print(f"ERROR in recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

def ai_irrigation_advisor(moisture, temp, humidity):
    """AI-based irrigation recommendation engine"""
    # Calculate evapotranspiration rate
    et_rate = calculate_evapotranspiration(temp, humidity)
    
    # Determine irrigation urgency
    if moisture < 30:
        status = 'critical'
        urgency = 'immediate'
        hours_until = 0
        advice = f'🚨 CRITICAL: Soil moisture at {moisture:.1f}%. Immediate irrigation required to prevent crop stress.'
    elif moisture < 45:
        status = 'action_needed'
        urgency = 'today'
        hours_until = 4
        advice = f'⚠️ LOW MOISTURE: At {moisture:.1f}%, irrigation needed within 4 hours. High ET rate ({et_rate:.1f}mm/day) accelerating water loss.'
    elif moisture < 60:
        status = 'warning'
        urgency = 'tomorrow'
        hours_until = 24
        advice = f'📊 MODERATE: Moisture at {moisture:.1f}%. Plan irrigation for tomorrow. Current ET rate: {et_rate:.1f}mm/day.'
    elif moisture < 75:
        status = 'optimal'
        urgency = '2-3 days'
        hours_until = 48
        advice = f'✅ OPTIMAL: Soil moisture at {moisture:.1f}% is ideal. Next irrigation in 2-3 days based on {et_rate:.1f}mm/day ET rate.'
    else:
        status = 'saturated'
        urgency = '4-5 days'
        hours_until = 96
        advice = f'💧 SATURATED: Moisture at {moisture:.1f}% is high. Delay irrigation 4-5 days to prevent waterlogging and root diseases.'
    
    # Calculate recommended water amount
    water_needed = calculate_water_requirement(moisture, temp, humidity)
    
    return {
        'status': status,
        'urgency': urgency,
        'hours_until': hours_until,
        'advice': advice,
        'next_irrigation': urgency,
        'water_amount': f'{water_needed:.1f} L/m²',
        'et_rate': f'{et_rate:.1f} mm/day',
        'ai_confidence': 92
    }

def ai_fertilizer_advisor(temp, humidity, air_quality):
    """AI-based fertilizer recommendation engine"""
    import random
    
    # Simulate nutrient analysis based on environmental conditions
    # In production, this would use soil sensors or lab analysis
    base_n = 70 + (temp - 25) * 2  # Temperature affects nitrogen uptake
    base_p = 65 + (humidity - 60) * 0.5  # Humidity affects phosphorus
    base_k = 75 + random.uniform(-5, 5)  # Potassium baseline
    
    # Normalize to 0-100 range
    nitrogen = max(0, min(100, base_n + random.uniform(-5, 5)))
    phosphorus = max(0, min(100, base_p + random.uniform(-5, 5)))
    potassium = max(0, min(100, base_k))
    
    # Determine fertilizer needs
    deficiencies = []
    if nitrogen < 60:
        deficiencies.append('Nitrogen (N)')
    if phosphorus < 60:
        deficiencies.append('Phosphorus (P)')
    if potassium < 60:
        deficiencies.append('Potassium (K)')
    
    if deficiencies:
        status = 'action_needed'
        advice = f'🌿 DEFICIENCY DETECTED: Low levels of {", ".join(deficiencies)}. Apply balanced NPK fertilizer immediately.'
        npk_ratio = '20-20-20'  # High concentration for deficiency
        timing = 'Now'
    elif nitrogen < 70 or phosphorus < 70 or potassium < 70:
        status = 'warning'
        advice = f'📊 MODERATE LEVELS: Nutrient levels declining. Schedule fertilizer application within 1 week.'
        npk_ratio = '10-10-10'  # Maintenance dose
        timing = '1 week'
    else:
        status = 'optimal'
        advice = f'✅ BALANCED: All nutrients in optimal range. Maintain current fertilization schedule.'
        npk_ratio = '5-5-5'  # Light maintenance
        timing = '2-3 weeks'
    
    return {
        'status': status,
        'advice': advice,
        'npk_ratio': npk_ratio,
        'timing': timing,
        'nutrients': {
            'nitrogen': round(nitrogen, 1),
            'phosphorus': round(phosphorus, 1),
            'potassium': round(potassium, 1)
        },
        'application_rate': '50-100 kg/hectare',
        'ai_confidence': 88
    }

def ai_pest_advisor(temp, humidity, air_quality, pm25):
    """AI-based pest control recommendation engine"""
    # AI model for pest risk assessment
    # High temp + high humidity = increased pest activity
    pest_risk_score = 0
    
    # Temperature factor (25-35°C optimal for pests)
    if 25 <= temp <= 35:
        pest_risk_score += 30
    elif 20 <= temp < 25 or 35 < temp <= 40:
        pest_risk_score += 15
    
    # Humidity factor (60-80% optimal for pests)
    if 60 <= humidity <= 80:
        pest_risk_score += 30
    elif 50 <= humidity < 60 or 80 < humidity <= 90:
        pest_risk_score += 15
    
    # Air quality factor (poor air = stressed plants = pest attraction)
    if air_quality > 150:
        pest_risk_score += 20
    elif air_quality > 100:
        pest_risk_score += 10
    
    # Particulate matter (can indicate pest activity)
    if pm25 > 35:
        pest_risk_score += 10
    
    # Determine risk level and recommendations
    if pest_risk_score >= 60:
        status = 'high_risk'
        advice = '🚨 HIGH RISK: Environmental conditions favor pest activity. Implement preventive measures immediately.'
        action = 'Apply organic pesticide (neem oil). Inspect crops twice daily. Set up pest traps.'
        risks = [
            {'name': 'Aphids', 'level': 'High', 'action': 'Spray neem oil solution'},
            {'name': 'Whiteflies', 'level': 'High', 'action': 'Use yellow sticky traps'},
            {'name': 'Caterpillars', 'level': 'Medium', 'action': 'Manual removal + Bt spray'}
        ]
    elif pest_risk_score >= 35:
        status = 'medium_risk'
        advice = '⚠️ MODERATE RISK: Conditions becoming favorable for pests. Increase monitoring frequency.'
        action = 'Daily crop inspection. Prepare preventive treatments. Monitor for early signs.'
        risks = [
            {'name': 'Aphids', 'level': 'Medium', 'action': 'Monitor closely'},
            {'name': 'Grasshoppers', 'level': 'Medium', 'action': 'Check field borders'},
            {'name': 'Mites', 'level': 'Low', 'action': 'Routine monitoring'}
        ]
    else:
        status = 'low_risk'
        advice = '✅ LOW RISK: Environmental conditions not favorable for major pest outbreaks. Continue routine monitoring.'
        action = 'Maintain regular inspection schedule (every 2-3 days). No immediate action needed.'
        risks = [
            {'name': 'Aphids', 'level': 'Low', 'action': 'Routine monitoring'},
            {'name': 'Caterpillars', 'level': 'Low', 'action': 'Weekly inspection'},
            {'name': 'Beetles', 'level': 'Low', 'action': 'Visual checks'}
        ]
    
    return {
        'status': status,
        'advice': advice,
        'action': action,
        'risk_score': pest_risk_score,
        'risks': risks,
        'inspection_frequency': 'Twice daily' if pest_risk_score >= 60 else 'Daily' if pest_risk_score >= 35 else 'Every 2-3 days',
        'ai_confidence': 85
    }

def ai_weather_advisor(temp, humidity):
    """AI-based weather prediction and farming advice"""
    import random
    
    # Simulate weather prediction (in production, use weather API)
    # Predict based on current conditions
    if humidity > 75:
        rain_probability = 70
        forecast = [
            {'day': 'Today', 'icon': '⛅', 'temp': temp, 'rain': 30},
            {'day': 'Tomorrow', 'icon': '🌧️', 'temp': temp - 2, 'rain': 70},
            {'day': 'Day 3', 'icon': '🌧️', 'temp': temp - 3, 'rain': 60}
        ]
        advice = '🌧️ RAIN EXPECTED: High probability of rain in 24-48 hours. Delay irrigation and fertilizer application. Prepare drainage systems.'
        actions = [
            'Postpone irrigation for 3-4 days',
            'Delay fertilizer application until after rain',
            'Check drainage channels',
            'Harvest ready crops before rain'
        ]
    elif humidity < 40:
        rain_probability = 10
        forecast = [
            {'day': 'Today', 'icon': '☀️', 'temp': temp, 'rain': 5},
            {'day': 'Tomorrow', 'icon': '☀️', 'temp': temp + 1, 'rain': 5},
            {'day': 'Day 3', 'icon': '☀️', 'temp': temp + 2, 'rain': 10}
        ]
        advice = '☀️ DRY CONDITIONS: Low humidity and no rain expected. Increase irrigation frequency. Monitor for heat stress.'
        actions = [
            'Increase irrigation frequency by 20%',
            'Apply mulch to retain moisture',
            'Monitor crops for wilting',
            'Consider shade nets for sensitive crops'
        ]
    else:
        rain_probability = 40
        forecast = [
            {'day': 'Today', 'icon': '⛅', 'temp': temp, 'rain': 20},
            {'day': 'Tomorrow', 'icon': '⛅', 'temp': temp - 1, 'rain': 30},
            {'day': 'Day 3', 'icon': '🌤️', 'temp': temp, 'rain': 25}
        ]
        advice = '🌤️ MIXED CONDITIONS: Variable weather expected. Maintain flexible farming schedule. Monitor forecasts daily.'
        actions = [
            'Follow standard irrigation schedule',
            'Be ready to adjust plans',
            'Monitor weather updates',
            'Prepare for both scenarios'
        ]
    
    return {
        'forecast': forecast,
        'advice': advice,
        'actions': actions,
        'rain_probability': rain_probability,
        'ai_confidence': 78
    }

def calculate_evapotranspiration(temp, humidity):
    """Calculate evapotranspiration rate (simplified Penman-Monteith)"""
    # Simplified ET calculation
    # Real implementation would use solar radiation, wind speed, etc.
    temp_diff = abs(temp - humidity)  # Use absolute value to avoid negative square root
    base_et = 0.0023 * (temp + 17.8) * (temp_diff ** 0.5)
    return max(0, base_et * 10)  # Convert to mm/day

def calculate_water_requirement(moisture, temp, humidity):
    """Calculate water requirement in L/m²"""
    target_moisture = 65  # Optimal soil moisture
    deficit = max(0, target_moisture - moisture)
    
    # Adjust for temperature and humidity
    temp_factor = 1 + (temp - 25) * 0.02
    humidity_factor = 1 - (humidity - 60) * 0.01
    
    water_needed = deficit * 0.5 * temp_factor * humidity_factor
    return max(0, water_needed)

def generate_ai_insights(moisture, temp, humidity, air_quality, tds):
    """Generate AI-powered farming insights"""
    insights = []
    
    # Moisture insight
    if moisture < 40:
        insights.append({
            'type': 'warning',
            'title': 'Soil Moisture Critical',
            'message': f'Moisture at {moisture:.1f}% is below optimal. Immediate action required.',
            'priority': 'high'
        })
    elif moisture > 80:
        insights.append({
            'type': 'warning',
            'title': 'Soil Too Wet',
            'message': f'Moisture at {moisture:.1f}% is too high. Risk of waterlogging and root diseases.',
            'priority': 'medium'
        })
    
    # Temperature insight
    if temp > 30:
        insights.append({
            'type': 'alert',
            'title': 'Heat Stress Risk',
            'message': f'Temperature {temp:.1f}°C may cause crop stress. Consider shade or cooling measures.',
            'priority': 'medium'
        })
    elif temp < 20:
        insights.append({
            'type': 'alert',
            'title': 'Cold Stress Risk',
            'message': f'Temperature {temp:.1f}°C is low. Protect sensitive crops from cold damage.',
            'priority': 'medium'
        })
    
    # Humidity insight
    if humidity > 75:
        insights.append({
            'type': 'warning',
            'title': 'High Humidity Alert',
            'message': f'Humidity {humidity:.1f}% increases fungal disease risk. Improve ventilation.',
            'priority': 'medium'
        })
    elif humidity < 40:
        insights.append({
            'type': 'alert',
            'title': 'Low Humidity Warning',
            'message': f'Humidity {humidity:.1f}% is low. Plants may experience water stress. Consider misting.',
            'priority': 'low'
        })
    
    # Air quality insight
    if air_quality > 100:
        insights.append({
            'type': 'alert',
            'title': 'Poor Air Quality',
            'message': f'Air quality {air_quality:.0f} ppm may affect crop health and photosynthesis. Monitor closely.',
            'priority': 'low'
        })
    
    # Water quality insight
    if tds > 400:
        insights.append({
            'type': 'warning',
            'title': 'Water Quality Issue',
            'message': f'TDS {tds:.0f} ppm is elevated. Consider water filtration for irrigation to prevent salt buildup.',
            'priority': 'medium'
        })
    
    # Positive insight
    if 50 <= moisture <= 75 and 20 <= temp <= 30 and 45 <= humidity <= 75 and air_quality < 100 and tds < 400:
        insights.append({
            'type': 'success',
            'title': 'Optimal Growing Conditions',
            'message': 'All parameters in ideal range. Crops should thrive! Continue current management practices.',
            'priority': 'info'
        })
    
    # If no specific issues, provide general positive feedback
    if len(insights) == 0:
        insights.append({
            'type': 'success',
            'title': 'Good Conditions',
            'message': 'Environmental conditions are favorable for crop growth. Continue monitoring.',
            'priority': 'info'
        })
    
    return insights

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('sensor_update', sensor_data)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print('╔════════════════════════════════════════════════════════╗')
    print('║  KrishiShakti - Flask Server                          ║')
    print('║  Smart Agriculture & IoT Monitoring System            ║')
    print('╚════════════════════════════════════════════════════════╝')
    print('\n🌐 Server running on http://localhost:5000')
    print('📊 Dashboard: http://localhost:5000/dashboard.html')
    print('🔔 Press Ctrl+C to stop\n')
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
