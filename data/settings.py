# data/settings.py

import pygame

# Экран и отображение
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Студенты против Злоключений"

MAX_TEAM_SIZE = 6

# Цвета
BLACK = (0, 0, 0); WHITE = (255, 255, 255); GREY = (128, 128, 128); DARK_GREY = (50, 50, 50)
GREEN = (0, 255, 0); RED = (255, 0, 0); BLUE = (0, 0, 255); YELLOW = (255, 255, 0)
BROWN = (139, 69, 19); PROGRESS_BLUE = (30, 144, 255); DESCRIPTION_PANEL_COLOR = (20, 20, 20, 220)
AURA_GREEN = (0, 255, 0, 50); AURA_RED = (255, 0, 0, 50); AURA_PINK = (255, 105, 180, 100)
CALAMITY_ORANGE = (255, 140, 0)

# Цвета по умолчанию для резервной отрисовки
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

# Игровое поле и пути
GRID_ROWS = 5; GRID_COLS = 9; CELL_SIZE_W = 110; CELL_SIZE_H = 110; GRID_START_X = 150
GRID_START_Y = 150; GRID_WIDTH = GRID_COLS * CELL_SIZE_W; GRID_HEIGHT = GRID_ROWS * CELL_SIZE_H
SHOP_PANEL_HEIGHT = 140; SHOP_CARD_SIZE = 100; SHOP_ITEM_PADDING = 20
ASSETS_DIR = 'assets'; IMAGES_DIR = f'{ASSETS_DIR}/images'

# ЗАЩИТНИКИ
DEFENDERS_DATA = {
    'programmer': {'cost': 100, 'health': 300, 'damage': 25, 'cooldown': 1.5, 'display_name': 'Мальчик-джун',
                   'description': "Стандартный стрелок, эффективен против одиночных слабых целей. Атакует первого врага на своей линии быстрыми снарядами ('скобками').",
                   'upgrades': {
                       'damage': {'value': 5, 'cost': 15},
                       'cooldown': {'value': -0.2, 'cost': 20}
                   }},
    'botanist': {'cost': 150, 'health': 300, 'damage': 50, 'cooldown': 2.5, 'radius': CELL_SIZE_W * 1.5, 'display_name': 'Девочка-ботан',
                 'description': "Находит самого сильного врага (по здоровью) на поле, смещает свой радиус атаки на него и наносит урон всем врагам в этой области.",
                 'upgrades': {
                     'damage': {'value': 15, 'cost': 25},
                     'radius': {'value': 20, 'cost': 15}
                 }},
    'coffee_machine': {'cost': 50, 'health': 200, 'damage': 0, 'cooldown': 5, 'production': 25, 'display_name': 'Кофемашина',
                       'description': "Производит кофейные зернышки.",
                       'upgrades': {
                           'production': {'value': 10, 'cost': 25},
                           'health': {'value': 100, 'cost': 15}
                       }},
    'activist': {'cost': 75, 'health': 400, 'damage': 0, 'cooldown': None, 'radius': CELL_SIZE_W * 2, 'buff': 1.5, 'display_name': 'Активист с рупором',
                 'description': "Не атакует, но усиливает урон союзников, находящихся в его ауре.",
                 'upgrades': {
                     'buff': {'value': 0.2, 'cost': 30},
                     'radius': {'value': 30, 'cost': 20}
                 }},
    'guitarist': {'cost': 150, 'health': 300, 'damage': 20, 'cooldown': 4, 'display_name': 'Гитарист',
                  'projectile_speed': 5,
                  'description': "Атакует звуковой волной всех врагов на линии.",
                  'upgrades': {
                      'damage': {'value': 10, 'cost': 25},
                      'projectile_speed': {'value': 2, 'cost': 15}
                  }},
    'medic': {'cost': 50, 'health': 250, 'damage': 0, 'cooldown': 1.0, 'heal_amount': 200, 'radius': CELL_SIZE_W * 2, 'display_name': 'Студент-медик',
              'description': "Постепенно отдает свое здоровье окружающим союзникам, в первую очередь самым раненым. Исчезает, когда у него кончаются запасы здоровья.",
              'upgrades': {
                  'heal_amount': {'value': 100, 'cost': 25}
              }},
    'artist': {'cost': 125, 'health': 300, 'damage': 10, 'cooldown': 2, 'slow_duration': 2000, 'slow_factor': 0.5, 'display_name': 'Художница',
               'description': "Погруженная в свое творчество, она не замечает ничего вокруг. Её кляксы краски попадают во врагов, замедляя их и нанося урон.",
               'upgrades': {
                   'damage': {'value': 10, 'cost': 20},
                   'slow_factor': {'value': -0.1, 'cost': 25}
               }},
    'modnik': {'cost': 125, 'health': 300, 'damage': 1800, 'radius': CELL_SIZE_W * 2.5, 'speed': 1.5, 'display_name': 'Модник', 'cooldown': None,
               'description': "Появляется раз в семестр помодничать и исчезает. Подходит к ближайшему врагу и взрывается, уничтожая всех в большом радиусе.",
               'upgrades': {
                   'radius': {'value': 40, 'cost': 30},
                   'damage': {'value': 200, 'cost': 25}
               }}
}

