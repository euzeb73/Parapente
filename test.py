from settings import *
from carte import Carte
import sys

map=Carte().map
pg.init()
screen = pg.display.set_mode(RES)
bg=pg.surfarray.make_surface(map)
screen.blit(bg)
# pg.display.flip()

def check_events():
    for e in pg.event.get():
        if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
            pg.quit()
            sys.exit()

    
def run():
    while True:
        check_events()

run()
