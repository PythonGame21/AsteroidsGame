import pygame
import time
import random

from vector import Vector
from consts import *
from os import path

img_dir = path.join(path.dirname(__file__), 'img')


class Bonus(pygame.sprite.Sprite):
    def __init__(self, location):
        pygame.sprite.Sprite.__init__(self)
        self.location = location
        self.image = pygame.transform.scale(self.bonus_image, (35, 35))
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))
        self.radius = int(self.rect.width / 2)
        self.move_dir = Vector.get_random_direct() * random.randrange(1, 5) / 5
        self.spawn_time = time.time()
        self.life_time = 8

        self.is_invisible = False

    def move(self):
        self.location += self.move_dir
        self.rect.x = self.location.x - self.rect.width / 2
        self.rect.y = self.location.y - self.rect.height / 2

    def update_image(self):
        if self.is_invisible:
            self.image = pygame.Surface((35, 35))
            self.image.set_colorkey(BLACK)
            self.is_invisible = False
        else:
            self.image = pygame.transform.scale(self.bonus_image, (35, 35))
            self.is_invisible = True

    def update(self):
        if time.time() - self.spawn_time > self.life_time - 2:
            self.update_image()
        if time.time() - self.spawn_time > self.life_time:
            self.kill()
        if self.rect.top > HEIGHT:
            x = self.rect.x + self.rect.width / 2
            y = -self.rect.height / 2
            self.relocate(x, y)
        if self.rect.bottom < 0:
            x = self.rect.x + self.rect.width / 2
            y = HEIGHT + self.rect.height / 2
            self.relocate(x, y)
        if self.rect.left > WIDTH:
            x = -self.rect.width / 2
            y = self.rect.y + self.rect.height / 2
            self.relocate(x, y)
        if self.rect.right < 0:
            x = WIDTH + self.rect.width / 2
            y = self.rect.y + self.rect.height / 2
            self.relocate(x, y)
        self.move()

    def relocate(self, x, y):
        self.location = Vector(x, y)


class Shield(Bonus):
    def __init__(self, location):
        self.bonus_image = pygame.image.load(path.join(img_dir, "shild.png"))
        super().__init__(location)


class Health(Bonus):
    def __init__(self, location):
        self.bonus_image = pygame.image.load(path.join(img_dir, "healt.png"))
        super().__init__(location)


class Energy(Bonus):
    def __init__(self, location):
        self.bonus_image = pygame.image.load(path.join(img_dir, "enrgy.png"))
        super().__init__(location)


class ScoreX2(Bonus):
    def __init__(self, location):
        self.bonus_image = pygame.image.load(path.join(img_dir, "scrx2.png"))
        super().__init__(location)\


class Invisibility(Bonus):
    def __init__(self, location):
        self.bonus_image = pygame.image.load(path.join(img_dir, "disap.png"))
        super().__init__(location)


class ActiveBonus:
    def __init__(self, validity_period, img):
        self.image = img
        self.activation_time = 0
        self.validity_period = validity_period
        self.is_active = False
        self.active_time = 0

    def activate(self):
        self.activation_time = time.time()
        self.is_active = True

    def update(self):
        self.activ_time = time.time() - self.activation_time
        if self.activ_time > self.validity_period:
            self.is_active = False
