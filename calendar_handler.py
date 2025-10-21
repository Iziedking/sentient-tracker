from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH')

def add_to_calendar(event, calendar_id):
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    
    start_time = datetime.datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
    end_time = start_time + datetime.timedelta(hours=1)
    
    g_event = {
        'summary': event['title'],
        'description': event.get('description', '') + f"\nLink: {event['link']}",
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
    }
    service.events().insert(calendarId=calendar_id, body=g_event).execute()