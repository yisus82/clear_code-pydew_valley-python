from os import path, walk
import pygame

from settings import TILESIZE


class Player(pygame.sprite.Sprite):
    def __init__(self, position, groups: list):
        super().__init__()
        self.groups = groups
        self.animations = {}
        self.import_animations()
        self.status = 'down_idle'
        self.frame_index = 0
        self.animation_speed = 0.05
        self.direction = pygame.math.Vector2()
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=position)
        self.speed = 5.0

    @staticmethod
    def import_folder(folder):
        pathname = path.normpath(folder)
        image_surfaces = []
        for _, _, filenames in walk(pathname):
            for filename in sorted(filenames):
                full_path = path.join(pathname, filename)
                try:
                    image_surface = pygame.image.load(full_path).convert_alpha()
                    image_surfaces.append(image_surface)
                except pygame.error:
                    pass
        return image_surfaces

    def import_animations(self):
        player_folder = path.join('..', 'graphics', 'player')
        self.animations = {
            'up': [],
            'up_idle': [],
            'down': [],
            'down_idle': [],
            'left': [],
            'left_idle': [],
            'right': [],
            'right_idle': [],
        }
        for animation_name in self.animations.keys():
            animation_folder = path.join(player_folder, animation_name)
            self.animations[animation_name] = self.import_folder(animation_folder)

    def input(self):
        keys = pygame.key.get_pressed()
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

    def move(self):
        if self.rect is not None:
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()
            self.rect.center = self.rect.center + self.direction * self.speed

    def animate(self):
        if self.status in self.animations:
            animation = self.animations[self.status]
            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                self.frame_index = 0
            self.image = animation[int(self.frame_index)]
            self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.input()
        self.update_status()
        self.move()
        self.animate()

    def draw(self, display_surface):
        display_surface.blit(self.image, self.rect)
