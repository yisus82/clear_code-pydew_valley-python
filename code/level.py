import pygame
from pytmx.util_pygame import load_pygame

from os import path
from random import randint

from camera_group import CameraGroup
from menu import Menu
from overlay import Overlay
from player import Player
from sky import Rain, Sky
from soil import SoilLayer
from sprites import Generic, Interactive, Particle, Tree, Water, WildFlower
from settings import LAYERS, TILESIZE
from transition import Transition
from utils import import_folder


class Level:
    def __init__(self):
        self.player = None
        self.display_surface = pygame.display.get_surface()
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.load_map()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0, 10) > 3
        self.soil_layer.raining = self.raining
        self.sky = Sky()
        self.shop_active = False
        self.menu = Menu(self.player, self.toggle_shop)
        self.background_music = pygame.mixer.Sound(path.join("..", "audio", "music.mp3"))
        self.background_music.set_volume(0.5)
        self.background_music.play(loops=-1)
        self.success_sound = pygame.mixer.Sound(path.join("..", "audio", "success.wav"))
        self.success_sound.set_volume(0.3)

    def load_map(self):
        map_path = path.join("..", "map", "map.tmx")
        tmx_data = load_pygame(map_path)

        # house
        for layer in ["HouseFloor", "HouseFurnitureBottom"]:
            for x, y, surface in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILESIZE, y * TILESIZE), surface, [self.all_sprites], LAYERS["house_bottom"])

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
                 obj.name.lower(), self.player_add)

        # wild flowers
        for obj in tmx_data.get_layer_by_name("Decoration"):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        # collision tiles
        for x, y, surface in tmx_data.get_layer_by_name("Collision").tiles():
            Generic((x * TILESIZE, y * TILESIZE), surface, [self.collision_sprites])

        # player
        for obj in tmx_data.get_layer_by_name("Player"):
            if obj.name == "Start":
                self.player = Player((obj.x, obj.y), [self.all_sprites], self.collision_sprites,
                                     self.tree_sprites, self.interaction_sprites, self.soil_layer, self.toggle_shop)
            if obj.name == "Bed":
                Interactive((obj.x, obj.y), (obj.width, obj.height), [self.interaction_sprites],
                            obj.name)

            if obj.name == "Trader":
                Interactive((obj.x, obj.y), (obj.width, obj.height), [self.interaction_sprites],
                            obj.name)

        # ground
        ground_path = path.join("..", "graphics", "world", "ground.png")
        Generic((0, 0), pygame.image.load(ground_path).convert_alpha(), [self.all_sprites],
                LAYERS["ground"])

    def check_plant_collisions(self):
        for plant in self.soil_layer.plant_sprites.sprites():
            if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                self.player_add(plant.plant_type)
                plant.kill()
                Particle(plant.rect.topleft, plant.image, [self.all_sprites], LAYERS["main"])
                self.soil_layer.grid[plant.rect.centery // TILESIZE][plant.rect.centerx // TILESIZE].has_plant = False

    def run(self):
        self.display_surface.fill("black")
        self.all_sprites.custom_draw(self.player)
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update()
            self.check_plant_collisions()
        self.overlay.display()
        if self.raining and not self.shop_active:
            self.rain.update()
        self.sky.display()
        if self.player.sleeping:
            self.transition.play()

    def player_add(self, item, amount=1):
        self.player.item_inventory[item] += amount
        self.success_sound.play()

    def toggle_shop(self):
        self.shop_active = not self.shop_active

    def reset(self):
        # sky
        self.sky.reset()

        # plants
        self.soil_layer.update_plants()

        # fruits on trees
        for tree in self.tree_sprites.sprites():
            if tree.health > 0:
                tree.health = 5
                for fruit in tree.fruit_sprites.sprites():
                    fruit.kill()
                tree.create_fruits()

        # soil
        self.soil_layer.remove_water()
        self.raining = randint(0, 10) > 3
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()
