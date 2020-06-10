# Mode d'emploi du projet

Bonjour, voici le mode d'emploi du module de Travaux d'Études et de Recherches sur le sujet suivant :
**Etude de l'exploitation de l'API REST google Calendar**

Ce mode d'emploi couvrira tout ce qu'il faut savoir pour lancer correctement le projet, bonne lecture.

## Auteur

Hocquigny Danyel, M1 RT DAS

## Contenu du projet

Le projet contient multiples fichiers et dossiers :

- credentials.json
Ceux-ci sont les identifiants du compte Google que j'ai créé spécialement pour le TER, il est vierge et ne contient rien d'important excepté quelques informations personnelles.

- Google.py
Ce fichier est la classe permettant d'intéragir avec l'API Google Calendar, il est le fichier contenant l'ensemble des fonctionnalités nécessaires

- Le site Web
    - static
    Ce sont les fichiers css et JS nécessaires au site web
    - templates 
    Ce sont les pages HTML du site Web
    - portail.py
    C'est la solution de requêtage que j'ai conçue, c'est un serveur Flask.

## Comment le tester

### Prérequis

Afin de lancer correctement le projet, il vous faudra :
- Python3
- Un compte Google 
- Le gestionnaire de paquets pip

Une fois pip installé, installez ces paquets :
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib
- Flask

Il vous faudra bien sûr aussi une connexion Internet.
Une dernière chose très importante est requise et change selon les conditions d'execution :
- Si vous exécutez ce projet sur une VM, faites une redirection de port du port 1606 (Côté hôte) vers le port 8080 (Côté VM), si le port 1606 est indisponible chez vous, vous pouvez utilisez le port 10000, mais veuillez à modifier la variable "PORT_REDIRECT" en haut de portail.py si tel est le cas
- Si vous exécutez ce projet à même votre ordinateur, il faut descendre tout en bas de "portail.py" et modifier le port sur lequel Flask tourne avec le port 1606. Encore une fois il vous est possible d'utiliser le port 10000 si jamais en effectuant les manipulations décrites au dessus

Si ces deux ports sont si importants, c'est parce que Google doit connaitre chaque port sur lequel est redirigé l'utilisateur après son authentification, et j'ai renseigné ces deux là

### Execution

Une fois tout-ceci préparé, vous pouvez lancer le serveur Flask avec la commande
> python3 portail.py

Il vous suffira alors de vous rendre sur localhost:1606 (ou localhost:10000 si indisponible) afin de tester la solution.

Notez que le SSL n'est pas disponible sur le serveur, attention au compte Google que vous allez utiliser pour tester l'API.

## Si je veux l'utiliser plus tard ?

Peu après les résultats du semestre, je supprimerai le compte Google qui agit en tant qu'entreprise reçevant les requêtes, il vous faudra alors activer vous même l'API sur un compte Google de votre choix. J'ai réservé une section à cet effet dans le rapport joint.