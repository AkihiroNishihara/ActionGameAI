import pygame
from pygame.locals import *
import sys
from project import header as h


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
        text_title = font.render(str_title, True, (255, 0, 0))  # テキストの作成
        text_title_rect = text_title.get_rect(center=(h.SCREEN_WIDTH / 2, h.SCREEN_HEIGHT / 2))  # テキストボックスのサイズ取得
        screen.blit(text_title, [text_title_rect.left, text_title_rect.top - 100])  # テキストの描写

        str_ope = "press Z"
        text_ope = font.render(str_ope, True, (255, 0, 0))  # テキストの作成
        text_ope_rect = text_ope.get_rect(center=(h.SCREEN_WIDTH / 2, h.SCREEN_HEIGHT / 2))  # テキストボックスのサイズ取得
        screen.blit(text_ope, [text_ope_rect.left, text_ope_rect.top + 100])  # テキストの描写
        pygame.display.update()

        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                operation_finish()
            elif event.type == KEYDOWN:
                if event.key == K_z:
                    operation_finish()
