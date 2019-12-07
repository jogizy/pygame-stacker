#!/usr/bin/env python3
# coding=UTF-8
#==============================================================================
# titre           :main.py
# description     :Jeu de vitesse qui permet de placer des cubes
# auteur          :Olivier Meloche
# date            :20190425
# version         :4.0
# utilisation     :python main.py
# notes           :COURS 420-PRS-DM
# python_version  :3.7.1
#==============================================================================
import pygame
from random import randint, choice
from pygame.locals import *
from pygame.compat import geterror
from class_pygame import load_image
from parametres import charger_parametres, modifier_parametres
from son_du_jeu import Son
from scores import ajouter_score, charger_scores
from sys import exit
from os import listdir

# Construit les labels du main()
class Label_Stats():
    def __init__(self, x, y, separ):
        self.font = pygame.font.Font("sprites/font.ttf", 8)
        self.rouge = (255, 0, 0)
        self.x = x
        self.y = y
        self.separ = separ
        self.etage = class_etage.etage
        self.niveau = class_niveau.niveau

    # Actualise tous les labels du main()
    def actualiser(self, text):
        y = self.y
        label = []
        for i in range(len(text)):
            label.append(self.font.render(str(text[i]), 1, self.rouge))
            screen.blit(label[i], (self.x, y))
            pygame.draw.line(screen, self.rouge, (self.x, y+15), (self.x+110, y+15), 1)
            y += self.separ

# Permet d'actualiser l'étage, la vitesse, le temps de jeu et la colonne de base
class Parametres_Cube():
    def __init__(self):
        self.colonne = -1
        self.etage = 0
        self.vitesse = 1000
        self.dict_vitesse = { "FACILE":50, "MOYEN":75, "DIFFI.":100 }
        self.temps_de_jeu = ""

    # Affecte la vitesse et l'étage du prochain cube
    def increment(self):
        self.etage += 1
        self.vitesse += self.dict_vitesse[class_niveau.niveau]

    # Met en mémoire la colonne du premier cube seulement
    def colonne_base(self, valeur):
        if self.colonne < 0:
            self.colonne = valeur

    # Appel la fonction d'initialisation de la classe
    def reinitialiser(self):
        self.__init__()

