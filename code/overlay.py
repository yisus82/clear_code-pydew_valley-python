import pygame

from os import path

from settings import ITEM_BOX_BORDER_WIDTH, ITEM_BOX_SIZE, OVERLAY_OFFSETS, UI_BG_COLOR, UI_BORDER_COLOR


class Overlay:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.tools = {}
        self.import_tools()
        self.seeds = {}
        self.import_seeds()

    def import_tools(self):
        overlay_path = path.join("..", "graphics", "overlay")
        tools_path = path.join(overlay_path, "tools")
        for tool in self.player.tools:
            tool_surface = pygame.image.load(path.join(tools_path, f"{tool}.png")).convert_alpha()
            self.tools[tool] = tool_surface

    def import_seeds(self):
        overlay_path = path.join("..", "graphics", "overlay")
        seeds_path = path.join(overlay_path, "seeds")
        for seed in self.player.seeds:
            seed_surface = pygame.image.load(path.join(seeds_path, f"{seed}.png")).convert_alpha()
            self.seeds[seed] = seed_surface

    def draw_selection_box(self, x, y, image=None):
        box_rect = pygame.Rect(x, y, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, box_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR,
                         box_rect, ITEM_BOX_BORDER_WIDTH)
        if image is not None:
            image_rect = image.get_rect(center=box_rect.center)
            self.display_surface.blit(image, image_rect)

    def display_seed(self):
        if self.player.selected_seed and self.player.selected_seed in self.player.seeds:
            seed_surface = self.seeds[self.player.selected_seed]
        else:
            seed_surface = None
        self.draw_selection_box(0 + OVERLAY_OFFSETS["seed"][0], self.display_surface.get_height()
                                + OVERLAY_OFFSETS["seed"][1], seed_surface)

    def display_tool(self):
        if self.player.selected_tool and self.player.selected_tool in self.player.tools:
            tool_surface = self.tools[self.player.selected_tool]
        else:
            tool_surface = None
        self.draw_selection_box(0 + OVERLAY_OFFSETS["tool"][0], self.display_surface.get_height()
                                + OVERLAY_OFFSETS["tool"][1], tool_surface)

    def display(self):
        self.display_tool()
        self.display_seed()
