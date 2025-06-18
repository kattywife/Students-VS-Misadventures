# data/levels.py

LEVELS = {
    1: {
        'name': "Курс 1",
        'start_coffee': 150,
        'neuro_slots': 2,
        'calamities': ['epidemic'], # Только одна, самая простая напасть
        'enemies': [
            # Вводим базовых врагов
            ('alarm_clock', 2),
            ('alarm_clock', 2),
            ('calculus', 3), # Вводим дальнобойного врага
            ('alarm_clock', 1),
            ('alarm_clock', 3),
            ('calculus', 2),
            ('alarm_clock', 2),
            ('alarm_clock', 2),
        ]
    },
    2: {
        'name': "Курс 2",
        'start_coffee': 200,
        'neuro_slots': 3,
        'calamities': ['epidemic', 'colloquium'],
        'enemies': [
            ('alarm_clock', 1),
            ('calculus', 3),
            ('math_teacher', 2), # Вводим нового врага - прыгуна
            ('alarm_clock', 2),
            ('alarm_clock', 4),
            ('calculus', 1),
            ('math_teacher', 3),
            ('alarm_clock', 0),
            ('calculus', 4),
            ('alarm_clock', 1),
            ('alarm_clock', 3),
            ('math_teacher', 2),
        ]
    },
    3: {
        'name': "Курс 3",
        'start_coffee': 250,
        'neuro_slots': 3,
        'calamities': ['colloquium', 'internet_down'],
        'enemies': [
            ('calculus', 1),
            ('thief', 3), # Вводим вора, угрозу для экономики
            ('math_teacher', 2),
            ('alarm_clock', 4),
            ('calculus', 0),
            ('thief', 2), # Второй вор для усиления давления
            ('alarm_clock', 1),
            ('math_teacher', 0),
            ('alarm_clock', 3),
            ('calculus', 4),
            ('alarm_clock', 2),
            ('alarm_clock', 2),
            ('math_teacher', 3),
            ('thief', 1),
        ]
    },
    4: {
        'name': "Курс 4",
        'start_coffee': 300,
        'neuro_slots': 4,
        'calamities': ['internet_down', 'big_party'],
        'enemies': [
            ('math_teacher', 1),
            ('math_teacher', 3),
            ('addict', 2), # Вводим убийцу, который охотится на сильных героев
            ('thief', 4),
            ('calculus', 0),
            ('alarm_clock', 2),
            ('addict', 3), # Второй убийца для хаоса
            ('calculus', 1),
            ('thief', 0),
            ('math_teacher', 4),
            ('alarm_clock', 1),
            ('alarm_clock', 3),
            ('calculus', 2),
            ('addict', 4),
            ('thief', 2),
            ('math_teacher', 0),
        ]
    },
    5: {
        'name': "Защита Диплома",
        'start_coffee': 400,
        'neuro_slots': 4,
        'calamities': ['epidemic', 'big_party', 'colloquium', 'internet_down'], # Все напасти возможны
        'enemies': [
            # Финальный уровень - все вместе и в большом количестве
            ('calculus', 0), ('calculus', 4),
            ('alarm_clock', 1), ('alarm_clock', 2), ('alarm_clock', 3),
            ('math_teacher', 2),
            ('thief', 0), ('addict', 4), # Одновременная атака на экономику и сильных юнитов
            ('alarm_clock', 0), ('alarm_clock', 4),
            ('calculus', 1), ('calculus', 3),
            ('math_teacher', 0), ('math_teacher', 4),
            ('thief', 1), ('addict', 3),
            ('alarm_clock', 2), ('alarm_clock', 2),
            ('calculus', 2),
            ('thief', 3),
            ('addict', 1),
            ('math_teacher', 1), ('math_teacher', 3),
            ('alarm_clock', 0), ('alarm_clock', 1), ('alarm_clock', 2), ('alarm_clock', 3), ('alarm_clock', 4), # Финальная волна
        ]
    }
}