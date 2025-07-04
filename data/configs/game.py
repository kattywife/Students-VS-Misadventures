# data/configs/game.py

# =============================================================================
# 1. ОСНОВНЫЕ НАСТРОЙКИ ИГРЫ
# =============================================================================
# Глобальные константы, определяющие окно игры и производительность.

SCREEN_WIDTH = 1280      # Ширина окна в пикселях
SCREEN_HEIGHT = 720     # Высота окна в пикселях
FPS = 60                # Целевая частота кадров в секунду
TITLE = "Студенты против Злоключений" # Заголовок окна игры

# =============================================================================
# 2. ПУТИ К ФАЙЛАМ
# =============================================================================
# Константы для путей к папкам с ресурсами.
ASSETS_DIR = 'assets'
IMAGES_DIR = f'{ASSETS_DIR}/images'

# =============================================================================
# 3. НАСТРОЙКИ БОЕВОЙ СЕТКИ
# =============================================================================
# Параметры, определяющие размер и положение игровой сетки на поле боя.

GRID_ROWS = 5           # Количество рядов (линий)
GRID_COLS = 9           # Количество колонок
CELL_SIZE_W = 110       # Ширина одной ячейки
CELL_SIZE_H = 110       # Высота одной ячейки
GRID_START_X = 150      # Отступ сетки от левого края экрана
GRID_START_Y = 150      # Отступ сетки от верхнего края экрана
GRID_WIDTH = GRID_COLS * CELL_SIZE_W   # Рассчитанная общая ширина сетки
GRID_HEIGHT = GRID_ROWS * CELL_SIZE_H  # Рассчитанная общая высота сетки

# =============================================================================
# 4. НАСТРОЙКИ КОМАНДЫ
# =============================================================================
# Параметры, связанные с командой игрока и экономикой на экране подготовки.

MAX_TEAM_SIZE = 6      # Максимальное количество героев в команде
INITIAL_STIPEND = 150  # Начальное количество стипендии для улучшений
CHAT_GPT_LIMIT = 2     # Максимальное количество нейросетей типа 'chat_gpt' в команде

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)