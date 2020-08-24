# coding:utf-8
import pygame
from project import mode_start


def main(_mode):
    MODE = _mode
    pygame.init()
    pygame.display.set_caption("Test")
    screen = pygame.display.set_mode((640, 480))

    while (1):
        if MODE is "START":
            MODE = mode_start.start(screen)


if __name__ == '__main__':
    main("START")
