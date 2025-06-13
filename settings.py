# settings.py
import pygame

# Экран и отображение
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Студенты против Злоключений"

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
PROGRESS_BLUE = (30, 144, 255)
DESCRIPTION_PANEL_COLOR = (20, 20, 20, 220)

# Цвета по умолчанию для резервной отрисовки
DEFAULT_COLORS = {
    'programmer': (60, 179, 113),
    'botanist': (255, 105, 180),
    'coffee_machine': (255, 215, 0),
    'coffee_bean': (255, 222, 173),
    'bracket': (0, 191, 255),
    'book_attack': (188, 143, 143),
    'alarm_clock': (169, 169, 169),
    'professor': (112, 128, 144),
    'calculus': (70, 130, 180),
    'akadem': (255, 69, 0),
    'background': (48, 124, 55),
    'shop_panel': (54, 45, 33),
    'shop_card': (87, 72, 54),
    'shop_border': (34, 28, 21),
    'button': (100, 100, 100),
    'pause_button': (200, 200, 200)
}

# Игровое поле (сетка)
GRID_ROWS = 5
GRID_COLS = 9
CELL_SIZE_W = 110
CELL_SIZE_H = 110
GRID_START_X = 150
GRID_START_Y = 150
GRID_WIDTH = GRID_COLS * CELL_SIZE_W
GRID_HEIGHT = GRID_ROWS * CELL_SIZE_H

# Панель магазина
SHOP_PANEL_HEIGHT = 140
SHOP_CARD_SIZE = 100
SHOP_ITEM_PADDING = 20

# Пути к ассетам
ASSETS_DIR = 'assets'
IMAGES_DIR = f'{ASSETS_DIR}/images'

# Данные юнитов
DEFENDERS_DATA = {
    'programmer': {
        'cost': 100, 'health': 300, 'cooldown': 1.5, 'damage': 25,
        'description': "Пишет код быстрее, чем ты говоришь 'дедлайн'. Стреляет скобочками.",
        'select_sound': 'programmer_select.mp3'
    },
    'botanist': {
        'cost': 150, 'health': 300, 'cooldown': 2.5, 'damage': 50, 'radius': CELL_SIZE_W * 1.5,
        'description': "Знает всё о матане и о том, как больно бить книгой. Атакует по области.",
        'select_sound': 'botanist_select.mp3'
    },
    'coffee_machine': {
        'cost': 50, 'health': 200, 'cooldown': 5, 'production': 25,
        'description': "Источник жизни и энергии. Производит бесценные кофейные зернышки.",
        'select_sound': 'coffee_machine_select.mp3'
    }
}

ENEMIES_DATA = {
    'alarm_clock': {
        'health': 100, 'speed': 0.8, 'damage': 50, 'display_name': "Будильник (8:30)",
        'description': "Безжалостный и неотвратимый. Его звон - предвестник беды. Стандартный враг.",
        'select_sound': 'alarm_clock_select.mp3'
    },
    'professor': {
        'health': 250, 'speed': 0.6, 'damage': 100, 'display_name': "Грозный Преподаватель",
        'description': "Крепкий и выносливый. Выдержит много критики и нанесет сокрушительный удар по самооценке.",
        'select_sound': 'professor_select.mp3'
    },
    'calculus': {
        'health': 180, 'speed': 1, 'damage': 75, 'display_name': "Матанализ",
        'description': "Быстрый и непредсказуемый. Может легко 'перепрыгнуть' через простые аргументы и застать врасплох.",
        'select_sound': 'calculus_select.mp3'
    }
}