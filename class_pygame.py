#!/usr/bin/env python3
# coding=UTF-8
#==============================================================================
# titre           :class_pygame.py
# description     :Ce script retourne les sprites et le son
#                   *(vien de l'exemple "chimps" de pygame)
# auteur          :Olivier Meloche
# date            :20190413
# version         :4.0
# utilisation     :python main.py
# notes           :COURS 420-PRS-DM
# python_version  :3.7.1
#==============================================================================
import pygame
from pygame.locals import *
from pygame.compat import geterror

def load_image(name, colorkey=None):
    try:
        image = pygame.image.load(name)
    except pygame.error:
        print("Cannot load image:", name)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    try:
        sound = pygame.mixer.Sound(name)
    except pygame.error:
        print("Cannot load sound: %s" % name)
        raise SystemExit(str(geterror()))
    return sound
