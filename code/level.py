import pygame
from pytmx.util_pygame import load_pygame

from os import path

from camera_group import CameraGroup
from overlay import Overlay
from player import Player
from sprites import Generic, Tree, Water, WildFlower
from settings import LAYERS, TILESIZE
from utils import import_folder


class Level:
    def __init__(self):
        self.player = None
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.load_map()
        self.overlay = Overlay(self.player)

    def load_map(self):
        map_path = path.join("..", "map", "map.tmx")
        tmx_data = load_pygame(map_path)

        # house
        for layer in ["HouseFloor", "HouseFurnitureBottom"]:
            for x, y, surface in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILESIZE, y * TILESIZE), surface, [self.all_sprites], LAYERS["house bottom"])

        for layer in ["HouseWalls", "HouseFurnitureTop"]:
            for x, y, surface in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILESIZE, y * TILESIZE), surface, [self.all_sprites])

        # fence
        for x, y, surface in tmx_data.get_layer_by_name("Fence").tiles():
            Generic((x * TILESIZE, y * TILESIZE), surface, [self.all_sprites, self.collision_sprites])

        # water
        water_path = path.join("..", "graphics", "water")
        water_frames = import_folder(water_path)
        for x, y, surface in tmx_data.get_layer_by_name("Water").tiles():
            Water((x * TILESIZE, y * TILESIZE), water_frames, [self.all_sprites])

        # trees
        for obj in tmx_data.get_layer_by_name("Trees"):
            Tree((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites, self.tree_sprites],
                 obj.name.lower())

        # wild flowers
        for obj in tmx_data.get_layer_by_name("Decoration"):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        # collision tiles
        for x, y, surface in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILESIZE, y * TILESIZE), surface, [self.collision_sprites])

        # player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player((obj.x, obj.y), [self.all_sprites], self.collision_sprites,
                                     self.tree_sprites)

        # ground
        ground_path = path.join("..", "graphics", "world", "ground.png")
        Generic((0, 0), pygame.image.load(ground_path).convert_alpha(), [self.all_sprites],
                LAYERS["ground"])

    def run(self):
        self.display_surface.fill("black")
        self.all_sprites.update()
        self.all_sprites.custom_draw(self.player)
        self.overlay.display()
