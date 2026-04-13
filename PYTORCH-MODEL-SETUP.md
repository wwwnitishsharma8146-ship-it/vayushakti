# 🚀 PyTorch Model Setup - MobileNetV2

## ✅ Your Model is Ready!

You have a **MobileNetV2** model from Hugging Face in the `models/` folder.

### 📁 Model Files Found:
```
models/
├── pytorch_model.bin          ✅ PyTorch model weights
├── config.json                ✅ Model configuration
└── preprocessor_config.json   ✅ Image preprocessing config
```

### 📊 Model Details:
- **Architecture**: MobileNetV2 (Google)
- **Framework**: PyTorch + Hugging Face Transformers
- **Classes**: 38 plant diseases
- **Input Size**: 224x224 RGB images
- **Model Type**: Image Classification

---

## 🚀 Quick Setup (3 Steps)

### 1️⃣ Install Dependencies

**Option A: Use the install script**
```bash
chmod +x install_pytorch_model.sh
./install_pytorch_model.sh
```

**Option B: Manual installation**
```bash
# Install PyTorch (CPU version)
/storage/Desktop/sem2/t5env/bin/python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install Transformers
/storage/Desktop/sem2/t5env/bin/python -m pip install transformers

# Install other dependencies
/storage/Desktop/sem2/t5env/bin/python -m pip install pillow numpy
```

### 2️⃣ Test the Model

```bash
/storage/Desktop/sem2/t5env/bin/python ai_disease_model.py
```

Expected output:
```
╔════════════════════════════════════════════════════════╗
║  AI Crop Disease Detection Model Test                ║
╚════════════════════════════════════════════════════════╝

✅ Models folder found: models
✅ Config loaded
   Model: google/mobilenet_v2_1.0_224
   Classes: 38
   Image size: 224

🔄 Testing model loading...
Loading disease detection model from models...
✅ Model loaded successfully on cpu!

📊 Sample disease classes:
   0: Apple Scab
   1: Apple with Black Rot
   2: Cedar Apple Rust
   3: Healthy Apple
   4: Healthy Blueberry Plant
   ... and 33 more

🎉 Disease detection is ready to use!
```

### 3️⃣ Start the Server

```bash
/storage/Desktop/sem2/t5env/bin/python app.py
```

Then open: `http://localhost:5001/agriculture.html`

---

## 🎯 Supported Disease Classes (38 Total)

Your model can detect:

### 🍎 Apple (4 classes)
- Apple Scab
- Apple with Black Rot
- Cedar Apple Rust
- Healthy Apple

### 🫐 Blueberry (1 class)
- Healthy Blueberry Plant

### 🍒 Cherry (2 classes)
- Cherry with Powdery Mildew
- Healthy Cherry Plant

### 🌽 Corn/Maize (4 classes)
- Corn with Cercospora and Gray Leaf Spot
- Corn with Common Rust
- Corn with Northern Leaf Blight
- Healthy Corn Plant

### 🍇 Grape (4 classes)
- Grape with Black Rot
- Grape with Esca (Black Measles)
- Grape with Isariopsis Leaf Spot
- Healthy Grape Plant

### 🍊 Orange (1 class)
- Orange with Citrus Greening

### 🍑 Peach (2 classes)
- Peach with Bacterial Spot
- Healthy Peach Plant

### 🌶️ Bell Pepper (2 classes)
- Bell Pepper with Bacterial Spot
- Healthy Bell Pepper Plant

### 🥔 Potato (3 classes)
- Potato with Early Blight
- Potato with Late Blight
- Healthy Potato Plant

### 🫐 Raspberry (1 class)
- Healthy Raspberry Plant

### 🫘 Soybean (1 class)
- Healthy Soybean Plant

### 🎃 Squash (1 class)
- Squash with Powdery Mildew

### 🍓 Strawberry (2 classes)
- Strawberry with Leaf Scorch
- Healthy Strawberry Plant

### 🍅 Tomato (10 classes)
- Tomato with Bacterial Spot
- Tomato with Early Blight
- Tomato with Late Blight
- Tomato with Leaf Mold
- Tomato with Septoria Leaf Spot
- Tomato with Spider Mites
- Tomato with Target Spot
- Tomato Yellow Leaf Curl Virus
- Tomato Mosaic Virus
- Healthy Tomato Plant

