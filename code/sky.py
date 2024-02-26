import pygame

from os import path
from random import randint, choice

from settings import LAYERS
from sprites import Generic
from timer import Timer
from utils import import_folder


class RainDrop(Generic):
    def __init__(self, surface, position, groups, sorting_layer, moving=False):
        super().__init__(position, surface, groups, sorting_layer)
        self.lifetime = randint(400, 500)
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250) / 100
        self.timer = Timer(self.lifetime, self.kill)
        self.timer.activate()

    def update(self):
        if self.moving:
            self.pos += self.direction * self.speed
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.timer.update()


class Rain:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        rain_drops_path = path.join("..", "graphics", "rain", "drops")
        self.rain_drops_surfaces = import_folder(rain_drops_path)
        rain_floor_path = path.join("..", "graphics", "rain", "floor")
        self.rain_floor_surfaces = import_folder(rain_floor_path)
        ground_path = path.join("..", "graphics", "world", "ground.png")
        ground = pygame.image.load("../graphics/world/ground.png")
        self.floor_width = ground.get_width()
        self.floor_height = ground.get_height()

    def create_floor(self):
        RainDrop(choice(self.rain_floor_surfaces),
                 (randint(0, self.floor_width), randint(0, self.floor_height)),
                 [self.all_sprites], LAYERS["rain_floor"])

    def create_drops(self):
        RainDrop(choice(self.rain_drops_surfaces),
                 (randint(0, self.floor_width), randint(0, self.floor_height)),
                 [self.all_sprites], LAYERS["rain_drops"], True)

    def update(self):
        self.create_floor()
        self.create_drops()


class Sky:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.full_surface = pygame.Surface((self.display_surface.get_width(), self.display_surface.get_height()))
        self.start_color = (255, 255, 255)
        self.end_color = (38, 101, 189)
        self.current_color = [c for c in self.start_color]

    def display(self):
        for index, value in enumerate(self.end_color):
            if self.current_color[index] > value:
                self.current_color[index] -= 0.05
        self.full_surface.fill(self.current_color)
        self.display_surface.blit(self.full_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def reset(self):
        self.current_color = [c for c in self.start_color]
