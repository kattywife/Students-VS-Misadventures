# data/settings.py

import pygame

# ... (Цвета и константы остаются без изменений)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Студенты против Злоключений"
MAX_TEAM_SIZE = 6
BLACK = (0, 0, 0); WHITE = (255, 255, 255); GREY = (128, 128, 128); DARK_GREY = (50, 50, 50)
GREEN = (0, 255, 0); RED = (255, 0, 0); BLUE = (0, 0, 255); YELLOW = (255, 255, 0)
BROWN = (139, 69, 19); PROGRESS_BLUE = (30, 144, 255); DESCRIPTION_PANEL_COLOR = (20, 20, 20, 220)
AURA_GREEN = (0, 255, 0, 50); AURA_RED = (255, 0, 0, 50); AURA_PINK = (255, 105, 180, 100)
CALAMITY_ORANGE = (255, 140, 0)
DEFAULT_COLORS = {
    'programmer': (60, 179, 113), 'botanist': (255, 105, 180), 'coffee_machine': (255, 215, 0),
    'activist': (0, 128, 128), 'guitarist': (218, 112, 214), 'medic': (240, 255, 255), 'artist': (255, 165, 0),
    'modnik': (128, 0, 128),
    'coffee_bean': (255, 222, 173), 'bracket': (0, 191, 255), 'book_attack': (188, 143, 143),
    'sound_wave': (138, 43, 226, 100), 'paint_splat': (255, 165, 0), 'integral': (100, 100, 100),
    'explosion': (255, 127, 80),
    'alarm_clock': (169, 169, 169), 'professor': (112, 128, 144), 'calculus': (70, 130, 180),
    'math_teacher': (210, 105, 30), 'addict': (0, 100, 0), 'thief': (139, 0, 0),
    'chat_gpt': (0, 168, 150), 'deepseek': (20, 20, 40), 'gemini': (106, 90, 205),
    'epidemic': (152, 251, 152, 100), 'big_party': (255, 20, 147, 100), 'colloquium': (255, 69, 0, 100), 'internet_down': (75, 0, 130, 100),
    'background': (48, 124, 55), 'shop_panel': (54, 45, 33), 'shop_card': (87, 72, 54),
    'shop_border': (34, 28, 21), 'button': (100, 100, 100), 'pause_button': (200, 200, 200)
}
GRID_ROWS = 5; GRID_COLS = 9; CELL_SIZE_W = 110; CELL_SIZE_H = 110; GRID_START_X = 150
GRID_START_Y = 150; GRID_WIDTH = GRID_COLS * CELL_SIZE_W; GRID_HEIGHT = GRID_ROWS * CELL_SIZE_H
SHOP_PANEL_HEIGHT = 140; SHOP_CARD_SIZE = 100; SHOP_ITEM_PADDING = 20
ASSETS_DIR = 'assets'; IMAGES_DIR = f'{ASSETS_DIR}/images'

DEFENDERS_DATA = {
    'programmer': {'cost': 100, 'health': 300, 'damage': 25, 'cooldown': 1.5, 'display_name': 'Мальчик-джун', 'category': 'defenders',
                   'description': "Стандартный стрелок...", 'upgrades': { 'damage': {'value': 5, 'cost': 15}, 'cooldown': {'value': -0.2, 'cost': 20} },
                   'animation_data': { 'folder': 'programmer', 'speed': 0.1, 'idle': [], 'attack': [], 'hit': [] }},
    'botanist': {'cost': 150, 'health': 300, 'damage': 50, 'cooldown': 2.5, 'radius': CELL_SIZE_W * 1.5, 'display_name': 'Девочка-ботан', 'category': 'defenders',
                 'description': "Находит самого сильного врага...", 'upgrades': { 'damage': {'value': 15, 'cost': 25}, 'radius': {'value': 20, 'cost': 15} },
                 'animation_data': { 'folder': 'botanist', 'speed': 0.15, 'idle': [], 'attack': [], 'hit': [] }},
    'coffee_machine': {'cost': 50, 'health': 200, 'damage': 0, 'cooldown': 5, 'production': 25, 'display_name': 'Кофемашина', 'category': 'defenders',
                       'description': "Производит кофейные зернышки.", 'upgrades': { 'production': {'value': 10, 'cost': 25}, 'health': {'value': 100, 'cost': 15} },
                       'animation_data': { 'folder': 'coffee_machine', 'speed': 0.2, 'idle': [], 'attack': [] }},
    'activist': {'cost': 75, 'health': 400, 'damage': 0, 'cooldown': None, 'radius': CELL_SIZE_W * 2, 'buff': 1.5,
                 'display_name': 'Активист', 'category': 'defenders',
                 'description': "Не атакует, но усиливает урон...",
                 'upgrades': {'buff': {'value': 0.2, 'cost': 30}, 'radius': {'value': 30, 'cost': 20}},
                 'animation_data': { 'folder': 'activist', 'speed': 0.1, 'idle': [], 'hit': [] }},
    'guitarist': {'cost': 150, 'health': 300, 'damage': 20, 'cooldown': 4, 'display_name': 'Гитарист', 'category': 'defenders',
                  'projectile_speed': 5, 'description': "Атакует звуковой волной...", 'upgrades': { 'damage': {'value': 10, 'cost': 25}, 'projectile_speed': {'value': 2, 'cost': 15} },
                  'animation_data': { 'folder': 'guitarist', 'speed': 0.15, 'idle': [], 'attack': [], 'hit': [] }},
    'medic': {'cost': 50, 'health': 250, 'damage': 0, 'cooldown': 1.0, 'heal_amount': 200, 'radius': CELL_SIZE_W * 2, 'display_name': 'Студент-медик', 'category': 'defenders',
              'description': "Постепенно отдает свое здоровье...", 'upgrades': { 'heal_amount': {'value': 100, 'cost': 25} },
              'animation_data': { 'folder': 'medic', 'speed': 0.1, 'idle': [], 'attack': [], 'hit': [] }},
    'artist': {'cost': 125, 'health': 300, 'damage': 10, 'cooldown': 2, 'slow_duration': 2000, 'slow_factor': 0.5, 'display_name': 'Художница', 'category': 'defenders',
               'description': "Её кляксы краски замедляют...", 'upgrades': { 'damage': {'value': 10, 'cost': 20}, 'slow_factor': {'value': -0.1, 'cost': 25} },
               'animation_data': { 'folder': 'artist', 'speed': 0.15, 'idle': [], 'attack': [], 'hit': [] }},
    'modnik': {'cost': 125, 'health': 300, 'damage': 1800, 'radius': CELL_SIZE_W * 2.5, 'speed': 1.5, 'display_name': 'Модник', 'category': 'defenders',
               'description': "Подходит к ближайшему врагу и взрывается...", 'upgrades': { 'radius': {'value': 40, 'cost': 30}, 'damage': {'value': 200, 'cost': 25} },
               'animation_data': { 'folder': 'modnik', 'speed': 0.1, 'idle': [], 'hit': [] }}
}

