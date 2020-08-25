# coding:utf-8
import pygame
from pygame.locals import *
import sys
from project import header as h, mode_start, mode_gamestage, mode_under_dev

# START, STAGE, END
mode_initial = "START"


class ActionGame:
    def __init__(self, _mode_ini):
        self.MODE = _mode_ini
        pygame.init()
        pygame.display.set_caption("Action Game AI")
        _screen = pygame.display.set_mode((h.SCREEN_WIDTH, h.SCREEN_HEIGHT))

        while True:
            mode_current = None
            if self.MODE is "START":
                mode_current = mode_start.Start(_screen)
                self.MODE = mode_current.get_mode_next()
            elif self.MODE is "STAGE":
                mode_current = mode_gamestage.GameStage(_screen)
                self.MODE = mode_current.get_mode_next()
            elif self.MODE is "END":
                mode_current = mode_under_dev.UnderDevelopment(_screen)


if __name__ == '__main__':
    ActionGame(mode_initial)
