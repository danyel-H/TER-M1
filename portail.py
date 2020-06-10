#!../bin/python3
from __future__ import print_function
from flask import Flask, request, render_template, redirect, url_for, session, make_response
import csv
import io
import datetime
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

#Le scope dans lequel l'api va intéragir
SCOPES = ['https://www.googleapis.com/auth/calendar']

#Le port sur lequel va être redirigé l'utilisateur après l'authentification
PORT_REDIRECT = "1606"

app = Flask(__name__)
app.secret_key = "Unsecrettressecret"


##################### URL DE SESSION #########################################

#La page consacrée à la connexion de l'utilisateur, il est redirigé vers le site de Google
@app.route("/auth")
def auth():
    #On charge les paramètres depuis le fichier des identifiants
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    flow.redirect_uri = 'http://localhost:'+PORT_REDIRECT+'/retourgoogle'
    authorization_url, statut = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = statut 

    return redirect(authorization_url)

#Après la redirection, l'utilisateur procède à un échange de Tokens
@app.route("/retourgoogle")
def establish_session():
    statut = session['state']
    #à l'aide des paramètres dans credentials.json, le site échange la session contre un jeton
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES, state=statut)
    flow.redirect_uri = "http://localhost:"+PORT_REDIRECT+"/retourgoogle"
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    #On déclare une session
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    #On construit le service qui servira à intéragir avec l'API
    service = build('calendar', 'v3', credentials=credentials)

    return redirect("/")

#Page de déconnexion
@app.route("/deconnect")
def deco():
    api = API(None)
    session.clear()

    return redirect("/")

##################### URL CONSACREES AUX AGENDAS #########################################

#Page utilisée pour sortir un CSV contenant tous les évènements
@app.route('/calendar/<id>/csv')
def dl_csv(id=None):
    if 'credentials' in session:
        #On construit le service
        calendar = None
        summary = None
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)
        
        calendar = api.get_events(id, service)
        summary = api.get_one_calendar(id, service)

        lignes = []
        lignes.append(["Titre", "Description", "Lieu", "Créateur" ,"Date de début" ,"Heure de début", "Date de fin","Heure de fin"])

        for ev in calendar:
            temp = []
            if "summary" in ev:
                temp.append(ev["summary"])
            else:
                temp.append("")

            if "description" in ev:
                temp.append(ev["description"])
            else:
                temp.append("")

            if "location" in ev:
                temp.append(ev["location"])
            else:
                temp.append("")

            temp.append(ev["creator"]["email"])
            dateDebut = getTimefromISO((ev["start"]["dateTime"]))
            dateFin = getTimefromISO((ev["end"]["dateTime"]))
            temp.append(dateDebut["jour"] +"/"+dateDebut["mois"] +"/"+ dateDebut["annee"])
            temp.append(dateDebut["heure"])
            temp.append(dateFin["jour"] +"/"+ dateFin["mois"] +"/"+ dateFin["annee"])
            temp.append(dateFin["heure"])

            lignes.append(temp)

        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerows(lignes)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename="+summary["summary"]+".csv"
        output.headers["charset"] = "utf-8"
        output.headers["Content-type"] = "text/csv"
        
        return output
    else:
        return redirect("/")
    


#Page d'upload d'un JSON sur le site
@app.route("/calendar/<cal>/upload", methods=["GET", "POST"])
def upload_json(cal=None):
    if 'credentials' in session:
        calendar = None
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)

        if(request.method == 'POST'):
            file = request.files['file']        
            myfile = file.read().decode()
            event = json.loads(myfile)

            api.add_event(cal, event, service)
        else:
            return render_template("upload_json.html", conn=True)
        
    return redirect("/calendar/"+cal)
   

#Page de suppression d'un agenda
@app.route("/calendar/<cal>/del")
def supp_cal(cal=None):
    if 'credentials' in session:
        calendar = None
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)

        api.del_calendar(cal, service)

    
    return redirect("/")


#Page d'ajout d'un calendrier
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


