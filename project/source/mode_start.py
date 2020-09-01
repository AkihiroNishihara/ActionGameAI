import pygame
from pygame.locals import *
from project.source import header as h, class_generate_rect


# TODO:ユーザプレイ，エージェントプレイ（未学習，学習済み），学習の分岐を作る


class Start:
    def __init__(self, _screen_class_arg):
        self.mode_next = "STAGE"
        self.player = ''
        self.screen = _screen_class_arg

        rect_title = class_generate_rect.Rectangle("Action Game AI", is_centering=True, _color=(255, 0, 0),
                                                   _size_font=80)
        rect_title.update_pos_rect(0, -150)

        rect_ope1 = class_generate_rect.Rectangle("1: play by user", is_centering=True, _color=(0, 0, 0), _size_font=40)
        rect_ope1.update_pos_rect(0, -50)
        rect_ope2 = class_generate_rect.Rectangle("2: play AI main stage", is_centering=True, _color=(0, 0, 0),
                                                  _size_font=40)
        rect_ope3 = class_generate_rect.Rectangle("3: play AI sub stage", is_centering=True, _color=(0, 0, 0),
                                                  _size_font=40)
        rect_ope3.update_pos_rect(0, 50)
        rect_ope4 = class_generate_rect.Rectangle("4: train AI", is_centering=True, _color=(0, 0, 0), _size_font=40)
        rect_ope4.update_pos_rect(0, 100)
        rect_help = class_generate_rect.Rectangle("Action = arrow key: move, space key: jump", is_centering=True,
                                                  _color=(0, 0, 255), _size_font=40)
        rect_help.update_pos_rect(0, 200)

        _is_loop = True
        while _is_loop:
            self.screen.fill((255, 255, 255))
            self.screen.blit(rect_title.get_obj(), rect_title.get_pos())  # テキストの描写
            self.screen.blit(rect_ope1.get_obj(), (150, (rect_ope1.get_pos()).center[1]))  # テキストの描写
            self.screen.blit(rect_ope2.get_obj(), (150, (rect_ope2.get_pos()).center[1]))  # テキストの描写
            self.screen.blit(rect_ope3.get_obj(), (150, (rect_ope3.get_pos()).center[1]))  # テキストの描写
            self.screen.blit(rect_ope4.get_obj(), (150, (rect_ope4.get_pos()).center[1]))  # テキストの描写
            self.screen.blit(rect_help.get_obj(), rect_help.get_pos())  # テキストの描写

            # 画面の更新
            pygame.display.update()

            # イベント処理
            for event in pygame.event.get():
                if event.type == QUIT:
                    h.operation_finish()
                elif event.type == KEYDOWN:
                    if event.key == K_1:
                        self.player = 'USER'
                        _is_loop = False
                        break
                    elif event.key == K_2:
                        self.player = 'AI_MAIN'
                        _is_loop = False
                        break
                    elif event.key == K_3:
                        self.player = 'AI_SUB'
                        _is_loop = False
                        break
                    elif event.key == K_4:
                        self.player = 'AGENT'
                        _is_loop = False
                        break
                    elif event.key == K_ESCAPE:
                        h.operation_finish()

    def get_mode_next(self):
        return self.mode_next, self.player
