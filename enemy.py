import pygame
from pathlib import Path
from random import randint

from matrix import MATRIX

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder as AStar
from pathfinding.core.diagonal_movement import DiagonalMovement

SPRITES_PATH = [
    Path("Resources") / "sprites" / "ghost-blue.png",
    Path("Resources") / "sprites" / "ghost-orange.png",
    Path("Resources") / "sprites" / "ghost-pink.png",
    Path("Resources") / "sprites" / "ghost-red.png",
    Path("Resources") / "sprites" / "ghost.gif",
    Path("Resources") / "sprites" / "Graphics" / "pixel-ghost-chase-24x24.png",
]

WALKABLE_TILES = []

for y, row in enumerate(MATRIX):
    for x, value in enumerate(row):
        if value == 1:
            WALKABLE_TILES.append((x, y))


TILE_SET = (448 / len(MATRIX[0]), 496 / len(MATRIX))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_group, walls_group):
        pygame.sprite.Sprite.__init__(self)
        self.blue_ghost = pygame.image.load(SPRITES_PATH[0])
        self.orange_ghost = pygame.image.load(SPRITES_PATH[1])
        self.pink_ghost = pygame.image.load(SPRITES_PATH[2])
        self.red_ghost = pygame.image.load(SPRITES_PATH[3])
        self.scared_ghost = pygame.image.load(SPRITES_PATH[4])

        self.ghosts = [self.blue_ghost, self.orange_ghost, self.pink_ghost, self.red_ghost]
        self.enemy_pos = [(200, 221), (250, 221), (200, 235), (250,235)]

        self.image = self.blue_ghost
        self.rect = self.image.get_rect()
        self.hitbox = (8, 8)
        self.rect.size = self.hitbox

        self.speed_y = 0
        self.speed_x = 0
        self.speed = 75
        self.speed_scared = 50

        self.points = 175

        self.player_group = player_group
        self.walls_group = walls_group

        self.current_state = "inactive"

        self.path = []
        self.last_player_tile = 0
        self.current_player_tile = 0
        self.target_tile = None
        self.random_target = None

        self.time_not_following_player = 0
        self.time_until_follows_player = 10

        self.time_not_moving_random = 0
        self.time_until_moving_random = 10

        self.time_inactive = 0
        self.until_active_time = 0

        self.time_scared = 0
        self.time_scared_max = 5


    def state(self, delta, screen):
        match self.current_state:
            case "inactive":
                self.time_inactive += delta
                if self.time_inactive >= self.until_active_time:
                    self.time_inactive = 0
                    self.current_state = "moving"

            case "moving":
                self.time_not_following_player += delta
                self.move(delta, screen, "random")
                
                if self.time_not_following_player >= self.time_until_follows_player:
                    self.time_not_following_player = 0
                    self.time_until_follows_player = randint(5, 30)
                    self.current_state = "following_player"
            
            case "following_player":
                self.time_not_moving_random += delta
                self.move(delta, screen, "player")

                if self.time_not_moving_random >= self.time_until_moving_random:
                    self.time_not_moving_random = 0
                    self.time_until_moving_random = randint(5, 30)
                    self.current_state = "moving"  
            
            case "scared":
                self.time_scared += delta
                self.image = self.scared_ghost
                self.move(delta, screen, "random")
                self.speed = self.speed_scared

                if self.time_scared >= self.time_scared_max:
                    self.time_scared = 0
                    self.current_state = "moving"
                    self.speed = 75
                    self.image = self.ghosts[self.enemies_list.index(self)]
        

    def spawn(self, index, enemy_group, enemies_list):
        self.enemies_list = enemies_list
        self.image = self.ghosts[index]
        self.rect.center = self.enemy_pos[index]

        self.add(enemy_group)
        enemies_list.append(self)
    

    def set_target(self, target: str="random"):
        """
        Args:
        target: "player"|"random"
        """

        enemy_tile_x = int(self.rect.centerx // TILE_SET[0])
        enemy_tile_y = int(self.rect.centery // TILE_SET[1])

        target_tile_x = 0
        target_tile_y = 0

        MAP_WIDTH = len(MATRIX[0]) #fix para poder meterme por el tunel

        match target:
            case "player":
                target_tile_x = int(
                    self.player_group.sprites()[0].rect.centerx // TILE_SET[0]
                )
                target_tile_y = int(
                    self.player_group.sprites()[0].rect.centery // TILE_SET[1]
                )

                new_player_tile = (target_tile_x, target_tile_y)

                if new_player_tile != self.current_player_tile:
                    self.last_player_tile = self.current_player_tile
                    self.current_player_tile = new_player_tile
        

            case "random":
                if self.random_target is None:
                    self.random_target = WALKABLE_TILES[randint(0, len(WALKABLE_TILES) - 1)]
                
                target_tile_x, target_tile_y = self.random_target
        
        enemy_tile_x %= MAP_WIDTH
        target_tile_x %= MAP_WIDTH

        return (enemy_tile_x, enemy_tile_y), (target_tile_x, target_tile_y)


    def make_path(self, enemy_pos: tuple, target: tuple):
        #creo grid. un start y un end, instancio el algoritmo y hago el path
        grid = Grid(matrix=MATRIX)

        start = grid.node(enemy_pos[0], enemy_pos[1])
        #verificacion de que el jugador sigue adentro del grid
        end = grid.node(target[0], target[1])

        finder = AStar(diagonal_movement=DiagonalMovement.only_when_no_obstacle)

        self.path, runs = finder.find_path(start, end, grid)


    def check_collisions(self, delta):
        self.rect.centerx += self.speed_x * delta

        for collision in self.walls_group:
            if self.rect.colliderect(collision.rect):
                if self.speed_x > 0:
                    self.rect.right = collision.rect.left
                elif self.speed_x < 0:
                    self.rect.left = collision.rect.right
        
        self.rect.centery += self.speed_y * delta

        for collision in self.walls_group:
            if self.rect.colliderect(collision.rect):
                if self.speed_y > 0:
                    self.rect.bottom = collision.rect.top
                elif self.speed_y < 0:
                    self.rect.top = collision.rect.bottom


    def move(self, delta, screen, target = "random"):
        """
        Args:
        target: "player"|"random"
        """

        enemy_tiles, target_tiles = self.set_target(target)

        if target_tiles != self.target_tile:
            self.target_tile = target_tiles
            self.make_path(enemy_tiles, target_tiles)

        if len(self.path) > 1:
            #si queda camino hago que siga al jugador
            target_tile_x, target_tile_y = self.path[1]

            #convierto las posiciones de tiles a pixeles
            target_x = target_tile_x * TILE_SET[0] + TILE_SET[0] // 2
            target_y = target_tile_y * TILE_SET[1] + TILE_SET[1] // 2

            direction = pygame.Vector2(
                target_x - self.rect.centerx,
                target_y - self.rect.centery
            )

            distance = direction.length()

            if distance > 0:
                direction.normalize_ip()

            self.speed_y = direction.y * self.speed
            self.speed_x = direction.x * self.speed


            if self.speed_x != 0 and self.speed_y != 0:
                self.speed_x *= 0.7071
                self.speed_y *= 0.7071
    
            self.check_collisions(delta)

            if distance < 2:
                self.rect.center = (target_x, target_y)
                self.path.pop(0)

                if len(self.path) <= 1:
                    self.random_target = None
                

            # for tile_x, tile_y in self.path:

            #     pygame.draw.circle(
            #         screen,
            #         "red",
            #         (
            #             tile_x * TILE_SET[0] + TILE_SET[0] // 2,
            #             tile_y * TILE_SET[1] + TILE_SET[1] // 2
            #         ),
            #         5
            #     )
