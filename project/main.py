# coding:utf-8
import pygame
from pygame.locals import *
import sys
from project import header as h, mode_start, mode_under_dev


def main(_mode):
    MODE = _mode
    pygame.init()
    pygame.display.set_caption("Test")
    screen = pygame.display.set_mode((h.SCREEN_WIDTH, h.SCREEN_HEIGHT))

    while (1):
        if MODE is "START":
            MODE = mode_start.start(screen)
        elif MODE is "STAGE":
            MODE = mode_under_dev.under_development(screen)


if __name__ == '__main__':
    main("START")
