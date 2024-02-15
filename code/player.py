import pygame

from os import path

from settings import LAYERS, PLAYER_TOOL_OFFSET
from timer import Timer
from utils import import_folder


class Player(pygame.sprite.Sprite):
    def __init__(self, position, groups, collision_sprites, tree_sprites, interaction_sprites):
        super().__init__(groups)
        self.collision_sprites = collision_sprites
        self.tree_sprites = tree_sprites
        self.interaction_sprites = interaction_sprites
        self.sorting_layer = LAYERS["main"]
        self.animations = {}
        self.import_animations()
        self.status = "down_idle"
        self.frame_index = 0
        self.animation_speed = 0.05
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = self.rect.inflate(-125, -70)
        self.speed = 5.0
        self.direction = pygame.math.Vector2()
        self.tools = ["axe", "hoe", "water"]
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        self.target_position = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
        self.seeds = ["corn", "tomato"]
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]
        self.sleeping = False
        self.item_inventory = {
            "wood": 0,
            "apple": 0,
            "corn": 0,
            "tomato": 0,
        }
        self.timers = {
            "select_tool": Timer(200),
            "use_tool": Timer(500, self.use_tool),
            "select_seed": Timer(200),
            "plant_seed": Timer(500, self.plant_seed),
        }

    def import_animations(self):
        player_folder = path.join("..", "graphics", "player")
        self.animations = {
            "down": [],
            "down_axe": [],
            "down_hoe": [],
            "down_idle": [],
            "down_water": [],
            "left": [],
            "left_axe": [],
            "left_hoe": [],
            "left_idle": [],
            "left_water": [],
            "right": [],
            "right_axe": [],
            "right_hoe": [],
            "right_idle": [],
            "right_water": [],
            "up": [],
            "up_axe": [],
            "up_hoe": [],
            "up_idle": [],
            "up_water": [],
        }
        for animation_name in self.animations.keys():
            animation_folder = path.join(player_folder, animation_name)
            self.animations[animation_name] = import_folder(animation_folder)

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def input(self):
        if self.sleeping:
            self.frame_index = 0
            self.direction.x = 0
            self.direction.y = 0
            self.status = "down_idle"
            return
        keys = pygame.key.get_pressed()
        if not self.timers["use_tool"].active and not self.timers["plant_seed"].active:
            if keys[pygame.K_j]:
                self.frame_index = 0
                self.direction.x = 0
                self.direction.y = 0
                self.timers["use_tool"].activate()
            elif keys[pygame.K_k]:
                self.frame_index = 0
                self.direction.x = 0
                self.direction.y = 0
                self.timers["plant_seed"].activate()
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
                if keys[pygame.K_q] and not self.timers["select_tool"].active:
                    self.timers["select_tool"].activate()
                    self.tool_index = (self.tool_index + 1) % len(self.tools)
                    self.selected_tool = self.tools[self.tool_index]
                if keys[pygame.K_e] and not self.timers["select_seed"].active:
                    self.timers["select_seed"].activate()
                    self.seed_index = (self.seed_index + 1) % len(self.seeds)
                    self.selected_seed = self.seeds[self.seed_index]
                if keys[pygame.K_RETURN]:
                    collided_interactive = pygame.sprite.spritecollideany(self, self.interaction_sprites)
                    if collided_interactive is not None:
                        if collided_interactive.name == "Bed":
                            self.hitbox.center = collided_interactive.rect.center
                            self.rect.center = self.hitbox.center
                            self.sleeping = True

    def update_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            self.status = self.status.split("_")[0] + "_idle"
        elif self.direction.x == 1 and self.direction.y == 0:
            self.status = "right"
        elif self.direction.x == -1 and self.direction.y == 0:
            self.status = "left"
        elif self.direction.y > 0:
            self.status = "down"
        elif self.direction.y < 0:
            self.status = "up"
        if self.selected_tool is not None and self.timers["use_tool"].active:
            self.status = self.status.split("_")[0] + "_" + self.selected_tool

    def collide(self, direction):
        if self.rect is not None:
            if direction == "horizontal":
                for sprite in self.collision_sprites:
                    if sprite.hitbox.colliderect(self.hitbox):
                        if self.direction.x > 0:  # moving right
                            self.hitbox.right = sprite.hitbox.left
                        elif self.direction.x < 0:  # moving left
                            self.hitbox.left = sprite.hitbox.right
            elif direction == "vertical":
                for sprite in self.collision_sprites:
                    if sprite.hitbox.colliderect(self.hitbox):
                        if self.direction.y > 0:  # moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        elif self.direction.y < 0:  # moving up
                            self.hitbox.top = sprite.hitbox.bottom

    def move(self):
        if self.rect is not None:
            if self.direction.magnitude() != 0:
                self.direction = self.direction.normalize()
            self.hitbox.move_ip(self.direction.x * self.speed, 0)
            self.collide("horizontal")
            self.hitbox.move_ip(0, self.direction.y * self.speed)
            self.collide("vertical")
            self.rect.center = self.hitbox.center

    def update_target_position(self):
        self.target_position = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    def use_tool(self):
        if self.selected_tool == "axe":
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_position):
                    tree.take_damage()
        elif self.selected_tool == "hoe":
            pass
        elif self.selected_tool == "water":
            pass

    def plant_seed(self):
        print(self.selected_seed, "planted")

    def animate(self):
        if self.status in self.animations:
            animation = self.animations[self.status]
            self.frame_index += self.animation_speed
            if self.frame_index >= len(animation):
                self.frame_index = 0
            self.image = animation[int(self.frame_index)]
            self.rect = self.image.get_rect(center=self.hitbox.center)

    def update(self):
        self.update_timers()
        self.input()
        self.update_status()
        self.move()
        self.update_target_position()
        self.animate()

    def draw(self, display_surface):
        display_surface.blit(self.image, self.rect)
