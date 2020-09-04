import pygame
from pygame.locals import *
import header as h, class_generate_rect


# TODO:ユーザプレイ，エージェントプレイ（未学習，学習済み），学習の分岐を作る


class Start:
    def __init__(self, _screen_class_arg):
        self.mode_next = "STAGE"
        self.player = ''
        self.num_stage = None
        self.screen = _screen_class_arg

        rect_title = class_generate_rect.Rectangle("Action Game AI", is_centering=True, _color=(255, 0, 0),
                                                   _size_font=80)
        rect_title.update_pos_rect(0, -150)

        # rect_ope1 = class_generate_rect.Rectangle("1: play by user", is_centering=True, _color=(0, 0, 0), _size_font=40)
        # rect_ope1.update_pos_rect(0, -50)
        # rect_ope2 = class_generate_rect.Rectangle("2: play AI main stage", is_centering=True, _color=(0, 0, 0),
        #                                           _size_font=40)
        # rect_ope3 = class_generate_rect.Rectangle("3: play AI sub stage", is_centering=True, _color=(0, 0, 0),
        #                                           _size_font=40)
        # rect_ope3.update_pos_rect(0, 50)
        # rect_ope4 = class_generate_rect.Rectangle("4: train AI", is_centering=True, _color=(0, 0, 0), _size_font=40)
        # rect_ope4.update_pos_rect(0, 100)
        rect_ope1 = class_generate_rect.Rectangle("play by user: 1 ~ 9", is_centering=True, _color=(0, 0, 0),
                                                  _size_font=40)
        rect_ope1.update_pos_rect(0, -50)
        rect_ope2 = class_generate_rect.Rectangle("play by AI: Q ~ O", is_centering=True, _color=(0, 0, 0),
                                                  _size_font=40)
        rect_help = class_generate_rect.Rectangle("[Action key] Right: move forward, Space: jump", is_centering=True,
                                                  _color=(0, 0, 255), _size_font=40)
        rect_help.update_pos_rect(0, 200)

        _is_loop = True
        while _is_loop:
            self.screen.fill((255, 255, 255))
            self.screen.blit(rect_title.get_obj(), rect_title.get_pos())  # テキストの描写
            self.screen.blit(rect_ope1.get_obj(), rect_ope1.get_pos())  # テキストの描写
            self.screen.blit(rect_ope2.get_obj(), rect_ope2.get_pos())  # テキストの描写
            # self.screen.blit(rect_ope1.get_obj(), (150, (rect_ope1.get_pos()).center[1]))  # テキストの描写
            # self.screen.blit(rect_ope2.get_obj(), (150, (rect_ope2.get_pos()).center[1]))  # テキストの描写
            # self.screen.blit(rect_ope3.get_obj(), (150, (rect_ope3.get_pos()).center[1]))  # テキストの描写
            # self.screen.blit(rect_ope4.get_obj(), (150, (rect_ope4.get_pos()).center[1]))  # テキストの描写
            self.screen.blit(rect_help.get_obj(), rect_help.get_pos())  # テキストの描写

            # 画面の更新
            pygame.display.update()

            _is_loop = self._catch_input()

    def get_mode_next(self):
        return self.mode_next, self.player, self.num_stage

    def _catch_input(self):
        # イベント処理
        is_loop = True
        list_key = [[K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0],
                    [K_q, K_w, K_e, K_r, K_t, K_y, K_u, K_i, K_o, K_p]]
        for event in pygame.event.get():
            if event.type == QUIT:
                h.operation_finish()
            elif event.type == KEYDOWN:
                if event.key in list_key[0]:
                    self.player = 'USER'
                    self.num_stage = (list_key[0].index(event.key) + 1) % 10
                    is_loop = False
                elif event.key in list_key[1]:
                    self.player = 'AI'
                    self.num_stage = (list_key[1].index(event.key) + 1) % 10
                    is_loop = False
                elif event.key == K_ESCAPE:
                    h.operation_finish()
        return is_loop
