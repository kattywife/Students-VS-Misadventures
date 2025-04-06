# --- Основные настройки ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_DURATION = 60.0 # Секунд
STARTING_SUN_POINTS = 150

# --- Цвета ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)       # Запасной для горохострела
DARK_GREEN = (0, 100, 0)    # Цвет для газона
YELLOW = (255, 255, 0)    # Запасной для подсолнуха и солнышка
BROWN = (139, 69, 19)     # Запасной для обычного зомби
DARK_GREY = (100, 100, 100) # Запасной для быстрого зомби и фона таймлайна
RED = (255, 0, 0)         # Для текста Game Over и ошибок
BLUE = (0, 0, 255)        # Запасной для снаряда
GREY = (128, 128, 128)    # Фон
LIGHT_BLUE = (173, 216, 230) # Для фона магазина
ORANGE = (255, 165, 0)    # Для таймлайна

# --- Настройки сетки и посадки ---
PLANT_SIZE = 50 # Размер растения будет размером ячейки
GRID_ROWS = 5
GRID_COLS = 9
CELL_WIDTH = PLANT_SIZE + 10
CELL_HEIGHT = PLANT_SIZE + 10
GRID_START_X = 50
# Расчет Y сетки
SHOP_HEIGHT = 80
TOTAL_GRID_HEIGHT = GRID_ROWS * CELL_HEIGHT
AVAILABLE_HEIGHT = SCREEN_HEIGHT - SHOP_HEIGHT
GRID_START_Y = SHOP_HEIGHT + (AVAILABLE_HEIGHT - TOTAL_GRID_HEIGHT) // 2
GRID_LINE_COLOR = (0, 80, 0)
GRID_BG_COLOR = (0, 100, 0)

# --- Параметры Горохострела ---
PEASHOOTER_SIZE = PLANT_SIZE
PEASHOOTER_COST = 100
PEASHOOTER_COOLDOWN = 1.5
PEASHOOTER_HEALTH = 100 # <<<--- Убедись, что это значение осмысленное

# --- Параметры Подсолнуха ---
SUNFLOWER_SIZE = PLANT_SIZE
SUNFLOWER_COST = 50
SUNFLOWER_PRODUCTION_RATE = 8.0 # Секунд на производство
SUNFLOWER_SUN_AMOUNT = 25
SUNFLOWER_HEALTH = 80  # <<<--- Подсолнух менее прочный

# --- Параметры Зомби ---
ZOMBIE_SIZE = 50
ZOMBIE_SPAWN_RATE = 5.0
ZOMBIE_DAMAGE = 10 # Урон зомби (за один "укус")
ZOMBIE_BITE_RATE = 1.0 # <<<--- НОВОЕ: Секунд между "укусами" зомби
ZOMBIE_TYPES = {
    "regular": {"speed": 0.8, "health": 100, "color": BROWN, "image": "zombie_regular.png"},
    "fast":    {"speed": 1.5, "health": 70, "color": DARK_GREY, "image": "zombie_fast.png"}
}

# --- Параметры Снаряда ---
PROJECTILE_SIZE = 15
PROJECTILE_SPEED = 5
PROJECTILE_DAMAGE = 25

# --- Параметры Газонокосилки ---
MOWER_WIDTH = 45
MOWER_HEIGHT = 45
MOWER_SPEED = 4

# --- Финальная волна ---
FINAL_WAVE_START_TIME = GAME_DURATION - 15.0
FINAL_WAVE_SPAWN_RATE = 1.5

IMAGE_FOLDER = "assets/images" # Базовая папка для картинок

PEASHOOTER_IMAGE_FILE = "peashooter.png"
SUNFLOWER_IMAGE_FILE = "sunflower.png"
PROJECTILE_IMAGE_FILE = "projectile.png"
SUN_IMAGE_FILE = "sun.png"
SUN_ICON_FILE = "sun_icon.png"
LAWNMOWER_IMAGE_FILE = "lawnmower.png"
# Имена файлов для зомби берутся из ZOMBIE_TYPES['image']

