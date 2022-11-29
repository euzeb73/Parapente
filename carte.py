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
    shape=(N,N)
    sigma=N/4
    m,n = [(ss-1.)/2. for ss in shape]
    y,x = np.ogrid[-m:m+1,-n:n+1]
    h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
    h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh
    return h

class Carte():
    def __init__(self):
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
        print('Lecture minimap')
        self.make_minimap()
        print('Fabrication de la grande carte')
        self.make_map()
        print('Ajout du bruit')
        self.add_noise(250,100)
        print('Lissage')
        self.smoothen(200)

    def make_minimap(self):
        self.minimap = [[int(num) for num in line]
                             for line in self.mapdef]

    def make_map(self):
        self.map : np.ndarray = np.empty((HEIGHT//TILE_SIZE, WIDTH//TILE_SIZE))
        height,width= self.map.shape
        for i in range(height):
            for j in range(width):
                minih,miniw=len(self.minimap),len(self.minimap[0])
                alti = self.minimap[i//(TILE_SIZE *  HEIGHT // minih)][j//(TILE_SIZE * WIDTH // miniw)]  # à revoir avec des cstes
                self.map[i, j] = HAUTEURS[alti]

    def add_noise(self,noise_amp, noise_size : int):
        '''
        du bruit: d'amplitude noise_amp
        de taille caractéristique noise_size
        '''
        height,width= self.map.shape
        for i in range(0,height,noise_size):
            for j in range(0,width,noise_size):
                altshift=random.normalvariate(0,noise_amp)
                tab_altshift=altshift*np.ones((noise_size,noise_size))
                self.map[i:i+noise_size,j:j+noise_size]=self.map[i:i+noise_size,j:j+noise_size]+tab_altshift

    def smoothen(self,N):
        '''
        un filtre moyenneur de taille NxN
        '''
        filtre=np.ones((N,N)) #Moyenne
        filtre=np.array(
            [[1,1,5,1,1],
             [1,5,9,5,1],
             [5,5,20,5,5],
             [1,5,9,5,1],
             [1,1,5,1,1]]) #un peu au pif mais trop petit
        filtre=filtre/np.sum(filtre)
        filtre=gauss2D(N)
        self.map : np.ndarray = convolve2d(self.map,filtre,mode= 'same')

    def plot3D(self):
        height,width= self.map.shape
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

# carte.plot3D()
# plt.figure()
# plt.imshow(carte.map)
# plt.show()

