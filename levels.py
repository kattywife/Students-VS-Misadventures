# levels.py

# Структура данных уровней
LEVEL_DATA = [
    # Уровень 0 не используется, начинаем с 1
    None,
    # Уровень 1
    {
        "id": 1,
        "name": "Уровень 1: Первые шаги",
        "starting_sun": 150,
        "allowed_zombies": ["regular"],
        "spawn_rate": 7.0, # Реже для начала
        "zombies_to_defeat": 10 # <<<--- НОВОЕ ПОЛЕ
    },
    # Уровень 2
    {
        "id": 2,
        "name": "Уровень 2: Шустрые лабы",
        "starting_sun": 125,
        "allowed_zombies": ["regular", "fast"],
        "spawn_rate": 6.0,
        "zombies_to_defeat": 15 # <<<--- НОВОЕ ПОЛЕ
    },
    # Уровень 3
    {
        "id": 3,
        "name": "Уровень 3: Натиск Матана",
        "starting_sun": 150,
        "allowed_zombies": ["regular", "regular", "fast"],
        "spawn_rate": 5.0,
        "zombies_to_defeat": 20 # <<<--- НОВОЕ ПОЛЕ
    },
    # Уровень 4
    {
        "id": 4,
        "name": "Уровень 4: Дедлайны горят",
        "starting_sun": 100,
        "allowed_zombies": ["regular", "fast", "fast"],
        "spawn_rate": 4.5,
        "zombies_to_defeat": 25 # <<<--- НОВОЕ ПОЛЕ
    },
    # Уровень 5
    {
        "id": 5,
        "name": "Уровень 5: Выпускной",
        "starting_sun": 150,
        "allowed_zombies": ["regular", "fast", "regular", "fast"],
        "spawn_rate": 4.0,
        "zombies_to_defeat": 30 # <<<--- НОВОЕ ПОЛЕ
    },
]