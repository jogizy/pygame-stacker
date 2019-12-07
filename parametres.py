#!/usr/bin/env python3
# coding=UTF-8
#==============================================================================
# titre           :parametres.py
# description     :Ce script permet de charger et d'enregistrer les paramètres
# auteur          :Olivier Meloche
# date            :20190425
# version         :4.0
# utilisation     :python main.py
# notes           :COURS 420-PRS-DM
# python_version  :3.7.1
#==============================================================================
fichier_source = "parametres.ini"
dict = { "COULEUR": 0, "VOLUME": 1, "ETAGE": 2, "NIVEAU": 3 }

# Retourne le type de paramètre appelé
def charger_parametres(ID):
    liste = []
    with open(fichier_source, "r") as fichier:
        liste = fichier.read().rstrip().split(":")
    print("[LECTURE PARAMÈRES] '"+str(ID)+"': "+liste[dict[ID]]+"'")
    return liste[dict[ID]]

# Enregistre le type de paramètre appelé
def modifier_parametres(ID, valeur):
    liste = []
    data = ""
    with open(fichier_source, "r") as fichier:
        # Sépare les paramètres actuel du fichier
        liste = fichier.read().rstrip().split(":")
    with open(fichier_source, "w") as fichier:
        liste[dict[ID]] = valeur
        print("[MODIFICATION PARAMÈTRES] '"+str(ID)+"': "+str(valeur)+"'")
        # Rajoute un ":" pour chaque paramètres, sauf le dernier
        for elem in liste[:-1]:
            data += str(elem) + ":"
        data += str(liste[-1])
        fichier.write(data)
