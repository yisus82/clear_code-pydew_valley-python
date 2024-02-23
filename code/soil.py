import pygame

from os import path
from pytmx.util_pygame import load_pygame
from random import choice

from settings import GROW_SPEED, LAYERS, TILESIZE
from utils import import_folder, import_folder_as_dict


class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered):
        super().__init__(groups)
        self.plant_type = plant_type
        seeds_path = path.join("..", "graphics", "seeds")
        self.frames = import_folder(path.join(seeds_path, plant_type))
        self.soil = soil
        self.check_watered = check_watered
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable = False
        self.image = self.frames[self.age]
        if plant_type == "corn":
            self.y_offset = -16
        else:
            self.y_offset = -8
        self.rect = self.image.get_rect(midbottom=soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
        self.sorting_layer = LAYERS["ground_plant"]
        self.hitbox = None

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed
            if int(self.age) > 0:
                self.sorting_layer = LAYERS["main"]
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)
            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True
            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.sorting_layer = LAYERS["soil"]


class SoilCell:
    def __init__(self, x, y, farmable=False, has_patch=False, has_water=False, has_plant=False):
        self.x = x
        self.y = y
        self.farmable = farmable
        self.has_patch = has_patch
        self.has_water = has_water
        self.has_plant = has_plant

    def __repr__(self):
        attributes = []
        if self.farmable:
            attributes.append("F")
        if self.has_patch:
            attributes.append("X")
        if self.has_water:
            attributes.append("W")
        if self.has_plant:
            attributes.append("P")
        return attributes.__repr__()


class SoilLayer:
    def __init__(self, all_sprites, collision_sprites):
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()
        soil_path = path.join("..", "graphics", "soil")
        self.soil_surfaces = import_folder_as_dict(soil_path)
        soil_water_path = path.join("..", "graphics", "soil_water")
        self.water_surfaces = import_folder(soil_water_path)
        self.grid = []
        self.create_grid()
        self.hit_rects = []
        self.create_hit_rects()
        self.raining = False

    def create_grid(self):
        ground_path = path.join("..", "graphics", "world", "ground.png")
        ground = pygame.image.load(ground_path).convert_alpha()
        num_horizontal_tiles = ground.get_width() // TILESIZE
        num_vertical_tiles = ground.get_height() // TILESIZE
        self.grid = [[SoilCell(col, row) for col in range(num_horizontal_tiles)] for row in range(num_vertical_tiles)]
        map_path = path.join("..", "map", "map.tmx")
        for x, y, _ in load_pygame(map_path).get_layer_by_name("Farmable").tiles():
            self.grid[y][x].farmable = True

    def create_hit_rects(self):
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if cell.farmable:
                    x = index_col * TILESIZE
                    y = index_row * TILESIZE
                    rect = pygame.Rect(x, y, TILESIZE, TILESIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILESIZE
                y = rect.y // TILESIZE
                if self.grid[y][x].farmable and not self.grid[y][x].has_patch:
                    self.grid[y][x].has_patch = True
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()

    def create_water_tile(self, soil_sprite):
        x = soil_sprite.rect.x // TILESIZE
        y = soil_sprite.rect.y // TILESIZE
        if not self.grid[y][x].has_water:
            self.grid[y][x].has_water = True
            position = soil_sprite.rect.topleft
            surface = choice(self.water_surfaces)
            WaterTile(position, surface, [self.all_sprites, self.water_sprites])

    def water(self, target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                self.create_water_tile(soil_sprite)

    def water_all(self):
        for soil_sprite in self.soil_sprites.sprites():
            self.create_water_tile(soil_sprite)

    def remove_water(self):
        # destroy all water sprites
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        # clean up the grid
        for row in self.grid:
            for cell in row:
                if cell.has_water:
                    cell.has_water = False

    def check_watered(self, position):
        x = position[0] // TILESIZE
        y = position[1] // TILESIZE
        cell = self.grid[y][x]
        return cell.has_water

    def plant_seed(self, target_position, seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_position):
                x = soil_sprite.rect.x // TILESIZE
                y = soil_sprite.rect.y // TILESIZE
                if not self.grid[y][x].has_plant:
                    self.grid[y][x].has_plant = True
                    Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite,
                          self.check_watered)

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if cell.has_patch:
                    # tile neighbors
                    t = self.grid[index_row - 1][index_col].has_patch
                    b = self.grid[index_row + 1][index_col].has_patch
                    r = row[index_col + 1].has_patch
                    l = row[index_col - 1].has_patch

                    # single tile
                    tile_type = "o"

                    # all sides
                    if all((t, r, b, l)):
                        tile_type = "x"

                    # horizontal tiles only
                    if l and not any((t, r, b)):
                        tile_type = "r"
                    if r and not any((t, l, b)):
                        tile_type = "l"
                    if r and l and not any((t, b)):
                        tile_type = "lr"

                    # vertical only
                    if t and not any((r, l, b)):
                        tile_type = "b"
                    if b and not any((r, l, t)):
                        tile_type = "t"
                    if b and t and not any((r, l)):
                        tile_type = "tb"

                    # corners
                    if l and b and not any((t, r)):
                        tile_type = "tr"
                    if r and b and not any((t, l)):
                        tile_type = "tl"
                    if l and t and not any((b, r)):
                        tile_type = "br"
                    if r and t and not any((b, l)):
                        tile_type = "bl"

                    # T shapes
                    if all((t, b, r)) and not l:
                        tile_type = "tbr"
                    if all((t, b, l)) and not r:
                        tile_type = "tbl"
                    if all((l, r, t)) and not b:
                        tile_type = "lrb"
                    if all((l, r, b)) and not t:
                        tile_type = "lrt"

                    SoilTile((index_col * TILESIZE, index_row * TILESIZE), self.soil_surfaces[tile_type],
                             [self.all_sprites, self.soil_sprites])


class WaterTile(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.sorting_layer = LAYERS["soil_water"]
