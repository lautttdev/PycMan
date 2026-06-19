import pygame
from pathlib import Path

SPRITES_LIFE = Path("Resources") / "sprites" / "pacman-0.png"
FONT = Path("Resources") / "fonts" / "ARCADE_R.TTF"
SIZE = (448, 496)

class GameUI:
    def __init__(self, player_lives: int, screen: pygame.surface.Surface, player_points: int):
        self.player_lives_sprites = pygame.image.load(SPRITES_LIFE)
        self.player_lives_sprites = pygame.transform.scale(self.player_lives_sprites, (20, 20))
        self.font = pygame.font.Font(FONT, 12)
        
        self.player_lives = player_lives
        self.player_points = player_points
        self.screen = screen
    

    def __update__(self):
        self.display_player_lives()
        self.display_points()


    def display_player_lives(self):
        for i in range(self.player_lives):
            life = self.player_lives_sprites
            self.screen.blit(life, (300 + i * 30, 25))
    

    def display_points(self):
        text = self.font.render(f"Points:{self.player_points}", False, "white")
        self.screen.blit(text, (30, 25))