ENEMIES_DATA = {
    'alarm_clock': {'health': 100, 'speed': 0.8, 'damage': 50, 'cooldown': 1.0, 'display_name': "Первая пара", 'category': 'enemies', 'description': "Базовый враг...",
                    'animation_data': {'folder': 'alarm_clock', 'speed': 0.15, 'walk': [], 'attack': [], 'hit': []}},
    'calculus': {'health': 180, 'speed': 0.8, 'damage': 15, 'cooldown': 3.0, 'display_name': "Матанализ", 'category': 'enemies', 'description': "Стреляет интегралами...",
                 'animation_data': {'folder': 'calculus', 'speed': 0.1, 'walk': [], 'attack': [], 'hit': []}},
    'professor': {'health': 350, 'speed': 0.5, 'damage': 50, 'cooldown': 1.0, 'radius': CELL_SIZE_W * 1.5, 'debuff': 0.5, 'display_name': "Душный препод", 'category': 'enemies', 'description': "Ослабляет урон...",
                  'battle_size': (CELL_SIZE_W+15, CELL_SIZE_H + 25), # Увеличиваем размер на поле
                  'animation_data': {'folder': 'professor', 'speed': 0.2, 'walk': [], 'attack': [], 'hit': []}},
    'math_teacher': {'health': 150, 'speed': 1.5, 'damage': 80, 'cooldown': 1.0, 'display_name': "Злая математичка", 'category': 'enemies', 'description': "Быстрый враг...",
                     'battle_size': (CELL_SIZE_W+15, CELL_SIZE_H+25), # Увеличиваем размер на поле
                     'animation_data': {'folder': 'math_teacher', 'speed': 0.1, 'walk': [], 'attack': [], 'hit': []}},
    'addict': {'health': 120, 'speed': 2.5, 'damage': 9999, 'cooldown': 0.5, 'display_name': "Наркоман", 'category': 'enemies', 'description': "Охотится за сильнейшим...",
               'animation_data': {'folder': 'addict', 'speed': 0.1, 'walk': [], 'attack': [], 'hit': []}},
    'thief': {'health': 120, 'speed': 2.5, 'damage': 9999, 'cooldown': 0.5, 'display_name': "Вор", 'category': 'enemies', 'description': "Его цель - кофемашины.",
              'animation_data': {'folder': 'thief', 'speed': 0.1, 'walk': [], 'attack': [], 'hit': []}}
}

NEURO_MOWERS_DATA = {
    'chat_gpt': {'cost': 25, 'display_name': 'ChatGPT', 'category': 'systems', 'description': 'Уничтожает всех врагов на линии.'},
    'deepseek': {'cost': 15, 'display_name': 'DeepSeek', 'category': 'systems', 'description': 'Уничтожает 3 самых близких врага.'},
    'gemini': {'cost': 40, 'display_name': 'Gemini', 'category': 'systems', 'description': 'Уничтожает 4 самых сильных врага.'}
}

CALAMITIES_DATA = {
    'epidemic': {'display_name': 'Эпидемия гриппа', 'category': 'calamities', 'description': 'Здоровье и урон героев падают в 2 раза.'},
    'big_party': {'display_name': 'Великая туса', 'category': 'calamities', 'description': '80% ваших героев покидают поле боя.'}, # <--- ДОБАВИТЬ СЮДА
    'colloquium': {'display_name': 'Внезапный коллоквиум', 'category': 'calamities', 'description': 'Атаки врагов становятся в 1.5 раза сильнее.'}, # <--- И СЮДА
    'internet_down': {'display_name': 'Отключение интернета', 'category': 'calamities', 'description': 'Здоровье врагов удваивается.'}
}

UI_ELEMENTS_DATA = {
    'stipend': {'display_name': 'Стипендия', 'category': 'ui'},
    'coffee_bean': {'display_name': 'Кофейные зернышки', 'category': 'resources'}
}

PROGRAMMER_PROJECTILE_TYPES = ['bracket_0', 'bracket_1', 'bracket_2']

CALCULUS_PROJECTILE_TYPES = ['plus', 'multiply', 'divide', 'seven', 'three', 'five', 'null']