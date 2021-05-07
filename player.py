import pygame
import keyboard
import time
import random

from consts import *
from vector import Vector
from bullet import Bullet
from os import path


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        img_dir = path.join(path.dirname(__file__), 'img')
        ship_image = pygame.image.load(path.join(img_dir, "ship.png"))
        ship_f_image = pygame.image.load(path.join(img_dir, "shipf.png"))
        self.or_image = pygame.transform.scale(ship_image, (50, 50))
        self.or_image_f = pygame.transform.scale(ship_f_image, (50, 50))
        self.image = self.or_image

        self.location = Vector(WIDTH / 2, HEIGHT / 2)
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))
        self.radius = int(self.rect.width * 0.85 / 2)

        self.add_speed = 18
        self.max_speed = 300
        self.resist_coef = 0.75

        self.direction = Vector(0, -1)
        self.move_dir = Vector(0, 0)
        self.rot_angle = 480

        self.cooldown = 0.2
        self.last_shoot_time = -self.cooldown

        self.hs_cooldown = 1.5
        self.last_hs_time = -self.hs_cooldown
        self.hs_dead_count = 0

        self.bullets = pygame.sprite.Group()

        self.life_count = 3
        self.is_undead = True
        self.undead_time = 2
        self.life_start_time = time.time()
        self.is_invisible = False

    def move(self):
        if keyboard.is_pressed('w'):
            new_md = self.move_dir + self.direction * self.add_speed / FPS
            if new_md.length() > self.max_speed / FPS:
                new_md = new_md.normalized() * self.max_speed / FPS
            self.move_dir = new_md
        if keyboard.is_pressed('a'):
            self.rotate(-self.rot_angle)
        if keyboard.is_pressed('d'):
            self.rotate(self.rot_angle)
        self.move_dir *= (1 - self.resist_coef / FPS)
        self.location += self.move_dir


    def update_image(self):
        if keyboard.is_pressed('w'):
            self.image = pygame.transform.rotozoom(self.or_image_f, -self.direction.angle() - 90, 1)
        else:
            self.image = pygame.transform.rotozoom(self.or_image, -self.direction.angle() - 90, 1)
        if self.is_undead:
            if self.is_invisible:
                self.image = pygame.Surface((50, 50))
                self.image.set_colorkey(BLACK)
                self.is_invisible = False
            else:
                self.is_invisible = True


    def update(self):
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
        self.update_image()
        self.move()
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))
        if time.time() - self.life_start_time > self.undead_time:
            self.is_undead = False
        if keyboard.is_pressed('space') and \
                time.time() - self.last_shoot_time > self.cooldown:
            self.shoot()
        if keyboard.is_pressed('x') and \
                time.time() - self.last_hs_time > self.hs_cooldown:
            self.hyper_scape()
        if self.hs_dead_count > 0:
            self.hs_dead_count -= 1

    def relocate(self, x, y):
        self.location = Vector(x, y)

    def rotate(self, rot_angle):
        self.direction = self.direction.rotate(rot_angle / FPS)

    def shoot(self):
        self.bullets.add(Bullet(self.location, self.direction))
        self.last_shoot_time = time.time()

    def hit(self):
        self.location = Vector(WIDTH / 2, HEIGHT / 2)

        self.direction = Vector(0, -1)
        self.move_dir = Vector(0, 0)

        self.is_undead = True
        self.life_count -= 1
        self.life_start_time = time.time()
        self.hs_dead_count = 0

    def hyper_scape(self):
        if self.is_undead:
            return
        new_x = (self.location.x + random.randrange(200, 500)) % WIDTH
        new_y = (self.location.y + random.randrange(200, 400)) % HEIGHT
        self.location = Vector(new_x, new_y)
        self.move_dir = Vector(0, 0)
        self.last_hs_time = time.time()
        self.hs_dead_count += 200

