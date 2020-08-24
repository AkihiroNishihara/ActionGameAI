import pygame
from pygame.locals import *
import sys

def start(screen):
    font = pygame.font.Font(None, 55)
    mode_next = "STAGE"

    while(1):
        screen.fill((0, 0, 255))
        text = font.render("TEST", True, (255, 255, 255))
        screen.blit(text, [20, 100])
        pygame.display.update()

        #イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

