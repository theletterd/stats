import gspread
from oauth2client.service_account import ServiceAccountCredentials
from secret import GSHEET_JSON_KEYFILE

from models import Stat

# use creds to create a client to interact with the Google Drive API
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive",]

creds = ServiceAccountCredentials.from_json_keyfile_dict(GSHEET_JSON_KEYFILE, scope)
client = gspread.authorize(creds)

def get_stats():
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    client.login()
    sheet = client.open("Stats").sheet1

    sheet_stats = sheet.get_all_records()
    
    stats = []
    for stat in sheet_stats:
        if stat.get("stat_id"):
            stats.append(
                Stat(
                    stat_id=stat['stat_id'],
                    description=stat['description'],
                    value=stat['value'],
                    notes=stat['notes']
            ))
    return stats
