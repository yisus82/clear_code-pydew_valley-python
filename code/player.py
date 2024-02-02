import pygame

from os import path

from utils import import_folder
from timer import Timer


class Player(pygame.sprite.Sprite):
    def __init__(self, position, groups: list):
        super().__init__()
        for group in groups:
            group.add(self)
        self.animations = {}
        self.import_animations()
        self.status = 'down_idle'
        self.frame_index = 0
        self.animation_speed = 0.05
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=position)
        self.speed = 5.0
        self.direction = pygame.math.Vector2()
        self.position = pygame.math.Vector2(self.rect.center)
        self.tools = ['axe', 'hoe', 'water']
        self.selected_tool = None
        self.seeds = ['corn', 'tomato']
        self.selected_seed = None
        self.timers = {
            'use_tool': Timer(500, self.use_tool),
            'plant_seed': Timer(500, self.plant_seed),
        }

    def import_animations(self):
        player_folder = path.join('..', 'graphics', 'player')
        self.animations = {
            'down': [],
            'down_axe': [],
            'down_hoe': [],
            'down_idle': [],
            'down_water': [],
            'left': [],
            'left_axe': [],
            'left_hoe': [],
            'left_idle': [],
            'left_water': [],
            'right': [],
            'right_axe': [],
            'right_hoe': [],
            'right_idle': [],
            'right_water': [],
            'up': [],
            'up_axe': [],
            'up_hoe': [],
            'up_idle': [],
            'up_water': [],
        }
        for animation_name in self.animations.keys():
            animation_folder = path.join(player_folder, animation_name)
            self.animations[animation_name] = import_folder(animation_folder)

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.timers['use_tool'].active and not self.timers['plant_seed'].active:
            if keys[pygame.K_j] and self.selected_tool is not None:
                self.frame_index = 0
                self.direction.x = 0
                self.direction.y = 0
                self.timers['use_tool'].activate()
            elif keys[pygame.K_k] and self.selected_seed is not None:
                self.frame_index = 0
                self.direction.x = 0
                self.direction.y = 0
                self.timers['plant_seed'].activate()
            else:
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.direction.y = -1
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.direction.y = 1
                else:
                    self.direction.y = 0
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.direction.x = 1
                elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.direction.x = -1
                else:
                    self.direction.x = 0
                if keys[pygame.K_1]:
                    self.selected_tool = self.tools[0]
                elif keys[pygame.K_2]:
                    self.selected_tool = self.tools[1]
                elif keys[pygame.K_3]:
                    self.selected_tool = self.tools[2]
                elif keys[pygame.K_4]:
                    self.selected_tool = None
                if keys[pygame.K_6]:
                    self.selected_seed = self.seeds[0]
                elif keys[pygame.K_7]:
                    self.selected_seed = self.seeds[1]
                elif keys[pygame.K_8]:
                    self.selected_seed = None

    def update_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            self.status = self.status.split('_')[0] + '_idle'
        elif self.direction.x == 1 and self.direction.y == 0:
            self.status = 'right'
        elif self.direction.x == -1 and self.direction.y == 0:
            self.status = 'left'
        elif self.direction.y > 0:
            self.status = 'down'
        elif self.direction.y < 0:
            self.status = 'up'
        if self.selected_tool is not None and self.timers['use_tool'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def move(self):
        if self.rect is not None:
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()

            self.position.x += self.direction.x * self.speed
            self.rect.centerx = self.position.x

            self.position.y += self.direction.y * self.speed
            self.rect.centery = self.position.y

    def use_tool(self):
        print(self.selected_tool, 'used')

    def plant_seed(self):
        print(self.selected_seed, 'planted')

    def animate(self):
        if self.status in self.animations:
            animation = self.animations[self.status]
            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                self.frame_index = 0
            self.image = animation[int(self.frame_index)]
            self.rect = self.image.get_rect(center=self.position)

    def update(self):
        self.update_timers()
        self.input()
        self.update_status()
        self.move()
        self.animate()

    def draw(self, display_surface):
        display_surface.blit(self.image, self.rect)
