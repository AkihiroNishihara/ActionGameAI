import pygame
from pygame.locals import *
import sys
from project import header as h


def start(screen):
    size_font = 80
    mode_next = "STAGE"
    is_loop = True
    # フォントの定義
    font = pygame.font.Font(None, size_font)

    while (is_loop):
        screen.fill((255, 255, 255))
        str_title = "Action Game AI"
        str_ope = "press 'z' to play game"

        # テキストの描写
        text_title = font.render(str_title, True, (255, 0, 0))  # テキストの作成
        text_title_rect = text_title.get_rect(center=(h.SCREEN_WIDTH / 2, h.SCREEN_HEIGHT / 2))  # テキストボックスのサイズ取得
        screen.blit(text_title, [text_title_rect.left, text_title_rect.top - 100])        # テキストの描写

        text_ope = font.render(str_ope, True, (0, 255, 0))
        text_ope_rect = text_ope.get_rect(center=(h.SCREEN_WIDTH / 2, h.SCREEN_HEIGHT / 2))
        screen.blit(text_ope, [text_ope_rect.left, text_ope_rect.top + 100])

        # 画面の更新
        pygame.display.update()

        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_z:
                    is_loop = False

    return mode_next
