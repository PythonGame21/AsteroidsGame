import pygame
import keyboard
from consts import *
from vector import Vector


class Player(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        ship_image = pygame.image.load('ship.png')
        ship_f_image = pygame.image.load('ship_fire.png')
        self.or_image = pygame.transform.scale(ship_image,
                                               (int(WIDTH / 20), int(HEIGHT / 16)))
        self.or_image_f = pygame.transform.scale(ship_f_image,
                                                 (int(WIDTH / 20), int(HEIGHT / 16)))
        self.image = self.or_image
        self.location = Vector(WIDTH / 2, HEIGHT / 2)
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))
        self.add_speed = WIDTH / 10000
        self.max_speed = WIDTH / 100
        self.direction = Vector(0, -1)
        self.move_dir = Vector(0, 0)
        self.rot_angle = 8

    def move(self):
        if keyboard.is_pressed('w'):
            new_md = self.move_dir + self.direction * self.add_speed
            if new_md.length() > self.max_speed:
                new_md = new_md.normalized() * self.max_speed
            self.move_dir = new_md
        if keyboard.is_pressed('a'):
            self.rotate(-self.rot_angle)
        if keyboard.is_pressed('d'):
            self.rotate(self.rot_angle)
        self.move_dir *= 0.999
        self.location += self.move_dir

    def update_image(self):
        if keyboard.is_pressed('w'):
            self.image = pygame.transform.rotozoom(self.or_image_f, -self.direction.angle() - 90, 1)
        else:
            self.image = pygame.transform.rotozoom(self.or_image, -self.direction.angle() - 90, 1)
        self.rect = self.image.get_rect(center=(self.location.x, self.location.y))

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

    def relocate(self, x, y):
        self.location = Vector(x, y)

    def rotate(self, rot_angle):
        self.direction = self.direction.rotate(rot_angle)
