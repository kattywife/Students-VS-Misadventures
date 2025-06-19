# data/assets.py

import pygame
import os
from data.settings import *
from data.levels import LEVELS  # Импортируем уровни для получения ID

SOUNDS = {}
CARD_IMAGES = {}
PROJECTILE_IMAGES = {}
MUSIC = {}
UI_IMAGES = {}


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
    load_sound('lose', 'lose.mp3')
    load_sound('no_money', 'no_money.mp3')
    load_sound('thief_laugh', 'thief_laugh.mp3')


    # Загрузка музыки
    load_music('main_team', 'main_team.mp3')
    load_music('prep_screen', 'prep_screen.mp3')
    for level_id in LEVELS:
        load_music(f'level_{level_id}', f'level_{level_id}.mp3')


    UI_IMAGES['toggle_on'] = load_image('ui/toggle_on.png', GREEN, (120, 60))
    UI_IMAGES['toggle_off'] = load_image('ui/toggle_off.png', GREY, (120, 60))
    UI_IMAGES['title_plaque'] = load_image('ui/title_plaque.png', None, (900, 180))

    all_units = {**DEFENDERS_DATA, **ENEMIES_DATA, **NEURO_MOWERS_DATA, **CALAMITIES_DATA, **UI_ELEMENTS_DATA}
    card_size = (SHOP_CARD_SIZE - 10, SHOP_CARD_SIZE - 10)
    for unit_type, data in all_units.items():
        category = data.get('category')
        anim_data = data.get('animation_data')

        path_to_card_img = ""
        if category:
            if anim_data:
                folder = anim_data.get('folder', unit_type)
                if category == 'enemies':
                    path_to_card_img = os.path.join(category, folder, 'walk_0.png')
                else:
                    path_to_card_img = os.path.join(category, folder, 'idle_0.png')
            else:
                path_to_card_img = os.path.join(category, f"{unit_type}.png")

        if path_to_card_img:
            current_size = card_size
            if unit_type in UI_ELEMENTS_DATA:
                current_size = None

            CARD_IMAGES[unit_type] = load_image(path_to_card_img, DEFAULT_COLORS.get(unit_type), current_size)

    projectile_size = (30, 30)
    for p_type in CALCULUS_PROJECTILE_TYPES:
        path = os.path.join('projectiles', 'calculus_projectiles', f'{p_type}.png')
        PROJECTILE_IMAGES[p_type] = load_image(path, DEFAULT_COLORS['integral'], projectile_size)

    for p_type in PROGRAMMER_PROJECTILE_TYPES:
        path = os.path.join('projectiles', 'programmer_projectiles', f'{p_type}.png')
        PROJECTILE_IMAGES[p_type] = load_image(path, DEFAULT_COLORS['bracket'], projectile_size)


# data/assets.py

def load_image(path, default_color, size=None):
    full_path = os.path.join(IMAGES_DIR, path)
    try:
        image = pygame.image.load(full_path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except (pygame.error, FileNotFoundError):
        print(f"Warning: Image '{full_path}' not found. Using fallback surface.")
        if size is None:
            size = (CELL_SIZE_W, CELL_SIZE_H)
        fallback_surface = pygame.Surface(size)

        # --- ИЗМЕНЕНИЕ: Проверяем, есть ли цвет, перед заливкой ---
        if default_color:
            fallback_surface.fill(default_color)
        else:
            # Если цвета нет, заливаем ярким цветом для отладки
            fallback_surface.fill((255, 0, 255))

        return fallback_surface

def load_sound(name, filename):
    path = os.path.join(ASSETS_DIR, 'sounds', filename)
    try:
        sound = pygame.mixer.Sound(path)
        SOUNDS[name] = sound
    except (pygame.error, FileNotFoundError):
        print(f"Warning: Sound '{path}' not found. Sound will not be played.")
        SOUNDS[name] = None


def load_music(name, filename):
    path = os.path.join(ASSETS_DIR, 'sounds', 'music', filename)
    if os.path.exists(path):
        MUSIC[name] = path
    else:
        print(f"Warning: Music file '{path}' not found.")
        MUSIC[name] = None