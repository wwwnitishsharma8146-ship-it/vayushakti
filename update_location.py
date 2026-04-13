#!/usr/bin/env python3
"""
Update location in sensor data
"""

import json
import os
from datetime import datetime

def update_location_in_history(city, country, latitude=None, longitude=None):
    """Update location in all historical data"""
    history_file = 'data/history.json'
    
    if not os.path.exists(history_file):
        print("❌ No history file found")
        return False
    
    try:
        # Load existing data
        with open(history_file, 'r') as f:
            data = json.load(f)
        
        print(f"📊 Found {len(data)} records")
        print(f"🔄 Updating location to: {city}, {country}")
        
        # Update location in all records
        updated_count = 0
        for record in data:
            if 'location' not in record:
                record['location'] = {}
            
            record['location']['city'] = city
            record['location']['country'] = country
            
            if latitude is not None:
                record['location']['latitude'] = latitude
            if longitude is not None:
                record['location']['longitude'] = longitude
            
            updated_count += 1
        
        # Save updated data
        with open(history_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Updated {updated_count} records")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def update_google_sheets_location(city, country):
    """Update location in Google Sheets"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        print("\n🔄 Updating Google Sheets...")
        
        # Connect
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # Open sheet
        spreadsheet = client.open("KrishiShaktiData")
        worksheet = spreadsheet.worksheet("Sensor Data")
        
        # Get all data
        all_data = worksheet.get_all_values()
        
        # Find city and country columns (K and L)
        city_col = 11  # Column K (0-indexed: 10, but 1-indexed for update: 11)
        country_col = 12  # Column L
        
        # Update all rows (skip header)
        print(f"📝 Updating {len(all_data)-1} rows in Google Sheets...")
        
        # Prepare batch update
        updates = []
        for i in range(2, len(all_data) + 1):  # Start from row 2 (skip header)
            updates.append({
                'range': f'K{i}',
                'values': [[city]]
            })
            updates.append({
                'range': f'L{i}',
                'values': [[country]]
            })
        
        # Batch update (more efficient)
        if updates:
            worksheet.batch_update(updates[:200])  # Update first 200 to avoid quota
            print(f"✅ Updated Google Sheets with new location")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Could not update Google Sheets: {str(e)}")
        return False

def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║  Update Location in Sensor Data                      ║")
    print("╚════════════════════════════════════════════════════════╝\n")
    
    print("📍 Common Indian Cities:")
    print("1. Delhi, India (28.6139°N, 77.2090°E)")
    print("2. Mumbai, India (19.0760°N, 72.8777°E)")
    print("3. Bangalore, India (12.9716°N, 77.5946°E)")
    print("4. Hyderabad, India (17.3850°N, 78.4867°E)")
    print("5. Chennai, India (13.0827°N, 80.2707°E)")
    print("6. Kolkata, India (22.5726°N, 88.3639°E)")
    print("7. Pune, India (18.5204°N, 73.8567°E)")
    print("8. Ahmedabad, India (23.0225°N, 72.5714°E)")
    print("9. Jaipur, India (26.9124°N, 75.7873°E)")
    print("10. Lucknow, India (26.8467°N, 80.9462°E)")
    print("11. Chandigarh, India (30.7333°N, 76.7794°E)")
    print("12. Amritsar, India (31.6340°N, 74.8723°E)")
    print("13. Custom location")
    
    choice = input("\n👉 Enter choice (1-13): ").strip()
    
    locations = {
        '1': ('Delhi', 'India', 28.6139, 77.2090),
        '2': ('Mumbai', 'India', 19.0760, 72.8777),
        '3': ('Bangalore', 'India', 12.9716, 77.5946),
        '4': ('Hyderabad', 'India', 17.3850, 78.4867),
        '5': ('Chennai', 'India', 13.0827, 80.2707),
        '6': ('Kolkata', 'India', 22.5726, 88.3639),
        '7': ('Pune', 'India', 18.5204, 73.8567),
        '8': ('Ahmedabad', 'India', 23.0225, 72.5714),
        '9': ('Jaipur', 'India', 26.9124, 75.7873),
        '10': ('Lucknow', 'India', 26.8467, 80.9462),
        '11': ('Chandigarh', 'India', 30.7333, 76.7794),
        '12': ('Amritsar', 'India', 31.6340, 74.8723),
    }
    
    if choice in locations:
        city, country, lat, lon = locations[choice]
    elif choice == '13':
        city = input("Enter city name: ").strip()
        country = input("Enter country name: ").strip()
        lat_input = input("Enter latitude (optional, press Enter to skip): ").strip()
        lon_input = input("Enter longitude (optional, press Enter to skip): ").strip()
        
        lat = float(lat_input) if lat_input else None
        lon = float(lon_input) if lon_input else None
    else:
        print("❌ Invalid choice")
        return
    
    print(f"\n📍 Setting location to: {city}, {country}")
    if lat and lon:
        print(f"   Coordinates: {lat}°, {lon}°")
    
    # Update local history
    if update_location_in_history(city, country, lat, lon):
        print("\n✅ Local data updated successfully!")
    
    # Update Google Sheets
    update_google_sheets_location(city, country)
    
    print("\n" + "="*60)
    print("✅ LOCATION UPDATED!")
    print("="*60)
    print(f"\n📍 New location: {city}, {country}")
    print("\n💡 Refresh your dashboard and Google Sheet to see changes:")
    print("   Dashboard: http://localhost:5001/dashboard.html")
    print("   Google Sheet: https://docs.google.com/spreadsheets/d/17FoN1d2P59MjaPIXD868wNYLq18HxBkq6DeQz46A-54")

if __name__ == '__main__':
    main()
