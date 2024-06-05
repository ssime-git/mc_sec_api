

example 1 : la clé d'encodage en clair (pas bonne pratique) = clé présente dans le scrpt
example 2 : 
1. même code mais avec une clée non présente en clair + avec un fichier d'en .env dans laquell eon va stoquer la variabel de chiffrement
2. utilisation de la fonction de chargement de env pour lire la clé
3. bien pour dev mais meilleur ave la clé stoqué ches un cloud provider (secret github)

Intro protocol OAuth
Meilleure dans un cadre pro. Ensemble de protocole (auth-code utilisé avec plusieurs app qui intéagisse en même temps). Un peu
Avec le script on va montrer l'auth password bearer.
Script example_oauth (password bearer)

Dans les slides on a le process d'auth avec plusieurs d'application