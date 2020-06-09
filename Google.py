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
            calendar_list = service.calendarList().list(pageToken=page_token, minAccessRole="owner").execute()
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

    #Permet de savoir si un agenda est l'agenda principal de l'utilisatuer
    def is_primary(self,id,service):
        retour = False
        cals = self.get_calendars(service)
        for cal in cals:
            if(cal['id'] == id):
                if("primary" in cal):
                    retour = True
        
        return retour

    def get_one_calendar(self, cal, service):
        retour = service.calendars().get(calendarId=cal).execute()
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
        event = service.events().get(calendarId=cal, eventId=id).execute()
        return event

    def get_events(self, id, service, single=True, filtre=None, tempsMax=None):
        events = None
        now = datetime.datetime.utcnow()
        if(tempsMax):
            if(tempsMax < now):
                tempsMax = None
            else:
                tempsMax = tempsMax.isoformat() + 'Z'

        now = datetime.datetime.utcnow().isoformat() + 'Z'

        events_result = service.events().list(calendarId=id, timeMin=now,
                                            singleEvents=single,
                                            orderBy='startTime', q=filtre, timeMax=tempsMax).execute()
        events = events_result.get('items', [])

        return events

    #permet de mettre à jour un évènement
    def update_event(self, cal,id,service, **kwargs):
        event = self.get_event(cal, id, service)

        if "nom" in kwargs and kwargs["nom"]:
            event["summary"] = kwargs["nom"]
        
        if "desc" in kwargs and kwargs["desc"]:
            event["description"] = kwargs["desc"]
        
        if "lieu" in kwargs and kwargs["lieu"]:
            event["location"] = kwargs["lieu"]

        if "dateDebut" in kwargs and kwargs["dateDebut"]:
            event["start"]["dateTime"] = kwargs["dateDebut"]

        if "dateFin" in kwargs and kwargs["dateFin"]:
            event["end"]["dateTime"] = kwargs["dateFin"]


        service.events().update(calendarId=cal, eventId=event['id'], body=event).execute()


    def get_creds(self):
        return self.creds