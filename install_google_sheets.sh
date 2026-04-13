#!/bin/bash

echo "╔════════════════════════════════════════════════════════╗"
echo "║  KrishiShakti Google Sheets Setup                     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

echo "📦 Installing Google Sheets libraries..."
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Libraries installed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Read GOOGLE-SHEETS-SETUP.md for complete instructions"
    echo "2. Go to https://console.cloud.google.com/"
    echo "3. Create a project and enable Google Sheets API"
    echo "4. Create service account and download credentials.json"
    echo "5. Place credentials.json in this folder"
    echo "6. Run: python google_sheets_setup.py"
    echo ""
else
    echo ""
    echo "❌ Installation failed!"
    echo "Try manually: pip install gspread google-auth"
fi
