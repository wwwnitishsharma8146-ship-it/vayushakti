import gspread
from google.oauth2.service_account import Credentials

# Google API scope
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from credentials.json
creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

# Authorize the client
client = gspread.authorize(creds)

# 🔥 IMPORTANT:
# Replace "KrishiShaktiData" with your exact Google Sheet name
sheet = client.open("KrishiShaktiData").sheet1


def add_farmer_query(name, phone, query):
    """
    Adds a new farmer query row to Google Sheet
    """
    sheet.append_row([name, phone, query])