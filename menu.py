import pygame.mouse

from consts import *
from os import path
from game import Game

font_name = pygame.font.match_font('arial')
img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')


class Menu:
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Asteroids")
    pygame.mixer.music.load(path.join(snd_dir, 'mus.mp3'))
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(loops=-1)

    @staticmethod
    def show_main_menu():
        bkg = pygame.image.load(path.join(img_dir, "bkg.png"))
        bkg_img = pygame.transform.scale(bkg, (WIDTH, HEIGHT))

        start_button = Button(300, 70)
        continue_button = Button(300, 70)
        hint_button = Button(300, 70)

        show = True
        while show:
            Menu.screen.blit(bkg_img, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    show = False

            quit_code = start_button.draw(Menu.screen, 450, 300, 'Start game', Menu.start_game)
            quit_code_2 = continue_button.draw(Menu.screen, 450, 400, 'Continue', Menu.continue_game)
            quit_code_3 = hint_button.draw(Menu.screen, 450, 500, 'Control', Menu.show_hint)

            if quit_code == 1 or quit_code_2 == 1 or quit_code_3 == 1:
                show = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    show = False

            pygame.display.flip()
        pygame.quit()

    @staticmethod
    def show_hint():
        bkgh = pygame.image.load(path.join(img_dir, "bkgh.png"))
        bkgh_img = pygame.transform.scale(bkgh, (WIDTH, HEIGHT))

        back_button = Button(300, 70)

        show = True
        while show:
            Menu.screen.blit(bkgh_img, (0, 0))

            stop = back_button.draw(Menu.screen, 850, 700, 'Back', Menu.back)

            if stop == 1:
                return 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 1
            pygame.display.flip()

    @staticmethod
    def start_game():
        game = Game(Menu.screen)
        quit_code = game.run()
        return quit_code


    @staticmethod
    def continue_game():
        game = Game(Menu.screen)
        game.load(Menu.screen)
        quit_code = game.run()
        return quit_code

    @staticmethod
    def back():
        return 1

class Button:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.active_clr = ACTIVE_CLR
        self.inactive_clr = INACTIVE_CLR

    def draw(self, screen, x, y, massage, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(screen, self.active_clr, (x, y, self.width, self.height))
            if click[0] == 1:
                pygame.time.delay(200)
                if action is not None:
                    quit_code = action()
                    return quit_code
        else:
            pygame.draw.rect(screen, self.inactive_clr, (x, y, self.width, self.height))
        Button.draw_text(screen, massage, 50, x + self.width / 2, y + 5)

    @staticmethod
    def draw_text(surf, text, size, x, y):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, GREEN)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surf.blit(text_surface, text_rect)

def main():
    Menu.show_main_menu()

if __name__ == "__main__":
    main()