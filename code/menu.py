import pygame

from os import path

from settings import PURCHASE_PRICES, SALE_PRICES
from timer import Timer


class Menu:
    def __init__(self, player, toggle_menu):
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        font_path = path.join("..", "font", "LycheeSoda.ttf")
        self.font = pygame.font.Font(font_path, 30)
        self.width = 400
        self.space = 10
        self.padding = 8
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.item_inventory) - 1
        self.text_surfaces = []
        self.total_height = 0
        for item in self.options:
            text_surface = self.font.render(item, False, "Black")
            self.text_surfaces.append(text_surface)
            self.total_height += text_surface.get_height() + (self.padding * 2)
        self.total_height += (len(self.text_surfaces) - 1) * self.space
        self.menu_top = self.display_surface.get_height() / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(self.display_surface.get_width() / 2 - self.width / 2, self.menu_top, self.width,
                                     self.total_height)
        self.buy_text = self.font.render("buy", False, "Black")
        self.sell_text = self.font.render("sell", False, "Black")
        self.selected_index = 0
        self.timer = Timer(200)

    def display_money(self):
        text_surface = self.font.render(f"${self.player.money}", False, "Black")
        text_rect = text_surface.get_rect(midbottom=(self.display_surface.get_width() / 2, self.menu_top - 50))
        pygame.draw.rect(self.display_surface, "White", text_rect.inflate(10, 10), 0, 4)
        self.display_surface.blit(text_surface, text_rect)

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_m]:
            self.toggle_menu()
        if not self.timer.active:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.selected_index = (self.selected_index - 1) % len(self.options)
                self.timer.activate()
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.selected_index = (self.selected_index + 1) % len(self.options)
                self.timer.activate()
            if keys[pygame.K_SPACE]:
                self.timer.activate()
                # get item
                current_item = self.options[self.selected_index]
                # sell
                if self.selected_index <= self.sell_border:
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += SALE_PRICES[current_item]
                # buy
                else:
                    if self.player.money >= PURCHASE_PRICES[current_item]:
                        self.player.seed_inventory[current_item] += 1
                        self.player.money -= PURCHASE_PRICES[current_item]

    def show_entry(self, text_surface, amount, top, selected):
        # background
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surface.get_height() + (self.padding * 2))
        pygame.draw.rect(self.display_surface, "White", bg_rect, 0, 4)

        # text
        text_rect = text_surface.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surface, text_rect)

        # amount
        amount_surf = self.font.render(str(amount), False, "Black")
        amount_rect = amount_surf.get_rect(midright=(self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)

        # selected
        if selected:
            pygame.draw.rect(self.display_surface, "black", bg_rect, 4, 4)
            pos_rect = self.sell_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))
            # sell
            if self.selected_index <= self.sell_border:
                self.display_surface.blit(self.sell_text, pos_rect)
            # buy
            else:
                self.display_surface.blit(self.buy_text, pos_rect)

    def display_items(self):
        for text_index, text_surface in enumerate(self.text_surfaces):
            top = self.main_rect.top + text_index * (text_surface.get_height() + (self.padding * 2) + self.space)
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
            amount = amount_list[text_index]
            self.show_entry(text_surface, amount, top, self.selected_index == text_index)

    def update(self):
        self.timer.update()
        self.input()
        self.display_money()
        self.display_items()
