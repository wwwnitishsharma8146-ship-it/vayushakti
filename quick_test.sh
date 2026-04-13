#!/bin/bash

# Quick test script for KrishiShakti AI Disease Detection

PYTHON="/storage/Desktop/sem2/t5env/bin/python"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  KrishiShakti - Quick Test Script                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "1. Checking Python environment..."
if [ -f "$PYTHON" ]; then
    echo "   ✓ Python found: $PYTHON"
    $PYTHON --version
else
    echo "   ✗ Python not found at $PYTHON"
    exit 1
fi

echo ""

# Check dependencies
echo "2. Checking dependencies..."
DEPS=("flask" "torch" "transformers" "pillow")
MISSING=()

for dep in "${DEPS[@]}"; do
    if $PYTHON -c "import ${dep}" 2>/dev/null; then
        echo "   ✓ ${dep}"
    else
        echo "   ✗ ${dep} (missing)"
        MISSING+=("${dep}")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  Missing dependencies: ${MISSING[*]}"
    echo ""
    echo "Install with:"
    echo "  $PYTHON -m pip install ${MISSING[*]}"
    echo ""
    read -p "Install now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $PYTHON -m pip install ${MISSING[*]}
    else
        exit 1
    fi
fi

echo ""

# Check model files
echo "3. Checking model files..."
if [ -d "models" ]; then
    echo "   ✓ models/ directory exists"
    
    if [ -f "models/pytorch_model.bin" ]; then
        echo "   ✓ pytorch_model.bin"
    else
        echo "   ✗ pytorch_model.bin (missing)"
    fi
    
    if [ -f "models/config.json" ]; then
        echo "   ✓ config.json"
    else
        echo "   ✗ config.json (missing)"
    fi
    
    if [ -f "models/preprocessor_config.json" ]; then
        echo "   ✓ preprocessor_config.json"
    else
        echo "   ✗ preprocessor_config.json (missing)"
    fi
else
    echo "   ✗ models/ directory not found"
    echo ""
    echo "⚠️  AI model will run in DEMO MODE"
fi

echo ""

# Check if Flask is running
echo "4. Checking Flask server..."
if curl -s http://localhost:5000/api/sensors > /dev/null 2>&1; then
    echo "   ✓ Flask server is running"
    echo ""
    echo "Running upload test..."
    echo ""
    $PYTHON test_image_upload.py
else
    echo "   ✗ Flask server is NOT running"
    echo ""
    echo "Start Flask server with:"
    echo "  $PYTHON app.py"
    echo ""
    echo "Then run this test again."
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  Test Complete                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
