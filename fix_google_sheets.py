#!/usr/bin/env python3
"""
Fix Google Sheets - Try to write data to existing sheet
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import os

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def connect_to_sheet():
    """Connect to Google Sheets"""
    try:
        print("🔄 Connecting to Google Sheets...")
        
        # Load credentials
        creds = Credentials.from_service_account_file(
            'credentials.json',
            scopes=SCOPES
        )
        
        # Connect
        client = gspread.authorize(creds)
        
        # Try to open the sheet by name
        sheet_name = "KrishiShaktiData"
        print(f"🔍 Looking for sheet: {sheet_name}")
        
        try:
            spreadsheet = client.open(sheet_name)
            print(f"✅ Found spreadsheet: {spreadsheet.title}")
            print(f"📊 URL: {spreadsheet.url}")
            return client, spreadsheet
        except gspread.SpreadsheetNotFound:
            print(f"❌ Spreadsheet '{sheet_name}' not found")
            print("\n📋 Available spreadsheets:")
            try:
                sheets = client.openall()
                for i, s in enumerate(sheets, 1):
                    print(f"   {i}. {s.title} - {s.url}")
            except:
                print("   Could not list spreadsheets")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None, None

def setup_worksheet(spreadsheet):
    """Setup or get worksheet"""
    try:
        # Try to get existing worksheet
        try:
            worksheet = spreadsheet.worksheet("Sensor Data")
            print(f"✅ Found worksheet: Sensor Data")
        except:
            # Create new worksheet
            worksheet = spreadsheet.add_worksheet(
                title="Sensor Data",
                rows=1000,
                cols=15
            )
            print(f"✅ Created worksheet: Sensor Data")
            
            # Add headers
            headers = [
                'Timestamp',
                'Date',
                'Time',
                'Temperature (°C)',
                'Humidity (%)',
                'Soil Moisture (%)',
                'Air Quality (ppm)',
                'PM2.5 (µg/m³)',
                'PM10 (µg/m³)',
                'Water Quality (ppm)',
                'City',
                'Country',
                'Status'
            ]
            worksheet.append_row(headers)
            
            # Format header
            worksheet.format('A1:M1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.2},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'horizontalAlignment': 'CENTER'
            })
            print("✅ Added headers")
        
        return worksheet
        
    except Exception as e:
        print(f"❌ Error setting up worksheet: {str(e)}")
        return None

def load_local_data():
    """Load data from local history file"""
    try:
        history_file = 'data/history.json'
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                data = json.load(f)
            print(f"✅ Loaded {len(data)} records from local storage")
            return data
        else:
            print("❌ No local data found")
            return []
    except Exception as e:
        print(f"❌ Error loading local data: {str(e)}")
        return []

def add_data_to_sheet(worksheet, data_list):
    """Add data to Google Sheet"""
    try:
        print(f"\n📝 Adding {len(data_list)} records to Google Sheet...")
        
        rows_to_add = []
        
        for data in data_list:
            # Parse timestamp
            timestamp = data.get('timestamp', datetime.now().isoformat())
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                dt = datetime.now()
            
            # Extract location
            location = data.get('location', {})
            city = location.get('city', 'Unknown') if location else 'Unknown'
            country = location.get('country', 'Unknown') if location else 'Unknown'
            
            # Extract sensor values
            temp = data.get('dht22', {}).get('temperature', 0)
            humidity = data.get('dht22', {}).get('humidity', 0)
            soil_moisture = data.get('fc28', {}).get('value', 0)
            air_quality = data.get('mq135', {}).get('value', 0)
            pm25 = data.get('pms5003', {}).get('pm25', 0)
            pm10 = data.get('pms5003', {}).get('pm10', 0)
            tds = data.get('tds', {}).get('value', 0)
            
            # Determine status
            status = 'Good'
            if soil_moisture < 30 or temp > 35 or air_quality > 200:
                status = 'Warning'
            if soil_moisture < 20 or temp > 40 or air_quality > 300:
                status = 'Critical'
            
            # Prepare row
            row = [
                timestamp,
                dt.strftime('%Y-%m-%d'),
                dt.strftime('%H:%M:%S'),
                round(temp, 1),
                round(humidity, 1),
                round(soil_moisture, 1),
                round(air_quality, 1),
                round(pm25, 1),
                round(pm10, 1),
                round(tds, 0),
                city,
                country,
                status
            ]
            
            rows_to_add.append(row)
        
        # Add all rows at once (more efficient)
        if rows_to_add:
            worksheet.append_rows(rows_to_add)
            print(f"✅ Successfully added {len(rows_to_add)} rows to Google Sheet!")
            return True
        else:
            print("⚠️ No data to add")
            return False
            
    except Exception as e:
        print(f"❌ Error adding data: {str(e)}")
        
        # If batch fails, try one by one
        if "quota" in str(e).lower() or "storage" in str(e).lower():
            print("\n⚠️ Storage quota exceeded!")
            print("\n💡 Solutions:")
            print("1. Go to https://drive.google.com")
            print("2. Delete unnecessary files to free up space")
            print("3. Or use a different Google account")
            print("4. Or upgrade Google Drive storage")
            return False
        
        print("\n🔄 Trying to add rows one by one...")
        success_count = 0
        for i, row in enumerate(rows_to_add[:10], 1):  # Try first 10
            try:
                worksheet.append_row(row)
                success_count += 1
                print(f"✓ Added row {i}/10")
            except Exception as e2:
                print(f"✗ Failed row {i}: {str(e2)}")
                break
        
        if success_count > 0:
            print(f"\n✅ Added {success_count} rows before error")
            return True
        return False

def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║  Fix Google Sheets - Add Data to Your Sheet          ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    # Connect to Google Sheets
    client, spreadsheet = connect_to_sheet()
    
    if not spreadsheet:
        print("\n❌ Could not connect to Google Sheets")
        print("\n💡 Make sure:")
        print("1. The sheet 'krishisaktidata' exists")
        print("2. It's shared with the service account email from credentials.json")
        print("3. The service account has 'Editor' permissions")
        return
    
    # Setup worksheet
    worksheet = setup_worksheet(spreadsheet)
    
    if not worksheet:
        print("\n❌ Could not setup worksheet")
        return
    
    # Load local data
    data_list = load_local_data()
    
    if not data_list:
        print("\n⚠️ No local data to upload")
        print("Run: python3 add_test_data.py to generate data first")
        return
    
    # Add data to sheet
    success = add_data_to_sheet(worksheet, data_list)
    
    if success:
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print(f"\n📊 Open your Google Sheet:")
        print(f"   {spreadsheet.url}")
        print("\n💡 Refresh the page to see your data!")
    else:
        print("\n" + "="*60)
        print("❌ FAILED")
        print("="*60)
        print("\n💡 Your data is still available locally at:")
        print("   http://localhost:5001/dashboard.html")

if __name__ == '__main__':
    main()
