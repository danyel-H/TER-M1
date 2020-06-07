from __future__ import print_function
import datetime
import logging
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class API:

    def __init__(self, creds):
        self.creds = creds
    
    #Utile pour l'authentification console
    def auth(self):
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                oui = flow.authorization_url()
                self.creds = flow.run_local_server(host="192.168.0.2.xip.io",port=43666, open_browser=False)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
            
            service = build('calendar', 'v3')


    def set_creds(self, creds):
        self.creds = creds
    
    def get_calendars(self, service):
        retour = [] 
        page_token = None
        number = 1
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for item in calendar_list['items']:
                retour.append(item)
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
            number+= 1 
        
        return retour

    #retourne le nom d'un calendrier à l'aide de l'id correspondant
    def get_summary(self, id, service):
        retour = None 
        page_token = None
        number = 1
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for item in calendar_list['items']:
                if(item["id"] == id):
                    retour = item["summary"]
            page_token = calendar_list.get('nextPageToken')
            if(not page_token):
                break
            number+= 1 
        
        return retour

    def del_calendar(self,cal,service):
        service.calendars().delete(calendarId=cal).execute()

    def add_calendar(self, json, service):
        created_calendar = service.calendars().insert(body=json).execute()

    def add_event(self, cal, json, service):
        event = service.events().insert(calendarId=cal, body=json).execute()

    def del_event(self,cal,id,service):
        service.events().delete(calendarId=cal, eventId=id).execute()

    #permet de récupérer un seul évènement en fonction de son id
    def get_event(self, cal, id, service):
        events = self.get_events(cal, service)
        retour = None
        for event in events:
            if(event['id'] == id):
                retour = event
        
        return retour

    def get_events(self, id, service):
        events = None
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        events_result = service.events().list(calendarId=id, timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        return events

    def get_creds(self):
        return self.creds