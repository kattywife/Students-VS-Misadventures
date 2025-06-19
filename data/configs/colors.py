# data/configs/colors.py

# =============================================================================
# ЦВЕТА
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

# --- Цвета для резервной отрисовки UI (если ассеты не загрузятся) ---
# Эти цвета будут собраны в общий словарь DEFAULT_COLORS в settings.py
FALLBACK_UI_COLORS = {
    'background': (48, 124, 55),
    'shop_panel': (70, 45, 30),
    'shop_card': (87, 72, 54),
    'shop_border': (34, 28, 21),
    'button': (100, 100, 100),
    'pause_button': (200, 200, 200),
    'bracket': (0, 191, 255),
    'book_attack': (188, 143, 143),
    'sound_wave': (138, 43, 226, 100),
    'paint_splat': (255, 165, 0),
    'integral': (100, 100, 100),
    'explosion': (255, 127, 80),
    'coffee_bean': (255, 222, 173), # <-- ВОТ ОНО, ИСПРАВЛЕНИЕ
}