# Construit et affecte le moteur du jeu
class Cube(pygame.sprite.Sprite):
    def __init__(self, x, y, vitesse):
        pygame.sprite.Sprite.__init__(self)
        self.couleur = class_couleur_cube.dict_inverse[class_couleur_cube.couleur_ID].lower()
        self.image, self.rect = load_image("sprites/cube_"+self.couleur+".png", -1)
        self.rect.topleft = x, y
        self.move = 16
        self.colonne = round(x/16)
        self.quantite_cube = len(sprites_cube.sprites())
        # Valide de quel coté commencer
        if self.colonne == 0:
            self.direction = -1
            self.move *= -1
        else:
            self.direction = 1
        self.nextFrame = 0
        dict_vitesse = { "FACILE":50, "MOYEN":75, "DIFFI.":100 }
        accelerateur = dict_vitesse[class_niveau.niveau]
        self.vitesse = 1000 + ((self.quantite_cube)*accelerateur)
        self.base = class_etage.etage*16
        self.hauteur_bloc = self.base-(16*(self.quantite_cube+2))
        self.verouiller = False
        self.mort = False
        self.timer = 0
        self.etat = "DEPLACER"
        self.gagne = False

    # Actualise le cube en cours selon son état (DEPLACER, VEROUILLER, TOMBE)
    def update(self):
        if self.etat == "DEPLACER":
            self.nextFrame += self.vitesse
            if self.nextFrame >= 6000:
                # Inverse la direction du bloc s'il touche aux extrémités
                if self.colonne == 6 or self.colonne == 0:
                    self.direction *= -1
                    self.move *= -1
                    class_son.corner_snd.play()
                # Valide si le bloc est près des extrémités
                if self.colonne == 2 or self.colonne == 4:
                    class_son.kick_snd.play()
                # Déplace le bloc de 16px selon sa direction en cours
                self.rect.move_ip(self.move, 0)
                self.colonne += self.direction
                self.nextFrame = 0

        # Empêche le cube en cours de se déplacer, puis l'affecte
        elif self.etat == "VEROUILLER":
            self.timer += 1
            if self.timer == 30: #(500ms)
                if self.gagne:
                    self.gagnant()
                    parametres_cube.increment()
                elif not self.mort:
                    self.spawn_cube()
                    parametres_cube.increment()
                else:
                    self.tombe()

        # Fait tomber le cube en cours jusqu'à ce qu'il touche le sol
        elif self.etat == "TOMBE":
            self.nextFrame += 1
            if self.nextFrame >= 3: #(50ms)
                if self.rect.y < self.base:
                    self.rect.move_ip(0, 16)
                    self.nextFrame = 0

    # Vérifie si le cube en cours est à la bonne position et retourne le
    # résultat. La fonction vérifie également si le joueur est au dernier étage
    def verifier(self):
        if self.colonne == parametres_cube.colonne:
            class_son.hit_snd.play()
            if self.quantite_cube+1 == class_etage.etage:
                self.gagne = True
            return False
        else:
            class_son.death_snd.play()
            return True

    # Empêche le cube de se déplacer jusqu'à vérification
    def stop(self):
        parametres_cube.colonne_base(self.colonne)
        self.etat = "VEROUILLER"
        self.mort = self.verifier()

    # Permet de créer le prochain cube et réactive le contrôle
    def spawn_cube(self):
        pygame.event.set_allowed(KEYDOWN)
        cube.append(Cube(randint(0,6)*16, self.hauteur_bloc, self.vitesse))
        sprites_cube.add(cube)

    # Actualise le cube en mode "TOMBE" et débute le délai qui fera sortir
    # le main de sa boucle.
    def tombe(self):
        self.nextFrame = 0
        self.etat = "TOMBE"
        delai(2500)
        # Joue un différent son si le cube était au dernier étage
        if self.rect.y > 0:
            class_son.fall_snd.play()
        else:
            class_son.long_fall_snd.play()

    # Joue le son final, débute le délai qui fera sortir le main de sa boucle
    # et inscrit le score du joueur dans le fichier "scores.txt"
    def gagnant(self):
        class_son.win_snd.play()
        delai(2500)
        ajouter_score(parametres_cube.temps_de_jeu, class_niveau.niveau, class_etage.etage)

# Construit un curseur personnalisé selon le type de menu à afficher
class Curseur(pygame.sprite.Sprite):
    def __init__(self, y, elem):
        pygame.sprite.Sprite.__init__(self)
        self.curseur_sprites = []
        self.curseur_sprites.append(pygame.image.load('sprites/cursor1.png'))
        self.curseur_sprites.append(pygame.image.load('sprites/cursor2.png'))
        self.rect = pygame.Rect(25, y, 32, 16)
        self.image = self.curseur_sprites[0]
        self.ID = 0
        self.nextFrame = 0
        self.index = 0
        self.element = elem-1

    # Actualise le curseur et clignote au 500ms
    def update(self):
        self.nextFrame += 1
        if self.nextFrame == 30:
            if self.index == 0:
                self.index = 1
            else:
                self.index = 0
            self.image = self.curseur_sprites[self.index]
            self.nextFrame = 0

    # Empêche le curseur de sortir des extrémités
    def deplacer(self, ID, y):
        if (self.ID != self.element and ID > 0) or (self.ID > 0 and ID < 0):
            class_son.move_snd.play()
            self.ID += ID
            self.rect.move_ip(0, y)
        else:
            class_son.error_snd.play()
        print("[SELECT] "+str(self.ID)+":"+str(self.element))

    # Modifie les parametres selon le type de fenêtre à l'écran
    def changer_config(self, valeur, fenetre=""): #[K_LEFT, K_RIGHT]
        if fenetre == "audio":
            if self.ID == 0: #AUDIO
                class_volume.changer_volume(round(valeur/10, 1))
            elif self.ID == 1: #MUSIQUE (CHOIX)
                class_musique.changer_musique(valeur)
            else:
                class_son.error_snd.play()

        elif fenetre == "parametres":
            if self.ID == 0: #NIVEAU
                class_niveau.changer_niveau(valeur)
            elif self.ID == 1: #ETAGE
                class_etage.changer_etage(valeur)
            elif self.ID == 4: #COULEUR CUBE
                class_couleur_cube.changer_couleur_cube(valeur)
            else:
                class_son.error_snd.play()

    def select(self, fenetre=""): #[K_SPACE]
        if fenetre == "menu":
            if self.ID == 0: #JOUER
                class_son.select_game_snd.play()
                delai(1000)
            elif self.ID == 1: #PARAMETRES
                class_son.select_snd.play()
                parametres()
            elif self.ID == 2: #SCORES
                class_son.select_snd.play()
                scores()

        elif fenetre == "parametres":
            if self.ID == 2: #MENU AUDIO
                class_son.select_snd.play()
                audio()
            elif self.ID == 3: #PLEIN ECRAN
                class_plein_ecran.basculer_plein_ecran()

        elif fenetre =="audio":
            if self.ID == 1: #MUSIQUE (JOUER)
                class_musique.select_musique()

