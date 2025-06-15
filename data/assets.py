# data/assets.py

import pygame
import os
from data.settings import *

SOUNDS = {}

def load_image(filename, default_color, size=None):
    path = os.path.join(IMAGES_DIR, filename)
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except (pygame.error, FileNotFoundError):
        print(f"Warning: Image '{path}' not found. Using fallback color.")
        if size is None:
            size = (CELL_SIZE_W, CELL_SIZE_H)
        fallback_surface = pygame.Surface(size)
        fallback_surface.fill(default_color)
        return fallback_surface

def load_sound(name, filename):
    path = os.path.join(ASSETS_DIR, 'sounds', filename)
    try:
        sound = pygame.mixer.Sound(path)
        SOUNDS[name] = sound
    except (pygame.error, FileNotFoundError):
        print(f"Warning: Sound '{path}' not found. Sound will not be played.")
        SOUNDS[name] = None