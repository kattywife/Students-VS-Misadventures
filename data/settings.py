# data/settings.py

import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Студенты против Злоключений"
MAX_TEAM_SIZE = 6
BLACK = (0, 0, 0);
WHITE = (255, 255, 255);
GREY = (128, 128, 128);
DARK_GREY = (50, 50, 50)
GREEN = (0, 255, 0);
RED = (255, 0, 0);
BLUE = (0, 0, 255);
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19);
PROGRESS_BLUE = (30, 144, 255);
DESCRIPTION_PANEL_COLOR = (20, 20, 20, 220)
AURA_GREEN = (0, 255, 0, 50);
AURA_RED = (255, 0, 0, 50);
AURA_PINK = (255, 105, 180, 100)
CALAMITY_ORANGE = (255, 140, 0)
GRID_COLOR = (200, 200, 200, 100) # Был коричневый, стал полупрозрачный белый/серый
TITLE_BROWN = (89, 57, 42) # <-- ДОБАВЬ ЭТУ СТРОКУ
EXIT_BUTTON_RED = (188, 74, 60)
START_BUTTON_GREEN = (0, 128, 0) # Насыщенный, но не яркий зеленый
CALAMITY_PANEL_BG = (70, 45, 30, 220) # Тот же коричневый, но с альфа-каналом 220 (почти непрозрачный)
CALAMITY_BORDER_RED = (188, 74, 60)
COFFEE_COST_COLOR = (205, 133, 63) # Яркий, "карамельный" коричневый
RANDOM_BUTTON_COLOR = (0, 139, 139) # Темно-бирюзовый для кнопок рандома

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
    'background': (48, 124, 55), 'shop_panel': (70, 45, 30), 'shop_card': (87, 72, 54),
    'shop_border': (34, 28, 21), 'button': (100, 100, 100), 'pause_button': (200, 200, 200)
}
GRID_ROWS = 5; GRID_COLS = 9; CELL_SIZE_W = 110; CELL_SIZE_H = 110; GRID_START_X = 150
GRID_START_Y = 150; GRID_WIDTH = GRID_COLS * CELL_SIZE_W; GRID_HEIGHT = GRID_ROWS * CELL_SIZE_H
SHOP_PANEL_HEIGHT = 140; SHOP_CARD_SIZE = 100; SHOP_ITEM_PADDING = 20
ASSETS_DIR = 'assets'; IMAGES_DIR = f'{ASSETS_DIR}/images'

# Константы для экрана расстановки нейросетей (увеличенная сетка)
PLACEMENT_GRID_CELL_W = 125
PLACEMENT_GRID_CELL_H = 120
PLACEMENT_GRID_START_Y = (SCREEN_HEIGHT - GRID_ROWS * PLACEMENT_GRID_CELL_H) / 2
PLACEMENT_ZONE_X = 20
PLACEMENT_GRID_START_X = PLACEMENT_ZONE_X + PLACEMENT_GRID_CELL_W + 20


