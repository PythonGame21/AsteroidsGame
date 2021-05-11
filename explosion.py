import pygame
import time

from consts import *
from os import path

gif_dir = path.join(path.dirname(__file__), 'exp_gif')
gif_pl_dir = path.join(path.dirname(__file__), 'pl_exp_gif')


class Explosion(pygame.sprite.Sprite):
    explosion_anim = {'bg': [], 'sm': [], 'md': [], 'player': []}
    for i in range(9):
        filename = 'regularExplosion0{}.png'.format(i)
        img = pygame.image.load(path.join(gif_dir, filename))
        img.set_colorkey(BLACK)
        img_bg = pygame.transform.scale(img, (75, 75))
        explosion_anim['bg'].append(img_bg)
        img_md = pygame.transform.scale(img, (50, 50))
        explosion_anim['md'].append(img_md)
        img_sm = pygame.transform.scale(img, (20, 20))
        explosion_anim['sm'].append(img_sm)
        filename = 'sonicExplosion0{}.png'.format(i)
        img = pygame.image.load(path.join(gif_pl_dir, filename))
        img.set_colorkey(BLACK)
        explosion_anim['player'].append(img)

    def __init__(self, loc, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = Explosion.explosion_anim[self.size][0]
        self.location = loc
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))
        self.frame = 0
        self.last_update = time.time()
        self.frame_rate = 0.1

    def update(self):
        now = time.time()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(Explosion.explosion_anim[self.size]):
                self.kill()
            else:
                self.image = Explosion.explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect = self.image.get_rect(center=(self.location.x, self.location.y))