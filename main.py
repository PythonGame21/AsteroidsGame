import pygame

from game import Game
from consts import *

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Asteroids")
    game = Game(screen)
    game.run()

if __name__ == "__main__":
    main()