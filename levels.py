# levels.py

LEVEL_DATA = [
    None,
    {
        "id": 1, "name": "Уровень 1: Первые шаги", "starting_sun": 150,
        "allowed_zombies": ["alarm_clock"], # <<<--- Изменено
        "spawn_rate": 7.0, "zombies_to_defeat": 10
    },
    {
        "id": 2, "name": "Уровень 2: Шустрые лабы", "starting_sun": 125,
        "allowed_zombies": ["alarm_clock", "matan"], # <<<--- Изменено
        "spawn_rate": 6.0, "zombies_to_defeat": 15
    },
    {
        "id": 3, "name": "Уровень 3: Натиск Матана", "starting_sun": 150,
        "allowed_zombies": ["alarm_clock", "matan", "matan"], # <<<--- Изменено
        "spawn_rate": 5.0, "zombies_to_defeat": 20
    },
    {
        "id": 4, "name": "Уровень 4: Дедлайны горят", "starting_sun": 100,
        "allowed_zombies": ["matan", "professor"], # <<<--- Изменено
        "spawn_rate": 4.5, "zombies_to_defeat": 25
    },
    {
        "id": 5, "name": "Уровень 5: Выпускной", "starting_sun": 150,
        "allowed_zombies": ["alarm_clock", "matan", "professor"], # <<<--- Изменено
        "spawn_rate": 4.0, "zombies_to_defeat": 30
    },
]