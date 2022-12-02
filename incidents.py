from typing import ParamSpec
from regex import P
from sympy import Parabola
from settings import *
from parapente import Parapente

class Incident():
    def __init__(self, parapente : Parapente):
        self.parapente = parapente

class Vrille(Incident):
    def __init__(self, parapente : Parapente):
        super().__init__(parapente)

class Fermeture(Incident):
    def __init__(self, parapente : Parapente, pourcent):
        super().__init__(parapente)
        self.pourcent=pourcent

class Abatee(Incident):
    def __init__(self, parapente : Parapente, angle):
        super().__init__(parapente)
        self.angle=angle