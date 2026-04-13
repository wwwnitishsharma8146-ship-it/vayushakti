# 📊 Google Sheets Integration Setup Guide

## Complete Step-by-Step Instructions

---

## 🎯 What You'll Get

After setup, your sensor data will automatically be saved to Google Sheets:
- **Real-time data logging** - Every sensor reading saved automatically
- **Beautiful dashboard** - Charts and summaries
- **Historical data** - Access data from anywhere
- **Shareable** - Share with team members
- **Backup** - Cloud storage of all data

---

## 📋 Step 1: Install Required Libraries

Run this command:

```bash
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

---

## 🔑 Step 2: Create Google Cloud Project & Get Credentials

### A. Go to Google Cloud Console

1. Open: https://console.cloud.google.com/
2. Sign in with your Google account

### B. Create New Project

1. Click on project dropdown (top left)
2. Click "NEW PROJECT"
3. Name: `KrishiShakti`
4. Click "CREATE"
5. Wait for project to be created (30 seconds)

### C. Enable APIs

1. Go to: https://console.cloud.google.com/apis/library
2. Search for "Google Sheets API"
3. Click on it
4. Click "ENABLE"
5. Go back and search for "Google Drive API"
6. Click on it
7. Click "ENABLE"

### D. Create Service Account

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click "CREATE SERVICE ACCOUNT"
3. Service account name: `krishishakti-bot`
4. Service account ID: (auto-filled)
5. Click "CREATE AND CONTINUE"
6. Role: Select "Editor" (or "Owner")
7. Click "CONTINUE"
8. Click "DONE"

### E. Create & Download Key

1. Click on the service account you just created
2. Go to "KEYS" tab
3. Click "ADD KEY" → "Create new key"
4. Choose "JSON"
5. Click "CREATE"
6. A file will download (e.g., `krishishakti-xxxxx.json`)
7. **IMPORTANT:** Rename this file to `credentials.json`
8. Move it to your project folder (same folder as app.py)

---

## 📊 Step 3: Create Google Sheet

### Option A: Let the Script Create It (Recommended)

The script will automatically create a new Google Sheet for you.

### Option B: Create Manually

1. Go to: https://sheets.google.com/
2. Click "Blank" to create new sheet
3. Name it: `KrishiShakti Sensor Data`
4. **IMPORTANT:** Share the sheet with the service account email:
   - Open the `credentials.json` file
   - Find the `client_email` field (looks like: `krishishakti-bot@xxxxx.iam.gserviceaccount.com`)
   - Copy this email
   - In Google Sheets, click "Share" button
   - Paste the email
   - Give "Editor" access
   - Click "Send"

---

## 🚀 Step 4: Test the Connection

Run the test script:

```bash
python google_sheets_setup.py
```

**Expected Output:**

```
╔════════════════════════════════════════════════════════╗
║  KrishiShakti Google Sheets Integration Test         ║
╚════════════════════════════════════════════════════════╝

✓ Connected to existing spreadsheet: KrishiShakti Sensor Data
✓ Created 'Sensor Data' worksheet with headers

📝 Adding sample data...
✓ Added data to Google Sheets (Row 2)
✓ Sample data added successfully!

============================================================
✅ Setup Complete!
============================================================

📊 Open your spreadsheet: https://docs.google.com/spreadsheets/d/xxxxx
```

---

## 🔄 Step 5: Restart Flask Server

Stop the current Flask server (Ctrl+C) and restart:

```bash
python app.py
```

**You should see:**

```
✅ Google Sheets connected!
📊 Spreadsheet: https://docs.google.com/spreadsheets/d/xxxxx
 * Running on http://127.0.0.1:5001
```

---

## 📊 Step 6: View Your Data in Google Sheets

1. Open the spreadsheet URL shown in the terminal
2. You'll see two sheets:
   - **Sensor Data** - All raw sensor readings
   - **Dashboard** - Summary and latest values

### Sensor Data Sheet Columns:

| Column | Data |
|--------|------|
| A | Timestamp (full) |
| B | Date |
| C | Time |
| D | Air Quality (ppm) |
| E | Temperature (°C) |
| F | Humidity (%) |
| G | PM2.5 (µg/m³) |
| H | PM10 (µg/m³) |
| I | Soil Moisture (%) |
| J | Water Quality (ppm) |
| K | City |
| L | Country |
| M | Latitude |
| N | Longitude |
| O | Status (Good/Warning/Critical) |

---

## 🎨 Step 7: Create Charts (Optional)

### Temperature Chart:

1. Select columns B (Date) and E (Temperature)
2. Click "Insert" → "Chart"
3. Chart type: "Line chart"
4. Customize as needed

### Soil Moisture Chart:

1. Select columns B (Date) and I (Soil Moisture)
2. Click "Insert" → "Chart"
3. Chart type: "Line chart"
4. Add horizontal line at 30% (warning threshold)

### Multi-Sensor Dashboard:

1. Select columns B, E, F, I (Date, Temp, Humidity, Moisture)
2. Click "Insert" → "Chart"
3. Chart type: "Combo chart"
4. Customize colors and axes

---

## 🔍 Troubleshooting

### Error: "credentials.json not found"

**Solution:**
- Make sure you downloaded the JSON key file
- Rename it to exactly `credentials.json`
- Place it in the same folder as `app.py`

### Error: "Permission denied" or "Spreadsheet not found"

**Solution:**
- Open `credentials.json`
- Copy the `client_email` value
- Go to your Google Sheet
- Click "Share"
- Add the service account email with "Editor" access

### Error: "API not enabled"

**Solution:**
- Go to https://console.cloud.google.com/apis/library
- Enable both "Google Sheets API" and "Google Drive API"
- Wait 1-2 minutes for changes to propagate

### Error: "Module not found: gspread"

**Solution:**
```bash
pip install gspread google-auth
```

### Data not appearing in Google Sheets

**Solution:**
- Check Flask console for errors
- Make sure simulator is running: `python simulator.py`
- Check Google Sheets quota (free tier: 100 requests/100 seconds)
- Verify service account has Editor access to the sheet

---

## 📈 Data Flow with Google Sheets

```
┌─────────────────┐
│   Simulator     │
│  (Every 2 sec)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Flask Server   │
│    (app.py)     │
└────┬───────┬────┘
     │       │
     │       └──────────────┐
     ▼                      ▼
