import pygame

from os import path, walk


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