DEFENDERS_DATA = {
    'programmer': {'cost': 100, 'health': 300, 'damage': 25, 'cooldown': 1.5, 'display_name': 'Мальчик-джун', 'category': 'defenders',
                   'description': "Стандартный стрелок, эффективный против одиночных целей. Его атаки быстры и точны, как идеально написанный код. Отлично подходит для уничтожения слабых врагов на линии.",
                   'upgrades': { 'damage': {'value': 10, 'cost': 20}, 'cooldown': {'value': -0.3, 'cost': 25} },
                   'animation_data': { 'folder': 'programmer', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }},
    'botanist': {'cost': 150, 'health': 300, 'damage': 50, 'cooldown': 2.5, 'radius': 2, 'display_name': 'Девочка-ботан', 'category': 'defenders',
                 'description': "Находит самого 'жирного' врага на поле и обрушивает на него и его соседей всю тяжесть своих знаний. Чем больше здоровья у цели, тем она привлекательнее для атаки.",
                 'upgrades': { 'damage': {'value': 25, 'cost': 30}, 'radius': {'value': 1, 'cost': 20} },
                 'animation_data': { 'folder': 'botanist', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }},
    'coffee_machine': {'cost': 50, 'health': 200, 'damage': 0, 'cooldown': 5, 'production': 25, 'display_name': 'Кофемашина', 'category': 'defenders',
                       'description': "Источник жизни и бодрости для всей команды. Не атакует, но исправно генерирует кофейные зернышки, необходимые для вызова новых защитников. Защищайте ее любой ценой!",
                       'upgrades': { 'production': {'value': 15, 'cost': 25}, 'health': {'value': 150, 'cost': 20} },
                       'animation_data': { 'folder': 'coffee_machine', 'speed': 0.3, 'idle': [], 'attack': [] }},
    'activist': {'cost': 75, 'health': 400, 'damage': 0, 'cooldown': None, 'radius': 2, 'buff': 1.5,
                 'display_name': 'Активист', 'category': 'defenders',
                 'description': "Его пламенные речи и несокрушимый энтузиазм вдохновляют всех вокруг. Создает ауру, которая значительно увеличивает урон союзников, попавших в ее радиус.",
                 'upgrades': {'buff': {'value': 0.3, 'cost': 30}, 'radius': {'value': 1, 'cost': 25}},
                 'animation_data': { 'folder': 'activist', 'speed': 0.3, 'idle': [], 'hit': [] }},
    'guitarist': {'cost': 150, 'health': 300, 'damage': 20, 'cooldown': 4, 'display_name': 'Гитарист', 'category': 'defenders',
                  'projectile_speed': 5, 'description': "Атакует всех врагов на своей линии мощной звуковой волной, которая пробивает их насквозь. Идеален для борьбы с плотными группами противников.",
                  'upgrades': { 'projectile_speed': {'value': 3, 'cost': 20}, 'damage': {'value': 15, 'cost': 25} },
                  'animation_data': { 'folder': 'guitarist', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }},
    'medic': {'cost': 50, 'health': 250, 'damage': 0, 'cooldown': 1.0, 'heal_amount': 200, 'radius': 2, 'display_name': 'Студент-медик', 'category': 'defenders',
              'description': "Живая аптечка. Постепенно отдает свое здоровье самому раненому союзнику в радиусе действия. Когда его запасы здоровья иссякнут, он героически исчезнет.",
              'upgrades': { 'radius': {'value': 1, 'cost': 20}, 'heal_amount': {'value': 150, 'cost': 25} },
              'animation_data': { 'folder': 'medic', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }},
    'artist': {'cost': 125, 'health': 300, 'damage': 10, 'cooldown': 2, 'slow_duration': 2000, 'slow_factor': 0.5, 'display_name': 'Художница', 'category': 'defenders',
               'description': "Погруженная в творчество, она не замечает ничего вокруг. Её кляксы краски, попадая во врагов, не только наносят урон, но и значительно замедляют их передвижение.",
               'upgrades': { 'slow_factor': {'value': -0.15, 'cost': 25}, 'damage': {'value': 15, 'cost': 20} },
               'animation_data': { 'folder': 'artist', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }},
    'modnik': {'cost': 125, 'health': 300, 'damage': 1800, 'radius': 2, 'speed': 1.5, 'display_name': 'Модник', 'category': 'defenders',
               'description': "Появляется раз в семестр, чтобы блеснуть. Очень быстрый юнит-камикадзе. Находит ближайшего врага, подбегает к нему и взрывается, нанося огромный урон по большой площади.",
               'upgrades': { 'radius': {'value': 1, 'cost': 30}, 'damage': {'value': 400, 'cost': 35} },
               'animation_data': { 'folder': 'modnik', 'speed': 0.3, 'idle': [], 'hit': [] }}
}

