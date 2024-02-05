import pygame

from settings import TILESIZE, LAYERS


class Generic(pygame.sprite.Sprite):
    def __init__(self, position, surface=pygame.Surface((TILESIZE, TILESIZE)), groups=[], sorting_layer=LAYERS['main']):
        super().__init__(groups)
        self.position = position
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.sorting_layer = sorting_layer


class Tree(Generic):
    def __init__(self, position, surface, groups, name):
        super().__init__(position, surface, groups)
        self.name = name


class Water(Generic):
    def __init__(self, position, frames=[pygame.Surface((TILESIZE, TILESIZE))], groups=[]):
        super().__init__(position, frames[0], groups, LAYERS['water'])
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = 0.05
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=position)

    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.position)

    def update(self):
        self.animate()


class WildFlower(Generic):
    def __init__(self, position, surface, groups):
        super().__init__(position, surface, groups)
