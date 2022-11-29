from settings import *
from carte import Carte
import sys
import time
import numpy as np
import matplotlib.pyplot as plt


class App:
    def __init__(self):
        #Création de la carte
        t1=time.time()
        # self.map=Carte().map
        self.carte : Carte=Carte()
        t2=time.time()
        print(f'chargement Carte en {t2-t1:.0f} s')
        
        pg.init()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0.01
       
        # game objects
        print('Conversion de la carte')
        t1=time.time()
        # self.bg=pg.surfarray.make_surface(self.carte.colormap)
        self.bg=pg.image.load(self.carte.colormapfile)
        self.bg=pg.transform.scale(self.bg,(WIDTH,HEIGHT))
        
        t2=time.time()
        print(f'conversion Carte en {t2-t1:.0f} s')

    def update(self):
        # self.scene.update()
        # self.main_group.update()
        pg.display.set_caption(f'{self.clock.get_fps(): .1f}')
        self.delta_time = self.clock.tick()

    def draw(self):
        self.screen.blit(self.bg,(0,0))
        # self.main_group.draw(self.screen)
        pg.display.flip()

    def check_events(self):
        self.anim_trigger = False
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()

    def get_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def run(self):
        self.draw()
        # plt.figure()
        # plt.imshow(self.carte.map,cmap='terrain')
        # plt.show()
        while True:
            self.check_events()
            self.get_time()
            self.update()
            self.clock.tick(120)
            


if __name__ == '__main__':
    app = App()
    app.run()
