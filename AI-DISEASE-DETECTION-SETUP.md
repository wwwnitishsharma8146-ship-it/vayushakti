# 🌱 AI Crop Disease Detection - Setup Guide

## ✅ Feature Successfully Added!

The AI crop disease detection feature has been integrated into your KrishiShakti Agriculture AI system.

## 📁 Files Created/Modified

### New Files:
1. **`ai_disease_model.py`** - AI model handler with 38 disease classes
2. **`AI-DISEASE-DETECTION-SETUP.md`** - This setup guide

### Modified Files:
1. **`app.py`** - Added `/api/predict-disease` endpoint
2. **`public/agriculture.js`** - Updated image upload and analysis functions

## 🚀 How It Works

### User Flow:
1. User opens **Agriculture AI** page (`/agriculture.html`)
2. Clicks "📸 Click Here to Upload Crop Image"
3. Selects an image from their device
4. Clicks "🔍 Analyze with AI"
5. System sends image to backend
6. AI model predicts disease
7. Results displayed with recommendations

### Technical Flow:
```
Frontend (agriculture.html)
    ↓ (Upload Image)
agriculture.js
    ↓ (FormData with image)
Flask Backend (app.py)
    ↓ (/api/predict-disease)
ai_disease_model.py
    ↓ (TensorFlow/Keras)
plant_disease_model.h5
    ↓ (Prediction)
JSON Response
    ↓
Display Results
```

## 📦 Installation

### 1. Install Required Dependencies

```bash
/storage/Desktop/sem2/t5env/bin/python -m pip install tensorflow pillow numpy
```

Or add to `requirements.txt`:
```
tensorflow>=2.13.0
pillow>=10.0.0
numpy>=1.24.0
```

### 2. Download the AI Model

You need a pretrained PlantVillage model. Here are your options:

#### Option A: Download from Kaggle
```bash
# Install kaggle CLI
pip install kaggle

# Download PlantVillage dataset with model
kaggle datasets download -d vipoooool/new-plant-diseases-dataset

# Or manually download from:
# https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset
```

#### Option B: Train Your Own Model
```python
# Use the PlantVillage dataset to train a model
# Example training script available at:
# https://github.com/spMohanty/PlantVillage-Dataset
```

#### Option C: Use Pre-trained Model
Search for "PlantVillage keras model" on:
- GitHub
- Kaggle
- TensorFlow Hub

### 3. Place Model File

Save the model as `plant_disease_model.h5` in your project root:

```
krisi_aman-main/
├── plant_disease_model.h5  ← Place model here
├── ai_disease_model.py
├── app.py
├── public/
│   ├── agriculture.html
│   └── agriculture.js
└── ...
```

### 4. Test the Model

```bash
/storage/Desktop/sem2/t5env/bin/python ai_disease_model.py
```

Expected output:
```
╔════════════════════════════════════════════════════════╗
║  AI Crop Disease Detection Model Test                ║
╚════════════════════════════════════════════════════════╝

✅ Model file found: plant_disease_model.h5
📊 Supported classes: 38

Testing model loading...
Loading disease detection model from plant_disease_model.h5...
✅ Model loaded successfully!
   Input shape: (None, 224, 224, 3)
   Output shape: (None, 38)

🎉 Disease detection is ready to use!
```

## 🎯 Supported Disease Classes (38 Total)

The model can detect diseases in these crops:

### 🍎 Apple (4 classes)
- Apple Scab
- Black Rot
- Cedar Apple Rust
- Healthy

### 🫐 Blueberry (1 class)
- Healthy

### 🍒 Cherry (2 classes)
- Powdery Mildew
- Healthy

### 🌽 Corn/Maize (4 classes)
- Cercospora Leaf Spot
- Common Rust
- Northern Leaf Blight
- Healthy

### 🍇 Grape (4 classes)
- Black Rot
- Esca (Black Measles)
- Leaf Blight
- Healthy

### 🍊 Orange (1 class)
- Huanglongbing (Citrus Greening)

### 🍑 Peach (2 classes)
- Bacterial Spot
- Healthy

### 🌶️ Pepper/Bell (2 classes)
- Bacterial Spot
- Healthy

### 🥔 Potato (3 classes)
- Early Blight
- Late Blight
- Healthy

### 🫐 Raspberry (1 class)
- Healthy

### 🫘 Soybean (1 class)
- Healthy

### 🎃 Squash (1 class)
- Powdery Mildew

### 🍓 Strawberry (2 classes)
- Leaf Scorch
- Healthy

### 🍅 Tomato (10 classes)
- Bacterial Spot
- Early Blight
- Late Blight
- Leaf Mold
- Septoria Leaf Spot
- Spider Mites
- Target Spot
- Yellow Leaf Curl Virus
- Mosaic Virus
- Healthy

## 🔧 API Endpoint

### POST `/api/predict-disease`

**Request:**
```javascript
const formData = new FormData();
formData.append('image', imageFile);

fetch('/api/predict-disease', {
    method: 'POST',
    body: formData
})
```

