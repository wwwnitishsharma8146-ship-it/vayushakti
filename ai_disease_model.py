"""
AI Crop Disease Detection Model
Uses pretrained MobileNetV2 model from Hugging Face for disease classification
"""

import torch
from PIL import Image
import os
import json
import numpy as np

# Model path
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "pytorch_model.bin")
CONFIG_PATH = os.path.join(MODEL_DIR, "config.json")
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "preprocessor_config.json")

# Load model (lazy loading)
_model = None
_config = None
_preprocessor_config = None
_device = None

def load_config():
    """Load model configuration"""
    global _config, _preprocessor_config
    
    if _config is None:
        with open(CONFIG_PATH, 'r') as f:
            _config = json.load(f)
    
    if _preprocessor_config is None:
        with open(PREPROCESSOR_PATH, 'r') as f:
            _preprocessor_config = json.load(f)
    
    return _config, _preprocessor_config

def load_model():
    """Load the pretrained PyTorch model using Hugging Face transformers"""
    global _model, _device
    
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model file '{MODEL_PATH}' not found. "
                "Please ensure the models folder contains pytorch_model.bin"
            )
        
        print(f"Loading disease detection model from {MODEL_DIR}...")
        
        try:
            # Import transformers
            from transformers import AutoModelForImageClassification, AutoImageProcessor
            
            # Load model and processor
            _model = AutoModelForImageClassification.from_pretrained(MODEL_DIR)
            
            # Set device (CPU or GPU)
            _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            _model.to(_device)
            _model.eval()
            
            print(f"✅ Model loaded successfully on {_device}!")
            
        except ImportError:
            raise ImportError(
                "Transformers library not found. Install with: "
                "pip install transformers torch torchvision"
            )
    
    return _model

def preprocess_image(image_file):
    """
    Preprocess image for model prediction using Hugging Face processor
    
    Args:
        image_file: File object or path to image
    
    Returns:
        Preprocessed tensor ready for prediction
    """
    from transformers import AutoImageProcessor
    
    # Load image processor
    processor = AutoImageProcessor.from_pretrained(MODEL_DIR)
    
    # Open and convert image to RGB
    img = Image.open(image_file).convert("RGB")
    
    # Process image
    inputs = processor(images=img, return_tensors="pt")
    
    # Move to device
    if _device:
        inputs = {k: v.to(_device) for k, v in inputs.items()}
    
    return inputs

def predict_disease(image_file):
    """
    Predict disease from crop image using PyTorch model
    
    Args:
        image_file: Uploaded image file
    
    Returns:
        dict: Prediction results with disease name, confidence, and recommendations
    """
    try:
        # Load model and config
        model = load_model()
        config, _ = load_config()
        
        # Get disease classes
        id2label = config['id2label']
        
        # Preprocess image
        inputs = preprocess_image(image_file)
        
        # Make prediction
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            
            # Get probabilities
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            
            # Get top prediction
            predicted_class_idx = probabilities.argmax(-1).item()
            confidence = probabilities[0][predicted_class_idx].item()
        
        # Get disease name
        disease_name = id2label[str(predicted_class_idx)]
        
        # Determine if healthy or diseased
        is_healthy = "healthy" in disease_name.lower()
        
        # Get recommendations
        recommendations = get_recommendations(disease_name, is_healthy)
        
        return {
            "success": True,
            "disease": disease_name,
            "confidence": round(confidence * 100, 2),
            "is_healthy": is_healthy,
            "recommendations": recommendations,
            "raw_class": disease_name,
            "model_type": "MobileNetV2 (PyTorch)"
        }
        
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Model files not found. Please ensure models folder contains all required files."
        }
    except ImportError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Required libraries not installed. Run: pip install transformers torch torchvision"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error processing image. Please try again with a clear crop image."
        }

