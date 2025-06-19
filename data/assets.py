# data/assets.py

import pygame
import os
from data.settings import *
from data.levels import LEVELS

# =============================================================================
# ГЛОБАЛЬНЫЕ СЛОВАРИ ДЛЯ ХРАНЕНИЯ АССЕТОВ
# =============================================================================
# Эти словари заполняются при вызове load_all_resources() и служат
# кэшем для всех загруженных ресурсов, чтобы избежать повторной загрузки
# с диска во время игры.

SOUNDS = {}
CARD_IMAGES = {}
PROJECTILE_IMAGES = {}
MUSIC = {}
UI_IMAGES = {}


def load_all_resources():
    """
    Главная функция для загрузки всех игровых ресурсов.
    Вызывается один раз при запуске игры.
    Заполняет глобальные словари SOUNDS, MUSIC, CARD_IMAGES и др.
    """
    # --- Загрузка звуковых эффектов (SFX) ---
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

    # --- Загрузка музыки ---
    load_music('main_team', 'main_team.mp3')
    load_music('prep_screen', 'prep_screen.mp3')
    # Динамическая загрузка музыки для каждого уровня на основе данных из levels.py
    for level_id in LEVELS:
        if level_id > 0:  # Не загружаем музыку для тестового уровня (ID 0)
            load_music(f'level_{level_id}', f'level_{level_id}.mp3')

    # --- Загрузка изображений для UI ---
    UI_IMAGES['toggle_on'] = load_image('ui/toggle_on.png', GREEN, SETTINGS_TOGGLE_SIZE)
    UI_IMAGES['toggle_off'] = load_image('ui/toggle_off.png', GREY, SETTINGS_TOGGLE_SIZE)
    UI_IMAGES['title_plaque'] = load_image('ui/title_plaque.png', None, TITLE_PLAQUE_SIZE)

    # --- Загрузка изображений для карточек юнитов ---
    # Объединяем все словари с данными юнитов в один для итерации
    all_units = {**DEFENDERS_DATA, **ENEMIES_DATA, **NEURO_MOWERS_DATA, **CALAMITIES_DATA, **UI_ELEMENTS_DATA}
    card_size = (SHOP_CARD_SIZE - 10, SHOP_CARD_SIZE - 10)  # Стандартный размер изображения на карточке

    for unit_type, data in all_units.items():
        category = data.get('category')
        anim_data = data.get('animation_data')
        path_to_card_img = ""

        if category:
            if anim_data:
                # Если у юнита есть анимации, берем первый кадр одной из них для карточки
                folder = anim_data.get('folder', unit_type)
                # Для врагов берем анимацию ходьбы, для остальных - ожидания
                anim_type_for_card = 'walk' if category == 'enemies' else 'idle'
                path_to_card_img = os.path.join(category, folder, f'{anim_type_for_card}_0.png')
            else:
                # Если анимаций нет, берем статичное изображение
                path_to_card_img = os.path.join(category, f"{unit_type}.png")

        if path_to_card_img:
            current_size = card_size
            # Для некоторых UI элементов не нужно менять размер
            if unit_type in UI_ELEMENTS_DATA:
                current_size = None

            CARD_IMAGES[unit_type] = load_image(path_to_card_img, DEFAULT_COLORS.get(unit_type), current_size)

    # --- Загрузка изображений для снарядов ---
    projectile_size = (30, 30)
    for p_type in CALCULUS_PROJECTILE_TYPES:
        path = os.path.join('projectiles', 'calculus_projectiles', f'{p_type}.png')
        PROJECTILE_IMAGES[p_type] = load_image(path, DEFAULT_COLORS['integral'], projectile_size)

    for p_type in PROGRAMMER_PROJECTILE_TYPES:
        path = os.path.join('projectiles', 'programmer_projectiles', f'{p_type}.png')
        PROJECTILE_IMAGES[p_type] = load_image(path, DEFAULT_COLORS['bracket'], projectile_size)


def load_image(path, default_color, size=None):
    """
    Загружает изображение из файла. Если файл не найден, создает и возвращает
    резервную поверхность заданного цвета, чтобы избежать падения игры.

    Args:
        path (str): Относительный путь к файлу изображения внутри папки `assets/images`.
        default_color (tuple | None): Цвет для резервной поверхности (fallback).
        size (tuple, optional): Кортеж (ширина, высота) для масштабирования.

    Returns:
        pygame.Surface: Загруженное и (опционально) масштабированное изображение.
    """
    full_path = os.path.join(IMAGES_DIR, path)
    try:
        image = pygame.image.load(full_path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except (pygame.error, FileNotFoundError):
        # Обработка ошибки, если файл не найден
        print(f"Warning: Image '{full_path}' not found. Using fallback surface.")
        if size is None:
            size = (CELL_SIZE_W, CELL_SIZE_H)
        fallback_surface = pygame.Surface(size, pygame.SRCALPHA)

        if default_color:
            fallback_surface.fill(default_color)
        else:
            # Если цвет не указан, делаем поверхность полностью прозрачной
            fallback_surface.fill((0, 0, 0, 0))

        return fallback_surface


def load_sound(name, filename):
    """
    Загружает звуковой эффект и добавляет его в глобальный словарь SOUNDS.
    Если файл не найден, выводит предупреждение.

    Args:
        name (str): Уникальное имя-ключ для доступа к звуку.
        filename (str): Имя файла в папке `assets/sounds`.
    """
    path = os.path.join(ASSETS_DIR, 'sounds', filename)
    try:
        sound = pygame.mixer.Sound(path)
        SOUNDS[name] = sound
    except (pygame.error, FileNotFoundError):
        print(f"Warning: Sound '{path}' not found. Sound will not be played.")
        SOUNDS[name] = None


def load_music(name, filename):
    """
    Загружает путь к музыкальному файлу и добавляет его в глобальный словарь MUSIC.
    Сама музыка загружается в память позже, при воспроизведении.

    Args:
        name (str): Уникальное имя-ключ для доступа к музыке.
        filename (str): Имя файла в папке `assets/sounds/music`.
    """
    path = os.path.join(ASSETS_DIR, 'sounds', 'music', filename)
    if os.path.exists(path):
        MUSIC[name] = path
    else:
        print(f"Warning: Music file '{path}' not found.")
        MUSIC[name] = None