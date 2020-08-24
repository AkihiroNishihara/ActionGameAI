import pygame
from pygame.locals import *
import sys


def operation_finish():
    pygame.quit()
    sys.exit()


def under_development(screen):
    size_font = 40
    font = pygame.font.Font(None, size_font)
    is_loop = True

    while (is_loop):
        screen.fill((255, 255, 255))
        str_title = "Under Development"
        str_operation = "press Z"
        text_title = font.render(str_title, True, (255, 0, 0))
        text_operation = font.render(str_operation, True, (255, 0, 0))
        screen.blit(text_title, [320 - size_font * len(str_title) / 2, 100])
        screen.blit(text_operation, [320 - size_font * len(str_title) / 2, 300])
        pygame.display.update()

        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                operation_finish()
            elif event.type == KEYDOWN:
                if event.key == K_z:
                    operation_finish()
