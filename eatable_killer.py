import pygame
from pathlib import Path
from matrix import *

SPRITE = Path("Resources") / "sprites" / "bullet-1.png"


class Eatable_Killer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(pygame.image.load(SPRITE), (20, 20))
        self.rect = self.image.get_rect()
        self.points = 500
        self.animation_time = 0
        self.animation_black = False


    def animation(self, delta):
        self.animation_time += delta
        if self.animation_time >= 0.5:
            match self.animation_black:
                case False:
                    self.animation_time = 0
                    self.animation_black = True
                    self.image = pygame.transform.scale(pygame.image.load(SPRITE), (20, 20))
                case True:
                    self.animation_time = 0
                    self.animation_black = False
                    self.image = pygame.Surface((20, 20))
                    self.image.fill("black")