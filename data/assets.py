# data/assets.py

import pygame
import os
import sys # <-- ДОБАВЛЕНО: для sys._MEIPASS
from data.settings import *
from data.levels import LEVELS

# =============================================================================
# ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ПРАВИЛЬНОГО ПУТИ К РЕСУРСАМ
# =============================================================================
def resource_path(relative_path):
    """
    Получить абсолютный путь к ресурсу, работает для разработки и для PyInstaller.
    'relative_path' должен быть путем относительно КОРНЯ ПРОЕКТА,
    например, "assets/images/player.png".
    """
    try:
        # PyInstaller создает временную папку и сохраняет путь в sys._MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # sys._MEIPASS не определен, значит мы запускаемся в обычном режиме Python
        base_path = os.path.abspath(".") # Корень проекта

    return os.path.join(base_path, relative_path)

# =============================================================================
# ГЛОБАЛЬНЫЕ СЛОВАРИ ДЛЯ ХРАНЕНИЯ АССЕТОВ
# =============================================================================
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
    for level_id in LEVELS:
        if level_id > 0:
            load_music(f'level_{level_id}', f'level_{level_id}.mp3')

    # --- Загрузка изображений для UI ---
    # Предполагается, что IMAGES_DIR - это что-то вроде "assets/images"
    # Тогда путь к ui/toggle_on.png будет IMAGES_DIR + 'ui/toggle_on.png'
    ui_toggle_on_path = 'ui/toggle_on.png'
    ui_toggle_off_path = 'ui/toggle_off.png'
    ui_title_plaque_path = 'ui/title_plaque.png'

    UI_IMAGES['toggle_on'] = load_image(ui_toggle_on_path, GREEN, SETTINGS_TOGGLE_SIZE)
    UI_IMAGES['toggle_off'] = load_image(ui_toggle_off_path, GREY, SETTINGS_TOGGLE_SIZE)
    UI_IMAGES['title_plaque'] = load_image(ui_title_plaque_path, None, TITLE_PLAQUE_SIZE)


    # --- Загрузка изображений для карточек юнитов ---
    all_units = {**DEFENDERS_DATA, **ENEMIES_DATA, **NEURO_MOWERS_DATA, **CALAMITIES_DATA, **UI_ELEMENTS_DATA}
    card_size = (SHOP_CARD_SIZE - 10, SHOP_CARD_SIZE - 10)

    for unit_type, data in all_units.items():
        category = data.get('category')
        anim_data = data.get('animation_data')
        relative_img_path_in_images_dir = "" # Путь ВНУТРИ папки IMAGES_DIR

        if category:
            if anim_data:
                folder = anim_data.get('folder', unit_type)
                anim_type_for_card = 'walk' if category == 'enemies' else 'idle'
                # Путь от папки IMAGES_DIR (e.g. assets/images)
                relative_img_path_in_images_dir = os.path.join(category, folder, f'{anim_type_for_card}_0.png')
            else:
                relative_img_path_in_images_dir = os.path.join(category, f"{unit_type}.png")
        print(relative_img_path_in_images_dir)
        if relative_img_path_in_images_dir:
            # Собираем полный путь от корня проекта
            #full_path_from_project_root = os.path.join(IMAGES_DIR, relative_img_path_in_images_dir)
            current_size = card_size
            if unit_type in UI_ELEMENTS_DATA:
                current_size = None
            CARD_IMAGES[unit_type] = load_image(relative_img_path_in_images_dir, DEFAULT_COLORS.get(unit_type), current_size)

    # --- Загрузка изображений для снарядов ---
    projectile_size = (30, 30)
    for p_type in CALCULUS_PROJECTILE_TYPES:
        # Путь от папки IMAGES_DIR (e.g. assets/images)
        path_in_images_dir = os.path.join('projectiles', 'calculus_projectiles', f'{p_type}.png')
        #full_path_from_project_root = os.path.join(IMAGES_DIR, path_in_images_dir)
        PROJECTILE_IMAGES[p_type] = load_image(path_in_images_dir, DEFAULT_COLORS['integral'], projectile_size)

    for p_type in PROGRAMMER_PROJECTILE_TYPES:
        path_in_images_dir = os.path.join('projectiles', 'programmer_projectiles', f'{p_type}.png')
        #full_path_from_project_root = os.path.join(IMAGES_DIR, path_in_images_dir)
        PROJECTILE_IMAGES[p_type] = load_image(path_in_images_dir, DEFAULT_COLORS['bracket'], projectile_size)


