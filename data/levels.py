# data/levels.py

LEVELS = {
    1: {
        'name': "Тестовый уровень (Все враги)",
        'start_coffee': 2000,
        'neuro_slots': 4,
        'calamities': ['epidemic', 'big_party', 'colloquium', 'internet_down'],
        'enemies': [
            # --- Первая волна: каждый враг на своей линии ---
            ('alarm_clock', 0),  # Базовый враг
            ('calculus', 1),  # Дальнобойный враг
            ('math_teacher', 2),  # Прыгающий враг
            ('addict', 3),  # Охотник за сильными
            ('thief', 4),  # Охотник за кофемашинами

            # --- Пауза перед второй волной ---
            ('alarm_clock', 0), ('alarm_clock', 0),  # Небольшое мясо для разминки

            # --- Вторая волна: смешанная атака ---
            ('thief', 0),  # Проверка поиска цели через все поле
            ('calculus', 4),  # Стрелок с другой стороны
            ('math_teacher', 1),  # Прыгун вперемешку с другими
            ('addict', 2),  # Убийца в центре
            ('alarm_clock', 3),  # Обычная пехота для поддержки
        ]
    },
    2: {
        'name': "Курс 2",
        'start_coffee': 200,
        'neuro_slots': 3,
        'calamities': ['colloquium'],
        'enemies': [
            ('alarm_clock', 2), ('calculus', 3), ('alarm_clock', 1),
            ('calculus', 2), ('alarm_clock', 0),
            ('alarm_clock', 4), ('calculus', 1),
            ('alarm_clock', 2), ('calculus', 0),
        ]
    },
    3: {
        'name': "Курс 3",
        'start_coffee': 250,
        'neuro_slots': 3,
        'calamities': ['internet_down'],
        'enemies': [
            ('calculus', 1), ('math_teacher', 3),
            ('math_teacher', 0), ('math_teacher', 4), ('calculus', 2),
            ('alarm_clock', 1),
            ('alarm_clock', 2), ('alarm_clock', 3),
            ('math_teacher', 2),
        ]
    },
    4: {
        'name': "Курс 4",
        'start_coffee': 300,
        'neuro_slots': 4,
        'calamities': ['epidemic', 'colloquium'],
        'enemies': [
            ('calculus', 1), ('calculus', 3),
            ('thief', 0), ('math_teacher', 1),
            ('math_teacher', 2), ('addict', 3), ('math_teacher', 4),
            ('calculus', 2), ('thief', 3),
            ('addict', 4),
        ]
    },
    5: {
        'name': "Защита Диплома",
        'start_coffee': 400,
        'neuro_slots': 4,
        'calamities': ['big_party', 'internet_down'],
        'enemies': [
            ('calculus', 0), ('calculus', 4),
            ('math_teacher', 2), ('thief', 0),
            ('addict', 4), ('thief', 1), ('addict', 3),
            ('calculus', 1), ('calculus', 3),
            ('math_teacher', 0), ('math_teacher', 4),
            ('thief', 2), ('addict', 2),
            ('calculus', 2),
        ]
    }
}