# coding:utf-8
import sys, pygame

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SIZE_BLOCK = 40  # 画像ブロックの一辺のサイズ(px)


# 強制終了の処理
def operation_finish():
    pygame.quit()
    sys.exit()
