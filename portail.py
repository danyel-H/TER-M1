#!../bin/python3
from __future__ import print_function
from flask import Flask, request, render_template, redirect, url_for, session
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import google.oauth2.credentials
import json
from Google import API
from random import *
import os 
import pytz

#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

app = Flask(__name__)
app.secret_key = "Unsecrettressecret"

@app.route("/auth")
def auth():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    flow.redirect_uri = 'http://localhost:1606/retourgoogle'
    authorization_url, statut = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = statut 

    return redirect(authorization_url)

@app.route("/retourgoogle")
def establish_session():
    statut = session['state']
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, state=statut)
    flow.redirect_uri = "http://localhost:1606/retourgoogle"
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    service = build('calendar', 'v3', credentials=credentials)

    return redirect("/")

@app.route("/deconnect")
def deco():
    api = API(None)
    session.clear()

    return redirect("/")

@app.route("/event/<cal>/<id>/")
def event(cal=None, id=None):
    if 'credentials' in session:
        calendar = None
        summary = None
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)
        
        summary = api.get_summary(cal, service)
        event = api.get_event(cal, id, service)

    
        debut = getTimefromISO((event["start"]["dateTime"]))
        fin = getTimefromISO((event["end"]["dateTime"]))
        
        event["debut"] = debut
        event["fin"] = fin

        return render_template("event.html", conn=True, cal=summary, event=event)
    else:
        return redirect("/")

@app.route("/calendar/<cal>/del")
def supp_cal(cal=None):
    if 'credentials' in session:
        calendar = None
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)

        api.del_calendar(cal, service)

        return redirect("/")

@app.route("/event/<cal>/<id>/del")
def supp_event(cal=None, id=None):
    if 'credentials' in session:
        calendar = None
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)

        api.del_event(cal,id, service)

        return redirect("/calendar/"+cal)
    else:
        return redirect("/")

@app.route("/add",  methods=['GET', 'POST'])
def create_calendar():
    if 'credentials' in session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)
        if(request.method == 'POST'):
            if request.form.get("nom") and request.form.get("tz"):
                json_cal = {
                    "summary" : request.form["nom"],
                    "timeZone" : request.form["tz"]
                } 
                if request.form.get("desc"):
                    json_cal["description"] = request.form["desc"]

                api.add_calendar(json_cal, service)
            return redirect("/")
        else:
            tz = pytz.common_timezones

            return render_template("create_cal.html", conn=True, tz=tz)

    else:
        return redirect("/")

@app.route("/calendar/<id>/add",  methods=['GET', 'POST'])
def create_event(id=None):
    if 'credentials' in session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)

        if(request.method == 'POST'):
            if request.form.get("dateDebut") and request.form.get("dateFin") and request.form.get("heureDebut") and request.form.get("heureFin"):
                
                #permet de vérifier que les dates sont bonnes
                temp = request.form["dateDebut"].split("-")
                temp2 = request.form.get("heureDebut").split(":")
                dateDebut = datetime.datetime(year=int(temp[0]), month=int(temp[1]), day=int(temp[2]), hour=int(temp2[0]), minute=int(temp2[1]), second=int(temp2[2]))

                temp = request.form["dateFin"].split("-")
                temp2 = request.form.get("heureFin").split(":")
                dateFin = datetime.datetime(year=int(temp[0]), month=int(temp[1]), day=int(temp[2]), hour=int(temp2[0]), minute=int(temp2[1]), second=int(temp2[2]))

                if(dateDebut < dateFin):
                    dateDebut = dateDebut.strftime('%Y-%m-%dT%H:%M:%S+02:00')
                    dateFin = dateFin.strftime('%Y-%m-%dT%H:%M:%S+02:00')

                    json_event = {
                        'summary' : "Un évènement test",
                        'start': {
                            'dateTime': dateDebut,
                            'timeZone': 'Europe/Paris'
                        },
                        'end': {
                            'dateTime': dateFin,
                            'timeZone': 'Europe/Paris'
                        }
                    }

                    api.add_event(id, json_event, service)

            return redirect("/calendar/"+id)
        else:
            tz = pytz.common_timezones

            return render_template("create_event.html", conn=True, tz=tz)

    else:
        return redirect("/")


@app.route("/calendar/<id>/")
def calendar(id=None):
    if 'credentials' in session:
        calendar = None
        summary = None
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)
        calendar = api.get_events(id, service)
        summary = api.get_summary(id, service)

        return render_template("calendar.html", cal=calendar, conn=True, nom=summary)
    else:
        return redirect("/")


@app.route("/")
def main():
    connect = False
    calendars = None
    if 'credentials' in session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        api.set_creds(credentials)
        connect = True
        service = build('calendar', 'v3', credentials=credentials)
        calendars = api.get_calendars(service)
        print(calendars)
    
    return render_template("index.html", conn=connect, cal=calendars)
    

def getTimefromISO(time):
        heure = time[12:19]
        date = time[:10]
        temp = date.split("-")        
        json = {
            "annee" : temp[0],
            "mois" : temp[1],
            "jour" : temp[2],
            "heure" : heure
        }

        return json


if __name__ == "__main__":
    api = API(None)
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(host='0.0.0.0', port=8080,debug=True)