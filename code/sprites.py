import pygame

from settings import TILESIZE, LAYERS


class Generic(pygame.sprite.Sprite):
    def __init__(self, position, surface=pygame.Surface((TILESIZE, TILESIZE)), groups=[], sorting_layer=LAYERS['main']):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.sorting_layer = sorting_layer
