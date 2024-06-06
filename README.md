# Securing API

## Securing attempt 1
example 1 : la clé d'encodage en clair --> mauvaise pratique

## Securing attempt 2
 
Même code mais avec une clé non présente en clair  et utilisation d'un fichier `.env` dans laquel on va stoquer la clée de chiffrement.

Bien pour lors de la phase de prototypage mais meilleur avec la clé enregistrée dans les secret github par exemple.

## OAuth simple : Avec password bearer (script `example_oauth.py`)

OAuth = Ensemble de protocole (auth-code utilisé avec plusieurs app qui intéagisse en même temps).

## OAuth entre plusieurs applications

Voir [slides](https://docs.google.com/presentation/d/1LmQAB2wKJdoj7cNDC6G40Jfd6m3r5xt_/edit#slide=id.g2c6c8d033b1_0_64)