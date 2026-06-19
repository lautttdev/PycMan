import pygame
from pathlib import Path
from matrix import MATRIX_EATABLES
from matrix import TILE_SIZE
from random import randint

SPRITES = [
    Path("Resources") / "sprites" / "Graphics" / "pixel-fruit-apple-24x24.png",
    Path("Resources") / "sprites" / "Graphics" / "pixel-fruit-cherry-24x24.png",
    Path("Resources") / "sprites" / "Graphics" / "pixel-fruit-orange-24x24.png",
    Path("Resources") / "sprites" / "Graphics" / "pixel-fruit-strawberry-24x24.png",
]

SPAWNEABLE_TILES = []

for y, row in enumerate(MATRIX_EATABLES):
    for x, value in enumerate(row):
        if value == 1:
            SPAWNEABLE_TILES.append((x, y))

MAP_WIDTH = len(MATRIX_EATABLES[0])


class Fruit(pygame.sprite.Sprite):
    def __init__(self, fruit_group: pygame.sprite.Group):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(SPRITES[0])
        self.rect = self.image.get_rect()

        self.fruit_group = fruit_group

        self.points = 500

        self.current_time_spawn = 0
        self.max_time_spawn = randint(15, 30)
    

    def spawn(self, delta):
        self.current_time_spawn += delta

        if self.current_time_spawn >= self.max_time_spawn:
            spawn_x, spawn_y = SPAWNEABLE_TILES[randint(0, len(SPAWNEABLE_TILES) - 1)]

            self.rect.center = (
                spawn_x * TILE_SIZE[0] + TILE_SIZE[1] // 2,
                spawn_y * TILE_SIZE[0] + TILE_SIZE[1] // 2
                )           

            self.image = pygame.image.load(SPRITES[randint(0, 3)])

            self.current_time_spawn = 0

            self.fruit_group.add(self)
