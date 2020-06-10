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

'''
Classe permettant d'intéragir avec l'API de Google.
'''
class API:

    def __init__(self, creds):
        self.creds = creds

    #permet de définir les crédentiels pour la session.
    #@param creds les crédentiels
    def set_creds(self, creds):
        self.creds = creds
    
    #Permet de retourner la liste de tous les calendriers de l'utilisateur
    #@param service le service, à construire à partir des crédentiels
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
    #@param id l'id du calendrier
    #@param service le service, à construire à partir des crédentiels
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

    #Permet de savoir si un agenda est l'agenda principal de l'utilisateur
    #@param id l'id du calendrier
    #@param service le service, à construire à partir des crédentiels
    def is_primary(self,id,service):
        retour = False
        cals = self.get_calendars(service)
        for cal in cals:
            if(cal['id'] == id):
                if("primary" in cal):
                    retour = True
        
        return retour

    #Permet de récupérer un calendrier et ses infos selon son ID
    #@param cal l'id du calendrier
    #@param service le service, à construire à partir des crédentiels
    def get_one_calendar(self, cal, service):
        retour = service.calendars().get(calendarId=cal).execute()
        return retour

    #Permet de supprimer un calendrier selon son ID
    #@param cal l'id du calendrier
    #@param service le service, à construire à partir des crédentiels
    def del_calendar(self,cal,service):
        service.calendars().delete(calendarId=cal).execute()

    #Permet d'ajouter un agenda à la liste des agendas de l'utilisateur
    #@param json le JSON à envoyer à l'API REST
    #@param service le service, à construire à partir des crédentiels
    def add_calendar(self, json, service):
        created_calendar = service.calendars().insert(body=json).execute()

    #Permet d'ajouter un évènement à un calendrier
    #@param cal l'id du calendrier
    #@param json le JSON à envoyer à l'API REST
    #@param service le service, à construire à partir des crédentiels
    def add_event(self, cal, json, service):
        event = service.events().insert(calendarId=cal, body=json).execute()


    #Permet de supprimer un évènement d'un calendrier
    #@param cal l'id du calendrier
    #@param id l'id de l'évènement
    #@param service le service, à construire à partir des crédentiels
    def del_event(self,cal,id,service):
        service.events().delete(calendarId=cal, eventId=id).execute()

    #permet de récupérer un seul évènement en fonction de son id
    #@param cal l'id du calendrier
    #@param id l'id de l'évènement
    #@param service le service, à construire à partir des crédentiels
    def get_event(self, cal, id, service):
        event = service.events().get(calendarId=cal, eventId=id).execute()
        return event


    #Permet de récupérer une liste d'évènements selon des paramètres rentrés
    #@param id l'id de l'évènement
    #@param service le service, à construire à partir des crédentiels
    #Si single est renseigné à False, il ne renvoie pas les évènements récurrents
    #Le filtre est un regex ne renvoyant que les évènements contenant le mot contenu dans le filtre
    #tempsMax est le temps en ISO-8601 jusqu'auquel il faut lister les évènements
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
    #@param cal l'id du calendrier
    #@param id l'id de l'évènement
    #@param service le service, à construire à partir des crédentiels
    #@param kwargs les champs à mettre à jour
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

    #permet de récupérer les crédentiels
    def get_creds(self):
        return self.creds