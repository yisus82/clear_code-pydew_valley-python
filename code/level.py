import pygame
from player import Player


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.player = Player((self.display_surface.get_width() / 2, self.display_surface.get_height() / 2), [])

    def run(self):
        self.display_surface.fill("black")
        self.player.update()
        self.player.draw(self.display_surface)
