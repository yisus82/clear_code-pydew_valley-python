import pygame

from os import path
from random import choice

from settings import FRUIT_POSITIONS, TILESIZE, LAYERS
from timer import Timer


class Generic(pygame.sprite.Sprite):
    def __init__(self, position, surface=pygame.Surface((TILESIZE, TILESIZE)), groups=[], sorting_layer=LAYERS["main"]):
        super().__init__(groups)
        self.position = position
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)
        self.sorting_layer = sorting_layer
        self.sprite_type = "generic"


class Interactive(Generic):
    def __init__(self, pos, size, groups, name):
        super().__init__(pos, pygame.Surface(size), groups)
        self.name = name


class Particle(Generic):
    def __init__(self, position, surface, groups, sorting_layer, duration=200):
        super().__init__(position, surface, groups, sorting_layer)
        self.sprite_type = "particle"
        mask_surface = pygame.mask.from_surface(self.image)
        new_surface = mask_surface.to_surface()
        new_surface.set_colorkey((0, 0, 0))
        self.image = new_surface
        self.timer = Timer(duration, self.kill)
        self.timer.activate()

    def update(self):
        self.timer.update()


class Tree(Generic):
    def __init__(self, position, surface, groups, size, player_add):
        super().__init__(position, surface, groups)
        self.size = size
        self.player_add = player_add
        self.sprite_type = "tree"
        self.health = 5
        self.alive = True
        stump_path = path.join("..", "graphics", "stumps", f"{self.size}.png")
        self.stump_surface = pygame.image.load(stump_path).convert_alpha()

        # fruits
        fruit_path = path.join("..", "graphics", "fruits", "apple.png")
        self.fruit_surface = pygame.image.load(fruit_path).convert_alpha()
        self.fruit_positions = FRUIT_POSITIONS[self.size]
        self.fruit_sprites = pygame.sprite.Group()
        self.create_fruits()

    def take_damage(self, damage=1):
        self.health -= damage

        # remove a fruit
        if len(self.fruit_sprites.sprites()) > 0:
            random_fruit = choice(self.fruit_sprites.sprites())
            Particle(random_fruit.rect.topleft, random_fruit.image, [self.groups()[0]], LAYERS["fruit"])
            self.player_add("apple")
            random_fruit.kill()

    def check_death(self):
        if self.health <= 0:
            Particle(self.rect.topleft, self.image, [self.groups()[0]], LAYERS["fruit"], 300)
            self.image = self.stump_surface
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.player_add("wood")
            self.alive = False

    def create_fruits(self):
        for position in self.fruit_positions:
            x = position[0] + self.rect.left
            y = position[1] + self.rect.top
            Generic((x, y), self.fruit_surface, [self.fruit_sprites, self.groups()[0]],
                    LAYERS["fruit"])

    def update(self):
        if self.alive:
            self.check_death()


class Water(Generic):
    def __init__(self, position, frames=[pygame.Surface((TILESIZE, TILESIZE))], groups=[]):
        super().__init__(position, frames[0], groups, LAYERS["water"])
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = 0.05
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=position)
        self.sprite_type = "water"

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
        self.hitbox = self.rect.inflate(-20, -self.rect.height * 0.9)
        self.sprite_type = "wild flower"
