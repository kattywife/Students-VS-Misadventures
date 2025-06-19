# data/settings.py

import pygame

# =============================================================================
# 1. ОСНОВНЫЕ НАСТРОЙКИ ИГРЫ
# =============================================================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Студенты против Злоключений"
MAX_TEAM_SIZE = 6
GRID_ROWS = 5
GRID_COLS = 9

# =============================================================================
# 2. ПУТИ К ФАЙЛАМ
# =============================================================================
ASSETS_DIR = 'assets'
IMAGES_DIR = f'{ASSETS_DIR}/images'

# =============================================================================
# 3. НАСТРОЙКИ АУДИО
# =============================================================================
AUDIO_FREQUENCY = 44100
AUDIO_SIZE = -16
AUDIO_CHANNELS = 2
AUDIO_BUFFER = 512
AUDIO_NUM_CHANNELS = 32
DEFAULT_MUSIC_VOLUME = 0.4

# =============================================================================
# 4. ЦВЕТА
# =============================================================================
# --- Базовые цвета ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
DARK_GREY = (50, 50, 50)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
# --- UI Цвета ---
PROGRESS_BLUE = (30, 144, 255)
AURA_PINK = (255, 105, 180, 100)
CALAMITY_ORANGE = (255, 140, 0)
GRID_COLOR = (200, 200, 200, 100)
TITLE_BROWN = (89, 57, 42)
EXIT_BUTTON_RED = (188, 74, 60)
START_BUTTON_GREEN = (0, 128, 0)
CALAMITY_PANEL_BG = (70, 45, 30, 220)
CALAMITY_BORDER_RED = (188, 74, 60)
COFFEE_COST_COLOR = (205, 133, 63)
RANDOM_BUTTON_COLOR = (0, 139, 139)
# --- Цвета по умолчанию для юнитов (fallback) ---
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

# =============================================================================
# 5. ШРИФТЫ
# =============================================================================
FONT_FAMILY_DEFAULT = 'Arial'
FONT_FAMILY_IMPACT = 'Impact'
FONT_FAMILY_TITLE = 'Georgia'
FONT_SIZE_TINY = 18
FONT_SIZE_SMALL = 24
FONT_SIZE_NORMAL = 32
FONT_SIZE_LARGE = 60
FONT_SIZE_HUGE = 120
FONT_SIZE_TITLE = 55

# =============================================================================
# 5.1. НАСТРОЙКИ ОБРАБОТКИ ТЕКСТА
# =============================================================================
WORD_SEPARATOR = ' '

# =============================================================================
# 6. НАСТРОЙКИ БОЕВОЙ СЕТКИ
# =============================================================================
CELL_SIZE_W = 110
CELL_SIZE_H = 110
GRID_START_X = 150
GRID_START_Y = 150
GRID_WIDTH = GRID_COLS * CELL_SIZE_W
GRID_HEIGHT = GRID_ROWS * CELL_SIZE_H

