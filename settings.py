import pygame as pg

vec2 = pg.math.Vector2
WIDTH, HEIGHT =1600, 900
RES = vec2(WIDTH, HEIGHT)
CENTER = H_WIDTH, H_HEIGHT = RES // 2
#Ecran
#PArtie carte
MWIDTH=4*HEIGHT//3
MHEIGHT=HEIGHT
#Partie HUB
#HUB UP
HUPWIDTH=WIDTH-MWIDTH
HUPHEIGHT=2*HEIGHT//3
#HUB DOWN
HDWIDTH=HUPWIDTH
HDHEIGHT=HEIGHT//3
#Carte
TILE_SIZE = 50 #1,2,4,5,10,20,25,50,100 sont les seules valeurs possibles
#Hauteurs correspondantes à 0,1,2,3 sur minimap
HAUTEURS=[100,500,1000,2000]
#Echelle horizontale en mpp (meter per pixel)
SCALE=0.5
















