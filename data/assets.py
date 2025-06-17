# data/assets.py

import pygame
import os
from data.settings import *

SOUNDS = {}
CARD_IMAGES = {} # Новый словарь для хранения изображений карточек

def load_all_resources():
    """ Загружает все звуки и изображения для карточек один раз при запуске. """
    # Загрузка звуков
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

    # Загрузка изображений для карточек
    all_units = {**DEFENDERS_DATA, **ENEMIES_DATA, **NEURO_MOWERS_DATA, **CALAMITIES_DATA}
    for unit_type, data in all_units.items():
        anim_data = data.get('animation_data')
        if anim_data:
            # Если есть анимация, берем первый кадр из нее для карточки
            all_frames = parse_spritesheet(anim_data['file'], anim_data['cols'], anim_data['rows'], (SHOP_CARD_SIZE - 10, SHOP_CARD_SIZE - 10))
            CARD_IMAGES[unit_type] = all_frames[0]
        else:
            # Если анимации нет, просто грузим одно изображение
            CARD_IMAGES[unit_type] = load_image(f"{unit_type}.png", DEFAULT_COLORS.get(unit_type, RED), (SHOP_CARD_SIZE - 10, SHOP_CARD_SIZE - 10))


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

def parse_spritesheet(filename, cols, rows, size):
    try:
        spritesheet = load_image(filename, None, None)
        if spritesheet is None: raise FileNotFoundError

        frames = []
        sheet_width, sheet_height = spritesheet.get_size()
        frame_width = sheet_width / cols
        frame_height = sheet_height / rows

        for row in range(rows):
            for col in range(cols):
                rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                frame = pygame.Surface(rect.size, pygame.SRCALPHA)
                frame.blit(spritesheet, (0, 0), rect)
                frame = pygame.transform.scale(frame, size)
                frames.append(frame)
        return frames
    except (pygame.error, FileNotFoundError, TypeError):
         print(f"Warning: Spritesheet '{filename}' not found or invalid. Using fallback.")
         fallback_frame = pygame.Surface(size)
         fallback_frame.fill(DEFAULT_COLORS.get(filename.split('.')[0], RED))
         return [fallback_frame]