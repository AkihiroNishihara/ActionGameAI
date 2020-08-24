import pygame
from pygame.locals import *
import sys
import itertools
from project import header as h


def game_stage(screen):
    size_font = 80
    mode_next = "END"
    is_loop = True
    # フォントの定義
    font = pygame.font.Font(None, size_font)
    # ステージ情報のロード(0:空，1:ブロック，2:player，3:ゴール)
    list_info_stage, list_pos_player_ini = load_info_gamestage()
    # 画像のロードおよび情報取得
    img_player = pygame.image.load("./image/player.png")
    rect_player = img_player.get_rect()
    img_brick = pygame.image.load("./image/brick.png")
    img_goal = pygame.image.load("./image/goal.png")
    # プレイヤーの初期位置更新
    rect_player.move_ip(h.SIZE_BLOCK * list_pos_player_ini[1], h.SIZE_BLOCK * list_pos_player_ini[0])

    while (is_loop):
        pygame.display.update()  # 画面の更新
        pygame.time.wait(30)  # 更新時間間隔
        screen.fill((200, 255, 255))
        pygame.draw.rect(screen, (200, 200, 200), Rect(0, 0, h.SCREEN_WIDTH, h.SIZE_BLOCK))  # 画面上部の四角形の描写

        # ブロックの描写
        for i, j in itertools.product(range(1, int(h.SCREEN_HEIGHT / h.SIZE_BLOCK)),
                                      range(int(h.SCREEN_WIDTH / h.SIZE_BLOCK))):
            if list_info_stage[i][j] == 1:
                screen.blit(img_brick, [h.SIZE_BLOCK * j, h.SIZE_BLOCK * i])
            elif list_info_stage[i][j] == 2:
                screen.blit(img_goal, [h.SIZE_BLOCK * j, h.SIZE_BLOCK * i])
            screen.blit(img_player, rect_player)

        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_z:
                    is_loop = False
                if event.key == K_LEFT:
                    rect_player.move_ip(-1, 0)
                if event.key == K_RIGHT:
                    rect_player.move_ip(1, 0)
                if event.key == K_UP:
                    rect_player.move_ip(0, -1)
                if event.key == K_DOWN:
                    rect_player.move_ip(0, 1)
    return mode_next


# ステージのブロックの配置およびプレイヤーの初期位置の取得
def load_info_gamestage():
    list_info_gamestage = []
    list_pos_player_ini = []
    fp = open("./stage_sample.txt", 'r')
    list_lines = fp.readlines()
    for line in list_lines:
        line = line.replace('\n', '')
        list_temp = [int(s) for s in list(line)]
        list_info_gamestage.append(list_temp)

    for i, j in itertools.product(range(len(list_info_gamestage)), range(len(list_info_gamestage))):
        if list_info_gamestage[i][j] == 3:
            list_pos_player_ini = [i, j]

    return list_info_gamestage, list_pos_player_ini
