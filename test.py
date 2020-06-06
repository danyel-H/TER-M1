#!../bin/python3
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=43666)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    '''event = {
    'summary': 'Go RE2',
    'location': 'Salle de ma chambre',
    'start': {
        'dateTime': '2020-03-20T22:00:00+01:00',
        'timeZone': 'Europe/Paris',
    },
    'end': {
        'dateTime': '2020-03-21T01:00:00+01:00',
        'timeZone': 'Europe/Paris',
    }
    }'''

    #event = service.events().insert(calendarId='5186ihqdrrj2emdrgh2lp6eb08@group.calendar.google.com', body=event).execute()
    #print("Event created:" + (event.get('htmlLink')))

    page_token = None
    number = 1
    print("Let's see the calendars :") 
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for item in calendar_list['items']:
            print(item['summary'])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
        number+= 1 
    
    '''# Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='5186ihqdrrj2emdrgh2lp6eb08@group.calendar.google.com', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(event['summary'])'''

if __name__ == '__main__':
    main()