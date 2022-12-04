
from settings import *
from carte import Carte


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

    def get_vz(self, z):
        
        """
        TODO
        Ajouter une dépendance radiale

        Corriger la dépendance avec l'altitude (ça depasse vsmax)
        """

        hauteur = self.zmax-self.zmin
        if z < self.zmin or z > self.zmax:
            return 0
        elif z > self.premiere_partie * hauteur + self.zmin and z <= self.zmax-self.derniere_partie * hauteur:
            # monte de plus en plus
            return (self.vzmax-self.vzmin)*(z-self.zmin)/(self.premiere_partie * hauteur)
        elif z > self.zmax-self.derniere_partie * hauteur:
            # monte de moins en moins
            return (-self.vzmax)*(z-self.zmax)/(self.derniere_partie * hauteur)

    def update(self):
        pass

    def draw(self):
        pg.draw.circle(self.screen, (200, 200, 200, 0), self.OM, self.radius)
