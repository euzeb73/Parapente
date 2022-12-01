from settings import *

class Parapente(pg.sprite.Sprite):
    def __init__(self,screen):
        super().__init__()
        self.screen=screen
        
        #Caractéristiques physique
        self.vmin = 6 #en m s^-1 vitesse décrochage
        
        #Position
        self.x,self.y, self.z= 50,50,3000 #en m
        OM=vec2([self.x,self.y])
        self.angle=0
        #vitesse
        self.v=10
        self.vecv=vec2((0,-self.v))
        self.vz=-1
        #Le sprite
        self.original_image=pg.image.load('parap.png')
        self.image=self.original_image.copy()
        self.width=self.image.get_width()
        self.height=self.image.get_height()

        #Rectangle du sprite
        self.rect=self.image.get_rect(center=(self.x/SCALE,self.y/SCALE))
        # self.rotate(-45)

    def rotate(self,angle):
        self.vecv.rotate_ip(angle)
        self.angle+=angle
        self.angle = self.angle % 360
        self.image=pg.transform.rotate(self.original_image,self.angle)
        self.rect=self.image.get_rect(center=self.rect.center)
        
    
    def update(self):
        self.OM=self.OM+DT*self.vecv