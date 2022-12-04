
from settings import *
from carte import Carte
from thermique import Thermique

class Frein():
    def __init__(self):
        self.longueur = 20  # cm "au contact"

    def bougepas(self):
        pass

    def monte(self):
        self.longueur = max(0, self.longueur-VITESSEMAIN)

    def descend(self):
        # débatement max 1m
        self.longueur = min(100, self.longueur+VITESSEMAIN)


class Parapente(pg.sprite.Sprite):
    def __init__(self, screen, carte : Carte):
        super().__init__()
        self.screen = screen
        self.carte=carte

        #Caractéristiques physiques
        self.vmin = 6  # en m s^-1 vitesse décrochage
        self.vmax = 11  # en m s^-1 vitesse bras hauts
        # en m s^-2 "accélération" pour changement de vitesse quand changement de freinage
        self.reactivite = 5/3
        self.wmax = 130  # vitesse angulaire maximale en deg s^-1 80 c'est environ 4g
        #vitesse verticale vz
        self.vzdecro = - 20  # ms^-1 en décrochage
        self.vzstd = -1  # en air calme à 20 cm
        #Position
        self.x, self.y, self.z = 50, 50, 3000  # en m
        self.OM = vec2([self.x, self.y])
        self.angle = 0
        #vitesse
        self.v = 10
        self.vecv: vec2 = vec2((0, -self.v))
        self.w = 0  # vitesse angulaire
        self.vecvvent :vec2 = vec2((0,0)) #qd y'aura du vent
        #vitesse verticale vz
        self.vz = -1
        self.vzthermique = 0  # qd y'aura du thermique

        #Le sprite
        self.original_image = pg.image.load('parap.png')
        self.image = self.original_image.copy()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        #Rectangle du sprite
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.rotate(-120)

    def rotate(self, angle):
        # ca toourne pas dans le même sens pour les vec2
        self.vecv.rotate_ip(-angle)
        self.angle += angle
        self.angle = self.angle % 360
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def change_v(self, deltav):
        rapport = (self.v+deltav) / self.v
        self.vecv = self.vecv*rapport
        self.v = self.vecv.length()
    
    def calculate_vzthermique(self):
        thermiques : list(Thermique) =self.carte.thermiques
        if len(thermiques)>0 :
            for thermique in thermiques:
                d_fromcenter=(self.OM-thermique.OM).length()
                if d_fromcenter < thermique.radius:
                    self.vzthermique=thermique.get_vz(self.z)
                else:
                    self.vzthermique = 0
        else:
            self.vzthermique = 0

    def update_v(self):
        pass

    def update(self):
        #mise à jour position
        self.OM = self.OM+DT*(self.vecv+self.vecvvent)    
        self.rect = self.image.get_rect(center=self.OM)
        #Mise à jour altitude:
        self.z += self.vz
        #Check thermique
        self.calculate_vzthermique()
        #Mise à jour vitesse
        self.update_v()


class Joueur(Parapente):
    def __init__(self, screen , carte : Carte):
        super().__init__(screen,carte)
        self.frein_gauche = Frein()
        self.frein_droit = Frein()

    def v_avec_position_mains(self):
        '''
        Renvoie la norme de la vitesse de vol (stabilisée cste) en air calme avec
        les mains placées comme self.frein_gauche.longueur et 
        self.frein_droit.longueur
        '''
        maing = self.frein_gauche.longueur
        maind = self.frein_droit.longueur
        longueur_moy = (maing+maind)/2
        #formule quadratique pour passer de longueur à vitesse
        # tiens compte de longueur max = 100 cm
        v = self.vmax-longueur_moy**2*(self.vmax-self.vmin)/10000

        #Pour vz polynome en x^4 foir esssai_fonction.py
        coeffs = [2.33380864e-08 , 4.96811029e-07 ,-5.82210285e-05 ,-9.22100853e-03, 1.20000000e+00]
        def f(x):
            if x <= 80 :
                return sum([coeffs[i]*x**(4-i) for i in range(5)])
            else:
                return (20-1.3)*(x-80)/20+1.3
        vz = - f(longueur_moy)

        return v , vz

    def w_avec_position_mains(self):
        '''
        Renvoie la vitesse angulaire de rotation (stabilisée cste) en air calme avec
        les mains placées comme self.frein_gauche.longueur et 
        self.frein_droit.longueur
        '''
        maing = self.frein_gauche.longueur
        maind = self.frein_droit.longueur
        #tourner à gauche: rotation sens + à droite sens -
        diff_gmoinsd = maing-maind
        #formule quadratique pour passer de longueur à vitesse
        # tiens compte de longueur max = 100 cm
        def sign(x): return 1 if x > 0 else -1
        w = sign(diff_gmoinsd) * self.wmax*diff_gmoinsd**2/10000
        return w

    def update_v(self):
        '''
        Pour mettre à jour la vitesse
        en fonction de la position des mains
        '''
        #NORME
        vmains , vzmains = self.v_avec_position_mains()
        if (self.v-vmains) > self.vmin/0.001:  # tolérance
            if self.v > vmains:  # il faut diminuer v
                deltav = - self.reactivite*DT
                self.change_v(deltav)
                diff = vmains-self.v
                if diff > 0:  # on a surcorrigé
                    self.change_v(diff)
            else:  # il faut augmenter v
                deltav = self.reactivite*DT
                self.change_v(deltav)
                diff = vmains-self.v
                if diff < 0:  # on a surcorrigé
                    self.change_v(diff)
        #ANGLE
        wmains = self.w_avec_position_mains()
        #DAns un premier temps sans inertie
        self.w = wmains
        self.rotate(self.w*DT)
        #vz
        #DAns un premier temps sans inertie
        #maisn En tenant compte du virage
        vzvirage=-12*(self.w/self.wmax)**2 #-12 ms^-1 en virage au taquet

        self.vz = vzmains+vzvirage+self.vzthermique
