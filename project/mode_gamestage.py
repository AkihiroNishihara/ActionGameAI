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

def game_stage(screen):
    mode_next = "END"
    is_loop = True
    is_game_over = False
    is_game_clear = False
    time_start = pygame.time.get_ticks()
    time_elapsed = 0
    # フォントの定義
    font = pygame.font.Font(None, 60)
    # ステージ情報のロード(0:空，1:ブロック，2:player，3:ゴール)
    list_info_stage, list_pos_player_ini, list_pos_goal_ini = load_info_gamestage()

    # 長方形オブジェクトの生成
    rect_player = class_generate_rect.Rectangle("./image/player.png", _is_alpha=True)
    rect_brick = class_generate_rect.Rectangle("./image/brick.png", _is_alpha=False)
    rect_goal = class_generate_rect.Rectangle("./image/goal.png", _is_alpha=True)
    rect_gameover = class_generate_rect.Rectangle("Game Over", _is_alpha=True, is_centering=True, _color=(50, 50, 50),
                                                  _size_font=60)
    rect_gameclear = class_generate_rect.Rectangle("Game Clear", _is_alpha=True, is_centering=True, _color=(50, 50, 50),
                                                   _size_font=60)
    rect_ope = class_generate_rect.Rectangle("press Enter", _is_alpha=True, is_centering=True, _color=(0, 255, 0),
                                             _size_font=60)

    # 長方形オブジェクトの初期位置更新
    rect_gameover.update_pos_rect(0, -50)
    rect_ope.update_pos_rect(0, 100)
    rect_player.update_pos_rect(h.SIZE_BLOCK * list_pos_player_ini[1], h.SIZE_BLOCK * list_pos_player_ini[0])
    rect_goal.update_pos_rect(h.SIZE_BLOCK * list_pos_goal_ini[1], h.SIZE_BLOCK * list_pos_goal_ini[0])

    while is_loop:
        pygame.display.update()  # 画面の更新
        pygame.time.wait(30)  # 更新時間間隔(30fps)

        # 移動処理(長押し)
        if not is_game_over and not is_game_clear:
            key_pressed = pygame.key.get_pressed()
            if key_pressed[K_LEFT]:
                rect_player.update_pos_rect(-DIST_BASE_MOVE, 0)
            if key_pressed[K_RIGHT]:
                rect_player.update_pos_rect(DIST_BASE_MOVE, 0)
            if key_pressed[K_DOWN]:
                rect_player.update_pos_rect(0, DIST_BASE_MOVE)
            if key_pressed[K_UP]:
                rect_player.update_pos_rect(0, -DIST_BASE_MOVE)

        # ベース描写
        screen.fill((200, 255, 255))
        pygame.draw.rect(screen, (200, 200, 200), Rect(0, 0, h.SCREEN_WIDTH, h.SIZE_BLOCK))  # 画面上部の四角形の描写

        # 経過時間の描写
        if not is_game_over and not is_game_clear:
            time_elapsed = int((pygame.time.get_ticks() - time_start) / 1000)
        time_remain = TIME_STAGE - time_elapsed
        text_time_remain = font.render(str(max(0, time_remain)), True, (255, 0, 0))  # テキストの作成
        screen.blit(text_time_remain, [0, 0])  # テキストの描写

        # ブロックの描写
        for i, j in itertools.product(range(1, int(h.SCREEN_HEIGHT / h.SIZE_BLOCK)),
                                      range(int(h.SCREEN_WIDTH / h.SIZE_BLOCK))):
            if list_info_stage[i][j] == 1:
                screen.blit(rect_brick.get_obj(), [h.SIZE_BLOCK * j, h.SIZE_BLOCK * i])
            elif list_info_stage[i][j] == 2:
                screen.blit(rect_goal.get_obj(), [h.SIZE_BLOCK * j, h.SIZE_BLOCK * i])
        # プレイヤー描写
        screen.blit(rect_player.get_obj(), rect_player.get_pos())

        # 終了イベント処理
        list_event = pygame.event.get()
        for event in list_event:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # クリア処理
        dist_goal = get_dist_goal(rect_player, rect_goal)  # ゴールまでの距離
        if dist_goal <= h.SIZE_BLOCK:
            is_game_clear = True
        if is_game_clear:
            screen.blit(rect_gameclear.get_obj(), rect_gameover.get_pos())
            screen.blit(rect_ope.get_obj(), rect_ope.get_pos())
            for event in list_event:
                if event.key == K_RETURN:
                    is_loop = False

        # ゲームオーバー処理
        is_game_over = check_is_gameover(time_remain, rect_player)
        if is_game_over:
            screen.blit(rect_gameover.get_obj(), rect_gameover.get_pos())
            screen.blit(rect_ope.get_obj(), rect_ope.get_pos())
            for event in list_event:
                if event.key == K_RETURN:
                    is_loop = False
    return mode_next


# ステージのブロックの配置およびプレイヤーの初期位置の取得
def load_info_gamestage():
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
def check_is_gameover(_time_remain, _rect_player):
    is_gameover = False
    if _time_remain < 0:
        is_gameover = True
    coordinate_bottom_player = (_rect_player.get_pos()).bottom
    if coordinate_bottom_player >= h.SCREEN_HEIGHT:
        is_gameover = True

    return is_gameover


def get_dist_goal(_rect_player, _rect_goal):
    is_clear = False
    x_player = (_rect_player.get_pos()).centerx
    y_player = (_rect_player.get_pos()).centery
    x_goal = (_rect_goal.get_pos()).centerx
    y_goal = (_rect_goal.get_pos()).centery
    dist = np.linalg.norm(np.array([x_player, y_player]) - np.array([x_goal, y_goal]))
    return dist