def get_recommendations(disease_name, is_healthy):
    """
    Get treatment recommendations based on disease
    
    Args:
        disease_name: Name of detected disease
        is_healthy: Boolean indicating if crop is healthy
    
    Returns:
        list: Treatment recommendations
    """
    if is_healthy:
        return [
            "✅ Your crop appears healthy!",
            "Continue regular monitoring",
            "Maintain proper watering schedule",
            "Ensure adequate sunlight and nutrients"
        ]
    
    # Disease-specific recommendations
    disease_lower = disease_name.lower()
    
    if "scab" in disease_lower:
        return [
            "Remove infected leaves immediately",
            "Apply fungicide (Captan or Myclobutanil)",
            "Improve air circulation around plants",
            "Avoid overhead watering",
            "Clean up fallen leaves and debris"
        ]
    elif "black rot" in disease_lower:
        return [
            "Prune and destroy infected parts",
            "Apply copper-based fungicide",
            "Remove fallen leaves and debris",
            "Ensure proper drainage",
            "Use disease-resistant varieties"
        ]
    elif "rust" in disease_lower:
        return [
            "Remove infected leaves",
            "Apply sulfur-based fungicide",
            "Improve air circulation",
            "Water at soil level, not leaves",
            "Avoid working with wet plants"
        ]
    elif "blight" in disease_lower:
        return [
            "Remove and destroy infected plants immediately",
            "Apply fungicide (Chlorothalonil or Mancozeb)",
            "Rotate crops next season",
            "Avoid overhead irrigation",
            "Space plants properly for air flow"
        ]
    elif "powdery mildew" in disease_lower:
        return [
            "Apply neem oil or sulfur spray",
            "Improve air circulation",
            "Remove infected leaves",
            "Avoid overhead watering",
            "Increase sunlight exposure"
        ]
    elif "bacterial spot" in disease_lower:
        return [
            "Remove infected leaves",
            "Apply copper-based bactericide",
            "Avoid overhead irrigation",
            "Use disease-free seeds next season",
            "Disinfect tools between plants"
        ]
    elif "leaf spot" in disease_lower or "cercospora" in disease_lower:
        return [
            "Remove infected leaves",
            "Apply appropriate fungicide",
            "Improve air circulation",
            "Water at base of plants",
            "Rotate crops annually"
        ]
    elif "mosaic" in disease_lower or "virus" in disease_lower or "curl" in disease_lower:
        return [
            "Remove and destroy infected plants",
            "Control aphids and other vectors",
            "Use virus-resistant varieties",
            "Disinfect tools between plants",
            "Remove weeds that harbor viruses"
        ]
    elif "mold" in disease_lower:
        return [
            "Improve ventilation and reduce humidity",
            "Remove infected leaves",
            "Apply fungicide if severe",
            "Avoid overhead watering",
            "Space plants for better air flow"
        ]
    elif "greening" in disease_lower:
        return [
            "Remove infected trees immediately",
            "Control psyllid insects (disease vector)",
            "Use certified disease-free nursery stock",
            "Apply systemic insecticides",
            "Consult local agricultural extension"
        ]
    else:
        return [
            "Consult local agricultural expert",
            "Remove infected plant parts",
            "Apply appropriate fungicide/pesticide",
            "Monitor crop regularly",
            "Improve overall plant health"
        ]

# Test function
if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════╗")
    print("║  AI Crop Disease Detection Model Test                ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    if not os.path.exists(MODEL_DIR):
        print(f"❌ Models folder '{MODEL_DIR}' not found!")
        print("\n📋 Required structure:")
        print("   models/")
        print("   ├── pytorch_model.bin")
        print("   ├── config.json")
        print("   └── preprocessor_config.json\n")
    elif not os.path.exists(MODEL_PATH):
        print(f"❌ Model file '{MODEL_PATH}' not found!")
    else:
        print(f"✅ Models folder found: {MODEL_DIR}")
        
        try:
            config, preprocessor = load_config()
            print(f"✅ Config loaded")
            print(f"   Model: {config.get('_name_or_path', 'Unknown')}")
            print(f"   Classes: {len(config.get('id2label', {}))}")
            print(f"   Image size: {config.get('image_size', 224)}")
            
            print("\n🔄 Testing model loading...")
            model = load_model()
            print(f"✅ Model loaded successfully!")
            
            print("\n📊 Sample disease classes:")
            id2label = config['id2label']
            for i in range(min(5, len(id2label))):
                print(f"   {i}: {id2label[str(i)]}")
            print(f"   ... and {len(id2label) - 5} more")
            
            print("\n🎉 Disease detection is ready to use!\n")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("\n💡 Make sure to install required packages:")
            print("   pip install transformers torch torchvision\n")
