from cmath import sqrt
from parapente import Joueur
from settings import *
import numpy as np
from math import sqrt,cos,sin
from numba import njit

@njit(fastmath=True)
def ray_casting(ecran,scale,OMplayer,zplayer,vecv,longueur,colormap,map):
    demi_angle = 30
    N = HDWIDTH  # nb de rayons
    # le array avec les pixels
    ecran[:]=np.array([200, 200, 255])
    milieu_ecran_vert = HDHEIGHT // 2  # milieu de l'écran
    delta_theta = np.deg2rad(2*demi_angle/N)
    # les valeurs du y le plus bas sur l'écran pour chaque rayon
    y_defaut = np.full(N, HDHEIGHT)
    direction = vecv / sqrt(vecv[0]**2+vecv[1]**2)
    demi_angle = -np.deg2rad(30)
    rot = np.array([[cos(demi_angle), -sin(demi_angle)], [sin(demi_angle), cos(demi_angle)]])
    direction=np.dot(rot,direction) # valeur de départ 
    for ray_num in range(N):
        for distance in range(1, longueur,5): #step élevé ça va plus vite mais moins de détails.
            x, y = OMplayer + direction * distance
            Nn, M = map.shape
            #il y aura du SCALE là de dans plus tard.
            j,i=int(round(x/scale)),int(round(y/scale)) #map et colormap sont pas dans le même sens map i->y j->x
            notinmap = j < 0 or j > M-1 or i < 0 or i > Nn-1
            if not(notinmap): #très élégant
                z = map[i,j]
                facteur = 20 #au pif pour que ça rende bien
                yscreen = int(facteur*(zplayer - z) /
                                distance) + milieu_ecran_vert
                # pour ne pas afficher ce qui est hors écran
                yscreen = max(yscreen, 0)
                if yscreen < y_defaut[ray_num]:
                    #il y aura du SCALE là dedans plus tard.
                    i, j = int(round(x/scale)), int(round(y/scale))#map et colormap sont pas dans le même sens colormap i->x j->y
                    couleur = colormap[i,j]
                    for y_ecran in range(yscreen, y_defaut[ray_num]):
                        # on peint jusqu'à défaut
                        ecran[ray_num, y_ecran] = couleur
                    # c'est le nouveau défaut le prochain point ne pourra pas peindre plus bas
                    y_defaut[ray_num] = yscreen

        # on décale la diretion du prochain rayon
        rot = np.array([[cos(delta_theta), -sin(delta_theta)], [sin(delta_theta), cos(delta_theta)]])
        direction=np.dot(rot,direction)
    return ecran

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
        N,M,L=self.colormap.shape
        for i in range(N):
            for j in range(M):
                self.colormap[i,j]=np.array([self.colormap[i,j,0],self.colormap[i,j,1],self.colormap[i,j,2]])

    def draw(self):
        longueur=1500
        N = HDWIDTH  # nb de rayons
        screen_array = np.full((N, HDHEIGHT, 3), np.array([200, 200, 255]))
        ecran = ray_casting(screen_array,self.joueur.carte.scale,np.array(self.joueur.OM),np.array(self.joueur.z),np.array(self.joueur.vecv),longueur,self.colormap,self.joueur.carte.map)
        view3D = pg.surfarray.make_surface(ecran)
        pg.Surface.blit(self.screen, view3D, self.hub)
        # pg.Surface.fill(self.screen, (0, 0, 255), rect=self.hub)

        #ajout de l'angle de vue + longueur
        direction = self.joueur.vecv / self.joueur.vecv.length()
        direction.rotate_ip(-30)
        OMplayer = self.joueur.OM
        pg.draw.line(self.screen, (128, 0, 128), OMplayer, OMplayer+longueur*direction)
        direction.rotate_ip(60)
        pg.draw.line(self.screen, (128, 0, 128), OMplayer, OMplayer+longueur*direction)
     
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