# Charge les parametres du niveau souhaité
class Niveau():
    def __init__(self):
        self.niveau = niveau
        self.dict = { "FACILE":0, "MOYEN":1, "DIFFI.":2 }
        self.dict_inverse = {cle: contenu for contenu, cle in self.dict.items()}
        self.niveau_ID = self.dict[self.niveau]

    # Change et sauvegarde le niveau, puis modifie sa label
    def changer_niveau(self, valeur):
        class_son.select_snd.play()
        if self.niveau_ID == 2 and valeur > 0:
            self.niveau_ID = 0
        elif self.niveau_ID == 0 and valeur < 0:
            self.niveau_ID = 2
        else:
            self.niveau_ID += valeur
        self.niveau = self.dict_inverse[self.niveau_ID]
        label_parametres.label[0] = label_parametres.font.render("NIV. ["+self.niveau+"]", 1, label_parametres.couleur)
        modifier_parametres("NIVEAU", self.dict_inverse[self.niveau_ID])

# Charge les parametres du nombre d'étages souhaité
class Etage():
    def __init__(self):
        self.etage = etage

    # Change et sauvegarde l'étage, puis modifie sa label
    def changer_etage(self, valeur):
        class_son.select_snd.play()
        if self.etage == 25 and valeur > 0:
            self.etage = 13
        elif self.etage == 13 and valeur < 0:
            self.etage = 25
        else:
            self.etage += valeur
        label_parametres.label[1] = label_parametres.font.render("ETAGE ["+str(self.etage)+"]", 1, label_parametres.couleur)
        modifier_parametres("ETAGE", self.etage)

# Charge les parametres de la couleur des cubes
class Couleur_Cube():
    def __init__(self):
        self.couleur_NOM = couleur
        self.dict = { "BLEU":0, "JAUNE":1, "MAUVE":2, "ROUGE":3, "VERT":4 }
        self.dict_inverse = {cle: contenu for contenu, cle in self.dict.items()}
        self.couleur_ID = self.dict[self.couleur_NOM]

    # Change et sauvegarde la couleur des cubes, puis affecte sa label
    def changer_couleur_cube(self, valeur):
        class_son.select_snd.play()
        if self.couleur_ID == 4 and valeur > 0:
            self.couleur_ID = 0
        elif self.couleur_ID == 0 and valeur < 0:
            self.couleur_ID = 4
        else:
            self.couleur_ID += valeur
        self.couleur_NOM = self.dict_inverse[self.couleur_ID]
        label_parametres.label[4] = label_parametres.font.render("CUBE ["+self.couleur_NOM+"]", 1, label_parametres.couleur)
        modifier_parametres("COULEUR", self.dict_inverse[self.couleur_ID])