# =============================================================================
# 7. НАСТРОЙКИ ПОЛЬЗОВАТЕЛЬСКОГО ИНТЕРФЕЙСА (UI)
# =============================================================================
# --- Общие элементы ---
DEFAULT_BORDER_RADIUS = 10
DEFAULT_BORDER_WIDTH = 2
THICK_BORDER_WIDTH = 3
# --- Стартовый экран и Меню ---
MENU_OVERLAY_ALPHA = 150
TITLE_PLAQUE_SIZE = (900, 180)
TITLE_PLAQUE_TEXT_V_OFFSET = 5
START_SCREEN_BUTTON_SIZE = (400, 80)
START_SCREEN_BUTTON_V_OFFSET = 50
START_SCREEN_BUTTON_V_SPACING = 120
PAUSE_MENU_BUTTON_SIZE = (400, 80)
PAUSE_MENU_V_SPACING = 100
# --- Главное меню ---
MAIN_MENU_PANEL_SIZE = (500, 600)
MAIN_MENU_PANEL_X_OFFSET = 100
MAIN_MENU_TITLE_TOP_OFFSET = 70
MAIN_MENU_LEVEL_BUTTON_SIZE = (400, 70)
MAIN_MENU_LEVEL_BUTTON_TOP_OFFSET = 180
MAIN_MENU_LEVEL_BUTTON_V_SPACING = 85
MAIN_MENU_CONTROL_BUTTON_SIZE = (200, 80)
MAIN_MENU_CONTROL_H_GAP = 20
MAIN_MENU_CONTROL_V_GAP = 20
MAIN_MENU_CONTROL_RIGHT_OFFSET = 150
MAIN_MENU_CONTROL_TOP_OFFSET = 250
# --- Боевой интерфейс (Shop, HUD) ---
SHOP_PANEL_HEIGHT = 140
SHOP_CARD_SIZE = 100
SHOP_ITEM_PADDING = 20
SHOP_COFFEE_AREA_WIDTH = 180
SHOP_COFFEE_ICON_SIZE = (50, 50)
SHOP_COFFEE_ICON_X_OFFSET = 20
SHOP_UPGRADE_BORDER_WIDTH = 4
SHOP_SELECTED_BORDER_WIDTH = 4
SHOP_CARD_IMG_Y_OFFSET = -10
SHOP_CARD_COST_Y_OFFSET = -15
PAUSE_BUTTON_SIZE = (60, 60)
PAUSE_BUTTON_X_OFFSET = -120
PAUSE_BAR_WIDTH = 8
PAUSE_BAR_HEIGHT = 30
PAUSE_BAR_H_SPACING = 10
HUD_BAR_WIDTH = 250
HUD_BAR_HEIGHT = 20
HUD_BAR_V_GAP = 5
HUD_RIGHT_MARGIN = 20
HUD_BOTTOM_MARGIN = 20
# --- Экран подготовки ---
PREP_TOP_Y = 70
PREP_PANEL_MARGIN = 20
PREP_STIPEND_PANEL_WIDTH = 320
PREP_STIPEND_PANEL_HEIGHT = 50
PREP_STIPEND_ICON_X_OFFSET = -20
PREP_STIPEND_ICON_TEXT_GAP = 10
PREP_TEAM_PANEL_TITLE_TOP_OFFSET = 30
PREP_HERO_SLOTS_TITLE_TOP_OFFSET = 70
PREP_HERO_SLOTS_TOP_OFFSET = 110
PREP_TEAM_CARD_SIZE = 80
PREP_TEAM_CARD_PADDING_X = 25
PREP_TEAM_CARD_PADDING_Y = 15
PREP_TEAM_COLS = 3
PREP_RANDOM_TEAM_BTN_SIZE = (220, 40)
PREP_RANDOM_TEAM_BTN_TOP_OFFSET = 35
PREP_NEURO_SLOTS_TOP_MARGIN = 30
PREP_NEURO_CARD_SIZE = 80
PREP_NEURO_CARD_H_SPACING = 10
PREP_NEURO_CARD_TOP_OFFSET = 40
PREP_RANDOM_NEURO_BTN_TOP_OFFSET = 30
PREP_SELECTION_HEROES_TITLE_TOP = 70
PREP_SELECTION_HEROES_LIST_TOP = 100
PREP_SELECTION_NEURO_TITLE_TOP = 350
PREP_SELECTION_NEURO_LIST_TOP = 380
PREP_SELECTION_CARD_SIZE = 80
PREP_SELECTION_CARD_PADDING = 15
PREP_SELECTION_COLS = 4
PREP_SELECTION_CARD_V_SPACING = 20
PREP_HUD_BOTTOM_MARGIN = 30
PREP_HUD_BUTTON_SIZE = (250, 60)
PREP_UNIT_CARD_IMG_PADDING = 10         # Отступ для изображения внутри карточки юнита
PREP_UNIT_CARD_COST_RIGHT_OFFSET = 5    # Отступ стоимости от правого края карточки
PREP_UNIT_CARD_COST_BOTTOM_OFFSET = 2   # Отступ стоимости от нижнего края карточки
PREP_UPGRADED_BORDER_INFLATE = 4        # Насколько "раздувается" рамка улучшенного юнита
PREP_UPGRADED_BORDER_RADIUS = 12        # Скругление для рамки улучшенного юнита
PREP_SELECTED_BORDER_RADIUS = 12        # Скругление для рамки выбранного юнита
PREP_EMPTY_SLOT_ALPHA = 50              # Прозрачность для пустого слота в команде
# --- Панель описания юнита ---
DESC_PANEL_SIZE = (700, 600)
DESC_PANEL_BORDER_RADIUS = 15
DESC_PANEL_IMG_SIZE = 120
DESC_PANEL_IMG_TOP_MARGIN = 20
DESC_PANEL_NAME_TOP_MARGIN = 10
DESC_PANEL_STATS_TOP_MARGIN = 25
DESC_PANEL_LEFT_MARGIN = 30
DESC_PANEL_RIGHT_MARGIN = 20
DESC_PANEL_LINE_HEIGHT = 35
DESC_PANEL_VALUE_X_OFFSET = 200
DESC_PANEL_UPGRADE_BTN_HEIGHT_ADJUST = -5
DESC_PANEL_UPGRADE_BTN_WIDTH = 120
DESC_PANEL_UPGRADE_BTN_WIDTH_WIDE = 250
DESC_PANEL_DESC_TITLE_V_OFFSET = 15
DESC_PANEL_DESC_TEXT_V_OFFSET = 50
DESC_PANEL_ACTION_BTN_SIZE = (250, 50)
DESC_PANEL_ACTION_BTN_BOTTOM_OFFSET = -45
DESC_PANEL_CLOSE_BUTTON_SIZE = 35
DESC_PANEL_CLOSE_BUTTON_MARGIN = 10
# --- Экран расстановки нейросетей ---
PLACEMENT_GRID_CELL_W = 125
PLACEMENT_GRID_CELL_H = 120
PLACEMENT_ZONE_X = 20
PLACEMENT_MOWER_SLOT_ALPHA = 200        # Прозрачность фона слота для нейросети
PLACEMENT_MOWER_IMG_PADDING = 10        # Отступ для изображения внутри карточки нейросети