def load_image(path_from_project_root, default_color, size=None):
    """
    Загружает изображение из файла. Если файл не найден, создает и возвращает
    резервную поверхность заданного цвета.

    Args:
        path_from_project_root (str): Относительный путь к файлу изображения
                                      ОТ КОРНЯ ПРОЕКТА (например, "assets/images/ui/toggle_on.png").
        default_color (tuple | None): Цвет для резервной поверхности (fallback).
        size (tuple, optional): Кортеж (ширина, высота) для масштабирования.

    Returns:
        pygame.Surface: Загруженное и (опционально) масштабированное изображение.
    """
    # Теперь path_from_project_root - это уже полный относительный путь от корня проекта
    actual_path = resource_path(os.path.join("assets","images",path_from_project_root))
    try:
        image = pygame.image.load(actual_path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except (pygame.error, FileNotFoundError):
        print(f"Warning: Image '{actual_path}' (original relative: '{path_from_project_root}') not found. Using fallback surface.")
        if size is None:
            size = (CELL_SIZE_W, CELL_SIZE_H)
        fallback_surface = pygame.Surface(size, pygame.SRCALPHA)
        if default_color:
            fallback_surface.fill(default_color)
        else:
            fallback_surface.fill((0, 0, 0, 0))
        return fallback_surface


def load_sound(name, filename_in_sounds_dir):
    """
    Загружает звуковой эффект и добавляет его в глобальный словарь SOUNDS.

    Args:
        name (str): Уникальное имя-ключ для доступа к звуку.
        filename_in_sounds_dir (str): Имя файла в папке `ASSETS_DIR/sounds`.
    """
    # Предполагается, что ASSETS_DIR - это "assets" или类似, SOUNDS_DIR - "assets/sounds"
    # Мы ожидаем, что в settings.py есть что-то вроде:
    # SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')
    # path_from_project_root = os.path.join(SOUNDS_DIR, filename_in_sounds_dir)
    # Если ASSETS_DIR это "assets", тогда:
    path_from_project_root = os.path.join(ASSETS_DIR, 'sounds', filename_in_sounds_dir)
    actual_path = resource_path(path_from_project_root)
    try:
        sound = pygame.mixer.Sound(actual_path)
        SOUNDS[name] = sound
    except (pygame.error, FileNotFoundError):
        print(f"Warning: Sound '{actual_path}' (original relative: '{path_from_project_root}') not found. Sound will not be played.")
        SOUNDS[name] = None


def load_music(name, filename_in_music_dir):
    """
    Загружает путь к музыкальному файлу и добавляет его в глобальный словарь MUSIC.

    Args:
        name (str): Уникальное имя-ключ для доступа к музыке.
        filename_in_music_dir (str): Имя файла в папке `ASSETS_DIR/sounds/music`.
    """
    # MUSIC_DIR = os.path.join(ASSETS_DIR, 'sounds', 'music')
    # path_from_project_root = os.path.join(MUSIC_DIR, filename_in_music_dir)
    # Если ASSETS_DIR это "assets", тогда:
    path_from_project_root = os.path.join(ASSETS_DIR, 'sounds', 'music', filename_in_music_dir)
    actual_path = resource_path(path_from_project_root)

    if os.path.exists(actual_path): # Проверяем существование файла по актуальному пути
        MUSIC[name] = actual_path
    else:
        print(f"Warning: Music file '{actual_path}' (original relative: '{path_from_project_root}') not found.")
        MUSIC[name] = None