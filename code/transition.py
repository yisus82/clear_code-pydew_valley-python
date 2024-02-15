import pygame


class Transition:
    def __init__(self, reset, player):
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player
        self.image = pygame.Surface((self.display_surface.get_width(), self.display_surface.get_height()))
        self.color = 255
        self.speed = -2

    def play(self):
        self.color += self.speed
        if self.color <= 0:
            self.speed *= -1
            self.color = 0
            self.reset()
        elif self.color > 255:
            self.color = 255
            self.player.sleeping = False
            self.speed = -2
        self.image.fill((self.color, self.color, self.color))
        self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)