# Permet de changer la fenêtre (DÉFAUT: non plein écran)
class Plein_Ecran():
    def __init__(self):
        self.plein_ecran = False

    # Bascule l'affichage selon son état actuel
    def basculer_plein_ecran(self):
        if not self.plein_ecran:
            pygame.display.set_mode((display), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((display))
        self.plein_ecran = not self.plein_ecran

# Charge la playlist et permet de changer de musique
class Musique():
    def __init__(self):
        self.musique_ID = -1
        self.directoire = "musics/"
        self.liste_musiques = listdir(self.directoire)
        self.nb_max = len(self.liste_musiques)-1

    # Permet en changer la musique en cours, puis affecte sa label
    # Le choix de musique revient à la première si la dernière est sélectionné
    def changer_musique(self, valeur):
        class_son.select_snd.play()
        if self.musique_ID == self.nb_max and valeur > 0:
            self.musique_ID = 0
        elif self.musique_ID == 0 and valeur < 0:
            self.musique_ID = self.nb_max
        else:
            self.musique_ID += valeur
        self.changer_label_musique()

    # Une fois la musique sélectionné, appel la fonction pour la jouer
    def select_musique(self):
        self.jouer_une_musique(self.musique_ID)

    # Joue la musique selon son ID (-1 aléatoire), puis affecte sa label
    def jouer_une_musique(self, ID=-1):
        if ID == -1:
            self.musique_ID = randint(0, self.nb_max)
        else:
            self.musique_ID = ID
        pygame.mixer.music.load(self.directoire+self.liste_musiques[self.musique_ID])
        pygame.mixer.music.play()
        self.changer_label_musique()
        print("[MUSIQUE EN COURS] "+self.liste_musiques[self.musique_ID])

    # Modifie la label cible
    def changer_label_musique(self):
        label_audio.label[1] = label_audio.font.render(self.liste_musiques[self.musique_ID].split(".")[0], 1, label_audio.couleur)

# Charge les parametres de volume du jeu
class Volume():
    def __init__(self):
        self.volume = volume

    # Change et sauvegarde le volume, puis affecte sa label
    # Empêche de dépasser la limite 0-100%
    def changer_volume(self, valeur):
        if curseur_audio.ID == 0:
            if (self.volume != 1 and valeur > 0) or (self.volume > 0 and valeur < 0):
                self.volume = round(self.volume + valeur, 1)
                pygame.mixer.music.set_volume(self.volume)
                class_son.select_snd.play()
                label_audio.label[0] = label_audio.font.render("VOLUME ["+str(round(self.volume*100,1))[:-2]+"%]", 1, label_audio.couleur)
                modifier_parametres("VOLUME", self.volume)
            else:
                class_son.error_snd.play()

# Construit les labels personnalisées selon le type de menu à afficher
class Label():
    def __init__(self, x, y, separ, couleur, taille, text):
        self.font = pygame.font.Font("sprites/font.ttf", taille)
        self.couleur = couleur
        self.label = []
        self.text = text
        self.x = x
        self.y = y
        self.separ = separ
        for i in range(len(self.text)):
            self.label.append(self.font.render(text[i], 1, self.couleur))

    # Actualise les tous les labels du menu en cours
    def actualiser(self):
        y = self.y
        for i in range(len(self.text)):
            screen.blit(self.label[i], (self.x, y))
            y += self.separ

# Cette fonction met un délai avant de déclencher la prochaine action
# Bloque l'accès au clavier également
def delai(temps):
    pygame.event.set_blocked(KEYDOWN)
    pygame.time.set_timer(PAUSE, temps)

# Cette fonction affiche le menu parametres audios
def audio():
    fin = False
    while not fin:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit();
            if event.type == SONG_END:
                class_musique.jouer_une_musique()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    curseur_audio.select("audio")
                elif event.key == K_LEFT:
                    curseur_audio.changer_config(-1, "audio")
                elif event.key == K_RIGHT:
                    curseur_audio.changer_config(1, "audio")
                elif event.key == K_DOWN:
                    curseur_audio.deplacer(1, 65)
                elif event.key == K_UP:
                    curseur_audio.deplacer(-1, -65)
                elif event.key == K_ESCAPE:
                    fin = True

        # Actualise le curseur, les labels et le frame
        screen.fill((0,0,0))
        pygame.draw.rect(screen, (255, 0, 255), ((20, 100), (200, 200)), 1)
        label_audio.actualiser()
        curseur_audio.update()
        sprites_curseur_audio.draw(screen)
        pygame.display.flip()

# Cette fonction affiche le menu parametres
def parametres():
    fin = False
    while not fin:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit();
            if event.type == SONG_END:
                class_musique.jouer_une_musique()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    curseur_parametres.select("parametres")
                elif event.key == K_LEFT:
                    curseur_parametres.changer_config(-1, "parametres")
                elif event.key == K_RIGHT:
                    curseur_parametres.changer_config(1, "parametres")
                elif event.key == K_DOWN:
                    curseur_parametres.deplacer(1, 40)
                elif event.key == K_UP:
                    curseur_parametres.deplacer(-1, -40)
                elif event.key == K_ESCAPE:
                    fin = True

        # Actualise le curseur, les labels et le frame
        screen.fill((0,0,0))
        pygame.draw.rect(screen, (255, 255, 0), ((20, 100), (200, 200)), 1)
        label_parametres.actualiser()
        curseur_parametres.update()
        sprites_curseur_parametres.draw(screen)
        pygame.display.flip()

# Cette fonction affiche le menu scores
def scores():
    # Construit la label personnalisée, puis charge tous les scores du fichier
    label_score = Label(5, 5, 8, (0, 255, 0), 4, charger_scores())
    fin = False
    while not fin:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit();
            if event.type == SONG_END:
                class_musique.jouer_une_musique()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    fin = True

        # Actualise le label et le frame
        screen.fill((0,0,0))
        pygame.draw.rect(screen,
                        (randint(0,255), randint(0,255), randint(0,255)),
                        ((0, 0), (239, 399)), 2)
        label_score.actualiser()
        pygame.display.flip()

# Cette fonction affiche le menu principal
def menu():
    class_musique.jouer_une_musique()
    fin = False
    while not fin:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit();
            if event.type == SONG_END:
                class_musique.jouer_une_musique()
            if event.type == PAUSE:
                print("'USEREVENT' EXÉCUTION MAIN()")
                pygame.time.set_timer(PAUSE, 0)
                pygame.event.set_allowed(KEYDOWN)
                main()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    curseur_menu.select("menu")
                elif event.key == K_DOWN:
                    curseur_menu.deplacer(1, 50)
                elif event.key == K_UP:
                    curseur_menu.deplacer(-1, -50)
                elif event.key == K_ESCAPE:
                    fin = True

        # Actualise le curseur, les labels et le frame
        screen.fill((0,0,0))
        pygame.draw.rect(screen, (255, 255, 255), ((20, 100), (200, 200)), 1)
        label_menu.actualiser()
        curseur_menu.update()
        sprites_curseur_menu.draw(screen)
        pygame.display.flip()

# Cette fonction exécute le jeu
def main():
    temps_debut = pygame.time.get_ticks()
    # Définie le nombre de pixel selon le nombre d'étage
    base = class_etage.etage*16
    # Cette variable sera utilisée durant la boucle pour déterminer
    # le cube à actualiser
    ID = 0
    # Apparition du premier cube (X, Y, VITESSE) et l'ajoute au groupe
    cube.append(Cube(48, base-16, 1000))
    sprites_cube.add(cube)
    game_over = False
    while not game_over:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); exit();
            # Joue une musique aléatoire lorsque celle-ci termine
            if event.type == SONG_END:
                class_musique.jouer_une_musique()
            # Active l'accès au clavier et quitte la boucle
            # une fois le délai terminé.
            if event.type == PAUSE:
                print("'USEREVENT' SORTIE DE LA BOUCLE MAIN()")
                pygame.time.set_timer(PAUSE, 0)
                pygame.event.set_allowed(KEYDOWN)
                game_over = True
            # Événement du clavier
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    game_over = True
                elif event.key == K_SPACE:
                    pygame.event.set_blocked(KEYDOWN)
                    cube[ID].stop()
                    ID += 1

        # Dessine à l'écran le frame et les cubes
        screen.fill((0,0,0))
        screen.fill((45,45,45), ((0,0),(112,base)))
        sprites_cube.update()
        sprites_cube.draw(screen)
        screen.fill((0,0,0), ((0,base),(112,display[1])))
        pygame.draw.rect(screen, (255, 255, 255), ((0,0), (112,base)), 1)
        pygame.draw.rect(screen, (255, 255, 255), ((0,0), (112,16)), 1)
        # Arrête le temps de jeu si le joueur meurt ou gagne
        if not cube[ID-1].gagne and not cube[ID-1].mort:
            parametres_cube.temps_de_jeu = str(round((pygame.time.get_ticks()-temps_debut)/1000, 1))
        # Actualise les label_stats
        label_stats.actualiser([
            "VITESSE: "+str(parametres_cube.vitesse),
            "TEMPS: "+parametres_cube.temps_de_jeu,
            "ETAGE: "+str(parametres_cube.etage)+"/"+str(class_etage.etage),
            "NIV. "+class_niveau.niveau])
        pygame.display.flip()

    # Réinitialise le jeu à la sortie de la boucle
    if game_over:
        parametres_cube.reinitialiser()
        cube.clear()
        sprites_cube.empty()