#Page d'ajout d'un évènement
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

                    cal = api.get_one_calendar(id, service)

                    json_event = {
                        'start': {
                            'dateTime': dateDebut,
                            'timeZone': cal["timeZone"]
                        },
                        'end': {
                            'dateTime': dateFin,
                            'timeZone': cal["timeZone"]
                        }
                    }

                    if request.form.get("nom"):
                        json_event["summary"] = request.form["nom"]
                    
                    if request.form.get("desc"):
                        json_event["description"] = request.form["desc"]

                    if request.form.get("lieu"):
                        json_event["location"] = request.form["lieu"]

                    api.add_event(id, json_event, service)

            return redirect("/calendar/"+id)
        else:
            tz = pytz.common_timezones

            return render_template("create_event.html", conn=True, tz=tz)

    else:
        return redirect("/")

#Page de détail d'un agenda, on affiche les évènements
@app.route("/calendar/<id>/")
def calendar(id=None):
    if 'credentials' in session:
        calendar = None
        summary = None
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)

        single = True
        tempsMax=None
        titre=""
        if(request.args.get("dateFin")):
            temp= request.args.get("dateFin").split("-")
            tempsMax = datetime.datetime(year=int(temp[0]), month=int(temp[1]), day=int(temp[2]))

        if(request.args.get("check")):
            single = False

        if(request.args.get("titre")):
            titre = request.args.get("titre")

        calendar = api.get_events(id, service, single, titre, tempsMax)
        summary = api.get_one_calendar(id, service)

        temp = api.is_primary(id, service)
        summary["primary"] = temp

        return render_template("calendar.html", cal=calendar, conn=True, nom=summary)
    else:
        return redirect("/")

##################### URL CONSACREES AUX EVENEMENTS #########################################


#Page de détail d'un évènement
@app.route("/event/<cal>/<id>/")
def event(cal=None, id=None):
    if 'credentials' in session:
        calendar = None
        summary = None
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)
        
        summary = api.get_summary(cal, service)
        event = api.get_event(cal, id, service)
    
        #On ajoute deux champs au JSON de l'évènement pour avoir un évènement lisible une fois sur la page
        debut = getTimefromISO((event["start"]["dateTime"]))
        fin = getTimefromISO((event["end"]["dateTime"]))
        
        event["debut"] = debut
        event["fin"] = fin

        return render_template("event.html", conn=True, cal=summary, event=event)
    else:
        return redirect("/")


#Page de mise à jour d'un évènement
@app.route("/event/<cal>/<id>/update", methods=["POST"])
def update_event(cal=None, id=None):
    if 'credentials' in session:
        calendar = None
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)
        
        nom = None
        desc = None
        lieu = None
        dateDebut = None
        dateFin = None

        if(request.form.get("nom")):
            nom = request.form["nom"]
        
        if(request.form.get("desc")):
            desc = request.form["desc"]
        
        if(request.form.get("lieu")):
            lieu = request.form["lieu"]

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

        api.update_event(cal, id,service, nom=nom, desc=desc, lieu=lieu, dateDebut=dateDebut, dateFin=dateFin)

        return redirect("/calendar/"+cal)
    else:
        return redirect("/")

#Page de suppression des évènements
@app.route("/event/<cal>/<id>/del")
def supp_event(cal=None, id=None):
    if 'credentials' in session:
        calendar = None
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
        service = build('calendar', 'v3', credentials=credentials)

        if(request.args.get("purpose")):
            purpose = request.args.get("purpose")
            if(purpose == "all"):
                event = api.get_event(cal, id, service)
                api.supp_recurrences(cal, event["recurringEventId"],service)
            elif(purpose == "simple"):
                api.del_event(cal,id, service)

        return redirect("/calendar/"+cal)
    else:
        return redirect("/")


#Page d'accueil
@app.route("/")
def main():
    connect = False
    calendars = []
    if 'credentials' in session:
        try:
            credentials = google.oauth2.credentials.Credentials(**session['credentials'])
            api.set_creds(credentials)
            connect = True
            service = build('calendar', 'v3', credentials=credentials)
            calendars = api.get_calendars(service)
        except(google.auth.exceptions.RefreshError):
            return redirect("/deconnect")
    
    return render_template("index.html", conn=connect, cal=calendars)
    
#permet de convertir une date ISO-8601 en JSON lisible
def getTimefromISO(time):
        heure = time[11:19]
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
    app.run(host='0.0.0.0', port=8080,debug=False)