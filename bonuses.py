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
        self.max_life_time = 8

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
        if time.time() - self.spawn_time > self.max_life_time - 2:
            self.update_image()
        if time.time() - self.spawn_time > self.max_life_time:
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

    def __getstate__(self) -> dict:
        state = {}
        state["location"] = self.location
        state["move_dir"] = self.move_dir
        state["life_time"] = time.time() - self.spawn_time
        return state

    def __setstate__(self, state: dict):
        self.__init__(state["location"])
        self.move_dir = state["move_dir"]
        self.spawn_time = time.time() - state["life_time"]


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
        super().__init__(location)


class Invisibility(Bonus):
    def __init__(self, location):
        self.bonus_image = pygame.image.load(path.join(img_dir, "disap.png"))
        super().__init__(location)




class ActiveBonus:
    def __init__(self):
        self.activation_time = 0
        self.is_active = False
        self.active_time = 0

    def activate(self):
        self.activation_time = time.time()
        self.is_active = True

    def update(self):
        self.active_time = time.time() - self.activation_time
        if self.active_time > self.validity_period:
            self.is_active = False

    def __getstate__(self) -> dict:
        state = {}
        state["active_time"] = self.active_time
        state["is_active"] = self.is_active
        return state

    def __setstate__(self, state: dict):
        self.__init__()
        self.is_active = state["is_active"]
        self.activation_time = time.time() - state["active_time"]


class ActShield(ActiveBonus):
    def __init__(self):
        shd_img = pygame.image.load(path.join(img_dir, "shild.png"))
        self.image = pygame.transform.scale(shd_img, (40, 40))
        self.validity_period = 8
        super().__init__()


class ActHealth(ActiveBonus):
    def __init__(self):
        self.image = None
        self.validity_period = -1
        super().__init__()

class ActEnergy(ActiveBonus):
    def __init__(self):
        eng_img = pygame.image.load(path.join(img_dir, "enrgy.png"))
        self.image = pygame.transform.scale(eng_img, (40, 40))
        self.validity_period = 5
        super().__init__()


class ActScoreX2(ActiveBonus):
    def __init__(self):
        sx2_img = pygame.image.load(path.join(img_dir, "scrx2.png"))
        self.image = pygame.transform.scale(sx2_img, (40, 40))
        self.validity_period = 10
        super().__init__()

class ActInvisibility(ActiveBonus):
    def __init__(self):
        inv_img = pygame.image.load(path.join(img_dir, "disap.png"))
        self.image = pygame.transform.scale(inv_img, (40, 40))
        self.validity_period = 8
        super().__init__()

