#!/usr/bin/env python3
"""
Quick location update - Edit the city and country below
"""

import json
import os
import gspread
from google.oauth2.service_account import Credentials

# ============================================
# EDIT THESE VALUES TO YOUR LOCATION
# ============================================
CITY = "Delhi"           # Change this to your city
COUNTRY = "India"        # Change this to your country
LATITUDE = 28.6139       # Optional: your latitude
LONGITUDE = 77.2090      # Optional: your longitude
# ============================================

def update_local_data():
    """Update location in local history file"""
    history_file = 'data/history.json'
    
    if not os.path.exists(history_file):
        print("❌ No history file found")
        return False
    
    try:
        with open(history_file, 'r') as f:
            data = json.load(f)
        
        print(f"📊 Updating {len(data)} records...")
        
        for record in data:
            if 'location' not in record:
                record['location'] = {}
            
            record['location']['city'] = CITY
            record['location']['country'] = COUNTRY
            record['location']['latitude'] = LATITUDE
            record['location']['longitude'] = LONGITUDE
        
        with open(history_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Updated local data to: {CITY}, {COUNTRY}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def update_google_sheets():
    """Update location in Google Sheets"""
    try:
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        print("\n🔄 Updating Google Sheets...")
        
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open("KrishiShaktiData")
        worksheet = spreadsheet.worksheet("Sensor Data")
        
        # Get number of rows
        all_values = worksheet.get_all_values()
        num_rows = len(all_values)
        
        print(f"📝 Updating {num_rows-1} rows...")
        
        # Update city column (K) and country column (L)
        # Build update list
        city_updates = [[CITY]] * (num_rows - 1)
        country_updates = [[COUNTRY]] * (num_rows - 1)
        
        # Update in batches
        worksheet.update(f'K2:K{num_rows}', city_updates)
        worksheet.update(f'L2:L{num_rows}', country_updates)
        
        print(f"✅ Google Sheets updated to: {CITY}, {COUNTRY}")
        return True
        
    except Exception as e:
        print(f"⚠️ Could not update Google Sheets: {str(e)}")
        return False

def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║  Quick Location Update                                ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    print(f"📍 Setting location to: {CITY}, {COUNTRY}")
    print(f"   Coordinates: {LATITUDE}°, {LONGITUDE}°\n")
    
    # Update local data
    update_local_data()
    
    # Update Google Sheets
    update_google_sheets()
    
    print("\n" + "="*60)
    print("✅ LOCATION UPDATED!")
    print("="*60)
    print(f"\n📍 New location: {CITY}, {COUNTRY}")
    print("\n💡 Refresh to see changes:")
    print("   Dashboard: http://localhost:5001/dashboard.html")
    print("   Google Sheet: https://docs.google.com/spreadsheets/d/17FoN1d2P59MjaPIXD868wNYLq18HxBkq6DeQz46A-54")

if __name__ == '__main__':
    main()
