import pygame
import keyboard
import random
import time

from consts import *
from player import Player
from asteroid import BigAsteroid, SmallAsteroid
from vector import Vector
from enemy import Enemy
from bullet import PlayerBullet
from os import path
from explosion import Explosion
from bonuses import Shield, ScoreX2, Health, Energy, Invisibility

font_name = pygame.font.match_font('arial')
img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')


class Game:
    def __init__(self):
        self.asteroids = pygame.sprite.Group()
        self.enemy = pygame.sprite.Group()
        self.all_bullets = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()
        self.player = Player()
        self.player_sprite = pygame.sprite.Group(self.player)
        self.explosions = pygame.sprite.Group()
        self.asteroid_spawn_cooldawn = 3
        self.enemy_count = 500
        self.last_astr_spawn_time = -self.asteroid_spawn_cooldawn
        self.score = 0
        self.score_multipl = 1

        self.is_player_alive = True
        self.dead_time = 2
        self.dead_start_time = 0

        self.shd_img = pygame.image.load(path.join(img_dir, "shild.png"))
        self.eng_img = pygame.image.load(path.join(img_dir, "enrgy.png"))
        self.sx2_img = pygame.image.load(path.join(img_dir, "scrx2.png"))
        self.inv_img = pygame.image.load(path.join(img_dir, "disap.png"))
        self.shd_img = pygame.transform.scale(self.shd_img, (40, 40))
        self.eng_img = pygame.transform.scale(self.eng_img, (40, 40))
        self.sx2_img = pygame.transform.scale(self.sx2_img, (40, 40))
        self.inv_img = pygame.transform.scale(self.inv_img, (40, 40))

    def run(self):
        pygame.init()
        pygame.mixer.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Asteroids")
        clock = pygame.time.Clock()

        pygame.mixer.music.load(path.join(snd_dir, 'mus.mp3'))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(loops=-1)

        bonus_sound = pygame.mixer.Sound(path.join(snd_dir, 'bonus.mp3'))

        expl_sounds = []
        for snd in ['expl1.wav', 'expl2.wav']:
            expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))

        running = True
        while running:
            if not self.is_player_alive:
                if time.time() - self.dead_start_time > self.dead_time:
                    running = False
            screen.fill(SPACE)

            player_astr_hits = pygame.sprite.spritecollide(self.player, self.asteroids,
                                                           False, pygame.sprite.collide_circle)
            player_enemy_hits = pygame.sprite.spritecollide(self.player, Enemy.bullets,
                                                            True, pygame.sprite.collide_circle)
            astr_bul_hits = pygame.sprite.groupcollide(self.asteroids, self.all_bullets,
                                                       True, True, pygame.sprite.collide_circle)
            enemy_hits = pygame.sprite.groupcollide(self.enemy, self.asteroids,
                                                    False, False, pygame.sprite.collide_circle)
            enemy_player_hits = pygame.sprite.groupcollide(self.enemy, self.player.bullets,
                                                           True, True, pygame.sprite.collide_circle)
            bonuses = pygame.sprite.spritecollide(self.player, self.bonuses,
                                                  True, pygame.sprite.collide_circle)

            for bonus in bonuses:
                bonus_sound.play()
                if type(bonus) is Shield:
                    self.player.active_bonuses['Shield'].activate()
                elif type(bonus) is ScoreX2:
                    self.player.active_bonuses['ScoreX2'].activate()
                elif type(bonus) is Health:
                    self.player.active_bonuses['Health'].activate()
                elif type(bonus) is Energy:
                    self.player.active_bonuses['Energy'].activate()
                else:
                    self.player.active_bonuses['Invisibility'].activate()

            for hitted_en in enemy_hits:
                if not hitted_en.is_undead:
                    self.explosions.add(Explosion(hitted_en.location, 'md'))
                    hitted_en.kill()
                    random.choice(expl_sounds).play()

            if self.player.active_bonuses['ScoreX2'].is_active:
                self.score_multipl = 2
            else:
                self.score_multipl = 1

            for hitted_en in enemy_player_hits:
                self.spawn_bonus(hitted_en.location)
                self.explosions.add(Explosion(hitted_en.location, 'md'))
                hitted_en.kill()
                random.choice(expl_sounds).play()
                self.score += 100 * self.score_multipl

            for hitted_astr, bullets in astr_bul_hits.items():
                if type(bullets[0]) is PlayerBullet:
                    self.spawn_bonus(hitted_astr.location)
                    self.score += hitted_astr.radius * self.score_multipl
                random.choice(expl_sounds).play()
                location = hitted_astr.location
                if type(hitted_astr) is BigAsteroid:
                    self.explosions.add(Explosion(location, 'bg'))
                    for i in range(2):
                        self.asteroids.add(SmallAsteroid(location, Vector.get_random_direct()))
                else:
                    self.explosions.add(Explosion(location, 'md'))

            if not self.player.is_undead:
                for hit in player_astr_hits:
                    self.explosions.add(Explosion(hit.location, 'bg'))
                    hit.kill()
                    random.choice(expl_sounds).play()
                    self.player.hit(hit.radius * 6)

                for hit in player_enemy_hits:
                    self.explosions.add(Explosion(hit.location, 'sm'))
                    self.player.hit(300)

                if self.player.hs_dead_count >= 500:
                    self.player.hit(250)

                if self.player.life_scale <= 0:
                    self.explosions.add(Explosion(hit.location, 'player'))
                    self.player.kill()
                    pygame.mixer.music.stop()
                    self.is_player_alive = False
                    self.dead_start_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or keyboard.is_pressed('esc'):
                    running = False

            if time.time() - self.last_astr_spawn_time > self.asteroid_spawn_cooldawn:
                self.spawn_asteroids()
                self.last_astr_spawn_time = time.time()

            if random.randrange(0, self.enemy_count) == 0:
                self.enemy.add(Enemy())

            self.update_all()
            self.draw_all(screen)

            Game.draw_text(screen, str(self.score), 25, WIDTH / 2, 10)
            Game.draw_bar(screen, 5, 5, 200, 20, self.player.life_scale / 10, RED, GREEN)
            self.draw_bonuses(screen)

            pygame.display.flip()

            clock.tick(FPS)
            print(self.score_multipl)

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

    def spawn_bonus(self, location):
        number = random.randrange(5)
        if number == 0:
            self.bonuses.add(Shield(location))
        elif number == 1:
            self.bonuses.add(ScoreX2(location))
        elif number == 2:
            self.bonuses.add(Health(location))
        elif number == 3:
            self.bonuses.add(Energy(location))
        else:
            self.bonuses.add(Invisibility(location))

    @staticmethod
    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, GREEN)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surf.blit(text_surface, text_rect)

    @staticmethod
    def draw_bar(surf, x, y, len, height, pct, clr1, clr2):
        if pct < 0:
            pct = 0
        BAR_LENGTH = len
        BAR_HEIGHT = height
        fill = (pct / 100) * BAR_LENGTH
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        back_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        pygame.draw.rect(surf, clr1, back_rect)
        pygame.draw.rect(surf, clr2, fill_rect)
        pygame.draw.rect(surf, WHITE, outline_rect, 2)

    def draw_bonuses(self, screen):
        count = 0
        for name, bonus in self.player.active_bonuses.items():
            x = WIDTH - 155
            y = 10 + 50 * count
            if bonus.is_active:
                if name == 'Shield':
                    img = self.shd_img
                elif name == 'Energy':
                    img = self.eng_img
                elif name == 'ScoreX2':
                    img = self.sx2_img
                elif name == 'Invisibility':
                    img = self.inv_img
                rect = img.get_rect(topleft=(x, y))
                screen.blit(img, rect)
                y += 15
                x += 45
                pct = 100 - (bonus.activ_time / bonus.validity_period) * 100
                Game.draw_bar(screen, x, y, 100, 10, pct, WHITE, BLUE)
                count += 1

    def update_all(self):
        self.bonuses.update()

        self.all_bullets.add(self.player.bullets)
        self.all_bullets.add(Enemy.bullets)
        self.all_bullets.update()
        self.asteroids.update()
        if self.player.active_bonuses['Invisibility'].is_active:
            self.enemy.update(Vector(random.randrange(0, WIDTH), random.randrange(0, HEIGHT)))
        else:
            self.enemy.update(self.player.location)
        self.player_sprite.update()
        self.explosions.update()

    def draw_all(self, screen):
        self.bonuses.draw(screen)
        self.all_bullets.draw(screen)
        self.asteroids.draw(screen)
        self.enemy.draw(screen)
        self.player_sprite.draw(screen)
        self.explosions.draw(screen)
