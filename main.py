import pygame
import keyboard

from consts import *
from player import Player

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.transform.scale(pygame.image.load('background.png'),
                                    (WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

running = True
while running:
    screen.blit(background, [0, 0])

    for event in pygame.event.get():
        if event.type == pygame.QUIT or keyboard.is_pressed('esc'):
            running = False
    all_sprites.update()
    all_sprites.draw(screen)
    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
