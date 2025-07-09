A CHANGER 
* HOST base de données sur app.py
* Requêtes SQL suivant les champs de la tables sur app.py

LANCER DOCKER:
* docker build -t pointage_image:latest .
* docker run -d -p port_host:port_container --name pointage pointage_image:latest