# *** УДАЛЕНО: PLACEMENT_GRID_START_Y. Будет вычисляться локально. ***
PLACEMENT_GRID_START_X = PLACEMENT_ZONE_X + PLACEMENT_GRID_CELL_W + 20
PLACEMENT_PANEL_SIZE = (600, 250)
PLACEMENT_PANEL_CARD_SIZE = 100
PLACEMENT_PANEL_CARD_PADDING = 20
PLACEMENT_PANEL_CARD_COLS = 4
PLACEMENT_PANEL_CARDS_TOP_OFFSET = 100
PLACEMENT_PANEL_START_BTN_SIZE = (300, 70)
PLACEMENT_PANEL_START_BTN_TOP_OFFSET = 60
# --- Окно настроек ---
SETTINGS_PANEL_SIZE = (600, 400)
SETTINGS_BORDER_RADIUS = 15
SETTINGS_TITLE_TOP_MARGIN = 30
SETTINGS_LABEL_LEFT_MARGIN = 50
SETTINGS_LABEL_V_OFFSET = 50
SETTINGS_TOGGLE_SIZE = (120, 60)
SETTINGS_TOGGLE_RIGHT_MARGIN = 50
SETTINGS_CLOSE_BUTTON_SIZE = 35
SETTINGS_CLOSE_BUTTON_MARGIN = 10
SETTINGS_CLOSE_BUTTON_LINE_WIDTH = 3
# --- Панель напастей ---
CALAMITY_PANEL_SIZE = (800, 250)
CALAMITY_PANEL_BORDER_WIDTH = 5
CALAMITY_PANEL_BORDER_RADIUS = 15
CALAMITY_ICON_SIZE = (120, 120)
CALAMITY_ICON_LEFT_MARGIN = 40
CALAMITY_TEXT_LEFT_MARGIN = 40
CALAMITY_NAME_TOP_MARGIN = 40
CALAMITY_DESC_TOP_MARGIN = 15

