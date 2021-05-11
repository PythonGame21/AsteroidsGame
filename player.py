import pygame
import keyboard
import time
import random

from consts import *
from vector import Vector
from bullet import PlayerBullet
from os import path
from bonuses import ActiveBonus

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        ship_image = pygame.image.load(path.join(img_dir, "ship.png"))
        ship_f_image = pygame.image.load(path.join(img_dir, "shipf.png"))
        ship_sh_image = pygame.image.load(path.join(img_dir, "shipsh.png"))
        ship_f_sh_image = pygame.image.load(path.join(img_dir, "shipfsh.png"))
        ship_dis = pygame.image.load(path.join(img_dir, "dissh.png"))
        self.or_image = pygame.transform.scale(ship_image, (50, 50))
        self.or_image_f = pygame.transform.scale(ship_f_image, (50, 50))
        self.or_sh_image = pygame.transform.scale(ship_sh_image, (50, 50))
        self.or_sh_image_f = pygame.transform.scale(ship_f_sh_image, (50, 50))
        self.or_sh_dis = pygame.transform.scale(ship_dis, (50, 50))
        self.image = self.or_image

        pygame.mixer.init()
        self.shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
        self.dmg_sound = pygame.mixer.Sound(path.join(snd_dir, 'damg.mp3'))
        self.hs_sound = pygame.mixer.Sound(path.join(snd_dir, 'hs.mp3'))

        self.location = Vector(WIDTH / 2, HEIGHT / 2)
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))
        self.radius = int(self.rect.width * 0.85 / 2)

        self.add_speed = 18
        self.max_speed = 300
        self.resist_coef = 0.75

        self.direction = Vector(0, -1)
        self.move_dir = Vector(0, 0)
        self.rot_angle = 300

        self.cooldown = 0.2
        self.last_shoot_time = -self.cooldown

        self.hs_cooldown = 1.5
        self.last_hs_time = -self.hs_cooldown
        self.hs_dead_count = 0

        self.active_bonuses = {'Shield': ActiveBonus(10),
                               'Health': ActiveBonus(-1),
                               'Energy': ActiveBonus(8),
                               'ScoreX2': ActiveBonus(10),
                               'Invisibility': ActiveBonus(12)}

        self.bullets = pygame.sprite.Group()

        self.life_scale = 1000
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
        if not self.active_bonuses['Invisibility'].is_active:
            self.image = pygame.transform.rotozoom(self.or_sh_image, -self.direction.angle() - 90, 1)
            if keyboard.is_pressed('w'):
                if self.active_bonuses['Shield'].is_active:
                    self.image = pygame.transform.rotozoom(self.or_sh_image_f, -self.direction.angle() - 90, 1)
                else:
                    self.image = pygame.transform.rotozoom(self.or_image_f, -self.direction.angle() - 90, 1)
            else:
                if self.active_bonuses['Shield'].is_active:
                    self.image = pygame.transform.rotozoom(self.or_sh_image, -self.direction.angle() - 90, 1)
                else:
                    self.image = pygame.transform.rotozoom(self.or_image, -self.direction.angle() - 90, 1)
        else:
            self.image = pygame.transform.rotozoom(self.or_sh_dis, -self.direction.angle() - 90, 1)
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
        self.update_bonuses()
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
        self.bullets.add(PlayerBullet(self.location, self.direction))
        self.shoot_sound.play()
        self.last_shoot_time = time.time()

    def hit(self, dmg):
        if self.active_bonuses['Shield'].is_active:
            return
        self.life_scale -= dmg
        self.dmg_sound.play()
        self.is_undead = True
        self.life_start_time = time.time()
        self.hs_dead_count = 0

    def hyper_scape(self):
        if self.is_undead:
            return
        self.hs_sound.play()
        new_x = (self.location.x + random.randrange(200, 500)) % WIDTH
        new_y = (self.location.y + random.randrange(200, 400)) % HEIGHT
        self.location = Vector(new_x, new_y)
        self.move_dir = Vector(0, 0)
        self.last_hs_time = time.time()
        self.hs_dead_count += 200

    def update_bonuses(self):
        if self.active_bonuses['Health'].is_active:
            self.life_scale += 400
            if self.life_scale > 1000:
                self.life_scale = 1000
        if self.active_bonuses['Energy'].is_active:
            self.cooldown = 0.1
        else:
            self.cooldown = 0.2
        for bonus in self.active_bonuses.values():
            bonus.update()
