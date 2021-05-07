import pygame
import keyboard
import random
import time

from consts import *
from player import Player
from asteroid import BigAsteroid, SmallAsteroid
from vector import Vector
from enemy import Enemy


class Game:
    def __init__(self):
        self.asteroids = pygame.sprite.Group()
        self.enemy = pygame.sprite.Group()
        self.all_bullets = pygame.sprite.Group()
        self.player = Player()
        self.player_sprite = pygame.sprite.Group(self.player)
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

            player_astr_hits = pygame.sprite.spritecollide(self.player, self.asteroids,
                                                           False, pygame.sprite.collide_circle)
            player_enemy_hits = pygame.sprite.spritecollide(self.player, Enemy.bullets,
                                                            True, pygame.sprite.collide_circle)
            astr_bul_hits = pygame.sprite.groupcollide(self.asteroids, self.all_bullets,
                                                       True, True, pygame.sprite.collide_circle)
            pygame.sprite.groupcollide(self.asteroids, self.all_bullets,
                                       True, True, pygame.sprite.collide_circle)
            enemy_hits = pygame.sprite.groupcollide(self.enemy, self.asteroids,
                                       False, False, pygame.sprite.collide_circle)
            pygame.sprite.groupcollide(self.enemy, self.player.bullets,
                                       True, True, pygame.sprite.collide_circle)

            for hitted_en in enemy_hits:
                if not hitted_en.is_undead:
                    hitted_en.kill()

            for hitted_astr in astr_bul_hits:
                if type(hitted_astr) is BigAsteroid:
                    location = hitted_astr.location
                    for i in range(2):
                        self.asteroids.add(SmallAsteroid(location, Vector.get_random_direct()))

            if player_astr_hits or player_enemy_hits or self.player.hs_dead_count >= 500:
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

            self.all_bullets.add(self.player.bullets)
            self.all_bullets.add(Enemy.bullets)
            self.all_bullets.update()
            self.all_bullets.draw(screen)

            self.asteroids.update()
            self.asteroids.draw(screen)

            if (random.randrange(0, 200) == 0):
                self.enemy.add(Enemy())

            self.enemy.update(self.player.location)
            self.enemy.draw(screen)

            self.player_sprite.update()
            self.player_sprite.draw(screen)

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
