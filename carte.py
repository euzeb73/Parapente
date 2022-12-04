from settings import*
import numpy as np
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
import random

import mayavi.mlab as ma


def gauss2D(N):
    """
    2D gaussian mask
    """
    shape = (N, N)
    sigma = N/4
    m, n = [(ss-1.)/2. for ss in shape]
    y, x = np.ogrid[-m:m+1, -n:n+1]
    h = np.exp(-(x*x + y*y) / (2.*sigma*sigma))
    h[h < np.finfo(h.dtype).eps*h.max()] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh
    return h


class Carte():
    def __init__(self,screen):
        self.screen = screen
        #taille 9x16
        # 0,1,2,3 pour les hauteurs()
        self.mapdef = ['3100011122211100',
                       '3100011000000023',
                       '3000001111000022',
                       '3310000112110033',
                       '3332200122220002',
                       '3332220011220001',
                       '3332222000110002',
                       '3333321111000003',
                       '3333333222220000']
        #taille 9x12
        # 0,1,2,3 pour les hauteurs()
        self.mapdef = ['310011221100',
                       '310010000023',
                       '300011100022',
                       '331000112103',
                       '332001222002',
                       '332200122001',
                       '332220011002',
                       '333321100003',
                       '333332220000']

        self.colormapfile = 'temp.png'

        print('Lecture minimap')
        self.make_minimap()
        print('Fabrication de la grande carte')
        self.make_map()
        #Pour du debug
        self.primmap=self.map.copy()
        print('Ajout du bruit')
        #en full c'est 250,100
        self.add_noise(250,TILE_SIZE)
        print('Lissage')
        self.smoothen(2*TILE_SIZE)
        # en full c'est 200
        
        #On élimine les 0:
        self.map [ self.map < 0] = 0

        self.create_colormap()

        #Pour affichage dans pygame
        self.bg = pg.image.load(self.colormapfile)
        self.bg = pg.transform.smoothscale(self.bg, (MWIDTH, MHEIGHT))

        #TODO: Clarifier
        #TILE_SIZE c'est la taille d'une tuile de minimap, pas trop utile en fait en dehors de carte
        #self.scale est l'échelle de self.map autrement dit entre i et i+1 il y a une distance scale en m
        #Ca doit avoir un rapport avec SCALE mais à clarifier
        self.scale = 2 # en m
        
    def add_thermique(self,thermiques_list):
        """
        les thermiques présents
        """
        self.thermiques=thermiques_list
    
    def add_vent(self,vent):
        """
        On verra
        """
        pass
    

    def make_minimap(self):
        self.minimap = [[int(num) for num in line]
                        for line in self.mapdef]

    def make_map(self):
        self.map: np.ndarray = np.empty((9*TILE_SIZE, 12*TILE_SIZE))
        height, width = self.map.shape
        for i in range(height):
            for j in range(width):
                # minih,miniw=len(self.minimap),len(self.minimap[0])
                alti = self.minimap[i//(TILE_SIZE)][j//(TILE_SIZE)]
                self.map[i, j] = HAUTEURS[alti]

    def add_noise(self, noise_amp, noise_size: int):
        '''
        du bruit: d'amplitude noise_amp en m
        de taille verticale noise_size en pixel 
        (taille horizontale=WIDTH/HEIGHT*taille vert)
        '''

        'mettre des rectangel '
        height, width = self.map.shape
        for i in range(0, height, noise_size):
            for j in range(0, width, noise_size):
                altshift = random.normalvariate(0, noise_amp)
                if j+MWIDTH*noise_size//MHEIGHT < width:
                    noisewidth = MWIDTH*noise_size//MHEIGHT
                else:
                    noisewidth = MWIDTH*noise_size//MHEIGHT - \
                        (j+MWIDTH*noise_size//MHEIGHT) % width
                if i+noise_size < height:
                    noiseheight = noise_size
                else:
                    noiseheight = noise_size-(i+noise_size) % height
                tab_altshift = altshift*np.ones((noiseheight, noisewidth))
                self.map[i:i+noise_size, j:j+MWIDTH*noise_size//MHEIGHT] = self.map[i:i +
                                                                                    noise_size, j:j+MWIDTH*noise_size//MHEIGHT]+tab_altshift

    def smoothen(self, N):
        '''
        un filtre moyenneur de taille NxN
        '''
        filtre = np.ones((N, N))  # Moyenne
        filtre = np.array(
            [[1, 1, 5, 1, 1],
             [1, 5, 9, 5, 1],
             [5, 5, 20, 5, 5],
             [1, 5, 9, 5, 1],
             [1, 1, 5, 1, 1]])  # un peu au pif mais trop petit
        filtre = filtre/np.sum(filtre)
        filtre = gauss2D(N)
        self.map: np.ndarray = convolve2d(
            self.map, filtre, mode='same', boundary='symm')

    def create_colormap(self):
        '''
        Version à la main

        maxi=np.max(self.map)
        mini=np.min(self.map)
        height,width= self.map.shape
        self.colormap=np.zeros((height,width,3))
        for i in range(height):
            for j in range(width):
                hauteur=self.map[i,j]
                x=(hauteur-mini)/(maxi-mini) #x varie de 0 à 1
                red=math.floor(200*x**6)
                green=math.floor(200*(1-math.exp(-x/0.2)))
                blue=math.floor(4*(x-0.5)**2 *200)
                pixel=np.array([red,green,blue])
                self.colormap[i,j]=pixel
        self.colormap=np.swapaxes(self.colormap,0,1)
        '''

        plt.imsave(self.colormapfile, self.map, cmap='terrain')

    def read_alt(self, x, y):
        """
        Renvoie l'altitude du point x,y si x,y n'est pas dans la map renvoie 4000 m
        """
        N, M = self.map.shape
        #il y aura du SCALE là de dans plus tard.
        j,i=int(round(x/self.scale)),int(round(y/self.scale))
        notinmap = j < 0 or j > M-1 or i < 0 or i > N-1
        if notinmap:
            return 4000
        else:
            return self.map[i,j]

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        if len(self.thermiques) > 0:
            for thermique in self.thermiques:
                thermique.draw()   

    def update(self):
        if len(self.thermiques) > 0:
            for thermique in self.thermiques:
                thermique.update()   

    def plot3D(self):
        height, width = self.map.shape
        X = SCALE*np.arange(width)
        Y = SCALE*np.arange(height)
        X, Y = np.meshgrid(X, Y)
        X = X.transpose()  # là y'a transposition d'après le manuel.
        Y = Y.transpose()
        fig = ma.figure()
        # pour que ça colle transposition+renversement des 2 axes
        tabalti = np.flip(self.map.transpose(), 1)
        ma.surf(X, Y, tabalti, colormap='gist_earth')
        ma.show()


if __name__ == '__main__':
    carte = Carte()
    # carte.plot3D()
    plt.figure()
    plt.imshow(carte.map, cmap='terrain')
    height, width = carte.map.shape
    X = np.arange(width)
    Y = np.arange(height)
    plt.contour(X, Y, carte.map)
    plt.show()
