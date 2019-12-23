import gspread
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive",]

creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

def get_stats():
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("Stats").sheet1

    sheet_stats = sheet.get_all_records()
    
    stats = {}
    for sheet_stat in sheet_stats:
        if sheet_stat.get("stat_id"):
            key = sheet_stat.pop('stat_id')
            stats[key] = sheet_stat

    return stats
