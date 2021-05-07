import pygame
import keyboard
import random
import time

from consts import *
from player import Player
from asteroid import BigAsteroid, SmallAsteroid
from vector import Vector
from os import path


class Game:
    def __init__(self):
        img_dir = path.join(path.dirname(__file__), 'img')

        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.asteroid_spawn_cooldawn = 10
        self.last_astr_spawn_time = -self.asteroid_spawn_cooldawn

    def run(self):
        pygame.init()
        pygame.mixer.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Asteroids")
        clock = pygame.time.Clock()

        running = True
        while running:
            screen.fill(SPACE)

            player_hits = pygame.sprite.spritecollide(self.player, self.asteroids, False, pygame.sprite.collide_circle)
            bul_hits = pygame.sprite.groupcollide(self.asteroids, self.player.bullets, True, True, pygame.sprite.collide_circle)

            for hitted in bul_hits:
                if type(hitted) is BigAsteroid:
                    location = hitted.location
                    for i in range(2):
                        self.asteroids.add(SmallAsteroid(location, Vector.get_random_direct()))

            if player_hits or self.player.hs_dead_count >= 500:
                if not self.player.is_undead:
                    if self.player.life_count == 0:
                        running = False
                    else:
                        self.player.hit()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or keyboard.is_pressed('esc'):
                    running = False
            if time.time() - self.last_astr_spawn_time > self.asteroid_spawn_cooldawn:
                self.spawn_asteroids()
                self.last_astr_spawn_time = time.time()

            self.player.bullets.update()
            self.player.bullets.draw(screen)

            self.asteroids.update()
            self.asteroids.draw(screen)

            self.all_sprites.update()
            self.all_sprites.draw(screen)

            pygame.display.flip()

            clock.tick(FPS)

        pygame.quit()

    def spawn_asteroids(self):
        count = 6
        asteroids = pygame.sprite.Group()
        for i in range(count):
            is_small = random.randrange(0, 2) == 1
            is_x_outofscreen = random.randrange(0, 2) == 1
            x = random.randrange(0, WIDTH)
            y = random.randrange(0, HEIGHT)
            if is_small:
                if is_x_outofscreen:
                    x = -45
                else:
                    y = -45
                asteroids.add(SmallAsteroid(Vector(x, y), Vector.get_random_direct()))
            else:
                if is_x_outofscreen:
                    x = -90
                else:
                    y = -90
                asteroids.add(BigAsteroid(Vector(x, y), Vector.get_random_direct()))
        self.asteroids.add(asteroids)
