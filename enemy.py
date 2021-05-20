import pygame
import time
import random

from consts import *
from vector import Vector
from bullet import EnemyBullet
from os import path

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')


class Enemy(pygame.sprite.Sprite):
    bullets = pygame.sprite.Group()
    pygame.mixer.init()
    shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'enem.mp3'))

    def __init__(self, x, y, dir):
        pygame.sprite.Sprite.__init__(self)

        self.location = Vector(x, y)
        self.direction = dir
        self.move_dir = self.direction * random.randrange(75, 125) / FPS

        ship_image = pygame.image.load(path.join(img_dir, "enemy.png"))
        self.or_image = pygame.transform.scale(ship_image, (50, 50))
        self.image = pygame.transform.rotozoom(self.or_image, -self.direction.angle() - 90, 1)

        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))
        self.radius = int(self.rect.width * 0.8 / 2)

        self.cooldown = 0.4
        self.last_shoot_time = 0

        self.is_undead = True
        self.undead_time = 1
        self.life_start_time = time.time()

    def shoot(self, player_loc):
        Enemy.bullets.add(EnemyBullet(self.location, player_loc - self.location))
        self.last_shoot_time = time.time()
        Enemy.shoot_sound.play()

    def move(self):
        self.location += self.move_dir

    def update(self, player_loc):
        if (self.rect.top > HEIGHT or self.rect.bottom < 0 or self.rect.left > WIDTH or self.rect.right < 0) and \
                not self.is_undead:
            self.kill()
        if time.time() - self.life_start_time > self.undead_time:
            self.is_undead = False
        self.move()
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))
        if time.time() - self.last_shoot_time > self.cooldown:
            self.shoot(player_loc)

    @staticmethod
    def get_random_position_out_of_screen():
        is_x_outofscreen = random.randrange(0, 2) == 1
        x = random.randrange(200, WIDTH - 200)
        y = random.randrange(200, HEIGHT - 200)
        if is_x_outofscreen:
            x = random.randrange(-20, WIDTH + 21, WIDTH + 40)
            if x < 0:
                direction = Vector(random.randrange(0, 100), random.randrange(-20, 20)).normalized()
            else:
                direction = Vector(random.randrange(-100, 0), random.randrange(-20, 20)).normalized()
        else:
            y = random.randrange(-20, HEIGHT + 21, HEIGHT + 40)
            if y < 0:
                direction = Vector(random.randrange(-20, 20), random.randrange(0, 100)).normalized()
            else:
                direction = Vector(random.randrange(-20, 20), random.randrange(-100, 0)).normalized()
        return x, y, direction.normalized()

    def __getstate__(self) -> dict:
        state = {}
        state["location"] = self.location
        state["direction"] = self.direction
        state["move_dir"] = self.move_dir
        state["all_bullets"] = Enemy.bullets
        state["cooldawn_time"] = time.time() - self.last_shoot_time
        return state

    def __setstate__(self, state: dict):
        loc_vec = state["location"]
        self.__init__(loc_vec.x, loc_vec.y, state["direction"])
        self.move_dir = state["move_dir"]
        self.last_shoot_time = time.time() - state["cooldawn_time"]
        Enemy.bullets = state["all_bullets"]

