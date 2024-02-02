import pygame

from player import Player
from overlay import Overlay


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = pygame.sprite.Group()
        self.player = Player((self.display_surface.get_width() / 2, self.display_surface.get_height() / 2),
                             [self.all_sprites])
        self.overlay = Overlay(self.player)

    def run(self):
        self.display_surface.fill("black")
        self.all_sprites.update()
        self.all_sprites.draw(self.display_surface)
        self.overlay.display()
