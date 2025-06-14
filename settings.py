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
DARK_GREY = (50, 50, 50)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
PROGRESS_BLUE = (30, 144, 255)
DESCRIPTION_PANEL_COLOR = (20, 20, 20, 220)
AURA_GREEN = (0, 255, 0, 50)
AURA_RED = (255, 0, 0, 50)
AURA_PINK = (255, 105, 180, 100)

# Цвета по умолчанию для резервной отрисовки
DEFAULT_COLORS = {
    'programmer': (60, 179, 113),
    'botanist': (255, 105, 180),
    'coffee_machine': (255, 215, 0),
    'activist': (0, 128, 128),
    'guitarist': (218, 112, 214),
    'medic': (240, 255, 255),
    'artist': (255, 165, 0),

    'coffee_bean': (255, 222, 173),
    'bracket': (0, 191, 255),
    'book_attack': (188, 143, 143),
    'sound_wave': (138, 43, 226, 100),
    'paint_splat': (255, 165, 0),
    'integral': (100, 100, 100),

    'alarm_clock': (169, 169, 169),
    'professor': (112, 128, 144),  # Ключ для "Душный препод"
    'calculus': (70, 130, 180),
    'math_teacher': (210, 105, 30),
    'addict': (0, 100, 0),
    'thief': (139, 0, 0),

    'chat_gpt': (0, 168, 150),
    'deepseek': (20, 20, 40),
    'gemini': (106, 90, 205),

    'epidemic': (152, 251, 152),
    'big_party': (255, 20, 147),
    'colloquium': (255, 69, 0),
    'internet_down': (75, 0, 130),

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

# --- ОБНОВЛЕННЫЕ ДАННЫЕ ЮНИТОВ ---

# ЗАЩИТНИКИ
DEFENDERS_DATA = {
    'programmer': {
        'cost': 100, 'health': 300, 'cooldown': 1.5, 'damage': 25,
        'display_name': 'Мальчик-джун',
        'description': "Урон: {damage}\nЗдоровье: {health}\nПерезарядка: {cooldown} сек\nОсобенность: стреляет быстрыми, но слабыми снарядами.",
        'select_sound': 'programmer_select.mp3',
        'upgrade': {'damage': 5, 'cost': 15}
    },
    'botanist': {
        'cost': 150, 'health': 300, 'cooldown': 2.5, 'damage': 50, 'radius': CELL_SIZE_W * 1.5,
        'display_name': 'Девочка-ботан',
        'description': "Урон: {damage}\nЗдоровье: {health}\nПерезарядка: {cooldown} сек\nОсобенность: атакует по области самого сильного врага.",
        'select_sound': 'botanist_select.mp3',
        'upgrade': {'damage': 10, 'cost': 25}
    },
    'coffee_machine': {
        'cost': 50, 'health': 200, 'cooldown': 5, 'production': 25,
        'display_name': 'Кофемашина',
        'description': "Здоровье: {health}\nПерезарядка: {cooldown} сек\nОсобенность: производит кофейные зернышки.",
        'select_sound': 'coffee_machine_select.mp3',
        'upgrade': {'cooldown': -0.5, 'cost': 20}
    },
    'activist': {
        'cost': 75, 'health': 400, 'cooldown': 10, 'radius': CELL_SIZE_W * 2, 'buff': 1.5,
        'display_name': 'Активист с рупором',
        'description': "Здоровье: {health}\nПерезарядка: {cooldown} сек\nОсобенность: не атакует, но усиливает урон союзников в радиусе в {buff} раза.",
        'select_sound': 'activist_select.mp3',
        'upgrade': {'radius': 20, 'cost': 30}
    },
    'guitarist': {
        'cost': 175, 'health': 300, 'cooldown': 4, 'damage': 20,
        'display_name': 'Гитарист',
        'description': "Урон: {damage}\nЗдоровье: {health}\nПерезарядка: {cooldown} сек\nОсобенность: атакует звуковой волной всех врагов на линии.",
        'select_sound': 'guitarist_select.mp3',
        'upgrade': {'damage': 5, 'cost': 20}
    },
    'medic': {
        'cost': 50, 'health': 250, 'cooldown': 20, 'heal_amount': 150, 'radius': CELL_SIZE_W * 4,
        'display_name': 'Студент-медик',
        'description': "Лечение: {heal_amount}\nЗдоровье: {health}\nПерезарядка: {cooldown} сек\nОсобенность: лечит самого раненого союзника и исчезает.",
        'select_sound': 'medic_select.mp3',
        'upgrade': {'heal_amount': 50, 'cost': 25}
    },
    'artist': {
        'cost': 125, 'health': 300, 'cooldown': 2, 'damage': 10, 'slow_duration': 2000, 'slow_factor': 0.5,
        'display_name': 'Художница',
        'description': "Урон: {damage}\nЗдоровье: {health}\nПерезарядка: {cooldown} сек\nОсобенность: снаряды замедляют врагов.",
        'select_sound': 'artist_select.mp3',
        'upgrade': {'slow_duration': 500, 'cost': 15}
    }
}

# ВРАГИ
ENEMIES_DATA = {
    'alarm_clock': {'health': 100, 'speed': 0.8, 'damage': 50, 'display_name': "Первая пара (8:30)",
                    'description': "Стандартный враг, просто идет вперед."},
    'calculus': {'health': 180, 'speed': 0.8, 'damage': 15, 'cooldown': 3, 'display_name': "Матанализ",
                 'description': "Стреляет интегралами с безопасного расстояния."},
    'professor': {'health': 350, 'speed': 0.5, 'radius': CELL_SIZE_W * 1.5, 'debuff': 0.5, 'damage': 50,
                    'display_name': "Душный препод",
                    'description': "Создает ауру, ослабляющую урон героев. Сам тоже может покусать."},
    'math_teacher': {'health': 150, 'speed': 1.5, 'damage': 80, 'display_name': "Злая математичка",
                     'description': "Быстрый враг, который может один раз перепрыгнуть защитника."},
    'addict': {'health': 120, 'speed': 2.5, 'damage': 9999, 'display_name': "Наркоман со шприцом",
               'description': "Очень быстрый, меняет линии. Мгновенно уничтожает любого героя при контакте."},
    'thief': {'health': 120, 'speed': 2.5, 'damage': 9999, 'display_name': "Вор",
              'description': "Очень быстрый, меняет линии. Его цель - украсть ваши кофемашины."}
}

# НЕЙРОСЕТИ
NEURO_MOWERS_DATA = {
    'chat_gpt': {'cost': 10, 'display_name': 'ChatGPT',
                 'description': 'Стандартная защита. При контакте уничтожает всех врагов на линии.'},
    'deepseek': {'cost': 25, 'display_name': 'DeepSeek',
                 'description': 'При контакте находит и уничтожает 3 самых близких к базе врага.'},
    'gemini': {'cost': 40, 'display_name': 'Gemini',
               'description': 'При контакте находит и уничтожает 4 самых сильных врага на поле.'}
}

# НАПАСТИ (СТИХИИ)
CALAMITIES_DATA = { # <-- ИЗМЕНЕНИЕ: Описания обновлены
    'epidemic': {'display_name': 'Эпидемия гриппа',
                 'description': 'Внезапно! Все ваши герои на поле заболевают. Их здоровье и урон падают в 2 раза до конца боя.'},
    'big_party': {'display_name': 'Великая туса',
                  'description': 'Зов вечеринки! 80% ваших героев случайным образом решают, что с них хватит, и покидают поле боя.'},
    'colloquium': {'display_name': 'Внезапный коллоквиум',
                   'description': 'Неожиданно! Все враги на поле получают прилив уверенности. Их атаки становятся в 1.5 раза сильнее до конца боя.'},
    'internet_down': {'display_name': 'Отключение интернета',
                      'description': 'Беда! Все враги на поле теряют доступ к ГДЗ и звереют. Их максимальное и текущее здоровье удваивается.'}
}