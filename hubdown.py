from settings import *
class HubDown():
    def __init__(self,screen):
        self.screen=screen
        self.hub=pg.Rect(MWIDTH,HUPHEIGHT,HDWIDTH,HDHEIGHT)
    def draw(self):
        pg.Surface.fill(self.screen,(0,0,255),rect=self.hub)
