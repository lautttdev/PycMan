import pygame
from pathlib import Path
from sounds import Sounds

SPRITES_PATH = (Path("Resources") / "sprites" / "pacman-0.png",
                Path("Resources") / "sprites" / "pacman-1.png")


class Player(pygame.sprite.Sprite):
    def __init__(self, walls_group: pygame.sprite.Group, tp_group: pygame.sprite.Group, eatable_group : pygame.sprite.Group, 
                 eatable_killer_group: pygame.sprite.Group, enemy_group: pygame.sprite.Group, fruit_group: pygame.sprite.Group):
        pygame.sprite.Sprite.__init__(self)
        self.keys = 0

        self.walls_group = walls_group 
        self.tp_group = tp_group
        self.enemy_group = enemy_group
        self.eatable_group = eatable_group
        self.eatable_killer_group = eatable_killer_group
        self.fruit_group = fruit_group

        self.total_points = 0

        self.sprites_idle = [
            pygame.image.load(SPRITES_PATH[0]),
            pygame.image.load(SPRITES_PATH[1])
        ]

        self.image = self.sprites_idle[0]
        self.image.set_alpha(0)

        self.max_index = 0
        self.current_index = self.max_index
        self.current_state = "init"

        self.speed_x = 0
        self.speed_y = 0
        self.speed = 100
        self.last_movement_x = self.speed
        self.last_movement_y = 0

        self.flip_h = False
        self.flip_v = 0

        self.timer = 0

        self.spawn_pos = (215, 270)
        self.rect = self.image.get_rect()
        self.hitbox = (16, 16)
        self.rect.size = self.hitbox

        self.max_lives = 3
        self.lives = 3
        self.invencible = False

        self.sounds = Sounds()
    
    
    def update_sprite(self, sprite, delta):
        self.timer += delta
        if self.timer >= 0.15:
            self.max_index = len(sprite) - 1

            if self.current_index < self.max_index:
                self.current_index += 1
            else:
                self.current_index = 0
            
            self.image = pygame.transform.rotate(pygame.transform.flip(sprite[self.current_index], self.flip_h, False), self.flip_v)
            self.timer = 0
    

    def state(self, delta):
        match self.current_state:
            case "init":
                self.rect.x, self.rect.y = self.spawn_pos
                self.alpha_animation(delta)
                self.invencible = False
                self.sounds.play_sound("waka")

            case "idle":
                self.update_sprite(self.sprites_idle, delta)
                self.move(delta)

            case "dying":
                self.alpha_animation(delta, "dying")
                self.sounds.play_sound("die")
                self.invencible = True
            
            case "died":
                pass


    def move(self, delta):
        self.keys = pygame.key.get_pressed()
        self.sprite_direction()

        self.speed_x = self.last_movement_x
        self.speed_y = self.last_movement_y
    

        if self.keys[pygame.K_d] or self.keys[pygame.K_RIGHT]:
            self.speed_x = self.speed; 
            self.last_movement_x = self.speed; self.last_movement_y = 0
        elif self.keys[pygame.K_a] or self.keys[pygame.K_LEFT]:
            self.speed_x = -self.speed
            self.last_movement_x = -self.speed; self.last_movement_y = 0
        if self.keys[pygame.K_w] or self.keys[pygame.K_UP]:
            self.speed_y = -self.speed
            self.last_movement_x = 0; self.last_movement_y = -self.speed
        elif self.keys[pygame.K_s] or self.keys[pygame.K_DOWN]:
            self.speed_y = self.speed
            self.last_movement_x = 0; self.last_movement_y = self.speed
            
        if self.speed_x != 0 and self.speed_y != 0:
            self.speed_x *= 0.7071
            self.speed_y *= 0.7071
    
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
    

    def sprite_direction(self):
        if self.keys[pygame.K_d] or self.keys[pygame.K_RIGHT]:
            self.flip_h = False; self.flip_v = 0
        elif self.keys[pygame.K_a] or self.keys[pygame.K_LEFT]:
            self.flip_h = True; self.flip_v = 0
        elif self.keys[pygame.K_w] or self.keys[pygame.K_UP]:
            self.flip_h = False; self.flip_v = 0; self.flip_v = 90
        elif self.keys[pygame.K_s] or self.keys[pygame.K_DOWN]:
            self.flip_h = False; self.flip_v = 0; self.flip_v = -90


    def alpha_animation(self, delta, state="init"):
        """
        State = "init, dying"
        """
        match state:
            case "init":
                self.image.set_alpha(self.image.get_alpha() + 5)
                if self.image.get_alpha() >= 254:
                    self.current_state = "idle"
            
            case "dying":
                self.image.set_alpha(self.image.get_alpha() - 10)
                if self.image.get_alpha() <= 1:
                    self.current_state = "died"

    
    def check_collisions(self, delta):
        for col in self.tp_group:
            if self.rect.colliderect(col.rect):
                self.rect.center = col.pos_tp
        
        for eatable in self.eatable_group:
            if self.rect.colliderect(eatable.rect):
                self.total_points += eatable.points
                self.eatable_group.remove(eatable)
        
        for eatable_killer in self.eatable_killer_group:
            if self.rect.colliderect(eatable_killer.rect):
                self.total_points += eatable_killer.points
                self.eatable_killer_group.remove(eatable_killer)
                self.sounds.play_sound("waka")

                for enemy in self.enemy_group:
                    if enemy.current_state != "inactive":
                        self.total_points += enemy.points
                        enemy.current_state = "scared"
        
        for fruit in self.fruit_group:
            if self.rect.colliderect(fruit.rect):
                self.total_points += fruit.points
                self.fruit_group.remove(fruit)
                self.sounds.play_sound("glup")
        
        for enemy in self.enemy_group:
            if self.rect.colliderect(enemy.rect):
                if enemy.current_state == "scared":
                    enemy.current_state = "inactive"
                    enemy.rect.center = enemy.enemy_pos[self.enemy_group.sprites().index(enemy)]
                    enemy.image = enemy.ghosts[self.enemy_group.sprites().index(enemy)]
                    self.sounds.play_sound("glup")
                    return
            
                if self.lives >= 0 and not self.invencible:
                    self.lives -= 1
                    self.current_state = "dying"
                    return
                
                    
        