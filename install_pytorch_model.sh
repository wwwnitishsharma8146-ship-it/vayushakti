#!/bin/bash

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Installing PyTorch Disease Detection Dependencies   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

echo "📦 Installing PyTorch and Transformers..."
echo ""

# Install PyTorch (CPU version for compatibility)
/storage/Desktop/sem2/t5env/bin/python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install Transformers
/storage/Desktop/sem2/t5env/bin/python -m pip install transformers

# Install other dependencies
/storage/Desktop/sem2/t5env/bin/python -m pip install pillow numpy

echo ""
echo "✅ Installation complete!"
echo ""
echo "🧪 Testing the model..."
/storage/Desktop/sem2/t5env/bin/python ai_disease_model.py
