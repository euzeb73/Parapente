from parapente import Joueur
from settings import *
import numpy as np
from numba import njit

@njit(fastmath=True)
def ray_casting():
    pass

class HubDown():
    def __init__(self, screen, joueur: Joueur):
        self.screen = screen
        self.joueur = joueur
        self.hub = pg.Rect(MWIDTH, HUPHEIGHT, HDWIDTH, HDHEIGHT)
        #Positions extrèmes des mains
        self.yhandsup = HUPHEIGHT+15*HDHEIGHT/100
        self.yhandsdown = HUPHEIGHT+85*HDHEIGHT/100
        #taille du cercle
        self.handsradius = 5*HDHEIGHT/100
        #position horiz
        self.xlefth = MWIDTH+15*HDWIDTH/100
        self.xrighth = MWIDTH+85*HDWIDTH/100
        #la carte pour les couleurs de ray casting
        self.colormap = pg.transform.smoothscale(self.joueur.carte.bg, (600, 450))  # sous forme d'image
        # array là où on va aller chercher les couleurs.
        self.colormap = pg.surfarray.array3d(self.colormap)

    def ray_casting(self):

        # échelle en m pour une distance i , i +1 dans le array
        scale = self.joueur.carte.scale
        demi_angle = 30
        N = HDWIDTH  # nb de rayons
        # le array avec les pixels
        self.ecran = np.full((N, HDHEIGHT, 3), (200, 200, 255))
        milieu_ecran_vert = HDHEIGHT // 2  # milieu de l'écran
        delta_theta = 2*demi_angle/N
        self.longueur = 1000  # distance max des rayons en pixels ou m
        OMplayer = self.joueur.OM
        zplayer = self.joueur.z
        # les valeurs du y le plus bas sur l'écran pour chaque rayon
        y_defaut = np.full(N, HDHEIGHT)
        direction = self.joueur.vecv / self.joueur.vecv.length()
        direction.rotate_ip(-demi_angle)  # valeur de départ
        for ray_num in range(N):
            for distance in range(1, self.longueur):
                x, y = OMplayer + direction * distance
                z = self.joueur.carte.read_alt(x, y)
                if z < 4000:  # On est dans la map
                    facteur = 20 #au pif pour que ça rende bien
                    yscreen = int(facteur*(zplayer - z) /
                                  distance) + milieu_ecran_vert
                    # pour ne pas afficher ce qui est hors écran
                    yscreen = max(yscreen, 0)
                    if yscreen < y_defaut[ray_num]:
                        #il y aura du SCALE là dedans plus tard.
                        i, j = int(round(x/scale)), int(round(y/scale))
                        couleur = self.colormap[i, j]
                        for y_ecran in range(yscreen, y_defaut[ray_num]):
                            # on peint jusqu'à défaut
                            self.ecran[ray_num, y_ecran] = couleur
                        # c'est le nouveau défaut le prochain point ne pourra pas peindre plus bas
                        y_defaut[ray_num] = yscreen

            # on décale la diretion du prochain rayon
            direction.rotate_ip(delta_theta)

    def draw(self):

        self.ray_casting()
        view3D = pg.surfarray.make_surface(self.ecran)
        pg.Surface.blit(self.screen, view3D, self.hub)
        # pg.Surface.fill(self.screen, (0, 0, 255), rect=self.hub)

        #ajout de l'angle de vue + longueur
        direction = self.joueur.vecv / self.joueur.vecv.length()
        direction.rotate_ip(-30)
        OMplayer = self.joueur.OM
        pg.draw.line(self.screen, (128, 0, 128), OMplayer, OMplayer+self.longueur*direction)
        direction.rotate_ip(60)
        pg.draw.line(self.screen, (128, 0, 128), OMplayer, OMplayer+self.longueur*direction)
     
        #Main gauche
        longueur = self.joueur.frein_gauche.longueur
        y = self.yhandsup + (self.yhandsdown-self.yhandsup) * longueur/100
        pg.draw.circle(self.screen, (0, 200, 0),
                       (self.xlefth, y), self.handsradius)
        #Main droite
        longueur = self.joueur.frein_droit.longueur
        y = self.yhandsup + (self.yhandsdown-self.yhandsup) * longueur/100
        pg.draw.circle(self.screen, (0, 200, 0),
                       (self.xrighth, y), self.handsradius)
