from calendar import monthcalendar
from settings import *
from carte import Carte
from hubup import HubUp
from hubdown import HubDown
from parapente import Joueur, Parapente
import sys
import time
import numpy as np
import matplotlib.pyplot as plt


class Font():
    def __init__(self, font=None, size=48):

        self.font = pg.font.SysFont(font, size)  # initialise la police
        self.textdic = dict()  # Dictionnaire vide

    def addtext(self, text, txtname=None, color=(255, 0, 0)):
        '''fabrique une image(surface) associée à text prete à coller'''
        if txtname == None:
            self.textdic[text] = self.font.render(text, True, color)
        else:
            self.textdic[txtname] = self.font.render(text, True, color)

class App:
    def __init__(self):
        #Création de la carte
        t1 = time.time()
        # self.map=Carte().map
        self.carte: Carte = Carte()
        t2 = time.time()
        print(f'chargement Carte en {t2-t1:.0f} s')

        pg.init()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0.01

        # game objects
        print('Conversion de la carte')
        t1 = time.time()
        self.bg = pg.image.load(self.carte.colormapfile)
        self.bg = pg.transform.scale(self.bg, (MWIDTH, MHEIGHT))
        t2 = time.time()
        print(f'conversion Carte en {t2-t1:.0f} s')

        #PArapente
        self.parapente = Joueur(self.screen)

        #HUBs
        self.hubup = HubUp(self.screen, self.parapente)
        self.hubdown = HubDown(self.screen, self.parapente)

        #sprites
        self.spritegroup = pg.sprite.Group()
        self.parapente.add(self.spritegroup)

        #Police d'affichage
        self.fontsmall = Font('segoescript', 16)

        #Mouvement des freins
        self.freind, self.freing = 0, 0

    def update(self):
        # self.scene.update()
        # self.main_group.update()
        pg.display.set_caption(f'{self.clock.get_fps(): .1f}')
        self.delta_time = self.clock.tick()
        self.spritegroup.update()

    def draw(self):
        #Background
        self.screen.blit(self.bg, (0, 0))
        #Hubs
        self.hubup.draw()
        self.hubdown.draw()

        #Sprites
        self.spritegroup.draw(self.screen)

        #Infos
        self.fontsmall.addtext(f'vz {self.parapente.vz}','vz')
        self.fontsmall.addtext(f'maind {self.parapente.frein_droit.longueur}','md')
        
        self.screen.blit(self.fontsmall.textdic['vz'], (100,100))
        self.screen.blit(self.fontsmall.textdic['md'], (100,130))
        # pg.draw.rect(self.screen,(255,0,0),self.parapente.rect)
        # self.main_group.draw(self.screen)
        pg.display.flip()

    def check_events(self):
        #Système freins à améliorer
        MONTE = -1
        DESCEND = 1
        BOUGEPAS = 0
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif e.type == pg.KEYUP:
                if e.key == pg.K_a or e.key == pg.K_q:
                    self.freing = BOUGEPAS
                if e.key == pg.K_p or e.key == pg.K_m:
                    self.freind = BOUGEPAS
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_r:
                    self.parapente.rotate(-10)
                if e.key == pg.K_a:
                    self.freing = MONTE
                if e.key == pg.K_p:
                    self.freind = MONTE
                if e.key == pg.K_q:
                    self.freing = DESCEND
                if e.key == pg.K_m:
                    self.freind = DESCEND
        if self.freind == MONTE:
            self.parapente.frein_droit.monte()
        elif self.freind == DESCEND:
            self.parapente.frein_droit.descend()
        if self.freing == MONTE:
            self.parapente.frein_gauche.monte()
        elif self.freing == DESCEND:
            self.parapente.frein_gauche.descend()

    def get_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def run(self):
        # plt.figure()
        # plt.imshow(self.carte.map,cmap='terrain')
        # plt.show()
        while True:
            self.check_events()
            self.get_time()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == '__main__':
    app = App()
    app.run()
