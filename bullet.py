import pygame

from consts import *


class Bullet(pygame.sprite.Sprite):

    def __init__(self, location, dir):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load('bullet.png')
        self.image = pygame.transform.scale(image, (int(WIDTH / 40), int(HEIGHT / 32)))
        self.location = location
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))
        self.speed = WIDTH / 100
        self.move_dir = dir.normalized() * self.speed

    def move(self):
        self.location += self.move_dir
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))

    def update(self):
        self.move()
        if self.rect.top > HEIGHT or self.rect.bottom < 0 or \
                self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()

