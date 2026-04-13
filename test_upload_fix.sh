#!/bin/bash

echo "=========================================="
echo "KrishiShakti - Test Image Upload Fix"
echo "=========================================="
echo ""

# Check if Flask is running
echo "Checking if Flask server is running..."
if curl -s http://localhost:5000/api/sensors > /dev/null 2>&1; then
    echo "✓ Flask server is running"
else
    echo "✗ Flask server is NOT running"
    echo ""
    echo "Please start the Flask server first:"
    echo "  /storage/Desktop/sem2/t5env/bin/python app.py"
    echo ""
    exit 1
fi

echo ""
echo "Running upload test..."
echo ""

# Run the test script
/storage/Desktop/sem2/t5env/bin/python test_image_upload.py

echo ""
echo "Test complete!"
