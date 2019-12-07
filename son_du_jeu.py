#!/usr/bin/env python3
# coding=UTF-8
#==============================================================================
# titre           :son_du_jeu.py
# description     :Ce script met en mémoire tous les sons du jeu
# auteur          :Olivier Meloche
# date            :20190413
# version         :4.0
# utilisation     :python main.py
# notes           :COURS 420-PRS-DM
# python_version  :3.7.1
#==============================================================================
from class_pygame import load_sound

# Met en mémoire tous les son du jeu
class Son():
    def __init__(self):
        self.error_snd = load_sound('sounds/error.wav')
        self.kick_snd = load_sound('sounds/kick.wav')
        self.corner_snd = load_sound('sounds/corner.wav')
        self.fall_snd = load_sound('sounds/fall.wav')
        self.long_fall_snd = load_sound('sounds/long_fall.wav')
        self.death_snd = load_sound('sounds/death.wav')
        self.win_snd = load_sound('sounds/win.wav')
        self.hit_snd = load_sound('sounds/hit.wav')
        self.move_snd = load_sound('sounds/move.wav')
        self.select_snd = load_sound('sounds/select.wav')
        self.select_game_snd = load_sound('sounds/select_game.wav')
