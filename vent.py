
from settings import *
from carte import Carte
import matplotlib.pyplot as plt


class Vent0():
    def __init__(self, carte: Carte):
        self.carte = carte

    def get_vwind(self, pos2D: vec2, z):
        '''
        renvoie le vent à la position pos2D et altitude z
        '''

        #Pour l'instant constant d'ouest
        vvent = 5  # ms^-1
        return vec2(vvent, 0)


class Vent():
    def __init__(self, carte: Carte, vecv: vec2):
        self.carte = carte
        self.carte_reduite = self.reduit_carte(1)  # a ajuster
        self.generate_wind(vecv)

    def reduit_carte(self, xystep=15):
        """
        renvoie une carte réduite en prenant un point tous les 
        xystep qui doit être un diviseur de 3*TILE_SIZE

        SANS DOUTE ce devrait etre une fonction de la classe Carte

        """
        assert 3*TILE_SIZE % xystep == 0  # doit être un diviseur de 3*TILE_SIZE
        map = self.carte.map
        N, M = map.shape
        Npetit, Mpetit = N//xystep, M // xystep
        carte_reduite = np.zeros((Npetit, Mpetit))
        for i in range(Npetit):
            for j in range(Mpetit):
                carte_reduite[i, j] = np.mean(
                    map[i*xystep:i*(xystep+1), j*xystep:j*(xystep+1)])
        self.scale_reduite=self.carte.scale*xystep
        return carte_reduite

    def generate_wind(self, vecv: vec2):
        ''' 
        génère un vent de secteur vecv (type vec2) qui se propage en tenant un peu compte
        du relief
        de l'altitude
        '''
        self.Nz = 5  # nombre de couches sur l'axe z, diviseur de 4000
        N, M = self.carte_reduite.shape
        # les tranches de cartes suivant l'altitude
        maps = np.zeros((N, M, self.Nz))
        for k in range(self.Nz):
            alt_couche = (k+1)*4000//N  # PAs de relief >4000
            for i in range(N):
                for j in range(M):
                    alt = self.carte_reduite[i, j]
                    if alt >= alt_couche:
                        # si on est en dessus de la couche
                        maps[i, j, k] = self.carte_reduite[i, j]
                        #sinon on laisse à 0

        # pour chaque position N,M, les Nz valeurs suivant l'altitude des coordonnées du vecteur vent
        self.vents = np.zeros((N, M, self.Nz, 2))
        for k in range(self.Nz):
            self.vents[:, :, k, :] = self.generate_vent_couche(
                maps[:, :, k], vecv)

    def generate_vent_couche(self, relief: np.ndarray, vecv: vec2):
        '''
        renvoie un array de même taille que relief avec une dimension de taille 2 en plus
        contenant les coordonnées du vecteur vitesse du vent
        exploration
        '''
        N, M = relief.shape
        vent = np.zeros((N, M, 2))
        tmax = 3600/2  # 30 min durée sur laquelle on simule l'écoulement
        Nt = 101  # nombre de pas de temps
        dt = tmax // (Nt-1)  # intervalle de temps
        for _ in range(Nt):
            vent_tplusdt = vent.copy()
            #advection en décalant les vecteurs vitesses
            for i in range(-1, N+1):  # -1 et N+1 sont les cases extérieures tjs à v=vecv
                for j in range(-1, M+1):
                    if self.carte.is_dedans(i, j):
                        v = vec2(list(vent[i, j]))
                    else:  # à l'extérieur tout vaut vecv
                        v = vecv
                    if v.length() > 0:  # si il y a un vent à propoager
                        x, y = self.carte.ij_to_xy(i, j)
                        # déplacement du vent pendant dt
                        xloin, yloin = vec2(x, y) + dt * vecv
                        inext, jnext = self.carte.xy_to_ij(xloin, yloin)
                        if self.carte.is_dedans(inext, jnext) and relief[inext, jnext] == 0:
                            vent_tplusdt[inext, jnext] = np.array(
                                v)  # nouvelle valeur
            #Incompressibilité
            Nincomp = 10  # nombre max d'itérations
            diff = 1000  # différence entre 2 tableaux initialisée à beaucoup
            difflimit = 1  # limite pour la moyenne des normes de la différence entre les vecteurs vitesses
            i = 0

            def compte_relief(i, j):
                """renvoie le nb de cases SANS du relief = nb voisins"""
                nb = 0
                voisins = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
                for voisin in voisins:
                    ivois, jvois = voisin
                    if self.carte.is_dedans(ivois, jvois):
                        if relief[ivois, jvois] == 0:
                            nb += 1
                    else:
                        nb += 1
                return nb

            while diff > 1 and i < Nincomp:
                vent_next = vent_tplusdt.copy()
                for i in range(N):
                    for j in range(M):
                        if i == N-1 and j == M-1:
                            vdessous, vdroite = vecv, vecv
                        else:
                            if i == N-1:  # En bas
                                vdessous = vecv
                            else:
                                vdessous = vec2(list(vent_next[i+1, j]))
                            if j == M-1:
                                vdroite = vecv
                            else:
                                vdroite = vec2(list(vent_next[i, j+1]))
                        v = vec2(list(vent_next[i, j]))
                        if relief[i, j] == 0:
                            nbvois = compte_relief(i, j)
                            div = vdessous.y-v.y+vdroite.x-v.x
                            correc = div/nbvois
                            #Pour gérer les cases avec des obstacles en voisins
                            imoins1, jmoins1 = 1, 1  # case en dessous et case à droite
                            if self.carte.is_dedans(i-1, j):
                                if relief[i-1, j] > 0:
                                    imoins1 = 0
                            if self.carte.is_dedans(i, j-1):
                                if relief[i-1, j] > 0:
                                    jmoins1 = 0
                            dvij = np.array((correc*jmoins1, correc*imoins1))
                            vent_next[i, j] = vent_next[i, j]+dvij  # case i,j
                            iplus1, jplus1 = 1, 1
                            if self.carte.is_dedans(i+1, j):
                                if relief[i+1, j] > 0:
                                    iplus1 = 0
                                dv = np.array((0, -iplus1*correc))
                                # case i+1,j
                                vent_next[i+1, j] = vent_next[i+1, j]+dv
                            if self.carte.is_dedans(i, j+1):
                                if relief[i, j+1] > 0:
                                    jplus1 = 0
                                dv = np.array((-jplus1*correc, 0))
                                vent_next[i, j+1] = vent_next[i,
                                                              j+1]+dv  # case i,j+1
                diff = np.mean(np.linalg.norm(vent_next-vent_tplusdt, axis=2))
                vent_tplusdt = vent_next.copy()

            #mise à jour des vents
            vent = vent_tplusdt.copy()

        """
        Ancienne idée avec A* mais c'est pas une bonne idée

        #On regarde sur quels côtés il faut commencer
        if vecv.x > 0:
            xstart = 0
        else:
            xstart = M
        for i in range(N):  # composante horizontale du vent
            vent[:, :, 0] = self.explore(
                relief, vent[:, :, 0], xstart, i, vecv, 'horiz')
        if vecv.y > 0:
            ystart = 0
        else:
            ystart = N

    def Astar(relief: np.ndarray, depart, arrivee):
        '''
        utilise A* pour relier depart (tuple) à arrivee sur la carte relief
        '''

    def explore(self, relief: np.ndarray, vent: np.ndarray, xdepart, ydepart, vecv, sens='horiz'):
        N, M = relief.shape
        if sens == 'horiz':
            v = vecv.x
            if xdepart == 0:
                xfin = M
            else:
                xfin = 0
        """

    def get_vwind(self, pos2D: vec2, z):
        '''
        renvoie le vent à la position pos2D et altitude z
        '''

        #Pour l'instant constant d'ouest
        vvent = 5  # ms^-1
        return vec2(vvent, 0)


if __name__ == '__main__':
    carte = Carte('pas pertinent')
    direction = vec2((3, 5))
    vent = Vent(carte, direction)
    z = 0

    vx, vy = [], []
    x, y = [], []
    map = carte.map
    N, M = map.shape
    for j in range(M):
        for i in range(N):
            vvent = vent.get_vwind(vec2(j, i), z)
            x.append(j)
            y.append(i)
            vx.append(vvent.x)
            vy.append(vvent.y)
    plt.figure()
    plt.imshow(map, cmap='gist_earth')
    plt.quiver([x, y], vx, vy)
