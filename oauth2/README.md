# Projet OAuth2 avec API Python

Ce projet est une implémentation simplifiée d'un flux OAuth2 en Python, comprenant un serveur d'autorisation, un serveur de ressources, un client, et une API RESTful. Il est conçu à des fins éducatives pour illustrer les concepts de base du protocole OAuth2.

## Objectifs du projet

1. Démontrer le flux OAuth2 de base
2. Illustrer la séparation des responsabilités entre les différents composants d'un système OAuth2
3. Fournir un exemple pratique d'une API RESTful utilisant Flask

## Structure du projet

- `auth_server.py` : Implémentation du serveur d'autorisation
- `resource_server.py` : Implémentation du serveur de ressources
- `client.py` : Client OAuth2 pour tester le flux
- `api.py` : API Flask exposant les endpoints OAuth2
- `main.py` : Script principal pour exécuter l'application
- `requirements.txt` : Liste des dépendances du projet

## Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

## Installation

1. Clonez ce dépôt ou téléchargez les fichiers dans un nouveau dossier.

2. (Optionnel mais recommandé) Créez un environnement virtuel :
   ```sh
   python -m venv venv
   source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
   ```

3. Installez les dépendances :
   ```sh
   pip install -r requirements.txt
   ```

## Exécution du projet

1. Assurez-vous d'être dans le dossier du projet et que votre environnement virtuel est activé (si vous en utilisez un).

2. Exécutez le script principal :
   ```sh
   python main.py
   ```

3. Le script va :
   - Démarrer le serveur Flask en arrière-plan
   - Utiliser le client pour simuler un flux OAuth2 complet

4. Vous devriez voir une sortie similaire à celle-ci :
   ```js
   Code d'autorisation obtenu : XXXXXXXX
   Jeton d'accès obtenu : XXXXXXXXXXXXXXXX
   Données de l'utilisateur : Données confidentielles d'Alice
   ```

## Comprendre le flux OAuth2

1. Le client demande un code d'autorisation au serveur d'autorisation.
2. Le serveur d'autorisation génère et renvoie un code d'autorisation.
3. Le client échange ce code contre un jeton d'accès.
4. Le client utilise ce jeton pour accéder aux ressources protégées via l'API.

```mermaid
sequenceDiagram
    participant C as Client
    participant API as API (Flask)
    participant AS as Authorization Server
    participant RS as Resource Server

    C->>API: POST /auth (client_id, username)
    API->>AS: generate_auth_code(client_id, username)
    AS-->>API: auth_code
    API-->>C: auth_code

    C->>API: POST /token (client_id, client_secret, auth_code)
    API->>AS: exchange_auth_code_for_token(auth_code, client_id, client_secret)
    AS-->>API: access_token
    API-->>C: access_token

    C->>API: GET /data (Bearer access_token)
    API->>AS: validate_token(access_token)
    AS-->>API: username (if valid)
    API->>RS: get_user_data(username)
    RS-->>API: user_data
    API-->>C: user_data

    Note over C,RS: Flux OAuth2 complet

    rect rgb(200, 220, 250)
        Note over AS: Authorization Server
        AS->>AS: generate_auth_code()
        AS->>AS: exchange_auth_code_for_token()
        AS->>AS: validate_token()
    end

    rect rgb(220, 250, 200)
        Note over RS: Resource Server
        RS->>RS: get_user_data()
    end

    rect rgb(250, 220, 200)
        Note over API: API (Flask)
        API->>API: /auth endpoint
        API->>API: /token endpoint
        API->>API: /data endpoint
    end
````

## Avertissement

Cette implémentation est simplifiée et ne comprend pas toutes les vérifications de sécurité qu'un vrai système OAuth2 devrait avoir. Elle sert principalement à illustrer les concepts de base du flux OAuth2 et ne doit pas être utilisée en production.

## Contribution

Les contributions à ce projet sont les bienvenues. N'hésitez pas à ouvrir une issue ou à soumettre une pull request si vous avez des suggestions d'amélioration.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.