# EXECUTION
if __name__ == '__main__':
    print("Chargement des données de sauvegarde")
    couleur = charger_parametres("COULEUR")
    volume = float(charger_parametres("VOLUME"))
    etage = int(charger_parametres("ETAGE"))
    niveau = charger_parametres("NIVEAU")

    print("Initialisation des composants pygame")
    version = "4.0"
    display = (240, 400) # Affichage par défaut
    pygame.mixer.init(22100, -16, 2, 64)
    pygame.init()
    pygame.mouse.set_visible(0)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(display)
    pygame.display.set_caption("Stacker v"+version)
    icon = pygame.image.load("sprites/icon.png")
    pygame.display.set_icon(icon)
    pygame.mixer.music.set_volume(volume)
    SONG_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(SONG_END)
    PAUSE = USEREVENT + 2

    print("Chargement du menu principal")
    nom_label_menu = ["JOUER", "PARAMETRES","SCORES"]
    label_menu = Label(60, 150, 50, (255, 255, 255), 10, nom_label_menu)
    curseur_menu = Curseur(150, len(nom_label_menu))
    sprites_curseur_menu = pygame.sprite.Group(curseur_menu)

    print("Chargement du menu parametres")
    nom_label_parametres = ["NIV. ["+str(niveau)+"]", "ETAGE ["+str(etage)+"]","AUDIO","PLEIN ECRAN","CUBE ["+couleur+"]"]
    label_parametres = Label(60, 115, 40, (255, 255, 0), 10, nom_label_parametres)
    curseur_parametres = Curseur(115, len(nom_label_parametres))
    sprites_curseur_parametres = pygame.sprite.Group(curseur_parametres)

    print("Chargement du menu audio")
    nom_label_audio = ["VOLUME"+" ["+str(round(volume*100,1))[:-2]+"%]", "MUSIQUE"]
    label_audio = Label(60, 165, 65, (255, 0, 255), 10, nom_label_audio)
    curseur_audio = Curseur(165, len(nom_label_audio))
    sprites_curseur_audio = pygame.sprite.Group(curseur_audio)

    print("Chargement des autres classes")
    class_plein_ecran = Plein_Ecran()
    class_musique = Musique()
    class_volume = Volume()
    class_couleur_cube = Couleur_Cube()
    class_etage = Etage()
    class_niveau = Niveau()
    class_son = Son()

    print("Chargement du jeu")
    parametres_cube = Parametres_Cube()
    label_stats = Label_Stats(120, 10, 35)
    cube = []
    sprites_cube = pygame.sprite.Group(cube)

    # Une fois tous les paramètres chargé, affiche le menu principal
    menu()
