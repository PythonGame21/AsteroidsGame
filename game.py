import pygame
import keyboard
import random
import time
import pickle

from consts import *
from player import Player
from asteroid import BigAsteroid, SmallAsteroid
from vector import Vector
from enemy import Enemy
from bullet import PlayerBullet
from os import path
from explosion import Explosion
from bonuses import Shield, ScoreX2, Health, Energy, Invisibility
from save import Save

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
        self.asteroid_spawn_cooldawn = 8
        self.enemy_count = 1000
        self.last_astr_spawn_time = -self.asteroid_spawn_cooldawn
        self.score = 0
        self.score_multipl = 1

        self.bonus_count = 8

        self.difficulty = 'Difficulty: Easy'
        self.space_clr = SPACE1

        self.is_player_alive = True
        self.dead_time = 2
        self.dead_start_time = 0

        self.is_paused = False

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

        save_data = Save()

        expl_sounds = []
        for snd in ['expl1.wav', 'expl2.wav']:
            expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))

        running = True
        while running:
            if not self.is_player_alive:
                if time.time() - self.dead_start_time > self.dead_time:
                    running = False
            screen.fill(self.space_clr)

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
                rnd = random.randrange(0, self.bonus_count)
                if rnd == 0:
                    self.spawn_bonus(hitted_astr.location)
                self.explosions.add(Explosion(hitted_en.location, 'md'))
                hitted_en.kill()
                random.choice(expl_sounds).play()
                self.score += 100 * self.score_multipl

            for hitted_astr, bullets in astr_bul_hits.items():
                if type(bullets[0]) is PlayerBullet:
                    rnd = random.randrange(0, self.bonus_count)
                    if rnd == 0:
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
                    self.player.hit(hit.radius * 8)

                for hit in player_enemy_hits:
                    self.explosions.add(Explosion(hit.location, 'sm'))
                    self.player.hit(350)

                if self.player.hs_dead_count >= 500:
                    self.player.hit(300)

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

            if not self.is_paused:
                self.update_all()
            self.draw_all(screen)

            Game.draw_text(screen, self.difficulty, 30, WIDTH / 2, HEIGHT - 50)
            Game.draw_text(screen, str(self.score), 25, WIDTH / 2, 10)
            Game.draw_bar(screen, 5, 5, 200, 20, self.player.life_scale / 10, RED, GREEN)
            self.draw_bonuses(screen)

            self.update_difficulty()

            if keyboard.is_pressed('g'):
                save_data.save(self)
            if keyboard.is_pressed('h'):
                pass

            if keyboard.is_pressed('p') and self.is_paused:
                self.is_paused = False
            elif keyboard.is_pressed('p') and not self.is_paused:
                self.is_paused = True
            if self.is_paused:
                Game.draw_text(screen, 'Paused', 50, WIDTH / 2, HEIGHT / 2)

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
            if name == 'Health':
                continue
            if bonus.is_active:
                img = bonus.image
                rect = img.get_rect(topleft=(x, y))
                screen.blit(img, rect)
                y += 15
                x += 45
                pct = 100 - (bonus.activ_time / bonus.validity_period) * 100
                Game.draw_bar(screen, x, y, 100, 10, pct, WHITE, BLUE)
                count += 1

    def update_difficulty(self):
        if self.score > 5000:
            self.difficulty = 'Difficulty: Hard'
            self.asteroid_spawn_cooldawn = 3
            self.enemy_count = 200
            self.bonus_count = 15
            if self.space_clr != SPACE3:
                self.space_clr = (self.space_clr[0] + 1, self.space_clr[1] - 1, 0)
        elif self.score > 1500:
            self.difficulty = 'Difficulty: Normal'
            self.asteroid_spawn_cooldawn = 5
            self.enemy_count = 500
            self.bonus_count = 12
            if self.space_clr != SPACE2:
                self.space_clr = (0, self.space_clr[1] + 1, self.space_clr[2] - 1)

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

    def __getstate__(self) -> dict:
        state = {}
        state["asteroids"] = self.asteroids
        state["enemy"] = self.enemy
        state["all_bullets"] = self.all_bullets
        state["bonuses"] = self.bonuses
        state["player"] = self.player
        state["player_sprite"] = self.player_sprite
        state["explosions"] = self.explosions
        state["asteroid_spawn_cooldawn"] = self.asteroid_spawn_cooldawn
        state["enemy_count"] = self.enemy_count
        state["last_astr_spawn_time"] = self.last_astr_spawn_time
        state["score"] = self.score
        state["score_multipl"] = self.score_multipl

        state["bonus_count"] = self.bonus_count

        state["difficulty"] = self.difficulty
        state["space_clr"] = self.space_clr

        state["is_player_alive"] = self.is_player_alive
        state["dead_time"] = self.dead_time
        state["dead_start_time"] = self.dead_start_time
        return state

    def __setstate__(self, state: dict):
        self.asteroids = state["asteroids"]
        self.enemy = state["enemy"]
        self.all_bullets = state["all_bullets"]
        self.bonuses = state["bonuses"]
        self.player = state["player"]
        self.player_sprite = state["player_sprite"]
        self.explosions = state["explosions"]
        self.asteroid_spawn_cooldawn = state["asteroid_spawn_cooldawn"]
        self.enemy_count = state["enemy_count"]
        self.last_astr_spawn_time = state["last_astr_spawn_time"]
        self.score = state["score"]
        self.score_multipl = state["score_multipl"]

        self.bonus_count = state["bonus_count"]

        self.difficulty = state["difficulty"]
        self.space_clr = state["space_clr"]

        self.is_player_alive = state["is_player_alive"]
        self.dead_time = state["dead_time"]
        self.dead_start_time = state["dead_start_time"]

    def save(self):
        with open("save.pkl", "wb") as sv:
            pickle.dump(self.__getstate__(), sv)

    def load(self):
        with open("save.pkl", "rb") as sv:
            info = pickle.load(sv)
            self.__setstate__(info)


