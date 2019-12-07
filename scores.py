#!/usr/bin/env python3
# coding=UTF-8
#==============================================================================
# titre           :scores.py
# description     :Ce script permet de charger et d'ajouter le score des joueurs
# auteur          :Olivier Meloche
# date            :20190425
# version         :4.0
# utilisation     :python main.py
# notes           :COURS 420-PRS-DM
# python_version  :3.7.1
#==============================================================================
from datetime import datetime
fichier_source = "scores.txt"

# Enregistre le score du joueur
def ajouter_score(temps, niveau, etage):
    with open(fichier_source, "a") as fichier:
        date = datetime.now()
        score = date.strftime("%x %X")+" TEMPS: "+str(temps)+"secs NIV: "+str(niveau)+" ETAGE: "+str(etage)
        fichier.write(score+"\n")
        print("[ENREGISTREMENT SCORE] '"+score+"'")

# Retourne tous les scores dans une liste
def charger_scores():
    liste = []
    with open(fichier_source, "r") as fichier:
        liste = fichier.read().split("\n")
    print("[LECTURE DES SCORES] '"+str(len(liste))+"'")
    return liste
