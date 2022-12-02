from parapente import Joueur
from settings import *
class HubDown():
    def __init__(self,screen,joueur : Joueur):
        self.screen=screen
        self.joueur=joueur
        self.hub=pg.Rect(MWIDTH,HUPHEIGHT,HDWIDTH,HDHEIGHT)
        #Positions extrèmes des mains
        self.yhandsup=HUPHEIGHT+15*HDHEIGHT/100
        self.yhandsdown=HUPHEIGHT+85*HDHEIGHT/100
        #taille du cercle
        self.handsradius=5*HDHEIGHT/100
        #position horiz
        self.xlefth=MWIDTH+15*HDWIDTH/100
        self.xrighth=MWIDTH+85*HDWIDTH/100
    def draw(self):
        pg.Surface.fill(self.screen,(0,0,255),rect=self.hub)
        #Main gauche
        longueur=self.joueur.frein_gauche.longueur
        y = self.yhandsup + (self.yhandsdown-self.yhandsup) *longueur/100
        pg.draw.circle(self.screen,(0,200,0),(self.xlefth,y),self.handsradius)
        longueur=self.joueur.frein_droit.longueur
        y = self.yhandsup + (self.yhandsdown-self.yhandsup) *longueur/100
        pg.draw.circle(self.screen,(0,200,0),(self.xrighth,y),self.handsradius)