**Response (Success):**
```json
{
    "success": true,
    "disease": "Tomato - Early Blight",
    "confidence": 87.3,
    "is_healthy": false,
    "recommendations": [
        "Remove infected leaves immediately",
        "Apply fungicide (Chlorothalonil or Mancozeb)",
        "Improve air circulation around plants",
        "Avoid overhead watering",
        "Rotate crops next season"
    ],
    "raw_class": "Tomato___Early_blight"
}
```

**Response (Error):**
```json
{
    "success": false,
    "error": "Model file not found",
    "message": "Please ensure plant_disease_model.h5 is in the project root."
}
```

## 🎨 Frontend Integration

The feature is already integrated into `agriculture.html`:

```html
<!-- Upload Section -->
<div class="simple-upload-section">
    <input type="file" id="crop-image" accept="image/*" style="display: none;">
    <button class="btn-upload-large" id="upload-btn">
        📸 Click Here to Upload Crop Image
    </button>
</div>

<!-- Preview Section -->
<div id="image-preview" style="display: none;">
    <img id="preview-img" src="" alt="Crop preview">
    <div class="preview-actions">
        <button class="btn-analyze" id="analyze-btn">🔍 Analyze with AI</button>
        <button class="btn-reset" id="reset-btn">🔄 Upload New Image</button>
    </div>
</div>

<!-- Results Section -->
<div id="analysis-result" class="analysis-result" style="display: none;">
    <!-- Results populated by JavaScript -->
</div>
```

## 🛡️ Demo Mode

If the model file is not available, the system automatically falls back to **Demo Mode**:

- ✅ System continues to work
- ✅ Returns simulated predictions
- ✅ Shows demo mode banner
- ✅ Provides realistic recommendations

Demo mode is perfect for:
- Testing the UI/UX
- Development without model file
- Demonstrations

## 🧪 Testing

### Test with Sample Images

1. Start the Flask server:
```bash
/storage/Desktop/sem2/t5env/bin/python app.py
```

2. Open browser:
```
http://localhost:5001/agriculture.html
```

3. Upload a crop image

4. Click "Analyze with AI"

5. View results

### Test API Directly

```bash
curl -X POST http://localhost:5001/api/predict-disease \
  -F "image=@/path/to/crop_image.jpg"
```

## 📊 Model Requirements

### Input:
- **Format**: RGB image
- **Size**: 224x224 pixels (auto-resized)
- **Normalization**: Pixel values scaled to [0, 1]
- **Batch**: Single image with batch dimension

### Output:
- **Format**: Softmax probabilities
- **Classes**: 38 disease categories
- **Confidence**: Percentage (0-100%)

## 🔐 Security Considerations

1. **File Size Limit**: Max 10MB per image
2. **File Type Validation**: Only image files accepted
3. **Error Handling**: Graceful fallback to demo mode
4. **Input Sanitization**: PIL Image validation

## 🚀 Performance

- **Prediction Time**: ~1-3 seconds (depends on hardware)
- **Model Size**: ~80-100 MB (typical for PlantVillage)
- **Memory Usage**: ~500MB-1GB during inference

## 📈 Future Enhancements

Potential improvements:
- [ ] Add image preprocessing (crop, rotate, enhance)
- [ ] Support multiple image upload
- [ ] Save prediction history
- [ ] Export results as PDF report
- [ ] Add confidence threshold settings
- [ ] Integrate with sensor data for context
- [ ] Multi-language support for recommendations
- [ ] Mobile app integration

## 🐛 Troubleshooting

### Model Not Loading
```
Error: Model file 'plant_disease_model.h5' not found
```
**Solution**: Download and place model in project root

### TensorFlow Import Error
```
ModuleNotFoundError: No module named 'tensorflow'
```
**Solution**: 
```bash
/storage/Desktop/sem2/t5env/bin/python -m pip install tensorflow
```

### Image Upload Not Working
**Solution**: Check browser console for errors, ensure file input is visible

### Low Confidence Predictions
**Solution**: 
- Use clear, well-lit images
- Ensure disease symptoms are visible
- Crop image to focus on affected area

## 📚 Resources

- **PlantVillage Dataset**: https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset
- **TensorFlow Docs**: https://www.tensorflow.org/
- **Keras Models**: https://keras.io/api/models/
- **Plant Disease Recognition**: https://github.com/spMohanty/PlantVillage-Dataset

## ✅ Verification Checklist

- [x] `ai_disease_model.py` created
- [x] `/api/predict-disease` endpoint added to `app.py`
- [x] Frontend updated in `agriculture.js`
- [x] Image upload functionality working
- [x] Demo mode fallback implemented
- [x] Error handling added
- [x] Documentation created

## 🎉 You're All Set!

The AI crop disease detection feature is now fully integrated. Once you add the model file, you'll have a powerful tool for identifying crop diseases in real-time!

---

**Need Help?** Check the troubleshooting section or review the code comments in `ai_disease_model.py`.