# ВРАГИ
ENEMIES_DATA = {
    'alarm_clock': {'health': 100, 'speed': 0.8, 'damage': 50, 'cooldown': 1.0, 'display_name': "Первая пара (8:30)",
                    'description': "Базовый враг. Идет вперед и атакует первого встречного в ближнем бою."},
    'calculus': {'health': 180, 'speed': 0.8, 'damage': 15, 'cooldown': 3.0, 'display_name': "Матанализ",
                 'description': "Дальнобойный враг. Идет вперед, пока перед ним на его линии не появится защитник. После этого останавливается и стреляет 'интегралами' с безопасного расстояния."},
    'professor': {'health': 350, 'speed': 0.5, 'damage': 50, 'cooldown': 1.0, 'radius': CELL_SIZE_W * 1.5, 'debuff': 0.5, 'display_name': "Душный препод",
                  'description': "Враг поддержки с аурой. Создает вокруг себя поле, которое уменьшает урон всех снарядов героев, пролетающих через него. Если дойдет до защитника вплотную, атакует в ближнем бою."},
    'math_teacher': {'health': 150, 'speed': 1.5, 'damage': 80, 'cooldown': 1.0, 'display_name': "Злая математичка",
                     'description': "Быстрый враг. При столкновении с первым защитником на линии перепрыгивает его. После прыжка её скорость снижается вдвое. Кусается сильно и больно."},
    'addict': {'health': 120, 'speed': 2.5, 'damage': 9999, 'cooldown': 0.5, 'display_name': "Наркоман со шприцом",
               'description': "Враг-убийца. Игнорирует всех, кроме защитника с самым большим текущим уроном на поле. Добегает до цели, хватает её и уносит с экрана."},
    'thief': {'health': 120, 'speed': 2.5, 'damage': 9999, 'cooldown': 0.5, 'display_name': "Вор",
              'description': "Обнесет весь институт не моргнув глазом. Его основная цель — Кофемашины. Он будет перебегать между линиями, чтобы украсть все Кофемашины на поле. Если Кофемашин не останется, он начинает вести себя как обычный враг."}
}

# НЕЙРОСЕТИ
NEURO_MOWERS_DATA = {
    'chat_gpt': {'cost': 25, 'display_name': 'ChatGPT', 'description': 'Активируется при контакте с врагом, едет по линии и уничтожает всех на своем пути.'},
    'deepseek': {'cost': 15, 'display_name': 'DeepSeek', 'description': 'Активируется при контакте, находит и уничтожает 3 самых близких к базе врага на всем поле.'},
    'gemini': {'cost': 40, 'display_name': 'Gemini', 'description': 'Активируется при контакте, находит и уничтожает 4 самых сильных (по здоровью) врага на всем поле.'}
}

# НАПАСТИ
CALAMITIES_DATA = {
    'epidemic': {'display_name': 'Эпидемия гриппа', 'description': 'Все ваши герои на поле заболевают! Их здоровье и урон временно падают в 2 раза.'},
    'big_party': {'display_name': 'Великая туса', 'description': 'Зов вечеринки! 80% ваших героев (кроме Кофемашин) случайным образом покидают поле боя.'},
    'colloquium': {'display_name': 'Внезапный коллоквиум', 'description': 'Все враги на поле получают прилив уверенности! Их атаки временно становятся в 1.5 раза сильнее.'},
    'internet_down': {'display_name': 'Отключение интернета', 'description': 'Студенты не могут списать, и все становится в два раза сложнее. (Здоровье всех врагов на поле временно удваивается).'}
}