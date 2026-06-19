import pygame
from pathlib import Path
from sounds import Sounds

LOGO = Path("Resources") / "sprites" / "Pac-Man-Logo.jpg"
FONT = Path("Resources") / "fonts" / "PressStart2P.ttf"

SIZE = WIDTH, HEIGHT = (448, 496)
MAP_SPRITE = pygame.transform.scale(pygame.image.load(Path("Resources") / "sprites" / "board.png"), SIZE)

class Menu:
    def __init__(self, screen: pygame.surface.Surface):
        self.logo = pygame.image.load(LOGO)
        self.logo = pygame.transform.scale_by(self.logo, 0.09)
        self.logo.set_colorkey((255, 255, 255))

        self.anim_scale = 0

        self.font = pygame.font.Font(FONT, 12)
        self.text = None

        self.screen = screen

        self.font_timer = 0
        self.color = "white"

        self.menu_active_check = True
        self.current_state = "init"

        self.sounds = Sounds()
    

    def state(self, delta, player, reboot_func):
        match self.current_state:
            case "init":
                self.sounds.play_sound("start")
                self.anim(delta, player, reboot_func, "init")

            case "menu":
                self.menu(delta)
            
            case "closing":
                self.anim(delta, player, reboot_func, "closing")
    
    
    def anim(self, delta, player, reboot_func, state = "init"):
        match state:
            case "init":
                    if self.anim_scale <= 0.09:
                        self.screen.blit(MAP_SPRITE, (0, 0))
                        self.logo = pygame.transform.scale_by(pygame.image.load(LOGO), self.anim_scale)
                        self.logo.set_colorkey((255, 255, 255))
                        self.screen.blit(self.logo, (WIDTH / 7.6, HEIGHT / 4.0))
                        self.anim_scale += delta * 0.03
                        return
                    
                    self.current_state = "menu"
            
            case "closing":
                    if self.anim_scale >= 0.00:
                        self.screen.blit(MAP_SPRITE, (0, 0))
                        self.logo = pygame.transform.scale_by(pygame.image.load(LOGO), self.anim_scale)
                        self.logo.set_colorkey((255, 255, 255))
                        self.screen.blit(self.logo, (WIDTH / 7.6, HEIGHT / 4.0))
                        self.anim_scale -= delta * 0.06
                        return

                    self.menu_active_check = False
                    self.anim_scale = 0
                    player.lives = 3
                    reboot_func()



    def menu(self, delta):
        if self.menu_active_check == True:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                self.current_state = "closing"
                return
        
            self.text = self.font.render("Press Start or Space to start", False, self.color)
        
            self.font_timer += delta

            if self.font_timer >= 0.5 and self.color == "white":
                self.color = "yellow"
                self.font_timer = 0
                
            elif self.font_timer >= 0.5 and self.color == "yellow":
                self.color = "white"
                self.font_timer = 0
                

            self.screen.blit(self.logo, (WIDTH / 7.6, HEIGHT / 4.0))
            self.screen.blit(self.text, (WIDTH / 7.5, HEIGHT / 1.5))
        