---

## 🔧 How It Works

### Image Processing Pipeline:
```
User uploads image
    ↓
PIL opens and converts to RGB
    ↓
Hugging Face AutoImageProcessor
    ↓
Resize to 224x224
    ↓
Normalize (mean=[0.5,0.5,0.5], std=[0.5,0.5,0.5])
    ↓
Convert to PyTorch tensor
    ↓
MobileNetV2 model prediction
    ↓
Softmax probabilities
    ↓
Top prediction + confidence
    ↓
Disease name + recommendations
```

### Model Architecture:
- **Base**: MobileNetV2 (efficient CNN)
- **Pretrained**: ImageNet weights
- **Fine-tuned**: PlantVillage dataset
- **Output**: 38-class classification

---

## 📊 API Response Format

```json
{
    "success": true,
    "disease": "Tomato with Early Blight",
    "confidence": 87.3,
    "is_healthy": false,
    "recommendations": [
        "Remove and destroy infected plants immediately",
        "Apply fungicide (Chlorothalonil or Mancozeb)",
        "Rotate crops next season",
        "Avoid overhead irrigation",
        "Space plants properly for air flow"
    ],
    "raw_class": "Tomato with Early Blight",
    "model_type": "MobileNetV2 (PyTorch)"
}
```

---

## 🎨 Usage Example

### From Web Interface:
1. Go to `http://localhost:5001/agriculture.html`
2. Click "📸 Click Here to Upload Crop Image"
3. Select a crop image (tomato, potato, apple, etc.)
4. Click "🔍 Analyze with AI"
5. View results with confidence score and recommendations

### From Python:
```python
from ai_disease_model import predict_disease

# Predict from image file
result = predict_disease('path/to/crop_image.jpg')

print(f"Disease: {result['disease']}")
print(f"Confidence: {result['confidence']}%")
print(f"Healthy: {result['is_healthy']}")
print(f"Recommendations: {result['recommendations']}")
```

---

## 🚀 Performance

### Speed:
- **CPU**: 1-3 seconds per image
- **GPU**: 0.5-1 second per image (if available)

### Accuracy:
- **Training Dataset**: PlantVillage
- **Model**: MobileNetV2 (optimized for mobile/edge)
- **Expected Accuracy**: 85-95% on clear images

### Requirements:
- **Memory**: ~500MB RAM
- **Storage**: ~15MB (model files)
- **CPU**: Any modern processor

---

## 🐛 Troubleshooting

### Error: "transformers not found"
```bash
/storage/Desktop/sem2/t5env/bin/python -m pip install transformers
```

### Error: "torch not found"
```bash
/storage/Desktop/sem2/t5env/bin/python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Error: "Model files not found"
Make sure you have:
```
models/
├── pytorch_model.bin
├── config.json
└── preprocessor_config.json
```

### Low Confidence Predictions
- Use clear, well-lit images
- Ensure disease symptoms are visible
- Crop image to focus on affected leaves
- Avoid blurry or dark images

---

## 📚 Technical Details

### Model Configuration:
```json
{
  "model_type": "mobilenet_v2",
  "image_size": 224,
  "num_channels": 3,
  "num_labels": 38,
  "architecture": "MobileNetV2ForImageClassification"
}
```

### Preprocessing:
```json
{
  "do_resize": true,
  "do_center_crop": true,
  "do_normalize": true,
  "image_mean": [0.5, 0.5, 0.5],
  "image_std": [0.5, 0.5, 0.5],
  "crop_size": {"height": 224, "width": 224}
}
```

---

## ✅ Advantages of MobileNetV2

1. **Lightweight**: Only ~15MB model size
2. **Fast**: Optimized for mobile/edge devices
3. **Accurate**: Good performance on plant diseases
4. **Efficient**: Low memory and CPU usage
5. **Portable**: Works on CPU without GPU

---

## 🎉 You're All Set!

Your PyTorch-based disease detection is ready to use!

### Next Steps:
1. ✅ Install dependencies (if not done)
2. ✅ Test the model
3. ✅ Start the Flask server
4. ✅ Upload crop images and get predictions!

---

**Need Help?** 
- Check `DISEASE-DETECTION-COMPLETE.md` for general info
- Review `ai_disease_model.py` for code details
- Run `test_disease_detection.py` to verify setup
