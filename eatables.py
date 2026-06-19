import pygame
from pathlib import Path
from matrix import *

SPRITE = Path("Resources") / "sprites" / "bullet-1.png"


class Eatable(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(SPRITE)
        self.rect = self.image.get_rect()
        self.points = 100