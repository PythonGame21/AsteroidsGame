import pygame
import time

from vector import Vector
from consts import *
from os import path

img_dir = path.join(path.dirname(__file__), 'img')


class Bullet(pygame.sprite.Sprite):
    def __init__(self, location, dir):
        pygame.sprite.Sprite.__init__(self)
        self.location = location
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))
        self.move_dir = dir.normalized() * self.speed
        self.spawn_time = time.time()

    def move(self):
        self.location += self.move_dir
        self.rect.x = self.location.x - self.rect.width / 2
        self.rect.y = self.location.y - self.rect.height / 2

    def update(self):
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

    def __getstate__(self) -> dict:
        state = {}
        state["location"] = self.location
        state["speed"] = self.speed
        state["move_dir"] = self.move_dir
        state["life_time"] = time.time() - self.spawn_time
        return state

    def __setstate__(self, state: dict):
        self.__init__(state["location"], state["move_dir"])
        self.speed = state["speed"]
        self.move_dir = state["move_dir"]
        self.spawn_time = time.time() - state["life_time"]


class EnemyBullet(Bullet):
    def __init__(self, location, dir):
        bul_image = pygame.image.load(path.join(img_dir, "enemybullet.png"))
        self.image = pygame.transform.scale(bul_image, (10, 10))

        self.speed = 300 / FPS

        self.life_time = (min(HEIGHT, WIDTH) - 100) / 400

        super().__init__(location, dir)


class PlayerBullet(Bullet):
    def __init__(self, location, dir):
        bul_image = pygame.image.load(path.join(img_dir, "bullet.png"))
        self.image = pygame.transform.scale(bul_image, (10, 10))

        self.speed = 800 / FPS

        self.life_time = (min(HEIGHT, WIDTH) - 100) / 800

        super().__init__(location, dir)
