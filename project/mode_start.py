import pygame
from pygame.locals import *
import sys
from project import class_generate_rect


class Start:
    def __init__(self, _screen_class_arg):
        self.mode_next = "STAGE"
        self.screen = _screen_class_arg
        _rect_title = class_generate_rect.Rectangle("Action Game AI", is_centering=True, _color=(255, 0, 0),
                                                    _size_font=80)
        _rect_title.update_pos_rect(0, -100)

        _rect_ope = class_generate_rect.Rectangle("press Enter to play game", is_centering=True, _color=(0, 255, 0),
                                                  _size_font=40)
        _rect_ope.update_pos_rect(0, 100)

        _is_loop = True
        while _is_loop:
            self.screen.fill((255, 255, 255))
            self.screen.blit(_rect_title.get_obj(), _rect_title.get_pos())  # テキストの描写
            self.screen.blit(_rect_ope.get_obj(), _rect_ope.get_pos())  # テキストの描写

            # 画面の更新
            pygame.display.update()

            # イベント処理
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        _is_loop = False
                        break

    def get_mode_next(self):
        return self.mode_next
