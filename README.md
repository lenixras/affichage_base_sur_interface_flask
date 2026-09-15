# Interface Flask avec Base de Données

Application Flask permettant d'afficher des données issues d'une base de données SQL.

## Configuration

Avant de lancer l'application, assurez-vous de configurer les éléments suivants dans `app.py` :

*   **Connexion à la base de données :** Modifiez les paramètres de connexion (host, port, user, password, db) pour pointer vers votre base de données.
*   **Requêtes SQL :** Mettez à jour les requêtes SQL dans les routes Flask pour correspondre à la structure de vos tables.

## Lancement avec Docker

Pour construire et exécuter l'application dans un conteneur :

1.  Construire l'image :
    ```bash
    docker build -t pointage_image:latest .
    ```

2.  Exécuter le conteneur :
    ```bash
    docker run -d -p 5000:5000 --name pointage pointage_image:latest
    ```

*Note : Remplacez `5000:5000` par les ports de votre choix si nécessaire.*
