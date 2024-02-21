import pygame

from os import path
from pytmx.util_pygame import load_pygame

from settings import LAYERS, TILESIZE
from utils import import_folder_as_dict


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.sorting_layer = LAYERS["soil"]


class SoilCell:
    def __init__(self, x, y, farmable=False, has_patch=False):
        self.x = x
        self.y = y
        self.farmable = farmable
        self.has_patch = has_patch

    def __repr__(self):
        attributes = []
        if self.farmable:
            attributes.append("F")
        if self.has_patch:
            attributes.append("X")
        return attributes.__repr__()


class SoilLayer:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        soil_path = path.join("..", "graphics", "soil")
        self.soil_surfaces = import_folder_as_dict(soil_path)
        self.grid = []
        self.create_grid()
        self.hit_rects = []
        self.create_hit_rects()

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
                    tile_type = 'o'

                    # all sides
                    if all((t, r, b, l)):
                        tile_type = 'x'

                    # horizontal tiles only
                    if l and not any((t, r, b)):
                        tile_type = 'r'
                    if r and not any((t, l, b)):
                        tile_type = 'l'
                    if r and l and not any((t, b)):
                        tile_type = 'lr'

                    # vertical only
                    if t and not any((r, l, b)):
                        tile_type = 'b'
                    if b and not any((r, l, t)):
                        tile_type = 't'
                    if b and t and not any((r, l)):
                        tile_type = 'tb'

                    # corners
                    if l and b and not any((t, r)):
                        tile_type = 'tr'
                    if r and b and not any((t, l)):
                        tile_type = 'tl'
                    if l and t and not any((b, r)):
                        tile_type = 'br'
                    if r and t and not any((b, l)):
                        tile_type = 'bl'

                    # T shapes
                    if all((t, b, r)) and not l:
                        tile_type = 'tbr'
                    if all((t, b, l)) and not r:
                        tile_type = 'tbl'
                    if all((l, r, t)) and not b:
                        tile_type = 'lrb'
                    if all((l, r, b)) and not t:
                        tile_type = 'lrt'

                    SoilTile((index_col * TILESIZE, index_row * TILESIZE), self.soil_surfaces[tile_type],
                             [self.all_sprites, self.soil_sprites])