# =============================================================================
# 8. НАСТРОЙКИ ИГРОВОЙ МЕХАНИКИ
# =============================================================================
# --- Тайминги (в миллисекундах) ---
INITIAL_SPAWN_COOLDOWN = 5000
FINAL_WAVE_SPAWN_COOLDOWN = 2000
DEFAULT_ATTACK_COOLDOWN_MS = 1000
COFFEE_BEAN_LIFETIME = 8000
COFFEE_MACHINE_PRODUCING_DURATION = 500
MEDIC_HEAL_COOLDOWN_MS = 3000
EXPLOSION_LIFETIME = 300
BOOK_ATTACK_LIFETIME = 200
SOUNDWAVE_LIFETIME = 5000
BUTTON_CLICK_DELAY = 100
VICTORY_SOUND_DELAY = 300
LEVEL_CLEAR_DEFAULT_DURATION = 3000
CALAMITY_NOTIFICATION_DURATION = 3000
CALAMITY_DURATION = 15000
# --- Игровой баланс и поведение ---
FINAL_WAVE_THRESHOLD = 0.6
BRACKET_PROJECTILE_SPEED = 10
INTEGRAL_PROJECTILE_SPEED = -5
SOUNDWAVE_PROJECTILE_SPEED = 5
NEURO_MOWER_CHAT_GPT_SPEED = 12
NEURO_MOWER_DEEPSEEK_TARGET_COUNT = 3
NEURO_MOWER_GEMINI_TARGET_COUNT = 4
ADDICT_ESCAPE_SPEED_MULTIPLIER = 2.0
THIEF_ESCAPE_SPEED_MULTIPLIER = 2.0
THIEF_STEAL_DISTANCE_THRESHOLD = 10
MATH_TEACHER_JUMP_HEIGHT = 90
MATH_TEACHER_JUMP_DURATION = 1300
MATH_TEACHER_SPEED_PENALTY = 2.0
MEDIC_HEAL_TICK_AMOUNT = 75
CHAT_GPT_LIMIT = 2
AURA_ANIMATION_SPEED = 0.1
ENEMY_ATTACK_OFFSET = 80
# --- Напасти ---
CALAMITY_TRIGGERS = [0.3, 0.7]
CALAMITY_EPIDEMIC_MULTIPLIER = 2.0
CALAMITY_BIG_PARTY_REMOVAL_RATIO = 0.8
CALAMITY_COLLOQUIUM_MULTIPLIER = 1.5
CALAMITY_INTERNET_DOWN_MULTIPLIER = 2.0


