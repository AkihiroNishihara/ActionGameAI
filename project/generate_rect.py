import pygame
from pygame.locals import *


class rectangle:
    def __init__(self, _object, _is_alpha=True, _color=(0, 0, 0), _size_font=60):
        self._obj = None
        self._rect = None
        self._type = None
        # 読み込むオブジェクトが画像
        if "./" in _object:
            self._type = "img"
            if _is_alpha == True:
                self._obj = pygame.image.load(_object).convert_alpha()  # 読み込みとピクセル形式の変更（透過あり）
            else:
                self._obj = pygame.image.load(_object).convert_alpha()  # 読み込みとピクセル形式の変更（透過あり）
        else:
            self._type = "font"
            font = pygame.font.Font(None, _size_font)
            self._obj = font.render(_object, _is_alpha, _color)

        self._rect = self._obj.get_rect()

    def get_obj(self):
        return self._obj

    def get_pos(self):
        return self._rect

    def update_pos_rect(self, __x, __y):
        self._rect.move_ip(__x, __y)
