import pygame
from pygame.locals import *
import sys
from project import generate_rect


def start(screen):
    mode_next = "STAGE"
    is_loop = True

    rect_title = generate_rect.rectangle("Action Game AI", is_centering=True, _color=(255, 0, 0), _size_font=80)
    rect_title.update_pos_rect(0, -100)

    rect_ope = generate_rect.rectangle("press 'z' to play game", is_centering=True, _color=(0, 255, 0), _size_font=40)
    rect_ope.update_pos_rect(0, 100)

    while (is_loop):
        screen.fill((255, 255, 255))
        screen.blit(rect_title.get_obj(), rect_title.get_pos())  # テキストの描写
        screen.blit(rect_ope.get_obj(), rect_ope.get_pos())  # テキストの描写

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
