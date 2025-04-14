# --- Основные настройки ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Настройки Главного Меню
MENU_TITLE_FONT_SIZE = 72
MENU_BUTTON_FONT_SIZE = 40
MENU_BUTTON_WIDTH = 200
MENU_BUTTON_HEIGHT = 50
MENU_BUTTON_COLOR = (0, 150, 0)
MENU_BUTTON_HOVER_COLOR = (0, 200, 0)
MENU_BUTTON_TEXT_COLOR = "WHITE"

# <<<--- Настройки прогресс-бара и волн ---
PROGRESS_BAR_WIDTH = 150
PROGRESS_BAR_HEIGHT = 20
MID_WAVE_THRESHOLD_RATIO = 0.5 # Порог начала волны (60% убитых зомби)
MID_WAVE_SPAWN_RATE = 6.0 # Частота спавна во время волны (сек)

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

# --- Пути к Ассетам ---
IMAGE_FOLDER = "assets/images"
# SOUND_FOLDER = "assets/sounds" # Для будущего

# --- Общие Игровые Параметры ---
STARTING_SUN_POINTS = 150 # Стартовое количество "Кофеина"

# ===========================================
# --- Настройки Персонажей и Объектов ---
# ===========================================

# --- Студент: Мальчик Джун ---
JUN_BOY_COST = 100
JUN_BOY_HEALTH = 100
JUN_BOY_SIZE = PLANT_SIZE
JUN_BOY_COOLDOWN = 1.5    # Перезарядка выстрела
JUN_BOY_IMAGE_FILE = "jun_boy.png"
# --- Снаряд Джуна: Шестеренка ---
GEAR_SIZE = 15
GEAR_SPEED = 6
GEAR_DAMAGE = 20
GEAR_IMAGE_FILE = "gear.png"

# --- Студент: Девочка Ботан ---
BOTAN_GIRL_COST = 150
BOTAN_GIRL_HEALTH = 75
BOTAN_GIRL_SIZE = PLANT_SIZE
BOTAN_GIRL_COOLDOWN = 2.0  # Перезарядка выстрела
BOTAN_GIRL_IMAGE_FILE = "botan_girl.png"
# --- Снаряд Ботана: Книга ---
BOOK_SIZE = 25
BOOK_SPEED = 4
BOOK_DAMAGE = 40
BOOK_IMAGE_FILE = "book.png"

# --- Генератор: Кофе-машина ---
COFFEE_MACHINE_COST = 50
COFFEE_MACHINE_HEALTH = 80
COFFEE_MACHINE_SIZE = PLANT_SIZE
COFFEE_MACHINE_PRODUCTION_RATE = 6.0 # Секунд на генерацию
COFFEE_MACHINE_IMAGE_FILE = "coffee_machine.png"
# --- Ресурс: Кофейное Зерно ---
COFFEE_BEAN_VALUE = 50       # Сколько "кофеина" дает
COFFEE_BEAN_SIZE = 35
COFFEE_BEAN_LIFETIME = 7.0    # Секунд жизни на экране
COFFEE_BEAN_IMAGE_FILE = "coffee_bean.png"
COFFEE_BEAN_ICON_FILE = "coffee_bean_icon.png" # Иконка для магазина

# --- "Газонокосилка": Академ ---
ACADEM_WIDTH = 45
ACADEM_HEIGHT = 45
ACADEM_SPEED = 5
ACADEM_IMAGE_FILE = "academ.png"

# --- "Зомби": Злоключения ---
ADVERSITY_SIZE = 50     # Общий размер для ректов
ADVERSITY_DAMAGE = 10   # Урон по студенту
ADVERSITY_BITE_RATE = 1.0 # Секунд между атаками

# Типы Злоключений (Зомби) и их индивидуальные параметры
ADVERSITY_TYPES = {
    "alarm_clock": { # Первая пара (будильник)
        "name": "Будильник 8:30", # Отображаемое имя (если нужно)
        "speed": 0.7,
        "health": 80,
        "color": (200, 200, 0), # Запасной цвет
        "image": "alarm_clock.png"
    },
    "professor": { # Преподаватель
        "name": "Профессор Дедлайн",
        "speed": 0.5,
        "health": 150,
        "color": (100, 100, 150),
        "image": "professor.png"
    },
    "matan": { # Матанализ (книга)
        "name": "Матан Неизбежный",
        "speed": 0.9,
        "health": 100,
        "color": (200, 100, 100),
        "image": "matan.png"
    }
    # Можно добавить другие типы: "session", "kursovaya", "diploma" и т.д.
}