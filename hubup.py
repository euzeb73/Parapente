from settings import *
class HubUp():
    def __init__(self,screen):
        self.screen=screen
        self.hub=pg.Rect(MWIDTH,0,HUPWIDTH,HUPHEIGHT)
    def draw(self):
        pg.Surface.fill(self.screen,(255,0,0),rect=self.hub)
