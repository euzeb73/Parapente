
from settings import *
from carte import Carte

class Vent():
    def __init__(self, carte : Carte):
        self.carte = carte

    def get_vwind(self,pos2D,z):
        '''
        renvoie le vent à la position pos2D et altitude z
        '''

        #Pour l'instant constant d'ouest
        vvent=5 #ms^-1
        return vec2(vvent,0)