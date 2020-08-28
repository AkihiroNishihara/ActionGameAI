import pygame
from pygame.locals import *
from project.source import header as h, class_generate_rect


class UnderDevelopment:
    def __init__(self, _screen):
        self.mode_next = "START"
        _is_loop = True
        _rect_title = class_generate_rect.Rectangle("Under Development", is_centering=True, _color=(255, 0, 0),
                                                    _size_font=40)
        _rect_title.update_pos_rect(0, -100)

        _rect_ope = class_generate_rect.Rectangle("press Enter", is_centering=True, _color=(0, 255, 0), _size_font=40)
        _rect_ope.update_pos_rect(0, 100)

        while (_is_loop):
            _screen.fill((255, 255, 255))
            _screen.blit(_rect_title.get_obj(), _rect_title.get_pos())  # テキストの描写
            _screen.blit(_rect_ope.get_obj(), _rect_ope.get_pos())  # テキストの描写
            pygame.display.update()

            # イベント処理
            for event in pygame.event.get():
                if event.type == QUIT:
                    h.operation_finish()
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        _is_loop = False

    def get_mode_next(self):
        return self.mode_next