# =============================================================================
# 9. ДАННЫЕ ИГРОВЫХ ОБЪЕКТОВ
# =============================================================================
# --- Снаряды ---
PROGRAMMER_PROJECTILE_TYPES = ['bracket_0', 'bracket_1', 'bracket_2']
CALCULUS_PROJECTILE_TYPES = ['plus', 'multiply', 'divide', 'seven', 'three', 'five', 'null']
# --- Данные защитников ---
DEFENDERS_DATA = {
    'programmer': {'cost': 100, 'health': 300, 'damage': 25, 'cooldown': 1.5, 'display_name': 'Мальчик-джун', 'category': 'defenders',
                   'description': "Стандартный стрелок, эффективный против одиночных целей. Его атаки быстры и точны, как идеально написанный код.",
                   'upgrades': { 'damage': {'value': 10, 'cost': 20}, 'cooldown': {'value': -0.3, 'cost': 25} },
                   'animation_data': { 'folder': 'programmer', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }},
    'botanist': {'cost': 150, 'health': 300, 'damage': 50, 'cooldown': 2.5, 'radius': 2, 'display_name': 'Девочка-ботан', 'category': 'defenders',
                 'description': "Находит самого 'жирного' врага на поле и обрушивает на него и его соседей всю тяжесть своих знаний. Атакует по области.",
                 'upgrades': { 'damage': {'value': 25, 'cost': 30}, 'radius': {'value': 1, 'cost': 20} },
                 'animation_data': { 'folder': 'botanist', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }},
    'coffee_machine': {'cost': 50, 'health': 200, 'damage': 0, 'cooldown': 5, 'production': 25, 'display_name': 'Кофемашина', 'category': 'defenders',
                       'description': "Источник жизни и бодрости. Не атакует, но исправно генерирует кофейные зернышки, необходимые для вызова новых защитников.",
                       'upgrades': { 'production': {'value': 15, 'cost': 25}, 'health': {'value': 150, 'cost': 20} },
                       'animation_data': { 'folder': 'coffee_machine', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }},
    'activist': {'cost': 75, 'health': 400, 'damage': 0, 'cooldown': None, 'radius': 2, 'buff': 1.5,
                 'display_name': 'Активист', 'category': 'defenders',
                 'description': "Его пламенные речи вдохновляют всех вокруг. Создает ауру, которая значительно увеличивает урон союзников в радиусе.",
                 'upgrades': {'buff': {'value': 0.3, 'cost': 30}, 'radius': {'value': 1, 'cost': 25}},
                 'animation_data': { 'folder': 'activist', 'speed': 0.3, 'idle': [], 'hit': [] }},
    'guitarist': {'cost': 150, 'health': 300, 'damage': 20, 'cooldown': 4, 'display_name': 'Гитарист', 'category': 'defenders',
                  'projectile_speed': 5, 'description': "Атакует всех врагов на своей линии мощной звуковой волной, которая пробивает их насквозь.",
                  'upgrades': { 'projectile_speed': {'value': 3, 'cost': 20}, 'damage': {'value': 15, 'cost': 25} },
                  'animation_data': { 'folder': 'guitarist', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }},
    'medic': {'cost': 50, 'health': 250, 'damage': 0, 'cooldown': 1.0, 'heal_amount': 200, 'radius': 2, 'display_name': 'Студент-медик', 'category': 'defenders',
              'description': "Живая аптечка. Постепенно отдает свое здоровье самому раненому союзнику в радиусе. Когда его запас здоровья иссякнет, он исчезнет.",
              'upgrades': { 'radius': {'value': 1, 'cost': 20}, 'heal_amount': {'value': 150, 'cost': 25} },
              'animation_data': { 'folder': 'medic', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }},
    'artist': {'cost': 125, 'health': 300, 'damage': 10, 'cooldown': 2, 'slow_duration': 2000, 'slow_factor': 0.5, 'display_name': 'Художница', 'category': 'defenders',
               'description': "Её кляксы краски, попадая во врагов, не только наносят урон, но и значительно замедляют их передвижение.",
               'upgrades': { 'slow_factor': {'value': -0.15, 'cost': 25}, 'damage': {'value': 15, 'cost': 20} },
               'animation_data': { 'folder': 'artist', 'speed': 0.3, 'idle': [], 'attack': [], 'hit': [] }},
    'modnik': {'cost': 125, 'health': 300, 'damage': 1800, 'radius': 2, 'speed': 1.5, 'display_name': 'Модник', 'category': 'defenders',
               'description': "Быстрый юнит-камикадзе. Находит ближайшего врага, подбегает и взрывается, нанося огромный урон по большой площади.",
               'upgrades': { 'radius': {'value': 1, 'cost': 30}, 'damage': {'value': 400, 'cost': 35} },
               'animation_data': { 'folder': 'modnik', 'speed': 0.3, 'idle': [], 'hit': [] }}
}
# --- Данные врагов ---
ENEMIES_DATA = {
    'alarm_clock': {'health': 100, 'speed': 0.8, 'damage': 50, 'cooldown': 1.0, 'display_name': "Первая пара", 'category': 'enemies', 'description': "Обычный враг, который просто идет вперед и больно кусает первого встречного. Берет числом, а не умением.",
                    'animation_data': {'folder': 'alarm_clock', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}},
    'calculus': {'health': 180, 'speed': 0.8, 'damage': 10, 'cooldown': 3.0, 'display_name': "Матанализ", 'category': 'enemies',
                 'description': "Опасный дальнобойный противник. Останавливается и обстреливает защитников на своей линии с безопасного расстояния.",
                 'animation_data': {'folder': 'calculus', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}},
    'math_teacher': {'health': 150, 'speed': 1.5, 'damage': 80, 'cooldown': 1.0, 'display_name': "Злая математичка", 'category': 'enemies', 'description': "Быстрый враг. При столкновении с первым защитником на линии перепрыгивает его, чтобы прорваться в тыл. После прыжка ее скорость снижается.",
                     'animation_data': {'folder': 'math_teacher', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}},
    'addict': {'health': 120, 'speed': 2.5, 'damage': 9999, 'cooldown': 0.5, 'display_name': "Наркоман", 'category': 'enemies', 'description': "Враг-убийца. Игнорирует всех, кроме защитника с самым большим уроном на поле. Целенаправленно бежит к нему и уносит с экрана.",
               'animation_data': {'folder': 'addict', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}},
    'thief': {'health': 120, 'speed': 2.5, 'damage': 9999, 'cooldown': 0.5, 'display_name': "Вор", 'category': 'enemies', 'description': "Главный враг экономики. Ищет Кофемашины, игнорируя героев. Украдет одну и вернется за следующей. Если Кофемашин нет, атакует как обычный враг.",
              'animation_data': {'folder': 'thief', 'speed': 0.3, 'walk': [], 'attack': [], 'hit': []}}
}
# --- Данные нейросетей ---
NEURO_MOWERS_DATA = {
    'chat_gpt': {'cost': 25, 'display_name': 'ChatGPT', 'category': 'systems', 'description': 'Последний рубеж обороны. При контакте с врагом активируется, едет по всей линии и уничтожает всех на своем пути. Может быть не более двух.'},
    'deepseek': {'cost': 15, 'display_name': 'DeepSeek', 'category': 'systems', 'description': 'Тактическая нейросеть. Уничтожает 3 самых близких к вашей базе врага на всем поле.'},
    'gemini': {'cost': 40, 'display_name': 'Gemini', 'category': 'systems', 'description': 'Элитная нейросеть. Уничтожает 4 самых сильных (по текущему здоровью) врага на всем поле.'}
}
# --- Данные напастей ---
CALAMITIES_DATA = {
    'epidemic': {'display_name': 'Эпидемия гриппа', 'category': 'calamities', 'description': 'Все ваши герои заболевают! Их здоровье и урон временно падают в 2 раза.'},
    'big_party': {'display_name': 'Великая туса', 'category': 'calamities', 'description': 'Зов вечеринки! 80% ваших героев (кроме Кофемашин) случайным образом покидают поле боя.'},
    'colloquium': {'display_name': 'Внезапный коллоквиум', 'category': 'calamities', 'description': 'Все враги на поле получают прилив уверенности! Их атаки временно становятся в 1.5 раза сильнее.'},
    'internet_down': {'display_name': 'Отключение интернета', 'category': 'calamities', 'description': 'Студенты не могут списать. Здоровье всех врагов на поле временно удваивается.'}
}
# --- Данные UI элементов для карточек ---
UI_ELEMENTS_DATA = {
    'stipend': {'display_name': 'Стипендия', 'category': 'ui'},
    'coffee_bean': {'display_name': 'Кофейные зернышки', 'category': 'resources'}
}