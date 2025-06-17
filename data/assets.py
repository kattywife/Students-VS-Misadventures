# data/assets.py

import pygame
import os
from data.settings import *

SOUNDS = {}
CARD_IMAGES = {}


def load_all_resources():
    load_sound('button', 'pressing a button.mp3')
    load_sound('purchase', 'purchase and landing of the hero.mp3')
    load_sound('taking', 'taking.mp3')
    load_sound('cards', 'cards.mp3')
    load_sound('damage', 'damage.mp3')
    load_sound('eating', 'eating.mp3')
    load_sound('scream', 'scream.mp3')
    load_sound('enemy_dead', 'enemy_dead.mp3')
    load_sound('hero_dead', 'hero_dead.mp3')
    load_sound('money', 'money.mp3')
    load_sound('win', 'win.mp3')
    load_sound('misfortune', 'misfortune.mp3')
    load_sound('tuning', 'tuning.mp3')

    all_units = {**DEFENDERS_DATA, **ENEMIES_DATA, **NEURO_MOWERS_DATA, **CALAMITIES_DATA, **UI_ELEMENTS_DATA}
    card_size = (SHOP_CARD_SIZE - 10, SHOP_CARD_SIZE - 10)
    for unit_type, data in all_units.items():
        category = data.get('category')
        anim_data = data.get('animation_data')

        # Собираем путь для карточки
        path_to_card_img = ""
        if anim_data:
            folder = anim_data.get('folder', unit_type)
            path_to_card_img = os.path.join(category, folder, 'idle_0.png')
        elif category:
            path_to_card_img = os.path.join(category, f"{unit_type}.png")

        if path_to_card_img:
            CARD_IMAGES[unit_type] = load_image(path_to_card_img, DEFAULT_COLORS.get(unit_type), card_size)


def load_image(path, default_color, size=None):
    # Теперь путь формируется относительно главной папки с картинками
    full_path = os.path.join(IMAGES_DIR, path)
    try:
        image = pygame.image.load(full_path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except (pygame.error, FileNotFoundError):
        print(f"Warning: Image '{full_path}' not found. Using fallback color.")
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