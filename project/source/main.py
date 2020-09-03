# coding:utf-8
import pygame
import os
from project.source import mode_gamestage, header as h, mode_start, mode_under_dev

# START, STAGE, END
mode_initial = "START"


class ActionGame:
    def __init__(self, _mode_ini):
        self.MODE = _mode_ini
        pygame.init()
        pygame.display.set_caption("Action Game AI")
        _screen = pygame.display.set_mode((h.SCREEN_WIDTH, h.SCREEN_HEIGHT))

        mode_current = None
        actor = None
        num_stage = None
        while True:
            if self.MODE is "START":
                mode_current = mode_start.Start(_screen)
                self.MODE, actor, num_stage = mode_current.get_mode_next()
            elif self.MODE is "STAGE":
                mode_current = mode_gamestage.GameStage(_screen, _num_stage=num_stage, _actor=actor)
                # if actor is 'USER':
                #     mode_current = mode_gamestage.GameStage(_screen, stage1, _actor=actor)
                # elif actor is 'AI_MAIN':
                #     mode_current = mode_gamestage.GameStage(_screen, stage2, _actor=actor)
                # elif actor is 'AI_SUB':
                #     mode_current = mode_gamestage.GameStage(_screen, stage3, _actor=actor)
                self.MODE = mode_current.get_mode_next()
            elif self.MODE is "END":
                mode_current = mode_under_dev.UnderDevelopment(_screen)
                self.MODE = mode_current.get_mode_next()
            else:
                print("wrong MODE is selected\n")
                os.system('PAUSE')
                exit(-1)


if __name__ == '__main__':
    ActionGame(mode_initial)
