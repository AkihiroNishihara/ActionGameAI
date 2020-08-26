import pygame
from pygame.locals import *
import sys
import itertools
import numpy as np
from project import header as h
from project import class_generate_rect

TIME_STAGE = 100
DIST_BASE_MOVE = 10


# TODO:当たり判定が必要なブロック群をSprite処理

class GameStage:
    def __init__(self, _screen_class_arg):
        self.mode_next = "END"
        self.screen = _screen_class_arg
        self.is_loop = True
        _is_game_over = False
        _is_game_clear = False
        _time_start = pygame.time.get_ticks()
        _time_elapsed = 0
        # フォントの定義
        _font = pygame.font.Font(None, 60)
        # ステージ情報のロード(0:空，1:ブロック，2:player，3:ゴール)
        _list_info_stage, _list_pos_player_ini, _list_pos_goal_ini = self._load_info_gamestage()

        # 長方形オブジェクトの生成
        self.rect_player = class_generate_rect.Rectangle("./image/player.png", _is_alpha=True)
        self.rect_brick = class_generate_rect.Rectangle("./image/brick.png", _is_alpha=False)
        self.rect_goal = class_generate_rect.Rectangle("./image/goal.png", _is_alpha=True)
        self.rect_gameover = class_generate_rect.Rectangle("Game Over", _is_alpha=True, is_centering=True,
                                                           _color=(50, 50, 50), _size_font=60)
        self.rect_gameclear = class_generate_rect.Rectangle("Game Clear", _is_alpha=True, is_centering=True,
                                                            _color=(50, 50, 50), _size_font=60)
        self.rect_ope = class_generate_rect.Rectangle("press Enter", _is_alpha=True, is_centering=True,
                                                      _color=(0, 255, 0), _size_font=60)

        # 長方形オブジェクトの初期位置更新
        self.rect_gameover.update_pos_rect(0, -50)
        self.rect_ope.update_pos_rect(0, 100)
        self.rect_player.update_pos_rect(h.SIZE_IMAGE_UNIT * _list_pos_player_ini[1], h.SIZE_IMAGE_UNIT * _list_pos_player_ini[0])
        self.rect_goal.update_pos_rect(h.SIZE_IMAGE_UNIT * _list_pos_goal_ini[1], h.SIZE_IMAGE_UNIT * _list_pos_goal_ini[0])

        while self.is_loop:
            pygame.display.update()  # 画面の更新
            pygame.time.wait(30)  # 更新時間間隔(30fps)

            # 移動処理(長押し)
            if not _is_game_over and not _is_game_clear:
                _key_pressed = pygame.key.get_pressed()
                if _key_pressed[K_LEFT]:
                    self.rect_player.update_pos_rect(-DIST_BASE_MOVE, 0)
                if _key_pressed[K_RIGHT]:
                    self.rect_player.update_pos_rect(DIST_BASE_MOVE, 0)
                if _key_pressed[K_DOWN]:
                    self.rect_player.update_pos_rect(0, DIST_BASE_MOVE)
                if _key_pressed[K_UP]:
                    self.rect_player.update_pos_rect(0, -DIST_BASE_MOVE)

            # ベース描写
            self.screen.fill((200, 255, 255))
            pygame.draw.rect(self.screen, (200, 200, 200), Rect(0, 0, h.SCREEN_WIDTH, h.SIZE_IMAGE_UNIT))  # 画面上部の四角形の描写

            # 経過時間の描写
            if not _is_game_over and not _is_game_clear:
                _time_elapsed = int((pygame.time.get_ticks() - _time_start) / 1000)
            self.time_remain = TIME_STAGE - _time_elapsed
            _text_time_remain = _font.render(str(max(0, self.time_remain)), True, (255, 0, 0))  # テキストの作成
            self.screen.blit(_text_time_remain, [0, 0])  # テキストの描写

            # ブロックの描写
            for i, j in itertools.product(range(1, int(h.SCREEN_HEIGHT / h.SIZE_IMAGE_UNIT)),
                                          range(int(h.SCREEN_WIDTH / h.SIZE_IMAGE_UNIT))):
                if _list_info_stage[i][j] == 1:
                    self.screen.blit(self.rect_brick.get_obj(), [h.SIZE_IMAGE_UNIT * j, h.SIZE_IMAGE_UNIT * i])
                elif _list_info_stage[i][j] == 2:
                    self.screen.blit(self.rect_goal.get_obj(), [h.SIZE_IMAGE_UNIT * j, h.SIZE_IMAGE_UNIT * i])
            # プレイヤー描写
            self.screen.blit(self.rect_player.get_obj(), self.rect_player.get_pos())

            # 終了イベント処理
            self.list_event = pygame.event.get()
            for event in self.list_event:
                if event.type == QUIT:
                    h.operation_finish()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        h.operation_finish()

            # クリア処理
            dist_goal = self._get_dist_goal()  # ゴールまでの距離
            if dist_goal <= h.SIZE_IMAGE_UNIT:
                _is_game_clear = True
            if _is_game_clear:
                self._process_gameclear()
                # self.screen.blit(self.rect_gameclear.get_obj(), self.rect_gameover.get_pos())
                # self.screen.blit(self.rect_ope.get_obj(), self.rect_ope.get_pos())
                # for event in self.list_event:
                #     if event.key == K_RETURN:
                #         _is_loop = False

            # ゲームオーバー処理
            _is_game_over = self._check_is_gameover()
            if _is_game_over:
                self._process_gameover()
                # self._screen.blit(self.rect_gameover.get_obj(), self.rect_gameover.get_pos())
                # self._screen.blit(self.rect_ope.get_obj(), self.rect_ope.get_pos())
                # for event in list_event:
                #     if event.key == K_RETURN:
                #         self._is_loop = False

    # ステージのブロックの配置およびプレイヤーの初期位置の取得
    def _load_info_gamestage(self):
        list_info_gamestage = []
        list_pos_player_ini = []
        list_pos_goal_ini = []
        fp = open("./stage_sample.txt", 'r')
        list_lines = fp.readlines()
        for line in list_lines:
            line = line.replace('\n', '')
            list_temp = [int(s) for s in list(line)]
            list_info_gamestage.append(list_temp)

        for i, j in itertools.product(range(len(list_info_gamestage)), range(len(list_info_gamestage[0]))):
            if list_info_gamestage[i][j] == 2:
                list_pos_goal_ini = [i, j]
            elif list_info_gamestage[i][j] == 3:
                list_pos_player_ini = [i, j]

        return list_info_gamestage, list_pos_player_ini, list_pos_goal_ini

    # 経過時間あるいはプレイヤーの位置によるゲームオーバー判定
    def _check_is_gameover(self):
        is_gameover = False
        if self.time_remain < 0:
            is_gameover = True
        coordinate_bottom_player = (self.rect_player.get_pos()).bottom
        if coordinate_bottom_player >= h.SCREEN_HEIGHT:
            is_gameover = True
        return is_gameover

    def _get_dist_goal(self):
        x_player = (self.rect_player.get_pos()).centerx
        y_player = (self.rect_player.get_pos()).centery
        x_goal = (self.rect_goal.get_pos()).centerx
        y_goal = (self.rect_goal.get_pos()).centery
        dist = np.linalg.norm(np.array([x_player, y_player]) - np.array([x_goal, y_goal]))
        return dist

    def _process_gameover(self):
        self.screen.blit(self.rect_gameover.get_obj(), self.rect_gameover.get_pos())
        self.screen.blit(self.rect_ope.get_obj(), self.rect_ope.get_pos())
        for event in self.list_event:
            if event.key == K_RETURN:
                self.is_loop = False

    def _process_gameclear(self):
        self.screen.blit(self.rect_gameclear.get_obj(), self.rect_gameover.get_pos())
        self.screen.blit(self.rect_ope.get_obj(), self.rect_ope.get_pos())
        for event in self.list_event:
            if event.key == K_RETURN:
                self.is_loop = False

    def get_mode_next(self):
        return self.mode_next


class CoordinateAroundPlayer:
    def __init__(self, _list_pos_player):
        self.coord_left = None
        self.coord_right = None
        self.coord_up = None
        self.coord_down = None
