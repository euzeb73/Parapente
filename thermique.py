
from settings import *
from carte import Carte
from vent import Vent


class Thermique():
    def __init__(self, screen, carte: Carte):
        self.screen = screen
        self.carte = carte
        self.set_param(20, 4, 3000)  # par défaut
        self.move_to(0, 0)  # par défaut aussi

    def move_to(self, x, y):
        self.OM = vec2(x, y)
        self.zmin = self.carte.read_alt(x, y)

    def set_param(self, radius, vzmax, zmax, vzmin=2):
        '''Génénère un thermique qui aura un vz
        qui augmente linéairement de vzmin à vzmax dans les
        premiere_partie % de sa hauteur puis diminue de vzmax à 0
        dans les derniere_partie % de sa hauteur'''
        if vzmax < vzmin:
            vzmax = vzmin
        self.premiere_partie = 25/100
        self.derniere_partie = 5/100
        self.radius = radius
        self.vzmin = vzmin
        self.vzmax = vzmax
        self.zmax = zmax

    def get_vz(self, pos2D: vec2, z):
        """
        Dépendance avec l'altitude linéaire par morceaux
        Dépendance radiale quadratique
        """
        vz = 0
        hauteur = self.zmax-self.zmin
        if z < self.zmin or z > self.zmax:
            vz = 0
        elif z > self.zmin and z < self.premiere_partie * hauteur + self.zmin:
            # monte de plus en plus
            vz = (self.vzmax-self.vzmin)*(z-self.zmin) / \
                (self.premiere_partie * hauteur)
        elif z > self.premiere_partie * hauteur + self.zmin and z < self.zmax-self.derniere_partie * hauteur:
            # Partie "milieu en hauteur" du thermique vz =cste= vzmax
            vz = self.vzmax
        elif z > self.zmax-self.derniere_partie * hauteur:
            # monte de moins en moins
            vz = (-self.vzmax)*(z-self.zmax)/(self.derniere_partie * hauteur)

        # Distance au centre
        d = (self.OM-pos2D).length()
        if d <= self.radius:  # dans le thermique
            vz = vz*(1-d/self.radius)**0.4
        else: # hors thermique
            vz = 0
        return vz

    def update(self):
        vent : Vent =self.carte.vent
        # Le thermique dérive à la vitesse du vent à son altitude mini
        vderive = vent.get_vwind(self.OM,self.zmin)
        self.OM += vderive*DT
        # self.move_to(*self.OM) #quand ce sera mieux fait.

    def draw(self):
        pg.draw.circle(self.screen, (200, 200, 200), self.OM/self.carte.scale, self.radius/self.carte.scale,width = 1)