ENEMIES_DATA = {
    'alarm_clock': {'health': 100, 'speed': 0.8, 'damage': 50, 'cooldown': 1.0, 'display_name': "Первая пара", 'category': 'enemies', 'description': "Самое страшное для первокурсника. Обычный враг, который просто идет вперед и больно кусает первого встречного. Берет числом, а не умением.",
                    'animation_data': {'folder': 'alarm_clock', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}},
    'calculus': {'health': 180, 'speed': 0.8, 'damage': 10, 'cooldown': 3.0, 'display_name': "Матанализ",
                 'category': 'enemies',
                 'description': "Опасный дальнобойный противник. Останавливается при виде защитника на своей линии и начинает обстреливать его интегралами, пределами и производными с безопасного расстояния.",
                 'animation_data': {'folder': 'calculus', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}},
    'math_teacher': {'health': 150, 'speed': 1.5, 'damage': 80, 'cooldown': 1.0, 'display_name': "Злая математичка", 'category': 'enemies', 'description': "Быстрый и непредсказуемый враг. При столкновении с первым защитником на линии перепрыгивает его, чтобы прорваться в тыл. После прыжка ее скорость снижается вдвое.",
                     'animation_data': {'folder': 'math_teacher', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}},
    'addict': {'health': 120, 'speed': 2.5, 'damage': 9999, 'cooldown': 0.5, 'display_name': "Наркоман", 'category': 'enemies', 'description': "Враг-убийца. Игнорирует всех, кроме защитника с самым большим текущим уроном на поле. Целенаправленно бежит к нему, хватает и уносит с экрана навсегда.",
               'animation_data': {'folder': 'addict', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}},
    'thief': {'health': 120, 'speed': 2.5, 'damage': 9999, 'cooldown': 0.5, 'display_name': "Вор", 'category': 'enemies', 'description': "Главный враг экономики. Ищет Кофемашины, игнорируя героев. Украдет одну, унесет с поля и вернется за следующей. Если Кофемашин нет, ведет себя как обычный враг ближнего боя.",
              'animation_data': {'folder': 'thief', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}}
}

NEURO_MOWERS_DATA = {
    'chat_gpt': {'cost': 25, 'display_name': 'ChatGPT', 'category': 'systems', 'description': 'Последний рубеж обороны. При контакте с врагом активируется, едет по всей линии и уничтожает всех на своем пути. Может быть не более двух на поле.'},
    'deepseek': {'cost': 15, 'display_name': 'DeepSeek', 'category': 'systems', 'description': 'Тактическая нейросеть. При контакте с врагом мгновенно находит и уничтожает 3 самых близких к вашей базе врага на всем поле, вне зависимости от их линии.'},
    'gemini': {'cost': 40, 'display_name': 'Gemini', 'category': 'systems', 'description': 'Элитная нейросеть-ликвидатор. При контакте с врагом находит и уничтожает 4 самых сильных (по текущему здоровью) врага на всем поле.'}
}

CALAMITIES_DATA = {
    'epidemic': {'display_name': 'Эпидемия гриппа', 'category': 'calamities', 'description': 'Все ваши герои на поле заболевают! Их здоровье и урон временно падают в 2 раза.'},
    'big_party': {'display_name': 'Великая туса', 'category': 'calamities', 'description': 'Зов вечеринки! 80% ваших героев (кроме Кофемашин) случайным образом покидают поле боя.'},
    'colloquium': {'display_name': 'Внезапный коллоквиум', 'category': 'calamities', 'description': 'Все враги на поле получают прилив уверенности! Их атаки временно становятся в 1.5 раза сильнее.'},
    'internet_down': {'display_name': 'Отключение интернета', 'category': 'calamities', 'description': 'Студенты не могут списать, и все становится в два раза сложнее. Здоровье всех врагов на поле временно удваивается.'}
}

UI_ELEMENTS_DATA = {
    'stipend': {'display_name': 'Стипендия', 'category': 'ui'},
    'coffee_bean': {'display_name': 'Кофейные зернышки', 'category': 'resources'}
}

PROGRAMMER_PROJECTILE_TYPES = ['bracket_0', 'bracket_1', 'bracket_2']

CALCULUS_PROJECTILE_TYPES = ['plus', 'multiply', 'divide', 'seven', 'three', 'five', 'null']