from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sympy import line_integrate
from carte import Carte
from parapente import Joueur
from settings import *
import numpy as np


class HubUp():
    def __init__(self, screen, joueur: Joueur, carte: Carte):
        self.joueur = joueur
        self.screen = screen
        self.carte = carte
        self.hub = pg.Rect(MWIDTH, 0, HUPWIDTH, HUPHEIGHT)
        self.distance = 250
        self.percent = 75/100  # le pourcentage de la distance qui est devant
        self.image = pg.transform.smoothscale(pg.image.load(
            'parap_cote.png'), (10*HUPWIDTH/100, 25*HUPHEIGHT/100))

    def get_altitudes(self):
        '''
        renvoie la liste des altitudes dans la direction de la vitesse du joueur
        sur une distance self.distance
        '''
        direction = self.joueur.vecv/self.joueur.vecv.length()
        self.debut = self.joueur.OM-self.distance*direction*(1-self.percent)
        self.fin = self.joueur.OM+self.distance*direction*self.percent
        altitudes=[]
        position=self.debut.copy()
        for i in range(self.distance):
            x,y=position
            alt=self.carte.read_alt(x,y)
            altitudes.append(alt)
            position+=direction
        
        return altitudes

    def prep_lines(self,altitudes):
        linelist=[(MWIDTH,HUPHEIGHT)] #en bas à gauche
        playeralt=self.joueur.z
        x=MWIDTH
        deltax=HUPWIDTH/self.distance
        for alt in altitudes:
            x+=deltax
            #A revoir
            y=HUPHEIGHT-(HUPHEIGHT-25*HUPHEIGHT/100)*alt/playeralt
            linelist.append((x,y))
        linelist.append((WIDTH,HUPHEIGHT)) #enbas à droite
        return linelist



    def update(self):
        alts = self.get_altitudes()
        self.linelist=self.prep_lines(alts)

    def draw(self):
        pg.Surface.fill(self.screen, (255, 0, 0), rect=self.hub)
        pg.draw.line(self.screen, (128, 0, 128), self.debut, self.fin,5)
        # LE parapente
        self.screen.blit(self.image, (MWIDTH+(1-self.percent)*HUPWIDTH, 0))
        couleur_terre=(153,76,0)
        pg.draw.polygon(self.screen,couleur_terre, self.linelist)
