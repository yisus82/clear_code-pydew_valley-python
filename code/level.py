import pygame

from os import path

from camera_group import CameraGroup
from overlay import Overlay
from player import Player
from sprites import Generic
from settings import LAYERS


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()
        self.player = Player((self.display_surface.get_width() / 2, self.display_surface.get_height() / 2),
                             [self.all_sprites])
        ground_path = path.join('..', 'graphics', 'world', 'ground.png')
        self.ground = Generic((0, 0), pygame.image.load(ground_path).convert_alpha(), [self.all_sprites],
                              LAYERS['ground'])
        self.overlay = Overlay(self.player)

    def run(self):
        self.display_surface.fill("black")
        self.all_sprites.update()
        self.all_sprites.custom_draw(self.player)
        self.overlay.display()
