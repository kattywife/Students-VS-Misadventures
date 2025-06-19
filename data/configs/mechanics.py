# data/configs/mechanics.py

# =============================================================================
# НАСТРОЙКИ ИГРОВОЙ МЕХАНИКИ
# =============================================================================
# Этот файл содержит "магические числа" и константы, которые определяют
# поведение и баланс различных игровых механик.

# --- Снаряды ---
# Списки типов снарядов для случайного выбора. Имена соответствуют файлам изображений.
PROGRAMMER_PROJECTILE_TYPES = ['bracket_0', 'bracket_1', 'bracket_2']
CALCULUS_PROJECTILE_TYPES = ['plus', 'multiply', 'divide', 'seven', 'three', 'five', 'null']

# --- Тайминги (в миллисекундах) ---
# Длительности и задержки для различных событий в игре.
INITIAL_SPAWN_COOLDOWN = 5000       # Начальная задержка между появлением врагов
FINAL_WAVE_SPAWN_COOLDOWN = 2000    # Ускоренная задержка для финальной волны
DEFAULT_ATTACK_COOLDOWN_MS = 1000   # Резервное значение перезарядки атаки
COFFEE_BEAN_LIFETIME = 8000         # Время жизни кофейного зерна
COFFEE_MACHINE_PRODUCING_DURATION = 500 # Длительность анимации производства кофе
MEDIC_HEAL_COOLDOWN_MS = 3000       # Перезарядка лечения у медика
EXPLOSION_LIFETIME = 300            # Длительность анимации взрыва
BOOK_ATTACK_LIFETIME = 200          # Длительность анимации атаки Ботана
SOUNDWAVE_LIFETIME = 5000           # Время жизни звуковой волны
BUTTON_CLICK_DELAY = 100            # Небольшая задержка после клика по кнопке
VICTORY_SOUND_DELAY = 300           # Задержка перед проигрыванием звука победы
LEVEL_CLEAR_DEFAULT_DURATION = 3000 # Длительность экрана "Уровень пройден"
CALAMITY_NOTIFICATION_DURATION = 3000 # Длительность отображения уведомления о напасти
CALAMITY_DURATION = 15000           # Общая длительность эффекта напасти

# --- Игровой баланс и поведение ---
# Числовые параметры, влияющие на геймплей.
FINAL_WAVE_THRESHOLD = 0.6          # Процент появления врагов, после которого начинается финальная волна
LEVEL_WIN_STIPEND_BONUS = 150       # Бонус к стипендии за победу на уровне
BRACKET_PROJECTILE_SPEED = 10       # Скорость снаряда Программиста
INTEGRAL_PROJECTILE_SPEED = -5      # Скорость снаряда Матанализа (отрицательная, так как летит влево)
SOUNDWAVE_PROJECTILE_SPEED = 5      # Скорость звуковой волны Гитариста
NEURO_MOWER_CHAT_GPT_SPEED = 12     # Скорость движения нейросети 'chat_gpt'
NEURO_MOWER_DEEPSEEK_TARGET_COUNT = 3 # Количество целей для 'deepseek'
NEURO_MOWER_GEMINI_TARGET_COUNT = 4   # Количество целей для 'gemini'
ADDICT_ESCAPE_SPEED_MULTIPLIER = 2.0 # Множитель скорости Наркомана при побеге
THIEF_ESCAPE_SPEED_MULTIPLIER = 2.0  # Множитель скорости Вора при побеге
THIEF_STEAL_DISTANCE_THRESHOLD = 10 # Расстояние, на котором Вор может украсть
MATH_TEACHER_JUMP_HEIGHT = 90       # Высота прыжка Математички
MATH_TEACHER_JUMP_DURATION = 1300   # Длительность прыжка Математички
MATH_TEACHER_SPEED_PENALTY = 2.0    # Делитель скорости Математички после прыжка
MEDIC_HEAL_TICK_AMOUNT = 75         # Количество здоровья, восстанавливаемое Медиком за раз
AURA_ANIMATION_SPEED = 0.1          # Скорость анимации ауры Активиста
ENEMY_ATTACK_OFFSET = 80            # Смещение врага при атаке, чтобы он "наезжал" на защитника

# --- Напасти ---
CALAMITY_TRIGGERS = [0.3, 0.7] # Прогресс спавна (30% и 70%), при котором срабатывают напасти
CALAMITY_EPIDEMIC_MULTIPLIER = 2.0      # Множитель ослабления героев при 'Эпидемии'
CALAMITY_BIG_PARTY_REMOVAL_RATIO = 0.8  # Процент героев, удаляемых при 'Великой тусе'
CALAMITY_COLLOQUIUM_MULTIPLIER = 1.5    # Множитель усиления урона врагов при 'Коллоквиуме'
CALAMITY_INTERNET_DOWN_MULTIPLIER = 2.0 # Множитель увеличения здоровья врагов при 'Отключении интернета'