┌─────────────┐    ┌──────────────────┐
│   Local     │    │  Google Sheets   │
│ history.json│    │  (Cloud Storage) │
└─────────────┘    └──────────────────┘
     │                      │
     └──────────┬───────────┘
                ▼
         ┌─────────────┐
         │  Dashboard  │
         │  (Browser)  │
         └─────────────┘
```

---

## 🎯 Features

### Automatic Data Logging
- Every sensor reading is automatically saved
- No manual intervention needed
- Runs 24/7 in background

### Color-Coded Status
- 🟢 **Green (Good):** All parameters normal
- 🟡 **Yellow (Warning):** Some parameters need attention
- 🔴 **Red (Critical):** Immediate action required

### Real-Time Updates
- Data appears in Google Sheets within seconds
- Refresh the sheet to see latest data
- Use Google Sheets mobile app for monitoring on-the-go

### Historical Analysis
- All data preserved forever (unless you delete it)
- Create custom charts and graphs
- Export to Excel/CSV for further analysis
- Share with team members or advisors

---

## 💡 Pro Tips

1. **Create Multiple Sheets:**
   - One for raw data
   - One for daily summaries
   - One for alerts/warnings

2. **Set Up Alerts:**
   - Use Google Sheets conditional formatting
   - Highlight critical values in red
   - Get email notifications for critical readings

3. **Create Pivot Tables:**
   - Analyze data by date, location, or sensor
   - Find patterns and trends
   - Generate reports

4. **Use Google Data Studio:**
   - Connect your Google Sheet
   - Create professional dashboards
   - Share interactive reports

5. **Backup Your Data:**
   - Google Sheets auto-saves
   - Download as Excel periodically
   - Keep local copy in history.json

---

## 📊 Sample Google Sheet Structure

### Sheet 1: Sensor Data (Raw Data)

```
| Timestamp           | Date       | Time     | Air Quality | Temp | Humidity | ... | Status   |
|---------------------|------------|----------|-------------|------|----------|-----|----------|
| 2026-02-19T20:30:45 | 2026-02-19 | 20:30:45 | 125.43      | 27.8 | 65.2     | ... | Good     |
| 2026-02-19T20:30:47 | 2026-02-19 | 20:30:47 | 132.15      | 27.9 | 64.8     | ... | Good     |
| 2026-02-19T20:30:49 | 2026-02-19 | 20:30:49 | 128.67      | 27.7 | 65.5     | ... | Warning  |
```

### Sheet 2: Dashboard (Summary)

```
KrishiShakti Sensor Dashboard

Latest Readings:
┌─────────────────┬───────────────┬──────────┐
│ Metric          │ Current Value │ Status   │
├─────────────────┼───────────────┼──────────┤
│ Temperature     │ 27.8°C        │ Normal   │
│ Humidity        │ 65.2%         │ Normal   │
│ Soil Moisture   │ 25.3%         │ Low      │
│ Air Quality     │ 125 ppm       │ Good     │
│ Water Quality   │ 287 ppm       │ Good     │
└─────────────────┴───────────────┴──────────┘
```

---

## 🔐 Security Notes

1. **Keep credentials.json private:**
   - Don't commit to Git
   - Don't share publicly
   - Add to .gitignore

2. **Service Account Permissions:**
   - Only give access to specific sheets
   - Use "Editor" not "Owner" role
   - Revoke access if compromised

3. **API Quotas:**
   - Free tier: 100 requests per 100 seconds
   - Monitor usage in Google Cloud Console
   - Upgrade if needed for high-frequency logging

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all steps were completed
3. Check Flask console for error messages
4. Verify Google Cloud APIs are enabled
5. Ensure service account has sheet access

---

## ✅ Quick Checklist

- [ ] Installed gspread and google-auth libraries
- [ ] Created Google Cloud project
- [ ] Enabled Google Sheets API
- [ ] Enabled Google Drive API
- [ ] Created service account
- [ ] Downloaded credentials.json
- [ ] Placed credentials.json in project folder
- [ ] Ran test script successfully
- [ ] Restarted Flask server
- [ ] Verified data appears in Google Sheets
- [ ] Created charts (optional)

---

**Created:** February 19, 2026
**Project:** KrishiShakti (कृषि शक्ति)
**Version:** 1.0
