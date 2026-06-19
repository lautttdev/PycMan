import pygame

from pathlib import Path
from matrix import *

from menu import Menu

from player import Player
from enemy import Enemy
from eatables import Eatable
from eatable_killer import Eatable_Killer
from fruit import Fruit

from game_ui import GameUI
from sounds import Sounds

from random import randint
from time import sleep

#pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

#muerte de jugador

SIZE = WIDTH, HEIGHT = (448, 496)
SCREEN = pygame.display.set_mode(SIZE)
CLOCK = pygame.time.Clock()
dt = 0

FAVICON = pygame.image.load(Path("Resources") / "sprites" / "favicon.png")

is_menu_active = True
MENU = Menu(SCREEN)
SOUNDS = Sounds()

MAP_SPRITE = pygame.transform.scale(pygame.image.load(Path("Resources") / "sprites" / "board.png"), SIZE)

COL_SURFACE = pygame.surface.Surface(SIZE, pygame.SRCALPHA)
COL_SPRITE = Path("Resources")/ "sprites" / "col_fix.jpg"

COL_GROUP = pygame.sprite.Group()
PLAYER_GROUP = pygame.sprite.GroupSingle()
ENEMIES_GROUP = pygame.sprite.Group()
EATABLE_GROUP = pygame.sprite.Group()
EATABLE_KILLER_GROUP = pygame.sprite.Group()
TP_GROUP = pygame.sprite.Group()
FRUIT_GROUP  = pygame.sprite.Group()

enemies_list = []

in_process = True

player = Player(tp_group=TP_GROUP, walls_group=COL_GROUP, eatable_group=EATABLE_GROUP, 
                eatable_killer_group=EATABLE_KILLER_GROUP, enemy_group=ENEMIES_GROUP, fruit_group=FRUIT_GROUP)


class WallCollision(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(COL_SPRITE)
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect()


class TpCollision(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(COL_SPRITE)
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect()
        self.pos_tp = pygame.Vector2(0, 0)


def map_blit_and_collisions():
    for row in range(len(MATRIX)):
        for col in range(len(MATRIX[row])):

            if MATRIX[row][col] == 0:
                collision = WallCollision()

                rect = pygame.Rect(
                    col * TILE_SIZE[0] + 4,
                    row * TILE_SIZE[1] + 4,
                    TILE_SIZE[0] - 8,
                    TILE_SIZE[1] - 8
                )

                collision.rect = rect

                COL_GROUP.add(collision)
    
    left_tp = TpCollision()
    left_tp.rect.centerx, left_tp.rect.centery = -60, 230
    left_tp.pos_tp = pygame.Vector2(478, 230)
    left_tp.add(TP_GROUP)

    right_tp = TpCollision()
    right_tp.rect.centerx, right_tp.rect.centery = 508, 230
    right_tp.pos_tp = pygame.Vector2(-30, 230)
    right_tp.add(TP_GROUP)


def spawn_enemies():
    for i in range(4):
        enemy = Enemy(PLAYER_GROUP, COL_GROUP)
        enemy.until_active_time = randint(5, 30)
        if i == 0: enemy.until_active_time = 1
        enemy.spawn(i, ENEMIES_GROUP, enemies_list)


def spawn_eatables():
    for row in range(len(MATRIX_EATABLES)):
        for col in range(len(MATRIX_EATABLES[row])):

            if MATRIX_EATABLES[row][col] == 1:
                eatable = Eatable()

                rect = pygame.Rect(
                    col * TILE_SIZE[0] + 4,
                    row * TILE_SIZE[1] + 4,
                    TILE_SIZE[0] - 8,
                    TILE_SIZE[1] - 8
                )

                eatable.rect = rect

                EATABLE_GROUP.add(eatable)


def spawn_eatables_killers():
    for row in range(len(MATRIX_EATABLES_KILLERS)):
        for col in range(len(MATRIX_EATABLES_KILLERS[row])):

            if MATRIX_EATABLES_KILLERS[row][col] == 1:
                eatable_killer = Eatable_Killer()

                rect = pygame.Rect(
                    col * TILE_SIZE[0],
                    row * TILE_SIZE[1],
                    TILE_SIZE[0] - 8,
                    TILE_SIZE[1] - 8
                )

                eatable_killer.rect = rect

                EATABLE_KILLER_GROUP.add(eatable_killer)


fruit = Fruit(FRUIT_GROUP)

def spawn_fruit():
    fruit.spawn(dt)


def draw_all():
    SCREEN.blit(MAP_SPRITE, (0, 0))
    COL_GROUP.draw(COL_SURFACE) #dibujar en COL_SURFACE
    PLAYER_GROUP.draw(SCREEN)
    EATABLE_GROUP.draw(SCREEN)
    EATABLE_KILLER_GROUP.draw(SCREEN)
    ENEMIES_GROUP.draw(SCREEN)
    TP_GROUP.draw(COL_SURFACE)
    FRUIT_GROUP.draw(SCREEN)


Game_UI = GameUI(player.lives, SCREEN, player.total_points)

def display_ui():
    Game_UI.player_lives = player.lives
    Game_UI.player_points = player.total_points
    Game_UI.__update__()


def _ready():
    pygame.display.set_icon(FAVICON)
    SCREEN.blit(MAP_SPRITE, (0, 0))
    PLAYER_GROUP.add(player); player.rect.x, player.rect.y = player.spawn_pos
    map_blit_and_collisions()
    spawn_enemies()
    spawn_eatables()
    spawn_eatables_killers()

_ready()


def REBOOT_GAME():
    enemies_list.clear()
    ENEMIES_GROUP.empty()
    EATABLE_GROUP.empty()
    EATABLE_KILLER_GROUP.empty()
    FRUIT_GROUP.empty()
    
    spawn_enemies()
    spawn_eatables()
    spawn_eatables_killers()

    player.current_state = "init"


def REBOOT_ALL_GAME():
    enemies_list.clear()
    ENEMIES_GROUP.empty()
    EATABLE_GROUP.empty()
    EATABLE_KILLER_GROUP.empty()
    FRUIT_GROUP.empty()

    player.total_points = 0
    player.current_state = "died"


while in_process:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            in_process = False
    
    if not is_menu_active:
        if len(EATABLE_GROUP.sprites()) > 0:
            if player.current_state != "dying" and player.current_state != "died":
                draw_all()
                display_ui()
                player.state(dt)
                player.check_collisions(dt)

                for i in range(len(enemies_list)):
                    enemies_list[i].state(dt, SCREEN)

                for i in range(len(EATABLE_KILLER_GROUP)):
                    EATABLE_KILLER_GROUP.sprites()[i].animation(dt)
                
                spawn_fruit()

            elif player.current_state == "dying":
                draw_all()
                display_ui()
                player.state(dt)
            
            elif player.current_state == "died" and player.lives > 0:
                REBOOT_GAME()
            
            else:
                REBOOT_ALL_GAME()
                MENU.current_state = "init"
                MENU.state(dt, player, REBOOT_GAME)
                is_menu_active = True
                MENU.menu_active_check = True
            
        else:
            SOUNDS.play_sound("win")
            sleep(6)
            
            REBOOT_ALL_GAME()
            MENU.current_state = "init"
            MENU.state(dt, player, REBOOT_GAME)
            is_menu_active = True
            MENU.menu_active_check = True
        
    else:
        MENU.state(dt, player, REBOOT_GAME)
        is_menu_active = MENU.menu_active_check

    pygame.display.flip()
    dt = CLOCK.tick(60) / 1000


pygame.quit()