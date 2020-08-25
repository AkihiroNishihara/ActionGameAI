import pygame
from pygame.locals import *
import sys
from project import class_generate_rect


def operation_finish():
    pygame.quit()
    sys.exit()


def under_development(screen):
    is_loop = True

    rect_title = class_generate_rect.Rectangle("Under Development", is_centering=True, _color=(255, 0, 0), _size_font=40)
    rect_title.update_pos_rect(0, -100)

    rect_ope = class_generate_rect.Rectangle("press Enter", is_centering=True, _color=(0, 255, 0), _size_font=40)
    rect_ope.update_pos_rect(0, 100)

    while (is_loop):
        screen.fill((255, 255, 255))
        screen.blit(rect_title.get_obj(), rect_title.get_pos())  # テキストの描写
        screen.blit(rect_ope.get_obj(), rect_ope.get_pos())  # テキストの描写
        pygame.display.update()

        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                operation_finish()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    operation_finish()
